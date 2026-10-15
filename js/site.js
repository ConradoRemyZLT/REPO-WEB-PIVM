/* Parque Industrial Vaca Muerta — comportamiento del sitio (sin dependencias) */
(function () {
  'use strict';
  var d = document, root = d.documentElement;
  root.classList.remove('no-js');

  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  var reduced = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- idioma ES / EN ---------- */
  function setLang(l, persist) {
    l = l === 'en' ? 'en' : 'es';
    root.setAttribute('lang', l);
    d.querySelectorAll('[data-lang-btn]').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-lang-btn') === l ? 'true' : 'false');
    });
    // atributos traducibles: data-es-<attr> / data-en-<attr>
    d.querySelectorAll('[data-i18n-attr]').forEach(function (el) {
      el.getAttribute('data-i18n-attr').split(',').forEach(function (a) {
        var v = el.getAttribute('data-' + l + '-' + a);
        if (v !== null) el.setAttribute(a, v);
      });
    });
    var t = d.querySelector('meta[name="title-' + l + '"]');
    if (t) d.title = t.content;
    if (persist) store.set('pivm-lang', l);
  }
  var qs = new URLSearchParams(location.search).get('lang');
  setLang(qs || store.get('pivm-lang') || root.getAttribute('lang') || 'es', !!qs);
  d.querySelectorAll('[data-lang-btn]').forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.getAttribute('data-lang-btn'), true); });
  });
  function L() { return root.getAttribute('lang') === 'en' ? 'en' : 'es'; }

  /* ---------- header / menú móvil ---------- */
  var hdr = d.getElementById('hdr'), wa = d.querySelector('.wa-float'), toTop = d.querySelector('.to-top');
  function onScroll() {
    var y = window.scrollY || 0;
    if (hdr) hdr.classList.toggle('scrolled', y > 40);
    if (wa) wa.classList.toggle('show', y > window.innerHeight * 0.6);
    if (toTop) toTop.classList.toggle('show', y > window.innerHeight * 0.6);
  }
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  if (toTop) toTop.addEventListener('click', function (e) {
    e.preventDefault();
    var rm = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({ top: 0, behavior: rm ? 'auto' : 'smooth' });
    if (history.replaceState) history.replaceState(null, '', location.pathname + location.search);
  });
  var mbtn = d.querySelector('.mbtn');
  if (mbtn) {
    mbtn.addEventListener('click', function () {
      var open = d.body.classList.toggle('mopen');
      mbtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    d.querySelectorAll('.mov a').forEach(function (a) {
      a.addEventListener('click', function () { d.body.classList.remove('mopen'); mbtn.setAttribute('aria-expanded', 'false'); });
    });
    addEventListener('keydown', function (e) { if (e.key === 'Escape') d.body.classList.remove('mopen'); });
  }

  /* ---------- reveal ---------- */
  var revealEls = d.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduced) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('revealed'); io.unobserve(e.target); } });
    }, { threshold: 0.14, rootMargin: '0px 0px -6% 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  } else revealEls.forEach(function (el) { el.classList.add('revealed'); });

  /* ---------- contadores ---------- */
  function animCount(el) {
    var target = el.getAttribute('data-count'); // ej. "1.350" o "34"
    var sep = target.indexOf('.') > -1 ? '.' : (target.indexOf(',') > -1 ? ',' : '');
    var end = parseInt(target.replace(/[.,]/g, ''), 10);
    if (isNaN(end) || reduced) return;
    var t0 = null, dur = 1500;
    function fmt(n) { return sep ? String(n).replace(/\B(?=(\d{3})+(?!\d))/g, sep) : String(n); }
    function step(ts) {
      if (!t0) t0 = ts;
      var p = Math.min((ts - t0) / dur, 1), e = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(Math.round(end * e));
      if (p < 1) requestAnimationFrame(step); else el.textContent = target;
    }
    requestAnimationFrame(step);
  }
  if ('IntersectionObserver' in window) {
    var cio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { animCount(e.target); cio.unobserve(e.target); } });
    }, { threshold: 0.6 });
    d.querySelectorAll('[data-count]').forEach(function (el) { cio.observe(el); });
  }

  /* ---------- video del hero ---------- */
  var hv = d.querySelector('[data-hero-video]');
  if (hv) {
    var mq = matchMedia('(max-aspect-ratio: 4/5)');
    var pickSrc = function () { return (mq.matches && hv.getAttribute('data-mobile')) || hv.getAttribute('data-desktop'); };
    var pickPoster = function () { return (mq.matches && hv.getAttribute('data-mobile-poster')) || hv.getAttribute('data-desktop-poster'); };
    // Video ambiental, sin sonido: arranca solo siempre (también con "reducir animaciones"
    // del sistema activado; el botón de pausa queda disponible). Se reintenta si el
    // navegador lo frena hasta que haya interacción, o al volver a la pestaña.
    hv.muted = true; hv.defaultMuted = true; hv.playsInline = true;
    var userPaused = false;
    var tryPlay = function () {
      if (userPaused || !hv.paused) return;
      var p = hv.play(); if (p && p.catch) p.catch(function () {});
    };
    var load = function () {
      var s = pickSrc();
      if (hv.getAttribute('src') === s) return;
      hv.setAttribute('poster', pickPoster());
      hv.src = s;
      hv.load();
      tryPlay();
    };
    load();
    ['loadeddata', 'canplay'].forEach(function (ev) { hv.addEventListener(ev, tryPlay); });
    d.addEventListener('visibilitychange', function () { if (!d.hidden) tryPlay(); });
    var kick = function () { tryPlay(); if (!hv.paused) ['pointerdown', 'touchstart', 'keydown', 'scroll'].forEach(function (ev) { window.removeEventListener(ev, kick); }); };
    ['pointerdown', 'touchstart', 'keydown', 'scroll'].forEach(function (ev) { window.addEventListener(ev, kick, { passive: true }); });
    if (mq.addEventListener) mq.addEventListener('change', load);
    var bPlay = d.querySelector('[data-v-play]'), bSnd = d.querySelector('[data-v-sound]');
    var sync = function () {
      if (bPlay) bPlay.classList.toggle('is-on', !hv.paused);
      if (bSnd) bSnd.classList.toggle('is-on', !hv.muted);
    };
    hv.addEventListener('play', sync); hv.addEventListener('pause', sync); hv.addEventListener('volumechange', sync);
    if (bPlay) bPlay.addEventListener('click', function () { if (hv.paused) { userPaused = false; hv.play(); } else { userPaused = true; hv.pause(); } });
    if (bSnd) bSnd.addEventListener('click', function () { hv.muted = !hv.muted; if (!hv.muted && hv.paused) hv.play(); });
    sync();
  }

  /* ---------- galerías ---------- */
  d.querySelectorAll('[data-gallery]').forEach(function (g) {
    var track = g.querySelector('.gtrack'), slides = g.querySelectorAll('.gslide'),
        dots = g.querySelectorAll('.gdot'), cur = g.querySelector('.gc-cur'), i = 0, n = slides.length, timer;
    function go(k) {
      i = (k + n) % n;
      track.style.transform = 'translateX(' + (-100 * i) + '%)';
      dots.forEach(function (dt, j) { dt.classList.toggle('on', j === i); dt.setAttribute('aria-current', j === i ? 'true' : 'false'); });
      if (cur) cur.textContent = i + 1;
      slides.forEach(function (s, j) { s.setAttribute('aria-hidden', j === i ? 'false' : 'true'); });
    }
    var prev = g.querySelector('.gprev'), next = g.querySelector('.gnext');
    if (prev) prev.addEventListener('click', function () { go(i - 1); stop(); });
    if (next) next.addEventListener('click', function () { go(i + 1); stop(); });
    dots.forEach(function (dt, j) { dt.addEventListener('click', function () { go(j); stop(); }); });
    var x0 = null;
    g.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    g.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 40) { go(dx < 0 ? i + 1 : i - 1); stop(); }
      x0 = null;
    });
    g.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { go(i - 1); stop(); }
      if (e.key === 'ArrowRight') { go(i + 1); stop(); }
    });
    function stop() { clearInterval(timer); }
    if (!reduced && g.hasAttribute('data-autoplay')) timer = setInterval(function () { go(i + 1); }, 5200);
    go(0);
  });

  /* ---------- videos de YouTube (se cargan al hacer clic) ---------- */
  d.querySelectorAll('[data-yt]').forEach(function (b) {
    b.addEventListener('click', function () {
      var id = b.getAttribute('data-yt'), fr = d.createElement('iframe');
      fr.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0&modestbranding=1';
      fr.title = b.getAttribute('aria-label') || 'Video';
      fr.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
      fr.allowFullscreen = true;
      b.parentNode.appendChild(fr); b.remove();
    });
  });
  // miniaturas reales de YouTube con escalera de respaldo
  d.querySelectorAll('img[data-yt-thumb]').forEach(function (img) {
    var id = img.getAttribute('data-yt-thumb'), q = ['maxresdefault', 'sddefault', 'hqdefault'], k = 0;
    img.addEventListener('error', function () {
      k++;
      if (k < q.length) img.src = 'https://i.ytimg.com/vi/' + id + '/' + q[k] + '.jpg';
      else if (img.getAttribute('data-fallback')) { img.src = img.getAttribute('data-fallback'); img.removeAttribute('data-yt-thumb'); }
    });
    img.src = 'https://i.ytimg.com/vi/' + id + '/' + q[0] + '.jpg';
  });

  /* ---------- recorrido 360° (Kuula) ---------- */
  d.querySelectorAll('.tour-box').forEach(function (box) {
    var b = box.querySelector('.tour-start');
    if (!b) return;
    b.addEventListener('click', function () {
      var f = d.createElement('iframe');
      f.src = 'https://kuula.co/share/collection/' + box.getAttribute('data-tour') + '?logo=1&info=1&fs=1&vr=0&zoom=1&initload=0&thumbs=-1&inst=' + L();
      f.title = 'Recorrido 360°'; f.setAttribute('allowfullscreen', '');
      f.allow = 'xr-spatial-tracking; gyroscope; accelerometer; fullscreen';
      box.appendChild(f); b.remove();
    });
  });

  /* ---------- formulario: WhatsApp o mail ---------- */
  var form = d.querySelector('[data-contact-form]');
  if (form) {
    var cfg = JSON.parse(form.getAttribute('data-cfg'));
    var pre = form.getAttribute('data-preselect');
    /* deslizante "Soy empresa / Soy inversor": filtra las opciones y adapta el texto de ayuda */
    var allOpts = form.perfil ? [].slice.call(form.perfil.options) : [];
    var msgEl = form.elements.msg;
    function setMode(m, want) {
      var r = form.querySelector('input[name="soy"][value="' + m + '"]'); if (r) r.checked = true;
      form.classList.toggle('m-inv', m === 'inversor');
      if (form.perfil) {
        form.perfil.innerHTML = '';
        allOpts.forEach(function (o) { if ((o.getAttribute('data-modes') || '').split(' ').indexOf(m) > -1) form.perfil.appendChild(o); });
        var has = want && allOpts.some(function (o) { return o.value === want && o.parentNode; });
        form.perfil.value = has ? want : form.perfil.options[0].value;
      }
      if (msgEl) {
        ['es', 'en'].forEach(function (lg) { msgEl.setAttribute('data-' + lg + '-placeholder', msgEl.getAttribute('data-ph-' + m + '-' + lg)); });
        msgEl.setAttribute('placeholder', msgEl.getAttribute('data-ph-' + m + '-' + L()));
      }
    }
    var modeOf = function (p) { return p === 'inversor' ? 'inversor' : 'empresa'; };
    form._setMode = function (p) { setMode(modeOf(p), p); };
    form.querySelectorAll('input[name="soy"]').forEach(function (r) { r.addEventListener('change', function () { if (r.checked) setMode(r.value); }); });
    setMode(modeOf(pre), pre);
    var labels = {
      es: { nombre: 'Nombre', empresa: 'Empresa', email: 'Email', tel: 'Celular', perfil: 'Perfil', msg: 'Consulta', subj: 'Consulta web · Parque Industrial Vaca Muerta', hi: 'Hola, les escribo desde la web del Parque Industrial Vaca Muerta.' },
      en: { nombre: 'Name', empresa: 'Company', email: 'Email', tel: 'Phone', perfil: 'Profile', msg: 'Message', subj: 'Website enquiry · Parque Industrial Vaca Muerta', hi: 'Hello, I am writing from the Parque Industrial Vaca Muerta website.' }
    };
    function val(n) { var el = form.elements[n]; return el ? String(el.value || '').trim() : ''; }
    function check() {
      var ok = true;
      ['nombre', 'tel'].forEach(function (n) {
        var f = form.elements[n].closest('.field'), bad = !val(n);
        f.classList.toggle('err', bad); if (bad) ok = false;
      });
      var em = val('email'), ef = form.elements.email.closest('.field');
      var badE = em && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em);
      ef.classList.toggle('err', !!badE); if (badE) ok = false;
      if (!ok) { var first = form.querySelector('.field.err input'); if (first) first.focus(); }
      return ok;
    }
    function body() {
      var l = labels[L()], sel = form.elements.perfil, perfilTxt = sel ? sel.options[sel.selectedIndex].text : '';
      var lines = [l.hi, '', l.nombre + ': ' + val('nombre')];
      if (val('empresa')) lines.push(l.empresa + ': ' + val('empresa'));
      lines.push(l.tel + ': ' + val('tel'));
      if (val('email')) lines.push(l.email + ': ' + val('email'));
      var soy = form.querySelector('input[name="soy"]:checked');
      if (soy) { var sl = form.querySelector('label[for="' + soy.id + '"] .l-' + L()); if (sl) lines.push(sl.textContent); }
      if (perfilTxt) lines.push(l.perfil + ': ' + perfilTxt);
      if (val('msg')) { lines.push(''); lines.push(l.msg + ': ' + val('msg')); }
      return lines.join('\n');
    }
    form.addEventListener('submit', function (e) { e.preventDefault(); });
    d.querySelectorAll('[data-send]').forEach(function (b) {
      b.addEventListener('click', function () {
        if (!check()) return;
        var how = b.getAttribute('data-send');
        if (how === 'wa') window.open('https://wa.me/' + cfg.wa + '?text=' + encodeURIComponent(body()), '_blank', 'noopener');
        else location.href = 'mailto:' + cfg.mail + '?subject=' + encodeURIComponent(labels[L()].subj) + '&body=' + encodeURIComponent(body());
      });
    });
    form.querySelectorAll('.field input').forEach(function (i) { i.addEventListener('input', function () { i.closest('.field').classList.remove('err'); }); });
  }

  /* botones que preseleccionan el perfil del formulario */
  d.querySelectorAll('[data-preselect]:not(form)').forEach(function (a) {
    a.addEventListener('click', function () {
      var f = d.querySelector('[data-contact-form]');
      if (f && f._setMode) f._setMode(a.getAttribute('data-preselect'));
      else if (f && f.perfil) f.perfil.value = a.getAttribute('data-preselect');
    });
  });

  /* enlaces de WhatsApp con mensaje según idioma */
  d.querySelectorAll('[data-wa]').forEach(function (a) {
    a.addEventListener('click', function () {
      a.href = 'https://wa.me/' + a.getAttribute('data-wa') + '?text=' + encodeURIComponent(a.getAttribute('data-' + L() + '-msg') || '');
    });
  });

  /* ---------- masterplan: lotes por tipología, ficha al pasar el mouse / tocar ---------- */
  d.querySelectorAll('.mp-int').forEach(function (fig) {
    var cfg = {}; try { cfg = JSON.parse(fig.getAttribute('data-mp')); } catch (e) { return; }
    var canvas = fig.querySelector('.mp-canvas'), tip = fig.querySelector('.mp-tip');
    var lots = fig.querySelectorAll('.lt'), keys = fig.querySelectorAll('.mp-key');
    var cur = null, pinned = null, stickyType = null;
    var nf = function (n) { return Math.round(n).toLocaleString(L() === 'en' ? 'en-US' : 'es-AR'); };
    var dec = function (n) { return L() === 'en' ? n.toFixed(2) : n.toFixed(2).replace('.', ','); };
    function fill(p) {
      var c = cfg[L()] || cfg.es, m2 = +p.getAttribute('data-m2'), ty = p.getAttribute('data-t');
      var col = getComputedStyle(p).getPropertyValue('--c');
      tip.innerHTML = '<div class="tp-h"><b>' + c.lot + ' ' + p.getAttribute('data-n') + '</b><span style="--c:' + col + '"><i></i>' + c.types[ty] + '</span></div>' +
        '<dl><dt>' + c.area + '</dt><dd>' + nf(m2) + ' m²</dd>' +
        '<dt>' + c.dims + '</dt><dd>' + p.getAttribute('data-f') + ' × ' + p.getAttribute('data-d') + ' m<small>' + c.front + ' × ' + c.depth + '</small></dd>' +
        '<dt>FOS</dt><dd>' + dec(cfg.fos) + '<small>' + c.upto + ' ' + nf(m2 * cfg.fos) + ' m²</small></dd>' +
        '<dt>FOT</dt><dd>' + dec(cfg.fot) + '<small>' + c.upto + ' ' + nf(m2 * cfg.fot) + ' m²</small></dd></dl>';
    }
    function place(x, y) {
      var r = canvas.getBoundingClientRect(), sr = canvas.parentNode.getBoundingClientRect(), lx = x - r.left, ly = y - r.top;
      var tw = tip.offsetWidth, th = tip.offsetHeight;
      var minX = Math.max(0, sr.left - r.left) + tw / 2 + 4, maxX = Math.min(r.width, sr.right - r.left) - tw / 2 - 4;
      lx = Math.max(minX, Math.min(maxX, lx));
      var below = ly - th - 20 < 0 || r.top + ly - th - 20 < 64;
      tip.classList.toggle('below', below);
      tip.style.left = lx + 'px'; tip.style.top = ly + 'px';
    }
    function show(p, x, y) {
      if (cur && cur !== p) cur.classList.remove('on');
      cur = p; p.classList.add('on'); fill(p);
      tip.hidden = false; place(x, y); tip.classList.add('show');
    }
    function hide() {
      if (cur) cur.classList.remove('on'); cur = null; pinned = null;
      tip.classList.remove('show'); tip.hidden = true;
    }
    lots.forEach(function (p) {
      p.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') show(p, e.clientX, e.clientY); });
      p.addEventListener('pointermove', function (e) { if (e.pointerType === 'mouse' && cur === p) place(e.clientX, e.clientY); });
      p.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse' && cur === p && !pinned) hide(); });
      p.addEventListener('click', function (e) {
        e.stopPropagation();
        if (pinned === p) { hide(); return; }
        var b = p.getBBox(), s = canvas.getBoundingClientRect(), vb = p.ownerSVGElement.viewBox.baseVal;
        var x = e.clientX || (s.left + (b.x + b.width / 2) / vb.width * s.width);
        var y = e.clientY || (s.top + (b.y + b.height / 2) / vb.height * s.height);
        show(p, x, y); pinned = p;
      });
    });
    d.addEventListener('click', function (e) { if (pinned && !fig.contains(e.target)) hide(); });
    canvas.addEventListener('click', function (e) { if (pinned && !e.target.closest('.lt')) hide(); });
    function focusType(ty) {
      fig.classList.toggle('focus', !!ty);
      lots.forEach(function (p) { p.classList.toggle('hl', !!ty && p.getAttribute('data-t') === ty); });
      keys.forEach(function (k) { k.classList.toggle('on', !!ty && k.getAttribute('data-type') === ty); });
    }
    keys.forEach(function (k) {
      var ty = k.getAttribute('data-type');
      k.addEventListener('mouseenter', function () { if (!stickyType) focusType(ty); });
      k.addEventListener('mouseleave', function () { if (!stickyType) focusType(null); });
      k.addEventListener('click', function () { stickyType = stickyType === ty ? null : ty; focusType(stickyType); });
    });
    d.querySelectorAll('[data-lang-btn]').forEach(function (b) { b.addEventListener('click', function () { if (cur) fill(cur); }); });
  });
})();
