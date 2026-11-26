/* AI Thought Partner checkout: terms box opens on click. */
(function(){
  document.addEventListener('click',function(e){
    var t=e.target.closest&&e.target.closest('.service-agreement-text');
    if(t&&!t.classList.contains('wtr-open'))t.classList.add('wtr-open');
  });
})();

/* WTR: optional mobile label + texting consent under the checkout phone field */
(function(){
  var T='Mobile number is optional. If you add it, you agree to get texts from Wreck the Room about your purchase and Jody’s work. Msg frequency varies. Msg & data rates may apply. Reply STOP to opt out, HELP for help. Consent is not a condition of purchase.';
  function add(){
    var p=document.getElementById('custom_35')||document.getElementById('phone');
    if(!p||document.querySelector('.wtr-sms-note'))return;
    p.setAttribute('placeholder','Mobile number (optional)');
    if(p.labels&&p.labels[0])p.labels[0].textContent='Mobile number (optional)';
    var n=document.createElement('p');n.className='wtr-sms-note';n.textContent=T;
    n.style.cssText='margin:6px 0 0;font:400 12px/1.5 Manrope,system-ui,sans-serif;color:#4a4232;';
    var f=p.closest('.sage-input')||p.parentNode;f.parentNode.insertBefore(n,f.nextSibling);
  }
  add();
  try{new MutationObserver(add).observe(document.documentElement,{childList:true,subtree:true});}catch(e){}
})();