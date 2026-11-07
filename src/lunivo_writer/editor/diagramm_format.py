"""Kompatibler Importpfad für die Diagrammformatierung."""

import sys as _sys

from .diagramme import diagramm_format as _modul

_sys.modules[__name__] = _modul
