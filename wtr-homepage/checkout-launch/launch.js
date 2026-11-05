
/* launch pricing: sticker + struck-through regular prices (re-applied when Kajabi re-renders the checkout) */
(function(){
  var WAS=window.WTR_WAS||{};var st=document.createElement("style");st.textContent="\n/* launch pricing: sticker on the card corner + struck-through regular prices */\n.kjb-embedded-checkout{position:relative !important;overflow:visible !important;}\n.wtr-sticker{position:absolute;top:-38px;right:-12px;z-index:30;width:124px;height:124px;border-radius:50%;\n  background:radial-gradient(circle at 34% 28%,#ef5b4b,#c21f1f 62%,#8f1414);border:3px solid #ecd69b;color:#fff;\n  display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;line-height:1;\n  transform:rotate(-12deg);box-shadow:0 12px 28px rgba(0,0,0,.5);font-family:Anton,Impact,sans-serif;text-transform:uppercase;pointer-events:none;\n  animation:wtrPop .6s cubic-bezier(.2,1.4,.4,1) both;}\n.wtr-sticker::before{content:\"\";position:absolute;inset:7px;border-radius:50%;border:1.5px dashed rgba(255,255,255,.65);}\n.wtr-sticker span{font-size:15px;letter-spacing:.14em;}\n.wtr-sticker b{font-size:27px;font-weight:400;letter-spacing:.02em;margin-top:2px;}\n.wtr-sticker i{font:700 9px/1 Manrope,system-ui,sans-serif;font-style:normal;letter-spacing:.2em;margin-top:6px;color:#ecd69b;}\n@keyframes wtrPop{from{transform:rotate(-30deg) scale(.4);opacity:0}to{transform:rotate(-12deg) scale(1);opacity:1}}\n.wtr-was{display:inline-block;margin-left:8px;font-weight:600;color:#8a7f6a !important;text-decoration:line-through;text-decoration-color:#d8483b;text-decoration-thickness:2px;}\n.wtr-was-big{display:block;font:700 12px/1.2 Manrope,system-ui,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:#c21f1f !important;margin-bottom:4px;}\n.wtr-was-big s{color:#8a7f6a;margin-left:6px;text-decoration-color:#d8483b;text-decoration-thickness:2px;letter-spacing:.04em;font-size:15px;}\n@media (max-width:767px){.wtr-sticker{width:92px;height:92px;top:-26px;right:-4px;}.wtr-sticker span{font-size:11px;}.wtr-sticker b{font-size:20px;}.wtr-sticker i{font-size:7px;}}\n";document.head.appendChild(st);
  function was(t){for(var k in WAS){if(t.indexOf('$'+k)>-1)return WAS[k];}return null;}
  function apply(){
    var co=document.querySelector('.kjb-embedded-checkout');
    if(co&&!co.querySelector('.wtr-sticker')){var s=document.createElement('div');s.className='wtr-sticker';s.setAttribute('aria-hidden','true');
      s.innerHTML='<span>Launch</span><b>Pricing</b><i>Limited time</i>';co.appendChild(s);}
    var p=document.getElementById('offer-price');
    if(p&&!(p.previousElementSibling&&p.previousElementSibling.classList.contains('wtr-was-big'))){var w=was(p.textContent);
      if(w){var d=document.createElement('span');d.className='wtr-was-big';d.innerHTML='Launch pricing <s>$'+w+'</s>';p.parentNode.insertBefore(d,p);}}
    document.querySelectorAll('.embedded-checkout-pricing-option p.description').forEach(function(el){
      if(el.querySelector('.wtr-was'))return;var w=was(el.textContent);
      if(w){var x=document.createElement('s');x.className='wtr-was';x.textContent='$'+w;el.appendChild(x);}
    });
  }
  var q=0;function later(){if(!q)q=setTimeout(function(){q=0;apply();},120);}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',apply);else apply();
  new MutationObserver(later).observe(document.documentElement,{childList:true,subtree:true});
})();
