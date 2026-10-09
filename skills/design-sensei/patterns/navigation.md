# Navigation playbook

Choose and build site headers, app shells, mobile menus and animated link treatments that stay keyboard-operable and do not shift layout.

In this file `design-sensei` means `${CLAUDE_SKILL_DIR}/scripts/design-sensei`.

## When to use / when not

- Use for primary navigation, mobile menus, floating docks, mega menus, in-page tabs and link hover effects.
- Not for page-to-page animation (see [page transitions](page-transitions.md)) or decorative cursors ([cursor interactions](cursor-interactions.md)).
- Navigation is the least forgiving place for effects: it is used on every page, by every input method. Default to plain, then add one effect.

## Pick the approach

| Situation | Pick | Reuse class | Notes |
| --- | --- | --- | --- |
| Dashboard, admin or docs app with side, top and mobile nav | [[astryx-app-shell-navigation]] | copy_with_attribution | Skip link, banner and main landmarks, drawer as modal dialog. React 19, pre-1.0 library. Give every nav slot a `label`. |
| Marketing header with dropdown groups | [[vengeance-ui-landing-navbars]] (mega-menu-navbar) | copy_with_attribution | Best keyboard and ARIA of the library: expanded and controls attributes, Escape, labelled mobile dialog. The in-tree file imports a site logo; the published one is self-contained. |
| Floating pill for a one-page site | spotlight-navbar in [[vengeance-ui-landing-navbars]] | copy_with_attribution | Anchors call `preventDefault`; wire navigation through `onItemClick`. Needs three global CSS classes. Spotlight is pointer only. |
| Bottom dock or expanding glass bar | [[vengeance-ui-floating-dock-navigation]] | copy_with_attribution | No reduced-motion handling in any of the three; glass-dock has little ARIA. Some components are ports of other authors' demos with unchecked terms. |
| Sliding pill, staggered overlay menu, card panels, flowing hover | [[react-bits-animated-navigation-menus]] | license_review_required | PillNav needs a React Router `Link` (edit for Next.js); FlowingMenu has no ARIA in the Tailwind copies; StaggeredMenu defaults to the upstream logo. Install into your app only. |
| Link or button label that rolls on hover | [[fancy-letter-swap-text]] | copy_with_attribution | Use the recipe version: it listens on focus too. Do not apply to long labels. |
| Glass nav pill over imagery | [[liquid-glass-css-fallback]] | copy_with_attribution | Needs a solid fallback and a scrim; see [hero sections](hero-sections.md). |
| Plain responsive header, one level | Native `header`, `nav`, `ul`, `a` with your tokens | original | Right answer when `allowed_dependencies` is `none` or `existing`. |

Dials: `motion_intensity` 1-3 means colour and underline changes only; 4-7 allows a sliding indicator or staggered panel under about 400 ms; 8+ allows overlay menus with choreography. `design_variance` high favours overlay or off-grid menus, but never at the cost of a visible text label for each destination.

## Search commands

```bash
design-sensei search "navbar" --category navigation
design-sensei search "menu mobile drawer" --category navigation --framework react
design-sensei search "link hover text" --category typography --max-gpu low
design-sensei search "navigation" --scope docs
```

## Implementation steps

1. List destinations (five to seven top level), the primary action and the mobile behaviour. Decide whether the header is static or sticky.
2. Write the semantic markup first: `header` containing a skip link, `nav aria-label="Primary"`, a list of links, `aria-current="page"` on the current link. Menus that expand use a `button` with `aria-expanded` and `aria-controls`.
3. Mobile: below the breakpoint, a button opens a modal surface (native `<dialog>` with `showModal()` is the pattern in the [Astryx accessibility note](../../../knowledge/components/astryx-accessibility-spec.md)): focus moves inside, Escape closes one layer, focus returns to the button, body scroll is locked (with Lenis: `stop` and `start`, see [[lenis-nested-scroll-and-modals]]).
4. Add the effect. Hover styling goes inside `@media (hover: hover)`; every hover effect has a focus-visible equivalent.
5. If a component library is chosen, install through its documented route ([Vengeance install recipe](../../../knowledge/implementation-recipes/vengeance-ui-install-and-verify-component.md), [React Bits install recipe](../../../knowledge/implementation-recipes/react-bits-choose-variant-and-install.md)), then run `tsc` and a keyboard pass: some payloads import site modules they do not ship.
6. Reserve the header height (fixed or `min-height`) so the sticky bar causes no layout shift; set `scroll-padding-top` so anchor targets and focused elements are not hidden behind it.
7. Gate looping or spotlight motion with the motion-safe wrapper for Vengeance components or `MotionGate` for React Bits.

## Accessibility and performance gates

- Every control reachable by Tab, operable by Enter and Space (buttons), Escape closes menus. Roving arrows only for true composite widgets.
- Visible `:focus-visible` ring with 3:1 contrast on every background; a sticky header must not cover the focused element (WCAG 2.2 Focus Not Obscured).
- Touch targets at least 24 by 24 CSS px, 44 recommended.
- Text contrast 4.5:1 in rest, hover and active states, light and dark; glass nav needs a scrim.
- `backdrop-filter` on a full-width sticky header repaints on scroll; keep blur small and test on a mid-range phone.
- Reduced motion: no sliding or stagger; state change is instant or a 150 ms fade.
- Icon-only buttons have an accessible name that contains the visible label.

## Common mistakes

- Hover-only dropdowns with no keyboard path; `preventDefault` on links with no replacement navigation.
- Hamburger as the only mobile affordance with no label, or an overlay menu without focus management.
- Letter-swap or scramble on every nav link so the menu is hard to read.
- Mixing a React Bits menu, a Vengeance dock and Astryx shell in one app: pick one navigation system.
- Copying PillNav or StaggeredMenu into a template repository (licence gate: use in your own app only).
- Fixed header with no height reservation, causing CLS.

## Where to read more

- Notes: [Astryx](../../../knowledge/components/astryx.md), [Astryx accessibility spec](../../../knowledge/components/astryx-accessibility-spec.md), [Vengeance UI](../../../knowledge/components/vengeance-ui.md), [React Bits catalog](../../../knowledge/components/react-bits-catalog.md) (navigation table), [React Bits licence use](../../../knowledge/implementation-recipes/react-bits-license-safe-usage.md).
- Recipes: [letter swap](../../../knowledge/implementation-recipes/fancy-letter-swap-text.md), [motion-safe wrapper](../../../knowledge/implementation-recipes/vengeance-ui-motion-safe-wrapper.md).
- Related playbooks: [hero sections](hero-sections.md), [microinteractions](microinteractions.md), [page transitions](page-transitions.md), [responsive layouts](responsive-layouts.md).
- References: [accessibility](../references/accessibility.md), [responsive design](../references/responsive-design.md), [component selection](../references/component-selection.md).
