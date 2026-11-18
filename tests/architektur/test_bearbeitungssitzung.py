"""Die zentrale Bearbeitungssitzung (``core.editing``) auf dem Qt-freien Dokumentmodell (``core.document``): Text, Formate, Listen, Tabellen, Objekte,
Abschnitte, Zusatzdaten, Schreibmarke und Auswahl, Schritte mit Rückgängig/Wiederholen, Änderungsstatus."""
import pytest

from lunivo_writer.core.document.dokument import Auswahl, Position
from lunivo_writer.core.editing import Bearbeitungssitzung, BearbeitungsFehler, Sitzung


def neu(text: str = "") -> Bearbeitungssitzung:
    s = Bearbeitungssitzung()
    if text:
        s.text_einfuegen(text)
    return s


def absaetze(s):
    return list(s.dokument.absaetze())


def test_sitzung_ist_der_name_der_bearbeitungssitzung():
    assert Sitzung is Bearbeitungssitzung


def test_neues_dokument_hat_einen_leeren_absatz_und_die_marke_am_anfang():
    s = Bearbeitungssitzung()
    assert s.text() == "" and len(absaetze(s)) == 1
    assert s.auswahl.leer and s.auswahl.kopf == s.dokument.anfang()
    assert s.pruefe() == []


def test_text_einfuegen_setzt_die_marke_hinter_den_text():
    s = neu("Hallo Welt")
    assert s.text() == "Hallo Welt"
    assert s.auswahl.kopf == Position(absaetze(s)[0].id, 10)


def test_zeilenwechsel_beginnt_einen_neuen_absatz():
    s = neu("Eins\nZwei")
    assert [a.text() for a in absaetze(s)] == ["Eins", "Zwei"]
    assert s.auswahl.kopf == Position(absaetze(s)[1].id, 4)


def test_loeschen_einer_auswahl_und_rueckwaerts_loeschen():
    s = neu("Hallo Welt")
    a = absaetze(s)[0]
    s.loeschen(Auswahl(Position(a.id, 5), Position(a.id, 10)))
    assert s.text() == "Hallo"
    s.zeichen_loeschen()                        # Rückschritt: das letzte Zeichen
    assert s.text() == "Hall"


def test_loeschen_ueber_absatzgrenze_verbindet_die_absaetze():
    s = neu("Eins\nZwei")
    a, b = absaetze(s)
    s.loeschen(Auswahl(Position(a.id, 4), Position(b.id, 0)))
    assert [x.text() for x in absaetze(s)] == ["EinsZwei"]


def test_ersetzen_ersetzt_die_auswahl():
    s = neu("Hallo Welt")
    a = absaetze(s)[0]
    s.ersetzen("Erde", Auswahl(Position(a.id, 6), Position(a.id, 10)))
    assert s.text() == "Hallo Erde"


def test_rueckgaengig_und_wiederholen():
    s = neu()
    s.text_einfuegen("abc")
    assert s.kann_rueckgaengig and not s.kann_wiederholen
    s.rueckgaengig()
    assert s.text() == "" and s.kann_wiederholen
    s.wiederholen()
    assert s.text() == "abc"


def test_gruppe_ist_ein_rueckgaengig_schritt():
    s = neu()
    with s.gruppe("Zwei Eingaben"):
        s.text_einfuegen("ab")
        s.text_einfuegen("cd")
    assert s.text() == "abcd"
    s.rueckgaengig()
    assert s.text() == ""


def test_aenderungsstatus_folgt_dem_gespeicherten_stand():
    s = neu()
    assert s.geaendert is False or s.geaendert is True
    s.als_gespeichert_merken()
    assert not s.geaendert
    s.text_einfuegen("x")
    assert s.geaendert
    s.rueckgaengig()
    assert not s.geaendert


def test_beobachter_werden_bei_aenderungen_benachrichtigt():
    s = neu()
    meldungen = []
    s.beobachte(meldungen.append)
    s.text_einfuegen("x")
    assert meldungen


