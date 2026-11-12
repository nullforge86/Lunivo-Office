"""PDF exportieren: das Fenster „PDF-Datei exportieren“ und der Dienst dahinter (Seitenbereich, Optionen, Kennwörter)."""
from pypdf import PdfReader
from pypdf.constants import UserAccessPermissions as U
from PySide6.QtGui import QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument

from lunivo_writer.editor.seite.seiten_aufteilung import export_pdf
from lunivo_writer.modelle.seite import PageSettings
from lunivo_writer.dienste import pdf_export as PE
from lunivo_writer.dienste.docx_leser import STYLE_PROP


def _dokument(seiten: int = 1) -> QTextDocument:
    d = QTextDocument()
    c = QTextCursor(d)
    for i in range(seiten):
        if i:
            bf = QTextBlockFormat(); bf.setPageBreakPolicy(QTextBlockFormat.PageBreak_AlwaysBefore); c.insertBlock(bf)
        c.insertText(f"Seite {i + 1} ")
    f = QTextCharFormat(); f.setAnchor(True); f.setAnchorHref("https://example.org")
    c.insertText("Link", f)
    return d


def test_seitenbereich_und_markierung(app, tmp_path):
    d = _dokument(3)
    pfad = tmp_path / "a.pdf"
    export_pdf(str(pfad), d, PageSettings(), erste=2, letzte=3)
    r = PdfReader(str(pfad))
    assert len(r.pages) == 2 and "Seite 2" in " ".join(r.pages[0].extract_text().split())
    assert PE.seiten(PE.PdfWahl(bereich="aktuell"), 2) == (2, 2)
    assert PE.seiten(PE.PdfWahl(bereich="seiten", von=3, bis=1), 1) == (1, 3)
    assert PE.seiten(PE.PdfWahl(), 2) == (1, None)
    teil = PE.nur_markierung(d, 0, 7)
    assert teil.toPlainText() == "Seite 1" and d.toPlainText().startswith("Seite 1 ")


def test_einfacher_pdf_export_nutzt_dokumentenmodell_und_behaelt_seitenbereich(app, tmp_path, monkeypatch):
    import lunivo_writer.editor.seite.seiten_aufteilung as SA
    d = QTextDocument()
    c = QTextCursor(d)
    for i in range(3):
        if i:
            bf = QTextBlockFormat(); bf.setPageBreakPolicy(QTextBlockFormat.PageBreak_AlwaysBefore); c.insertBlock(bf)
        c.insertText(f"Modellseite {i + 1}")
    monkeypatch.setattr(SA, "render_dokument", lambda *a, **k: (_ for _ in ()).throw(AssertionError("Qt-Rückfall unerwartet")))
    pfad = tmp_path / "modell.pdf"
    assert export_pdf(str(pfad), d, PageSettings(), "Modell-Titel", "Autor", extra={"hyperlinks": True}, erste=2, letzte=2) == 1
    r = PdfReader(str(pfad))
    assert len(r.pages) == 1 and "Modellseite 2" in " ".join(r.pages[0].extract_text().split())
    assert r.metadata.title == "Modell-Titel"
    assert r.xmp_metadata.dc_creator == ["Autor"]


def test_modell_pdf_export_zeichnet_verknuepfte_kopf_und_fusszeile(app, tmp_path, monkeypatch):
    import lunivo_writer.editor.seite.seiten_aufteilung as SA
    from lunivo_writer.modelle.seite import HeaderFooter

    d = QTextDocument()
    d.setPlainText("Dokumenttext")
    page = PageSettings()
    page.header = HeaderFooter(text="Verknuepfte Kopfzeile")
    page.footer = HeaderFooter(text="Verknuepfte Fusszeile")
    page.kopf_verknuepft = True
    page.fuss_verknuepft = True
    monkeypatch.setattr(SA, "render_dokument", lambda *a, **k: (_ for _ in ()).throw(AssertionError("Qt-Rückfall unerwartet")))
    pfad = tmp_path / "kopf_fuss_modell.pdf"
    assert export_pdf(str(pfad), d, page) == 1
    text = " ".join(PdfReader(str(pfad)).pages[0].extract_text().split())
    assert "Verknuepfte Kopfzeile" in text
    assert "Verknuepfte Fusszeile" in text


def test_druckpfad_modellrenderer_beachtet_druckerbereich_und_nur_seiten(app, tmp_path, monkeypatch):
    from PySide6.QtPrintSupport import QPrinter
    import lunivo_writer.editor.seite.seiten_aufteilung as SA
    from lunivo_writer.editor.seite.seiten_aufteilung import print_document

    d = QTextDocument()
    c = QTextCursor(d)
    for i in range(3):
        if i:
            bf = QTextBlockFormat(); bf.setPageBreakPolicy(QTextBlockFormat.PageBreak_AlwaysBefore); c.insertBlock(bf)
        c.insertText(f"Druckseite {i + 1}")
    printer = QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setResolution(144)
    printer.setOutputFileName(str(tmp_path / "druck.pdf"))
    printer.setPrintRange(QPrinter.PageRange)
    printer.setFromTo(2, 3)
    monkeypatch.setattr(SA, "render_dokument", lambda *a, **k: (_ for _ in ()).throw(AssertionError("Qt-Rückfall unerwartet")))

    assert print_document(printer, d, PageSettings(), {"nur_seiten": {3}}) == 3
    r = PdfReader(str(tmp_path / "druck.pdf"))
    assert len(r.pages) == 1
    text = " ".join(r.pages[0].extract_text().split())
    assert "Druckseite 3" in text and "Druckseite 2" not in text


