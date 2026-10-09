# Cursor interactions playbook

Choose and build pointer-driven effects (custom cursors, trails, proximity text, spotlights) that are decorative, gated to fine pointers and safe for keyboard and touch users.

In this file `design-sensei` means `${CLAUDE_SKILL_DIR}/scripts/design-sensei`.

## When to use / when not

- Use for portfolios, creative and campaign sites where pointer play is part of the brand, on desktop with a mouse or trackpad.
- Not for dashboards, forms, checkout, documentation or any page where users read or act under pressure.
- Treat every cursor effect as decoration. Nothing essential may be reachable only by pointer, and keyboard users get no equivalent from these effects, so the page must stand without them. Choose one cursor effect per site.

## Pick the approach

| Situation | Pick | Reuse class | Cost and notes |
| --- | --- | --- | --- |
| Cursor that locks onto links and buttons | [[react-bits-target-cursor]] | license_review_required | DOM and GSAP, no GPU. Hides the native cursor on the whole page by default: pass `hideDefaultCursor={false}` or keep a fallback. Touch detection by sniffing: gate it yourself. |
| Images follow the pointer after a distance threshold | [[vengeance-ui-cursor-image-trails]] | copy_with_attribution | `image-trail` caps live items and has a `disabled` prop to bind to the visitor's setting; defaults hotlink Unsplash photos. Pointer only. |
| Same idea with a pooled child set | [[fancy-image-trail]] | copy_with_attribution | Mutates inline styles on pointer events; `repeatChildren` duplicates ids and refs. Motion intensity: intense. |
| Pixel-grid trail | [[fancy-pixel-trail]] | copy_with_attribution | One `motion.div` per cell, so grid size is cost; cells have no default colour. |
| Letters react to pointer distance | [[fancy-cursor-proximity-text]] | copy_with_attribution | Upstream measures every letter every frame; the recipe measures once and updates on pointer events. Large display text only. |
| Light, fluid or ghost trail on the GPU | [[react-bits-webgl-cursor-trails]] | license_review_required | GPU high. SplashCursor has no cleanup: mount once at the root. Only BlobCursor reads reduced motion. Use the budget recipe. |
| Card spotlight or glow under the pointer | [[react-bits-pointer-lit-cards]] | license_review_required | DOM and CSS. See [cards and grids](cards-and-grids.md). |
| Nav pill with a cursor spotlight | [[vengeance-ui-landing-navbars]] | copy_with_attribution | Spotlight is pointer only; see [navigation](navigation.md). |
| Elements pulled or pushed by the cursor | [[fancy-matter-gravity]] (attractor variant) | copy_with_attribution | Matter.js loop; upstream leaks listeners when `grabCursor` is on. The recipe defines a static variant. |
| Timing and gating rules | [[motion-principles]] | original | Cursor-follow and magnetic effects are off under reduced motion. |

Dials: `motion_intensity` below 6 means no trail or full-page cursor; 6-7 one DOM effect; 8+ one effect, GPU cursors only when `webgl_enabled` is true and the budget allows. `visual_density` high pages should skip cursor effects. `reduced_motion` either value: effect off.

## Search commands

```bash
design-sensei search "cursor" --category cursor
design-sensei search "pointer trail" --category cursor --max-gpu low --reduced-motion-safe
design-sensei search "hover spotlight" --category card-grid,cursor,navigation
design-sensei search "cursor pointer" --scope docs
```

## Implementation steps

1. Decide the single effect and its job (brand personality, link targeting). If the job is information, use text, not the cursor.
2. Build the page without it. Native cursor, native focus ring, full keyboard path.
3. Gate mounting: `(prefers-reduced-motion: no-preference)` and `(hover: hover) and (pointer: fine)`, evaluated live with `matchMedia` (React Bits: `MotionGate requireFinePointer`; Vengeance: `disabled={!ready || !motionOk}` on `image-trail`). Prefer feature detection to user-agent sniffing.
4. Listen to `pointermove` on the container, not the whole window, where possible; write one reusable setter per property (`gsap.quickTo` or CSS variables) instead of creating a tween or React state update per event.
5. Never hide the native cursor unless the replacement is mounted and working; restore it on unmount and on gate change.
6. Keep trails bounded: cap live items (Vengeance `image-trail` `maxItems`), remove timers on unmount, pause when the tab is hidden or the section is offscreen.
7. Keyboard parity: where a cursor effect highlights a target, the focus ring must do the same job (the catalog notes say these cursors give keyboard users no focus indicator).
8. Supply your own licensed images for trails; remove hotlinked demo images.

## Accessibility and performance gates

- Reduced motion: do not mount the effect; show static content. No parallax or magnetic motion.
- Touch and coarse pointers: effect off, native behaviour intact.
- No information, label or state conveyed only by pointer position; alt text on trail images is decorative (`alt=""`) unless the image carries meaning.
- A cursor replacement must not cover the element under it, and the targets it points at keep the 24 px minimum size (44 recommended).
- Flash: no more than three flashes per second.
- INP at most 200 ms. Per-frame `getBoundingClientRect()` on many nodes (proximity text) is a layout-thrash risk: measure once, update on events.
- Respect `max_webgl_canvases`: a GPU cursor counts against it. Mount once at the root; free on unmount.

## Common mistakes

- Custom cursor hides the native cursor and then fails to load, leaving no cursor.
- Cursor effect shipped to touch devices or with no reduced-motion branch.
- Full-screen fluid simulation on a content page; two cursor effects together.
- Pointer-only affordances (hover preview cards with generic alt text) for essential content.
- Copying React Bits cursor files into a template (licence gate) or reusing the Vengeance demo photos.

## Where to read more

- Notes: [Fancy components](../../../knowledge/components/fancy.md), [React Bits catalog](../../../knowledge/components/react-bits-catalog.md) (cursor table), [Vengeance UI](../../../knowledge/components/vengeance-ui.md), [motion principles](../../../knowledge/animations/motion-principles-for-ui.md).
- Recipes: [cursor proximity text](../../../knowledge/implementation-recipes/fancy-cursor-proximity-text.md), [heavy background and cursor budget](../../../knowledge/implementation-recipes/react-bits-heavy-background-budget.md), [React Bits install and MotionGate](../../../knowledge/implementation-recipes/react-bits-choose-variant-and-install.md), [motion-safe wrapper](../../../knowledge/implementation-recipes/vengeance-ui-motion-safe-wrapper.md).
- Related playbooks: [typography effects](typography-effects.md), [cards and grids](cards-and-grids.md), [microinteractions](microinteractions.md).
- References: [motion design](../references/motion-design.md), [accessibility](../references/accessibility.md), [performance](../references/performance.md).
