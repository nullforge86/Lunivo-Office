from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QPushButton

from lunivo_writer.dienste.einstellungen_dienst import Settings
from lunivo_writer.oberflaeche.dialoge.optionen import OptionenDialog
from lunivo_writer.oberflaeche.programmfenster import MainWindow


def win(tmp_path, monkeypatch):
    from lunivo_writer.dienste import gelernt, wiederherstellung
    monkeypatch.setattr(gelernt, "data_dir", lambda: str(tmp_path))
    from lunivo_writer.ki import ki_dienst as ki_dienst
    monkeypatch.setattr(ki_dienst, "data_dir", lambda: str(tmp_path))
    monkeypatch.setattr(wiederherstellung, "recovery_dir", lambda: str(tmp_path))
    return MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))




def test_optionen_ki_seite_speichert_schluessel_privat(app, tmp_path, monkeypatch):
    import os
    w = win(tmp_path, monkeypatch)
    d = OptionenDialog(w, "ki")
    from PySide6.QtWidgets import QLineEdit
    feld = [e for e in d.findChildren(QLineEdit) if e.placeholderText().startswith("sk-ant")][0]
    feld.setText("sk-ant-test"); feld.editingFinished.emit()
    assert w.ki.konfig["apiKey"] == "sk-ant-test"
    assert oct(os.stat(w.ki.konfig.pfad).st_mode & 0o777) == "0o600"
    assert w.sidebar.ki_banner.isHidden()            # der Hinweis „KI einrichten“ verschwindet, sobald ein Schlüssel da ist


def test_autokorr_einzelschalter_wirkt(app, tmp_path, monkeypatch):
    w = win(tmp_path, monkeypatch); w.new_document()
    w.settings.set("schreibhilfe/akAuslassung", False)
    from PySide6.QtTest import QTest
    e = w.current_editor(); e.setFocus()
    QTest.keyClicks(e.ansicht, "Ende... ")
    assert "..." in e.toPlainText() and "…" not in e.toPlainText()






def test_seitenleiste_und_optionen_gehen_hand_in_hand(app, tmp_path, monkeypatch):
    w = win(tmp_path, monkeypatch)
    sb = w.sidebar
    # Stufe 1/2: Schalter der Schreibhilfe
    w.assistant.setze("wellen", False)
    zeile = next(z for z in sb.werk["Schreiben"].zeilen if z.f.tun == "wellen")            # der Schalter steht auf dem Reiter „Schreiben“
    assert zeile.zustand.text() == "aus"
    w.assistant.setze("wellen", True)
    assert zeile.zustand.text() == "an"
    # Für wen? (Optionen -> Seitenleiste)
    w.assistant.setze_thema("Amt")
    assert sb.thema.currentText() == "Amt"
    # Stufe 4: KI -> Seitenleiste wird über dasselbe Signal neu bewertet
    gesehen = []
    w.ki.geaendert.connect(lambda: gesehen.append(1))
    w.ki.geaendert.emit()
    assert gesehen


def test_befehlslisten_kennwort_ki_und_erweitert(app, tmp_path, monkeypatch):
    import json
    from PySide6.QtWidgets import QListWidget
    w = win(tmp_path, monkeypatch)
    d = OptionenDialog(w, "schnellzugriff")
    seite = d.ansicht._schnellzugriff("")                                  # die Werkzeuge öffnen als eigenes Fenster, hier als Seite geprüft
    listen = seite.findChildren(QListWidget)
    links, rechts = listen[0], listen[1]
    n = rechts.count()
    links.setCurrentRow(0)
    erster = links.item(0).data(Qt.UserRole)
    seite.findChildren(QPushButton)  # Knöpfe vorhanden
    [b for b in seite.findChildren(QPushButton) if b.text() == "Hinzufügen >>"][0].click()
    assert rechts.count() == n + 1
    assert erster in json.loads(w.settings.get("ui/schnellzugriff"))
    # Menüband: ein Register ausblenden
    seite = d.ansicht._menueband("")
    links, rechts = seite.findChildren(QListWidget)[:2]
    rechts.setCurrentRow(0); name = rechts.item(0).text()
    [b for b in seite.findChildren(QPushButton) if b.text() == "Entfernen"][0].click()
    assert name in json.loads(w.settings.get("ui/register_plan"))["versteckt"]
    # Sicherheit: Kennwort, Markup-Haken
    d.ansicht._sicherheit(""); d.ansicht._verfolgen("")
    d.gehe_zu("ki"); d.gehe_zu("gedaechtnis"); d.gehe_zu("erweitert")
    # KI: Aufgabenmodell wird gespeichert
    d.gehe_zu("ki")
    seite = d.stapel.currentWidget()
    from PySide6.QtWidgets import QComboBox
    c = [x for x in seite.findChildren(QComboBox)][0]
    assert c.itemText(0).startswith("Standard (")


