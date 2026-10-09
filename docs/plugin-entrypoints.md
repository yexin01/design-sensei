# Plugin entry points

Besides the `design-sensei` skill (which Claude loads on its own for UI design work), the plugin ships four slash commands and one subagent. They are direct entry points to single steps of the skill's workflow (inspect, art-direct, discover, implement, verify). They reference the skill's files instead of copying them, so the skill stays the one source of truth.

Commands live in `commands/` and the agent in `agents/` at the plugin root. Claude Code discovers both directories by default, so `.claude-plugin/plugin.json` declares nothing for them. Commands are namespaced by the plugin name.

| Entry point | Invoke as | What it does | Writes files? |
| --- | --- | --- | --- |
| Brief | `/design-sensei:brief <goal>` | Checks the toolkit, inspects the project, picks a style and writes the art-direction brief (audience and emotion, style, type, colour tokens, layout, motion, dials, sources with reuse class). Ends by asking for approval. | No code, no files |
| Style | `/design-sensei:style <mood words>` | Finds style candidates (`design-sensei recommend` when the CLI has it, always `design-sensei search --category design-style`), reads the style notes and presents 2 or 3 options with fit, poor fit, pairings and a recommendation. | No |
| Review | `/design-sensei:review [target]` | Runs the project checks and `design-sensei eval`, collects browser evidence when a browser tool exists (375, 768, 1280 and 1920 px, reduced motion, keyboard, console, contrast), then hands the evidence to the `design-reviewer` agent for the scoring pass and relays its report. | No |
| Sources | `/design-sensei:sources [id]` | Lists which upstream sources are downloaded, their licence and reuse class, and the patterns that cite them. Prints the exact `sources sync` commands and asks before running any. | No |
| Reviewer agent | `design-reviewer` (Claude picks it, or `/design-sensei:review` delegates) | Read-only QA pass: scores the ten categories of `skills/design-sensei/references/design-qa.md` with evidence, flags licence and provenance problems, and returns scores, prioritised fixes and a list of what could not be verified. | Never |

## How the pieces call the CLI

Commands use the launcher `${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei`, the same program as the `design-sensei` on the Bash tool's `PATH`, and list only read-only subcommands in their `allowed-tools` (`search`, `recommend`, `eval`, `doctor`, `config show`, `sources list|status|show`). `sources sync` is deliberately not allow-listed: Claude Code prompts, and the commands say never to run it without an explicit yes.

The reviewer agent has `Read`, `Grep`, `Glob` and `Bash` only. Its prompt limits `Bash` to the CLI's inspection commands and the project's own build, lint and test scripts. It cannot drive a browser; `/design-sensei:review` gathers browser evidence in the main session (screenshots saved outside the repository) and passes the file paths and measurements in the prompt. Anything the bundle does not cover is reported as not verified.

## Checks

`tests/unit/test_plugin_entrypoints.py` parses the front matter of every file in `commands/` and `agents/`, checks that each mentioned CLI sub-command, flag, `${CLAUDE_PLUGIN_ROOT}` path, repository path and relative link exists, that the reviewer stays read-only and names all ten rubric categories, and that `/design-sensei:style` keeps its search fallback. `claude plugin validate --strict commands` and `claude plugin validate --strict agents` check the components with Claude Code itself.
