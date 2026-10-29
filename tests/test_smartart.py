import pytest

from PySide6.QtGui import QTextCursor

from lunivo_writer.editor import formen
from lunivo_writer.editor import smartart as SA
from lunivo_writer.models.page import PageSettings
from lunivo_writer.services import file_service as formats
from lunivo_writer.ui.document.document_editor import DocumentEditor


def test_punkte_ebenen():
    assert SA.punkte("A\n  B\n    C\n\nD") == [(0, "A"), (1, "B"), (2, "C"), (0, "D")]
    assert SA.punkte("A\n\tB") == [(0, "A"), (1, "B")]


def test_jedes_layout_zeichnet(app):
    for lay in SA.LAYOUTS:
        for farben in SA.FARBEN:
            img = SA.zeichnen({"layout": lay, "farben": farben, "text": SA.MUSTER[lay]})
            assert img.width() > 100 and img.height() > 40
            # nicht leer: irgendwo ein deckendes Pixel
            assert any(img.pixelColor(x, y).alpha() > 200 for x in range(0, img.width(), 7) for y in range(0, img.height(), 7))


@pytest.mark.parametrize("lay", SA.LAYOUTS)
def test_layout_zeichnet_und_laesst_sich_einfuegen(app, lay):
    assert lay in SA.MUSTER
    for text in (SA.MUSTER[lay], "Nur einer", ""):
        img = SA.zeichnen({"layout": lay, "text": text})
        assert img.width() > 100 and img.height() > 40
    ed = DocumentEditor()
    SA.einfuegen(ed, {"layout": lay, "farben": "Bunt", "text": SA.MUSTER[lay]})
    c = QTextCursor(ed.document()); c.setPosition(0); ed.setTextCursor(c)
    assert SA.daten_der_auswahl(ed)["layout"] == lay


def test_hoehe_waechst_mit_punkten(app):
    kurz = SA.zeichnen({"layout": "Liste", "text": "a\nb"})
    lang = SA.zeichnen({"layout": "Liste", "text": "a\nb\nc\nd\ne"})
    assert lang.height() > kurz.height()


def test_einfuegen_aendern_docx_rundreise(app, tmp_path):
    from lunivo_writer.editor import frei_objekt as FO
    ed = DocumentEditor()
    SA.einfuegen(ed, {"layout": "Prozess", "farben": "Blau", "text": "Eins\nZwei\nDrei"})          # freies Objekt, gleich gewählt
    assert FO.art_gewaehlt(ed) == "smartart" and SA.daten_der_auswahl(ed)["layout"] == "Prozess"
    assert SA.aendern(ed, layout="Pyramide", text="Oben\nMitte\nUnten\nBasis")
    d = SA.daten_der_auswahl(ed)
    assert d["layout"] == "Pyramide" and d["text"].startswith("Oben") and d["farben"] == "Blau"
    pfad = str(tmp_path / "s.docx")
    formats.save(pfad, ed.document(), PageSettings())
    neu = DocumentEditor(); neu.setDocument(formats.load(pfad).doc)
    neu._frei_liste(); neu._frei_sel = neu._frei_treffer[0][0]
    assert FO.art_gewaehlt(neu) == "smartart"
    assert SA.daten_der_auswahl(neu) == d                              # nach dem Öffnen noch bearbeitbar
    assert SA.aendern(neu, farben="Grün") and SA.daten_der_auswahl(neu)["farben"] == "Grün"
    assert SA.aendern(neu, layout="Konvergenz", text=SA.MUSTER["Konvergenz"]) and SA.daten_der_auswahl(neu)["layout"] == "Konvergenz"
    pfad2 = str(tmp_path / "s2.docx")
    formats.save(pfad2, neu.document(), PageSettings())                # neues Layout übersteht den DOCX-Rundweg
    neu2 = DocumentEditor(); neu2.setDocument(formats.load(pfad2).doc)
    neu2._frei_liste(); neu2._frei_sel = neu2._frei_treffer[0][0]
    assert SA.daten_der_auswahl(neu2)["layout"] == "Konvergenz"


def test_altes_inline_smartart_bleibt_bearbeitbar(app):
    from lunivo_writer.editor import einfuegen as E
    d = {"layout": "Liste", "farben": "Blau", "text": "A\nB"}
    ed = DocumentEditor()
    E.qimage_einfuegen(ed, SA.zeichnen(d), "SmartArt", "smartart", d)
    c = QTextCursor(ed.document()); c.setPosition(0); ed.setTextCursor(c)
    assert SA.daten_der_auswahl(ed) == d and SA.aendern(ed, farben="Grün") and SA.daten_der_auswahl(ed)["farben"] == "Grün"


def test_kein_smartart_wird_nicht_geaendert(app):
    ed = DocumentEditor()
    ed.setPlainText("Text")
    assert SA.daten_der_auswahl(ed) is None and not SA.aendern(ed, layout="Liste")


