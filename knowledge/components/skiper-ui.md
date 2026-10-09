---
title: "Skiper UI clone (reference only)"
kind: component-library
summary: "Factual description of an unlicensed, unofficial frontend clone of the Skiper UI site: its structure, component categories and observed techniques, with a clear warning that it may be read for ideas only and that no code, assets or copy may be reused."
source_ids: [skiper-ui]
pattern_ids: [skiper-ui-theme-toggle-view-transition, skiper-ui-coverflow-card-carousel, skiper-ui-stepped-feature-card]
updated: "2026-10-09"
---

# Skiper UI clone (reference only)

**Reuse status: ideas only.** The repository has no licence file and no licence field in its manifest, and its own README says it is an educational frontend clone of someone else's site design (`skiper-ui:README.md`). Treat everything in it as all rights reserved. Do not copy code, class strings, SVG paths, images, fonts or text from it, and do not derive recipes from it. No code or copy is quoted on this page.

## What it is

- A single-page Next.js project that imitates the landing page of the Skiper UI component site. The README names the original site (skiper-ui.com) as the design inspiration and describes the repository as a learning and demonstration clone, not the official library (`skiper-ui:README.md`).
- It is therefore not a component library in the usual sense: there is no registry, no install command for components, no docs and no tests. `skiper-ui:package.json` is private, version 0.1.0, with the stock Next.js scripts.
- Catalog facts (`catalog/sources.yaml`, `catalog/licenses.yaml`): no licence found at the pinned commit, status `not_found`, redistribution `unresolved`, review state `needs_human_review`. The catalog notes that the rights to the design and components are likely held by the authors of the original project, so check the original project's own terms before using anything.

## Stack (from `skiper-ui:package.json`)

Next.js 15.4.4, React 19.1.0, Tailwind CSS 4, `motion` and `framer-motion` (both ^12), `swiper` ^11, `next-themes`, `lucide-react`, `react-wrap-balancer`, `class-variance-authority` with `@radix-ui/react-slot`, and `tw-animate-css`. shadcn is configured through `skiper-ui:components.json` (style `new-york`, `lucide` icons). The README describes the animation library only as implied by the project structure; the manifest confirms `motion`.

## Structure

| Path | Contents |
|---|---|
| `skiper-ui:src/app/page.tsx` | the landing page: navbar, hero, carousel card, template cards, stepped feature card, AI input card, theme toggles |
| `skiper-ui:src/app/layout.tsx` | root layout with two Google fonts; the page metadata is still the unchanged create-next-app default |
| `skiper-ui:src/app/globals.css` | shadcn-style colour tokens in oklch with a dark variant, plus one local `@font-face` |
| `skiper-ui:src/componets/` | all components. The folder name is misspelled; the README structure listing says `src/components` |
| `skiper-ui:src/lib/utils.ts` | the usual `cn` helper |
| `skiper-ui:public/images/` | eight WebP card images; `skiper-ui:public/fonts/` holds two woff2 files |

## Component categories

| Category | Files | What it does, in prose | Pattern |
|---|---|---|---|
| Navigation | `skiper-ui:src/componets/navbar/Navbar.tsx`<br>`skiper-ui:src/componets/navbar/NavPart1.tsx`<br>`skiper-ui:src/componets/navbar/NavPart2.tsx` | Logo, text links and a pill-shaped fake search field with a keyboard hint; static markup with no menu logic | - |
| Hero | `skiper-ui:src/componets/landingPage/HeroContent.tsx` | Centred two-line headline, a call-to-action pill button, a hand-drawn arrow graphic and two decorative background images loaded from the original site | - |
| Carousel | `skiper-ui:src/componets/ui/card-carousel.tsx`<br>`skiper-ui:src/componets/homeCards/CardCarouselParent.tsx` | Centred slides in a depth-style coverflow arrangement, looping and autoplaying, built on the Swiper library | `skiper-ui-coverflow-card-carousel` |
| Template cards | `skiper-ui:src/componets/ui/minimal-card.tsx`<br>`skiper-ui:src/componets/homeCards/TemplateCard.tsx` | A card family (image, title, description, content, footer) whose tactile look comes from several layered inset and outer shadows, with separate light and dark stacks | - |
| Stepped feature card | `skiper-ui:src/componets/ui/skiper-card.tsx`<br>`skiper-ui:src/componets/homeCards/SpecialCard.tsx` | A dark card of stacked screenshots that cross-fade through four states; a timer advances the state every few seconds and a click skips ahead; a three-item progress list shows where you are | `skiper-ui-stepped-feature-card` |
| AI input | `skiper-ui:src/componets/ui/ai-input.tsx`<br>`skiper-ui:src/componets/homeCards/AiInputCard.tsx` | Chat-style input: auto-growing textarea with a height cap, an animated placeholder that swaps between an ask wording and a search wording, a search toggle chip, an image attachment with preview, Enter to send and Shift+Enter for a new line | - |
| Theme toggle | `skiper-ui:src/componets/ui/theme-toggle-button.tsx`<br>`skiper-ui:src/componets/ui/theme-animations.ts`<br>`skiper-ui:src/componets/homeCards/ThemeChange.tsx` | Icon button that switches light and dark with an animated reveal; the demo section renders eight of them (two with a GIF mask, six with the default blurred-circle reveal) | `skiper-ui-theme-toggle-view-transition` |
| Buttons and badges | `skiper-ui:src/componets/ui/wrap-button.tsx`<br>`skiper-ui:src/componets/ui/badge-button.tsx`<br>`skiper-ui:src/componets/ui/badge.tsx`<br>`skiper-ui:src/componets/ui/button.tsx` | A pill button with an inner coloured capsule and a circular arrow badge that shifts and turns on hover; a small outlined badge; the standard variant-based button | - |
| Primitives | `skiper-ui:src/componets/ui/textarea.tsx`<br>`skiper-ui:src/componets/ui/theme-provider.tsx` | A shadcn-style textarea and a thin wrapper around the `next-themes` provider; the wrapper is never mounted anywhere in `src/` | - |

