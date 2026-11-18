"""Die Schnittstelle der Oberfläche zum Dokumentenkern (``KernEditor``): Befehle des Bandes wirken über die Bearbeitungssitzung auf das Dokumentmodell."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
from PySide6.QtGui import QImage

from lunivo_writer.core.document import neues_dokument
from lunivo_writer.oberflaeche.dokument.bearbeitung.kern_editor import KernEditor


@pytest.fixture
def ed(app):
    e = KernEditor(neues_dokument())
    e.ansicht.resize(900, 700)
    yield e
    e.ansicht.deleteLater()


def schreibe(e, text):
    e.ansicht.einfuegen(text)


def absaetze(e):
    return list(e.sitzung.dokument.absaetze())


def test_schreiben_und_aenderungsstatus(ed):
    assert not ed.document().isModified()
    schreibe(ed, "Hallo Welt")
    assert ed.toPlainText() == "Hallo Welt" and ed.document().isModified()
    ed.document().setModified(False)
    assert not ed.document().isModified()


def test_rueckgaengig_wiederholen(ed):
    schreibe(ed, "abc")
    ed.undo()
    assert ed.toPlainText() == ""
    ed.redo()
    assert ed.toPlainText() == "abc"


def test_textcursor_setzen_markieren_und_ersetzen(ed):
    schreibe(ed, "Hallo Welt")
    c = ed.textCursor()
    c.setPosition(6)
    c.setPosition(10, c.KeepAnchor)
    assert c.hasSelection() and c.selectedText() == "Welt"
    ed.setTextCursor(c)
    c.insertText("Erde")
    assert ed.toPlainText() == "Hallo Erde"
    c2 = ed.textCursor()
    c2.select(c2.Document)
    assert c2.selectedText() == "Hallo Erde"
    c2.movePosition(c2.Start)
    assert c2.position() == 0 and c2.atBlockStart()


def test_zeichenformat_fett_kursiv_und_abfrage(ed):
    schreibe(ed, "Hallo Welt")
    ed.select_range(0, 5)
    ed.toggle_bold(True)
    ed.toggle_italic(True)
    f = ed.textCursor().charFormat()
    assert f.fontWeight() >= 600 and f.fontItalic()
    ed.set_font_size(18)
    assert ed.zeichenformat()["groesse_pt"] == 18


def test_absatzformat_ausrichtung_einzug_abstand(ed):
    schreibe(ed, "Text")
    ed.set_alignment("mitte")
    assert ed.absatzformat()["ausrichtung"] == "mitte"
    ed.set_indents(10, 5, 0)
    assert round(ed.absatzformat()["einzug_links"]) == 38
    ed.set_paragraph_spacing(6, 12)
    assert ed.absatzformat()["abstand_vor"] > 0


def test_formatvorlage_anwenden(ed):
    schreibe(ed, "Titel")
    ed.apply_style("Überschrift 1")
    assert ed.current_style() == "Überschrift 1"


def test_liste_umschalten_und_spec(ed):
    schreibe(ed, "Eins\nZwei")
    ed.select_range(0, 8)
    ed.toggle_list("number")
    assert ed.liste_spec() is not None and all(a.liste_id is not None for a in absaetze(ed))
    ed.toggle_list("number")
    assert all(a.liste_id is None for a in absaetze(ed))


def test_tabelle_einfuegen_und_zeile_spalte(ed):
    ed.insert_table(2, 3)
    t = ed.tabelle_an_marke()
    assert t is not None and (t.rows(), t.columns()) == (2, 3)
    assert ed.tabelle_aktion("zeile_unten") and ed.tabelle_an_marke().rows() == 3
    assert ed.tabelle_aktion("spalte_rechts") and ed.tabelle_an_marke().columns() == 4
    assert ed.zellformat({"hintergrund": "#ffff00"})
    assert ed.tabellenformat({"rahmen_breite": 1.0})


def test_objekt_frei_einfuegen_drehen_und_loeschen(ed):
    bild = QImage(40, 20, QImage.Format_ARGB32)
    bild.fill(0xff2f6fb5)
    oid = ed.objekt_frei_einfuegen("bild", {}, 80.0, 40.0, bild, "Alt")
    assert oid in ed.sitzung.dokument.objekte and ed.objekt_gewaehlt().id == oid
    ed.objekt_drehen(90.0)
    assert ed.objekt_gewaehlt().daten["dreh"] == 90.0
    assert ed.objekt_umbruch("quadrat") and ed.objekt_gewaehlt().umbruch == "quadrat"
    assert ed.objekt_loeschen() and oid not in ed.sitzung.dokument.objekte


def test_bild_im_text_einfuegen_und_auswaehlen(ed):
    schreibe(ed, "Text")
    bild = QImage(40, 20, QImage.Format_ARGB32)
    bild.fill(0xff2f6fb5)
    assert ed.bild_im_text_einfuegen(bild, "Beschreibung")
    ed.ansicht.sitzung.setze_auswahl(*[ed.sitzung.objekt_position(i.id) for i in [ed.sitzung._inline_alle()[0]]] * 1) if hasattr(ed.sitzung, "_inline_alle") else None
    gefunden = [x for a in absaetze(ed) for x in a.inhalte if not hasattr(x, "text")]
    assert gefunden and gefunden[0].alt_text == "Beschreibung"


def test_kommentar_note_und_springen(ed):
    schreibe(ed, "Hallo Welt")
    ed.select_range(0, 5)
    kid = ed.kommentar_neu("Prüfen")
    assert kid in ed.sitzung.dokument.kommentare and ed.kommentare[kid]["text"] == "Prüfen"
    ed.kommentar_geloest(kid, True)
    assert ed.kommentare[kid]["geloest"]
    ed.select_range(10, 10)
    nid = ed.note_neu("f", "Eine Fußnote")
    assert ed.noten["f"][nid] == "Eine Fußnote"
    ed.note_loeschen("f", nid)
    assert nid not in ed.noten["f"]


def test_suchen_ersetzen_ueber_rohtext(ed):
    schreibe(ed, "eins zwei eins")
    assert ed.replace_range(0, 4, "drei", erwartet="eins")
    assert ed.toPlainText() == "drei zwei eins"
    assert not ed.replace_range(0, 4, "x", erwartet="falsch")


def test_markdown_ersetzen_setzt_formate(ed):
    schreibe(ed, "Anfang")
    assert ed.replace_range(0, 6, "# Titel\n**fett** und *kursiv*", markdown=True)
    a = absaetze(ed)
    assert a[0].text() == "Titel" and a[0].format.get("vorlage") == "Überschrift 1"
    assert a[1].text() == "fett und kursiv"


def test_gehe_zu_ziele_und_verzeichnis(ed):
    from lunivo_writer.editor.dokument import gehe_zu as G, verzeichnis as V
    schreibe(ed, "Eins\nText\nZwei")
    ed.select_range(0, 0)
    ed.apply_style("Überschrift 1")
    assert [t for t, _p in G.ziele(ed, "Überschrift")] == ["Eins"]
    assert V.verzeichnis_einfuegen(ed, "toc") == 1
    assert V.vorhanden(ed.sitzung.dokument, "toc")
    assert ed.sitzung.pruefe() == []


def test_beschriftung_und_querverweis(ed):
    from lunivo_writer.editor.dokument import verweise as W
    schreibe(ed, "Absatz")
    W.beschriftung_einfuegen(ed, "Abbildung", "Ein Bild")
    liste = W.beschriftungen_liste(ed)
    assert liste and liste[0]["text"].startswith("Abbildung 1")
    ziele = [z for z in W.querverweis_ziele(ed) if z["art"] == "Abbildung"]
    assert ziele
    ed.select_range(0, 0)
    W.querverweis_einfuegen(ed, ziele[0], "nummer")
    assert "Abbildung 1" in ed.toPlainText()


def test_formularfeld_einfuegen_und_zuruecksetzen(ed):
    from lunivo_writer.editor.dokument import formular as FO
    FO.einfuegen(ed, FO.meta("kasten", "Haken"))
    assert FO.bereiche(ed.sitzung.dokument)
    FO.klick(ed, 0)
    assert FO.daten(ed.sitzung.dokument)[0] == ("Haken", "ja")
    assert FO.alle_zuruecksetzen(ed) == 1


def test_textbaustein_einfuegen_mit_format(ed):
    from lunivo_writer.dienste import bausteine
    schreibe(ed, "Text")
    ed.select_range(0, 4)
    ed.toggle_bold(True)
    bloecke = ed.sitzung.ausschnitt()
    b = {"name": "t", "bloecke": __import__("lunivo_writer.core.document.serialisierung", fromlist=["x"]).bloecke_zu_daten(bloecke), "text": "Text"}
    ed.select_range(4, 4)
    bausteine.einfuegen(ed, b)
    assert ed.toPlainText() == "TextText"


def test_abschnitt_leere_seite_und_design(ed):
    schreibe(ed, "Eins")
    n = ed.abschnitt_einfuegen("naechste")
    assert n == 1 and ed.abschnitte_anzahl() == 2
    ed.apply_design("Liberation Serif", "Liberation Sans", "#336699")
    v = ed.sitzung.dokument.vorlagen
    assert v["Überschrift 1"].zeichen.get("farbe") == "#336699" if "Überschrift 1" in v else True


def test_markup_nachverfolgen_und_annehmen(ed):
    schreibe(ed, "Hallo Welt")
    ed.set_verfolgen(True)
    ed.select_range(5, 10)
    ed.ansicht.entfernen(False)
    ed.set_verfolgen(False)
    assert ed.aenderungen()
    ed.alle_aenderungen(False)
    assert ed.toPlainText() == "Hallo Welt"
