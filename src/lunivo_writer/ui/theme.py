"""Hell/Dunkel über Qt-Paletten (Stil „Fusion“) — keine Stylesheets für das Grundlayout."""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QRectF
from PySide6.QtGui import QColor, QPainterPath, QPalette, QRegion
from PySide6.QtWidgets import QApplication, QStyleFactory
from lunivo_writer.ui.widgets import icons
from lunivo_writer.ui.baukasten.mass import (
    BREITE_BANDREITER_KNOPF,
    BREITE_FELDKNOPF_MIN,
    BREITE_KNOPF_KLEIN,
    HOEHE_BANDREITER_KNOPF,
    HOEHE_KNOPF_GROSS,
    HOEHE_LISTENZEILEN_KNOPF,
    HOEHE_TRENNLINIE_MAX,
    MARGIN_BANDREITER,
    MARGIN_MENUETRENNER,
    MARGIN_OBEN_GRUPPE,
    MARGIN_RECHTS_REITER,
    MARGIN_REITER_KOMPAKT,
    MARGIN_SCROLLBALKEN_GRIFF,
    PADDING_BANDREITER,
    PADDING_BANDREITER_KOMPAKT,
    PADDING_BAUMEINTRAG_GLOBAL,
    PADDING_DOKUMENTREITER,
    PADDING_EINGABEFELD_GLOBAL,
    PADDING_FELDKNOPF,
    PADDING_GRUPPENTITEL_GLOBAL,
    PADDING_GRUPPE_OBEN,
    PADDING_KNOPF_GLOBAL,
    DROPDOWN_ZEILE_PADDING,
    PADDING_KOPFFUSS_ABSATZKNOPF,
    PADDING_KOPFFUSS_WERKZEUG,
    PADDING_LAYOUTOPTIONEN_TITEL,
    PADDING_LINKS_MENUESYMBOL,
    PADDING_MINILEISTE_KNOPF,
    PADDING_POPUP_LINKKNOPF,
    PADDING_VORGABEMENUE_KOPF,
    PADDING_LISTENZEILE_GLOBAL,
    PADDING_MENUE_KOMPAKT,
    PADDING_MENUEEINTRAG_KOMPAKT,
    SCHRIFT_HINWEIS,
    PADDING_MENUEEINTRAG_GLOBAL,
    PADDING_MENUE_GLOBAL,
    PADDING_OPTIONSKNOPF_GLOBAL,
    PADDING_RECHTS_MENUEKNOPF,
    PADDING_REITER_GLOBAL,
    PADDING_WERKZEUGKNOPF_GLOBAL,
    RADIUS_EINTRAG,
    RADIUS_FELD,
    RADIUS_KLEIN,
    RADIUS_LEISTENKNOPF,
    RADIUS_MARKE,
    RADIUS_MITTEL,
    RADIUS_REGLER_GRIFF,
    RADIUS_REGLER_RINNE,
)


_FUSION = False
_MINT = False                                                       # Thema „Mint“ aktiv (fast schwarzes Grün mit hellem Grün-Akzent, Farben aus dem Muster-Bildschirmfoto gemessen)


AUF_AKZENT = "#0f1511"                                              # die eine Farbe für Symbole und Schrift auf dem grünen Akzent (Thema Mint) — nirgends sonst fest eintragen


def kopf_symbolfarbe() -> str | None:
    """Symbolfarbe für den grünen Kopfbereich im Thema Mint (dunkel auf Hellgrün); sonst ``None`` = Farbe der Palette."""
    return AUF_AKZENT if _MINT else None                # dunkle Symbole auf dem hellgrünen Kopf


class _RundFilter(QObject):
    """Rundet die Ecken eines Widgets (Maske), solange er installiert ist; Radius aus ``MINT_FARBEN``."""
    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.Resize:
            self.runden(obj)
        return False

    @staticmethod
    def runden(w) -> None:
        pfad = QPainterPath()
        pfad.addRoundedRect(QRectF(w.rect()), MINT_FARBEN["radius"], MINT_FARBEN["radius"])
        w.setMask(QRegion(pfad.toFillPolygon().toPolygon()))


_RUND = _RundFilter()


def karten_rand() -> int:
    """Breite des Kartenrands der Seitenleisten-Panels im aktuellen Thema (Mint: ``luft``, sonst 0)."""
    return MINT_FARBEN["luft"] if _MINT else 0


def karte_einrichten(widget, layout, breite: int | None = None) -> None:
    """Seitenleisten-Karte (Mint): gemeinsame Eigenschaft für das Stylesheet und der Innenrand = Breite des Kartenrands, sonst überdeckt der Rand die
    untersten Knöpfe und Felder. Ein Ort für alle Seitenleisten-Panels (links und rechts); in Hell/Dunkel bleibt der Rand 0."""
    widget.setProperty("seitenKarte", True)
    if breite is not None:
        widget.setProperty("kartenBreite", breite)               # feste Breite des Inhalts: der Kartenrand kommt dazu, der Inhalt bleibt gleich breit
    _karten_rand_setzen(widget)


