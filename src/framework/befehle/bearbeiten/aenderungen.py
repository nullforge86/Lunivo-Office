"""Änderungen am Dokument als Befehle anhand der Kennung: Text, Format, Listen, Tabellen, Objekte, Kommentare, Noten, Abschnitte.

Jeder Befehl ist ein Schritt für Rückgängig und gibt ``False`` zurück, wenn der Kern die Änderung ablehnt (das Dokument bleibt dann unverändert).
Befehle, die etwas Neues anlegen, geben dessen Nummer zurück und ``None`` bei Ablehnung. Stellen sind ``(Absatz-Id, Zeichenstelle)``,
Bereiche ``(Anker, Kopf)``."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

from framework.anbindung import Daten
from framework.sitzungen import sitzung as _steuerung

Stelle = tuple[int, int]
Bereich = tuple[Stelle, Stelle]
ZEICHEN_DER_PROBE = ("schrift", "groesse_pt", "fett", "kursiv", "unterstrichen", "durchgestrichen", "farbe", "marker", "hoch_tief", "kapitaelchen",
                     "grossbuchstaben", "zeichenabstand", "effekt")
KOPF_FUSS = ("header", "footer", "first_header", "first_footer", "even_header", "even_footer")


def _sitzung(kennung: int):
    return _steuerung._sitzungen[kennung].sitzung


def _tun(kennung: int, tat) -> bool:
    from core.bearbeitung import BearbeitungsFehler
    try:
        tat(_sitzung(kennung))
    except BearbeitungsFehler:
        return False
    return True


def _wert(kennung: int, tat):
    from core.bearbeitung import BearbeitungsFehler
    try:
        return tat(_sitzung(kennung))
    except BearbeitungsFehler:
        return None


def _d(m):
    return None if m is None else dict(m)


def _l(folge):
    return None if folge is None else list(folge)


def _auswahl(b):
    from core.dokument import Auswahl, Position
    return None if b is None else Auswahl(Position(*b[0]), Position(*b[1]))


def _stelle(st):
    from core.dokument import Position
    return None if st is None else Position(*st)


def _seite(felder: Mapping):
    from core.dokument.abschnitte import HeaderFooter, PageSettings
    return PageSettings(**{k: HeaderFooter(**v) if k in KOPF_FUSS and isinstance(v, Mapping) else v for k, v in felder.items()})


# ---- Text ------------------------------------------------------------------------------------------------------------------------------------------
def text_einfuegen(kennung: int, text: str, format: Mapping[str, Daten] | None = None) -> bool:
    """Text an der Auswahl einfügen (ersetzt sie); ``format``: Zeichenformat des Textes."""
    return _tun(kennung, lambda s: s.text_einfuegen(text, format=_d(format)))


def loeschen(kennung: int, bereich: Bereich | None = None) -> bool:
    """Die Auswahl (oder den Bereich) löschen."""
    return _tun(kennung, lambda s: s.loeschen(_auswahl(bereich)))


def loeschen_bis(kennung: int, ziel: Stelle) -> bool:
    """Von der Schreibmarke bis ``ziel`` löschen."""
    from core.dokument import Auswahl
    return _tun(kennung, lambda s: s.loeschen(Auswahl(s.auswahl.kopf, _stelle(ziel))))


def loeschen_von(kennung: int, anfang: Stelle) -> bool:
    """Von ``anfang`` bis zur Schreibmarke löschen."""
    from core.dokument import Auswahl
    return _tun(kennung, lambda s: s.loeschen(Auswahl(_stelle(anfang), s.auswahl.kopf)))


def zeichen_loeschen(kennung: int, vorwaerts: bool = False) -> bool:
    return _tun(kennung, lambda s: s.zeichen_loeschen(vorwaerts=vorwaerts))


def ersetzen(kennung: int, text: str) -> bool:
    """Die Auswahl durch ``text`` ersetzen."""
    return _tun(kennung, lambda s: s.ersetzen(text))


def fundstelle_ersetzen(kennung: int, von: int, bis: int, neu: str, zeichen: Mapping[str, Daten] | None = None, absatz: Mapping[str, Daten] | None = None,
                        vorlage: str | None = None) -> bool:
    """Den Rohtext-Bereich durch ``neu`` ersetzen (mit Zeichen-/Absatzformat) und dem Absatz danach die Formatvorlage geben."""
    def tat(s):
        with s.gruppe("Ersetzen"):
            ende = s.ersetzen_durch(von, bis, neu, _d(zeichen), _d(absatz))
            if vorlage:
                s.vorlage_anwenden("Standard" if vorlage == "Fließtext" else vorlage, absatz_ids=[ende.absatz_id])
    return _tun(kennung, tat)


def ersetzen_verfolgt(kennung: int, von: int, bis: int, neu: str, autor: str = "") -> bool:
    """Den Rohtext-Bereich als nachverfolgte Änderung des Bearbeiters ``autor`` ersetzen."""
    s = _sitzung(kennung)
    vorher = s.nachverfolgen
    s.nachverfolgen = True
    try:
        return _tun(kennung, lambda sitz: (setattr(sitz, "autor", autor or sitz.autor), sitz.ersetzen_durch(von, bis, neu, None, None)))
    finally:
        s.nachverfolgen = vorher


def markdown_ersetzen(kennung: int, von: int, bis: int, bloecke: Sequence[Mapping[str, Daten]], anfang: Stelle) -> bool:
    """Den Rohtext-Bereich durch die Blöcke eines Markdown-Textes ersetzen (je Block Text, Vorlage, Liste, formatierte Läufe)."""
    def tat(s):
        with s.gruppe("Ersetzen"):
            ende = s.ersetzen_durch(von, bis, " ".join(b["text"] for b in bloecke), None, None)
            absaetze = list(s.dokument.absaetze())
            letzter = next(k for k, a in enumerate(absaetze) if a.id == ende.absatz_id)
            ziele = absaetze[letzter - len(bloecke) + 1:letzter + 1]
            for k, (b, a) in enumerate(zip(bloecke, ziele)):
                basis = anfang[1] if k == 0 and a.id == anfang[0] else 0
                if b["vorlage"] and basis == 0:
                    s.vorlage_anwenden(b["vorlage"], absatz_ids=[a.id])
                if b["liste"] and basis == 0:
                    s.liste_anwenden(s.liste_anlegen(b["liste"]), absatz_ids=[a.id])
                for st, en, fmt in b["laeufe"]:
                    s.zeichenformat_anwenden(fmt, _auswahl(((a.id, basis + st), (a.id, basis + en))))
    return _tun(kennung, tat)


def feld_einfuegen(kennung: int, anweisung: str, ergebnis: str, format: Mapping[str, Daten] | None = None) -> bool:
    return _tun(kennung, lambda s: s.feld_einfuegen(anweisung, ergebnis, format=_d(format)))


def link_setzen(kennung: int, ziel: str, text: str | None = None, tipp: str = "") -> bool:
    """Verknüpfung auf die Auswahl; ohne Auswahl und mit ``text`` wird der Text eingefügt, sonst gilt sie für das Wort an der Schreibmarke."""
    def tat(s):
        with s.gruppe("Hyperlink"):
            if s.auswahl.leer and text:
                s.link_setzen(ziel, None, text)
            else:
                s.link_setzen(ziel)
            if tipp:
                s.zeichenformat_anwenden({"tooltip": tipp}, s.auswahl if not s.auswahl.leer else None)
    return _tun(kennung, tat)


def leittext_setzen(kennung: int, teile: Sequence[tuple[str, str, Mapping[str, Daten]]]) -> bool:
    """Phonetisches Leitzeichen: die Auswahl durch die Textstücke mit ihrem Leittext ersetzen; je Stück (Basis, Leittext, Ausrichtung/Abstand/Größe)."""
    from core.formatierung.schrift import ruby_text

    def tat(s):
        with s.gruppe("Phonetisches Leitzeichen"):
            if not s.auswahl.leer:
                s.loeschen()
            for basis, ruby, wie in teile:
                s.text_einfuegen(basis, format={"ruby": ruby_text(ruby, wie["ausrichtung"], wie["abstand"], wie["groesse"])})
    return _tun(kennung, tat)


# ---- Format ----------------------------------------------------------------------------------------------------------------------------------------
def zeichenformat_anwenden(kennung: int, aenderung: Mapping[str, Daten], bereich: Bereich | None = None, ersetzen: bool = False) -> bool:
    return _tun(kennung, lambda s: s.zeichenformat_anwenden(dict(aenderung), _auswahl(bereich), ersetzen=ersetzen))


def absatzformat_anwenden(kennung: int, aenderung: Mapping[str, Daten], absatz_ids: Sequence[int] | None = None, ersetzen: bool = False) -> bool:
    return _tun(kennung, lambda s: s.absatzformat_anwenden(dict(aenderung), absatz_ids=_l(absatz_ids), ersetzen=ersetzen))


def format_uebertragen(kennung: int, zeichen: Mapping[str, Daten], absatz: Mapping[str, Daten]) -> bool:
    """Das aufgenommene Format auf die Auswahl legen (Zeichen) – bei leerer Auswahl auch auf den Absatz."""
    def tat(s):
        with s.gruppe("Format übertragen"):
            s.zeichenformat_anwenden({k: zeichen.get(k) for k in ZEICHEN_DER_PROBE})
            if s.auswahl.leer:
                s.absatzformat_anwenden({k: v for k, v in absatz.items() if k not in ("seitenumbruch_vor", "seitenumbruch_nach")}, ersetzen=True)
    return _tun(kennung, tat)


def design_anwenden(kennung: int, text_schrift: str | None, kopf_schrift: str | None, farbe: str | None) -> bool:
    """Dokumentdesign: Schrift des Fließtextes, Schrift und Farbe der Überschriften – über die Formatvorlagen des Dokuments."""
    import dataclasses

    def tat(s):
        with s.gruppe("Design"):
            for name, v in list(s.dokument.vorlagen.items()):
                z = dict(v.zeichen)
                if v.ebene > 0:
                    if kopf_schrift:
                        z["schrift"] = kopf_schrift
                    if farbe:
                        z["farbe"] = farbe
                elif text_schrift and name == "Standard":
                    z["schrift"] = text_schrift
                if z != v.zeichen:
                    s.vorlage_setzen(dataclasses.replace(v, zeichen=z))
    return _tun(kennung, tat)


def vorlage_loeschen(kennung: int, name: str) -> bool:
    return _tun(kennung, lambda s: s.vorlage_loeschen(name))


def umbruch_einfuegen(kennung: int, art: str) -> bool:
    """Den Absatz an der Schreibmarke teilen und davor umbrechen; ``art``: ``seite`` oder ``spalte``."""
    name, feld = {"seite": ("Seitenumbruch", "seitenumbruch_vor"), "spalte": ("Spaltenumbruch", "spaltenumbruch_vor")}[art]

    def tat(s):
        with s.gruppe(name):
            s.absatz_teilen()
            s.absatzformat_anwenden({feld: True})
    return _tun(kennung, tat)


def absaetze_umstellen(kennung: int, absatz_ids: Sequence[int], ordnung: Sequence[int]) -> bool:
    return _tun(kennung, lambda s: s.absaetze_umstellen(list(absatz_ids), list(ordnung)))


def eigenschaft_setzen(kennung: int, name: str, wert: Daten = None) -> bool:
    """Eine Eigenschaft des Dokuments (zum Beispiel ``tab_abstand``, ``zitierweise``)."""
    return _tun(kennung, lambda s: s.eigenschaft_setzen(name, wert))


# ---- Listen ----------------------------------------------------------------------------------------------------------------------------------------
def liste_entfernen(kennung: int) -> bool:
    return _tun(kennung, lambda s: s.liste_entfernen())


def liste_anlegen_anwenden(kennung: int, ebenen: Daten) -> bool:
    """Eine neue Liste anlegen und auf die Auswahl legen."""
    def tat(s):
        with s.gruppe("Liste"):
            s.liste_anwenden(s.liste_anlegen(ebenen))
    return _tun(kennung, tat)


def liste_neu_beginnen(kennung: int, absatz_id: int, start: int | None = 1) -> bool:
    return _tun(kennung, lambda s: s.liste_neu_beginnen(absatz_id, start))


def listenebene_aendern(kennung: int, schritte: int) -> bool:
    return _tun(kennung, lambda s: s.listenebene_aendern(schritte))


# ---- Tabellen --------------------------------------------------------------------------------------------------------------------------------------
def tabelle_einfuegen(kennung: int, zeilen: int, spalten: int, format: Mapping[str, Daten] | None = None, stelle: Stelle | None = None) -> bool:
    """Eine Tabelle einfügen; mit ``stelle`` steht die Schreibmarke vorher dort (Tabelle zeichnen)."""
    if stelle is None:
        return _tun(kennung, lambda s: s.tabelle_einfuegen(zeilen, spalten, format=_d(format)))

    def tat(s):
        with s.gruppe("Tabelle zeichnen"):
            s.setze_auswahl(_stelle(stelle))
            s.tabelle_einfuegen(zeilen, spalten, format=_d(format))
    return _tun(kennung, tat)


def textfeld_einfuegen(kennung: int, text: str, format: Mapping[str, Daten]) -> bool:
    """Ein Textfeld als einzellige Tabelle mit dem Tabellenformat ``format`` und dem Text darin."""
    def tat(s):
        with s.gruppe("Textfeld"):
            tid = s.tabelle_einfuegen(1, 1, format=dict(format))
            s.text_einfuegen(text, s.zelle_anfang(tid, 0, 0))
    return _tun(kennung, tat)


def text_zu_tabelle(kennung: int, trenner: str, spalten: int | None) -> bool:
    return _tun(kennung, lambda s: s.text_zu_tabelle(None, trenner, spalten))


def tabelle_zu_text(kennung: int, tabellen_id: int, trenner: str, geschachtelt: bool) -> bool:
    return _tun(kennung, lambda s: s.tabelle_zu_text(tabellen_id, trenner, geschachtelt))


def tabelle_loeschen(kennung: int, tabellen_id: int) -> bool:
    return _tun(kennung, lambda s: s.tabelle_loeschen(tabellen_id))


def tabelle_sortieren(kennung: int, tabellen_id: int, spalte: int, aufsteigend: bool = True) -> bool:
    return _tun(kennung, lambda s: s.tabelle_sortieren(tabellen_id, spalte, aufsteigend))


def tabelle_skalieren(kennung: int, tabellen_id: int, faktor_breite: float, faktor_hoehe: float) -> bool:
    return _tun(kennung, lambda s: s.tabelle_skalieren(tabellen_id, faktor_breite, faktor_hoehe))


def tabellenformat_anwenden(kennung: int, tabellen_id: int, aenderung: Mapping[str, Daten]) -> bool:
    return _tun(kennung, lambda s: s.tabellenformat_anwenden(tabellen_id, dict(aenderung)))


def zellformat_anwenden(kennung: int, tabellen_id: int, aenderung: Mapping[str, Daten], zellen: Sequence[tuple[int, int]] | None = None) -> bool:
    return _tun(kennung, lambda s: s.zellformat_anwenden(tabellen_id, dict(aenderung), _l(zellen)))


def zell_richtung(kennung: int, tabellen_id: int, zellen: Sequence[tuple[int, int]], absatz_ids: Sequence[int], richtung: str) -> bool:
    """Textrichtung der Zellen und ihrer Absätze."""
    def tat(s):
        with s.gruppe("Textrichtung"):
            s.zellformat_anwenden(tabellen_id, {"textrichtung": richtung}, list(zellen))
            if absatz_ids:
                s.absatzformat_anwenden({"richtung": richtung}, absatz_ids=list(absatz_ids))
    return _tun(kennung, tat)


def spaltenbreiten_setzen(kennung: int, tabellen_id: int, breiten: Sequence[float]) -> bool:
    return _tun(kennung, lambda s: s.spaltenbreiten_setzen(tabellen_id, list(breiten)))


def zeilenhoehen_setzen(kennung: int, tabellen_id: int, hoehen: Mapping[int, float]) -> bool:
    """Zeilenhöhen: Zeilenindex → Höhe."""
    return _tun(kennung, lambda s: s.zeilenhoehen_setzen(tabellen_id, dict(hoehen)))


def zeilen_gleich(kennung: int, tabellen_id: int, hoehe: float) -> bool:
    return _tun(kennung, lambda s: s.zeilen_gleich(tabellen_id, hoehe))


def tabelle_an_inhalt(kennung: int, tabellen_id: int, spalten: int, zeilen: int) -> bool:
    """„An Inhalt anpassen“: Spaltenbreiten und Zeilenhöhen frei, Tabellenbreite automatisch."""
    return _tun(kennung, lambda s: (s.spaltenbreiten_setzen(tabellen_id, [0.0] * spalten), s.zeilenhoehen_setzen(tabellen_id, [0.0] * zeilen),
                                    s.tabellenformat_anwenden(tabellen_id, {"breite_art": "auto", "breite": None})))


def tabelle_an_fenster(kennung: int, tabellen_id: int, spalten: int, breite: float) -> bool:
    """„An Fenster anpassen“: gleich breite Spalten über die ganze Satzbreite ``breite``."""
    return _tun(kennung, lambda s: (s.spaltenbreiten_setzen(tabellen_id, [breite / spalten] * spalten),
                                    s.tabellenformat_anwenden(tabellen_id, {"breite_art": "prozent", "breite": 100.0})))


def zeilen_einfuegen(kennung: int, tabellen_id: int, index: int, anzahl: int = 1) -> bool:
    return _tun(kennung, lambda s: s.zeilen_einfuegen(tabellen_id, index, anzahl))


def spalten_einfuegen(kennung: int, tabellen_id: int, index: int) -> bool:
    return _tun(kennung, lambda s: s.spalten_einfuegen(tabellen_id, index))


def zeilen_loeschen(kennung: int, tabellen_id: int, index: int) -> bool:
    return _tun(kennung, lambda s: s.zeilen_loeschen(tabellen_id, index))


def spalten_loeschen(kennung: int, tabellen_id: int, index: int) -> bool:
    return _tun(kennung, lambda s: s.spalten_loeschen(tabellen_id, index))


def zellen_verbinden(kennung: int, tabellen_id: int, zeile: int, spalte: int, zeilen: int, spalten: int) -> bool:
    return _tun(kennung, lambda s: s.zellen_verbinden(tabellen_id, zeile, spalte, zeilen, spalten))


def zelle_teilen(kennung: int, tabellen_id: int, zeile: int, spalte: int, zeilen: int = 1, spalten: int = 1) -> bool:
    return _tun(kennung, lambda s: s.zelle_teilen(tabellen_id, zeile, spalte, zeilen, spalten))


def tabellenvorlage_anwenden(kennung: int, tabellen_id: int, name: str, kopf: bool, streifen: bool, spalte: bool, rahmenfarbe: str) -> bool:
    """Eine Tabellenvorlage (Füllungen, Fettdruck, Rahmen) auf die Zellen anwenden; die Optionen bleiben an der Tabelle gespeichert."""
    from core.tabellen.formatierung import VORLAGEN, zeilengrund
    kopf_fill, kopf_schrift, streifen_fill, rahmen = VORLAGEN[name]

    def tat(s):
        with s.gruppe("Tabellenformatvorlage"):
            tab = s._tabelle(tabellen_id)
            s.tabellenformat_anwenden(tabellen_id, {"vorlage": name, "optionen": (1 if kopf else 0) | (2 if streifen else 0) | (4 if spalte else 0) or None,
                                                    "kopfzeilen": 1 if kopf else None, "rahmen_breite": 1.0 if rahmen else None,
                                                    "rahmen_farbe": rahmenfarbe if rahmen else None, "rahmen_art": "einfach" if rahmen else None})
            for z in range(tab.zeilen):
                for sp in range(tab.spalten):
                    zelle = tab.zellen[z][sp]
                    if zelle.verdeckt_von is not None:
                        continue
                    grund = zeilengrund(z, kopf, kopf_fill, streifen_fill if streifen else "") or None
                    s.zellformat_anwenden(tabellen_id, {"hintergrund": grund}, [(z, sp)])
                    ist_kopf = kopf and z == 0
                    fett = ist_kopf or (spalte and sp == 0)
                    ids = [b.id for b in zelle.bloecke if hasattr(b, "inhalte")]
                    if ids and (fett or sp == 0 or z == 0):
                        farbe = kopf_schrift if ist_kopf and kopf_fill else None
                        ende = s._absatz(ids[-1]).laenge
                        s.zeichenformat_anwenden({"fett": True if fett else None, "farbe": farbe}, _auswahl(((ids[0], 0), (ids[-1], ende))))
    return _tun(kennung, tat)


# ---- Objekte ---------------------------------------------------------------------------------------------------------------------------------------
def objekt_einfuegen(kennung: int, art: str, breite: float, hoehe: float, bilddaten: bytes | None = None, daten: Mapping[str, Daten] | None = None,
                     alt_text: str = "") -> bool:
    """Ein Objekt im Text an der Schreibmarke einfügen."""
    return _tun(kennung, lambda s: s.objekt_einfuegen(art, breite, hoehe, bilddaten=bilddaten, daten=_d(daten), alt_text=alt_text))


def objekt_frei_einfuegen(kennung: int, art: str, breite: float, hoehe: float, bilddaten: bytes | None, daten: Mapping[str, Daten],
                          alt_text: str = "") -> int | None:
    """Ein frei positioniertes Objekt am Absatz der Schreibmarke anlegen; → seine Id."""
    return _wert(kennung, lambda s: s.objekt_frei_einfuegen(art, breite, hoehe, None, bilddaten=bilddaten, daten=dict(daten), alt_text=alt_text))


def objekt_aendern(kennung: int, objekt_id: int, **felder: Daten) -> bool:
    return _tun(kennung, lambda s: s.objekt_aendern(objekt_id, **felder))


def inline_aendern(kennung: int, objekt_id: int, ressourcen: Mapping[str, bytes], felder: Mapping[str, Daten]) -> bool:
    """Ein Objekt im Text ändern; neue Bilder (``ressourcen``) kommen im selben Schritt ins Dokument."""
    def tat(s):
        with s.gruppe("Objekt ändern"):
            for name, daten in ressourcen.items():
                s.ressource_setzen(name, daten)
            s.objekt_aendern(objekt_id, **felder)
    return _tun(kennung, tat)


def objekt_entfernen(kennung: int, objekt_id: int) -> bool:
    return _tun(kennung, lambda s: s.objekt_entfernen(objekt_id))


def objekt_ebene(kennung: int, objekt_id: int, wohin: str) -> bool:
    return _tun(kennung, lambda s: s.objekt_ebene(objekt_id, wohin))


def objekt_zu_inline(kennung: int, objekt_id: int) -> bool:
    return _tun(kennung, lambda s: s.objekt_zu_inline(objekt_id))


def objekt_zu_frei(kennung: int, objekt_id: int, umbruch: str) -> bool:
    def tat(s):
        with s.gruppe("Textumbruch"):
            s.objekt_zu_frei(objekt_id, umbruch)
    return _tun(kennung, tat)


# ---- Kommentare, Noten, nachverfolgte Änderungen, Quellen ----------------------------------------------------------------------------------------------
def kommentar_einfuegen(kennung: int, text: str, autor: str = "", initialen: str = "") -> int | None:
    return _wert(kennung, lambda s: s.kommentar_einfuegen(text, autor, initialen))


def kommentar_aendern(kennung: int, kommentar_id: int, text: str | None = None, geloest: bool | None = None) -> bool:
    return _tun(kennung, lambda s: s.kommentar_aendern(kommentar_id, text=text, geloest=geloest))


def kommentar_loeschen(kennung: int, kommentar_id: int | None = None) -> bool:
    return _tun(kennung, lambda s: s.kommentar_loeschen(kommentar_id))


def aenderungen_entscheiden(kennung: int, annehmen: bool, bereich: Bereich | None = None) -> bool:
    """Nachverfolgte Änderungen im Bereich (ohne Angabe: alle) annehmen oder ablehnen."""
    return _tun(kennung, lambda s: (s.aenderungen_annehmen if annehmen else s.aenderungen_ablehnen)(_auswahl(bereich)))


def note_einfuegen(kennung: int, text: str, art: str = "f") -> int | None:
    return _wert(kennung, lambda s: s.note_einfuegen(text, art))


def note_aendern(kennung: int, art: str, note_id: int, text: str) -> bool:
    return _tun(kennung, lambda s: s.note_aendern(art, note_id, text))


def note_loeschen(kennung: int, art: str, note_id: int) -> bool:
    return _tun(kennung, lambda s: s.note_loeschen(art, note_id))


def beschriftungen_nummerieren(kennung: int) -> bool:
    return _tun(kennung, lambda s: s.beschriftungen_nummerieren())


def quelle_setzen(kennung: int, quelle: Mapping[str, Daten]) -> bool:
    return _tun(kennung, lambda s: s.quelle_setzen(dict(quelle)))


def quelle_loeschen(kennung: int, tag: str) -> bool:
    return _tun(kennung, lambda s: s.quelle_loeschen(tag))


# ---- Abschnitte und Seiten ---------------------------------------------------------------------------------------------------------------------------
def abschnitt_einfuegen(kennung: int, beginn: str = "naechste") -> int | None:
    """Einen Abschnittswechsel an der Schreibmarke einfügen; → Nummer des neuen Abschnitts."""
    return _wert(kennung, lambda s: s.abschnitt_einfuegen(beginn=beginn))


def abschnitt_entfernen(kennung: int, index: int, behalte: str = "vorher") -> bool:
    return _tun(kennung, lambda s: s.abschnitt_entfernen(index, behalte))


def abschnitt_beginn_setzen(kennung: int, index: int, beginn: str) -> bool:
    return _tun(kennung, lambda s: s.abschnitt_beginn_setzen(index, beginn))


def seite_ersetzen(kennung: int, index: int, einrichtung: Mapping[str, Daten]) -> bool:
    """Die Seiteneinrichtung des Abschnitts ganz ersetzen; ``einrichtung``: ihre Felder als Wörterbuch (Kopf- und Fußzeilen ebenfalls als Wörterbuch)."""
    return _tun(kennung, lambda s: s.seite_ersetzen(index, _seite(einrichtung)))


def seite_setzen(kennung: int, index: int, **felder: Daten) -> bool:
    """Einzelne Felder der Seiteneinrichtung des Abschnitts setzen."""
    return _tun(kennung, lambda s: s.seite_setzen(index, **felder))


def leere_seite(kennung: int, letzter_absatz: int, blatt: Mapping[str, Daten] | None, einrichtung: Mapping[str, Daten]) -> bool:
    """Ein leeres Blatt hinter dem Absatz ``letzter_absatz``; mit ``blatt`` (eigene Seiteneinrichtung) bekommt es einen eigenen Abschnitt, und
    der Text danach geht mit ``einrichtung`` weiter."""
    def tat(s):
        with s.gruppe("Leere Seite"):
            letzter = s._absatz(letzter_absatz)
            absaetze = list(s.dokument.absaetze())
            nach = next((absaetze[i + 1] for i, a in enumerate(absaetze) if a.id == letzter.id and i + 1 < len(absaetze)), None)
            neu = s.absatz_teilen(_stelle((letzter.id, letzter.laenge)))
            s.absatzformat_anwenden({"seitenumbruch_vor": True, "seitenumbruch_nach": True}, absatz_ids=[neu.absatz_id])
            if blatt is not None:
                s.abschnitt_einfuegen(_stelle((neu.absatz_id, 0)), "naechste", _seite(blatt))
                if nach is not None:
                    s.abschnitt_einfuegen(_stelle((nach.id, 0)), "naechste", _seite(einrichtung))
            s.setze_auswahl(_stelle((neu.absatz_id, 0)))
    return _tun(kennung, tat)


def titelblatt_einfuegen(kennung: int, teile: Sequence[tuple[str, Mapping[str, Daten], Mapping[str, Daten]]]) -> bool:
    """Ein einfaches Deckblatt an den Anfang setzen: je Zeile (Text, Absatzformat, Zeichenformat); danach beginnt der Text auf einer neuen Seite."""
    def tat(s):
        with s.gruppe("Deckblatt"):
            s.text_einfuegen("\n".join(t[0] for t in teile) + "\n\n", s.dokument.anfang())
            absaetze = list(s.dokument.absaetze())
            for (_text, af, zf), a in zip(teile, absaetze):
                s.absatzformat_anwenden(dict(af), absatz_ids=[a.id])
                if a.laenge:
                    s.zeichenformat_anwenden(dict(zf), _auswahl(((a.id, 0), (a.id, a.laenge))))
                s.absatz_zeichenformat_anwenden(dict(zf), absatz_ids=[a.id])
            s.absatzformat_anwenden({"seitenumbruch_nach": True}, absatz_ids=[absaetze[len(teile)].id])
            s.setze_auswahl(_stelle((absaetze[len(teile)].id, 0)))
    return _tun(kennung, tat)


def deckblatt_einfuegen(kennung: int, felder: Sequence[tuple[str, Mapping[str, Daten], Mapping[str, Daten]]], deck: Mapping[str, Daten],
                        rest: Mapping[str, Daten]) -> bool:
    """Ein Deckblatt als ersten Abschnitt an den Anfang setzen: je Feld (Text, Absatzformat, Zeichenformat), die Seiteneinrichtung ``deck``
    des Deckblatts und ``rest`` für das Dokument dahinter."""
    def tat(s):
        with s.gruppe("Deckblatt"):
            s.text_einfuegen("\n".join(text for text, _af, _zf in felder) + "\n", s.dokument.anfang(), format={})
            absaetze = list(s.dokument.absaetze())
            for (_text, af, zf), a in zip(felder, absaetze):
                s.absatzformat_anwenden(dict(af), absatz_ids=[a.id])
                s.absatz_zeichenformat_anwenden(dict(zf), absatz_ids=[a.id])
                if a.laenge:
                    s.zeichenformat_anwenden(dict(zf), _auswahl(((a.id, 0), (a.id, a.laenge))))
            erster_rest = absaetze[len(felder)]                                   # der bisherige Anfang (die Id des ersten Absatzes bleibt beim Deckblatt)
            s.abschnitt_einfuegen(_stelle((erster_rest.id, 0)), "naechste", _seite(rest))    # das Dokument beginnt hinter dem Deckblatt auf einem neuen Blatt
            s.seite_ersetzen(0, _seite(deck))
            s.setze_auswahl(_stelle((absaetze[0].id, 0)))
    return _tun(kennung, tat)
