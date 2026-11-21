# Fix Her Hair Brand website (Flask)

Run locally:
    pip install -r requirements.txt
    python app.py          # http://localhost:5000

Deploy (Railway / Render): start command `gunicorn app:app`.
Set env vars: SECRET_KEY, ADMIN_PASSWORD (default is fixher2026, change it!).

Edit products.py to change wigs, prices, services, reviews, phone, Instagram, address.
Bookings, messages and orders are stored in fixher.db. View them at /admin.
