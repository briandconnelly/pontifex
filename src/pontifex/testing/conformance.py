"""Adapter conformance: does a backend implementation honor its contract?

Structural conformance (``isinstance(backend, AgentBackend)``) only proves the
members exist; these checks probe the INVARIANTS that made the protocol
necessary. Each returns violation strings (empty = pass).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pontifex.backend.protocol import AgentBackend, RunRequest
from pontifex.testing.surface_honesty import find_contract_self_contradictions

if TYPE_CHECKING:
    from pontifex.backend.contract import BackendContract


def check_contract(contract: BackendContract) -> list[str]:
    """Static invariants a contract must satisfy on its own."""
    out: list[str] = []
    out.extend(
        find_contract_self_contradictions(
            contract.forbidden_surface_phrases,
            {
                "readonly_honesty_statement": contract.readonly_honesty_statement,
                "implicit_context_disclosure": contract.implicit_context_disclosure,
            },
        )
    )
    overlap = set(contract.always_send_flags) & set(contract.help_gated_flags)
    if overlap:
        out.append(
            f"flags {sorted(overlap)} are both always-send and help-gated; a flag has "
            "exactly one gating class"
        )
    if (
        contract.limits.max_argv_prompt_chars is not None
        and contract.limits.max_argv_prompt_chars <= 0
    ):
        out.append("max_argv_prompt_chars must be positive when set")
    if "usage_accounting" in contract.supported_features and not contract.usage_event_markers:
        out.append(
            "contract declares usage_accounting but lists no usage_event_markers to extract it from"
        )
    return out


def check_backend(contract: BackendContract, backend: object) -> list[str]:
    """Behavioral invariants, probed without spawning the real CLI. The backend
    under test may be the real adapter with its subprocess seams stubbed, or a
    fake standing in for one during protocol development."""
    out: list[str] = []
    if not isinstance(backend, AgentBackend):
        out.append("backend does not structurally implement AgentBackend")
        return out

    if contract.effort_silently_ignored_upstream:
        # The upstream CLI accepts a bad effort and exits 0, so spend-side
        # validation is the ONLY protection. An adapter that lets a bogus effort
        # through will burn money and silently produce a default-effort answer.
        bogus = RunRequest(
            kind="consult",
            prompt="conformance probe",
            cwd=".",
            timeout_seconds=1,
            reasoning_effort="not-a-real-effort-level",
        )
        if backend.validate_request(bogus) is None:
            out.append(
                "contract says effort is silently ignored upstream, but "
                "validate_request accepted a bogus reasoning_effort — pre-spend "
                "validation is mandatory for this backend"
            )
    return out