def _karten_rand_setzen(widget) -> None:
    lay = widget.layout()
    if lay is not None:
        r = karten_rand()
        lay.setContentsMargins(r, r, r, r)
    basis = widget.property("kartenBreite")
    if basis:
        widget.setFixedWidth(int(basis) + 2 * karten_rand())


def mint_abstaende(fenster) -> None:
    """Thema-Hook für das Hauptfenster: im Thema Mint Außenränder um Arbeitsbereich und Band, Band als Karte, Dokumentfläche mit runden Ecken;
    in Hell/Dunkel alles wie zuvor (Ränder 0, Maske weg)."""
    a, luft = (MINT_FARBEN["aussen"], MINT_FARBEN["luft"]) if _MINT else (0, 0)
    arbeit, band, docs = getattr(fenster, "arbeit", None), getattr(fenster, "band", None), getattr(fenster, "docs", None)
    if arbeit is not None and arbeit.layout() is not None:
        arbeit.layout().setContentsMargins(a, 0, a, 0)
    stapel = getattr(band, "stapel", None)
    if stapel is not None and hasattr(band, "BAND_HOEHE"):
        stapel.setFixedHeight(band.BAND_HOEHE[band.kompakt] + 2 * luft)
    if docs is not None:
        stack = docs.stack
        if _MINT:
            if stack.property("mintRund") is None:
                stack.setProperty("mintRund", True)
                stack.installEventFilter(_RUND)
            _RundFilter.runden(stack)
        elif stack.property("mintRund"):
            stack.setProperty("mintRund", None)
            stack.removeEventFilter(_RUND)
            stack.clearMask()


def apply_theme(app: QApplication, mode: str) -> None:
    global _MINT
    _MINT = mode == "mint"
    from lunivo_writer.core.farben import Farbe
    Farbe.AN, Farbe.AN_SCHRIFT = (MINT_FARBEN["akzent"], AUF_AKZENT) if _MINT else ("#2f9e75", "#ffffff")
    Farbe.AUF_AKZENT = AUF_AKZENT if _MINT else "#ffffff"
    Farbe.SYMBOL_AUS_AKZENT = "#5d7a45"   # ausgegraute Symbole auf dem hellen Akzent (nur Mint: Hellgrün); in allen Themen gleich
    # Mint: der Kopf ist hellgrün, der Kontext-Reiter dunkel mit grüner Schrift (sonst wäre er auf dem Grün unsichtbar)
    Farbe.KONTEXT, Farbe.KONTEXT_TEXT, Farbe.KONTEXT_SCHRIFT = (AUF_AKZENT, AUF_AKZENT, MINT_FARBEN["akzent"]) if _MINT else (None, "#9cc4f0", "#ffffff")
    _setze(app, mode)
    Farbe.HINWEIS = app.palette().color(QPalette.Mid).name()     # Mid der Palette des Themas (Mint: MINT_FARBEN["grau"])
    _stil(app)
    for w in app.topLevelWidgets():
        if hasattr(w, "arbeit"):
            mint_abstaende(w)
    # Stylesheets mit palette(...) werden sonst nicht neu ausgewertet
    from lunivo_writer.ui.baukasten.texte import auffrischen
    for w in app.allWidgets():
        auffrischen(w)
        if w.property("seitenKarte"):                              # schon gebaute Seitenleisten-Karten: Innenrand passend zum Thema
            _karten_rand_setzen(w)
        ss = w.styleSheet()
        if ss and "palette(" in ss:
            w.setStyleSheet("")
            w.setStyleSheet(ss)


def _ist_dunkel(app: QApplication) -> bool:
    return app.palette().color(QPalette.Window).lightness() < 128


FARBEN = {
    False: dict(bg="#f3f4f6", flaeche="#ffffff", karte="#ffffff", tafel="#f3f4f6", feld="#ffffff", dokleiste="#f3f4f6", rand="#d9dde3",
                text="#1f2328", text2="#59616b", hover="#e6eaf0", akzent="#2f6fb5", weich="#d8e6f7", grau="#7a828c", griff="#c3c9d1",
                griff_h="#a9b1bb"),
    # Dunkel wie in der ersten Fassung (aus deinem Bildschirmfoto gemessen): Leisten und Band #2A2E32, Seitenleisten #26292D,
    # Knöpfe und Menüs #2F3338, Eingabefelder und Dokument-Reiterzeile wie die Fläche um das Blatt #1F2225, Ränder #3A3F45,
    # Schrift #E6E9EC, Nebenschrift #A7AFB7, Deaktiviertes #7C858E
    True: dict(bg="#2a2e32", flaeche="#2a2e32", karte="#2f3338", tafel="#26292d", feld="#1f2225", dokleiste="#1f2225", rand="#3a3f45",
               text="#e6e9ec", text2="#a7afb7", hover="#363b41", akzent="#4a8fd8", weich="#2f4966", grau="#7c858e", griff="#454b52",
               griff_h="#5a6169"),
}

