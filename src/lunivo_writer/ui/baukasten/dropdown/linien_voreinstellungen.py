"""Popup der Linie im Kopf (Vorlage): „Keine Linie“ und „Voreingestellte Linie“ — 8 Strichtypen (Zeilen) × 4 Formen (Spalten).

    m = linien_menue(parent, aktuell="gestrichelt|doppelt|2.25", arten=None)   # ``gewaehlt(schluessel)``: "" (keine Linie) oder „strichtyp|form|breite_pt“
    pm = linien_bild({"art": "lang", "form": "einfach", "breite": 0.75, "farbe": "#868e96"}, KopfDropdown.SYMBOL)   # das Feld im Kopf; art "keine" = leer
    linien_schluessel(art, form, breite) -> str            # der Schlüssel zu einer Einstellung (für ``aktuell``)

Strichtypen aus ``editor/diagramm_format.STRICHTYPEN``, gezeichnet von ``textfx._kontur_pfade``. Der Baustein malt nur; die Linie setzt der Aufrufer.
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPalette, QPixmap
from PySide6.QtWidgets import QWidget

from lunivo_writer.editor import diagramm_format as F
from lunivo_writer.editor import textfx as X
from lunivo_writer.ui.baukasten.dropdown.kopf_dropdown import keine_zeile
from lunivo_writer.ui.baukasten.dropdown.voreinstellung_menue import VoreinstellungMenue
from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.basis.mass import GROESSE_LINIENVORGABE_KACHEL

KACHEL = QSize(*GROESSE_LINIENVORGABE_KACHEL)                        # Vorlage: Kachelabstand 107 x 29 px
BREITE = 412
SPALTEN = (("einfach", 0.75), ("einfach", 2.25), ("doppelt", 2.25), ("dick_duenn", 2.25))      # Form, Breite in pt je Spalte
_FORMEN = {"einfach": "Einfach", "doppelt": "Doppelt", "dick_duenn": "Dick–dünn"}


def linien_schluessel(art: str, form: str, breite: float) -> str:
    return f"{art}|{form}|{float(breite):g}"


def linien_bild(spec: dict, groesse: QSize) -> QPixmap:
    """Eine Linie der Strichart/Form/Breite (pt) in Farbe über die Breite, mittig; ``art`` "keine" gibt ein leeres Bild."""
    pm = QPixmap(groesse); pm.fill(Qt.transparent)
    if spec.get("art") == "keine":
        return pm
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    pf = QPainterPath(); pf.moveTo(3, groesse.height() / 2); pf.lineTo(groesse.width() - 3, groesse.height() / 2)
    if (spec.get("form") or "einfach") != "einfach":
        p.setClipRect(QRectF(3, 0, groesse.width() - 6, groesse.height()))          # die Enden der Mehrfachlinien bleiben offen (keine Kappen)
    dicke = min(max(float(spec.get("breite") or 0.75) * 96 / 72, 1.2), 3.2)
    for fl in X._kontur_pfade(pf, dicke, spec.get("form") or "einfach", spec.get("art") or "einfach"):
        p.fillPath(fl, QColor(spec.get("farbe") or Farbe.GRAU))
    p.end()
    return pm


def linien_menue(parent: QWidget | None = None, aktuell: str = "", arten: dict[str, str] | None = None) -> VoreinstellungMenue:
    m = VoreinstellungMenue(parent, keine=None, kachel=KACHEL)
    m.aktuell = aktuell
    keine_zeile(m, "Keine Linie")
    farbe = (parent.palette() if parent is not None else m.palette()).color(QPalette.WindowText).name()
    namen = arten or dict(F.STRICHTYPEN)                 # Schlüssel → Name der Zeilen (Standard: die Strichtypen des Diagramms; Text: ``texteffekt.KONTUR_ARTEN``)
    eintraege = [(linien_schluessel(art, form, br), QIcon(linien_bild({"art": art, "form": form, "breite": br, "farbe": farbe}, KACHEL)),
                  f"{namen[art]}, {_FORMEN[form]}, {br:g} pt") for art in namen for form, br in SPALTEN]
    m.abschnitt("Voreingestellte Linie", eintraege, len(SPALTEN))
    return m
