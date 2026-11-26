"""Dashboard-Regeln — die EINE Quelle für das Aussehen der Dashboard-Seiten (Datei-Ansicht, Optionen, Speichern-Fenster).

Ebene 1 (Designsystem), Schwester von ``karte.py``: ``thema.py`` ruft ``dashboard_regeln(farben)`` auf und nimmt den Text in das Programm-Stylesheet auf.
Farben kommen ausschließlich als Themenfarben (``farben``), Maße ausschließlich aus ``mass``. Seiten und Fenster setzen KEIN eigenes Stylesheet:
sie kennzeichnen ihre Widgets nur mit einem Namen (``setObjectName``) oder einer Rolle (``darstellung.rolle``). Die Wurzel jeder Dashboard-Seite trägt ``dashboard=true`` (``darstellung.grundschrift``); darunter gilt ``mass.SCHRIFT_DASHBOARD_TEXT``. Rollen:

* ``rolle="hinweis"`` / ``"text"`` / ``"kursiv"`` (Label)  ·  ``"link"`` / ``"link_links"`` (flacher Knopf in Akzentschrift)
* ``rolle="plakette"`` mit ``status="an"|"aus"`` (kleine Anzeige)  ·  ``rolle="fehler"`` (Meldung)  ·  ``rolle="papiervorschau"``
* ``QGroupBox[gruppenart="karte"]`` (Kachel einer Optionen-Seite), ``QWidget[letzte="true"]`` (letzte Zeile ohne Trennlinie)
"""
from __future__ import annotations

from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende import mass as m

