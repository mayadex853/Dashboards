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
  var targets=root.querySelectorAll('.w-rv,[data-wall],[data-steps]');
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
    var y=t.getBoundingClientRect().top+window.pageYOffset-40;
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
      var note=document.createElement('p');note.className='w-fnote';note.textContent='Not sure of a date or budget yet? Send what you have — approximate is fine.';
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
