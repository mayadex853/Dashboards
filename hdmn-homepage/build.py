"""Build the HD Music Now homepage embed.

Outputs:
  preview.html       standalone page for local review (posters loaded from ./posters)
  kajabi-embed.html  paste into a single Kajabi Code block (posters loaded from jsDelivr)

Usage: python3 build.py [CDN_REF]   (CDN_REF = git branch or commit, default: the working branch)
"""
import html
import random
import sys
from pathlib import Path

HERE = Path(__file__).parent
CDN_REF = sys.argv[1] if len(sys.argv) > 1 else "claude/hd-music-now-homepage-tt724m"
CDN_BASE = f"https://cdn.jsdelivr.net/gh/mayadex853/Dashboards@{CDN_REF}/hdmn-homepage/posters/"

CATALOG_URL = "https://hdmusicnow.sourceaudio.com/#!label?l=1222458&page=albums"
CONTACT_ANCHOR = "#section-1792000000008"
IMDB_URL = "https://www.imdb.com/name/nm3112237/"

# (title, slug, credit type, network/studio)
POSTERS = [
    ("The Fall Guy", "the-fall-guy", "Feature Film", "Universal"),
    ("Superman", "superman", "Trailer", "Warner Bros. / DC"),
    ("Daredevil: Born Again", "daredevil-born-again", "TV Series", "Disney+"),
    ("Grey's Anatomy", "grey-s-anatomy", "TV Series", "ABC"),
    ("The Fall of the House of Usher", "the-fall-of-the-house-of-usher", "TV Series", "Netflix"),
    ("Spirited", "spirited", "Feature Film", "Apple TV+"),
    ("Street Fighter", "street-fighter", "Feature Film", "Paramount"),
    ("Spider-Noir", "spider-noir", "Trailer", "Prime Video"),
    ("Migration", "migration", "Trailer", "Universal / Illumination"),
    ("Station 19", "station-19", "TV Series", "ABC"),
    ("Riverdale", "riverdale", "TV Series", "The CW"),
    ("Magnum P.I.", "magnum-p-i", "TV Series", "NBC"),
    ("Fantasy Island", "fantasy-island", "Trailer", "Sony / Blumhouse"),
    ("Sistas", "sistas", "TV Series", "BET"),
    ("Three Women", "three-women", "TV Series", "Starz"),
    ("Animal Control", "animal-control", "TV Series", "FOX"),
    ("Alert: Missing Persons Unit", "alert-missing-persons-unit", "TV Series", "FOX"),
    ("It's What's Inside", "it-s-what-s-inside", "Indie Film", "Netflix"),
    ("Landscape with Invisible Hand", "landscape-with-invisible-hand", "Trailer", "MGM"),
    ("The End of Oak Street", "the-end-of-oak-street", "Trailer", "Warner Bros."),
    ("The Front Room", "the-front-room", "Feature Film", "A24"),
    ("Not Without Hope", "not-without-hope", "Feature Film", "Lionsgate"),
    ("The Sheep Detectives", "the-sheep-detectives", "Feature Film", "MGM"),
]

CREDITS = {
    "TV Series": ["SEAL Team", "Station 19", "The Fall of the House of Usher", "Self Portrait as a Coffee Pot",
                  "Demascus", "Riverdale", "Little America", "Animal Control", "Alert: Missing Persons",
                  "Sirens", "Lopez vs. Lopez", "Call Me Kat", "Three Women", "Grey's Anatomy",
                  "Daredevil: Born Again", "The Rookie", "Magnum P.I.", "The Way Home", "Selling Sunset",
                  "I Can See Your Voice", "Say It Loud", "Sweet Caroline", "Sistas", "The Murder of JonBenet"],
    "Feature Film": ["Street Fighter", "The Front Room", "Tapawingo", "The Fall Guy", "Not Without Hope",
                     "Spirited", "One Mile", "The Sheep Detectives"],
    "Trailer": ["Superman", "Spider-Noir", "Migration", "Landscape with Invisible Hand", "Fantasy Island",
                "Skyscraper Live", "The End of Oak Street", "Runner"],
    "Documentary": ["Mistress Dispeller", "Ferragamo", "Love and Treason"],
    "Indie Film": ["Sisters of Ukraine", "It's What's Inside", "Lineage", "Idea of Progress", "An Expectation"],
    "Commercial / Blanket": ["Sweeney Todd (Broadway Revival)", "Mariposa", "Slipstream",
                             "Anthem / Legendary Sound Ideas", "The Instigators"],
}

CLIENTS = ["Netflix", "Disney+", "Apple TV+", "HBO", "Hulu", "ABC", "NBC", "CBS", "Showtime", "Universal",
           "Warner Bros.", "Sony", "The CW", "BET", "MTV", "Bunim/Murray"]

