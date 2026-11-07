"""Kompatibler Importpfad für Kreisdiagramme."""

import sys as _sys

from .diagramme import diagramm_kreis as _modul

_sys.modules[__name__] = _modul
