(function () {
  /* ── Shared header ── */
  var H = '<div class="container nav">'
    + '<a href="/" class="brand" aria-label="AISearch Global home">'
    + '<img src="/assets/images/logos/header-logo.svg" alt="AISearch Global" loading="eager" decoding="async" style="height:34px;width:auto;max-width:260px;display:block">'
    + '</a>'
    + '<button class="nav-toggle" id="menuBtn" aria-controls="siteNav" aria-expanded="false">Menu</button>'
    + '<ul id="siteNav" class="nav-links links">'
    + '<li><a href="/#what">What is AI Visibility</a></li>'
    + '<li><a href="/#services">Services</a></li>'
    + '<li><a href="/about/">About</a></li>'
    + '<li><a href="/insights/">Insights</a></li>'
    + '<li><a href="/#contact" class="cta-link">Check Visibility</a></li>'
    + '</ul></div>';

  var header = document.querySelector('header');
  if (header) header.innerHTML = H;

  /* ── Shared footer ── */
  var F = '<div class="container">'
    + '<div>&copy; 2026 AISearch Global | Sydney | NSW | Australia</div>'
    + '<div class="footer-links">'
    + '<a href="/insights/">Insights</a>'
    + '<a href="/about/">About</a>'
    + '<a href="/#services">Services</a>'
    + '<a href="/#faq">FAQ</a>'
    + '<a href="/privacy/">Privacy</a>'
    + '<a href="/terms/">Terms</a>'
    + '<a href="/#contact">Contact</a>'
    + '</div>'
    + '<div class="social-links" style="display:flex;gap:.75rem;flex-wrap:wrap;margin-top:.75rem">'
    + '<a href="https://www.facebook.com/aisearch.global" aria-label="Facebook" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><i class="bi bi-facebook"></i></a>'
    + '<a href="https://www.instagram.com/aisearch.global/" aria-label="Instagram" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><i class="bi bi-instagram"></i></a>'
    + '<a href="https://www.threads.net/@aisearch.global" aria-label="Threads" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><i class="bi bi-threads"></i></a>'
    + '<a href="https://www.linkedin.com/company/ai-search-global/" aria-label="LinkedIn" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><i class="bi bi-linkedin"></i></a>'
    + '<a href="https://x.com/aisearch_global" aria-label="X" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><i class="bi bi-twitter-x"></i></a>'
    + '<a href="https://www.youtube.com/@aisearch.global" aria-label="YouTube" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><i class="bi bi-youtube"></i></a>'
    + '<a href="https://au.pinterest.com/aisearch_global/" aria-label="Pinterest" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><i class="bi bi-pinterest"></i></a>'
    + '<a href="https://www.tiktok.com/@aisearch.global" aria-label="TikTok" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><i class="bi bi-tiktok"></i></a>'
    + '<a href="https://www.google.com/maps/place/AISearch+Global/@-34.0511229,150.7699384,17z/data=!3m1!4b1!4m6!3m5!1s0x6b12efbcf56f819f:0xb9ebe1179a042329!8m2!3d-34.0511229!4d150.7699384!16s%2Fg%2F11zbqjqkfp" aria-label="Google Maps" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><i class="bi bi-geo-alt-fill"></i></a>'
    + '</div></div>';

  var footer = document.querySelector('footer');
  if (footer) footer.innerHTML = F;

  /* ── Mobile nav toggle ── */
  var btn = document.getElementById('menuBtn');
  var nav = document.getElementById('siteNav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var x = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!x));
      nav.classList.toggle('open');
    });
    nav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        nav.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ── GA event tracking ── */
  document.querySelectorAll('[data-track]').forEach(function (el) {
    el.addEventListener('click', function () {
      if (typeof gtag === 'function') {
        gtag('event', 'click', { event_category: 'engagement', event_label: el.getAttribute('data-track') });
      }
    });
  });
  document.querySelectorAll('[data-track-form]').forEach(function (f) {
    f.addEventListener('submit', function () {
      if (typeof gtag === 'function') {
        gtag('event', 'generate_lead', { event_category: 'conversion', event_label: f.getAttribute('data-track-form') });
      }
    });
  });
})();
