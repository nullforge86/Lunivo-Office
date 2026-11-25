"""Die Grundfarben der Oberfläche (``Farbe.AKZENT`` statt ``"#2f6fb5"``): eine eigene Farbtafel der Oberfläche mit den Werten aus ``writer``.

Das Farbthema (``thema/thema.py``) stellt einzelne Farben dieser Tafel um. Die Farben des Kerns bleiben davon unberührt: Was Qt hier ändert,
erreicht weder das Dokument noch dessen Darstellung."""
from __future__ import annotations

from writer.werte import grundfarben as _grundfarben


class Farbe:
    """Grundfarben der Oberfläche; die Namen sind dieselben wie im Kern, die Werte eine Kopie."""


for _name, _wert in _grundfarben().items():
    setattr(Farbe, _name, _wert)
del _name, _wert
