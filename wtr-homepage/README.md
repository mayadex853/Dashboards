# Wreck the Room homepage

Custom homepage for wrecktheroom.com, embedded in Kajabi as a single Code block (same setup as `hdmn-homepage`).

```html
<div id="wtr-mount" data-dir="brick"></div>
<script src="https://mayadex853.github.io/Dashboards/wtr-homepage/wtr.js"></script>
```

- `data-dir="brick"` is **Direction B, Demolition** (condensed caps, gold on black with Wreck the Room red as the accent). This is the chosen design.
- `data-dir="noir"` is **Direction A, Gold Noir** (serif display type, gold on black), kept as an alternative.

`preview.html` shows the page with a stand-in Kajabi header. Use the switch in the bottom-left corner to flip between the two directions (it opens on B; add `#a` to the URL to open on A).

## Logo

`img/wtr-logo.png` is the Wreck the Room logo cut out onto a transparent background (for dark backgrounds). The preview has a **Logo** switch to compare it with the JF logo in the header. The live header logo is set in Kajabi (Header settings → Logo); upload this file there to use it.

`img/badge-1.png`, `img/badge-2.png` and `img/badge-3.png` are circular sledgehammer badges (one per hammer artwork, 512×512, transparent corners) that stay readable at header size. `img/badge-2-nogold.png` is Badge 2 without the gold ring (thin red edge only) and `img/hammer-mark.png` is the hammer on its own with no circle. The preview's Logo switch compares Badge 2, the no-gold version and the hammer-only mark.

## Installing on Kajabi

1. On the homepage, keep the header, footer and the **Two-Step Opt-in** pop-up (the booking form) as they are.
2. Remove the existing body sections and add one **Custom Code** section with the snippet above.
3. Publish. Changes merged to `main` go live within about 10 minutes with no further Kajabi edits.

## Live status and rollback

The redesign is live as the homepage (Kajabi landing page `home`, theme 2163962849), in a section called `wtr_home` that holds one Custom Code block. The old sections are still saved in the theme, just not shown. To roll back, set the theme's `content_for_index` to the list in `data/old-homepage-layout.json`.

## How the CTAs work

- **Quiz:** every quiz button links to `https://quiz.wrecktheroom.com`, the same link as today.
- **Booking form:** the page moves Kajabi's own booking form out of the pop-up and into the booking section. It submits exactly as before (same form, fields, security token and validation) and only the styling and the button label change. Any other "Book Jody to speak" button on the page, including the one in the header, scrolls to that section. If Kajabi ever changes the pop-up and the form can't be found, the section shows a button that opens the pop-up instead.

## Editing

The sources are in `src/` (`wtr.html` for copy, `wtr.css` for styles and `wtr.js` for behavior). After editing, run:

```bash
python3 build.py   # writes preview.html, kajabi-embed.html, wtr.js
```

Images are served from the site's existing Kajabi uploads. Testimonial videos play from the same Vimeo and Wistia IDs the current page uses.

## Credits page (wrecktheroom.com/credits)

`build_credits.py` builds the credits page from the same Google Sheet that feeds hdmusicnow.com ("HD Music Now – Website Credits"), so editing the sheet updates both sites. The page reads the sheet live; `data/credits.json` is a snapshot that renders instantly and is used if the sheet can't be reached.

- **Projects** (Section `Project`) are Jody's own credits. Any credit whose role mentions "Producer" (Ethan Bloom) leads the grid with a Producer tag, and the featured Ethan Bloom section sits above it.
- **Placements** (Section `Placement`) are shown as music placed through HD Music Now, with the poster marquee and category tabs.
- Posters come from `hdmn-homepage/posters/` on GitHub Pages.

```bash
python3 build_credits.py            # refresh the snapshot from the sheet and rebuild
python3 build_credits.py --offline  # rebuild from the saved snapshot
```

The Kajabi page is a landing page with the slug `credits`, holding one Custom Code block:

```html
<div id="wtr-credits-mount"></div>
<script src="https://mayadex853.github.io/Dashboards/wtr-homepage/credits.js"></script>
```

## Guided Transformation pages (Drifting, Stalling, Renovating, Rebuilding)

`build_programs.py` builds one offer page per $997 program from a single script; the Code block picks the program with `data-v` (`drifting`, `stalling`, `renovating` or `rebuilding`):

```html
<div id="wtr-prog-mount" data-v="drifting"></div>
<script src="https://mayadex853.github.io/Dashboards/wtr-homepage/programs.js"></script>
```

- Each page's buttons go to that program's Kajabi checkout. Copy comes from the offer descriptions; the client stories are the same videos as the homepage.
- Adding `?bonus=1` to the page URL shows the quiz-bonus banner (a private 30-minute call with Jody at week 3 for joining within 5 days). The quiz follow-up emails link with it; without it the banner is hidden.
- `programs-preview.html?v=stalling&bonus=1` previews any version.
- Live at `wrecktheroom.com/{drifting,stalling,renovating,rebuilding}-program`. Those Kajabi pages load the script from jsDelivr pinned to a commit (`https://cdn.jsdelivr.net/gh/mayadex853/Dashboards@<commit>/wtr-homepage/programs.js`), so they work before this branch reaches `main`. After a rebuild, update the commit in all four Code blocks.

```bash
python3 build_programs.py   # writes programs-preview.html, programs.js
```
