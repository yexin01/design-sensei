# sources/

This directory is the **default local source library** when you work from a
git checkout of Design Sensei. Everything here except this file is ignored by
git (see `.gitignore`), so upstream code is never committed to this repository.

```bash
./bin/design-sensei setup --full          # clone every eligible upstream source
./bin/design-sensei sources sync lenis    # clone just one
./bin/design-sensei sources status        # what is present, at which commit
```

Each upstream lives in `sources/<local_path>/` and keeps its own license files
and copyright notices untouched. Revisions are pinned in `catalog/sources.yaml`
(`pinned_commit`), so two people running the same command get the same files.

When Design Sensei is installed as a Claude Code plugin there is no git
checkout, so the library lives in `~/.design-sensei/sources/` instead (override
with `DESIGN_SENSEI_HOME`). See `docs/installation.md` and
`docs/source-management.md`.

Do not edit files inside upstream clones. Sync refuses to touch a clone that has
local modifications; keep your own experiments in your own project.
