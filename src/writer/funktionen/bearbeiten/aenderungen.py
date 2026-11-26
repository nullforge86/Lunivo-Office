"""Änderungen am Dokument für die Oberfläche: ordnet jede Bedienaktion ihrem Framework-Befehl zu (ein Schritt für Rückgängig; ``False`` oder
``None``, wenn der Kern ablehnt). Stellen sind ``(Absatz-Id, Zeichenstelle)``, Bereiche ``(Anker, Kopf)``."""
from __future__ import annotations

from framework.befehle import bearbeiten as _befehle


def aenderung_text_einfuegen(kennung, text, format=None):
    """Text an der Auswahl einfügen (ersetzt sie); ``format``: Zeichenformat des Textes."""
    return _befehle.aenderung_text_einfuegen(kennung, text, format)


def aenderung_loeschen(kennung, bereich=None):
    """Die Auswahl (oder den Bereich) löschen."""
    return _befehle.aenderung_loeschen(kennung, bereich)


def aenderung_loeschen_bis(kennung, ziel):
    """Von der Schreibmarke bis ``ziel`` löschen."""
    return _befehle.aenderung_loeschen_bis(kennung, ziel)


def aenderung_loeschen_von(kennung, anfang):
    """Von ``anfang`` bis zur Schreibmarke löschen."""
    return _befehle.aenderung_loeschen_von(kennung, anfang)


def aenderung_zeichen_loeschen(kennung, vorwaerts=False):
    return _befehle.aenderung_zeichen_loeschen(kennung, vorwaerts)


def aenderung_ersetzen(kennung, text):
    """Die Auswahl durch ``text`` ersetzen."""
    return _befehle.aenderung_ersetzen(kennung, text)


def aenderung_fundstelle_ersetzen(kennung, von, bis, neu, zeichen=None, absatz=None, vorlage=None):
    """Den Rohtext-Bereich durch ``neu`` ersetzen (mit Zeichen-/Absatzformat) und dem Absatz danach die Formatvorlage geben."""
    return _befehle.aenderung_fundstelle_ersetzen(kennung, von, bis, neu, zeichen, absatz, vorlage)


def aenderung_ersetzen_verfolgt(kennung, von, bis, neu, autor=''):
    """Den Rohtext-Bereich als nachverfolgte Änderung des Bearbeiters ``autor`` ersetzen."""
    return _befehle.aenderung_ersetzen_verfolgt(kennung, von, bis, neu, autor)


def aenderung_markdown_ersetzen(kennung, von, bis, bloecke, anfang):
    """Den Rohtext-Bereich durch die Blöcke eines Markdown-Textes ersetzen (je Block Text, Vorlage, Liste, formatierte Läufe)."""
    return _befehle.aenderung_markdown_ersetzen(kennung, von, bis, bloecke, anfang)


def aenderung_feld_einfuegen(kennung, anweisung, ergebnis, format=None):
    return _befehle.aenderung_feld_einfuegen(kennung, anweisung, ergebnis, format)


def aenderung_link_setzen(kennung, ziel, text=None, tipp=''):
    """Verknüpfung auf die Auswahl; ohne Auswahl und mit ``text`` wird der Text eingefügt, sonst gilt sie für das Wort an der Schreibmarke."""
    return _befehle.aenderung_link_setzen(kennung, ziel, text, tipp)


def aenderung_leittext_setzen(kennung, teile):
    """Phonetisches Leitzeichen: die Auswahl durch die Textstücke mit ihrem Leittext ersetzen; je Stück (Basis, Leittext, Ausrichtung/Abstand/Größe)."""
    return _befehle.aenderung_leittext_setzen(kennung, teile)


def aenderung_zeichenformat_anwenden(kennung, aenderung, bereich=None, ersetzen=False):
    return _befehle.aenderung_zeichenformat_anwenden(kennung, aenderung, bereich, ersetzen)


def aenderung_absatzformat_anwenden(kennung, aenderung, absatz_ids=None, ersetzen=False):
    return _befehle.aenderung_absatzformat_anwenden(kennung, aenderung, absatz_ids, ersetzen)


def aenderung_format_uebertragen(kennung, zeichen, absatz):
    """Das aufgenommene Format auf die Auswahl legen (Zeichen) – bei leerer Auswahl auch auf den Absatz."""
    return _befehle.aenderung_format_uebertragen(kennung, zeichen, absatz)


