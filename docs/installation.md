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

The launcher `skills/design-sensei/scripts/design-sensei` follows the symlink back to the clone, so catalog, knowledge notes and scripts are found. A skill folder that is *copied* instead of linked cannot find them; set `DESIGN_SENSEI_ROOT=~/src/design-sensei` (or clone to `~/.design-sensei/toolkit`) and the launcher uses that. Without either it exits with code 4 and tells you so.

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
| 4 | `~/.design-sensei/sources/` | installed plugin or any copy without `.git` |

`design-sensei doctor` prints the location it chose and why. The library is deliberately **not** inside the plugin directory, because Claude Code replaces that directory on every update.

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
rm -rf ~/.design-sensei          # the downloaded sources and state (your choice; it is a cache)
```
