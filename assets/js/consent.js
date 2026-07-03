(function(){
  var CONSENT_KEY = 'aisearch_consent';

  function loadQuantcast(){
    if(window._qevents) return;
    window._qevents = [];
    var elem = document.createElement('script');
    elem.src = (document.location.protocol == 'https:' ? 'https://secure' : 'http://edge') + '.quantserve.com/quant.js';
    elem.async = true;
    elem.type = 'text/javascript';
    var scpt = document.getElementsByTagName('script')[0];
    scpt.parentNode.insertBefore(elem, scpt);
    window._qevents.push({ qacct: 'p-dCP3ZrYDcXUbx' });
  }

  function getConsent(){
    try { return localStorage.getItem(CONSENT_KEY); } catch(e){ return null; }
  }

  function setConsent(value){
    try { localStorage.setItem(CONSENT_KEY, value); } catch(e){}
    hideBanner();
    if(value === 'accepted') loadQuantcast();
  }

  function hideBanner(){
    var b = document.getElementById('cookie-consent-banner');
    if(b) b.remove();
  }

  function showBanner(){
    var css = document.createElement('style');
    css.textContent =
      '#cookie-consent-banner{position:fixed;left:0;right:0;bottom:0;z-index:9999;'+
      'background:#15181d;border-top:1px solid rgba(255,255,255,.12);color:#e3e8ee;'+
      'padding:1rem 1.25rem;display:flex;flex-wrap:wrap;gap:.85rem;align-items:center;'+
      'justify-content:center;font:15px/1.5 "DM Sans",system-ui,sans-serif}'+
      '#cookie-consent-banner p{margin:0;flex:1 1 320px;min-width:200px;color:#95a0ad}'+
      '#cookie-consent-banner a{color:#0abab5;text-decoration:underline}'+
      '#cookie-consent-banner .cc-actions{display:flex;gap:.6rem;flex-wrap:wrap}'+
      '#cookie-consent-banner button{border-radius:0;padding:.55rem 1.1rem;font-size:.85rem;'+
      'cursor:pointer;font-weight:600;font-family:inherit}'+
      '#cookie-consent-banner .cc-accept{background:#0abab5;color:#000;border:1px solid #0abab5}'+
      '#cookie-consent-banner .cc-decline{background:transparent;color:#e3e8ee;border:1px solid rgba(255,255,255,.3)}';
    document.head.appendChild(css);

    var wrap = document.createElement('div');
    wrap.id = 'cookie-consent-banner';
    wrap.setAttribute('role', 'dialog');
    wrap.setAttribute('aria-label', 'Cookie consent');
    wrap.innerHTML =
      '<p>We use cookies to measure ad performance (Quantcast). See our <a href="/privacy/">privacy policy</a>.</p>'+
      '<div class="cc-actions">'+
      '<button type="button" class="cc-decline">Decline</button>'+
      '<button type="button" class="cc-accept">Accept</button>'+
      '</div>';
    document.body.appendChild(wrap);

    wrap.querySelector('.cc-accept').addEventListener('click', function(){ setConsent('accepted'); });
    wrap.querySelector('.cc-decline').addEventListener('click', function(){ setConsent('declined'); });
  }

  var stored = getConsent();
  if(stored === 'accepted'){
    loadQuantcast();
  } else if(stored !== 'declined'){
    showBanner();
  }
})();