def aenderung_design_anwenden(kennung, text_schrift, kopf_schrift, farbe):
    """Dokumentdesign: Schrift des Fließtextes, Schrift und Farbe der Überschriften – über die Formatvorlagen des Dokuments."""
    return _befehle.aenderung_design_anwenden(kennung, text_schrift, kopf_schrift, farbe)


def aenderung_vorlage_loeschen(kennung, name):
    return _befehle.aenderung_vorlage_loeschen(kennung, name)


def aenderung_umbruch_einfuegen(kennung, art):
    """Den Absatz an der Schreibmarke teilen und davor umbrechen; ``art``: ``seite`` oder ``spalte``."""
    return _befehle.aenderung_umbruch_einfuegen(kennung, art)


def aenderung_absaetze_umstellen(kennung, absatz_ids, ordnung):
    return _befehle.aenderung_absaetze_umstellen(kennung, absatz_ids, ordnung)


def aenderung_eigenschaft_setzen(kennung, name, wert=None):
    """Eine Eigenschaft des Dokuments (zum Beispiel ``tab_abstand``, ``zitierweise``)."""
    return _befehle.aenderung_eigenschaft_setzen(kennung, name, wert)


def aenderung_liste_entfernen(kennung):
    return _befehle.aenderung_liste_entfernen(kennung)


def aenderung_liste_anlegen_anwenden(kennung, ebenen):
    """Eine neue Liste anlegen und auf die Auswahl legen."""
    return _befehle.aenderung_liste_anlegen_anwenden(kennung, ebenen)


def aenderung_liste_neu_beginnen(kennung, absatz_id, start=1):
    return _befehle.aenderung_liste_neu_beginnen(kennung, absatz_id, start)


def aenderung_listenebene_aendern(kennung, schritte):
    return _befehle.aenderung_listenebene_aendern(kennung, schritte)


def aenderung_tabelle_einfuegen(kennung, zeilen, spalten, format=None, stelle=None):
    """Eine Tabelle einfügen; mit ``stelle`` steht die Schreibmarke vorher dort (Tabelle zeichnen)."""
    return _befehle.aenderung_tabelle_einfuegen(kennung, zeilen, spalten, format, stelle)


def aenderung_textfeld_einfuegen(kennung, text, format):
    """Ein Textfeld als einzellige Tabelle mit dem Tabellenformat ``format`` und dem Text darin."""
    return _befehle.aenderung_textfeld_einfuegen(kennung, text, format)


def aenderung_text_zu_tabelle(kennung, trenner, spalten):
    return _befehle.aenderung_text_zu_tabelle(kennung, trenner, spalten)


def aenderung_tabelle_zu_text(kennung, tabellen_id, trenner, geschachtelt):
    return _befehle.aenderung_tabelle_zu_text(kennung, tabellen_id, trenner, geschachtelt)


def aenderung_tabelle_loeschen(kennung, tabellen_id):
    return _befehle.aenderung_tabelle_loeschen(kennung, tabellen_id)


def aenderung_tabelle_sortieren(kennung, tabellen_id, spalte, aufsteigend=True):
    return _befehle.aenderung_tabelle_sortieren(kennung, tabellen_id, spalte, aufsteigend)


def aenderung_tabelle_frei_setzen(kennung, tabellen_id, x, y, vor_absatz_id=None):
    """Die Tabelle frei platzieren (obere linke Ecke ab der oberen linken Ecke des Satzspiegels); ihr Anker wandert vor den Absatz ``vor_absatz_id``."""
    return _befehle.aenderung_tabelle_frei_setzen(kennung, tabellen_id, x, y, vor_absatz_id)


def aenderung_tabelle_skalieren(kennung, tabellen_id, faktor_breite, faktor_hoehe, breiten=(), hoehen=()):
    return _befehle.aenderung_tabelle_skalieren(kennung, tabellen_id, faktor_breite, faktor_hoehe, breiten, hoehen)


def aenderung_tabellenformat_anwenden(kennung, tabellen_id, aenderung):
    return _befehle.aenderung_tabellenformat_anwenden(kennung, tabellen_id, aenderung)


def aenderung_zellformat_anwenden(kennung, tabellen_id, aenderung, zellen=None):
    return _befehle.aenderung_zellformat_anwenden(kennung, tabellen_id, aenderung, zellen)


