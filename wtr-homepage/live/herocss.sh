# phone: keep each hero headline phrase on one line
grep -q "hero-1line" src/wtr.css || printf '\n/* hero-1line */\n@media (max-width:760px){.wtr .w-hero h1,.wtr[data-dir="brick"] .w-hero h1{white-space:nowrap;font-size:clamp(32px,11vw,52px);}.w-hero .w-eb{letter-spacing:.16em;}}\n' >> src/wtr.css
