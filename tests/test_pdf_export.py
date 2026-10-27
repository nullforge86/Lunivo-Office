"""PDF exportieren: das Fenster „PDF-Datei exportieren“ und der Dienst dahinter (Seitenbereich, Optionen, Kennwörter)."""
from pypdf import PdfReader
from pypdf.constants import UserAccessPermissions as U
from PySide6.QtGui import QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument

from lunivo_writer.editor.pagination import export_pdf
from lunivo_writer.models.page import PageSettings
from lunivo_writer.services import pdf_export as PE
from lunivo_writer.services.docx_reader import STYLE_PROP


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
    from lunivo_writer.ui.baukasten.pdf_export import PdfExportFenster
    exportiert, warnungen = [], []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: warnungen.append(a[2]))
    f = PdfExportFenster(None, PE.PdfWahl(pfad=str(tmp_path / "x.pdf"), schliessen=False), 4, 2, False,
                         lambda w: exportiert.append(w) or True)
    assert not f.b_markierung.isEnabled() and f.b_alles.isChecked() and not f.von.isEnabled() and f.bis.value() == 4
    f.b_seiten.setChecked(True); f.von.setValue(2); f.bis.setValue(3)
    f.optionen["hyperlinks"].setChecked(False)
    f.verschluesseln.setChecked(True); f.oeffnen_kw.setText("a"); f.oeffnen_kw2.setText("b")
    f.ok.click()
    assert not exportiert and warnungen and f.reiter.currentIndex() == 1
    f.oeffnen_kw2.setText("a"); f.druck.setCurrentIndex(2)
    f.ok.click()
    w = exportiert[-1]
    assert (w.bereich, w.von, w.bis, w.hyperlinks, w.kennwort_oeffnen, w.druck) == ("seiten", 2, 3, False, "a", "kein")
    assert f.meldung.isVisibleTo(f) and f.wahl() is w                       # bleibt offen, zeigt, was geschrieben wurde


def test_export_aus_dem_hauptfenster_verschluesselt(app, tmp_path, monkeypatch):
    from PySide6.QtCore import QSettings
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.baukasten import pdf_export as PF
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.current_editor().insertPlainText("Geheim")
    ziel = str(tmp_path / "g.pdf")

    def ok(fenster):
        fenster.pfad.setText(ziel); fenster.verschluesseln.setChecked(True)
        fenster.oeffnen_kw.setText("pw"); fenster.oeffnen_kw2.setText("pw"); fenster.optionen["kommentare"].setChecked(True)
        fenster.ok.click()
        return 0
    monkeypatch.setattr(PF.PdfExportFenster, "exec", ok)
    w.export_pdf_dialog()
    r = PdfReader(ziel)
    assert r.is_encrypted and r.decrypt("pw") and "Geheim" in r.pages[0].extract_text()
    assert w.settings.get_bool("pdf/kommentare", False) and not any("pw" in str(w.settings.get(k, "")) for k in ("pdf/kennwort",))
