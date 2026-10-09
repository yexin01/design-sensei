# Licensing and attribution

> Everything on this page is a description of how this project treats licenses. It is **not legal advice**. License detection in the tooling is a heuristic text match; anything it cannot recognise, or that looks restrictive, is flagged for a person to read.

## Scope of this repository's own license

The original work in this repository (scripts, plugin, skill, schemas, catalog metadata, knowledge notes, recipes, playbooks, documentation) is MIT licensed, see `LICENSE`.
It does **not** contain upstream code. Upstream projects are never committed here; each keeps its own license and copyright notices in the clone on the user's machine, and the generated [`ATTRIBUTION.md`](../ATTRIBUTION.md) lists them.
Knowledge notes describe upstream projects in their own words and cite files by path (`source-id:path`). Recipes contain original code that calls public APIs. Short quotations (at most about eight lines, with a citation) are used only from permissively licensed sources.

## What is recorded for every source

In `catalog/sources.yaml`: URL, name, license identifier, `license_status`, `redistribution_status`, attribution line, acquisition method, pinned commit, last-checked date, notes.
In `catalog/licenses.yaml` (written by `design-sensei licenses scan --write`): the license files found at the pinned commit with their SHA-256, copyright lines, license fields declared by package manifests, the commit that was reviewed, restrictions, and a review status.

### `license_status`

| Value | Meaning |
| --- | --- |
| `verified` | the license text was found at the pinned commit and matches the SPDX identifier |
| `custom_terms` | non-standard or modified license text: read it |
| `proprietary_terms` | terms restrict redistribution (for example a paid product) |
| `not_found` | no license or terms found: all rights reserved by default |
| `pending_verification` | not inspected yet |
| `unknown` | inspected, but the situation could not be decided (for example MIT declared in a README but no license file) |

### `redistribution_status` and the reuse class shown by search

| `redistribution_status` | Reuse class | What it means for your project |
| --- | --- | --- |
| `redistributable_with_notice` | `copy_with_attribution` | permissive license: adapt and copy, keep the copyright and license notice, list the project in `THIRD_PARTY_NOTICES.md` |
| `license_specific` | `license_review_required` | custom terms: read `design-sensei sources show <id>` and the upstream license; use the published package rather than copying source; never bundle or republish |
| `unresolved` | `reimplement_only` | no license granted: study the idea, write your own code |
| `reference_only` | `reference_only` | link and describe only |
| `pending_verification` | `verify_first` | treat as reference-only until checked |

A pattern's reuse class is the most restrictive class among its sources. Patterns that are project-authored guidance show `original`.

## Source-by-source status (inspected 2026-10-09)

The authoritative, regenerated version is [`ATTRIBUTION.md`](../ATTRIBUTION.md). Summary of what needs human attention:

| Source | Situation | Handling |
| --- | --- | --- |
| `react-bits` | "MIT + Commons Clause": free to use in an application, website or product, but not to sell, sublicense or redistribute the components themselves (alone, in a bundle or ported) | custom terms, `license_specific`. Notes describe it; no code is quoted; recipes only explain how to consume it as a dependency |
| `gsap` | No LICENSE file in the repository; `package.json` and the README point to the "Standard 'no charge' license" at gsap.com (read on 2026-10-09: owned by Webflow, free use on websites and apps, prohibits use in visual animation builders that compete with Webflow, may be amended) | custom terms, `license_specific`. Use the npm package; GSAP source is never copied here |
| `skiper-ui` | No license anywhere. Its README says it is an educational frontend clone of the original Skiper UI design (skiper-ui.com), so rights belong to someone else | `not_found` / `unresolved`: ideas only, no code, no recipes derived from it |
| `shadergradient` | MIT is declared in the README and in several `package.json` files, but there is no LICENSE file with a copyright notice | `unknown` / `license_specific`: keep the README attribution; ask the maintainers for a LICENSE file |
| `animmaster-lib` | Commercial library; its terms grant a purchaser a license and prohibit redistributing the library or its source files | `proprietary_terms` / `reference_only`; website is linked, nothing downloaded |
| `refero-styles` | Website; its robots.txt disallows AI crawlers (ClaudeBot, anthropic-ai, GPTBot and others). Terms not reviewed | `unknown` / `reference_only`: no fetching, scraping or snapshots by this project |
| `uxplanet-50-design-styles` | Article behind a Cloudflare challenge; inspection blocked (HTTP 403). Copyright with its author and publisher | `unknown` / `reference_only`; nothing reproduced. The style taxonomy in `knowledge/design-styles/` is original writing |
| `taste-skill`, `awesome-opus-videos`, `liquid-logo`, `vengeance-ui`, `fancy`, `astryx`, `react-three-fiber`, `liquid-glass-js`, `lenis` | MIT, license file found and matched | `verified`. Media (sponsor logos, photos, avatars, sample images) inside these repositories may have other owners: do not reuse media |
| `design-md`, `img2threejs` | Apache-2.0, license file found and matched | `verified`. Keep the NOTICE and state significant changes when adapting |

Items that still need a person: the exact current text of the GSAP and animmaster terms, the Refero terms of use, and the shadergradient licensing question. They are marked `needs_human_review` in `catalog/licenses.yaml`.

## Rules the tooling enforces

* `redistributable_with_notice` requires `license_status: verified` and an SPDX identifier whose policy class is permissive or public domain (`catalog/licenses.yaml` `policy.spdx`).
* A source with no license cannot be anything but `unresolved` or `reference_only`; a proprietary one must be `reference_only`.
* `verified` is impossible for a reference-only source (nothing was inspected).
* A pattern's declared `license_status` must equal the status derived from its sources.
* `design-sensei licenses check` compares each downloaded clone's license files against the catalog and the recorded SHA-256, and reports mismatches, missing files, changed files, stale reviews, nested licenses of a different kind and package manifests that disagree.
* `design-sensei eval` warns when project code credits a source whose reuse class forbids copying, or credits a permissive source without a notice file.

## Regenerating the attribution report

```bash
design-sensei licenses scan --write        # refresh catalog/licenses.yaml from downloaded clones
design-sensei licenses report              # rewrites ATTRIBUTION.md from the catalog (deterministic)
design-sensei licenses report --check      # exit 1 if ATTRIBUTION.md is stale (used by CI)
```

## If you reuse code from a source

1. Check the reuse class in the search result or `sources show <id>`.
2. For `copy_with_attribution`: keep the upstream copyright line and license text with the copied code (a comment header and an entry in `THIRD_PARTY_NOTICES.md`), and note significant changes for Apache-2.0.
3. For anything else: depend on the published package, or reimplement from the idea.
4. Never copy media. Never assume that what you can see on a website may be redistributed.
