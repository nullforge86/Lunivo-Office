"""DOCX laden und speichern über das Dokumentenmodell (``core.document.Dokument``): Seiteneinrichtung, Noten, Übergabe an den Tab, Zeilenhöhen.

Das Modell wird ohne Qt-Textdokument gelesen und geschrieben; den früheren Rundlauf über ein Qt-Dokument gibt es nicht mehr (siehe ``test_dokumentmodell_neu.py``
und ``test_rundlauf_modell.py`` für den Rundlauf des Modells)."""
import os
import zipfile

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

DATEN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dokument", "formate", "daten", "lo_dokument.docx")


def test_docx_als_modell_laden(app):
    """Das Laden einer DOCX-Datei liefert das ``Dokument``: Seiteneinrichtung, Text und Noten sind da."""
    from lunivo_writer.dienste.modell_laden import lade_modell
    m = lade_modell(DATEN)
    assert m.page.width_mm == m.document.abschnitte[0].seite.width_mm and m.page.width_mm > 0
    assert m.document.text().strip()
    assert any(n.text == "Die Fußnote von LibreOffice." for n in m.document.noten["f"].values())


def test_normaler_docx_ladepfad_uebergibt_importiertes_modell_an_documenttab(app):
    from lunivo_writer.dienste.modell_laden import lade_modell
    from lunivo_writer.oberflaeche.dokument.dokumentfenster.dokument_bereich import DocumentTab
    geladen = lade_modell(DATEN)
    tab = DocumentTab(geladen, DATEN)
    tab.set_layout("kern")
    assert tab.editor.sitzung.dokument is geladen.document


def test_docx_zeilenhoehe_mindestens_und_genau_im_rundlauf(app, tmp_path):
    from docx import Document as WordDocument
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from lunivo_writer.core.document.dokument import Tabelle
    from lunivo_writer.dienste.modell_laden import lade_modell
    from lunivo_writer.dienste.modell_speichern import speichere_modell

    docx = WordDocument()
    t = docx.add_table(rows=2, cols=2)
    for ri, art in enumerate(("atLeast", "exact")):
        row = t.rows[ri]
        row.cells[0].text = f"Links {art}"
        row.cells[1].text = f"Rechts {art}"
        height = OxmlElement("w:trHeight")
        height.set(qn("w:val"), str(720 + ri * 240))
        height.set(qn("w:hRule"), art)
        row._tr.get_or_add_trPr().append(height)
    pfad = tmp_path / "zeilenhoehe.docx"
    docx.save(pfad)

    geladen = lade_modell(str(pfad))
    tab = next(b for b in geladen.document.abschnitte[0].bloecke if isinstance(b, Tabelle))
    assert tab.zeilenhoehen[0] == pytest.approx(48.0) and tab.zeilenhoehen[1] == pytest.approx(64.0)
    assert tab.format.get("zeilenhoehe_exakt") == [1]
    ausgabe = tmp_path / "zeilenhoehe_rundlauf.docx"
    speichere_modell(str(ausgabe), geladen.document, geladen.page, geladen.meta)
    zurueck = WordDocument(str(ausgabe))
    regeln = [r._tr.xpath("w:trPr/w:trHeight/@w:hRule")[0] for r in zurueck.tables[0].rows]
    assert regeln == ["atLeast", "exact"]
    assert zipfile.is_zipfile(ausgabe)
