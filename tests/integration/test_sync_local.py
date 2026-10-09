"""Source synchronisation against real local git repositories (no network needed)."""

import json
import os
import shutil
import unittest
from pathlib import Path

from tests import helpers
from tests.helpers import NEEDS_GIT, make_source
import sync_sources as ss
from dslib import catalog, gitops


@NEEDS_GIT
class SyncBase(helpers.TempDirTest):
    def setUp(self):
        super().setUp()
        self.up = helpers.Upstream(self.tmp)
        self.c1 = self.up.commit({"README.md": "# one\n", "src/a.js": "a", "docs/guide.md": "g", "my dir/file name.txt": "space"}, "first")
        self.c2 = self.up.commit({"src/a.js": "a2", "extra.txt": "x"}, "second")
        self.opts = ss.SyncOptions(allow_local_urls=True, min_free_mb=1, retries=2, sleep=lambda s: None)

    def make(self, **overrides):
        src = make_source("alpha", url=self.up.url, pinned_commit=self.c1, **overrides)
        self.layout = helpers.make_toolkit(self.tmp, sources=[src])
        return src

    def dest(self, sid="alpha"):
        return self.layout.sources_dir / sid


class AcquireTests(SyncBase):
    def test_fresh_clone_checks_out_the_pinned_commit_not_the_tip(self):
        src = self.make()
        res = ss.sync_one(self.layout, src, self.opts)
        self.assertEqual((res.status, res.commit), (ss.ACQUIRED, self.c1))
        self.assertEqual(gitops.head_commit(str(self.dest())), self.c1)
        self.assertEqual((self.dest() / "src" / "a.js").read_text(), "a")  # content of the first commit
        self.assertFalse((self.dest() / "extra.txt").exists())
        self.assertEqual((self.dest() / "my dir" / "file name.txt").read_text(), "space")  # paths with spaces

    def test_clone_is_shallow_and_detached(self):
        src = self.make()
        ss.sync_one(self.layout, src, self.opts)
        self.assertEqual(gitops.run_git(["rev-list", "--count", "HEAD"], cwd=str(self.dest())).stdout.strip(), "1")
        self.assertEqual(gitops.run_git(["branch", "--show-current"], cwd=str(self.dest())).stdout.strip(), "")  # detached HEAD

    def test_second_sync_is_up_to_date_and_idempotent(self):
        src = self.make()
        ss.sync_one(self.layout, src, self.opts)
        res = ss.sync_one(self.layout, src, self.opts)
        self.assertEqual((res.status, res.commit), (ss.UP_TO_DATE, self.c1))

    def test_unpinned_source_resolves_branch_tip(self):
        src = self.make()
        src["pinned_commit"] = None
        res = ss.sync_one(self.layout, src, self.opts)
        self.assertEqual(res.commit, self.c2)

    def test_sparse_checkout_limits_files_but_keeps_root_files(self):
        src = self.make(acquisition_method="git_sparse", sparse_paths=["src"])
        res = ss.sync_one(self.layout, src, self.opts)
        self.assertEqual(res.status, ss.ACQUIRED, res.message)
        self.assertTrue((self.dest() / "src" / "a.js").exists())
        self.assertTrue((self.dest() / "README.md").exists())  # root files are always included
        self.assertFalse((self.dest() / "docs").exists())
        self.assertIn("sparse: src", res.message)

    def test_changing_sparse_paths_updates_an_existing_checkout(self):
        src = self.make(acquisition_method="git_sparse", sparse_paths=["src"])
        ss.sync_one(self.layout, src, self.opts)
        src["sparse_paths"] = ["src", "docs"]
        res = ss.sync_one(self.layout, src, self.opts)
        self.assertEqual(res.status, ss.UPDATED, res.message)
        self.assertTrue((self.dest() / "docs" / "guide.md").exists())
        self.assertTrue((self.dest() / "src" / "a.js").exists())

    def test_reference_only_is_never_downloaded(self):
        src = make_source("site", type="website", acquisition_method="reference_only", pinned_commit=None, license="NOASSERTION",
                          license_status="unknown", redistribution_status="reference_only")
        layout = helpers.make_toolkit(self.tmp, sources=[src])
        res = ss.sync_one(layout, src, self.opts)
        self.assertEqual(res.status, ss.REFERENCE_ONLY)
        self.assertFalse((layout.sources_dir / "site").exists())

    def test_dry_run_changes_nothing(self):
        src = self.make()
        opts = ss.SyncOptions(allow_local_urls=True, dry_run=True, min_free_mb=1)
        res = ss.sync_one(self.layout, src, opts)
        self.assertEqual(res.status, ss.WOULD_ACQUIRE)
        self.assertFalse(self.dest().exists())
        self.assertFalse(self.layout.lock_path.exists())


