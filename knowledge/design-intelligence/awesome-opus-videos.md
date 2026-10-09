---
title: "Awesome Opus 5.5 videos: prompt library"
kind: guide
summary: "Guide to the awesome-opus-videos repository: 513 third-party prompts for videos and animations made with Claude Opus 5.5, the data and prompts layout, example entries, how to mine them for art-direction vocabulary, and caveats about attribution."
source_ids: [awesome-opus-videos]
pattern_ids: [awesome-opus-videos-prompt-mining]
updated: "2026-10-09"
---

# Awesome Opus 5.5 videos

## What it is

A curated list, by yihui-dev, of viral videos made with Claude Opus 5.5, each paired with the prompt its creator shared (or, when
none was published, the creator's original post). According to the README (`awesome-opus-videos:README.md`), every video was made
by asking the model to write the animation as code (HTML, Canvas, SVG, Three.js and similar). The data lists 513 entries from
476 distinct creators. Pinned commit `7562902`, latest batch added 2026-10-08. The videos are third-party works linked by URL;
previews are hosted on a third-party site (Skillry). It is a prompt corpus, not a design system and not a website pattern library.

## Structure

| Path | Contents |
| --- | --- |
| `awesome-opus-videos:README.md` | counts, 100 highlighted entries in HTML tables under four category headings (58 motion graphics, 16 explainers, 14 3D scenes, 12 games and interactive), a "how to use a prompt" section, credits |
| `awesome-opus-videos:data/videos.json` | one JSON array with all 513 entries |
| `awesome-opus-videos:prompts/` | 513 Markdown files, one per entry; file names equal the `slug` field |
| `awesome-opus-videos:LICENSE` | MIT, "Copyright (c) 2026 yihui-dev" |

Each `videos.json` entry has eleven fields (counts computed over the pinned data):

| Field | Meaning |
| --- | --- |
| `slug` | lower-cased author handle plus the last six digits of the post id, for example `ajith-io-890146` (holds for all 513) |
| `author`, `author_url`, `post_url` | creator handle, profile and original post |
| `category` | `motion` 317, `interactive` 70, `explainer` 67, `3d` 59 |
| `tech_tags` | one to four of `canvas` 351, `svg` 219, `threejs` 147, `shader` 104, `gsap` 100, `css` 68, `audio` 36, `particles` 26, `playable` 22, `pixel` 16, `ai-image` 10, `webgl` 9, `physics` 9 |
| `prompt`, `prompt_partial` | the text; `true` for 234 entries where only part of the prompt, or just the creator's post, is available |
| `poster_url`, `skillry_url`, `added` | preview image, remake page, batch date (2026-09-26, 09-28, 09-29, 10-08) |

Each prompt file has the same layout: an H1 "Opus 5.5 video by @handle", a links line (remake page, original post), a bullet
list (category, "Remake built with", author), an optional blockquote saying the author shared only part of the prompt or only
a post (5 and 229 files respectively), then `## Prompt` and the text in a fenced `text` block (two files use four backticks
because the prompt contains fences).

## Example entries

| Path | Length | What it shows |
| --- | --- | --- |
| `awesome-opus-videos:prompts/ajith-io-890146.md` | 151 chars | the most common shape: a one-sentence "showreel" request; the same sentence appears in 36 entries after whitespace and case normalisation |
| `awesome-opus-videos:prompts/twoclipping-402193.md` | 2,711 chars | a reusable template with tagged blocks (inputs, direction, structure, build, gotchas, start); 12 entries use the family; the direction block gives a reference, a palette, one UI font, spring behaviour and a short banned list |
| `awesome-opus-videos:prompts/brainextends-606193.md` | 8,142 chars | a brand-themed brief with deliverables, an art-direction block (stage proportions, background treatment, colours, font), generated artwork instructions and a per-second timeline |
| `awesome-opus-videos:prompts/iamtanzil-675031.md` | 11,155 chars | closest to web work: a section spec for a scroll-scrubbed hero header (fonts, container sizes, element-by-element structure, GSAP and framer-motion behaviour), using externally hosted assets |
| `awesome-opus-videos:prompts/alexwtlf-981005.md` | 22,367 chars | the longest entry: a shot-by-shot film spec (scene context, blocking, cuts, optics, lighting in Kelvin, audio, a list of invariants) |

A partial entry (slug `gautam-mer1-530003`, 34 characters) carries only the creator's one-line description, which is why
`prompt_partial` must be filtered before any analysis.

## Mining the prompts for art-direction vocabulary

The corpus is dominated by short prompts: 105 are under 100 characters, 264 are 100-299, 96 are 300-999, only 48 reach 1,000, and
the median is 180. Only complete, long, distinct prompts carry usable direction. A read-only filter (original code, reads the JSON
only):

```python
import json, re, sys

rows = json.load(open(sys.argv[1], encoding="utf-8"))  # <library>/sources/awesome-opus-videos/data/videos.json
seen, keep = set(), []
for r in rows:
    text = " ".join(r["prompt"].split()).lower()
    if r["prompt_partial"] or len(text) < 700 or text in seen:
        continue
    seen.add(text)
    keep.append(r)

CLASSES = {
    "typography": r"\b(fonts?|typeface|tracking|kerning|serif|monospace)\b",
    "colour": r"\b(palette|accent|gradient)\b|#[0-9a-f]{6}\b",
    "motion": r"\b(easing|springs?|overshoot|stagger(ed)?|loops?)\b",
    "camera": r"\b(camera|lens|focal|orbit|zoom)\b",
    "light": r"\b(lighting|glow|shadows?|grain|reflections?)\b",
}
for cls, pattern in CLASSES.items():
    slugs = [r["slug"] for r in keep if re.search(pattern, r["prompt"].lower())]
    print(cls, len(slugs), "of", len(keep))
```

On the pinned data 37 of 513 entries survive the filter (7%), and they touch the classes as follows: typography 12, colour 13,
motion 18, camera 18, light 11. Method:

1. Filter as above, then read only the matching passages of each surviving prompt.
2. Write glossary entries in your own words (term, what it controls, example slug); never paste whole blocks.
3. Map each term to a Design Sensei decision or dial; discard terms that only make sense for video rendering.
4. Keep provenance: slug, creator handle and `post_url`. A quote needs the handle, the link and at most eight lines.

Vocabulary patterns seen in the surviving prompts (paraphrased):

| Pattern | Use in Design Sensei |
| --- | --- |
| a named reference plus a mood instead of adjectives alone | open the art-direction brief with one specific reference |
| a short explicit banned list (for example bouncy easing, glows) | add a don'ts list to the brief |
| one UI font and one accent, or pure black and white | colour and type restraint at low design variance |
| springs with a tiny overshoot, stagger per beat | motion tokens for `motion_intensity` 4-7 |
| first frame equals last frame | seamless hero loops, with a static frame for reduced motion |
| lens focal length, key and fill light by colour temperature | camera and lighting briefs for 3D scenes |
| a list of invariants ("locks") the result must satisfy | acceptance criteria |
| time-ranged beats | choreography tables for scroll or intro sequences |

## Caveats

- Third-party works: every prompt and video belongs to its creator (README credits). The MIT licence names yihui-dev and may not
  grant rights over creators' text. Quote briefly with attribution; never bulk-copy or republish.
- 234 of 513 entries are partial; 456 distinct texts remain after normalising duplicates.
- Web design is rare: roughly ten prompts (by keyword search) concern a hero, a landing page or a website; most are video, 3D or game briefs.
- Prompts may depend on files, attachments, accounts or tools that are not in the repo, name real brands, or carry personal,
  political or promotional content. Do not use brand-themed prompts to imitate a brand.
- Nothing verifies that outputs match the claims; no quality ranking exists. Upstream may change or remove entries on request.

## How Design Sensei should use it

Use it offline, as local reading material for art-direction vocabulary and brief structure, never as a dependency and never as
a pattern source for code. Keep any derived glossary original. Do not fetch the linked posts or previews.

## Licence and attribution

MIT, "Copyright (c) 2026 yihui-dev" (`awesome-opus-videos:LICENSE`); catalog attribution: "awesome-opus5-5-videos by yihui-dev
(https://github.com/yihui-dev/awesome-opus5-5-videos)". This note describes entries and quotes nothing.
