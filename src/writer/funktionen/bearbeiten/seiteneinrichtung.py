"""Kopf- und Fußzeile eines Abschnitts als Text setzen und die Seitenzahl einfügen: ordnet die Bedienung den Framework-Befehlen zu."""
from __future__ import annotations

from framework.befehle import kopffuss as _befehle


def kopffuss_zeile_setzen(kennung: int, abschnitt: int, zeile: str, text: str, ausrichtung: str) -> bool:
    """Die Zeile (``header``, ``footer``, ``first_header`` oder ``first_footer``) des Abschnitts durch Text mit Ausrichtung ersetzen."""
    return _befehle.zeile_setzen(kennung, abschnitt, zeile, text, ausrichtung)


def seitenzahl_einfuegen(kennung: int, abschnitt: int) -> bool:
    """Die Seitenzahl in die Fußzeile des Abschnitts setzen (leere Fußzeile: mittig; sonst angehängt)."""
    return _befehle.seitenzahl_einfuegen(kennung, abschnitt)


KOPF_FUSS = ("header", "footer", "first_header", "first_footer", "even_header", "even_footer")


class Zeile:
    """Eine Kopf- oder Fußzeile der Seiteneinrichtung der Oberfläche: Text, Ausrichtung, Zeichenformat und Textstücke."""

    def __init__(self, text: str = "", align: str = "center", fmt: dict | None = None, runs: list | None = None):
        self.text, self.align, self.fmt, self.runs = text, align, dict(fmt or {}), [dict(r) for r in (runs or [])]

    def kopie(self, text: str | None = None, align: str | None = None) -> "Zeile":
        return Zeile(self.text if text is None else text, self.align if align is None else align, self.fmt, self.runs)

    def is_empty(self) -> bool:
        return not self.text.strip()

    def als_felder(self) -> dict:
        return {"text": self.text, "align": self.align, "fmt": dict(self.fmt), "runs": [dict(r) for r in self.runs]}


class Seiteneinrichtung:
    """Die Seiteneinrichtung eines Abschnitts als eigener Wert der Oberfläche (dieselben Felder wie im Dokument). Ändern wirkt erst, wenn die
    Einrichtung über einen Befehl an das Dokument zurückgeht."""

    def __init__(self, felder: dict):
        import copy
        for name, wert in felder.items():
            setattr(self, name, Zeile(**wert) if name in KOPF_FUSS else copy.deepcopy(wert))
        self._namen = tuple(felder)

    @property
    def landscape(self) -> bool:
        return self.width_mm > self.height_mm

    def set_orientation(self, landscape: bool) -> None:
        if landscape != self.landscape:
            self.width_mm, self.height_mm = self.height_mm, self.width_mm

    def set_paper(self, name: str) -> None:
        from writer.anbindung.seite import paper_mm
        w, h = paper_mm()[name]
        if self.landscape:
            w, h = h, w
        self.width_mm, self.height_mm = w, h

    def paper_name(self) -> str:
        from writer.anbindung.seite import papier_name
        return papier_name(self.width_mm, self.height_mm)

    def _inhalt(self) -> tuple[float, float]:
        from writer.anbindung.seite import inhalt_px
        return inhalt_px(self.width_mm, self.height_mm, self.margin_top_mm, self.margin_bottom_mm, self.margin_left_mm, self.margin_right_mm)

    @property
    def content_width_px(self) -> float:
        return self._inhalt()[0]

    @property
    def content_height_px(self) -> float:
        return self._inhalt()[1]

    def als_felder(self) -> dict:
        """Die Felder als Wörterbuch für den Befehl an das Dokument (Kopf- und Fußzeilen ebenfalls als Wörterbuch)."""
        import copy
        return {n: getattr(self, n).als_felder() if n in KOPF_FUSS else copy.deepcopy(getattr(self, n)) for n in self._namen}

    def copy(self) -> "Seiteneinrichtung":
        return Seiteneinrichtung(self.als_felder())


def seite_des_abschnitts(kennung: int, index: int) -> Seiteneinrichtung:
    """Die Seiteneinrichtung des Abschnitts ``index`` (höchstens der letzte) als eigene Kopie der Oberfläche."""
    from framework.befehle import bearbeiten as _bearbeiten
    from writer.werte import eigene_kopie
    return Seiteneinrichtung(eigene_kopie(_bearbeiten.abbild_seite_felder(kennung, index)))


def dokument_metadaten(kennung: int) -> dict:
    """Die Metadaten des Dokuments als eigene Kopie der Oberfläche."""
    from framework.befehle import bearbeiten as _bearbeiten
    from writer.werte import eigene_kopie
    return eigene_kopie(_bearbeiten.abbild_metadaten(kennung))