class SafetyTests(SyncBase):
    def test_dirty_checkout_is_never_touched(self):
        src = self.make()
        ss.sync_one(self.layout, src, self.opts)
        edited = self.dest() / "src" / "a.js"
        edited.write_text("my local edit")
        src["pinned_commit"] = self.c2
        res = ss.sync_one(self.layout, src, self.opts)
        self.assertEqual(res.status, ss.BLOCKED)
        self.assertEqual(edited.read_text(), "my local edit")
        self.assertEqual(gitops.head_commit(str(self.dest())), self.c1)
        self.assertIn("locally modified", res.message)

    def test_untracked_files_survive_an_update(self):
        src = self.make()
        ss.sync_one(self.layout, src, self.opts)
        (self.dest() / "notes.txt").write_text("mine")
        src["pinned_commit"] = self.c2
        res = ss.sync_one(self.layout, src, self.opts)
        self.assertEqual((res.status, res.commit), (ss.UPDATED, self.c2))
        self.assertEqual((self.dest() / "notes.txt").read_text(), "mine")
        self.assertEqual((self.dest() / "src" / "a.js").read_text(), "a2")

    def test_existing_non_git_directory_is_left_alone(self):
        src = self.make()
        self.dest().mkdir(parents=True)
        (self.dest() / "keep.txt").write_text("precious")
        res = ss.sync_one(self.layout, src, self.opts)
        self.assertEqual(res.status, ss.BLOCKED)
        self.assertEqual((self.dest() / "keep.txt").read_text(), "precious")

    def test_remote_mismatch_is_blocked(self):
        src = self.make()
        ss.sync_one(self.layout, src, self.opts)
        gitops.run_git(["remote", "set-url", "origin", "https://example.com/other/repo"], cwd=str(self.dest()))
        res = ss.sync_one(self.layout, src, self.opts)
        self.assertEqual(res.status, ss.BLOCKED)
        self.assertIn("expected", res.message)

    def test_non_https_urls_are_refused(self):
        for url in ("http://example.com/x.git", "ext::sh -c touch /tmp/pwned", "ssh://git@example.com/x.git", "file:///etc"):
            with self.subTest(url=url):
                src = make_source("alpha", url=url)
                layout = helpers.make_toolkit(self.tmp, sources=[src])
                res = ss.sync_one(layout, src, ss.SyncOptions(min_free_mb=1))
                self.assertEqual((res.status, res.kind), (ss.FAILED, "policy"))
        self.assertFalse((self.tmp / "pwned").exists())

    def test_sparse_path_traversal_refused(self):
        src = self.make(acquisition_method="git_sparse", sparse_paths=["../escape"])
        res = ss.sync_one(self.layout, src, self.opts)
        self.assertEqual((res.status, res.kind), (ss.FAILED, "policy"))

    def test_failed_download_leaves_no_partial_directory(self):
        src = self.make()
        src["pinned_commit"] = "f" * 40  # does not exist upstream
        res = ss.sync_one(self.layout, src, self.opts)
        self.assertEqual(res.status, ss.FAILED)
        self.assertFalse(self.dest().exists())
        leftovers = [p.name for p in self.layout.sources_dir.iterdir()] if self.layout.sources_dir.exists() else []
        self.assertEqual(leftovers, [])

    def test_hooks_in_downloaded_repo_are_not_executed(self):
        marker = self.tmp / "hook-ran"
        hook = self.up.path / ".git" / "hooks" / "post-checkout"
        hook.write_text("#!/bin/sh\ntouch '%s'\n" % marker)
        hook.chmod(0o755)
        src = self.make()
        ss.sync_one(self.layout, src, self.opts)
        self.assertFalse(marker.exists())

    def test_insufficient_disk_space_is_reported(self):
        src = self.make()
        res = ss.sync_one(self.layout, src, ss.SyncOptions(allow_local_urls=True, min_free_mb=10 ** 9))
        self.assertEqual((res.status, res.kind), (ss.FAILED, "disk"))
        self.assertFalse(self.dest().exists())


