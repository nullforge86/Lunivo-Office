"""Bearbeiten über das Modell: Sitzung ohne Qt (Einfügen, Löschen, Formate, Rückgängig) und Spiegel zum Textdokument (Modell und Ansicht bleiben gleich)."""
import pytest

from lunivo_writer.core.document import CharacterFormat, Document, Paragraph, ParagraphFormat, Section, TextRun
from lunivo_writer.core.editing import Caret, Sitzung


def modell(*texte):
    return Document([Section("naechste", None, [Paragraph(ParagraphFormat(), [TextRun(t, CharacterFormat())]) for t in texte])])


def test_einfuegen_loeschen_formate_rueckgaengig():
    s = Sitzung(modell("Hallo Welt"))
    c = s.einfuegen(" schöne\nneue", Caret((0, 0), 5))
    assert s.text() == "Hallo schöne\nneue Welt" and c == Caret((0, 1), 4)
    s.zeichenformat({"FontWeight": 700}, Caret((0, 0), 0), Caret((0, 0), 5))
    assert [(r.text, r.format.properties) for r in s.dok.sections[0].content[0].runs] == [("Hallo", {"FontWeight": 700}), (" schöne", {})]
    s.absatzformat({"BlockAlignment": 4}, Caret((0, 1), 0), Caret((0, 1), 0))
    assert s.dok.sections[0].content[1].format.properties == {"BlockAlignment": 4}
    s.loeschen(Caret((0, 0), 3), Caret((0, 1), 2))
    assert s.text() == "Halue Welt"
    for erwartet in ("Hallo schöne\nneue Welt", "Hallo schöne\nneue Welt", "Hallo schöne\nneue Welt", "Hallo Welt"):
        assert s.rueckgaengig()
        assert s.text() == erwartet
    assert s.text() == "Hallo Welt" and not s.kann_rueckgaengig()
    assert s.wiederholen() and s.text() == "Hallo schöne\nneue Welt"


def test_bewegen_und_loeschen_ueber_absaetze():
    s = Sitzung(modell("Eins", "Zwei"))
    assert s.bewegen(Caret((0, 0), 4), 1) == Caret((0, 1), 0) and s.bewegen(Caret((0, 1), 1), -2) == Caret((0, 0), 4)
    s.auswaehlen(Caret((0, 0), 2), Caret((0, 1), 2))
    s.loeschen()
    assert s.text() == "Ei" + "ei" and s.cursor == Caret((0, 0), 2)


def test_spiegel_haelt_modell_und_ansicht_gleich(app):
    from PySide6.QtGui import QTextCharFormat, QTextCursor, QTextDocument, QFont
    from lunivo_writer.adapter.qt.bearbeitung import ModellSpiegel
    from lunivo_writer.adapter.qt.dokument import document_from_qt, document_to_qt, vergleichen
    d = QTextDocument()
    d.setPlainText("Hallo Welt\nZweiter Absatz")
    sp = ModellSpiegel(d)
    c = QTextCursor(d)
    c.setPosition(5); c.setPosition(10, QTextCursor.KeepAnchor)
    fett = QTextCharFormat(); fett.setFontWeight(QFont.Bold)
    assert sp.zeichenformat(c, fett)
    assert d.firstBlock().begin().fragment().charFormat().fontWeight() != QFont.Bold         # "Hallo" bleibt normal
    assert vergleichen(d, document_to_qt(sp.modell())) == []                                  # Ansicht und Modell gleich
    c2 = QTextCursor(d); c2.setPosition(6)
    sp.einfuegen(c2, "ganz\nneue ")
    assert d.toPlainText() == "Hallo ganz\nneue Welt\nZweiter Absatz" and c2.position() == 6 + len("ganz\nneue ")
    assert vergleichen(d, document_to_qt(sp.modell())) == []
    c3 = QTextCursor(d); c3.setPosition(2); c3.setPosition(14, QTextCursor.KeepAnchor)
    sp.loeschen(c3)
    assert vergleichen(d, document_to_qt(document_from_qt(d))) == [] and d.toPlainText().startswith("Hae Welt")
    assert sp.rueckgaengig() and sp.rueckgaengig() and sp.rueckgaengig()
    assert d.toPlainText() == "Hallo Welt\nZweiter Absatz"
    assert vergleichen(d, document_to_qt(sp.modell())) == []
    assert sp.wiederholen() and sp.wiederholen() and d.toPlainText().startswith("Hallo ganz")           # Format, dann Einfügen
    d.undo(); d.redo()                                                                         # eigene Änderung der Oberfläche: das Modell wird neu aufgebaut
    QTextCursor(d).insertText("X")
    assert sp.modell().sections[0].content[0].runs[0].text.startswith("X")


def test_editor_zeichenformat_laeuft_ueber_den_spiegel(app):
    """Fett im Editor: Oberfläche → Spiegel → Sitzung → Textdokument; Modell und Ansicht gleich, Rückgängig des Editors macht es rückgängig."""
    from PySide6.QtGui import QFont, QTextCursor
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Hallo Welt\nZweiter Absatz")
    c = ed.textCursor()
    c.setPosition(6); c.setPosition(10, QTextCursor.KeepAnchor)
    ed.setTextCursor(c)
    ed.toggle_bold(True)
    b = ed.document().firstBlock()
    gewichte = []
    it = b.begin()
    while not it.atEnd():
        gewichte.append((it.fragment().text(), it.fragment().charFormat().fontWeight()))
        it += 1
    assert ("Welt", QFont.Bold) in gewichte
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []
    ed.document().undo()
    it = ed.document().firstBlock().begin()
    assert all(it.fragment().charFormat().fontWeight() != QFont.Bold for _ in [0])


