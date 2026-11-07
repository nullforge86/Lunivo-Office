"""Kompatibler Importpfad für zusätzliche Diagrammelemente."""

import sys as _sys

from .diagramme import diagramm_zusatz as _modul

_sys.modules[__name__] = _modul
