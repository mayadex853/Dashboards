/* Wreck The Room™ checkout: brand bar, headline and three steps above Kajabi's checkout; terms box opens on click. */
(function(){
  function top(){
    var co=document.querySelector('.kjb-embedded-checkout');
    if(!co||document.querySelector('.wtr-co-top'))return;
    var d=document.createElement('div');d.className='wtr-co-top';
    d.innerHTML='<div class="wtr-co-bar"><a href="https://www.wrecktheroom.com/"><img src="https://kajabi-storefronts-production.kajabi-cdn.com/kajabi-storefronts-production/file-uploads/themes/2162751237/settings_images/47ed02-ebc5-250f-cdd2-17c278b4e31_JODY_LOGO_smaller.png" alt="Jody Friedman"></a>'
      +'<span class="wtr-co-lock"><svg viewBox="0 0 24 24"><rect x="5" y="11" width="14" height="10" rx="1"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>Secure checkout</span></div>'
      +'<div class="wtr-co-head"><small>Wreck The Room™</small><h1>You’re one step <em>away.</em></h1></div>'
      +'<ol class="wtr-co-steps"><li><b>1</b>Enter your email &amp; name</li><li><b>2</b>Choose how to pay</li><li><b>3</b>Get instant access by email</li></ol>';
    co.parentNode.insertBefore(d,co);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',top);else top();
  document.addEventListener('click',function(e){
    var t=e.target.closest&&e.target.closest('.service-agreement-text');
    if(t&&!t.classList.contains('wtr-open'))t.classList.add('wtr-open');
  });
})();

/* launch pricing sticker + strikethrough prices */
window.WTR_WAS={"3,500": "5,000", "1,877": "2,650"};(function(){var s=document.createElement('script');s.src='https://cdn.jsdelivr.net/gh/mayadex853/Dashboards@__SHA__/wtr-homepage/checkout-launch/launch.js';document.head.appendChild(s);})();