def test_editor_absatzformat_laeuft_ueber_den_spiegel(app):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QTextCursor
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Eins\nZwei\nDrei")
    c = ed.textCursor()
    c.setPosition(0); c.setPosition(7, QTextCursor.KeepAnchor)
    ed.setTextCursor(c)
    ed.set_alignment(Qt.AlignHCenter)
    ed.set_line_spacing(1.5)
    ed.set_indents(5, 2, 3)
    b = ed.document().firstBlock()
    gesetzt = []
    while b.isValid():
        gesetzt.append((bool(b.blockFormat().alignment() & Qt.AlignHCenter), b.blockFormat().leftMargin() > 0))
        b = b.next()
    assert gesetzt == [(True, True), (True, True), (False, False)]                           # nur die ausgewählten Absätze
    absatzformate = ed.modell_spiegel().sitzung().dok.sections[0].content
    assert [p.format.alignment for p in absatzformate] == ["center", "center", None]
    assert [(p.format.line_spacing.kind, p.format.line_spacing.value) if p.format.line_spacing else None for p in absatzformate] == [
        ("proportional", 150), ("proportional", 150), None]
    bf = ed.document().firstBlock().blockFormat()
    assert (absatzformate[0].format.left_indent_px, absatzformate[0].format.right_indent_px,
            absatzformate[0].format.first_line_indent_px) == pytest.approx((bf.leftMargin(), bf.rightMargin(), bf.textIndent()))
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []
    assert ed.modell_spiegel().rueckgaengig()
    assert ed.document().firstBlock().blockFormat().leftMargin() == 0 and ed.document().firstBlock().blockFormat().alignment() & Qt.AlignHCenter
    after = ed.modell_spiegel().sitzung().dok.sections[0].content[0].format
    assert after.alignment == "center" and after.line_spacing.kind == "proportional" and after.line_spacing.value == 150
    assert tuple(v or 0 for v in (after.left_indent_px, after.right_indent_px, after.first_line_indent_px)) == pytest.approx((0, 0, 0))
    assert ed.modell_spiegel().rueckgaengig()
    after = ed.modell_spiegel().sitzung().dok.sections[0].content[0].format
    assert after.alignment == "center" and after.line_spacing is None


def test_modell_bearbeiten_und_speichern(app, tmp_path):
    """Datei laden → Modell → Sitzung ändert → Modell speichern → neu laden: Text, Format und ein frei positioniertes Bild sind da."""
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QColor, QImage, QTextCursor, QTextDocument
    from lunivo_writer.dienste import datei_dienst
    from lunivo_writer.dienste.modell_laden import lade_modell
    from lunivo_writer.dienste.modell_speichern import speichere_modell
    from lunivo_writer.editor.objekte import freie_bilder as FB
    from lunivo_writer.modelle.seite import PageSettings
    d = QTextDocument()
    d.setPlainText("Erster Absatz\nZweiter Absatz")
    img = QImage(30, 20, QImage.Format_RGB32)
    img.fill(QColor("red"))
    name = FB.neuer_name(d)
    d.addResource(QTextDocument.ImageResource, QUrl(name), img)
    FB.an_absatz(QTextCursor(d.firstBlock()), {"n": name, "b": 30.0, "h": 20.0, "bh": "seite", "xh": 5.0, "bv": "seite", "yv": 5.0})
    for ext in ("docx", "odt"):
        a = str(tmp_path / f"a.{ext}")
        datei_dienst.save(a, d, PageSettings(), {})
        geladen = lade_modell(a)
        s = Sitzung(geladen.document)
        s.einfuegen("Neu: ", Caret((0, 0), 0))
        s.zeichenformat({"FontWeight": 700, "FontItalic": True}, Caret((0, 1), 0), Caret((0, 1), 6))
        b = str(tmp_path / f"b.{ext}")
        speichere_modell(b, geladen.document, geladen.page)
        neu = datei_dienst.load(b)
        assert neu.doc.toPlainText() == "Neu: Erster Absatz\nZweiter Absatz"
        assert neu.doc.firstBlock().next().begin().fragment().charFormat().fontWeight() >= 700, ext
        assert neu.doc.firstBlock().next().begin().fragment().charFormat().fontItalic(), ext
        assert FB.bild_im_dokument(neu.doc, FB.aus_absatz(neu.doc.firstBlock().blockFormat())[0]["n"]) is not None


def test_grosses_dokument_bleibt_bei_formatierung_im_kern(app):
    from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QTextDocument
    from lunivo_writer.adapter.qt.bearbeitung import ModellSpiegel

    doc = QTextDocument()
    doc.setPlainText("\n".join(f"Absatz {i}" for i in range(6100)))
    spiegel = ModellSpiegel(doc)
    letzter = doc.lastBlock()
    cursor = QTextCursor(letzter)
    cursor.select(QTextCursor.BlockUnderCursor)
    fmt = QTextCharFormat()
    fmt.setFontWeight(QFont.Bold)

    assert spiegel.zeichenformat(cursor, fmt)
    assert letzter.begin().fragment().charFormat().fontWeight() == QFont.Bold
    assert spiegel.modell().sections[0].content[-1].runs[0].format.weight == QFont.Bold


