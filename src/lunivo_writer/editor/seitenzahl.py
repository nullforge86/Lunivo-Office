"""Seitenzahlen in Kopf- oder Fußzeile setzen und entfernen (Einfügen ▸ Seitenzahl). Arbeitet auf ``PageSettings``; keine Oberfläche.

    seitenzahl_setzen(page, "fuss", "right", "Seite {PAGE} von {PAGES}")
    seitenzahlen_entfernen(page)
"""
from __future__ import annotations

import re

from lunivo_writer.models.page import HeaderFooter, PageSettings

# Muster → Beschriftung im Fenster „Seitenzahl einfügen“
MUSTER = [("{PAGE}", "1, 2, 3 …"), ("Seite {PAGE}", "Seite 1"), ("Seite {PAGE} von {PAGES}", "Seite 1 von 3"), ("- {PAGE} -", "- 1 -"),
          ("{PAGE} / {PAGES}", "1 / 3")]
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


def seitenzahl_setzen(page: PageSettings, ort: str, ausrichtung: str, muster: str = "{PAGE}") -> PageSettings:
    """Seitenzahl in Kopf- (``ort="kopf"``) oder Fußzeile setzen. Eine vorhandene Seitenzahl dort wird ersetzt, übriger Text bleibt;
    die Seitenzahl in der anderen Zeile wird entfernt, damit sie nicht doppelt erscheint."""
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