# „Weicher Kontrast“ (Optionen ▸ Ansicht): dunkel ein Anthrazit statt fast Schwarz, hell ein warmes Creme statt Weiß-auf-Grau
WEICH = False
WEICHE_FARBEN = {
    False: dict(bg="#efebe3", flaeche="#f5f2ec", karte="#ffffff", tafel="#f5f2ec", feld="#ffffff", dokleiste="#efebe3", rand="#c9c3b8",
                text="#232019", text2="#5a5449", hover="#e4dfd5", akzent="#2f6fb5", weich="#d8e6f7", grau="#86806f", griff="#c9c3b8",
                griff_h="#b3ac9e"),
    True: dict(bg="#3d444b", flaeche="#3d444b", karte="#434b53", tafel="#394046", feld="#343a40", dokleiste="#343a40", rand="#525b63",
               text="#dde2e6", text2="#b9c1c8", hover="#4a525a", akzent="#75abe8", weich="#35506b", grau="#8c949b", griff="#59626b",
               griff_h="#6b747d"),
}

# Thema „Mint“: Farben aus Kays Muster-Bildschirmfoto gemessen (Grund #0F1511, Flächen #131A15, Akzent #85bd49, Auswahl #85bd49)
MINT_FARBEN = dict(bg="#0c0d0d", flaeche="#161817", karte="#1f2221", tafel="#1a1c1b", feld="#101211", dokleiste="#0c0d0d", kopf="#85bd49", rand="#363a38",
                   text="#e8ebe9", text2="#a4aaa6", hover="#272b29", akzent="#85bd49", weich="#85bd49", grau="#767d79", griff="#3a3f3c",
                   griff_h="#4f5652", auf_akzent=AUF_AKZENT, kopf_hover="#75a83f", radius=12, radius_klein=8, luft=6, aussen=10)

