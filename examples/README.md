# Examples

## 1. `glass-hero/` - a verified example of the `liquid-glass-css-fallback` approach

A static hero section (HTML + CSS, no JavaScript, no dependencies, no images): frosted glass panels over three slowly drifting blurred blobs.
It is original work written for this repository following the plain-CSS glass guidance in
[`knowledge/implementation-recipes/liquid-glass-ui-with-css-fallback.md`](../knowledge/implementation-recipes/liquid-glass-ui-with-css-fallback.md) and the playbook
[`skills/design-sensei/patterns/liquid-glass.md`](../skills/design-sensei/patterns/liquid-glass.md).

Open `glass-hero/index.html` in a browser.

What was checked (2026-10-09):

| Check | Result |
| --- | --- |
| `design-sensei eval examples/glass-hero --verbose` | no findings in any category |
| Headless Chromium, 1280x800 and 375x812 | renders as designed; no horizontal overflow at 375 px; screenshots inspected |
| Console and network | no console messages; only `index.html` and `styles.css` requested |
| Text contrast | computed against the worst-case surface behind the glass (bright amber or teal blob under the scrim): primary text 6.4:1, secondary text 4.9:1 (WCAG AA body text needs 4.5:1) |
| Reduced motion | `prefers-reduced-motion: reduce` removes the blob animation and button transitions (checked in the stylesheet; not emulated in the browser) |
| Fallbacks | `@supports not (backdrop-filter ...)` solid surface and `forced-colors` rules present (not exercised in a browser) |

Not checked: other browsers, real devices, screen readers, `prefers-contrast` and `prefers-reduced-transparency` (the playbook lists them as gaps), performance measurement beyond the absence of images and scripts.

## 2. Using the skill: a worked flow

The commands below are real; the output shape is shown abbreviated.

```bash
# 0. Is everything in place?
design-sensei doctor --brief

# 1. After inspecting the project and writing the art-direction brief, look for implementations
design-sensei search "frosted glass card" --max-gpu low --reduced-motion-safe
#   1. liquid-glass-css-fallback  [liquid-glass]
#      sources: liquid-glass-js (MIT, verified) | reuse: copy_with_attribution
#      recipe: .../knowledge/implementation-recipes/liquid-glass-ui-with-css-fallback.md
#      file: .../sources/liquid-glass-js/glass.css

# 2. Read the recipe and the real file, compare an alternative
design-sensei search "glass" --scope all --limit 5
design-sensei sources show liquid-glass-js          # license, pin, local state

# 3. A source that is not downloaded yet (asks permission, needs git and network)
design-sensei sources sync liquid-glass-js

# 4. After implementing
design-sensei eval ./my-site
```

A restricted source shows its class in the result: for example `design-sensei search "aurora background" --source react-bits` prints `reuse: license_review_required`, and the skill then uses the library as a dependency or writes an original implementation instead of copying files.

## 3. Project configuration

```bash
cd my-site
design-sensei config init      # writes a commented .design-sensei.yaml
design-sensei config show      # effective values and where each comes from
```

A restrained product site might set `design_variance: 4`, `motion_intensity: 3`, `visual_density: 7`, `allowed_dependencies: none`, `webgl_enabled: false`; a campaign microsite `design_variance: 9`, `motion_intensity: 8`, `reduced_motion: static_first`.
