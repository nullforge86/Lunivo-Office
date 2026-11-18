"""Positionen der Funde bei Dokumentänderungen: Verschieben über echte contentsChange-Meldungen eines QTextDocument."""
from PySide6.QtGui import QImage, QTextCursor, QTextDocument

from lunivo_writer.korrektur import fund, inkrement, pruefung

ABSATZ = "Das ist ein Satz mit  zwei Leerzeichen und einem Tippfehler wie Fehlr."


class Beobachter:
    """Hält Funde eines Dokuments wie WritingAssistant._geaendert es tut."""

    def __init__(self, doc):
        self.doc = doc
        self.funde = fund.markieren(pruefung.finde_probleme(doc.toPlainText()), "eigen")
        doc.contentsChange.connect(self._geaendert)

    def _geaendert(self, pos, entfernt, hinzu):
        self.funde = inkrement.verschieben(self.funde, pos, entfernt, hinzu)

    def passt(self):
        text = self.doc.toPlainText()
        return all(text[f.von:f.bis] == f.alt for f in self.funde)


def _doc(text):
    d = QTextDocument()
    d.documentLayout()          # contentsChange kommt erst, wenn das Dokument ein Layout hat (im Editor immer der Fall)
    d.setPlainText(text)
    return d


def test_funde_vorhanden(app):
    assert pruefung.finde_probleme(ABSATZ), "Beispielabsatz liefert keine Funde"


def test_einfuegen_und_loeschen_vor_den_funden_verschiebt_sie(app):
    d = _doc("Vorspann.\n" + ABSATZ)
    b = Beobachter(d)
    n = len(b.funde)
    c = QTextCursor(d)
    c.insertText("Neue Zeile davor.\n")
    assert len(b.funde) == n and b.passt()
    c.setPosition(0)
    c.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 5)
    c.removeSelectedText()
    assert len(b.funde) == n and b.passt()


def test_aenderung_im_fund_verwirft_ihn_aenderung_dahinter_laesst_ihn(app):
    d = _doc(ABSATZ)
    b = Beobachter(d)
    f = b.funde[0]
    n = len(b.funde)
    c = QTextCursor(d)
    c.setPosition(len(ABSATZ))
    c.insertText(" Ende.")
    assert len(b.funde) == n and b.passt()
    c.setPosition(f.von + 1)
    c.insertText("x")
    assert len(b.funde) < n and b.passt()


def test_ersetzen_ueber_fundgrenze_und_undo(app):
    d = _doc("Anfang " + ABSATZ)
    b = Beobachter(d)
    c = QTextCursor(d)
    c.setPosition(3)
    c.setPosition(12, QTextCursor.KeepAnchor)
    c.insertText("ZZ")
    assert b.passt()
    d.undo()
    assert b.passt()           # Positionen bleiben stimmig, auch wenn der verworfene Fund nicht zurückkehrt


def test_bild_und_tabelle_verschieben_positionen_wie_der_text(app):
    d = _doc(ABSATZ)
    b = Beobachter(d)
    n = len(b.funde)
    c = QTextCursor(d)
    c.setPosition(0)
    d.addResource(QTextDocument.ImageResource, "bild", QImage(4, 4, QImage.Format_RGB32))
    c.insertImage("bild")
    c.insertTable(2, 2)
    assert len(b.funde) == n and b.passt()


def test_inkrementell_gleich_ganze_pruefung(app):
    absaetze = [ABSATZ.replace("Fehlr", f"Fehlr{i % 3}") for i in range(40)]
    text = "\n".join(absaetze)
    assert len(text) >= inkrement.MIN_ZEICHEN
    d = _doc(text)
    b = Beobachter(d)
    c = QTextCursor(d)
    c.setPosition(len(absaetze[0]) + 1 + 10)
    c.insertText("  und noch  ein Fehlr")
    alt_text = d.toPlainText()
    pos = len(absaetze[0]) + 1 + 10
    schmutz = inkrement.schmutz_abbilden(None, pos, 0, len("  und noch  ein Fehlr"))
    von, bis = inkrement.pruefbereich(alt_text, *schmutz)
    assert inkrement.lohnt(len(alt_text), von, bis)
    roh = fund.markieren(pruefung.finde_probleme(alt_text[von:bis]), "eigen")
    inkr = inkrement.einsetzen(b.funde, von, bis, roh)
    voll = fund.markieren(pruefung.finde_probleme(alt_text), "eigen")
    schluessel = lambda fs: sorted((f.von, f.bis, f.alt) for f in fs)
    assert schluessel(inkr) == schluessel(voll)
