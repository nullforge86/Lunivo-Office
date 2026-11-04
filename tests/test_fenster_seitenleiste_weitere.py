"""Weitere Fenster öffnen in der rechten Seitenleiste (``PanelFaehig``) und passen dort in die Breite: Oberfläche (Register, Symbole,
Benutzeroberfläche), Lesehilfe, „Welche Hilfe wann“, die kleinen Abfragen (``EingabeFenster``), Diagrammdaten, Tabelleneigenschaften,
Bild zuschneiden (Kay, 2026-10-28: Fenster nicht mehr frei, sondern in der Seitenleiste, nach Funktion im Reiter)."""
from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings, QTimer
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QTabWidget, QWidget

from lunivo_writer.services.settings_service import Settings
from lunivo_writer.ui.baukasten.eingabe_fenster import EingabeFenster
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig, ZusatzPanel
from lunivo_writer.ui.main_window import MainWindow


def _settings(tmp_path):
    return Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat))


def _hauptfenster(tmp_path):
    w = MainWindow(_settings(tmp_path)); w.new_document()
    return w


def _daten():
    from lunivo_writer.ui.ribbon.ribbon_bar import lade_register
    return lade_register()


def _kopffuss_optionen(tp):
    """Das Fenster „Optionen für Kopf- und Fußzeile“ (lokale Klasse in ``kfOptionen``): ``ausfuehren`` fängt es ab, statt es zu zeigen."""
    from lunivo_writer.ui.baukasten import fenster_stapel as F
    w = _hauptfenster(tp); fang = []
    alt = F.ausfuehren
    F.ausfuehren = lambda d, *a, **k: (fang.append(d), False)[1]
    try:
        w.befehle.kfOptionen()
    finally:
        F.ausfuehren = alt
    fang[0]._halter = w
    return fang[0]


def _o():
    from lunivo_writer.ui.dialogs import oberflaeche_dialoge as O
    return O


