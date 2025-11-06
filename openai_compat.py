"""
Compatibility helpers for newer OpenAI Python SDK versions.

`langchain-openai` (<=0.2.x) still attempts to pass a `proxies` keyword to
`openai.OpenAI`. Starting in openai>=1.53 the constructor no longer accepts
that parameter directly. This module patches the client at import time so the
kwarg is still tolerated and routed through an `httpx` client, allowing the
rest of the codebase—and LangChain adapters—to continue working unchanged.
"""

from __future__ import annotations


def patch_openai_client() -> None:
    try:
        import inspect
        import openai
    except Exception:
        return

    client_cls = getattr(openai, "OpenAI", None)
    if client_cls is None:
        return

    sig = inspect.signature(client_cls.__init__)
    if "proxies" in sig.parameters:
        # The current SDK still accepts `proxies`; nothing to patch.
        return

    original_init = client_cls.__init__

    def patched_init(self, *args, proxies=None, **kwargs):  # type: ignore[override]
        if proxies:
            try:
                import httpx

                timeout = kwargs.get("timeout", None)
                http_client = httpx.Client(proxies=proxies, timeout=timeout)
                kwargs["http_client"] = http_client
            except Exception:
                # Silently ignore proxy setup issues; fall back to default transport.
                pass
        return original_init(self, *args, **kwargs)

    client_cls.__init__ = patched_init  # type: ignore[assignment]


patch_openai_client()

