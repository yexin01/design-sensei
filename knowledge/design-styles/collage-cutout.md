---
title: "Collage and cutout"
kind: design-style
summary: "Layered paper cutouts, torn edges, tape, stickers and mixed-media fragments arranged like a zine page or mood board. Covers layer discipline, cut-edge and shadow techniques in CSS, ink and flat-colour contrast numbers, reading order, image weight and the cases where the style should stay out."
source_ids: []
pattern_ids: [style-collage-cutout]
updated: "2026-10-09"
---

# Collage and cutout

Collage design behaves like a tabletop scene: photographs and shapes are cut out, overlapped and glued to a paper ground, with tape, stickers, stamps, scribbles and scraps of print around them. The charm is the physicality of layers and the unexpected pairings of images and type. It is expressive and editorial, closer to a zine, a gig poster or a mood board than to a product interface. It needs a skeleton: a hidden grid, a clean surface for every block of reading text, and a strict limit on how many pieces compete at once. This note is fully original; the local sources contain no collage implementation.

## Visual characteristics
- Subjects cut from their backgrounds with slightly rough, irregular or scissor-straight edges, sometimes with a thin white sticker outline.
- Paper grounds (cream, newsprint, kraft) with flat blocks of hot colour; torn strips, scalloped shapes, circles and stars as accent pieces.
- Overlap and rotation of 1-6 degrees; tape strips, staples, pins and paper clips holding elements down.
- Tight, hard, low-offset shadows (2-4 px) that suggest paper thickness, not soft glows.
- Mixed media: halftone photos, scanned textures, hand marks, cut-out letters and stamped or typewritten labels.
- Unexpected scale jumps: a giant hand beside a tiny building; surreal juxtapositions with a clear subject.

## When it fits, when it does not
- Fits: music, art, fashion and culture brands, festivals and exhibitions, zines and independent publishing, creative-agency portfolios, campaign microsites, youth and community brands, editorial features and campaign hero sections.
- Poor fit: checkout and account flows, dashboards, documentation, medical or legal content, any product that sells on reliability and calm.
- Supporting influences that work: grain-and-texture, retro-vintage, editorial, maximalism, neo-brutalism, hand-drawn-doodle, y2k for a glossy variant. Avoid minimalism, swiss-international-typographic, dark-technical-developer-tools and glassmorphism.

## Typography
- Control the chaos with roles: one condensed or heavy display face for headlines (Anton, Bebas Neue, Archivo Black), one expressive serif italic or stencil for accents, one mono for labels and captions (Space Mono, IBM Plex Mono), and a plain text face for paragraphs.
- Display 56-140 px, tracking -0.01 to 0em; mono labels 12-14 px uppercase at +0.06em.
- Ransom-note headlines, where each letter has a different font, size and background patch, are decoration. Keep the heading as one real element with each letter in an `aria-hidden` span and the whole phrase in an `aria-label`, otherwise some screen readers announce it letter by letter.
- Body text sits on a solid paper panel at 16-18 px, weight 400, never directly over a busy cutout.

## Colour
- Paper and ink: ink #111111 on paper #F3EDE0 is 16.19:1; on newsprint #E4D9BD it is 13.45:1.
- Hot flats: ink on yellow #FFD60A is 13.38:1, on pink #FF7AB6 7.83:1, on mint #7DD3C0 10.75:1. White on cobalt #2B3FD6 is 7.54:1, but ink on cobalt is 2.50:1 and fails.
- Tomato #E63946 is borderline: ink on it is 4.53:1, white 4.17:1 (fails for small text) and paper-coloured text 3.57:1. Use deep red #C1121F with white (6.22:1) when text sits on red, or keep red for shapes.
- Coloured text on paper: deep red 5.34:1, cobalt 6.46:1, tomato only 3.57:1 and yellow 1.21:1, so yellow is for fills only.
- Limit the flats to two or three hues plus ink and paper. Let photography be black and white or duotoned so it unifies with the flats. Muddy tinted overlays across everything reduce the contrast of text laid over them.

## Composition and layout
- Build on a grid and break it in measured ways: 12 columns, pieces overlapping neighbouring cells, text always in a defined column. Keep the key message and the primary action on a clean block, not on the collage.
- Layers: a ground, a few large cutouts, small accents on top. Five to seven pieces in view is plenty; more reads as noise and costs rendering time.
- Overlap with CSS Grid (several children placed in the same cell with `z-index`) instead of absolute positioning, so the DOM stays in logical reading order while the visual order is free.
- Responsive: on phones reduce rotation to 0-2 degrees, stack the pieces with modest negative margins, hide secondary accents and keep one signature cutout per screen.
- Images: transparent WebP or AVIF cutouts at display size (not full-resolution PNG), a shared pixel density, one consistent edge treatment. Use licensed or original material; found-image collage needs clearance.

