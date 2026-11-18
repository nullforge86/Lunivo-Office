"""Reiter Einfügen nach Kays Vorlagen (Ordner einfuegen/): Klappmenüs, Zahl, Felder, Text ↔ Tabelle, Leere Seite quer."""
from __future__ import annotations

import pytest
from PySide6.QtGui import QTextCursor


@pytest.fixture
def fenster(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.programmfenster import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document()
    yield w
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def _texte(m):
    return [a.text().replace("&", "") for a in m.actions() if a.text()]


def test_klappmenues_wie_vorlage(fenster):
    b = fenster.befehle
    assert _texte(b.klappe("leereSeiteKlappe")) == ["Vertikal", "Horizontal"]
    assert _texte(b.klappe("umbruecheKlappe")) == [
        "Seitenumbruch(P)\tStrg+Enter", "Spaltenumbruch", "Textflussumbruch(W)\tUmschalt+Enter",
        "Abschnittsumbruch von nächster Seite", "Fortlaufenden Abschnittsumbruch", "Abschnittsumbruch von gerader Seite",
        "Abschnittsumbruch von ungerader Seite"]
    assert _texte(b.klappe("bildKlappe")) == ["Bild aus Datei einfügen …", "Bildschirmfoto …", "Piktogramm …"]
    tf = b.klappe("textfeldKlappe")
    assert _texte(tf) == ["Horizontal", "Vertikal", "Mehrzeiliger Text"]
    assert all(a.isEnabled() for a in tf.actions() if a.text())          # wie in der Vorlage: alle drei wählbar
    assert _texte(b.klappe("schnellbausteineKlappe")) == ["AutoText-Liste", "Felder …"]
    assert b.hat("textflussumbruch")                        # auch im Seitenlayout-Menü nicht mehr grau


def test_textfeld_vertikal_ist_freies_textfeld(fenster):
    from lunivo_writer.editor.objekte import frei_objekt as FO
    ed = fenster.current_editor()
    fenster.befehle.textfeldVertikal()
    z = FO.ziel(ed)
    assert z[0] == "textfeld" and z[1]["richtung"] == "senkrecht_rl"                 # Form mit Text, senkrecht gesetzt
    assert z[3]["h"] > z[3]["b"]

def test_band_einfuegen_reihenfolge(fenster):
    from lunivo_writer.oberflaeche.band.plan import plan
    from lunivo_writer.oberflaeche.band.band_leiste import lade_register
    tab = next(t for t in plan(lade_register()) if t["name"] == "Einfügen")
    namen = [e["name"] for g in tab["gruppen"] if g["name"] != "Weitere" for e in g["knoepfe"]]
    for a, z in (("Deckblatt", "Leere Seite"), ("Leere Seite", "Umbrüche"), ("Umbrüche", "Tabelle"), ("Tabelle", "Bild"),
                 ("Textfeld", "WordArt"), ("Symbol", "Gleichung"), ("Gleichung", "Zahl"), ("Zahl", "Hyperlink")):
        assert namen.index(a) < namen.index(z)
    assert all(g["name"] != "Weitere" for g in tab["gruppen"])     # nicht länger als die Vorlage (Kay, 2026-10-28)
    # nichts geht verloren: was die Vorlage nicht im Band hat, steht in den Klappen
    assert "Text aus Datei …" in _texte(fenster.befehle.klappe("objektKlappe"))


def test_symbol_zuletzt_verwendet(fenster):
    b = fenster.befehle
    e = fenster.current_editor()
    m = b.klappe("symbolKlappe")
    assert m.knoepfe["zuletzt0"].isHidden() and "kg" in m.knoepfe
    m.gewaehlt.emit("§")
    assert e.toPlainText().endswith("§")
    m.aboutToShow.emit()
    assert not m.knoepfe["zuletzt0"].isHidden() and m.knoepfe["zuletzt0"].toolTip() == "„§“ einfügen"
    m.gewaehlt.emit("zuletzt0")
    assert e.toPlainText().endswith("§§")


def test_symbol_fenster_einfuegen_und_benutzerdefiniert(fenster):
    """Fenster „Symbol“: Einfügen setzt das Zeichen und merkt es; die benutzerdefinierte Liste (gleiche Daten wie die Klappe) lässt sich
    verschieben, abhaken, entfernen und zurücksetzen."""
    from PySide6.QtCore import Qt
    from lunivo_writer.oberflaeche.dialoge.einfuegen.sonderzeichen import SonderzeichenDialog
    b = fenster.befehle
    e = fenster.current_editor()
    d = SonderzeichenDialog(None, e.insertPlainText, b._symbol_daten())
    d.zeichencode.setText("167"); d._code_getippt("167")                     # Reiter Symbole: Zeichencode 167 = §
    d.ok.click()
    assert e.toPlainText().endswith("§") and b._symbole_zuletzt()[0] == "§"
    d.reiter.setCurrentIndex(1); d.sonder.setCurrentItem(d.sonder.topLevelItem(0)); d.ok.click()   # Reiter Sonderzeichen: Geviertstrich
    assert e.toPlainText().endswith("—") and d.abbrechen.text() == "Abbrechen"
    d.reiter.setCurrentIndex(2)
    assert d.abbrechen.text() == "Schließen" and not d.bei_benutzer.isEnabled()
    erste = [z for z, _ in b._symbol_daten().benutzer()]
    assert d.liste.topLevelItemCount() == len(erste) and not d.hoch.isEnabled()
    d.liste.setCurrentItem(d.liste.topLevelItem(0)); d.runter.click()
    assert [z for z, _ in b._symbol_daten().benutzer()][:2] == [erste[1], erste[0]]
    d.liste.topLevelItem(0).setCheckState(0, Qt.Unchecked)
    assert erste[1] not in b._symbol_daten().sichtbar() and erste[1] not in b.klappe("symbolKlappe").knoepfe
    d.liste.setCurrentItem(d.liste.topLevelItem(1)); d.entfernen.click()
    assert erste[0] not in [z for z, _ in b._symbol_daten().benutzer()]
    d.reiter.setCurrentIndex(0); d.zeichencode.setText("A"); d.von.setCurrentIndex(1); d._code_getippt("21"); d.bei_benutzer.click()
    assert b._symbol_daten().benutzer()[-1] == ("!", True)
    d.reiter.setCurrentIndex(2); d.zurueck.click()
    assert [z for z, _ in b._symbol_daten().benutzer()] == list(b.BENUTZER_SYMBOLE)


def test_symbol_sonderzeichen_rollt_und_fuegt_ein(fenster):
    """Reiter „Sonderzeichen“: Liste rollt über zwölf Zeilen hinaus; das Zeichen des gewählten Eintrags (auch unsichtbare) wird eingefügt."""
    from lunivo_writer.oberflaeche.dialoge.einfuegen.sonderzeichen import SonderzeichenDialog
    e = fenster.current_editor()
    d = SonderzeichenDialog(None, e.insertPlainText, fenster.befehle._symbol_daten())
    assert d.sonder.topLevelItemCount() > 12
    d.reiter.setCurrentIndex(1)
    d.sonder.setCurrentItem(d.sonder.topLevelItem(d.sonder.topLevelItemCount() - 1)); d.ok.click()
    assert e.toPlainText().endswith("’")


def test_zahl_typen():
    from lunivo_writer.editor.text.zahlformat import zahl_text
    assert [zahl_text(14, "roemisch"), zahl_text(28, "gross"), zahl_text(3, "klein"), zahl_text(5, "kreis"), zahl_text(7, "null")] == \
        ["XIV", "AB", "c", "⑤", "07"]
    assert [zahl_text(n, "wort") for n in (1, 21, 101, 1000, 2026)] == ["eins", "einundzwanzig", "einhunderteins", "eintausend",
                                                                        "zweitausendsechsundzwanzig"]
    with pytest.raises(ValueError):
        zahl_text(0, "roemisch")


def test_zahl_fenster_prueft_eingabe(app):
    from lunivo_writer.oberflaeche.dialoge.einfuegen.einfuegen_fenster import ZahlDialog
    d = ZahlDialog()
    d.zahl.setText("abc"); d._pruefen()
    assert d.result() == 0 and d.hinweis.text()
    d.zahl.setText("12"); d.typ.setCurrentRow(3); d._pruefen()
    assert d.result() == 1 and d.ergebnis() == "XII"










def test_datei_objekt_wie_vorlage(fenster, tmp_path, monkeypatch):
    from lunivo_writer.oberflaeche.baukasten.dokument import speichern_fenster as SF
    datei = tmp_path / "notiz.txt"; datei.write_text("Aus der Datei", encoding="utf-8")
    gefragt = []
    monkeypatch.setattr(SF, "datei_waehlen", lambda p, titel, start, filt, mehrere=False: gefragt.append((titel, filt)) or [str(datei)])
    fenster.befehle.dateiObjekt()
    assert gefragt[0][0] == "Dateiobjekt einfügen" and "PDF (*.pdf)" in gefragt[0][1]
    assert "Aus der Datei" in fenster.current_editor().toPlainText()






def test_tabelle_in_text_fenster_wie_vorlage():
    from lunivo_writer.oberflaeche.dialoge.einfuegen.einfuegen_fenster import TrennerDialog
    from PySide6.QtWidgets import QRadioButton
    d = TrennerDialog(None, zu_tabelle=False)
    assert [r.text().replace("&", "") for r in d.findChildren(QRadioButton)] == ["Absätze", "Tabstopps", "Kommata", "Andere:"]
    assert d.trenner() == "\t" and d.geschachtelt.isChecked() and d.geschachtelt.isEnabled()






def _seitentext(e, n):
    """n Seiten Text, jede mit eigenem Seitenumbruch davor; die Schreibmarke steht mitten auf Seite 1."""
    from PySide6.QtGui import QTextBlockFormat
    for i in range(n):
        if i:
            e.insert_page_break()
        for j, t in enumerate(("Anfang", "Mitte", "Ende")):
            c = e.textCursor()
            if j:
                c.insertBlock(QTextBlockFormat())
            c.insertText(f"Seite {i + 1} {t}"); e.setTextCursor(c)
    c = e.textCursor(); c.setPosition(10); e.setTextCursor(c)










def test_seitenzahl_vorgaben_und_entfernen(fenster):
    from lunivo_writer.editor.seite import seitenzahl as SZ
    from lunivo_writer.modelle.seite import HeaderFooter, PageSettings
    p = PageSettings(); p.header = HeaderFooter("Bericht", "left")
    SZ.seitenzahl_setzen(p, "kopf", "right", "Seite {PAGE} von {PAGES}")
    assert (p.header.text, p.header.align) == ("Bericht Seite {PAGE} von {PAGES}", "right")
    SZ.seitenzahl_setzen(p, "fuss", "center")
    assert p.footer.text == "{PAGE}" and p.header.text == "Bericht"          # nicht doppelt
    assert SZ.seitenzahlen_entfernen(p) and p.footer.text == "" and not SZ.seitenzahlen_entfernen(p)
    m = fenster.befehle.klappe("seitenzahlKlappe")
    assert len(m.knoepfe) == 10 and all(k.isEnabled() for k in m.knoepfe.values())        # außen/innen wie in der Vorlage wählbar
    m.gewaehlt.emit("fuss_rechts")
    s = fenster.current_editor().abschnitt_seite()
    assert (s.footer.text, s.footer.align) == ("{PAGE}", "right")


def test_seitenzahl_zahlenart_aussen_kapitel():
    from lunivo_writer.editor.seite import seitenzahl as SZ
    from lunivo_writer.modelle.seite import PageSettings
    p = PageSettings(); p.seiten_format = "roem_gross"
    assert SZ.text("Seite {PAGE} von {PAGES}", 4, 9, p) == "Seite IV von 9"
    p.kapitel_ebene, p.kapitel_trenner, p.seiten_format = 1, ".", "dezimal"
    assert SZ.nummer(3, p, "2") == "2.3" and SZ.nummer(3, p, "") == "3"
    assert [SZ.ausrichtung("aussen", n) for n in (1, 2)] == ["right", "left"]
    assert [SZ.ausrichtung("innen", n) for n in (1, 2)] == ["left", "right"] and SZ.ausrichtung("center", 2) == "center"




def test_seitenzahl_fenster_wie_vorlage(app):
    from lunivo_writer.modelle.seite import PageSettings
    from lunivo_writer.oberflaeche.dialoge.einfuegen.einfuegen_fenster import SeitenzahlDialog
    d = SeitenzahlDialog(None, PageSettings())
    assert d.muster.count() == 9 and d.position.count() == 10 and d.position.currentText() == "Unten zentriert"
    assert [d.ebene.itemText(i) for i in (0, 8)] == ["Überschrift 1", "Überschrift 9"]
    assert not d.ebene.isEnabled() and not d.start.isEnabled() and d.fortsetzen.isChecked()       # grau wie in der Vorlage
    assert [b.text() for b in d.bereich.buttons()] == ["Gesamtes &Dokument", "Von aktueller Seite (&p)", "Aktueller Abschnit&t"]
    d.kapitel.setChecked(True); d.trenner.setCurrentIndex(1); d.beginnen.setChecked(True); d.start.setValue(5)
    d.muster.setCurrentIndex(5); d.position.setCurrentIndex(3)
    assert d.ebene.isEnabled() and d.beispiel.text() == "1.1, 1.A"
    assert d.werte() == {"ort": "kopf", "ausrichtung": "aussen", "muster": "{PAGE}", "format": "roem_gross", "start": 5,
                         "kapitel": (1, "."), "bereich": "dokument"}






def test_wasserzeichen_galerie(fenster):
    import json
    m = fenster.befehle.klappe("wasserzeichenKlappe")
    assert {"VERTRAULICH", "EILT", "neu"} <= set(m.knoepfe) and m.knoepfe["eigen0"].isHidden()
    m.gewaehlt.emit("EILT")
    assert fenster.current_editor().abschnitt_seite().watermark["text"] == "EILT"
    fenster.settings.set(fenster.befehle.EIGENE_WASSERZEICHEN, json.dumps([{"text": "ENTWURF", "winkel": 0}]))
    m.aboutToShow.emit()
    assert not m.knoepfe["eigen0"].isHidden() and m.knoepfe["eigen0"].toolTip() == "ENTWURF"
    m.gewaehlt.emit("eigen0")
    assert fenster.current_editor().abschnitt_seite().watermark["text"] == "ENTWURF"


def test_wasserzeichen_fenster_wie_vorlage(app, tmp_path):
    from PySide6.QtGui import QColor, QImage
    from lunivo_writer.oberflaeche.dialoge.einfuegen.wasserzeichen_fenster import WasserzeichenDialog
    d = WasserzeichenDialog(None, None)
    assert not d.mit_bild.isChecked() and not d.mit_text.isChecked() and d.ergebnis() is None
    assert not d.zoom.isEnabled() and not d.inhalt.isEnabled() and not d.transparenz.isEnabled()      # grau wie in der Vorlage
    assert d.inhalt.itemText(1) == "NICHT KOPIEREN" and d.groesse.itemText(0) == "Automatisch" and d.transparenz.value() == 50
    assert [d.bereich_wahl.itemText(i) for i in range(2)] == ["Gesamtes Dokument", "Aktueller Abschnitt"]
    d.mit_text.setChecked(True); d.inhalt.setCurrentText("MUSTER"); d.text_format.setCurrentIndex(1); d.text_v.setCurrentIndex(1)
    assert d.inhalt.isEnabled() and d.text_v_mm.isEnabled() and not d.text_h_mm.isEnabled()
    w = d.ergebnis()
    assert (w["text"], w["winkel"], w["v"], w["groesse_pt"], w["transparenz"]) == ("MUSTER", -45, "oben", 0, 50)
    img = QImage(40, 20, QImage.Format_RGB32); img.fill(QColor("red")); img.save(str(tmp_path / "b.png"))
    d.mit_bild.setChecked(True)
    assert not d.mit_text.isChecked()                                                      # nur eine Art
    assert d.bild_laden(str(tmp_path / "b.png")) and d.bild_name.text() == "b.png"
    d.bereich_wahl.setCurrentIndex(1)
    w = d.ergebnis()
    assert w["bild"] and w["auswaschen"] and w["zoom"] == 0 and w["abschnitt"] and d.bereich() == "abschnitt"
    d2 = WasserzeichenDialog(None, w)                                                       # Vorbelegung
    assert d2.mit_bild.isChecked() and d2.bereich() == "abschnitt" and d2.ergebnis()["bild"] == w["bild"]








def test_diagramm_alle_arten_und_fenster(app):
    from lunivo_writer.editor.diagramme import diagramm as D
    from lunivo_writer.oberflaeche.dialoge.einfuegen.einfuegen_dialoge import DiagrammDialog
    for _g, _s, unter in D.TYPEN:
        for u, _n in unter:
            img = D.bild(u, "T", D.BEISPIEL_KATEGORIEN, D.BEISPIEL_REIHEN, 200, 140)
            assert not img.isNull() and img.pixelColor(100, 70).name() != "#000000"
    d = DiagrammDialog(None)
    gruppen = [g for g, _s, _u in D.TYPEN]
    assert gruppen == ["Säule", "Linie", "Kreis", "Balken", "Fläche", "X Y (Punkt)", "Kurs", "Netz", "Kombination"]
    assert d.arten.count() == len(gruppen) + 1 and d.arten.item(d.arten.count() - 1).text() == "Vorlagen"
    d.arten.setCurrentRow(1)                                               # Linie
    assert d.untertyp == "linie" and d.name.text() == "Linie" and len(d._knoepfe.buttons()) == 6
    assert d.daten()["kategorien"] == D.BEISPIEL_KATEGORIEN and d.kombi_teil.isHidden()
    d.arten.setCurrentRow(gruppen.index("Kurs"))
    assert d.untertyp == "kurs_hts" and len(d._knoepfe.buttons()) == 4
    # Kombination wie in der Vorlage: vier Untertypen und die Tabelle Datenreihen / Diagrammtyp / Sekundärachse
    d.arten.setCurrentRow(gruppen.index("Kombination"))
    assert len(d._knoepfe.buttons()) == 4 and not d.kombi_teil.isHidden() and len(d._kombi_felder) == 3
    assert d.kombi == [("saeule", False), ("saeule", False), ("linie", False)]
    _l, box, kasten = d._kombi_felder[2]
    kasten.setChecked(True)
    assert d.untertyp == "kombi_eigen" and d.daten()["kombi"][2] == ["linie", True]
    d.arten.setCurrentRow(d.arten.count() - 1)                             # Vorlagen: leere Seite, Knopf, OK aus
    assert d.vorlagen_seite.isVisibleTo(d) and not d.seite.isVisibleTo(d) and not d._ok.isEnabled() and d.daten() == {}
    d.arten.setCurrentRow(gruppen.index("Kreis"))                          # Beispieldaten folgen der Art, solange nichts geändert wurde
    assert d._ok.isEnabled() and d.titel_text == "Vertrieb" and d.kategorien[0] == "1. Quartal"
    d._daten_geaendert = True; d.titel_text = "Mein Titel"
    d.arten.setCurrentRow(gruppen.index("Fläche"))
    assert d.titel_text == "Mein Titel"


def test_datum_fenster_mit_feld(app):
    from lunivo_writer.oberflaeche.dialoge.einfuegen.einfuegen_dialoge import DatumDialog
    d = DatumDialog(None, "en_US")
    assert d.sprache.currentData() == "en_US" and "/" in d.ergebnis()
    assert d.feldanweisung() is None
    d.auto.setChecked(True)
    assert d.feldanweisung() == 'DATE \\@ "M/d/yyyy"'
    d.sprache.setCurrentIndex(0); d.liste.setCurrentRow(d.liste.count() - 3)          # HH:mm
    assert d.feldanweisung().startswith("TIME")


def test_hyperlink_fenster(app, tmp_path):
    from lunivo_writer.oberflaeche.dialoge.einfuegen.einfuegen_fenster import HyperlinkDialog
    H = HyperlinkDialog
    assert H.adresse_zu_href("www.beispiel.de") == "https://www.beispiel.de"
    assert H.adresse_zu_href("/tmp/a b.pdf") == "file:///tmp/a b.pdf"
    d = H(None, text="hier", ziele=[{"art": "Überschrift", "text": "Kapitel 1", "pos": 0, "block": 3}], ordner=str(tmp_path))
    assert not d.ok.isEnabled()
    d.adresse.setText("www.beispiel.de"); d.tipp = "Zur Seite"
    assert d.ok.isEnabled() and d.ergebnis() == {"art": "datei", "href": "https://www.beispiel.de", "text": "hier", "tipp": "Zur Seite"}
    d.art_waehlen(2); assert not d.ok.isEnabled()
    d.mail.setText("kay@example.org"); d.betreff.setText("Hallo Welt")
    r = d.ergebnis()
    assert r["href"].startswith("mailto:kay@example.org?subject=Hallo") and d.ok.isEnabled()
    d.art_waehlen(1)
    kapitel = d.stellen.topLevelItem(1).child(0)
    d.stellen.setCurrentItem(kapitel)
    assert d.ergebnis()["ziel"]["block"] == 3




def test_objekt_fenster(app, tmp_path):
    from lunivo_writer.oberflaeche.dialoge.einfuegen.einfuegen_fenster import ObjektDialog
    txt = tmp_path / "notiz.txt"; txt.write_text("Hallo")
    zip_ = tmp_path / "paket.zip"; zip_.write_bytes(b"PK")
    d = ObjektDialog(None)
    assert not d.neu.isEnabled() and not d.ok.isEnabled()
    d.datei.setText(str(txt)); assert d.art() == "text" and d.ok.isEnabled()
    d.datei.setText(str(zip_)); assert d.art() == "symbol"
    d.datei.setText(str(txt)); d.symbol.setChecked(True); assert d.art() == "symbol"








