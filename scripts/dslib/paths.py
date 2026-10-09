"""Locate the toolkit root, the local source library and the state directory.

Three places matter and they are deliberately separate:

* **toolkit root**  - the directory holding ``catalog/``, ``knowledge/`` and ``scripts/``.
  For a plugin install this is the plugin cache directory (read-only by convention,
  replaced on update); for a contributor it is the git checkout.
* **library home**  - where downloaded upstream sources and local state live. It must
  survive plugin updates, so it is *not* inside an installed plugin.
* **project dir**   - the application being designed (``.design-sensei.yaml`` lives here).

Library home resolution, first match wins:
  1. ``--home PATH`` on the command line
  2. ``DESIGN_SENSEI_HOME`` environment variable
  3. the toolkit root itself when it is a git checkout (contributor workflow;
     ``sources/`` and ``.state/`` are git-ignored there)
  4. ``~/.design-sensei``
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping, Optional

ENV_ROOT = "DESIGN_SENSEI_ROOT"
ENV_HOME = "DESIGN_SENSEI_HOME"
STATE_DIRNAME = ".state"
SOURCES_DIRNAME = "sources"


class LayoutError(RuntimeError):
    """The toolkit cannot find its own files."""


class Layout(object):
    """Resolved filesystem locations for one invocation."""

    def __init__(self, root: Path, home: Path, home_reason: str):
        self.root = Path(root)
        self.home = Path(home)
        self.home_reason = home_reason

    # toolkit (read-only) ---------------------------------------------------
    @property
    def catalog_dir(self) -> Path:
        return self.root / "catalog"

    @property
    def schemas_dir(self) -> Path:
        return self.catalog_dir / "schemas"

    @property
    def sources_yaml(self) -> Path:
        return self.catalog_dir / "sources.yaml"

    @property
    def patterns_yaml(self) -> Path:
        return self.catalog_dir / "patterns.yaml"

    @property
    def licenses_yaml(self) -> Path:
        return self.catalog_dir / "licenses.yaml"

    @property
    def knowledge_dir(self) -> Path:
        return self.root / "knowledge"

    @property
    def skill_dir(self) -> Path:
        return self.root / "skills" / "design-sensei"

    @property
    def defaults_yaml(self) -> Path:
        return self.skill_dir / "config" / "defaults.yaml"

    # library (writable) ------------------------------------------------------
    @property
    def sources_dir(self) -> Path:
        return self.home / SOURCES_DIRNAME

    @property
    def state_dir(self) -> Path:
        return self.home / STATE_DIRNAME

    @property
    def lock_path(self) -> Path:
        return self.state_dir / "lock.json"

    @property
    def source_index_path(self) -> Path:
        return self.state_dir / "source-index.json"

    @property
    def user_config_path(self) -> Path:
        return self.home / "config.yaml"

    def source_path(self, source: Mapping[str, object]) -> Path:
        """Directory of one source inside the local library."""
        return self.sources_dir / str(source.get("local_path") or source["id"])

    def is_dev_checkout(self) -> bool:
        return (self.root / ".git").exists()


def default_root() -> Path:
    # scripts/dslib/paths.py -> scripts/dslib -> scripts -> <root>
    return Path(__file__).resolve().parents[2]


def resolve_layout(
    root: Optional[str] = None,
    home: Optional[str] = None,
    env: Optional[Mapping[str, str]] = None,
) -> Layout:
    """Resolve toolkit root and library home. ``env`` defaults to ``os.environ``."""
    env = os.environ if env is None else env
    root_path = Path(root or env.get(ENV_ROOT) or default_root()).expanduser().resolve()
    if not (root_path / "catalog" / "sources.yaml").is_file():
        raise LayoutError(
            "cannot find the Design Sensei catalog under %s (expected catalog/sources.yaml). "
            "Set %s to a checkout or plugin directory of design-sensei." % (root_path, ENV_ROOT)
        )
    if home:
        home_path, reason = Path(home).expanduser(), "--home option"
    elif env.get(ENV_HOME):
        home_path, reason = Path(env[ENV_HOME]).expanduser(), "%s environment variable" % ENV_HOME
    elif (root_path / ".git").exists():
        home_path, reason = root_path, "development checkout (sources/ inside the repository, git-ignored)"
    else:
        home_path, reason = Path.home() / ".design-sensei", "default user library (~/.design-sensei)"
    return Layout(root_path, home_path.resolve() if home_path.exists() else home_path.absolute(), reason)


def find_project_config(start: Optional[Path] = None) -> Optional[Path]:
    """Walk up from ``start`` (default: cwd) looking for ``.design-sensei.yaml``."""
    current = Path(start or Path.cwd()).resolve()
    for directory in [current] + list(current.parents):
        candidate = directory / ".design-sensei.yaml"
        if candidate.is_file():
            return candidate
        if directory == Path.home():
            break
    return None