LABELS = [
    ("Flagship Catalog", "HD Music Now",
     "Today's best independent artists, composers, producers and sound designers, plus classic catalogs.",
     "Search Catalog", CATALOG_URL),
    ("Trailer Label", "Collaborate Music",
     "Trailer, promo and teaser cues built with the impact, builds and hits that cut-to-picture demands.",
     "Visit Collaborate", "https://www.collaboratemusic.com"),
    ("Premium Collection", "HDMN Prime",
     "A curated, premium tier of the catalog for high-profile placements.",
     "Explore Prime", "https://hdmusicnow.sourceaudio.com/catalog/6588?page=albums"),
    ("Via APM Music", "Stacks to Tracks",
     "Our library distributed through APM Music, searchable and licensable directly on APM.",
     "Search on APM", "https://www.apmmusic.com/libraries/stacks-to-tracks-(strx)"),
    ("Via APM Music", "Ocho Music Group",
     "Our library distributed through APM Music, searchable and licensable directly on APM.",
     "Visit Ocho", "https://www.ochomusicgroup.com"),
]

SUBPUBS = ["HDMN Royalty Music UK", "BMG", "Sonoton", "ViMusica", "Moodoofind", "Red Igloo", "Kouros",
           "Yellowgroove", "Miles of Musik", "Apollo Music"]

e = html.escape


def poster_src(slug, base):
    return f"{base}{slug}.jpg"


def build(base):
    rnd = random.Random(7)
    rows = []
    for r in range(4):
        picks = POSTERS[:]
        rnd.shuffle(picks)
        picks = picks[:12]
        imgs = "".join(f'<img src="{poster_src(p[1], base)}" alt="">' for p in picks * 2)
        rows.append(f'<div class="hd-wall-row{" rev" if r % 2 else ""}" style="animation-duration:{90 + r * 20}s">{imgs}</div>')

    ticker = "".join(f"<span>{e(c)}</span><i></i>" for c in CLIENTS) * 2

    cards = "".join(
        f'<figure class="hd-card"><img src="{poster_src(slug, base)}" alt="{e(t)} poster" loading="lazy">'
        f'<figcaption><span>{e(kind)} &middot; {e(net)}</span><strong>{e(t)}</strong></figcaption></figure>'
        for t, slug, kind, net in POSTERS)

    roll = "".join(f"<h5>{e(cat)}</h5>" + "".join(f"<div>{e(t)}</div>" for t in titles)
                   for cat, titles in CREDITS.items())

    labels = "".join(
        f'<a class="hd-label hd-reveal" href="{e(url)}" target="_blank" rel="noopener">'
        f'<span class="hd-label-k">{e(k)}</span><h3>{e(name)}</h3><p>{e(desc)}</p>'
        f'<span class="hd-label-cta">{e(cta)} <b>&rarr;</b></span></a>'
        for k, name, desc, cta, url in LABELS)

    subpubs = " <i>&middot;</i> ".join(e(s) for s in SUBPUBS)

    return TEMPLATE.format(
        css=CSS, wall="".join(rows), ticker=ticker, cards=cards, roll=roll, labels=labels,
        subpubs=subpubs, catalog=e(CATALOG_URL), contact=CONTACT_ANCHOR, imdb=IMDB_URL, js=JS)


CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700&display=swap');
.hd{--bg:#050608;--ink:#fff;--mute:#9aa3b2;--vio:#b14bf4;--vio2:#c084fc;--blu:#38bdf8;--brand:#7b1fa2;
  background:var(--bg);color:var(--mute);font-family:Inter,system-ui,sans-serif;font-size:17px;line-height:1.6;
  overflow:hidden;position:relative;-webkit-font-smoothing:antialiased;text-align:left;}
.hd *{box-sizing:border-box;}
.hd h1,.hd h2,.hd h3,.hd h4,.hd h5{font-family:'Bebas Neue',Impact,sans-serif !important;font-weight:400 !important;
  text-transform:uppercase;letter-spacing:.02em;color:var(--ink);margin:0;line-height:.9 !important;}
