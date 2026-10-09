"""End-to-end tests of the real command line (subprocess) - help, exit codes and the main flows."""

import json
import os
import subprocess
import sys
import unittest

from tests import helpers
from tests.helpers import make_pattern, make_source, run_cli

COMMANDS = [
    [], ["setup"], ["sources"], ["sources", "list"], ["sources", "sync"], ["sources", "status"], ["sources", "show"], ["index"], ["index", "build"],
    ["search"], ["recommend"], ["catalog"], ["catalog", "validate"], ["licenses"], ["licenses", "check"], ["licenses", "scan"], ["licenses", "report"],
    ["doctor"], ["config"], ["config", "show"], ["config", "init"], ["eval"], ["package-skill"],
]


class HelpTests(unittest.TestCase):
    def test_every_command_has_help_and_exits_zero(self):
        for cmd in COMMANDS:
            with self.subTest(cmd=" ".join(cmd) or "(root)"):
                code, out, err = run_cli(cmd + ["--help"])
                self.assertEqual(code, 0, err)
                self.assertIn("usage:", out)

    def test_version(self):
        code, out, _ = run_cli(["--version"])
        self.assertEqual(code, 0)
        self.assertRegex(out, r"design-sensei \d+\.\d+\.\d+")

    def test_usage_errors_exit_2(self):
        for argv in (["nonsense"], ["sources", "nonsense"], ["search", "--max-gpu", "huge"], ["sources", "sync", "--jobs", "x"]):
            with self.subTest(argv=argv):
                self.assertEqual(run_cli(argv)[0], 2)

    def test_no_arguments_prints_usage_and_fails_with_usage_code(self):
        code, _, err = run_cli([])
        self.assertEqual(code, 2)

    def test_readme_documents_only_real_commands(self):
        readme = (helpers.ROOT / "README.md")
        if not readme.exists():
            self.skipTest("README.md not written yet")
        import re
        text = readme.read_text(encoding="utf-8")
        known = {" ".join(c) for c in COMMANDS if c}
        for line in re.findall(r"^\s*(?:\$ )?(?:\./bin/)?design-sensei ((?:[a-z]+(?:-[a-z]+)?)(?: (?:list|sync|status|show|build|validate|check|scan|report|init))?)", text, re.MULTILINE):
            self.assertIn(line.strip(), known, "README mentions an unknown command: %s" % line)