def test_zeichenformat_auf_auswahl_und_effektive_abfrage():
    s = neu("Hallo Welt")
    a = absaetze(s)[0]
    s.zeichenformat_anwenden({"fett": True}, Auswahl(Position(a.id, 0), Position(a.id, 5)))
    assert s.zeichenformat_bei(Position(a.id, 3)).get("fett") is True
    assert not s.zeichenformat_bei(Position(a.id, 8)).get("fett")
    s.zeichenformat_anwenden({"fett": None}, Auswahl(Position(a.id, 0), Position(a.id, 5)))
    assert not s.zeichenformat_bei(Position(a.id, 3)).get("fett")


def test_absatzformat_und_formatvorlage():
    s = neu("Titel\nText")
    a, b = absaetze(s)
    s.absatzformat_anwenden({"ausrichtung": "mitte"}, absatz_ids=[a.id])
    assert a.format["ausrichtung"] == "mitte"
    from lunivo_writer.core.document.formatvorlagen import eingebaute_vorlagen
    for v in eingebaute_vorlagen().values():
        s.vorlage_setzen(v)
    s.vorlage_anwenden("Überschrift 1", absatz_ids=[a.id])
    assert a.format.get("vorlage") == "Überschrift 1"
    with pytest.raises(BearbeitungsFehler):
        s.vorlage_anwenden("Gibt es nicht", absatz_ids=[b.id])


def test_liste_anlegen_anwenden_und_ebene():
    s = neu("Eins\nZwei")
    lid = s.liste_anlegen("dezimal")
    s.liste_anwenden(lid, Auswahl(Position(absaetze(s)[0].id, 0), Position(absaetze(s)[1].id, 3)))
    a, b = absaetze(s)
    assert a.liste_id == lid == b.liste_id
    marken = s.listenmarken()
    assert marken[a.id] != marken[b.id]
    s.listenebene_aendern(1, absatz_ids=[b.id])
    assert b.ebene == 1
    s.liste_entfernen(absatz_ids=[a.id, b.id])
    assert a.liste_id is None


def test_tabelle_einfuegen_zeilen_spalten_und_verbinden():
    s = neu("Davor")
    tid = s.tabelle_einfuegen(2, 2)
    t = s.dokument.tabelle(tid)
    assert (t.zeilen, t.spalten) == (2, 2)
    s.zeilen_einfuegen(tid, 1)
    s.spalten_einfuegen(tid, 2)
    assert (t.zeilen, t.spalten) == (3, 3)
    s.zellen_verbinden(tid, 0, 0, 1, 2)
    assert t.zellen[0][0].spaltenspanne == 2 and t.zellen[0][1].verdeckt_von == (0, 0)
    s.zelle_teilen(tid, 0, 0, 1, 2)
    assert t.zellen[0][0].spaltenspanne == 1
    s.zeilen_loeschen(tid, 2)
    s.spalten_loeschen(tid, 2)
    assert (t.zeilen, t.spalten) == (2, 2)
    s.tabelle_loeschen(tid)
    assert not list(s.dokument.tabellen())
    assert s.pruefe() == []


def test_tabelle_rueckgaengig_stellt_die_tabelle_wieder_her():
    s = neu("Davor")
    tid = s.tabelle_einfuegen(2, 2)
    s.rueckgaengig()
    assert not list(s.dokument.tabellen())
    s.wiederholen()
    assert tid in {t.id for t in s.dokument.tabellen()}


def test_objekt_einfuegen_frei_und_im_text():
    s = neu("Text")
    oid = s.objekt_einfuegen("bild", 40.0, 20.0, bilddaten=b"\x89PNG-daten")
    assert s.objekt_position(oid) is not None
    frei = s.objekt_frei_einfuegen("form", 30.0, 30.0)
    assert frei in s.dokument.objekte
    s.objekt_aendern(frei, breite=50.0)
    assert s.dokument.objekte[frei].breite == 50.0
    s.objekt_ebene(frei, "hinten")
    s.objekt_entfernen(frei)
    assert frei not in s.dokument.objekte
    s.rueckgaengig()
    assert frei in s.dokument.objekte
    assert s.pruefe() == []


