---
title: "Taste Skill: anti-generic UI skills and dials"
kind: guide
summary: "Guide to the taste-skill repository: its 13 agent skills, the three 1-10 dials (variance, motion, density), the rules it imposes on generated UI, its LLM-laziness research folder, its limits, and how Design Sensei uses it as inspiration rather than a dependency."
source_ids: [taste-skill]
pattern_ids: [taste-skill-three-dials, taste-skill-anti-generic-ui-checklist, taste-skill-image-to-code-workflow, taste-skill-redesign-audit-protocol]
updated: "2026-10-09"
---

# Taste Skill

## What it is

Taste Skill is a set of portable agent skills by Leonxlnx. Each skill is a Markdown file (`SKILL.md`) that tells a coding
agent how to avoid the generic look of AI-built interfaces. It is not a runtime library: nothing is added to the app. This
note was written against the pinned commit `18dfc92` (2026-10-08). The default skill is labelled "v2 (experimental)"; the
changelog says install name, dial names and section structure are only promised to stabilise at v2.0.0
(`taste-skill:CHANGELOG.md`). Upstream documents `npx skills add <repo-url>` (all skills) or `--skill "<install name>"`
(one skill), or copying a `SKILL.md` by hand (`taste-skill:README.md`). Design Sensei runs none of this.

## Repository map

| Path | Contents |
| --- | --- |
| `taste-skill:README.md` | install commands, skill table, three-dial summary, sponsor and product promotion |
| `taste-skill:CHANGELOG.md` | v1 to v2 differences and the stated reasons |
| `taste-skill:skills/` | 13 skill folders (next section) and `taste-skill:skills/llms.txt`, one line per skill |
| `taste-skill:skill.sh` | shell lookup table from skill name to `SKILL.md` path (read only, never executed here) |
| `taste-skill:.claude-plugin/plugin.json` | Claude Code plugin manifest (name `taste-skill`, version 1.0.0, MIT); `marketplace.json` lists the same plugin |
| `taste-skill:.github/copilot-instructions.md` | an 11-line "anti-slop" manifesto for GitHub Copilot |
| `taste-skill:research/` | background research on why LLMs truncate output (see below) |
| `taste-skill:examples/` | three screenshots of one sample page, a florist landing page called Floria |
| `taste-skill:assets/` | README banners and logos; `taste-skill:assets/sponsors/` holds third-party sponsor logos |
| `taste-skill:scripts/` | four Node scripts that process README images with sharp; unrelated to the skills |

## Skills shipped (13, verified against each front matter)

Implementation skills write code:

| Folder | Install name | What it is for | Dials |
| --- | --- | --- | --- |
| `taste-skill:skills/taste-skill/SKILL.md` | `design-taste-frontend` | Default v2. Infer the brief into a one-line "design read", set three dials, pick a real design system or label an aesthetic honestly, apply hard rules, finish with a 62-box pre-flight list. 1,206 lines. Scope: landing pages, portfolios, redesigns | three, baseline 8/6/4 |
| `taste-skill:skills/taste-skill-v1/SKILL.md` | `design-taste-frontend-v1` | The original, kept for exact backward compatibility; shorter (226 lines) and includes a "motion-engine bento" section | the same three |
| `taste-skill:skills/gpt-tasteskill/SKILL.md` | `gpt-taste` | Stricter variant for GPT/Codex: the model simulates a seeded random pick of hero, type stack, components and GSAP paradigms in a `<design_plan>`, AIDA page structure, 2-3 line hero headline, gapless bento, mandatory GSAP motion | none |
| `taste-skill:skills/image-to-code-skill/SKILL.md` | `image-to-code` | Image first: generate section reference images, analyse them in detail, then implement to match. 1,228 lines | nine of its own |
| `taste-skill:skills/redesign-skill/SKILL.md` | `redesign-existing-projects` | Existing code: scan, diagnose with an audit list, fix in priority order without changing the stack | none |
| `taste-skill:skills/soft-skill/SKILL.md` | `high-end-visual-design` | "Expensive" look: banned defaults, pick one vibe and one layout archetype, nested double-bezel cards, custom spring-like easing | none |
| `taste-skill:skills/minimalist-skill/SKILL.md` | `minimalist-ui` | Editorial utilitarian look: warm monochrome with named hex values, serif/sans/mono roles, flat bento, muted pastel tags | none |
| `taste-skill:skills/brutalist-skill/SKILL.md` | `industrial-brutalist-ui` | Choose one of two archetypes (Swiss industrial print, light; tactical terminal, dark): extreme type scale, rigid grid, zero radius, halftone and scanline effects. Marked Beta in `llms.txt` | none |
| `taste-skill:skills/stitch-skill/SKILL.md` | `stitch-design-taste` | Generates a prose-style `DESIGN.md` for Google Stitch; `taste-skill:skills/stitch-skill/DESIGN.md` is a finished example | four (Creativity 8, Density 4, Variance 8, Motion Intent 6) |
| `taste-skill:skills/output-skill/SKILL.md` | `full-output-enforcement` | Not visual: forbids placeholder comments and truncated answers, defines a pause marker for token-limit splits | none |

