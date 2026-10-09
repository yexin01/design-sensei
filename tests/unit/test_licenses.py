import json
import unittest

from tests import helpers
from tests.helpers import make_source
import check_licenses as cl
from dslib import catalog, yamlite

MIT_TEXT = """MIT License

Copyright (c) 2024 Jane Doe

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
"""
CURLY_MIT = MIT_TEXT.replace('"Software"', "“Software”").replace('"AS IS"', "“AS IS”")
APACHE = "Apache License\nVersion 2.0, January 2004\nhttp://www.apache.org/licenses/\n\n   Copyright [yyyy] [name of copyright owner]\n"
COMMONS = MIT_TEXT + "\nCommons Clause License Condition v1.0\nThe Software may not be sold.\n"
BSD3 = "Copyright (c) 2020 Foo\nRedistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:\n * this list of conditions\n * Neither the name of Foo nor the names of its contributors may be used\n"
ISC = "Copyright (c) 2019 Bar\n\nPermission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted\n"
CUSTOM = "You may look at this code. Do not use it for anything else.\nAll rights reserved.\n"


class DetectionTests(unittest.TestCase):
    def test_known_licenses(self):
        cases = {"MIT": MIT_TEXT, "Apache-2.0": APACHE, "BSD-3-Clause": BSD3, "ISC": ISC, "LicenseRef-MIT-Commons-Clause": COMMONS}
        for expected, text in cases.items():
            with self.subTest(expected):
                self.assertEqual(cl.detect_spdx(text)[0], expected)

    def test_curly_quotes_do_not_break_mit_detection(self):
        self.assertEqual(cl.detect_spdx(CURLY_MIT)[0], "MIT")

    def test_custom_text_is_flagged_not_guessed(self):
        spdx, hints = cl.detect_spdx(CUSTOM)
        self.assertEqual(spdx, "LicenseRef-Custom")

    def test_restriction_hints(self):
        self.assertTrue(any("Commons Clause" in h for h in cl.detect_spdx(COMMONS)[1]))
        self.assertTrue(any("non-commercial" in h for h in cl.detect_spdx("Creative Commons NonCommercial 4.0")[1]))

    def test_copyright_lines_skip_boilerplate(self):
        self.assertEqual(cl.copyright_lines(MIT_TEXT), ["Copyright (c) 2024 Jane Doe"])
        self.assertEqual(cl.copyright_lines(APACHE), [])
        self.assertEqual(cl.copyright_lines("Copyright 2026 hoainho\nCopyright (c) 2019-2025 Poimandres"), ["Copyright 2026 hoainho", "Copyright (c) 2019-2025 Poimandres"])


class ScanTests(helpers.TempDirTest):
    def make_clone(self, layout, sid="alpha", files=None):
        root = layout.sources_dir / sid
        root.mkdir(parents=True)
        for rel, text in (files or {}).items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")
        return root

    def test_scan_collects_files_copyright_and_manifest_license(self):
        layout = helpers.make_toolkit(self.tmp)
        self.make_clone(layout, files={"LICENSE": MIT_TEXT, "NOTICE": "notice text", "package.json": json.dumps({"name": "a", "license": "MIT"}),
                                       "packages/x/package.json": json.dumps({"name": "x", "license": "ISC"})})
        scan = cl.scan_source(layout, make_source("alpha"))
        self.assertEqual(scan["spdx_detected"], "MIT")
        self.assertEqual([f["path"] for f in scan["license_files"]], ["LICENSE", "NOTICE"])
        self.assertEqual(scan["copyright"], ["Copyright (c) 2024 Jane Doe"])
        self.assertEqual(scan["package_manifest_licenses"], ["ISC", "MIT"])

    def test_scan_returns_none_when_not_downloaded_or_reference_only(self):
        layout = helpers.make_toolkit(self.tmp)
        self.assertIsNone(cl.scan_source(layout, make_source("alpha")))
        self.make_clone(layout)
        self.assertIsNone(cl.scan_source(layout, make_source("alpha", acquisition_method="reference_only")))

    def test_nested_license_files_found_outside_dependency_dirs(self):
        layout = helpers.make_toolkit(self.tmp)
        self.make_clone(layout, files={"LICENSE": MIT_TEXT, "assets/LICENSE.txt": CUSTOM, "node_modules/dep/LICENSE": APACHE})
        scan = cl.scan_source(layout, make_source("alpha"))
        self.assertEqual([n["path"] for n in scan["nested_license_files"]], ["assets/LICENSE.txt"])

    def findings(self, layout, src, scan, review=None):
        return {f.code: f for f in cl.check_source(layout, src, review, scan)}

    def test_mismatch_is_an_error(self):
        layout = helpers.make_toolkit(self.tmp)
        self.make_clone(layout, files={"LICENSE": APACHE})
        found = self.findings(layout, make_source("alpha", license="MIT"), cl.scan_source(layout, make_source("alpha")))
        self.assertEqual(found["mismatch"].level, "error")

    def test_verified_claim_without_license_file_is_an_error(self):
        layout = helpers.make_toolkit(self.tmp)
        self.make_clone(layout, files={"README.md": "x"})
        found = self.findings(layout, make_source("alpha"), cl.scan_source(layout, make_source("alpha")))
        self.assertEqual(found["claims_verified"].level, "error")
        self.assertIn("no_license_file", found)

    def test_custom_and_restrictive_terms_need_human_review(self):
        layout = helpers.make_toolkit(self.tmp)
        self.make_clone(layout, files={"LICENSE.md": COMMONS})
        src = make_source("alpha", license="LicenseRef-MIT-Commons-Clause", license_status="custom_terms", redistribution_status="license_specific")
        found = self.findings(layout, src, cl.scan_source(layout, src))
        self.assertIn("needs_human_review", found)
        self.assertNotIn("mismatch", found)

    def test_changed_license_file_and_stale_review_are_detected(self):
        layout = helpers.make_toolkit(self.tmp)
        self.make_clone(layout, files={"LICENSE": MIT_TEXT})
        src = make_source("alpha")
        scan = cl.scan_source(layout, src)
        review = cl.merge_review(None, scan, src)
        self.assertNotIn("license_changed", self.findings(layout, src, scan, review))
        (layout.sources_dir / "alpha" / "LICENSE").write_text(MIT_TEXT + "\nextra")
        self.assertIn("license_changed", self.findings(layout, src, cl.scan_source(layout, src), review))

    def test_reference_only_and_not_synced_are_informational(self):
        layout = helpers.make_toolkit(self.tmp)
        site = make_source("site", type="website", acquisition_method="reference_only", pinned_commit=None, license="NOASSERTION", license_status="unknown", redistribution_status="reference_only")
        self.assertEqual({f.level for f in cl.check_source(layout, site, None, None)}, {"info"})
        self.assertEqual({f.code for f in cl.check_source(layout, make_source("alpha"), None, None)}, {"not_synced"})