QSS = """
QToolButton { border: none; border-radius: """ f"{RADIUS_EINTRAG}" """px; padding: """ f"{PADDING_WERKZEUGKNOPF_GLOBAL}" """; background: transparent; }
QToolButton:hover { background: %(hover)s; }
QToolButton:pressed, QToolButton:checked { background: %(weich)s; }
QToolButton:disabled { color: %(grau)s; }
QToolButton[popupMode="1"] { padding-right: """ f"{PADDING_RECHTS_MENUEKNOPF}" """; }
QToolButton::menu-button { border: none; width: 12px; border-top-right-radius: 5px; border-bottom-right-radius: 5px; }
QToolButton::menu-arrow { image: url(%(pfeil_unten)s); width: 9px; height: 9px; }
QToolButton::menu-indicator { image: none; width: 0px; }
QToolButton::menu-button:hover { background: %(hover)s; }
QPushButton { border: 1px solid %(rand)s; border-radius: """ f"{RADIUS_FELD}" """px; padding: """ f"{PADDING_KNOPF_GLOBAL}" """; background: %(karte)s; }
QPushButton:hover { background: %(hover)s; }
QPushButton:pressed { background: %(weich)s; }
QPushButton:disabled { color: %(grau)s; background: transparent; }
QPushButton:default { border-color: %(akzent)s; }
QPushButton[listenzeile="true"] { text-align: left; padding: """ f"{PADDING_LISTENZEILE_GLOBAL}" """; min-height: """ f"{HOEHE_LISTENZEILEN_KNOPF}" """px; }
QPushButton[dropdownZeile] { text-align: left; padding: """ f"{DROPDOWN_ZEILE_PADDING}" """; border: none; border-radius: """ f"{RADIUS_FELD}" """px; }
QPushButton[dropdownZeile="hinweis"] { font-size: """ f"{SCHRIFT_HINWEIS}" """pt; }
QPushButton[dropdownZeile]:hover:enabled { background: %(hover)s; }
QPushButton[feldknopf="true"] { text-align: left; padding: """ f"{PADDING_FELDKNOPF}" """; min-width: """ f"{BREITE_FELDKNOPF_MIN}" """px; }
QPushButton[hervorgehoben="true"] { background: %(akzent)s; color: white; border-color: %(akzent)s; }
QPushButton[hervorgehoben="true"]:hover { border-color: %(text)s; }
QToolButton[kachel="true"]:checked { background: %(weich)s; border: 1px solid %(akzent)s; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit { border: 1px solid %(rand)s; border-radius: """ f"{RADIUS_FELD}" """px; padding: """ f"{PADDING_EINGABEFELD_GLOBAL}" """;
    background: %(feld)s; selection-background-color: %(akzent)s; selection-color: white; }
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus { border-color: %(akzent)s; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox::down-arrow { image: url(%(pfeil_unten)s); width: 10px; height: 10px; }
QSpinBox::up-button, QDoubleSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::down-button { border: none; width: 16px; background: transparent; }
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow { image: url(%(pfeil_oben)s); width: 8px; height: 8px; }
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow { image: url(%(pfeil_unten)s); width: 8px; height: 8px; }
QScrollArea#bandSeite QScrollBar:horizontal { height: 6px; margin: 0; }
QScrollArea#bandSeite QScrollBar::handle:horizontal { margin: 0; border-radius: """ f"{RADIUS_MARKE}" """px; }
QComboBox, QAbstractSpinBox[dropdownFeld] { background: %(karte)s; color: %(text)s; }          /* Dropdowns und dropdown-artige Maßfelder: ein Hintergrund */
QComboBox QAbstractItemView { border: 1px solid %(rand)s; background: %(karte)s; selection-background-color: %(weich)s; selection-color: %(text)s; outline: 0; border-radius: """ f"{RADIUS_MITTEL}" """px; }
QComboBox QAbstractItemView::item { border-radius: """ f"{RADIUS_EINTRAG}" """px; }
QMenu { background: %(karte)s; border: 1px solid %(rand)s; border-radius: """ f"{RADIUS_MITTEL}" """px; padding: """ f"{PADDING_MENUE_GLOBAL}" """; }
QMenu::item { padding: """ f"{PADDING_MENUEEINTRAG_GLOBAL}" """; border-radius: """ f"{RADIUS_EINTRAG}" """px; }
QMenu[variante="kompakt"] { padding: """ f"{PADDING_MENUE_KOMPAKT}" """; }
QMenu[variante="kompakt"]::item { padding: """ f"{PADDING_MENUEEINTRAG_KOMPAKT}" """; }
QMenu[variante="kompakt"]::icon { padding-left: """ f"{PADDING_LINKS_MENUESYMBOL}" """; }
QMenu::item:selected { background: %(weich)s; color: %(text)s; }
QMenu::item:disabled { color: %(grau)s; }
QMenu::separator { height: 1px; background: %(rand)s; margin: """ f"{MARGIN_MENUETRENNER}" """; }
QFrame[dropdownFenster] { background: %(karte)s; border: 1px solid %(rand)s; border-radius: """ f"{RADIUS_MITTEL}" """px; }
QLabel[dropdownTitel="kopf"] { color: %(akzent)s; font-weight: 600; }
QLabel[dropdownTitel="abschnitt"] { background: %(hover)s; padding: """ f"{PADDING_LAYOUTOPTIONEN_TITEL}" """; border-radius: """ f"{RADIUS_MARKE}" """px; }
QLabel[dropdownTitel="kopfzeile"] { font-weight: 600; padding: """ f"{PADDING_VORGABEMENUE_KOPF}" """; }
QToolButton[dropdownKachel] { border: 1px solid transparent; border-radius: """ f"{RADIUS_MARKE}" """px; }
QToolButton[dropdownKachel]:hover { border-color: %(akzent)s; }
QToolButton[dropdownKachel]:checked { border-color: %(akzent)s; background: %(hover)s; color: %(text)s; }
QToolButton[dropdownKachel="stil"]:checked { border: 2px solid %(akzent)s; background: transparent; }
QToolButton[dropdownKopf] { font-weight: 600; border: none; }
QPushButton[dropdownLink] { color: %(akzent)s; text-align: left; text-decoration: underline; border: none; background: transparent; padding: """ f"{PADDING_POPUP_LINKKNOPF}" """; }
QFrame#miniLeiste { background: %(karte)s; border: 1px solid %(rand)s; border-radius: """ f"{RADIUS_FELD}" """px; }
QFrame#miniLeiste QToolButton { padding: """ f"{PADDING_MINILEISTE_KNOPF}" """; }
QToolButton[papierKnopf], QWidget#kfLeiste QToolButton { background: %(kf_leiste)s; color: %(kf_tinte)s; border: 1px solid %(kf_leiste_rand)s; border-radius: """ f"{RADIUS_LEISTENKNOPF}" """px; }
QToolButton[papierKnopf]:hover, QWidget#kfLeiste QToolButton:hover { background: %(kf_gitter)s; }
QWidget#kfLeiste QToolButton { padding: """ f"{PADDING_KOPFFUSS_ABSATZKNOPF}" """; }
QToolButton[papierKnopf="absatz"] { padding: """ f"{PADDING_KOPFFUSS_WERKZEUG}" """; }
QToolButton[papierKnopf="griff"] { padding: 0; }
QToolTip { background: %(karte)s; color: %(text)s; border: 1px solid %(rand)s; padding: """ f"{PADDING_LISTENZEILE_GLOBAL}" """; }
QStatusBar { background: %(bg)s; border-top: 1px solid %(rand)s; }
QStatusBar::item { border: none; }
QScrollBar:vertical { width: 11px; background: transparent; margin: 0; }
QScrollBar:horizontal { height: 11px; background: transparent; margin: 0; }
QScrollBar::handle:vertical { background: %(griff)s; border-radius: """ f"{RADIUS_KLEIN}" """px; min-height: """ f"{HOEHE_KNOPF_GROSS}" """px; margin: """ f"{MARGIN_SCROLLBALKEN_GRIFF}" """; }
QScrollBar::handle:horizontal { background: %(griff)s; border-radius: """ f"{RADIUS_KLEIN}" """px; min-width: """ f"{BREITE_KNOPF_KLEIN}" """px; margin: """ f"{MARGIN_SCROLLBALKEN_GRIFF}" """; }
QScrollBar::handle:hover { background: %(griff_h)s; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; border: none; background: none; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
QSlider::groove:horizontal { height: 4px; background: %(rand)s; border-radius: """ f"{RADIUS_REGLER_RINNE}" """px; }
QSlider::sub-page:horizontal { background: %(akzent)s; border-radius: """ f"{RADIUS_REGLER_RINNE}" """px; }
QSlider::handle:horizontal { background: %(karte)s; border: 2px solid %(akzent)s; width: 10px; height: 10px; margin: -6px 0; border-radius: """ f"{RADIUS_REGLER_GRIFF}" """px; }
QCheckBox::indicator { width: 15px; height: 15px; border: 1px solid %(grau)s; border-radius: """ f"{RADIUS_KLEIN}" """px; background: %(karte)s; }
QCheckBox::indicator:checked { background: %(akzent)s; border-color: %(akzent)s; }
QRadioButton::indicator { width: 14px; height: 14px; border: 1px solid %(grau)s; border-radius: """ f"{RADIUS_MITTEL}" """px; background: %(feld)s; }
QRadioButton::indicator:checked { border: 1px solid %(akzent)s; background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 %(akzent)s, stop:0.5 %(akzent)s, stop:0.56 %(feld)s, stop:1 %(feld)s); }
QRadioButton { spacing: 8px; padding: """ f"{PADDING_OPTIONSKNOPF_GLOBAL}" """; }
QGroupBox { border: 1px solid %(rand)s; border-radius: """ f"{RADIUS_MITTEL}" """px; margin-top: """ f"{MARGIN_OBEN_GRUPPE}" """; padding-top: """ f"{PADDING_GRUPPE_OBEN}" """; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: """ f"{PADDING_GRUPPENTITEL_GLOBAL}" """; color: %(grau)s; }
QTreeWidget, QListWidget { border: 1px solid %(rand)s; border-radius: """ f"{RADIUS_FELD}" """px; background: %(karte)s; outline: 0; }
QTreeWidget::item, QListWidget::item { padding: """ f"{PADDING_BAUMEINTRAG_GLOBAL}" """; border-radius: """ f"{RADIUS_KLEIN}" """px; }
QTreeWidget::item:selected, QListWidget::item:selected { background: %(weich)s; color: %(text)s; }
QTabBar::tab { background: transparent; border: 1px solid %(rand)s; border-bottom: none; border-top-left-radius: 6px; border-top-right-radius: 6px;
    padding: """ f"{PADDING_REITER_GLOBAL}" """; margin-right: """ f"{MARGIN_RECHTS_REITER}" """; color: %(text2)s; }
QTabBar::tab:selected { background: %(karte)s; color: %(text)s; font-weight: 600; }
QTabBar::tab:hover:!selected { background: %(hover)s; }
QTabWidget::pane { border: 1px solid %(rand)s; border-radius: """ f"{RADIUS_FELD}" """px; top: -1px; }
QTabBar#bandReiter { background: transparent; }
QTabBar#bandReiter::tab { background: transparent; border: none; border-bottom: 3px solid transparent;
    padding: """ f"{PADDING_BANDREITER}" """; margin: """ f"{MARGIN_BANDREITER}" """; }
QTabBar#bandReiter::tab { color: %(text2)s; }
QTabBar#bandReiter[kompakt="true"]::tab { padding: """ f"{PADDING_BANDREITER_KOMPAKT}" """; margin: """ f"{MARGIN_REITER_KOMPAKT}" """; }
QTabBar#bandReiter QToolButton { min-width: """ f"{BREITE_BANDREITER_KNOPF}" """px; min-height: """ f"{HOEHE_BANDREITER_KNOPF}" """px; }
QTabBar#bandReiter::tab:hover { background: %(hover)s; border-top-left-radius: 6px; border-top-right-radius: 6px; }
QTabBar#bandReiter::tab:selected { color: %(akzent)s; font-weight: 600; border-bottom: 3px solid %(akzent)s; }
QTabBar#bandReiter:focus::tab:selected { background: %(hover)s; border-top-left-radius: 6px; border-top-right-radius: 6px; }
QTabBar#dokReiter::tab { background: transparent; border: none; padding: """ f"{PADDING_DOKUMENTREITER}" """; margin: """ f"{MARGIN_REITER_KOMPAKT}" """;
    border-top-left-radius: 8px; border-top-right-radius: 8px; }
QTabBar#dokReiter::tab:hover { background: %(hover)s; }
QTabBar#dokReiter::close-button { image: url(%(x_bild)s); subcontrol-position: right; border-radius: """ f"{RADIUS_KLEIN}" """px; padding: """ f"{PADDING_WERKZEUGKNOPF_GLOBAL}" """; }
QTabBar#dokReiter::close-button:hover { background: %(hover)s; }
QTabBar#dokReiter::tab:selected { background: %(flaeche)s; font-weight: 600; }
QWidget#bandKopf { background: %(bg)s; }
QStackedWidget#bandStapel, QScrollArea#bandSeite, QScrollArea#bandSeite > QWidget > QWidget { background: %(flaeche)s; }
QWidget#dokLeiste { background: %(dokleiste)s; }
FlacheReiterLeiste QToolButton { border: none; background: transparent; padding: 0; }          /* die dezenten Rollpfeile der flachen Reiterleiste */
QToolButton#menueKnopf:checked { color: %(akzent)s; }
*[seitenKarte="true"] { background: %(tafel)s; }                                       /* alle Seitenleisten-Panels (links und rechts, alle Themen): EINE Regel */
*[seitenKarte="true"] QAbstractScrollArea { background: transparent; border: none; }          /* ein homogener Kasten, keine Fläche im Kasten */
*[seitenKarte="true"] QAbstractScrollArea > QWidget > QWidget { background: transparent; }
QPushButton#optFertig, QPushButton#sfSpeichern { background: %(akzent)s; color: %(auf_akzent)s; }
QPushButton#optFertig:hover, QPushButton#sfSpeichern:hover { background: %(akzent_hover)s; }
*[akzentSchrift="true"] { color: %(akzent)s; }
QToolButton[akzentSchrift="true"]:checked { background: transparent; color: %(akzent)s; }
*[akzentRand="true"] { color: %(akzent)s; border-color: %(akzent)s; }
*[akzentFlaeche="true"] { background: %(akzent)s; color: %(auf_akzent)s; }
#kfPanel QRadioButton::indicator:checked { background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 %(akzent)s, stop:0.5 %(akzent)s, stop:0.6 %(kf_papier)s, stop:1 %(kf_papier)s); border-color: %(akzent)s; }
#kfPanel QPushButton { background: %(akzent)s; color: %(auf_akzent)s; }
"""


