"""Guard against version drift between the package attribute and the wheel
metadata. The two are declared in different files (``__init__.py`` and
``pyproject.toml``) with no single source, so only this pin keeps them equal —
it caught a real drift (``__version__`` stuck at 0.3.0.dev0 across two bumps).
"""

from __future__ import annotations

import importlib.metadata

import pontifex


def test_dunder_version_matches_distribution_metadata():
    assert pontifex.__version__ == importlib.metadata.version("pontifex")