## Observed techniques (described, not reproduced)

- **Theme reveal with the View Transitions API.** Before toggling the theme, the button writes a style element containing the transition rules for the chosen variant (expanding circle from a corner, circle with a soft blurred edge, polygon sweep, or a GIF used as a mask) and then asks the browser to run the theme change inside a view transition. If the API is missing it switches the theme immediately. The View Transitions API itself is a public web-platform feature; learn it from its own documentation, not from this repository.
- **Coverflow carousel.** Swiper supplies the coverflow effect, centred slides, looping, grab cursor and autoplay; the component passes a delay prop (default 1.5 seconds) and keeps autoplay running after user interaction. It renders the image list twice to give the loop enough slides, and injects a style tag to override some Swiper shadow classes.
- **Step cycler.** A counter in React state advances on an interval and on click; each step toggles opacity and translation classes on stacked absolutely positioned images, so the "animation" is a CSS transition between staged states. Children mount only after the first client render to avoid a hydration mismatch.
- **Pointer position as CSS variables.** The feature card tracks the pointer into motion values and writes them to two CSS custom properties on its wrapper. Nothing in the repository reads those properties, so the effect is unfinished.
- **Auto-growing textarea.** The height is reset to a minimum, then set to the scroll height up to a maximum, on input and on window resize. The attachment preview uses an object URL and revokes it in an effect cleanup.
- **Layered shadows for depth.** Cards stack a hairline ring, a soft drop shadow and an inset highlight, with a different stack in dark mode.

## Observations on quality

- No `prefers-reduced-motion` handling anywhere in `skiper-ui:src/`. The carousel autoplays and the step cycler runs on a timer with no pause control; one button variant spins a globe icon continuously.
- The theme toggle leaves debug `console.log` calls in place and checks only for exactly the light theme when deciding the next theme. The `next-themes` provider wrapper exists but is not used in the layout or page, so in this checkout the toggles have no theme state to drive (read, not run).
- Accessibility gaps: the AI input hides its native placeholder and draws a separate animated hint, has no label tied to the textarea, and its send, attach and clear controls are icon-only without accessible names. The step list does use a labelled navigation landmark.
- Responsiveness is doubtful despite the README's mobile-first claim: several wrappers use a fixed fraction of the page width, template cards use a fixed pixel width, and hero decorations are absolutely positioned at fixed offsets.
- Several visuals are hot-linked from third parties (Product Hunt badge, original-site background SVGs, Twitter-hosted images, Giphy GIFs). Those assets are not the clone author's to give away.
- A user-agent plus media-query helper decides "mobile" for the pointer effect; prefer feature detection (`pointer: coarse`, `hover: none`) in new code.

## Reduced-motion alternatives for the three ideas (guidance, no code)

The clone has none, so an independent build should add them:

- **Theme reveal:** when `prefers-reduced-motion: reduce` is set, switch the theme immediately without a view transition (a short cross-fade is acceptable).
- **Coverflow carousel:** no autoplay under reduced motion; show slides in a plain scrollable row or a static grid. If autoplay stays for other users, add a visible pause control.
- **Stepped feature card:** stop the timer, show the first state, and let people move between states with buttons, or list all states statically.

## Using it legitimately

1. Read it to see which effects the original site is known for: coverflow carousel, step-through feature card, animated theme switch, chat-style input, layered-shadow cards.
2. Rebuild any of them independently from the public documentation of the underlying tools (Swiper, Motion, the browser View Transitions API, `next-themes`). Use your own markup, class names, copy, colours and images.
3. For maintained, licensed alternatives with comparable techniques, see `knowledge/components/fancy.md`.

## Related

- Pattern records (reference only, no recipes): `skiper-ui-theme-toggle-view-transition`, `skiper-ui-coverflow-card-carousel`, `skiper-ui-stepped-feature-card` in `catalog/patterns.d/ui-fancy-skiper.yaml`.