class OfflineAndFailureTests(SyncBase):
    def test_offline_skips_missing_but_keeps_present(self):
        src = self.make()
        offline = ss.SyncOptions(allow_local_urls=True, offline=True, min_free_mb=1)
        res = ss.sync_one(self.layout, src, offline)
        self.assertEqual(res.status, ss.SKIPPED_OFFLINE)
        self.assertFalse(self.dest().exists())
        ss.sync_one(self.layout, src, self.opts)
        res = ss.sync_one(self.layout, src, offline)
        self.assertEqual((res.status, res.commit), (ss.UP_TO_DATE, self.c1))

    def test_offline_never_calls_git_fetch(self):
        src = self.make()
        ss.sync_one(self.layout, src, self.opts)
        shutil.rmtree(str(self.up.path))  # upstream disappears: any network use would fail loudly
        res = ss.sync_one(self.layout, src, ss.SyncOptions(allow_local_urls=True, offline=True, min_free_mb=1))
        self.assertEqual(res.status, ss.UP_TO_DATE)

    def test_offline_present_but_behind_pin_is_reported(self):
        src = self.make()
        ss.sync_one(self.layout, src, self.opts)
        src["pinned_commit"] = self.c2
        res = ss.sync_one(self.layout, src, ss.SyncOptions(allow_local_urls=True, offline=True, min_free_mb=1))
        self.assertEqual(res.status, ss.SKIPPED_OFFLINE)
        self.assertEqual(gitops.head_commit(str(self.dest())), self.c1)

    def test_unreachable_remote_is_a_failure_with_a_reason(self):
        src = make_source("alpha", url=(self.tmp / "does not exist").as_uri(), pinned_commit="a" * 40)
        layout = helpers.make_toolkit(self.tmp, sources=[src])
        res = ss.sync_one(layout, src, self.opts)
        self.assertEqual(res.status, ss.FAILED)
        self.assertIn(res.kind, ("not_found", "git_error", "network"))
        self.assertFalse((layout.sources_dir / "alpha").exists())

    def test_missing_git_is_reported_clearly(self):
        src = self.make()
        old = os.environ["PATH"]
        os.environ["PATH"] = ""
        try:
            res = ss.sync_one(self.layout, src, self.opts)
        finally:
            os.environ["PATH"] = old
        self.assertEqual((res.status, res.kind), (ss.FAILED, "missing_git"))
        self.assertEqual(ss.exit_code_for([res]), 4)

    def test_transient_failures_are_retried(self):
        src = self.make()
        calls = {"n": 0}
        real = gitops.run_git

        def flaky(args, *a, **kw):
            if args[0] == "fetch":
                calls["n"] += 1
                if calls["n"] == 1:
                    raise gitops.GitError("net", 1, "Could not resolve host", "network")
            return real(args, *a, **kw)

        gitops.run_git = flaky
        try:
            res = ss.sync_one(self.layout, src, self.opts)
        finally:
            gitops.run_git = real
        self.assertEqual(res.status, ss.ACQUIRED, res.message)
        self.assertEqual(calls["n"], 2)


