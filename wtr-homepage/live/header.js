/* Wreck The Room™ site header, shared by the custom Kajabi pages.
   Include it where the header should sit:
     <script src=".../wtr-homepage/live/header.js" data-btn="Take the quiz" data-href="https://quiz.wrecktheroom.com"></script>
   data-kbook on the script adds data-k-book to the button (pages that open the Kajabi booking popup).
   Desktop shows the main links plus a "More" dropdown; below 1200px everything moves into the hamburger menu. */
(function(){
  var s=document.currentScript||{dataset:{}};
  var d=s.dataset||{};
  var btn=d.btn||'Take the quiz', href=d.href||'https://quiz.wrecktheroom.com';
  var W='https://www.wrecktheroom.com';
  var main=[['About','/about'],['Speaking','/speaker2'],['Wreck The Room&trade;','/rebuild'],['Work With Me','/coaching']];
  var more=[['Testimonials','/testimonials'],['Credits','/credits'],['Blog','/blog']];
  var a=function(l){return '<a href="'+W+l[1]+'">'+l[0]+'</a>';};
  var css='html{scroll-padding-top:96px}'
   +'.wtr-hd{position:fixed;top:0;left:0;right:0;z-index:900;display:flex;align-items:center;justify-content:space-between;padding:20px 32px;font:600 12px/1 Manrope,system-ui,sans-serif;letter-spacing:.2em;text-transform:uppercase;transition:background .35s,padding .35s,box-shadow .35s}'
   +'.wtr-hd.sc{background:rgba(10,9,8,.94);padding-top:12px;padding-bottom:12px;box-shadow:0 1px 0 rgba(201,168,76,.22)}'
   +'.wtr-hd img{width:150px;height:auto;display:block;transition:width .35s}.wtr-hd.sc img{width:124px}'
   +'.wtr-hd nav{display:flex;gap:30px;align-items:center}'
   +'.wtr-hd a{color:#d9d2c4 !important;text-decoration:none !important;white-space:nowrap}.wtr-hd nav a:hover{color:#ecd69b !important}'
   +'.wtr-hd .bk{border:1px solid #c9a84c;color:#ecd69b !important;padding:14px 20px}'
   +'.wtr-hd .r{display:flex;align-items:center;gap:10px}'
   +'.wtr-hd .mo{position:relative}'
   +'.wtr-hd .mo>button{background:none;border:0;padding:8px 0;margin:0;cursor:pointer;font:inherit;letter-spacing:inherit;text-transform:inherit;color:#d9d2c4;display:flex;align-items:center;gap:7px}'
   +'.wtr-hd .mo>button:hover,.wtr-hd .mo.open>button{color:#ecd69b}'
   +'.wtr-hd .mo>button i{width:7px;height:7px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:translateY(-2px) rotate(45deg);transition:transform .25s}'
   +'.wtr-hd .mo.open>button i{transform:translateY(1px) rotate(-135deg)}'
   +'.wtr-hd .dd{position:absolute;top:calc(100% + 14px);right:-18px;min-width:190px;padding:10px 0;background:rgba(10,9,8,.97);border:1px solid rgba(201,168,76,.35);box-shadow:0 18px 40px rgba(0,0,0,.5);display:flex;flex-direction:column;opacity:0;visibility:hidden;transform:translateY(-6px);transition:opacity .2s,transform .2s,visibility .2s}'
   +'.wtr-hd .dd::before{content:"";position:absolute;left:0;right:0;top:-16px;height:16px}'
   +'.wtr-hd .dd a{padding:13px 22px}.wtr-hd .dd a:hover{background:rgba(201,168,76,.1)}'
   +'.wtr-hd .mo.open .dd{opacity:1;visibility:visible;transform:none}'
   +'@media(hover:hover) and (min-width:1001px){.wtr-hd .mo:hover .dd{opacity:1;visibility:visible;transform:none}}'
   +'.wtr-hd .mb{display:none;background:none;border:1px solid rgba(201,168,76,.45);width:40px;height:38px;padding:0;cursor:pointer;position:relative}'
   +'.wtr-hd .mb i{position:absolute;left:10px;right:10px;height:1.5px;background:#ecd69b;transition:transform .3s,opacity .3s}'
   +'.wtr-hd .mb i:nth-child(1){top:12px}.wtr-hd .mb i:nth-child(2){top:18px}.wtr-hd .mb i:nth-child(3){top:24px}'
   +'.wtr-hd.open .mb i:nth-child(1){transform:translateY(6px) rotate(45deg)}.wtr-hd.open .mb i:nth-child(2){opacity:0}.wtr-hd.open .mb i:nth-child(3){transform:translateY(-6px) rotate(-45deg)}'
   +'@media(max-width:1140px){.wtr-hd nav{gap:22px;letter-spacing:.14em}.wtr-hd .bk{padding:12px 14px}}'
   +'@media(max-width:1000px){.wtr-hd{padding:14px 20px}.wtr-hd.sc{padding-top:10px;padding-bottom:10px}.wtr-hd img,.wtr-hd.sc img{width:116px}.wtr-hd .mb{display:block}.wtr-hd .bk{padding:11px 12px;font-size:10px}'
   +'.wtr-hd nav{position:fixed;top:0;left:0;right:0;bottom:0;z-index:-1;flex-direction:column;justify-content:center;gap:28px;background:#0a0908;font-size:15px;letter-spacing:.24em;opacity:0;visibility:hidden;transition:opacity .3s,visibility .3s;overflow-y:auto}'
   +'.wtr-hd.open nav{opacity:1;visibility:visible}'
   +'.wtr-hd .mo{display:contents}.wtr-hd .mo>button{display:none}'
   +'.wtr-hd .dd{position:static;display:contents;opacity:1;visibility:visible;transform:none;background:none;border:0;box-shadow:none;padding:0;min-width:0}.wtr-hd .dd::before{display:none}.wtr-hd .dd a{padding:0}.wtr-hd .dd a:hover{background:none}}';
  var html='<style>'+css+'</style><div class="wtr-hd"><a href="'+W+'/"><img src="https://kajabi-storefronts-production.kajabi-cdn.com/kajabi-storefronts-production/file-uploads/themes/2162751237/settings_images/47ed02-ebc5-250f-cdd2-17c278b4e31_JODY_LOGO_smaller.png" alt="Jody Friedman"></a>'
   +'<div class="r"><nav>'+main.map(a).join('')
   +'<div class="mo"><button type="button" aria-expanded="false" aria-haspopup="true">More <i></i></button><div class="dd">'+more.map(a).join('')+'</div></div></nav>'
   +'<a class="bk" href="'+href+'"'+(d.kbook!==undefined?' data-k-book':'')+'>'+btn+'</a>'
   +'<button class="mb" type="button" aria-label="Menu" aria-expanded="false"><i></i><i></i><i></i></button></div></div>';
  if(document.readyState==='loading'&&s.parentNode){document.write(html);}
  else if(s.parentNode){var r=document.createRange();r.selectNode(s);s.parentNode.insertBefore(r.createContextualFragment(html),s.nextSibling);}
  var hs=document.querySelectorAll('.wtr-hd'),h=hs[hs.length-1];
  if(!h||h.__w)return;h.__w=1;
  var mb=h.querySelector('.mb'),mo=h.querySelector('.mo'),mt=mo.querySelector('button');
  function sc(){h.classList.toggle('sc',window.pageYOffset>40);}
  window.addEventListener('scroll',sc,{passive:true});sc();
  mb.addEventListener('click',function(){var o=h.classList.toggle('open');mb.setAttribute('aria-expanded',o);});
  mt.addEventListener('click',function(e){e.stopPropagation();var o=mo.classList.toggle('open');mt.setAttribute('aria-expanded',o);});
  document.addEventListener('click',function(e){if(!mo.contains(e.target)){mo.classList.remove('open');mt.setAttribute('aria-expanded','false');}});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'){mo.classList.remove('open');h.classList.remove('open');}});
  h.querySelector('nav').addEventListener('click',function(e){if(e.target.closest('a'))h.classList.remove('open');});
  h.querySelector('.bk').addEventListener('click',function(){h.classList.remove('open');});
})();
