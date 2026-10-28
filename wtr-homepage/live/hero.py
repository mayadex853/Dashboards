import sys,re
p=sys.argv[1]+'/src/wtr.html';s=open(p,encoding='utf8').read()
EB='<span class="w-eb">For founders doing $250K+ who are ready for 7 figures</span>'
H1='<h1><span class="ln"><span>Scale to 7 figures.</span></span><span class="ln"><span><em>Without it costing</em></span></span><span class="ln"><span><em>you your life.</em></span></span></h1>'
SUB='<p class="w-hero-sub">The founder who got you to $250K can’t get you to $1M. Wreck The Room™ rebuilds the identity running your business, so you become the one who can.</p>'
s=re.sub(r'<span class="w-eb">(Jody Friedman &nbsp;·&nbsp; Wreck the Room™|For founders doing[^<]*)</span>',EB,s,count=1)
s=re.sub(r'<h1>.*?</h1>',H1,s,count=1,flags=re.S)
s=re.sub(r'<p class="w-hero-sub">.*?</p>',SUB,s,count=1,flags=re.S)
open(p,'w',encoding='utf8').write(s)
