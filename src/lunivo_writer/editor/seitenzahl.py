"""Seitenzahlen in Kopf- oder Fußzeile setzen und entfernen (Einfügen ▸ Seitenzahl). Arbeitet auf ``PageSettings``; keine Oberfläche.

    seitenzahl_setzen(page, "fuss", "right", "Seite {PAGE} von {PAGES}")
    seitenzahlen_entfernen(page)

Dazu, was beim Zeichnen aus {PAGE} wird: Zahlenart (``page.seiten_format``), Kapitelnummer davor (``page.kapitel_ebene``) und die
Ausrichtung „außen“/„innen“, die auf geraden und ungeraden Seiten wechselt:

    text(hf.text, n, gesamt, page, kapitel)      ausrichtung(hf.align, n)      kapitel_je_seite(doc, ebene, seitenwechsel(doc, ch))
"""
from __future__ import annotations

import re

from lunivo_writer.models.page import HeaderFooter, PageSettings

# Liste „Format“ im Fenster „Seitenzahl einfügen“: (Muster, Zahlenart, Beschriftung)
MUSTER = [("{PAGE}", "dezimal", "1, 2, 3 …"), ("- {PAGE} -", "dezimal", "-1-, -2-, -3- …"), ("{PAGE}", "klein", "a, b, c …"),
          ("{PAGE}", "gross", "A, B, C …"), ("{PAGE}", "roem_klein", "i, ii, iii …"), ("{PAGE}", "roem_gross", "I, II, III …"),
          ("Seite {PAGE}", "dezimal", "Seite 1"), ("Seite {PAGE} von {PAGES}", "dezimal", "Seite 1 von X"),
          ("{PAGE} / {PAGES}", "dezimal", "1 / X")]
# Liste „Position“: (Ort, Ausrichtung, Beschriftung)
POSITIONEN = [("kopf", "left", "Oben links"), ("kopf", "center", "Oben zentriert"), ("kopf", "right", "Oben rechts"),
              ("kopf", "aussen", "Oben außen"), ("kopf", "innen", "Oben innen"),
              ("fuss", "left", "Unten links"), ("fuss", "center", "Unten zentriert"), ("fuss", "right", "Unten rechts"),
              ("fuss", "aussen", "Unten außen"), ("fuss", "innen", "Unten innen")]
# Trennzeichen zwischen Kapitel- und Seitennummer: (Zeichen, Beschriftung, DOCX w:chapSep)
TRENNER = [("-", "- (Bindestrich)", "hyphen"), (".", ". (Punkt)", "period"), (":", ": (Doppelpunkt)", "colon"),
           ("—", "— (Geviertstrich)", "emDash"), ("–", "– (Halbgeviertstrich)", "enDash")]
# Zahlenart ↔ DOCX w:fmt
DOCX_FORMAT = {"dezimal": "decimal", "klein": "lowerLetter", "gross": "upperLetter", "roem_klein": "lowerRoman", "roem_gross": "upperRoman"}
# Die Galerie wie in der Vorlage: (Schlüssel, Beschriftung, Ort, Ausrichtung); innen/außen braucht gerade/ungerade Seiten
VORGABEN = [("kopf_links", "Kopfzeile links", "kopf", "left"), ("kopf_mitte", "Kopfzeile Mitte", "kopf", "center"),
            ("kopf_rechts", "Kopfzeile rechts", "kopf", "right"), ("kopf_aussen", "Kopfzeile außen", "kopf", "aussen"),
            ("kopf_innen", "Kopfzeile innen", "kopf", "innen"),
            ("fuss_links", "Fußzeile links", "fuss", "left"), ("fuss_mitte", "Fußzeile Mitte", "fuss", "center"),
            ("fuss_rechts", "Fußzeile rechts", "fuss", "right"), ("fuss_aussen", "Fußzeile außen", "fuss", "aussen"),
            ("fuss_innen", "Fußzeile innen", "fuss", "innen")]
