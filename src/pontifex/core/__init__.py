"""Generic agent-bridge core.

These modules are deliberately free of any backend-specific knowledge. The
dependency rule is one-way: ``pontifex.core`` never imports from the rest of
the ``pontifex`` package (enforced by import-linter in CI). This is what keeps
the core reusable by every bridge regardless of which backend, conventions, or
testing pieces it adopts.
"""