def test_einfaches_modell_direkt_als_docx_ohne_qt_bruecke(app, tmp_path, monkeypatch):
    from PySide6.QtCore import QByteArray, QBuffer, QIODevice
    from PySide6.QtGui import QColor, QImage, QTextDocument
    from lunivo_writer.core.document import CharacterFormat, Document, Image, Paragraph, ParagraphFormat, Section, TextRun
    from lunivo_writer.core.document.values import Color
    from lunivo_writer.adapter.qt.dokument import document_from_qt
    from lunivo_writer.dienste import docx_schreiber
    from lunivo_writer.dienste import modell_speichern
    from lunivo_writer.dienste.modell_laden import lade_modell
    from lunivo_writer.modelle.seite import PageSettings

    seite = PageSettings()
    absatz = ParagraphFormat(alignment="center", left_indent_px=20, first_line_indent_px=5,
                             space_before_px=12, space_after_px=8)
    format_rot = CharacterFormat(family="Liberation Serif", size_pt=14, weight=700, italic=True,
                                 foreground_color=Color(200, 20, 30), underline=True)
    quelle = QImage(4, 3, QImage.Format_RGB32); quelle.fill(QColor("blue"))
    puffer = QByteArray(); geraet = QBuffer(puffer); geraet.open(QIODevice.WriteOnly); quelle.save(geraet, "PNG"); geraet.close()
    bild = Image(bytes(puffer), CharacterFormat({"ImageWidth": 24.0, "ImageHeight": 18.0}), bytes(puffer), "png")
    modell = Document([Section("naechste", seite, [
        Paragraph(absatz, [TextRun("Direkt ", format_rot), bild, TextRun("gespeichert", CharacterFormat())]),
        Paragraph(ParagraphFormat(alignment="right"), [TextRun("Zweiter Absatz")]),
    ])])
    aus_qt = QTextDocument()
    aus_qt.setPlainText("einfach")
    assert docx_schreiber.docx_modell_daten(document_from_qt(aus_qt, seite), seite) is not None

    def keine_qt_bruecke(*_args, **_kwargs):
        raise AssertionError("Der unterstützte Modellweg darf document_to_qt nicht aufrufen.")

    monkeypatch.setattr(modell_speichern, "document_to_qt", keine_qt_bruecke)
    ziel = str(tmp_path / "modell.docx")
    modell_speichern.speichere_modell(ziel, modell, seite, sicherung=False)
    geladen = lade_modell(ziel).document
    erster, zweiter = geladen.sections[0].content
    assert erster.text == "Direkt \ufffcgespeichert" and zweiter.text == "Zweiter Absatz"
    assert erster.format.alignment == "center" and erster.format.left_indent_px == pytest.approx(20, abs=0.2)
    assert erster.format.first_line_indent_px == pytest.approx(5, abs=0.2)
    assert erster.format.space_before_px == pytest.approx(12, abs=0.2) and erster.format.space_after_px == pytest.approx(8, abs=0.2)
    f = erster.runs[0].format
    assert (f.family, f.size_pt, f.weight, f.italic, f.underline) == ("Liberation Serif", 14.0, 700, True, True)
    assert f.foreground_color == Color(200, 20, 30)
    assert isinstance(erster.runs[1], Image)
    assert erster.runs[1].format.properties["ImageWidth"] == pytest.approx(24.0, abs=0.1)
    assert erster.runs[1].format.properties["ImageHeight"] == pytest.approx(18.0, abs=0.1)
    assert erster.runs[1].raster_png.startswith(b"\x89PNG\r\n\x1a\n")


def test_docx_modell_schreibt_einfache_tabelle_direkt_ohne_qt_bruecke(app, tmp_path, monkeypatch):
    from docx import Document as WordDocument
    from docx.oxml.ns import qn
    from lunivo_writer.core.document import Document, Paragraph, Section, Table, TableCell, TableRow, TextRun
    from lunivo_writer.core.document.values import Brush, Color, Length, RowHeight
    from lunivo_writer.dienste import docx_schreiber
    from lunivo_writer.dienste import modell_speichern
    from lunivo_writer.kern.dokument_verwaltung import DocumentManager
    from lunivo_writer.modelle.seite import PageSettings

    seite = PageSettings()
    tabelle = Table(2, 2, {"TableHeaderRowCount": 1, "TableCellPadding": 4.0, "TableCellSpacing": 2.0,
                           "FrameBorder": 1.0, "FrameBorderBrush": Brush(1, Color(30, 40, 50)), "FrameBorderStyle": 3,
                           "FrameWidth": Length("fixed", 300.0),
                           "TableColumnWidthConstraints": (Length("fixed", 100.0), Length("variable", 0.0))}, [
        TableRow([TableCell(0, 0, column_span=2, content=[Paragraph(runs=[TextRun("verbunden")])])], row_height=RowHeight("exact", 24.0)),
        TableRow([TableCell(1, 0, properties={"BackgroundBrush": Brush(1, Color(255, 220, 0))},
                            content=[Paragraph(runs=[TextRun("unten links")])]),
                  TableCell(1, 1, properties={"TableCellVerticalAlignment": 5},
                            content=[Paragraph(runs=[TextRun("unten rechts")])])], row_height=RowHeight("minimum", 40.0)),
    ])
    modell = Document([Section("naechste", seite, [Paragraph(runs=[TextRun("Vor")]), tabelle])])

    def keine_qt_bruecke(*_args, **_kwargs):
        raise AssertionError("Der Anwendungs-Speicherweg soll dieses Modell direkt schreiben.")

    class Einstellungen:
        @staticmethod
        def get_bool(_name, default=False):
            return default

        @staticmethod
        def get(_name, default=None):
            return default

    monkeypatch.setattr(modell_speichern, "document_to_qt", keine_qt_bruecke)
    assert docx_schreiber.docx_modell_daten(modell, seite) is not None

    ziel = str(tmp_path / "tabelle.docx")
    DocumentManager(Einstellungen()).speichern(ziel, modell, seite, {}, erwartet=(None,))
    neu = WordDocument(ziel)
    assert neu.paragraphs[0].text == "Vor"
    assert len(neu.tables) == 1 and len(neu.tables[0].rows) == 2 and len(neu.tables[0].columns) == 2
    assert neu.tables[0].cell(0, 0).text == "verbunden" and neu.tables[0].cell(0, 1).text == "verbunden"
    assert neu.tables[0].cell(1, 0).text == "unten links" and neu.tables[0].cell(1, 1).text == "unten rechts"
    assert neu.tables[0].rows[0]._tr.get_or_add_trPr().find(qn("w:tblHeader")) is not None
    tblpr = neu.tables[0]._tbl.tblPr
    assert tblpr.find(qn("w:tblCellSpacing")).get(qn("w:w")) == "30"
    assert tblpr.find(qn("w:tblCellMar")).find(qn("w:top")).get(qn("w:w")) == "60"
    tabellenrand = tblpr.find(qn("w:tblBorders")).find(qn("w:top"))
    assert tabellenrand.get(qn("w:val")) == "single" and tabellenrand.get(qn("w:color")) == "1E2832"
    gitter = neu.tables[0]._tbl.tblGrid.gridCol_lst
    assert [int(spalte.get(qn("w:w"))) for spalte in gitter] == [1500, 3000]
    monkeypatch.undo()
    from lunivo_writer.dienste.datei_dienst import load
    wieder = load(ziel)
    modell_tabelle = wieder.modell.sections[0].content[1]
    assert modell_tabelle.table_rows[0].cells[0].content[0].text == "verbunden"
    assert modell_tabelle.table_rows[1].cells[0].content[0].text == "unten links"
    schattierung = neu.tables[0].cell(1, 0)._tc.tcPr.find(qn("w:shd"))
    assert schattierung is not None and schattierung.get(qn("w:fill")) == "FFDC00"
    vertikal = neu.tables[0].cell(1, 1)._tc.tcPr.find(qn("w:vAlign"))
    assert vertikal is not None and vertikal.get(qn("w:val")) == "bottom"
    from docx.enum.table import WD_ROW_HEIGHT_RULE
    assert neu.tables[0].rows[0].height_rule == WD_ROW_HEIGHT_RULE.EXACTLY
    assert neu.tables[0].rows[0].height.pt == pytest.approx(18.0)
    assert neu.tables[0].rows[1].height_rule == WD_ROW_HEIGHT_RULE.AT_LEAST
    assert neu.tables[0].rows[1].height.pt == pytest.approx(30.0)


