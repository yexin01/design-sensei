---
description: Review current UI work against the design QA rubric
argument-hint: "[project dir, file or URL; default is the current project]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Task
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei eval *)
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei search *)
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei sources show *)
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei config show *)
---

Review target: $ARGUMENTS

If the target above is empty, review the project in the current directory and the UI work done in this conversation. A URL means a running site to inspect in the browser; a path means source to evaluate.

This is step 5 of the `design-sensei` skill. Follow the protocol in `${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/references/design-qa.md` (rubric, run order, browser procedure, report template). This command reviews; it does not edit project files. Offer fixes at the end instead of applying them.

In this file `design-sensei` means `${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei` (quote the path if it contains spaces).

1. **Settings and brief.** Run `design-sensei config show --project .`. Find the art-direction brief (earlier in this conversation, `DESIGN.md`, or the project's tokens); the review is measured against it. If no brief exists, say so and judge against the generic-tells list only.
2. **Project checks.** Run the project's own build, type-check, lint and test scripts from `package.json` (or the equivalent). Quote exit codes and the tail of failing output.
3. **Static check.** Run `design-sensei eval <project-dir> --verbose`. It is a heuristic linter over source text; a clean run is not a pass.
4. **Browser evidence.** If a browser tool exists (Playwright MCP, Chrome DevTools MCP, a headless-browser skill), start the app with the project's dev command and collect, saving screenshots outside the repository (scratch directory):
   - screenshots at 375, 768, 1280 and 1920 px, plus `scrollWidth` versus `clientWidth` at each width;
   - console errors and non-2xx network requests;
   - `prefers-reduced-motion: reduce` emulated (reload, then toggle live once);
   - a keyboard walk from the top with real Tab presses, noting focus visibility, order and traps;
   - contrast measured from computed colours, not by eye;
   - a Lighthouse or performance trace if the tool offers one (label numbers as lab).
   If no browser tool exists, say so in the first line of the report and list every check you could not run; never describe how the result "looks".
5. **Delegate the scoring pass** to the `design-reviewer` agent (Task tool, `subagent_type: design-reviewer`; if it is not found under that name, use the namespaced `design-sensei:design-reviewer`). Give it an evidence bundle in the prompt: the target and project root, the effective config, the brief, the build and test results, the full `eval` output, the screenshot file paths and measurements from step 4, the list of checks that could not be run, and the CLI path `${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei`. It cannot open a browser; it can Read the screenshot files you saved.
6. **Report.** Relay the agent's structured report: scores table (pass, concern, fail, not verified per category, with evidence), prioritised fixes (blockers first: accessibility, responsive behaviour, technical correctness), licence or provenance problems, and what was not verified. Use no superlatives and no total score; describe differences against the brief. End by asking which fixes to apply.
