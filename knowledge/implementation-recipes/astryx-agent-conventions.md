---
title: "Keep coding agents on-system with Astryx conventions"
kind: recipe
summary: "Set up Astryx's agent tooling (CLI init, bootstrap commands), add a short project rules block built from its documented conventions, and enforce the mechanical ones with a small checker script that you run in CI."
source_ids: [astryx]
pattern_ids: [astryx-agent-ready-workflow, astryx-design-system-react, astryx-button-family]
updated: "2026-10-09"
---

# Keep coding agents on-system with Astryx conventions

## Goal

An agent that builds UI with Astryx should read the real component docs instead of guessing, follow the library's naming and
spacing conventions, and be checked by a script that catches the mistakes the docs call out most often.

## When to use, and when not

Use it in a project that already depends on `@astryxdesign/core`. It does not make output good by itself: the Astryx authors report
nightly "vibe test" runs where an agent hallucinated imports and props on a bad night and the scorecard dropped
(`astryx:apps/docsite/src/content/blog/posts/vibe-tests.md`, self-reported). Treat the rules as guard rails, and review the result.
The CLI is not in the local checkout; its commands below are as documented in `astryx:AGENTS.md` and `astryx:packages/core/README.md`.

## Prerequisites

`@astryxdesign/core` 0.6.6 installed (`astryx:packages/core/package.json`), Node able to run ES modules, and `@astryxdesign/cli` as a
dev dependency (`npm install -D @astryxdesign/cli`). Use the scoped name when the CLI is not installed: bare `npx astryx` resolves to an
unrelated package until it is (`astryx:packages/core/docs.mjs`). A repo-level `"astryx"` script that runs
`node node_modules/@astryxdesign/cli/clients/cli/bin/astryx.mjs` avoids path errors for agents (`astryx:README.md`).

## Steps

1. Run `npx @astryxdesign/cli init` (or `npx astryx init` once the CLI is a dependency). Core's README says it writes the Astryx component index into `AGENTS.md` or `CLAUDE.md`; the block sits
   between `<!-- ASTRYX:START -->` and `<!-- ASTRYX:END -->`, and the files it looks in are `AGENTS.md`, `CLAUDE.md`,
   `.claude/CLAUDE.md`, `.cursorrules`, `.hermes.md` and `HERMES.md` (`astryx:packages/core/scripts/agent-doc-state.mjs`). A core
   postinstall script prints a one-line nudge to run init when no block exists; it never fails an install
   (`astryx:packages/core/scripts/postinstall.mjs`). `astryx upgrade` re-renders the block (`astryx:docs/architecture/cli-surface.md`,
   INV13), so keep your own rules outside the markers (whether text outside them is preserved was not verified).
2. Make the agent bootstrap on every branch, as `astryx:AGENTS.md` does for the Astryx repo: `astryx help`, `astryx docs`,
   `astryx docs principles --dense`, `astryx docs tokens --dense`, `astryx docs theme --dense`, `astryx component --list`,
   `astryx template --list`. Before editing a component run `astryx component <Name> --dense`; to find a starting point run
   `astryx build "<what you are making>"`, which the project describes as a deterministic ranker over components, hooks, docs and
   templates with no network call (`astryx:apps/docsite/src/content/blog/posts/astryx-cli-build-command.md`). After a core bump run
   `astryx upgrade --from <old version> --apply`.
3. Add project rules next to the generated block. Original wording; each line is backed by a `.doc.mjs` or family record:

   ```markdown
   ## Astryx rules
   - Read a component's docs (`npx astryx component <Name> --dense`) before using or editing it. Do not guess props.
   - Spacing props take numbers from 0, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, for example `gap={4}`. Never `gap="md"`.
   - Stack direction is 'horizontal' or 'vertical'. Text takes `type`, not `variant`. Icon takes `icon`, not `name`.
   - Button, IconButton and ToggleButton always need `label`. One primary button per view; confirm destructive actions.
   - Use Heading for headings (levels in order) and Text for copy. No raw h1-h6 or p for themed text.
   - Section groups page regions; Card is only for discrete items. No nested cards, no repeated icon-heading-text card grids.
   - Colours, radii, shadows and spacing come from tokens (`var(--color-...)`), not hex or pixel literals.
   - Override styles with `xstyle` (a `stylex.create` value) or `className`, not inline style objects.
   - Links go through Astryx Link or Button `href` so the shared URL-safety rule applies.
   - Use AppShell once. Do not add a second skip link or main element. Give every nav slot a `label`.
   - TabList is a nav strip unless `role="tablist"` and a `panelId` per tab are set. Charts need a `title`.
   ```

   Sources: `astryx:packages/core/src/Stack/Stack.doc.mjs`, `astryx:packages/core/src/Text/Text.doc.mjs`,
   `astryx:packages/core/src/Icon/Icon.doc.mjs`, `astryx:packages/core/src/Button/Button.doc.mjs`,
   `astryx:packages/core/src/Card/Card.doc.mjs`, `astryx:packages/core/src/Section/Section.doc.mjs`,
   `astryx:packages/core/src/AppShell/AppShell.doc.mjs`, `astryx:packages/core/src/TabList/TabList.doc.mjs`,
   `astryx:docs/families/buttons.md`, `astryx:docs/families/navigation-destinations.md`.
