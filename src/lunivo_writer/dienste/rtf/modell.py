"""RTF-Zwischenmodell: Absätze, Tabellen und das Sammelziel (Haupttext, Kopf- oder Fußzeile)."""
from __future__ import annotations

from lunivo_writer.core.dokument.bericht import DocumentIOError

GRENZE_BYTES = 512 * 1024 * 1024


def daten_lesen(path: str) -> bytes:
    """Die Bytes einer RTF-Datei; wirft ``DocumentIOError`` bei unlesbarer, zu großer oder gar nicht RTF-Datei."""
    try:
        with open(path, "rb") as fh:
            daten = fh.read(GRENZE_BYTES + 1)
    except OSError as e:
        raise DocumentIOError(f"Datei nicht lesbar: {e.strerror or e}") from e
    if len(daten) > GRENZE_BYTES:
        raise DocumentIOError("Die RTF-Datei ist zu groß, um sie sicher zu öffnen.")
    if not daten.lstrip().startswith(b"{\\rtf"):
        raise DocumentIOError("Die Datei ist kein gültiges RTF-Dokument oder beschädigt.")
    return daten


class NichtImModell(Exception):
    """RTF-Konstrukt, das noch nicht verlustfrei ins Kernmodell überführt wird."""


class Abschnittswechsel:
    """Ende eines Abschnitts im Haupttext (\\sect), nur im Modellweg."""


class Absatz:
    def __init__(self, props: dict, laeufe: list, liste: str | None):
        self.props, self.laeufe, self.liste = props, laeufe, liste


class Tabelle:
    def __init__(self):
        self.zeilen: list[tuple[list[list[Absatz]], list[int]]] = []
        self.merken: list[list[set]] = []          # je Zeile die Verbundmarken (clmgf, clmrg, clvmgf, clvmrg) je Zelle
        self.hintergruende: list[list] = []        # je Zeile die Schattierung (Farbindex oder None) je Zelle


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

    def reihe_ende(self, cellx: list[int], merken: list | None = None, hintergruende: list | None = None) -> None:
        if self.zelle or self.laeufe:
            self.zelle_ende({"intbl": True})
        if self.tabelle is None:
            self.tabelle = Tabelle()
            self.teile.append(self.tabelle)
        self.tabelle.zeilen.append((self.reihe, list(cellx)))
        self.tabelle.merken.append([set(m) for m in (merken or [])])
        self.tabelle.hintergruende.append(list(hintergruende or []))
        self.reihe = []

    def abschliessen(self, absatz: dict) -> None:
        if self.laeufe:
            self.absatz(dict(absatz, intbl=False))
        if self.reihe or self.zelle:
            self.reihe_ende([])
