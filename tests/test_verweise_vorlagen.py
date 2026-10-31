"""Reiter Verweise nach Kays Vorlagen (Ordner verweise/): Band, Klappe Inhaltsverzeichnis, Fenster Inhaltsverzeichnis und
Indexeintrag festlegen, Fuß- und Endnoten einzeln durchgehen."""
from __future__ import annotations

import pytest
from PySide6.QtGui import QTextBlockFormat, QTextCursor

from lunivo_writer.editor import verweise
from lunivo_writer.editor import verzeichnis as V
from lunivo_writer.editor.indexeintrag import Eintrag, aus_feld, feld
from lunivo_writer.editor.zusatz import B_TOC
from lunivo_writer.services import docx_reader, docx_writer
from lunivo_writer.ui.document.document_editor import DocumentEditor


@pytest.fixture
def fenster(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document()
    yield w
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def _ed(*absaetze):
    e = DocumentEditor(); e.zusatz_binden({})
    c = e.textCursor()
    for i, t in enumerate(absaetze):
        if i:
            c.insertBlock(QTextBlockFormat())
        c.insertText(t)
    e.setTextCursor(c)
    return e


def _gehe(e, text):
    c = e.textCursor(); c.setPosition(e.toPlainText().index(text)); e.setTextCursor(c)


def _toc_zeilen(doc):
    b, out = doc.firstBlock(), []
    while b.isValid():
        if str(b.blockFormat().property(B_TOC) or "").startswith("zeile"):
            out.append(b)
        b = b.next()
    return out


def test_band_verweise_wie_vorlage(fenster):
    from lunivo_writer.ui.ribbon.plan import plan
    from lunivo_writer.ui.ribbon.ribbon_bar import lade_register
    tab = next(t for t in plan(lade_register()) if t["name"] == "Verweise")
    namen = [e["name"] for g in tab["gruppen"] for e in g["knoepfe"]]
    reihe = ["TOC einfügen", "Inhaltsverzeichnis aktualisieren", "Inhaltsverzeichnis", "Fußnote einfügen", "Vorherige Fußnote",
             "Nächste Fußnote", "Endnote einfügen", "Vorherige Endnote", "Nächste Endnote", "Fußnote/Endnotentrennlinie",
             "Beschriftung", "Abbildungsverzeichnis einfügen", "Querverweis", "Eintrag festlegen", "Index einfügen",
             "Index aktualisieren", "Seriendruck"]
    assert [n for n in namen if n in reihe] == reihe
    kn = {e["name"]: e for g in tab["gruppen"] for e in g["knoepfe"]}
    assert kn["Inhaltsverzeichnis"]["klappe"] == "inhaltsverzeichnisKlappe"
    for n in ("TOC einfügen", "Inhaltsverzeichnis aktualisieren", "Vorherige Fußnote", "Nächste Endnote", "Eintrag festlegen",
              "Index aktualisieren", "Seriendruck"):
        assert fenster.befehle.hat(kn[n]["tun"]), n
    assert not fenster.befehle.hat(kn["Fußnote/Endnotentrennlinie"]["tun"])      # bleibt grau sichtbar
    assert "Zitat einfügen" in namen and "Nächste Note" not in namen


def test_klappe_inhaltsverzeichnis_ebenen(fenster):
    e = fenster.current_editor()
    e.insertPlainText("Kapitel")
    m = fenster.befehle.klappe("inhaltsverzeichnisKlappe")
    texte = [a.text().replace("&", "") for a in m.actions() if a.text()]
    assert texte == [f"Ebene {n}" for n in range(1, 10)] + ["Textkörper(B)"]
    m.aboutToShow.emit()
    assert m.actions()[9].isChecked()
    m.actions()[4].trigger(); m.aboutToShow.emit()
    assert e.textCursor().blockFormat().headingLevel() == 5 and m.actions()[4].isChecked() and not m.actions()[9].isChecked()
    m.actions()[9].trigger()
    assert e.textCursor().blockFormat().headingLevel() == 0


def test_inhaltsverzeichnis_optionen(app, tmp_path):
    from lunivo_writer.editor import tabfuell
    e = _ed("Eins", "Text", "Zwei", "Text", "Vier")
    for t, s in (("Eins", "Überschrift 1"), ("Zwei", "Überschrift 2"), ("Vier", "Überschrift 4")):
        _gehe(e, t); e.apply_style(s)
    c = e.textCursor(); c.setPosition(0); e.setTextCursor(c)
    assert V.verzeichnis_einfuegen(e, "toc", {"ebenen": 3}) == 2                       # Ebene 4 bleibt draußen
    zeilen = _toc_zeilen(e.document())
    assert [z.text().split("\t")[0] for z in zeilen] == ["Eins", "Zwei"]
    assert tabfuell.lesen(zeilen[0].blockFormat()) and "\t" in zeilen[0].text()          # Punkte bis zur Seitenzahl rechts
    href = next(f.charFormat().anchorHref() for f in e._fragmente() if f.charFormat().anchorHref())
    assert href.startswith("#_Toc") and verweise.intern_springen(e, href) and e.textCursor().selectedText() == "Eins"
    assert all(not d["name"].startswith("_") for d in verweise.lesezeichen_liste(e, versteckte=False))
    # dasselbe Verzeichnis neu: 4 Ebenen, ohne Seitenzahlen, ohne Verknüpfungen — es bleibt eines
    assert V.verzeichnis_einfuegen(e, "toc", {"ebenen": 4, "seitenzahlen": False, "links": False}) == 3
    zeilen = _toc_zeilen(e.document())
    assert [z.text() for z in zeilen] == ["Eins", "Zwei", "Vier"] and e.toPlainText().count("Inhaltsverzeichnis") == 1
    assert V.toc_optionen(e.document())["ebenen"] == 4
    V.verzeichnis_aktualisieren(e)                                                        # die Einstellungen bleiben
    assert [z.text() for z in _toc_zeilen(e.document())] == ["Eins", "Zwei", "Vier"]
    # DOCX: Zeilen ab Ebene 4 als „TOC 4“ wiedererkannt
    out = tmp_path / "t.docx"
    docx_writer.write_docx(str(out), e.document(), e.page, dict(e._meta))
    d2, _p, _m, _r = docx_reader.read_docx(str(out))
    assert [b.blockFormat().property(B_TOC) for b in _toc_zeilen(d2)] == ["zeile1", "zeile2", "zeile4"]


def test_fenster_inhaltsverzeichnis(app):
    from lunivo_writer.ui.dialogs.verweise_fenster import InhaltsverzeichnisDialog
    d = InhaltsverzeichnisDialog(None, {"fuell": "strich", "ebenen": 5})
    assert d.ergebnis() == {"fuell": "strich", "ebenen": 5, "seitenzahlen": True, "rechts": True, "links": True}
    d.seitenzahlen.setChecked(False)
    assert not d.rechts.isEnabled() and not d.fuell.isEnabled()
    d.grab()                                                                              # Vorschau zeichnet ohne Fehler


def test_indexeintrag_feld():
    e = Eintrag("Obst", "Apfel", siehe="Kernobst", fett=True, lesung="obst")
    f = feld(e)
    assert f.startswith('XE "Obst:Apfel"') and "\\b" in f
    assert aus_feld(f) == e and aus_feld('XE "Birne" \\i').kursiv and aus_feld("SEQ x") is None


def test_index_mit_unter_siehe_und_bereich(app, tmp_path):
    e = _ed("Apfel und Birne", "Der Apfel ist rund.", "Birne", "Ende")
    _gehe(e, "Apfel"); c = e.textCursor(); c.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor); e.setTextCursor(c)
    assert verweise.index_eintragen(e, Eintrag("Obst", "Apfel", fett=True), alle=True) == 2
    _gehe(e, "Birne"); assert verweise.index_eintragen(e, Eintrag("Birne", siehe="Obst")) == 1
    _gehe(e, "Ende"); c = e.textCursor(); c.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor); e.setTextCursor(c)
    verweise.lesezeichen_setzen(e, "Schluss")
    _gehe(e, "rund"); assert verweise.index_eintragen(e, Eintrag("Form", marke="Schluss", kursiv=True)) == 1
    c = e.textCursor(); c.movePosition(QTextCursor.End); e.setTextCursor(c)
    assert V.verzeichnis_einfuegen(e, "index") == 4
    zeilen = [(b.text(), b.blockFormat().property(B_TOC)) for b in _bloecke(e.document()) if b.blockFormat().property(B_TOC) != "kopf"
              and b.blockFormat().hasProperty(B_TOC)]
    assert zeilen == [("Birne\tSiehe Obst", "zeile1"), ("Form\t1", "zeile1"), ("Obst", "zeile1"), ("Apfel\t1", "zeile2")]
    fett = [f for f in e._fragmente() if f.text() == "1" and f.charFormat().fontWeight() > 50]
    assert fett                                                                            # \\b: fette Seitenzahl
    out = tmp_path / "i.docx"
    docx_writer.write_docx(str(out), e.document(), e.page, dict(e._meta))
    d2, p2, m2, _r = docx_reader.read_docx(str(out))
    e2 = DocumentEditor(); e2.set_document_and_page(d2, p2); e2.zusatz_binden(m2)
    V.verzeichnis_aktualisieren(e2, "index")
    assert "Birne\tSiehe Obst" in e2.toPlainText() and "Apfel\t1" in e2.toPlainText()


