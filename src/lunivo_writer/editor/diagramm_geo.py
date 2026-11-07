"""Kompatibler Importpfad für die Diagrammgeometrie."""

import sys as _sys

from .diagramme import diagramm_geo as _modul

_sys.modules[__name__] = _modul
