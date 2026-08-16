"""Pontifex: shared core library for agent-bridge MCP servers.

The supported public surface in this release is ``pontifex.core`` (see its
docstring for the module inventory) and ``pontifex.conventions`` /
``pontifex.testing``. ``pontifex.backend`` is PROVISIONAL until its
``CONTRACT_API_VERSION`` reaches 1 — required members may change in any 0.x
release. Anything not documented as public is internal and may change without
notice.
"""

from __future__ import annotations

__version__ = "0.2.0.dev0"

__all__ = ["__version__"]