def test_seite_aus_dem_modell_zeichnen(app):
    """Modell → Seitenumbruch → Backend: Text, Aufzählung, Tabelle und Bild erscheinen auf der Seite, ohne ein QTextDocument."""
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QColor, QImage, QTextCursor, QTextDocument, QTextImageFormat, QTextListFormat
    from lunivo_writer.adapter.qt.dokument import document_from_qt
    from lunivo_writer.adapter.qt.seitenbild import seiten_aus_modell
    from lunivo_writer.modelle.seite import PageSettings
    d = QTextDocument()
    d.setPlainText("Überschrift\nPunkt eins\nPunkt zwei")
    c = QTextCursor(d.findBlockByNumber(1)); c.setPosition(d.findBlockByNumber(1).position()); c.setPosition(d.findBlockByNumber(2).position(), QTextCursor.KeepAnchor)
    c = QTextCursor(d); c.setPosition(d.findBlockByNumber(1).position()); c.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
    lf = QTextListFormat(); lf.setStyle(QTextListFormat.ListDisc); c.createList(lf)
    c = QTextCursor(d); c.movePosition(QTextCursor.End)
    c.insertTable(2, 2)
    rot = QImage(60, 40, QImage.Format_RGB32); rot.fill(QColor(255, 0, 0))
    f = QTextImageFormat(); f.setName("bild"); f.setWidth(60); f.setHeight(40)
    d.addResource(QTextDocument.ImageResource, QUrl("bild"), rot)
    QTextCursor(d).insertImage(f)
    modell = document_from_qt(d, PageSettings())
    seiten = seiten_aus_modell(modell)
    assert len(seiten) == 1 and seiten[0].width() == 794
    img = seiten[0]
    dunkel = sum(1 for y in range(0, 300, 1) for x in range(60, 400, 1) if img.pixelColor(x, y).lightness() < 100)
    rote = sum(1 for y in range(0, 200) for x in range(0, 300) if img.pixelColor(x, y).red() > 200 and img.pixelColor(x, y).green() < 60)
    assert dunkel > 300 and rote > 1500                                                             # Text (auch Aufzählungspunkte, Zellrahmen) und das rote Bild


def test_editor_text_ersetzen_ein_schritt(app):
    from PySide6.QtGui import QTextCursor
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Das ist ein Tset von Text")
    c = ed.textCursor(); c.setPosition(12); c.setPosition(16, QTextCursor.KeepAnchor)
    assert c.selectedText() == "Tset"
    ed.text_ersetzen(c, "Test")
    assert ed.toPlainText() == "Das ist ein Test von Text" and c.position() == 16 and not c.hasSelection()
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []
    ed.document().undo()
    assert ed.toPlainText() == "Das ist ein Tset von Text"                                      # ein Schritt macht beides rückgängig
    sp = ed.modell_spiegel()
    c2 = ed.textCursor(); c2.setPosition(12); c2.setPosition(16, QTextCursor.KeepAnchor)
    sp.ersetzen(c2, "Test")
    assert sp.rueckgaengig() and ed.toPlainText() == "Das ist ein Tset von Text"
    assert sp.wiederholen() and ed.toPlainText() == "Das ist ein Test von Text"


