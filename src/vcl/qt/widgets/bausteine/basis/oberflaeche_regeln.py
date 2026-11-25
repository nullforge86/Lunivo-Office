"""Oberflächen-Regeln — die EINE Quelle für das Aussehen aller Rollen außerhalb des Dashboards (Ribbon, Seitenleisten, Dialoge, Formulare).

Ebene 1 (Designsystem), Schwester von ``dashboard_regeln.py`` und ``karte.py``: ``thema.py`` ruft ``oberflaeche_regeln(farben, fehler)`` auf. Ein Widget
setzt dafür kein eigenes Stylesheet; es trägt nur eine Rolle (``darstellung.rolle(widget, "name")`` bzw. ``widget.setProperty("rolle", "name")``).

Rollen: ``warnung``, ``fehler``, ``fett``, ``abschnittsbeschriftung``, ``abschnittsknopf``, ``abschnittsband``, ``ohne_pfeile``, ``rahmenwahl``, ``rahmenknopf``,
``lese_ende_status``, ``lese_ende``, ``schweb``, ``bandpfeil``, ``bandstarter``, ``worum``, ``werkreiter``, ``rahmen``, ``vorschaublatt``, ``vorschautext``,
``stufennummer``, ``stufe``, ``tastenchip``, ``pille``, ``pille_akzent``, ``kompaktleiste``, ``schalter_an``, ``textknopf``, ``transparent``, ``listentext``, ``listentext_fett``;
Container mit ``reiterart="flach"`` zeigen ihre Reiter flach (nur Linie unter dem gewählten Reiter).
"""
from __future__ import annotations

from framework.datentypen.farben import Farbe
from writer.baukasten.basis import mass as m

_REGELN = """
QLabel[rolle="warnung"] { color: %(orange)s; }
QLabel[rolle="fehler"] { color: %(fehler)s; }
*[rolle="fett"] { font-weight: 600; }
QLabel[rolle="abschnittsbeschriftung"] { color: %(grau)s; font-size: %(s_klein)spt; font-weight: 600; }
QToolButton[rolle="abschnittsknopf"], QToolButton[rolle="abschnittsknopf"]:hover { border: none; border-radius: 0; border-bottom: 2px solid transparent; background: transparent; padding: %(pad_abschnittsknopf)s; color: %(text)s; }
QToolButton[rolle="abschnittsknopf"]:checked { color: %(akzent)s; border-bottom: 2px solid %(akzent)s; background: transparent; }
*[rolle="abschnittsband"] { background: %(hover)s; padding: %(pad_abschnittsband)s; }
QDoubleSpinBox[rolle="ohne_pfeile"]::up-button, QDoubleSpinBox[rolle="ohne_pfeile"]::down-button { width: 0px; border: none; }
QDoubleSpinBox[rolle="ohne_pfeile"]::up-arrow, QDoubleSpinBox[rolle="ohne_pfeile"]::down-arrow { width: 0px; height: 0px; }
QToolButton[rolle="rahmenwahl"] { border: 1px solid transparent; border-radius: %(r_feld)spx; }
QToolButton[rolle="rahmenwahl"]:checked { background: %(hover)s; border-color: %(grau)s; }
QToolButton[rolle="rahmenknopf"] { border: 1px solid %(rand)s; border-radius: %(r_feld)spx; }
QToolButton[rolle="rahmenknopf"]:hover { background: %(hover)s; border-color: %(grau)s; }
QToolButton[rolle="rahmenknopf"]:checked { background: %(grau)s; border-color: %(akzent)s; }
QPushButton[rolle="lese_ende_status"] { background: %(akzent)s; color: %(auf_akzent)s; border: none; border-radius: %(r_feld)spx; padding: %(pad_lese_ende_status)s; font-weight: bold; }
QPushButton[rolle="lese_ende_status"]:hover { background: %(akzent_hover)s; color: %(schwarz)s; }
QPushButton[rolle="lese_ende"] { background: %(akzent)s; color: %(auf_akzent)s; border: 2px solid %(text)s; border-radius: %(r_karte)spx; padding: %(pad_lese_ende)s; font-size: %(s_lese_ende)spt; font-weight: bold; }
QPushButton[rolle="lese_ende"]:hover { background: %(akzent_hover)s; color: %(schwarz)s; }
QToolButton[rolle="schweb"] { background: %(karte)s; border: 1px solid %(grau)s; border-radius: %(r_mittel)spx; }
QToolButton[rolle="schweb"]:hover { background: %(hover)s; }
QToolButton[rolle="schweb"]:focus { border: 2px solid %(akzent)s; }
QToolButton[rolle="bandpfeil"] { border: none; border-radius: 0; font-size: %(s_bandknopf)spt; font-weight: 600; padding: %(pad_bandknopf)s; background: %(bg)s; color: %(text)s; }
QToolButton[rolle="bandpfeil"]:hover { background: %(hover)s; }
QToolButton[rolle="bandpfeil"]:focus { border: 2px solid %(akzent)s; }
QToolButton[rolle="bandstarter"] { font-size: %(s_bandgruppe_titel)spt; }
QLineEdit[rolle="worum"] { border: none; border-bottom: 1px dashed %(warnung)s; background: transparent; padding: %(pad_worum)s; border-radius: 0; }
QLabel[rolle="worum"] { color: %(warnung)s; }
QPushButton[rolle="werkreiter"] { border: none; border-bottom: 3px solid transparent; border-radius: 0; padding: %(pad_werkreiter)s; font-weight: bold; color: %(grau)s; background: transparent; }
QPushButton[rolle="werkreiter"]:checked { color: %(text)s; border-bottom: 3px solid %(akzent)s; }
QPushButton[rolle="werkreiter"]:hover { color: %(text)s; }
QPushButton[rolle="werkreiter"]:focus { border-bottom: 3px solid %(akzent)s; }
*[rolle="rahmen"] { border: 1px solid %(rand)s; border-radius: %(r_mittel)spx; }
*[rolle="vorschaublatt"] { background: %(papier)s; border: 1px solid %(grau_hell)s; }
QTextEdit[rolle="vorschautext"] { background: %(papier)s; color: %(tinte)s; font-size: %(s_vorschau)spt; }
QLabel[rolle="stufennummer"] { font-weight: bold; }
QLabel[rolle="stufe"] { font-weight: bold; border-radius: %(r_stufe)spx; }
QLabel[rolle="tastenchip"] { border: 1px solid %(grau)s; border-radius: %(r_marke)spx; padding: %(pad_tastenchip)s; font-size: %(s_klein)spt; }
QPushButton[rolle="pille"] { border: 1px solid %(grau)s; border-radius: %(r_pille)spx; padding: 0; }
QPushButton[rolle="pille"]:checked { background: %(an)s; color: %(an_schrift)s; border-color: %(an)s; }
QPushButton[rolle="pille_akzent"] { border-width: 1px; border-style: solid; border-radius: %(r_pille)spx; padding: 0; }
QWidget[rolle="kompaktleiste"] QPushButton { padding: %(pad_navigation_knopf)s; font-size: %(s_hinweis)spt; }
QPushButton[rolle="schalter_an"]:checked { background: %(an)s; color: %(an_schrift)s; border-color: %(an)s; font-weight: bold; }
QToolButton[rolle="textknopf"] { font-weight: bold; }
QScrollArea[rolle="transparent"], QScrollArea[rolle="transparent"] > QWidget > QWidget { background: transparent; }
*[rolle="listentext"] { border: none; background: transparent; font-size: %(s_liste)spt; }
*[rolle="listentext_fett"] { font-size: %(s_liste)spt; font-weight: 600; }
QFrame[rolle="transparent"] { border: none; background: transparent; }
*[rolle="kachelfeld"] QToolButton:focus { border: 2px solid %(akzent)s; border-radius: %(r_klein)spx; }
*[rolle="kapsel"] { background: transparent; color: %(grau)s; border: 1px solid %(grau)s; border-radius: %(r_kapsel)spx; }
*[rolle="kapsel"][status="an"] { background: %(an)s; color: %(an_schrift)s; border: 1px solid %(an)s; font-weight: bold; }
*[reiterart="flach"] QTabWidget::pane { border: none; border-top: 1px solid %(rand)s; padding-top: %(abstand_unter_reiter)spx; }
*[reiterart="flach"] QTabBar::tab { background: transparent; border: none; border-bottom: 2px solid transparent; padding: %(pad_zusatz_reiter)s; margin-right: %(margin_zusatz_reiter)s; color: %(text)s; }
*[reiterart="flach"] QTabBar::tab:selected { font-weight: 600; border-bottom: 2px solid %(akzent)s; }
*[reiterart="flach"] QTabBar::tab:hover:!selected { border-bottom: 2px solid %(hover)s; }
"""


