import unittest

from tests import helpers
from dslib import config as ds_config
from dslib import yamlite
from dslib.jsonschema_lite import validate
from dslib.catalog import load_json


class ConfigTests(helpers.TempDirTest):
    def setUp(self):
        super().setUp()
        self.layout = helpers.make_toolkit(self.tmp)

    def test_defaults_only(self):
        values, origins, problems = ds_config.effective_config(self.layout, self.tmp)
        self.assertEqual(problems, [])
        self.assertEqual(values["design_variance"], 6)
        self.assertEqual(values["reduced_motion"], "respect")
        self.assertEqual(set(origins.values()), {"default"})

    def test_project_overrides_user_overrides_default(self):
        self.layout.home.mkdir(parents=True)
        self.layout.user_config_path.write_text("motion_intensity: 2\ndesign_variance: 9\n")
        project = self.tmp / "proj"
        project.mkdir()
        (project / ".design-sensei.yaml").write_text("motion_intensity: 8\nwebgl_enabled: false\n")
        values, origins, problems = ds_config.effective_config(self.layout, project)
        self.assertEqual(problems, [])
        self.assertEqual((values["motion_intensity"], origins["motion_intensity"]), (8, "project"))
        self.assertEqual((values["design_variance"], origins["design_variance"]), (9, "user"))
        self.assertEqual((values["webgl_enabled"], origins["webgl_enabled"]), (False, "project"))
        self.assertEqual(origins["visual_density"], "default")

    def test_invalid_values_are_reported_not_applied(self):
        project = self.tmp / "proj"
        project.mkdir()
        (project / ".design-sensei.yaml").write_text("motion_intensity: 11\nunknown_key: 1\n")
        values, _, problems = ds_config.effective_config(self.layout, project)
        self.assertTrue(problems)
        self.assertEqual(values["motion_intensity"], 5)  # default kept

    def test_broken_yaml_is_reported(self):
        project = self.tmp / "proj"
        project.mkdir()
        (project / ".design-sensei.yaml").write_text("a: yes\n")
        _, _, problems = ds_config.effective_config(self.layout, project)
        self.assertTrue(any("ambiguous" in p for p in problems))

    def test_allowed_dependencies_accepts_keyword_or_list(self):
        schema = load_json(self.layout.schemas_dir / "config.schema.json")
        self.assertEqual(validate({"allowed_dependencies": "none"}, schema), [])
        self.assertEqual(validate({"allowed_dependencies": ["gsap", "lenis"]}, schema), [])
        self.assertTrue(validate({"allowed_dependencies": "everything"}, schema))

    def test_example_template_and_defaults_are_valid(self):
        schema = load_json(self.layout.schemas_dir / "config.schema.json")
        template = yamlite.loads(ds_config.template(self.layout))
        self.assertEqual(validate(template, schema), [])
        self.assertEqual(validate(yamlite.load(self.layout.defaults_yaml), schema), [])
        self.assertEqual(template, yamlite.load(self.layout.defaults_yaml))  # the template documents the defaults

    def test_output_detail_default_enum_and_show(self):
        values, _, _ = ds_config.effective_config(self.layout, self.tmp)
        self.assertEqual(values["output_detail"], "normal")
        schema = load_json(self.layout.schemas_dir / "config.schema.json")
        for ok in ("brief", "normal", "full"):
            self.assertEqual(validate({"output_detail": ok}, schema), [])
        self.assertTrue(validate({"output_detail": "verbose"}, schema))
        self.assertIn("output_detail", ds_config.render(values, {k: "default" for k in values}))

    def test_render_marks_origins(self):
        values, origins, _ = ds_config.effective_config(self.layout, self.tmp)
        text = ds_config.render(values, origins)
        self.assertIn("design_variance", text)
        self.assertIn("# from default", text)
        self.assertEqual(yamlite.loads(text.replace("  # from default", "")), values)


if __name__ == "__main__":
    unittest.main()
