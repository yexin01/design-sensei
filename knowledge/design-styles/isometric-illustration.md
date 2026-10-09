---
title: "Isometric and 3D illustration"
kind: design-style
summary: "Objects drawn on a shared 30-degree grid with no perspective, three tonal faces per solid and one light direction, plus the softer rendered 3D branch. Covers projection maths, face-tone contrast numbers, SVG construction, motion on the vertical axis and text alternatives for diagrams."
source_ids: [vengeance-ui]
pattern_ids: [style-isometric-illustration]
updated: "2026-10-09"
---

# Isometric and 3D illustration

Isometric illustration draws objects as if seen along a diagonal with the vanishing point removed: parallel edges stay parallel, all three axes shorten equally and every solid shows a top face and two side faces. It turns abstract things (pipelines, infrastructure, workflows, cities, warehouses) into tidy miniature worlds you can point at. The sibling branch, soft 3D illustration, uses rendered or hand-shaded rounded volumes with studio lighting and is delivered as images. Both live or die on consistency: one angle, one light direction, one unit of scale across the whole set.

## Visual characteristics
- True isometric: the two ground axes run 30 degrees above horizontal and the third axis is vertical. Game-style 2:1 dimetric (about 26.6 degrees) is a close cousin and the natural fit for pixel work.
- Each solid shows a lit top face, a mid-tone left face and a dark right face (or the mirror image, but always the same way round), all from one hue family.
- Flat fills with a uniform thin outline or none; gradients are rare and shadows are flat low-opacity shapes on the ground plane.
- Scenes are assembled from platforms, tiles, blocks, stacks, pipes and screens, with small figures or icons for scale and clear gaps between objects.
- The 3D branch: rounded forms, matte materials, soft key light with a faint bounce, shallow depth, one or two accent colours.

## When it fits, when it does not
- Fits: architecture and workflow explainers, B2B and developer-infrastructure heroes, fintech and logistics stories, onboarding steps, feature sections, maps, floor plans, infographics, game-adjacent and educational products.
- Poor fit: cases where the real product screen is the better proof, dense data where the tilt distorts reading, strictly minimal brands, content that changes weekly (each scene is costly to edit), and anything shown below roughly 200 px wide where faces merge into blobs.
- Supporting influences that work: product-led-saas, bento-layouts, minimalism, pixel-art-8bit (for the 2:1 variant), experimental-3d (when the scene must actually rotate), generative-design. Avoid brutalism and hand-drawn-doodle, whose wobble fights a rigid grid.

## Typography
- Keep type flat and upright. Skewing text onto an isometric plane is acceptable for a single display word on a face; everything else belongs in HTML beside the drawing.
- Neutral geometric or humanist sans such as DM Sans, Manrope or Plus Jakarta Sans for headings and callouts, with a mono (JetBrains Mono, IBM Plex Mono) for technical tags. Headings 32-56 px at weight 600-700, tracking -0.01 to -0.02em.
- Callout labels 13-14 px minimum at weight 500-600; numbered badges 24-28 px circles; connect labels to objects with leader lines instead of squeezing text onto faces.

