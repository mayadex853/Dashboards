function wtrCredits(root, DATA, POSTERS, SHEET){
  if(!root||root.__wtr)return; root.__wtr=1;
  var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  function $(id){return root.querySelector('#'+id);}
  function esc(x){return String(x==null?'':x).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  function pic(v){v=String(v||'').trim();if(!v)return '';return /^https?:\/\//.test(v)?v:POSTERS+v;}
  function yes(v){return /^y/i.test(String(v||''));}
  function byOrder(a,b){var x=parseFloat(a.Order),y=parseFloat(b.Order);x=isNaN(x)?1e9:x;y=isNaN(y)?1e9:y;return x-y;}
  // Sheets turns the title "9-1-1" into a date; put it back.
  function title(r){var t=String(r.Title==null?'':r.Title).trim();return /^9[-\/]1[-\/](2001|01)$/.test(t)?'9-1-1':t;}

  /* ---- reveal on scroll ---- */
  var io=('IntersectionObserver' in window)&&!reduce?new IntersectionObserver(function(es){
    es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});
  },{rootMargin:'0px 0px -8% 0px',threshold:.08}):null;
  function watch(els){[].forEach.call(els,function(el){if(io)io.observe(el);else el.classList.add('in');});}

  var SHOW=45; // titles shown per placement tab before "Show all"
  var ROLE_FILTERS=[['All',/./],['Supervision',/supervis|producer|consult/i],['Clearance',/clearance/i],['Coordination',/coordinat/i]];

  function render(rows){
    var sec=function(n){return rows.filter(function(r){return String(r.Section||'').trim().toLowerCase()===n;});};
    var P=sec('placement'),J=sec('project'),A=sec('award/panel'),R=sec('podcast/radio'),N=sec('press'),S=sec('stat');
    if(!P.length&&!J.length)return false;

    /* stats (the library's sound-effects count belongs to HD Music Now, not to Jody's credits) */
    var stats=S.filter(function(r){return !/sound effect/i.test(r.Detail||'');});
    stats.sort(function(a,b){return (/project/i.test(b.Detail)?1:0)-(/project/i.test(a.Detail)?1:0);});
    $('c-stats').innerHTML=stats.map(function(r){return '<div class="c-stat"><b>'+esc(title(r))+'</b><span>'+esc(r.Detail)+'</span></div>';}).join('');

    /* hero poster wall */
    var all=J.concat(P).filter(function(r){return pic(r.Poster);}).map(function(r){return pic(r.Poster);});
    var cols='';for(var c=0;c<4;c++){var set=[];for(var k=0;k<7;k++){set.push(all[(c*7+k*5+c*3)%all.length]);}
      var imgs=set.map(function(s){return '<img src="'+esc(s)+'" alt="" loading="lazy">';}).join('');cols+='<div>'+imgs+imgs+'</div>';}
    if(all.length)$('c-hero-wall').innerHTML=cols;

    /* projects grid: the producer credit leads, then the sheet's order */
    var lead=J.filter(function(r){return /producer/i.test(r.Detail||'');});
    var rest=J.filter(function(r){return lead.indexOf(r)<0;});
    var projects=lead.concat(rest);
    function card(r){var p=pic(r.Poster),prod=/producer/i.test(r.Detail||'');
      return '<figure class="c-card" data-role="'+esc(r.Detail)+'"><div class="pic">'+(prod?'<span class="badge">Producer</span>':'')
        +(p?'<img src="'+esc(p)+'" alt="'+esc(title(r))+' poster" loading="lazy">':'<div class="tx"><b>'+esc(title(r))+'</b><i>'+esc(r.Type||'')+'</i></div>')
        +'</div><figcaption><strong>'+esc(title(r))+'</strong><span><em>'+esc(r.Detail)+'</em>'+(r.Year?' · '+esc(r.Year):'')+'</span></figcaption></figure>';}
    $('c-grid').innerHTML=projects.map(card).join('');
    $('c-chips').innerHTML=ROLE_FILTERS.map(function(f,i){var n=projects.filter(function(r){return f[1].test(r.Detail||'');}).length;
      return '<button role="tab" aria-selected="'+(i===0)+'" data-f="'+i+'">'+f[0]+'<sup>'+n+'</sup></button>';}).join('');
    watch(root.querySelectorAll('.c-card'));

    /* placements: poster marquee + category tabs */
    var pc=P.filter(function(r){return yes(r.Carousel)&&pic(r.Poster);}).sort(byOrder);
    if(pc.length){var half=Math.ceil(pc.length/2);
      var row=function(list,cls){var imgs=list.map(function(r){return '<img src="'+esc(pic(r.Poster))+'" alt="'+esc(title(r))+'" loading="lazy">';}).join('');return '<div class="c-row'+cls+'">'+imgs+imgs+'</div>';};
      $('c-marquee').innerHTML=row(pc.slice(0,half),'')+row(pc.slice(half),' r');}
    var cats=['TV','Film','Trailers','Ads & Campaigns','Video Games'];
    P.forEach(function(r){var c=String(r.Type||'TV').trim()||'TV';if(cats.indexOf(c)<0)cats.push(c);});
    var groups=cats.map(function(c){return P.filter(function(r){return (String(r.Type||'TV').trim()||'TV')===c;});});
    var tabs='',panels='',first=-1;
    groups.forEach(function(g,i){if(!g.length)return;if(first<0)first=i;
      tabs+='<button role="tab" aria-selected="'+(i===first)+'" data-t="'+i+'">'+esc(cats[i])+'<sup>'+g.length+'</sup></button>';
      panels+='<div class="c-panel'+(i===first?' on':'')+'" data-p="'+i+'"><ul'+(g.length>SHOW?' class="clip"':'')+'>'+g.map(function(r){return '<li><b>'+esc(title(r))+'</b>'+(r.Detail?'<span>'+esc(r.Detail)+'</span>':'')+'</li>';}).join('')+'</ul>'
        +(g.length>SHOW?'<button class="c-more w-link">Show all '+g.length+' '+esc(cats[i])+' credits ↓</button>':'')+'</div>';});
    $('c-tabs').innerHTML=tabs;$('c-panels').innerHTML=panels;

    /* stage & press */
    [[A,'c-awards'],[R,'c-pods'],[N,'c-press']].forEach(function(x){if(x[0].length)$(x[1]).innerHTML=x[0].map(function(r){return '<li><span>'+esc(title(r))+'</span><em>'+esc(r.Detail)+'</em></li>';}).join('');});
    return true;
  }

  /* ---- interactions ---- */
  root.addEventListener('click',function(e){
    var f=e.target.closest('#c-chips button');
    if(f){var re=ROLE_FILTERS[+f.dataset.f][1];
      [].forEach.call(root.querySelectorAll('#c-chips button'),function(b){b.setAttribute('aria-selected',b===f);});
      [].forEach.call(root.querySelectorAll('.c-card'),function(c){c.style.display=re.test(c.dataset.role)?'':'none';c.classList.add('in');});}
    var m=e.target.closest('.c-more');
    if(m){m.previousElementSibling.classList.remove('clip');m.remove();}
    var t=e.target.closest('#c-tabs button');
    if(t){[].forEach.call(root.querySelectorAll('#c-tabs button'),function(b){b.setAttribute('aria-selected',b===t);});
      [].forEach.call(root.querySelectorAll('.c-panel'),function(p){p.classList.toggle('on',p.dataset.p===t.dataset.t);});}
  });

  render(DATA);
  watch(root.querySelectorAll('.w-rv'));

  /* ---- live data: the same Google Sheet that feeds hdmusicnow.com ---- */
  if(SHEET){
    var cb='__wtrSheet'+Date.now();
    window[cb]=function(resp){try{if(!resp||resp.status!=='ok')return;var cols=resp.table.cols.map(function(c){return c.label;});
      var rows=resp.table.rows.map(function(row){var o={};row.c.forEach(function(cell,i){o[cols[i]]=cell?(cell.f!=null?cell.f:cell.v):'';});return o;});
      if(rows.length)render(rows);}catch(err){}finally{delete window[cb];}};
    var sc=document.createElement('script');
    sc.src='https://docs.google.com/spreadsheets/d/'+SHEET+'/gviz/tq?headers=1&tqx=out:json;responseHandler:'+cb;
    sc.onerror=function(){delete window[cb];};document.head.appendChild(sc);
  }
}
