/* vISIon: minimal behaviour. No frameworks, no build step. */
(function () {
  'use strict';

  // ====================================================================
  // ANALYTICS. Set this to your GoatCounter code and analytics turn on
  // across the whole site. Leave it empty and nothing is loaded at all:
  // no script, no request, no cookie.
  //
  // If your dashboard is at https://isi-vision.goatcounter.com, then the
  // code is: isi-vision
  // ====================================================================
  var GOATCOUNTER_CODE = 'isi-vision';

  if (GOATCOUNTER_CODE) {
    var gc = document.createElement('script');
    gc.async = true;
    gc.src = 'https://gc.zgo.at/count.js';
    gc.setAttribute('data-goatcounter',
      'https://' + GOATCOUNTER_CODE + '.goatcounter.com/count');
    document.head.appendChild(gc);
  }

  // Mobile navigation
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });

    // Close the menu when a link is followed
    nav.addEventListener('click', function (event) {
      if (event.target.tagName === 'A') {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.setAttribute('aria-label', 'Open menu');
      }
    });

    // Close on Escape
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && nav.classList.contains('open')) {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  // Keep the copyright year current
  var years = document.querySelectorAll('[data-year]');
  for (var i = 0; i < years.length; i++) {
    years[i].textContent = new Date().getFullYear();
  }

  // ---- Contact form -------------------------------------------------
  // Submits without leaving the page. If JavaScript is off, the form
  // still posts normally to the provider, so nothing is lost.
  var form = document.getElementById('contact-form');
  if (form) {
    var status  = document.getElementById('cf-status');
    var button  = document.getElementById('cf-submit');
    var topic   = document.getElementById('cf-topic');
    var subject = document.getElementById('cf-subject');

    // Deep link: contact.html?topic=pitch preselects the reason
    var wanted = new URLSearchParams(location.search).get('topic');
    var map = {
      pitch: 'Pitch an article',
      letter: 'Letter to the editor',
      correction: 'Correction',
      board: 'Join the editorial board'
    };
    if (wanted && map[wanted]) topic.value = map[wanted];

    function syncSubject() { subject.value = 'vISIon: ' + topic.value; }
    topic.addEventListener('change', syncSubject);
    syncSubject();

    function say(message, kind) {
      status.textContent = message;
      status.className = 'form-status ' + kind;
    }

    form.addEventListener('submit', function (event) {
      if (form.action.indexOf('REPLACE_WITH_YOUR_FORM_ID') !== -1) {
        event.preventDefault();
        say('This form is not connected yet. Please write to the editors through the ISI in the meantime.', 'is-error');
        return;
      }
      event.preventDefault();
      button.disabled = true;
      say('Sending\u2026', '');

      fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' }
      }).then(function (response) {
        if (response.ok) {
          form.reset();
          syncSubject();
          say('Thank you. Your message is on its way to the editors, and you should hear back before long.', 'is-ok');
        } else {
          say('Something went wrong at our end and the message was not sent. Please try again in a moment.', 'is-error');
        }
      }).catch(function () {
        say('The message could not be sent. Please check your connection and try again.', 'is-error');
      }).then(function () {
        button.disabled = false;
      });
    });
  }

  // ---- Count reads of each issue -------------------------------------
  // Fires a "download" event when someone opens an issue PDF, so that
  // reads can be counted alongside page views. Silent if no analytics
  // provider is loaded.
  document.addEventListener('click', function (event) {
    var link = event.target.closest ? event.target.closest('a[href$=".pdf"], a[href*=".pdf#"]') : null;
    if (!link) return;
    var name = link.getAttribute('href').split('/').pop().split('#')[0];
    if (window.goatcounter && window.goatcounter.count) {
      window.goatcounter.count({ path: 'pdf/' + name, title: 'Issue PDF: ' + name, event: true });
    } else if (typeof window.gtag === 'function') {
      window.gtag('event', 'file_download', { file_name: name, file_extension: 'pdf' });
    }
  });
})();
