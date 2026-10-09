"""Shared helpers for the Design Sensei test-suite (standard library only)."""

from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from dslib import yamlite  # noqa: E402
from dslib.paths import Layout  # noqa: E402

GIT = shutil.which("git")
NEEDS_GIT = unittest.skipUnless(GIT, "git is not installed")


def make_source(sid: str = "alpha", **overrides: Any) -> Dict[str, Any]:
    data = {
        "id": sid, "name": sid.title(), "url": "https://github.com/example/%s" % sid, "type": "git_repository",
        "category": "ui_components", "acquisition_method": "git_shallow", "default_branch": "main",
        "pinned_commit": "a" * 40, "license": "MIT", "license_status": "verified",
        "redistribution_status": "redistributable_with_notice", "attribution": "%s by Example" % sid.title(),
        "local_path": sid, "frameworks": ["react"], "tags": ["demo"], "last_checked": "2026-01-01",
        "inspection_status": "inspected_local", "notes": "Fixture source.",
    }
    data.update(overrides)
    return data


def make_pattern(pid: str = "demo-pattern", source_ids: Optional[List[str]] = None, **overrides: Any) -> Dict[str, Any]:
    data = {
        "id": pid, "title": pid.replace("-", " ").title(), "category": "hero",
        "summary": "A fixture pattern that is long enough to satisfy the schema minimum.",
        "provenance": "upstream", "tags": ["demo"], "source_ids": source_ids if source_ids is not None else ["alpha"],
        "frameworks": ["react"], "dependencies": [], "implementation_status": "reference_only",
        "use_cases": ["landing page"], "performance": {"gpu_intensity": "none", "fallback_required": False},
        "accessibility": {"motion": "none", "reduced_motion_alternative": False}, "source_paths": [],
    }
    data.update(overrides)
    return data


def make_toolkit(tmp: Path, sources: Optional[Sequence[Dict[str, Any]]] = None, patterns: Optional[Sequence[Dict[str, Any]]] = None,
                 reviews: Optional[Sequence[Dict[str, Any]]] = None, docs: Optional[Dict[str, str]] = None, home: Optional[Path] = None,
                 pattern_files: Optional[Dict[str, Sequence[Dict[str, Any]]]] = None) -> Layout:
    """Create a miniature toolkit root (real schemas + fixture catalog) and return its Layout."""
    root = tmp / "toolkit root"  # space on purpose
    if root.exists():
        shutil.rmtree(str(root))
    (root / "catalog" / "schemas").mkdir(parents=True)
    for schema in (ROOT / "catalog" / "schemas").glob("*.json"):
        shutil.copy(str(schema), str(root / "catalog" / "schemas" / schema.name))
    (root / "skills" / "design-sensei" / "config").mkdir(parents=True)
    for name in ("defaults.yaml", "config.example.yaml"):
        shutil.copy(str(ROOT / "skills" / "design-sensei" / "config" / name), str(root / "skills" / "design-sensei" / "config" / name))
    (root / "knowledge").mkdir()
    sources = list(sources if sources is not None else [make_source("alpha")])
    (root / "catalog" / "sources.yaml").write_text(yamlite.dumps({"schema_version": 1, "sources": sources}), encoding="utf-8")
    patterns = list(patterns if patterns is not None else [])
    (root / "catalog" / "patterns.yaml").write_text(yamlite.dumps({"schema_version": 1, "patterns": patterns}), encoding="utf-8")
    for name, items in (pattern_files or {}).items():
        (root / "catalog" / "patterns.d").mkdir(exist_ok=True)
        (root / "catalog" / "patterns.d" / name).write_text(yamlite.dumps({"schema_version": 1, "patterns": list(items)}), encoding="utf-8")
    licenses = {
        "schema_version": 1,
        "policy": {"spdx": {"MIT": {"class": "permissive", "requires": ["keep notice"]}, "Apache-2.0": {"class": "permissive", "requires": []},
                            "LicenseRef-Custom-Terms": {"class": "restricted", "requires": []}},
                   "unknown_handling": "Treat unknown licenses as reference only."},
        "reviews": list(reviews or []),
    }
    (root / "catalog" / "licenses.yaml").write_text(yamlite.dumps(licenses), encoding="utf-8")
    for rel, text in (docs or {}).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    home = home or (tmp / "library home")
    return Layout(root, home, "test")


class Upstream(object):
    """A real local git repository used as an 'upstream' (cloned via file://)."""

    def __init__(self, base: Path, name: str = "upstream repo"):
        self.path = base / name
        self.path.mkdir(parents=True)
        self._git("init", "-q", "-b", "main")

    @property
    def url(self) -> str:
        return self.path.as_uri()

    def _git(self, *args: str) -> str:
        env = dict(os.environ, GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="t@example.com")
        out = subprocess.run([GIT or "git", "-C", str(self.path)] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=env)
        if out.returncode != 0:
            raise RuntimeError("git %s failed: %s" % (" ".join(args), out.stderr))
        return out.stdout.strip()

    def commit(self, files: Dict[str, str], message: str = "commit") -> str:
        for rel, text in files.items():
            target = self.path / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        self._git("add", "-A")
        self._git("commit", "-q", "-m", message)
        return self._git("rev-parse", "HEAD")


def run_cli(argv: Sequence[str], env: Optional[Dict[str, str]] = None) -> Tuple[int, str, str]:
    """Run the real command line in a subprocess; returns (exit code, stdout, stderr)."""
    full_env = dict(os.environ)
    full_env.pop("DESIGN_SENSEI_HOME", None)
    full_env.pop("DESIGN_SENSEI_ROOT", None)
    full_env.update(env or {})
    proc = subprocess.run([sys.executable, str(SCRIPTS / "design_sensei.py")] + list(argv), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True, env=full_env, cwd=str(ROOT))
    return proc.returncode, proc.stdout, proc.stderr


def call_main(main, argv: Sequence[str]) -> Tuple[int, str, str]:
    """Call a ``main(argv)`` in-process capturing output (fast, for unit tests)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = main(list(argv))
        except SystemExit as exc:  # argparse
            code = int(exc.code) if isinstance(exc.code, int) else 1
    return code, out.getvalue(), err.getvalue()


class TempDirTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="ds test ")
        self.tmp = Path(self._tmp.name).resolve()
        self.addCleanup(self._tmp.cleanup)
