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
      + 'footer .social-links a{color:rgba(255,255,255,.8);text-decoration:none}'
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
      + '<li><a href="/faq.html">FAQ</a></li>'
      + '<li><a href="/aeo-score-calculator.html" class="cta-link">AEO Score Calculator</a></li>'
      + '</ul></div>';

   var header = document.querySelector('header');
    if (header) header.innerHTML = H;

   /* ── Shared footer ── */
   var F = '<div class="container">'
      + '<div>&copy; 2026 AISearch Global | Sydney | NSW | Australia</div>'
      + '<div style="margin-top:.35rem;font-size:.8rem;opacity:1;color:rgba(255,255,255,.7)">Watkins Crescent, Currans Hill NSW 2567, Australia &nbsp;|&nbsp; ABN 13 490 201 041 &nbsp;|&nbsp; <a href="tel:+61240192419" style="color:inherit;text-decoration:none">02 4019 2419</a> &nbsp;|&nbsp; <a href="mailto:hello@aisearch.global" style="color:inherit;text-decoration:none">hello@aisearch.global</a></div>'
      + '<div class="footer-links">'
      + '<a href="/insights/">Insights</a>'
      + '<a href="/about/">About</a>'
      + '<a href="/services/">Services</a>'
      + '<a href="/faq.html">FAQ</a>'
      + '<a href="/privacy/">Privacy</a>'
      + '<a href="/terms/">Terms</a>'
      + '<a href="/#contact">Contact</a>'
      + '</div>'
      + '<div class="social-links" style="display:flex;gap:.75rem;flex-wrap:wrap;margin-top:.75rem">'
      + '<a href="https://www.facebook.com/aisearch.global" aria-label="Facebook" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg></a>'
      + '<a href="https://www.instagram.com/aisearch.global/" aria-label="Instagram" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" fill="none" stroke="currentColor" stroke-width="2"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5" stroke="currentColor" stroke-width="2"/></svg></a>'
      + '<a href="https://www.threads.net/@aisearch.global" aria-label="Threads" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.186 24h-.007c-3.581-.024-6.334-1.205-8.184-3.509C2.35 18.44 1.5 15.586 1.472 12.01v-.017c.028-3.579.879-6.43 2.525-8.482C5.845 1.205 8.6.024 12.18 0h.014c2.746.02 5.043.725 6.826 2.098 1.677 1.29 2.858 3.13 3.509 5.467l-2.04.569c-1.104-3.96-3.898-5.984-8.304-6.015-2.91.022-5.11.936-6.54 2.717C4.307 6.504 3.616 8.914 3.589 12c.027 3.086.718 5.496 2.057 7.164 1.43 1.783 3.631 2.698 6.54 2.717 1.593-.012 2.999-.264 4.088-.96 1.443-.934 2.17-2.446 2.286-4.553l.013-.281H12.42v-2.022h8.317l-.004.498c-.023 2.411-.73 4.306-2.1 5.636-1.24 1.2-2.99 1.85-5.16 1.93z"/></svg></a>'
      + '<a href="https://www.linkedin.com/company/ai-search-global/" aria-label="LinkedIn" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z"/><circle cx="4" cy="4" r="2"/></svg></a>'
      + '<a href="https://x.com/aisearch_global" aria-label="X" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.259 5.63zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg></a>'
      + '<a href="https://www.youtube.com/@aisearch.global" aria-label="YouTube" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.95-1.96C18.88 4 12 4 12 4s-6.88 0-8.59.46a2.78 2.78 0 0 0-1.95 1.96A29 29 0 0 0 1 12a29 29 0 0 0 .46 5.58A2.78 2.78 0 0 0 3.41 19.6C5.12 20 12 20 12 20s6.88 0 8.59-.4a2.78 2.78 0 0 0 1.95-1.95A29 29 0 0 0 23 12a29 29 0 0 0-.46-5.58z"/><polygon points="9.75 15.02 15.5 12 9.75 8.98 9.75 15.02" fill="#fff"/></svg></a>'
      + '<a href="https://au.pinterest.com/aisearch_global/" aria-label="Pinterest" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 0 1 .083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z"/></svg></a>'
      + '<a href="https://www.tiktok.com/@aisearch.global" aria-label="TikTok" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-2.88 2.5 2.89 2.89 0 0 1-2.89-2.89 2.89 2.89 0 0 1 2.89-2.89c.28 0 .54.04.79.1V9.01a6.27 6.27 0 0 0-.79-.05 6.34 6.34 0 0 0-6.34 6.34 6.34 6.34 0 0 0 6.34 6.34 6.34 6.34 0 0 0 6.33-6.34v-7a8.16 8.16 0 0 0 4.77 1.52V6.4a4.85 4.85 0 0 1-1-.29z"/></svg></a>'
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