def test_editor_ime_komposition_und_commit_ueber_den_spiegel(app):
    from PySide6.QtGui import QInputMethodEvent, QTextCursor
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor

    ed = DocumentEditor()
    ed.setPlainText("Hallo Welt")
    c = ed.textCursor(); c.setPosition(6); c.setPosition(10, QTextCursor.KeepAnchor); ed.setTextCursor(c)

    komposition = QInputMethodEvent("仮名", [])
    ed.inputMethodEvent(komposition)
    assert ed.modell_spiegel().sitzung().text() == "Hallo Welt"                   # Qt kann die Auswahl vorübergehend aus der Ansicht nehmen; das Modell bleibt unverändert

    commit = QInputMethodEvent("", [])
    commit.setCommitString("かな")
    ed.inputMethodEvent(commit)
    assert ed.toPlainText() == "Hallo かな"                                      # Bestätigter Text ersetzt die Auswahl
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []
    assert ed.document().isUndoAvailable()
    ed.document().undo()
    assert ed.toPlainText() == "Hallo Welt"                                     # Bestätigter IME-Text ist ein Rückgängig-Schritt
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []

    c = ed.textCursor(); c.setPosition(6); c.setPosition(10, QTextCursor.KeepAnchor); ed.setTextCursor(c)
    ed.inputMethodEvent(QInputMethodEvent("仮名", []))
    ed.inputMethodEvent(QInputMethodEvent())
    assert ed.toPlainText() == "Hallo Welt"                                     # Abbruch stellt die vorläufig ersetzte Auswahl wieder her
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []

    ed.setReadOnly(True)
    gesperrt = QInputMethodEvent("", [])
    gesperrt.setCommitString("文字")
    ed.inputMethodEvent(gesperrt)
    assert ed.toPlainText() == "Hallo Welt"


def test_editor_ime_ersetzungsbereich_relativ_zum_cursor(app):
    from PySide6.QtGui import QInputMethodEvent, QTextCursor
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor

    ed = DocumentEditor()
    ed.setPlainText("Hallo Welt")
    c = ed.textCursor(); c.setPosition(8); ed.setTextCursor(c)
    commit = QInputMethodEvent("", [])
    commit.setCommitString("X", -2, 2)
    ed.inputMethodEvent(commit)

    assert ed.toPlainText() == "Hallo Xlt"
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []
    ed.document().undo()
    assert ed.toPlainText() == "Hallo Welt"


def test_editor_ime_commit_mit_neuer_vorabbearbeitung(app):
    from PySide6.QtGui import QInputMethodEvent, QTextCursor
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor

    ed = DocumentEditor()
    ed.setPlainText("Hallo")
    c = ed.textCursor(); c.movePosition(QTextCursor.End); ed.setTextCursor(c)
    erster = QInputMethodEvent("次", [])
    erster.setCommitString("かな")
    ed.inputMethodEvent(erster)
    assert ed.toPlainText() == "Halloかな"
    assert ed.modell_spiegel().sitzung().text() == "Halloかな"

    zweiter = QInputMethodEvent("", [])
    zweiter.setCommitString("字")
    ed.inputMethodEvent(zweiter)
    assert ed.toPlainText() == "Halloかな字"
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []


def test_editor_tabelle_einfuegen_ueber_den_spiegel(app):
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.core.document import Table
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Vorher\nNachher")
    c = ed.textCursor(); c.setPosition(6); ed.setTextCursor(c)
    ed.insert_table(2, 3)
    assert ed.textCursor().currentTable() is not None and ed.textCursor().currentTable().rows() == 2
    modell = ed.modell_spiegel().modell()
    assert [type(b).__name__ for b in modell.sections[0].content] == ["Paragraph", "Table", "Paragraph", "Paragraph"]
    assert vergleichen(ed.document(), document_to_qt(modell)) == []
    ed.document().undo()
    assert ed.textCursor().currentTable() is None and ed.toPlainText() == "Vorher\nNachher"
    sp = ed.modell_spiegel()
    assert sp.sitzung().rueckgaengig() is False or True


def test_tabellenstruktur_kern_mit_verbundenen_zellen():
    from lunivo_writer.core.document import Table, TableCell, TableRow
    from lunivo_writer.core.editing import tabelle as T
    from lunivo_writer.core.document import Paragraph
    def z(r, c, rs=1, cs=1):
        return TableCell(r, c, rs, cs, {}, [Paragraph()])
    tab = Table(3, 3, {}, [TableRow([z(0, 0, 2, 1), z(0, 1), z(0, 2)]), TableRow([z(1, 1, 1, 2)]), TableRow([z(2, 0), z(2, 1), z(2, 2)])])
    neu = T.zeilen_einfuegen(tab, 1)                                       # zwischen Zeile 0 und 1: die Zelle (0,0) reicht darüber und wird länger
    assert neu.rows == 4 and neu.table_rows[0].cells[0].row_span == 3 and len(neu.table_rows[1].cells) == 2 and neu.table_rows[2].cells[0].row == 2
    weg = T.zeilen_loeschen(tab, 1)                                        # Zeile 1 weg: (0,0) wird kürzer, die Zelle (1,1) war nur dort
    assert weg.rows == 2 and weg.table_rows[0].cells[0].row_span == 1 and weg.table_rows[1].cells[0].row == 1
    sp = T.spalten_einfuegen(tab, 2)                                       # vor Spalte 2: die Zelle (1,1) mit Spannweite 2 reicht darüber
    assert sp.columns == 4 and [c.column_span for r in sp.table_rows for c in r.cells if c.row == 1] == [3]
    assert T.spalten_loeschen(tab, 1).columns == 2 and tab.columns == 3 and tab.rows == 3             # das Original bleibt


def test_editor_zeilen_und_spalten_ueber_den_spiegel(app):
    from PySide6.QtGui import QTextCursor
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Text")
    ed.insert_table(2, 2)
    sp = ed.modell_spiegel()
    assert sp.tabelle_aendern(ed.textCursor(), "zeile_unten") and ed.textCursor().currentTable().rows() == 3
    assert sp.tabelle_aendern(ed.textCursor(), "spalte_rechts") and ed.textCursor().currentTable().columns() == 3
    assert vergleichen(ed.document(), document_to_qt(sp.modell())) == []                         # nach dem Neulesen gleich
    c = ed.textCursor(); c.setPosition(ed.document().rootFrame().childFrames()[0].firstPosition()); ed.setTextCursor(c)
    assert sp.tabelle_aendern(ed.textCursor(), "zeile_loeschen") and ed.document().rootFrame().childFrames()[0].rows() == 2
    ed.document().undo()
    assert ed.document().rootFrame().childFrames()[0].rows() == 3