_REST = re.compile(r"(Seite\s*)?\{PAGE\}(\s*(von|/)\s*\{PAGES\})?|-\s*\{PAGE\}\s*-")


def _ohne_zahl(text: str) -> str:
    return re.sub(r"\s{2,}", " ", _REST.sub("", text)).strip()


def seitenzahl_setzen(page: PageSettings, ort: str, ausrichtung: str, muster: str = "{PAGE}", format: str | None = None,
                      start: int | None = None, kapitel: tuple[int, str] | None = None) -> PageSettings:
    """Seitenzahl in Kopf- (``ort="kopf"``) oder Fußzeile setzen. Eine vorhandene Seitenzahl dort wird ersetzt, übriger Text bleibt;
    die Seitenzahl in der anderen Zeile wird entfernt, damit sie nicht doppelt erscheint. ``format`` (Zahlenart), ``start`` (0 = fortsetzen)
    und ``kapitel`` ((Ebene, Trennzeichen); Ebene 0 = keine Kapitelnummer) werden nur gesetzt, wenn angegeben."""
    if format is not None:
        page.seiten_format = format
    if start is not None:
        page.seiten_start = max(0, int(start))
    if kapitel is not None:
        page.kapitel_ebene, page.kapitel_trenner = int(kapitel[0]), kapitel[1]
    ziel, andere = ("header", "footer") if ort == "kopf" else ("footer", "header")
    alt = getattr(page, ziel)
    rest = _ohne_zahl(alt.text)
    setattr(page, ziel, HeaderFooter((rest + " " + muster).strip() if rest else muster, ausrichtung))
    zweite = getattr(page, andere)
    if "{PAGE}" in zweite.text:
        setattr(page, andere, HeaderFooter(_ohne_zahl(zweite.text), zweite.align))
    return page


def seitenzahlen_entfernen(page: PageSettings) -> bool:
    """Seitenzahl (mit „Seite … von …“) aus Kopf- und Fußzeile entfernen. → ob es eine gab."""
    gab = False
    for feld in ("header", "footer", "first_header", "first_footer"):
        hf = getattr(page, feld)
        if "{PAGE" in hf.text:
            setattr(page, feld, HeaderFooter(_ohne_zahl(hf.text).replace("{PAGES}", "").strip(), hf.align))
            gab = True
    return gab


def seitenzahl_loeschen_bereich(page: PageSettings, art: str, blatt: int = 0) -> bool | None:
    """Seitenzahl nur auf einem Teil der Seiten eines Abschnitts entfernen (Seitenzahl löschen ▾ in der Kopf-/Fußzeilenleiste).
    ``art``: "aktuelle" (nur Blatt ``blatt``), "auf" (bis einschließlich), "von" (ab dem Blatt), "abschnitt" (alle). ``blatt`` ist 0-basiert.
    Darstellbar ist, was „Erste Seite anders“ trägt: die erste Seite getrennt von den übrigen. → True: geändert, False: gab keine
    Seitenzahl, None: so nicht darstellbar."""
    if art == "abschnitt" or (art == "von" and blatt == 0):
        return seitenzahlen_entfernen(page)
    if blatt == 0 and art in ("aktuelle", "auf"):
        erste_hat = "{PAGE" in (page.first_header.text + page.first_footer.text) if page.diff_first else "{PAGE" in (page.header.text + page.footer.text)
        if not page.diff_first:
            page.first_header = HeaderFooter(page.header.text, page.header.align)
            page.first_footer = HeaderFooter(page.footer.text, page.footer.align)
            page.diff_first = True
        for feld in ("first_header", "first_footer"):
            hf = getattr(page, feld)
            if "{PAGE" in hf.text:
                setattr(page, feld, HeaderFooter(_ohne_zahl(hf.text).replace("{PAGES}", "").strip(), hf.align))
        return erste_hat
    if art == "von" and blatt == 1:                            # alle außer der ersten Seite
        hatte = any("{PAGE" in getattr(page, f).text for f in ("header", "footer"))
        if not page.diff_first:
            page.first_header = HeaderFooter(page.header.text, page.header.align)
            page.first_footer = HeaderFooter(page.footer.text, page.footer.align)
            page.diff_first = True
        for feld in ("header", "footer"):
            hf = getattr(page, feld)
            if "{PAGE" in hf.text:
                setattr(page, feld, HeaderFooter(_ohne_zahl(hf.text).replace("{PAGES}", "").strip(), hf.align))
        return hatte
    return None


