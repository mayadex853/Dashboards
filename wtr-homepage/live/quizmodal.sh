# Quiz pop-up: links to quiz.wrecktheroom.com open the assessment in an on-page overlay instead of leaving the site.
grep -q "wq-box" src/wtr.css || cat >> src/wtr.css <<'EOF'

/* quiz pop-up */
.wq{position:fixed;inset:0;z-index:100000;display:none;}
.wq.on{display:block;}
.wq-bg{position:absolute;inset:0;background:rgba(5,4,3,.84);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);}
.wq-box{position:absolute;left:50%;top:52%;transform:translate(-50%,-50%);width:min(980px,94vw);height:min(860px,86vh);background:#0a0908;border:1px solid #c9a84c;box-shadow:0 40px 100px rgba(0,0,0,.6),0 0 0 6px rgba(201,168,76,.08);}
.wq iframe{position:relative;width:100%;height:100%;border:0;display:block;opacity:0;transition:opacity .35s;}
.wq.ready iframe{opacity:1;}
.wq-load{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#c9a84c;font:600 12px/1 Manrope,system-ui,sans-serif;letter-spacing:.26em;text-transform:uppercase;}
.wq.ready .wq-load{display:none;}
.wq-x{position:absolute;top:-50px;right:0;width:42px;height:42px;display:flex;align-items:center;justify-content:center;background:rgba(10,9,8,.6);border:1px solid rgba(201,168,76,.55);color:#ecd69b;font:300 28px/1 Manrope,system-ui,sans-serif;cursor:pointer;}
.wq-x:hover{border-color:#ecd69b;}
@media (max-width:760px){
  .wq-box{left:0;top:0;transform:none;width:100%;height:100%;border:0;padding-top:56px;}
  .wq-x{top:8px;right:10px;}
  .wq-box::before{content:"Wreck The Room™ assessment";position:absolute;top:0;left:0;right:0;height:56px;display:flex;align-items:center;padding:0 18px;color:#c9a84c;font:600 11px/1 Manrope,system-ui,sans-serif;letter-spacing:.2em;text-transform:uppercase;border-bottom:1px solid rgba(201,168,76,.25);}
}
EOF
grep -q "__wq" src/wtr.js || cat >> src/wtr.js <<'EOF'

/* Quiz pop-up: open quiz.wrecktheroom.com links in an on-page overlay so visitors never leave the site. */
(function(){
  if(window.__wq)return;window.__wq=1;
  var Q=/^https?:\/\/quiz\.wrecktheroom\.com/i,m,f;
  function build(){
    m=document.createElement('div');m.className='wq';
    m.innerHTML='<div class="wq-bg" data-wq-x></div><div class="wq-box" role="dialog" aria-modal="true" aria-label="Wreck The Room™ assessment">'
      +'<button class="wq-x" type="button" data-wq-x aria-label="Close the assessment">×</button><div class="wq-load">Loading your assessment…</div>'
      +'<iframe title="Wreck The Room™ assessment" allow="clipboard-write"></iframe></div>';
    document.body.appendChild(m);f=m.querySelector('iframe');
    m.addEventListener('click',function(e){if(e.target.closest('[data-wq-x]'))close();});
    f.addEventListener('load',function(){
      m.classList.add('ready');
      // If the quiz sends people on to a page on this site (results, booking), open it as the full page.
      try{var h=f.contentWindow.location.href;if(h&&h.indexOf(location.origin)===0)window.location.href=h;}catch(x){}
    });
  }
  function open(u){
    if(!m)build();
    if(f.getAttribute('src')!==u){m.classList.remove('ready');f.setAttribute('src',u);}
    m.classList.add('on');document.documentElement.style.overflow='hidden';
    setTimeout(function(){m.querySelector('.wq-x').focus({preventScroll:true});},50);
  }
  function close(){m.classList.remove('on');document.documentElement.style.overflow='';}
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[href]');
    if(!a||!Q.test(a.href)||e.metaKey||e.ctrlKey||e.shiftKey||e.button)return;
    e.preventDefault();e.stopPropagation();open(a.href);
  },true);
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&m&&m.classList.contains('on'))close();});
})();
EOF
