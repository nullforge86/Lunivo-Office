"""PDF exportieren: das Fenster „PDF-Datei exportieren“ und der Dienst dahinter (Seitenbereich, Auswahl, Optionen, Kennwörter) — über das Dokumentenmodell."""
from pypdf import PdfReader
from pypdf.constants import UserAccessPermissions as U

from lunivo_writer.core.document.dokument import Auswahl, Position
from lunivo_writer.dienste import pdf_export as PE
from lunivo_writer.modelle.seite import HeaderFooter, PageSettings
from tests.hilfen_dokument import als_pdf, dokument, seiten_dokument, sitzung


def _text(r, i=0):
    return " ".join(r.pages[i].extract_text().split())


def _mit_link():
    """Ein Dokument, dessen Text mit dem verknüpften Wort „Link“ endet."""
    s = sitzung("Seite 1 ")
    a = next(iter(s.dokument.absaetze()))
    s.text_einfuegen("Link", pos=Position(a.id, a.laenge), format={"link": "https://example.org"})
    return s


def test_seitenbereich_und_markierung(app, tmp_path):
    d = seiten_dokument(3, "Seite {n} ")
    pfad = tmp_path / "a.pdf"
    als_pdf(d, pfad, erste=2, letzte=3)
    r = PdfReader(str(pfad))
    assert len(r.pages) == 2 and "Seite 2" in _text(r)
    assert PE.seiten(PE.PdfWahl(bereich="aktuell"), 2) == (2, 2)
    assert PE.seiten(PE.PdfWahl(bereich="seiten", von=3, bis=1), 1) == (1, 3)
    assert PE.seiten(PE.PdfWahl(), 2) == (1, None)
    erster = next(iter(d.absaetze()))
    teil = PE.nur_markierung(d, Auswahl(Position(erster.id, 0), Position(erster.id, 7)))
    assert "".join(a.text() for a in teil.absaetze()) == "Seite 1" and next(iter(d.absaetze())).text().startswith("Seite 1 ")


def test_pdf_export_behaelt_seitenbereich_titel_und_autor(app, tmp_path):
    d = seiten_dokument(3, "Modellseite {n}")
    pfad = tmp_path / "modell.pdf"
    assert als_pdf(d, pfad, "Modell-Titel", "Autor", erste=2, letzte=2) == 1
    r = PdfReader(str(pfad))
    assert len(r.pages) == 1 and "Modellseite 2" in _text(r)
    assert r.metadata.title == "Modell-Titel" and r.metadata.creator == "Autor"


def test_pdf_export_zeichnet_kopf_und_fusszeile(app, tmp_path):
    page = PageSettings()
    page.header = HeaderFooter(text="Verknuepfte Kopfzeile")
    page.footer = HeaderFooter(text="Verknuepfte Fusszeile")
    pfad = tmp_path / "kopf_fuss_modell.pdf"
    assert als_pdf(dokument("Dokumenttext", page), pfad) == 1
    text = _text(PdfReader(str(pfad)))
    assert "Verknuepfte Kopfzeile" in text and "Verknuepfte Fusszeile" in text


def test_druck_beachtet_seitenwahl(app, tmp_path):
    from PySide6.QtPrintSupport import QPrinter
    from lunivo_writer.dienste.drucken import drucken
    d = seiten_dokument(3, "Druckseite {n}")
    printer = QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setResolution(144)
    printer.setOutputFileName(str(tmp_path / "druck.pdf"))
    assert drucken(printer, d, {"bereich": "seiten", "seiten_text": "3"}) == 1
    r = PdfReader(str(tmp_path / "druck.pdf"))
    assert len(r.pages) == 1
    assert "Druckseite 3" in _text(r) and "Druckseite 2" not in _text(r)


def test_ohne_hyperlinks_und_mit_lesezeichen(app, tmp_path):
    s = _mit_link()
    a = next(iter(s.dokument.absaetze()))
    s.absatzformat_anwenden({"gliederungsebene": 1}, absatz_ids=[a.id])
    mit, ohne = tmp_path / "mit.pdf", tmp_path / "ohne.pdf"
    als_pdf(s.dokument, mit, struktur={"lesezeichen": {"ueberschriften": True}, "hyperlinks": True})
    als_pdf(s.dokument, ohne, struktur={"lesezeichen": None, "hyperlinks": False})
    r_mit, r_ohne = PdfReader(str(mit)), PdfReader(str(ohne))
    links = lambda r: [x.get_object() for x in (r.pages[0].get("/Annots") or [])]
    assert any(x.get("/Subtype") == "/Link" for x in links(r_mit)) and not links(r_ohne)
    assert [o.title for o in r_mit.outline] and not r_ohne.outline
    assert a.text().endswith("Link")                                   # das Original bleibt unverändert


def test_berechtigungen_und_kennwort(app, tmp_path):
    w = PE.PdfWahl(verschluesseln=True, kennwort_rechte="chef", kennwort_oeffnen="lesen", kopieren=False, druck="niedrig")
    rechte = PE.berechtigungen(w)
    assert not rechte & U.EXTRACT and rechte & U.PRINT and not rechte & U.PRINT_TO_REPRESENTATION and rechte & U.MODIFY
    assert not PE.berechtigungen(PE.PdfWahl(druck="kein")) & U.PRINT
    pfad = tmp_path / "k.pdf"
    als_pdf(dokument("Seite 1"), pfad)
    PE.verschluesseln(str(pfad), w)
    r = PdfReader(str(pfad))
    assert r.is_encrypted and not r.decrypt("falsch") and r.decrypt("lesen")
    assert "Seite 1" in _text(r)
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
    w.new_document(); w.current_editor().textCursor().insertText("Geheim")
    ziel = str(tmp_path / "g.pdf")

    ansicht = w.pdf_export_widget()                          # der PDF-Export ist eine Seite im Datei-Menü, kein eigenes Fenster
    ansicht.pfad.setText(ziel); ansicht.verschluesseln.setChecked(True)
    ansicht.oeffnen_kw.setText("pw"); ansicht.oeffnen_kw2.setText("pw"); ansicht.optionen["kommentare"].setChecked(True)
    ansicht.ok.click()
    r = PdfReader(ziel)
    assert r.is_encrypted and r.decrypt("pw") and "Geheim" in r.pages[0].extract_text()
    assert w.settings.get_bool("pdf/kommentare", False) and not any("pw" in str(w.settings.get(k, "")) for k in ("pdf/kennwort",))
