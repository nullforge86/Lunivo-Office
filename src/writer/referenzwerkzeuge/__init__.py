"""Tür des Pakets ``writer.referenzwerkzeuge`` (Funktion „Verweise“). Aufrufer außerhalb des Pakets importieren nur von hier."""
from __future__ import annotations

__all__ = ["verweise_befehle"]


def __getattr__(name: str):
    if name == "verweise_befehle":
        from writer.referenzwerkzeuge.verweise import verweise_befehle
        return verweise_befehle
    raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
