"""Project configuration: defaults < user config < project ``.design-sensei.yaml``."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import yamlite
from .catalog import CatalogError, load_json, load_yaml
from .jsonschema_lite import validate
from .paths import Layout, find_project_config

SOURCE_DEFAULT = "default"
SOURCE_USER = "user"
SOURCE_PROJECT = "project"


def load_layers(layout: Layout, project_dir: Optional[Path] = None) -> Tuple[Dict[str, Tuple[Any, str]], List[str]]:
    """Return ({key: (value, origin)}, [problems]) for the effective configuration."""
    problems = []  # type: List[str]
    schema = load_json(layout.schemas_dir / "config.schema.json")
    effective = {}  # type: Dict[str, Tuple[Any, str]]
    layers = [(layout.defaults_yaml, SOURCE_DEFAULT), (layout.user_config_path, SOURCE_USER)]
    project = find_project_config(project_dir)
    if project is not None:
        layers.append((project, SOURCE_PROJECT))
    for path, origin in layers:
        if not path.is_file():
            if origin == SOURCE_DEFAULT:
                problems.append("missing defaults file %s" % path)
            continue
        try:
            data = load_yaml(path) or {}
        except CatalogError as exc:
            problems.append(str(exc))
            continue
        if not isinstance(data, dict):
            problems.append("%s must be a mapping" % path)
            continue
        errors = validate(data, schema)
        if errors:
            problems.extend("%s: %s" % (path, e) for e in errors)
            continue
        for key, value in data.items():
            effective[key] = (value, origin)
    return effective, problems


def effective_config(layout: Layout, project_dir: Optional[Path] = None) -> Tuple[Dict[str, Any], Dict[str, str], List[str]]:
    layered, problems = load_layers(layout, project_dir)
    values = {k: v for k, (v, _) in layered.items()}
    origins = {k: o for k, (_, o) in layered.items()}
    return values, origins, problems


def template(layout: Layout) -> str:
    """The commented template written by ``config init``."""
    path = layout.skill_dir / "config" / "config.example.yaml"
    return path.read_text(encoding="utf-8")


def render(values: Dict[str, Any], origins: Dict[str, str]) -> str:
    lines = []
    for key in sorted(values):
        dumped = yamlite.dumps({key: values[key]}).rstrip("\n").split("\n")
        dumped[0] = "%-24s  # from %s" % (dumped[0], origins.get(key, "?")) if len(dumped) == 1 else dumped[0] + "  # from %s" % origins.get(key, "?")
        lines.extend(dumped)
    return "\n".join(lines) + "\n"
