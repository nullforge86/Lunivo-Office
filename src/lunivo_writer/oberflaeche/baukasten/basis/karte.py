"""Karte/Zeile: die eine Quelle für abgesetzte Flächen in den Seitenleisten (Kommentar, Fund, Funktionszeile, KI-Blase).

Ein Widget wird nur mit ``als_karte(widget, art)`` gekennzeichnet (Eigenschaft ``karte``); die Regeln dazu stehen genau einmal hier und werden vom Thema
(``oberflaeche/thema.py``) in das Programm-Stylesheet aufgenommen. Kein Widget setzt dafür ein eigenes Stylesheet."""
from __future__ import annotations

from lunivo_writer.oberflaeche.baukasten.basis.mass import CHAT_CHIP_HOEHE, PADDING_KI_ANBIETER_EINTRAG, PADDING_KI_LISTENEINTRAG, RADIUS_FELD, CHAT_SENDEN, SCHRIFT_HINWEIS, PADDING_HILFE_CHIP, RADIUS_CHIP, RADIUS_EINGABEKASTEN, RADIUS_KLEIN, RADIUS_KARTE, RADIUS_MITTEL

ARTEN = ("zeile", "karte", "kompakt", "ki", "markiert", "nutzer", "fehler", "eingabe", "chip", "senden", "anhang", "miniatur", "liste", "liste_eng", "listenleiste", "listenfuss")


def als_karte(widget, art: str = "karte"):
    """Kennzeichnet das Widget als Karte der Art ``art``: zeile (anklickbar, durchsichtig), karte (Fund), kompakt (Kommentar), ki/markiert (Blase mit Streifen links),
    nutzer (graue Nutzerblase), fehler (Fehlerkarte), eingabe (Eingabekasten; Eigenschaft ``fokus`` = Rahmen in Akzentfarbe), chip (QPushButton), senden (runder QPushButton), anhang (Bild-Anhang über dem Textfeld), miniatur (QLabel mit Bildvorschau, dünner Rahmen), liste / liste_eng (QListWidget mit Rahmen, hohe bzw. engere Zeilen; listenleiste / listenfuss (``ListenLeiste``: Rahmen um Liste + Knopfleiste, Trennlinie über den Knöpfen); ein ``chip`` ist checkbar: gewählt = Akzent)."""
    widget.setProperty("karte", art)
    widget.style().unpolish(widget); widget.style().polish(widget)          # eine spätere Art (z. B. Liste „eng“ statt „liste“) gilt auch für ein schon eingerichtetes Widget
    return widget


def karte_regeln(fokus: str, ki: str, grau: str, fehler: str = "#c92a2a") -> str:
    """QSS-Text aller Kartenarten; Farben ``fokus`` (Fokusrahmen, KI-Streifen), ``ki`` (Streifen KI-Blase), ``grau`` (Streifen sonst), ``fehler`` (Fehlerkarte) kommen vom Thema."""
    flaeche = "border: 1px solid palette(midlight); "
    return (
        'QFrame[karte="zeile"] { ' + flaeche + 'border-radius: ' + str(RADIUS_MITTEL) + 'px; background: transparent; }'
        'QFrame[karte="zeile"]:hover { background: palette(alternate-base); border-color: palette(mid); }'
        'QFrame[karte="zeile"]:focus { border: 2px solid ' + fokus + '; }'
        'QFrame[karte="karte"] { ' + flaeche + 'border-radius: ' + str(RADIUS_KARTE) + 'px; background: rgba(128, 128, 128, 0.07); }'
        'QFrame[karte="kompakt"] { ' + flaeche + 'border-radius: ' + str(RADIUS_MITTEL) + 'px; background: rgba(128, 128, 128, 0.06); }'
        'QFrame[karte="karte"] QLabel, QFrame[karte="kompakt"] QLabel { border: none; background: transparent; }'
        'QFrame[karte="ki"], QFrame[karte="ki"] QFrame { border-left: 4px solid ' + ki + '; }'
        'QFrame[karte="markiert"], QFrame[karte="markiert"] QFrame { border-left: 4px solid ' + grau + '; }'
        'QFrame[karte="nutzer"] { border: none; border-radius: ' + str(RADIUS_KARTE) + 'px; background: rgba(128, 128, 128, 0.20); }'
        'QFrame[karte="fehler"] { border: 1px solid ' + fehler + '; border-radius: ' + str(RADIUS_KARTE) + 'px; background: rgba(128, 128, 128, 0.07); }'
        'QFrame[karte="nutzer"] QLabel, QFrame[karte="fehler"] QLabel { border: none; background: transparent; }'
        'QFrame[karte="eingabe"] { border: 1px solid palette(mid); border-radius: ' + str(RADIUS_EINGABEKASTEN) + 'px; background: palette(base); }'
        'QFrame[karte="eingabe"][fokus="true"] { border: 1px solid ' + fokus + '; }'
        'QPushButton[karte="chip"] { border: 1px solid palette(mid); border-radius: ' + str(CHAT_CHIP_HOEHE // 2) + 'px; padding: ' + PADDING_HILFE_CHIP + '; background: transparent; font-size: ' + str(SCHRIFT_HINWEIS) + 'pt; }'
        'QPushButton[karte="chip"]:hover { background: palette(alternate-base); }'
        'QPushButton[karte="chip"]:disabled { border-color: palette(midlight); color: palette(mid); }'
        'QPushButton[karte="chip"]:checked { background: palette(highlight); color: palette(highlighted-text); border-color: palette(highlight); }'
        'QListWidget[karte="liste"], QListWidget[karte="liste_eng"] { border: 1px solid palette(mid); border-radius: ' + str(RADIUS_FELD) + 'px; }'
        'QListWidget[karte="liste"]::item { padding: ' + PADDING_KI_ANBIETER_EINTRAG + '; border-bottom: 1px solid palette(midlight); }'
        'QListWidget[karte="liste_eng"]::item { padding: ' + PADDING_KI_LISTENEINTRAG + '; border-bottom: 1px solid palette(midlight); }'
        'QListWidget[karte="liste"]::item:selected, QListWidget[karte="liste_eng"]::item:selected { background: palette(highlight); color: palette(highlighted-text); }'
        'QListWidget[karte="liste"]::item:hover:!selected, QListWidget[karte="liste_eng"]::item:hover:!selected { background: palette(alternate-base); }'
        'QFrame[karte="listenleiste"] { border: 1px solid palette(mid); border-radius: ' + str(RADIUS_FELD) + 'px; background: palette(base); }'
        'QFrame[karte="listenleiste"] QListWidget[karte="liste"] { border: none; border-radius: 0px; background: transparent; }'
        'QFrame[karte="listenfuss"] { border: none; border-top: 1px solid palette(midlight); background: transparent; }'
        'QFrame[karte="anhang"] { border: 1px solid palette(mid); border-radius: ' + str(RADIUS_MITTEL) + 'px; background: rgba(128, 128, 128, 0.10); }'
        'QFrame[karte="anhang"] QLabel { border: none; background: transparent; }'
        'QLabel[karte="miniatur"] { border: 1px solid palette(mid); border-radius: ' + str(RADIUS_KLEIN) + 'px; background: palette(base); }'
        'QPushButton[karte="senden"] { border: none; padding: 0px; border-radius: ' + str(CHAT_SENDEN // 2) + 'px; background: ' + fokus + '; }'
        'QPushButton[karte="senden"]:disabled { background: rgba(128, 128, 128, 0.25); }'
    )
