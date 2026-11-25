"""Freie Objekte (Textfeld, WordArt, Form, Bild): Vorgaben neuer Objekte, Verknüpfung von Textfeldern und die Angaben, die gespeichert werden. Die
Fachdaten liegen im Kern; die Oberfläche erhält unveränderliche Werte."""
from __future__ import annotations

from core.objekte.formen import frei_objekt_daten as verknuepfung
from core.objekte.formen import freie_bilder_daten as angaben
from core.objekte.textfelder.modell import frei_objekt_text_daten as modell
from framework.befehle import lesen
from framework.schnittstellen.datentypen.objektdaten import TextfeldVorgabe, WordartVorgabe

TEXTFELD_STANDARD: TextfeldVorgabe = TextfeldVorgabe(text=modell.TEXTFELD_STANDARD["text"], schrift=modell.TEXTFELD_STANDARD["schrift"],
                                                     pt=modell.TEXTFELD_STANDARD["pt"], farbe=modell.TEXTFELD_STANDARD["farbe"])
WORDART_STANDARD: WordartVorgabe = WordartVorgabe(text=modell.WORDART_STANDARD["text"], vorlage=modell.WORDART_STANDARD["vorlage"],
                                                  pt=modell.WORDART_STANDARD["pt"], schrift=modell.WORDART_STANDARD["schrift"])


def ist_verknuepft(kennung: int, schluessel: tuple[str, int]) -> bool:
    """Gehört das Textfeld ``schluessel`` zu einer Kette verknüpfter Textfelder (hat es einen Vorgänger oder einen Nachfolger)?"""
    return bool(lesen(kennung, lambda s: int(verknuepfung.ist_verknuepft(s.dokument, schluessel))))


def hat_nachfolger(kennung: int, schluessel: tuple[str, int]) -> bool:
    """Fließt der Text des Textfelds ``schluessel`` in ein nächstes Feld weiter?"""
    return bool(lesen(kennung, lambda s: int(verknuepfung.hat_nachfolger(s.dokument, schluessel))))


def ohne_hilfsangaben(schluessel: tuple[str, ...]) -> tuple[str, ...]:
    """Von den Schlüsseln der Angabe eines freien Objekts die, die gespeichert werden (Hilfsangaben der Anzeige entfallen)."""
    return tuple(angaben.ohne_hilfsangaben(dict.fromkeys(schluessel)))