# Seitenleisten im Muster: die schmalen Leisten rechts und links als abgesetzte, abgerundete Karten
MINT_QSS = """
QWidget#dokLeiste, QWidget#bandKopfZeile, QTabBar#bandReiter { background: %(kopf)s; }
QWidget#bandKopf { background: %(bg)s; }
QWidget#bandKopfZeile { border-bottom-left-radius: %(radius)s; border-bottom-right-radius: %(radius)s; }
QStackedWidget#bandStapel { background: %(flaeche)s; border-radius: %(radius)s; margin: %(luft)s %(aussen)s %(luft)s %(aussen)s; }
QStackedWidget#bandStapel QScrollArea#bandSeite, QStackedWidget#bandStapel QScrollArea#bandSeite > QWidget > QWidget { background: transparent; }
QTabBar#bandReiter:focus::tab:selected { background: %(kopf)s; }
QTabBar#bandReiter::tab { color: %(auf_akzent)s; }
QTabBar#bandReiter::tab:selected { color: %(auf_akzent)s; font-weight: bold; border-bottom: 3px solid %(auf_akzent)s; }
QTabBar#bandReiter::tab:hover { background: %(kopf_hover)s; border-radius: %(radius_klein)s; }
QMenu::item:selected, QComboBox QAbstractItemView, QTreeWidget::item:selected, QListWidget::item:selected { selection-color: %(auf_akzent)s; }
QMenu::item:selected, QTreeWidget::item:selected, QListWidget::item:selected { color: %(auf_akzent)s; }
QToolButton:checked { color: %(auf_akzent)s; }
QListWidget#bsListe::item:selected, QListWidget#bsListe::item:hover:enabled, QListWidget#hilfeNav::item:selected { color: %(text)s; selection-color: %(text)s; }
QListWidget#sfOrte::item:selected { color: %(akzent)s; selection-color: %(akzent)s; }
QToolButton:pressed:!checked, QPushButton:pressed { background: %(hover)s; color: %(text)s; }
QFrame#leisteLinks, QFrame#leisteRechts { background: %(flaeche)s; border: 0 solid %(bg)s; border-top-width: %(luft)s; border-bottom-width: %(luft)s;
    border-radius: %(radius)s; background-clip: padding; }
QFrame#leisteLinks QToolButton, QFrame#leisteRechts QToolButton { border-radius: %(radius_klein)s; }
QFrame#leisteLinks QToolButton:checked, QFrame#leisteRechts QToolButton:checked { background: %(weich)s; border: none; color: %(auf_akzent)s; }
QToolButton#menueKnopf { color: %(auf_akzent)s; }
QToolButton#menueKnopf:checked { color: %(auf_akzent)s; }
QScrollArea[tafel="true"], QScrollArea[tafel="true"] > QWidget > QWidget { background: %(tafel)s; }
*[seitenKarte="true"] { border: %(luft)s solid %(bg)s; border-radius: %(radius)s; background-clip: padding; }          /* Mint: zusätzlich als Karte mit Rand */
QPushButton, QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QPlainTextEdit { border-radius: %(radius_klein)s; border-color: %(karte)s; }
QPushButton { border-color: %(hover)s; }
QPushButton:default { border-color: %(akzent)s; }
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus { border-color: %(akzent)s; }
QToolButton { border-radius: %(radius_klein)s; }
QMenu, QFrame[dropdownFenster], QComboBox QAbstractItemView { border-radius: %(radius)s; border-color: %(hover)s; }
QMenu::item, QComboBox QAbstractItemView::item { border-radius: %(radius_klein)s; }
QMenu::separator { background: %(hover)s; }
QTreeWidget, QListWidget { border-color: %(hover)s; border-radius: %(radius_klein)s; }
QGroupBox { border-color: %(hover)s; border-radius: %(radius)s; }
QStatusBar { border-top: none; background: %(flaeche)s; border-top-left-radius: %(radius)s; border-top-right-radius: %(radius)s; }
QFrame[frameShape="4"] { border: none; background: %(flaeche)s; max-height: """ f"{HOEHE_TRENNLINIE_MAX}" """px; }
QTabBar#bandReiter::tab:selected { border-bottom: 3px solid %(auf_akzent)s; }
"""


