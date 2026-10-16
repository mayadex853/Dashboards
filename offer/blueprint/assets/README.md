# Blueprint offer page assets

Drop these files here using the exact filenames. Missing files show a labeled frame instead of a broken image.

| File | Used in | Status |
|---|---|---|
| `AA Logo copy.jpg` | Nav mark | Safe as-is |
| `Drifting Final.png` | "The room you're in" strip | Safe as-is |
| `Stalling.png` | "The room you're in" strip | Safe as-is |
| `Renovating.png` | "The room you're in" strip | Safe as-is |
| `Rebuilding.png` | "The room you're in" strip | Safe as-is |

## Deliberately NOT used

- `Blueprint.png`: has "128 lessons" baked in. Wrong for this tier (27 / 78 / 105). Needs a regenerated version.
- `Activated Architects*.png`: retired wordmark baked in. Replaced by `Architects Wide.jpg`.
- `Foundation.png`: not needed on this page.

## Added

- `Architects Wide.jpg`: Architects community banner (current "ARCHITECTS" wordmark). Used in the Architects section.
- `Wreck the Room Logo.webp`: primary logo (hammer + wordmark). Used in the nav, hero and final call to action. Replaces `AA Logo copy.jpg` on this page.
- `blueprint-paper.jpg`: seamless cyanotype paper texture (generated, 1600px, tiles at 800px). To use an Adobe Stock texture instead, export a seamless/tileable blueprint paper image and save it over this file with the same name. No code changes needed.
- `room-see.webp`, `room-wreck.webp`, `room-rebuild.webp`: framework section "Same room. Three stages." strip. AI-generated (ElevenLabs, gpt-image-2), background keyed out so the page's blueprint paper shows through.
- `og-share.jpg`: 1200x630 social share image (source: `og-share.source.html`, rendered with Chromium).