4. Add the checker. It reads `.tsx` and `.jsx` files, only for tags imported from `@astryxdesign/*` (so a local `Button` is
   ignored), and reports string or invalid spacing steps, a bad `Stack` direction, `Text variant`, `Icon name`, and Button-family
   controls without `label` (unless a spread could supply it). Tested against sample files with each mistake; heuristic by design.

   ```js
   #!/usr/bin/env node
   // Heuristic scan for Astryx usage that its docs call wrong. Not a parser: expect misses and false positives.
   // Usage: node scripts/check-astryx-usage.mjs src [more files or dirs]   (exit 1 when something is found)
   import {readdirSync, readFileSync, statSync} from 'node:fs';
   import {extname, join} from 'node:path';

   const SPACING = new Set(['gap', 'rowGap', 'columnGap', 'padding', 'paddingInline', 'paddingBlock',
     'paddingInlineStart', 'paddingInlineEnd', 'paddingBlockStart', 'paddingBlockEnd']);
   const SPACING_TAGS = new Set(['Stack', 'HStack', 'VStack', 'Grid', 'Center', 'Card', 'Section']);
   const STEPS = new Set([0, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10]);
   const NEEDS_LABEL = new Set(['Button', 'IconButton', 'ToggleButton']);

   function* files(path) {
     if (statSync(path).isFile()) { yield path; return; }
     for (const e of readdirSync(path, {withFileTypes: true})) {
       if (e.name === 'node_modules' || e.name.startsWith('.')) continue;
       const p = join(path, e.name);
       if (e.isDirectory()) yield* files(p);
       else if (['.tsx', '.jsx'].includes(extname(e.name))) yield p;
     }
   }

   // local JSX name -> Astryx export name, from `import {A as B} from '@astryxdesign/...'`
   function astryxNames(src) {
     const map = new Map();
     for (const m of src.matchAll(/import\s*\{([^}]*)\}\s*from\s*['"]@astryxdesign\/[^'"]*['"]/g)) {
       for (const part of m[1].split(',')) {
         const [orig, local] = part.trim().replace(/^type\s+/, '').split(/\s+as\s+/);
         if (orig) map.set(local || orig, orig);
       }
     }
     return map;
   }

   function skipBraces(s, i) { // s[i] === '{'; returns the index after the matching '}'
     let depth = 0, quote = null;
     for (; i < s.length; i++) {
       const c = s[i];
       if (quote) { if (c === quote && s[i - 1] !== '\\') quote = null; continue; }
       if (c === '"' || c === "'" || c === '`') quote = c;
       else if (c === '{') depth++;
       else if (c === '}' && --depth === 0) return i + 1;
     }
     return s.length;
   }

   // Walk one opening tag's attribute text -> {list: [{name, kind, value}], hasSpread, end}
   function readAttrs(s, i) {
     const list = [];
     let hasSpread = false;
     while (i < s.length && s[i] !== '>') {
       if (s[i] === '{') { hasSpread = true; i = skipBraces(s, i); continue; }
       const nm = /^[A-Za-z_][\w:-]*/.exec(s.slice(i, i + 80));
       if (!nm) { i++; continue; }
       i += nm[0].length;
       const eq = /^\s*=\s*/.exec(s.slice(i, i + 20));
       if (!eq) { list.push({name: nm[0], kind: 'bool', value: ''}); continue; }
       i += eq[0].length;
       if (s[i] === '"' || s[i] === "'") {
         const end = s.indexOf(s[i], i + 1);
         list.push({name: nm[0], kind: 'string', value: s.slice(i + 1, end)});
         i = end + 1;
       } else if (s[i] === '{') {
         const end = skipBraces(s, i);
         list.push({name: nm[0], kind: 'expr', value: s.slice(i + 1, end - 1).trim()});
         i = end;
       }
     }
     return {list, hasSpread};
   }

   const found = [];
   const roots = process.argv.slice(2).length ? process.argv.slice(2) : ['src'];
   for (const root of roots) {
     for (const file of files(root)) {
       const src = readFileSync(file, 'utf8');
       const names = astryxNames(src);
       for (const m of src.matchAll(/<([A-Z][A-Za-z0-9]*)(?=[\s/>])/g)) {
         const name = names.get(m[1]);
         if (!name) continue;
         const {list, hasSpread} = readAttrs(src, m.index + m[0].length);
         const at = (rule, msg) =>
           found.push(`${file}:${src.slice(0, m.index).split('\n').length} [${rule}] ${msg}`);
         for (const a of list) {
           if (SPACING_TAGS.has(name) && SPACING.has(a.name)) {
             const lit = a.kind === 'string' ? a.value : /^(['"])(.*)\1$/.exec(a.value)?.[2];
             const num = a.kind === 'expr' && /^-?\d+(\.\d+)?$/.test(a.value) ? Number(a.value) : null;
             if (lit != null) at('spacing', `${name} ${a.name}="${lit}": use a numeric step such as ${a.name}={4}`);
             else if (num !== null && !STEPS.has(num)) at('spacing', `${name} ${a.name}={${num}} is not a step (0, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10)`);
           }
           if (name === 'Stack' && a.name === 'direction' && a.kind === 'string' && !['horizontal', 'vertical'].includes(a.value))
             at('direction', `Stack direction="${a.value}": use 'horizontal' or 'vertical'`);
           if (name === 'Text' && a.name === 'variant') at('text', 'Text has no variant prop: use type, or Heading for headings');
           if (name === 'Icon' && a.name === 'name') at('icon', 'Icon takes icon={...}, not name');
         }
         if (NEEDS_LABEL.has(name) && !hasSpread && !list.some(a => a.name === 'label'))
           at('label', `${name} needs a label (it is also the accessible name)`);
       }
     }
   }
   console.log(found.length ? found.join('\n') : 'no findings');
   process.exit(found.length ? 1 : 0);
   ```

   Run `node scripts/check-astryx-usage.mjs src` in CI and in a pre-commit hook. Extend `NEEDS_LABEL` and the rule list when your
   own conventions grow.
5. Optional: the docs site route handlers expose `/llms.txt` and an MCP endpoint with `search` and `get` tools
   (`astryx:apps/docsite/src/app/llms.txt/route.ts`, `astryx:apps/docsite/src/app/mcp/route.ts`). The `llms.txt` text itself tells
   agents to prefer the CLI over crawling. Whether the public site serves the endpoint was not verified.
6. Measure, borrowing the project's method (`astryx:apps/docsite/src/content/blog/posts/vibe-tests.md`): write prompts that describe the
   user experience rather than components, run each in a fresh context with no memory of earlier sessions, compare 3 to 5 candidate
   setups (for example with and without the rules block), and let a separate agent judge instead of self-scoring.

## Verification checklist

- `node scripts/check-astryx-usage.mjs src` exits 0 on the generated code, and a deliberate `gap="md"` makes it exit 1.
- TypeScript passes; props the docs list as required are present; no import path outside `@astryxdesign/*` exports.
- Browser: keyboard path works, focus ring visible, dark mode, 320px width, reduced motion, no console errors.
- The page has one h1, one main landmark and labelled navigation landmarks if it uses AppShell.
- Generated block and your rules are both present in `AGENTS.md`, and a fresh agent session actually reads them.

## Pitfalls

- Stale sources mislead agents: theme READMEs show `XDSTheme` and a blog example uses `gap="md"`; tell agents to trust `.doc.mjs` and
  the CLI over READMEs and posts.
- `docs/design/*` are mostly drafts; only records with `authority: current` govern (`astryx:docs/README.md`).
- The checker cannot see props passed through variables, wrapper components or generics.

## Upstream references

`astryx:AGENTS.md`, `astryx:CLAUDE.md`, `astryx:packages/core/README.md`, `astryx:packages/core/docs.mjs`,
`astryx:docs/architecture/cli-surface.md`, `astryx:docs/contributing/api-conventions.md` (naming grammar: `is`/`has` booleans,
`on` callbacks, `<verb>Action` transitions, `start`/`end` logical sides).

## Licence notes

Astryx is MIT (`astryx:LICENSE`). The rules text and script above are original and call no upstream code. Do not paste upstream
`AGENTS.md` blocks verbatim into other projects without keeping the copyright notice; let `astryx init` generate its own block.
