"""Kompatibilitätsmodul für verschobene Baukasten-Bausteine."""
from importlib import import_module as _import_module

_modul = _import_module(f"lunivo_writer.ui.baukasten.gestaltung.{__name__.rsplit('.', 1)[-1]}")
globals().update({k: v for k, v in vars(_modul).items() if not k.startswith("_")})
