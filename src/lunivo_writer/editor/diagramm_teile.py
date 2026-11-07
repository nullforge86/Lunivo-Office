"""Kompatibler Importpfad für die Auswahl von Diagrammteilen."""

import sys as _sys

from .diagramme import diagramm_teile as _modul

_sys.modules[__name__] = _modul
