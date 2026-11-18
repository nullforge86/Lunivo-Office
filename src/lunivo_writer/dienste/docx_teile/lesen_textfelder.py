"""DOCX lesen: Textfelder (``wps:wsp`` mit ``wps:txbx``/``wps:linkedTxbx``) und ihre Verknüpfungsketten.

Das Bild des Textfelds und die Lage liest ``lesen_objekte`` (``_frei``); hier stehen nur die Parameter des Textfelds."""
from __future__ import annotations

import json

from lunivo_writer.dienste.docx_teile.lesen_gemeinsam import (
    qn,
    QTextCursor,
    _xp,
)

_TITEL_VORSATZ = "lunivo:"
_ZEICHEN_FLAGS = (("fett", "w:b"), ("kursiv", "w:i"), ("durch", "w:strike"))             # Schlüssel des Programms → DOCX-Element
_STANDARD = {"text": "", "schrift": "Liberation Sans", "pt": 11, "farbe": "#1f1f1f"}      # Vorgaben eines Textfelds


class TextfeldMixin:
    """DOCX lesen: Parameter von Textfeldern, Läufe darin und Verknüpfungen."""

    def _textfeld_daten(self, drawing, wsp) -> dict:
        """Die Parameter eines Textfelds (``editor/objekte/frei_objekt.py``): genau die gespeicherten aus dem Titel („lunivo:“), sonst aus dem Text des
        Kastens (``w:txbxContent``) und seiner Verknüpfung (``wps:linkedTxbx`` mit ``id`` und ``seq``)."""
        gespeichert = self._textfeld_aus_titel(drawing)
        if gespeichert is not None:
            return gespeichert
        daten: dict = dict(_STANDARD)
        laeufe = self._textfeld_laeufe(wsp)
        for r in laeufe:                                           # was dem Standard des Textfelds entspricht, ist keine eigene Angabe
            if r.get("pt") == daten["pt"]:
                r.pop("pt")
            if r.get("fuell") == daten["farbe"]:
                r.pop("fuell")
        daten["text"] = "".join(r["t"] for r in laeufe)
        self._textfeld_innen(wsp, daten)
        if any(len(r) > 1 for r in laeufe):
            daten["laeufe"] = laeufe
        self._textfeld_kette(wsp, daten)
        return daten

    @staticmethod
    def _textfeld_innen(wsp, daten: dict) -> None:
        """Innenabstand des Textes (``wps:bodyPr`` lIns/tIns/rIns/bIns, EMU) als ``innen`` [links, oben, rechts, unten] in Bildpunkten; nur wenn er
        vom Standard des Textfelds abweicht. Fehlt eine Angabe, gilt der DOCX-Standard (0,25 cm links/rechts, 0,125 cm oben/unten)."""
        from lunivo_writer.editor.objekte.freie_bilder import emu_zu_px
        from lunivo_writer.editor.objekte.frei_objekt_text import TEXTRAND
        bp = _xp(wsp, "wps:bodyPr")
        if not bp:
            return
        standard = {"lIns": 91440, "tIns": 45720, "rIns": 91440, "bIns": 45720}
        try:
            w = [emu_zu_px(bp[0].get(k) or standard[k]) for k in ("lIns", "tIns", "rIns", "bIns")]
        except (TypeError, ValueError):
            return
        if any(abs(x - TEXTRAND) > 0.01 for x in w):
            daten["innen"] = [round(x, 2) for x in w]

    @staticmethod
    def _textfeld_aus_titel(drawing):
        """Die vom Programm gespeicherten Parameter aus dem Titel des Objekts, sonst None."""
        titel = _xp(drawing, ".//wp:docPr/@title")
        if titel and titel[0].startswith(_TITEL_VORSATZ):
            try:
                o = json.loads(titel[0][len(_TITEL_VORSATZ):])
                if o.get("art") == "textfeld" and isinstance(o.get("daten"), dict):
                    return o["daten"]
            except ValueError:
                pass
        return None

    def _textfeld_laeufe(self, wsp) -> list:
        """Läufe aller Absätze des Kastens; Absätze werden durch einen Lauf mit Zeilenumbruch getrennt."""
        laeufe: list[dict] = []
        for i, p in enumerate(_xp(wsp, "wps:txbx/w:txbxContent/w:p")):
            if i:
                laeufe.append({"t": "\n"})
            for r in _xp(p, "w:r"):
                t = "".join(_xp(r, "w:t/text()"))
                if t:
                    laeufe.append(self._textfeld_lauf(r, t))
        return laeufe

    def _textfeld_lauf(self, r, t: str) -> dict:
        lauf = {"t": t}
        rpr = _xp(r, "w:rPr")
        if rpr:
            self._textfeld_zeichen(rpr[0], lauf)
            self._textfeld_farben_groesse(rpr[0], lauf)
        return lauf

    @staticmethod
    def _textfeld_zeichen(rp, lauf: dict) -> None:
        """Fett, Kursiv, Durchgestrichen, Unterstrichen, Hoch-/Tiefgestellt."""
        for k, ausdruck in _ZEICHEN_FLAGS:
            el = _xp(rp, ausdruck)
            if el and el[0].get(qn("w:val")) not in ("0", "false"):
                lauf[k] = True
        u = _xp(rp, "w:u/@w:val")
        if u and u[0] != "none":
            lauf["unter"] = True
        va = _xp(rp, "w:vertAlign/@w:val")
        if va and va[0] in ("superscript", "subscript"):
            lauf["hoch" if va[0] == "superscript" else "tief"] = True

    @staticmethod
    def _textfeld_farben_groesse(rp, lauf: dict) -> None:
        """Schriftfarbe, Hervorhebung (Hintergrund) und Größe."""
        c = _xp(rp, "w:color/@w:val")
        if c and c[0] not in ("auto", ""):
            lauf["fuell"] = "#" + c[0].lower()
        shd = _xp(rp, "w:shd/@w:fill")
        if shd and shd[0] not in ("auto", ""):
            lauf["hervor"] = "#" + shd[0].lower()
        sz = _xp(rp, "w:sz/@w:val")
        if sz and sz[0].isdigit():
            lauf["pt"] = int(sz[0]) / 2

    @staticmethod
    def _textfeld_kette(wsp, daten: dict) -> None:
        """Verknüpfung (``wps:linkedTxbx`` mit Kette und Stelle): Kennung des Felds sowie Vorgänger und Nachfolger."""
        ver = _xp(wsp, "wps:linkedTxbx")
        kopf = _xp(wsp, "wps:txbx/@id")
        kette, seq = (ver[0].get("id"), int(ver[0].get("seq") or 0)) if ver else (kopf[0] if kopf else None, 0)
        if ver and kette is not None:
            daten["id"] = f"k{kette}_{seq}"
            if seq > 0:
                daten["von"] = f"k{kette}_{seq - 1}"
            daten["weiter"] = f"k{kette}_{seq + 1}"                # unbekannte Folgefelder entfernt ``_ketten_bereinigen``

    def _ketten_bereinigen(self) -> None:
        """Nach dem Lesen: Verweise auf Folgefelder, die es nicht gibt, entfernen."""
        from lunivo_writer.editor.objekte import freie_bilder as FB
        ids = set()
        b = self.doc.firstBlock()
        while b.isValid():
            for a in FB.aus_absatz(b.blockFormat()):
                if a.get("art") == "textfeld" and a.get("daten", {}).get("id"):
                    ids.add(a["daten"]["id"])
            b = b.next()
        b = self.doc.firstBlock()
        while b.isValid():
            self._kette_bereinigen_absatz(b, ids)
            b = b.next()

    @staticmethod
    def _kette_bereinigen_absatz(b, ids: set) -> None:
        """Entfernt in den Textfeldern des Absatzes Verweise (weiter, von) auf unbekannte Felder und schreibt den Absatz neu, wenn nötig."""
        from lunivo_writer.editor.objekte import freie_bilder as FB
        from lunivo_writer.editor.dokument.zusatz import B_BILDANKER
        liste = FB.aus_absatz(b.blockFormat())
        geaendert = False
        for a in liste:
            d = a.get("daten") if a.get("art") == "textfeld" else None
            for schluessel in ("weiter", "von"):
                if d and d.get(schluessel) and d[schluessel] not in ids:
                    d.pop(schluessel); geaendert = True
        if geaendert:
            bf = b.blockFormat(); bf.setProperty(B_BILDANKER, json.dumps(liste, separators=(",", ":")))
            QTextCursor(b).setBlockFormat(bf)