def _bloecke(doc):
    b = doc.firstBlock()
    while b.isValid():
        yield b
        b = b.next()


def test_fenster_indexeintrag_meldet(app):
    from lunivo_writer.ui.dialogs.verweise_fenster import IndexeintragDialog
    d = IndexeintragDialog(None, "Apfel", [], auswahl=True)
    assert d.knopf_alle.isEnabled() and not d.r_bereich.isEnabled() and not d.siehe.isEnabled()
    gemeldet = []
    d.markieren.connect(lambda e, alle: gemeldet.append((e, alle)))
    d.unter.setText("rot"); d.r_siehe.setChecked(True); d.siehe.setText("Obst"); d.kursiv.setChecked(True)
    d.knopf_alle.click()
    assert gemeldet == [(Eintrag("Apfel", "rot", siehe="Obst", kursiv=True), True)]
    assert IndexeintragDialog(None, "", ["M"]).knopf_alle.isEnabled() is False


def test_fussnoten_und_endnoten_einzeln(fenster):
    e = fenster.current_editor(); b = fenster.befehle
    e.insertPlainText("a "); e.note_neu("f", "F1"); e.insertPlainText(" b "); e.note_neu("e", "E1")
    e.insertPlainText(" c "); e.note_neu("f", "F2")
    c = e.textCursor(); c.setPosition(0); e.setTextCursor(c)
    b.endnoteWeiter()
    assert e.textCursor().selectionStart() == e.noten_stellen()[1]["von"]
    b.fussnoteWeiter()
    assert e.textCursor().selectionStart() == e.noten_stellen()[2]["von"]
    b.fussnoteZurueck()                                                                   # die Endnote dazwischen wird übersprungen
    assert e.textCursor().selectionStart() == e.noten_stellen()[0]["von"]
    b.indexAktualisieren()
    assert "keinen Index" in fenster.statusBar().currentMessage()