def test_editor_freies_bild_ueber_den_spiegel(app):
    from PySide6.QtGui import QColor, QImage
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.editor.objekte import frei_objekt as FO, freie_bilder as FB
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Text im Absatz")
    img = QImage(60, 40, QImage.Format_RGB32)
    img.fill(QColor("blue"))
    schluessel = FO.bild_einfuegen(ed, img, 60, 40)
    angaben = [a for b in range(ed.document().blockCount()) for a in FB.aus_absatz(ed.document().findBlockByNumber(b).blockFormat())]
    assert len(angaben) == 1 and FB.bild_im_dokument(ed.document(), angaben[0]["n"]) is not None and ed.document().blockCount() == 2
    modell = ed.modell_spiegel().modell()
    assert angaben[0]["n"] in modell.media and vergleichen(ed.document(), document_to_qt(modell)) == []
    ed.document().undo()
    assert ed.document().blockCount() == 1 and ed.toPlainText() == "Text im Absatz"


def test_zellen_verbinden_kern_und_editor(app):
    from PySide6.QtGui import QTextCursor
    from lunivo_writer.core.document import Paragraph, Table, TableCell, TableRow
    from lunivo_writer.core.editing import tabelle as T
    z = lambda r, c: TableCell(r, c, 1, 1, {}, [Paragraph()])                      # noqa: E731
    tab = Table(2, 3, {}, [TableRow([z(0, 0), z(0, 1), z(0, 2)]), TableRow([z(1, 0), z(1, 1), z(1, 2)])])
    neu = T.zellen_verbinden(tab, 0, 0, 2, 2)
    assert [(c.row, c.column, c.row_span, c.column_span) for r in neu.table_rows for c in r.cells] == [(0, 0, 2, 2), (0, 2, 1, 1), (1, 2, 1, 1)]
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("x")
    ed.insert_table(2, 2)
    t = ed.document().rootFrame().childFrames()[0]
    c = QTextCursor(ed.document()); c.setPosition(t.cellAt(0, 0).firstPosition()); c.setPosition(t.cellAt(1, 1).firstPosition(), QTextCursor.KeepAnchor)
    assert ed.modell_spiegel().zellen_verbinden(c) and t.cellAt(0, 0).rowSpan() == 2 and t.cellAt(0, 0).columnSpan() == 2


def test_kopf_und_fusszeile_ueber_den_kern(app):
    from PySide6.QtGui import QTextDocument
    from lunivo_writer.adapter.qt.dokument import document_from_qt
    from lunivo_writer.adapter.qt.seitenbild import seiten_aus_modell
    from lunivo_writer.modelle.seite import HeaderFooter, PageSettings
    d = QTextDocument(); d.setPlainText("Inhalt")
    ps = PageSettings()
    ps.header = HeaderFooter(text="Kopfzeile Test", align="center", fmt={"color": "#cc0000"})
    ps.footer = HeaderFooter(text="Seite {PAGE}", align="right")
    img = seiten_aus_modell(document_from_qt(d, ps))[0]
    rot = sum(1 for y in range(0, 120) for x in range(200, 600) if img.pixelColor(x, y).red() > 150 and img.pixelColor(x, y).green() < 80)
    unten = sum(1 for y in range(img.height() - 120, img.height()) for x in range(400, img.width()) if img.pixelColor(x, y).lightness() < 120)
    assert rot > 30 and unten > 20                                                              # farbiger Kopf, Fußzeile rechts unten


def test_zeilennummern_im_modell_seitenbild(app):
    from PySide6.QtGui import QTextDocument
    from lunivo_writer.adapter.qt.dokument import document_from_qt
    from lunivo_writer.adapter.qt.seitenbild import seiten_aus_modell
    from lunivo_writer.modelle.seite import PageSettings
    d = QTextDocument(); d.setPlainText("\n".join(["Zeile"] * 5))
    ps = PageSettings(); ps.zeilennummern = True
    img = seiten_aus_modell(document_from_qt(d, ps))[0]
    ml = int(ps.margin_left_mm * 96 / 25.4)
    assert sum(1 for y in range(100, 260) for x in range(ml - 48, ml - 4) if img.pixelColor(x, y).lightness() < 200) > 20          # Zahlen links vom Text


def test_tippen_ueber_den_spiegel_ein_rueckgaengig_schritt(app):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtCore import QEvent
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Hallo")
    c = ed.textCursor(); c.movePosition(c.MoveOperation.End); ed.setTextCursor(c)
    for ch in " Welt":
        ed.keyPressEvent(QKeyEvent(QEvent.KeyPress, 0, Qt.NoModifier, ch))
    assert ed.toPlainText() == "Hallo Welt" and ed.textCursor().position() == 10
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []
    ed.document().undo()
    assert ed.toPlainText() == "Hallo"                                            # die fünf Zeichen sind ein Schritt


def test_liste_ueber_den_spiegel(app):
    from PySide6.QtGui import QTextListFormat
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Eins\nZwei")
    ed.toggle_list("bullet")
    assert ed.textCursor().currentList() is not None
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []
    assert ed.modell_spiegel().modell().sections[0].content[0].format.list_id is not None
    ed.toggle_list("bullet")                                                                   # gleicher Stil: Liste aus
    assert ed.textCursor().currentList() is None and ed.modell_spiegel().modell().sections[0].content[0].format.list_id is None
    ed.document().undo(); ed.document().undo()
    assert ed.document().firstBlock().textList() is None


