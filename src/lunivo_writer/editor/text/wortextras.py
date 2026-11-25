"""Wort-Extras: Absätze aufräumen — über die Markierung, ohne Markierung über das ganze Dokument. Jede Handlung ist ein Schritt für Rückgängig.

Texte in Tabellen bleiben unberührt; leere Absätze, Bilder und Zeilenumbrüche werden dort gesucht, wo sie im Fließtext stehen."""
from __future__ import annotations


ZEILENUMBRUCH = " "
SATZENDE = tuple(".!?:;…\"“”»«)")


def _bloecke(ed, s) -> list:
    """Die Absätze der Markierung (ohne Markierung: alle) außerhalb von Tabellen, in Dokumentreihenfolge."""
    alle = [b for ab in s.dokument.abschnitte for b in ab.bloecke if hasattr(b, "inhalte")]
    if s.auswahl.leer:
        return alle
    von, bis = s._bereich()
    ids = [a.id for a in s.dokument.absaetze()]
    lo, hi = ids.index(von.absatz_id), ids.index(bis.absatz_id)
    return [a for a in alle if lo <= ids.index(a.id) <= hi]


def _leer(a) -> bool:
    """Ein Absatz ohne Zeichen und ohne Bild."""
    return a.laenge == 0


def _nachbar(s, a, schritt: int):
    """Der Absatz davor oder dahinter im selben Textfluss (``None``, wenn dort keiner steht)."""
    n = s.nachbar(a.id, schritt)
    return n if n is not None and hasattr(n, "inhalte") else None


def _schritt(ed, arbeit) -> int:
    """Führt ``arbeit(sitzung, absaetze)`` als einen Rückgängig-Schritt aus. → Zahl der Änderungen."""
    zahl = [0]

    def f(s):
        with s.gruppe("Wort-Extras"):
            zahl[0] = arbeit(s, _bloecke(ed, s)) or 0
    ed.ansicht._aendern(f)
    return zahl[0]


def _auswahl(a, von: int, bis: int):
    from lunivo_writer.core.dokument.dokument import Auswahl, Position
    return Auswahl(Position(a.id, von), Position(a.id, bis))


def leere_loeschen(ed) -> int:
    from lunivo_writer.core.dokument.dokument import Auswahl, Position

    def arbeit(s, bloecke):
        n = 0
        for a in reversed(bloecke):
            nxt = _nachbar(s, a, 1)
            if _leer(a) and nxt is not None:
                s.loeschen(Auswahl(Position(a.id, 0), Position(nxt.id, 0))); n += 1
        return n
    return _schritt(ed, arbeit)


def leere_einfuegen(ed) -> int:
    from lunivo_writer.core.dokument.dokument import Position

    def arbeit(s, bloecke):
        n = 0
        for a in reversed(bloecke):
            nxt = _nachbar(s, a, 1)
            if not _leer(a) and nxt is not None and not _leer(nxt):
                s.absatz_teilen(Position(a.id, a.laenge)); n += 1
        return n
    return _schritt(ed, arbeit)


def zeilenumbruch_in_return(ed) -> int:
    def arbeit(s, bloecke):
        n = 0
        for a in reversed(bloecke):
            while (i := s._absatz(a.id).text().rfind(ZEILENUMBRUCH)) >= 0:
                s.ersetzen("\n", _auswahl(a, i, i + 1)); n += 1
        return n
    return _schritt(ed, arbeit)


def absaetze_neu_anordnen(ed) -> int:
    """Absätze, die mitten im Satz enden (hartes Return in einem Satz, etwa aus PDF-Text), werden zu einem Absatz."""
    from lunivo_writer.core.dokument.dokument import Auswahl, Position
    from lunivo_writer.core.dokument.formatvorlagen import ueberschriftsebene

    def arbeit(s, bloecke):
        n = 0
        for a in reversed(bloecke):
            nxt = _nachbar(s, a, 1)
            t = a.text().rstrip()
            if t and not t.endswith(SATZENDE) and nxt is not None and nxt.text().strip() and a.liste_id is None and nxt.liste_id is None \
                    and ueberschriftsebene(s.dokument, a) == 0:
                s.ersetzen(" ", Auswahl(Position(a.id, a.laenge), Position(nxt.id, 0))); n += 1
        return n
    return _schritt(ed, arbeit)


def leerzeichen_bereinigen(ed) -> int:
    """Doppelte Leerzeichen und Leerzeichen am Anfang und Ende der Absätze entfernen."""
    import re

    def arbeit(s, bloecke):
        n = 0
        for a in reversed(bloecke):
            t = a.text()
            for m in reversed(list(re.finditer(r"^[ \t]+|[ \t]+$|(?<=\S)[ ]{2,}", t))):
                von, bis = m.start(), m.end()
                if m.group().strip() == "" and von > 0 and bis < len(t):          # mitten im Satz bleibt ein Leerzeichen
                    von += 1
                s.loeschen(_auswahl(a, von, bis)); n += 1
        return n
    return _schritt(ed, arbeit)


def _punkte(s, a) -> float:
    from lunivo_writer.core.layout import formatwerte as F
    return float(F.zeichenformat(s.dokument, a, {}).get("groesse_pt") or 11.0)


