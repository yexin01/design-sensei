# Evals

Two kinds of evals for the `design-sensei` skill, both in the format used by Anthropic's `skill-creator` plugin.

| File | What it is | Status |
| --- | --- | --- |
| `trigger-queries.json` | 24 realistic prompts (12 should trigger the skill, 12 near-misses that should not) | run, see `results-trigger.md` |
| `results-trigger.md` | baseline vs final trigger rates, iteration table, chosen description | generated |
| `evals.json` | 5 behavioural task prompts with verifiable expectations | authored, not run yet |
| `run_eval-local-patch.diff` | the three small changes we made to skill-creator's `run_eval.py` (below) | reference |

## Trigger evals (does the description make Claude pick the skill?)

Needs the `skill-creator` plugin, the `claude` CLI, and Python 3.10+. Each run starts a headless `claude -p` session with
the skill description injected as a slash command and checks whether the model calls it. Roughly 70 CLI calls per
description at `--runs-per-query 3` (about 3 cents each).

```bash
SC=~/.claude/plugins/cache/claude-plugins-official/skill-creator/<hash>/skills/skill-creator
mkdir -p /tmp/ds-eval/project/.claude          # run from a scratch project, never from this repo or ~/.claude
cd /tmp/ds-eval/project
PYTHONPATH=$SC python3.13 -m scripts.run_loop \
  --eval-set <repo>/evals/trigger-queries.json --skill-path <repo>/skills/design-sensei \
  --model <model-id> --max-iterations 4 --runs-per-query 3 --holdout 0.4 --report none --verbose
```

The harness writes into `./.claude/commands` of the nearest directory that has a `.claude/`, so always run it from a
scratch directory. Setup that made the numbers reproducible (details in `results-trigger.md`):

- A wrapper named `claude` earlier on `PATH` that adds `--setting-sources project,local --no-session-persistence`, so the
  nested session loads no user plugins, hooks or MCP servers and leaves no session files.
- Stub copies of competing design skills (`frontend-design`, `impeccable`, `ui-ux-pro-max`, `design-consultation`: name and
  real description only) in the scratch project's `.claude/skills/`, so the description has to win against realistic
  alternatives.
- `run_eval-local-patch.diff` applied to a copy of skill-creator's `scripts/`. It fixes two harness problems: parallel
  workers shared one commands directory, so a run could call a sibling's identical copy and be counted as a miss; and a run
  was scored as a miss whenever a `Bash`/`Read` call came before the `Skill` call in the same turn. Set
  `TRIGGER_EVAL_LOG=<file>` to also log which skill each run chose, and `TRIGGER_EVAL_TURNS=<n>` to look at more than the
  first assistant turn.

Re-run after any change to the `description:` field. Do not tune on the held-out half of the queries.

## Behavioural evals (does the skill make the work better?)

`evals.json` follows skill-creator's `references/schemas.md`. To run it, follow the skill-creator "run test cases" flow:
for each eval, run the prompt once with the skill and once without (or against the previous skill version), grade the
`expectations` against the transcript and outputs, aggregate with `scripts/aggregate_benchmark.py`, and review in
`eval-viewer/generate_review.py`. Keep all workspaces and transcripts outside the repository.