FENSTER = {
    # Reiter Ansicht
    "Register anpassen": lambda tp: _o().RegisterAnpassenDialog(None, _settings(tp), _daten()),
    "Schnellzugriff": lambda tp: _o().SchnellzugriffDialog(None, _settings(tp), __import__("lunivo_writer.ui.ribbon.ribbon_bar", fromlist=["x"]).RegisterBand.SCHNELL_ALLE, []),
    "Symbol austauschen": lambda tp: _o().SymbolTauschenDialog(None, _settings(tp)),
    "Eigene Zeichnung": lambda tp: _o().EigeneZeichnungDialog(None),
    "Benutzeroberfläche": lambda tp: _o().OberflaecheDialog(None, _settings(tp)),
    # Reiter Schreibhilfe
    "Lesehilfe": lambda tp: __import__("lunivo_writer.ui.dialogs.lesehilfe_dialog", fromlist=["x"]).LesehilfeDialog(_hauptfenster(tp)),
    "Welche Hilfe wann": lambda tp: __import__("lunivo_writer.ui.dialogs.welche_hilfe", fromlist=["x"]).HilfeWannDialog(_hauptfenster(tp)),
    # kleine Abfragen (Sprache, Seriendruckfeld, Adressblock, Zitierweise, Zitat, Inhalte einfügen)
    "Abfrage Auswahl": lambda tp: EingabeFenster(None, "Sprache für die Korrekturhilfen", "Sprache des Dokuments (wird in der Datei vermerkt).\n"
                                                 "Die Schreibhilfe selbst prüft weiter auf Deutsch.",
                                                 ["Deutsch", "Deutsch (Österreich)", "Deutsch (Schweiz)", "Englisch", "Englisch (UK)", "Französisch"], 0),
    "Abfrage Text": lambda tp: EingabeFenster(None, "Seriendruckfeld", "Feldname (muss in der Kopfzeile der Empfängerliste stehen):", None, text="Name"),
    # Einfügen, Tabelle, Bild
    "Diagrammdaten": lambda tp: __import__("lunivo_writer.ui.dialogs.einfuegen_dialoge", fromlist=["x"]).DiagrammDatenDialog(
        None, "Titel", ["A", "B", "C"], {"Reihe 1": [1.0, 2.0, 3.0], "Reihe 2": [2.0, 1.0, 4.0]}),
    "Tabelleneigenschaften": lambda tp: __import__("lunivo_writer.ui.dialogs.dokument_dialoge", fromlist=["x"]).TabellenEigenschaftenDialog(None, 100, 0, 1.0, 4.0, True),
    "Bild zuschneiden": lambda tp: __import__("lunivo_writer.ui.dialogs.dokument_dialoge", fromlist=["x"]).BildZuschneidenDialog(None),
    # Sendungen, Verweise, Formularfelder, Silben (alle mit FormularGitter/FlussLayout)
    "Umschlag": lambda tp: __import__("lunivo_writer.ui.dialogs.sendungen_dialoge", fromlist=["x"]).UmschlagDialog(None),
    "Etiketten": lambda tp: __import__("lunivo_writer.ui.dialogs.sendungen_dialoge", fromlist=["x"]).EtikettenDialog(None),
    "Seriendruck": lambda tp: __import__("lunivo_writer.ui.dialogs.sendungen_dialoge", fromlist=["x"]).SeriendruckDialog(None, ["Name"], ""),
    "Regel": lambda tp: __import__("lunivo_writer.ui.dialogs.sendungen_dialoge", fromlist=["x"]).RegelDialog(None),
    "Quelle": lambda tp: __import__("lunivo_writer.ui.dialogs.verweise_dialoge", fromlist=["x"]).QuelleDialog(None),
    "Formularfeld": lambda tp: __import__("lunivo_writer.ui.dialogs.formular_dialog", fromlist=["x"]).FormFeldDialog(_hauptfenster(tp), "auswahl"),
    # Umgestellt auf FormularGitter/FlussLayout (Schreibweise, Auswahl, Überprüfen, Mailings, Sortieren, Umschlossen, Formatvorlagen)
    "Schreibweise": lambda tp: __import__("lunivo_writer.ui.baukasten.schreibweise_dialog", fromlist=["x"]).SchreibweiseDialog(None),
    "Auswahlbereich": lambda tp: __import__("lunivo_writer.ui.baukasten.auswahl_bereich", fromlist=["x"]).AuswahlBereich(None, None),
    "Wörter zählen": lambda tp: __import__("lunivo_writer.ui.dialogs.ueberpruefen_fenster", fromlist=["x"]).WoerterDialog(None, {"seiten": 1}, {"seiten": 1}),
    "Bearbeitung einschränken": lambda tp: __import__("lunivo_writer.ui.dialogs.ueberpruefen_fenster", fromlist=["x"]).SchutzDialog(None, None),
    "Seriendruckfeld": lambda tp: __import__("lunivo_writer.ui.dialogs.serien_fenster", fromlist=["x"]).FeldDialog(None, ["Name", "Ort"]),
    "Text sortieren": lambda tp: __import__("lunivo_writer.ui.baukasten.sortieren_dialog", fromlist=["x"]).SortierenDialog(None, ["a", "b"]),
    "Sortieroptionen": lambda tp: __import__("lunivo_writer.ui.baukasten.sortieren_dialog", fromlist=["x"]).SortierOptionenDialog(None),
    "Eingeschlossene Zeichen": lambda tp: __import__("lunivo_writer.ui.baukasten.umschlossen_dialog", fromlist=["x"]).UmschlosseneZeichenDialog(None, "A"),
    "Formatvorlagen-Bereich": lambda tp: __import__("lunivo_writer.ui.baukasten.formatvorlagen_bereich", fromlist=["x"]).FormatvorlagenBereich(None),
    "Seite einrichten": lambda tp: __import__("lunivo_writer.ui.dialogs.dokument_dialoge", fromlist=["x"]).PageSetupDialog(__import__("lunivo_writer.models.page", fromlist=["x"]).PageSettings()),
    "Kopfzeile": lambda tp: __import__("lunivo_writer.ui.dialogs.dokument_dialoge", fromlist=["x"]).HeaderFooterDialog("Kopfzeile", __import__("lunivo_writer.models.page", fromlist=["x"]).HeaderFooter("", "center")),
    "Tabelle einfügen": lambda tp: __import__("lunivo_writer.ui.dialogs.dokument_dialoge", fromlist=["x"]).TableDialog(None),
    "Bildgröße": lambda tp: __import__("lunivo_writer.ui.dialogs.dokument_dialoge", fromlist=["x"]).BildGroesseDialog(400, 300),
    "Zoom": lambda tp: __import__("lunivo_writer.ui.dialogs.dokument_dialoge", fromlist=["x"]).ZoomDialog(None, 1.0),
    "Liste": lambda tp: __import__("lunivo_writer.ui.baukasten.liste_dialog", fromlist=["x"]).ListenDialog(None),
    "Nummerierung anpassen": lambda tp: __import__("lunivo_writer.ui.baukasten.liste_dialog", fromlist=["x"]).NummerierungAnpassenDialog(None),
    "Gliederung anpassen": lambda tp: __import__("lunivo_writer.ui.baukasten.liste_dialog", fromlist=["x"]).GliederungAnpassenDialog(None),
    "Texteffekt": lambda tp: __import__("lunivo_writer.ui.baukasten.texteffekt_dialog", fromlist=["x"]).TexteffektDialog(None),
    "Wasserzeichen": lambda tp: __import__("lunivo_writer.ui.dialogs.wasserzeichen_fenster", fromlist=["x"]).WasserzeichenDialog(None, None),
    "Inhaltsverzeichnis": lambda tp: __import__("lunivo_writer.ui.dialogs.verweise_fenster", fromlist=["x"]).InhaltsverzeichnisDialog(None),
    "Diagramm": lambda tp: __import__("lunivo_writer.ui.dialogs.diagramm_fenster", fromlist=["x"]).DiagrammDialog(None),
    # Einfügen: Felder, Trenner, Seitenzahl, Hyperlink, Objekt, Datum, Piktogramm, Deckblatt
    "Felder": lambda tp: __import__("lunivo_writer.ui.dialogs.einfuegen_fenster", fromlist=["x"]).FelderDialog(None, {}),
    "Trenner": lambda tp: __import__("lunivo_writer.ui.dialogs.einfuegen_fenster", fromlist=["x"]).TrennerDialog(None, zu_tabelle=True, texte=["a;b"]),
    "Seitenzahl": lambda tp: __import__("lunivo_writer.ui.dialogs.einfuegen_fenster", fromlist=["x"]).SeitenzahlDialog(None),
    "Hyperlink": lambda tp: __import__("lunivo_writer.ui.dialogs.einfuegen_fenster", fromlist=["x"]).HyperlinkDialog(None),
    "Objekt": lambda tp: __import__("lunivo_writer.ui.dialogs.einfuegen_fenster", fromlist=["x"]).ObjektDialog(None),
    "Datum und Uhrzeit": lambda tp: __import__("lunivo_writer.ui.dialogs.einfuegen_dialoge", fromlist=["x"]).DatumDialog(None),
    "Piktogramm": lambda tp: __import__("lunivo_writer.ui.dialogs.einfuegen_dialoge", fromlist=["x"]).PiktogrammDialog(None),
    "Deckblatt": lambda tp: __import__("lunivo_writer.ui.dialogs.einfuegen_dialoge", fromlist=["x"]).DeckblattDialog(None, "Kay"),
    "Silben farbig": lambda tp: __import__("lunivo_writer.ui.dialogs.silben_dialog", fromlist=["x"]).SilbenDialog(_hauptfenster(tp)),
    # Nachgetragen (Inventar 2026-11-04): alle weiteren PanelFaehig-Fenster der Seitenleiste
    "Rahmen und Schattierung": lambda tp: __import__("lunivo_writer.ui.baukasten.rahmen_schattierung", fromlist=["x"]).RahmenSchattierungDialog(None),
    "Farben": lambda tp: __import__("lunivo_writer.ui.baukasten.farbwaehler", fromlist=["x"]).FarbenDialog(None),
    "Formatvorlage": lambda tp: __import__("lunivo_writer.ui.baukasten.formatvorlage_dialog", fromlist=["x"]).FormatvorlageDialog(None),
    "Kopf- und Fußzeile Optionen": _kopffuss_optionen,
    "Layout Objekt": lambda tp: __import__("lunivo_writer.ui.baukasten.layout_dialog_objekt", fromlist=["x"]).LayoutDialogObjekt(None),
    "SmartArt Foto": lambda tp: __import__("lunivo_writer.ui.dialogs.smartart_dialog_foto", fromlist=["x"]).SmartArtDialogFoto(_hauptfenster(tp)),
    "Layout": lambda tp: __import__("lunivo_writer.ui.baukasten.layout_dialog", fromlist=["x"]).LayoutDialog(None),
    "Ruby": lambda tp: __import__("lunivo_writer.ui.baukasten.ruby_dialog", fromlist=["x"]).RubyDialog(None),
    "Textbaustein": lambda tp: __import__("lunivo_writer.ui.dialogs.einfuegen_dialoge", fromlist=["x"]).BausteinDialog(None, __import__("PySide6.QtWidgets", fromlist=["x"]).QTextEdit()),
    "Textmarke": lambda tp: __import__("lunivo_writer.ui.dialogs.verweise_dialoge", fromlist=["x"]).TextmarkeDialog(None, _hauptfenster(tp).current_editor()),
    "Quellen": lambda tp: __import__("lunivo_writer.ui.dialogs.verweise_dialoge", fromlist=["x"]).QuellenDialog(None, _hauptfenster(tp).current_editor()),
    "KI-Einstellungen": lambda tp: __import__("lunivo_writer.ui.dialogs.ki_dialoge", fromlist=["x"]).KIEinstellungenDialog(_hauptfenster(tp)),
    "Schnelle KI-Aktion": lambda tp: __import__("lunivo_writer.ui.dialogs.ki_dialoge", fromlist=["x"]).SchnelleAktionDialog(_hauptfenster(tp)),
    "KI-Ergebnisse": lambda tp: __import__("lunivo_writer.ui.dialogs.ki_dialoge", fromlist=["x"]).ErgebnisseDialog(_hauptfenster(tp)),
}


