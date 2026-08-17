"""Guard the single-sourced version.

``pontonier.__version__`` now reads the installed distribution metadata, so the
attribute can no longer drift from the wheel it ships in. What it CAN drift from
is the source tree: an editable install records the version at install time, so
a bump to ``pyproject.toml`` without a re-sync leaves the metadata stale. The
first test pins that, and it is what makes ``pyproject.toml`` the single source
in practice rather than only on paper. The second keeps the attribute derived,
so a future edit cannot quietly reintroduce a hardcoded literal.
"""

from __future__ import annotations

import importlib.metadata
import tomllib
from pathlib import Path

import pontonier

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


def test_distribution_metadata_matches_pyproject():
    declared = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["version"]
    assert importlib.metadata.version("pontonier") == declared


def test_dunder_version_is_the_distribution_metadata():
    assert pontonier.__version__ == importlib.metadata.version("pontonier")
