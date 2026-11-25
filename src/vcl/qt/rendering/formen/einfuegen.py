from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from core.dokument.dokument import Auswahl, Position
from core.layout.drucklayout import formatwerte as F
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

    def f(s):
        with s.gruppe("Deckblatt"):
            anfang = s.dokument.anfang()
            texte = [t[0] for t in teile]
            s.text_einfuegen("\n".join(texte) + "\n\n", anfang)
            absaetze = list(s.dokument.absaetze())
            for (text, pt, fett, abstand), a in zip(teile, absaetze):
                af = {"abstand_vor": abstand / 0.75, "ausrichtung": "mitte" if zentriert else "links"}
                zf = {"groesse_pt": float(pt), "fett": True if fett else None}
                if vorlage == "Farbband" and fett:                  # Titel weiß auf farbigem Band über die ganze Breite
                    af.update(hintergrund=Farbe.AKZENT, abstand_nach=18 / 0.75)
                    zf["farbe"] = Farbe.WEISS
                s.absatzformat_anwenden(af, absatz_ids=[a.id])
                if a.laenge:
                    s.zeichenformat_anwenden(zf, Auswahl(Position(a.id, 0), Position(a.id, a.laenge)))
                s.absatz_zeichenformat_anwenden(zf, absatz_ids=[a.id])
            s.absatzformat_anwenden({"seitenumbruch_nach": True}, absatz_ids=[absaetze[len(teile)].id])
            s.setze_auswahl(Position(absaetze[len(teile)].id, 0))
    ed.ansicht._aendern(f)


# ---- Text aus Datei ---------------------------------------------------------------------------------------------------------------
def _fremde_bloecke(s, fremd) -> list:
    """Die Blöcke des Haupttextes eines geladenen Dokuments für die Sitzung ``s``: Listen werden angelegt, Bilddaten unter neuen Namen abgelegt."""
    import copy
    from core.dokument.dokument import Absatz, InlineObjekt, Rahmen, Tabelle
    bloecke = copy.deepcopy([b for a in fremd.abschnitte for b in a.bloecke])
    listen: dict = {}
    namen: dict = {}

    def absatz(a):
        if a.liste_id is not None:
            if a.liste_id not in listen:
                d = fremd.listen.get(a.liste_id)
                listen[a.liste_id] = s.liste_anlegen(copy.deepcopy(d.ebenen)) if d is not None and d.ebenen else None
            a.liste_id = listen[a.liste_id]
        for x in a.inhalte:
            if isinstance(x, InlineObjekt) and x.ressource and x.ressource in fremd.ressourcen:
                if x.ressource not in namen:
                    namen[x.ressource] = f"import-{len(s.dokument.ressourcen) + len(namen) + 1}-{x.ressource}"
                    s.ressource_setzen(namen[x.ressource], fremd.ressourcen[x.ressource])
                x.ressource = namen[x.ressource]

    def lauf(liste):
        for b in liste:
            if isinstance(b, Absatz):
                absatz(b)
            elif isinstance(b, Tabelle):
                for zeile in b.zellen:
                    for z in zeile:
                        lauf(z.bloecke)
            elif isinstance(b, Rahmen):
                lauf(b.bloecke)
    lauf(bloecke)
    return bloecke


def text_aus_datei(ed, pfad: str):
    """Fügt den Inhalt einer Datei (DOCX, ODT, RTF, TXT …) an der Schreibmarke ein; → Bericht über Nicht-Übernommenes."""
    from framework.dokumentverwaltung.dateizugriff.modell_laden import lade_modell
    geladen = lade_modell(pfad)

    def f(s):
        with s.gruppe("Text aus Datei"):
            s.ausschnitt_einfuegen(_fremde_bloecke(s, geladen.document))
    ed.ansicht._aendern(f)
    return geladen.report


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
    s = ed.sitzung
    a = s._absatz(s.auswahl.kopf.absatz_id)
    if not a.text.strip():
        return False
    pt = float(F.zeichenformat(s.dokument, a, {}).get("groesse_pt") or 11.0) * zeilen * 1.4
    return ed.ansicht._aendern(lambda sitz: sitz.zeichenformat_anwenden({"groesse_pt": pt, "fett": True}, Auswahl(Position(a.id, 0), Position(a.id, 1))))


def textfeld(ed, text: str = "Text hier eingeben", breite: int = 50) -> None:
    """Ein Textfeld als einzellige Tabelle mit Rahmen."""
    def f(sitz):
        with sitz.gruppe("Textfeld"):
            tid = sitz.tabelle_einfuegen(1, 1, format={"rahmen_breite": 1.5, "rahmen_farbe": Farbe.FORM_LINIE, "rahmen_art": "einfach", "zellpolster": 8.0,
                                                       "breite_art": "prozent", "breite": float(breite)})
            sitz.text_einfuegen(text, sitz.zelle_anfang(tid, 0, 0))
    ed.ansicht._aendern(f)