def test_abschnitt_einfuegen_und_entfernen():
    s = neu("Eins\nZwei")
    b = absaetze(s)[1]
    n = s.abschnitt_einfuegen(Position(b.id, 0), "naechste")
    assert n == 1 and len(s.dokument.abschnitte) == 2
    s.abschnitt_entfernen(1)
    assert len(s.dokument.abschnitte) == 1
    assert s.pruefe() == []


def test_kommentar_notiz_und_textmarke():
    s = neu("Hallo Welt")
    a = absaetze(s)[0]
    kid = s.kommentar_einfuegen("Prüfen", "Kay", "K", "", Auswahl(Position(a.id, 0), Position(a.id, 5)))
    assert s.dokument.kommentare[kid].text == "Prüfen"
    s.kommentar_aendern(kid, geloest=True)
    assert s.dokument.kommentare[kid].geloest
    nid = s.note_einfuegen("Fußnote", "f", Position(a.id, 10))
    assert s.dokument.noten["f"][nid].text == "Fußnote"
    s.textmarke_setzen("Anfang", Auswahl(Position(a.id, 0), Position(a.id, 5)))
    assert "Anfang" in s.textmarken()
    s.textmarke_loeschen("Anfang")
    assert "Anfang" not in s.textmarken()
    s.kommentar_loeschen(kid)
    assert kid not in s.dokument.kommentare


def test_nachverfolgte_aenderungen_annehmen_und_ablehnen():
    s = neu("Hallo Welt")
    a = absaetze(s)[0]
    s.nachverfolgen = True
    s.autor, s.datum = "Kay", "2026-01-01"
    s.loeschen(Auswahl(Position(a.id, 5), Position(a.id, 10)))
    s.text_einfuegen("!", Position(a.id, 5))
    s.nachverfolgen = False
    arten = {art for _f, art, _a, _d in s.aenderungen()}
    assert arten == {"ins", "del"}
    s.aenderungen_ablehnen()
    assert s.text() == "Hallo Welt"


def test_suchen_und_alle_ersetzen_mit_einem_schritt():
    s = neu("eins zwei eins")
    assert len(s.suche("eins")) == 2
    assert s.alle_ersetzen("eins", "drei") == 2
    assert s.text() == "drei zwei drei"
    s.rueckgaengig()
    assert s.text() == "eins zwei eins"


def test_ausschnitt_kopieren_und_einfuegen():
    s = neu("Hallo Welt")
    a = absaetze(s)[0]
    stueck = s.ausschnitt(Auswahl(Position(a.id, 0), Position(a.id, 5)))
    s.ausschnitt_einfuegen(stueck, Position(a.id, 10))
    assert s.text() == "Hallo WeltHallo"


def test_falsche_stelle_ist_ein_bearbeitungsfehler():
    s = neu("abc")
    with pytest.raises(BearbeitungsFehler):
        s.text_einfuegen("x", Position(absaetze(s)[0].id, 99))


def test_absaetze_umstellen_und_ersetzen():
    s = neu("B\nA\nC")
    ids = [a.id for a in absaetze(s)]
    s.absaetze_umstellen(ids, [1, 0, 2])
    assert [a.text() for a in absaetze(s)] == ["A", "B", "C"]
    s.rueckgaengig()
    assert [a.text() for a in absaetze(s)] == ["B", "A", "C"]


def test_dokument_ersetzen_ist_ein_schritt():
    from lunivo_writer.core.document.dokument import neues_dokument
    s = neu("alt")
    anderes = neues_dokument()
    Bearbeitungssitzung(anderes).text_einfuegen("neu")
    s.dokument_ersetzen(anderes)
    assert s.text() == "neu"
    s.rueckgaengig()
    assert s.text() == "alt"
