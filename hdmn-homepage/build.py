"""Build the HD Music Now homepage embed.

Outputs:
  preview.html       standalone page for local review (posters loaded from ./posters)
  kajabi-embed.html  full embed, can be pasted into a single Kajabi Code block (posters loaded from jsDelivr)
  hdmn.js            the same embed as a script; the Kajabi Code block loads it with:
                       <div id="hdmn-mount"></div>
                       <script src="https://mayadex853.github.io/Dashboards/hdmn-homepage/hdmn.js"></script>

Usage: python3 build.py   (then merge to main; GitHub Pages serves main, so no Kajabi edit is needed)
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
CDN_REF = sys.argv[1] if len(sys.argv) > 1 else "main"
# Posters are served from GitHub Pages (main branch); raw.githubusercontent.com is the automatic fallback
# if an image fails.
CDN_BASE = "https://mayadex853.github.io/Dashboards/hdmn-homepage/posters/"
FALLBACK_BASE = f"https://raw.githubusercontent.com/mayadex853/Dashboards/{CDN_REF}/hdmn-homepage/posters/"

# Google Sheet Jody edits; the page reads it live (falls back to the built-in data if unreachable).
LOGO_URL = "https://kajabi-storefronts-production.kajabi-cdn.com/kajabi-storefronts-production/themes/2149398140/settings_images/5pvwVfsaSKOnEoufXhp5_HDMN_3D.png"

SHEET_ID = "1CBPFj3m63C8k471r3ONv7FZtacY-HdBJon5hwO40bjQ"

CATALOG_URL = "https://hdmusicnow.sourceaudio.com/#!label?l=1222458&page=albums"
CONTACT_ANCHOR = "#section-1792000000008"
IMDB_URL = "https://www.imdb.com/name/nm3112237/"

from credits import BRANDS, CATEGORIES, FEATURES, PRESS, STAGE, SUPERVISION  # noqa: E402

# Poster manifest written by the poster fetch step: [{title, slug, kind, net, group}]
# group is "placement" (music licensed into the project) or "supervision" (Jody's supervision/clearance credit).
MANIFEST = json.loads((HERE / "posters" / "manifest.json").read_text())
PLACEMENT_POSTERS = [p for p in MANIFEST if p["group"] == "placement"]
SUPERVISION_POSTERS = [p for p in MANIFEST if p["group"] == "supervision"]

CLIENTS = ["Netflix", "HBO", "AMC", "Marvel", "Disney+", "Apple TV+", "Amazon", "Hulu", "FX", "Showtime", "ABC",
           "NBC", "CBS", "FOX", "Universal", "Warner Bros.", "Sony", "Paramount", "Lionsgate", "Focus Features", "A24",
           "Searchlight", "The CW", "Starz", "TNT", "E!", "MTV", "BET", "Nickelodeon", "Adult Swim"]

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
    ("For UK Productions", "HDMN Royalty Music UK",
     "MCPS & PRS approved. Our home for productions based in the UK.",
     "Visit Royalty Music UK", "https://www.royaltymusicuk.com"),
]

# "Search Catalog" opens a short finder; each answer routes to the right catalog (new tab) or to the brief form.
SOURCEAUDIO_URL = "https://hdmusicnow.sourceaudio.com/"
FINDER = [
    ("Latin Music", "Ocho Music Group", "https://www.ochomusicgroup.com"),
    ("Trailer Music", "Collaborate Music", "https://www.collaboratemusic.com"),
    ("Vintage and/or Ethnic Music", "Stacks to Tracks on APM", "https://www.apmmusic.com/libraries/stacks-to-tracks-(strx)"),
    ("SFX", "500K+ effects on SourceAudio", SOURCEAUDIO_URL),
    ("UK Production (MCPS & PRS)", "HDMN Royalty Music UK", "https://www.royaltymusicuk.com"),
    ("Other", "Tell us what you need", ""),
]

# Ethan Bloom: Jody's feature as Producer & Music Supervisor (sources: Menemsha Films, festival listings)
EB_TRAILER = "P_yeWY0b_RE"
EB_SHOWTIMES = "https://www.menemshafilms.com/ethan-bloom"
EB_FESTIVALS = [
    "Miami Film Festival \u00b7 World Premiere", "Sedona International Film Festival \u00b7 Award Winner",
    "Austin Film Festival", "Boston Jewish Film Festival", "San Diego Jewish Film Festival",
    "Santa Barbara Jewish Film Festival", "Key Biscayne Film Festival", "Palm Springs Jewish Film Festival",
    "East Bay International Jewish Film Festival", "New Jersey Jewish Film Festival", "Jewish Film Festival of Dallas",
    "JFilm Festival Pittsburgh", "St. Louis Jewish Film Festival", "Lenore Marwil Jewish Film Festival (Detroit)",
    "Boca Raton Jewish Film Festival", "Dayton Jewish International Film Festival", "Charlotte Jewish Film Festival",
    "Cincinnati Jewish & Israeli Film Festival", "Nashville Jewish Film Festival", "New Hampshire Jewish Film Festival",
    "Rehoboth Beach Jewish Film Festival", "Stowe Jewish Film Festival", "Wilmington Jewish Film Festival",
    "Michiana Jewish Film Festival", "Fresno Jewish Film Series", "Jewish International Film Festival (Australia)",
]
EB_QUOTES = [
    ("Paints a raw and authentic portrait of adolescence.", "The Austin Chronicle"),
    ("A simple story, big heart, and a lasting impression.", "True View Reviews"),
    ("5 stars for tweens and teens to Grandma and Grandpa.", "ACED Magazine"),
]

SUBPUBS = ["HDMN Royalty Music UK", "BMG", "Sonoton", "ViMusica", "Moodoofind", "Red Igloo", "Kouros",
           "Yellowgroove", "Miles of Musik", "Apollo Music"]

e = html.escape


def _min(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return re.sub(r"\s*\n\s*", "", css).strip()


def poster_src(slug, base):
    return f"{base}{slug}.jpg"


def _card(p, base, caption):
    return (f'<figure class="hd-card"><img src="{poster_src(p["slug"], base)}" alt="{e(p["title"])} poster" loading="lazy">'
            f'<figcaption><span>{caption}</span><strong>{e(p["title"])}</strong></figcaption></figure>')


def _marquee(items):
    return "".join(f"<span>{e(c)}</span><i></i>" for c in items) * 2


def build(base):
    sup_roles = {t: (role, year) for t, role, year, _ in SUPERVISION}

    cards = "".join(_card(p, base, f'{e(p["kind"])} &middot; {e(p["net"])}') for p in PLACEMENT_POSTERS)
    def sup_role(title):  # poster titles may be short forms of the IMDb title
        return sup_roles.get(title) or next((v for t, v in sup_roles.items() if t.startswith(title)), None)

    sup_cards = "".join(
        _card(p, base, f'{e(sup_role(p["title"])[0])} &middot; {sup_role(p["title"])[1]}')
        for p in SUPERVISION_POSTERS if sup_role(p["title"]))

    tabs = "".join(
        f'<button class="hd-tab{" on" if i == 0 else ""}" data-tab="{i}">{e(name)} <sup>{len(items)}</sup></button>'
        for i, (name, items) in enumerate(CATEGORIES))
    panels = "".join(
        f'<ul class="hd-panel{" on" if i == 0 else ""}" data-panel="{i}">'
        + "".join(f"<li><b>{e(t)}</b>{f'<span>{e(n)}</span>' if n else ''}</li>" for t, n in items)
        + "</ul>"
        for i, (_, items) in enumerate(CATEGORIES))
    total_placements = len({t for _, items in CATEGORIES for t, _ in items})

    sup_rows = "".join(
        f'<li><span class="hd-yr">{year}</span><b>{e(t)}</b><span class="hd-role">{e(role)}</span>'
        f'<span class="hd-kind">{e(kind)}</span></li>'
        for t, role, year, kind in SUPERVISION)

    labels = "".join(
        f'<a class="hd-label hd-reveal" href="{e(url)}" target="_blank" rel="noopener">'
        f'<span class="hd-label-k">{e(k)}</span><h3>{e(name)}</h3><p>{e(desc)}</p>'
        f'<span class="hd-label-cta">{e(cta)} <b>&rarr;</b></span></a>'
        for k, name, desc, cta, url in LABELS)

    subpubs = " <i>&middot;</i> ".join(e(s) for s in SUBPUBS)
    def li(items):
        return "".join(f"<li><span>{e(name)}</span><em>{e(note)}</em></li>" for name, note in items)
    speaking, press, features = li(STAGE), li(PRESS), li(FEATURES)
    all_slugs = ",".join(p["slug"] for p in MANIFEST)
    eb_fest = _marquee(EB_FESTIVALS)
    eb_quotes = "".join(f'<figure class="hd-eb-q hd-reveal"><blockquote>&ldquo;{e(q)}&rdquo;</blockquote><figcaption>{e(src)}</figcaption></figure>' for q, src in EB_QUOTES)
    finder = "".join(
        f'<button type="button" class="hd-fopt" data-label="{e(label)}" data-url="{e(url)}">'
        f'<b>{e(label)}</b><small>{e(dest)}</small><i>{"&#8599;" if url else "&rarr;"}</i></button>'
        for label, dest, url in FINDER)

    return TEMPLATE.format(
        css=_min(CSS), ticker=_marquee(CLIENTS), brands=_marquee(BRANDS), cards=cards, sup_cards=sup_cards,
        tabs=tabs, panels=panels, total="10,000+", total_n=10000, sup_rows=sup_rows,
        sup_total=len(SUPERVISION), labels=labels, subpubs=subpubs, speaking=speaking, press=press, features=features,
        catalog=e(CATALOG_URL), contact=CONTACT_ANCHOR, imdb=IMDB_URL, logo=LOGO_URL, finder=finder, eb_fest=eb_fest, eb_quotes=eb_quotes, eb_n=len(EB_FESTIVALS), eb_showtimes=EB_SHOWTIMES, eb_trailer=EB_TRAILER, base=base, sourceaudio=e(SOURCEAUDIO_URL),
        js=JS.replace("__CONTACT__", CONTACT_ANCHOR).replace("__SHEET__", SHEET_ID).replace("__FALLBACK__", FALLBACK_BASE if base == CDN_BASE else "").replace("__BASE__", base).replace("__SLUGS__", all_slugs))


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

/* NAV (replaces the Kajabi header on this page) */
header.header{display:none !important;}
.hd-nav{position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:9999;width:min(1240px,calc(100% - 32px));
  display:flex;align-items:center;gap:22px;padding:10px 10px 10px 16px;border-radius:999px;
  background:rgba(8,9,14,.55);backdrop-filter:blur(18px) saturate(1.4);-webkit-backdrop-filter:blur(18px) saturate(1.4);
  border:1px solid rgba(255,255,255,.1);box-shadow:0 10px 40px rgba(0,0,0,.45);transition:background .35s,box-shadow .35s,top .35s;}
.hd-nav.solid,.hd-nav.open{background:rgba(8,9,14,.94);box-shadow:0 14px 50px rgba(0,0,0,.6),0 0 0 1px rgba(177,75,244,.25);}
.hd-nav-logo{display:flex;align-items:center;gap:10px;flex:none;color:#fff !important;}
.hd-nav-logo img{width:40px;height:40px;border-radius:50%;filter:drop-shadow(0 0 10px rgba(177,75,244,.6));}
.hd-nav-logo span{font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:.1em;line-height:1;}
.hd-nav-links{display:flex;align-items:center;gap:4px;margin:0 auto;}
.hd-nav-links a{position:relative;padding:10px 14px;border-radius:999px;font-size:11px;font-weight:700;letter-spacing:.22em;
  text-transform:uppercase;color:#cfd4de !important;transition:color .2s,background .2s;white-space:nowrap;}
.hd-nav-links a:hover{color:#fff !important;background:rgba(255,255,255,.06);}
.hd-nav-links a.on{color:#fff !important;background:rgba(177,75,244,.22);box-shadow:inset 0 0 0 1px rgba(192,132,252,.45);}
.hd-nav .hd-btn{padding:13px 20px;font-size:11px;flex:none;}
.hd-nav-tog{display:none;flex:none;width:44px;height:44px;border-radius:50%;border:1px solid rgba(255,255,255,.2);background:transparent;
  cursor:pointer;position:relative;}
.hd-nav-tog i{position:absolute;left:13px;right:13px;height:2px;background:#fff;transition:transform .3s,opacity .3s;}
.hd-nav-tog i:nth-child(1){top:15px}.hd-nav-tog i:nth-child(2){top:21px}.hd-nav-tog i:nth-child(3){top:27px}
.hd-nav.open .hd-nav-tog i:nth-child(1){transform:translateY(6px) rotate(45deg)}
.hd-nav.open .hd-nav-tog i:nth-child(2){opacity:0}
.hd-nav.open .hd-nav-tog i:nth-child(3){transform:translateY(-6px) rotate(-45deg)}
.hd [id^="hd-"]{scroll-margin-top:96px;}
@media(max-width:1100px){.hd-nav-links a{padding:10px 9px;letter-spacing:.14em}}
@media(max-width:960px){
  .hd-nav{top:10px;width:calc(100% - 20px);border-radius:28px;flex-wrap:wrap;gap:10px;padding:8px 8px 8px 12px;}
  .hd-nav-logo span{display:none}
  .hd-nav .hd-btn{margin-left:auto;padding:12px 16px;font-size:10px;}
  .hd-nav-tog{display:block}
  .hd-nav-links{order:3;width:100%;flex-direction:column;align-items:stretch;gap:2px;margin:0;max-height:0;overflow:hidden;
    transition:max-height .4s ease,padding .4s ease;}
  .hd-nav.open .hd-nav-links{max-height:420px;padding:6px 0 8px;}
  .hd-nav-links a{padding:14px 12px;font-size:12px;letter-spacing:.2em;}
}
@media(max-width:380px){.hd-nav .hd-btn{display:none}.hd-nav-tog{margin-left:auto}}

/* ETHAN BLOOM */
.hd-ethan{position:relative;overflow:hidden;padding:140px 0 0;background:#06070b;}
.hd-eb-bg{position:absolute;inset:0;background-size:cover;background-position:center 30%;opacity:.28;filter:saturate(1.1);}
.hd-ethan::before{content:"";position:absolute;inset:0;z-index:0;background:linear-gradient(90deg,#06070b 8%,rgba(6,7,11,.75) 45%,rgba(6,7,11,.9)),linear-gradient(0deg,#06070b,transparent 40%);}
.hd-eb-grid{position:relative;z-index:1;display:grid;grid-template-columns:.8fr 1.2fr;gap:80px;align-items:center;}
.hd-eb-play{display:block;position:relative;width:100%;padding:0;border:0;background:none;cursor:pointer;border-radius:6px;overflow:hidden;
  box-shadow:0 40px 120px rgba(0,0,0,.7),0 0 0 1px rgba(255,255,255,.08);transform:rotate(-2deg);transition:transform .5s cubic-bezier(.2,.8,.2,1),box-shadow .5s;}
.hd-eb-play img{display:block;width:100%;height:auto;}
.hd-eb-play:hover{transform:rotate(0) scale(1.02);box-shadow:0 50px 140px rgba(0,0,0,.8),0 0 80px rgba(177,75,244,.45);}
.hd-eb-playbtn{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:88px;height:88px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  background:rgba(123,31,162,.88);color:#fff;font-size:30px;padding-left:6px;box-shadow:0 0 60px rgba(177,75,244,.8);transition:transform .3s;}
.hd-eb-play:hover .hd-eb-playbtn{transform:translate(-50%,-50%) scale(1.12);}
.hd-laurel{margin:34px auto 0;max-width:340px;text-align:center;position:relative;padding:18px 26px 16px;color:#f5e9c8;
  border:1px solid rgba(217,196,138,.55);border-radius:4px;background:linear-gradient(180deg,rgba(217,196,138,.12),rgba(217,196,138,.02));}
.hd-laurel::before{content:"\2605";position:absolute;top:-12px;left:50%;transform:translateX(-50%);padding:0 10px;background:#06070b;color:#d9c48a;font-size:16px;line-height:24px;}
.hd-laurel span{display:block;font-size:10px;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:#d9c48a;}
.hd-laurel b{display:block;font-family:'Bebas Neue',sans-serif;font-weight:400;font-size:30px;letter-spacing:.04em;line-height:1.05;margin:4px 0;color:#fff;}
.hd-eb-copy .hd-h2{margin-bottom:8px;}
.hd-eb-role{font-size:13px !important;font-weight:700;letter-spacing:.3em;text-transform:uppercase;color:#e9d5ff;margin:0 0 26px;}
.hd-eb-role b{color:#fff;}
.hd-eb-log{font-size:20px;line-height:1.55;color:#d7dce5;max-width:640px;}
.hd-eb-cred{font-size:14px;line-height:1.8;color:#8d95a5;margin:18px 0 30px;}
.hd-eb-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:2px;background:#1c2230;border:1px solid #1c2230;margin-bottom:34px;max-width:620px;}
.hd-eb-stats div{background:#0b0d14;padding:20px 22px;}
.hd-eb-stats b{display:block;font-family:'Bebas Neue',sans-serif;font-weight:400;font-size:46px;line-height:1;color:#fff;}
.hd-eb-stats span{font-size:12px;letter-spacing:.06em;color:#9aa3b2;}
.hd-eb-la{margin-top:30px;max-width:640px;padding:20px 24px;border-left:3px solid var(--vio);background:rgba(177,75,244,.1);border-radius:0 8px 8px 0;}
.hd-eb-la[hidden]{display:none;}
.hd-eb-la-k{display:block;font-size:11px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:var(--vio2);margin-bottom:8px;}
.hd-eb-la p{margin:0;font-size:15px;color:#e5e7eb;}
.hd-eb-la b{color:#fff;}
.hd-eb-la .hd-eb-la-s{margin-top:6px;font-size:13px;color:#9aa3b2;}
.hd-eb-quotes{position:relative;z-index:1;display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:100px;}
.hd-eb-q{margin:0;padding:30px 30px 26px;border:1px solid #1c2230;background:rgba(11,13,20,.8);border-radius:4px;}
.hd-eb-q blockquote{margin:0 0 16px;font-family:'Bebas Neue',sans-serif;font-size:30px;line-height:1.1;letter-spacing:.01em;color:#fff;}
.hd-eb-q figcaption{font-size:11px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:var(--vio2);}
.hd-eb-fest{position:relative;z-index:1;margin-top:90px;}
.hd-trailer{position:fixed;inset:0;z-index:10001;display:flex;align-items:center;justify-content:center;padding:16px;}
.hd-trailer[hidden]{display:none;}
.hd-tr-box{position:relative;width:min(1100px,100%);animation:hd-pop .35s cubic-bezier(.2,.8,.2,1);}
.hd-tr-box .hd-f-x{top:-52px;right:0;}
.hd-tr-frame{position:relative;padding-top:56.25%;background:#000;border-radius:10px;overflow:hidden;box-shadow:0 40px 120px rgba(0,0,0,.8);}
.hd-tr-frame iframe{position:absolute;inset:0;width:100%;height:100%;border:0;}
@media(max-width:960px){
  .hd-ethan{padding-top:90px;}
  .hd-eb-grid{grid-template-columns:1fr;gap:40px;}
  .hd-eb-poster{max-width:380px;margin:0 auto;}
  .hd-eb-quotes{grid-template-columns:1fr;margin-top:60px;}
  .hd-eb-stats b{font-size:36px;}
  .hd-eb-stats div{padding:16px;}
}

/* FINDER */
.hd-finder{position:fixed;inset:0;z-index:10000;display:flex;align-items:center;justify-content:center;padding:16px;}
.hd-finder[hidden]{display:none;}
.hd-f-back{position:absolute;inset:0;background:rgba(3,4,8,.78);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);animation:hd-fade .3s ease;}
.hd-f-box{position:relative;width:min(640px,100%);max-height:calc(100vh - 32px);overflow:auto;padding:36px 40px 0;border-radius:22px;
  background:linear-gradient(180deg,#141022,#08090e);border:1px solid rgba(192,132,252,.3);
  box-shadow:0 40px 120px rgba(0,0,0,.7),0 0 80px rgba(177,75,244,.25);animation:hd-pop .35s cubic-bezier(.2,.8,.2,1);}
.hd-f-box h3{font-family:'Bebas Neue',sans-serif;font-weight:400;font-size:clamp(34px,5vw,46px);line-height:1;letter-spacing:.02em;color:#fff;margin:12px 0 24px;}
.hd-f-box p{color:#c3c9d4;font-size:16px;line-height:1.6;margin:0 0 26px;}
.hd-f-x{position:absolute;top:14px;right:14px;width:40px;height:40px;border-radius:50%;border:1px solid rgba(255,255,255,.2);
  background:transparent;color:#fff;font-size:24px;line-height:1;cursor:pointer;}
.hd-f-x:hover{background:rgba(255,255,255,.1);}
.hd-f-opts{display:grid;gap:8px;}
.hd-fopt{display:grid;grid-template-columns:1fr auto;align-items:center;gap:2px 16px;text-align:left;width:100%;padding:14px 22px;
  border-radius:14px;border:1px solid #2a3142;background:rgba(255,255,255,.03);color:#fff;cursor:pointer;transition:all .2s;font:inherit;}
.hd-fopt b{font-size:17px;font-weight:700;letter-spacing:.01em;}
.hd-fopt small{grid-row:2;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#8d95a5;}
.hd-fopt i{grid-row:1/3;grid-column:2;font-style:normal;font-size:20px;color:var(--vio2);transition:transform .2s;}
.hd-fopt:hover,.hd-fopt:focus-visible{border-color:rgba(192,132,252,.7);background:rgba(177,75,244,.14);transform:translateX(4px);outline:none;}
.hd-fopt:hover i{transform:translateX(4px);}
.hd-f-row{display:flex;flex-wrap:wrap;gap:12px;}
.hd-f-prev{margin-top:22px;background:none;border:0;color:#8d95a5;font:inherit;font-size:13px;letter-spacing:.1em;cursor:pointer;padding:0;}
.hd-f-prev:hover{color:#fff;}
.hd-f-brief{display:block;width:calc(100% + 80px);margin:24px -40px 0;padding:18px 40px;border:0;border-top:1px solid rgba(255,255,255,.08);
  background:rgba(177,75,244,.1);color:#e9dcff;font:inherit;font-size:14px;text-align:left;cursor:pointer;transition:background .2s;}
.hd-f-brief span{display:block;font-size:11px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--vio2);margin-bottom:4px;}
.hd-f-brief[hidden]{display:none;}
.hd-f-brief:hover{background:rgba(177,75,244,.22);}
@keyframes hd-fade{from{opacity:0}}
@keyframes hd-pop{from{opacity:0;transform:translateY(24px) scale(.97)}}
@media(max-width:600px){.hd-f-box{padding:38px 20px 0}.hd-f-brief{width:calc(100% + 40px);margin:26px -20px 0;padding:18px 20px}
  .hd-fopt{padding:15px 16px}.hd-f-row .hd-btn{width:100%;text-align:center}}

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
  radial-gradient(ellipse 58% 55% at 50% 52%,rgba(5,6,8,.92) 0%,rgba(5,6,8,.72) 60%,rgba(5,6,8,.4) 100%),
  linear-gradient(180deg,rgba(5,6,8,.85) 0%,rgba(5,6,8,0) 25%,rgba(5,6,8,0) 70%,rgba(5,6,8,1) 100%);}
.hd-glow{position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen;background:
  radial-gradient(ellipse 40% 45% at 10% 5%,rgba(177,75,244,.55),transparent 60%),
  radial-gradient(ellipse 40% 45% at 92% 98%,rgba(56,189,248,.4),transparent 60%);}
.hd-beam{position:absolute;top:-20%;left:62%;width:3px;height:140%;transform:rotate(22deg);pointer-events:none;
  background:linear-gradient(transparent,rgba(255,255,255,.55),transparent);box-shadow:0 0 140px 50px rgba(177,75,244,.22);
  animation:hd-beam 9s ease-in-out infinite alternate;}
@keyframes hd-beam{from{left:58%;opacity:.6}to{left:70%;opacity:1}}
.hd-hero-in{position:relative;z-index:2;text-align:center;padding:110px 24px 90px;max-width:1180px;}
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

/* rotating pain line */
.hd-pain-line{display:grid;min-height:1.2em;}
.hd-pl{grid-area:1/1;opacity:0;transform:translateY(10px);transition:opacity .6s ease,transform .6s ease;}
.hd-pl.on{opacity:1;transform:none;transition-delay:.55s;}
@media(max-width:640px){.hd-pain-line{min-height:2.6em;align-items:end;}}

/* TICKER */
.hd-ticker{background:#000;padding:34px 0;border-bottom:1px solid rgba(255,255,255,.06);}
.hd-ticker-k{text-align:center;font-size:11px;font-weight:700;letter-spacing:.42em;color:#6b7382;margin-bottom:14px;}
.hd-marquee{overflow:hidden;white-space:nowrap;-webkit-mask-image:linear-gradient(90deg,transparent,#000 10%,#000 90%,transparent);
  mask-image:linear-gradient(90deg,transparent,#000 10%,#000 90%,transparent);}
.hd-track{display:inline-block;animation:hd-left 55s linear infinite;}
.hd-track span{font-family:'Bebas Neue',sans-serif;font-size:54px;letter-spacing:.05em;color:rgba(255,255,255,.9);margin:0 34px;vertical-align:middle;}
.hd-track.rev{animation-name:hd-right;}
.hd-brands{border-top:1px solid rgba(255,255,255,.06);}
.hd-track i{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--vio);box-shadow:0 0 14px var(--vio);vertical-align:middle;}

/* PROBLEM */
.hd-problem{background:radial-gradient(ellipse 60% 50% at 100% 0%,rgba(99,19,133,.25),transparent 70%),var(--bg);}
.hd-problem-head{max-width:900px;margin-bottom:70px;}
.hd-pains{display:grid;grid-template-columns:repeat(2,1fr);gap:26px;}
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

.hd-badges{display:flex;flex-wrap:wrap;gap:10px;margin:26px 0 8px;}
.hd-badge{display:inline-flex;align-items:center;gap:6px;font-size:13px;color:#d5dae3 !important;padding:10px 16px;border-radius:40px;
  background:linear-gradient(#0d1018,#0d1018) padding-box,linear-gradient(120deg,var(--vio),var(--blu)) border-box;border:1px solid transparent;transition:box-shadow .3s;}
.hd-badge b{color:#fff;font-weight:700;}.hd-badge i{color:var(--vio2);font-style:italic;}
a.hd-badge:hover{box-shadow:0 0 30px rgba(177,75,244,.5);}

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

/* FILMOGRAPHY TABS */
.hd-filmo{margin-top:90px;}
.hd-filmo-head{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:12px;border-bottom:1px solid #1c2230;padding-bottom:18px;}
.hd-filmo-head .hd-eb{margin:0;}.hd-filmo-head p{margin:0;font-size:14px;}
.hd-tabs{display:flex;gap:8px;flex-wrap:wrap;margin:26px 0 30px;}
.hd-tab{font:700 12px/1 Inter,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:#c7cdd8;background:transparent;
  border:1px solid #2a3142;border-radius:40px;padding:13px 20px;cursor:pointer;transition:all .25s;}
.hd-tab sup{font-size:10px;color:var(--vio2);margin-left:4px;letter-spacing:0;}
.hd-tab:hover{border-color:var(--vio2);color:#fff;}
.hd-tab.on{background:var(--brand);border-color:var(--brand);color:#fff;box-shadow:0 0 30px rgba(177,75,244,.5);}
.hd-tab.on sup{color:#fff;}
.hd-panels{position:relative;max-height:560px;overflow-y:auto;padding-right:6px;scrollbar-width:thin;scrollbar-color:#3a2a55 transparent;
  -webkit-mask-image:linear-gradient(#000 88%,transparent);mask-image:linear-gradient(#000 88%,transparent);}
.hd-panel{display:none;columns:3;column-gap:40px;list-style:none;margin:0;padding:0 0 60px;}
.hd-panel.on{display:block;animation:hd-up .6s ease;}
.hd-panel li{break-inside:avoid;padding:9px 0;border-bottom:1px solid #12161f;display:flex;justify-content:space-between;gap:12px;align-items:baseline;transition:padding .25s;}
.hd-panel li:hover{padding-left:8px;}
.hd-panel li b{font-family:'Bebas Neue',sans-serif;font-weight:400;font-size:23px;letter-spacing:.03em;color:#fff;line-height:1.1;}
.hd-panel li:hover b{color:var(--vio2);}
.hd-panel li span{font-size:11px;font-weight:600;letter-spacing:.08em;color:#6b7382;text-transform:uppercase;white-space:nowrap;}

/* SUPERVISION CREDITS LIST */
.hd-car-sup{margin-top:20px;}
.hd-credlist{list-style:none;margin:20px 0 0;padding:0 6px 50px 0;columns:2;column-gap:50px;max-height:640px;overflow-y:auto;scrollbar-width:thin;scrollbar-color:#6b3b8f transparent;-webkit-mask-image:linear-gradient(#000 88%,transparent);mask-image:linear-gradient(#000 88%,transparent);}
.hd-credlist li{break-inside:avoid;display:grid;grid-template-columns:52px 1fr auto;gap:4px 14px;align-items:baseline;padding:12px 0;border-bottom:1px solid rgba(255,255,255,.1);}
.hd-credlist b{font-family:'Bebas Neue',sans-serif;font-weight:400;font-size:24px;color:#fff;letter-spacing:.03em;line-height:1.05;}
.hd-yr{font-size:12px;font-weight:700;color:#e9d5ff;letter-spacing:.1em;}
.hd-role{font-size:10px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#e9d5ff;border:1px solid rgba(233,213,255,.35);padding:5px 9px;border-radius:30px;white-space:nowrap;}
.hd-kind{grid-column:2;font-size:12px;color:#b9a9cc;}
.hd-cred-note{margin-top:24px;font-size:13px;color:#b9a9cc !important;}
.hd-cred-note a{color:#fff !important;border-bottom:1px solid var(--vio2);}

/* SPEAKING & PRESS */
.hd-voice{background:#000;padding:110px 0;}
.hd-voice-grid{display:grid;grid-template-columns:1.15fr 1.15fr .8fr;gap:50px;}
.hd-voice h3{font-size:44px !important;margin-bottom:26px;}
.hd-voice ul{list-style:none;margin:0;padding:0;}
.hd-voice li{font-size:16px;color:#d5dae3;padding:13px 0;border-bottom:1px solid #1c2230;display:flex;align-items:center;gap:12px;}
.hd-voice li span{flex:1;}
.hd-voice li em{font-style:normal;font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--vio2);white-space:nowrap;}
.hd-voice li::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--vio);box-shadow:0 0 10px var(--vio);flex:none;}

/* ROSTER */
.hd-roster{background:radial-gradient(ellipse 50% 60% at 0% 100%,rgba(56,189,248,.12),transparent 70%),var(--bg);}
.hd-roster-head{display:flex;justify-content:space-between;align-items:flex-end;gap:40px;margin-bottom:60px;flex-wrap:wrap;}
.hd-roster-head p{max-width:420px;margin:0;}
.hd-labels{display:grid;grid-template-columns:repeat(6,1fr);gap:22px;}
.hd-label{grid-column:span 2;position:relative;display:flex;flex-direction:column;padding:40px 32px 34px;min-height:320px;border-radius:4px;
  background:linear-gradient(#0c0f17,#0c0f17) padding-box,linear-gradient(140deg,#2a3142,#141924) border-box;border:1px solid transparent;
  transition:all .45s ease;overflow:hidden;}
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

/* also representing */
.hd-more{margin-top:56px;}
.hd-more-k{display:block;font-size:11px;font-weight:700;letter-spacing:.42em;color:#6b7382;text-transform:uppercase;margin-bottom:20px;}
.hd-more-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;}
.hd-more-item{padding:22px 20px;border:1px solid #1c2230;border-radius:4px;background:#0b0d14;transition:all .35s ease;}
.hd-more-item:hover{border-color:var(--vio);box-shadow:0 18px 50px rgba(177,75,244,.22);transform:translateY(-4px);}
.hd-more-item b{display:block;font-family:'Bebas Neue',sans-serif;font-weight:400;font-size:28px;letter-spacing:.03em;color:#fff;line-height:1;margin-bottom:8px;}
.hd-more-item span{font-size:11px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--vio2);}
.hd-more-plus{background:linear-gradient(140deg,rgba(123,31,162,.35),rgba(56,189,248,.12));border-color:rgba(177,75,244,.45);}
.hd-more-plus span{color:#d9cfe6;letter-spacing:.06em;text-transform:none;font-weight:500;font-size:13px;}
@media(max-width:980px){.hd-more-grid{grid-template-columns:repeat(2,1fr);}}

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
  .hd-panel{columns:2;}
  .hd-credlist{columns:1;}
  .hd-voice-grid{grid-template-columns:1fr;gap:50px;}
}
@media(max-width:640px){
  .hd{font-size:16px;}
  .hd-sec{padding:90px 0;}
  .hd-wrap{padding:0 20px;}

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
  .hd-panel{columns:1;}
  .hd-panels{max-height:480px;}
  .hd-credlist{max-height:520px;}
  .hd-credlist li{grid-template-columns:44px 1fr;}
  .hd-role{grid-column:2;justify-self:start;}
  .hd-deep-n{font-size:50px;}
}
@media(prefers-reduced-motion:reduce){
  .hd-wall-row,.hd-track,.hd-beam,.hd-scroll{animation:none !important;}
  .hd-up,.hd-reveal{opacity:1 !important;transform:none !important;animation:none !important;}
}
"""

