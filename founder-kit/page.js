/* Founder Kit: copy buttons, part labels, kit map, scroll progress, back-to-top. */
(function(){
  function copyBtns(){
    document.querySelectorAll('.prompt-box').forEach(function(b){
      if(b.getAttribute('data-cp'))return;b.setAttribute('data-cp','1');
      var h=b.nextElementSibling;if(!navigator.clipboard)return;
      if(h&&h.classList.contains('copy-hint'))h.style.display='none';
      var btn=document.createElement('button');btn.type='button';btn.className='copy-btn';btn.textContent='Copy prompt';
      btn.addEventListener('click',function(){navigator.clipboard.writeText(b.innerText).then(function(){btn.textContent='Copied ✓';btn.classList.add('ok');setTimeout(function(){btn.textContent='Copy prompt';btn.classList.remove('ok');},1600);});});
      b.parentNode.insertBefore(btn,b.nextSibling);
    });
  }
  function labels(){
    var items=[],n=0;
    document.querySelectorAll('.kit h2').forEach(function(h){
      if(h.getAttribute('data-fk'))return;h.setAttribute('data-fk','1');n++;
      var t=h.textContent.trim(),m=t.match(/^Part (\d+):\s*(.*)$/),id='fk-'+n;h.id=id;
      if(m){h.innerHTML='<span class="pn">Part '+m[1]+'</span>'+m[2].replace(/&/g,'&amp;').replace(/</g,'&lt;');items.push(['0'+m[1],m[2],id]);}
      else{items.push([t==='Start here'?'00':'★',t,id]);}
      if(/AI can.t take/.test(t)){var s=h.closest('section')||h.closest('[data-nova-role=section]')||h.parentNode.parentNode;if(s)s.setAttribute('data-fk-close','1');}
    });
    document.querySelectorAll('.kit h3').forEach(function(h){
      if(h.getAttribute('data-fk'))return;h.setAttribute('data-fk','1');
      var m=h.textContent.trim().match(/^(\d+)\.\s*(.*)$/);
      if(m)h.innerHTML='<span class="hn">'+(m[1].length<2?'0'+m[1]:m[1])+'</span><span>'+m[2].replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</span>';
    });
    var map=document.querySelector('[data-fk-map]');
    if(map&&!map.children.length&&items.length){
      map.innerHTML=items.map(function(i){return '<a href="#'+i[2]+'"><b>'+i[0]+'</b><span>'+i[1].replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</span></a>';}).join('');
      map.addEventListener('click',function(e){var a=e.target.closest('a');if(!a)return;var t=document.getElementById(a.getAttribute('href').slice(1));if(t){e.preventDefault();t.scrollIntoView({behavior:'smooth',block:'start'});}});
    }
  }
  function chrome(){
    if(!document.querySelector('.fk-progress')){var p=document.createElement('div');p.className='fk-progress';document.body.appendChild(p);
      var b=document.createElement('button');b.className='fk-top-btn';b.type='button';b.setAttribute('aria-label','Back to top');b.innerHTML='&#8593;';b.onclick=function(){window.scrollTo({top:0,behavior:'smooth'});};document.body.appendChild(b);
      window.addEventListener('scroll',function(){var h=document.documentElement,max=h.scrollHeight-h.clientHeight;p.style.width=(max>0?(h.scrollTop/max*100):0)+'%';b.classList.toggle('show',h.scrollTop>900);},{passive:true});}
  }
  function init(){copyBtns();labels();chrome();}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
  window.addEventListener('load',init);
})();