## Colour
- Build every hue as a three-step ladder. One indigo example on a cool ground: top #A5B4FC, left #6366F1, right #4338CA, ground #F4F6FB, ink #1B2340.
- Text on those fills: ink on ground is 14.27:1, ink on the top face 7.74:1, white on the right face 7.90:1. Ink on the left face is only 3.45:1 and white on it 4.47:1, so put labels on top faces in ink, on dark faces in white, or outside the drawing.
- The pale top face against the ground is just 1.84:1, while the left (4.13:1) and right (7.31:1) faces still hold the silhouette. If the outline of a shape carries meaning, add a 1.5 px ink stroke or darken the ground to reach 3:1.
- Use one accent for the object you want noticed (amber #FFD166 takes ink text at 10.70:1) and keep the rest to one or two base hues plus neutrals.
- Shadows are flat ink shapes at 10-20% opacity. In dark mode keep the top face the lightest tone, since light still comes from above.

## Composition and layout
- Work on an invisible grid. With an edge length of 40 units a grid corner (gx, gy, gz) lands at x = (gx - gy) * 34.64 and y = (gx + gy) * 20 - gz * 40, and a cube in cell (i, j, k) is drawn with its near-top vertex at corner (i+1, j+1, k+1). Snapping to the grid prevents the slight wobble that makes amateur scenes look off.
- Draw from far to near by sorting on gx + gy + gz; wrong depth order is the most visible error.
- One hero scene per section with five to nine objects, space along the diagonals, and connectors that travel only along the three axes.
- Deliver as SVG with a `viewBox` so it scales; keep headings, labels and links in HTML. On narrow screens crop to the key object or turn the scene into a vertical stack, keeping each object at least 64 px wide.
- Icon and illustration sets share angle, outline weight and corner radius; never mix an isometric object with a perspective camera.

## Interaction and motion
- Motion happens on the vertical axis and along the grid axes only: a hover lift of 4-8 px with the shadow shrinking, blocks sliding in along an axis, connectors drawing with `stroke-dashoffset` over 600-900 ms, an idle bob of 6-12 px every 4 s.
- Do not rotate an object in 2D; it breaks the projection. A real turntable calls for actual 3D (see experimental-3d).
- Animate `transform` and `opacity`. Inside SVG set `transform-box: fill-box` so group transforms use the group's own box. Pause scenes that are off-screen.
- Reduced motion: no loops or bob, show the assembled scene, and turn the hover lift into an instant outline or colour change. SMIL `animateTransform` is not stopped by CSS media queries, so check `matchMedia('(prefers-reduced-motion: reduce)')` in script and do not render it.

## Accessibility cautions
- A scene that explains something is a text-bearing image: give the SVG `role="img"` with `<title>` and `<desc>` (or `aria-labelledby`) and repeat the content as a nearby list or caption. Decorative scenes get `aria-hidden="true"`.
- Never encode meaning in face tone or hue alone; add labels, numbers or icons.
- Hotspots should be real buttons or links positioned over the drawing, with 44 px targets where possible and a 3 px focus ring, not click handlers on polygons.
- Forced-colors mode can replace SVG paint, collapsing the three tones into one. Add `stroke: CanvasText` outlines inside a forced-colors block and keep labels as HTML.
- Never bake text into rendered 3D raster images; write alt text that states the point of the picture, not its appearance.

## Common mistakes
- Mixed angles (some objects at 30 degrees, others at 45 top-down) and mixed light directions.
- Scenes with thirty objects and microscopic text on faces; skewed paragraphs.
- Floating objects with no contact shadow or grid relation; wrong depth order.
- Glow and heavy gradients over an otherwise flat scene; cube clip-art that illustrates nothing in the copy.
- Oversized unoptimised PNG renders in the 3D branch and no dark-mode variant.

## Typical mistakes of AI-generated versions
- Image models produce "isometric" scenes whose angles drift, whose screens contain garbled text and whose style cannot be repeated across a set; every concept becomes a floating cube on a purple-to-blue gradient with neon glow and scattered tiny people.
- Code versions use `rotateX(60deg) rotateZ(45deg)`, which gives a 2:1 dimetric look rather than isometric (true isometric needs about 54.74 and 45 degrees), then skew the text with the plane so it becomes illegible.

## How to build it
- Pattern: `style-isometric-illustration`. Tokens: edge length, the three face tones per hue, ink, ground, one accent, a stroke weight. The recipe below is original: one cube symbol, reused by `<use>` at grid positions.

```html
<svg viewBox="-60 -90 150 170" role="img" aria-labelledby="t d">
  <title id="t">A stack of two blocks beside a single block</title>
  <desc id="d">Two blocks stacked at the back left, one block in front on the right.</desc>
  <defs><g id="cube"><polygon class="top" points="0,0 34.64,-20 0,-40 -34.64,-20"/>
    <polygon class="lft" points="0,0 -34.64,-20 -34.64,20 0,40"/>
    <polygon class="rgt" points="0,0 34.64,-20 34.64,20 0,40"/></g></defs>
  <use class="block" href="#cube" x="0" y="0"/>        <!-- cell 0,0,0 -->
  <use class="block" href="#cube" x="0" y="-40"/>      <!-- cell 0,0,1 -->
  <use class="block" href="#cube" x="34.64" y="20"/>   <!-- cell 1,0,0, drawn last: nearest -->
</svg>
```

```css
.top { fill: #A5B4FC } .lft { fill: #6366F1 } .rgt { fill: #4338CA }
polygon { stroke: #1B2340; stroke-width: 1.5; stroke-linejoin: round }
.block { transition: transform .2s ease-out }
.block:hover { transform: translateY(-6px) }
@media (prefers-reduced-motion: reduce) { .block { transition: none } }
@media (forced-colors: active) { polygon { fill: Canvas; stroke: CanvasText } }
```

- Closest local reference: `vengeance-ui:src/components/landing/ui/isometric-hero-box.tsx` builds an isometric stage in inline SVG with affine matrices made from 0.866 (cos 30 degrees) and 0.5 (sin 30 degrees), floats a cube with SMIL `animateTransform`, and pauses that animation when scrolled out of view via IntersectionObserver. It also maps live HTML onto the left and right faces with `foreignObject` under a skew matrix and swaps the previews every 3 seconds. It has no reduced-motion handling and no pause control for the rotating faces, so treat it as a projection reference and add both if you adapt the idea.

## Sources
Original guidance written for this project. vengeance-ui is MIT-licensed and cited as reference only; nothing was copied from it.