def _pfeile(farbe: str) -> tuple[str, str]:
    """Dropdown-Pfeile aus dem zentralen Lucide-Katalog für Qt-Stylesheets."""
    return icons.svg_datei("chevron-down", farbe), icons.svg_datei("chevron-up", farbe)


def _kreuz(farbe: str) -> str:
    return icons.svg_datei("x", farbe)


def _stil(app: QApplication) -> None:
    f = dict(MINT_FARBEN if _MINT else (WEICHE_FARBEN if WEICH else FARBEN)[_ist_dunkel(app)])
    f["pfeil_unten"], f["pfeil_oben"] = _pfeile(f["text"])
    f["x_bild"] = _kreuz(f["grau"])
    f["x_dunkel"] = _kreuz(AUF_AKZENT)
    from lunivo_writer.core.farben import Farbe
    f.setdefault("auf_akzent", Farbe.AUF_AKZENT)                       # Schrift auf der Akzentfläche (Mint: dunkel, sonst weiß)
    f["akzent_hover"] = f["kopf_hover"] if _MINT else Farbe.AKZENT_DUNKEL
    f["kf_papier"] = Farbe.PAPIER
    f["kf_leiste"], f["kf_leiste_rand"], f["kf_gitter"], f["kf_tinte"] = Farbe.LEISTE, Farbe.LEISTE_RAND, Farbe.GITTER, Farbe.TINTE     # Knöpfe auf dem Papier: unabhängig vom Thema
    from lunivo_writer.ui.baukasten.karte import karte_regeln
    qss = QSS % f + karte_regeln(f["akzent"], f["akzent"], Farbe.GRAU)           # Karten/Zeilen: eine Quelle (baukasten/karte.py)
    if _MINT:
        qss += MINT_QSS % f
    if app.styleSheet() != qss:                                    # unverändert: nichts neu auswerten lassen
        app.setStyleSheet(qss)