# ---- beim Zeichnen ---------------------------------------------------------------------------------------------------
def nummer(n: int, page: PageSettings | None = None, kapitel: str = "") -> str:
    """Die Seitennummer ``n`` in der Zahlenart der Einrichtung, mit Kapitelnummer davor („2-1“)."""
    from lunivo_writer.editor.mehrstufig import nummer_text
    z = nummer_text(page.seiten_format, n) if page is not None and n > 0 else str(n)
    if kapitel and page is not None and page.kapitel_ebene:
        return f"{kapitel}{page.kapitel_trenner}{z}"
    return z


def text(vorlage: str, n: int, gesamt: int, page: PageSettings | None = None, kapitel: str = "") -> str:
    return vorlage.replace("{PAGES}", str(gesamt)).replace("{PAGE}", nummer(n, page, kapitel))


def ausrichtung(align: str, n: int) -> str:
    """„außen“: ungerade (rechte) Seiten rechts, gerade links; „innen“ umgekehrt. Andere Werte bleiben."""
    if align == "aussen":
        return "right" if n % 2 else "left"
    if align == "innen":
        return "left" if n % 2 else "right"
    return align


def erste_nummer(page: PageSettings) -> int:
    """Nummer der ersten Seite eines Abschnitts, wenn er nicht fortsetzt (sonst 1)."""
    return page.seiten_start if page.seiten_start > 0 else 1


def seitenwechsel(d, seitenhoehe: float) -> list[int]:
    """Zeichenstellen, an denen eine neue Seite beginnt (erste Zeile der Seiten 2, 3, …), nach der Höhe einer Seite im Layout."""
    lay = d.documentLayout()
    stellen, seite = [], 0
    b = d.firstBlock()
    while b.isValid():
        tl = b.layout()
        if tl is not None and tl.lineCount():
            top = lay.blockBoundingRect(b).top()
            for i in range(tl.lineCount()):
                ln = tl.lineAt(i)
                k = int((top + ln.y() + 0.5) // seitenhoehe)
                if k > seite:
                    seite = k
                    stellen.append(b.position() + ln.textStart())
        b = b.next()
    return stellen


def _kapitel_nummer(b, mehr: dict) -> str:
    if b.blockNumber() in mehr:
        t = mehr[b.blockNumber()]
    else:
        lst = b.textList()
        t = lst.itemText(b) if lst is not None else ""
    return t.strip().rstrip(".").strip()


def kapitel_je_seite(d, ebene: int, wechsel: list[int]) -> list[str]:
    """Kapitelnummer jeder Seite (Index 0 = Seite 1): die Nummer der letzten Überschrift der Ebene ``ebene``, die auf der Seite oder
    davor beginnt. Ohne solche Überschrift bleibt sie leer."""
    from lunivo_writer.editor.mehrstufig import nummern
    mehr = {b.blockNumber(): t for b, t, _n, _e in nummern(d)}
    out, aktuell, k = [], "", 0
    grenzen = list(wechsel) + [d.characterCount() + 1]
    b = d.firstBlock()
    while b.isValid():
        while b.position() >= grenzen[k]:
            out.append(aktuell); k += 1
        if b.blockFormat().headingLevel() == ebene and b.text().strip():
            aktuell = _kapitel_nummer(b, mehr)
        b = b.next()
    while len(out) < len(grenzen):
        out.append(aktuell)
    return out