def oberflaeche_regeln(f: dict, fehler: str) -> str:
    """QSS-Text der Rollen; ``f`` sind die Themenfarben aus ``thema.py``, ``fehler`` die Fehlerfarbe des Themas."""
    werte = dict(f)
    werte.update(
        fehler=fehler, orange=Farbe.ORANGE, warnung=Farbe.WARNUNG, schwarz=Farbe.SCHWARZ, grau_hell=Farbe.GRAU_HELL, papier=Farbe.PAPIER, tinte=Farbe.SYMBOL,
        an=Farbe.AN, an_schrift=Farbe.AN_SCHRIFT,
        s_klein=m.SCHRIFT_KLEIN, s_hinweis=m.SCHRIFT_HINWEIS, s_liste=m.SCHRIFT_LISTE, s_vorschau=m.SCHRIFT_VORSCHAU, s_bandknopf=m.SCHRIFT_BANDKNOPF,
        s_bandgruppe_titel=m.SCHRIFT_BANDGRUPPE_TITEL, s_lese_ende=m.SCHRIFT_LESEENDEKNOPF,
        r_feld=m.RADIUS_FELD, r_klein=m.RADIUS_KLEIN, r_kapsel=m.RADIUS_KAPSEL, r_mittel=m.RADIUS_MITTEL, r_karte=m.RADIUS_KARTE, r_pille=m.RADIUS_PILLE, r_marke=m.RADIUS_MARKE, r_stufe=m.RADIUS_STUFE,
        pad_abschnittsknopf=m.PADDING_ABSCHNITT_KNOPF, pad_abschnittsband=m.PADDING_ABSCHNITTSBAND, pad_lese_ende_status=m.PADDING_LESEENDE_STATUS,
        pad_lese_ende=m.PADDING_LESEENDEKNOPF, pad_bandknopf=m.PADDING_BANDKNOPF, pad_worum=m.PADDING_SEITENLEISTE_WARNUNG, pad_werkreiter=m.PADDING_SEITENLEISTE_REITER,
        pad_tastenchip=m.PADDING_TASTENKUERZEL, pad_navigation_knopf=m.PADDING_NAVIGATION_KNOPF, pad_zusatz_reiter=m.PADDING_ZUSATZ_REITER, abstand_unter_reiter=m.ABSTAND_UNTER_REITER,
        margin_zusatz_reiter=m.MARGIN_RECHTS_ZUSATZ_REITER,
    )
    return _REGELN % werte