def _setze(app: QApplication, mode: str) -> None:
    global _FUSION
    if not _FUSION:                                                 # ein Stilwechsel baut alle Widgets neu auf (Sekunden): nur einmal
        fusion = QStyleFactory.create("Fusion")
        if fusion is not None:
            app.setStyle(fusion)
            _FUSION = True
    if mode == "mint":
        app.setPalette(_mint_palette())
    elif mode == "dark":
        p = QPalette()
        bg, base, txt = QColor(42, 46, 50), QColor(31, 34, 37), QColor(230, 233, 236)      # Leiste, Fläche um das Blatt, Schrift
        p.setColor(QPalette.Window, bg); p.setColor(QPalette.WindowText, txt)
        p.setColor(QPalette.Base, base); p.setColor(QPalette.AlternateBase, QColor(47, 51, 56))
        p.setColor(QPalette.Text, txt); p.setColor(QPalette.Button, QColor(47, 51, 56))
        p.setColor(QPalette.ButtonText, txt); p.setColor(QPalette.ToolTipBase, base)
        p.setColor(QPalette.ToolTipText, txt); p.setColor(QPalette.Highlight, QColor(74, 143, 216))
        p.setColor(QPalette.HighlightedText, Qt_white()); p.setColor(QPalette.Mid, QColor(124, 133, 142))
        p.setColor(QPalette.Dark, QColor(31, 34, 37))
        p.setColor(QPalette.Light, QColor(70, 74, 80)); p.setColor(QPalette.Midlight, QColor(58, 63, 69))
        p.setColor(QPalette.Link, QColor(110, 168, 230)); p.setColor(QPalette.LinkVisited, QColor(170, 140, 220))
        p.setColor(QPalette.BrightText, QColor(255, 255, 255))
        p.setColor(QPalette.PlaceholderText, QColor(150, 156, 162))
        grau = QColor(125, 130, 136)
        for rolle in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
            p.setColor(QPalette.Disabled, rolle, grau)
        p.setColor(QPalette.Disabled, QPalette.Base, QColor(38, 41, 45))
        p.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 86, 94))
        if WEICH:
            fenster, flaeche, knopf, schrift = QColor(61, 68, 75), QColor(52, 58, 64), QColor(67, 75, 83), QColor(221, 226, 230)
            for rolle, farbe in ((QPalette.Window, fenster), (QPalette.Base, flaeche), (QPalette.Dark, flaeche), (QPalette.Button, knopf),
                                 (QPalette.AlternateBase, knopf), (QPalette.WindowText, schrift), (QPalette.Text, schrift),
                                 (QPalette.ButtonText, schrift), (QPalette.Mid, QColor(140, 148, 155)), (QPalette.ToolTipBase, flaeche)):
                p.setColor(rolle, farbe)
        app.setPalette(p)
    elif mode == "light":
        app.setPalette(_helle_palette())                            # „Immer hell“ darf nie vom Systemdesign (z. B. qt5ct dunkel) abhängen
        _hell_feinschliff(app)
    else:
        app.setPalette(app.style().standardPalette())
        if _ist_dunkel(app):
            _setze(app, "dark")                                     # dunkles System: dieselbe Palette wie „Immer dunkel“
        else:
            _hell_feinschliff(app)


