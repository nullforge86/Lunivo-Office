"""Galerie und Vorschau der Formatvorlagen im Menüband."""
from __future__ import annotations

import json
import os
from lunivo_writer.ui.baukasten.basis.texte import hinweis_stil, trennlinie
from lunivo_writer.core import paths

from PySide6.QtCore import QPropertyAnimation, QRectF, QSize, QTimer, Qt, Signal
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPainter
from PySide6.QtWidgets import (
    QCheckBox, QFontComboBox, QFrame, QHBoxLayout, QLabel, QMenu, QScrollArea, QSizePolicy, QStackedWidget, QToolButton,
    QVBoxLayout, QWidget,
)

from lunivo_writer.ui.baukasten.dropdown.objektmenues.bild_diagramm_menues import FELDER, GALERIEN, KLAPPEN
from lunivo_writer.ui.baukasten.formatierung.text_format import groesse_feld, schrift_feld
from lunivo_writer.ui.document.bearbeitung.document_editor import STYLES
from lunivo_writer.ui.widgets import icons
from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.ui.baukasten.controls.flache_reiter_leiste import UeberlaufLeiste
from lunivo_writer.ui.baukasten.controls.formular_gitter import tabellen_gitter
from lunivo_writer.ui.baukasten.controls.karten_raster import kachel_gitter
from lunivo_writer.ui.theme import kopf_symbolfarbe
from lunivo_writer.ui.ribbon.plan import plan

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.basis.mass import (
    DROPDOWN_HOEHE,
    ABSTAND_DICHT,
    ABSTAND_ENG,
    ABSTAND_KLEIN,
    BREITE_AUFKLAPPPFEIL,
    BREITE_BAND_GRUPPENKNOPF,
    BREITE_GRUPPENTRENNER,
    BREITE_MASSFELD_BAND,
    BREITE_RANDFELD_BAND,
    BREITE_VORLAGEN_AKTUALISIEREN,
    GROESSE_BANDKNOPF_ICON_KLEIN,
    GROESSE_GRUPPEN_STARTER,
    HOEHE_BAND_GRUPPENKNOPF,
    HOEHE_BAND_GRUPPENKNOPF_KOMPAKT,
    ICON_GROSS,
    ICON_KLEIN,
    ICON_NORMAL,
    PADDING_BANDKNOPF,
    RAND_BANDGALERIE,
    RAND_BANDREITER,
    RAND_KEIN,
    RAND_POPUP_KOPF,
    SCHRIFT_BANDGRUPPE_TITEL,
    SCHRIFT_BANDKNOPF,
)
from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Schriftauswahl
from lunivo_writer.ui.baukasten.dropdown.dropdown_knopf import DropdownKnopf

STILE_KATALOG = ["Standard", "Überschrift 1", "Überschrift 2", "Überschrift 3", "Überschrift 4", "Überschrift 5", "Überschrift 6", "Überschrift 7", "Überschrift 8", "Überschrift 9", "Titel", "Untertitel", "Zitat", "Kein Abstand"]


