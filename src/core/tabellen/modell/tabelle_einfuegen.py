"""Tabelle einfuegen: aus ``vcl.qt.rendering.formen.einfuegen`` herausgelöst."""
from __future__ import annotations


# ---- Schnelltabellen -----------------------------------------------------------------------------------------------------------
def _tabelle(ed, zeilen: list[list[str]], kopf: bool = True, breit: bool = True):
    """Fügt eine Tabelle mit Rahmen und dem Text je Zelle ein (erste Zeile als Kopfzeile, wenn ``kopf``)."""
    spalten = max(len(z) for z in zeilen)

    def f(sitz):
        with sitz.gruppe("Tabelle einfügen"):
            fmt = {"rahmen_breite": 1.0, "rahmen_farbe": "#333333", "rahmen_art": "einfach", "zellpolster": 4.0, "breite_art": "prozent", "breite": 100.0 if breit else 60.0}
            if kopf:
                fmt["kopfzeilen"] = 1
            tid = sitz.tabelle_einfuegen(len(zeilen), spalten, format=fmt)
            for r, z in enumerate(zeilen):
                for k, v in enumerate(z):
                    if v:
                        sitz.text_einfuegen(v, sitz.zelle_anfang(tid, r, k), format={"fett": True} if kopf and r == 0 else None)
            if kopf:
                sitz.zellformat_anwenden(tid, {"hintergrund": "#e7eef8"}, [(0, k) for k in range(spalten)])
            sitz.setze_auswahl(sitz.zelle_anfang(tid, 0, 0))
    ed.ansicht._aendern(f)


def schnelltabelle(ed, name: str) -> None:
    if name.startswith("Tabelle mit Kopfzeile"):
        _tabelle(ed, [["Spalte 1", "Spalte 2", "Spalte 3"]] + [["", "", ""] for _ in range(3)])
    elif name == "Zwei Spalten":
        _tabelle(ed, [["Begriff", "Erklärung"]] + [["", ""] for _ in range(4)])
    elif name.startswith("Kalender"):
        import calendar
        import datetime
        h = datetime.date.today()
        tage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        zeilen = [tage]
        for woche in calendar.Calendar(0).monthdayscalendar(h.year, h.month):
            zeilen.append([str(d) if d else "" for d in woche])
        _tabelle(ed, zeilen)
    elif name.startswith("Matrix"):
        _tabelle(ed, [["", "A", "B"], ["A", "", ""], ["B", "", ""]], kopf=True)
    else:
        _tabelle(ed, [["Zeit", "Was", "Wer"]] + [["", "", ""] for _ in range(5)])
