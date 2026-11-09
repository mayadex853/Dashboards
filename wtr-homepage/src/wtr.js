function wtrInit(root){
  if(!root||root.__wtr)return; root.__wtr=1;
  var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- brick wall (built in JS so the markup stays light) ---- */
  var wall=root.querySelector('[data-wall]');
  if(wall){
    var rows=9,cols=4,h=100/rows,frag=document.createDocumentFragment();
    for(var r=0;r<rows;r++){
      var off=r%2?-.5:0;
      for(var c=0;c<=cols;c++){
        var x0=Math.max(0,(c+off)*(100/cols)),x1=Math.min(100,(c+off+1)*(100/cols));
        if(x1-x0<1)continue;
        var b=document.createElement('i');
        b.style.left='calc('+x0+'% + 3px)';b.style.width='calc('+(x1-x0)+'% - 6px)';b.style.top=(r*h)+'%';
        var cx=(x0+x1)/2,cy=(r+.5)*h;
        // the doorway: bricks in the lower middle fall away
        if(cx>28&&cx<72&&cy>50){
          b.dataset.fall=1;
          b.style.transitionDelay=(.15+(100-cy)/100*.9+Math.abs(cx-50)/100).toFixed(2)+'s';
        }
        frag.appendChild(b);
      }
    }
    wall.appendChild(frag);
  }

  /* ---- reveal on scroll ---- */
  function fire(el){
    el.classList.add('in');
    if(el.hasAttribute('data-wall')){
      el.classList.add('go');
      [].forEach.call(el.querySelectorAll('i[data-fall]'),function(b,i){
        var dx=(Math.random()*60-30),rot=(Math.random()*70-35);
        b.style.transform='translate('+dx+'px,'+(180+Math.random()*120)+'px) rotate('+rot+'deg)';
        b.style.opacity='0';
      });
    }
  }
  var targets=root.querySelectorAll('.w-rv,[data-wall],[data-steps],[data-curve]');
  if(reduce||!('IntersectionObserver' in window)){
    [].forEach.call(targets,fire);
  }else{
    var io=new IntersectionObserver(function(es){
      es.forEach(function(e){if(e.isIntersecting){fire(e.target);io.unobserve(e.target);}});
    },{rootMargin:'0px 0px -12% 0px',threshold:.12});
    [].forEach.call(targets,function(t){io.observe(t);});
  }

  /* ---- smooth in-page scroll ---- */
  function go(id){
    var t=document.getElementById(id);if(!t)return;
    var hd=document.querySelector('#section-header header'),hh=hd?hd.getBoundingClientRect().height:0; // Kajabi's sticky header
    var y=t.getBoundingClientRect().top+window.pageYOffset-Math.max(40,Math.min(hh,160)+20);
    window.scrollTo({top:y,behavior:reduce?'auto':'smooth'});
  }
  root.addEventListener('click',function(e){
    var a=e.target.closest('[data-w-scroll]');
    if(a){e.preventDefault();go(a.getAttribute('href').slice(1));}
  });

  /* ---- click-to-play video facades ---- */
  root.addEventListener('click',function(e){
    var v=e.target.closest('.w-vid');if(!v||v.querySelector('iframe'))return;
    var src=v.dataset.vimeo?'https://player.vimeo.com/video/'+v.dataset.vimeo+'?autoplay=1&badge=0&autopause=0&title=0&byline=0&portrait=0&color=c9a84c'
      :'https://fast.wistia.net/embed/iframe/'+v.dataset.wistia+'?autoPlay=true&playerColor=c9a84c';
    var f=document.createElement('iframe');
    f.src=src;f.allow='autoplay; fullscreen; picture-in-picture';f.setAttribute('allowfullscreen','');f.title=v.getAttribute('aria-label')||'Video';
    v.appendChild(f);
  });

  /* ---- booking form ----
     Live on Kajabi: the page's own booking form (inside the #two-step pop-up) is moved into this section,
     so it submits exactly as before (same action, fields, token and validation). Any other
     "Book Jody to speak" button on the page then scrolls here instead of opening an empty pop-up. */
  var slot=root.querySelector('#wtr-fslot');
  if(slot){
    var form=slot.querySelector('form')||document.querySelector('#two-step form');
    if(form){
      if(form.parentNode!==slot){slot.innerHTML='';slot.appendChild(form);}
      [['form_submission_custom_4','form_submission_custom_5'],['form_submission_email','form_submission_phone_number'],
       ['form_submission_custom_6','form_submission_custom_7'],['form_submission_custom_8','form_submission_custom_9']].forEach(function(p){
        var a=form.querySelector('#'+p[0]),b=form.querySelector('#'+p[1]);
        a=a&&a.closest('.form-group');b=b&&b.closest('.form-group');
        if(a&&b&&a.parentNode===b.parentNode){var w=document.createElement('div');w.className='w-f2';a.parentNode.insertBefore(w,a);w.appendChild(a);w.appendChild(b);}
      });
      var btn=form.querySelector('button[type=submit]');
      if(btn)btn.innerHTML='Check Jody’s availability &nbsp;→';
      var note=document.createElement('p');note.className='w-fnote';note.textContent='Not sure of a date or budget yet? Send what you have. Approximate is fine.';
      form.appendChild(note);
      document.addEventListener('click',function(e){
        var t=e.target.closest&&e.target.closest('[data-target="#two-step"],a[href="#two-step"]');
        if(t&&!root.contains(t)){e.preventDefault();e.stopPropagation();go('wtr-book');}
      },true);
    }else{
      // Form not found (e.g. Kajabi changed the pop-up): fall back to opening the pop-up as before.
      slot.innerHTML='<div class="w-fallback"><a class="w-btn p" href="#two-step" data-target="#two-step">Open the booking form <span class="ar">→</span></a></div>';
      slot.querySelector('a').addEventListener('click',function(e){
        e.preventDefault();
        var m=document.querySelector('.two-step');
        if(m){m.classList.add('modal--open');document.documentElement.classList.add('stop-scroll--html');document.body.classList.add('stop-scroll--body');}
      });
    }
  }
  // Every in-page "Book Jody" link inside this embed goes to the form.
  [].forEach.call(root.querySelectorAll('a[href="#wtr-speaking"]'),function(a){a.setAttribute('data-w-scroll','');});
}

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

/* Phone quiz bar: appears once the hero button scrolls away, hides while another quiz button is on screen. */
(function(){
  if(window.__wstick)return;window.__wstick=1;
  function init(){
    var bar=document.querySelector('.w-stick');if(!bar)return;
    var hero=document.querySelector('.w-hero');
    function tick(){
      var past=hero?hero.getBoundingClientRect().bottom<80:window.pageYOffset>600;
      var other=[].some.call(document.querySelectorAll('.wtr a.w-btn[href*="quiz.wrecktheroom.com"]'),function(b){var r=b.getBoundingClientRect();return r.top<innerHeight&&r.bottom>0;});
      bar.classList.toggle('on',past&&!other);
    }
    window.addEventListener('scroll',tick,{passive:true});tick();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else setTimeout(init,0);
})();
