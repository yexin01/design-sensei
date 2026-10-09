# Troubleshooting

Start with `design-sensei doctor`. It checks Python, git, the toolkit, the catalog, plugin packaging, every downloaded source, the file index and your configuration, and prints a hint for each problem.

| Symptom | Cause | Fix |
| --- | --- | --- |
| `design-sensei: command not found` | the plugin is not enabled in this session, or `bin/` is not on `PATH` | run `claude plugin list`; or call `${CLAUDE_SKILL_DIR}/scripts/design-sensei`; or `./bin/design-sensei` from a clone |
| `cannot find the toolkit (catalog/ and scripts/)`, exit 4 | the skill folder was copied on its own | install as a plugin, symlink the skill folder from a clone, copy a [portable bundle](installation.md#option-b2---portable-bundle-copy-it-no-clone-needed) instead (`design-sensei package-skill`), or set `DESIGN_SENSEI_ROOT` |
| `cannot find the Design Sensei catalog under ...` | `DESIGN_SENSEI_ROOT` points at the wrong directory | point it at the directory that contains `catalog/sources.yaml` |
| `sources sync` exits 4 | git is missing, or `--offline` / `source_acquisition_mode: offline` and the source is not downloaded yet | install git, or sync without `--offline`, or pass `--online` once |
| `sources sync` exits 3 | some sources failed (network, disk, blocked checkout) | read the printed reasons; rerun for just those ids, one failing source never stops the others |
| `blocked: ... locally modified file(s)` | you edited a file inside a clone | the clone is never touched; commit or discard your change inside it, or delete the clone (it is a cache) and sync again |
| `blocked: ... exists but is not a git checkout` | a directory with the same name is in the library | move it away or change `local_path` |
| `pinned commit ... is not reachable` | the upstream rewrote history or deleted the commit | `design-sensei sources sync <id> --update --write-pins`, then review the diff and revalidate |
| `only N MB free ... need 1024 MB` | the disk-space guard | free space or lower `--min-free-mb` |
| search shows `(not downloaded)` next to files | the source is not in the library yet | `design-sensei sources sync <id>` |
| `no source index yet` | `--scope files` without an index | `design-sensei index build` |
| `catalog validate` reports `does not exist in <id> at the checked-out commit` | the pin moved or a note cites a wrong path | fix the path, or sync to the pinned commit with `sources sync <id>` |
| a YAML file fails with `ambiguous plain scalar` | the catalog dialect rejects values such as `yes`, `2026-10-09`, `0123` | quote the value: `"2026-10-09"` |
| `config show` exits 1 | invalid value in `.design-sensei.yaml` or `~/.design-sensei/config.yaml` | the message names the file and the rule; see `catalog/schemas/config.schema.json` |
| Claude does not use the skill | description did not match the request, or plugin disabled | invoke it explicitly with `/design-sensei:design-sensei`; check `claude plugin list` |
| `claude plugin validate` warns about `CLAUDE.md` | a `CLAUDE.md` at the plugin root is not loaded as context | do not add one to this repository root |

## Resetting

* Local state only: delete `<library>/.state/` (it is rebuilt by `design-sensei index build`; the lock file is informational).
* Everything downloaded: delete `<library>/sources/`. Nothing in the repository depends on it.
* Where is the library? `design-sensei doctor` prints `library: <path> (<reason>)`.

## Reporting a problem

Include the output of `design-sensei doctor --json`, your OS, Python and git versions, and the command that failed. Remove any private paths.
