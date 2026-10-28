# Homepage = one goal: the quiz. Speaker content lives on /speaker2 (header button goes there).
import sys,re
root=sys.argv[1]
p=root+'/src/wtr.html';s=open(p,encoding='utf8').read()
if 'class="w-stick"' not in s:
    s=s.replace('      <p style="margin-top:30px"><a class="w-link" href="#wtr-speaking" data-w-scroll>Booking a speaker? Start here →</a></p>\n','')
    a=s.index('<!-- ===================== PATH CHOOSER'); b=s.index('<!-- ===================== TRACK I ')
    s=s[:a]+s[b:]
    s=s.replace('  <div class="w-rail" aria-hidden="true"><span>Track I · For high achievers</span></div>\n','')
    s=re.sub(r'\n\s*<a class="w-link" href="https://www.wrecktheroom.com/about">Read Jody’s story →</a>','',s)
    a=s.index('<!-- ===================== TRACK II')
    s=s[:a].rstrip()+'\n\n<a class="w-stick" href="https://quiz.wrecktheroom.com">Discover which room you’re in <span class="ar">→</span></a>\n\n</div>\n'
    open(p,'w',encoding='utf8').write(s)
c=root+'/src/wtr.css';t=open(c,encoding='utf8').read()
if '.w-stick{' not in t:
    t+='''
/* phone: quiz button pinned to the bottom of the screen */
.w-stick{display:none;}
@media (max-width:760px){
  .w-stick{position:fixed;left:12px;right:12px;bottom:12px;z-index:800;display:flex;align-items:center;justify-content:center;gap:10px;height:56px;
    background:linear-gradient(135deg,#ecd69b,#c9a84c 55%,#a5862f);color:#0b0a08 !important;text-decoration:none !important;
    font:800 12.5px/1 Manrope,system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;box-shadow:0 14px 34px rgba(0,0,0,.55);
    transform:translateY(160%);transition:transform .35s cubic-bezier(.2,.8,.2,1);}
  .w-stick.on{transform:none;}
}
'''
    open(c,'w',encoding='utf8').write(t)
j=root+'/src/wtr.js';u=open(j,encoding='utf8').read()
if '__wstick' not in u:
    u+='''
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
'''
    open(j,'w',encoding='utf8').write(u)
print('ok')
