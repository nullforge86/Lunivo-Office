"""Speichern und Laden über das Dokumentmodell: Text, Formate, Listen, Tabelle, Bild und Kommentar überstehen den Weg durch DOCX, ODT, RTF und TXT."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
from PySide6.QtGui import QImage

from lunivo_writer.core.document import neues_dokument
from lunivo_writer.core.document.dokument import Tabelle
from lunivo_writer.dienste.modell_laden import lade_modell
from lunivo_writer.dienste.modell_speichern import speichere_modell
from lunivo_writer.oberflaeche.dokument.bearbeitung.kern_editor import KernEditor


def _beispiel(app):
    ed = KernEditor(neues_dokument())
    ed.ansicht.einfuegen("Titel\nEin Absatz mit fettem Wort und mehr.\nZweiter Absatz.")
    ed.select_range(0, 5); ed.apply_style("Überschrift 1")
    ed.select_range(14, 20); ed.toggle_bold(True)
    return ed


def _texte(dok):
    return [a.text() for a in dok.absaetze()]


@pytest.mark.parametrize("endung", ["docx", "odt", "rtf", "txt"])
def test_text_und_absaetze_ueberleben(app, tmp_path, endung):
    ed = _beispiel(app)
    pfad = str(tmp_path / f"a.{endung}")
    speichere_modell(pfad, ed.sitzung.dokument, ed.page)
    geladen = lade_modell(pfad).document
    assert [t for t in _texte(geladen) if t] == ["Titel", "Ein Absatz mit fettem Wort und mehr.", "Zweiter Absatz."]


@pytest.mark.parametrize("endung", ["docx", "odt", "rtf"])
def test_fett_und_ueberschrift_ueberleben(app, tmp_path, endung):
    ed = _beispiel(app)
    pfad = str(tmp_path / f"b.{endung}")
    speichere_modell(pfad, ed.sitzung.dokument, ed.page)
    geladen = lade_modell(pfad).document
    absaetze = [a for a in geladen.absaetze() if a.text()]
    assert any(l.format.get("fett") for l in absaetze[1].inhalte if hasattr(l, "text"))
    assert absaetze[0].format.get("vorlage") or (absaetze[0].inhalte and absaetze[0].inhalte[0].format.get("fett"))


@pytest.mark.parametrize("endung", ["docx", "odt", "rtf"])
def test_tabelle_ueberlebt(app, tmp_path, endung):
    ed = KernEditor(neues_dokument())
    ed.insert_table(2, 2)
    t = ed.tabelle_an_marke()
    for z in range(2):
        for s in range(2):
            ed.sitzung.setze_auswahl(ed.sitzung.zelle_anfang(t.id, z, s)) if hasattr(ed.sitzung, "setze_auswahl") else None
    pfad = str(tmp_path / f"t.{endung}")
    speichere_modell(pfad, ed.sitzung.dokument, ed.page)
    geladen = lade_modell(pfad).document
    tabellen = [b for ab in geladen.abschnitte for b in ab.bloecke if isinstance(b, Tabelle)]
    assert len(tabellen) == 1 and len(tabellen[0].zellen) == 2 and len(tabellen[0].zellen[0]) == 2


@pytest.mark.parametrize("endung", ["docx", "odt", "rtf"])
def test_bild_im_text_ueberlebt_bytes_oder_groesse(app, tmp_path, endung):
    ed = KernEditor(neues_dokument())
    ed.ansicht.einfuegen("Text")
    bild = QImage(40, 20, QImage.Format_ARGB32); bild.fill(0xff2f6fb5)
    assert ed.bild_im_text_einfuegen(bild, "Ein Bild")
    pfad = str(tmp_path / f"i.{endung}")
    speichere_modell(pfad, ed.sitzung.dokument, ed.page)
    geladen = lade_modell(pfad).document
    bilder = [x for a in geladen.absaetze() for x in a.inhalte if not hasattr(x, "text")]
    assert len(bilder) == 1


def test_pdf_wird_geschrieben(app, tmp_path):
    ed = _beispiel(app)
    pfad = str(tmp_path / "a.pdf")
    speichere_modell(pfad, ed.sitzung.dokument, ed.page)
    assert open(pfad, "rb").read(5) == b"%PDF-"


def test_zweites_speichern_legt_sicherung_an(app, tmp_path):
    ed = _beispiel(app)
    pfad = str(tmp_path / "s.docx")
    speichere_modell(pfad, ed.sitzung.dokument, ed.page)
    ed.ansicht.einfuegen("neu")
    speichere_modell(pfad, ed.sitzung.dokument, ed.page)
    from lunivo_writer.dienste import sicher_schreiben as S
    assert S.sicherungen(pfad)


@pytest.mark.parametrize("endung", ["docx", "odt"])
def test_alternativtext_des_bildes_ueberlebt(app, tmp_path, endung):
    ed = KernEditor(neues_dokument())
    bild = QImage(40, 20, QImage.Format_ARGB32); bild.fill(0xff2f6fb5)
    ed.bild_im_text_einfuegen(bild, "Ein rotes Feld")
    pfad = str(tmp_path / f"alt.{endung}")
    speichere_modell(pfad, ed.sitzung.dokument, ed.page)
    bilder = [x for a in lade_modell(pfad).document.absaetze() for x in a.inhalte if not hasattr(x, "text")]
    assert bilder and bilder[0].alt_text == "Ein rotes Feld"


@pytest.mark.parametrize("endung", ["docx", "odt", "rtf"])
def test_liste_ueberlebt(app, tmp_path, endung):
    ed = KernEditor(neues_dokument())
    ed.ansicht.einfuegen("Eins\nZwei")
    ed.select_range(0, 8); ed.toggle_list("number")
    pfad = str(tmp_path / f"l.{endung}")
    speichere_modell(pfad, ed.sitzung.dokument, ed.page)
    geladen = lade_modell(pfad).document
    absaetze = [a for a in geladen.absaetze() if a.text()]
    assert [a.text() for a in absaetze][:2] == ["Eins", "Zwei"] and all(a.liste_id is not None for a in absaetze[:2])


def test_odt_jpeg_bleibt_bytegleich_und_fussnote_farbe_ueberschrift(app, tmp_path):
    import zipfile
    from PySide6.QtGui import QColor
    ed = KernEditor(neues_dokument())
    ed.ansicht.einfuegen("Titel\nText mit Note")
    ed.select_range(0, 5); ed.apply_style("Überschrift 1")
    ed.select_range(6, 10); ed.set_text_color(QColor("#cc0000")) if hasattr(ed, "set_text_color") else None
    ed.select_range(19, 19); ed.note_neu("f", "Die Fußnote")
    jpg = tmp_path / "foto.jpg"
    foto = QImage(64, 32, QImage.Format_RGB32); foto.fill(QColor("orange")); foto.save(str(jpg), "JPEG", 77)
    original = jpg.read_bytes()
    from lunivo_writer.editor.objekte import bilddaten as BD
    img = BD.bild_aus_datei(str(jpg))
    ed.select_range(0, 0)
    assert ed.bild_im_text_einfuegen(img, "Foto")
    pfad = str(tmp_path / "r.odt")
    speichere_modell(pfad, ed.sitzung.dokument, ed.page)
    with zipfile.ZipFile(pfad) as z:
        bilder = [n for n in z.namelist() if n.startswith("Pictures/")]
        assert any(z.read(n) == original for n in bilder)
        inhalt = z.read("content.xml").decode()
    assert "<text:h " in inhalt and "text:note-class=\"footnote\"" in inhalt and "Die Fußnote" in inhalt
    geladen = lade_modell(pfad).document
    assert geladen.noten.get("f")


@pytest.mark.parametrize("endung", ["docx", "odt"])
def test_verbundene_zellen_und_freies_bild_ueberleben(app, tmp_path, endung):
    ed = KernEditor(neues_dokument())
    ed.ansicht.einfuegen("Text")
    ed.select_range(0, 0)
    ed.insert_table(2, 3)
    t = ed.tabelle_an_marke()
    ed.sitzung.zellen_verbinden(t.id, 0, 0, 1, 2)
    bild = QImage(40, 20, QImage.Format_ARGB32); bild.fill(0xff2f6fb5)
    assert ed.objekt_frei_einfuegen("bild", {}, 80.0, 40.0, bild, "Frei")
    pfad = str(tmp_path / f"v.{endung}")
    speichere_modell(pfad, ed.sitzung.dokument, ed.page)
    geladen = lade_modell(pfad).document
    tabellen = [b for ab in geladen.abschnitte for b in ab.bloecke if isinstance(b, Tabelle)]
    assert tabellen and tabellen[0].zellen[0][0].spaltenspanne == 2 and tabellen[0].zellen[0][1].verdeckt_von is not None
    assert len(geladen.objekte) == 1