# Unterfenster, die sich über ``zeige_unter`` als weitere Seite in der Seitenleiste legen (nicht ``PanelFaehig``, aber gleiche Breitenregel).
UNTERFENSTER = {
    "Rahmenoptionen Absatz": lambda tp: __import__("lunivo_writer.ui.baukasten.rahmen_schattierung", fromlist=["x"])._PolsterDialog(None, (1.0, 1.0, 4.0, 4.0)),
    "Rahmenoptionen Seitenrand": lambda tp: __import__("lunivo_writer.ui.baukasten.rahmen_schattierung", fromlist=["x"])._SeitenOptionenDialog(None, {'messen': 'text', 'abstand': (24.0, 24.0, 24.0, 24.0), 'ausrichten': True, 'vordergrund': True, 'kopf': True, 'fuss': True}),
    "Abstand Seitenrand": lambda tp: __import__("lunivo_writer.ui.baukasten.rahmen_schattierung", fromlist=["x"])._AbstandDialog(None, 24.0),
    "Anbieter": lambda tp: __import__("lunivo_writer.ui.dialogs.ki_dialoge", fromlist=["x"]).AnbieterDialog(None, _hauptfenster(tp).ki.konfig),
    "Anbieter bearbeiten": lambda tp: __import__("lunivo_writer.ui.dialogs.ki_dialoge", fromlist=["x"]).AnbieterDialog(None, _hauptfenster(tp).ki.konfig, {"id": "x", "name": "Test", "url": "https://a.example/v1", "schluessel": "", "modell": "m", "verwendungFuer": ["text"]}),
    "KI-Konfiguration": lambda tp: __import__("lunivo_writer.ui.dialogs.ki_dialoge", fromlist=["x"]).KIKonfigurationDialog(_hauptfenster(tp)),
    "MCP-Server": lambda tp: __import__("lunivo_writer.ui.dialogs.ki_dialoge", fromlist=["x"]).McpDialog(None),
    "Tastenkombination": lambda tp: __import__("lunivo_writer.ui.dialogs.sonderzeichen", fromlist=["x"])._TastenFenster(None, "", belegt={}),
    "KI-Modellliste": lambda tp: __import__("lunivo_writer.ui.dialogs.ki_dialoge", fromlist=["x"]).ModellListeDialog(None, _hauptfenster(tp).ki.konfig),
}


