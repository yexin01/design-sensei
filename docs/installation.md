# Installation

Design Sensei has two parts that you install separately on purpose:

1. **The toolkit** (plugin, skill, catalog, knowledge notes, CLI). Small, text only, safe to update.
2. **The source library** (optional): shallow clones of the upstream projects, at pinned commits, stored *outside* the toolkit. Roughly 300 MB for all 15 downloadable sources; `design-sensei setup` downloads nothing by default.

## Requirements

| Needed | For | Notes |
| --- | --- | --- |
| Claude Code | the skill | plugin commands need a version that has `claude plugin ...` (developed against 2.1.295) |
| Python 3.9 or newer | the CLI | standard library only, no `pip install` |
| git | downloading sources | not needed to search the catalog |
| A browser tool (Playwright MCP, Chrome DevTools, a headless browser skill) | visual verification | optional; the skill says so when it is missing |

What has actually been tested: macOS (Darwin 25.6, Apple silicon) with Python 3.9.6 and 3.13 (the whole test suite passes on both), git 2.53, and Claude Code 2.1.295 (`claude plugin validate --strict`, `marketplace add`, `install` and `details` in an isolated config directory). Linux and Windows are **not** tested yet; the CLI is plain POSIX-friendly Python and the CI workflow targets Ubuntu and macOS, but treat both as unverified until CI has run.

## Option A - install as a Claude Code plugin (recommended)

From a clone of this repository:

```bash
git clone https://github.com/yexin01/design-sensei.git
claude plugin marketplace add ./design-sensei
claude plugin install design-sensei@design-sensei
claude plugin list          # design-sensei@design-sensei  Status: enabled
```

Inside a Claude Code session the same steps are `/plugin marketplace add ./design-sensei` and `/plugin install design-sensei@design-sensei`.
Once the repository is published you can add it by GitHub name instead (`/plugin marketplace add <owner>/design-sensei`, as described in the Claude Code plugin documentation; not exercised against a published repository yet).
To try it for one session without installing, Claude Code documents `claude --plugin-dir ./design-sensei`.

What you get:

* the **skill** `design-sensei` (Claude uses it automatically for UI design work, or run `/design-sensei:design-sensei`),
* the command **`design-sensei`** on the Bash tool's `PATH` while the plugin is enabled (`bin/`),
* nothing is copied into your application. You never copy this repository into a project.

Update and remove: `claude plugin update design-sensei@design-sensei`, `claude plugin uninstall design-sensei@design-sensei`. Uninstalling does not delete the source library (see below).

## Option B - skill only (no plugin)

```bash
git clone https://github.com/yexin01/design-sensei.git ~/src/design-sensei
ln -s ~/src/design-sensei/skills/design-sensei ~/.claude/skills/design-sensei   # personal skill, all projects
# or, for one project:  ln -s ~/src/design-sensei/skills/design-sensei <project>/.claude/skills/design-sensei
```

