"""Build the Ocho Music Group site embed.

Outputs:
  ocho.js       the whole site as one script. Each Kajabi page gets a single Code block:
                  <div id="ocho-mount" data-page="home" data-lang="en"></div>
                  <script src="https://cdn.jsdelivr.net/gh/mayadex853/Dashboards@<commit>/ocho-site/ocho.js"></script>
                data-page: home | about | albums | placements | learn    data-lang: en | es
  preview.html  standalone preview of every page in both languages (hash routing, images from ./img)

Usage: python3 build.py [CDN_REF]   (CDN_REF = git branch or commit the images are served from)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import data

HERE = Path(__file__).parent
# Images and track lists come from a fixed commit: by default the last commit that changed them, so code-only
# rebuilds keep the same (already cached) asset URLs.
# jsDelivr is the primary host (fast, no rate limit, and it cannot resolve branch names containing "/");
# raw.githubusercontent.com is the automatic fallback.
CDN_REF = sys.argv[1] if len(sys.argv) > 1 else subprocess.run(
    ["git", "log", "-1", "--format=%H", "--", "img", "tracks"], cwd=Path(__file__).parent,
    capture_output=True, text=True, check=True).stdout.strip()
CDN_BASE = f"https://cdn.jsdelivr.net/gh/mayadex853/Dashboards@{CDN_REF}/ocho-site/img/"
FALLBACK_BASE = f"https://raw.githubusercontent.com/mayadex853/Dashboards/{CDN_REF}/ocho-site/img/"

# Google Sheet with the album and placement lists; the page reads it live and falls back to data.py.
SHEET_ID = (HERE / "SHEET_ID").read_text().strip() if (HERE / "SHEET_ID").exists() else ""
# Public base URL of the streaming audio (Cloudflare R2 bucket); empty hides the player.
AUDIO_BASE = (HERE / "AUDIO_BASE").read_text().strip() if (HERE / "AUDIO_BASE").exists() else ""
TRACKS_BASE = f"https://cdn.jsdelivr.net/gh/mayadex853/Dashboards@{CDN_REF}/ocho-site/tracks/"


def _min(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return re.sub(r"\s*\n\s*", "", css).strip()


def site_data(base, fallback, preview, audio="", tracks=""):
    return {
        "t": data.T, "faq": data.FAQ, "learn": data.LEARN, "paths": data.PATHS, "testPaths": data.TEST_PATHS,
        "pdf": {"en": data.PDF_EN, "es": data.PDF_ES},
        "albums": [{"id": k, "title": t, "artist": a, "cat": c, "img": i} for k, t, a, c, i in data.ALBUMS],
        "placements": [{"title": t, "net": n, "cat": c, "img": i} for t, n, c, i in data.PLACEMENTS],
        "albumCats": data.ALBUM_CATS, "placeCats": data.PLACEMENT_CATS, "catsEs": data.CATS_ES,
        "networks": data.NETWORKS, "genres": data.GENRES,
        "pos": data.PHOTO_POS, "base": base, "fallback": fallback, "sheet": SHEET_ID, "preview": preview, "audio": audio, "tracksBase": tracks,
        "email": ["music", "ochomusicgroup.com"],
    }


CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600;700;800&display=swap');
.o{--bg:#07050a;--bg2:#0d0912;--line:#241a2e;--ink:#fff;--mute:#a79fb3;--mag:#ff2e9a;--pink:#ff5f8f;--cy:#22e1ff;--sun:#ff8a1f;
  --grad:linear-gradient(95deg,#ff2e9a 0%,#ff5f8f 45%,#ff8a1f 100%);
  background:var(--bg);color:var(--mute);font-family:Inter,system-ui,sans-serif;font-size:17px;line-height:1.6;
  position:relative;overflow:hidden;-webkit-font-smoothing:antialiased;text-align:left;}
.o *{box-sizing:border-box;}
.o h1,.o h2,.o h3,.o h4{font-family:Anton,Impact,'Arial Narrow',sans-serif !important;font-weight:400 !important;
  text-transform:uppercase;letter-spacing:.01em;color:var(--ink);margin:0;line-height:.92 !important;}
.o p{margin:0 0 1em;color:var(--mute);}
.o a{text-decoration:none !important;color:inherit;}
.o img{max-width:100%;}
.o button{font-family:inherit;}
.o-wrap{max-width:1240px;margin:0 auto;padding:0 28px;position:relative;}
.o-eb{display:inline-block;font-size:12px;font-weight:800;letter-spacing:.4em;text-transform:uppercase;color:var(--cy);margin-bottom:22px;}
.o-eb::before{content:"";display:inline-block;width:26px;height:2px;background:var(--cy);box-shadow:0 0 12px var(--cy);vertical-align:middle;margin:-3px 12px 0 0;}
.o-h2{font-size:clamp(50px,7.4vw,112px) !important;}
.o-grad{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent !important;}
.o-neon{color:#fff;text-shadow:0 0 6px #fff,0 0 22px var(--mag),0 0 48px var(--mag),0 0 90px rgba(255,46,154,.7);animation:o-flick 6s infinite;}
@keyframes o-flick{0%,18%,22%,25%,53%,57%,100%{opacity:1}20%,24%,55%{opacity:.55}}
.o-sec{position:relative;padding:130px 0;}
.o-btn{display:inline-flex;align-items:center;gap:10px;font:800 13px/1 Inter,sans-serif;letter-spacing:.18em;text-transform:uppercase;
  padding:20px 32px;border-radius:999px;transition:all .25s ease;cursor:pointer;border:0;white-space:nowrap;}
.o-btn small{font-size:9px;letter-spacing:.2em;opacity:.75;font-weight:700;}
.o-btn.p{background:var(--grad);color:#fff !important;box-shadow:0 0 40px rgba(255,46,154,.55);}
.o-btn.p:hover{transform:translateY(-3px);box-shadow:0 0 80px rgba(255,46,154,.95);}
.o-btn.c{background:transparent;color:#fff !important;box-shadow:inset 0 0 0 2px var(--cy),0 0 26px rgba(34,225,255,.35);}
.o-btn.c:hover{background:var(--cy);color:#07050a !important;box-shadow:0 0 60px rgba(34,225,255,.8);transform:translateY(-3px);}
.o-reveal{opacity:0;transform:translateY(46px);transition:opacity 1s ease,transform 1s cubic-bezier(.2,.8,.2,1);}
.o-reveal.in{opacity:1;transform:none;}
.o-grain{position:absolute;inset:0;pointer-events:none;z-index:50;opacity:.07;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");}

/* NAV */
.o-top{position:fixed;top:0;left:0;right:0;z-index:1000;transition:transform .35s ease;}
.o-banner{display:block;text-align:center;font-size:11px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#fff !important;
  padding:9px 16px;background:linear-gradient(90deg,#b0126b,#ff2e9a 40%,#ff8a1f);}
.o-banner b{display:inline-block;margin-left:8px;transition:transform .3s;}
.o-banner:hover b{transform:translateX(6px);}
.o-nav{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:16px 32px;transition:all .35s ease;}
.o-top.solid .o-nav{background:rgba(7,5,10,.86);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  padding:10px 32px;border-bottom:1px solid rgba(255,255,255,.07);}
.o-top.solid .o-banner{display:none;}
.o-logo img{height:66px;width:auto;display:block;filter:drop-shadow(0 0 14px rgba(255,46,154,.45));transition:height .35s;}
.o-top.solid .o-logo img{height:50px;}
.o-links{display:flex;align-items:center;gap:30px;}
.o-links a:not(.o-btn){font-size:12px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:#e3dceb !important;transition:color .2s;position:relative;}
.o-links a:not(.o-btn):hover,.o-links a.on{color:var(--pink) !important;}
.o-links a.on::after{content:"";position:absolute;left:0;right:0;bottom:-8px;height:2px;background:var(--grad);box-shadow:0 0 10px var(--mag);}
.o-links .o-btn{padding:13px 20px;font-size:11px;}
.o-lang{border:1px solid rgba(255,255,255,.35);border-radius:999px;padding:7px 12px !important;letter-spacing:.14em !important;}
.o-burger{display:none;background:none;border:0;width:44px;height:44px;cursor:pointer;position:relative;}
.o-burger i{position:absolute;left:10px;right:10px;height:2px;background:#fff;transition:all .3s;}
.o-burger i:nth-child(1){top:15px}.o-burger i:nth-child(2){top:21px}.o-burger i:nth-child(3){top:27px}
.o-top.open .o-burger i:nth-child(1){top:21px;transform:rotate(45deg)}
.o-top.open .o-burger i:nth-child(2){opacity:0}
.o-top.open .o-burger i:nth-child(3){top:21px;transform:rotate(-45deg)}

/* HERO */
.o-hero{position:relative;min-height:100vh;display:flex;align-items:center;justify-content:center;overflow:hidden;}
.o-wall{position:absolute;top:-35%;left:-25%;right:-25%;bottom:-35%;transform:rotate(-12deg) skewX(-4deg);display:flex;flex-direction:column;justify-content:center;gap:18px;opacity:.85;}
.o-wall-row{display:flex;gap:18px;width:max-content;animation:o-left 110s linear infinite;}
.o-wall-row.rev{animation-name:o-right;}
.o-wall-row img{width:210px;height:210px;object-fit:cover;border-radius:6px;flex:none;}
@keyframes o-left{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@keyframes o-right{from{transform:translateX(-50%)}to{transform:translateX(0)}}
.o-shade{position:absolute;inset:0;background:
  radial-gradient(ellipse 60% 58% at 50% 50%,rgba(7,5,10,.93) 0%,rgba(7,5,10,.78) 55%,rgba(7,5,10,.35) 100%),
  linear-gradient(180deg,rgba(7,5,10,.9) 0%,rgba(7,5,10,0) 22%,rgba(7,5,10,0) 72%,var(--bg) 100%);}
.o-glow{position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen;background:
  radial-gradient(ellipse 45% 50% at 6% 8%,rgba(255,46,154,.55),transparent 60%),
  radial-gradient(ellipse 40% 45% at 96% 95%,rgba(34,225,255,.42),transparent 60%),
  radial-gradient(ellipse 30% 30% at 90% 10%,rgba(255,138,31,.25),transparent 60%);}
.o-sunset{position:absolute;left:50%;bottom:-38vmin;width:76vmin;height:76vmin;transform:translateX(-50%);border-radius:50%;pointer-events:none;opacity:.32;
  background:repeating-linear-gradient(180deg,transparent 0 14px,var(--bg) 14px 22px),linear-gradient(180deg,#ff8a1f,#ff2e9a 55%,#7a0ebd);
  -webkit-mask-image:linear-gradient(180deg,#000 30%,transparent 75%);mask-image:linear-gradient(180deg,#000 30%,transparent 75%);}
.o-hero-in{position:relative;z-index:2;text-align:center;padding:170px 24px 110px;max-width:1180px;}
.o-hero-logo{width:min(340px,70vw);height:auto;margin:0 auto 18px;display:block;filter:drop-shadow(0 0 30px rgba(255,46,154,.55));}
.o-hero h1{font-size:clamp(64px,10.5vw,170px) !important;line-height:.86 !important;margin-bottom:30px;filter:drop-shadow(0 8px 40px rgba(0,0,0,.9));}
.o-hero .o-sub{font-size:20px;color:#efe8f5;max-width:760px;margin:0 auto 42px;text-shadow:0 2px 20px #000;}
.o-ctas{display:flex;gap:16px;justify-content:center;flex-wrap:wrap;}
.o-ctas .o-btn{flex-direction:column;gap:7px;padding:18px 34px;}
.o-heard{margin-top:46px;font-size:11px;font-weight:700;letter-spacing:.32em;color:#8e85a0;line-height:2.2;text-transform:uppercase;}
.o-heard b{color:#fff;}
.o-rot{display:grid;min-height:1.3em;}
.o-rot::before{display:none;}
.o-rl{grid-area:1/1;opacity:0;transform:translateY(10px);transition:opacity .6s ease,transform .6s ease;}
.o-rl.on{opacity:1;transform:none;transition-delay:.5s;}
.o-up{opacity:0;transform:translateY(28px);animation:o-up 1.1s cubic-bezier(.2,.8,.2,1) forwards;}
@keyframes o-up{to{opacity:1;transform:none}}
.o-eq{display:flex;gap:5px;justify-content:center;align-items:flex-end;height:34px;margin:0 auto 26px;}
.o-eq i{width:5px;border-radius:3px;background:var(--grad);box-shadow:0 0 12px rgba(255,46,154,.7);animation:o-eq 1s ease-in-out infinite alternate;}
@keyframes o-eq{from{height:6px}to{height:34px}}

/* MARQUEES */
.o-ticker{background:#000;padding:32px 0;border-top:1px solid rgba(255,255,255,.06);border-bottom:1px solid rgba(255,255,255,.06);}
.o-ticker-k{text-align:center;font-size:11px;font-weight:800;letter-spacing:.42em;color:#6f667e;margin-bottom:12px;text-transform:uppercase;}
.o-mq{overflow:hidden;white-space:nowrap;-webkit-mask-image:linear-gradient(90deg,transparent,#000 10%,#000 90%,transparent);mask-image:linear-gradient(90deg,transparent,#000 10%,#000 90%,transparent);}
.o-track{display:inline-block;animation:o-left 50s linear infinite;}
.o-track span{font-family:Anton,sans-serif;font-size:50px;letter-spacing:.03em;color:rgba(255,255,255,.92);margin:0 30px;vertical-align:middle;text-transform:uppercase;}
.o-track i{display:inline-block;width:9px;height:9px;transform:rotate(45deg);background:var(--mag);box-shadow:0 0 14px var(--mag);vertical-align:middle;}
.o-tape{position:relative;height:250px;overflow:hidden;background:var(--bg);}
.o-tape .o-band{position:absolute;left:-5%;right:-5%;top:50%;padding:18px 0;overflow:hidden;white-space:nowrap;}
.o-tape .o-band.a{background:var(--grad);transform:translateY(-50%) rotate(-4deg);z-index:2;box-shadow:0 0 60px rgba(255,46,154,.45);}
.o-tape .o-band.b{background:#000;transform:translateY(-50%) rotate(3deg);border-top:2px solid var(--cy);border-bottom:2px solid var(--cy);}
.o-band .o-track span{font-size:46px;color:#07050a;margin:0 24px;}
.o-band.b .o-track span{color:transparent;-webkit-text-stroke:1.5px var(--cy);}
.o-band .o-track i{background:#07050a;box-shadow:none;}
.o-band.b .o-track i{background:var(--cy);box-shadow:0 0 12px var(--cy);}
.o-band.b .o-track{animation-name:o-right;animation-duration:60s;}

/* DIFFERENCE */
.o-diff{background:radial-gradient(ellipse 60% 50% at 100% 0%,rgba(122,14,189,.28),transparent 70%),var(--bg);}
.o-diff-head{max-width:920px;margin-bottom:70px;}
.o-pillars{display:grid;grid-template-columns:repeat(4,1fr);gap:22px;}
.o-pill{position:relative;padding:40px 30px 36px;background:linear-gradient(180deg,#120c19,#0a070e);border:1px solid var(--line);border-radius:18px;overflow:hidden;
  transition:transform .45s cubic-bezier(.2,.8,.2,1),border-color .4s,box-shadow .4s;}
.o-pill::after{content:"";position:absolute;inset:auto -40% -60% auto;width:220px;height:220px;border-radius:50%;background:radial-gradient(circle,rgba(255,46,154,.35),transparent 70%);opacity:0;transition:opacity .4s;}
.o-pill:hover{transform:translateY(-12px) rotate(-1deg);border-color:var(--mag);box-shadow:0 30px 80px rgba(255,46,154,.25);}
.o-pill:hover::after{opacity:1;}
.o-pill-n{font-family:Anton,sans-serif;font-size:96px;line-height:.8;color:transparent;-webkit-text-stroke:1.5px var(--pink);display:block;margin-bottom:24px;}
.o-pill:nth-child(2) .o-pill-n{-webkit-text-stroke-color:var(--sun);}
.o-pill:nth-child(3) .o-pill-n{-webkit-text-stroke-color:var(--cy);}
.o-pill:nth-child(4) .o-pill-n{-webkit-text-stroke-color:#b56bff;}
.o-pill h3{font-size:34px !important;margin-bottom:14px;}
.o-pill p{font-size:15px;margin:0;}

/* COVERFLOW */
.o-albums{background:#000;padding:130px 0 110px;overflow:hidden;}
.o-center{text-align:center;}
.o-center p{max-width:640px;margin:22px auto 0;}
.o-flow{position:relative;height:520px;margin-top:40px;perspective:1400px;user-select:none;-webkit-user-select:none;touch-action:pan-y;cursor:grab;}
.o-flow:active{cursor:grabbing;}
.o-fi{position:absolute;left:50%;top:40px;width:360px;height:360px;margin-left:-180px;transition:transform .7s cubic-bezier(.2,.8,.2,1),opacity .7s,filter .7s;
  transform-style:preserve-3d;cursor:pointer;}
.o-fi img{width:100%;height:100%;object-fit:cover;border-radius:10px;display:block;box-shadow:0 30px 80px rgba(0,0,0,.8);
  -webkit-box-reflect:below 6px linear-gradient(transparent 62%,rgba(255,255,255,.22));pointer-events:none;}
.o-fi.on img{box-shadow:0 30px 90px rgba(255,46,154,.55),0 0 0 2px rgba(255,95,143,.8);}
.o-fcap{text-align:center;margin-top:-4px;min-height:80px;}
.o-fcap strong{display:block;font-family:Anton,sans-serif;font-weight:400;font-size:38px;color:#fff;text-transform:uppercase;line-height:1;}
.o-fcap span{font-size:12px;font-weight:800;letter-spacing:.28em;text-transform:uppercase;color:var(--pink);}
.o-nav-btn{position:absolute;top:220px;z-index:5;width:60px;height:60px;border-radius:50%;border:1px solid rgba(255,255,255,.35);background:rgba(7,5,10,.7);
  color:#fff;font-size:30px;line-height:1;cursor:pointer;backdrop-filter:blur(6px);transition:all .25s;display:flex;align-items:center;justify-content:center;padding:0;}
.o-nav-btn:hover{background:var(--mag);border-color:var(--pink);box-shadow:0 0 30px rgba(255,46,154,.8);}
.o-prev{left:4vw}.o-next{right:4vw}

.o-sounds{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;margin-top:70px;}
.o-sound{position:relative;aspect-ratio:1;border-radius:14px;overflow:hidden;display:flex;align-items:flex-end;padding:16px;isolation:isolate;
  border:1px solid var(--line);transition:transform .4s,box-shadow .4s,border-color .4s;}
.o-sound img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:-2;filter:saturate(1.2) brightness(.55);transition:transform .7s,filter .5s;}
.o-sound::before{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(180deg,transparent 30%,rgba(7,5,10,.95));}
.o-sound b{font-family:Anton,sans-serif;font-weight:400;font-size:22px;line-height:1;color:#fff;text-transform:uppercase;}
.o-sound em{display:block;font-style:normal;font-size:10px;font-weight:800;letter-spacing:.2em;color:var(--cy);margin-top:6px;}
.o-sound:hover{transform:translateY(-8px);border-color:var(--cy);box-shadow:0 20px 60px rgba(34,225,255,.25);}
.o-sound:hover img{transform:scale(1.12) rotate(2deg);filter:saturate(1.3) brightness(.8);}
.o-more{text-align:center;margin-top:56px;}

/* POSTER RAIL */
.o-place{background:radial-gradient(ellipse 50% 60% at 0% 100%,rgba(34,225,255,.12),transparent 70%),var(--bg);}
.o-rail{display:flex;gap:22px;overflow-x:auto;scroll-snap-type:x mandatory;scroll-behavior:smooth;padding:50px 8vw 60px;scrollbar-width:none;
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 7%,#000 93%,transparent);mask-image:linear-gradient(90deg,transparent,#000 7%,#000 93%,transparent);}
.o-rail::-webkit-scrollbar{display:none;}
.o-card{flex:none;width:240px;margin:0;scroll-snap-align:center;position:relative;border-radius:12px;overflow:hidden;background:#120c19;cursor:pointer;
  box-shadow:0 22px 60px rgba(0,0,0,.7);transition:transform .5s cubic-bezier(.2,.8,.2,1),box-shadow .5s;}
.o-card img{display:block;width:100%;aspect-ratio:2/3;object-fit:cover;transition:transform .7s ease;}
.o-card figcaption{position:absolute;left:0;right:0;bottom:0;padding:70px 16px 16px;background:linear-gradient(transparent,rgba(7,5,10,.96));
  transform:translateY(30%);opacity:0;transition:all .45s ease;}
.o-card figcaption span{display:block;font-size:9px;font-weight:800;letter-spacing:.26em;color:var(--cy);text-transform:uppercase;margin-bottom:6px;}
.o-card figcaption strong{display:block;font-family:Anton,sans-serif;font-weight:400;font-size:24px;color:#fff;line-height:1;text-transform:uppercase;}
.o-card:hover{transform:translateY(-14px) scale(1.05) rotate(-1deg);box-shadow:0 34px 90px rgba(255,46,154,.45),0 0 0 2px rgba(255,95,143,.7);z-index:3;}
.o-card:hover img{transform:scale(1.07);}
.o-card:hover figcaption{transform:none;opacity:1;}
.o-rail-wrap{position:relative;}
.o-rail-wrap .o-nav-btn{top:50%;transform:translateY(-50%);}

/* LICENSING (one door) */
.o-doors{background:#000;}
.o-one{position:relative;overflow:hidden;display:grid;grid-template-columns:1.05fr .95fr;gap:60px;align-items:center;padding:70px 64px;border-radius:26px;
  background:linear-gradient(#120a14,#120a14) padding-box,var(--grad) border-box;border:2px solid transparent;box-shadow:0 30px 120px rgba(255,46,154,.18);}
.o-one-head p{font-size:18px;color:#efe8f5;max-width:560px;margin:24px 0 32px;}
.o-steps{list-style:none;margin:0;padding:0;position:relative;z-index:1;}
.o-steps li{display:grid;grid-template-columns:70px 1fr;grid-template-rows:auto auto;column-gap:16px;padding:22px 0;border-bottom:1px solid rgba(255,255,255,.12);}
.o-steps li:last-child{border-bottom:0;}
.o-step-n{grid-row:1/3;font-family:Anton,sans-serif;font-size:54px;line-height:1;color:transparent;-webkit-text-stroke:1.5px var(--pink);}
.o-steps b{font-family:Anton,sans-serif;font-weight:400;font-size:28px;color:#fff;text-transform:uppercase;line-height:1.05;}
.o-steps li>span:last-child{font-size:15px;color:var(--mute);margin-top:4px;}
.o-globe{position:absolute;right:-80px;bottom:-80px;width:320px;height:320px;border-radius:50%;opacity:.16;pointer-events:none;
  background:repeating-radial-gradient(circle,transparent 0 18px,rgba(255,255,255,.5) 18px 19px),repeating-linear-gradient(90deg,transparent 0 28px,rgba(255,255,255,.4) 28px 29px);
  -webkit-mask-image:radial-gradient(circle,#000 60%,transparent 71%);mask-image:radial-gradient(circle,#000 60%,transparent 71%);animation:o-spin 40s linear infinite;}
@keyframes o-spin{to{transform:rotate(360deg)}}

/* FOUNDERS */
.o-founders{background:var(--bg2);}
.o-fgrid{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-top:64px;}
.o-fcard{position:relative;border-radius:22px;overflow:hidden;background:#000;border:1px solid var(--line);display:grid;grid-template-columns:.9fr 1.1fr;min-height:360px;transition:transform .45s,border-color .45s;}
.o-fcard:hover{transform:translateY(-8px);border-color:var(--mag);}
.o-fcard figure{margin:0;position:relative;overflow:hidden;}
.o-fcard figure img{width:100%;height:100%;object-fit:cover;filter:grayscale(.2) contrast(1.05);transition:transform .8s;}
.o-fcard:hover figure img{transform:scale(1.06);}
.o-fcard figure::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,transparent 60%,#000),linear-gradient(0deg,rgba(255,46,154,.25),transparent 50%);mix-blend-mode:normal;}
.o-fcard-in{padding:34px 30px;display:flex;flex-direction:column;justify-content:center;}
.o-fcard h3{font-size:44px !important;margin-bottom:8px;}
.o-role{font-size:11px;font-weight:800;letter-spacing:.24em;text-transform:uppercase;color:var(--pink);margin-bottom:16px;}
.o-fcard p{font-size:15px;margin:0;}
.o-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:2px;background:var(--line);border:1px solid var(--line);border-radius:16px;overflow:hidden;margin-top:30px;}
.o-stat{background:#0a070e;padding:34px 26px;}
.o-stat b{display:block;font-family:Anton,sans-serif;font-weight:400;font-size:72px;line-height:.95;background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent;}
.o-stat span{display:block;font-size:13px;line-height:1.5;margin-top:8px;}

/* ARTISTS */
.o-artists{background:linear-gradient(120deg,#4a0838 0%,#170818 45%,#05283a 100%);overflow:hidden;}
.o-artists::after{content:"";position:absolute;inset:0;pointer-events:none;opacity:.35;background:repeating-linear-gradient(90deg,transparent 0 120px,rgba(255,255,255,.03) 120px 121px);}
.o-agrid{position:relative;z-index:1;display:grid;grid-template-columns:1.1fr .9fr;gap:60px;align-items:center;}
.o-artists p{color:#f1e3ee;font-size:19px;}
.o-rules{list-style:none;margin:0;padding:0;}
.o-rules li{display:flex;gap:16px;align-items:flex-start;padding:16px 0;border-bottom:1px solid rgba(255,255,255,.15);color:#f5ecf3;font-size:16px;}
.o-rules li::before{content:"";flex:none;width:12px;height:12px;margin-top:6px;transform:rotate(45deg);background:var(--cy);box-shadow:0 0 12px var(--cy);}
.o-rules li:last-child::before{background:var(--sun);box-shadow:0 0 12px var(--sun);}
.o-rules b{color:#fff;}

/* FAQ */
.o-faq{background:var(--bg);}
.o-faq-grid{display:grid;grid-template-columns:.8fr 1.2fr;gap:70px;align-items:start;}
.o-q{border-bottom:1px solid var(--line);}
.o-q button{width:100%;display:flex;justify-content:space-between;align-items:center;gap:20px;background:none;border:0;cursor:pointer;padding:28px 0;text-align:left;
  font-family:Anton,sans-serif;font-size:28px;line-height:1.1;color:#fff;text-transform:uppercase;transition:color .25s;}
.o-q button:hover{color:var(--pink);}
.o-q button i{flex:none;width:34px;height:34px;border-radius:50%;border:1px solid rgba(255,255,255,.35);position:relative;transition:all .35s;}
.o-q button i::before,.o-q button i::after{content:"";position:absolute;left:50%;top:50%;width:12px;height:2px;margin:-1px 0 0 -6px;background:#fff;transition:transform .35s;}
.o-q button i::after{transform:rotate(90deg);}
.o-q.on button i{background:var(--mag);border-color:var(--mag);box-shadow:0 0 20px var(--mag);transform:rotate(180deg);}
.o-q.on button i::after{transform:rotate(0);}
.o-a{display:grid;grid-template-rows:0fr;transition:grid-template-rows .45s ease;}
.o-a>div{overflow:hidden;}
.o-a p{padding-bottom:26px;margin:0;font-size:16px;}
.o-q.on .o-a{grid-template-rows:1fr;}

/* CONTACT */
.o-contact{background:radial-gradient(ellipse 50% 70% at 0% 0%,rgba(255,46,154,.22),transparent 70%),radial-gradient(ellipse 50% 60% at 100% 100%,rgba(34,225,255,.14),transparent 70%),#000;padding:120px 0 70px;}
.o-cgrid{display:grid;grid-template-columns:1.2fr .8fr;gap:50px;align-items:end;}
.o-mail{display:inline-flex;align-items:center;gap:12px;font-family:Anton,sans-serif;font-size:clamp(26px,3vw,40px);color:#fff !important;text-transform:lowercase;letter-spacing:.01em;border-bottom:3px solid var(--mag);padding-bottom:4px;transition:color .25s,border-color .25s;}
.o-mail:hover{color:var(--cy) !important;border-color:var(--cy);}
.o-stub{margin-top:60px;border:2px dashed rgba(255,255,255,.2);border-radius:16px;padding:60px 24px;text-align:center;font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:#7d7389;}

/* FOOTER */
.o-foot{background:#000;border-top:1px solid rgba(255,255,255,.08);padding:60px 0 40px;}
.o-foot-grid{display:flex;justify-content:space-between;align-items:center;gap:30px;flex-wrap:wrap;}
.o-foot img{height:90px;width:auto;}
.o-foot nav{display:flex;gap:26px;flex-wrap:wrap;}
.o-foot nav a{font-size:11px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:#cfc6da !important;}
.o-foot nav a:hover{color:var(--pink) !important;}
.o-foot small{display:block;margin-top:30px;font-size:12px;color:#5f566c;}

/* PAGE HERO (inner pages) */
.o-phero{position:relative;padding:220px 0 70px;overflow:hidden;}
.o-phero h1{font-size:clamp(70px,12vw,190px) !important;line-height:.84 !important;}
.o-phero p{max-width:620px;font-size:19px;margin-top:26px;}
.o-phero .o-glow{opacity:.8;}
.o-count{position:absolute;right:28px;bottom:70px;text-align:right;}
.o-count b{display:block;font-family:Anton,sans-serif;font-weight:400;font-size:120px;line-height:.85;color:transparent;-webkit-text-stroke:2px var(--cy);}
.o-count span{font-size:11px;font-weight:800;letter-spacing:.3em;text-transform:uppercase;color:var(--cy);}

/* TOOLBAR + GRIDS */
.o-tools{position:sticky;top:64px;z-index:20;display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap;padding:18px 0;margin-bottom:40px;
  background:rgba(7,5,10,.9);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line);}
.o-chips{display:flex;gap:8px;flex-wrap:wrap;}
.o-chip{font:800 11px/1 Inter,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:#d6cee0;background:transparent;border:1px solid #3a2e48;border-radius:999px;padding:12px 18px;cursor:pointer;transition:all .25s;}
.o-chip sup{font-size:9px;color:var(--pink);margin-left:3px;letter-spacing:0;}
.o-chip:hover{border-color:var(--pink);color:#fff;}
.o-chip.on{background:var(--grad);border-color:transparent;color:#fff;box-shadow:0 0 26px rgba(255,46,154,.5);}
.o-chip.on sup{color:#fff;}
.o-search{flex:0 1 320px;background:#0e0a14;border:1px solid #3a2e48;border-radius:999px;padding:13px 20px;color:#fff;font:500 14px Inter,sans-serif;outline:none;transition:border-color .25s,box-shadow .25s;}
.o-search:focus{border-color:var(--cy);box-shadow:0 0 0 3px rgba(34,225,255,.2);}
.o-agrid2{display:grid;grid-template-columns:repeat(4,1fr);gap:46px 34px;padding:10px 0 40px;}
.o-al{position:relative;cursor:pointer;perspective:900px;}
.o-al-in{position:relative;transition:transform .25s ease-out;transform-style:preserve-3d;}
.o-vinyl{position:absolute;top:4%;left:4%;width:92%;height:92%;border-radius:50%;z-index:0;transition:transform .7s cubic-bezier(.2,.8,.2,1);
  background:radial-gradient(circle,var(--mag) 0 9%,#111 9.5% 10.5%,transparent 11%),repeating-radial-gradient(circle,#0b0b0b 0 2px,#1d1d1d 2px 3px);box-shadow:0 10px 30px rgba(0,0,0,.7);}
.o-al:hover .o-vinyl{transform:translateX(26%) rotate(180deg);}
.o-al img{position:relative;z-index:1;width:100%;aspect-ratio:1;object-fit:cover;border-radius:8px;display:block;box-shadow:0 20px 50px rgba(0,0,0,.7);transition:box-shadow .4s;}
.o-al:hover img{box-shadow:0 26px 70px rgba(255,46,154,.45),0 0 0 2px rgba(255,95,143,.7);}
.o-al-cap{margin-top:18px;}
.o-al-cap strong{display:block;font-family:Anton,sans-serif;font-weight:400;font-size:24px;color:#fff;text-transform:uppercase;line-height:1.05;}
.o-al-cap span{display:block;font-size:12px;color:var(--mute);margin-top:4px;}
.o-al-cap em{display:inline-block;font-style:normal;font-size:9px;font-weight:800;letter-spacing:.2em;text-transform:uppercase;color:var(--cy);border:1px solid rgba(34,225,255,.4);border-radius:99px;padding:5px 9px;margin-top:10px;}
.o-pgrid{display:grid;grid-template-columns:repeat(5,1fr);gap:26px;padding:10px 0 40px;}
.o-pgrid .o-card{width:auto;}
.o-pgrid .o-card{background:#0e0a14;border:1px solid var(--line);}
.o-pgrid .o-card figcaption{position:static;transform:none;opacity:1;padding:14px 14px 16px;background:none;}
.o-pgrid .o-card figcaption strong{font-size:21px;}
.o-empty{grid-column:1/-1;text-align:center;padding:80px 0;font-size:15px;}
.o-hide{display:none !important;}

/* LIGHTBOX */
.o-lb{position:fixed;inset:0;z-index:2000;display:flex;align-items:center;justify-content:center;padding:30px;background:rgba(5,3,8,.86);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  opacity:0;pointer-events:none;transition:opacity .35s;}
.o-lb.on{opacity:1;pointer-events:auto;}
.o-lb-box{display:grid;grid-template-columns:auto 1fr;gap:46px;align-items:center;max-width:1080px;width:100%;transform:scale(.94);transition:transform .45s cubic-bezier(.2,.8,.2,1);}
.o-lb.on .o-lb-box{transform:none;}
.o-lb-box img{max-height:76vh;max-width:52vw;border-radius:12px;box-shadow:0 30px 120px rgba(255,46,154,.45);}
.o-lb h3{font-size:clamp(44px,5vw,78px) !important;margin:6px 0 12px;}
.o-lb .o-lb-k{font-size:11px;font-weight:800;letter-spacing:.3em;text-transform:uppercase;color:var(--cy);}
.o-lb .o-lb-a{font-size:18px;color:#efe8f5;margin-bottom:30px;}
.o-lb .o-ctas{justify-content:flex-start;}
.o-lb .o-ctas .o-btn{flex-direction:row;padding:17px 26px;font-size:12px;}
.o-lb-x{position:absolute;top:22px;right:26px;width:50px;height:50px;border-radius:50%;background:none;border:1px solid rgba(255,255,255,.4);color:#fff;font-size:26px;cursor:pointer;line-height:1;}
.o-lb-x:hover{background:var(--mag);border-color:var(--mag);}
.o-lb-arrow{position:absolute;top:50%;transform:translateY(-50%);width:54px;height:54px;border-radius:50%;background:rgba(0,0,0,.4);border:1px solid rgba(255,255,255,.3);color:#fff;font-size:30px;cursor:pointer;}
.o-lb-arrow:hover{background:var(--mag);}
.o-lb-l{left:18px}.o-lb-r{right:18px}

/* STREAMING */
.o-lb-album{grid-template-columns:300px 1fr;align-items:start;gap:40px;max-width:1180px;}
.o-la-side img{width:100%;max-width:300px;max-height:none;border-radius:12px;display:block;margin-bottom:22px;}
.o-la-side .o-ctas{flex-direction:column;align-items:stretch;}
.o-la-side .o-ctas .o-btn{justify-content:center;white-space:normal;text-align:center;}
.o-la-main{min-width:0;display:flex;flex-direction:column;max-height:84vh;}
.o-la-main h3{font-size:clamp(40px,4.4vw,66px) !important;}
.o-la-main .o-lb-a{margin-bottom:8px;}
.o-la-desc{font-size:14px;margin:0 0 14px;max-width:70ch;}
.o-tl{overflow-y:auto;min-height:0;padding-right:6px;scrollbar-width:thin;scrollbar-color:#4a2a55 transparent;border-top:1px solid var(--line);}
.o-tl-note{font-size:14px;padding:22px 0;margin:0;}
.o-tr{display:grid;grid-template-columns:40px minmax(0,1.3fr) minmax(0,1fr) auto 110px;align-items:center;gap:14px;padding:10px 6px;border-bottom:1px solid var(--line);cursor:pointer;transition:background .2s;}
.o-tr:hover,.o-tr.on{background:rgba(255,46,154,.08);}
.o-tr.sub{grid-template-columns:40px minmax(0,1.3fr) minmax(0,1fr) auto;padding-left:26px;background:rgba(255,255,255,.02);}
.o-tp{width:38px;height:38px;border-radius:50%;border:1px solid rgba(255,255,255,.35);background:transparent;color:#fff;display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;transition:all .2s;}
.o-tp svg,.o-pbar svg,.o-al-play svg,.o-fplay svg{width:16px;height:16px;fill:currentColor;}
.o-tr:hover .o-tp,.o-tr.on .o-tp{background:var(--grad);border-color:transparent;box-shadow:0 0 18px rgba(255,46,154,.6);}
.o-tn{min-width:0;}
.o-tn b{display:block;font-weight:700;font-size:15px;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.o-tr.sub .o-tn b{font-weight:600;font-size:13px;color:#d6cee0;}
.o-tn small{display:block;font-size:12px;color:var(--mute);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.o-tw{width:100%;height:34px;display:block;}
.o-tm{font-size:12px;color:#cfc6da;white-space:nowrap;font-variant-numeric:tabular-nums;}
.o-tvb{font:800 10px/1 Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--cy);background:transparent;border:1px solid rgba(34,225,255,.4);border-radius:99px;padding:8px 10px;cursor:pointer;white-space:nowrap;}
.o-tvb:hover,.o-tvb[aria-expanded="true"]{background:var(--cy);color:#07050a;}
.o-al-play{position:absolute;z-index:3;right:12px;bottom:12px;width:52px;height:52px;border-radius:50%;border:0;background:var(--grad);color:#fff;display:flex;align-items:center;justify-content:center;cursor:pointer;
  box-shadow:0 0 30px rgba(255,46,154,.7);opacity:0;transform:translateY(10px) scale(.9);transition:all .3s;}
.o-al-play svg{width:20px;height:20px;}
.o-al:hover .o-al-play{opacity:1;transform:none;}
.o-fplay{margin-top:16px;padding:14px 24px;}
.o-pbar{position:fixed !important;left:0;right:0;bottom:0;z-index:1500;overflow:visible !important;display:grid;grid-template-columns:auto minmax(120px,240px) auto minmax(0,1fr) 90px auto auto;align-items:center;gap:18px;
  padding:12px max(18px,env(safe-area-inset-right,0px)) calc(12px + env(safe-area-inset-bottom,0px)) max(18px,env(safe-area-inset-left,0px));
  background:rgba(10,7,14,.94);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-top:1px solid rgba(255,46,154,.35);box-shadow:0 -20px 60px rgba(0,0,0,.6);}
.o-pbar[hidden]{display:none !important;}
.o-pb-cover{width:52px;height:52px;border-radius:6px;object-fit:cover;}
.o-pb-meta{min-width:0;}
.o-pb-meta strong{display:block;color:#fff;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.o-pb-meta span{display:block;font-size:12px;color:var(--mute);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.o-pb-ctl{display:flex;align-items:center;gap:8px;}
.o-pb-ctl button,.o-pb-x{background:none;border:0;color:#fff;cursor:pointer;width:38px;height:38px;display:flex;align-items:center;justify-content:center;border-radius:50%;padding:0;}
.o-pb-ctl button:hover,.o-pb-x:hover{background:rgba(255,255,255,.1);}
.o-pb-ctl .o-pb-play{width:48px;height:48px;background:var(--grad);box-shadow:0 0 24px rgba(255,46,154,.6);}
.o-pb-ctl .o-pb-play:hover{background:var(--grad);}
.o-pb-wave{display:flex;align-items:center;gap:12px;min-width:0;font-size:12px;color:#cfc6da;font-variant-numeric:tabular-nums;}
.o-pb-wave canvas{flex:1;min-width:0;height:40px;cursor:pointer;}
.o-pb-vol{width:90px;accent-color:#ff2e9a;}
.o-pb-lic{padding:12px 18px;font-size:11px;}
.o-pb-x{font-size:24px;}

/* ABOUT */
.o-about-hero{padding:210px 0 110px;overflow:hidden;}
.o-about-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:70px;align-items:center;}
.o-about-hero h1{font-size:clamp(70px,10vw,160px) !important;line-height:.85 !important;margin-bottom:34px;}
.o-about-hero p{font-size:18px;}
.o-tagline{font-family:Anton,sans-serif;font-size:30px;text-transform:uppercase;color:#fff;margin:26px 0 34px;letter-spacing:.02em;}
.o-tagline span{color:var(--pink);}
.o-collage{position:relative;height:560px;}
.o-pol{position:absolute;background:#fff;padding:10px 10px 38px;border-radius:4px;box-shadow:0 30px 80px rgba(0,0,0,.7);transition:transform .5s cubic-bezier(.2,.8,.2,1),z-index 0s;margin:0;}
.o-pol img{display:block;width:100%;height:100%;object-fit:cover;}
.o-pol figcaption{position:absolute;left:0;right:0;bottom:9px;text-align:center;font:700 10px/1 Inter,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:#333;}
.o-pol:hover{transform:rotate(0) scale(1.06) !important;z-index:9;}
.o-person{border-top:1px solid var(--line);}
.o-pgrid2{display:grid;grid-template-columns:.85fr 1.15fr;gap:80px;align-items:start;}
.o-person.r .o-pgrid2{grid-template-columns:1.15fr .85fr;}
.o-person.r .o-ptext{order:-1;}
.o-photos{position:sticky;top:120px;display:grid;grid-template-columns:1fr 1fr;gap:14px;}
.o-photos figure{margin:0;border-radius:14px;overflow:hidden;position:relative;}
.o-photos figure:first-child{grid-column:1/-1;aspect-ratio:4/3;}
.o-photos figure:not(:first-child){aspect-ratio:1;}
.o-photos img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .8s;}
.o-photos figure:hover img{transform:scale(1.07);}
.o-photos figure::after{content:"";position:absolute;inset:0;border-radius:14px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.08);}
.o-bigname{font-size:clamp(64px,8vw,130px) !important;line-height:.86 !important;margin:0 0 10px;}
.o-bigname span{display:block;color:transparent;-webkit-text-stroke:2px var(--pink);}
.o-person.r .o-bigname span{-webkit-text-stroke-color:var(--cy);}
.o-ptext .o-role{font-size:12px;margin-bottom:30px;}
.o-ptext p{font-size:17px;}
.o-ptext p a{color:#fff !important;border-bottom:1px solid var(--pink);}
.o-ptext p b{color:#fff;}
.o-creds{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:0 0 36px;}
.o-pgrid2>*,.o-cred{min-width:0;overflow-wrap:anywhere;}
.o-creds.n4{grid-template-columns:repeat(2,minmax(0,1fr));}
.o-stage-h{font-size:28px !important;margin:34px 0 14px;}
.o-stage{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 24px;}
.o-stage li{display:flex;flex-direction:column;gap:2px;padding:12px 0;border-bottom:1px solid var(--line);}
.o-stage b{font-size:10px;font-weight:800;letter-spacing:.2em;text-transform:uppercase;color:var(--cy);}
.o-stage span{font-size:15px;color:#efe8f5;}
.o-cred{border:1px solid var(--line);border-radius:14px;padding:18px 16px;background:#0b0810;}
.o-cred b{display:block;font-family:Anton,sans-serif;font-weight:400;font-size:40px;line-height:1;background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent;}
.o-person.r .o-cred b{background:linear-gradient(95deg,var(--cy),#8fe9ff);-webkit-background-clip:text;background-clip:text;}
.o-cred span{display:block;font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-top:6px;color:#cfc6da;}
.o-panel{background:#000;}
.o-panel-card{display:grid;grid-template-columns:1fr 1fr;gap:0;border-radius:24px;overflow:hidden;border:1px solid var(--line);
  background:linear-gradient(#0c0910,#0c0910) padding-box,linear-gradient(130deg,var(--mag),var(--cy)) border-box;border:2px solid transparent;}
.o-panel-card figure{margin:0;background:#120c19;display:flex;align-items:center;}
.o-panel-card figure img{width:100%;display:block;}
.o-panel-in{padding:50px 46px;}
.o-panel-in h3{font-size:clamp(36px,3.6vw,54px) !important;margin:0 0 14px;}
.o-panel-in .o-role{margin-bottom:24px;}
.o-panel-in p{font-size:15px;}

@media(max-width:1080px){
  .o-pillars{grid-template-columns:1fr 1fr;}
  .o-sounds{grid-template-columns:repeat(3,1fr);}
  .o-agrid2{grid-template-columns:repeat(3,1fr);}
  .o-pgrid{grid-template-columns:repeat(4,1fr);}
  .o-fcard{grid-template-columns:1fr;}
  .o-fcard figure{height:300px;}
  .o-fcard figure::after{background:linear-gradient(180deg,transparent 60%,#000);}
  .o-stats{grid-template-columns:1fr 1fr;}
}
@media(max-width:900px){
  .o-links{position:fixed;top:0;left:0;right:0;bottom:0;flex-direction:column;justify-content:center;gap:26px;background:rgba(7,5,10,.97);
    opacity:0;pointer-events:none;transition:opacity .3s;z-index:-1;}
  .o-top.open .o-links{opacity:1;pointer-events:auto;}
  .o-links a:not(.o-btn){font-size:18px;}
  .o-burger{display:block;}
  .o-one,.o-fgrid,.o-agrid,.o-faq-grid,.o-cgrid,.o-about-grid,.o-pgrid2,.o-person.r .o-pgrid2,.o-panel-card{grid-template-columns:1fr;}
  .o-person.r .o-ptext{order:0;}
  .o-photos{position:relative;top:0;}
  .o-faq-grid{gap:30px;}
  .o-lb-box{grid-template-columns:1fr;gap:24px;text-align:center;max-height:100%;overflow:auto;}
  .o-lb-box img{max-width:80vw;max-height:48vh;margin:0 auto;}
  .o-lb-album{grid-template-columns:1fr;text-align:left;padding-top:56px;}
  .o-la-side{display:grid;grid-template-columns:120px 1fr;gap:16px;align-items:start;}
  .o-la-side img{max-width:120px;margin:0;}
  .o-la-main{max-height:none;}
  .o-tl{overflow:visible;}
  .o-tr{grid-template-columns:38px minmax(0,1fr) auto;row-gap:6px;}
  .o-tr .o-tw{grid-column:2/-1;grid-row:2;height:28px;}
  .o-tr .o-tm{grid-column:3;grid-row:1;}
  .o-tr>span:last-child:empty{display:none;}
  .o-tr:has(.o-tvb) .o-tw{grid-column:2;}
  .o-tr .o-tvb{grid-column:3;grid-row:2;}
  .o-tr.sub{grid-template-columns:38px minmax(0,1fr) auto;}
  .o-pbar{grid-template-columns:auto minmax(0,1fr) auto auto;gap:10px;}
  .o-pb-wave{grid-column:1/-1;grid-row:2;}
  .o-pb-vol,.o-pb-lic{display:none;}
  .o-pb-ctl button[data-pb="prev"]{display:none;}
  .o-al-play{opacity:1;transform:none;width:44px;height:44px;}
  .o-lb .o-ctas{justify-content:center;}
  .o-collage{height:440px;}
  .o-count{position:static;text-align:left;margin-top:30px;}
}
@media(max-width:640px){
  .o{font-size:16px;}
  .o-sec{padding:90px 0;}
  .o-wrap{padding:0 20px;}
  .o-nav,.o-top.solid .o-nav{padding:10px 16px;}
  .o-banner{font-size:9px;letter-spacing:.1em;padding:8px 12px;}
  .o-logo img{height:48px;}
  .o-wall-row img{width:130px;height:130px;}
  .o-hero .o-sub{font-size:17px;}
  .o-hero-in{padding-top:150px;}
  .o-ctas .o-btn{width:100%;justify-content:center;white-space:normal;text-align:center;line-height:1.3;}
  .o-hero h1{font-size:50px !important;line-height:.92 !important;}
  .o-agrid>*{min-width:0;}
  .o-pillars,.o-stats{grid-template-columns:1fr;}
  .o-sounds{grid-template-columns:1fr 1fr;}
  .o-flow{height:400px;}
  .o-fi{width:240px;height:240px;margin-left:-120px;}
  .o-nav-btn{display:none;}
  .o-track span{font-size:34px;margin:0 18px;}
  .o-band .o-track span{font-size:32px;}
  .o-tape{height:190px;}
  .o-card{width:180px;}
  .o-card figcaption{transform:none;opacity:1;padding-top:50px;}
  .o-card figcaption strong{font-size:20px;}
  .o-one{padding:40px 24px;gap:30px;}
  .o-step-n{font-size:40px;}
  .o-steps li{grid-template-columns:52px 1fr;}
  .o-agrid2{grid-template-columns:1fr 1fr;gap:34px 18px;}
  .o-al-cap strong{font-size:19px;}
  .o-pgrid{grid-template-columns:1fr 1fr;gap:16px;}
  .o-tools{top:58px;}
  .o-search{flex:1 1 100%;}
  .o-chips{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;width:100%;}
  .o-chip{flex:none;}
  .o-creds{grid-template-columns:1fr 1fr 1fr;gap:8px;}
  .o-creds.n4{grid-template-columns:1fr 1fr;}
  .o-stage{grid-template-columns:1fr;}
  .o-cred{padding:14px 10px;}
  .o-cred b{font-size:22px;}
  .o-cred span{font-size:9px;letter-spacing:.06em;}
  .o-q button{font-size:22px;}
  .o-panel-in{padding:34px 24px;}
  .o-collage{height:380px;}
  .o-lb{padding:16px;}
  .o-lb-arrow{display:none;}
  .o-phero{padding-top:170px;}
  .o-count b{font-size:80px;}
}
/* LEARN (production music explainer) */
.o-lhero{position:relative;padding:210px 0 90px;overflow:hidden;}
.o-lhero .o-wrap{display:grid;grid-template-columns:1.25fr .75fr;gap:60px;align-items:center;}
.o-lhero h1{font-size:clamp(58px,8.6vw,140px) !important;line-height:.86 !important;}
.o-lhero p{max-width:600px;font-size:19px;margin-top:26px;}
.o-scrollcue{display:inline-flex;align-items:center;gap:12px;margin-top:40px;font-size:11px;font-weight:800;letter-spacing:.3em;text-transform:uppercase;color:var(--mute);}
.o-scrollcue i{width:2px;height:38px;background:linear-gradient(var(--cy),transparent);animation:o-cue 1.8s ease-in-out infinite;transform-origin:top;}
@keyframes o-cue{0%{transform:scaleY(0)}50%{transform:scaleY(1)}100%{transform:scaleY(1);opacity:0}}
.o-deck{position:relative;width:100%;max-width:440px;aspect-ratio:1;margin:auto;}
.o-disc{position:absolute;inset:6%;border-radius:50%;background:repeating-radial-gradient(circle,#141018 0 2px,#08060a 2px 4px);
  box-shadow:0 0 0 2px #241a2e,0 0 90px rgba(255,46,154,.35),inset 0 0 60px #000;animation:o-spin 3.2s linear infinite;}
.o-disc::before{content:"";position:absolute;inset:0;border-radius:50%;background:conic-gradient(from 0deg,transparent 0 40deg,rgba(255,255,255,.09) 60deg,transparent 80deg 220deg,rgba(34,225,255,.08) 240deg,transparent 260deg);}
.o-disc b{position:absolute;inset:34%;border-radius:50%;background:var(--grad);display:flex;align-items:center;justify-content:center;box-shadow:0 0 30px rgba(255,46,154,.6);}
.o-disc b img{width:70%;}
.o-disc b::after{content:"";position:absolute;width:7%;height:7%;border-radius:50%;background:#07050a;}
@keyframes o-spin{to{transform:rotate(360deg)}}
.o-arm{position:absolute;top:-2%;right:2%;width:12%;height:62%;transform-origin:50% 8%;transform:rotate(-34deg);animation:o-drop 1.4s 1s cubic-bezier(.5,0,.2,1) forwards;}
.o-arm::before{content:"";position:absolute;left:50%;top:0;width:28px;height:28px;margin-left:-14px;border-radius:50%;background:#2a2033;box-shadow:0 0 0 3px #3a2d45;}
.o-arm::after{content:"";position:absolute;left:50%;top:14px;bottom:0;width:6px;margin-left:-3px;border-radius:3px;background:linear-gradient(#cfc6d8,#8c8396);}
.o-arm i{position:absolute;left:50%;bottom:-6%;width:26px;height:40px;margin-left:-13px;border-radius:5px;background:var(--cy);box-shadow:0 0 22px var(--cy);}
@keyframes o-drop{to{transform:rotate(4deg)}}
.o-chap{border-top:1px solid var(--line);}
.o-chap-grid{display:grid;grid-template-columns:.9fr 1.1fr;gap:70px;align-items:center;}
.o-chap p{font-size:18px;}
.o-pipe{position:relative;display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:70px;}
.o-pipe::before{content:"";position:absolute;left:12%;right:12%;top:44px;height:2px;background:var(--line);}
.o-pipe::after{content:"";position:absolute;left:12%;top:39px;width:12px;height:12px;border-radius:50%;background:var(--cy);box-shadow:0 0 18px var(--cy),0 0 40px var(--cy);opacity:0;}
.o-pipe.in::after{animation:o-travel 3.6s 1.2s ease-in-out infinite;}
@keyframes o-travel{0%{left:12%;opacity:0}8%{opacity:1}92%{opacity:1}100%{left:calc(88% - 12px);opacity:0}}
.o-pipe.money::after{background:var(--sun);box-shadow:0 0 18px var(--sun),0 0 40px var(--sun);}
.o-node{position:relative;text-align:center;opacity:0;transform:translateY(20px);transition:all .7s cubic-bezier(.2,.8,.2,1);}
.o-pipe.in .o-node{opacity:1;transform:none;}
.o-pipe.in .o-node:nth-child(2){transition-delay:.25s}.o-pipe.in .o-node:nth-child(3){transition-delay:.5s}.o-pipe.in .o-node:nth-child(4){transition-delay:.75s}
.o-node b{display:flex;align-items:center;justify-content:center;width:88px;height:88px;margin:0 auto 18px;border-radius:50%;background:#0d0912;border:2px solid var(--line);
  font:400 30px/1 Anton,sans-serif;color:#fff;position:relative;z-index:1;}
.o-pipe.in .o-node b{animation:o-ping 3.6s ease-in-out infinite;}
.o-pipe.in .o-node:nth-child(1) b{animation-delay:1.2s}.o-pipe.in .o-node:nth-child(2) b{animation-delay:2.2s}
.o-pipe.in .o-node:nth-child(3) b{animation-delay:3.2s}.o-pipe.in .o-node:nth-child(4) b{animation-delay:4.2s}
@keyframes o-ping{0%,30%,100%{border-color:var(--line);box-shadow:none}10%{border-color:var(--pink);box-shadow:0 0 34px rgba(255,46,154,.7)}}
.o-pipe.money.in .o-node b{animation-name:o-ping2;}
@keyframes o-ping2{0%,30%,100%{border-color:var(--line);box-shadow:none}10%{border-color:var(--sun);box-shadow:0 0 34px rgba(255,138,31,.75)}}
.o-node span{display:block;font-size:13px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#fff;line-height:1.4;}
.o-why{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:70px;}
.o-why div{padding:30px 28px;border:1px solid var(--line);border-radius:18px;background:linear-gradient(180deg,#120c19,#0a070e);}
.o-why h3{font:400 30px/1 Anton,sans-serif !important;text-transform:uppercase;color:#fff;margin:0 0 12px;}
.o-why p{font-size:15px !important;margin:0;}
.o-cuts{display:flex;flex-direction:column;gap:14px;}
.o-cut{display:grid;grid-template-columns:150px 1fr 54px;gap:16px;align-items:center;font-size:12px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:#fff;}
.o-cut em{font-style:normal;color:var(--mute);text-align:right;letter-spacing:.06em;}
.o-bar{height:34px;border-radius:8px;background:#120c19;overflow:hidden;}
.o-bar i{display:block;height:100%;width:0;border-radius:8px;background:repeating-linear-gradient(90deg,rgba(255,255,255,.55) 0 2px,transparent 2px 6px),var(--grad);
  -webkit-mask:repeating-linear-gradient(90deg,#000 0 3px,transparent 3px 5px);transition:width 1.4s cubic-bezier(.2,.8,.2,1);}
.o-cuts.in .o-bar i{width:var(--w);}
.o-lics{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:60px;}
.o-lic{padding:34px 30px;border:1px solid var(--line);border-radius:20px;background:linear-gradient(180deg,#120c19,#0a070e);}
.o-lic h3{font:400 34px/1 Anton,sans-serif !important;text-transform:uppercase;color:#fff;margin:26px 0 14px;}
.o-lic p{font-size:15px !important;margin:0;}
.o-ico{position:relative;height:120px;border-radius:14px;background:#08060b;overflow:hidden;}
.o-ico.sync .f{position:absolute;left:0;right:0;top:18px;height:34px;background:repeating-linear-gradient(90deg,#2b2236 0 44px,transparent 44px 52px);
  border-top:5px dotted #3a2d45;border-bottom:5px dotted #3a2d45;animation:o-slide 3s linear infinite;width:200%;}
.o-ico.sync .w{position:absolute;left:0;bottom:16px;height:36px;width:200%;background:repeating-linear-gradient(90deg,var(--cy) 0 3px,transparent 3px 7px);
  -webkit-mask:linear-gradient(transparent,#000 30%,#000 70%,transparent);animation:o-slide 3s linear infinite reverse;opacity:.85;}
@keyframes o-slide{to{transform:translateX(-50%)}}
.o-ico.sync::after{content:"";position:absolute;left:50%;top:10px;bottom:10px;width:2px;background:var(--pink);box-shadow:0 0 14px var(--pink);}
.o-ico.needle .d{position:absolute;left:50%;top:50%;width:96px;height:96px;margin:-48px 0 0 -48px;border-radius:50%;
  background:repeating-radial-gradient(circle,#1b1522 0 2px,#09070c 2px 4px);animation:o-spin 2s linear infinite;}
.o-ico.needle .d::after{content:"";position:absolute;inset:36%;border-radius:50%;background:var(--grad);}
.o-ico.needle .a{position:absolute;left:calc(50% + 40px);top:8px;width:6px;height:64px;border-radius:3px;background:#bdb3c9;transform-origin:50% 0;animation:o-ndl 4s ease-in-out infinite;}
.o-ico.needle .a::after{content:"";position:absolute;left:-5px;bottom:-8px;width:16px;height:14px;border-radius:3px;background:var(--cy);box-shadow:0 0 14px var(--cy);}
@keyframes o-ndl{0%,15%{transform:rotate(-30deg)}35%,80%{transform:rotate(12deg)}100%{transform:rotate(-30deg)}}
.o-ico.blanket{display:grid;grid-template-columns:repeat(8,1fr);gap:6px;padding:14px;}
.o-ico.blanket i{border-radius:4px;background:#1a1322;animation:o-lite 3.2s ease-in-out infinite;}
@keyframes o-lite{0%,60%,100%{background:#1a1322;box-shadow:none}25%{background:var(--pink);box-shadow:0 0 12px var(--pink)}}
.o-note{margin-top:46px;padding:22px 28px;border-left:3px solid var(--sun);background:rgba(255,138,31,.07);border-radius:0 12px 12px 0;color:#fff;font-size:16px;font-weight:600;}
.o-fit{display:grid;grid-template-columns:1fr 1.1fr;gap:70px;align-items:center;}
.o-funnel{position:relative;width:100%;}
.o-funnel svg{width:100%;height:auto;display:block;overflow:visible;}
.o-funnel .ln{fill:none;stroke:#2c2238;stroke-width:2;}
.o-funnel .fl{fill:none;stroke-width:3;stroke-dasharray:10 18;stroke-linecap:round;animation:o-dash 1.6s linear infinite;}
@keyframes o-dash{to{stroke-dashoffset:-56}}
.o-funnel .cmp{fill:#120c19;stroke:#3a2d45;stroke-width:2;}
.o-funnel .hub{fill:#0d0912;stroke:url(#ogr);stroke-width:4;}
.o-funnel text{font-family:Inter,sans-serif;font-weight:800;fill:#fff;letter-spacing:.14em;}
.o-terr{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:40px;}
.o-terr div{padding:28px 26px;border-radius:18px;border:1px solid var(--line);background:linear-gradient(180deg,#120c19,#0a070e);}
.o-terr div:first-child{box-shadow:inset 0 3px 0 var(--cy);}
.o-terr div:last-child{box-shadow:inset 0 3px 0 var(--pink);}
.o-terr h3{font:400 30px/1 Anton,sans-serif !important;text-transform:uppercase;color:#fff;margin:0 0 12px;}
.o-terr p{font-size:15px !important;margin:0;}
.o-terr b{color:#fff;}
.o-lcta{text-align:center;}
.o-lcta p{max-width:560px;margin:24px auto 0;font-size:18px;}
.o-lcta .o-ctas{justify-content:center;margin-top:36px;}
@media(max-width:900px){
  .o-lhero .o-wrap,.o-chap-grid,.o-fit{grid-template-columns:1fr;gap:40px;}
  .o-deck{max-width:300px;}
  .o-why,.o-lics,.o-terr{grid-template-columns:1fr;}
  .o-pipe{grid-template-columns:1fr 1fr;row-gap:34px;}
  .o-pipe::before,.o-pipe::after{display:none;}
}
@media(max-width:640px){
  .o-lhero{padding:170px 0 60px;}
  .o-cut{grid-template-columns:96px 1fr 44px;gap:10px;font-size:10px;}
  .o-node b{width:70px;height:70px;font-size:24px;}
}
@media(prefers-reduced-motion:reduce){
  .o-disc,.o-ico *,.o-funnel .fl,.o-pipe::after,.o-node b,.o-scrollcue i{animation:none !important;}
  .o-arm{animation:none;transform:rotate(4deg);}
  .o-bar i{transition:none;}
}
@media(prefers-reduced-motion:reduce){
  .o-wall-row,.o-track,.o-eq i,.o-neon,.o-globe{animation:none !important;}
  .o-up,.o-reveal{opacity:1 !important;transform:none !important;animation:none !important;}
}
"""

