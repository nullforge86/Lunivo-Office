"""Etiketten: ein Bogen als Tabelle ohne Rahmen, je Etikett eine Zelle."""
from __future__ import annotations

from lunivo_writer.kern.bearbeitung import Bearbeitungssitzung
from lunivo_writer.kern.dokument.dokument import Dokument, neues_dokument
from lunivo_writer.kern.dokument.seite import PageSettings
from lunivo_writer.kern.geometrie import mm_to_px

ETIKETTEN = {"70 × 37 mm — 24 Stück (3 × 8)": (3, 8, 70, 37), "70 × 42,3 mm — 21 Stück (3 × 7)": (3, 7, 70, 42.3),
             "70 × 50,8 mm — 15 Stück (3 × 5)": (3, 5, 70, 50.8), "105 × 42,3 mm — 14 Stück (2 × 7)": (2, 7, 105, 42.3),
             "105 × 148 mm — 4 Stück (2 × 2)": (2, 2, 105, 148)}


def etiketten_erstellen(bogen: str, text: str, gleich: bool) -> tuple[Dokument, PageSettings]:
    """Das Dokument des Etikettenbogens und seine Seiteneinrichtung; die Übernahme in den Editor ist Sache des Aufrufers."""
    sp, ze, b, h = ETIKETTEN[bogen]
    pg = PageSettings(margin_top_mm=8, margin_bottom_mm=8, margin_left_mm=5, margin_right_mm=5)
    zeilen = [z.strip() for z in text.splitlines() if z.strip()]
    neu = neues_dokument()
    s = Bearbeitungssitzung(neu)
    tid = s.tabelle_einfuegen(ze, sp, format={"zellpolster": mm_to_px(2)}, spaltenbreiten=[mm_to_px(b)] * sp)
    s.zeilenhoehen_setzen(tid, [mm_to_px(h)] * ze)
    n = 0
    for r in range(ze):
        for k in range(sp):
            inhalt = " ".join(zeilen) if gleich else (zeilen[n] if n < len(zeilen) else "")
            if inhalt:
                s.text_einfuegen(inhalt, s.zelle_anfang(tid, r, k), format={"groesse_pt": 10.0})
            n += 1
    neu.abschnitte[0].seite = pg
    return neu, pg
