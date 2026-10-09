import os
import unittest
from pathlib import Path

from tests import helpers
from dslib import gitops
from dslib.paths import LayoutError, find_project_config, resolve_layout


class LayoutTests(helpers.TempDirTest):
    def test_flag_beats_env_beats_dev_checkout(self):
        layout = helpers.make_toolkit(self.tmp)
        env = {"DESIGN_SENSEI_HOME": str(self.tmp / "from env")}
        self.assertEqual(resolve_layout(root=str(layout.root), home=str(self.tmp / "from flag"), env=env).home.name, "from flag")
        self.assertEqual(resolve_layout(root=str(layout.root), env=env).home.name, "from env")

    def test_dev_checkout_uses_repo_as_home(self):
        layout = helpers.make_toolkit(self.tmp)
        (layout.root / ".git").mkdir()
        resolved = resolve_layout(root=str(layout.root), env={})
        self.assertEqual(resolved.home, layout.root.resolve())
        self.assertIn("development checkout", resolved.home_reason)
        self.assertEqual(resolved.sources_dir, layout.root.resolve() / "sources")

    def test_installed_plugin_uses_user_library(self):
        layout = helpers.make_toolkit(self.tmp)
        resolved = resolve_layout(root=str(layout.root), env={})
        self.assertEqual(resolved.home, Path.home() / ".design-sensei")

    def test_missing_catalog_is_a_clear_error(self):
        with self.assertRaises(LayoutError) as ctx:
            resolve_layout(root=str(self.tmp), env={})
        self.assertIn("DESIGN_SENSEI_ROOT", str(ctx.exception))

    def test_paths_with_spaces(self):
        layout = helpers.make_toolkit(self.tmp)
        self.assertIn(" ", str(layout.root))
        self.assertIn(" ", str(layout.home))
        self.assertEqual(layout.source_path({"id": "x", "local_path": "my dir"}), layout.sources_dir / "my dir")

    def test_project_config_discovery_walks_up(self):
        project = self.tmp / "proj"
        (project / "a" / "b").mkdir(parents=True)
        (project / ".design-sensei.yaml").write_text("motion_intensity: 3\n")
        self.assertEqual(find_project_config(project / "a" / "b"), (project / ".design-sensei.yaml").resolve())
        self.assertIsNone(find_project_config(self.tmp / "nowhere") if (self.tmp / "nowhere").exists() else None)

    def test_pattern_files_include_drop_ins_sorted(self):
        layout = helpers.make_toolkit(self.tmp, pattern_files={"b.yaml": [], "a.yaml": []})
        names = [p.name for p in layout.pattern_files()]
        self.assertEqual(names, ["patterns.yaml", "a.yaml", "b.yaml"])


class GitOpsTests(unittest.TestCase):
    def test_classify_error(self):
        self.assertEqual(gitops.classify_error("fatal: unable to access 'x': Could not resolve host: github.com"), "network")
        self.assertEqual(gitops.classify_error("fatal: repository 'x' not found"), "not_found")
        self.assertEqual(gitops.classify_error("fatal: could not read Username for 'https://github.com': terminal prompts disabled"), "auth")
        self.assertEqual(gitops.classify_error("error: something odd"), "git_error")

    def test_retries_transient_then_succeeds(self):
        calls = []
        delays = []

        def op():
            calls.append(1)
            if len(calls) < 3:
                raise gitops.GitError("net", 1, "", "network")
            return "ok"

        self.assertEqual(gitops.with_retries(op, attempts=3, base_delay=1.0, sleep=delays.append), "ok")
        self.assertEqual(len(calls), 3)
        self.assertEqual(delays, [1.0, 2.0])

    def test_retries_stop_on_permanent_error(self):
        calls = []

        def op():
            calls.append(1)
            raise gitops.GitError("nope", 1, "", "not_found")

        with self.assertRaises(gitops.GitError):
            gitops.with_retries(op, attempts=3, sleep=lambda s: None)
        self.assertEqual(len(calls), 1)

    def test_retries_give_up_after_attempts(self):
        calls = []

        def op():
            calls.append(1)
            raise gitops.GitError("net", 1, "", "network")

        with self.assertRaises(gitops.GitError):
            gitops.with_retries(op, attempts=2, sleep=lambda s: None)
        self.assertEqual(len(calls), 2)

    def test_normalize_url(self):
        self.assertEqual(gitops.normalize_url("https://GitHub.com/A/B.git/"), "https://github.com/a/b")
        self.assertEqual(gitops.normalize_url("https://github.com/a/b"), gitops.normalize_url("https://github.com/A/B.git"))

    def test_missing_git_raises_clear_error(self):
        old = os.environ.get("PATH", "")
        os.environ["PATH"] = ""
        try:
            self.assertIsNone(gitops.git_executable())
            with self.assertRaises(gitops.GitError) as ctx:
                gitops.run_git(["--version"])
            self.assertEqual(ctx.exception.kind, "missing_git")
        finally:
            os.environ["PATH"] = old


if __name__ == "__main__":
    unittest.main()