def test_fenster_beschriftung(app):
    from lunivo_writer.ui.dialogs.verweise_fenster import BeschriftungDialog
    d = BeschriftungDialog(None, ["Bild"], lambda label, zahl: "II" if zahl == "roemisch" else "3", objekt=False, label="Tabelle")
    assert d.text.text() == "Tabelle 3" and not d.pos.isEnabled() and not d.loeschen.isEnabled()
    d.text.setText("Tabelle 3: Preise")
    d.label.setCurrentText("Gleichung")                                                   # der geschriebene Rest bleibt
    assert d.text.text() == "Gleichung 3: Preise"
    d.zahl = "roemisch"; d.ohne.setChecked(True)
    assert d.text.text() == "II: Preise"
    assert d.ergebnis() == {"label": "Gleichung", "nach": ": Preise", "oben": False, "ohne": True, "zahl": "roemisch"}
    d.label.setCurrentText("Bild"); assert d.loeschen.isEnabled()
    d.loeschen.click()
    assert d.eigene == [] and d.label.findText("Bild") < 0


def test_beschriftung_roemisch_ohne_bezeichnung_und_querverweis(app):
    from lunivo_writer.editor.zusatz import P_FELD
    e = _ed("Erstes Bild", "Zweites Bild", "Text")
    _gehe(e, "Erstes")
    verweise.beschriftung_einfuegen(e, "Abbildung", "", nach=": Sonne", zahl="roemisch")
    _gehe(e, "Zweites")
    assert verweise.naechste_nummer(e, "Abbildung", "roemisch") == "II"
    verweise.beschriftung_einfuegen(e, "Abbildung", "", nach=" Mond", ohne_bezeichnung=True, zahl="roemisch")
    texte = [k["text"] for k in verweise.beschriftungen_liste(e)]
    assert texte == ["Abbildung I: Sonne", "II Mond"]
    assert any("ROMAN" in f.charFormat().stringProperty(P_FELD) for f in e._fragmente())
    ziele = [z for z in verweise.querverweis_ziele(e) if z["art"] == "Abbildung"]
    assert [z["nummer"] for z in ziele] == ["Abbildung I", "II"] and ziele[0]["inhalt"] == "Sonne"
    c = e.textCursor(); c.movePosition(QTextCursor.End); e.setTextCursor(c)
    verweise.querverweis_einfuegen(e, ziele[0], "nummer", oben_unten=True)
    verweise.querverweis_einfuegen(e, ziele[0], "nur_text", link=False)
    assert e.toPlainText().endswith("Abbildung I oben Sonne ")
    href = next(f.charFormat().anchorHref() for f in e._fragmente() if f.charFormat().anchorHref())
    assert href.startswith("#_Ref") and verweise.intern_springen(e, href)
    assert all(not d["name"].startswith("_") for d in verweise.lesezeichen_liste(e, versteckte=False))