def aenderung_zell_richtung(kennung, tabellen_id, zellen, absatz_ids, richtung):
    """Textrichtung der Zellen und ihrer Absätze."""
    return _befehle.aenderung_zell_richtung(kennung, tabellen_id, zellen, absatz_ids, richtung)


def aenderung_spaltenbreiten_setzen(kennung, tabellen_id, breiten):
    return _befehle.aenderung_spaltenbreiten_setzen(kennung, tabellen_id, breiten)


def aenderung_zeilenhoehen_setzen(kennung, tabellen_id, hoehen):
    """Zeilenhöhen: Zeilenindex → Höhe."""
    return _befehle.aenderung_zeilenhoehen_setzen(kennung, tabellen_id, hoehen)


def aenderung_zeilen_gleich(kennung, tabellen_id, hoehe):
    return _befehle.aenderung_zeilen_gleich(kennung, tabellen_id, hoehe)


def aenderung_tabelle_an_inhalt(kennung, tabellen_id, spalten, zeilen):
    """„An Inhalt anpassen“: Spaltenbreiten und Zeilenhöhen frei, Tabellenbreite automatisch."""
    return _befehle.aenderung_tabelle_an_inhalt(kennung, tabellen_id, spalten, zeilen)


def aenderung_tabelle_an_fenster(kennung, tabellen_id, spalten, breite):
    """„An Fenster anpassen“: gleich breite Spalten über die ganze Satzbreite ``breite``."""
    return _befehle.aenderung_tabelle_an_fenster(kennung, tabellen_id, spalten, breite)


def aenderung_zeilen_einfuegen(kennung, tabellen_id, index, anzahl=1):
    return _befehle.aenderung_zeilen_einfuegen(kennung, tabellen_id, index, anzahl)


def aenderung_spalten_einfuegen(kennung, tabellen_id, index):
    return _befehle.aenderung_spalten_einfuegen(kennung, tabellen_id, index)


def aenderung_zeilen_loeschen(kennung, tabellen_id, index):
    return _befehle.aenderung_zeilen_loeschen(kennung, tabellen_id, index)


def aenderung_spalten_loeschen(kennung, tabellen_id, index):
    return _befehle.aenderung_spalten_loeschen(kennung, tabellen_id, index)


def aenderung_zellen_verbinden(kennung, tabellen_id, zeile, spalte, zeilen, spalten):
    return _befehle.aenderung_zellen_verbinden(kennung, tabellen_id, zeile, spalte, zeilen, spalten)


def aenderung_zelle_teilen(kennung, tabellen_id, zeile, spalte, zeilen=1, spalten=1):
    return _befehle.aenderung_zelle_teilen(kennung, tabellen_id, zeile, spalte, zeilen, spalten)


def aenderung_tabellenvorlage_anwenden(kennung, tabellen_id, name, kopf, streifen, spalte, rahmenfarbe):
    """Eine Tabellenvorlage (Füllungen, Fettdruck, Rahmen) auf die Zellen anwenden; die Optionen bleiben an der Tabelle gespeichert."""
    return _befehle.aenderung_tabellenvorlage_anwenden(kennung, tabellen_id, name, kopf, streifen, spalte, rahmenfarbe)


def aenderung_objekt_einfuegen(kennung, art, breite, hoehe, bilddaten=None, daten=None, alt_text=''):
    """Ein Objekt im Text an der Schreibmarke einfügen."""
    return _befehle.aenderung_objekt_einfuegen(kennung, art, breite, hoehe, bilddaten, daten, alt_text)


def aenderung_objekt_frei_einfuegen(kennung, art, breite, hoehe, bilddaten, daten, alt_text=''):
    """Ein frei positioniertes Objekt am Absatz der Schreibmarke anlegen; → seine Id."""
    return _befehle.aenderung_objekt_frei_einfuegen(kennung, art, breite, hoehe, bilddaten, daten, alt_text)


def aenderung_objekt_aendern(kennung, objekt_id, **felder):
    return _befehle.aenderung_objekt_aendern(kennung, objekt_id, **felder)


def aenderung_inline_aendern(kennung, objekt_id, ressourcen, felder):
    """Ein Objekt im Text ändern; neue Bilder (``ressourcen``) kommen im selben Schritt ins Dokument."""
    return _befehle.aenderung_inline_aendern(kennung, objekt_id, ressourcen, felder)


