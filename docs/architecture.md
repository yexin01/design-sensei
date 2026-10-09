# Architecture

Design Sensei is four layers around one idea: **Claude should design from decisions and real implementations, not from vague adjectives.** Everything works locally with the standard library; there is no server, database, API key or vector store.

```
                          ┌──────────────────────────────────────────────┐
  Layer 3  Claude Code    │ plugin (.claude-plugin/)   skill (skills/)   │
                          │ SKILL.md workflow, references/, patterns/     │
                          └──────────────┬───────────────────────────────┘
                                         │ runs `design-sensei …`
                          ┌──────────────▼───────────────────────────────┐
  Layer 4  Tooling        │ scripts/  setup · sources · index · search    │
                          │ catalog validate · licenses · doctor · eval   │
                          └───────┬──────────────────────┬───────────────┘
                 reads/validates  │                      │ writes (library home)
                          ┌───────▼───────────┐   ┌──────▼────────────────────┐
  Layer 2  Knowledge      │ catalog/ (YAML)   │   │ Layer 1  Upstream sources  │
  (committed)             │ knowledge/ notes  │   │ sources/<id>/ git clones   │
                          └───────────────────┘   │ .state/ lock + file index  │
                                                  └────────────────────────────┘
                                                    (git-ignored, per machine)
```

## Layer 1 - upstream sources

Git sources are shallow (and for large repositories sparse) clones at commits pinned in `catalog/sources.yaml`. Websites and articles are recorded but never fetched. The library lives outside the plugin directory so it survives updates. Details: [source-management.md](source-management.md).

## Layer 2 - curated knowledge (committed)

| Path | Contents |
| --- | --- |
| `catalog/sources.yaml` | registry of all 18 upstream sources |
| `catalog/patterns.yaml`, `catalog/patterns.d/*.yaml` | searchable patterns and design styles; ids unique across all files |
| `catalog/licenses.yaml` | license policy table and the per-source review ledger |
| `catalog/schemas/*.json` | JSON Schemas for all of the above, config and note front matter |
| `knowledge/design-styles/` | style taxonomy (original writing) |
| `knowledge/components/`, `shaders/`, `animations/`, `design-intelligence/` | what each upstream provides, with cited file paths |
| `knowledge/website-references/` | reference-only sites: URL, observations, terms stance |
| `knowledge/implementation-recipes/` | step-by-step recipes with original code |
| `knowledge/pattern-index/` | generated browsable views and `pattern-index.json` |

Provenance is machine-checked. A pattern lists `source_ids` and `source_paths` (`source-id:path`); a note lists `source_ids` and cites files in backticks. `catalog validate` resolves every reference against the checked-out pinned commit whenever the source is present. Original, upstream-derived and generated material are separate: the `provenance` field of a pattern says which, and generated files carry a header.

## Layer 3 - plugin and skill

`.claude-plugin/plugin.json` and `marketplace.json` package the repository root as one plugin. The skill is `skills/design-sensei/SKILL.md`: a short workflow (inspect, art-direct, discover, implement, verify) that loads `references/*.md` and `patterns/*.md` only when needed. It reaches the toolkit through `${CLAUDE_SKILL_DIR}/scripts/design-sensei`, a launcher that locates the toolkit relative to itself, so it works from a plugin install, a symlinked skill folder, a checkout or a copied portable bundle (`<skill folder>/toolkit`) without assuming a working directory. `bin/design-sensei` puts the same command on the Bash tool's `PATH` while the plugin is enabled.

## Layer 4 - tooling (`scripts/`)

| Module | Responsibility |
| --- | --- |
| `design_sensei.py` | command line entry point and `setup`, `config` |
| `sync_sources.py` | acquisition, pinning, status, non-destructive updates |
| `index_sources.py` | deterministic file-level index of downloaded sources |
| `build_index.py` | pattern index documents (Markdown + JSON) and `index build` |
| `search_patterns.py` | ranked search over patterns, notes and files, with filters |
| `recommend.py` | one-call brief to recommendation: primary and supporting style, top patterns, licence gate, fallback, next steps (reuses the search ranking, honours the project configuration) |
| `validate_catalog.py` | schemas, cross references, license rules, file references |
| `check_licenses.py` | license detection, ledger, attribution report |
| `doctor.py` | environment and installation diagnostics |
| `design_eval.py` | static design lint against the evaluation rubric |
| `build_portable_skill.py` | `package-skill`: self-contained skill folder with a private `toolkit/` (and a deterministic zip) that works when copied anywhere, see [installation.md](installation.md#option-b2---portable-bundle-copy-it-no-clone-needed) |
| `dslib/` | `yamlite` (YAML subset parser), `jsonschema_lite`, git wrapper, paths, catalog and config loaders |

### Design decisions

* **Standard library only.** The tooling must run on a stock Python 3.9+ without installing anything. Python has no YAML parser, so `dslib/yamlite.py` parses the small, strict YAML dialect the catalog uses and *rejects* anything ambiguous (YAML 1.1 booleans, dates, octal-looking numbers, anchors, tabs, duplicate keys). Because it refuses constructs on which parsers disagree, everything it accepts loads identically in PyYAML; a test cross-checks that when PyYAML is installed. The JSON Schemas are standard draft-07 files; `jsonschema_lite` implements the subset they use and raises on any keyword it does not implement instead of silently skipping a rule.
* **Deterministic search, no embeddings.** Weighted fields, inverse document frequency, light stemming and a small synonym table are enough for a catalog of this size, are explainable, reproducible and testable. Embeddings would add a model dependency without a demonstrated benefit.
* **Upstream code is never committed.** It is large, under many licenses, and changes. Pins make it reproducible; a hygiene test enforces it.
* **Generated outputs are separate and reproducible.** `knowledge/pattern-index/` and `ATTRIBUTION.md` contain no timestamps and are checked for staleness in CI; the source file index and lock file stay local.
* **Honest verification.** Every status field has an explicit "unknown/pending" value, doctor and validate say what could not be checked, and the evaluator labels itself a heuristic.

## Data flow of a typical task

1. The skill runs `doctor --brief` and `config show` (library location, sources present, settings).
2. After the art-direction brief it runs `recommend "<mood and goal words>"` (or `search "<effect>" --framework … --reduced-motion-safe` for a single effect). Results come from `patterns.yaml` + `patterns.d/` with license and reuse class derived from the sources.
3. It reads the printed `knowledge_doc`/`recipe` paths and, if present, the real files under the library; otherwise `sources sync <id>`.
4. It implements in the user's project, then runs `eval` and a browser check.

## Configuration

`skills/design-sensei/config/defaults.yaml` < `<library home>/config.yaml` < the project's `.design-sensei.yaml`. All layers are validated against `catalog/schemas/config.schema.json`; `config show` prints each value with its origin.
