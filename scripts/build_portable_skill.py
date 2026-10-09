#!/usr/bin/env python3
"""Assemble a self-contained, portable copy of the Design Sensei skill.

``design-sensei package-skill``             write dist/design-sensei/ (a ready-to-copy skill folder)
``design-sensei package-skill --zip``       also write dist/design-sensei-skill-<version>.zip (+ .sha256)
``design-sensei package-skill --out DIR``   build under DIR instead of dist/

Why: a skill folder that is *copied* (not symlinked, not plugin-installed) cannot find the
catalog, knowledge notes and scripts that live outside ``skills/design-sensei/``. The bundle
puts everything next to the skill so that copying the folder to ``~/.claude/skills/`` is all
an install needs:

    design-sensei/                 <- the skill folder (copy this)
      SKILL.md references/ patterns/ config/ scripts/design-sensei
      toolkit/
        bundle.json                marker: this toolkit is a bundle (library defaults to ~/.design-sensei)
        catalog/ knowledge/        the registry, schemas, pattern catalog and notes
        scripts/                   every Python module of the command line
        docs/ examples/glass-hero  user documentation and the original example
        LICENSE ATTRIBUTION.md NOTICE

The launcher finds ``<skill folder>/toolkit`` on its own (see skills/design-sensei/scripts/design-sensei).

The only transformation of source files: relative paths that leave the skill folder to reach the
repository (``../../../knowledge/...`` in references/ and patterns/, ``${CLAUDE_SKILL_DIR}/../../catalog/...``
in SKILL.md) are rewritten to the bundled toolkit (``../toolkit/knowledge/...``,
``${CLAUDE_SKILL_DIR}/toolkit/catalog/...``). Nothing else in any file changes, and the sources
in the repository are never modified. Every relative Markdown link in the skill and the knowledge notes is checked (dead links in docs/ only warn).

Never included: upstream clones (sources/), local state (.state/), git data, secrets, caches, tests
and anything the repository's .gitignore matches. A stray file of that kind inside an included
folder stops the build instead of being skipped silently. Output is deterministic: sorted entries,
fixed timestamps, normalised permissions (so the zip is byte-identical for the same input, Python
and zlib).
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import posixpath
import re
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Dict, Iterator, List, NamedTuple, Optional, Sequence, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dslib import EXIT_FAILURE, EXIT_OK, __version__
from dslib.cli import add_global_options, eprint, fail, run_with_layout
from dslib.paths import BUNDLE_MARKER, Layout

SKILL_NAME = "design-sensei"
TOOLKIT_DIRNAME = "toolkit"
FIXED_DATE = (1980, 1, 1, 0, 0, 0)  # zip's earliest timestamp
FIXED_EPOCH = 315532800  # the same instant (UTC) for files written to disk

# What goes into toolkit/, relative to the repository root.
TOOLKIT_DIRS = ("catalog", "knowledge", "scripts", "docs", "examples/glass-hero")
TOOLKIT_FILES = ("LICENSE", "ATTRIBUTION.md", "CONTRIBUTING.md", "SECURITY.md")  # the last two are linked from docs/ and knowledge/
MAINTAINER_DOCS = frozenset({"docs/publishing.md"})  # release steps; nothing in the bundle links to it

# Names that are never part of a bundle. Mirrors the secrets / sources / state categories of .gitignore;
# the real .gitignore is applied on top, so new ignore rules are honoured automatically.
NOISE_DIRS = frozenset({"__pycache__"})
NOISE_FILES = ("*.pyc", "*.pyo", ".DS_Store", "._*", "Thumbs.db", "Desktop.ini", "*.swp", "*.swo", "*~")
FORBIDDEN_DIRS = frozenset({".git", ".state", "sources", "node_modules"})
FORBIDDEN_FILES = (".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "id_rsa*", "id_ed25519*", "credentials*.json", "secrets.*", ".netrc", ".npmrc")
ALLOWED_FORBIDDEN_NAMES = frozenset({".env.example"})

# Dead relative links stop the build for the skill itself and the knowledge base; in the other bundled
# Markdown (docs/, examples/, top-level files) they are reported as warnings, because documentation may
# legitimately point at repository-only files such as the README.
LENIENT_LINK_PREFIXES = ("toolkit/docs/", "toolkit/examples/", "toolkit/CONTRIBUTING.md", "toolkit/SECURITY.md")

REQUIRED = (
    "SKILL.md", "scripts/design-sensei", "config/defaults.yaml",
    "toolkit/" + BUNDLE_MARKER, "toolkit/LICENSE", "toolkit/ATTRIBUTION.md", "toolkit/NOTICE",
    "toolkit/catalog/sources.yaml", "toolkit/catalog/patterns.yaml", "toolkit/catalog/licenses.yaml",
    "toolkit/knowledge/pattern-index/pattern-index.json", "toolkit/scripts/design_sensei.py", "toolkit/scripts/dslib/paths.py",
)

# A relative path that climbs out of the skill folder to a top-level item of the repository.
_ESCAPE_RE = re.compile(r"(?:^|(?<=[\s(`'\"<\[=])|(?<=\}/))((?:\.\./)+)((?:catalog|knowledge|docs|examples|scripts)(?=[/)\s`'\"#]|$)|ATTRIBUTION\.md|LICENSE)")
_LINK_RE = re.compile(r"\]\((?!https?://|#|mailto:)([^)#\s]+)")
_CODE_RE = re.compile(r"^[ \t]*(```|~~~).*?^[ \t]*\1[^\n]*$|`[^`\n]*`", re.S | re.M)  # fenced blocks and inline code: their "](" is not a link

NOTICE_TEXT = """Design Sensei %(version)s - portable skill bundle

