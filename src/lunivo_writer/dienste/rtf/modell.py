"""RTF-Zwischenmodell: Absätze, Tabellen und das Sammelziel (Haupttext, Kopf- oder Fußzeile)."""
from __future__ import annotations


class NichtImModell(Exception):
    """RTF-Konstrukt, das noch nicht verlustfrei ins Kernmodell überführt wird."""


class Absatz:
    def __init__(self, props: dict, laeufe: list, liste: str | None):
        self.props, self.laeufe, self.liste = props, laeufe, liste


class Tabelle:
    def __init__(self):
        self.zeilen: list[tuple[list[list[Absatz]], list[int]]] = []


class Ziel:
    """Sammelt Absätze und Tabellen — für den Haupttext und je Kopf-/Fußzeile."""

    def __init__(self, haupt: bool):
        self.haupt = haupt
        self.teile: list = []
        self.laeufe: list = []
        self.liste: str | None = None
        self.zelle: list[Absatz] = []
        self.reihe: list[list[Absatz]] = []
        self.tabelle: Tabelle | None = None

    def text(self, s: str, zeichen: dict) -> None:
        if not s:
            return
        schl = tuple(sorted(zeichen.items()))
        if self.laeufe and self.laeufe[-1][0] == "t" and self.laeufe[-1][2] == schl:
            self.laeufe[-1] = ("t", self.laeufe[-1][1] + s, schl)
        else:
            self.laeufe.append(("t", s, schl))

    def absatz(self, absatz: dict) -> None:
        a = Absatz(dict(absatz), self.laeufe, self.liste)
        self.laeufe, self.liste = [], None
        if self.haupt and absatz.get("intbl"):
            self.zelle.append(a)
            return
        self.tabelle = None
        self.teile.append(a)

    def zelle_ende(self, absatz: dict) -> None:
        if self.laeufe or not self.zelle:
            self.absatz(dict(absatz, intbl=True))
        self.reihe.append(self.zelle)
        self.zelle = []

    def reihe_ende(self, cellx: list[int]) -> None:
        if self.zelle or self.laeufe:
            self.zelle_ende({"intbl": True})
        if self.tabelle is None:
            self.tabelle = Tabelle()
            self.teile.append(self.tabelle)
        self.tabelle.zeilen.append((self.reihe, list(cellx)))
        self.reihe = []

    def abschliessen(self, absatz: dict) -> None:
        if self.laeufe:
            self.absatz(dict(absatz, intbl=False))
        if self.reihe or self.zelle:
            self.reihe_ende([])
