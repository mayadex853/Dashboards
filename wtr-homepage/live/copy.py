# Homepage copy for founders doing $250K+ heading to 7 figures (approved Oct 2026).
import sys
p=sys.argv[1]+'/src/wtr.html';s=open(p,encoding='utf8').read()
R=[
('<span class="w-micro"><b>Free 3-minute assessment.</b> See which room is running your life.</span>',
 '<span class="w-micro"><b>Free 3-minute assessment.</b> See what’s capping your growth and get your next step.</span>'),
('''    <span><b>Former CNN</b> &amp; Good Morning America</span>
    <span>Music Supervisor, <b>The Bachelor</b> franchise</span>
    <span>Film producer</span>''',
'''    <span><b>Multi-7-figure</b> entrepreneur</span>
    <span><b>Former CNN</b> &amp; Good Morning America</span>
    <span>Music Supervisor, <b>The Bachelor</b> franchise</span>'''),
('<h2>Why more effort stops working at a certain&nbsp;level.</h2>','<h2>Why working harder stopped&nbsp;working.</h2>'),
('''        <p class="w-lead w-rv">Most high achievers don’t feel stuck because they lack discipline, intelligence, or ambition.</p>
        <p class="w-rv d1">They feel stuck because the identity that built their success was created in childhood to survive. It has quietly become the prison that keeps them from reaching their potential.</p>
        <p class="w-rv d2">The habits, pressures, roles, and expectations that once helped you win eventually start demanding more than they give back.</p>''',
'''        <p class="w-lead w-rv">You’re past $250K. You’ve proven you can build. But the next level isn’t coming from more hours, and you can feel it: every decision still lands on you, the team waits on you, and a week off feels impossible.</p>
        <p class="w-rv d1">That isn’t a strategy gap. The way you learned to win (do it yourself, say yes, push through) was built long before this business. It got you here. It can’t get you to 7 figures.</p>'''),
('''          <span>Decision-making gets heavier.</span>
          <span>Energy gets thinner.</span>
          <span>Success starts costing more than it should.</span>''',
'''          <span>Every decision still runs through you.</span>
          <span>You’re making more and enjoying it less.</span>
          <span>Growth costs more than it should.</span>'''),
('''        <p class="w-rv">At this stage, more strategy doesn’t create freedom. More effort doesn’t create clarity.</p>
        <p class="w-rv"><strong>What’s required is a rebuild at the identity level, in how you lead and how you measure success, before the cost becomes permanent.</strong></p>''',
'''        <p class="w-rv"><strong>More tactics won’t change that. A rebuild at the identity level will: how you lead, and how you measure success.</strong></p>'''),
('They help. They just work on a different layer than the one that’s holding you.','They help. They just work on a different layer than the one holding you back.'),
('<p>Valuable for making sense of your past. It doesn’t, on its own, change how you run your company or your life today.</p>',
 '<p>Valuable for making sense of your past. On its own, it doesn’t change how you run your company today.</p>'),
('<span class="w-vs-k">Coaching &amp; strategy</span><span class="w-vs-q">Helps you perform better inside the room.</span><p>New tactics and accountability, applied by the same identity that’s already hitting its ceiling.</p>',
 '<span class="w-vs-k">Coaching, masterminds &amp; strategy</span><span class="w-vs-q">Helps you perform better inside the room.</span><p>Better tactics, run by the same identity that’s already hitting its ceiling.</p>'),
('<p>Identifies the room you’re operating from, dismantles what you’ve outgrown, and rebuilds how you operate, lead, and decide.</p>',
 '<p>It finds the pattern capping your growth, takes it apart and rebuilds how you lead. Built for business owners, not the therapy couch.</p>'),
('They create safety, structure, and momentum.','They create safety and momentum.'),
('<span class="w-micro">Are you drifting, stalling, renovating, or rebuilding? <b>Find out in 3 minutes.</b></span>',
 '<span class="w-micro">Are you drifting, stalling, renovating or rebuilding? <b>Find out in 3 minutes.</b></span>'),
('<h3>Your next level.</h3><p>Successful on paper, misaligned inside. Start with the free assessment.</p>',
 '<h3>Scale to 7 figures.</h3><p>You’re past $250K and ready for what’s next, without it costing you your life. Start with the free assessment.</p>'),
('''        <span class="w-eb w-rv">Track I · For high achievers</span>
        <h2 class="w-rv">Break through to your <em>next level.</em></h2>
        <p class="w-lead w-rv">You’re successful on paper. You’ve built a great income, a strong reputation, and a life others admire. But internally, something feels off. Misaligned. Incomplete.</p>
        <p class="w-rv">Through the Wreck The Room™ methodology, we find what’s limiting your growth and rebuild a life that fits who you’re becoming, so your income can grow without burning down your health or your family in the process.</p>''',
'''        <span class="w-eb w-rv">For founders doing $250K+</span>
        <h2 class="w-rv">Grow to 7 figures without it <em>consuming your life.</em></h2>
        <p class="w-lead w-rv">You’ve built something real, and people admire it. But inside something’s off, and every new level feels heavier than the last.</p>
        <p class="w-rv">Through the Wreck The Room™ method, we find the pattern capping your growth and rebuild how you operate, so the business reaches 7 figures without burning down your health or your family.</p>'''),
('<span class="w-micro"><b>Free · 3 minutes.</b> You’ll get your operating mode and a simple next step based on where you are.</span>',
 '<span class="w-micro"><b>Free · 3 minutes.</b> Find out which room is currently running your life and your exact next step right away. If it’s a fit, you can book a call with Jody.</span>'),
('and what’s actually creating the friction.</p>','and what’s capping your growth.</p>'),
]
miss=0
for a,b in R:
    if a in s: s=s.replace(a,b)
    elif b not in s: print('MISS:',a[:70]); miss+=1
open(p,'w',encoding='utf8').write(s); print('missing',miss)