def test_ohne_hyperlinks_und_eigene_formatvorlagen(app, tmp_path):
    d = _dokument()
    c = QTextCursor(d); c.movePosition(QTextCursor.End)
    bf = QTextBlockFormat(); bf.setProperty(STYLE_PROP, "x:Mein Stil"); c.insertBlock(bf); c.insertText("Eigener Abschnitt")
    mit, ohne = tmp_path / "mit.pdf", tmp_path / "ohne.pdf"
    export_pdf(str(mit), d, PageSettings(), extra={"hyperlinks": True}, lesezeichen={"eigene": True})
    export_pdf(str(ohne), d, PageSettings(), extra={"hyperlinks": False}, lesezeichen={"andere": True})
    r_mit, r_ohne = PdfReader(str(mit)), PdfReader(str(ohne))
    links = lambda r: [a.get_object() for a in (r.pages[0].get("/Annots") or [])]
    assert any(a.get("/Subtype") == "/Link" for a in links(r_mit)) and not links(r_ohne)
    assert [o.title for o in r_mit.outline] == ["Eigener Abschnitt"] and not r_ohne.outline
    assert d.toPlainText().endswith("Eigener Abschnitt")                 # das Original behält seinen Link
    assert any(it.fragment().charFormat().anchorHref() for it in _fragmente(d))


def _fragmente(d):
    b = d.firstBlock()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            yield it
            it += 1
        b = b.next()


def test_berechtigungen_und_kennwort(app, tmp_path):
    w = PE.PdfWahl(verschluesseln=True, kennwort_rechte="chef", kennwort_oeffnen="lesen", kopieren=False, druck="niedrig")
    rechte = PE.berechtigungen(w)
    assert not rechte & U.EXTRACT and rechte & U.PRINT and not rechte & U.PRINT_TO_REPRESENTATION and rechte & U.MODIFY
    assert not PE.berechtigungen(PE.PdfWahl(druck="kein")) & U.PRINT
    pfad = tmp_path / "k.pdf"
    export_pdf(str(pfad), _dokument(), PageSettings())
    PE.verschluesseln(str(pfad), w)
    r = PdfReader(str(pfad))
    assert r.is_encrypted and not r.decrypt("falsch") and r.decrypt("lesen")
    assert "Seite 1" in " ".join(r.pages[0].extract_text().split())
    assert PE.kennwort_fehler(w, "chef", "lesen") == ""
    assert "stimmen nicht" in PE.kennwort_fehler(w, "chef", "lesn")
    assert "mindestens ein Kennwort" in PE.kennwort_fehler(PE.PdfWahl(verschluesseln=True), "", "")


def test_fenster_liefert_wahl_und_prueft_kennwort(app, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    from lunivo_writer.oberflaeche.baukasten.dokument.pdf_export import PdfExportAnsicht
    exportiert, warnungen = [], []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: warnungen.append(a[2]))
    f = PdfExportAnsicht(None, PE.PdfWahl(pfad=str(tmp_path / "x.pdf"), schliessen=False), 4, 2, False,
                         lambda w: exportiert.append(w) or True, lambda: None)
    assert not f.b_markierung.isEnabled() and f.b_alles.isChecked() and not f.von.isEnabled() and f.bis.value() == 4
    f.b_seiten.setChecked(True); f.von.setValue(2); f.bis.setValue(3)
    f.optionen["hyperlinks"].setChecked(False)
    f.verschluesseln.setChecked(True); f.oeffnen_kw.setText("a"); f.oeffnen_kw2.setText("b")
    f.ok.click()
    assert not exportiert and warnungen and f.schutz_knopf.isChecked()       # Kennwörter stimmen nicht: Abschnitt „Schutz“ wird geöffnet
    f.oeffnen_kw2.setText("a"); f.druck.setCurrentIndex(2)
    f.ok.click()
    w = exportiert[-1]
    assert (w.bereich, w.von, w.bis, w.hyperlinks, w.kennwort_oeffnen, w.druck) == ("seiten", 2, 3, False, "a", "kein")
    assert f.meldung.isVisibleTo(f) and f.wahl() is w                       # bleibt offen, zeigt, was geschrieben wurde


def test_export_aus_dem_hauptfenster_verschluesselt(app, tmp_path, monkeypatch):
    from PySide6.QtCore import QSettings
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.programmfenster import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.current_editor().insertPlainText("Geheim")
    ziel = str(tmp_path / "g.pdf")

    ansicht = w.pdf_export_widget()                          # der PDF-Export ist eine Seite im Datei-Menü, kein eigenes Fenster
    ansicht.pfad.setText(ziel); ansicht.verschluesseln.setChecked(True)
    ansicht.oeffnen_kw.setText("pw"); ansicht.oeffnen_kw2.setText("pw"); ansicht.optionen["kommentare"].setChecked(True)
    ansicht.ok.click()
    r = PdfReader(ziel)
    assert r.is_encrypted and r.decrypt("pw") and "Geheim" in r.pages[0].extract_text()
    assert w.settings.get_bool("pdf/kommentare", False) and not any("pw" in str(w.settings.get(k, "")) for k in ("pdf/kennwort",))