# Noch offen (liste_dialog.py): „Beginnen mit:“ ist bei 300 px abgeschnitten. Darf nur kleiner werden.
LABEL_NOCH_ABGESCHNITTEN: set[str] = set()


ALLE = {**FENSTER, **UNTERFENSTER}


@pytest.mark.parametrize("breite", [444, 300])
@pytest.mark.parametrize("name", list(ALLE))
def test_weitere_fenster_in_der_seitenleiste_und_passen(app, tmp_path, name, breite):
    """Jedes Fenster ist ``PanelFaehig`` (Unterfenster: ``zeige_unter``-Seite) und ragt auch bei 300 px (schmalste Seitenleiste) nirgends links oder rechts hinaus."""
    p = ZusatzPanel(); p.verfuegbar, p.verfuegbar_hoehe = breite, 587; p.resize(breite + 36, 727)
    d = ALLE[name](tmp_path)
    assert isinstance(d, PanelFaehig) or name in UNTERFENSTER, name
    p.oeffne(d); p.show(); app.processEvents(); app.processEvents()
    reiter = [w for w in d.findChildren(QTabWidget)]
    seiten = max([r.count() for r in reiter], default=1)
    for i in range(seiten):
        for r in reiter:
            if i < r.count():
                r.setCurrentIndex(i)
        app.processEvents(); app.processEvents()
        vp = p.stapel.currentWidget().sa.viewport()
        zu = [type(c).__name__ for c in d.findChildren(QWidget) if c.isVisible() and c.width() > 0
              and (c.mapTo(vp, c.rect().topLeft()).x() < -1 or c.mapTo(vp, c.rect().topRight()).x() > vp.width())]
        assert not zu, (name, breite, i, zu)
        # Beschriftungen müssen vollständig lesbar sein (nicht am Rand abgeschnitten)
        ab = [l.text() for l in d.findChildren(QLabel) if l.isVisible() and l.text() and not l.wordWrap() and l.pixmap().isNull()
              and not l.text().startswith("<") and l.fontMetrics().horizontalAdvance(l.text().replace("&", "")) > l.width() + 1]
        assert not ab or name in LABEL_NOCH_ABGESCHNITTEN, (name, breite, i, ab)
    p.close()