JS = r"""
(function(){
  /* Ethan Bloom: trailer pop-up and date-limited screening notice */
  var tr=document.getElementById('hd-trailer');
  if(tr){
    var frame=tr.querySelector('.hd-tr-frame'),trLast=null;
    function trOpen(ev){ev.preventDefault();trLast=document.activeElement;
      frame.innerHTML='<iframe src="https://www.youtube-nocookie.com/embed/'+frame.getAttribute('data-yt')+'?autoplay=1&rel=0" title="Ethan Bloom trailer" referrerpolicy="strict-origin-when-cross-origin" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
      tr.hidden=false;document.documentElement.style.overflow='hidden';setTimeout(function(){tr.querySelector('.hd-f-x').focus();},50);}
    function trClose(){tr.hidden=true;frame.innerHTML='';document.documentElement.style.overflow='';if(trLast&&trLast.focus)trLast.focus();}
    [].forEach.call(document.querySelectorAll('[data-hd-trailer]'),function(b){b.addEventListener('click',trOpen);});
    tr.addEventListener('click',function(ev){if(ev.target.closest('[data-tclose]'))trClose();});
    document.addEventListener('keydown',function(ev){if(!tr.hidden&&ev.key==='Escape')trClose();});
  }
  [].forEach.call(document.querySelectorAll('[data-until]'),function(el){
    var d=new Date(el.getAttribute('data-until')+'T23:59:59-07:00');if(!isNaN(d)&&new Date()>d)el.hidden=true;});

  /* music finder: "Search Catalog" asks what they need, then routes them */
  var fd=document.getElementById('hd-finder');
  if(fd){
    var lastFocus=null,choice='';
    function step(n){[].forEach.call(fd.querySelectorAll('.hd-f-step'),function(s){s.hidden=s.getAttribute('data-step')!=String(n);});fd.querySelector('.hd-f-brief').hidden=n!==1;}
    function openF(ev){ev.preventDefault();lastFocus=document.activeElement;choice='';step(1);fd.hidden=false;
      document.documentElement.style.overflow='hidden';var nv=document.querySelector('.hd-nav');if(nv)nv.classList.remove('open');
      setTimeout(function(){var f=fd.querySelector('.hd-fopt');if(f)f.focus();},50);}
    function closeF(){fd.hidden=true;document.documentElement.style.overflow='';if(lastFocus&&lastFocus.focus)lastFocus.focus();}
    function brief(){closeF();
      var form=document.querySelector('textarea[name="form_submission[custom_1]"]'),sec=form&&form.closest('section,[id^="section-"]');
      var t=sec||document.querySelector('[id^="section-1792000000008"]');
      if(form&&!form.value)form.value=(choice&&choice!=='Other'?'Looking for: '+choice+'\n\n':'')+'Project / scene / deadline / budget: ';
      if(t){window.scrollTo({top:t.getBoundingClientRect().top+window.pageYOffset-90,behavior:'smooth'});
        if(form)setTimeout(function(){form.focus({preventScroll:true});},900);}
      else location.href='__CONTACT__';}
    [].forEach.call(document.querySelectorAll('[data-hd-finder]'),function(a){a.addEventListener('click',openF);});
    fd.addEventListener('click',function(ev){var t=ev.target.closest('[data-close],[data-brief],[data-prev],.hd-fopt');if(!t)return;
      if(t.hasAttribute('data-close'))return closeF();
      if(t.hasAttribute('data-brief'))return brief();
      if(t.hasAttribute('data-prev'))return step(1);
      choice=t.getAttribute('data-label');var u=t.getAttribute('data-url');
      if(u){window.open(u,'_blank','noopener');closeF();}else step(2);});
    document.addEventListener('keydown',function(ev){if(!fd.hidden&&ev.key==='Escape')closeF();});
  }

  /* floating nav: solid on scroll, mobile menu, smooth jumps, active section */
  var nav=document.querySelector('.hd-nav');
  if(nav){
    var tog=nav.querySelector('.hd-nav-tog'),links=[].slice.call(nav.querySelectorAll('.hd-nav-links a, .hd-nav-logo'));
    function setOpen(v){nav.classList.toggle('open',v);tog.setAttribute('aria-expanded',v?'true':'false');}
    tog.addEventListener('click',function(){setOpen(!nav.classList.contains('open'));});
    links.forEach(function(a){a.addEventListener('click',function(ev){
      var id=(a.getAttribute('href')||'').split('#')[1],t=id&&document.getElementById(id);
      if(!t)return;ev.preventDefault();setOpen(false);
      var off=window.innerWidth<=960?84:96,n=0;
      function go(beh){var y=id==='hd-top'?0:t.getBoundingClientRect().top+window.pageYOffset-off;window.scrollTo({top:y,behavior:beh});return y;}
      go('smooth');
      /* content above can still be loading; re-aim until the section settles under the nav */
      (function fix(){setTimeout(function(){var d=id==='hd-top'?window.pageYOffset:t.getBoundingClientRect().top-off;
        if(Math.abs(d)>6&&n++<4){go(n>2?'auto':'smooth');fix();}},700);})();
    });});
    var secs=links.map(function(a){var id=(a.getAttribute('href')||'').split('#')[1];return {a:a,el:id&&id!=='hd-top'&&document.getElementById(id)};}).filter(function(x){return x.el;});
    var tick=false;
    function onScroll(){tick=false;var y=window.pageYOffset;nav.classList.toggle('solid',y>40);
      var cur=null,line=window.innerHeight*0.35;
      secs.forEach(function(x){var r=x.el.getBoundingClientRect();if(r.top<=line&&r.bottom>line)cur=x;});
      secs.forEach(function(x){x.a.classList.toggle('on',x===cur);});}
    window.addEventListener('scroll',function(){if(!tick){tick=true;requestAnimationFrame(onScroll);}},{passive:true});
    document.addEventListener('keydown',function(ev){if(ev.key==='Escape')setOpen(false);});
    onScroll();
  }
  var root=document.getElementById('hdmn');if(!root)return;
  // poster wall (decorative)
  var base='__BASE__',slugs='__SLUGS__'.split(','),wall=root.querySelector('.hd-wall');
  function shuffled(seed){var a=slugs.slice(),s=seed;for(var i=a.length-1;i>0;i--){s=(s*9301+49297)%233280;var j=Math.floor(s/233280*(i+1));var t=a[i];a[i]=a[j];a[j]=t;}return a.slice(0,12);}
  for(var r=0;r<4;r++){var row=document.createElement('div');row.className='hd-wall-row'+(r%2?' rev':'');row.style.animationDuration=(90+r*20)+'s';
    var pick=shuffled(r+3),h='';for(var k=0;k<2;k++)pick.forEach(function(sl){h+='<img src="'+base+'thumb/'+sl+'.jpg" alt="">';});row.innerHTML=h;wall.appendChild(row);}
  // filmography tabs
  var tabbar=root.querySelector('.hd-tabs');
  if(tabbar)tabbar.addEventListener('click',function(ev){var t=ev.target.closest('.hd-tab');if(!t)return;var i=t.getAttribute('data-tab');
    root.querySelectorAll('.hd-tab').forEach(function(x){x.classList.toggle('on',x===t);});
    root.querySelectorAll('.hd-panel').forEach(function(p){p.classList.toggle('on',p.getAttribute('data-panel')===i);});
    var box=root.querySelector('.hd-panels');if(box)box.scrollTop=0;});
  // nav goes solid on scroll
  // cycle the hero pain line
  var pls=root.querySelectorAll('.hd-pl');
  if(pls.length>1&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches){var pi=0;
    setInterval(function(){pls[pi].classList.remove('on');pi=(pi+1)%pls.length;pls[pi].classList.add('on');},3400);}

  // retry any poster that fails on the primary host from the fallback host
  var fb='__FALLBACK__';
  if(fb){root.addEventListener('error',function(ev){var im=ev.target;if(im.tagName!=='IMG'||im.dataset.fb)return;
    var i=im.src.indexOf('/posters/');if(i<0)return;im.dataset.fb='1';im.src=fb+im.src.slice(i+9);},true);}
  // reveal on scroll
  var els=root.querySelectorAll('.hd-reveal');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target);}});},{threshold:0,rootMargin:'0px 0px -8% 0px'});
    els.forEach(function(el){io.observe(el);});
  }else{els.forEach(function(el){el.classList.add('in');});}
  // count-up stats
  root.querySelectorAll('.hd-stat b').forEach(function(el){
    var done=false;
    var o=new IntersectionObserver(function(es){if(es[0].isIntersecting&&!done){done=true;
      if(!el.hasAttribute('data-count'))return;  // read late: the Google Sheet may have changed these
      var end=parseFloat(el.getAttribute('data-count')),suf=el.getAttribute('data-suffix')||'',t0=null;
      function f(t){if(!t0)t0=t;var p=Math.min((t-t0)/1600,1),v=Math.round(end*(1-Math.pow(1-p,3)));el.textContent=v.toLocaleString('en-US')+suf;if(p<1)requestAnimationFrame(f);}
      requestAnimationFrame(f);}},{threshold:.5});o.observe(el);
  });
  // ---- live data from Jody's Google Sheet (JSONP via the gviz endpoint; no API key needed)
  var SHEET='__SHEET__';
  function esc(x){return String(x==null?'':x).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  function pic(v){v=String(v||'').trim();if(!v)return '';return /^https?:\/\//.test(v)?v:base+v;}
  function card(src,cap,title){return '<figure class="hd-card"><img src="'+esc(src)+'" alt="'+esc(title)+' poster" loading="lazy"><figcaption><span>'+cap+'</span><strong>'+esc(title)+'</strong></figcaption></figure>';}
  function byOrder(a,b){var x=parseFloat(a.Order),y=parseFloat(b.Order);x=isNaN(x)?1e9:x;y=isNaN(y)?1e9:y;return x-y;}
  function yes(v){return /^y/i.test(String(v||''));}
  function applySheet(rows){
    var sec=function(n){return rows.filter(function(r){return String(r.Section||'').trim().toLowerCase()===n;});};
    var P=sec('placement'),J=sec('project'),A=sec('award/panel'),R=sec('podcast/radio'),N=sec('press'),S=sec('stat');
    if(!P.length&&!J.length)return;
    // stats
    var stats=root.querySelectorAll('.hd-stat');
    S.slice(0,stats.length).forEach(function(r,i){var t=String(r.Title==null?'':r.Title).trim();if(!t)return;var m=t.match(/^([\d,.]+)(.*)$/),b=stats[i].querySelector('b');
      b.textContent=t;if(m){b.setAttribute('data-count',m[1].replace(/,/g,''));b.setAttribute('data-suffix',m[2]);}else{b.removeAttribute('data-count');}
      stats[i].querySelector('span').textContent=r.Detail||'';});
    // placements filmography
    if(P.length){var cats=['TV','Film','Trailers','Ads & Campaigns','Video Games'];
      P.forEach(function(r){var c=String(r.Type||'TV').trim()||'TV';if(cats.indexOf(c)<0)cats.push(c);});
      var groups=cats.map(function(c){return P.filter(function(r){return (String(r.Type||'TV').trim()||'TV')===c;});});
      var tabs='',panels='',first=-1;
      groups.forEach(function(g,i){if(!g.length)return;if(first<0)first=i;
        tabs+='<button class="hd-tab'+(i===first?' on':'')+'" data-tab="'+i+'">'+esc(cats[i])+' <sup>'+g.length+'</sup></button>';
        panels+='<ul class="hd-panel'+(i===first?' on':'')+'" data-panel="'+i+'">'+g.map(function(r){return '<li><b>'+esc(r.Title)+'</b>'+(r.Detail?'<span>'+esc(r.Detail)+'</span>':'')+'</li>';}).join('')+'</ul>';});
      root.querySelector('.hd-tabs').innerHTML=tabs;root.querySelector('.hd-panels').innerHTML=panels;
      var kind={'TV':'TV Series','Film':'Feature Film','Trailers':'Trailer','Ads & Campaigns':'Campaign','Video Games':'Video Game'};
      var pc=P.filter(function(r){return yes(r.Carousel)&&pic(r.Poster);}).sort(byOrder);
      if(pc.length)root.querySelector('.hd-car:not(.hd-car-sup) .hd-car-track').innerHTML=pc.map(function(r){var t=String(r.Type||'TV').trim();
        return card(pic(r.Poster),esc(kind[t]||t)+(r.Detail?' &middot; '+esc(r.Detail):''),r.Title);}).join('');}
    // projects worked on
    if(J.length){root.querySelector('.hd-credlist').innerHTML=J.map(function(r){return '<li><span class="hd-yr">'+esc(r.Year)+'</span><b>'+esc(r.Title)+'</b><span class="hd-role">'+esc(r.Detail)+'</span><span class="hd-kind">'+esc(r.Type)+'</span></li>';}).join('');
      var jc=J.filter(function(r){return yes(r.Carousel)&&pic(r.Poster);}).sort(byOrder);
      if(jc.length)root.querySelector('.hd-car-sup .hd-car-track').innerHTML=jc.map(function(r){return card(pic(r.Poster),esc(r.Detail)+(r.Year?' &middot; '+esc(r.Year):''),r.Title);}).join('');}
    // awards, podcasts, press
    var lists=root.querySelectorAll('.hd-voice ul');
    [A,R,N].forEach(function(g,i){if(g.length&&lists[i])lists[i].innerHTML=g.map(function(r){return '<li><span>'+esc(r.Title)+'</span><em>'+esc(r.Detail)+'</em></li>';}).join('');});
  }
  if(SHEET){
    var cb='__hdmnSheet'+Date.now();
    window[cb]=function(resp){try{if(!resp||resp.status!=='ok')return;var cols=resp.table.cols.map(function(c){return c.label;});
      var rows=resp.table.rows.map(function(row){var o={};row.c.forEach(function(cell,i){o[cols[i]]=cell?(cell.f!=null?cell.f:cell.v):'';});return o;});
      applySheet(rows);}catch(e){}finally{delete window[cb];}};
    var sc=document.createElement('script');
    sc.src='https://docs.google.com/spreadsheets/d/'+SHEET+'/gviz/tq?headers=1&tqx=out:json;responseHandler:'+cb;
    sc.onerror=function(){delete window[cb];};document.head.appendChild(sc);
  }

  // poster carousels
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  root.querySelectorAll('.hd-car').forEach(function(car,ci){
    var tr=car.querySelector('.hd-car-track');if(!tr)return;
    function step(){var c=tr.querySelector('.hd-card');return c?(c.offsetWidth+24)*2:500;}
    function next(){if(tr.scrollLeft+tr.clientWidth>=tr.scrollWidth-10){tr.scrollTo({left:0});}else{tr.scrollBy({left:step()});}}
    function prev(){if(tr.scrollLeft<=5){tr.scrollTo({left:tr.scrollWidth});}else{tr.scrollBy({left:-step()});}}
    car.querySelector('.hd-car-next').addEventListener('click',next);
    car.querySelector('.hd-car-prev').addEventListener('click',prev);
    var paused=false;
    car.addEventListener('mouseenter',function(){paused=true;});
    car.addEventListener('mouseleave',function(){paused=false;});
    car.addEventListener('touchstart',function(){paused=true;},{passive:true});
    if(!reduce){setInterval(function(){if(!paused&&!document.hidden)next();},3000+ci*700);}
  });
})();
"""

