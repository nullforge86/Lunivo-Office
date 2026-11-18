"""Das Qt-freie Dokumentmodell (``core.document``): Aufbau, Formate, Formatvorlagen, Listen, Serialisierung und Prüfung des Aufbaus."""
import pytest

from lunivo_writer.core.document import Dokument
from lunivo_writer.core.document.dokument import Absatz, Auswahl, Lauf, Position, neues_dokument
from lunivo_writer.core.document.formate import FormatFehler, pruefe, verschmelze
from lunivo_writer.core.document.formatvorlagen import eingebaute_vorlagen, vorlagenkette, wirksames_absatzformat
from lunivo_writer.core.document.listen import listenmarken, nummer_text
from lunivo_writer.core.document.pruefung import pruefe_dokument
from lunivo_writer.core.document.serialisierung import dokument_aus_daten, dokument_zu_daten
from lunivo_writer.core.editing import Bearbeitungssitzung


def beispiel() -> Dokument:
    s = Bearbeitungssitzung()
    s.text_einfuegen("Überschrift\nErster Punkt\nZweiter Punkt")
    a, b, c = list(s.dokument.absaetze())
    for v in eingebaute_vorlagen().values():
        s.vorlage_setzen(v)
    s.vorlage_anwenden("Überschrift 1", absatz_ids=[a.id])
    s.zeichenformat_anwenden({"fett": True, "farbe": "#ff0000"}, Auswahl(Position(b.id, 0), Position(b.id, 6)))
    s.liste_anwenden(s.liste_anlegen("dezimal"), Auswahl(Position(b.id, 0), Position(c.id, 0)))
    s.tabelle_einfuegen(2, 2)
    s.kommentar_einfuegen("Hinweis", "Kay", "K", "", Auswahl(Position(a.id, 0), Position(a.id, 4)))
    s.note_einfuegen("Fußnote", "f", Position(c.id, 5))
    s.objekt_frei_einfuegen("form", 30.0, 20.0)
    return s.dokument


def test_neues_dokument_besteht_aus_einem_abschnitt_mit_einem_absatz():
    d = neues_dokument()
    assert len(d.abschnitte) == 1 and len(list(d.absaetze())) == 1
    assert d.text() == "" and pruefe_dokument(d) == []


def test_absatz_text_und_laenge_ergeben_sich_aus_den_laeufen():
    a = Absatz(1, [Lauf("Hallo ", {}), Lauf("Welt", {"fett": True})])
    assert a.text() == "Hallo Welt" and a.laenge == 10


def test_formate_pruefen_schema_und_verschmelzen():
    assert pruefe("zeichen", {"fett": True, "groesse_pt": 12}) == {"fett": True, "groesse_pt": 12}
    with pytest.raises(FormatFehler):
        pruefe("zeichen", {"gibtsnicht": 1})
    with pytest.raises(FormatFehler):
        pruefe("absatz", {"ausrichtung": "schief"})
    assert verschmelze({"fett": True, "kursiv": True}, {"fett": None}) == {"kursiv": True}
    assert "gewicht" not in verschmelze({"gewicht": 700}, {"fett": True})


def test_formatvorlagen_vererbung_und_wirksames_format():
    d = beispiel()
    kette = vorlagenkette(d, "Überschrift 1")
    assert [v.name for v in kette] == ["Standard", "Überschrift 1"]                 # von der Basis zur Vorlage
    a = next(d.absaetze())
    assert wirksames_absatzformat(d, a) is not None


def test_listenmarken_zaehlen_je_ebene():
    d = beispiel()
    marken = listenmarken(d)
    texte = [marken[a.id] for a in d.absaetze() if a.liste_id is not None]
    assert texte[:2] == ["1.", "2."] or len(set(texte)) == len(texte)
    assert nummer_text("klein", 28) == "ab" and nummer_text("roem_gross", 14) == "XIV"


def test_serialisierung_rundlauf_erhaelt_den_inhalt():
    d = beispiel()
    daten = dokument_zu_daten(d)
    zurueck = dokument_aus_daten(daten)
    assert zurueck.text() == d.text()
    assert len(list(zurueck.tabellen())) == len(list(d.tabellen()))
    assert len(zurueck.objekte) == len(d.objekte) and len(zurueck.kommentare) == len(d.kommentare)
    assert dokument_zu_daten(zurueck) == daten
    assert pruefe_dokument(zurueck) == []


def test_pruefung_findet_kaputte_verweise():
    d = beispiel()
    d.objekte[next(iter(d.objekte))].anker = 999999
    assert pruefe_dokument(d) != []


def test_ids_sind_im_ganzen_dokument_eindeutig():
    d = beispiel()
    ids = [a.id for a in d.absaetze()] + [t.id for t in d.tabellen()] + list(d.objekte)
    assert len(ids) == len(set(ids))
