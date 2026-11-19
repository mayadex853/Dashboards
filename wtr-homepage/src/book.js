/* Book waitlist forms: post to Kajabi's "[Waitlist] Book Release - 1st Book" form in the background,
   so the visitor stays on the page (the training video keeps playing). */
(function(){
  var FORM = '/forms/2149477099/form_submissions';
  function token(){ var m=document.querySelector('meta[name="csrf-token"]'); return m?m.getAttribute('content'):''; }
  function bind(f){
    if(f.__wb)return; f.__wb=1;
    f.addEventListener('submit',function(e){
      e.preventDefault();
      var box=f.closest('[data-wb]'), msg=box.querySelector('.wb-msg'), btn=f.querySelector('button');
      var name=f.elements.name.value.trim(), email=f.elements.email.value.trim();
      if(!name||!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)){ msg.textContent='Please add your name and a valid email.'; msg.className='wb-msg err'; return; }
      btn.disabled=true; btn.setAttribute('data-l',btn.textContent); btn.textContent='Saving your spot…'; msg.textContent=''; msg.className='wb-msg';
      var body=new URLSearchParams();
      body.append('authenticity_token',token()); body.append('website_url',''); body.append('kjb_fk_checksum','');
      try{ body.append('kjb_visitor_time_zone',Intl.DateTimeFormat().resolvedOptions().timeZone||'UTC'); }catch(x){ body.append('kjb_visitor_time_zone','UTC'); }
      if(box.getAttribute('data-lp')) body.append('form_submission[landing_page_id]',box.getAttribute('data-lp'));
      body.append('thank_you_url','');
      body.append('form_submission[name]',name); body.append('form_submission[email]',email);
      fetch(FORM,{method:'POST',body:body,credentials:'same-origin',headers:{'Accept':'text/html'}})
        .then(function(r){
          // Kajabi redirects back with form_submission_error=1 (and a reason) when it rejects a sign-up.
          if(!r.ok) throw new Error('http');
          var m=/form_submission_error_reason=([^&]+)/.exec(r.url||'');
          if(/form_submission_error=1/.test(r.url||'')) throw new Error(m?decodeURIComponent(m[1]):'rejected');
          box.classList.add('wb-done');
        })
        .catch(function(err){
          btn.disabled=false; btn.textContent=btn.getAttribute('data-l');
          msg.innerHTML=err.message==='email'?'That email didn’t go through. Please use your main email address.'
            :'Something went wrong. Please try again, or <a href="https://www.wrecktheroom.com/book">join on the book page</a>.';
          msg.className='wb-msg err';
        });
    });
  }
  function init(){
    [].forEach.call(document.querySelectorAll('[data-wb] form'),bind);
    [].forEach.call(document.querySelectorAll('[data-wb-open]'),function(a){
      a.addEventListener('click',function(e){ e.preventDefault(); var b=a.closest('[data-wb]'); b.classList.add('wb-open'); var i=b.querySelector('input[name=name]'); if(i) setTimeout(function(){ i.focus({preventScroll:true}); },60); });
    });
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
