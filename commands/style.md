---
description: Compare 2-3 design style options for given mood words
argument-hint: "[mood words, e.g. calm editorial warm]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei recommend *)
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei search *)
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei read *)
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei config show *)
---

Mood words: $ARGUMENTS

If the mood words above are empty, take them from the conversation or the project (product type, audience, an existing brief). If there is nothing to go on, ask for three mood words and stop.

This is the style-selection part of step 2 of the `design-sensei` skill. Present options and a recommendation; do not write code or files.

In this file `design-sensei` means `${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei` (quote the path if it contains spaces).

1. **Settings that prune the shortlist.** Run `design-sensei config show --project .`. If `webgl_enabled` is false or the performance budget is tight, drop shader and 3D styles; if `reduced_motion` is `static_first`, prefer styles that work without motion.
2. **Find candidates.** The `recommend` subcommand may not exist in every version, so test for it first with `design-sensei recommend --help`.
   - If it succeeds, run `design-sensei recommend "<mood words>" --project .` (add `--framework`, `--max-gpu` or `--no-webgl` when the project settings call for it). Use its STYLE section as the baseline: the primary and supporting style, the "pairs well with / avoid" hints and the project filters it applied. Ignore its PATTERNS list here; that belongs to implementation.
   - Then, with or without `recommend`, run `design-sensei search "<mood words>" --category design-style --scope patterns --limit 6` to get the alternatives you need for a comparison of two or three options. If `recommend --help` fails, this search is the only source of candidates.
   - If the results are thin, retry once with synonyms or the product type; `design-sensei search --facets` lists the vocabulary.
3. **Read the style notes.** Run `design-sensei read <style-slug>` (quick card) for the top three or four results; use `--section` for any part you need in full. Each note lists fit, poor fit, typography, colour, layout, motion, accessibility cautions and typical AI mistakes. Reject any style whose poor fit matches the product. If nothing fits, use the style index at `${CLAUDE_PLUGIN_ROOT}/knowledge/design-styles/README.md` and the signal table in `${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/references/art-direction.md` (section "Picking a style").
4. **Present 2 or 3 options**, one block each: style name and pattern id; why it fits these mood words; poor fit and cautions for this product; pairings (the one supporting influence that works, and what never to combine it with); the typography, colour and motion consequences in one line each; reuse class and source ids from the search output (the style notes are original guidance, but code in cited upstream files follows its source's reuse class).
5. **Recommend one** primary style and at most one supporting influence, with a reason tied to the mood words and the project. Say what you would change in the default if it looks generic.
6. **End with a question**: which option to take into `/design-sensei:brief`, or what to adjust. Do not choose for the user beyond the recommendation.
