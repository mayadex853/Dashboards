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

## Installing on Kajabi

1. On the homepage, keep the header, footer and the **Two-Step Opt-in** pop-up (the booking form) as they are.
2. Remove the existing body sections and add one **Custom Code** section with the snippet above.
3. Publish. Changes merged to `main` go live within about 10 minutes with no further Kajabi edits.

## How the CTAs work

- **Quiz:** every quiz button links to `https://quiz.wrecktheroom.com`, the same link as today.
- **Booking form:** the page moves Kajabi's own booking form out of the pop-up and into the booking section. It submits exactly as before (same form, fields, security token and validation) and only the styling and the button label change. Any other "Book Jody to speak" button on the page, including the one in the header, scrolls to that section. If Kajabi ever changes the pop-up and the form can't be found, the section shows a button that opens the pop-up instead.

## Editing

The sources are in `src/` (`wtr.html` for copy, `wtr.css` for styles and `wtr.js` for behavior). After editing, run:

```bash
python3 build.py   # writes preview.html, kajabi-embed.html, wtr.js
```

Images are served from the site's existing Kajabi uploads. Testimonial videos play from the same Vimeo and Wistia IDs the current page uses.