Design Sensei itself (skill, command line, catalog, knowledge notes, recipes, documentation)
is MIT licensed; see LICENSE.

This bundle contains NO upstream source code. The knowledge notes describe upstream projects
in their own words and cite files by path; short quotations (a few lines, with a citation) come
only from permissively licensed sources. ATTRIBUTION.md lists every upstream project with its
licence, the pinned commit, what may be reused and under which terms. Upstream projects are
downloaded on demand, at the pinned commit, to ~/.design-sensei/sources/ (never into this folder)
and keep their own licences and notices there: read them before copying any code, and keep the
copyright and licence notice of whatever you reuse. Items marked "needs_human_review" in
catalog/licenses.yaml are not settled.

This text is not legal advice. See docs/licensing.md.
"""


class BuildError(Exception):
    """The bundle cannot be assembled safely; nothing is written."""


class Entry(NamedTuple):
    arcname: str  # POSIX path relative to the skill folder
    data: bytes
    mode: int  # 0o644 or 0o755


class BuildResult(NamedTuple):
    directory: Path
    zip_path: Optional[Path]
    zip_sha256: Optional[str]
    files: int
    bytes: int
    zip_bytes: int
    warnings: List[str]


# --- .gitignore -------------------------------------------------------------------------------------------

def _glob_to_regex(glob: str) -> str:
    out = []  # type: List[str]
    i = 0
    while i < len(glob):
        c = glob[i]
        if glob.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif glob.startswith("/**", i) and i + 3 == len(glob):
            out.append("/.*")
            i += 3
        elif c == "*":
            out.append(".*" if glob.startswith("**", i) else "[^/]*")
            i += 2 if glob.startswith("**", i) else 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        elif c == "[":
            end = glob.find("]", i + 2)
            if end == -1:
                out.append(re.escape(c))
                i += 1
            else:
                body = glob[i + 1:end]
                out.append("[" + ("^" + body[1:] if body[:1] == "!" else body) + "]")
                i = end + 1
        elif c == "\\" and i + 1 < len(glob):
            out.append(re.escape(glob[i + 1]))
            i += 2
        else:
            out.append(re.escape(c))
            i += 1
    return "".join(out)


class IgnoreRules(object):
    """The subset of .gitignore syntax this repository uses (comments, negation, anchoring, dir-only, * ? ** [])."""

    def __init__(self, text: str = ""):
        self.rules = []  # type: List[Tuple[str, "re.Pattern[str]", bool, bool]]
        for raw in text.splitlines():
            line = raw.rstrip()
            if not line or line.startswith("#"):
                continue
            negate = line.startswith("!")
            body = line[1:] if negate else line
            dir_only = body.endswith("/")
            body = body.rstrip("/")
            anchored = "/" in body
            regex = _glob_to_regex(body.lstrip("/"))
            compiled = re.compile(("^%s$" if anchored else "^(?:.*/)?%s$") % regex)
            self.rules.append((line, compiled, negate, dir_only))

    def matching_rule(self, rel: str, is_dir: bool) -> Optional[str]:
        """Return the .gitignore line that ignores ``rel`` (or one of its parent folders), else None."""
        parts = rel.split("/")
        for i in range(1, len(parts) + 1):
            sub = "/".join(parts[:i])
            sub_is_dir = is_dir or i < len(parts)
            verdict = None  # type: Optional[str]
            for line, regex, negate, dir_only in self.rules:
                if dir_only and not sub_is_dir:
                    continue
                if regex.match(sub):
                    verdict = None if negate else line
            if verdict:
                return verdict
        return None


class Policy(object):
    """Decides for every path below the repository root: include, skip as noise, or refuse."""

    def __init__(self, rules: IgnoreRules):
        self.rules = rules

    def classify(self, rel: str, is_dir: bool) -> Tuple[str, str]:
        name = posixpath.basename(rel)
        if is_dir and name in NOISE_DIRS:
            return "skip", "cache folder"
        if not is_dir and any(fnmatch.fnmatchcase(name, g) for g in NOISE_FILES):
            return "skip", "cache or editor file"
        if is_dir and name in FORBIDDEN_DIRS:
            return "deny", "%s/ is never part of a bundle (upstream clones, local state, git data)" % name
        if not is_dir and name not in ALLOWED_FORBIDDEN_NAMES and any(fnmatch.fnmatchcase(name, g) for g in FORBIDDEN_FILES):
            return "deny", "looks like a secret or credential"
        rule = self.rules.matching_rule(rel, is_dir)
        if rule:
            return "deny", "matched by .gitignore rule %r" % rule
        return "ok", ""


# --- collecting -------------------------------------------------------------------------------------------

def _walk(repo: Path, rel_dir: str, policy: Policy) -> Iterator[Tuple[str, Path]]:
    """Yield (repo-relative POSIX path, absolute path) of every includable file below ``rel_dir``, sorted."""
    base = repo / rel_dir
    if not base.is_dir():
        raise BuildError("missing folder %s" % rel_dir)
    for dirpath, dirnames, filenames in os.walk(str(base)):
        current = Path(dirpath)
        keep = []  # type: List[str]
        for name in sorted(dirnames):
            rel = current.joinpath(name).relative_to(repo).as_posix()
            if os.path.islink(str(current / name)):
                raise BuildError("%s is a symbolic link; a portable bundle contains regular files only" % rel)
            verdict, why = policy.classify(rel, True)
            if verdict == "deny":
                raise BuildError("refusing to bundle %s/: %s" % (rel, why))
            if verdict == "ok":
                keep.append(name)
        dirnames[:] = keep
        for name in sorted(filenames):
            full = current / name
            rel = full.relative_to(repo).as_posix()
            if os.path.islink(str(full)):
                raise BuildError("%s is a symbolic link; a portable bundle contains regular files only" % rel)
            verdict, why = policy.classify(rel, False)
            if verdict == "deny":
                raise BuildError("refusing to bundle %s: %s" % (rel, why))
            if verdict == "ok":
                yield rel, full


def _mode_of(path: Path) -> int:
    return 0o755 if os.stat(str(path)).st_mode & 0o111 else 0o644


def relocate_links(text: str, depth: int) -> Tuple[str, int]:
    """Rewrite paths that leave the skill folder for the repository so they point into ``toolkit/``.

    ``depth`` is how many folders below the skill folder the file (or, for ${CLAUDE_SKILL_DIR}/..., the
    base) sits. In the repository the skill folder is two levels below the root, so a path with
    ``depth + 2`` leading ``../`` reaches a top-level repository item; in the bundle that item is
    ``toolkit/<item>`` directly below the skill folder.
    """
    count = [0]

    def repl(match: "re.Match[str]") -> str:
        ups = len(match.group(1)) // 3
        if ups != depth + 2:
            return match.group(0)
        count[0] += 1
        return "../" * depth + TOOLKIT_DIRNAME + "/" + match.group(2)

    return _ESCAPE_RE.sub(repl, text), count[0]


def _check_links(entries: Dict[str, Entry]) -> List[str]:
    """Raise BuildError for dead relative links in strict files; return the dead links of lenient ones."""
    files = set(entries)
    folders = set()  # type: set
    for name in files:
        parent = posixpath.dirname(name)
        while parent:
            folders.add(parent)
            parent = posixpath.dirname(parent)
    broken, tolerated = [], []  # type: List[str], List[str]
    for name in sorted(files):
        if not name.endswith(".md"):
            continue
        text = entries[name].data.decode("utf-8", "replace")
        for target in _LINK_RE.findall(_CODE_RE.sub("", text)):
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), target))
            if resolved.startswith("..") or (resolved not in files and resolved not in folders):
                (tolerated if name.startswith(LENIENT_LINK_PREFIXES) else broken).append("%s -> %s" % (name, target))
    if broken:
        raise BuildError("relative links that do not resolve inside the bundle (%d), first: %s" % (len(broken), "; ".join(broken[:5])))
    return tolerated


def collect(root: Path) -> Tuple[Dict[str, Entry], List[str]]:
    """Read every file of the bundle from the repository at ``root``: (entries by name, warnings). Raises BuildError; writes nothing."""
    root = Path(root)
    skill_src = root / "skills" / SKILL_NAME
    if not (skill_src / "SKILL.md").is_file():
        raise BuildError("%s is not a Design Sensei checkout (no skills/%s/SKILL.md); package-skill must run from a repository or plugin checkout, not from a bundle" % (root, SKILL_NAME))
    gitignore = root / ".gitignore"
    policy = Policy(IgnoreRules(gitignore.read_text(encoding="utf-8") if gitignore.is_file() else ""))
    entries = {}  # type: Dict[str, Entry]

    def add(arcname: str, data: bytes, mode: int) -> None:
        entries[arcname] = Entry(arcname, data, mode)

    relocated = 0
    for rel, full in _walk(root, "skills/" + SKILL_NAME, policy):
        arc = rel[len("skills/" + SKILL_NAME + "/"):]
        data = full.read_bytes()
        if arc.endswith(".md"):
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                raise BuildError("%s is not valid UTF-8" % rel)
            text, n = relocate_links(text, arc.count("/"))
            relocated += n
            data = text.encode("utf-8")
        add(arc, data, _mode_of(full))

    for top in TOOLKIT_DIRS:
        for rel, full in _walk(root, top, policy):
            if rel in MAINTAINER_DOCS:
                continue
            add(TOOLKIT_DIRNAME + "/" + rel, full.read_bytes(), _mode_of(full))
    for name in TOOLKIT_FILES:
        path = root / name
        verdict, why = policy.classify(name, False)
        if not path.is_file() or verdict != "ok":
            raise BuildError("%s is required in the bundle but %s" % (name, "is missing" if not path.is_file() else why))
        add(TOOLKIT_DIRNAME + "/" + name, path.read_bytes(), 0o644)

    add(TOOLKIT_DIRNAME + "/NOTICE", (NOTICE_TEXT % {"version": __version__}).encode("utf-8"), 0o644)
    info = {
        "format": 1,
        "kind": "portable-skill",
        "name": SKILL_NAME,
        "version": __version__,
        "library_home_default": "~/.design-sensei",
        "link_rewrites": "paths leaving the skill folder for the repository (../../../knowledge/..., ${CLAUDE_SKILL_DIR}/../../catalog/...) now point into toolkit/",
        "excluded": ["sources/", ".state/", ".git", "tests/", ".claude-plugin/", "bin/", "docs/publishing.md", "everything matched by .gitignore"],
    }
    add(TOOLKIT_DIRNAME + "/" + BUNDLE_MARKER, (json.dumps(info, indent=2, sort_keys=True) + "\n").encode("utf-8"), 0o644)

    missing = [name for name in REQUIRED if name not in entries]
    if missing:
        raise BuildError("the bundle would be incomplete, missing: %s" % ", ".join(missing))
    if not entries["scripts/design-sensei"].mode & 0o111:
        raise BuildError("skills/%s/scripts/design-sensei must be executable" % SKILL_NAME)
    warnings = _check_links(entries)
    return dict(sorted(entries.items())), ["dead link in the bundled docs: " + w for w in warnings]


# --- writing ----------------------------------------------------------------------------------------------

def _inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def write_directory(entries: Dict[str, Entry], dest: Path) -> None:
    if dest.exists():
        if (dest / TOOLKIT_DIRNAME / BUNDLE_MARKER).is_file():
            shutil.rmtree(str(dest))
        elif dest.is_dir() and not any(dest.iterdir()):
            pass
        else:
            raise BuildError("%s exists and is not a previous bundle; remove it or choose another --out" % dest)
    for arc, entry in entries.items():
        target = dest.joinpath(*arc.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(entry.data)
        os.chmod(str(target), entry.mode)
        os.utime(str(target), (FIXED_EPOCH, FIXED_EPOCH))


def write_zip(entries: Dict[str, Entry], zip_path: Path) -> str:
    """Write a deterministic zip whose single top-level folder is ``design-sensei/``. Returns its SHA-256."""
    tmp = zip_path.with_name(zip_path.name + ".part")
    with zipfile.ZipFile(str(tmp), "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for arc, entry in entries.items():
            info = zipfile.ZipInfo(SKILL_NAME + "/" + arc, FIXED_DATE)
            info.create_system = 3  # Unix, so the permission bits below are honoured on extraction
            info.external_attr = (0o100000 | entry.mode) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, entry.data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    digest = hashlib.sha256(tmp.read_bytes()).hexdigest()
    os.replace(str(tmp), str(zip_path))
    zip_path.with_name(zip_path.name + ".sha256").write_text("%s  %s\n" % (digest, zip_path.name), encoding="utf-8")
    return digest


def build(root: Path, out: Path, make_zip: bool = False) -> BuildResult:
    root, out = Path(root).resolve(), Path(out).resolve()
    for part in ("skills", "catalog", "knowledge", "scripts", "docs", "examples"):
        if _inside(out, root / part):
            raise BuildError("--out %s is inside %s/, which is bundled; choose a folder outside it (default: dist/)" % (out, part))
    entries, warnings = collect(root)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / SKILL_NAME
    write_directory(entries, dest)
    zip_path, digest, zip_size = None, None, 0
    if make_zip:
        zip_path = out / ("%s-skill-%s.zip" % (SKILL_NAME, __version__))
        digest = write_zip(entries, zip_path)
        zip_size = zip_path.stat().st_size
    return BuildResult(dest, zip_path, digest, len(entries), sum(len(e.data) for e in entries.values()), zip_size, warnings)


# --- command line -----------------------------------------------------------------------------------------

def _kb(n: int) -> str:
    return "%.1f MB" % (n / 1048576.0) if n >= 1048576 else "%d KB" % ((n + 1023) // 1024)


def cmd_package_skill(layout: Layout, args: argparse.Namespace) -> int:
    if layout.is_bundle():
        return fail("this is already a portable bundle; run package-skill from a repository or plugin checkout")
    out = Path(args.out).expanduser() if args.out else layout.root / "dist"
    try:
        result = build(layout.root, out, make_zip=args.zip)
    except BuildError as exc:
        return fail(str(exc))
    except OSError as exc:
        return fail("cannot write the bundle: %s" % exc)
    for warning in result.warnings:
        eprint("warning: " + warning)
    print("portable skill: %s  (%d files, %s)" % (result.directory, result.files, _kb(result.bytes)))
    if result.zip_path:
        print("zip:            %s  (%s)" % (result.zip_path, _kb(result.zip_bytes)))
        print("sha256:         %s" % result.zip_sha256)
    print("install:        cp -R '%s' ~/.claude/skills/        (or unzip the archive there)" % result.directory)
    print("check:          ~/.claude/skills/%s/scripts/%s doctor --brief" % (SKILL_NAME, SKILL_NAME))
    return EXIT_OK


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--out", metavar="DIR", help="build below this folder (default: <checkout>/dist); the skill folder is DIR/%s/" % SKILL_NAME)
    parser.add_argument("--zip", action="store_true", help="also write DIR/%s-skill-<version>.zip and its .sha256 (deterministic, for GitHub releases)" % SKILL_NAME)
    add_global_options(parser)
    parser.set_defaults(func=lambda a: run_with_layout(a, cmd_package_skill))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="build_portable_skill.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(parser)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