def einzug_zwei_zeichen(ed) -> int:
    """Erstzeileneinzug um zwei Zeichen der Schriftgröße des Absatzes."""
    def arbeit(s, bloecke):
        n = 0
        for a in bloecke:
            if _leer(a) or a.liste_id is not None:
                continue
            s.absatzformat_anwenden({"einzug_erste": 2 * _punkte(s, a) * 96 / 72}, absatz_ids=[a.id]); n += 1
        return n
    return _schritt(ed, arbeit)


def smart_anordnen(ed) -> int:
    """Leerzeichen bereinigen, leere Absätze löschen, Erstzeileneinzug um zwei Zeichen (zusammen ein Schritt für Rückgängig)."""
    zahl = [0]

    def f(s):
        with s.gruppe("Smart-Anordnen"):
            zahl[0] = leerzeichen_bereinigen(ed) + leere_loeschen(ed) + einzug_zwei_zeichen(ed)
    ed.ansicht._aendern(f)
    return zahl[0]


def fuehrende_leerzeichen_loeschen(ed) -> int:
    """Leerzeichen und Tabs am Anfang der Absätze entfernen."""
    def arbeit(s, bloecke):
        n = 0
        for a in reversed(bloecke):
            t = a.text()
            k = len(t) - len(t.lstrip(" \t\u00a0\u3000"))
            if k and t.strip():
                s.loeschen(_auswahl(a, 0, k)); n += 1
        return n
    return _schritt(ed, arbeit)


def zeilenumbrueche_loeschen(ed) -> int:
    """Manuelle Zeilenumbrüche (Umschalt+Enter) entfernen; die Zeilen laufen zusammen, zwischen zwei Wörtern bleibt ein Leerzeichen."""
    def arbeit(s, bloecke):
        n = 0
        for a in reversed(bloecke):
            while (i := s._absatz(a.id).text().rfind(ZEILENUMBRUCH)) >= 0:
                t = s._absatz(a.id).text()
                luecke = 0 < i < len(t) - 1 and not t[i - 1].isspace() and not t[i + 1].isspace()
                s.ersetzen(" " if luecke else "", _auswahl(a, i, i + 1)); n += 1
        return n
    return _schritt(ed, arbeit)


def leerabsatz_modus_wechseln(ed) -> int:
    """Trennung durch leere Absätze umschalten: Stehen zwischen den Absätzen leere Absätze, verschwinden sie; sonst kommt zwischen
    je zwei Absätzen einer."""
    s = ed.sitzung
    bloecke = _bloecke(ed, s)
    zwischen = any(_leer(a) and (v := _nachbar(s, a, -1)) is not None and not _leer(v) and (nx := _nachbar(s, a, 1)) is not None and not _leer(nx)
                   for a in bloecke)
    return leere_loeschen(ed) if zwischen else leere_einfuegen(ed)


def einzug_in_leerzeichen(ed) -> int:
    """Den Erstzeileneinzug eines Absatzes in Leerzeichen am Absatzanfang umwandeln (gleich breit), der Einzug selbst wird 0."""
    from lunivo_writer.core.dokument.dokument import Position
    from lunivo_writer.core.layout import formatwerte as F

    def arbeit(s, bloecke):
        n = 0
        for a in bloecke:
            erste = F.einzuege(F.absatzformat(s.dokument, a))[2]
            if erste <= 0 or _leer(a):
                continue
            breite = 0.28 * _punkte(s, a) * 96 / 72 or 4.0
            s.absatzformat_anwenden({"einzug_erste": None}, absatz_ids=[a.id])
            s.text_einfuegen(" " * max(1, round(erste / breite)), Position(a.id, 0)); n += 1
        return n
    return _schritt(ed, arbeit)


# Das Menü am Knopf „Wort-Extras“ in der Anordnung der Vorlage: (Text, Symbol, Funktion), "-" = Trennlinie,
# („Löschen“, Symbol, [Untereinträge]) = Untermenü
MENUE = [("Absätze neu anordnen", "weNeu", absaetze_neu_anordnen),
         ("Smart-Anordnen", "weSmart", smart_anordnen),
         ("Leerabsatz-Trennung umschalten", "weLeerModus", leerabsatz_modus_wechseln),
         "-",
         ("Löschen", "weLoeschen", [("Leere Absätze löschen", "weLeerWeg", leere_loeschen),
                                    ("Führende Leerzeichen löschen", "weFuehrend", fuehrende_leerzeichen_loeschen),
                                    ("Leerzeichen löschen", "weLeerz", leerzeichen_bereinigen),
                                    ("Zeilenumbrüche löschen", "weZeilenWeg", zeilenumbrueche_loeschen)]),
         ("Zeilenumbruch in Absatzmarke umwandeln", "weReturn", zeilenumbruch_in_return),
         "-",
         ("Absatzeinzug um 2 Zeichen", "weEinzug", einzug_zwei_zeichen),
         ("Absatzeinzug in Leerzeichen umwandeln", "weEinzugLeer", einzug_in_leerzeichen),
         ("Leere Absätze einfügen", "weLeerEin", leere_einfuegen)]