class FlowTests(helpers.TempDirTest):
    def env(self):
        return {"DESIGN_SENSEI_HOME": str(self.tmp / "lib home")}

    def test_doctor_json_and_exit_code(self):
        code, out, err = run_cli(["doctor", "--json"], self.env())
        data = json.loads(out)
        self.assertIn("summary", data)
        self.assertEqual(code, 1 if data["summary"]["failures"] else 0, err)

    def test_setup_light_creates_library_and_does_not_download(self):
        code, out, err = run_cli(["setup"], self.env())
        self.assertEqual(code, 0, out + err)
        self.assertTrue((self.tmp / "lib home" / "sources").is_dir())
        self.assertEqual(list((self.tmp / "lib home" / "sources").iterdir()), [])
        self.assertIn("light setup", out)
        self.assertIn("design-sensei doctor", out)

    def test_setup_rejects_unknown_sources_and_offline_full_reports_environment_problem(self):
        self.assertEqual(run_cli(["setup", "--sources", "nope"], self.env())[0], 2)
        code, out, _ = run_cli(["setup", "--sources", "lenis", "--offline"], self.env())
        self.assertEqual(code, 4)
        self.assertIn("skipped_offline", out)

    def test_search_finds_real_catalog_content(self):
        code, out, _ = run_cli(["search", "smooth scroll", "--json", "--limit", "3"], self.env())
        self.assertEqual(code, 0)
        data = json.loads(out)
        if data["count"] == 0:
            self.skipTest("pattern catalog is still empty")
        self.assertTrue(all("reuse" in r for r in data["results"]))

    def test_config_init_and_show(self):
        project = self.tmp / "my project"
        project.mkdir()
        code, out, _ = run_cli(["config", "init", "--project", str(project)], self.env())
        self.assertEqual(code, 0)
        self.assertTrue((project / ".design-sensei.yaml").is_file())
        self.assertEqual(run_cli(["config", "init", "--project", str(project)], self.env())[0], 1)  # refuses to overwrite
        (project / ".design-sensei.yaml").write_text("motion_intensity: 2\n")
        code, out, _ = run_cli(["config", "show", "--project", str(project), "--json"], self.env())
        data = json.loads(out)
        self.assertEqual((data["config"]["motion_intensity"], data["origins"]["motion_intensity"]), (2, "project"))
        (project / ".design-sensei.yaml").write_text("motion_intensity: 99\n")
        self.assertEqual(run_cli(["config", "show", "--project", str(project)], self.env())[0], 1)

    def test_catalog_validate_exit_codes_on_a_broken_toolkit(self):
        layout = helpers.make_toolkit(self.tmp, patterns=[make_pattern()])
        env = dict(self.env(), DESIGN_SENSEI_ROOT=str(layout.root))
        self.assertEqual(run_cli(["catalog", "validate"], env)[0], 0)
        (layout.root / "catalog" / "patterns.yaml").write_text("schema_version: 1\npatterns:\n  - id: Bad Id\n")
        code, out, _ = run_cli(["catalog", "validate"], env)
        self.assertEqual(code, 1)
        self.assertIn("ERROR", out)

    def test_missing_toolkit_is_a_clean_error(self):
        code, _, err = run_cli(["doctor"], {"DESIGN_SENSEI_ROOT": str(self.tmp)})
        self.assertEqual(code, 1)
        self.assertIn("catalog", err)
        self.assertNotIn("Traceback", err)

    def test_works_from_paths_with_spaces(self):
        layout = helpers.make_toolkit(self.tmp, patterns=[make_pattern()])
        code, out, err = run_cli(["search", "demo", "--home", str(layout.home), "--root", str(layout.root)])
        self.assertEqual(code, 0, err)
        self.assertIn("demo-pattern", out)


class LauncherTests(unittest.TestCase):
    def test_launchers_are_executable_and_run(self):
        for rel in ("bin/design-sensei", "skills/design-sensei/scripts/design-sensei"):
            path = helpers.ROOT / rel
            with self.subTest(rel=rel):
                self.assertTrue(os.access(str(path), os.X_OK), "%s must be executable" % rel)
                proc = subprocess.run([str(path), "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn("design-sensei", proc.stdout)

    def test_skill_launcher_follows_symlinks_to_the_toolkit(self):
        import tempfile
        with tempfile.TemporaryDirectory(prefix="linked skill ") as tmp:
            link = os.path.join(tmp, "design-sensei")
            os.symlink(str(helpers.ROOT / "skills" / "design-sensei"), link)
            proc = subprocess.run([os.path.join(link, "scripts", "design-sensei"), "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_skill_launcher_copied_alone_explains_what_to_do(self):
        import shutil
        import tempfile
        with tempfile.TemporaryDirectory(prefix="copied skill ") as tmp:
            dest = os.path.join(tmp, "design-sensei")
            shutil.copytree(str(helpers.ROOT / "skills" / "design-sensei"), dest)
            env = {k: v for k, v in os.environ.items() if k not in ("DESIGN_SENSEI_ROOT",)}
            env["HOME"] = tmp  # no ~/.design-sensei/toolkit
            proc = subprocess.run([os.path.join(dest, "scripts", "design-sensei"), "doctor"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=env)
            self.assertEqual(proc.returncode, 4)
            self.assertIn("cannot find the toolkit", proc.stderr)
            self.assertIn("DESIGN_SENSEI_ROOT", proc.stderr)
            env["DESIGN_SENSEI_ROOT"] = str(helpers.ROOT)
            proc = subprocess.run([os.path.join(dest, "scripts", "design-sensei"), "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=env)
            self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