_REGELN = """
/* ---- Knöpfe: EINE Höhe, EIN Innenabstand, EIN Rahmen für jeden Knopf der Dashboard-Seiten; Hauptknöpfe (Akzent) und Rolle "aktion" sind zusätzlich gleich breit ---- */
QWidget[dashboard="true"] QPushButton { min-height: %(h_innen)spx; min-width: %(b_innen)spx; padding: 0 %(pad_h)spx; }
QWidget[dashboard="true"] QPushButton#optFertig, QWidget[dashboard="true"] QPushButton#sfSpeichern { border: 1px solid %(akzent)s; min-width: %(b_aktion_innen)spx; }
QWidget[dashboard="true"] QPushButton#bsKnopf, QWidget[dashboard="true"] QPushButton#bsDatei, QWidget[dashboard="true"] QPushButton#optZurueck, QWidget[dashboard="true"] QPushButton#optWahl { min-width: 0; min-height: 0; }
QWidget[dashboard="true"] QPushButton#bsDatei { min-height: %(h_zuletzt)spx; }
QWidget[dashboard="true"] QPushButton#optWahl { min-height: %(h_wahl)spx; }
QPushButton[rolle="aktion"] { min-width: %(b_aktion_innen)spx; }
QPushButton[rolle="symbol"] { min-width: %(b_symbol_innen)spx; padding: 0; }
QPushButton[rolle="link"], QPushButton[rolle="link_links"] { min-width: 0; min-height: 0; }

/* ---- gemeinsame Rollen der Dashboard-Seiten ---- */
QLabel[rolle="seitentitel"] { font-size: %(s_titel)spt; font-weight: 600; }
QLabel[rolle="text"] { color: %(text)s; }
QLabel[rolle="hinweis"] { color: %(text)s; font-size: %(s_hinweis)spt; }
QLabel[rolle="kursiv"] { color: %(text)s; font-style: italic; }
QLabel[rolle="fehler"] { color: %(fehler)s; }
QLabel[rolle="plakette"] { border-radius: %(r_klein)spx; font-weight: 700; font-size: %(s_klein)spt; padding: %(pad_plakette)s; color: %(an_schrift)s; background: %(grau)s; }
QLabel[rolle="plakette"][status="an"] { background: %(an)s; }
QLabel[rolle="papiervorschau"] { color: %(tinte)s; border-radius: %(r_feld)spx; padding: %(pad_vorschau)s; }
QToolButton[rolle="steuerknopf"] { font-weight: 600; padding: %(pad_steuerknopf)s; }
QPushButton[rolle="link"], QPushButton[rolle="link_links"] { border: none; background: transparent; }
QPushButton[rolle="link_links"] { text-align: left; padding: %(pad_link)s; }
QWidget#optPaar[letzte="true"] { border-bottom: none; }
QGroupBox[gruppenart="karte"] { border: 1px solid %(rand)s; border-radius: %(r_karte)spx; margin-top: %(margin_gruppe)s; padding: %(pad_gruppe)s; background: transparent; }
QGroupBox[gruppenart="karte"]::title { subcontrol-origin: margin; subcontrol-position: top left; left: 2px; padding: 0; color: %(text)s; font-size: %(s_klein)spt; font-weight: 600; }
QGroupBox[gruppenart="flach"] { border: none; border-top: 1px solid %(rand)s; margin-top: %(margin_gruppe_flach)s; padding-top: %(pad_gruppe_oben)s; }
QGroupBox[gruppenart="flach"]::title { subcontrol-origin: margin; subcontrol-position: top left; padding: %(pad_gruppentitel)s; color: %(grau)s; font-size: %(s_klein)spt; font-weight: 600; }

/* ---- Datei-Ansicht (Backstage) ---- */
QWidget#bsLinks { background: %(bg)s; }
QListWidget#bsListe { background: transparent; border: none; outline: none; font-size: %(s_liste)spt; }
QListWidget#bsListe::item { padding-left: %(pad_liste_links)s; border: none; }
QListWidget#bsListe::item:selected, QListWidget#bsListe::item:hover:enabled { background: %(hover)s; color: %(text)s; }
QListWidget#bsListe::item:disabled { color: %(grau)s; }
QLabel#bsZuletzt { font-size: %(s_liste)spt; }
QPushButton#bsDatei { border: none; background: transparent; text-align: left; padding: %(pad_navi)s; border-radius: %(r_klein)spx; }
QPushButton#bsDatei:hover:enabled { background: %(hover)s; }
QToolButton#bsKlein { border: none; background: transparent; border-radius: %(r_klein)spx; }
QToolButton#bsKlein:hover { background: %(hover)s; }
QWidget#bsRechts, QWidget#bsInhalt, QScrollArea#bsSeite, QScrollArea#bsSeite > QWidget > QWidget { background: %(flaeche)s; }
QLabel#bsTitel { font-size: %(s_titel)spt; }
QLabel#bsGruppe { font-size: %(s_liste)spt; font-weight: 600; }
QLabel#bsHinweis { color: %(grau)s; }
QPushButton#bsKnopf { border: none; background: transparent; padding: %(pad_knopf)s; text-align: left; border-radius: %(r_feld)spx; }
QPushButton#bsKnopf:hover:enabled { background: %(hover)s; }
QPushButton#bsKnopf:disabled { color: %(grau)s; }
QWidget#optKopf { border: none; }
QPushButton#optZurueck { border: none; background: transparent; font-size: %(s_titel_klein)spt; font-weight: 600; text-align: left; padding: %(pad_zurueck)s; }
QPushButton#optFertig { font-weight: 600; }

/* ---- Optionen ---- */
QWidget#optLinks { background: %(bg)s; border-right: 1px solid %(rand)s; }
QAbstractItemView#optNavigation { background: transparent; border: none; outline: none; }
QAbstractItemView#optNavigation::item { padding: %(pad_navi)s; margin: %(margin_navi)s; border-radius: %(r_feld)spx; color: %(text)s; }
QAbstractItemView#optNavigation::item:selected { background: %(akzent)s; color: %(auf_akzent)s; font-weight: 600; }
QAbstractItemView#optNavigation::item:hover:enabled:!selected { background: %(hover)s; }
QScrollArea#optSeite, QScrollArea#optSeite > QWidget > QWidget { background: transparent; border: none; }
QWidget#optPaar { border-bottom: 1px solid %(rand)s; }
QLabel#optErklaerung { color: %(text)s; font-style: italic; padding: %(pad_erklaerung)s; border-top: 1px solid %(rand)s; }
QFrame#optSchriftkarte { border: 1px solid %(rand)s; border-radius: %(r_mittel)spx; }
QLabel#optVorschau { background: %(papier)s; color: %(tinte)s; border-radius: %(r_feld)spx; padding: %(pad_vorschau)s; }
QLabel#optHinweis { color: %(text)s; font-size: %(s_hinweis)spt; padding-left: %(pad_hinweis_links)s; }
QPushButton#optWahl { border: 1px solid %(grau)s; border-radius: %(r_mittel)spx; padding: %(pad_wahl)s; }
QPushButton#optWahl:checked { background: %(akzent)s; color: %(auf_akzent)s; font-weight: 600; border-color: %(akzent)s; }
QPushButton#optWahl:focus { border: 2px solid %(akzent)s; }
QWidget#optAnsicht QToolButton:focus { border: 2px solid %(akzent)s; border-radius: %(r_klein)spx; }

/* ---- Drucken: Seiten der Druckvorschau ---- */
QLabel#vorschauSeite { border: 1px solid %(grau)s; }
QLabel#vorschauSeite[gewaehlt="true"] { border-color: %(akzent)s; }

/* ---- Hilfe (Handbuch-Gliederung, Erweiterungskarten) ---- */
QListWidget#hilfeNav { background: %(bg)s; border: 1px solid %(rand)s; border-radius: %(r_feld)spx; padding: %(pad_hilfe_nav)s; outline: none; }
QListWidget#hilfeNav::item { padding: %(pad_hilfe_eintrag)s; border-radius: %(r_eintrag)spx; }
QListWidget#hilfeNav::item:selected { background: %(hover)s; color: %(text)s; }
QFrame#erwKarte { border: 1px solid %(rand)s; border-radius: %(r_mittel)spx; }

/* ---- Speichern-Fenster ---- */
QWidget#sfLinks { background: %(bg)s; border-right: 1px solid %(rand)s; }
QLabel#sfTitel { font-size: %(s_titel)spt; font-weight: 600; padding: %(pad_sf_titel)s; }
QListWidget#sfOrte { background: transparent; border: none; outline: none; font-size: %(s_liste)spt; }
QListWidget#sfOrte::item { padding-left: %(pad_sf_ort)s; border-radius: %(r_feld)spx; }
QListWidget#sfOrte::item:selected { background: %(hover)s; color: %(akzent)s; }
QListWidget#sfOrte::item:hover:!selected { background: %(hover)s; }
QFrame#sfPfad { border: 1px solid %(grau)s; border-radius: %(r_klein)spx; }
QFrame#sfPfad QToolButton { border: none; padding: %(pad_sf_pfad)s; }
QFrame#sfPfad QToolButton:hover { background: %(hover)s; border-radius: %(r_marke)spx; }
QPushButton#sfSpeichern { font-weight: 600; }
QTreeView#sfListe::item { padding: %(pad_sf_datei)s; }
QPushButton#sfSpeichern:disabled { background: %(grau)s; }
"""


