# Knowledge base

Project-authored notes about design styles, upstream libraries and implementation recipes. Original writing; upstream code is described and cited by path (`` `source-id:path` ``), never copied beyond short quotations from permissively licensed sources.

| Folder | Contents |
| --- | --- |
| [design-styles/](design-styles/README.md) | 28 style notes: characteristics, fit, typography, color, motion, mistakes, how to build |
| [design-intelligence/](design-intelligence/) | taste-skill, the DESIGN.md format, the Opus videos prompt collection |
| [components/](components/) | component libraries and 3D tooling: what they are, how they are consumed, notable components, pitfalls |
| [shaders/](shaders/) | liquid metal, liquid glass, shader gradients, GLSL fundamentals for UI |
| [animations/](animations/) | Lenis, GSAP, scroll storytelling, motion principles, R3F animation |
| [website-references/](website-references/) | reference-only sites: what is known, terms stance |
| [implementation-recipes/](implementation-recipes/) | step-by-step recipes with original code and verification checklists |
| [pattern-index/](pattern-index/README.md) | generated, browsable views of the pattern catalog |

Every note has front matter (`title`, `kind`, `summary`, `source_ids`, `pattern_ids`, `updated`) validated by `design-sensei catalog validate`, and every cited file path is checked against the pinned upstream commit when the source is downloaded. Search: `design-sensei search "<words>" --scope docs`. Formats: [../docs/contributing.md](../docs/contributing.md).