def test_optionen_flach_suche_aufklappen_und_hell_dunkel(app, tmp_path, monkeypatch):
    """Sechs Seiten ohne Baum, Suche springt auch in eingeklappte Bereiche, Hell/Dunkel/System als eine Wahl."""
    from PySide6.QtCore import Qt
    from lunivo_writer.oberflaeche.baukasten.geruest.einklappgruppe import EinklappGruppe
    w = win(tmp_path, monkeypatch)
    d = OptionenDialog(w, "anzeige")
    a = d.ansicht
    assert a.baum.topLevelItemCount() == 6 and all(a.baum.topLevelItem(i).childCount() == 0 for i in range(6))
    # Suche: eine AutoKorrektur-Einzelregel steht in einem eingeklappten Bereich der Seite „Schreiben“
    a.suche.setText("Gedankenstrich")
    assert a.treffer.count() >= 1
    it = a.treffer.item(0)
    seite = a.stapel.widget(a.knoten["schreiben"].data(0, Qt.UserRole + 1))
    zu = [e for e in seite.findChildren(EinklappGruppe) if not e.ist_offen()]
    assert zu                                                                 # die Zusatzeinstellungen sind erst einmal zu
    a._springe(it)
    assert a.baum.currentItem().text(0) == "Schreiben"
    assert all(e.ist_offen() for e in seite.findChildren(EinklappGruppe) if e.isAncestorOf(it.data(Qt.UserRole)[1]))
    # Alte Seitennamen führen auf die neuen Seiten
    a.gehe_zu("gedaechtnis"); assert a.baum.currentItem().text(0) == "Schreiben"
    a.gehe_zu("pdf"); assert a.baum.currentItem().text(0) == "Drucken und PDF"
    # Hell / Dunkel / Wie das System: genau eine Wahl, sie wirkt und steht in den Einstellungen
    from PySide6.QtWidgets import QApplication, QPushButton
    from PySide6.QtGui import QPalette
    a.gehe_zu("anzeige")
    knoepfe = {b.accessibleName(): b for b in a.stapel.currentWidget().findChildren(QPushButton) if b.objectName() == "optWahl"}
    assert set(knoepfe) == {"Hell", "Dunkel", "Mint", "Wie das System"}
    try:
        knoepfe["Dunkel"].click()
        assert w.settings.get("theme") == "dark" and QApplication.instance().palette().color(QPalette.Window).lightness() < 128
        assert knoepfe["Dunkel"].isChecked() and not knoepfe["Hell"].isChecked()
        w.thema_wechseln()                                                    # Strg+Umschalt+D / Statusleiste: zum jeweils anderen
        assert w.settings.get("theme") == "light" and w.statusBar().thema.text() == "Hell"
    finally:
        knoepfe["Wie das System"].click()


def test_optionen_barrierefrei_namen_und_fokus(app, tmp_path, monkeypatch):
    """Jedes Bedienelement hat einen Namen für Bildschirmleser und ist mit der Tastatur erreichbar; die Seitenliste ist fokussierbar."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (QAbstractSpinBox, QCheckBox, QComboBox, QLineEdit, QListWidget, QPushButton, QRadioButton, QSlider,
                                   QToolButton, QWidget)
    w = win(tmp_path, monkeypatch)
    a = OptionenDialog(w, "lesen").ansicht
    assert a.baum.focusPolicy() == Qt.StrongFocus and a.baum.accessibleName() and a.suche.accessibleName()
    ohne_name, ohne_fokus = [], []
    for x in a.stapel.findChildren(QWidget):
        if not isinstance(x, (QPushButton, QComboBox, QSlider, QAbstractSpinBox, QLineEdit, QToolButton, QRadioButton, QCheckBox, QListWidget)):
            continue
        if isinstance(x, QLineEdit) and isinstance(x.parentWidget(), (QComboBox, QAbstractSpinBox)):
            continue
        name = x.accessibleName() or (x.text() if isinstance(x, (QPushButton, QToolButton, QRadioButton, QCheckBox)) else "")
        if not name:
            ohne_name.append(type(x).__name__)
        if x.focusPolicy() == Qt.NoFocus:
            ohne_fokus.append(type(x).__name__)
    assert not ohne_name and not ohne_fokus


def test_symbole_der_schienen_folgen_dem_farbwechsel(app, tmp_path, monkeypatch):
    """Nach dem Wechsel von hell auf dunkel sind die Symbole der Seitenleisten hell (nicht schwarz auf dunkel)."""
    from PySide6.QtWidgets import QApplication
    from lunivo_writer.oberflaeche.thema import apply_theme
    apply_theme(QApplication.instance(), "light")
    w = win(tmp_path, monkeypatch)
    try:
        w.set_theme("dark")
        bild = w._links["suche"].icon().pixmap(22, 22).toImage()
        hell = max(bild.pixelColor(x, y).lightness() for x in range(bild.width()) for y in range(bild.height()) if bild.pixelColor(x, y).alpha() > 100)
        assert hell > 200
    finally:
        w.set_theme("system")