The Stitch `DESIGN.md` is not the Google Labs format covered in `knowledge/design-intelligence/design-md-format.md`: it has
numbered prose sections and no YAML tokens.

Image-generation skills output reference images only, never code:

| Folder | Install name | What it is for | Dials |
| --- | --- | --- | --- |
| `taste-skill:skills/imagegen-frontend-web/SKILL.md` | `imagegen-frontend-web` | One separate horizontal comp per page section (default 6 for a landing page, 8 for a full site), hero composition bias away from left-text/right-image | eight |
| `taste-skill:skills/imagegen-frontend-mobile/SKILL.md` | `imagegen-frontend-mobile` | Mobile screen sets and flows, platform mode, phone-mockup rules | nineteen |
| `taste-skill:skills/brandkit/SKILL.md` | `brandkit` | Brand-kit boards: strategy first, 3 x 3 panel grid, five logo-concept methods, eight visual modes | none |

## The dials

The default skill defines three integer dials from 1 to 10, set by the agent from the brief and overridden in conversation
(the file says not to ask the user to edit it). Exact text of the definition (`taste-skill:skills/taste-skill/SKILL.md`, section 1):

> * **`DESIGN_VARIANCE: 8`** - 1 = Perfect Symmetry, 10 = Artsy Chaos
> * **`MOTION_INTENSITY: 6`** - 1 = Static, 10 = Cinematic / Physics
> * **`VISUAL_DENSITY: 4`** - 1 = Art Gallery / Airy, 10 = Cockpit / Packed Data

Section 7 gives the band meanings (paraphrased):

| Dial | 1-3 | 4-7 | 8-10 |
| --- | --- | --- | --- |
| `DESIGN_VARIANCE` | symmetric 12-column grid, equal paddings, centred | offset overlaps, mixed image ratios, left-aligned headers over centred data | masonry, fractional grids such as 2fr 1fr 1fr, very large empty zones |
| `MOTION_INTENSITY` | no automatic animation, hover and active only | CSS transitions with an ease-out curve, delay cascades on load | scroll-triggered reveals, parallax, scroll-driven animation; never window scroll listeners |
| `VISUAL_DENSITY` | huge section gaps (py-32 to py-48) | standard app spacing (py-16 to py-24) | tight padding, no card boxes, 1px dividers, monospace numbers |

Other rules are gated by thresholds: centred hero avoided above variance 4; no generic cards above density 7; reduced motion
mandatory above motion 3; the page must really animate above motion 4 ("motion claimed, motion shown", otherwise lower the
dial to 3); magnetic and perpetual micro-interactions only above motion 5; asymmetric layouts for variance 4-10 collapse to
one column under 768px. Section 1.A maps brief signals to dials (calm or editorial: 5-6 / 3-4 / 2-3; playful or agency:
9-10 / 8-10 / 3-4; trust-first public sector: 3-4 / 2-3 / 4-5; redesign: relative to the existing site) and section 1.B lists
use-case presets.

Sibling skills define their own dial families, all in section 1 of each file: `image-to-code` (DESIGN_VARIANCE,
VISUAL_DENSITY, ART_DIRECTION, IMPLEMENTATION_CLARITY, IMAGE_USAGE_PRIORITY, SPACING_GENEROSITY, ANALYSIS_PRECISION,
IMAGE_GENERATION_EAGERNESS, UI_SIMPLICITY_DISCIPLINE); `imagegen-frontend-web` (the same first six names plus
LAYOUT_VARIATION and CONVERSION_DISCIPLINE; eight in all); `imagegen-frontend-mobile` (19, including PLATFORM_AWARENESS,
FLOW_VARIETY, TEXTURE_STRENGTH and MIN_TEXT_SIZE_DISCIPLINE); the Stitch `DESIGN.md` uses a four-dial table with different names.

## Rules the default skill imposes (paraphrased, with section numbers)

- **Process (0, 2):** read page kind, vibe words, references, audience, brand assets and quiet constraints (accessibility,
  regulation) first; state a one-line design read; ask at most one question; avoid the usual LLM defaults (purple gradient,
  centred hero on dark mesh, three equal cards, glass everywhere, endless loops). Brief names a design system (Material,
  Fluent, Carbon, Polaris, Primer, GOV.UK, USWDS, Radix, shadcn...)? Use the official package, one system per project. Brief
  names an aesthetic? Build with web standards and say so; Apple Liquid Glass has no official web package, call it an approximation.
- **Stack (3):** React or Next.js with server components, interactive code in small client leaves; Tailwind v4; Motion
  (`motion/react`); `next/font` or self-hosted fonts; verify `package.json` before importing anything; Phosphor, HugeIcons,
  Radix or Tabler icons (Lucide discouraged, no hand-drawn SVG icons); `min-h-[100dvh]`, CSS Grid, no React state for
  continuous input.
