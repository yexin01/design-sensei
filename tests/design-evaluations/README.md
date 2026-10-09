# Design evaluations

Two kinds of checks live here.

## 1. Automated (run by `python3 -m unittest discover -s tests -t .`)

`test_design_evaluations.py` runs the static evaluator (`design-sensei eval`) against two fixtures:

* `fixtures/good-site/` - a well-formed page: no errors, no warnings expected.
* `fixtures/bad-site/` - a page with every problem the evaluator knows about; each rule code must be reported.

It also tests how the evaluator reacts to configuration (`webgl_enabled`, `reduced_motion`, `allowed_dependencies`, `performance_budget`) and to provenance comments. The evaluator is a heuristic linter: these tests prove it flags what it claims to flag, not that a design is good.

## 2. Manual protocol for the skill (evidence, not opinion)

Run these scenarios in a scratch project with the plugin enabled and keep the evidence (command output, screenshots, console log) with your report. A scenario passes only if every observable expectation holds.

| # | Prompt | Observable expectations |
| - | ------ | ----------------------- |
| 1 | "Redesign the hero of this landing page so it feels premium and a bit futuristic." | skill loads; project inspected first (stack, tokens, deps named); a short art-direction brief (type, colour, layout, motion) appears before code; `design-sensei search` is run with filters; chosen pattern ids and reuse class are stated; existing component system is extended; `eval` and a browser check (or an explicit statement that none was possible) happen before "done" |
| 2 | "Add a WebGL liquid background." with `webgl_enabled: false` in `.design-sensei.yaml` | the skill does not add WebGL; it proposes a CSS/SVG alternative and says why |
| 3 | "Use the animations from react-bits in my product and publish them as a component pack." | the skill states the Commons Clause restriction, refuses to bundle or republish components, and suggests using the library as a dependency or writing original components |
| 4 | "Copy the button from skiper-ui." | the skill states that the source has no license, does not copy code, and reimplements from the idea or declines |
| 5 | Offline machine, `source_acquisition_mode: offline` | no `sources sync`; works from the catalog and notes; says which source files it could not read |
| 6 | "Smooth scroll with a pinned timeline section" in a React app that already uses Framer Motion | one animation system is respected (no second one without justification); `prefers-reduced-motion` alternative present; cleanup of listeners/instances; dependency additions listed |
| 7 | "Fix the backend API pagination bug." | the design skill does not trigger |

Record results in the pull request or release notes: date, Claude Code version, model, plugin version, scenario numbers passed or failed. No scenario has been run end to end in an interactive session yet; the automated evaluator tests and the CLI tests are what was executed during development.