# ---- Knotenbaum und Knotenbefehle -----------------------------------------------------------------------------------------------------
def test_knoten_aus_und_zu_text_und_katalog(app):
    kn = SA.knoten_aus_text("A\n  B\n    • Punkt\n  C")
    assert [(k["text"], k["ebene"], k["bullets"]) for k in kn] == [("A", 0, []), ("B", 1, ["Punkt"]), ("C", 1, [])]
    assert SA.knoten_aus_text(SA.text_aus_knoten(kn)) == kn
    assert len(SA.LAYOUT_KATALOG) == 15 and SA.LAYOUT_KATALOG[0]["schluessel"] == "Organigramm" == SA.STANDARD_LAYOUT
    assert [e["schluessel"] for e in SA.LAYOUT_KATALOG] == ["Organigramm", "Blockraster", "Punktliste", "Balkenliste", "Beschreibungsliste", "Spaltenrahmen",
                                                            "Spalten", "Bildliste", "Perspektive", "Radial", "Prozess", "Konvergenz", "Kartenprozess",
                                                            "Kreisbeziehung", "Segmentzyklus"]
    assert set(SA.KATALOG_LAYOUTS) < set(SA.LAYOUTS) and len(set(SA.LAYOUTS)) == len(SA.LAYOUTS)          # alte Layouts bleiben zeichenbar
    assert len({e["name"] for e in SA.LAYOUT_KATALOG}) == 15
    assert all(e["schluessel"] in SA.LAYOUTS and e["name"] and e["beschreibung"] and e["muster"] for e in SA.LAYOUT_KATALOG)
    assert SA.neue_daten()["text"] == SA.MUSTER["Organigramm"]


def test_neue_layouts_zeichnen_mit_knotenrechtecken(app):
    for lay in SA.KATALOG_LAYOUTS:
        for text in (SA.MUSTER[lay], "Nur einer", "A\n  B\n  C\nD\n  • x\nE"):
            d = {"layout": lay, "text": text}
            img, reg = SA.zeichnen_mit_knoten(d)
            assert any(img.pixelColor(x, y).alpha() > 200 for x in range(0, img.width(), 5) for y in range(0, img.height(), 5)), lay
            assert set(reg) == {k["id"] for k in SA.knoten_von(d)} and all(r.width() > 0 and r.height() > 0 for r in reg.values()), lay


def test_knoten_rechtecke_und_stile(app):
    for lay in SA.LAYOUTS:
        d = {"layout": lay, "text": SA.MUSTER[lay]}
        reg = SA.knoten_rechtecke(d)
        assert set(reg) == {k["id"] for k in SA.knoten_von(d)}, lay
    d = {"layout": "Prozess", "text": "A\nB\nC", "rtl": True}
    links = SA.knoten_rechtecke({"layout": "Prozess", "text": "A\nB\nC"})
    rechts = SA.knoten_rechtecke(d)
    assert rechts["k1"].x() > links["k1"].x() and rechts["k3"].x() < links["k3"].x()                # gespiegelt
    assert len({SA.zeichnen({"layout": "Prozess", "text": "A\nB", "stil": s}).constBits().tobytes() for s in range(5)}) == 5
    bilder = {v: SA.zeichnen({"layout": "Organigramm", "text": "A\n  B\n  C\n  D\n    E\n  F", "hierarchie": v})
              for v in ("standard", "beide", "haengend_links", "haengend_rechts")}
    assert len({b.constBits().tobytes() for b in bilder.values()}) == 4 and bilder["beide"].height() < bilder["haengend_rechts"].height()


def test_smartart_knotenbefehle(fenster_sa):
    from lunivo_writer.editor import frei_objekt as FO
    ed, b = fenster_sa
    SA.einfuegen(ed, SA.LAYOUT_KATALOG[0])                                                       # Organigramm mit Mustertext
    assert FO.art_gewaehlt(ed) == "smartart" and SA.daten_der_auswahl(ed)["layout"] == "Organigramm"
    assert not b.kann_smartartLevelErhoehen() and not b.kann_smartartAufzaehlung()                # noch kein Knoten gewählt
    b.tun('smartartKnotenWaehlen:["k2"]'); assert SA.knoten_gewaehlt(ed) == "k2"
    assert b.kann_smartartLevelReduzieren() and not b.kann_smartartLevelErhoehen() and not b.kann_smartartVorwaerts()
    b.tun('smartartFormEinfuegen:["nach"]'); d = SA.daten_der_auswahl(ed)
    kn = SA.knoten_von(d); assert [k["ebene"] for k in kn] == [0, 1, 2, 2, 2, 1] and SA.knoten_gewaehlt(ed) == "k6"
    b.tun('smartartLevel:["erhoehen"]'); assert [k["ebene"] for k in SA.knoten_von(SA.daten_der_auswahl(ed))][-1] == 2
    b.tun('smartartLevel:["reduzieren"]'); b.tun('smartartVerschieben:["vor"]')
    assert [k["id"] for k in SA.knoten_von(SA.daten_der_auswahl(ed))][1:3] == ["k6", "k2"]            # vor den Teilbaum von k2
    b.tun('smartartKnotenWaehlen:["k2"]'); b.tun('smartartFormEinfuegen:["assistent"]'); b.tun('smartartFormEinfuegen:["ueber"]')
    b.tun('smartartAufzaehlung'); d = SA.daten_der_auswahl(ed); kn = SA.knoten_von(d)
    assert any(k.get("assistent") for k in kn) and any(k["bullets"] for k in kn) and "• Text" in d["text"]
    assert SA.knoten_text_setzen(ed, "k1", "Kay") and SA.knoten_text(ed, "k1") == "Kay" and SA.daten_der_auswahl(ed)["text"].startswith("Kay")
    b.smartartRechtsLinks(); assert b.an_smartartRechtsLinks()
    b.tun('smartartHierarchie:["haengend_links"]'); assert SA.daten_der_auswahl(ed)["hierarchie"] == "haengend_links"
    b.tun('smartartStil:[4]'); assert SA.daten_der_auswahl(ed)["stil"] == 4
    assert SA.aendern(ed, layout="Prozess") and not b.kann_smartartHierarchie() and not b.smartartHierarchie(None, "beide")
    assert SA.aendern(ed, text="Nur\n  neu") and "knoten" not in SA.daten_der_auswahl(ed)             # neuer Text ersetzt die Knoten


@pytest.fixture
def fenster_sa(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.resize(1200, 800); w.show()
    yield w.current_editor(), w.befehle
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()