def _in_der_seitenleiste_bestaetigen(app, w, aktion):
    """Wartet, bis ein Fenster als Seite in der Seitenleiste steht (nicht frei), und ruft ``aktion(dialog)``; danach „OK“."""
    gesehen = {}

    def lauf():
        z = getattr(w.sidebar, "_zusatz", None)
        if z is None or not z._seiten:
            return
        d = z._seiten[-1][0]
        gesehen["titel"] = d.windowTitle()
        gesehen["frei"] = any(t is d for t in QApplication.topLevelWidgets() if t.isVisible())
        aktion(d)
        d.accept()
    uhr = QTimer(); uhr.setSingleShot(True); uhr.setInterval(80); uhr.timeout.connect(lauf); uhr.start()
    return gesehen, uhr


def test_zitierweise_oeffnet_in_der_seitenleiste_und_wirkt(app, tmp_path):
    from lunivo_writer.editor.literatur import ZITIERWEISEN
    w = _hauptfenster(tmp_path); w.resize(1380, 860); w.show()
    ziel = [z for z in ZITIERWEISEN if z != w.current_editor().zitierweise][0]
    gesehen, _uhr = _in_der_seitenleiste_bestaetigen(app, w, lambda d: d.liste.setCurrentRow(ZITIERWEISEN.index(ziel)))
    w.befehle.zitierweise()
    assert gesehen == {"titel": "Zitierweise", "frei": False}
    assert w.current_editor().zitierweise == ziel
    w.current_editor().document().setModified(False); w.close()


