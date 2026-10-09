"""Guards that keep the repository safe to publish: no secrets, no local paths, no upstream code."""

import os
import re
import subprocess
import unittest
from pathlib import Path

from tests import helpers

ROOT = helpers.ROOT
SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key id"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"), "GitHub token"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{30,}"), "GitHub fine-grained token"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "API secret key"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"(?i)\b(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*['\"][A-Za-z0-9/+_-]{16,}['\"]"), "hard-coded credential"),
]
LOCAL_PATH_RE = re.compile(r"(/Users/[A-Za-z0-9._-]+|/home/[a-z][A-Za-z0-9._-]+/|C:\\Users\\)")
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".txt", ".html", ".css", ".js", ".mjs", ".ts", ".tsx", ".sh", ""}


def tracked_files():
    proc = subprocess.run(["git", "ls-files", "-z"], cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        return None
    return [ROOT / p for p in proc.stdout.decode("utf-8").split("\0") if p]


class HygieneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = tracked_files()
        # Files not yet added to git are checked as well, so problems are caught before the commit.
        proc = subprocess.run(["git", "ls-files", "-z", "--others", "--exclude-standard"], cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        extra = [ROOT / p for p in proc.stdout.decode("utf-8").split("\0") if p] if proc.returncode == 0 else []
        cls.files = (cls.files or []) + extra

    def setUp(self):
        if not self.files:
            self.skipTest("not a git checkout")

    def text_files(self):
        for path in self.files:
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and path.stat().st_size < 2_000_000:
                yield path

    def test_no_secrets(self):
        for path in self.text_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern, label in SECRET_PATTERNS:
                match = pattern.search(text)
                self.assertIsNone(match, "%s looks like it contains a %s" % (path.relative_to(ROOT), label))

    def test_no_machine_specific_paths(self):
        allowed_files = {"tests/unit/test_repo_hygiene.py"}
        for path in self.text_files():
            rel = path.relative_to(ROOT).as_posix()
            if rel in allowed_files:
                continue
            m = LOCAL_PATH_RE.search(path.read_text(encoding="utf-8", errors="ignore"))
            self.assertIsNone(m, "%s contains a machine-specific path: %s" % (rel, m.group(0) if m else ""))

    def test_upstream_sources_are_never_tracked(self):
        offenders = [p.relative_to(ROOT).as_posix() for p in self.files if p.relative_to(ROOT).parts[0] == "sources" and p.name != "README.md"]
        self.assertEqual(offenders, [])

    def test_local_state_and_caches_are_ignored(self):
        bad = [p.relative_to(ROOT).as_posix() for p in self.files
               if ".state" in p.parts or "__pycache__" in p.parts or p.suffix == ".pyc" or p.name == ".DS_Store" or "node_modules" in p.parts
               or ".remember" in p.parts or p.name.startswith(".env")]
        self.assertEqual(bad, [])

    def test_gitignore_covers_the_important_cases(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for needle in ("/sources/*", "!/sources/README.md", "/.state/", "node_modules/", "__pycache__/", ".env", ".DS_Store", ".remember/", ".claude/"):
            self.assertIn(needle, text)
        for sample in ("sources/lenis/package.json", ".state/lock.json", "node_modules/x/index.js", ".env", ".remember/now.md"):
            proc = subprocess.run(["git", "check-ignore", "-q", sample], cwd=str(ROOT))
            self.assertEqual(proc.returncode, 0, "%s should be ignored" % sample)
        proc = subprocess.run(["git", "check-ignore", "-q", "sources/README.md"], cwd=str(ROOT))
        self.assertEqual(proc.returncode, 1, "sources/README.md must stay tracked")

    def test_no_large_or_binary_files(self):
        for path in self.files:
            if path.is_file():
                self.assertLess(path.stat().st_size, 1_500_000, "%s is large; do not commit bulky files" % path.relative_to(ROOT))

    def test_license_and_attribution_files_exist(self):
        for name in ("LICENSE",):
            self.assertTrue((ROOT / name).is_file(), name)

    def test_every_python_file_compiles_with_the_running_interpreter(self):
        # CI runs this on every supported Python version (3.9+), so syntax newer than 3.9 is caught there.
        for folder in ("scripts", "tests"):
            for path in (ROOT / folder).rglob("*.py"):
                compile(path.read_text(encoding="utf-8"), str(path), "exec")


if __name__ == "__main__":
    unittest.main()
