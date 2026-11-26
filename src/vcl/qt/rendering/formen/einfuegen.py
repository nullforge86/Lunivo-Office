from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from writer.funktionen import bearbeiten as _bearbeiten
from writer.werte import Bereich, Stelle
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.rendering.formen import formen_katalog as K
from writer.anbindung.einfuegen_hilfen import wordart_vorlagen


FORMEN = ["Rechteck", "Abgerundetes Rechteck", "Ellipse", "Dreieck", "Raute", "Pfeil nach rechts", "Stern", "Sprechblase", "Linie"]


FORMEN += [n for n in K.namen() if n not in FORMEN]           # die ganze Galerie (Einfügen ▸ Formen), auch im Fenster „Form“


def _leer(w: int, h: int) -> QImage:
    img = QImage(w, h, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    return img


# ---- WordArt --------------------------------------------------------------------------------------------------------
WORDART_STILE = ["Verlauf", "Schatten", "Umriss", "Regenbogen", "Welle"]


WORDART_VORGABEN = [(n, "Vorlage", Farbe.AKZENT) for n, *_r in wordart_vorlagen()]    # bleibt für ältere Aufrufer (Name, Stil, Farbe)


WORDART_STANDARDTEXT = "Hier Text einfügen"


# ---- Diagramm --------------------------------------------------------------------------------------------------------
DIAGRAMMARTEN = ["Säulen", "Balken", "Linie", "Kreis"]


def diagramm_bild(art: str, titel: str, kategorien: list[str], reihen: dict[str, list[float]], b: int = 640, h: int = 400) -> QImage:
    """``art``: Untertyp aus ``editor.diagramme.diagramm.TYPEN`` oder einer der früheren Namen (Säulen, Balken, Linie, Kreis)."""
    from vcl.qt.rendering import diagramme as D
    return D.bild(art, titel, kategorien, reihen, b, h)


# Galerie „Integriert“ (Einfügen ▸ Gleichung ▾): (Name, Formel in der einfachen Schreibweise von ``formel_teile``)
GLEICHUNGEN = [("Kreisfläche", "A = \\pi r^2"),
               ("Binomischer Lehrsatz", "(x + a)^n = \\sum_{k=0}^{n} C(n,k) x^k a^{n−k}"),
               ("Summenentwicklung", "(1 + x)^n = 1 + nx/1! + n(n − 1)x^2/2! + …"),
               ("Fourier-Reihe", "f(x) = a_0 + \\sum_{n=1}^{\\infty} (a_n cos(n\\pi x/L) + b_n sin(n\\pi x/L))"),
               ("Satz des Pythagoras", "a^2 + b^2 = c^2"),
               ("Quadratische Formel", "x = (−b \\pm sqrt(b^2 − 4ac)) / 2a"),
               ("Taylor-Entwicklung", "e^x = 1 + x/1! + x^2/2! + x^3/3! + …,  −\\infty < x < \\infty")]


# ---- Deckblatt ----------------------------------------------------------------------------------------------------------------
DECKBLATT_VORLAGEN = ["Schlicht", "Mit Linie", "Zentriert", "Farbband"]


def deckblatt_einfuegen(ed, vorlage: str, titel: str, untertitel: str, autor: str, datum: str) -> None:
    """Setzt ein Deckblatt an den Anfang des Dokuments; danach beginnt der Text auf einer neuen Seite."""
    zentriert = vorlage in ("Zentriert", "Mit Linie")
    teile = [(titel, 30, True, 120), (untertitel, 16, False, 6), ("", 12, False, 160), (autor, 13, False, 4), (datum, 12, False, 4)]

    zeilen = []
    for text, pt, fett, abstand in teile:
        af = {"abstand_vor": abstand / 0.75, "ausrichtung": "mitte" if zentriert else "links"}
        zf = {"groesse_pt": float(pt), "fett": True if fett else None}
        if vorlage == "Farbband" and fett:                  # Titel weiß auf farbigem Band über die ganze Breite
            af.update(hintergrund=Farbe.AKZENT, abstand_nach=18 / 0.75)
            zf["farbe"] = Farbe.WEISS
        zeilen.append((text, af, zf))
    ed.ansicht._befehl(lambda: _bearbeiten.aenderung_titelblatt_einfuegen(ed.kennung, zeilen))


# ---- Text aus Datei ---------------------------------------------------------------------------------------------------------------
def text_aus_datei(ed, pfad: str) -> tuple[str, ...]:
    """Fügt den Inhalt einer Datei (DOCX, ODT, RTF, TXT …) an der Schreibmarke ein; → Hinweise über Nicht-Übernommenes. Eine Datei, die sich nicht
    lesen lässt, meldet ``Dateifehler`` (``writer.werte``)."""
    nummer, hinweise = _bearbeiten.fremdtext_laden(pfad)
    try:
        ed.ansicht._befehl(lambda: _bearbeiten.fremdtext_einfuegen(ed.kennung, nummer))
    finally:
        _bearbeiten.fremdtext_verwerfen(nummer)
    return hinweise


# ---- Datum und Uhrzeit ----------------------------------------------------------------------------------------------------------------
DATUMSFORMATE = ["dd.MM.yyyy", "dddd, d. MMMM yyyy", "d. MMMM yyyy", "dd.MM.yy", "yyyy-MM-dd", "d. MMM yy", "dd.MM.", "MMMM yy",
                 "MMM yy", "dd.MM.yyyy HH:mm", "dd.MM.yyyy HH:mm:ss", "HH:mm", "HH:mm:ss", "d. MMMM yyyy, HH:mm 'Uhr'"]


# Sprache → (Beschriftung, Formate) für das Fenster „Datum und Uhrzeit“
DATUM_SPRACHEN = {
    "de_DE": ("Deutsch (Deutschland)", DATUMSFORMATE),
    "de_AT": ("Deutsch (Österreich)", DATUMSFORMATE),
    "de_CH": ("Deutsch (Schweiz)", DATUMSFORMATE),
    "en_US": ("Englisch (USA)", ["M/d/yyyy", "dddd, MMMM d, yyyy", "MMMM d, yyyy", "M/d/yy", "yyyy-MM-dd", "d-MMM-yy", "M.d.yyyy",
                                 "MMM. d, yy", "d MMMM yyyy", "MMMM yy", "MMM-yy", "M/d/yyyy h:mm AP", "M/d/yyyy h:mm:ss AP", "h:mm AP",
                                 "h:mm:ss AP", "HH:mm"]),
    "en_GB": ("Englisch (Großbritannien)", ["dd/MM/yyyy", "dddd, d MMMM yyyy", "d MMMM yyyy", "dd/MM/yy", "yyyy-MM-dd", "d-MMM-yy",
                                            "dd.MM.yyyy", "d MMM. yy", "MMMM yy", "MMM-yy", "dd/MM/yyyy HH:mm", "dd/MM/yyyy HH:mm:ss",
                                            "HH:mm", "HH:mm:ss"]),
}


def datum_feldanweisung(fmt: str) -> str:
    """Qt-Datumsformat → DOCX-Feld (DATE, bei reinen Uhrzeiten TIME) für „Automatisch aktualisieren“."""
    bild = fmt.replace("AP", "AM/PM").replace('"', "'")
    art = "TIME" if not any(z in fmt for z in "dMy") else "DATE"
    return f'{art} \\@ "{bild}"'


def datum_text(fmt: str, sprache: str = "de_DE") -> str:
    from PySide6.QtCore import QDateTime, QLocale
    return QLocale(sprache).toString(QDateTime.currentDateTime(), fmt)


# ---- Initiale -------------------------------------------------------------------------------------------------------------------------------
def initiale(ed, zeilen: int = 3) -> bool:
    """Erster Buchstabe des Absatzes groß und fett (im Absatz, in der Zeile)."""
    a = _bearbeiten.dok_absatz_an_marke(ed.kennung)
    if not a.text().strip():
        return False
    pt = _bearbeiten.absatz_schriftgroesse(ed.kennung) * zeilen * 1.4
    return ed.ansicht._befehl(lambda: _bearbeiten.aenderung_zeichenformat_anwenden(ed.kennung, {"groesse_pt": pt, "fett": True}, ((a.id, 0), (a.id, 1))))


def textfeld(ed, text: str = "Text hier eingeben", breite: int = 50) -> None:
    """Ein Textfeld als einzellige Tabelle mit Rahmen."""
    form = {"rahmen_breite": 1.5, "rahmen_farbe": Farbe.FORM_LINIE, "rahmen_art": "einfach", "zellpolster": 8.0, "breite_art": "prozent", "breite": float(breite)}
    ed.ansicht._befehl(lambda: _bearbeiten.aenderung_textfeld_einfuegen(ed.kennung, text, form))