def test_seriendruckfeld_abfrage_in_der_seitenleiste(app, tmp_path):
    w = _hauptfenster(tmp_path); w.resize(1380, 860); w.show()
    gesehen, _uhr = _in_der_seitenleiste_bestaetigen(app, w, lambda d: d.feld.setText("Ort"))
    w.befehle.seriendruckfeld()
    assert gesehen == {"titel": "Seriendruckfeld", "frei": False}
    assert "Ort" in w.current_editor().toPlainText()
    w.current_editor().document().setModified(False); w.close()


def test_abbrechen_gibt_nichts_zurueck(app, tmp_path):
    w = _hauptfenster(tmp_path); w.resize(1380, 860); w.show()
    uhr = QTimer(); uhr.setSingleShot(True); uhr.setInterval(80)
    uhr.timeout.connect(lambda: w.sidebar._zusatz._seiten[-1][0].reject()); uhr.start()
    assert EingabeFenster.getItem(w, "Test", "Frage:", ["a", "b"], 1) == ("", False)
    w.close()


def test_tabelle_eigenschaften_und_bild_zuschneiden_werte(app):
    from lunivo_writer.ui.dialogs.dokument_dialoge import BildZuschneidenDialog, TabellenEigenschaftenDialog
    t = TabellenEigenschaftenDialog(None, 80, 1, 0.5, 3.0, False)
    assert (t.breite.value(), t.ausr.currentIndex(), t.rand.value(), t.pad.value(), t.kopf.isChecked()) == (80, 1, 0.5, 3.0, False)
    b = BildZuschneidenDialog(None)
    b.felder["Oben"].setValue(7); b.felder["Unten"].setValue(2)
    assert b.werte() == (0, 7, 0, 2)
    assert isinstance(b, QDialog)


# ---- Wächter: ausnahmslos jedes Seitenleisten-Fenster nutzt das Raster und steht im Breitentest ------------------------------------------
# Die Liste darf nur kleiner werden (Eigentümer, 2026-11-04: alle Fenster der Seitenleiste in der Rasteransicht, ohne Ausnahme).
WAECHTER_NOCH_ERLAUBT: set[str] = set()


def _alle_panelfaehig_klassen():
    import importlib, inspect, pkgutil
    import lunivo_writer
    out = {}
    for m in pkgutil.walk_packages(lunivo_writer.__path__, "lunivo_writer."):
        if ".werkzeug" in m.name or m.name.endswith("__main__"):
            continue
        try:
            mod = importlib.import_module(m.name)
        except Exception:
            continue
        for n, c in inspect.getmembers(mod, inspect.isclass):
            if c.__module__ == m.name and issubclass(c, PanelFaehig) and c is not PanelFaehig:
                out[f"{c.__module__}.{n}"] = c
    return out


def test_waechter_jedes_seitenleisten_fenster_nutzt_das_raster_und_steht_im_test():
    import inspect, re
    from pathlib import Path
    tests = Path(__file__).parent
    text = "".join((tests / f).read_text(encoding="utf-8") for f in ("test_fenster_seitenleiste_weitere.py", "test_fenster_seitenleiste.py"))
    fehler = []
    for name, c in _alle_panelfaehig_klassen().items():
        kurz = name.rsplit(".", 1)[1]
        if kurz in WAECHTER_NOCH_ERLAUBT:
            continue
        if kurz not in text:
            fehler.append(f"{name}: nicht im Breitentest")
        quelle = inspect.getsource(c)
        for muster, was in ((r"QGridLayout\(", "QGridLayout"), (r"QFormLayout\(", "QFormLayout"), (r"\.setMinimumWidth\((?:[1-9]\d{2,}|[7-9]\d)\)", "feste Mindestbreite (ab 70 px)"),
                            (r"\.setMinimumSize\(\d{3}", "festes Mindestmaß")):
            if re.search(muster, quelle):
                fehler.append(f"{name}: {was}")
    assert not fehler, "\n".join(sorted(fehler))