def _mint_palette() -> QPalette:
    p = QPalette()
    f = MINT_FARBEN
    fest = {QPalette.Window: f["bg"], QPalette.WindowText: f["text"], QPalette.Base: f["feld"], QPalette.AlternateBase: f["karte"],
            QPalette.Text: f["text"], QPalette.Button: f["karte"], QPalette.ButtonText: f["text"], QPalette.ToolTipBase: f["karte"],
            QPalette.ToolTipText: f["text"], QPalette.Highlight: "#85bd49", QPalette.HighlightedText: AUF_AKZENT, QPalette.Mid: f["grau"],
            QPalette.Dark: f["feld"], QPalette.Light: "#2c302e", QPalette.Midlight: f["rand"], QPalette.Link: "#85bd49",
            QPalette.LinkVisited: "#b49bd6", QPalette.BrightText: "#ffffff", QPalette.PlaceholderText: "#868d89"}
    for rolle, farbe in fest.items():
        p.setColor(rolle, QColor(farbe))
    for rolle in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
        p.setColor(QPalette.Disabled, rolle, QColor("#5f6f64"))
    p.setColor(QPalette.Disabled, QPalette.Highlight, QColor("#2e3330"))
    return p


def _helle_palette() -> QPalette:
    """Feste helle Grundpalette (wie Fusion hell), unabhängig von der Palette des Plattformdesigns."""
    p = QPalette()
    fest = {QPalette.Window: "#efefef", QPalette.WindowText: "#000000", QPalette.Base: "#ffffff", QPalette.AlternateBase: "#f7f7f7",
            QPalette.ToolTipBase: "#ffffdc", QPalette.ToolTipText: "#000000", QPalette.Text: "#000000", QPalette.Button: "#efefef",
            QPalette.ButtonText: "#000000", QPalette.BrightText: "#ffffff", QPalette.Light: "#ffffff", QPalette.Midlight: "#cacaca",
            QPalette.Mid: "#a0a0a0", QPalette.Dark: "#9f9f9f", QPalette.Shadow: "#767676", QPalette.Highlight: "#2f6fb5",
            QPalette.HighlightedText: "#ffffff", QPalette.Link: "#0000ff", QPalette.LinkVisited: "#ff00ff",
            QPalette.PlaceholderText: "#808080"}
    for rolle, farbe in fest.items():
        p.setColor(rolle, QColor(farbe))
    grau = QColor("#bebebe")
    for rolle in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
        p.setColor(QPalette.Disabled, rolle, grau)
    return p


def _hell_feinschliff(app: QApplication) -> None:
    """Helle Palette: Fläche um das Blatt; mit „Weichem Kontrast“ warme Töne."""
    pal = app.palette()
    pal.setColor(QPalette.Dark, QColor(215, 210, 200) if WEICH else QColor(226, 229, 234))
    if WEICH:
        for rolle, farbe in ((QPalette.Window, QColor(239, 235, 227)), (QPalette.Button, QColor(245, 242, 236)),
                             (QPalette.WindowText, QColor(35, 32, 25)), (QPalette.Text, QColor(35, 32, 25)),
                             (QPalette.ButtonText, QColor(35, 32, 25)), (QPalette.Mid, QColor(134, 128, 111))):
            pal.setColor(rolle, farbe)
    app.setPalette(pal)


def Qt_white() -> QColor:
    return QColor(255, 255, 255)
