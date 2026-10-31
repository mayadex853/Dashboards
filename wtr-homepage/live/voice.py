import sys,os
R={
'src/wtr.html':[
("I help high-achieving founders and leaders rebuild the identity, standards, and operating systems required for their next level of wealth, leadership, and impact.",
 "I help founders and leaders rebuild the identity behind their success, so the next level stops feeling out of reach."),
("was created in childhood to survive — and it has quietly become the prison","was created in childhood to survive. It has quietly become the prison"),
("What’s required is a rebuild at the identity level — how you operate, lead, decide, and measure success — before the cost becomes permanent.",
 "What’s required is a rebuild at the identity level, in how you lead and how you measure success, before the cost becomes permanent."),
("New tactics and accountability — applied by","New tactics and accountability, applied by"),
("Over time, those walls become rooms you live — and lead — from.","Over time, those walls become the rooms you live and lead from."),
("how you operate next — before the room decides for you.","how you operate next, before the room decides for you."),
("Name the walls — the wins, wounds, and expectations — that quietly became","Name the walls, the wins and wounds that quietly became"),
("Intentionally choose how you operate, lead, and measure success next — on purpose, not by default.","Choose how you lead and measure success next. On purpose, not by default."),
("Track I — For high achievers","Track I · For high achievers"),
("Through the Wreck the Room methodology, we will identify what’s limiting your growth, and rebuild a life that fully aligns with who you’re becoming — so your energy, influence, and income can grow without burning down your health, family, or integrity in the process.",
 "Through the Wreck the Room methodology, we find what’s limiting your growth and rebuild a life that fits who you’re becoming, so your income can grow without burning down your health or your family in the process."),
("&nbsp;— from his story","&nbsp;· from his story"),
("renovating, or rebuilding — and what’s actually creating the friction.","renovating or rebuilding, and what’s actually creating the friction."),
("Track II — For your stage","Track II · For your stage"),
("Cinematic, personal storytelling — your audience leaves changed, not just inspired","Cinematic, personal storytelling that leaves your audience changed"),
],
'src/wtr.js':[("Send what you have — approximate is fine.","Send what you have. Approximate is fine.")],
'src/speaker.html':[
("tell better stories under pressure — from producing feature films to managing million-dollar creative projects — and now I help organizations rewrite theirs.",
 "tell better stories under pressure, from producing feature films to managing million-dollar creative projects. Now I help organizations rewrite theirs."),
("Your audience won’t just leave inspired — they’ll have a clear framework to break through what’s limiting their performance and unlock breakthrough results.",
 "Your audience leaves with a clear framework to break through what’s limiting their performance."),
("Stagnant teams aren’t broken — they’re just operating from outdated patterns.","Stagnant teams are usually running on outdated patterns."),
("hit like a live show — pro broadcast setup, real-time audience interaction, and the kind of energy that makes people forget they’re sitting at a desk.",
 "hit like a live show, with a pro broadcast setup and real-time audience interaction. People forget they’re sitting at a desk."),
],
'src/vip.html':[
("This retreat isn’t about fixing a broken business. It’s about upgrading the person running it — so your income, impact, and freedom finally match what you’re capable of.",
 "This retreat upgrades the person running the business, so your income and your freedom finally match what you’re capable of."),
("the patterns that stopped compounding — and design","the patterns that stopped compounding and design"),
("This retreat is designed to immerse you in the rhythm, pace, and presence of how ultra-high performers actually live — not as an escape, but as a reminder of what’s possible when identity, decisions, and environment are aligned.",
 "This retreat immerses you in how ultra-high performers actually live. You leave with a clear picture of what’s possible when your identity and your decisions line up."),
],
'src/coaching.html':[("Wreck the Room — 1:1","Wreck the Room · 1:1")],
}
root=sys.argv[1]
for f,pairs in R.items():
  p=os.path.join(root,f)
  if not os.path.exists(p): continue
  s=open(p,encoding='utf8').read()
  for a,b in pairs:
    if a in s: s=s.replace(a,b)
    elif b not in s: print('MISS',f,a[:60])
  open(p,'w',encoding='utf8').write(s)
  print(f,'em dashes left:',s.count('—'))