def _raster(app, breite, spannen):
    from PySide6.QtWidgets import QFrame, QSizePolicy
    from lunivo_writer.ui.baukasten.karten_raster import KartenRaster
    w = QWidget(); r = KartenRaster(w, min_breite=100, abstand=6)
    for k, sp in enumerate(spannen):
        karte = QFrame(); karte.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)         # wie FunktionsZeile: wächst mit der Spanne
        r.addWidget(karte, sp)
    w.resize(breite, 600); w.show(); app.processEvents()
    return w, r, [r.itemAt(k).geometry() for k in range(len(spannen))]


def test_kartenraster_spannen_maßsystem(app):
    """Größe nur aus der Rasterspanne: gleiche Spanne = gleiche Außenmaße, 2x1 = zwei Zellen + Abstand, 2x2 = zwei Zeilen + Abstand, nichts überlagert oder ragt heraus."""
    w, r, g = _raster(app, 320, ["karte", "karte", "breit", "gross", "karte", "karte", "band"])
    n = r.spalten(320); assert n == 3
    zb = (320 - 6 * (n - 1)) // n
    assert g[0].size() == g[1].size() == g[4].size() == g[5].size()
    assert g[2].width() == 2 * zb + 6 and g[2].height() == g[0].height()
    assert g[3].width() == 2 * zb + 6 and g[3].height() == 2 * g[0].height() + 6
    assert g[6].width() == n * zb + (n - 1) * 6 and 0 <= 320 - g[6].width() < n    # 3x1 belegt alle drei Spalten (Rest nur Rundung der ganzzahligen Zellenbreite)
    for a in range(len(g)):
        assert g[a].left() >= 0 and g[a].right() <= 320
        for b in range(a + 1, len(g)):
            assert not g[a].intersects(g[b]), (a, b)


def test_kartenraster_umbruch_bei_schmal_und_spaltenzahl_dynamisch(app):
    """Wird es schmaler, sinkt die Spaltenzahl; eine zu breite Spanne wird auf die vorhandenen Spalten gekürzt (ganze Zeile), nichts ragt hinaus."""
    for breite, spalten in ((120, 1), (230, 2), (330, 3)):
        w, r, g = _raster(app, breite, ["karte", "band", "breit", "karte"])
        assert r.spalten(breite) == spalten
        assert all(0 <= x.left() and x.right() <= breite for x in g), (breite, g)
        assert not any(g[a].intersects(g[b]) for a in range(4) for b in range(a + 1, 4))
    w, r, g = _raster(app, 230, ["band", "karte"])
    assert g[0].width() == 2 * ((230 - 6) // 2) + 6                              # 3x1 passt bei 2 Spalten nicht: auf 2 Spalten gekürzt = ganze Zeile


def test_seitenleiste_breite_springt_nie(app, tmp_path):
    """Die Breite der Seitenleiste hängt nicht vom Inhalt ab: gleich in allen Reitern, im KI-Chat und mit einem geöffneten Fenster."""
    w = _hauptfenster(tmp_path); w.resize(1380, 860); w.show(); app.processEvents()
    breiten = set()
    for n in ("Prüfen", "Lesen", "Schreiben", "KI", "Prüfen"):
        w.sidebar.zeige_reiter(n); app.processEvents(); app.processEvents()
        breiten.add(w.sidebar.width())
    w.sidebar.zeige_bereich(1); app.processEvents(); breiten.add(w.sidebar.width())
    w.sidebar.zeige_bereich(0); app.processEvents()
    gesehen, _uhr = _in_der_seitenleiste_bestaetigen(app, w, lambda d: breiten.add(w.sidebar.width()))
    w.befehle.zitierweise()
    assert len(breiten) == 1, breiten
    w.current_editor().document().setModified(False); w.close()
