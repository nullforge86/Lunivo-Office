"""Kontext einer Kern-Funktion: was sie über das Dokument an der Schreibmarke braucht – berechnet aus der Bearbeitungssitzung, ohne Oberfläche.

Ersetzt den früheren Zugriff des Kerns auf den Editor der Oberfläche (``ed``). Stellen im Text sind Zeichenstellen des Rohtextes (Absätze durch je
ein Zeichen getrennt). Seitenzahlen kommen aus dem Druck-Layout des Kerns."""
from __future__ import annotations

from core.bearbeitung.verlauf import BearbeitungsFehler
from core.dokument import teile
from core.suche.textsuche import offset_zu_position, position_zu_offset


class Kontext:
    def __init__(self, sitzung) -> None:
        self.sitzung = sitzung
        self.bewegt = False                  # die Auswahl wurde gesetzt (Sprung): das Framework meldet es der Oberfläche

    # ---- Ändern und Auswählen -------------------------------------------------------------------------------------------------------
    def aendern(self, arbeit) -> bool:
        """Führt ``arbeit(sitzung)`` aus; ``False``, wenn der Kern die Änderung ablehnt."""
        try:
            arbeit(self.sitzung)
        except BearbeitungsFehler:
            return False
        return True

    def auswaehlen(self, von: int, bis: int) -> None:
        d = self.sitzung.dokument
        self.sitzung.setze_auswahl(offset_zu_position(d, von), offset_zu_position(d, bis))
        self.bewegt = True

    def springe(self, bereiche: list, delta: int):
        """Wählt den nächsten (``delta`` 1) oder vorigen (-1) Bereich hinter bzw. vor der Schreibmarke (mit Umlauf); ``None``, wenn es keinen gibt."""
        if not bereiche:
            return None
        anfang, ende = self.auswahl_stellen()
        pos = ende if delta > 0 else anfang
        if delta > 0:
            ziel = next((b for b in bereiche if b["von"] >= pos), bereiche[0])
        else:
            ziel = next((b for b in reversed(bereiche) if b["bis"] <= pos or b["von"] < pos), bereiche[-1])
        self.auswaehlen(ziel["von"], ziel["bis"])
        return ziel

    # ---- Lesen -----------------------------------------------------------------------------------------------------------------------
    def position(self) -> int:
        """Stelle der Schreibmarke (Kopf der Auswahl)."""
        return position_zu_offset(self.sitzung.dokument, self.sitzung.auswahl.kopf)

    def auswahl_stellen(self) -> tuple[int, int]:
        d = self.sitzung.dokument
        a, k = position_zu_offset(d, self.sitzung.auswahl.anker), position_zu_offset(d, self.sitzung.auswahl.kopf)
        return min(a, k), max(a, k)

    def seiten_von(self, stellen: list) -> list:
        """Die Seitenzahlen der Stellen (``"?"``, wenn eine Stelle nirgends steht) – aus dem Druck-Layout."""
        from core.layout import LayoutEngine
        d = self.sitzung.dokument
        erg = LayoutEngine().berechnen(d)
        aus = []
        for o in stellen:
            seite = erg.seite_von(offset_zu_position(d, o).absatz_id)
            aus.append(str(erg.seiten[seite].nummer or seite + 1) if seite is not None else "?")
        return aus

    def absatzformat(self) -> dict:
        """Das wirksame Absatzformat des Absatzes an der Schreibmarke."""
        from core.layout.drucklayout import absatzformat
        s = self.sitzung
        return absatzformat(s.dokument, s._absatz(s.auswahl.kopf.absatz_id))

    def auswahl_text(self) -> str:
        s = self.sitzung
        return "" if s.auswahl.leer else s.text(s.auswahl)

    @property
    def quellen(self) -> list:
        return [dict(q) for q in self.sitzung.dokument.quellen]

    @property
    def zitierweise(self) -> str:
        return str(self.sitzung.dokument.eigenschaften.get("zitierweise") or "APA")

    @property
    def noten(self) -> dict:
        return {art: {n.id: n.text for n in noten.values()} for art, noten in self.sitzung.dokument.noten.items()}

    def noten_stellen(self) -> list:
        d = self.sitzung.dokument
        aus = []
        for b in self.sitzung.bereiche(lambda f: "note" in f):
            a = self.sitzung._absatz(b.anker.absatz_id)
            rest = teile(a.inhalte, b.anker.versatz)[1]
            art, _, nid = (rest[0].format if rest else {})["note"].partition(":")
            aus.append({"von": position_zu_offset(d, b.anker), "bis": position_zu_offset(d, b.kopf), "art": art, "id": int(nid)})
        return aus

    @property
    def seite(self):
        """Die Seiteneinrichtung des Abschnitts an der Schreibmarke."""
        s = self.sitzung
        abschnitte = s.dokument.abschnitte
        return abschnitte[min(s.abschnitt_index(s.auswahl.kopf.absatz_id), len(abschnitte) - 1)].seite

    def tabelle_an_marke(self):
        """Die Tabelle, in der die Schreibmarke steht (sonst ``None``)."""
        stelle = self.sitzung.tabelle_von(self.sitzung.auswahl.kopf.absatz_id)
        return stelle[0] if stelle is not None else None
