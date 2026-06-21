(function () {
    /* ── Shared header/footer styling (self-contained so injected markup renders consistently on every page) ── */
   var S = document.createElement('style');
    S.textContent =
          'footer{border-top:1px solid rgba(255,255,255,.12);padding:1.5rem 0;margin-top:2rem}'
      + 'footer .container{text-align:center}'
      + 'footer .footer-links{display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;margin-top:.5rem}'
      + 'footer .footer-links a{text-decoration:none;color:inherit;opacity:.7;font-size:.9rem}'
      + 'footer .footer-links a:hover{opacity:1;color:#0abab5}'
      + 'footer .social-links{justify-content:center}'
      + 'footer .social-links a{color:rgba(255,255,255,.8);text-decoration:none;font-size:1.2rem}'
      + 'footer .social-links a:hover{color:#0abab5}'
      + 'header .nav-links a,header .links a{text-decoration:none}'
      + 'header .brand{text-decoration:none;display:inline-flex;align-items:center}'
      + 'header .brand img{display:block;height:34px;width:auto;max-width:260px}';
    document.head.appendChild(S);   var L=document.createElement('link');L.rel='stylesheet';L.href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css';document.head.appendChild(L);

   /* ── Shared header ── */
   var H = '<div class="container nav">'
      + '<a href="/" class="brand" aria-label="AISearch Global home"><img src="/assets/images/logos/header-logo.svg" alt="AISearch Global" width="200" height="34"></a>'
      + '<button class="nav-toggle" id="menuBtn" aria-controls="siteNav" aria-expanded="false">Menu</button>'
      + '<ul id="siteNav" class="nav-links links">'
      + '<li><a href="/#what">What is AI Visibility</a></li>'
      + '<li><a href="/services/">Services</a></li>'
      + '<li><a href="/about/">About</a></li>'
      + '<li><a href="/insights/">Insights</a></li>'
      + '<li><a href="/faq">FAQ</a></li>'
      + '<li><a href="/aeo-score-calculator" class="cta-link">AEO Score Calculator</a></li>'
      + '</ul></div>';

   var header = document.querySelector('header');
    if (header) header.innerHTML = H;

   /* ── Shared footer ── */
   var F = '<div class="container">'
      + '<div style="font-size:.8rem;opacity:1;color:rgba(255,255,255,.7)">&copy; 2026 AISearch Global &nbsp;|&nbsp; Sydney, NSW, Australia &nbsp;|&nbsp; ABN 13 490 201 041 &nbsp;|&nbsp; <a href="tel:+61240192419" style="color:inherit;text-decoration:none">+61 2 4019 2419</a> &nbsp;|&nbsp; <a href="mailto:hello@aisearch.global" style="color:inherit;text-decoration:none">hello@aisearch.global</a></div>'
      + '<div class="footer-links">'
      + '<a href="/insights/">Insights</a>'
      + '<a href="/about/">About</a>'
      + '<a href="/services/">Services</a>'
      + '<a href="/faq">FAQ</a>'
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
