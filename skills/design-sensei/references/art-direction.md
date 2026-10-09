# Art direction

Turn a vague brief into a written, checkable set of design decisions before any code exists.

## When to load this

Load it at step 2 of the workflow, after inspecting the project and before searching for patterns. Skip the brief when a `DESIGN.md`, brand guide or
existing token system already fixes these decisions: that file outranks everything here. Then only fill the gaps it leaves open.
Never ask the user to fill in a questionnaire; infer the brief from the request and the codebase, state it, and let them correct it.

## The brief template

Keep it in your task notes (not in the repo) and show the filled version in your summary. Every line needs a one-line reason.

```text
Design read:   <page kind> for <audience>, <visual language>, <base system or aesthetic>
Audience/emotion: who uses it, what they should feel in the first five seconds, what they must be able to do
Dials:         design_variance N, motion_intensity N, visual_density N   (reason for each)
Style:         primary <style-id>; supporting <style-id or none>; avoid <conflicting styles>
Typography:    display <family>, text <family>, mono <family or none>; scale ratio; body size/leading; measure; weights
Colour:        bg / surface / text / muted / border / accent / state tokens, light and dark, rule for the accent
Layout:        grid, container width, hero composition, section layouts, mobile order
Spacing:       base unit, scale, section padding
Surfaces:      radius rule, border or shadow (one edge language), glass/grain/texture if any, image treatment
Motion:        easing, duration scale, which moments move and why, reduced-motion state
Interaction:   hover/focus/pressed/disabled, forms, navigation behaviour, touch alternatives
Don'ts:        3 to 6 specific things to avoid (from the tells list below)
Sources:       one catalog pattern id per borrowed idea, written as double-bracket links, with its reuse class
```

Fill it in this order. Each section constrains the next: emotion picks the style, the style narrows type and colour, type and colour
constrain layout, and motion comes last.

## Worked mini example

Request: "a landing page for a small ceramics studio that sells weekend workshops". Nothing else is specified.

```text
Design read:   conversion page for hobbyists booking a Saturday class; editorial with a warm, tactile finish; plain CSS
Audience/emotion: adults 30-60, often on phones; unhurried, handmade, trustworthy; must find dates and price in two scrolls
Dials:         variance 6 (distinctive but bookable), motion 3 (calm; images carry it), density 3 (one idea per screen)
Style:         primary [[style-editorial]]; supporting [[style-grain-and-texture]] at 4% on the hero only; avoid glass and neon
Typography:    display Newsreader (optical-size axis), text Public Sans; ratio 1.25; body 18/1.6; measure 62ch; weights 400/600
Colour:        paper #FAF8F4, ink #1B1A17, muted #5F5B53, accent #C2410C used for the primary action and links only
Layout:        12 columns, 7/5 asymmetric hero (headline left, photo right), 3 section layouts across 7 sections, one column under 768 px
Spacing:       4 px base, section padding clamp(4rem, 8vw, 8rem)
Surfaces:      radius 4 px, 1 px hairlines, no shadows; all photos graded to one warm profile, fixed aspect-ratio boxes
Motion:        one easing (cubic-bezier(0.16, 1, 0.3, 1)), 150/300/600 ms; photos fade and rise 12 px once; reduced motion shows final state
Interaction:   link underline offset grows on hover; 2 px accent focus ring, 2 px offset; booking form with visible labels
Don'ts:        no gradient blobs, no three-icon-card row, no placeholder testimonials, no serif on buttons or form labels
Sources:       fancy vertical-cut reveal is optional for the headline; [[fancy-vertical-cut-reveal]] (copy_with_attribution)
```

Why this works as a brief: every line is a decision someone can check in the result (does the accent appear anywhere else? are there 3
section layouts? does the page work with motion off?). Adjectives like "warm" were converted into a paper colour, a serif and a grain level.

## How the dials map to decisions

Defaults are 6 / 5 / 5. A user's wording moves a dial ("make it calmer" lowers `motion_intensity`); do not ask them to edit config.
The full per-band decision tables with starting values live in
[the dials recipe](../../../knowledge/implementation-recipes/art-direction-brief-from-dials.md); the dial definitions are
[[taste-skill-three-dials]]. Summary:

