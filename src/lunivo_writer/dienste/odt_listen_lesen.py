"""ODT lesen: Listen (``text:list``) → Listen im QTextDocument, Aufzählungs- und Nummernart aus der Listenvorlage.

Als Baustein ``_ODTListen`` in ``odt_reader._Leser`` eingemischt; braucht dessen ``stile``, ``absatz`` und ``bereich``.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

from PySide6.QtGui import QTextCursor, QTextListFormat

from lunivo_writer.dienste.odt_xml import _q

_NUMMER_ART = {"a": QTextListFormat.ListLowerAlpha, "A": QTextListFormat.ListUpperAlpha,
               "i": QTextListFormat.ListLowerRoman, "I": QTextListFormat.ListUpperRoman}
_PUNKT_ART = {"◦": QTextListFormat.ListCircle, "○": QTextListFormat.ListCircle, "▪": QTextListFormat.ListSquare,
              "■": QTextListFormat.ListSquare}


class _ODTListen:
    def listenpunkt(self, cur: QTextCursor, listen: dict, stil: str | None, ebene: int) -> None:
        if ebene not in listen:
            lf = QTextListFormat()
            lf.setIndent(ebene)
            lf.setStyle(self._listenart(stil, ebene))
            listen[ebene] = cur.createList(lf)
        else:
            listen[ebene].add(cur.block())
        for tiefer in [e for e in listen if e > ebene]:
            del listen[tiefer]

    def _listenart(self, stil: str | None, ebene: int):
        ls = self.stile.listen.get(stil or "")
        for k in (ls if ls is not None else ()):
            if k.get(_q("text:level")) != str(ebene):
                continue
            if k.tag == _q("text:list-level-style-number"):
                return _NUMMER_ART.get(k.get(_q("style:num-format"), "1"), QTextListFormat.ListDecimal)
            return _PUNKT_ART.get(k.get(_q("text:bullet-char"), "•"), QTextListFormat.ListDisc)
        return QTextListFormat.ListDisc

    def liste(self, el: ET.Element, ort, listen: dict | None = None, stil: str | None = None, ebene: int = 1) -> None:
        stil = el.get(_q("text:style-name")) or stil
        listen = {} if listen is None else listen
        for punkt in el:
            if punkt.tag not in (_q("text:list-item"), _q("text:list-header")):
                continue
            for k in punkt:
                if k.tag in (_q("text:p"), _q("text:h")):
                    self.absatz(k, ort, (listen, stil or self.stile.liste_von(k.get(_q("text:style-name"))), ebene)
                                if punkt.tag == _q("text:list-item") else None)
                elif k.tag == _q("text:list"):
                    self.liste(k, ort, listen, stil, ebene + 1)
                else:
                    self.bereich([k], ort)
