---
title: "Use React Bits within its licence"
kind: recipe
summary: "Plain-words guide to what the MIT plus Commons Clause terms of React Bits appear to allow and forbid, how to keep a project on the safe side, and how Design Sensei itself handles the source. Not legal advice."
source_ids: [react-bits]
pattern_ids:
  - react-bits-ogl-shader-backgrounds
  - react-bits-self-pausing-shader-backgrounds
  - react-bits-three-r3f-backgrounds
  - react-bits-webgpu-backgrounds
  - react-bits-canvas-grid-backgrounds
  - react-bits-gsap-text-reveals
  - react-bits-lightweight-text-effects
  - react-bits-target-cursor
  - react-bits-webgl-cursor-trails
  - react-bits-scroll-driven-components
  - react-bits-bento-and-card-grids
  - react-bits-pointer-lit-cards
  - react-bits-animated-navigation-menus
  - react-bits-3d-image-galleries
  - react-bits-glass-surfaces
  - react-bits-micro-spring-controls
updated: "2026-10-09"
---

# Use React Bits within its licence

This is a reading aid, not legal advice. The licence text is short and partly ambiguous; when money or a distribution plan depends on it, ask the maintainer or a lawyer.

## Goal

Use React Bits components in real projects without breaking the terms, and keep Design Sensei from redistributing them.

## When to use

- Before adding React Bits code to a client site, a product, a template, a starter repository or an AI-generated project.
- Before any step that would put React Bits code somewhere other people receive it as components.

## What the licence says, paraphrased

Source: `react-bits:LICENSE.md` (a custom "MIT plus Commons Clause" text, copyright 2026 David Haz), summarised in the README licence and credit sections (`react-bits:README.md`).

1. You may use, copy, modify, merge, publish and distribute the software as part of an application, website or product, provided the copyright notice and permission notice are included in all copies or substantial portions.
2. Commercial use is fine, as long as you do not sell, sublicense or redistribute the components themselves, whether alone, in a bundle, or as a ported version.
3. The software comes with no warranty.
4. The README calls it free for personal and commercial use, and says some components are rewritten from public code examples; people who recognise their work can ask for credit through an issue.
5. Community contributions of new components are not accepted (`react-bits:CONTRIBUTING.md`), so the maintainer is the sole upstream.

Design Sensei's own ledger records the licence as needing human review and as not detected by GitHub (`catalog/licenses.yaml`, `catalog/sources.yaml`).

## A conservative reading

| Activity | Reading |
|---|---|
| Use components in a site or app you build, for yourself or a client, including commercial products | Allowed |
| Edit the copied source, props, styles, markup | Allowed |
| Keep the app repository private or public as a whole application | Allowed, with the notice kept |
| Sell the components, or a pack, kit or template whose value is mostly these components | Not allowed |
| Publish them as an npm package, component registry, snippet library or shadcn-style registry | Not allowed |
| Port them to another framework (Vue, Svelte, Angular, native) and share the port | Not allowed (the text names ported versions) |
| Grant others different licence terms for the components (sublicense) | Not allowed |
| Ship them inside a product whose main deliverable is the code itself, such as a boilerplate | Grey area: ask |
| Reimplement an effect from its public behaviour without reading its code | Not covered by this licence; document that you worked independently |
| Reimplement by closely following the source | Risky: may count as a port or derivative |
| Use the Pro product, tools output, logos or sponsor media | Separate terms or not granted here; do not assume |

## Steps for a project

1. Decide the distribution model. If someone other than your own users receives the components as source (a template, a starter, an open-source component repo), stop and get permission first.
2. Install through the upstream channels (`knowledge/implementation-recipes/react-bits-choose-variant-and-install.md`) so each copy comes from the maintainer.
3. Keep the notice: store the upstream copyright and permission notice in your repository, for example in a third-party notices file, and keep file headers intact.
4. Keep copies inside the application. Do not export them from a shared package that you publish.
5. Replace branded or placeholder assets: the upstream logo default in StaggeredMenu, remote Unsplash, picsum and pravatar images, sponsor and README media.
6. Check the licences of the npm packages each component imports. GSAP in particular has its own terms (`catalog/licenses.yaml`).
7. Record the upstream commit or date of every copied component so you can show where it came from.

## How Design Sensei applies it

- Notes and recipes describe behaviour in our own words and cite upstream paths; they never include React Bits code, even short excerpts.
- Recipes teach installing the library into the user's app and wrapping it with original code; they never output a React Bits component.
- Pattern records point at upstream files and are marked `recipe_available` only for the wrapper and install guidance.
- Agents using this knowledge should tell users to install through the CLI instead of pasting component code from memory.

## Verification checklist

- [ ] The upstream notice is stored in the project.
- [ ] No React Bits component is in a published package, a sold template or a public registry.
- [ ] No React Bits logo, sponsor media or demo media ships in the product.
- [ ] Remote placeholder images are replaced.
- [ ] Each copied component has a recorded source commit or date.
- [ ] Dependency licences (GSAP and others) were checked.

## Upstream references

`react-bits:LICENSE.md`, `react-bits:README.md`, `react-bits:CONTRIBUTING.md`, `react-bits:src/ts-tailwind/Components/StaggeredMenu/StaggeredMenu.tsx` (default branding path), `react-bits:package.json`.

## Licence notes

Everything here paraphrases the files above and carries no React Bits code. Interpretation is ours and may be wrong.