class LedgerTests(helpers.TempDirTest):
    def test_merge_keeps_human_fields_and_downgrades_on_change(self):
        layout = helpers.make_toolkit(self.tmp)
        root = layout.sources_dir / "alpha"
        root.mkdir(parents=True)
        (root / "LICENSE").write_text(MIT_TEXT)
        src = make_source("alpha")
        scan = cl.scan_source(layout, src)
        first = cl.merge_review(None, scan, src)
        self.assertEqual(first["review_status"], "auto_checked")
        reviewed = dict(first, review_status="human_reviewed", notes="Checked by a person.", restrictions=["manual note"])
        again = cl.merge_review(reviewed, scan, src)
        self.assertEqual((again["review_status"], again["notes"], again["restrictions"]), ("human_reviewed", "Checked by a person.", ["manual note"]))
        (root / "LICENSE").write_text(MIT_TEXT + "\nchanged")
        changed = cl.merge_review(reviewed, cl.scan_source(layout, src), src)
        self.assertEqual(changed["review_status"], "auto_checked")
        self.assertEqual(changed["notes"], "Checked by a person.")

    def test_write_ledger_round_trips_and_validates(self):
        layout = helpers.make_toolkit(self.tmp)
        root = layout.sources_dir / "alpha"
        root.mkdir(parents=True)
        (root / "LICENSE").write_text(MIT_TEXT)
        sources = catalog.load_sources(layout)
        scans = {s["id"]: cl.scan_source(layout, s) for s in sources}
        self.assertEqual(cl.write_ledger(layout, scans, sources), ["alpha"])
        text = layout.licenses_yaml.read_text()
        self.assertTrue(text.startswith("# License policy"))
        reviews = catalog.load_licenses(layout)["reviews"]
        self.assertEqual(reviews[0]["source_id"], "alpha")
        self.assertEqual(reviews[0]["spdx_detected"], "MIT")
        self.assertEqual(cl.write_ledger(layout, scans, sources), ["alpha"])
        self.assertEqual(layout.licenses_yaml.read_text(), text)  # deterministic


class AttributionReportTests(helpers.TempDirTest):
    def test_report_lists_every_source_and_is_deterministic(self):
        sources = [make_source("alpha"), make_source("beta", license_status="custom_terms", redistribution_status="license_specific", license="LicenseRef-Custom-Terms")]
        layout = helpers.make_toolkit(self.tmp, sources=sources)
        text = cl.render_attribution(layout)
        self.assertIn("Alpha", text)
        self.assertIn("Beta", text)
        self.assertIn("not legal advice", text)
        self.assertIn("does not include or redistribute", text)
        self.assertEqual(text, cl.render_attribution(layout))

    def test_report_command_check_mode(self):
        layout = helpers.make_toolkit(self.tmp)
        out = self.tmp / "ATTRIBUTION.md"
        args = ["report", "--root", str(layout.root), "--home", str(layout.home), "--output", str(out)]
        self.assertEqual(helpers.call_main(cl.main, args)[0], 0)
        self.assertEqual(helpers.call_main(cl.main, args + ["--check"])[0], 0)
        out.write_text(out.read_text() + "tampered")
        self.assertEqual(helpers.call_main(cl.main, args + ["--check"])[0], 1)

    def test_committed_attribution_is_up_to_date(self):
        from dslib.paths import resolve_layout
        layout = resolve_layout(home=str(self.tmp / "h"))
        path = layout.root / "ATTRIBUTION.md"
        if not path.exists():
            self.skipTest("ATTRIBUTION.md not generated yet")
        self.assertEqual(path.read_text(encoding="utf-8"), cl.render_attribution(layout))


class CheckCommandTests(helpers.TempDirTest):
    def test_exit_codes(self):
        layout = helpers.make_toolkit(self.tmp)
        root = layout.sources_dir / "alpha"
        root.mkdir(parents=True)
        (root / "LICENSE").write_text(APACHE)
        base = ["--root", str(layout.root), "--home", str(layout.home)]
        code, out, _ = helpers.call_main(cl.main, ["check"] + base)
        self.assertEqual(code, 1)  # catalog says MIT, file says Apache
        self.assertIn("mismatch", out)
        (root / "LICENSE").write_text(MIT_TEXT)
        self.assertEqual(helpers.call_main(cl.main, ["check"] + base)[0], 0)
        self.assertEqual(helpers.call_main(cl.main, ["check", "ghost"] + base)[0], 2)
        self.assertEqual(helpers.call_main(cl.main, ["check", "--strict"] + base)[0], 1)  # no review entry warning


if __name__ == "__main__":
    unittest.main()