class UpdateAndStatusTests(SyncBase):
    def test_update_moves_to_branch_tip_and_pins_can_be_written_back(self):
        src = self.make()
        ss.sync_one(self.layout, src, self.opts)
        res = ss.sync_one(self.layout, src, ss.SyncOptions(update=True, allow_local_urls=True, min_free_mb=1))
        self.assertEqual((res.status, res.commit), (ss.UPDATED, self.c2))
        before = self.layout.sources_yaml.read_text()
        catalog.update_source_fields(self.layout.sources_yaml, "alpha", {"pinned_commit": self.c2, "last_checked": "2026-10-10"})
        after = self.layout.sources_yaml.read_text()
        self.assertIn(self.c2, after)
        self.assertIn("2026-10-10", after)
        self.assertEqual(len(before.splitlines()), len(after.splitlines()))
        self.assertEqual(catalog.load_sources(self.layout)[0]["pinned_commit"], self.c2)

    def test_update_source_fields_preserves_comments_and_other_sources(self):
        text = "# header\nschema_version: 1\nsources:\n  - id: a\n    pinned_commit: %s  # keep me\n    last_checked: \"2026-01-01\"\n  - id: b\n    pinned_commit: %s\n    last_checked: null\n" % ("a" * 40, "b" * 40)
        path = self.tmp / "sources.yaml"
        path.write_text(text)
        catalog.update_source_fields(path, "b", {"pinned_commit": "c" * 40, "last_checked": "2026-10-10"})
        out = path.read_text()
        self.assertIn("# header", out)
        self.assertIn("# keep me", out)
        self.assertIn("pinned_commit: %s" % ("a" * 40), out)
        self.assertIn("pinned_commit: %s" % ("c" * 40), out)
        with self.assertRaises(catalog.CatalogError):
            catalog.update_source_fields(path, "ghost", {"pinned_commit": "c" * 40})

    def test_status_states(self):
        src = self.make()
        self.assertEqual(ss.source_status(self.layout, src)["state"], "missing")
        ss.sync_one(self.layout, src, self.opts)
        self.assertEqual(ss.source_status(self.layout, src)["state"], "at_pin")
        src2 = dict(src, pinned_commit=self.c2)
        self.assertEqual(ss.source_status(self.layout, src2)["state"], "off_pin")
        (self.dest() / "src" / "a.js").write_text("dirty")
        info = ss.source_status(self.layout, src)
        self.assertEqual((info["state"], info["dirty_files"]), ("dirty", 1))

    def test_status_detects_upstream_changes(self):
        src = self.make()
        ss.sync_one(self.layout, src, self.opts)
        info = ss.source_status(self.layout, src, check_upstream=True)
        self.assertEqual((info["upstream"], info["upstream_commit"]), ("ahead_of_pin", self.c2))
        info = ss.source_status(self.layout, dict(src, pinned_commit=self.c2), check_upstream=True)
        self.assertEqual(info["upstream"], "same_as_pin")

    def test_lock_file_records_commits(self):
        src = self.make()
        results = ss.sync_many(self.layout, [src], self.opts, jobs=1)
        lock = json.loads(self.layout.lock_path.read_text())
        self.assertEqual(lock["sources"]["alpha"]["commit"], self.c1)
        self.assertEqual(lock["sources"]["alpha"]["url"], self.up.url)
        self.assertEqual(results[0].status, ss.ACQUIRED)