The launcher `skills/design-sensei/scripts/design-sensei` follows the symlink back to the clone, so catalog, knowledge notes and scripts are found. A skill folder that is *copied* instead of linked cannot find them, because they live outside `skills/design-sensei/`. Three ways out: build a self-contained copy ([Option B2](#option-b2---portable-bundle-copy-it-no-clone-needed), recommended when you want to copy), set `DESIGN_SENSEI_ROOT=~/src/design-sensei`, or clone to `~/.design-sensei/toolkit`. With none of them the launcher exits with code 4 and tells you so.

## Option B2 - portable bundle (copy it, no clone needed)

A bundle is the skill plus a private copy of everything it needs, in one folder. Copy or unzip it to `~/.claude/skills/` (or `<project>/.claude/skills/`) and it works, from any location, with nothing else installed except Python 3.9+.

```bash
# build it (from a clone), or download design-sensei-skill-<version>.zip from a GitHub release
design-sensei package-skill --zip        # -> dist/design-sensei/ and dist/design-sensei-skill-<version>.zip (+ .sha256)
cp -R dist/design-sensei ~/.claude/skills/               # personal skill, all projects
# or:  unzip design-sensei-skill-<version>.zip -d ~/.claude/skills/
# or, for one project:  cp -R dist/design-sensei <project>/.claude/skills/

~/.claude/skills/design-sensei/scripts/design-sensei doctor --brief      # toolkit: .../design-sensei/toolkit
```

`package-skill [--out DIR] [--zip]` writes `DIR/design-sensei/` (default `DIR` is `dist/` in the checkout, which is git-ignored) and, with `--zip`, `DIR/design-sensei-skill-<version>.zip` plus its `.sha256`. It is also available as `python3 scripts/build_portable_skill.py`. Run it from a clone or plugin checkout, not from a bundle.

What the folder contains (about 190 files, 2.2 MB; the zip is about 0.8 MB):

```
design-sensei/
  SKILL.md  references/  patterns/  config/  scripts/design-sensei    the skill, exactly as in skills/design-sensei/
  toolkit/
    bundle.json           marks this toolkit as a bundle (see "Where the library lives")
    catalog/  knowledge/  registry, schemas, pattern catalog, notes, generated pattern index
    scripts/              every Python module of the command line (standard library only)
    docs/  examples/glass-hero/   user documentation and the original example
    LICENSE  ATTRIBUTION.md  NOTICE  CONTRIBUTING.md  SECURITY.md
```

What it never contains: the upstream source clones (`sources/`), local state (`.state/`), git data, tests, plugin manifests, secrets, caches, and anything the repository's `.gitignore` matches. If a stray secret-like or ignored file sits inside an included folder, the build **stops with an error** instead of quietly skipping it, and nothing is written. Upstream code is downloaded on demand into `~/.design-sensei/sources/`, as with every other install.

How it works:

* **Finding the toolkit.** The launcher tries, in order: `$DESIGN_SENSEI_ROOT`, the repository layout (three levels above the launcher: git checkout and plugin install), `<skill folder>/toolkit`, `~/.design-sensei/toolkit`. A symlinked bundle is resolved to its real folder first.
* **Where the library lives.** A bundle keeps the source library and state in `~/.design-sensei/` (or `$DESIGN_SENSEI_HOME`, or `--home`), never inside the skill folder, which may be read-only and is replaced when you update. `doctor` prints "portable skill bundle" as the reason. The folder is never written to while it runs.
* **One mechanical change to the Markdown.** In the repository the skill folder sits two levels below the root, so skill files reach notes with paths such as `../../../knowledge/...` (in `references/` and `patterns/`) or `${CLAUDE_SKILL_DIR}/../../catalog/...` (in `SKILL.md`). Those paths cannot work from a copied folder, so the build rewrites every relative path that climbs out of the skill folder to a top-level repository item (`catalog`, `knowledge`, `docs`, `examples`, `scripts`, `ATTRIBUTION.md`, `LICENSE`) so that it points into the bundled toolkit: `../../../knowledge/x.md` in `patterns/` becomes `../toolkit/knowledge/x.md`, and `${CLAUDE_SKILL_DIR}/../../catalog/patterns.yaml` becomes `${CLAUDE_SKILL_DIR}/toolkit/catalog/patterns.yaml`. Nothing else is changed in any file, the sources in the repository are never touched, and the build fails if a relative Markdown link in the skill or the knowledge notes does not resolve (a dead link in the bundled `docs/` only prints a warning). Everything the launcher and `${CLAUDE_SKILL_DIR}/scripts/design-sensei` do is unchanged.
* **Reproducible.** Entries are sorted, timestamps are fixed (1980-01-01), permissions are normalised (0644, the launcher 0755). The same checkout gives a byte-identical zip with the same Python and zlib; compare the `.sha256`.

Verify a copy: `design-sensei doctor --brief`, `design-sensei catalog validate --strict` and `design-sensei search "liquid glass"` all work from the installed folder with `DESIGN_SENSEI_ROOT` unset.

Limits: a bundle is a skill, not a plugin. It does not put `design-sensei` on the Bash tool's `PATH` (the skill calls `${CLAUDE_SKILL_DIR}/scripts/design-sensei`) and carries none of the plugin's other components. It is a snapshot: update it by building or downloading a newer bundle and replacing the folder (your library in `~/.design-sensei/` is untouched). Tools that unpack zips without Unix permissions (some GUI archivers, Python's `zipfile.extractall`) drop the launcher's executable bit; `doctor` reports it, and `chmod +x ~/.claude/skills/design-sensei/scripts/design-sensei` fixes it. Untested so far on Linux and Windows, like the rest of the project.

## Option C - command line only

```bash
git clone https://github.com/yexin01/design-sensei.git
cd design-sensei
./bin/design-sensei doctor
./bin/design-sensei search "liquid glass button"
```

Add `bin/` to your `PATH` if you want to type `design-sensei` anywhere.

## The source library

`design-sensei setup` creates the library folder, validates the catalog and builds the file index. It downloads **nothing** unless you ask:

```bash
design-sensei setup                      # light: catalog, notes and search only
design-sensei setup --sources lenis,gsap # a few sources
design-sensei setup --full               # all 15 downloadable sources (about 300 MB)
design-sensei sources sync react-bits    # add one later, on demand
design-sensei sources status             # present / at pin / modified / missing
```

Where the library lives (first match wins):

| Order | Location | When |
| --- | --- | --- |
| 1 | `--home DIR` | explicit |
| 2 | `$DESIGN_SENSEI_HOME` | environment variable |
| 3 | `<repository>/sources/` | you are working in a git checkout (contributors; git-ignored) |
| 4 | `~/.design-sensei/sources/` | installed plugin, [portable bundle](#option-b2---portable-bundle-copy-it-no-clone-needed) (always, because it carries a `toolkit/bundle.json` marker) or any copy without `.git` |

`design-sensei doctor` prints the location it chose and why. The library is deliberately **not** inside the plugin directory or a skill folder, because Claude Code replaces plugin directories on every update and a skill folder can be read-only.

Sources are cloned shallow (`--depth 1`) at the exact commit pinned in `catalog/sources.yaml`; large repositories use a sparse checkout. Three sources are websites or articles and are never downloaded. See [source-management.md](source-management.md).

### Source acquisition modes

Set `source_acquisition_mode` in `~/.design-sensei/config.yaml` (user) or the project's `.design-sensei.yaml`:

| Mode | Behaviour |
| --- | --- |
| `on_demand` (default) | the skill downloads a source the first time a pattern needs it (the command asks for permission) |
| `full` | you expect everything to be present; `doctor` reports what is missing |
| `offline` | `sources sync` never touches the network; existing sources keep working |

## Using it in another application

1. Open Claude Code in your application. Nothing needs to be copied or installed into it.
2. Optional: `design-sensei config init` writes a commented `.design-sensei.yaml` (design variance, motion intensity, visual density, allowed dependencies, performance budget, WebGL on/off, reduced-motion policy).
3. Ask for UI work ("redesign the landing page hero with a liquid glass look"). The skill inspects the project, writes an art-direction brief, searches the catalog, implements, and verifies.

## Removing everything

```bash
claude plugin uninstall design-sensei@design-sensei
claude plugin marketplace remove design-sensei
rm -rf ~/.claude/skills/design-sensei   # a portable bundle or a skill symlink
rm -rf ~/.design-sensei          # the downloaded sources and state (your choice; it is a cache)
```
