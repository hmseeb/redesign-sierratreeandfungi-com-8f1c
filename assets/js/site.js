/* Sierra Tree & Fungi — site behaviour
   Vanilla JS, no dependencies. Everything degrades gracefully without JS. */
(function () {
  'use strict';

  /* ---------------------------------------------------------------- header */
  var head = document.querySelector('.site-head');
  if (head) {
    var onScroll = function () {
      head.classList.toggle('is-stuck', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* --------------------------------------------------------- desktop mega */
  var megaButtons = Array.prototype.slice.call(document.querySelectorAll('.nav-link[aria-controls]'));
  var closeAllMegas = function (except) {
    megaButtons.forEach(function (btn) {
      if (btn === except) return;
      var panel = document.getElementById(btn.getAttribute('aria-controls'));
      btn.setAttribute('aria-expanded', 'false');
      if (panel) panel.classList.remove('is-open');
    });
  };

  megaButtons.forEach(function (btn) {
    var panel = document.getElementById(btn.getAttribute('aria-controls'));
    if (!panel) return;
    var wrapper = btn.parentElement;
    var hoverTimer = null;

    var open = function () {
      closeAllMegas(btn);
      btn.setAttribute('aria-expanded', 'true');
      panel.classList.add('is-open');
    };
    var close = function () {
      btn.setAttribute('aria-expanded', 'false');
      panel.classList.remove('is-open');
    };

    btn.addEventListener('click', function (e) {
      e.preventDefault();
      if (btn.getAttribute('aria-expanded') === 'true') { close(); } else { open(); }
    });

    if (window.matchMedia('(hover: hover)').matches) {
      wrapper.addEventListener('mouseenter', function () {
        clearTimeout(hoverTimer);
        open();
      });
      wrapper.addEventListener('mouseleave', function () {
        hoverTimer = setTimeout(close, 160);
      });
    }

    panel.addEventListener('click', function (e) {
      if (e.target.closest('a')) close();
    });
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.has-sub')) closeAllMegas(null);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeAllMegas(null);
      if (burger && burger.getAttribute('aria-expanded') === 'true') toggleMobile(false);
    }
  });

  /* ---------------------------------------------------------- mobile menu */
  var burger = document.querySelector('.burger');
  var drawer = document.getElementById('mobileNav');

  function toggleMobile(open) {
    if (!burger || !drawer) return;
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    drawer.classList.toggle('is-open', open);
    document.documentElement.style.overflow = open ? 'hidden' : '';
  }

  if (burger && drawer) {
    burger.addEventListener('click', function () {
      toggleMobile(burger.getAttribute('aria-expanded') !== 'true');
    });
    drawer.addEventListener('click', function (e) {
      if (e.target.closest('a')) toggleMobile(false);
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 1080) toggleMobile(false);
    });
  }

  /* ------------------------------------------------------ table of contents */
  var toc = document.getElementById('pageToc');
  var article = document.querySelector('.prose');
  if (toc && article) {
    var headings = Array.prototype.slice.call(article.querySelectorAll('h2[id]'));
    if (headings.length > 2) {
      var ol = document.createElement('ol');
      headings.forEach(function (h) {
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.href = '#' + h.id;
        a.textContent = h.textContent;
        li.appendChild(a);
        ol.appendChild(li);
      });
      toc.appendChild(ol);
      toc.hidden = false;

      var links = Array.prototype.slice.call(ol.querySelectorAll('a'));
      if ('IntersectionObserver' in window) {
        var spy = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            links.forEach(function (l) {
              l.classList.toggle('is-active', l.getAttribute('href') === '#' + entry.target.id);
            });
          });
        }, { rootMargin: '-96px 0px -72% 0px', threshold: 0 });
        headings.forEach(function (h) { spy.observe(h); });
      }
    }
  }

  /* ------------------------------------------------------------- reveal in */
  var revealables = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function settle(el) {
    el.classList.remove('is-pending');
    el.classList.add('is-in');
  }

  if (revealables.length && 'IntersectionObserver' in window && !reduceMotion) {
    var pending = revealables.filter(function (el) {
      return el.getBoundingClientRect().top > window.innerHeight * 0.9;
    });
    pending.forEach(function (el) { el.classList.add('is-pending'); });

    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          settle(entry.target);
          obs.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.05 });
    pending.forEach(function (el) { io.observe(el); });

    /* Safety net: nothing stays hidden, whatever happens with scrolling. */
    window.setTimeout(function () {
      pending.forEach(function (el) {
        if (el.classList.contains('is-pending')) settle(el);
      });
    }, 1500);
  }

  /* ------------------------------------------------------------- forms */
  var CONFIRMATION = 'Thanks, your message was sent. I will get back to you shortly, usually the same day.';
  var forms = Array.prototype.slice.call(document.querySelectorAll('form[data-leadr]'));
  var submitted = /[?&]submitted=1(&|$)/.test(window.location.search);

  forms.forEach(function (form) {
    var pageField = form.querySelector('input[name="_page"]');
    if (pageField) pageField.value = window.location.href;

    var status = form.querySelector('.form-status');

    var show = function (message, isError) {
      if (!status) { if (isError) window.alert(message); return; }
      status.textContent = message;
      status.classList.add('is-visible');
      status.classList.toggle('is-error', !!isError);
    };

    if (submitted) {
      show(CONFIRMATION, false);
    }

    form.addEventListener('submit', function (e) {
      if (!window.fetch || !form.reportValidity) return; // let the plain POST happen
      if (!form.reportValidity()) return;
      e.preventDefault();

      var button = form.querySelector('button[type="submit"]');
      var label = button ? button.textContent : '';
      if (button) { button.disabled = true; button.textContent = 'Sending…'; }

      var payload = {};
      new FormData(form).forEach(function (value, key) { payload[key] = value; });
      payload._page = window.location.href;

      window.fetch(form.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function (res) { return res.json().catch(function () { return { ok: res.ok }; }); })
        .then(function (data) {
          if (data && data.ok) {
            form.reset();
            var pf = form.querySelector('input[name="_page"]');
            if (pf) pf.value = window.location.href;
            show(CONFIRMATION, false);
            if (status && status.scrollIntoView) status.scrollIntoView({ behavior: 'smooth', block: 'center' });
          } else {
            throw new Error('Submission failed');
          }
        })
        .catch(function () {
          show('Sorry, that did not go through. Please call or text (530) 391-6100 and I will pick it up from there.', true);
        })
        .then(function () {
          if (button) { button.disabled = false; button.textContent = label; }
        });
    });
  });

  /* Prefill the "Service needed" select from ?service= or the current page. */
  var select = document.querySelector('select[name="Service needed"]');
  if (select) {
    var slug = window.location.pathname.replace(/\/+$/, '').split('/').pop();
    var preset = document.body.getAttribute('data-service');
    var wanted = preset || slug;
    if (wanted) {
      Array.prototype.slice.call(select.options).forEach(function (opt) {
        if (opt.value && opt.value.toLowerCase() === String(wanted).toLowerCase()) select.value = opt.value;
      });
    }
  }
})();
