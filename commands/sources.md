---
description: Show downloaded upstream sources and their licence class
argument-hint: "[source id, optional]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei sources list *)
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei sources status *)
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei sources show *)
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei doctor *)
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei config show *)
---

Source filter: $ARGUMENTS

If a source id is given above, report on that source only (use `sources show <id>`); otherwise report on all sources. This is a read-only inventory: do not download, update or modify anything.

In this file `design-sensei` means `${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei` (quote the path if it contains spaces). Background on the reuse classes is in `${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/references/source-usage.md`.

1. **Mode and library.** Run `design-sensei config show --project .` and note `source_acquisition_mode`. Run `design-sensei doctor --brief` for the library location and the "N of M downloadable present" line.
2. **State of every source.** Run `design-sensei sources list` (add `--json` if you need to parse it) and `design-sensei sources status`. A source is *downloaded* when its local state is present (`at_pin` is current; anything else means a moved pin or local changes). `reference_only` sources have no code to download by design.
3. **Licence class.** For each source (or the one asked for) run `design-sensei sources show <id>` and read the `license`, `reuse`, `local`, `restriction` and `patterns` lines. Run these in parallel.
4. **Present one table**: source id | downloaded (yes, no, reference only) | local commit versus pin | licence and status | reuse class | number of catalog patterns that cite it. Below it, group the sources by reuse class (`copy_with_attribution`, `license_review_required`, `reimplement_only`, `reference_only`, `verify_first`) and call out anything that needs a person to read the licence text (for example custom terms, `needs_human_review`, licence not found). Name the patterns affected for those sources, because those patterns inherit the restriction.
5. **Offer the exact commands, never run them.** Print the ones that apply, using the full launcher path:
   - missing downloadable sources: `${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei sources sync <id> [<id> ...]` (needs network and git);
   - everything, about 300 MB: `${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei sources sync --all`;
   - a preview first: add `--dry-run`.
   If `source_acquisition_mode` is `offline`, say that syncing is disabled by the project's configuration and ask whether the user wants to change that before suggesting `--online`. Do not suggest `--update` (it moves pins to upstream tips) unless the user asks.
6. **Ask before acting.** End by asking whether to run any of the offered commands. Run `sources sync` only after an explicit yes for specific ids, and never run install scripts or other code from a downloaded repository.