| Decision | Low (1-3) | Mid (4-7) | High (8-10) |
| --- | --- | --- | --- |
| Hero | centred or 50/50 | asymmetric split (about 7/5), offset heading | off-grid composition, overlaps, large voids |
| Type | one family, ratio 1.2 | display + text, ratio 1.333, one expressive moment | expressive display at 7-8x body, tight tracking, at most 2 families |
| Colour | neutrals + one accent | tinted neutrals + accent + one supporting tone | bold limited palette, still one accent role |
| Section layouts | 2-3, repetition accepted | 3-4 per 8 sections | 4+ per 8, none repeated back to back |
| Surfaces | flat, one radius | two levels, radius scale of 2-3 steps | layered materials with solid fallbacks, one radius rule |
| Motion | hover/focus only | reveals 300-600 ms, at most one scroll moment | scroll scenes and shared elements, each with a purpose |
| Density | one idea per screen, section padding 80-160 px | 2-3 columns, padding 64-96 px | 4+ per row, padding 24-48 px, dividers instead of cards |

Conflicts: high variance with high density, keep data regions at variance 5 or lower. High motion with high density, animate only state
changes. A page claiming `motion_intensity` 5 or more must visibly contain at least three motion moments, otherwise lower the dial.
`reduced_motion: static_first` means design the static layout first and treat motion as the enhancement. `webgl_enabled: false` or a low
`performance_budget` removes shader and 3D options from the style shortlist before you choose.

## Picking a style

1. Search, using the mood words and the product type, not framework names:
   `design-sensei search "calm editorial warm" --category design-style --scope patterns --limit 5`
2. Read the style note of the top two or three results. Each lists fit, poor fit, typography, colour, layout, motion, accessibility cautions and
   typical AI mistakes. Reject any style whose "poor fit" matches the product (for example glassmorphism for a text-heavy docs site).
3. Pick one primary style and at most one supporting influence from its "supporting influences that work" line. Never pair the
   opposites its note warns against.
4. Record the style as a double-bracket pattern link such as the ones in the table below. The style patterns are original guidance; their reuse class describes the cited upstream files, not
   the note. Check the class in search output before copying any code from those files (see [source usage](source-usage.md)).

| Brief signal | Start from | Typical supporting influence |
| --- | --- | --- |
| Publication, essay, case study, cultural institution | [[style-editorial]] ([note](../../../knowledge/design-styles/editorial.md)) | [[style-grain-and-texture]], [[style-minimalism]] |
| Technical docs, research, studio, many parallel items | [[style-swiss-international-typographic]] ([note](../../../knowledge/design-styles/swiss-international-typographic.md)) | [[style-minimalism]] |
| Focused tool, portfolio, one message | [[style-minimalism]] ([note](../../../knowledge/design-styles/minimalism.md)) | [[style-editorial]] |
| Software product with a real interface | [[style-product-led-saas]] ([note](../../../knowledge/design-styles/product-led-saas.md)) | [[style-bento-layouts]] |
| Developer tool, observability, API docs | [[style-dark-technical-developer-tools]] ([note](../../../knowledge/design-styles/dark-technical-developer-tools.md)) | [[style-bento-layouts]] |
| Feature overview of several equal ideas | [[style-bento-layouts]] ([note](../../../knowledge/design-styles/bento-layouts.md)) | [[style-product-led-saas]] |
| Atmospheric hero over rich colour | [[style-aurora-gradient-mesh]] ([note](../../../knowledge/design-styles/aurora-gradient-mesh.md)) | [[style-grain-and-texture]] |
| Overlays above imagery or gradients | [[style-glassmorphism]] ([note](../../../knowledge/design-styles/glassmorphism.md)) | [[style-aurora-gradient-mesh]] |
| Type-led brand moment or campaign | [[style-kinetic-typography]] ([note](../../../knowledge/design-styles/kinetic-typography.md)) | [[style-editorial]] |
| Scroll-driven narrative | [[style-motion-led-storytelling]] | [[style-editorial]] |
| Luxury, fashion, restraint | [[style-high-fashion-luxury]] | [[style-editorial]] |