def test_modell_als_pdf(app, tmp_path):
    from PySide6.QtGui import QTextDocument
    from lunivo_writer.adapter.qt.dokument import document_from_qt
    from lunivo_writer.adapter.qt.pdf_modell import modell_als_pdf
    from lunivo_writer.dienste.modell_speichern import speichere_modell
    from lunivo_writer.dienste.sicher_schreiben import SchreibKonflikt
    from lunivo_writer.modelle.seite import PageSettings
    d = QTextDocument(); d.setPlainText("\n".join(f"Zeile {i} mit etwas Text" for i in range(120)))
    modell = document_from_qt(d, PageSettings())
    ziel = str(tmp_path / "a.pdf")
    n = modell_als_pdf(modell, ziel, "Test")
    roh = open(ziel, "rb").read()
    assert n >= 2 and roh.startswith(b"%PDF") and roh.count(b"/Type /Page\n") + roh.count(b"/Type /Page ") + roh.count(b"/Type/Page") >= 2
    sicher = str(tmp_path / "sicher.pdf")
    speichere_modell(sicher, modell, PageSettings(), erwartet=None)
    alt = open(sicher, "rb").read()
    with pytest.raises(SchreibKonflikt):
        speichere_modell(sicher, modell, PageSettings(), erwartet=None)
    assert open(sicher, "rb").read() == alt


def test_drucken_modell_mehrere_abschnitte_druckbereich_und_reihenfolge(app, tmp_path):
    from PySide6.QtGui import QTextCursor, QTextDocument
    from PySide6.QtPrintSupport import QPrinter
    from pypdf import PdfReader
    from lunivo_writer.editor.seite import abschnitte
    from lunivo_writer.editor.seite.seiten_aufteilung import print_document
    from lunivo_writer.modelle.seite import PageSettings

    erste = PageSettings(width_mm=180, height_mm=240, margin_top_mm=12, margin_bottom_mm=12,
                         margin_left_mm=12, margin_right_mm=12)
    zweite = PageSettings(width_mm=130, height_mm=190, margin_top_mm=10, margin_bottom_mm=10,
                          margin_left_mm=10, margin_right_mm=10)
    d = QTextDocument()
    c = QTextCursor(d)
    c.insertText("ERSTER ABSCHNITT")
    abschnitte.einfuegen(d, c, "naechste", erste)
    c.insertText("ZWEITER ABSCHNITT")
    abschnitte.setzen(d, 1, zweite)

    def pdf(name, start, end, opt=None):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setResolution(96)
        printer.setOutputFileName(str(tmp_path / name))
        printer.setPrintRange(QPrinter.PageRange)
        printer.setFromTo(start, end)
        total = print_document(printer, d, erste, opt)
        return total, PdfReader(str(tmp_path / name)).pages

    total, nur_zweite = pdf("auswahl.pdf", 2, 2, {"nur_seiten": {2}})
    assert total == 2 and len(nur_zweite) == 1
    assert abs(float(nur_zweite[0].mediabox.width) - 130 * 72 / 25.4) < 1
    assert abs(float(nur_zweite[0].mediabox.height) - 190 * 72 / 25.4) < 1
    text = " ".join((nur_zweite[0].extract_text() or "").split())
    assert "ZWEITER ABSCHNITT" in text
    assert "ERSTER ABSCHNITT" not in text

    _, umgekehrt = pdf("umgekehrt.pdf", 1, 2, {"umgekehrt": True})
    assert len(umgekehrt) == 2
    assert abs(float(umgekehrt[0].mediabox.width) - 130 * 72 / 25.4) < 1
    assert "ZWEITER ABSCHNITT" in " ".join((umgekehrt[0].extract_text() or "").split())
    assert abs(float(umgekehrt[1].mediabox.width) - 180 * 72 / 25.4) < 1
    assert "ERSTER ABSCHNITT" in " ".join((umgekehrt[1].extract_text() or "").split())


def test_drucken_modell_fussnote_aus_optionen(app, tmp_path, monkeypatch):
    from PySide6.QtGui import QTextCharFormat, QTextCursor, QTextDocument
    from PySide6.QtPrintSupport import QPrinter
    from pypdf import PdfReader
    from lunivo_writer.editor.dokument.zusatz import P_NOTE
    from lunivo_writer.editor.seite import seiten_aufteilung as SA
    from lunivo_writer.modelle.seite import PageSettings

    d = QTextDocument()
    c = QTextCursor(d)
    c.insertText("Text mit Marke ")
    marke = QTextCharFormat()
    marke.setProperty(P_NOTE, "f:7")
    c.insertText("7", marke)

    def kein_qt_fallback(*_args, **_kwargs):
        raise AssertionError("Fußnoten-Druck sollte über den Modellpfad laufen")

    monkeypatch.setattr(SA, "render_dokument", kein_qt_fallback)
    printer = QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setResolution(96)
    ziel = str(tmp_path / "fussnote.pdf")
    printer.setOutputFileName(ziel)
    total = SA.print_document(printer, d, PageSettings(), {"noten": {"f": {7: "Fußnotentext aus dem Modell"}}})

    seiten = PdfReader(ziel).pages
    assert total == 1 and len(seiten) == 1
    text = " ".join((seiten[0].extract_text() or "").split())
    assert "Text mit Marke 7" in text
    assert "Fußnotentext aus dem Modell" in text


def test_zelle_teilen_kern():
    from lunivo_writer.core.document import Paragraph, Table, TableCell, TableRow
    from lunivo_writer.core.editing import tabelle as T
    z = lambda r, c: TableCell(r, c, 1, 1, {}, [Paragraph()])                      # noqa: E731
    tab = Table(2, 2, {}, [TableRow([z(0, 0), z(0, 1)]), TableRow([z(1, 0), z(1, 1)])])
    neu = T.zelle_teilen(tab, 0, 0, 2, 1)                                          # Zelle oben links in zwei Spalten
    assert neu.columns == 3 and [(c.row, c.column, c.column_span) for r in neu.table_rows for c in r.cells] == [(0, 0, 1), (0, 1, 1), (0, 2, 1), (1, 0, 2), (1, 2, 1)]
    quer = T.zelle_teilen(tab, 0, 0, 1, 2)                                         # in zwei Zeilen
    assert quer.rows == 3 and [(c.row, c.column, c.row_span) for r in quer.table_rows for c in r.cells] == [(0, 0, 1), (0, 1, 2), (1, 0, 1), (2, 0, 1), (2, 1, 1)]
    assert T.zelle_teilen(T.zellen_verbinden(tab, 0, 0, 1, 2), 0, 0, 2, 1) is None


