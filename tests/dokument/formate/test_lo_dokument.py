"""Ein von einem fremden Programm erzeugtes DOCX (nicht von uns geschrieben) lässt sich lesen: Ausrichtung „start“, Fußnote, Kommentar,
nachverfolgte Änderungen, Textmarke, Tabelle.

Gelesen wird die mitgelieferte Referenzdatei ``daten/lo_dokument.docx``; das fremde Programm wird zum Testen nicht gebraucht. Sie entstand einmalig
aus dem unten stehenden ``FODT`` mit einem fremden Programm. Neu erzeugen nur, wenn sich ``FODT`` ändert."""
import os

from lunivo_writer.dienste import docx_leser
from lunivo_writer.editor.dokument import verweise
from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor

FODT = """<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:dc="http://purl.org/dc/elements/1.1/" office:version="1.3" office:mimetype="application/vnd.oasis.opendocument.text">
<office:body><office:text>
<text:tracked-changes text:track-changes="false">
 <text:changed-region text:id="ct1"><text:insertion><office:change-info><dc:creator>Berta</dc:creator><dc:date>2026-03-04T10:00:00</dc:date></office:change-info></text:insertion></text:changed-region>
 <text:changed-region text:id="ct2"><text:deletion><office:change-info><dc:creator>Carl</dc:creator><dc:date>2026-03-05T11:00:00</dc:date></office:change-info><text:p>alt</text:p></text:deletion></text:changed-region>
</text:tracked-changes>
<text:h text:outline-level="1">Kapitel Eins</text:h>
<text:p>Text mit Fußnote<text:note text:id="ftn1" text:note-class="footnote"><text:note-citation>1</text:note-citation><text:note-body><text:p>Die Fußnote von LibreOffice.</text:p></text:note-body></text:note> und <office:annotation><dc:creator>Ann</dc:creator><dc:date>2026-01-02T03:04:05</dc:date><text:p>Kommentar von LO</text:p></office:annotation>kommentiertem Wort<office:annotation-end/>.</text:p>
<text:p>Vorher <text:change-start text:change-id="ct1"/>eingefügt<text:change-end text:change-id="ct1"/> und <text:change text:change-id="ct2"/> danach <text:bookmark text:name="Marke1"/>Ziel<text:bookmark-end text:name="Marke1"/>.</text:p>
<table:table table:name="T1"><table:table-column table:number-columns-repeated="2"/><table:table-row><table:table-cell><text:p>A1</text:p></table:table-cell><table:table-cell><text:p>B1</text:p></table:table-cell></table:table-row></table:table>
<text:p>Ende</text:p>
</office:text></office:body></office:document>
"""

def test_von_fremdem_programm_erzeugtes_docx_lesen(app):
    daten = os.path.join(os.path.dirname(__file__), "daten", "lo_dokument.docx")
    d, p, meta, rep = docx_leser.read_docx(daten)  # früher: ValueError wegen w:jc="start"
    t = d.toPlainText()
    assert "Kapitel Eins" in t and "Text mit Fußnote1 und kommentiertem Wort." in t and "A1" in t and "Ende" in t
    assert list(meta["noten"]["f"].values()) == ["Die Fußnote von LibreOffice."]
    assert list(meta["kommentare"].values())[0]["text"] == "Kommentar von LO"
    e = DocumentEditor(); e.set_document_and_page(d, p); e.zusatz_binden(meta)
    arten = [(b["wert"], t[b["von"]:b["bis"]], b["cf"].stringProperty(0x100000 + 23)) for b in e.aenderungen()]
    assert arten == [("ins", "eingefügt", "Berta"), ("del", "alt", "Carl")]
    assert [t[b["von"]:b["bis"]] for b in e.kommentar_bereiche()] == ["kommentiertem Wort"]
    assert [m["name"] for m in verweise.lesezeichen_liste(e)] == ["Marke1"]
    assert not rep.warnings


def test_fodt_fussnote_bleibt_im_dokumentenmodell(app, tmp_path):
    from lunivo_writer.dienste.datei_dienst import load
    from lunivo_writer.dienste.modell_laden import lade_modell
    from lunivo_writer.core.layout import umbrechen
    from lunivo_writer.dienste.textsatz import standard_engine
    from lunivo_writer.dienste.odt_schreiber import odt_daten

    pfad = tmp_path / "mit_fussnote.fodt"
    pfad.write_text(FODT, encoding="utf-8")
    geladen = lade_modell(str(pfad))
    assert any(n.kind == "f" and n.text == "Die Fußnote von LibreOffice." for n in geladen.document.notes)
    seiten = umbrechen(geladen.document, standard_engine()).seiten
    assert any(p.art == "fussnote" for s in seiten for p in s.plaetze)
    quelle = load(str(pfad))
    daten, _bericht = odt_daten(quelle.doc, quelle.page, quelle.meta)
    ausgabe = tmp_path / "rundlauf.odt"
    ausgabe.write_bytes(daten)
    zurueck = load(str(ausgabe))
    assert list(zurueck.meta["noten"]["f"].values()) == ["Die Fußnote von LibreOffice."]


def test_fodt_freies_rechteck_wird_nativ_im_modell_gezeichnet(app, tmp_path):
    from lunivo_writer.dienste.datei_dienst import load
    from lunivo_writer.adapter.qt.seitenbild import seiten_aus_modell
    from lunivo_writer.dienste.modell_laden import lade_modell
    from lunivo_writer.dienste.odt_schreiber import odt_daten

    fodt = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
 xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
 xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
 xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
 office:version="1.3" office:mimetype="application/vnd.oasis.opendocument.text">
 <office:automatic-styles><style:style style:name="G1" style:family="graphic"><style:graphic-properties
 style:horizontal-rel="page" style:vertical-rel="page" style:horizontal-pos="from-left" style:vertical-pos="from-top"/></style:style></office:automatic-styles>
 <office:body><office:text><text:p>Zeichnung</text:p><draw:rect draw:style-name="G1" text:anchor-type="page"
 svg:x="20mm" svg:y="50mm" svg:width="20mm" svg:height="10mm" draw:fill="solid" draw:fill-color="#ff0000" draw:stroke="none"/>
 </office:text></office:body></office:document>'''
    pfad = tmp_path / "rechteck.fodt"
    pfad.write_text(fodt, encoding="utf-8")
    modell = lade_modell(str(pfad)).document
    bild = seiten_aus_modell(modell)[0]
    assert bild.pixelColor(110, 205).red() > 220 and bild.pixelColor(110, 205).green() < 60
    geladen = load(str(pfad))
    daten, _bericht = odt_daten(geladen.doc, geladen.page, geladen.meta)
    ausgabe = tmp_path / "rechteck_rundlauf.odt"
    ausgabe.write_bytes(daten)
    zurueck = lade_modell(str(ausgabe)).document
    bild_zurueck = seiten_aus_modell(zurueck)[0]
    assert bild_zurueck.pixelColor(110, 205).red() > 220 and bild_zurueck.pixelColor(110, 205).green() < 60
