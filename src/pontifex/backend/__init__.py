"""The backend adapter layer: what a bridge must say and do about its CLI.

**PROVISIONAL.** This protocol ships unfrozen: it is validated against fakes
until every real adapter (Codex, Kimi, Claude) compiles, type-checks, and
passes golden fixtures. Required members may still change in any 0.x release
until ``CONTRACT_API_VERSION`` reaches 1. After the freeze, required Protocol
members and required BackendContract fields are frozen within a minor line —
"additive" changes to a Protocol or a frozen dataclass are breaking, so new
behavior lands as optional capability protocols or defaulted fields.
"""

from __future__ import annotations

# 0 = provisional. Set to 1 when all three real adapters pass their conformance
# and golden fixtures (plan milestone M4).
CONTRACT_API_VERSION = 0