.hd p{margin:0 0 1em;color:var(--mute);}
.hd a{text-decoration:none !important;}
.hd-wrap{max-width:1240px;margin:0 auto;padding:0 28px;}
.hd-eb{display:inline-block;font-size:12px;font-weight:700;letter-spacing:.42em;color:var(--vio2);text-transform:uppercase;margin-bottom:22px;}
.hd-h2{font-size:clamp(52px,7.5vw,112px) !important;}
.hd-grad{background:linear-gradient(95deg,#fff 0%,#f3e8ff 38%,var(--vio2) 70%,var(--blu) 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent !important;}
.hd-sec{position:relative;padding:130px 0;}
.hd-btn{display:inline-flex;align-items:center;gap:10px;font:700 13px/1 Inter,sans-serif;letter-spacing:.2em;text-transform:uppercase;
  padding:20px 34px;border-radius:2px;transition:all .25s ease;cursor:pointer;}
.hd-btn.p{background:var(--brand);color:#fff !important;box-shadow:0 0 40px rgba(177,75,244,.55);}
.hd-btn.p:hover{background:#9333ea;transform:translateY(-2px);box-shadow:0 0 70px rgba(177,75,244,.9);}
.hd-btn.o{border:1px solid rgba(255,255,255,.6);color:#fff !important;background:rgba(5,6,8,.4);}
.hd-btn.o:hover{background:#fff;color:#050608 !important;}
.hd-reveal{opacity:0;transform:translateY(40px);transition:opacity 1s ease,transform 1s cubic-bezier(.2,.8,.2,1);}
.hd-reveal.in{opacity:1;transform:none;}

/* NAV */
.hd-nav{position:fixed;top:0;left:0;right:0;z-index:1000;display:flex;align-items:center;justify-content:space-between;
  padding:18px 32px;transition:all .35s ease;}
.hd-nav.solid{background:rgba(5,6,8,.85);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  padding:12px 32px;border-bottom:1px solid rgba(255,255,255,.07);}
.hd-logo{font-family:'Bebas Neue',sans-serif;font-size:30px;letter-spacing:.08em;color:#fff !important;line-height:1;}
.hd-logo b{font-weight:400;color:var(--vio2);text-shadow:0 0 18px rgba(177,75,244,.8);}
.hd-links{display:flex;align-items:center;gap:34px;}
.hd-links a:not(.hd-btn){font-size:12px;font-weight:700;letter-spacing:.25em;text-transform:uppercase;color:#d5dae3 !important;transition:color .2s;}
.hd-links a:not(.hd-btn):hover{color:var(--vio2) !important;}
.hd-links .hd-btn{padding:14px 22px;font-size:11px;}

/* HERO */
.hd-hero{position:relative;min-height:100vh;display:flex;align-items:center;justify-content:center;overflow:hidden;
  border-top:30px solid #000;border-bottom:30px solid #000;}
.hd-wall{position:absolute;top:-30%;left:-20%;right:-20%;bottom:-30%;transform:rotate(-9deg);display:flex;flex-direction:column;
  justify-content:center;gap:20px;opacity:.9;}
.hd-wall-row{display:flex;gap:20px;width:max-content;animation:hd-left 100s linear infinite;}
.hd-wall-row.rev{animation-name:hd-right;}
.hd-wall-row img{width:180px;height:268px;object-fit:cover;border-radius:6px;flex:none;filter:saturate(1.05) contrast(1.05);}
@keyframes hd-left{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@keyframes hd-right{from{transform:translateX(-50%)}to{transform:translateX(0)}}
.hd-shade{position:absolute;inset:0;background:
  radial-gradient(ellipse 55% 50% at 50% 50%,rgba(5,6,8,.86) 0%,rgba(5,6,8,.62) 60%,rgba(5,6,8,.35) 100%),
  linear-gradient(180deg,rgba(5,6,8,.85) 0%,rgba(5,6,8,0) 25%,rgba(5,6,8,0) 70%,rgba(5,6,8,1) 100%);}
.hd-glow{position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen;background:
  radial-gradient(ellipse 40% 45% at 10% 5%,rgba(177,75,244,.55),transparent 60%),
  radial-gradient(ellipse 40% 45% at 92% 98%,rgba(56,189,248,.4),transparent 60%);}
.hd-beam{position:absolute;top:-20%;left:62%;width:3px;height:140%;transform:rotate(22deg);pointer-events:none;
  background:linear-gradient(transparent,rgba(255,255,255,.55),transparent);box-shadow:0 0 140px 50px rgba(177,75,244,.22);
  animation:hd-beam 9s ease-in-out infinite alternate;}
@keyframes hd-beam{from{left:58%;opacity:.6}to{left:70%;opacity:1}}
.hd-hero-in{position:relative;z-index:2;text-align:center;padding:150px 24px 90px;max-width:1180px;}
.hd-hero h1{font-size:clamp(72px,11.5vw,184px) !important;line-height:.82 !important;margin-bottom:30px;
  filter:drop-shadow(0 8px 40px rgba(0,0,0,.85));}
.hd-hero .hd-sub{font-size:21px;color:#e7ebf1;max-width:720px;margin:0 auto 42px;text-shadow:0 2px 20px #000;}
.hd-ctas{display:flex;gap:16px;justify-content:center;flex-wrap:wrap;}
.hd-heard{margin-top:50px;font-size:11px;font-weight:700;letter-spacing:.34em;color:#8a93a3;line-height:2.2;}
.hd-heard b{color:#fff;font-weight:700;}
.hd-up{opacity:0;transform:translateY(28px);animation:hd-up 1.1s cubic-bezier(.2,.8,.2,1) forwards;}
@keyframes hd-up{to{opacity:1;transform:none}}
.hd-scroll{position:absolute;bottom:28px;left:50%;transform:translateX(-50%);z-index:2;width:1px;height:60px;
  background:linear-gradient(var(--vio2),transparent);animation:hd-pulse 2s ease-in-out infinite;}
@keyframes hd-pulse{0%,100%{opacity:.3}50%{opacity:1}}

/* TICKER */
.hd-ticker{background:#000;padding:34px 0;border-bottom:1px solid rgba(255,255,255,.06);}
.hd-ticker-k{text-align:center;font-size:11px;font-weight:700;letter-spacing:.42em;color:#6b7382;margin-bottom:14px;}
.hd-marquee{overflow:hidden;white-space:nowrap;-webkit-mask-image:linear-gradient(90deg,transparent,#000 10%,#000 90%,transparent);
  mask-image:linear-gradient(90deg,transparent,#000 10%,#000 90%,transparent);}
.hd-track{display:inline-block;animation:hd-left 55s linear infinite;}
.hd-track span{font-family:'Bebas Neue',sans-serif;font-size:54px;letter-spacing:.05em;color:rgba(255,255,255,.9);margin:0 34px;vertical-align:middle;}
.hd-track i{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--vio);box-shadow:0 0 14px var(--vio);vertical-align:middle;}

/* PROBLEM */
.hd-problem{background:radial-gradient(ellipse 60% 50% at 100% 0%,rgba(99,19,133,.25),transparent 70%),var(--bg);}
.hd-problem-head{max-width:900px;margin-bottom:70px;}
.hd-pains{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;}
.hd-pain{position:relative;padding:44px 34px 38px;background:linear-gradient(180deg,#0e111a,#08090e);border:1px solid #1c2230;
  border-radius:4px;overflow:hidden;transition:transform .4s ease,border-color .4s,box-shadow .4s;}
.hd-pain:hover{transform:translateY(-10px);border-color:var(--vio);box-shadow:0 30px 80px rgba(177,75,244,.25);}
.hd-pain-n{font-family:'Bebas Neue',sans-serif;font-size:120px;line-height:.8;color:transparent;-webkit-text-stroke:1.5px var(--vio);
  display:block;margin-bottom:22px;opacity:.9;}
.hd-pain h3{font-size:38px !important;margin-bottom:16px;}
.hd-pain p{font-size:16px;margin:0;}

/* FOUNDER */
.hd-founder{background:#08090e;}
.hd-founder-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:80px;align-items:center;}
.hd-founder .hd-quote{font-family:'Bebas Neue',sans-serif;font-size:clamp(60px,8vw,128px);line-height:.86 !important;color:#fff;margin:0 0 34px;}
.hd-quote em{font-style:normal;color:transparent;-webkit-text-stroke:2px #fff;}
.hd-founder p:not(.hd-quote){font-size:18px;}
.hd-sig{margin-top:30px;display:flex;align-items:center;gap:18px;}
.hd-sig-name{font-family:'Bebas Neue',sans-serif;font-size:34px;color:#fff;letter-spacing:.05em;line-height:1;}
.hd-sig-role{font-size:11px;font-weight:700;letter-spacing:.32em;color:var(--vio2);}
.hd-sig-line{width:60px;height:2px;background:linear-gradient(90deg,var(--vio),var(--blu));}
.hd-stats{display:grid;grid-template-columns:1fr 1fr;gap:2px;background:#1c2230;border:1px solid #1c2230;}
.hd-stat{background:#0b0d14;padding:40px 30px;}
.hd-stat b{display:block;font-family:'Bebas Neue',sans-serif;font-weight:400;font-size:84px;line-height:.9;
  background:linear-gradient(180deg,#fff,var(--vio2));-webkit-background-clip:text;background-clip:text;color:transparent;}
.hd-stat span{display:block;font-size:13px;line-height:1.5;color:var(--mute);margin-top:10px;}

/* NOW SHOWING */
.hd-showing{background:#000;padding:130px 0 110px;}
.hd-center{text-align:center;}
.hd-showing .hd-center p{max-width:620px;margin:22px auto 0;}
.hd-car{position:relative;margin-top:60px;}
.hd-car-track{display:flex;gap:24px;overflow-x:auto;scroll-snap-type:x mandatory;scroll-behavior:smooth;padding:40px 8vw 60px;
  scrollbar-width:none;-webkit-mask-image:linear-gradient(90deg,transparent,#000 7%,#000 93%,transparent);
  mask-image:linear-gradient(90deg,transparent,#000 7%,#000 93%,transparent);}
.hd-car-track::-webkit-scrollbar{display:none;}
.hd-card{flex:none;width:250px;margin:0;scroll-snap-align:center;position:relative;border-radius:8px;overflow:hidden;background:#0d1018;
  box-shadow:0 22px 60px rgba(0,0,0,.7);transition:transform .5s cubic-bezier(.2,.8,.2,1),box-shadow .5s;}
.hd-card img{display:block;width:100%;aspect-ratio:2/3;object-fit:cover;transition:transform .7s ease;}
.hd-card figcaption{position:absolute;left:0;right:0;bottom:0;padding:70px 18px 18px;background:linear-gradient(transparent,rgba(5,6,8,.96));
  transform:translateY(30%);opacity:0;transition:all .45s ease;}
.hd-card figcaption span{display:block;font-size:9px;font-weight:700;letter-spacing:.28em;color:var(--vio2);text-transform:uppercase;margin-bottom:6px;}
.hd-card figcaption strong{display:block;font-family:'Bebas Neue',sans-serif;font-weight:400;font-size:28px;color:#fff;line-height:.95;}
.hd-card:hover{transform:translateY(-14px) scale(1.06);box-shadow:0 34px 90px rgba(177,75,244,.5),0 0 0 1px rgba(192,132,252,.7);z-index:3;}
.hd-card:hover img{transform:scale(1.07);}
.hd-card:hover figcaption{transform:none;opacity:1;}
.hd-car-nav{position:absolute;top:50%;transform:translateY(-50%);z-index:5;width:60px;height:60px;border-radius:50%;
  border:1px solid rgba(255,255,255,.35);background:rgba(5,6,8,.75);color:#fff;font-size:28px;line-height:1;cursor:pointer;
  backdrop-filter:blur(6px);transition:all .25s;display:flex;align-items:center;justify-content:center;padding:0;}
.hd-car-nav:hover{background:var(--brand);border-color:var(--vio2);box-shadow:0 0 30px rgba(177,75,244,.7);}
.hd-car-prev{left:22px;}.hd-car-next{right:22px;}

/* CREDITS ROLL */
.hd-roll-wrap{max-width:760px;margin:80px auto 0;}
.hd-roll-k{text-align:center;font-size:11px;font-weight:700;letter-spacing:.42em;color:#6b7382;}
.hd-roll{position:relative;height:540px;overflow:hidden;margin-top:20px;
  -webkit-mask-image:linear-gradient(transparent,#000 15%,#000 85%,transparent);mask-image:linear-gradient(transparent,#000 15%,#000 85%,transparent);}
.hd-roll-in{animation:hd-roll 120s linear infinite;text-align:center;}
.hd-roll:hover .hd-roll-in{animation-play-state:paused;}
.hd-roll h5{font-size:20px !important;letter-spacing:.38em !important;color:var(--vio2) !important;margin:60px 0 16px !important;}
.hd-roll div div,.hd-roll-in>div{font-family:'Bebas Neue',sans-serif;font-size:36px;letter-spacing:.04em;color:#fff;line-height:1.3;}
@keyframes hd-roll{from{transform:translateY(0)}to{transform:translateY(-50%)}}

/* ROSTER */
.hd-roster{background:radial-gradient(ellipse 50% 60% at 0% 100%,rgba(56,189,248,.12),transparent 70%),var(--bg);}
.hd-roster-head{display:flex;justify-content:space-between;align-items:flex-end;gap:40px;margin-bottom:60px;flex-wrap:wrap;}
.hd-roster-head p{max-width:420px;margin:0;}
.hd-labels{display:grid;grid-template-columns:repeat(6,1fr);gap:22px;}
.hd-label{grid-column:span 2;position:relative;display:flex;flex-direction:column;padding:40px 32px 34px;min-height:320px;border-radius:4px;
  background:linear-gradient(#0c0f17,#0c0f17) padding-box,linear-gradient(140deg,#2a3142,#141924) border-box;border:1px solid transparent;
  transition:all .45s ease;overflow:hidden;}
.hd-label:nth-child(4),.hd-label:nth-child(5){grid-column:span 3;}
.hd-label::before{content:"";position:absolute;inset:0;opacity:0;transition:opacity .45s;
  background:radial-gradient(ellipse 80% 70% at 100% 0%,rgba(177,75,244,.28),transparent 70%);}
.hd-label:hover{transform:translateY(-8px);background:linear-gradient(#0c0f17,#0c0f17) padding-box,linear-gradient(140deg,var(--vio),var(--blu)) border-box;
  box-shadow:0 30px 80px rgba(177,75,244,.25);}
.hd-label:hover::before{opacity:1;}
.hd-label>*{position:relative;}
.hd-label-k{font-size:10px;font-weight:700;letter-spacing:.32em;color:var(--vio2);text-transform:uppercase;margin-bottom:18px;}
.hd-label h3{font-size:48px !important;margin-bottom:16px;}
.hd-label p{font-size:15px;flex:1;}
.hd-label-cta{font-size:11px;font-weight:700;letter-spacing:.25em;text-transform:uppercase;color:#fff;}
.hd-label-cta b{display:inline-block;transition:transform .3s;color:var(--vio2);}
.hd-label:hover .hd-label-cta b{transform:translateX(8px);}

/* DEEP CUTS */
.hd-deep{background:#000;}
.hd-deep-list{margin-top:60px;border-top:1px solid #1c2230;}
.hd-deep-row{display:grid;grid-template-columns:120px 1fr 1.1fr;gap:40px;align-items:center;padding:46px 0;border-bottom:1px solid #1c2230;
  transition:background .4s,padding .4s;}
.hd-deep-row:hover{background:linear-gradient(90deg,rgba(177,75,244,.12),transparent);padding-left:24px;}
.hd-deep-n{font-family:'Bebas Neue',sans-serif;font-size:72px;color:transparent;-webkit-text-stroke:1.5px #3a4256;line-height:1;transition:-webkit-text-stroke-color .4s;}
.hd-deep-row:hover .hd-deep-n{-webkit-text-stroke-color:var(--vio);}
.hd-deep-row h3{font-size:clamp(40px,4.5vw,64px) !important;}
.hd-deep-row small{display:block;font-size:11px;font-weight:700;letter-spacing:.32em;color:var(--vio2);margin-bottom:10px;}
.hd-deep-row p{margin:0;}
.hd-deep-cta{margin-top:50px;text-align:center;}

/* SUPERVISION */
.hd-sup{background:linear-gradient(115deg,#3b0a59 0%,#14081f 48%,#05243b 100%);overflow:hidden;}
.hd-sup::after{content:"";position:absolute;inset:0;pointer-events:none;opacity:.35;
  background:repeating-linear-gradient(90deg,transparent 0 120px,rgba(255,255,255,.03) 120px 121px);}
.hd-sup-grid{position:relative;z-index:1;display:grid;grid-template-columns:1.3fr .7fr;gap:60px;align-items:center;}
.hd-sup p{color:#e6dcef;font-size:19px;max-width:640px;}
.hd-sup-side{border-left:1px solid rgba(255,255,255,.2);padding-left:44px;}
.hd-sup-side li{list-style:none;font-family:'Bebas Neue',sans-serif;font-size:34px;color:#fff;line-height:1.35;}
.hd-sup-side ul{margin:0 0 30px;padding:0;}
.hd-sup .hd-eb{color:#e9d5ff;}

/* SUB-PUBLISHERS */
.hd-subs{background:var(--bg);padding:90px 0;text-align:center;border-top:1px solid #12161f;}
.hd-subs h4{font-size:38px !important;margin-bottom:22px;}
.hd-subs p{font-size:15px;letter-spacing:.06em;line-height:2.1;max-width:980px;margin:0 auto;color:#c7cdd8;}
.hd-subs i{color:var(--vio);font-style:normal;margin:0 8px;}

@media(max-width:980px){
  .hd-pains,.hd-founder-grid,.hd-sup-grid{grid-template-columns:1fr;}
  .hd-founder-grid{gap:50px;}
  .hd-labels{grid-template-columns:1fr;}
  .hd-label,.hd-label:nth-child(4),.hd-label:nth-child(5){grid-column:auto;min-height:0;}
  .hd-deep-row{grid-template-columns:70px 1fr;}
  .hd-deep-row p{grid-column:2;}
  .hd-sup-side{border-left:0;padding-left:0;}
  .hd-links a:not(.hd-btn){display:none;}
}
@media(max-width:640px){
  .hd{font-size:16px;}
  .hd-sec{padding:90px 0;}
  .hd-wrap{padding:0 20px;}
  .hd-nav{padding:14px 18px;}.hd-nav.solid{padding:10px 18px;}
  .hd-logo{font-size:24px;}
  .hd-hero{border-width:14px;}
  .hd-wall-row img{width:118px;height:176px;}
  .hd-hero .hd-sub{font-size:17px;}
  .hd-ctas .hd-btn{width:100%;justify-content:center;}
  .hd-card{width:180px;}
  .hd-card figcaption{transform:none;opacity:1;padding-top:50px;}
  .hd-card figcaption strong{font-size:22px;}
  .hd-car-nav{display:none;}
  .hd-track span{font-size:36px;margin:0 20px;}
  .hd-stat b{font-size:60px;}
  .hd-roll{height:440px;}
  .hd-roll-in>div{font-size:28px;}
  .hd-deep-n{font-size:50px;}
}
@media(prefers-reduced-motion:reduce){
  .hd-wall-row,.hd-track,.hd-beam,.hd-roll-in,.hd-scroll{animation:none !important;}
  .hd-up,.hd-reveal{opacity:1 !important;transform:none !important;animation:none !important;}
}
"""

JS = r"""
(function(){
  var root=document.getElementById('hdmn');if(!root)return;
  // nav goes solid on scroll
  var nav=root.querySelector('.hd-nav');
  function onScroll(){nav.classList.toggle('solid',window.scrollY>60);}
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();
  // reveal on scroll
  var els=root.querySelectorAll('.hd-reveal');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target);}});},{threshold:.15});
    els.forEach(function(el){io.observe(el);});
  }else{els.forEach(function(el){el.classList.add('in');});}
  // count-up stats
  root.querySelectorAll('[data-count]').forEach(function(el){
    var end=parseFloat(el.getAttribute('data-count')),suf=el.getAttribute('data-suffix')||'',done=false;
    var o=new IntersectionObserver(function(es){if(es[0].isIntersecting&&!done){done=true;var t0=null;
      function f(t){if(!t0)t0=t;var p=Math.min((t-t0)/1600,1),v=Math.round(end*(1-Math.pow(1-p,3)));el.textContent=v+suf;if(p<1)requestAnimationFrame(f);}
      requestAnimationFrame(f);}},{threshold:.5});o.observe(el);
  });
  // poster carousel
  var car=root.querySelector('.hd-car'),tr=car.querySelector('.hd-car-track');
  function step(){var c=tr.querySelector('.hd-card');return c?(c.offsetWidth+24)*2:500;}
  function next(){if(tr.scrollLeft+tr.clientWidth>=tr.scrollWidth-10){tr.scrollTo({left:0});}else{tr.scrollBy({left:step()});}}
  function prev(){if(tr.scrollLeft<=5){tr.scrollTo({left:tr.scrollWidth});}else{tr.scrollBy({left:-step()});}}
  car.querySelector('.hd-car-next').addEventListener('click',next);
  car.querySelector('.hd-car-prev').addEventListener('click',prev);
  var paused=false;
  car.addEventListener('mouseenter',function(){paused=true;});
  car.addEventListener('mouseleave',function(){paused=false;});
  car.addEventListener('touchstart',function(){paused=true;},{passive:true});
  if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    setInterval(function(){if(!paused&&!document.hidden)next();},3000);
  }
})();
"""

TEMPLATE = """<style>{css}</style>
<div class="hd" id="hdmn">

<nav class="hd-nav">
  <a class="hd-logo" href="#hdmn">HD MUSIC <b>NOW</b></a>
  <div class="hd-links">
    <a href="#hd-credits">Credits</a><a href="#hd-roster">Catalogs</a><a href="#hd-sup">Supervision</a><a href="{contact}">Contact</a>
    <a class="hd-btn p" href="{catalog}" target="_blank" rel="noopener">&#9654; Search</a>
  </div>
</nav>

<header class="hd-hero">
  <div class="hd-wall" aria-hidden="true">{wall}</div>
  <div class="hd-shade"></div><div class="hd-glow"></div><div class="hd-beam"></div>
  <div class="hd-hero-in">
    <span class="hd-eb hd-up">In a world where the deadline was yesterday&hellip;</span>
    <h1 class="hd-grad hd-up" style="animation-delay:.2s">Find it.<br>Clear it.<br>Cut to picture.</h1>
    <p class="hd-sub hd-up" style="animation-delay:.45s">Music, trailer cues and 500,000+ sound effects, from a team that's sat in the music supervisor's chair for over two decades.</p>
    <div class="hd-ctas hd-up" style="animation-delay:.7s">
      <a class="hd-btn p" href="{catalog}" target="_blank" rel="noopener">&#9654; Search the Catalog</a>
      <a class="hd-btn o" href="{contact}">Send Us a Brief</a>
    </div>
    <p class="hd-heard hd-up" style="animation-delay:1s">AS HEARD IN&nbsp; <b>THE FALL GUY &middot; GREY'S ANATOMY &middot; DAREDEVIL: BORN AGAIN &middot; SUPERMAN (TRAILER)</b></p>
  </div>
  <div class="hd-scroll"></div>
</header>

<section class="hd-ticker">
  <div class="hd-ticker-k">TRUSTED BY STUDIOS, NETWORKS &amp; STREAMERS</div>
  <div class="hd-marquee"><div class="hd-track">{ticker}</div></div>
</section>

<section class="hd-sec hd-problem">
  <div class="hd-wrap">
    <div class="hd-problem-head hd-reveal">
      <span class="hd-eb">The Problem</span>
      <h2 class="hd-h2">Every supervisor has <span class="hd-grad">seen this movie.</span></h2>
    </div>
    <div class="hd-pains">
      <div class="hd-pain hd-reveal"><span class="hd-pain-n">01</span><h3>The Deadline</h3><p>The cut changed. The temp is loved. Air date doesn't move. You need real options today, not after another week of digging.</p></div>
      <div class="hd-pain hd-reveal" style="transition-delay:.15s"><span class="hd-pain-n">02</span><h3>The Clearance</h3><p>The perfect song dies at the last minute over split ownership, a slow publisher or a surprise fee.</p></div>
      <div class="hd-pain hd-reveal" style="transition-delay:.3s"><span class="hd-pain-n">03</span><h3>The Impossible Brief</h3><p>Period-authentic vintage. A regional folk recording. The karaoke version of a hit. The exact door creak. Most libraries just don't have it.</p></div>
    </div>
  </div>
</section>

<section class="hd-sec hd-founder">
  <div class="hd-wrap hd-founder-grid">
    <div class="hd-reveal">
      <span class="hd-eb">The Fix</span>
      <p class="hd-quote">I've sat in <em>both</em> chairs.</p>
      <p>For more than twenty years I've worked as a sync agent pitching music, and for more than twenty years as a music supervisor searching for it. From both sides I kept seeing the same problem: supervisors buried in music that doesn't fit, can't clear in time, or simply doesn't exist in the libraries they use.</p>
      <p>HD Music Now is my answer. Curated catalogs, hard-to-find specialty music, half a million sound effects, and a supervisor's ear on every request, so you get what the scene needs and get back to the edit.</p>
      <div class="hd-sig"><div class="hd-sig-line"></div><div><div class="hd-sig-name">Jody Friedman</div><div class="hd-sig-role">FOUNDER &middot; MUSIC SUPERVISOR</div></div></div>
    </div>
    <div class="hd-stats hd-reveal" style="transition-delay:.2s">
      <div class="hd-stat"><b data-count="20" data-suffix="+">20+</b><span>Years as a sync agent and as a music supervisor</span></div>
      <div class="hd-stat"><b data-count="500" data-suffix="K+">500K+</b><span>Sound effects from Sound Ideas, Hollywood Edge &amp; BOOM Library</span></div>
      <div class="hd-stat"><b data-count="50" data-suffix="+">50+</b><span>Recent credits across series, features, trailers &amp; docs</span></div>
      <div class="hd-stat"><b data-count="20" data-suffix=" YRS">20 YRS</b><span>Representing the Naxos classical, vintage &amp; world catalog</span></div>
    </div>
  </div>
</section>

<section class="hd-showing" id="hd-credits">
  <div class="hd-wrap hd-center hd-reveal">
    <span class="hd-eb">Now Showing</span>
    <h2 class="hd-h2">Heard <span class="hd-grad">on</span></h2>
    <p>Features, series, trailers, docs and campaigns. Hover a poster for the credit.</p>
  </div>
  <div class="hd-car">
    <button class="hd-car-nav hd-car-prev" aria-label="Previous posters">&#8249;</button>
    <div class="hd-car-track">{cards}</div>
    <button class="hd-car-nav hd-car-next" aria-label="Next posters">&#8250;</button>
  </div>
  <div class="hd-roll-wrap hd-reveal">
    <div class="hd-roll-k">THE FULL CREDITS</div>
    <div class="hd-roll"><div class="hd-roll-in"><div>{roll}</div><div aria-hidden="true">{roll}</div></div></div>
  </div>
</section>

<section class="hd-sec hd-roster" id="hd-roster">
  <div class="hd-wrap">
    <div class="hd-roster-head hd-reveal">
      <div><span class="hd-eb">The Roster</span><h2 class="hd-h2">Five labels.<br><span class="hd-grad">One call.</span></h2></div>
      <p>From a needle-drop for a cold open to a trailer cue that hits on the cut.</p>
    </div>
    <div class="hd-labels">{labels}</div>
  </div>
</section>

<section class="hd-sec hd-deep">
  <div class="hd-wrap">
    <div class="hd-reveal"><span class="hd-eb">The Deep Cuts</span><h2 class="hd-h2">The music no one<br><span class="hd-grad">else can find.</span></h2></div>
    <div class="hd-deep-list">
      <div class="hd-deep-row hd-reveal"><span class="hd-deep-n">01</span><div><small>CLASSICAL &middot; VINTAGE &middot; WORLD</small><h3>Naxos</h3></div><p>One of the world's deepest classical, vintage and world music catalogs. We've represented Naxos for twenty years.</p></div>
      <div class="hd-deep-row hd-reveal"><span class="hd-deep-n">02</span><div><small>KARAOKE &middot; COVERS</small><h3>Covered Records</h3></div><p>The largest karaoke catalog in the world. Instrumental and sound-alike versions of the songs your scene is reaching for.</p></div>
      <div class="hd-deep-row hd-reveal"><span class="hd-deep-n">03</span><div><small>500,000+ SOUND EFFECTS</small><h3>Sound Ideas &middot; Hollywood Edge &middot; BOOM</h3></div><p>Sound design from two of the largest SFX distributors in the world, from foley and ambiences to cinematic impacts.</p></div>
    </div>
    <div class="hd-deep-cta hd-reveal"><a class="hd-btn p" href="{contact}">Request a Specialty Search</a></div>
  </div>
</section>

<section class="hd-sec hd-sup" id="hd-sup">
  <div class="hd-wrap hd-sup-grid">
    <div class="hd-reveal">
      <span class="hd-eb">Music Supervision &amp; Clearance</span>
      <h2 class="hd-h2" style="margin-bottom:28px">Need more<br>than a track?</h2>
      <p>Bring us in as your music supervisor. We source, negotiate and clear music for films, TV, web series and trailers, and help brands define one consistent sound across everything they make.</p>
      <div class="hd-ctas" style="justify-content:flex-start;margin-top:34px">
        <a class="hd-btn p" href="{contact}">Start a Project</a>
        <a class="hd-btn o" href="{imdb}" target="_blank" rel="noopener">View IMDb Credits</a>
      </div>
    </div>
    <div class="hd-sup-side hd-reveal" style="transition-delay:.2s">
      <ul><li>Film</li><li>Television</li><li>Trailers &amp; Promos</li><li>Web Series</li><li>Brands</li></ul>
    </div>
  </div>
</section>

<section class="hd-subs">
  <div class="hd-wrap hd-reveal">
    <span class="hd-eb">Worldwide Representation</span>
    <h4>International sub-publishers</h4>
    <p>{subpubs}</p>
  </div>
</section>

</div>
<script>{js}</script>
"""


def main():
    embed = build(CDN_BASE)
    (HERE / "kajabi-embed.html").write_text(embed)
    preview = build("posters/")
    (HERE / "preview.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>HD Music Now — Homepage Preview</title></head>'
        '<body style="margin:0;background:#050608">' + preview + "</body></html>")
    print(f"kajabi-embed.html: {len(embed):,} chars (CDN ref: {CDN_REF})")


if __name__ == "__main__":
    main()