TEMPLATE = """<style>{css}</style>
<div class="hd" id="hdmn">
<nav class="hd-nav" aria-label="Page sections">
  <a class="hd-nav-logo" href="#hd-top" aria-label="HD Music Now, back to top"><img src="{logo}" alt="" width="40" height="40"><span>HD Music Now</span></a>
  <div class="hd-nav-links" id="hd-nav-links">
    <a href="#hd-why">Why Us</a>
    <a href="#hd-ethan">Ethan Bloom</a>
    <a href="#hd-credits">Credits</a>
    <a href="#hd-roster">Catalogs</a>
    <a href="#hd-deep">Specialty</a>
    <a href="#hd-sup">Supervision</a>
    <a href="#hd-voice">Press</a>
    <a href="{contact}">Contact</a>
  </div>
  <a class="hd-btn p" href="{catalog}" target="_blank" rel="noopener" data-hd-finder>&#9654; Search Catalog</a>
  <button class="hd-nav-tog" type="button" aria-label="Menu" aria-expanded="false" aria-controls="hd-nav-links"><i></i><i></i><i></i></button>
</nav>
<div class="hd-finder" id="hd-finder" role="dialog" aria-modal="true" aria-labelledby="hd-f-title" hidden>
  <div class="hd-f-back" data-close></div>
  <div class="hd-f-box">
    <button type="button" class="hd-f-x" data-close aria-label="Close">&times;</button>
    <div class="hd-f-step" data-step="1">
      <span class="hd-eb">Find your music</span>
      <h3 id="hd-f-title">What type of music are you looking for?</h3>
      <div class="hd-f-opts">{finder}</div>
    </div>
    <div class="hd-f-step" data-step="2" hidden>
      <span class="hd-eb">Not everything is online</span>
      <h3>Tell us what you need.</h3>
      <p>Many of our catalogs aren&rsquo;t searchable online. Send us your brief and we&rsquo;ll compile a custom playlist for you, or browse what&rsquo;s on SourceAudio.</p>
      <div class="hd-f-row">
        <button type="button" class="hd-btn p" data-brief>Send Us Your Brief</button>
        <a class="hd-btn o" href="{sourceaudio}" target="_blank" rel="noopener">Browse SourceAudio &#8599;</a>
      </div>
      <button type="button" class="hd-f-prev" data-prev>&larr; Back to options</button>
    </div>
    <button type="button" class="hd-f-brief" data-brief><span>Need something specific?</span> Send us your brief and we&rsquo;ll compile a custom playlist &rarr;</button>
  </div>
</div>

<header class="hd-hero" id="hd-top">
  <div class="hd-wall" aria-hidden="true"></div>
  <div class="hd-shade"></div><div class="hd-glow"></div><div class="hd-beam"></div>
  <div class="hd-hero-in">
    <span class="hd-eb hd-up hd-pain-line" aria-live="polite"><span class="hd-pl on">The director loves the temp. The budget doesn&rsquo;t.</span><span class="hd-pl">Locked cut. Uncleared song. Mix is Friday.</span><span class="hd-pl">47 libraries. 3 million tracks. Nothing fits.</span><span class="hd-pl">In a world where the deadline was yesterday&hellip;</span></span>
    <h1 class="hd-grad hd-up" style="animation-delay:.2s">Temp it.<br>Love it.<br>Keep it.</h1>
    <p class="hd-sub hd-up" style="animation-delay:.45s">Cut with our music as your temp, fall in love with it, then keep it: budget-friendly and cleared before your deadline. A music supervisor's ear on every request, not library roulette.</p>
    <div class="hd-ctas hd-up" style="animation-delay:.7s">
      <a class="hd-btn p" href="{catalog}" target="_blank" rel="noopener" data-hd-finder>&#9654; Search the Catalog</a>
      <a class="hd-btn o" href="{contact}">Send Us a Brief</a>
    </div>
    <p class="hd-heard hd-up" style="animation-delay:1s">AS HEARD IN&nbsp; <b>SATURDAY NIGHT LIVE &middot; BREAKING BAD &middot; NOPE &middot; AVENGERS: ENDGAME (TRAILER)</b></p>
  </div>
  <div class="hd-scroll"></div>
</header>

<section class="hd-ticker">
  <div class="hd-ticker-k">TRUSTED BY STUDIOS, NETWORKS &amp; STREAMERS</div>
  <div class="hd-marquee"><div class="hd-track">{ticker}</div></div>
</section>

<section class="hd-sec hd-problem" id="hd-why">
  <div class="hd-wrap">
    <div class="hd-problem-head hd-reveal">
      <span class="hd-eb">The Problem</span>
      <h2 class="hd-h2">Every production has <span class="hd-grad">seen this movie.</span></h2>
    </div>
    <div class="hd-pains">
      <div class="hd-pain hd-reveal"><span class="hd-pain-n">01</span><h3>Temp Love</h3><p>The director's married to the temp track, and the licensing quote just came back at three times your music budget. Temp with music you can actually keep.</p></div>
      <div class="hd-pain hd-reveal" style="transition-delay:.1s"><span class="hd-pain-n">02</span><h3>The Deadline</h3><p>The cut changed. The mix is Friday. Air date doesn't move. You need real options today, not after another week of digging.</p></div>
      <div class="hd-pain hd-reveal" style="transition-delay:.2s"><span class="hd-pain-n">03</span><h3>The Clearance</h3><p>The perfect song dies at the last minute over split ownership, a slow publisher or a surprise fee, after the cut is locked.</p></div>
      <div class="hd-pain hd-reveal" style="transition-delay:.3s"><span class="hd-pain-n">04</span><h3>Library Roulette</h3><p>Dozens of libraries, millions of tracks, and nothing that fits. Period-authentic vintage, a regional folk recording, the exact door creak: most libraries just don't have it.</p></div>
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
      <p>I'm also a songwriter and producer. Songs I've written and produced have landed in <em>Law &amp; Order: Organized Crime</em>, <em>Murdaugh: Death in the Family</em>, CBS's <em>Evil</em> and Hulu's <em>The Handmaid's Tale</em> trailer campaign.</p>
      <div class="hd-badges">
        <span class="hd-badge"><b>Songwriter</b> &amp; Producer</span>
        <span class="hd-badge"><b>#1 Best-Selling Author</b> of <i>The Sync Placement Formula</i></span>
        <a class="hd-badge" href="https://www.wrecktheroom.com" target="_blank" rel="noopener"><b>Creator</b> of Wreck The Room&trade;</a>
      </div>
      <div class="hd-sig"><div class="hd-sig-line"></div><div><div class="hd-sig-name">Jody Friedman</div><div class="hd-sig-role">FOUNDER &middot; SONGWRITER &middot; PRODUCER</div></div></div>
    </div>
    <div class="hd-stats hd-reveal" style="transition-delay:.2s">
      <div class="hd-stat"><b data-count="20" data-suffix="+">20+</b><span>Years as a sync agent and as a music supervisor</span></div>
      <div class="hd-stat"><b data-count="500" data-suffix="K+">500K+</b><span>Sound effects from Sound Ideas, Hollywood Edge &amp; BOOM Library</span></div>
      <div class="hd-stat"><b data-count="{total_n}" data-suffix="+">{total}</b><span>Placements worldwide across TV, film, trailers, ads &amp; games</span></div>
      <div class="hd-stat"><b data-count="{sup_total}" data-suffix="">{sup_total}</b><span>Projects worked on in music supervision, clearance &amp; coordination</span></div>
    </div>
  </div>
</section>

<section class="hd-ethan" id="hd-ethan">
  <div class="hd-eb-bg" style="background-image:url('{base}ethan-bloom-still.jpg')"></div>
  <div class="hd-wrap hd-eb-grid">
    <div class="hd-eb-poster hd-reveal">
      <button type="button" class="hd-eb-play" data-hd-trailer aria-label="Play the Ethan Bloom trailer">
        <img src="{base}ethan-bloom-key.jpg" alt="Ethan Bloom theatrical poster" loading="lazy" width="600" height="889">
        <span class="hd-eb-playbtn">&#9654;</span>
      </button>
      <div class="hd-laurel"><span>Director&rsquo;s Choice Award</span><b>Best Feature &middot; Comedy</b><span>Sedona International Film Festival 2026</span></div>
    </div>
    <div class="hd-eb-copy hd-reveal" style="transition-delay:.15s">
      <span class="hd-eb">Now in Theaters &middot; A Jody Friedman Production</span>
      <h2 class="hd-h2 hd-grad">Ethan Bloom</h2>
      <p class="hd-eb-role"><b>Producer</b> &amp; <b>Music Supervisor</b></p>
      <p class="hd-eb-log">A 13-year-old who should be studying for his bar mitzvah secretly finds comfort in the Catholic church. A heartfelt coming-of-age comedy about grief, faith and first love, set in Miami&rsquo;s Coconut Grove.</p>
      <p class="hd-eb-cred">Directed by Herschel Faber &middot; Written by Maylen Dominguez<br>Starring Joshua Malina, Rachelle Lefevre, Carlos Ponce, Mindy Sterling, Caroline Valencia and Hank Greenspan<br>Distributed in North America by Menemsha Films</p>
      <div class="hd-eb-stats">
        <div><b>29</b><span>Weeks &amp; counting in theaters</span></div>
        <div><b>{eb_n}+</b><span>Festival selections</span></div>
        <div><b>1</b><span>Award: Best Feature, Comedy</span></div>
      </div>
      <div class="hd-ctas" style="justify-content:flex-start">
        <button type="button" class="hd-btn p" data-hd-trailer>&#9654; Watch the Trailer</button>
        <a class="hd-btn o" href="{eb_showtimes}" target="_blank" rel="noopener">Showtimes &#8599;</a>
      </div>
      <div class="hd-eb-la" data-until="2026-10-23">
        <span class="hd-eb-la-k">LA Premiere &middot; Two Nights Only</span>
        <p><b>Wed, Oct 21</b> Laemmle&rsquo;s Royal, West LA &nbsp;&middot;&nbsp; <b>Thu, Oct 22</b> Laemmle Town Center 5, Encino</p>
        <p class="hd-eb-la-s">With Q&amp;As featuring stars Joshua Malina, Hank Greenspan and Mindy Sterling. Coming soon to New York and Boston.</p>
      </div>
    </div>
  </div>
  <div class="hd-wrap hd-eb-quotes">{eb_quotes}</div>
  <div class="hd-ticker hd-eb-fest"><div class="hd-ticker-k">OFFICIAL SELECTION</div><div class="hd-marquee"><div class="hd-track">{eb_fest}</div></div></div>
</section>
<div class="hd-trailer" id="hd-trailer" role="dialog" aria-modal="true" aria-label="Ethan Bloom trailer" hidden>
  <div class="hd-f-back" data-tclose></div>
  <div class="hd-tr-box"><button type="button" class="hd-f-x" data-tclose aria-label="Close">&times;</button><div class="hd-tr-frame" data-yt="{eb_trailer}"></div></div>
</div>

<section class="hd-showing" id="hd-credits">
  <div class="hd-wrap hd-center hd-reveal">
    <span class="hd-eb">Now Showing</span>
    <h2 class="hd-h2">Heard <span class="hd-grad">on</span></h2>
    <p>Music we've placed in series, features, trailers, campaigns and games. Hover a poster for the credit.</p>
  </div>
  <div class="hd-car">
    <button class="hd-car-nav hd-car-prev" aria-label="Previous posters">&#8249;</button>
    <div class="hd-car-track">{cards}</div>
    <button class="hd-car-nav hd-car-next" aria-label="Next posters">&#8250;</button>
  </div>
  <div class="hd-wrap hd-filmo hd-reveal">
    <div class="hd-filmo-head"><span class="hd-eb">The Full Filmography</span><p>Partial list of placements. Pick a category.</p></div>
    <div class="hd-tabs" role="tablist">{tabs}</div>
    <div class="hd-panels">{panels}</div>
  </div>
</section>

<section class="hd-ticker hd-brands">
  <div class="hd-ticker-k">ADVERTISING &amp; CAMPAIGNS FOR</div>
  <div class="hd-marquee"><div class="hd-track rev">{brands}</div></div>
</section>

<section class="hd-sec hd-roster" id="hd-roster">
  <div class="hd-wrap">
    <div class="hd-roster-head hd-reveal">
      <div><span class="hd-eb">The Roster</span><h2 class="hd-h2">Six labels.<br><span class="hd-grad">One call.</span></h2></div>
      <p>From a needle-drop for a cold open to a trailer cue that hits on the cut.</p>
    </div>
    <div class="hd-labels">{labels}</div>
  </div>
</section>

<section class="hd-sec hd-deep" id="hd-deep">
  <div class="hd-wrap">
    <div class="hd-reveal"><span class="hd-eb">The Deep Cuts</span><h2 class="hd-h2">The music no one<br><span class="hd-grad">else can find.</span></h2></div>
    <div class="hd-deep-list">
      <div class="hd-deep-row hd-reveal"><span class="hd-deep-n">01</span><div><small>CLASSICAL &middot; VINTAGE &middot; WORLD</small><h3>Naxos</h3></div><p>One of the world's deepest classical, vintage and world music catalogs. We've represented Naxos for twenty years.</p></div>
      <div class="hd-deep-row hd-reveal"><span class="hd-deep-n">02</span><div><small>KARAOKE &middot; COVERS</small><h3>Covered Records</h3></div><p>The largest karaoke catalog in the world. Instrumental and sound-alike versions of the songs your scene is reaching for.</p></div>
      <div class="hd-deep-row hd-reveal"><span class="hd-deep-n">03</span><div><small>500,000+ SOUND EFFECTS</small><h3>Sound Ideas &middot; Hollywood Edge &middot; BOOM</h3></div><p>Sound design from two of the largest SFX distributors in the world, from foley and ambiences to cinematic impacts.</p></div>
    </div>
    <div class="hd-more hd-reveal">
      <span class="hd-more-k">Also representing</span>
      <div class="hd-more-grid">
        <div class="hd-more-item"><b>Reality Entertainment</b><span>Metal</span></div>
        <div class="hd-more-item"><b>El Toro Records</b><span>Vintage Rockabilly</span></div>
        <div class="hd-more-item"><b>Record Kicks</b><span>Soul &middot; Funk</span></div>
        <div class="hd-more-item"><b>Four Flies Records</b><span>Italian &middot; Disco &middot; Vintage</span></div>
        <div class="hd-more-item hd-more-plus"><b>&amp; much more</b><span>Ask us for the sound you can't find</span></div>
      </div>
    </div>
    <div class="hd-deep-cta hd-reveal"><a class="hd-btn p" href="{contact}">Request a Specialty Search</a></div>
  </div>
</section>

<section class="hd-sec hd-sup" id="hd-sup">
  <div class="hd-wrap hd-sup-grid">
    <div class="hd-reveal">
      <span class="hd-eb">Music Supervision &middot; Clearance &middot; Coordination</span>
      <h2 class="hd-h2" style="margin-bottom:28px">Need more<br>than a track?</h2>
      <p>Bring us in on your project. We source, negotiate and clear music for films, series, docs and trailers, and help brands define one consistent sound across everything they make.</p>
      <div class="hd-ctas" style="justify-content:flex-start;margin-top:34px">
        <a class="hd-btn p" href="{contact}">Start a Project</a>
        <a class="hd-btn o" href="{imdb}" target="_blank" rel="noopener">Full IMDb Credits</a>
      </div>
    </div>
    <div class="hd-sup-side hd-reveal" style="transition-delay:.2s">
      <ul><li>Film</li><li>Television</li><li>Docs &amp; Unscripted</li><li>Trailers &amp; Promos</li><li>Brands</li></ul>
    </div>
  </div>
  <div class="hd-wrap hd-reveal" style="position:relative;z-index:1;margin-top:90px">
    <span class="hd-eb">Projects I've Worked On</span>
    <p style="max-width:640px;color:#d9cfe6">Music supervision, clearance and coordination credits, with the exact role on each. Hover a poster for the credit.</p>
  </div>
  <div class="hd-car hd-car-sup">
    <button class="hd-car-nav hd-car-prev" aria-label="Previous posters">&#8249;</button>
    <div class="hd-car-track">{sup_cards}</div>
    <button class="hd-car-nav hd-car-next" aria-label="Next posters">&#8250;</button>
  </div>
  <div class="hd-wrap hd-reveal" style="position:relative;z-index:1">
    <ul class="hd-credlist">{sup_rows}</ul>
    <p class="hd-cred-note">Source: IMDb. <a href="{imdb}" target="_blank" rel="noopener">View the full profile &rarr;</a></p>
  </div>
</section>

<section class="hd-sec hd-voice" id="hd-voice">
  <div class="hd-wrap">
    <div class="hd-reveal" style="margin-bottom:60px"><span class="hd-eb">Industry Voice</span><h2 class="hd-h2">On stage. <span class="hd-grad">On air.</span></h2></div>
    <div class="hd-voice-grid">
      <div class="hd-reveal"><span class="hd-eb">Awards &amp; Panels</span><ul>{speaking}</ul></div>
      <div class="hd-reveal" style="transition-delay:.15s"><span class="hd-eb">Podcasts &amp; Radio</span><ul>{press}</ul></div>
      <div class="hd-reveal" style="transition-delay:.3s"><span class="hd-eb">In Print &amp; Online</span><ul>{features}</ul></div>
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


def loader_js(embed):
    """Wrap the embed as a script that mounts into <div id="hdmn-mount"> (scripts in innerHTML don't run)."""
    markup, script = embed.split("<script>", 1)
    script = script.rsplit("</script>", 1)[0]
    return ("(function(){var m=document.getElementById('hdmn-mount');if(!m)return;m.innerHTML="
            + json.dumps(markup) + ";\n" + script + "\n})();\n")


def main():
    embed = build(CDN_BASE)
    (HERE / "kajabi-embed.html").write_text(embed)
    (HERE / "hdmn.js").write_text(loader_js(embed))
    preview = build("posters/")
    (HERE / "preview.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>HD Music Now — Homepage Preview</title></head>'
        '<body style="margin:0;background:#050608">' + preview + "</body></html>")
    print(f"kajabi-embed.html: {len(embed):,} chars (CDN ref: {CDN_REF})")


if __name__ == "__main__":
    main()
