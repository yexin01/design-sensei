"""The portable skill bundle: assembled by `design-sensei package-skill`, copied anywhere, runs standalone."""

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from tests import helpers

import build_portable_skill as bps
from dslib.paths import resolve_layout

ROOT = helpers.ROOT
LAUNCHER = Path("scripts") / "design-sensei"
SOURCE_ITEMS = ("skills", "catalog", "knowledge", "scripts", "docs", "examples", "LICENSE", "ATTRIBUTION.md", "CONTRIBUTING.md", "SECURITY.md", ".gitignore")
IS_ROOT = hasattr(os, "geteuid") and os.geteuid() == 0


def child_env(home, **extra):
    env = dict(os.environ)
    for name in ("DESIGN_SENSEI_ROOT", "DESIGN_SENSEI_HOME"):
        env.pop(name, None)
    env.update({"HOME": str(home), "USERPROFILE": str(home), "PYTHONDONTWRITEBYTECODE": "1"})
    env.update(extra)
    return env


def run_launcher(skill_dir, args, home, cwd, **extra):
    proc = subprocess.run([sys.executable, str(Path(skill_dir) / LAUNCHER)] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True, env=child_env(home, **extra), cwd=str(cwd))
    return proc.returncode, proc.stdout, proc.stderr


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_source_tree(dest):
    """A copy of the parts of the repository that the bundle is built from (so tests can plant bad files in it)."""
    dest.mkdir(parents=True)
    for item in SOURCE_ITEMS:
        src = ROOT / item
        if src.is_dir():
            shutil.copytree(str(src), str(dest / item), ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        elif src.is_file():
            shutil.copy(str(src), str(dest / item))
    return dest


class BundleTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory(prefix="ds bundle ")
        cls.tmp = Path(cls._tmp.name).resolve()
        cls.skill_md_before = sha256(ROOT / "skills" / "design-sensei" / "SKILL.md")
        cls.out = cls.tmp / "out"
        cls.result = bps.build(ROOT, cls.out, make_zip=True)
        cls.bundle = cls.result.directory
        cls.zip_path = cls.result.zip_path

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def fresh_copy(self, name="install"):
        """A plain (non-symlink) copy of the bundle at a new location whose path contains a space."""
        dest = self.tmp / ("fresh place %s" % name) / "skills" / "design-sensei"
        if dest.exists():
            shutil.rmtree(str(dest))
        shutil.copytree(str(self.bundle), str(dest), symlinks=False)
        self.assertEqual([p for p in dest.rglob("*") if p.is_symlink()], [])
        return dest

    def bundle_files(self):
        return sorted(p.relative_to(self.bundle).as_posix() for p in self.bundle.rglob("*") if p.is_file())


class BundleContentTests(BundleTestCase):
    def test_layout_of_the_bundle(self):
        files = set(self.bundle_files())
        for name in ("SKILL.md", "scripts/design-sensei", "config/defaults.yaml", "references/art-direction.md", "patterns/liquid-glass.md",
                     "toolkit/bundle.json", "toolkit/LICENSE", "toolkit/ATTRIBUTION.md", "toolkit/NOTICE",
                     "toolkit/catalog/sources.yaml", "toolkit/catalog/patterns.yaml", "toolkit/catalog/licenses.yaml", "toolkit/catalog/schemas/sources.schema.json",
                     "toolkit/knowledge/pattern-index/pattern-index.json", "toolkit/scripts/design_sensei.py", "toolkit/scripts/dslib/paths.py",
                     "toolkit/docs/installation.md", "toolkit/examples/glass-hero/index.html"):
            self.assertIn(name, files)
        self.assertTrue(os.access(str(self.bundle / LAUNCHER), os.X_OK), "the launcher must stay executable")
        self.assertFalse(os.access(str(self.bundle / "toolkit" / "scripts" / "dslib" / "paths.py"), os.X_OK))
        info = json.loads((self.bundle / "toolkit" / "bundle.json").read_text(encoding="utf-8"))
        self.assertEqual((info["kind"], info["name"]), ("portable-skill", "design-sensei"))

    def test_every_script_module_of_the_cli_is_included(self):
        expected = {p.relative_to(ROOT).as_posix() for p in (ROOT / "scripts").rglob("*.py")}
        got = {"scripts/" + f.split("toolkit/scripts/", 1)[1] for f in self.bundle_files() if f.startswith("toolkit/scripts/")}
        self.assertEqual(got, expected)

    def test_excluded_paths_are_absent(self):
        forbidden_parts = {"sources", ".state", ".git", "__pycache__", "node_modules", "tests", ".claude-plugin", "bin", ".claude", ".remember", "dist"}
        rules = bps.IgnoreRules((ROOT / ".gitignore").read_text(encoding="utf-8"))
        for rel in self.bundle_files():
            parts = rel.split("/")
            self.assertFalse(forbidden_parts & set(parts), rel)
            name = parts[-1]
            self.assertFalse(name.endswith((".pyc", ".pem", ".key", ".log")) or name in (".DS_Store", ".env", ".netrc", ".npmrc"), rel)
            self.assertFalse(name.startswith((".env.", "id_rsa", "id_ed25519", "credentials", "secrets.")), rel)
            as_in_repo = rel[len("toolkit/"):] if rel.startswith("toolkit/") else "skills/design-sensei/" + rel
            self.assertIsNone(rules.matching_rule(as_in_repo, False), "%s is matched by .gitignore" % rel)
        self.assertEqual([p for p in self.bundle.rglob("*") if p.is_symlink()], [])
        self.assertNotIn("publishing.md", " ".join(self.bundle_files()))

    def test_the_repository_is_not_modified(self):
        self.assertEqual(sha256(ROOT / "skills" / "design-sensei" / "SKILL.md"), self.skill_md_before)

    def test_only_escaping_paths_differ_from_the_sources(self):
        skill = ROOT / "skills" / "design-sensei"
        changed = 0
        for src in sorted(p for p in skill.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
            rel = src.relative_to(skill).as_posix()
            got = (self.bundle / rel).read_bytes()
            if rel.endswith(".md"):
                want, n = bps.relocate_links(src.read_text(encoding="utf-8"), rel.count("/"))
                changed += n
                self.assertEqual(got.decode("utf-8"), want, rel)
            else:
                self.assertEqual(got, src.read_bytes(), rel)
        self.assertGreater(changed, 100)

    def test_skill_md_points_into_the_toolkit(self):
        text = (self.bundle / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("${CLAUDE_SKILL_DIR}/../../", text)
        self.assertIn("${CLAUDE_SKILL_DIR}/toolkit/knowledge/pattern-index/by-category.md", text)
        self.assertIn("${CLAUDE_SKILL_DIR}/scripts/design-sensei", text)  # the launcher path is unchanged
        reference = (self.bundle / "references" / "performance.md").read_text(encoding="utf-8")
        self.assertIn("](../toolkit/knowledge/animations/gsap.md)", reference)
        self.assertNotIn("../../../", reference)

    def test_every_relative_markdown_link_resolves(self):
        broken = []
        for rel in self.bundle_files():
            if rel.endswith(".md") and not rel.startswith(bps.LENIENT_LINK_PREFIXES):
                for target in bps._LINK_RE.findall(bps._CODE_RE.sub("", (self.bundle / rel).read_text(encoding="utf-8"))):
                    if not (self.bundle / rel).parent.joinpath(target).resolve().exists():
                        broken.append("%s -> %s" % (rel, target))
        self.assertEqual(broken, [])

    def test_fixed_modification_times_on_disk(self):
        for rel in ("SKILL.md", "toolkit/bundle.json", "toolkit/catalog/sources.yaml"):
            self.assertEqual(int((self.bundle / rel).stat().st_mtime), bps.FIXED_EPOCH)

    def test_relocate_links(self):
        text = "[a](../../../knowledge/x.md) `${CLAUDE_SKILL_DIR}/../../catalog/p.yaml` [b](../references/y.md) [c](https://e.org/../../../knowledge/z) [d](../../../ATTRIBUTION.md#top)"
        self.assertEqual(bps.relocate_links(text, 1)[0],
                         "[a](../toolkit/knowledge/x.md) `${CLAUDE_SKILL_DIR}/../../catalog/p.yaml` [b](../references/y.md) [c](https://e.org/../../../knowledge/z) [d](../toolkit/ATTRIBUTION.md#top)")
        self.assertEqual(bps.relocate_links("`${CLAUDE_SKILL_DIR}/../../catalog/p.yaml` and ../../knowledge", 0),
                         ("`${CLAUDE_SKILL_DIR}/toolkit/catalog/p.yaml` and toolkit/knowledge", 2))
        self.assertEqual(bps.relocate_links("../../../knowledge/a ../../../knowledgebase/a", 2), ("../../../knowledge/a ../../../knowledgebase/a", 0))


class ZipTests(BundleTestCase):
    def test_zip_is_deterministic(self):
        again = bps.build(ROOT, self.tmp / "second", make_zip=True)
        self.assertEqual(again.zip_sha256, self.result.zip_sha256)
        self.assertEqual(sha256(again.zip_path), sha256(self.zip_path))
        third = bps.build(ROOT, self.tmp / "second", make_zip=True)  # rebuild over a previous bundle
        self.assertEqual(third.zip_sha256, self.result.zip_sha256)
        self.assertEqual(self.result.zip_sha256, sha256(self.zip_path))
        checksum = Path(str(self.zip_path) + ".sha256").read_text(encoding="utf-8")
        self.assertEqual(checksum, "%s  %s\n" % (self.result.zip_sha256, self.zip_path.name))

    def test_zip_entries_are_sorted_normalised_and_match_the_directory(self):
        with zipfile.ZipFile(str(self.zip_path)) as zf:
            names = zf.namelist()
            self.assertEqual(names, sorted(names))
            self.assertTrue(all(n.startswith("design-sensei/") and ".." not in n and not n.startswith("/") for n in names))
            self.assertEqual(sorted(n[len("design-sensei/"):] for n in names), self.bundle_files())
            for info in zf.infolist():
                self.assertEqual(info.date_time, bps.FIXED_DATE)
                self.assertEqual(info.create_system, 3)
                self.assertIn((info.external_attr >> 16) & 0o777, (0o644, 0o755))
                self.assertEqual(zf.read(info), (self.bundle / info.filename[len("design-sensei/"):]).read_bytes())
            launcher = zf.getinfo("design-sensei/scripts/design-sensei")
            self.assertEqual((launcher.external_attr >> 16) & 0o777, 0o755)
            self.assertIsNone(zf.testzip())

    def test_bundle_is_small(self):
        self.assertLess(self.result.zip_bytes, 3 * 1024 * 1024)
        self.assertLess(self.result.bytes, 8 * 1024 * 1024)


class StandaloneRunTests(BundleTestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="home ", dir=str(self.tmp)))
        self.work = Path(tempfile.mkdtemp(prefix="work ", dir=str(self.tmp)))

    def run_copy(self, skill, args, **extra):
        return run_launcher(skill, args, self.home, self.work, **extra)

    def test_copied_skill_runs_standalone(self):
        skill = self.fresh_copy("standalone")
        code, out, err = self.run_copy(skill, ["doctor", "--brief"])
        self.assertEqual(code, 0, out + err)
        self.assertIn("toolkit: %s" % (skill.resolve() / "toolkit"), out)
        self.assertIn("status: 0 failure(s)", out)
        self.assertIn(str(self.home / ".design-sensei"), out)
        self.assertIn("portable skill bundle", out)
        code, out, err = self.run_copy(skill, ["search", "liquid glass"])
        self.assertEqual(code, 0, err)
        self.assertIn("liquid-glass", out)
        self.assertIn("root: %s" % (skill.resolve() / "toolkit"), out)  # one root line, every note path relative to it
        self.assertIn("knowledge/shaders/liquid-glass.md", out)
        for argv in (["catalog", "validate", "--strict"], ["licenses", "report", "--check"], ["index", "build", "--check"], ["config", "show"]):
            code, out, err = self.run_copy(skill, argv)
            self.assertEqual(code, 0, "%s: %s%s" % (" ".join(argv), out, err))
        code, out, err = self.run_copy(skill, ["eval", str(skill / "toolkit" / "examples" / "glass-hero")])
        self.assertEqual(code, 0, out + err)
        self.assertIn("scanned 2 file(s)", out)

    def test_doctor_json_has_no_failures_and_no_plugin_warning(self):
        skill = self.fresh_copy("doctor")
        code, out, err = self.run_copy(skill, ["doctor", "--json"])
        self.assertEqual(code, 0, err)
        report = json.loads(out)
        self.assertEqual(report["summary"]["failures"], 0)
        levels = {(c["name"], c["level"]) for c in report["checks"]}
        self.assertIn(("bundle", "ok"), levels)
        self.assertFalse([c for c in report["checks"] if c["name"] in ("plugin", "skill", "launcher", "bundle") and c["level"] != "ok"])
        self.assertNotIn("plugin", {c["name"] for c in report["checks"]})

    def test_doctor_notices_a_launcher_that_lost_its_exec_bit(self):
        skill = self.fresh_copy("exec")
        launcher = skill / LAUNCHER
        launcher.chmod(0o644)
        code, out, err = self.run_copy(skill, ["doctor", "--brief"])
        self.assertEqual(code, 1, out)
        self.assertIn("not executable", out)

    def test_library_stays_outside_the_skill_folder(self):
        skill = self.fresh_copy("library")
        before = sorted(p.relative_to(skill).as_posix() for p in skill.rglob("*"))
        code, out, err = self.run_copy(skill, ["setup"])
        self.assertEqual(code, 0, out + err)
        self.assertTrue((self.home / ".design-sensei" / "sources").is_dir())
        self.assertTrue((self.home / ".design-sensei" / ".state").is_dir())
        self.assertEqual(sorted(p.relative_to(skill).as_posix() for p in skill.rglob("*")), before)
        code, out, err = self.run_copy(skill, ["doctor", "--brief"], DESIGN_SENSEI_HOME=str(self.tmp / "custom library"))
        self.assertIn("library: %s" % (self.tmp / "custom library"), out)

    @unittest.skipIf(IS_ROOT or os.name == "nt", "file permissions are not enforced for root or on Windows")
    def test_works_when_the_skill_folder_is_read_only(self):
        skill = self.fresh_copy("readonly")

        def restore():
            for p in [skill] + list(skill.rglob("*")):
                p.chmod(p.stat().st_mode | stat.S_IWUSR)

        self.addCleanup(restore)
        for p in sorted(skill.rglob("*"), reverse=True) + [skill]:
            p.chmod(p.stat().st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
        for argv in (["doctor", "--brief"], ["search", "scroll"], ["catalog", "validate"]):
            code, out, err = self.run_copy(skill, argv)
            self.assertEqual(code, 0, "%s: %s%s" % (" ".join(argv), out, err))

    def test_package_skill_refuses_to_run_inside_a_bundle(self):
        skill = self.fresh_copy("nested")
        code, out, err = self.run_copy(skill, ["package-skill", "--out", str(self.tmp / "nested out")])
        self.assertEqual(code, 1)
        self.assertIn("already a portable bundle", err)
        self.assertFalse((self.tmp / "nested out").exists())


class LauncherLookupTests(BundleTestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="home ", dir=str(self.tmp)))
        self.work = Path(tempfile.mkdtemp(prefix="work ", dir=str(self.tmp)))

    def fake_toolkit(self, base):
        (base / "catalog").mkdir(parents=True)
        (base / "catalog" / "sources.yaml").write_text("sources: []\n", encoding="utf-8")
        (base / "scripts").mkdir()
        (base / "scripts" / "design_sensei.py").write_text("import os\n\ndef main():\n    print('fake toolkit ' + os.environ['DESIGN_SENSEI_ROOT'])\n    return 0\n", encoding="utf-8")
        return base

    def lone_launcher(self, name):
        """A skill folder holding nothing but the launcher: what a bare copy of skills/design-sensei/scripts looks like."""
        skill = self.tmp / name / "design-sensei"
        (skill / "scripts").mkdir(parents=True)
        shutil.copy(str(self.bundle / LAUNCHER), str(skill / LAUNCHER))
        return skill

    def test_exits_4_with_the_documented_message_when_nothing_is_found(self):
        skill = self.lone_launcher("lone")
        code, out, err = run_launcher(skill, ["doctor"], self.home, self.work)
        self.assertEqual(code, 4)
        self.assertIn("cannot find the toolkit (catalog/ and scripts/)", err)
        self.assertIn("DESIGN_SENSEI_ROOT", err)

    def test_environment_variable_comes_first(self):
        skill = self.fresh_copy("lookup env")
        fake = self.fake_toolkit(self.tmp / "env toolkit")
        code, out, err = run_launcher(skill, [], self.home, self.work, DESIGN_SENSEI_ROOT=str(fake))
        self.assertEqual(code, 0, err)
        self.assertIn("fake toolkit %s" % fake, out)

    def test_bundled_toolkit_beats_the_home_toolkit(self):
        skill = self.fresh_copy("lookup order")
        self.fake_toolkit(self.home / ".design-sensei" / "toolkit")
        code, out, err = run_launcher(skill, ["doctor", "--brief"], self.home, self.work)
        self.assertEqual(code, 0, out + err)
        self.assertIn("toolkit: %s" % (skill.resolve() / "toolkit"), out)

    def test_home_toolkit_is_the_last_resort(self):
        skill = self.lone_launcher("last resort")
        fake = self.fake_toolkit(self.home / ".design-sensei" / "toolkit")
        code, out, err = run_launcher(skill, [], self.home, self.work)
        self.assertEqual(code, 0, err)
        self.assertIn("fake toolkit %s" % fake, out)

    def test_checkout_layout_still_works(self):
        # skills/design-sensei/scripts/design-sensei three levels below a toolkit root (git checkout and plugin install)
        root = self.fake_toolkit(self.tmp / "checkout")
        (root / "skills" / "design-sensei" / "scripts").mkdir(parents=True)
        shutil.copy(str(self.bundle / LAUNCHER), str(root / "skills" / "design-sensei" / LAUNCHER))
        code, out, err = run_launcher(root / "skills" / "design-sensei", [], self.home, self.work)
        self.assertEqual(code, 0, err)
        self.assertIn("fake toolkit %s" % root.resolve(), out)

    @unittest.skipIf(os.name == "nt", "symlinks need privileges on Windows")
    def test_symlinked_bundle_resolves_to_the_real_folder(self):
        skill = self.fresh_copy("linked")
        link = self.tmp / "linked skills" / "design-sensei"
        link.parent.mkdir()
        os.symlink(str(skill), str(link))
        code, out, err = run_launcher(link, ["doctor", "--brief"], self.home, self.work)
        self.assertEqual(code, 0, out + err)
        self.assertIn("toolkit: %s" % (skill.resolve() / "toolkit"), out)


class RefusalTests(BundleTestCase):
    def source(self, name):
        return make_source_tree(self.tmp / ("src " + name))

    def assert_refused(self, src, *needles):
        out = self.tmp / ("refused out " + src.name)
        with self.assertRaises(bps.BuildError) as ctx:
            bps.build(src, out, make_zip=True)
        for needle in needles:
            self.assertIn(needle, str(ctx.exception))
        self.assertFalse(out.exists() and any(out.iterdir()), "a refused build must not leave output behind")

    def test_the_unmodified_copy_builds(self):
        src = self.source("clean")
        again = bps.build(src, self.tmp / "clean out", make_zip=True)
        self.assertEqual(again.zip_sha256, self.result.zip_sha256, "a copy of the repository yields the same bundle")

    def test_secrets_are_refused(self):
        for name, rel in (("env", "knowledge/.env"), ("envlocal", "catalog/.env.production"), ("pem", "knowledge/x/server.pem"), ("key", "scripts/dslib/signing.key"),
                          ("rsa", "docs/id_rsa"), ("creds", "knowledge/credentials-prod.json"), ("secrets", "catalog/secrets.yaml"), ("netrc", "skills/design-sensei/.netrc")):
            src = self.source(name)
            target = src / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("not really a secret\n", encoding="utf-8")
            self.assert_refused(src, rel, "secret")
            shutil.rmtree(str(src))

    def test_sources_state_and_git_data_are_refused(self):
        for name, rel in (("sources", "catalog/sources/lenis/package.json"), ("state", "scripts/.state/lock.json"), ("git", "knowledge/.git/HEAD"), ("nm", "examples/glass-hero/node_modules/x/index.js")):
            src = self.source(name)
            target = src / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("x\n", encoding="utf-8")
            self.assert_refused(src, "refusing to bundle")
            shutil.rmtree(str(src))

    def test_new_gitignore_rules_are_honoured(self):
        src = self.source("gitignore")
        with open(str(src / ".gitignore"), "a", encoding="utf-8") as fh:
            fh.write("\n*.draft\n/knowledge/private-notes/\n")
        (src / "knowledge" / "idea.draft").write_text("x\n", encoding="utf-8")
        self.assert_refused(src, "knowledge/idea.draft", "*.draft")
        (src / "knowledge" / "idea.draft").unlink()
        (src / "knowledge" / "private-notes").mkdir()
        (src / "knowledge" / "private-notes" / "a.md").write_text("x\n", encoding="utf-8")
        self.assert_refused(src, "knowledge/private-notes", "private-notes")

    @unittest.skipIf(os.name == "nt", "symlinks need privileges on Windows")
    def test_symbolic_links_are_refused(self):
        src = self.source("symlink")
        os.symlink(str(ROOT / "LICENSE"), str(src / "knowledge" / "link.md"))
        self.assert_refused(src, "symbolic link")

    def test_caches_and_editor_files_are_skipped_not_fatal(self):
        src = self.source("noise")
        (src / "scripts" / "__pycache__").mkdir()
        (src / "scripts" / "__pycache__" / "x.cpython-39.pyc").write_bytes(b"\0")
        (src / "knowledge" / ".DS_Store").write_bytes(b"\0")
        (src / "knowledge" / "notes.md~").write_text("x", encoding="utf-8")
        result = bps.build(src, self.tmp / "noise out")
        files = {p.name for p in result.directory.rglob("*") if p.is_file()}
        self.assertFalse(files & {"x.cpython-39.pyc", ".DS_Store", "notes.md~"})

    def test_a_broken_link_stops_the_build(self):
        src = self.source("broken")
        with open(str(src / "skills" / "design-sensei" / "references" / "typography.md"), "a", encoding="utf-8") as fh:
            fh.write("\nSee [missing](../../../knowledge/does-not-exist.md).\n")
        self.assert_refused(src, "do not resolve", "does-not-exist.md")

    def test_dead_links_in_docs_only_warn_but_in_the_knowledge_base_they_stop_the_build(self):
        src = self.source("lenient")
        with open(str(src / "docs" / "installation.md"), "a", encoding="utf-8") as fh:
            fh.write("\nSee the [readme](../README.md).\n")
        result = bps.build(src, self.tmp / "lenient out")
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("docs/installation.md -> ../README.md", result.warnings[0])
        with open(str(src / "knowledge" / "README.md"), "a", encoding="utf-8") as fh:
            fh.write("\nSee the [readme](../README.md).\n")
        self.assert_refused(src, "do not resolve", "knowledge/README.md")

    def test_an_incomplete_source_tree_is_refused(self):
        src = self.source("incomplete")
        (src / "catalog" / "licenses.yaml").unlink()
        self.assert_refused(src, "incomplete", "licenses.yaml")
        bundle_src = self.tmp / "not a checkout"
        bundle_src.mkdir()
        with self.assertRaises(bps.BuildError):
            bps.collect(bundle_src)

    def test_output_inside_a_bundled_folder_is_refused(self):
        src = self.source("outdir")
        with self.assertRaises(bps.BuildError) as ctx:
            bps.build(src, src / "knowledge" / "build")
        self.assertIn("bundled", str(ctx.exception))

    def test_an_unrelated_existing_folder_is_never_deleted(self):
        out = self.tmp / "precious"
        (out / "design-sensei").mkdir(parents=True)
        (out / "design-sensei" / "mine.txt").write_text("keep me\n", encoding="utf-8")
        with self.assertRaises(bps.BuildError) as ctx:
            bps.build(ROOT, out)
        self.assertIn("not a previous bundle", str(ctx.exception))
        self.assertEqual((out / "design-sensei" / "mine.txt").read_text(encoding="utf-8"), "keep me\n")

    def test_rebuilding_replaces_a_previous_bundle(self):
        out = self.tmp / "rebuild"
        first = bps.build(ROOT, out)
        (first.directory / "stale.txt").write_text("old\n", encoding="utf-8")
        (first.directory / "toolkit" / "knowledge" / "README.md").write_text("tampered\n", encoding="utf-8")
        second = bps.build(ROOT, out)
        self.assertFalse((second.directory / "stale.txt").exists())
        self.assertEqual((second.directory / "toolkit" / "knowledge" / "README.md").read_bytes(), (ROOT / "knowledge" / "README.md").read_bytes())

    def test_policy_covers_the_gitignore_secret_categories(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        section = text.split("# Secrets and credentials", 1)[1].split("# ----", 2)[1]
        samples = []
        for line in section.splitlines():
            line = line.strip()
            if line and not line.startswith(("#", "!", "-")):
                samples.append(line.replace("*", "x"))
        self.assertGreaterEqual(len(samples), 8)
        for rules in (bps.IgnoreRules(text), bps.IgnoreRules("")):  # with the real .gitignore and with the built-in floor alone
            policy = bps.Policy(rules)
            for sample in samples:
                self.assertEqual(policy.classify("knowledge/" + sample, False)[0], "deny", sample)
            for rel in ("sources", ".state", "knowledge/.git", "node_modules"):
                self.assertEqual(policy.classify(rel, True)[0], "deny", rel)
            self.assertEqual(policy.classify("knowledge/.env.example", False)[0], "ok")
            self.assertEqual(policy.classify("knowledge/README.md", False)[0], "ok")
            self.assertEqual(policy.classify("scripts/__pycache__", True)[0], "skip")


class IgnoreRulesTests(unittest.TestCase):
    def test_gitignore_subset(self):
        rules = bps.IgnoreRules("# comment\n\n/sources/*\n!/sources/README.md\n/.state/\n*.log\n.env.*\n!.env.example\nbuild/\n/examples/**/dist/\n/out/\n*.py[co]\n")
        ignored = lambda rel, is_dir=False: rules.matching_rule(rel, is_dir) is not None  # noqa: E731
        self.assertTrue(ignored("sources/lenis"))
        self.assertTrue(ignored("sources/lenis/package.json"))
        self.assertFalse(ignored("sources/README.md"))
        self.assertTrue(ignored(".state", True))
        self.assertTrue(ignored(".state/lock.json"))
        self.assertFalse(ignored("docs/.state-of-the-art.md"))
        self.assertTrue(ignored("deep/er/run.log"))
        self.assertTrue(ignored("deep/.env.local"))
        self.assertFalse(ignored("deep/.env.example"))
        self.assertTrue(ignored("a/build/x.txt"))
        self.assertFalse(ignored("a/build"))  # a file called "build" is not the ignored directory
        self.assertTrue(ignored("examples/a/b/dist/x.js"))
        self.assertFalse(ignored("examples/dist.js"))
        self.assertTrue(ignored("out/x"))
        self.assertFalse(ignored("docs/out/x"))  # anchored to the repository root
        self.assertTrue(ignored("m.pyc") and ignored("m.pyo") and not ignored("m.pyd"))

    def test_the_repository_gitignore_agrees_with_git(self):
        gitignore = ROOT / ".gitignore"
        rules = bps.IgnoreRules(gitignore.read_text(encoding="utf-8"))
        samples = ["sources/lenis/package.json", "sources/README.md", ".state/lock.json", "dist/design-sensei/SKILL.md", ".env", ".env.example", "knowledge/a.pem",
                   "node_modules/x/y.js", "scripts/__pycache__/a.pyc", "examples/glass-hero/dist/a.js", "docs/installation.md", "skills/design-sensei/SKILL.md", ".claude/x", "a/b.log"]
        for rel in samples:
            try:
                proc = subprocess.run(["git", "check-ignore", "-q", "--no-index", rel], cwd=str(ROOT))
            except OSError:
                self.skipTest("git is not installed")
            if proc.returncode not in (0, 1):
                self.skipTest("git check-ignore is unavailable")
            self.assertEqual(rules.matching_rule(rel, False) is not None, proc.returncode == 0, rel)


class BundleLayoutTests(helpers.TempDirTest):
    def make_bundle_toolkit(self):
        toolkit = self.tmp / "skill dir" / "toolkit"
        (toolkit / "catalog").mkdir(parents=True)
        (toolkit / "catalog" / "sources.yaml").write_text("sources: []\n", encoding="utf-8")
        (toolkit / "bundle.json").write_text("{}\n", encoding="utf-8")
        return toolkit

    def test_bundle_defaults_to_the_user_library_and_the_skill_folder_is_the_parent(self):
        toolkit = self.make_bundle_toolkit()
        (toolkit / ".git").mkdir()  # must not turn the bundle into a "development checkout"
        with mock.patch.dict(os.environ, {"HOME": str(self.tmp / "home"), "USERPROFILE": str(self.tmp / "home")}):
            layout = resolve_layout(root=str(toolkit), env={})
        self.assertTrue(layout.is_bundle())
        self.assertEqual(layout.home, self.tmp / "home" / ".design-sensei")
        self.assertEqual(layout.sources_dir, self.tmp / "home" / ".design-sensei" / "sources")
        self.assertIn("portable skill bundle", layout.home_reason)
        self.assertEqual(layout.skill_dir, toolkit.parent)
        self.assertEqual(layout.defaults_yaml, toolkit.parent / "config" / "defaults.yaml")
        self.assertNotIn(str(layout.root), str(layout.sources_dir))

    def test_explicit_home_still_wins_in_a_bundle(self):
        toolkit = self.make_bundle_toolkit()
        layout = resolve_layout(root=str(toolkit), home=str(self.tmp / "flag"), env={})
        self.assertEqual(layout.home, self.tmp / "flag")
        layout = resolve_layout(root=str(toolkit), env={"DESIGN_SENSEI_HOME": str(self.tmp / "from env")})
        self.assertEqual(layout.home, self.tmp / "from env")

    def test_without_the_marker_nothing_changes(self):
        layout = helpers.make_toolkit(self.tmp)
        self.assertFalse(layout.is_bundle())
        self.assertEqual(layout.skill_dir, layout.root / "skills" / "design-sensei")


class CommandLineTests(helpers.TempDirTest):
    def test_package_skill_through_the_command_line(self):
        code, out, err = helpers.run_cli(["package-skill", "--out", str(self.tmp / "cli out"), "--zip"])
        self.assertEqual(code, 0, out + err)
        self.assertIn("portable skill:", out)
        zip_path = self.tmp / "cli out" / ("design-sensei-skill-%s.zip" % bps.__version__)
        self.assertTrue(zip_path.is_file())
        self.assertIn(sha256(zip_path), out)
        self.assertTrue((self.tmp / "cli out" / "design-sensei" / "toolkit" / "bundle.json").is_file())
        self.assertNotIn("Traceback", err)
        code, out, err = helpers.run_cli(["package-skill", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("--zip", out)

    def test_refusal_is_a_clean_error_exit_1(self):
        src = make_source_tree(self.tmp / "src")
        (src / "knowledge" / ".env").write_text("x\n", encoding="utf-8")
        code, out, err = helpers.run_cli(["package-skill", "--out", str(self.tmp / "refused"), "--root", str(src)])
        self.assertEqual(code, 1)
        self.assertIn("refusing to bundle knowledge/.env", err)
        self.assertNotIn("Traceback", err)
        self.assertFalse((self.tmp / "refused" / "design-sensei").exists())


if __name__ == "__main__":
    unittest.main()
