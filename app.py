import os
import re
import sqlite3
import urllib.parse
from datetime import date, datetime, timedelta
from functools import wraps

from flask import (Flask, Response, abort, flash, g, jsonify, redirect,
                   render_template, request, session, url_for)

from products import BRAND, FAQS, PRODUCTS, REVIEWS, SERVICES, TIME_SLOTS

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE, "fixher.db"))
os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "fixher2026")

PRODUCT_MAP = {p["slug"]: p for p in PRODUCTS}
SERVICE_MAP = {s["slug"]: s for s in SERVICES}


# ---------- database ----------
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, phone TEXT NOT NULL, service TEXT NOT NULL,
            booking_date TEXT NOT NULL, booking_time TEXT NOT NULL,
            wig_source TEXT, notes TEXT, status TEXT DEFAULT 'new',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, phone TEXT, message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, phone TEXT, items TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()


init_db()


# ---------- helpers ----------
def wa_link(text=""):
    base = f"https://wa.me/{BRAND['whatsapp']}"
    return f"{base}?text={urllib.parse.quote(text)}" if text else base


def naira(n):
    return "₦{:,.0f}".format(n)


@app.context_processor
def inject_globals():
    return dict(
        brand=BRAND, wa_link=wa_link, naira=naira,
        nav_services=SERVICES, year=datetime.now().year,
    )


def clean_phone(p):
    return re.sub(r"[^\d+]", "", p or "")


def admin_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*a, **kw)
    return wrapper


# ---------- public pages ----------
@app.route("/")
def home():
    return render_template("home.html", products=PRODUCTS, services=SERVICES,
                           reviews=REVIEWS, page="home")


@app.route("/services")
def services():
    return render_template("services.html", services=SERVICES, faqs=FAQS, page="services")


@app.route("/shop")
def shop():
    return render_template("shop.html", products=PRODUCTS, page="shop")


@app.route("/shop/<slug>")
def product(slug):
    p = PRODUCT_MAP.get(slug) or abort(404)
    related = [x for x in PRODUCTS if x["slug"] != slug]
    return render_template("product.html", p=p, related=related, page="shop")


@app.route("/gallery")
def gallery():
    return render_template("gallery.html", products=PRODUCTS, page="gallery")


@app.route("/about")
def about():
    return render_template("about.html", page="about")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        msg = request.form.get("message", "").strip()
        if not name or not msg:
            flash("Please add your name and a message.", "error")
        else:
            db().execute("INSERT INTO messages (name, phone, message) VALUES (?,?,?)",
                         (name, clean_phone(request.form.get("phone")), msg))
            db().commit()
            flash("Thank you! We received your message and will reply shortly.", "ok")
            return redirect(url_for("contact"))
    return render_template("contact.html", page="contact")


@app.route("/book", methods=["GET", "POST"])
def book():
    today = date.today()
    max_day = today + timedelta(days=60)
    preselect = request.args.get("service", "")
    if request.method == "POST":
        f = request.form
        name = f.get("name", "").strip()
        phone = clean_phone(f.get("phone"))
        service = f.get("service", "")
        bdate = f.get("date", "")
        btime = f.get("time", "")
        errors = []
        if len(name) < 2:
            errors.append("Please enter your name.")
        if len(re.sub(r"\D", "", phone)) < 10:
            errors.append("Please enter a valid phone number.")
        if service not in SERVICE_MAP:
            errors.append("Please choose a service.")
        try:
            d = datetime.strptime(bdate, "%Y-%m-%d").date()
            if d < today or d > max_day:
                errors.append("Please choose a date in the next 60 days.")
            elif d.weekday() == 6:
                errors.append("We are closed on Sundays. Please choose another day.")
        except ValueError:
            errors.append("Please choose a valid date.")
        if btime not in TIME_SLOTS:
            errors.append("Please choose a time slot.")
        if not errors:
            taken = db().execute(
                "SELECT 1 FROM bookings WHERE booking_date=? AND booking_time=? AND status!='cancelled'",
                (bdate, btime)).fetchone()
            if taken:
                errors.append("Sorry, that slot was just taken. Please pick another time.")
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("book.html", slots=TIME_SLOTS, today=today.isoformat(),
                                   max_day=max_day.isoformat(), preselect=service or preselect,
                                   form=f, page="book"), 400
        cur = db().execute(
            "INSERT INTO bookings (name, phone, service, booking_date, booking_time, wig_source, notes) VALUES (?,?,?,?,?,?,?)",
            (name, phone, service, bdate, btime, f.get("wig_source", ""), f.get("notes", "").strip()))
        db().commit()
        return redirect(url_for("booked", bid=cur.lastrowid))
    return render_template("book.html", slots=TIME_SLOTS, today=today.isoformat(),
                           max_day=max_day.isoformat(), preselect=preselect, form={}, page="book")


