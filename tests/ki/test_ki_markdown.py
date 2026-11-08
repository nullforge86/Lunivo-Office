"""KI-Markdown: dieselben Regeln für Chat-Anzeige, Vorschau und Übernahme ins Dokument (``editor.text.ki_markdown``)."""
from PySide6.QtGui import QFont, QTextCursor, QTextDocument, QTextList, QTextListFormat
from PySide6.QtCore import Qt

from lunivo_writer.editor.text import ki_markdown as KM
from lunivo_writer.ai import chat_bezug as CB
from lunivo_writer.ui.document.bearbeitung.document_editor import DocumentEditor
from lunivo_writer.ui.baukasten.dokument.aenderungs_vorschau import AenderungsVorschau
from lunivo_writer.ui.baukasten.chat.chat_blase import antwort_label

ANTWORT = ("# Titel\n\n## Unterpunkt\n\nText mit **fett** und *kursiv*.\n\n- Eins\n  - Eins a\n  - Eins b\n- Zwei\n\n1. Erst\n2. Dann\n\n"
           "| A | B |\n|---|---|\n| 1 | 2 |\n\nSchluss")


def ed(text="Vorher"):
    e = DocumentEditor(); e.setPlainText(text); e.zusatz_binden({})
    c = e.textCursor(); c.movePosition(QTextCursor.End); e.setTextCursor(c)
    return e


def bloecke(doc):
    b = doc.begin()
    while b.isValid():
        yield b
        b = b.next()


def anfang(block):
    """Zeichenformat des ersten Textstücks (das Blockformat sagt nichts über den Text)."""
    return block.begin().fragment().charFormat()


def einfuegen(e, text):
    c = QTextCursor(e.document()); c.movePosition(QTextCursor.End)
    KM.einfuegen(e, c, text)


def test_struktur_erkennung_und_einfacher_text(app):
    assert KM.hat_struktur(ANTWORT)
    assert KM.hat_struktur("Das ist **wichtig**.") and KM.hat_struktur("- a\n- b") and KM.hat_struktur("# T")
    assert not KM.hat_struktur("Ganz normale Antwort mit snake_case und 3 * 4.\n\nZweiter Absatz.")
    assert not KM.hat_struktur("")


def test_zeilenumbrueche_bleiben_und_rohe_marken_nicht_gedeutet(app):
    assert KM.klartext("eins\nzwei") == "eins\nzwei" and KM.dokument("eins\nzwei").blockCount() == 2     # kein stilles Zusammenziehen zu einer Zeile
    assert "<b>" in KM.klartext("Das ist <b>roh</b>")


def test_uebernahme_ueberschriften_als_formatvorlage(app):
    e = ed(); einfuegen(e, "# Titel\n\n## Unter\n\nText")
    bl = [b for b in bloecke(e.document())]
    t = next(b for b in bl if b.text() == "Titel"); u = next(b for b in bl if b.text() == "Unter")
    assert t.blockFormat().headingLevel() == 1 and u.blockFormat().headingLevel() == 2
    assert anfang(t).fontWeight() >= QFont.Bold and anfang(t).fontPointSize() == 20
    text = next(b for b in bl if b.text() == "Text")
    assert text.blockFormat().headingLevel() == 0 and anfang(text).fontWeight() < QFont.Bold


def test_uebernahme_verschachtelte_und_nummerierte_listen(app):
    e = ed(); einfuegen(e, "- Eins\n  - Eins a\n  - Eins b\n- Zwei\n\n1. Erst\n2. Dann")
    bl = {b.text(): b for b in bloecke(e.document())}
    assert bl["Eins"].textList().format().indent() == 1 and bl["Eins a"].textList().format().indent() == 2
    assert bl["Eins"].textList() is bl["Zwei"].textList()
    assert bl["Eins a"].textList() is bl["Eins b"].textList() and bl["Eins a"].textList() is not bl["Eins"].textList()
    assert bl["Erst"].textList().format().style() == QTextListFormat.ListDecimal
    assert bl["Erst"].textList() is bl["Dann"].textList() and bl["Dann"].textList().itemNumber(bl["Dann"]) == 1


