# Trigger eval results

Measured 2026-10-09 with skill-creator's description-optimization loop (`run_loop.py`), Claude Code 2.1.295,
model `claude-sonnet-5-5`. Queries are in `trigger-queries.json` (12 should trigger, 12 near-misses that should not).
How to re-run: `README.md`.

## Summary

| | Baseline (original description) | Final (chosen description) |
| --- | --- | --- |
| Train queries passed (16, 8 positive and 8 negative) | 12/16 | 16/16 |
| Held-out test queries passed (8, 4 positive and 4 negative) | 5/8 | 6/8 |
| All 24 queries passed | 17/24 | 22/24 |
| Should-trigger runs that triggered (36 runs) | 13/36 (36%) | 29/36 (81%) |
| Should-not-trigger runs that triggered (36 runs) | 0/36 (0%) | 0/36 (0%) |
| Held-out should-trigger runs that triggered (12 runs) | 3/12 (25%) | 5/12 (42%) |

A query passes when its trigger rate over 3 runs is at least 0.5 (positives) or below 0.5 (negatives).
A "trigger" means the model called the injected skill during its first assistant turn.

Reading the numbers:

- The original description almost never triggered on concrete implementation requests that name an effect or a library
  (route transitions, shader background, 3D product viewer, Lenis/GSAP scrolling): 0/3 on all four. In those runs the model
  started with `Bash`/`Read` to look at the project and never called any skill. A follow-up check that allowed three
  assistant turns found 0/14 runs on the seven failing positives, so the miss is "never", not "later".
- The rewritten description fixes that class (all eight train positives now 3/3) and adds no false triggers. The gain on the
  held-out half is smaller (one more query passed, kinetic typography 0/3 to 2/3), and eight test queries is too few to call
  that statistically solid. The train score is also flattered because the optimizer saw the train failures and the new text
  names several of those effects.