- **Typography (4.1):** tight display tracking, body near 65ch; Inter and serif faces are discouraged as defaults, with
  explicit override paths; Fraunces and Instrument Serif named as banned defaults; emphasise within one family; italic
  descender clearance.
- **Colour (4.2, 8):** one accent below 80% saturation, one neutral family, accent locked page-wide; avoid the AI purple glow
  and the beige/brass/espresso palette for premium-consumer briefs; no pure black or white.
- **Layout (4.3-4.7, 4.11):** hero fits the viewport (headline at most two lines, about 20 words of subtext, at most four text
  elements); one-line navigation at most 80px; at most one eyebrow label per three sections; no split headline/paragraph
  headers, at most two consecutive zigzag sections, four layout families per eight sections, bento cells equal to items,
  one radius system, one page theme.
- **Content and imagery (4.8-4.10, 9):** copy self-audit; realistic names and numbers; no div-built fake screenshots; images
  from a generation tool first, Picsum seed URLs second, labelled placeholders last; real SVG logos; a long "AI tells" ban
  list (section-number eyebrows, version labels, scroll cues, decorative dots, locale strips) and a total em-dash ban.
- **Motion and performance (5, 6):** every animation must be motivated; one marquee per page; no scroll listeners; GSAP
  sticky-stack and horizontal-pan skeletons (start `top top`, `pin: true`); transform and opacity only; reduced motion above
  dial 3; LCP under 2.5 s, INP under 200 ms, CLS under 0.1; dark mode designed in.
- **Redesign (11):** detect greenfield, preserve or overhaul; audit before touching; never change URLs, nav labels, form
  field names, logo or legal copy silently; apply levers in order (type, spacing, colour, motion, hero, blocks).

Section 10 names 50 effects in eight groups (hero paradigms, navigation, layouts, cards, scroll animations, galleries, type,
micro-interactions). Section 12 specifies a `blocks/` library contract, but no such folder exists at the pinned commit.

## Research folder

`taste-skill:research/README.md` lists one topic, `laziness/` (`taste-skill:research/laziness/README.md`): eleven Markdown files in
three subfolders on why models emit placeholders and truncated answers. Four root-cause notes
(`taste-skill:research/laziness/root-causes/rlhf-and-compute.md` and three more), four remedies (parameter tuning, prompt
engineering, lazy-loaded skills and MCP, and ready-made prompts in `taste-skill:research/laziness/remediation/reference-prompts.md`),
and two findings notes. It is about output completeness, not visual design, and overlaps in subject with
`full-output-enforcement`. It names studies without links and quotes percentages (for example prompt-stimulus gains) that were
not verified here; treat it as background reading.

## Strengths and limits

Strengths: concrete, checkable rules (counts, limits, thresholds); an explicit override path on many rules; a design-read step before
styling; a redesign protocol; honesty about what is official (Liquid Glass); a pre-flight list that can be used as a review rubric.

Limits:
- No evaluation data ships with the repo; "tells" and improvement claims are the authors' observations.
- Rules are absolute in tone (zero em-dashes, banned fonts) and can fight a real brand; sibling skills contradict each other
  (v2 avoids a centred hero above variance 4, `gpt-taste` prefers a centred cinematic hero; v1 bans Inter, v2 only discourages it;
  the Stitch skill suggests Fraunces and Instrument Serif, which v2 bans as defaults). Pick one skill, do not stack them.
- Marketing-page scope: section 13 excludes dashboards, data tables, multi-step forms, code editors, native mobile.
- Length: the default skill is 1,206 lines, expensive to load whole. The v2 skill is pre-release.
- The Floria screenshots show an uppercase eyebrow pill and numbered process markers, which v2 discourages; the README does not
  say which version produced them.

## How Design Sensei should use it

Treat it as inspiration, not a dependency: never required, never vendored, never executed. Concretely:

| Idea | Design Sensei treatment |
| --- | --- |
| Design read before code | one line in the art-direction brief |
| Three dials | `design_variance`, `motion_intensity`, `visual_density` (defaults 6 / 5 / 5, not 8 / 6 / 4), turned into decisions by `knowledge/implementation-recipes/art-direction-brief-from-dials.md` |
| Anti-generic rules | an evaluation rubric; each rule is a default with an override, never a hard ban |
| Redesign protocol | the inspect step when a codebase exists |
| Image-first workflow | optional, only when an image generator is available |

## Licence and attribution

MIT, "Copyright (c) 2026 Leonxlnx" (`taste-skill:LICENSE`); catalog attribution: "Taste Skill by Leonxlnx
(https://github.com/Leonxlnx/taste-skill)". The licence covers the text and code. The logos in `taste-skill:assets/sponsors/`
belong to their sponsors, and the README banners are the project's branding: do not reuse either. This note paraphrases and
quotes three lines; it copies no rule text.