def aenderung_objekt_entfernen(kennung, objekt_id):
    return _befehle.aenderung_objekt_entfernen(kennung, objekt_id)


def aenderung_objekt_ebene(kennung, objekt_id, wohin):
    return _befehle.aenderung_objekt_ebene(kennung, objekt_id, wohin)


def aenderung_objekt_zu_inline(kennung, objekt_id):
    return _befehle.aenderung_objekt_zu_inline(kennung, objekt_id)


def aenderung_objekt_zu_frei(kennung, objekt_id, umbruch):
    return _befehle.aenderung_objekt_zu_frei(kennung, objekt_id, umbruch)


def aenderung_kommentar_einfuegen(kennung, text, autor='', initialen=''):
    return _befehle.aenderung_kommentar_einfuegen(kennung, text, autor, initialen)


def aenderung_kommentar_aendern(kennung, kommentar_id, text=None, geloest=None):
    return _befehle.aenderung_kommentar_aendern(kennung, kommentar_id, text, geloest)


def aenderung_kommentar_loeschen(kennung, kommentar_id=None):
    return _befehle.aenderung_kommentar_loeschen(kennung, kommentar_id)


def aenderung_aenderungen_entscheiden(kennung, annehmen, bereich=None):
    """Nachverfolgte Änderungen im Bereich (ohne Angabe: alle) annehmen oder ablehnen."""
    return _befehle.aenderung_aenderungen_entscheiden(kennung, annehmen, bereich)


def aenderung_note_einfuegen(kennung, text, art='f'):
    return _befehle.aenderung_note_einfuegen(kennung, text, art)


def aenderung_note_aendern(kennung, art, note_id, text):
    return _befehle.aenderung_note_aendern(kennung, art, note_id, text)


def aenderung_note_loeschen(kennung, art, note_id):
    return _befehle.aenderung_note_loeschen(kennung, art, note_id)


def aenderung_beschriftungen_nummerieren(kennung):
    return _befehle.aenderung_beschriftungen_nummerieren(kennung)


def aenderung_quelle_setzen(kennung, quelle):
    return _befehle.aenderung_quelle_setzen(kennung, quelle)


def aenderung_quelle_loeschen(kennung, tag):
    return _befehle.aenderung_quelle_loeschen(kennung, tag)


def aenderung_abschnitt_einfuegen(kennung, beginn='naechste'):
    """Einen Abschnittswechsel an der Schreibmarke einfügen; → Nummer des neuen Abschnitts."""
    return _befehle.aenderung_abschnitt_einfuegen(kennung, beginn)


def aenderung_abschnitt_entfernen(kennung, index, behalte='vorher'):
    return _befehle.aenderung_abschnitt_entfernen(kennung, index, behalte)


def aenderung_abschnitt_beginn_setzen(kennung, index, beginn):
    return _befehle.aenderung_abschnitt_beginn_setzen(kennung, index, beginn)


def aenderung_seite_ersetzen(kennung, index, einrichtung):
    """Die Seiteneinrichtung des Abschnitts ganz ersetzen; ``einrichtung``: ihre Felder als Wörterbuch (Kopf- und Fußzeilen ebenfalls als Wörterbuch)."""
    return _befehle.aenderung_seite_ersetzen(kennung, index, einrichtung)


def aenderung_seite_setzen(kennung, index, **felder):
    """Einzelne Felder der Seiteneinrichtung des Abschnitts setzen."""
    return _befehle.aenderung_seite_setzen(kennung, index, **felder)


def aenderung_leere_seite(kennung, letzter_absatz, blatt, einrichtung):
    return _befehle.aenderung_leere_seite(kennung, letzter_absatz, blatt, einrichtung)


def aenderung_titelblatt_einfuegen(kennung, teile):
    """Ein einfaches Deckblatt an den Anfang setzen: je Zeile (Text, Absatzformat, Zeichenformat); danach beginnt der Text auf einer neuen Seite."""
    return _befehle.aenderung_titelblatt_einfuegen(kennung, teile)


def aenderung_deckblatt_einfuegen(kennung, felder, deck, rest):
    return _befehle.aenderung_deckblatt_einfuegen(kennung, felder, deck, rest)