## Interaction and motion
- Pieces land with a short stepped slap-on (scale 1.08 to 1 and 2 degrees of rotation settle over 180-260 ms), tape and stickers peel or wiggle on hover, and layers shift a few pixels on pointer move or scroll for parallax.
- Drag-and-arrange canvases are a natural fit for portfolios, but every drag needs a keyboard route (arrow keys to nudge, Enter to pick up and drop) and a reset.
- Animate `transform` and `opacity` only. Heavy `filter: drop-shadow` on dozens of animating images is slow; shadow a wrapper or use a pre-baked shadow.
- Reduced motion: pieces are in their final place, with no parallax, wiggle or slap-on; hover states change outline or shadow instantly.

## Accessibility cautions
- Meaningful cutouts need alt text that says what the picture shows or conveys; decorative scraps, tape and stickers get `alt=""` or `aria-hidden="true"`.
- Never place text on top of photographic or busy fragments without a solid panel; torn or rotated text blocks are hard to read, so rotate only short labels.
- Reading order and tab order follow the DOM. A free visual arrangement must not scramble it, and focus must be visible on top of overlapping layers (use a 3 px outline and raise the focused element's `z-index`).
- Forced-colors mode removes `box-shadow` and replaces background colours; tape and torn-edge decoration should disappear gracefully, and cards need a real `border` to stay distinct.
- Rotation, scale jumps and parallax can disorient some users: keep rotation small, avoid motion on scroll for large areas, and respect reduced motion.
- Large image sets cost data and memory; lazy-load below-the-fold cutouts and give them intrinsic `width` and `height` to avoid layout shift.

## Common mistakes
- Twenty pieces at once, all the same size, all rotated by random amounts; text rotated with them.
- Soft digital shadows and glows that contradict the paper logic, and mixed edge styles (some torn, some vector-clean) in one scene.
- Text over photographs without a panel; contrast measured against the ground, not the busiest region beneath the text.
- `position: absolute` everywhere, which breaks reading order and responsiveness.
- Cutouts with rough halos from automatic background removal, and decorative PNGs shipped at several megabytes.

## Typical mistakes of AI-generated versions
- A torn-paper PNG pasted across the top of each section as the only gesture at "collage", random rotation on every card and button including inputs, a blurry drop shadow, mixed-style stock cutouts with fringed edges, and ransom-note letters built as separate spans without an accessible name.

## How to build it
- Pattern: `style-collage-cutout`. No collage implementation exists in the local sources, so this recipe is original. Tokens: paper, ink, two or three flat hues, a rotation limit (6 degrees), one shadow offset, one edge treatment, a list of layers with `z-index` values.

```css
.collage { display: grid; grid-template-columns: repeat(12, 1fr); background: #F3EDE0; color: #111111; }
.collage > * { grid-row: 1; }                       /* every piece shares row 1 and overlaps by columns and z-index */
.cut { position: relative; filter: drop-shadow(3px 4px 0 rgb(17 17 17 / .35)); transform: rotate(-3deg); }
.cut img { display: block; width: 100%; clip-path: polygon(2% 5%, 30% 0, 64% 4%, 98% 1%, 100% 40%, 97% 74%, 99% 99%, 61% 95%, 27% 100%, 1% 96%, 3% 55%); }
.cut::after { content: ""; position: absolute; top: -10px; left: 38%; width: 84px; height: 24px; background: rgb(255 214 10 / .8); transform: rotate(5deg); }
.panel { background: #F3EDE0; color: #111111; padding: 1.25rem; border: 2px solid #111111; }
@media (max-width: 40rem) { .cut { transform: none } }
@media (prefers-reduced-motion: no-preference) { .cut { transition: transform .2s } .cut:hover { transform: rotate(-1deg) translateY(-4px) } }
@media (forced-colors: active) { .cut::after { display: none } .cut { outline: 2px solid CanvasText } }
```

- The drop shadow goes on the wrapper and the `clip-path` on the child image on purpose: filters run before clipping, so a shadow on the clipped element itself would be cut away.
- Torn edges: prefer a pre-cut image with an alpha channel or an SVG mask with a jagged path made once in a vector tool, over a full-width bitmap overlay. Tile a small grain texture across the ground only if it stays under text-safe contrast.
- Ransom-note headline: `<h1 aria-label="Open call"><span aria-hidden="true">O</span>...</h1>`, with a different font, rotation and background for each letter span.

## Sources
Original guidance written for this project; no local source files are cited.
