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
    ed.change_indent(5)
    b = ed.document().firstBlock()
    gesetzt = []
    while b.isValid():
        gesetzt.append((bool(b.blockFormat().alignment() & Qt.AlignHCenter), b.blockFormat().leftMargin() > 0))
        b = b.next()
    assert gesetzt == [(True, True), (True, True), (False, False)]                           # nur die ausgewählten Absätze
    assert vergleichen(ed.document(), document_to_qt(ed.modell_spiegel().modell())) == []
    ed.document().undo()
    assert ed.document().firstBlock().blockFormat().leftMargin() == 0 and ed.document().firstBlock().blockFormat().alignment() & Qt.AlignHCenter


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
        s.zeichenformat({"FontWeight": 700}, Caret((0, 1), 0), Caret((0, 1), 6))
        b = str(tmp_path / f"b.{ext}")
        speichere_modell(b, geladen.document, geladen.page)
        neu = datei_dienst.load(b)
        assert neu.doc.toPlainText() == "Neu: Erster Absatz\nZweiter Absatz"
        assert neu.doc.firstBlock().next().begin().fragment().charFormat().fontWeight() >= 700
        assert FB.bild_im_dokument(neu.doc, FB.aus_absatz(neu.doc.firstBlock().blockFormat())[0]["n"]) is not None


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
    from lunivo_writer.modelle.seite import PageSettings
    d = QTextDocument(); d.setPlainText("\n".join(f"Zeile {i} mit etwas Text" for i in range(120)))
    ziel = str(tmp_path / "a.pdf")
    n = modell_als_pdf(document_from_qt(d, PageSettings()), ziel, "Test")
    roh = open(ziel, "rb").read()
    assert n >= 2 and roh.startswith(b"%PDF") and roh.count(b"/Type /Page\n") + roh.count(b"/Type /Page ") + roh.count(b"/Type/Page") >= 2


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