JS = r"""
(function(){
var M=document.getElementById('ocho-mount');if(!M)return;
var D=__DATA__,CSS=__CSS__;
if(!document.getElementById('ocho-css')){var st=document.createElement('style');st.id='ocho-css';st.textContent=CSS;document.head.appendChild(st);}
var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
var page,lang,t,timers=[],io;

function esc(x){return String(x==null?'':x).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function route(){
  if(D.preview){var h=(location.hash||'').replace(/^#\/?/,'').replace(/\?.*$/,'').split('/');lang=h[0]==='es'?'es':'en';page=['home','about','albums','placements','learn'].indexOf(h[1])>=0?h[1]:'home';}
  else{lang=M.getAttribute('data-lang')==='es'?'es':'en';page=M.getAttribute('data-page')||'home';}
  t=D.t[lang];
}
function href(p,l){l=l||lang;return D.preview?'#/'+l+'/'+p:(M.getAttribute('data-test')?D.testPaths:D.paths)[l][p];}
function cat(c){return lang==='es'?(D.catsEs[c]||c):c;}
function drive(v){var m=String(v).match(/drive\.google\.com\/(?:file\/d\/|open\?id=|uc\?(?:export=\w+&)?id=)([\w-]+)/);return m?'https://lh3.googleusercontent.com/d/'+m[1]+'=w900':v;}
function src(v,kind,thumb){v=String(v||'').trim();if(!v)return '';if(/^https?:\/\//.test(v))return drive(v);v=v.replace(/\.jpg$/i,'');return D.base+kind+'/'+(thumb?'thumb/':'')+v+'.jpg';}
function photo(n){return D.base+'photos/'+n+'.jpg';}
function pimg(n,alt){return '<img src="'+photo(n)+'" alt="'+esc(alt)+'" loading="lazy" style="object-position:'+(D.pos[n]||'50% 30%')+'">';}
function mail(){return D.email[0]+'@'+D.email[1];}
function track(items,cls){var h='';items.forEach(function(x){h+='<span>'+esc(x)+'</span><i></i>';});return '<div class="o-track'+(cls||'')+'">'+h+h+'</div>';}

/* ---------- shared blocks ---------- */
function nav(){
  var L=function(p,label){return '<a href="'+href(p)+'"'+(page===p?' class="on"':'')+'>'+label+'</a>';};
  return '<div class="o-top"><a class="o-banner" href="'+href('learn')+'">'+t.banner+' <b>&rarr;</b></a>'+
    '<nav class="o-nav"><a class="o-logo" href="'+href('home')+'"><img src="'+D.base+'logo.png" alt="Ocho Music Group"></a>'+
    '<div class="o-links">'+L('about',t.nav_about)+L('albums',t.nav_albums)+L('placements',t.nav_placements)+
    '<a href="#o-faq" data-go="faq">'+t.nav_faq+'</a><a href="#o-contact" data-go="contact">'+t.nav_contact+'</a>'+
    '<a class="o-lang" href="'+href(page,lang==='en'?'es':'en')+'" title="'+t.lang_name+'">'+t.lang_label+'</a>'+
    '<a class="o-btn p" href="'+href('albums')+'">'+t.nav_cta+'</a></div>'+
    '<button class="o-burger" aria-label="Menu"><i></i><i></i><i></i></button></nav></div>';
}
function ticker(){return '<section class="o-ticker"><div class="o-ticker-k">'+t.heard+'</div><div class="o-mq">'+track(D.networks)+'</div></section>';}
function tape(){return '<section class="o-tape" aria-hidden="true"><div class="o-band a">'+track(D.genres)+'</div><div class="o-band b">'+track(D.genres.slice().reverse())+'</div></section>';}
function doors(){
  var steps=t.steps.map(function(x,i){return '<li><span class="o-step-n">0'+(i+1)+'</span><b>'+x[0]+'</b><span>'+x[1]+'</span></li>';}).join('');
  return '<section class="o-sec o-doors" id="o-license"><div class="o-wrap"><div class="o-one o-reveal"><div class="o-globe"></div>'+
  '<div class="o-one-head"><span class="o-eb">'+t.doors_eb+'</span><h2 class="o-h2">'+t.doors_h2+'</h2><p>'+t.doors_p+'</p>'+
  '<a class="o-btn p" href="#o-contact" data-go="contact">'+t.doors_cta+' &rarr;</a></div><ol class="o-steps">'+steps+'</ol></div></div></section>';
}
function faq(){
  var q=D.faq[lang].map(function(x,i){return '<div class="o-q'+(i===0?' on':'')+'"><button aria-expanded="'+(i===0)+'">'+esc(x[0])+'<i></i></button><div class="o-a"><div><p>'+esc(x[1])+'</p></div></div></div>';}).join('');
  return '<section class="o-sec o-faq" id="o-faq"><div class="o-wrap o-faq-grid"><div class="o-reveal"><span class="o-eb">'+t.faq_eb+'</span><h2 class="o-h2">'+t.faq_h2+'</h2></div><div class="o-reveal">'+q+'</div></div></section>';
}
function artists(){
  return '<section class="o-sec o-artists" id="o-artists"><div class="o-wrap o-agrid"><div class="o-reveal"><span class="o-eb" style="color:#ffd0e6">'+t.artists_eb+'</span><h2 class="o-h2" style="margin-bottom:26px">'+t.artists_h2+'</h2><p>'+t.artists_p+'</p>'+
  '<div class="o-ctas" style="justify-content:flex-start;margin-top:30px"><a class="o-btn p" href="#o-contact" data-go="contact">'+t.artists_cta+'</a></div></div>'+
  '<ul class="o-rules o-reveal" style="transition-delay:.15s">'+t.artists_rules.map(function(r){return '<li><span>'+r+'</span></li>';}).join('')+'</ul></div></section>';
}
function contact(){
  return '<section class="o-contact" id="o-contact"><div class="o-wrap o-cgrid"><div class="o-reveal"><span class="o-eb">'+t.contact_eb+'</span><h2 class="o-h2" style="margin-bottom:24px">'+t.contact_h2+'</h2><p>'+t.contact_p+'</p></div>'+
  '<div class="o-reveal" style="transition-delay:.15s"><a class="o-mail" href="#" data-mail>'+esc(D.email[0])+' [at] '+esc(D.email[1])+'</a></div></div>'+
  (D.preview?'<div class="o-wrap"><div class="o-stub">'+t.form_stub+'</div></div>':'')+'</section>';
}
function footer(){
  return '<footer class="o-foot"><div class="o-wrap"><div class="o-foot-grid"><a href="'+href('home')+'"><img src="'+D.base+'logo.png" alt="Ocho Music Group"></a>'+
  '<nav><a href="'+href('about')+'">'+t.nav_about+'</a><a href="'+href('albums')+'">'+t.nav_albums+'</a><a href="'+href('placements')+'">'+t.nav_placements+'</a><a href="'+href(page,lang==='en'?'es':'en')+'">'+t.lang_name+'</a></nav></div>'+
  '<small>&copy; '+new Date().getFullYear()+' Ocho Music Group LLC &middot; '+t.footer_tag+'</small></div></footer>';
}
function lightbox(){return '<div class="o-lb" role="dialog" aria-modal="true"><button class="o-lb-x" aria-label="Close">&times;</button><button class="o-lb-arrow o-lb-l" aria-label="Previous">&#8249;</button><button class="o-lb-arrow o-lb-r" aria-label="Next">&#8250;</button><div class="o-lb-box"></div></div>';}

/* ---------- data-driven blocks ---------- */
function coverflow(){return D.albums.map(function(a,i){return '<div class="o-fi" data-i="'+i+'"><img src="'+esc(src(a.img,'covers'))+'" alt="'+esc(a.title)+' album cover" loading="lazy"></div>';}).join('');}
function sounds(){
  return D.albumCats.map(function(c){var list=D.albums.filter(function(a){return a.cat===c;});if(!list.length)return '';
    return '<a class="o-sound" href="'+href('albums')+(D.preview?'?':'#')+'cat='+encodeURIComponent(c)+'" data-cat="'+esc(c)+'"><img src="'+esc(src(list[0].img,'covers',1))+'" alt="" loading="lazy"><div><b>'+esc(cat(c))+'</b><em>'+list.length+' '+t.albums_count+'</em></div></a>';}).join('');
}
function pcard(p,i){return '<figure class="o-card" data-i="'+i+'"><img src="'+esc(src(p.img,'posters'))+'" alt="'+esc(p.title)+' poster" loading="lazy"><figcaption><span>'+esc(cat(p.cat))+(p.net?' &middot; '+esc(p.net):'')+'</span><strong>'+esc(p.title)+'</strong></figcaption></figure>';}
function rail(){return D.placements.map(pcard).join('');}
function chips(cats,list){
  var h='<button class="o-chip on" data-cat="">'+t.all+' <sup>'+list.length+'</sup></button>';
  cats.forEach(function(c){var n=list.filter(function(x){return x.cat===c;}).length;if(n)h+='<button class="o-chip" data-cat="'+esc(c)+'">'+esc(cat(c))+' <sup>'+n+'</sup></button>';});
  list.forEach(function(x){if(cats.indexOf(x.cat)<0&&x.cat&&h.indexOf('data-cat="'+esc(x.cat)+'"')<0)h+='<button class="o-chip" data-cat="'+esc(x.cat)+'">'+esc(cat(x.cat))+'</button>';});
  return h;
}
function agrid(){return D.albums.map(function(a,i){return '<div class="o-al o-reveal" data-i="'+i+'" data-cat="'+esc(a.cat)+'" data-q="'+esc((a.title+' '+a.artist).toLowerCase())+'"><div class="o-al-in"><div class="o-vinyl"></div>'+(D.audio&&a.id?'<button class="o-al-play" data-play="'+esc(a.id)+'" aria-label="'+t.play+'">'+IC.play+'</button>':'')+'<img src="'+esc(src(a.img,'covers'))+'" alt="'+esc(a.title)+' album cover" loading="lazy"></div><div class="o-al-cap"><strong>'+esc(a.title)+'</strong><span>'+esc(a.artist)+'</span><em>'+esc(cat(a.cat))+'</em></div></div>';}).join('')+'<p class="o-empty o-hide">'+t.no_results+'</p>';}
function pgrid(){return D.placements.map(function(p,i){return pcard(p,i).replace('class="o-card"','class="o-card o-reveal" data-cat="'+esc(p.cat)+'"');}).join('');}

/* ---------- pages ---------- */
function learnPage(){
  var L=D.learn[lang],n=function(i){return i<9?'0'+(i+1):String(i+1);};
  var flow=function(items,cls){return '<div class="o-pipe o-reveal'+(cls||'')+'">'+items.map(function(x,i){return '<div class="o-node"><b>'+n(i)+'</b><span>'+x+'</span></div>';}).join('')+'</div>';};
  var cuts=L.cuts.map(function(c){return '<div class="o-cut"><span>'+c[0]+'</span><div class="o-bar"><i style="--w:'+c[1]+'%"></i></div><em>'+c[2]+'</em></div>';}).join('');
  var blank='';for(var b=0;b<24;b++)blank+='<i style="animation-delay:'+((b*7)%24*0.13).toFixed(2)+'s"></i>';
  var icos=['<div class="o-ico sync"><div class="f"></div><div class="w"></div></div>','<div class="o-ico needle"><div class="d"></div><div class="a"></div></div>','<div class="o-ico blanket">'+blank+'</div>'];
  var lics=L.lic.map(function(x,i){return '<div class="o-lic o-reveal" style="transition-delay:'+(i*.15)+'s">'+icos[i]+'<h3>'+x[0]+'</h3><p>'+x[1]+'</p></div>';}).join('');
  var why=L.why.map(function(x,i){return '<div class="o-reveal" style="transition-delay:'+(i*.12)+'s"><h3>'+x[0]+'</h3><p>'+x[1]+'</p></div>';}).join('');
  var ys=[30,80,130,180,230,280],paths='',dots='';
  ys.forEach(function(y,i){var d='M40 '+y+' C 160 '+y+', 170 155, 270 155';paths+='<path class="ln" d="'+d+'"/><path class="fl" stroke="url(#ogr)" style="animation-delay:'+(-i*.27)+'s" d="'+d+'"/>';dots+='<circle class="cmp" cx="28" cy="'+y+'" r="13"/>';});
  var outs='<path class="ln" d="M330 155 C 400 155, 410 70, 500 70"/><path class="fl" stroke="#22e1ff" d="M330 155 C 400 155, 410 70, 500 70"/>'+
    '<path class="ln" d="M330 155 C 400 155, 410 240, 500 240"/><path class="fl" stroke="#ff2e9a" d="M330 155 C 400 155, 410 240, 500 240"/>'+
    '<circle cx="508" cy="70" r="9" fill="#22e1ff"/><circle cx="508" cy="240" r="9" fill="#ff2e9a"/>'+
    '<text x="508" y="44" font-size="13" text-anchor="middle">'+L.terr[0][0].replace('&amp;','&#38;')+'</text><text x="508" y="276" font-size="13" text-anchor="middle">'+L.terr[1][0]+'</text>';
  var svg='<svg viewBox="0 0 580 310" role="img" aria-label="'+esc(L.c5_eb.replace(/&middot;/,''))+'"><defs><linearGradient id="ogr" x1="0" x2="1"><stop offset="0" stop-color="#ff2e9a"/><stop offset="1" stop-color="#ff8a1f"/></linearGradient></defs>'+
    paths+outs+dots+'<circle class="hub" cx="300" cy="155" r="44"/><image href="'+D.base+'logo.png" x="266" y="132" width="68" height="46"/></svg>';
  var terr=L.terr.map(function(x){return '<div><h3>'+x[0]+'</h3><p>'+x[1]+'</p></div>';}).join('');
  return '<header class="o-lhero"><div class="o-glow"></div><div class="o-wrap"><div><span class="o-eb o-up">'+L.eb+'</span><h1 class="o-up" style="animation-delay:.15s">'+L.h1+'</h1><p class="o-up" style="animation-delay:.3s">'+L.p+'</p>'+
    '<div class="o-scrollcue o-up" style="animation-delay:.45s"><i></i>'+L.scroll+'</div></div>'+
    '<div class="o-deck o-up" style="animation-delay:.3s" aria-hidden="true"><div class="o-disc"><b><img src="'+D.base+'logo.png" alt=""></b></div><div class="o-arm"><i></i></div></div></div></header>'+
  '<section class="o-sec o-chap"><div class="o-wrap"><div class="o-chap-grid"><div class="o-reveal"><span class="o-eb">'+L.c1_eb+'</span><h2 class="o-h2">'+L.c1_h+'</h2></div><p class="o-reveal">'+L.c1_p+'</p></div>'+
    flow(L.flow)+'<div class="o-why">'+why+'</div></div></section>'+
  '<section class="o-sec o-chap"><div class="o-wrap o-chap-grid"><div class="o-reveal"><span class="o-eb">'+L.c2_eb+'</span><h2 class="o-h2">'+L.c2_h+'</h2><p style="margin-top:26px">'+L.c2_p+'</p></div><div class="o-cuts o-reveal">'+cuts+'</div></div></section>'+
  '<section class="o-sec o-chap"><div class="o-wrap"><div class="o-chap-grid"><div class="o-reveal"><span class="o-eb">'+L.c3_eb+'</span><h2 class="o-h2">'+L.c3_h+'</h2></div><p class="o-reveal">'+L.c3_p+'</p></div><div class="o-lics">'+lics+'</div></div></section>'+
  '<section class="o-sec o-chap"><div class="o-wrap"><div class="o-chap-grid"><div class="o-reveal"><span class="o-eb">'+L.c4_eb+'</span><h2 class="o-h2">'+L.c4_h+'</h2></div><p class="o-reveal">'+L.c4_p+'</p></div>'+
    flow(L.roy,' money')+'<div class="o-note o-reveal">'+L.roy_note+'</div></div></section>'+
  '<section class="o-sec o-chap"><div class="o-wrap o-fit"><div class="o-reveal"><span class="o-eb">'+L.c5_eb+'</span><h2 class="o-h2">'+L.c5_h+'</h2><p style="margin-top:26px">'+L.c5_p+'</p></div>'+
    '<div class="o-reveal"><div class="o-funnel">'+svg+'</div><div class="o-terr">'+terr+'</div><div class="o-note" style="border-color:var(--cy);background:rgba(34,225,255,.06)">'+L.terr_note+'</div></div></div></section>'+
  '<section class="o-sec o-chap o-lcta"><div class="o-wrap o-reveal"><h2 class="o-h2">'+L.cta_h+'</h2><p>'+L.cta_p+'</p><div class="o-ctas"><a class="o-btn p" href="#o-contact" data-go="contact">'+L.cta_a+'</a><a class="o-btn c" href="'+href('albums')+'">'+L.cta_b+'</a></div></div></section>'+
  contact();
}
function home(){
  var lines=t.hero_lines.map(function(l,i){return '<span class="o-rl'+(i===0?' on':'')+'">'+l+'</span>';}).join('');
  var eq='';for(var i=0;i<14;i++)eq+='<i style="animation-delay:'+(-(i*137%1000)/1000).toFixed(2)+'s;animation-duration:'+(0.6+(i*53%50)/100).toFixed(2)+'s"></i>';
  var pills=t.pillars.map(function(p,i){return '<div class="o-pill o-reveal" style="transition-delay:'+(i*.1)+'s"><span class="o-pill-n">0'+(i+1)+'</span><h3>'+p[0]+'</h3><p>'+p[1]+'</p></div>';}).join('');
  var stats=t.stats.map(function(s){return '<div class="o-stat"><b>'+s[0]+'</b><span>'+s[1]+'</span></div>';}).join('');
  return '<header class="o-hero"><div class="o-wall" aria-hidden="true"></div><div class="o-shade"></div><div class="o-sunset"></div><div class="o-glow"></div>'+
  '<div class="o-hero-in"><div class="o-eq o-up" aria-hidden="true">'+eq+'</div>'+
  '<span class="o-eb o-up o-rot" style="margin-bottom:26px" aria-live="polite">'+lines+'</span>'+
  '<h1 class="o-up" style="animation-delay:.2s">'+t.hero_h1+'</h1>'+
  '<p class="o-sub o-up" style="animation-delay:.45s">'+t.hero_sub+'</p>'+
  '<div class="o-ctas o-up" style="animation-delay:.7s"><a class="o-btn p" href="#o-contact" data-go="contact">'+t.cta_license+'<small>'+t.cta_license_note+'</small></a><a class="o-btn c" href="'+href('albums')+'">'+t.cta_albums+'<small>'+t.cta_albums_note+'</small></a></div>'+
  '<p class="o-heard o-up" style="animation-delay:1s">'+t.heard+'&nbsp; <b>Apple TV+ &middot; NBC &middot; Telemundo &middot; Hulu &middot; Discovery &middot; UFC &middot; PlayStation</b></p></div></header>'+
  ticker()+
  '<section class="o-sec o-diff"><div class="o-wrap"><div class="o-diff-head o-reveal"><span class="o-eb">'+t.diff_eb+'</span><h2 class="o-h2">'+t.diff_h2+'</h2></div><div class="o-pillars">'+pills+'</div></div></section>'+
  '<section class="o-albums" id="o-albums"><div class="o-wrap o-center o-reveal"><span class="o-eb">'+t.albums_eb+'</span><h2 class="o-h2">'+t.albums_h2+'</h2><p>'+t.albums_p+'</p></div>'+
  '<div class="o-flow" data-block="flow"><button class="o-nav-btn o-prev" aria-label="Previous">&#8249;</button>'+coverflow()+'<button class="o-nav-btn o-next" aria-label="Next">&#8250;</button></div><div class="o-fcap" aria-live="polite"></div>'+
  '<div class="o-wrap"><div class="o-reveal" style="margin-top:40px"><span class="o-eb">'+t.sounds_eb+'</span></div><div class="o-sounds o-reveal" data-block="sounds" style="margin-top:0">'+sounds()+'</div>'+
  '<div class="o-more"><a class="o-btn p" href="'+href('albums')+'">'+t.albums_all+' &rarr;</a></div></div></section>'+
  tape()+
  '<section class="o-sec o-place"><div class="o-wrap o-reveal"><span class="o-eb">'+t.place_eb+'</span><h2 class="o-h2">'+t.place_h2+'</h2><p style="max-width:620px;margin-top:22px">'+t.place_p+'</p></div>'+
  '<div class="o-rail-wrap"><button class="o-nav-btn o-prev" aria-label="Previous">&#8249;</button><div class="o-rail" data-block="rail">'+rail()+'</div><button class="o-nav-btn o-next" aria-label="Next">&#8250;</button></div>'+
  '<div class="o-more" style="margin-top:10px"><a class="o-btn c" href="'+href('placements')+'">'+t.place_all+' &rarr;</a></div></section>'+
  doors()+
  '<section class="o-sec o-founders"><div class="o-wrap"><div class="o-reveal" style="max-width:900px"><span class="o-eb">'+t.founders_eb+'</span><h2 class="o-h2" style="font-size:clamp(44px,6vw,88px) !important">'+t.founders_h2+'</h2><p style="max-width:640px;margin-top:24px">'+t.founders_p+'</p></div>'+
  '<div class="o-fgrid"><a class="o-fcard o-reveal" href="'+href('about')+'"><figure>'+pimg('mike-1','Michael Lazarus')+'</figure><div class="o-fcard-in"><h3>'+t.mike_name+'</h3><div class="o-role">'+t.mike_role+'</div><p>'+t.mike_short+'</p></div></a>'+
  '<a class="o-fcard o-reveal" style="transition-delay:.12s" href="'+href('about')+'"><figure>'+pimg('jody-1','Jody Friedman')+'</figure><div class="o-fcard-in"><h3>'+t.jody_name+'</h3><div class="o-role">'+t.jody_role+'</div><p>'+t.jody_short+'</p></div></a></div>'+
  '<div class="o-stats o-reveal">'+stats+'</div><div class="o-more"><a class="o-btn c" href="'+href('about')+'">'+t.about_cta+' &rarr;</a></div></div></section>'+
  artists()+faq()+contact();
}
function person(key,photos,rev){
  var ph=photos.map(function(p){return '<figure>'+pimg(p[0],p[1])+'</figure>';}).join('');
  var nm=t[key+'_name'].split(' ');
  var creds=t[key+'_creds'].map(function(c){return '<div class="o-cred"><b>'+c[0]+'</b><span>'+c[1]+'</span></div>';}).join('');
  return '<section class="o-sec o-person'+(rev?' r':'')+'"><div class="o-wrap o-pgrid2"><div class="o-photos o-reveal">'+ph+'</div>'+
  '<div class="o-ptext o-reveal"><h2 class="o-bigname">'+esc(nm[0])+'<span>'+esc(nm.slice(1).join(' '))+'</span></h2><div class="o-role">'+t[key+'_role']+'</div><div class="o-creds'+(t[key+'_creds'].length>3?' n4':'')+'">'+creds+'</div>'+
  t[key+'_bio'].map(function(p){return '<p>'+p+'</p>';}).join('')+
  (t[key+'_stage']?'<h4 class="o-stage-h">'+t.stage_h+'</h4><ul class="o-stage">'+t[key+'_stage'].map(function(x){return '<li><b>'+x[0]+'</b><span>'+x[1]+'</span></li>';}).join('')+'</ul>':'')+'</div></div></section>';
}
function about(){
  var pol=[['jody-mike','Jody & Michael',{left:'4%',top:'6%',width:'64%',height:'58%',transform:'rotate(-5deg)',zIndex:3}],
           ['latin-grammys','Latin Grammy®',{right:'0',top:'0',width:'44%',height:'40%',transform:'rotate(6deg)',zIndex:2}],
           ['cubadisco-2024','Cubadisco 2024',{right:'6%',bottom:'2%',width:'34%',height:'52%',transform:'rotate(4deg)',zIndex:4}],
           ['jody-namm','NAMM 2025',{left:'0',bottom:'0',width:'52%',height:'40%',transform:'rotate(-3deg)',zIndex:5}]];
  var col=pol.map(function(p){var s='';for(var k in p[2])s+=k.replace(/[A-Z]/g,function(m){return '-'+m.toLowerCase();})+':'+p[2][k]+';';
    return '<figure class="o-pol" style="'+s+'">'+pimg(p[0],p[1])+'<figcaption>'+esc(p[1])+'</figcaption></figure>';}).join('');
  return '<header class="o-sec o-about-hero"><div class="o-glow"></div><div class="o-wrap o-about-grid"><div class="o-up"><span class="o-eb">'+t.about_eb+'</span><h1>'+t.about_h1+'</h1><p>'+t.about_story+'</p>'+
  '<p class="o-tagline">'+t.about_tag.replace(/\. /g,'.<span> / </span>')+'</p><div class="o-ctas" style="justify-content:flex-start"><a class="o-btn p" href="#o-contact" data-go="contact">'+t.cta_license+'<small>'+t.cta_license_note+'</small></a><a class="o-btn c" href="'+href('albums')+'">'+t.cta_albums+'<small>'+t.cta_albums_note+'</small></a></div></div>'+
  '<div class="o-collage o-up" style="animation-delay:.3s">'+col+'</div></div></header>'+
  ticker()+
  person('mike',[['mike-bass','Michael Lazarus on bass'],['latin-grammys','Latin Grammy awards'],['mike-4','Michael Lazarus']],false)+
  '<section class="o-sec o-panel"><div class="o-wrap"><div class="o-panel-card o-reveal"><figure><img src="'+photo('pmc-2024-panel')+'" alt="PMC 2024 panel" loading="lazy"></figure><div class="o-panel-in"><span class="o-eb">'+t.panel_eb+'</span><h3>'+t.panel_h+'</h3><div class="o-role">'+t.panel_k+'</div>'+t.panel_p.map(function(p){return '<p>'+p+'</p>';}).join('')+'</div></div></div></section>'+
  person('jody',[['jody-1','Jody Friedman'],['jody-gms-awards','Jody Friedman at the Guild of Music Supervisors Awards'],['jody-stage','Jody Friedman speaking']],true)+
  doors()+faq()+contact();
}
function albumsPage(){
  return '<header class="o-phero"><div class="o-glow"></div><div class="o-wrap"><span class="o-eb o-up">'+t.albums_page_eb+'</span><h1 class="o-up" style="animation-delay:.15s">'+t.albums_page_h1+'</h1><p class="o-up" style="animation-delay:.3s">'+t.albums_page_p+'</p>'+
  '<div class="o-count o-up" style="animation-delay:.45s"><b data-block="acount">'+D.albums.length+'</b><span>'+t.albums_count+'</span></div></div></header>'+
  '<section style="padding:0 0 90px"><div class="o-wrap"><div class="o-tools"><div class="o-chips" data-block="achips">'+chips(D.albumCats,D.albums)+'</div><input class="o-search" type="search" placeholder="'+t.search+'" aria-label="'+t.search+'"></div>'+
  '<div class="o-agrid2" data-block="agrid">'+agrid()+'</div></div></section>'+tape()+doors()+contact();
}
function placementsPage(){
  return '<header class="o-phero"><div class="o-glow"></div><div class="o-wrap"><span class="o-eb o-up">'+t.place_page_eb+'</span><h1 class="o-up" style="animation-delay:.15s">'+t.place_page_h1+'</h1><p class="o-up" style="animation-delay:.3s">'+t.place_page_p+'</p>'+
  '<div class="o-count o-up" style="animation-delay:.45s"><b data-block="pcount">'+D.placements.length+'</b><span>'+t.place_count+'</span></div></div></header>'+
  '<section style="padding:0 0 90px"><div class="o-wrap"><div class="o-tools"><div class="o-chips" data-block="pchips">'+chips(D.placeCats,D.placements)+'</div></div>'+
  '<div class="o-pgrid" data-block="pgrid">'+pgrid()+'</div></div></section>'+ticker()+doors()+contact();
}

/* ---------- streaming player ---------- */
var IC={play:'<svg viewBox="0 0 24 24"><path d="M7 4.5v15l13-7.5z"/></svg>',pause:'<svg viewBox="0 0 24 24"><path d="M6 4h4v16H6zM14 4h4v16h-4z"/></svg>',
  prev:'<svg viewBox="0 0 24 24"><path d="M6 5h2v14H6zM20 5v14L9 12z"/></svg>',next:'<svg viewBox="0 0 24 24"><path d="M16 5h2v14h-2zM4 5v14l11-7z"/></svg>'};
var ALB={},TRQ={},P={a:null,cur:null,peaks:[],bar:null};
function loadTracks(id){if(!id||!D.audio)return Promise.resolve(null);
  if(!TRQ[id])TRQ[id]=fetch(D.tracksBase+id+'.json').then(function(r){return r.ok?r.json():null;}).then(function(d){if(d)ALB[id]=d;return d;}).catch(function(){return null;});return TRQ[id];}
function fmt(s){s=Math.max(0,Math.round(s||0));return Math.floor(s/60)+':'+('0'+s%60).slice(-2);}
function drawWave(cv,peaks,prog){if(!cv||!peaks)return;var dpr=window.devicePixelRatio||1,w=cv.clientWidth,h=cv.clientHeight;if(!w||!h)return;
  if(cv.width!==Math.round(w*dpr)){cv.width=Math.round(w*dpr);cv.height=Math.round(h*dpr);}
  var c=cv.getContext('2d');c.setTransform(dpr,0,0,dpr,0,0);c.clearRect(0,0,w,h);var n=peaks.length,bw=w/n,g=c.createLinearGradient(0,0,w,0);
  g.addColorStop(0,'#ff2e9a');g.addColorStop(1,'#ff8a1f');
  for(var i=0;i<n;i++){var v=Math.max(6,peaks[i])/100*h*.94;c.fillStyle=(i+.5)/n<=prog?g:'rgba(255,255,255,.26)';c.fillRect(i*bw+bw*.18,(h-v)/2,Math.max(1,bw*.64),v);}}
function verAt(id,ti,vi){var d=ALB[id];return d&&d.tracks[ti]&&d.tracks[ti].v[vi];}
function isCur(id,ti,vi){return P.cur&&P.cur.id===id&&P.cur.t===ti&&P.cur.v===vi;}
function tlist(id,d){
  return d.tracks.map(function(tr,ti){var m=tr.v[0],more=tr.v.length-1;
    var row=function(v,vi,sub){return '<div class="o-tr'+(sub?' sub':'')+'" data-a="'+esc(id)+'" data-t="'+ti+'" data-v="'+vi+'"><button class="o-tp" aria-label="'+t.play+'">'+IC.play+'</button>'+
      '<div class="o-tn"><b>'+esc(sub?(v.l||tr.t):tr.t)+'</b>'+(!sub&&tr.desc?'<small title="'+esc(tr.desc)+'">'+esc(tr.desc)+'</small>':'')+'</div>'+
      '<canvas class="o-tw"></canvas><span class="o-tm">'+(!sub&&tr.bpm?esc(tr.bpm)+' BPM &middot; ':'')+fmt(v.d)+'</span>'+
      (!sub&&more?'<button class="o-tvb" aria-expanded="false">+'+more+' '+t.versions+'</button>':(!sub?'<span></span>':''))+'</div>';};
    return '<div class="o-tg">'+row(m,0,false)+(more?'<div class="o-vers" hidden>'+tr.v.slice(1).map(function(v,k){return row(v,k+1,true);}).join('')+'</div>':'')+'</div>';}).join('');
}
function drawRows(scope){requestAnimationFrame(function(){(scope||document).querySelectorAll('.o-tr').forEach(function(r){var id=r.getAttribute('data-a'),ti=+r.getAttribute('data-t'),vi=+r.getAttribute('data-v'),v=verAt(id,ti,vi);
  var on=isCur(id,ti,vi);r.classList.toggle('on',!!on);r.querySelector('.o-tp').innerHTML=on&&P.a&&!P.a.paused?IC.pause:IC.play;
  if(v)drawWave(r.querySelector('.o-tw'),v.p,on&&P.a&&P.a.duration?P.a.currentTime/P.a.duration:0);});});}
function bar(){
  if(P.bar)return P.bar;
  var b=document.createElement('div');b.id='ocho-player';b.className='o o-pbar';b.hidden=true;
  b.innerHTML='<img class="o-pb-cover" alt=""><div class="o-pb-meta"><strong></strong><span></span></div>'+
    '<div class="o-pb-ctl"><button data-pb="prev" aria-label="Previous">'+IC.prev+'</button><button data-pb="play" class="o-pb-play" aria-label="Play">'+IC.play+'</button><button data-pb="next" aria-label="Next">'+IC.next+'</button></div>'+
    '<div class="o-pb-wave"><span class="o-pb-t">0:00</span><canvas></canvas><span class="o-pb-d">0:00</span></div>'+
    '<input class="o-pb-vol" type="range" min="0" max="1" step="0.01" value="1" aria-label="Volume">'+
    '<a class="o-btn p o-pb-lic" href="#o-contact" data-pb="lic"></a><button data-pb="close" class="o-pb-x" aria-label="Close">&times;</button>';
  document.body.appendChild(b);
  var a=P.a=new Audio();a.preload='auto';
  a.addEventListener('timeupdate',tick);a.addEventListener('play',sync);a.addEventListener('pause',sync);a.addEventListener('loadedmetadata',tick);
  a.addEventListener('ended',function(){step(1);});
  b.addEventListener('click',function(e){var k=e.target.closest('[data-pb]');if(!k)return;k=k.getAttribute('data-pb');
    if(k==='play'){if(a.paused)a.play();else a.pause();}else if(k==='next')step(1);else if(k==='prev'){if(a.currentTime>3)a.currentTime=0;else step(-1);}
    else if(k==='lic'){e.preventDefault();goContact();}
    else if(k==='close'){a.pause();b.hidden=true;document.body.style.paddingBottom='';P.cur=null;drawRows(M);}});
  b.querySelector('.o-pb-vol').oninput=function(){a.volume=+this.value;};
  b.querySelector('canvas').addEventListener('click',function(e){var r=this.getBoundingClientRect();if(a.duration)a.currentTime=(e.clientX-r.left)/r.width*a.duration;});
  window.addEventListener('resize',function(){tick();});
  return P.bar=b;
}
function tick(){if(!P.bar||!P.a)return;var a=P.a,d=a.duration||(P.cur&&P.cur.d)||0,p=d?a.currentTime/d:0;
  P.bar.querySelector('.o-pb-t').textContent=fmt(a.currentTime);P.bar.querySelector('.o-pb-d').textContent=fmt(d);drawWave(P.bar.querySelector('canvas'),P.peaks,p);
  if(P.cur){var r=M.querySelector('.o-tr[data-a="'+P.cur.id+'"][data-t="'+P.cur.t+'"][data-v="'+P.cur.v+'"]');if(r)drawWave(r.querySelector('.o-tw'),P.peaks,p);}}
function sync(){if(!P.bar)return;P.bar.querySelector('.o-pb-play').innerHTML=P.a.paused?IC.play:IC.pause;drawRows(M);}
function play(id,ti,vi,seek){
  var v=verAt(id,ti,vi);if(!v)return;var b=bar(),a=P.a,al=D.albums.filter(function(x){return x.id===id;})[0]||{},tr=ALB[id].tracks[ti];
  if(isCur(id,ti,vi)){if(seek!=null&&a.duration){a.currentTime=seek*a.duration;if(a.paused)a.play();}else if(a.paused)a.play();else a.pause();return;}
  P.cur={id:id,t:ti,v:vi,d:v.d};P.peaks=v.p;a.src=D.audio+v.f;
  if(seek!=null)a.addEventListener('loadedmetadata',function f(){a.removeEventListener('loadedmetadata',f);a.currentTime=seek*a.duration;});
  a.play().catch(function(){});
  b.querySelector('.o-pb-cover').src=src(al.img,'covers',1);
  b.querySelector('.o-pb-meta strong').textContent=tr.t+(v.l?' ('+v.l+')':'');
  b.querySelector('.o-pb-meta span').textContent=(al.title||'')+(al.artist?' · '+al.artist:'');
  b.querySelector('.o-pb-lic').textContent=t.license;
  if(b.hidden){b.hidden=false;}document.body.style.paddingBottom=b.offsetHeight+'px';
  drawRows(M);tick();
}
function step(d){if(!P.cur)return;var n=ALB[P.cur.id].tracks.length,ti=(P.cur.t+d+n)%n;if(d>0&&P.cur.t+d>=n){P.a.pause();return;}play(P.cur.id,ti,0);}
function playAlbum(id){loadTracks(id).then(function(d){if(d&&d.tracks.length)play(id,0,0);});}
document.addEventListener('keydown',function(e){if(e.code!=='Space'||!P.cur||/INPUT|TEXTAREA|BUTTON|SELECT/.test(e.target.tagName))return;e.preventDefault();if(P.a.paused)P.a.play();else P.a.pause();});

/* ---------- behaviour ---------- */
function goContact(){
  var f=D.preview?null:document.querySelector('form[action*="/forms/"]');
  var el=f?(f.closest('section')||f):document.getElementById('o-contact');
  if(el){var y=el.getBoundingClientRect().top+window.pageYOffset-90;window.scrollTo({top:y,behavior:'smooth'});}
}
function goFaq(){var el=document.getElementById('o-faq');if(el){window.scrollTo({top:el.getBoundingClientRect().top+window.pageYOffset-80,behavior:'smooth'});}else{location.href=href('home')+(D.preview?'':'#o-faq');}}
function goArtists(){var el=document.getElementById('o-artists');if(el){window.scrollTo({top:el.getBoundingClientRect().top+window.pageYOffset-70,behavior:'smooth'});}else{location.href=href('home')+(D.preview?'':'#o-artists');}}
function every(fn,ms){timers.push(setInterval(fn,ms));}
function reveal(scope){
  var els=(scope||M).querySelectorAll('.o-reveal:not(.in)');
  if(!io&&'IntersectionObserver' in window)io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target);}});},{threshold:0,rootMargin:'0px 0px -6% 0px'});
  els.forEach(function(el){if(io)io.observe(el);else el.classList.add('in');});
}
var LB={list:null,i:0,kind:''};
function lbShow(){
  var lb=M.querySelector('.o-lb'),x=LB.list[LB.i],box=lb.querySelector('.o-lb-box');
  if(LB.kind==='album'){
    box.className='o-lb-box o-lb-album';
    box.innerHTML='<div class="o-la-side"><img src="'+esc(src(x.img,'covers'))+'" alt="'+esc(x.title)+'">'+
      '<div class="o-ctas"><a class="o-btn p" href="#o-contact" data-go="contact">'+t.license_album+'</a></div></div>'+
      '<div class="o-la-main"><span class="o-lb-k">'+esc(cat(x.cat))+'</span><h3>'+esc(x.title)+'</h3><p class="o-lb-a">'+esc(x.artist)+'</p><p class="o-la-desc"></p>'+
      '<div class="o-tl">'+(D.audio&&x.id?'<p class="o-tl-note">'+t.loading+'</p>':'')+'</div></div>';
    if(D.audio&&x.id)loadTracks(x.id).then(function(d){if(LB.list[LB.i]!==x||!lb.classList.contains('on'))return;var tl=box.querySelector('.o-tl');
      if(!d||!d.tracks.length){tl.innerHTML='<p class="o-tl-note">'+t.no_audio+'</p>';return;}
      box.querySelector('.o-la-desc').textContent=d.desc||'';tl.innerHTML=tlist(x.id,d);drawRows(tl);});
  }else{
    box.className='o-lb-box';
    box.innerHTML='<img src="'+esc(src(x.img,'posters'))+'" alt="'+esc(x.title)+'"><div><span class="o-lb-k">'+esc(cat(x.cat))+'</span><h3>'+esc(x.title)+'</h3><p class="o-lb-a">'+esc(x.net)+'</p>'+
      '<div class="o-ctas"><a class="o-btn p" href="#o-contact" data-go="contact">'+t.license_world+'</a><a class="o-btn c" href="'+href('albums')+'">'+t.cta_albums+'</a></div></div>';
  }
  lb.classList.add('on');document.documentElement.style.overflow='hidden';
}
function lbOpen(list,i,kind){LB.list=list;LB.i=i;LB.kind=kind;lbShow();}
function lbClose(){var lb=M.querySelector('.o-lb');if(lb)lb.classList.remove('on');document.documentElement.style.overflow='';}

var flowI=0;
function flowSet(i){
  var fl=M.querySelector('.o-flow');if(!fl)return;var items=fl.querySelectorAll('.o-fi'),n=items.length;if(!n)return;
  flowI=(i+n)%n;var sm=window.innerWidth<640,b0=sm?150:300,st=sm?46:130;
  items.forEach(function(el,k){var d=k-flowI;if(d>n/2)d-=n;if(d<-n/2)d+=n;var a=Math.abs(d);
    el.style.transform='translateX('+(d===0?0:(d>0?1:-1)*(b0+(a-1)*st))+'px) translateZ('+(-a*140)+'px) rotateY('+(d===0?0:(d>0?-42:42))+'deg) scale('+(d===0?1.08:1)+')';
    el.style.opacity=a>4?0:1;el.style.zIndex=100-a;el.style.filter=d===0?'none':'brightness('+(1-a*.15)+')';el.classList.toggle('on',d===0);});
  var a=D.albums[flowI],cap=M.querySelector('.o-fcap');if(cap&&a)cap.innerHTML='<strong>'+esc(a.title)+'</strong><span>'+esc(a.artist)+' &middot; '+esc(cat(a.cat))+'</span>'+(D.audio&&a.id?'<button class="o-btn p o-fplay" data-play="'+esc(a.id)+'">'+IC.play+' '+t.play+'</button>':'');
}
var fx0=null,fMoved=false,fPaused=false;
function bindFlow(){
  var fl=M.querySelector('.o-flow');if(!fl)return;fPaused=false;
  fl.querySelector('.o-prev').onclick=function(e){e.stopPropagation();flowSet(flowI-1);};
  fl.querySelector('.o-next').onclick=function(e){e.stopPropagation();flowSet(flowI+1);};
  fl.onclick=function(e){if(fMoved)return;var it=e.target.closest('.o-fi');if(!it)return;var i=+it.getAttribute('data-i');if(i===flowI)lbOpen(D.albums,i,'album');else flowSet(i);};
  fl.onpointerdown=function(e){fx0=e.clientX;fMoved=false;fPaused=true;};
  fl.onmouseenter=function(){fPaused=true;};fl.onmouseleave=function(){fPaused=false;};
  flowSet(flowI);
  if(!reduce)every(function(){if(!fPaused&&!document.hidden)flowSet(flowI+1);},3200);
}
window.addEventListener('pointerup',function(e){if(fx0==null)return;var dx=e.clientX-fx0;fx0=null;if(Math.abs(dx)>40){fMoved=true;flowSet(flowI+(dx<0?1:-1)*Math.max(1,Math.round(Math.abs(dx)/160)));setTimeout(function(){fMoved=false;},50);}});
function bindRail(){
  M.querySelectorAll('.o-rail-wrap').forEach(function(w){var tr=w.querySelector('.o-rail'),paused=false;
    function step(){var c=tr.querySelector('.o-card');return c?(c.offsetWidth+22)*2:480;}
    function next(){if(tr.scrollLeft+tr.clientWidth>=tr.scrollWidth-10)tr.scrollTo({left:0});else tr.scrollBy({left:step()});}
    w.querySelector('.o-next').onclick=next;w.querySelector('.o-prev').onclick=function(){if(tr.scrollLeft<=5)tr.scrollTo({left:tr.scrollWidth});else tr.scrollBy({left:-step()});};
    w.onmouseenter=function(){paused=true;};w.onmouseleave=function(){paused=false;};w.ontouchstart=function(){paused=true;};
    if(!reduce)every(function(){if(!paused&&!document.hidden)next();},3400);});
}
function bindFilter(gridSel,chipSel,searchSel){
  var grid=M.querySelector(gridSel);if(!grid)return;var cur='',q='';
  function apply(){var shown=0;grid.querySelectorAll('[data-i]').forEach(function(el){var ok=(!cur||el.getAttribute('data-cat')===cur)&&(!q||(el.getAttribute('data-q')||'').indexOf(q)>=0);el.classList.toggle('o-hide',!ok);if(ok){shown++;el.classList.add('in');}});
    var em=grid.querySelector('.o-empty');if(em)em.classList.toggle('o-hide',shown>0);}
  var ch=M.querySelector(chipSel);
  ch.onclick=function(e){var b=e.target.closest('.o-chip');if(!b)return;cur=b.getAttribute('data-cat');ch.querySelectorAll('.o-chip').forEach(function(x){x.classList.toggle('on',x===b);});apply();};
  var s=searchSel&&M.querySelector(searchSel);if(s)s.oninput=function(){q=s.value.trim().toLowerCase();apply();};
  var m=(D.preview?location.hash:location.search+location.hash).match(/cat=([^&]+)/);
  if(m){var c=decodeURIComponent(m[1]);var b=[].filter.call(ch.querySelectorAll('.o-chip'),function(x){return x.getAttribute('data-cat')===c;})[0];if(b)b.click();}
}
function bindTilt(){
  if(reduce||window.matchMedia('(hover: none)').matches)return;
  M.querySelectorAll('.o-al').forEach(function(el){var inn=el.querySelector('.o-al-in');
    el.onmousemove=function(e){var r=el.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.width-.5;inn.style.transform='rotateY('+(x*16)+'deg) rotateX('+(-y*16)+'deg)';};
    el.onmouseleave=function(){inn.style.transform='';};});
}
function bindData(){
  bindFlow();bindRail();bindTilt();
  if(page==='albums')bindFilter('[data-block="agrid"]','[data-block="achips"]','.o-search');
  if(page==='placements')bindFilter('[data-block="pgrid"]','[data-block="pchips"]');
}
function wall(){
  var w=M.querySelector('.o-wall');if(!w)return;var imgs=D.albums.map(function(a){return src(a.img,'covers',1);}).concat(D.placements.map(function(p){return src(p.img,'posters',1);}));
  imgs=imgs.filter(Boolean);var h='';
  for(var r=0;r<4;r++){var s=r*7+3,a=imgs.slice();for(var i=a.length-1;i>0;i--){s=(s*9301+49297)%233280;var j=Math.floor(s/233280*(i+1));var tmp=a[i];a[i]=a[j];a[j]=tmp;}
    a=a.slice(0,12);var row='';for(var k=0;k<2;k++)a.forEach(function(u){row+='<img src="'+esc(u)+'" alt="">';});
    h+='<div class="o-wall-row'+(r%2?' rev':'')+'" style="animation-duration:'+(100+r*22)+'s">'+row+'</div>';}
  w.innerHTML=h;
}
function placeFoot(){
  var kf=document.querySelector('form[action*="/forms/"]'),ks=kf&&kf.closest('[id^="section-"]'),ft=M.querySelector('.o-foot');
  if(!ks||!ft)return;var w=document.createElement('div');w.id='ocho-foot';w.className='o';w.appendChild(ft);ks.parentNode.insertBefore(w,ks.nextSibling);
}
function render(){
  timers.forEach(clearInterval);timers=[];lbClose();
  route();document.documentElement.lang=lang;
  var body=page==='learn'?learnPage():page==='about'?about():page==='albums'?albumsPage():page==='placements'?placementsPage():home();
  M.innerHTML='<div class="o" id="ocho"><div class="o-grain"></div>'+nav()+body+footer()+lightbox()+'</div>';
  wall();reveal();bindData();
  if(!D.preview&&/^#o-(artists|faq)$/.test(location.hash))setTimeout(function(){var el=document.getElementById(location.hash.slice(1));if(el)window.scrollTo(0,el.getBoundingClientRect().top+window.pageYOffset-70);},300);
  var rl=M.querySelectorAll('.o-rl');
  if(rl.length>1&&!reduce){var ri=0;every(function(){rl[ri].classList.remove('on');ri=(ri+1)%rl.length;rl[ri].classList.add('on');},3400);}
  M.querySelectorAll('[data-mail]').forEach(function(a){a.href='mailto:'+mail();a.textContent=mail();});
  // live pages: the Kajabi contact form section follows the code block, so move the footer below it
  var old=document.getElementById('ocho-foot');if(old)old.remove();
  if(!D.preview){if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',placeFoot);else placeFoot();}
}

function handleTrack(e){var tvb=e.target.closest('.o-tvb');if(tvb){var vs=tvb.closest('.o-tg').querySelector('.o-vers');vs.hidden=!vs.hidden;tvb.setAttribute('aria-expanded',!vs.hidden);if(!vs.hidden)drawRows(vs);return;}
  var tw=e.target.closest('.o-tw'),trow=e.target.closest('.o-tr'),r=tw?tw.getBoundingClientRect():null;play(trow.getAttribute('data-a'),+trow.getAttribute('data-t'),+trow.getAttribute('data-v'),r?(e.clientX-r.left)/r.width:null);}
/* global listeners (bound once) */
M.addEventListener('click',function(e){
  var g=e.target.closest('[data-go]');
  if(g){e.preventDefault();var top=M.querySelector('.o-top');if(top)top.classList.remove('open');lbClose();var gg=g.getAttribute('data-go');if(gg==='contact')goContact();else if(gg==='artists')goArtists();else goFaq();return;}
  if(e.target.closest('.o-burger')){M.querySelector('.o-top').classList.toggle('open');return;}
  if(e.target.closest('.o-links a')){M.querySelector('.o-top').classList.remove('open');}
  var q=e.target.closest('.o-q button');
  if(q){var it=q.parentNode,on=!it.classList.contains('on');it.classList.toggle('on',on);q.setAttribute('aria-expanded',on);return;}
  if(e.target.closest('.o-lb .o-tr,.o-lb .o-tvb')){handleTrack(e);return;}
  var lb=e.target.closest('.o-lb');
  if(lb){if(e.target.closest('.o-lb-x')||e.target===lb){lbClose();return;}
    if(e.target.closest('.o-lb-l')){LB.i=(LB.i-1+LB.list.length)%LB.list.length;lbShow();return;}
    if(e.target.closest('.o-lb-r')){LB.i=(LB.i+1)%LB.list.length;lbShow();return;}return;}
  var tvb=e.target.closest('.o-tvb');if(tvb){var vs=tvb.closest('.o-tg').querySelector('.o-vers');vs.hidden=!vs.hidden;tvb.setAttribute('aria-expanded',!vs.hidden);if(!vs.hidden)drawRows(vs);return;}
  var tw=e.target.closest('.o-tw');var trow=e.target.closest('.o-tr');
  if(trow){var r=tw?tw.getBoundingClientRect():null;play(trow.getAttribute('data-a'),+trow.getAttribute('data-t'),+trow.getAttribute('data-v'),r?(e.clientX-r.left)/r.width:null);return;}
  var pa=e.target.closest('[data-play]');if(pa){e.preventDefault();playAlbum(pa.getAttribute('data-play'));return;}
  var al=e.target.closest('.o-al');if(al){lbOpen(D.albums,+al.getAttribute('data-i'),'album');return;}
  var pc=e.target.closest('.o-card');if(pc){lbOpen(D.placements,+pc.getAttribute('data-i'),'place');return;}
});
document.addEventListener('keydown',function(e){var lb=M.querySelector('.o-lb.on');if(!lb)return;
  if(e.key==='Escape')lbClose();else if(e.key==='ArrowRight'){LB.i=(LB.i+1)%LB.list.length;lbShow();}else if(e.key==='ArrowLeft'){LB.i=(LB.i-1+LB.list.length)%LB.list.length;lbShow();}});
window.addEventListener('scroll',function(){var top=M.querySelector('.o-top');if(top)top.classList.toggle('solid',window.pageYOffset>40);},{passive:true});
window.addEventListener('resize',function(){flowSet(flowI);});
if(D.preview)window.addEventListener('hashchange',function(){render();window.scrollTo(0,0);});
// images that fail on the primary host retry from the fallback host
if(D.fallback)M.addEventListener('error',function(ev){var im=ev.target;if(im.tagName!=='IMG'||im.dataset.fb||im.src.indexOf(D.base)!==0)return;im.dataset.fb='1';im.src=D.fallback+im.src.slice(D.base.length);},true);
// the primary CDN can stall on a cold file without erroring: swap images that sit unloaded near the viewport for 6s
if(D.fallback)setInterval(function(){var now=Date.now(),vh=window.innerHeight;document.querySelectorAll('#ocho img, #ocho-player img').forEach(function(im){
  if(im.complete||im.dataset.fb||im.src.indexOf(D.base)!==0)return;var r=im.getBoundingClientRect();if(r.bottom<-vh||r.top>2*vh){delete im.dataset.wt;return;}
  if(!im.dataset.wt){im.dataset.wt=now;return;}if(now-im.dataset.wt>6000){im.dataset.fb='1';im.src=D.fallback+im.src.slice(D.base.length);}});},2000);

render();

// ---- live albums & placements from the Google Sheet (gviz JSONP, no API key) ----
function applySheet(rows){
  var pick=function(n){return rows.filter(function(r){return String(r.Section||'').trim().toLowerCase()===n;});};
  var ord=function(a,b){var x=parseFloat(a.Order),y=parseFloat(b.Order);return (isNaN(x)?1e9:x)-(isNaN(y)?1e9:y);};
  var A=pick('album').filter(function(r){return r.Title&&r.Image;}).sort(ord),P=pick('placement').filter(function(r){return r.Title&&r.Image;}).sort(ord);
  var changed=false;
  var nt=function(x){return String(x||'').toLowerCase().normalize('NFD').replace(/[^a-z0-9]/g,'');},ids={};D.albums.forEach(function(a){ids[nt(a.title)]=a.id;});
  if(A.length){D.albums=A.map(function(r){return {id:String(r.ID||'').trim()||ids[nt(r.Title)]||'',title:String(r.Title).trim(),artist:String(r['Artist / Network']||'').trim(),cat:String(r.Category||'').trim(),img:String(r.Image).trim()};});changed=true;}
  if(P.length){D.placements=P.map(function(r){return {title:String(r.Title).trim(),net:String(r['Artist / Network']||'').trim(),cat:String(r.Category||'').trim(),img:String(r.Image).trim()};});changed=true;}
  if(!changed)return;
  var set=function(sel,h){var el=M.querySelector('[data-block="'+sel+'"]');if(el)el.innerHTML=h;return el;};
  timers.forEach(clearInterval);timers=[];
  var fl=M.querySelector('.o-flow');if(fl){fl.querySelectorAll('.o-fi').forEach(function(x){x.remove();});fl.querySelector('.o-next').insertAdjacentHTML('beforebegin',coverflow());}
  set('sounds',sounds());set('rail',rail());set('achips',chips(D.albumCats,D.albums));set('agrid',agrid());set('pchips',chips(D.placeCats,D.placements));set('pgrid',pgrid());
  set('acount',D.albums.length);set('pcount',D.placements.length);
  wall();reveal();
  bindData();
  var rl=M.querySelectorAll('.o-rl');if(rl.length>1&&!reduce){var ri=0;rl.forEach(function(x,i){if(x.classList.contains('on'))ri=i;});every(function(){rl[ri].classList.remove('on');ri=(ri+1)%rl.length;rl[ri].classList.add('on');},3400);}
}
if(D.sheet){
  var cb='__ochoSheet'+Date.now();
  window[cb]=function(resp){try{if(!resp||resp.status!=='ok')return;var cols=resp.table.cols.map(function(c){return c.label;});
    var rows=resp.table.rows.map(function(row){var o={};row.c.forEach(function(cell,i){o[cols[i]]=cell?(cell.f!=null?cell.f:cell.v):'';});return o;});
    applySheet(rows);}catch(e){}finally{delete window[cb];}};
  var sc=document.createElement('script');sc.src='https://docs.google.com/spreadsheets/d/'+D.sheet+'/gviz/tq?headers=1&tqx=out:json;responseHandler:'+cb;
  sc.onerror=function(){delete window[cb];};document.head.appendChild(sc);
}
})();
"""


def bundle(base, fallback, preview, audio="", tracks=""):
    d = json.dumps(site_data(base, fallback, preview, audio, tracks), ensure_ascii=False)
    return JS.replace("__DATA__", d).replace("__CSS__", json.dumps(_min(CSS)))


def main():
    (HERE / "ocho.js").write_text(bundle(CDN_BASE, FALLBACK_BASE, False, AUDIO_BASE, TRACKS_BASE))
    (HERE / "preview.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Ocho Music Group</title></head><body style="margin:0;background:#07050a">'
        '<div id="ocho-mount"></div><script>' + bundle("img/", "", True, "audio/", "tracks/") + "</script></body></html>")
    print(f"ocho.js: {(HERE / 'ocho.js').stat().st_size:,} bytes (CDN ref: {CDN_REF}); sheet: {SHEET_ID or 'none'}")


if __name__ == "__main__":
    main()