- Still failing, both in the held-out half: a design-direction request with no technology named ("what visual style should
  we go for ... then build the home page", answered in plain text without any skill), and "polish the visual design of our
  analytics dashboard" (the built-in `dataviz` skill or plain exploration wins). These are the next candidates for a
  description change, but tuning on them now would contaminate the held-out set; add fresh queries first.

## Iteration table

The loop stopped after one improvement because every train query passed (`all_passed (iteration 2)`); the best iteration
is chosen by held-out test score, ties going to the earlier one.

| Iter | Description | Train queries | Test queries | Train runs correct | Test runs correct |
| --- | --- | --- | --- | --- | --- |
| 1 (baseline) | original | 12/16 | 5/8 | 34/48 (recall 42%, precision 100%) | 15/24 (recall 25%, precision 100%) |
| 2 (chosen) | rewritten by the optimizer, kept verbatim | 16/16 | 6/8 | 48/48 | 17/24 (recall 42%, precision 100%) |

Check of the final description over all 24 queries, 2 runs each, allowing the first three assistant turns: 22/24 queries
passed, 20/24 positive runs triggered, 0/24 negative runs triggered (same two failures as above).

## Descriptions

Before (614 characters):

> Design intelligence for building distinctive, production-quality interfaces. Use when asked to design, redesign, polish or art-direct a website, landing page, app UI or component, or to add animation, scroll storytelling, shaders, WebGL or 3D scenes, liquid glass, animated gradients, kinetic typography or other advanced visual effects. Runs an inspect, art-direct, search, implement, verify workflow backed by a local catalog of design styles and implementation patterns that point to real open-source code (React Three Fiber, GSAP, Lenis, shader and component libraries), with licence guidance for every source.

After (984 characters, limit 1024):

> Use this skill whenever the task is to make a web interface look, feel or move better, especially anything involving motion or graphics code. Trigger for: designing, redesigning or art-directing a site, landing page, dashboard or component so it feels distinctive rather than templated; and for implementing visual or interactive effects such as page and route transitions, shared-element morphs, GSAP/ScrollTrigger and Lenis smooth scrolling, parallax and pinned scroll sections, animated shader or gradient backgrounds, WebGL, Three.js / React Three Fiber scenes, 3D product viewers (GLB models, orbit controls, lighting), liquid glass, cursor effects and kinetic typography. Includes performance-conscious tuning of these effects on mobile. Provides an inspect, art-direct, search, implement, verify workflow with a catalog of styles and open-source code patterns, plus licence guidance. Skip for backend, tests, copywriting, non-visual refactors and generic performance debugging.

## Per-query results

| Split | Should trigger | Baseline (of 3) | Final (of 3) | Final, 3-turn window (of 2) | Query |
| --- | --- | --- | --- | --- | --- |
| train | yes | 3 | 3 | 2 | portfolio hero feels flat n boring. wanna add a webgl water ripple distortion on the... |
| train | yes | 2 | 3 | 2 | this dashboard looks like every shadcn template ever lol. can u make it look less gen... |
| train | yes | 0 | 3 | 2 | add route transitions to my next app router site - like a curtain wipe or a shared el... |
| train | yes | 0 | 3 | 2 | put an animated shader behind the hero in index.html, something like a slow aurora /... |
| train | yes | 0 | 3 | 2 | need a 3d product viewer for our headphones. glb is at public/models/cans.glb, we use... |
| train | yes | 2 | 3 | 2 | our marketing site at src/app/(marketing)/page.tsx looks like every other b2b saas te... |
| train | yes | 0 | 3 | 2 | add smooth scrolling w/ lenis to the about page and a gsap scrolltrigger pinned secti... |
| train | yes | 3 | 3 | 2 | we're building a scroll-driven page for our annual impact report. sections fade in, b... |
| train | no | 0 | 0 | 0 | our next.js app has a 4.8s LCP on the product page. bundle analyzer shows moment.js a... |
| train | no | 0 | 0 | 0 | write a README for packages/tokens (our design tokens package) - how to install it, h... |
| train | no | 0 | 0 | 0 | jest test for the useDebounce hook in src/hooks/useDebounce.test.ts is flaky, fails l... |
| train | no | 0 | 0 | 0 | refactor utils/geo.py - it has a pile of module level globals. turn it into a class w... |
| train | no | 0 | 0 | 0 | the submit button in components/CheckoutModal.vue is unclickable on iphone, pretty su... |
| train | no | 0 | 0 | 0 | i have ~40 icons in a figma file. whats the best way to export them as optimized svgs... |
| train | no | 0 | 0 | 0 | rewrite the headline and subhead on the pricing page, they sound too corporate: 'Ente... |
| train | no | 0 | 0 | 0 | add pagination and rate limiting to GET /api/orders in services/orders/handler.ts. ex... |
| test | yes | 0 | 0 | 0 | polish the visual design of our analytics dashboard - spacing is inconsistent, hierar... |
| test | yes | 0 | 2 | 2 | make the homepage headline do a kinetic type thing - letters split and stagger in on... |
| test | yes | 3 | 3 | 2 | i want the sticky navbar to have that apple liquid glass look, refraction + blur, sit... |
| test | yes | 0 | 0 | 0 | launching a site for a small natural wine bar in lisbon (3 people, tiny budget). what... |
| test | no | 0 | 0 | 0 | audit the alt text, link text and error message wording in content/en/*.json for scre... |
| test | no | 0 | 0 | 0 | can you explain how gsap scrolltrigger actually works under the hood? like what does... |
| test | no | 0 | 0 | 0 | the airflow dag dags/clickstream_daily.py that loads events into bigquery is double c... |
| test | no | 0 | 0 | 0 | my three.js + cannon-es physics sim leaks memory, the heap grows every time I reset t... |

## Method and caveats

- **CLI**: `claude` 2.1.295 from the VS Code extension (`~/.vscode/extensions/anthropic.claude-code-2.1.295-darwin-arm64`),
  put on `PATH` through a wrapper in the session scratch directory; no user configuration was changed.
- **Environment**: nested sessions ran with `--setting-sources project,local --no-session-persistence` (no user plugins,
  hooks or MCP servers; 22 built-in skills) from a scratch project directory outside the repository. Four real competing
  design skills were added as name-and-description stubs (`frontend-design`, `impeccable`, `ui-ux-pro-max`,
  `design-consultation`) so the description competes with realistic alternatives. Results will differ in an environment
  with more or fewer skills; the built-in `dataviz` skill was also in play.
- **Local harness patch** (`run_eval-local-patch.diff`): (1) each run gets its own project directory, because with
  parallel workers sharing one commands directory a session sees every sibling's identical copy and may call a sibling's, which
  the stock check scores as a miss (seen in a smoke test: one run called a sibling's copy and was counted as a miss); (2) a run
  counts as triggered when the injected skill is called anywhere in the first assistant turn, not only when it is the first
  tool call (the model often emits `Bash ls` and `Skill` in parallel). With the stock "first tool call" rule the same
  runs score 10/36 (baseline) and 26/36 (final) on positives.
- **Limits**: the scratch project is empty, so prompts that mention file paths lead the model to explore first; queries
  were written by us, not sampled from real traffic; the description optimizer and the model under test are the same model; single
  split (seed 42), three runs per query.
- **Cost**: 244 `claude` CLI invocations in total: 37 for set-up and smoke tests, 144 for the two evaluations in the loop
  (24 queries x 3 runs x 2 iterations), 1 for the description-improvement call, 14 for the three-turn check of the
  original description, and 48 for the three-turn check of the final one. Roughly 30K tokens of context per call
  (about 3 cents each when cached); the whole session is on the order of 10 USD at list price (estimate, not metered).