@app.route("/book/slots")
def slots():
    """Return slots with availability for a given date (used by the booking form)."""
    d = request.args.get("date", "")
    rows = db().execute(
        "SELECT booking_time FROM bookings WHERE booking_date=? AND status!='cancelled'", (d,)).fetchall()
    taken = {r["booking_time"] for r in rows}
    return jsonify([{"time": t, "available": t not in taken} for t in TIME_SLOTS])


@app.route("/booked/<int:bid>")
def booked(bid):
    b = db().execute("SELECT * FROM bookings WHERE id=?", (bid,)).fetchone() or abort(404)
    service = SERVICE_MAP[b["service"]]["name"]
    pretty = datetime.strptime(b["booking_date"], "%Y-%m-%d").strftime("%A, %d %B %Y")
    msg = (f"Hello Fix Her! I just booked online.\n\nName: {b['name']}\nService: {service}\n"
           f"Date: {pretty}\nTime: {b['booking_time']}\nRef: FH-{b['id']:04d}\n\nPlease confirm my appointment.")
    return render_template("booked.html", b=b, service=service, pretty=pretty,
                           ref=f"FH-{b['id']:04d}", confirm_link=wa_link(msg), page="book")


@app.route("/wishlist")
def wishlist():
    return render_template("wishlist.html", products=PRODUCTS, page="wishlist")


@app.route("/cart")
def cart():
    catalog = {
        p["slug"]: {
            "name": p["name"],
            "img": url_for("static", filename="img/" + p["image_sm"]),
            "price": p["price"],
            "url": url_for("product", slug=p["slug"]),
        }
        for p in PRODUCTS
    }
    return render_template("cart.html", catalog=catalog, page="cart")


@app.route("/account")
def account():
    return render_template("account.html", page="account")


@app.route("/api/enquiry", methods=["POST"])
def enquiry():
    data = request.get_json(silent=True) or {}
    items = [i for i in data.get("items", []) if i.get("slug") in PRODUCT_MAP]
    if not items:
        return jsonify(ok=False, error="Your basket is empty."), 400
    lines, stored = [], []
    for i in items:
        p = PRODUCT_MAP[i["slug"]]
        qty = max(1, min(int(i.get("qty", 1) or 1), 20))
        lines.append(f"• {p['name']} × {qty}")
        stored.append(f"{p['name']} x{qty}")
    name = str(data.get("name", ""))[:80]
    phone = clean_phone(data.get("phone", ""))
    db().execute("INSERT INTO enquiries (name, phone, items) VALUES (?,?,?)", (name, phone, "; ".join(stored)))
    db().commit()
    text = "Hello Fix Her! I'd like to order / enquire about:\n\n" + "\n".join(lines)
    if name:
        text += f"\n\nName: {name}"
    text += "\n\nPlease send me prices and availability."
    return jsonify(ok=True, link=wa_link(text))


@app.route("/sitemap.xml")
def sitemap():
    urls = [url_for(e, _external=True) for e in
            ("home", "services", "shop", "gallery", "about", "contact", "book")]
    urls += [url_for("product", slug=p["slug"], _external=True) for p in PRODUCTS]
    xml = ('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>")
    return Response(xml, mimetype="application/xml")


@app.route("/robots.txt")
def robots():
    return Response(f"User-agent: *\nAllow: /\nDisallow: /admin\nSitemap: {url_for('sitemap', _external=True)}\n",
                    mimetype="text/plain")


# ---------- admin ----------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
        flash("Wrong password.", "error")
    return render_template("admin_login.html", page="admin")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("home"))


@app.route("/admin")
@admin_required
def admin():
    bookings = db().execute("SELECT * FROM bookings ORDER BY booking_date, booking_time").fetchall()
    msgs = db().execute("SELECT * FROM messages ORDER BY id DESC LIMIT 50").fetchall()
    enq = db().execute("SELECT * FROM enquiries ORDER BY id DESC LIMIT 50").fetchall()
    return render_template("admin.html", bookings=bookings, msgs=msgs, enq=enq,
                           service_map=SERVICE_MAP, page="admin")


@app.route("/admin/booking/<int:bid>/<status>", methods=["POST"])
@admin_required
def admin_booking_status(bid, status):
    if status not in ("new", "confirmed", "done", "cancelled"):
        abort(400)
    db().execute("UPDATE bookings SET status=? WHERE id=?", (status, bid))
    db().commit()
    return redirect(url_for("admin"))


@app.errorhandler(404)
def not_found(_e):
    return render_template("404.html", page="404"), 404


@app.after_request
def cache_headers(resp):
    if request.path.startswith("/static/"):
        resp.headers["Cache-Control"] = "public, max-age=604800"
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=bool(os.environ.get("DEBUG")))
