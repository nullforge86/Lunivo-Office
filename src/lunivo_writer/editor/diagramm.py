"""Kompatibler Importpfad für den Diagrammzeichner."""

import sys as _sys

from .diagramme import diagramm as _modul

_sys.modules[__name__] = _modul
