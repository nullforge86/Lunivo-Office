"""Menüleiste, gebaut aus register.json („menues“)."""
from __future__ import annotations

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenu, QMenuBar

from lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste import MenueListe

NICHT_DA = "{} — in der nativen Fassung noch nicht umgesetzt"
TASTEN = {"Strg": "Ctrl", "Umschalt": "Shift", "Alt": "Alt"}


def _taste(t: str) -> str:
    for de, en in TASTEN.items():
        t = t.replace(de, en)
    return t.replace("−", "-")


def baue_menueleiste(mb: QMenuBar, menues: list, befehle) -> int:
    """Füllt die Menüleiste. → Anzahl der Menüpunkte ohne nativen Befehl."""
    fehlend = 0

    def fuellen(menu: MenueListe, punkte: list):
        nonlocal fehlend
        for p in punkte:
            if p.get("trenner"):
                menu.addSeparator()
            elif p.get("unter"):
                fuellen(menu.untermenue(p["name"]), p["unter"])
            elif p.get("unter_dynamisch"):
                m = menu.untermenue(p["name"])
                if p["name"] == "Fenster":
                    m.aboutToShow.connect(lambda m=m: _fenster_menue(m, befehle))
            else:
                t = p.get("tun")
                if p["name"] == "Optionen":
                    aktion, aktiv, tip = (lambda: befehle.optionen()), True, ""
                elif t and t != "eigen" and befehle.hat(t):
                    aktion, aktiv, tip = (lambda t=t: befehle.tun(t)), True, ""
                else:
                    aktion, aktiv, tip = None, False, NICHT_DA.format(p["name"])
                    fehlend += 1
                menu.eintrag(p["name"], aktion, kuerzel=p.get("taste") or "", aktiv=aktiv, tip=tip)

    for m in menues:
        fuellen(MenueListe.in_leiste(mb, m["name"]), m["punkte"])
    return fehlend


def _fenster_menue(m: QMenu, befehle) -> None:
    m.clear()
    w = befehle.w
    for i, t in enumerate(w._doc_tabs()):
        m.eintrag(("● " if t.is_modified() else "") + t.title, lambda t=t: befehle.fensterWaehlen(t), haken=t is w.current_tab())
    m.addSeparator()
    m.eintrag("Neues Dokument", w.new_document)
    m.eintrag("Dokument schließen", lambda: w.close_tab(w.docs.currentIndex()))