def test_uebernahme_fett_kursiv_absaetze_umbrueche(app):
    e = ed(); einfuegen(e, "Eins **fett** und *schief*.\nZweite Zeile\n\nNeuer Absatz")
    bl = list(bloecke(e.document()))
    erster = next(b for b in bl if "fett" in b.text())
    assert [b.text() for b in bl][-2:] == ["Zweite Zeile", "Neuer Absatz"]            # Zeilenumbruch und Absatz bleiben getrennte Zeilen
    frs = []
    it = erster.begin()
    while not it.atEnd():
        frs.append((it.fragment().text(), it.fragment().charFormat())); it += 1
    assert any(t == "fett" and f.fontWeight() >= QFont.Bold for t, f in frs)
    assert any(t == "schief" and f.fontItalic() for t, f in frs)
    assert any(b.text() == "Neuer Absatz" for b in bl)


def test_uebernahme_tabelle_nativ(app):
    e = ed(); einfuegen(e, "| A | B |\n|---|---|\n| 1 | **2** |\n\nDanach")
    t = e.document().rootFrame().childFrames()[0]
    assert t.rows() == 2 and t.columns() == 2
    assert t.cellAt(0, 0).firstCursorPosition().block().text() == "A" and t.cellAt(1, 1).firstCursorPosition().block().text() == "2"
    assert e.document().toPlainText().rstrip().endswith("Danach")


def test_bestehende_formatierung_bleibt(app):
    e = DocumentEditor(); e.setPlainText("Anfang\nEnde"); e.zusatz_binden({})
    c = QTextCursor(e.document()); c.setPosition(0); c.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
    f = c.charFormat(); f.setFontWeight(QFont.Bold); f.setFontFamilies(["Courier New"]); c.mergeCharFormat(f)
    alles = QTextCursor(e.document()); alles.select(QTextCursor.Document); alles.mergeCharFormat(f)      # ganzes Dokument in Courier
    ende = QTextCursor(e.document()); ende.movePosition(QTextCursor.End)
    KM.einfuegen(e, ende, " plus *neu*")
    assert e.document().firstBlock().text() == "Anfang" and anfang(e.document().firstBlock()).fontWeight() >= QFont.Bold
    letzter = e.document().lastBlock()
    assert letzter.text().startswith("Ende") and letzter.text().endswith("plus neu")
    letzte = None
    it = letzter.begin()
    while not it.atEnd():
        letzte = it.fragment().charFormat(); it += 1
    assert letzte.fontFamilies() == ["Courier New"] and letzte.fontItalic()        # neuer Text übernimmt die Schrift der Stelle


def test_replace_range_markdown_ersetzt_markierung_als_ein_schritt(app):
    e = ed("Alt Text hier"); doc = e.document()
    assert e.replace_range(4, 8, "# Neu\n\n- a\n- b", erwartet="Text", markdown=True)
    assert doc.toPlainText().startswith("Alt ") and any(b.blockFormat().headingLevel() == 1 for b in bloecke(doc))
    assert any(b.textList() is not None for b in bloecke(doc))


def test_einfacher_text_ohne_markdown_bleibt_unveraendert(app):
    e = ed("A"); assert e.replace_range(1, 1, " 2*3 snake_case", markdown=False)
    assert e.toPlainText() == "A 2*3 snake_case"
    assert not any(b.blockFormat().headingLevel() or b.textList() for b in bloecke(e.document()))


def test_chat_anzeige_und_vorschau_nutzen_dieselben_regeln(app):
    l = antwort_label(ANTWORT)
    assert l.textFormat() == Qt.MarkdownText and l.text() == KM.normalisieren(ANTWORT)
    assert antwort_label("Nur Text, schlicht.").textFormat() == Qt.PlainText
    v = AenderungsVorschau(); v.stuecke_setzen(CB.vorschau_einfuegen(ANTWORT), markdown=True)
    d = v.document()
    assert not any("#" in b.text() or "**" in b.text() for b in bloecke(d))
    assert any(b.blockFormat().headingLevel() == 1 for b in bloecke(d)) and any(b.textList() for b in bloecke(d))
    assert CB.vorschau_stuecke("alt", ANTWORT) == [("entfernt", "alt"), ("neu", ANTWORT)]
    assert CB.vorschau_stuecke("a b", "a c")[0][0] == "gleich"