def test_fenster_querverweis_bleibt_offen(app):
    from lunivo_writer.ui.dialogs.verweise_fenster import QuerverweisDialog
    e = _ed("Kapitel", "Text")
    _gehe(e, "Kapitel"); e.apply_style("Überschrift 1")
    d = QuerverweisDialog(None, verweise.querverweis_ziele(e))
    assert d.art.currentText() == "Nummeriertes Element" and d.auf.currentData() == "seite" and not d.zeile.ok.isEnabled()
    d.art.setCurrentText("Überschrift")
    assert d.liste.count() == 1 and d.fuer.text() == "Für welche Überschrift:"
    d.liste.setCurrentRow(0); d.auf.setCurrentIndex(d.auf.findData("text"))
    assert not d.oben_unten.isEnabled() and d.zeile.ok.isEnabled()
    gemeldet = []
    d.einfuegen.connect(lambda z, wie, link, ou: gemeldet.append((z["text"], wie, link, ou)))
    d.zeile.ok.click()
    assert gemeldet == [("Kapitel", "text", True, False)] and d.zeile.abbrechen.text() == "Schließen"
    assert [x for x in verweise.VERWEISTYPEN if x not in [d.art.itemText(i) for i in range(d.art.count())]] == []


def test_befehle_beschriftung_und_querverweis(fenster, monkeypatch):
    from PySide6.QtWidgets import QDialog
    from lunivo_writer.ui.dialogs import verweise_fenster as VF
    e = fenster.current_editor()
    e.insertPlainText("Bild")

    def beschriftung_exec(self):
        self.text.setText(self.text.text() + ": Hund"); return QDialog.Accepted
    monkeypatch.setattr(VF.BeschriftungDialog, "exec", beschriftung_exec)
    fenster.befehle.beschriftung()
    assert "Abbildung 1: Hund" in e.toPlainText()

    def querverweis_exec(self):
        self.art.setCurrentText("Abbildung"); self.liste.setCurrentRow(0)
        self.auf.setCurrentIndex(self.auf.findData("nummer")); self.zeile.ok.click(); return QDialog.Rejected
    monkeypatch.setattr(VF.QuerverweisDialog, "exec", querverweis_exec)
    c = e.textCursor(); c.movePosition(QTextCursor.End); e.setTextCursor(c); e.insertPlainText("\nSiehe ")
    fenster.befehle.querverweis()
    assert e.toPlainText().endswith("Siehe Abbildung 1 ")
