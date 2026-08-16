"""Pontifex: shared core library for agent-bridge MCP servers.

The supported public surface in this release is ``pontifex.core`` (see its
docstring for the module inventory) and ``pontifex.conventions`` /
``pontifex.testing``, and ``pontifex.backend`` (FROZEN at
``CONTRACT_API_VERSION = 1``: required members are stable within a minor line;
new behavior lands as defaulted fields or optional capability protocols).
Anything not documented as public is internal and may change without notice.
"""

from __future__ import annotations

__version__ = "0.3.0.dev0"

__all__ = ["__version__"]
