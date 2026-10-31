/* Wreck The Room™ site header, shared by the custom Kajabi pages.
   Include it where the header should sit:
     <script src=".../wtr-homepage/live/header.js" data-btn="Take the quiz" data-href="https://quiz.wrecktheroom.com"></script>
   data-kbook on the script adds data-k-book to the button (pages that open the Kajabi booking popup).
   data-solid keeps the dark bar on from the top (pages with a light or plain first section).
   Desktop: logo left, links centered (plus a "More" dropdown), button far right. Below 1100px the links move into the hamburger menu.
   Every rule is scoped to #wtr-site-hd with !important where Kajabi theme styles would otherwise win. */
(function(){
  var s=document.currentScript||{dataset:{}};
  var d=s.dataset||{};
  var btn=d.btn||'Take the quiz', href=d.href||'https://quiz.wrecktheroom.com';
  var W='https://www.wrecktheroom.com';
  var main=[['About','/about'],['Speaking','/speaker2'],['Wreck The Room&trade;','/rebuild'],['Work With Me','/coaching']];
  var more=[['Testimonials','/testimonials'],['Credits','/credits'],['Blog','/blog']];
  var a=function(l){return '<a href="'+W+l[1]+'">'+l[0]+'</a>';};
  var I='#wtr-site-hd';
  var css='html{scroll-padding-top:96px}'
   +I+','+I+' *{box-sizing:border-box !important;margin:0;font-family:Manrope,system-ui,-apple-system,"Segoe UI",sans-serif !important}'
   +I+'{position:fixed !important;top:0;left:0;right:0;z-index:900;display:grid !important;grid-template-columns:1fr auto 1fr;align-items:center;column-gap:24px;padding:20px 32px !important;background:transparent;font-size:12px !important;font-weight:600 !important;line-height:1 !important;letter-spacing:.2em !important;text-transform:uppercase !important;transition:background .35s,padding .35s,box-shadow .35s}'
   +I+'.sc{background:rgba(10,9,8,.94) !important;padding-top:12px !important;padding-bottom:12px !important;box-shadow:0 1px 0 rgba(201,168,76,.22)}'
   +I+' .lg{justify-self:start;display:block;line-height:0}'
   +I+' .lg img{width:150px !important;max-width:none !important;height:auto !important;display:block !important;transition:width .35s}'+I+'.sc .lg img{width:124px !important}'
   +I+' nav{justify-self:center;display:flex !important;flex-direction:row;gap:30px;align-items:center;padding:0 !important;background:none;border:0;position:static}'
   +I+' a{color:#d9d2c4 !important;text-decoration:none !important;white-space:nowrap;font-size:inherit !important;font-weight:inherit !important;letter-spacing:inherit !important;text-transform:inherit !important;line-height:1 !important;background:none !important;border:0;padding:0;box-shadow:none !important}'
   +I+' nav a:hover{color:#ecd69b !important}'
   +I+' .r{justify-self:end;display:flex !important;align-items:center;gap:10px}'
   +I+' .bk{border:1px solid #c9a84c !important;color:#ecd69b !important;padding:14px 20px !important}'
   +I+' .mo{position:relative;display:block}'
   +I+' .mo>button{all:unset;cursor:pointer;display:flex !important;align-items:center;gap:7px;padding:8px 0;color:#d9d2c4 !important;font:inherit !important;letter-spacing:inherit !important;text-transform:uppercase !important;line-height:1 !important}'
   +I+' .mo>button:hover,'+I+' .mo.open>button{color:#ecd69b !important}'
   +I+' .mo>button i{display:block;width:7px;height:7px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:translateY(-2px) rotate(45deg);transition:transform .25s}'
   +I+' .mo.open>button i{transform:translateY(1px) rotate(-135deg)}'
   +I+' .dd{position:absolute !important;top:calc(100% + 14px);left:50%;margin-left:-95px;width:190px;padding:10px 0 !important;background:rgba(10,9,8,.97) !important;border:1px solid rgba(201,168,76,.35) !important;box-shadow:0 18px 40px rgba(0,0,0,.5);display:flex !important;flex-direction:column;opacity:0;visibility:hidden;transform:translateY(-6px);transition:opacity .2s,transform .2s,visibility .2s;z-index:2}'
   +I+' .dd::before{content:"";position:absolute;left:0;right:0;top:-16px;height:16px}'
   +I+' .dd a{display:block !important;padding:13px 22px !important}'+I+' .dd a:hover{background:rgba(201,168,76,.1) !important}'
   +I+' .mo.open .dd{opacity:1;visibility:visible;transform:none}'
   +'@media(hover:hover) and (min-width:1101px){'+I+' .mo:hover .dd{opacity:1;visibility:visible;transform:none}}'
   +I+' .mb{all:unset;display:none !important;cursor:pointer;position:relative;width:40px;height:38px;border:1px solid rgba(201,168,76,.45) !important;box-sizing:border-box !important}'
   +I+' .mb i{position:absolute;left:10px;right:10px;height:1.5px;background:#ecd69b;transition:transform .3s,opacity .3s}'
   +I+' .mb i:nth-child(1){top:12px}'+I+' .mb i:nth-child(2){top:18px}'+I+' .mb i:nth-child(3){top:24px}'
   +I+'.open .mb i:nth-child(1){transform:translateY(6px) rotate(45deg)}'+I+'.open .mb i:nth-child(2){opacity:0}'+I+'.open .mb i:nth-child(3){transform:translateY(-6px) rotate(-45deg)}'
   +'@media(max-width:1260px){'+I+' nav{gap:20px;letter-spacing:.14em}'+I+'{column-gap:16px}'+I+' .bk{padding:12px 14px !important}}'
   +'@media(max-width:1100px){'+I+'{grid-template-columns:auto 1fr;padding:14px 20px !important}'+I+'.sc{padding-top:10px !important;padding-bottom:10px !important}'
   +I+' .lg img,'+I+'.sc .lg img{width:116px !important}'+I+' .mb{display:block !important}'+I+' .bk{padding:11px 12px !important;font-size:10px !important}'
   +I+' nav{position:fixed !important;top:0;left:0;right:0;bottom:0;z-index:-1;flex-direction:column !important;justify-content:center;gap:28px;background:#0a0908 !important;font-size:15px !important;letter-spacing:.24em !important;opacity:0;visibility:hidden;transition:opacity .3s,visibility .3s;overflow-y:auto}'
   +I+'.open nav{opacity:1;visibility:visible}'
   +I+' .mo{display:contents !important}'+I+' .mo>button{display:none !important}'
   +I+' .dd{position:static !important;display:contents !important;opacity:1;visibility:visible;transform:none;background:none !important;border:0 !important;box-shadow:none;padding:0 !important;width:auto;margin:0}'+I+' .dd::before{display:none}'+I+' .dd a{padding:0 !important}'+I+' .dd a:hover{background:none !important}}';
  var html='<style>'+css+'</style><div class="wtr-hd" id="wtr-site-hd"><a class="lg" href="'+W+'/"><img src="https://kajabi-storefronts-production.kajabi-cdn.com/kajabi-storefronts-production/file-uploads/themes/2162751237/settings_images/47ed02-ebc5-250f-cdd2-17c278b4e31_JODY_LOGO_smaller.png" alt="Jody Friedman"></a>'
   +'<nav aria-label="Main">'+main.map(a).join('')
   +'<div class="mo"><button type="button" aria-expanded="false" aria-haspopup="true">More <i></i></button><div class="dd">'+more.map(a).join('')+'</div></div></nav>'
   +'<div class="r"><a class="bk" href="'+href+'"'+(d.kbook!==undefined?' data-k-book':'')+'>'+btn+'</a>'
   +'<button class="mb" type="button" aria-label="Menu" aria-expanded="false"><i></i><i></i><i></i></button></div></div>';
  if(document.readyState==='loading'&&s.parentNode){document.write(html);}
  else if(s.parentNode){var r=document.createRange();r.selectNode(s);s.parentNode.insertBefore(r.createContextualFragment(html),s.nextSibling);}
  var hs=document.querySelectorAll('#wtr-site-hd'),h=hs[hs.length-1];
  if(!h||h.__w)return;h.__w=1;
  var mb=h.querySelector('.mb'),mo=h.querySelector('.mo'),mt=mo.querySelector('button');
  var solid=d.solid!==undefined;
  function sc(){h.classList.toggle('sc',solid||window.pageYOffset>40);}
  window.addEventListener('scroll',sc,{passive:true});sc();
  mb.addEventListener('click',function(){var o=h.classList.toggle('open');mb.setAttribute('aria-expanded',o);});
  mt.addEventListener('click',function(e){e.stopPropagation();var o=mo.classList.toggle('open');mt.setAttribute('aria-expanded',o);});
  document.addEventListener('click',function(e){if(!mo.contains(e.target)){mo.classList.remove('open');mt.setAttribute('aria-expanded','false');}});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'){mo.classList.remove('open');h.classList.remove('open');}});
  h.querySelector('nav').addEventListener('click',function(e){if(e.target.closest('a'))h.classList.remove('open');});
  h.querySelector('.bk').addEventListener('click',function(){h.classList.remove('open');});
})();
