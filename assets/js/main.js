/* ── Amplitude Analytics (EU region, CDN init) ── */
(function(e,t){var n=e.amplitude||{_q:[],_iq:{}};if(n.invoked){e.console&&console.error&&console.error("Amplitude snippet has been loaded.");return}n.invoked=true;var s=t.createElement("script");s.type="text/javascript";s.integrity="sha384-XNX6U2ua04l5JNPk8racSkagg14UYkjDin4RpBnpRNMeRKBgeNWJ7H8R28LpEDM";s.crossOrigin="anonymous";s.async=true;s.src="https://cdn.amplitude.com/libs/analytics-browser-2.11.5-min.js.gz";s.onload=function(){if(!e.amplitude.runQueuedFunctions){console.log("[Amplitude] Error: could not load SDK")}};var r=t.getElementsByTagName("script")[0];r.parentNode.insertBefore(s,r);function i(e,t){e.prototype[t]=function(){e._q&&e._q.push([t].concat(Array.prototype.slice.call(arguments,0)));return this}}var o=function(){this._q=[];return this};var a=["add","append","clearAll","prepend","set","setOnce","unset","preInsert","postInsert","remove","getUserProperties"];for(var c=0;c<a.length;c++){i(o,a[c])}n.Identify=o;var l=function(){this._q=[];return this};var u=["getEventProperties","setProductId","setQuantity","setPrice","setRevenue","setRevenueType","setEventProperties"];for(var p=0;p<u.length;p++){i(l,u[p])}n.Revenue=l;var d=["getDeviceId","setDeviceId","getSessionId","setSessionId","getUserId","setUserId","setOptOut","setTransport","reset"];for(var v=0;v<d.length;v++){(function(t){n[t]=function(){n._q.push([t].concat(Array.prototype.slice.call(arguments,0)));return n}})(d[v])}n.init=function(e,t,o,r){n._q.push(["init",e,t,o,r]);return n};n.track=function(e,t,o){n._q.push(["track",e,t,o]);return n};n.logEvent=function(e,t,o){n._q.push(["logEvent",e,t,o]);return n};n.identify=function(e,t){n._q.push(["identify",e,t]);return n};n.groupIdentify=function(e,t,n,r){n._q&&n._q.push(["groupIdentify",e,t,n,r]);return n};n.setGroup=function(e,t,n){n._q.push(["setGroup",e,t,n]);return n};n.revenue=function(e,t){n._q.push(["revenue",e,t]);return n};n.add=function(e){n._q.push(["add",e]);return n};n.snippet={version:"2.11.5",iife:false};e.amplitude=n})(window,document);

amplitude.init('3c57360b46002d54e4911e690e1198c3', {
  serverUrl: 'https://api.eu.amplitude.com/2/httpapi', // EU data residency
  autocapture: {
    attribution: true,             // UTM / referrer attribution events
    pageViews: true,               // SPA route changes + initial load
    sessions: true,                // Session start / end events
    formInteractions: true,        // Form starts + submits
    fileDownloads: true,           // Downloads of common file types
    elementInteractions: true,     // Click + change on instrumented els
    frustrationInteractions: true, // Rage clicks, dead clicks
    pageUrlEnrichment: true,       // Adds path / search to event props
  },
});

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
      + '<li><a href="/services/">Services</a></li>'
      + '<li><a href="/insights/">Insights</a></li>'
      + '<li><a href="/resources/">Resources</a></li>'
      + '<li><a href="/about/">About</a></li>'
      + '<li><a href="/faq">FAQ</a></li>'
      + '<li><a href="/#contact" class="cta-link">Book an Audit</a></li>'
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