class BandStileBaustein:
    """Stellt die Formatvorlagen-Galerie und ihre Ereignisbehandlung bereit."""

    def _stile(self, spalten: int = 3) -> QWidget:
        host = QWidget()
        g = tabellen_gitter(host, abstand=ABSTAND_DICHT)
        self._stile_host, self._stile_gitter, self._stil_knoepfe = host, g, []
        self.stile_aktualisieren()
 # wie in der Vorlage: drei Spalten sichtbar (``"spalten": N`` im Gruppeneintrag nimmt weniger), der Rest wird durchgescrollt
        sa = QScrollArea()
        sa.setObjectName("stileGalerie")
        sa.setWidget(host)
        sa.setWidgetResizable(False)
        sa.setFrameShape(QFrame.NoFrame)
        sa.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sa.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        host.adjustSize()
        sa.setFixedWidth(spalten * 85 + 4)
        sa.setFixedHeight(host.sizeHint().height() + 2)
        sa.setStyleSheet("QScrollArea#stileGalerie, QScrollArea#stileGalerie > QWidget > QWidget { background: transparent; }")
        pfeil = QToolButton(); pfeil.setIcon(icons.icon("klappe", ICON_KLEIN)); pfeil.setIconSize(QSize(ICON_KLEIN, ICON_KLEIN)); pfeil.setAutoRaise(True); pfeil.setFixedWidth(BREITE_AUFKLAPPPFEIL)
        pfeil.setToolTip("Alle Formatvorlagen")
        pfeil.clicked.connect(lambda: self._stile_popup(pfeil))
        sa.viewport().installEventFilter(self)
        self._stile_scroll = sa
        aussen = QWidget()
        h = QHBoxLayout(aussen); h.setContentsMargins(*RAND_KEIN); h.setSpacing(0)
        h.addWidget(sa); h.addWidget(pfeil, 0, Qt.AlignVCenter)
        return aussen

    def _stile_popup(self, unter: QWidget) -> None:
        """Alle Formatvorlagen als Galerie (Pfeil rechts neben der Reihe): Probe in der Vorlage, Name darunter; Überfahren zeigt live."""
        from lunivo_writer.editor.text import stile
        from lunivo_writer.ui.baukasten import GalerieAuswahl
        w = self.b.w
        m = GalerieAuswahl(w, titel="Stile")
        e = w.current_editor()
        aktuell = e.current_style() if e is not None else None
        aktuell = "Standard" if aktuell == "Fließtext" else aktuell
        mehr = w.settings.get_bool("ui/stile_mehr", True)
        selten = {f"Überschrift {i}" for i in range(5, 10)}               # „Weitere Stile“: die selten gebrauchten
        for name in STILE_KATALOG + [n for n in stile.namen() if n not in STILE_KATALOG]:
            if not mehr and name in selten and name != aktuell:
                continue
            d = stile.definition(name)
            f = QFont("Liberation Sans")
            f.setPointSizeF(min(15.0, max(9.0, float(d["groesse"] or 10) * 0.8)))
            f.setBold(name.startswith("Überschrift") or name == "Titel" or bool(d["fett"]))
            f.setItalic(name in ("Untertitel", "Zitat") or bool(d["kursiv"]))
            m.kachel(name, name, f, farbe=d["farbe"] or None, aktuell=name == aktuell,
                     tipp=name + (" (eigene Vorlage)" if stile.ist_eigen(name) else ""))
        m.gewaehlt.connect(self.b.stilAnwenden)
        m.ueberfahren.connect(lambda name: w.vorschau.zeigen(lambda ed: self.b.stilVorschau(name, ed)))
        m.verlassen.connect(w.vorschau.ende)
        m.aktion("Neue Formatvorlage …", lambda: self.b.neueFormatvorlage(), icons.icon("pinsel", ICON_GROSS))
        m.aktion("Stil löschen", lambda: self.b.formatvorlageLoeschen(aktuell), icons.icon("radierer", ICON_GROSS),
                 aktiv=bool(aktuell) and stile.ist_eigen(aktuell))
        m.aktion("Weitere Stile anzeigen", lambda an: w.settings.set("ui/stile_mehr", an), haken=mehr)

        def kontext(name, pos):
            from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
            km = MenueListe(m)
            km.eintrag("Ändern …", lambda: (m.close(), self.b.formatvorlageAendern(name)))
            if stile.ist_eigen(name):
                km.eintrag("Löschen", lambda: (m.close(), self.b.formatvorlageLoeschen(name)))
            km.exec(pos)
        m.kontext.connect(kontext)
        m.aboutToHide.connect(w.vorschau.ende)
        from PySide6.QtCore import QPoint
        m.popup(unter.mapToGlobal(QPoint(-m.sizeHint().width() + unter.width() + 4, unter.height())))

    def stile_aktualisieren(self) -> None:
        """Die Galerie neu füllen — die eingebauten Vorlagen und die selbst angelegten (editor/text/stile.py)."""
        from lunivo_writer.editor.text import stile
        from lunivo_writer.ui.widgets.live_vorschau import Ueberfahren
        g = self._stile_gitter
        alt = {id(k) for k in self._stil_knoepfe}
        self.knoepfe = [e for e in self.knoepfe if id(e[0]) not in alt]
        for k in self._stil_knoepfe:
            g.removeWidget(k); k.hide(); k.setParent(None); k.deleteLater()
        self._stil_knoepfe = []
        for i, name in enumerate(STILE_KATALOG + [n for n in stile.namen() if n not in STILE_KATALOG]):
            k = QToolButton()
            k.setAutoRaise(True)
            k.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            d = stile.definition(name)
            k.setText(f"Aa\n{name}")
            f = k.font()
            f.setPointSizeF(8)
            if name.startswith("Überschrift") or name == "Titel" or (stile.ist_eigen(name) and d["fett"]):
                f.setBold(True)
            if name in ("Untertitel", "Zitat") or (stile.ist_eigen(name) and d["kursiv"]):
                f.setItalic(True)
            k.setFont(f)
            k.setFixedWidth(BREITE_VORLAGEN_AKTUALISIEREN)
            k.setToolTip(name + (" (eigene Vorlage)" if stile.ist_eigen(name) else ""))
            k.clicked.connect(lambda _=False, n=name: self.b.stilAnwenden(n))
            fl = Ueberfahren(self.b.w.vorschau, lambda e, n=name: self.b.stilVorschau(n, e))
            k.installEventFilter(fl)
            k._ueberfahren = fl                                  # am Knopf festhalten, sonst räumt Python den Filter ab
            g.addWidget(k, i % 2, i // 2)
            self.knoepfe.append((k, None, True))
            self._stil_knoepfe.append(k)
        self._stile_host.adjustSize()

    def eventFilter(self, obj, ev):
        from PySide6.QtCore import QEvent
        sa = getattr(self, "_stile_scroll", None)
        if sa is not None and obj is sa.viewport() and ev.type() == QEvent.Wheel:
            sa.horizontalScrollBar().setValue(sa.horizontalScrollBar().value() - ev.angleDelta().y() // 2)
            return True
        return super().eventFilter(obj, ev)

