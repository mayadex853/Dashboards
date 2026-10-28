import sys
p=sys.argv[1]+'/src/wtr.html';s=open(p,encoding='utf8').read()
R=[('<span class="w-eb">Jody Friedman &nbsp;·&nbsp; Wreck the Room™</span>','<span class="w-eb">For founders doing $250K to $1M a year</span>'),
('<h1><span class="ln"><span>You can’t reach</span></span><span class="ln"><span>your next level</span></span><span class="ln"><span>with an <em>old identity.</em></span></span></h1>',
 '<h1><span class="ln"><span>Grow the business.</span></span><span class="ln"><span><em>Get your life back.</em></span></span></h1>'),
('<p class="w-hero-sub">I help founders and leaders rebuild the identity behind their success, so the next level stops feeling out of reach.</p>',
 '<p class="w-hero-sub">The version of you that built this can’t take it further. Wreck the Room rebuilds the identity running your business, so it keeps growing and stops running you.</p>')]
for a,b in R:
    if a in s: s=s.replace(a,b)
    elif b not in s: print('MISS',a[:50])
open(p,'w',encoding='utf8').write(s)
