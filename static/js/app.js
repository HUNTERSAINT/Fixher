(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  function load(key) { try { return JSON.parse(localStorage.getItem(key)) || []; } catch (e) { return []; } }
  function save(key, v) { try { localStorage.setItem(key, JSON.stringify(v)); } catch (e) {} }

  var toastEl = $('#toast'), toastT;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg; toastEl.classList.add('show');
    clearTimeout(toastT); toastT = setTimeout(function () { toastEl.classList.remove('show'); }, 2200);
  }

  /* header shadow */
  var header = $('#header');
  function onScroll() { header && header.classList.toggle('scrolled', window.scrollY > 20); }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  /* drawer */
  var drawer = $('#drawer'), burger = $('#burger');
  function setDrawer(open) {
    drawer.classList.toggle('open', open);
    drawer.setAttribute('aria-hidden', String(!open));
    burger.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
  }
  if (burger) burger.addEventListener('click', function () { setDrawer(true); });
  var dc = $('#drawerClose'); if (dc) dc.addEventListener('click', function () { setDrawer(false); });
  if (drawer) drawer.addEventListener('click', function (e) { if (e.target === drawer) setDrawer(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { setDrawer(false); closeLb(); } });

  /* reveal on scroll */
  var rev = $$('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { threshold: 0.12 });
    rev.forEach(function (el) { io.observe(el); });
  } else { rev.forEach(function (el) { el.classList.add('in'); }); }

  /* wishlist + cart state */
  function wish() { return load('fh_wish'); }
  function cart() { return load('fh_cart'); }
  function refreshCounts() {
    var w = wish().length, c = cart().reduce(function (a, i) { return a + i.qty; }, 0);
    $$('[data-wish-count]').forEach(function (el) { el.textContent = w; el.classList.toggle('zero', !w && el.classList.contains('count')); });
    $$('[data-cart-count]').forEach(function (el) { el.textContent = c; el.classList.toggle('zero', !c && el.classList.contains('count')); });
    var ws = wish();
    $$('[data-wish]').forEach(function (b) {
      var on = ws.indexOf(b.dataset.wish) > -1;
      b.classList.toggle('on', on); b.setAttribute('aria-pressed', String(on));
    });
  }
  document.addEventListener('click', function (e) {
    var h = e.target.closest('[data-wish]');
    if (h) {
      var s = h.dataset.wish, w = wish(), i = w.indexOf(s);
      if (i > -1) { w.splice(i, 1); toast('Removed from wishlist'); } else { w.push(s); toast('Saved to wishlist ♡'); }
      save('fh_wish', w); refreshCounts(); renderWishlist(); return;
    }
    var a = e.target.closest('[data-add]');
    if (a) {
      var c = cart(), slug = a.dataset.add, f = c.filter(function (x) { return x.slug === slug; })[0];
      if (f) f.qty = Math.min(20, f.qty + 1); else c.push({ slug: slug, qty: 1 });
      save('fh_cart', c); refreshCounts(); toast('Added to basket');
    }
  });

  function renderWishlist() {
    var grid = $('#wishGrid'); if (!grid) return;
    var ws = wish(), shown = 0;
    $$('.wish-item', grid).forEach(function (el) { var on = ws.indexOf(el.dataset.slug) > -1; el.hidden = !on; if (on) shown++; });
    var empty = $('#wishEmpty'); if (empty) empty.hidden = shown > 0;
    $$('.wish-item .reveal', grid).forEach(function (el) { el.classList.add('in'); });
  }

  /* cart page */
  var catEl = $('#catalogData');
  function renderCart() {
    if (!catEl) return;
    var data = JSON.parse(catEl.textContent), list = $('#cartList'), c = cart().filter(function (i) { return data[i.slug]; });
    list.innerHTML = '';
    c.forEach(function (i) {
      var p = data[i.slug], d = document.createElement('div');
      d.className = 'cart-item';
      d.innerHTML = '<img alt=""><div><h4><a></a></h4><div class="qty"><button aria-label="Less">−</button><span></span><button aria-label="More">+</button></div></div><button class="rm">Remove</button>';
      d.querySelector('img').src = p.img;
      var a = d.querySelector('a'); a.href = p.url; a.textContent = p.name;
      d.querySelector('.qty span').textContent = i.qty;
      var b = d.querySelectorAll('.qty button');
      b[0].onclick = function () { i.qty = Math.max(1, i.qty - 1); persist(c); };
      b[1].onclick = function () { i.qty = Math.min(20, i.qty + 1); persist(c); };
      d.querySelector('.rm').onclick = function () { persist(c.filter(function (x) { return x !== i; })); };
      list.appendChild(d);
    });
    $('#cartEmpty').hidden = c.length > 0; $('#cartForm').hidden = c.length === 0;
  }
  function persist(c) { save('fh_cart', c); refreshCounts(); renderCart(); }
  var cf = $('#cartForm');
  if (cf) cf.addEventListener('submit', function (e) {
    e.preventDefault();
    var win = window.open('', '_blank');
    fetch('/api/enquiry', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items: cart(), name: cf.name.value }) })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        if (!j.ok) { if (win) win.close(); toast(j.error || 'Something went wrong'); return; }
        if (win) win.location = j.link; else window.location = j.link;
        save('fh_cart', []); refreshCounts(); renderCart();
      }).catch(function () { if (win) win.close(); toast('Network error. Please try again.'); });
  });

  /* reviews carousel */
  var rv = $('#reviews');
  if (rv) {
    var items = $$('.review', rv), dots = $$('.dots button', rv), idx = 0, timer;
    function show(n) {
      idx = (n + items.length) % items.length;
      items.forEach(function (el, k) { el.classList.toggle('on', k === idx); });
      dots.forEach(function (el, k) { el.classList.toggle('on', k === idx); });
    }
    function auto() { clearInterval(timer); timer = setInterval(function () { show(idx + 1); }, 5500); }
    dots.forEach(function (d, k) { d.addEventListener('click', function () { show(k); auto(); }); });
    auto();
  }

  /* gallery lightbox */
  var lb = $('#lightbox');
  function closeLb() { if (lb) lb.hidden = true; }
  if (lb) {
    $$('.m-item').forEach(function (b) { b.addEventListener('click', function () { $('img', lb).src = b.dataset.full; lb.hidden = false; }); });
    lb.addEventListener('click', closeLb);
  }

  /* booking: live slot availability, Sundays closed */
  var bd = $('#bDate');
  if (bd) {
    var slotsBox = $('#slots'), hint = $('#dateHint');
    function paint(list) {
      $$('.slot', slotsBox).forEach(function (el) {
        var t = $('input', el).value, rec = list.filter(function (x) { return x.time === t; })[0];
        var ok = !rec || rec.available, inp = $('input', el);
        el.classList.toggle('taken', !ok); inp.disabled = !ok; if (!ok) inp.checked = false;
      });
    }
    function check() {
      if (!bd.value) return;
      var d = new Date(bd.value + 'T12:00:00');
      if (d.getDay() === 0) { hint.textContent = 'We are closed on Sundays. Please pick another day.'; hint.style.color = '#8b2a17'; bd.value = ''; return; }
      hint.textContent = 'Greyed-out times are already booked.'; hint.style.color = '';
      fetch('/book/slots?date=' + encodeURIComponent(bd.value)).then(function (r) { return r.json(); }).then(paint).catch(function () {});
    }
    bd.addEventListener('change', check); check();
    $('#bookForm').addEventListener('submit', function (e) {
      var f = e.target;
      if (!f.service.value || !f.date.value || !f.time.value || !f.name.value.trim() || !f.phone.value.trim()) {
        e.preventDefault(); toast('Please complete service, date, time, name and phone.');
      }
    });
  }

  refreshCounts(); renderWishlist(); renderCart();
})();