The full list of 40 styles with group, summary and pairings is [the style index](../../../knowledge/design-styles/README.md). Use it when
nothing in the table fits. If the brief names a design system (Material, shadcn, a company system), that is the style; one system per project.

## Brief to implementation

- Write the tokens (colour, type, spacing, radius, timing) before components. If the project has no token file, offer a `DESIGN.md`
  ([[design-md-spec]], [format note](../../../knowledge/design-intelligence/design-md-format.md)); do not create one unasked.
- Re-read the brief after each layer (tokens, type, layout, surfaces, motion). If a decision stopped fitting its dial band, change the dial or the
  decision deliberately, not just the CSS.
- Then continue with [design principles](design-principles.md), [typography](typography.md), [colour](color-systems.md) and
  [layout](layout-composition.md) for the concrete values, and [motion design](motion-design.md) for step 7.

## Generic-AI-tells checklist

Treat each as a default to override with a reason, not a ban. Source of the idea: [[taste-skill-anti-generic-ui-checklist]]
([note](../../../knowledge/design-intelligence/taste-skill.md)); the numbers below are Design Sensei's, not upstream rules.

- [ ] One typeface for everything, usually Inter at default sizes, with no display/text contrast
- [ ] Indigo-to-violet-to-pink gradient, or three blurred blobs behind a centred headline
- [ ] Centred hero, then exactly three identical icon cards, then a testimonial strip
- [ ] Glass, glow or shadow on every container, so nothing stands out
- [ ] More than one accent colour, or the accent used for decoration as well as action
- [ ] Hierarchy made from size alone; secondary text in a pale grey that fails 4.5:1
- [ ] Invented content: round numbers ("10x"), stock names, logos of companies that do not exist, `div` rectangles posing as a dashboard screenshot
- [ ] Section eyebrows, numbered labels and scroll cues added as ornament with no structural job
- [ ] Every heading wrapped in the same fade-up reveal; infinite loops that never pause
- [ ] Several radius values with no rule; the same section layout repeated back to back
- [ ] Effects chosen because they impress (WebGL, parallax) rather than because the message needs them

If you recognise your direction as the default, change one major decision (type pairing, layout archetype or colour logic) on purpose, then re-check
that the change serves the audience.

## Checklist before saying done

- [ ] Brief written with a reason per line and shown in the result summary
- [ ] Dials stated and honoured (motion claimed means motion shown; low density means real whitespace)
- [ ] One primary style, at most one supporting influence, every borrowed idea linked to a pattern id and reuse class
- [ ] Tokens exist for colour, type, spacing, radius and timing; components read them
- [ ] No more than one accent role; one radius rule; one edge language (border or shadow, not both at full strength)
- [ ] Brief survives the squint test: blur the screenshot, the hierarchy and the primary action are still obvious
- [ ] Reduced-motion and no-WebGL states exist for every effect the brief includes

## Common mistakes

- Picking a style from a screenshot or a trend and ignoring its "poor fit" line.
- Describing the brief in adjectives ("clean, modern, premium") that nobody can verify.
- Combining three or more styles, or two that conflict (minimalism with maximalism, glass with brutalism).
- Writing the brief and then never reading it again while coding.
- Letting the dial defaults drive the design when the product is a dashboard (variance 3, density 8 fits better) or a campaign microsite (variance 8-9).
- Treating the tells list as law and swapping one cliche for another; the aim is a reason for each decision.

## Related

Patterns: [[taste-skill-three-dials]], [[taste-skill-redesign-audit-protocol]] (redesigns), [[taste-skill-image-to-code-workflow]] (optional, needs an
image generator), [[design-md-spec]], [[astryx-theme-presets]] (worked examples of complete theme personalities).
Notes: [dials recipe](../../../knowledge/implementation-recipes/art-direction-brief-from-dials.md),
[taste-skill note](../../../knowledge/design-intelligence/taste-skill.md), [write a DESIGN.md](../../../knowledge/implementation-recipes/write-a-design-md.md),
[Astryx themes and tokens](../../../knowledge/components/astryx-themes-and-tokens.md).
References: [design-principles.md](design-principles.md), [typography.md](typography.md), [color-systems.md](color-systems.md),
[layout-composition.md](layout-composition.md), [motion-design.md](motion-design.md), [design-qa.md](design-qa.md).