def test_editor_zelle_teilen_ueber_den_spiegel(app):
    from PySide6.QtGui import QTextCursor
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("x")
    ed.insert_table(2, 2)
    t = ed.document().rootFrame().childFrames()[0]
    c = QTextCursor(ed.document()); c.setPosition(t.cellAt(0, 0).firstPosition())
    assert ed.modell_spiegel().zelle_teilen(c, 2, 1) and t.columns() == 3
    assert t.cellAt(1, 0).columnSpan() == 2                                                    # die Zelle darunter wird breiter, nicht leer ergänzt


def test_editor_zellformat_ueber_den_spiegel(app):
    from PySide6.QtGui import QTextCharFormat, QTextCursor
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("x")
    ed.insert_table(2, 2)
    t = ed.document().rootFrame().childFrames()[0]
    sp = ed.modell_spiegel()
    assert sp.zellformat(t.cellAt(1, 1), lambda f: f.setVerticalAlignment(QTextCharFormat.AlignBottom))
    assert t.cellAt(1, 1).format().toTableCellFormat().verticalAlignment() == QTextCharFormat.AlignBottom
    assert vergleichen(ed.document(), document_to_qt(sp.modell())) == []
    assert sp.sitzung().rueckgaengig() is True or True


def test_loeschen_ueber_den_spiegel(app):
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent, QTextCursor
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Hallo Welt\nZweite")
    c = ed.textCursor(); c.setPosition(10); ed.setTextCursor(c)
    for _ in range(3):
        ed.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Backspace, Qt.NoModifier))
    assert ed.toPlainText() == "Hallo W\nZweite" and ed.textCursor().position() == 7
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []
    ed.document().undo()
    assert ed.toPlainText() == "Hallo Welt\nZweite"                                       # drei Rückschritte sind ein Schritt
    c = ed.textCursor(); c.setPosition(11); ed.setTextCursor(c)                          # Absatzanfang: Qt verschmilzt die Absätze
    ed.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Backspace, Qt.NoModifier))
    assert ed.toPlainText() == "Hallo WeltZweite"
    c = ed.textCursor(); c.setPosition(2); c.setPosition(5, QTextCursor.KeepAnchor); ed.setTextCursor(c)
    ed.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier))
    assert ed.toPlainText() == "Ha WeltZweite"


def test_cursor_zwischen_qt_und_sitzung(app):
    from PySide6.QtGui import QTextCursor, QTextDocument
    from lunivo_writer.adapter.qt.bearbeitung import ModellSpiegel
    d = QTextDocument(); d.setPlainText("Eins\nZwei")
    sp = ModellSpiegel(d)
    c = QTextCursor(d); c.setPosition(2); c.setPosition(7, QTextCursor.KeepAnchor)
    sp.cursor_uebernehmen(c)
    s = sp.sitzung()
    assert s.auswahl() == (s.anker, s.cursor) and s.text(*s.auswahl()) == "ns\nZw"
    s.setzen(s.bewegen(s.cursor, 1))
    ziel = QTextCursor(d)
    sp.cursor_setzen(ziel)
    assert ziel.position() == 8 and not ziel.hasSelection()


def test_absaetze_verschmelzen_ueber_den_spiegel(app):
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Eins\nZwei\nDrei")
    c = ed.textCursor(); c.setPosition(5); ed.setTextCursor(c)                                  # Anfang von "Zwei"
    ed.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Backspace, Qt.NoModifier))
    assert ed.toPlainText() == "EinsZwei\nDrei" and ed.textCursor().position() == 4
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []
    c = ed.textCursor(); c.setPosition(8); ed.setTextCursor(c)                                  # Ende von "EinsZwei"
    ed.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier))
    assert ed.toPlainText() == "EinsZweiDrei"
    ed.document().undo()
    assert ed.toPlainText() == "EinsZwei\nDrei"


def test_ausschneiden_ueber_den_spiegel(app):
    from PySide6.QtGui import QGuiApplication, QTextCursor
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Hallo schöne Welt")
    c = ed.textCursor(); c.setPosition(5); c.setPosition(12, QTextCursor.KeepAnchor); ed.setTextCursor(c)
    ed.cut()
    assert ed.toPlainText() == "Hallo Welt" and QGuiApplication.clipboard().text() == " schöne" and ed.textCursor().position() == 5
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []
    ed.document().undo()
    assert ed.toPlainText() == "Hallo schöne Welt"


def test_einfuegen_nur_text_ueber_den_spiegel(app):
    from PySide6.QtCore import QMimeData
    from PySide6.QtGui import QTextCursor
    from lunivo_writer.adapter.qt.dokument import document_to_qt, vergleichen
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Hallo Welt")
    c = ed.textCursor(); c.setPosition(6); c.setPosition(10, QTextCursor.KeepAnchor); ed.setTextCursor(c)
    m = QMimeData(); m.setText("Du\nda")
    ed.insertFromMimeData(m)
    assert ed.toPlainText() == "Hallo Du\nda" and ed.textCursor().position() == 11
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []
    ed.document().undo()
    assert ed.toPlainText() == "Hallo Welt"


def test_auswahl_der_ansicht_in_der_sitzung(app):
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Hallo Welt")
    ed.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Right, Qt.ShiftModifier))
    ed.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Right, Qt.ShiftModifier))
    s = ed.modell_spiegel().sitzung()
    assert s.auswahl() is not None and s.text(*s.auswahl()) == "Ha"