_TYPEN = ("QLabel", "QCheckBox", "QRadioButton", "QPushButton", "QToolButton", "QLineEdit", "QSpinBox", "QDoubleSpinBox", "QComboBox", "QGroupBox",
          "QListWidget", "QTreeWidget", "QTreeView", "QPlainTextEdit", "QTextBrowser")
_WURZEL = 'QWidget[dashboard="true"] '


def _unter_wurzel(text: str) -> str:
    """Rollenregeln gelten nur unter einer Dashboard-Wurzel und sind dort spezifischer als die Grundschrift."""
    zeilen = []
    for z in text.split("\n"):
        if "[rolle=" in z and " {" in z:
            wahl, rest = z.split(" {", 1)
            z = ", ".join(_WURZEL + w.strip() for w in wahl.split(",")) + " {" + rest
        zeilen.append(z)
    return "\n".join(zeilen)


def dashboard_regeln(f: dict) -> str:
    """QSS-Text der Dashboard-Seiten; ``f`` sind die Themenfarben aus ``thema.py``."""
    werte = dict(f)
    werte.update(
        papier=Farbe.PAPIER, tinte=Farbe.SYMBOL, an=Farbe.AN, an_schrift=Farbe.AN_SCHRIFT, fehler=Farbe.ROT_HELL,
        s_text=m.SCHRIFT_DASHBOARD_TEXT, s_klein=m.SCHRIFT_DASHBOARD_KLEIN, s_hinweis=m.SCHRIFT_DASHBOARD_HINWEIS, s_liste=m.SCHRIFT_DASHBOARD_LISTE,
        s_titel=m.SCHRIFT_DASHBOARD_TITEL, s_titel_klein=m.SCHRIFT_DASHBOARD_TITEL_KLEIN,
        r_klein=m.RADIUS_KLEIN, r_mittel=m.RADIUS_MITTEL, r_karte=m.RADIUS_KARTE, r_feld=m.RADIUS_FELD, r_marke=m.RADIUS_MARKE,
        pad_plakette=m.PADDING_PLAKETTE, pad_vorschau=m.PADDING_OPTIONEN_VORSCHAU, pad_link=m.PADDING_STARTKNOPF_LINK,
        margin_gruppe=m.MARGIN_OBEN_OPTIONEN_GRUPPE, pad_gruppe=m.PADDING_OPTIONEN_GRUPPE, pad_liste_links=m.PADDING_LINKS_BACKSTAGE_LISTE,
        pad_navi=m.PADDING_NAVIGATION_EINTRAG, margin_navi=m.MARGIN_NAVIGATION_EINTRAG, pad_knopf=m.PADDING_BACKSTAGE_KNOPF,
        pad_zurueck=m.PADDING_BACKSTAGE_ZURUECK, pad_erklaerung=m.PADDING_OPTIONEN_ERKLAERUNG,
        pad_hinweis_links=m.PADDING_LINKS_OPTIONEN_HINWEIS, pad_wahl=m.PADDING_OPTIONEN_WAHL, pad_sf_titel=m.PADDING_SPEICHERN_TITEL,
        pad_sf_ort=m.PADDING_LINKS_SPEICHERN_ORT, pad_sf_pfad=m.PADDING_SPEICHERN_PFADKNOPF,
        h_innen=m.HOEHE_KNOPF - 2, b_innen=m.GROESSE_KNOPF_MIN[0] - 2 * m.PADDING_KNOPF_DASHBOARD_H - 2, pad_h=m.PADDING_KNOPF_DASHBOARD_H,
        b_aktion_innen=m.BREITE_KNOPF_AKTION - 2 * m.PADDING_KNOPF_DASHBOARD_H - 2, b_symbol_innen=m.BREITE_KNOPF_KLEIN - 2, h_zuletzt=m.HOEHE_ZEILE_ZULETZT, h_wahl=m.HOEHE_WAHLKARTE,
        pad_hilfe_nav=m.PADDING_HANDBUCH_NAVIGATION, pad_hilfe_eintrag=m.PADDING_HANDBUCH_EINTRAG, r_eintrag=m.RADIUS_EINTRAG, pad_steuerknopf=m.PADDING_BACKSTAGE_STEUERKNOPF, pad_sf_datei=m.PADDING_SPEICHERN_DATEIZEILE, margin_gruppe_flach=m.MARGIN_OBEN_GRUPPE_ZUSATZ, pad_gruppe_oben=m.PADDING_GRUPPE_OBEN, pad_gruppentitel=m.PADDING_GRUPPENTITEL,
    )
    grund = ", ".join(_WURZEL + t for t in _TYPEN) + " { font-size: %(s_text)spt; }\n"
    return (grund + _unter_wurzel(_REGELN)) % werte
