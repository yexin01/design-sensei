---
title: "High-fashion and luxury"
kind: design-style
summary: "Exclusivity through restraint, slowness and image quality: art-directed full-bleed photography, high-contrast serifs or light grotesques, widely tracked small caps, muted metallic accents and unhurried motion. Warns against the black-and-gold cliche and contrast traps."
source_ids: [lenis, taste-skill]
pattern_ids: [style-high-fashion-luxury]
updated: "2026-10-09"
---

# High-fashion and luxury

Luxury and high-fashion sites signal exclusivity by getting out of the way. The interface recedes; photography, film and typography carry the brand; interactions are slow and sure; nothing looks like a discount. It is not "black and gold". The quality bar is the imagery: with weak photography the style collapses.

## Visual characteristics
- Large, full-bleed, art-directed photography or film with generous negative space.
- A high-contrast serif or an ultra-light grotesque for display; small uppercase navigation with wide tracking.
- A monochrome base (black, ivory, stone) with one muted metal or jewel accent used sparingly.
- Hairline rules and thin icons; no badges, banners, countdowns or urgency devices.
- Slow cinematic transitions; navigation led by lookbooks and collections.

## When it fits, when it does not
- Fits: fashion houses, jewellery, watches, fragrance, hospitality, premium property, galleries, high-end automotive and product launches.
- Poor fit: price-led retail, marketplaces, grocery, B2B tools, anything needing dense comparison or fast task completion, and brands without a photography budget.
- Supporting influences that work: editorial, minimalism, art-deco, grain-and-texture, motion-led-storytelling, a single-product experimental-3d scene. Avoid neo-brutalism, y2k and claymorphism.

## Typography
- Display: a Didone or transitional serif (Bodoni Moda, Playfair Display, Cormorant, Newsreader; commercial options include Didot and Canela) or a light, wide grotesque. 48-120 px at weight 300-400, tracking -0.01 to -0.03em for serifs.
- Navigation and labels: uppercase sans at 12 px or larger, tracking +0.12 to +0.3em, weight 400-500, five to seven items at most.
- Body 15-17 px at line-height 1.7, weight 400. Weights below 400 fail over photography and on low-density screens.
- Hairline Didone strokes vanish at small sizes; use an optical-size cut or switch to a sturdier family below about 28 px. No script faces, no all-caps paragraphs.

## Colour
- Black (#0B0B0B) and ivory (#F5F0E6), or warm black (#14110F) with ivory text at 16.6:1; stone and taupe mid-tones; one accent such as champagne, bronze, oxblood or emerald.
- Metallic gold needs care. #C9A961 on white is 2.25:1 and #D4AF37 on white is 2.10:1, so on light grounds gold is decoration only; use a deep bronze like #8A6D1F (4.9:1) for text. On near-black, #D4AF37 reaches 9.4:1 and champagne #C8B27A on #14110F reaches 9.05:1.
- Avoid faux-metal gradients; if you use one, keep it to a thin highlight on large display elements, not buttons.
- Grade imagery consistently with restrained saturation; black and white is acceptable.

## Composition and layout
- A full-bleed hero (image or looped film with a poster frame), a minimal fixed header (logo centred, navigation at the sides), margins of 6-10vw, one idea per screen, asymmetric text placement.
- Collection grids of two or three columns with 32-64 px gutters and one aspect ratio (for example 4:5); minimal captions.
- Product pages are image-led with a sticky text column and zoom.
- On phones use single-column image stacks and keep the header minimal; do not rely on a hamburger alone on desktop.

## Interaction and motion
- Slow and damped: 600-1200 ms ease-out (for example `cubic-bezier(0.22, 1, 0.36, 1)`), image reveals from scale 1.04 to 1, hover cross-fade to an alternate product image.
- Skip long preloaders. If one is used, keep it to 1.5 s or less and skippable; never delay content for an animation.
- Avoid custom cursors. Smooth scrolling is optional, and Lenis disables its smoothing for reduced-motion users by default.
- Reduced motion: swap slow reveals for instant states or 150 ms fades, remove scale and parallax, show the poster instead of autoplaying video.

## Accessibility cautions
- Light weights, wide tracking and photography combine badly. Use scrims or reserved text zones and test the busiest region of each image.
- Autoplay video needs a pause control and no audio (WCAG 2.2.2); respect data-saver settings.
- Eleven-pixel tracked-out labels are hard to read for many users; use 12-14 px at 4.5:1 and a visible focus style.
- Image-led navigation still needs text labels. Product alt text should describe colour, material and cut, which is the information buyers need.
- Do not hide price or availability behind hover.

## Common mistakes
- Black with gold gradients everywhere, plus script type.
- Heavy motion and preloaders that delay content; multi-megabyte hero films.
- Light type directly on photography; tiny navigation.
- Discount mechanics (banners, countdowns, pop-ups) that contradict the positioning.
- One low-resolution photograph is enough to break the premium impression.

## Typical mistakes of AI-generated versions
- "Luxury" rendered as a black page, metallic-gold gradient buttons, Playfair Display and "Elevate your style" copy over stock lifestyle photos.
- Gold text on mixed light and dark sections, and 11 px labels that fail contrast.
- Parallax, zoom and fade effects all firing at once on one screen.

## How to build it
- Pattern: `style-high-fashion-luxury`. Order of work: photography selection and crops, type tokens, layout, then motion tokens (600-1200 ms).
- The Editorial Luxury archetype in `taste-skill:skills/soft-skill/SKILL.md` (warm creams, variable serifs, faint grain) and its guardrails are useful: put grain on a fixed, non-interactive layer, and apply backdrop blur only to fixed or sticky elements.
- Smooth scroll: `lenis:README.md` documents `respectReducedMotion` (default on, smoothing off and anchor jumps instant when the user prefers reduced motion) and the `prefersReducedMotion` getter; the implementation is in `lenis:packages/core/src/lenis.ts`.
- Content-level reduced-motion handling for scroll-linked effects is your job; Lenis only governs scroll smoothing.

## Sources
Original guidance written for this project. lenis and taste-skill are MIT-licensed and cited as reference only.