class ExitCodeAndCliTests(SyncBase):
    def R(self, status, kind=None):
        return ss.SyncResult("x", status, "m", kind=kind)

    def test_exit_code_matrix(self):
        self.assertEqual(ss.exit_code_for([self.R(ss.ACQUIRED), self.R(ss.REFERENCE_ONLY)]), 0)
        self.assertEqual(ss.exit_code_for([self.R(ss.ACQUIRED), self.R(ss.FAILED, "network")]), 3)
        self.assertEqual(ss.exit_code_for([self.R(ss.FAILED, "network")]), 1)
        self.assertEqual(ss.exit_code_for([self.R(ss.SKIPPED_OFFLINE, "offline")]), 4)
        self.assertEqual(ss.exit_code_for([self.R(ss.UP_TO_DATE), self.R(ss.SKIPPED_OFFLINE, "offline")]), 3)
        self.assertEqual(ss.exit_code_for([self.R(ss.BLOCKED, "policy")]), 1)

    def test_cli_sync_list_status_show(self):
        src = self.make()
        base = ["--root", str(self.layout.root), "--home", str(self.layout.home)]
        code, out, _ = helpers.call_main(ss.main, ["sync", "alpha", "--allow-local-urls", "--min-free-mb", "1", "--jobs", "1"] + base)
        self.assertEqual(code, 0, out)
        self.assertIn("acquired", out)
        code, out, _ = helpers.call_main(ss.main, ["sync", "--all", "--allow-local-urls", "--min-free-mb", "1", "--offline"] + base)
        self.assertEqual(code, 0)
        self.assertIn("up_to_date", out)
        code, out, _ = helpers.call_main(ss.main, ["status", "--json"] + base)
        self.assertEqual(json.loads(out)[0]["state"], "at_pin")
        code, out, _ = helpers.call_main(ss.main, ["list", "--present"] + base)
        self.assertIn("alpha", out)
        code, out, _ = helpers.call_main(ss.main, ["show", "alpha"] + base)
        self.assertEqual(code, 0)
        self.assertIn("pinned commit:  " + self.c1, out)
        self.assertEqual(helpers.call_main(ss.main, ["show", "ghost"] + base)[0], 2)
        self.assertEqual(helpers.call_main(ss.main, ["sync", "ghost"] + base)[0], 2)

    def test_cli_offline_missing_exits_4_and_update_offline_is_usage_error(self):
        self.make()
        base = ["--root", str(self.layout.root), "--home", str(self.layout.home)]
        self.assertEqual(helpers.call_main(ss.main, ["sync", "alpha", "--allow-local-urls", "--offline"] + base)[0], 4)
        self.assertEqual(helpers.call_main(ss.main, ["sync", "alpha", "--update", "--offline"] + base)[0], 2)

    def test_cli_write_pins(self):
        self.make()
        base = ["--root", str(self.layout.root), "--home", str(self.layout.home)]
        code, out, _ = helpers.call_main(ss.main, ["sync", "alpha", "--update", "--write-pins", "--allow-local-urls", "--min-free-mb", "1"] + base)
        self.assertEqual(code, 0, out)
        self.assertEqual(catalog.load_sources(self.layout)[0]["pinned_commit"], self.c2)

    def test_parallel_jobs_produce_ordered_results(self):
        sources = []
        for i in range(3):
            up = helpers.Upstream(self.tmp, "up%d" % i)
            sha = up.commit({"f.txt": str(i)})
            sources.append(make_source("s%d" % i, url=up.url, pinned_commit=sha))
        layout = helpers.make_toolkit(self.tmp, sources=sources)
        results = ss.sync_many(layout, sources, self.opts, jobs=3)
        self.assertEqual([r.id for r in results], ["s0", "s1", "s2"])
        self.assertTrue(all(r.status == ss.ACQUIRED for r in results))


@unittest.skipUnless(os.environ.get("DESIGN_SENSEI_NETWORK_TESTS") == "1", "set DESIGN_SENSEI_NETWORK_TESTS=1 to run tests that use the real network")
class RealNetworkTests(helpers.TempDirTest):
    def test_sync_a_small_real_source_at_its_pin(self):
        from dslib.paths import resolve_layout
        real = resolve_layout(home=str(self.tmp / "real home"))
        sources = [s for s in catalog.load_sources(real) if s["id"] == "lenis"]
        res = ss.sync_many(real, sources, ss.SyncOptions(min_free_mb=1), jobs=1)[0]
        self.assertEqual(res.status, ss.ACQUIRED, res.message)
        self.assertEqual(res.commit, sources[0]["pinned_commit"])
        self.assertTrue((real.sources_dir / "lenis" / "LICENSE").is_file())


if __name__ == "__main__":
    unittest.main()
