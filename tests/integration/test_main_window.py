import os
import subprocess
import sys
import textwrap

import docx
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtTest import QTest

from lunivo_writer.services.settings_service import Settings
from lunivo_writer.ui.main_window import MainWindow


FENSTER = "lunivo_writer.ui.hauptfenster.dateien_speichern.speicherort_waehlen"


def win(tmp_path):
    return MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))


def _schliesse(w):
    """Schließt ein Testfenster ohne Rückfrage wegen absichtlich geänderter Testdokumente."""
    if w is None:
        return
    for index in reversed(range(w.tabs.count())):
        tab = w.tabs.widget(index)
        editor = getattr(tab, "editor", None)
        if editor is not None:
            editor.document().setModified(False)
        w.close_tab(index)
    w.close()


def test_new_edit_save_reopen(app, tmp_path, monkeypatch):
    w = win(tmp_path)
    w.new_document()
    e = w.current_editor()
    e.insertPlainText("Erster Absatz\nZweiter Absatz")
    c = e.textCursor()
    c.select(QTextCursor.Document)
    e.setTextCursor(c)
    w.befehle.fett()
    assert e.document().isModified() and w.current_tab().is_modified()
    assert e.textCursor().charFormat().fontWeight() >= 600

    target = str(tmp_path / "doc.docx")
    monkeypatch.setattr(FENSTER, lambda *a, **k: (target, ".docx"))
    assert w.save()
    assert not e.document().isModified()
    assert docx.Document(target).paragraphs[0].runs[0].bold

    w2 = win(tmp_path)
    assert w2.open_path(target)
    assert w2.current_editor().toPlainText() == "Erster Absatz\nZweiter Absatz"
    assert target in w2.settings.recent()
    _schliesse(w2)
    _schliesse(w)


def test_pdf_export_and_status(app, tmp_path, monkeypatch):
    w = win(tmp_path)
    w.new_document()
    w.current_editor().insertPlainText("\n".join(f"Z{i}" for i in range(150)))
    w.current_editor()._recount()
    w._sync_status()
    assert " von 3" in w.lbl_page.text() or " von 2" in w.lbl_page.text()

    out = str(tmp_path / "x.pdf")
    ansicht = w.pdf_export_widget()
    ansicht.pfad.setText(out)
    ansicht.ok.click()
    assert os.path.getsize(out) > 500
    _schliesse(w)


def test_close_asks_when_modified(app, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox

    w = win(tmp_path)
    w.new_document()
    w.current_editor().insertPlainText("x")
    monkeypatch.setattr(QMessageBox, "exec", lambda self: QMessageBox.Cancel)
    assert w.close_tab(0) is False and w.tabs.count() == 1

    monkeypatch.setattr(QMessageBox, "exec", lambda self: QMessageBox.Discard)
    assert w.close_tab(0) is True and w.tabs.count() == 0
    _schliesse(w)


def test_invalid_file_is_reported_not_crashing(app, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox

    shown = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: shown.append(a))
    bad = tmp_path / "kaputt.docx"
    bad.write_bytes(b"nope")
    w = win(tmp_path)
    assert w.open_path(str(bad)) is False and shown and w.tabs.count() == 0
    _schliesse(w)


def test_autosave_and_recovery(app, tmp_path, monkeypatch):
    from lunivo_writer.services import recovery
    from lunivo_writer.services import file_service as formats

    def recovery_dir():
        pfad = tmp_path / "rec"
        pfad.mkdir(exist_ok=True)
        return str(pfad)

    monkeypatch.setattr(recovery, "recovery_dir", recovery_dir)
    w = win(tmp_path)
    w.new_document()
    w.current_editor().insertPlainText("Rettungstext")
    w.autosave_now()

    ent = recovery.pending()
    assert len(ent) == 1
    assert "Rettungstext" in formats.load(ent[0].docx_path).doc.toPlainText()

    w.current_editor().document().setModified(False)
    w.close_tab(0)
    assert recovery.pending() == []
    _schliesse(w)


def test_no_web_modules_loaded(app):
    """Frischer Prozess: der neue Startpfad lädt weder WebEngine noch WebKit noch einen Webserver."""
    wurzel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    code = textwrap.dedent(
        """
        import os, sys
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        from PySide6.QtWidgets import QApplication
        app = QApplication([])
        import lunivo_writer.app
        from lunivo_writer.ui.main_window import MainWindow
        w = MainWindow()
        w.new_document()
        bad = [m for m in sys.modules if m.startswith((
            "PySide6.QtWebEngine", "PySide6.QtWebKit", "PySide6.QtWebChannel",
            "PySide6.QtWebView", "http.server", "socketserver", "flask",
            "gi.repository.WebKit"
        ))]
        print("BAD", bad)
        sys.exit(1 if bad else 0)
        """
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (os.path.join(wurzel, "src"), env.get("PYTHONPATH", "")) if part
    )
    env["QT_QPA_PLATFORM"] = "offscreen"
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=wurzel,
        env=env,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "BAD []" in result.stdout, result.stdout + result.stderr


def test_quelltext_ohne_web_oberflaeche():
    """Im neuen Programm kommt keine HTML/JS-Oberfläche vor."""
    import pathlib
    import re

    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "lunivo_writer"
    muster = re.compile(
        r"QtWebEngine|QtWebKit|QWebEngineView|WebKit2|http\.server|SimpleHTTPRequestHandler"
    )
    treffer = [
        str(p)
        for p in wurzel.rglob("*.py")
        if muster.search(p.read_text(encoding="utf-8", errors="replace"))
    ]
    assert treffer == []
    assert not list(wurzel.rglob("*.html")) and not list(wurzel.rglob("*.js"))


# Das Einfügen aus der Zwischenablage nimmt Inhalte aus fremden Programmen an. Das ist
# keine von Lunivo erzeugte Datei und kein eigenes Speicherformat. Die einzige weitere
# Ausnahme ordnet fremden HTML-Dateien lediglich ein Dateisymbol zu.
HTML_NOCH_ERLAUBT = {
    "ui/document/bearbeitung/base.py",
    "ui/document/bearbeitung/editor_einfuegen.py",
    "ui/baukasten/medien/datei_symbole.py",
}


def test_kein_html_im_projekt():
    """Lunivo ist eine native Qt-Anwendung: HTML, JavaScript und CSS kommen weder als Dateien noch im Quelltext vor."""
    import pathlib
    import re

    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent
    ohne = {
        ".venv",
        ".git",
        ".claude",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "node_modules",
        "htmlcov",
        "build",
        "dist",
    }
    projektdateien = [
        p
        for p in wurzel.rglob("*")
        if p.is_file() and not (ohne & set(p.relative_to(wurzel).parts))
    ]
    web = [
        str(p.relative_to(wurzel))
        for p in projektdateien
        if p.suffix.lower() in {".html", ".htm", ".js", ".mjs", ".css", ".ts"}
    ]
    assert web == [], "Web-Dateien im Projekt: " + ", ".join(web)

    code = re.compile(
        r"toHtml|setHtml|insertHtml|fromHtml|hasHtml|\.html\(\)|import html\b|<html|<body|<img |<table|<br>|"
        r"</?(?:b|i|s|u|br|p|h[1-6]|code|sup|sub|a|span|div|table|tr|td|ul|li|font|em|strong)(?:\s[^>]*)?/?>|"
        r"[\"']\.html?[\"']|\"html\"|QtWebEngine|QtWebKit|QWebEngine|WebKit2|http\.server|SimpleHTTPRequestHandler"
    )
    treffer = []
    for p in projektdateien:
        rel = p.relative_to(wurzel).as_posix()
        if p.suffix.lower() not in {".py", ".json", ".sh", ".toml"}:
            continue
        if rel.startswith(("tests/", "src/lunivo_writer/resources/daten/")):
            continue
        if rel.removeprefix("src/lunivo_writer/") in HTML_NOCH_ERLAUBT:
            continue
        if rel == "werkzeug/pruefen/funktionspruefung.py":
            continue
        for nummer, zeile in enumerate(
            p.read_text(encoding="utf-8", errors="replace").splitlines(), 1
        ):
            if code.search(zeile):
                treffer.append(f"{rel}:{nummer}: {zeile.strip()[:90]}")
    assert treffer == [], "HTML im Quelltext:\n" + "\n".join(treffer)


COMBO_NOCH_ERLAUBT: set[str] = set()


def test_kein_combobox_ausser_auswahlfeld():
    """Dropdowns kommen aus ui/baukasten/dropdown/auswahlfeld.py."""
    import pathlib
    import re

    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "lunivo_writer"
    muster = re.compile(r"\bQComboBox\s*\(|\bQFontComboBox\s*\(")
    treffer = {
        p.relative_to(wurzel).as_posix()
        for p in wurzel.rglob("*.py")
        if muster.search(p.read_text(encoding="utf-8", errors="replace"))
    }
    treffer.discard("ui/baukasten/dropdown/auswahlfeld.py")
    assert treffer <= COMBO_NOCH_ERLAUBT, (
        "QComboBox( außerhalb von auswahlfeld.py: "
        + ", ".join(sorted(treffer - COMBO_NOCH_ERLAUBT))
    )


REITER_NOCH_ERLAUBT: set[str] = set()


def test_kein_rohe_reiterleiste():
    """Rohe Reiterleisten sind nur in flache_reiter_leiste.py/formular_gitter.py erlaubt."""
    import pathlib
    import re

    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "lunivo_writer"
    muster = re.compile(r"\bQTabBar\s*\(|\bQTabWidget\s*\(|setUsesScrollButtons\(\s*True")
    treffer = {
        p.relative_to(wurzel).as_posix()
        for p in wurzel.rglob("*.py")
        if muster.search(p.read_text(encoding="utf-8", errors="replace"))
    }
    treffer -= {
        "ui/baukasten/controls/flache_reiter_leiste.py",
        "ui/baukasten/controls/formular_gitter.py",
    }
    assert treffer <= REITER_NOCH_ERLAUBT, (
        "rohe Reiterleiste außerhalb des Bausteins: "
        + ", ".join(sorted(treffer - REITER_NOCH_ERLAUBT))
    )


def test_dropdown_groesse_nur_im_paket_dropdown():
    """Feldlänge, Größenregel und Zeilenzahl eines Dropdowns setzt nur das Paket dropdown."""
    import pathlib
    import re

    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "lunivo_writer"
    muster = re.compile(r"\.(setSizeAdjustPolicy|setMinimumContentsLength|setMaxVisibleItems)\(")
    treffer = sorted(
        p.relative_to(wurzel).as_posix()
        for p in wurzel.rglob("*.py")
        if "ui/baukasten/dropdown/" not in p.as_posix()
        and muster.search(p.read_text(encoding="utf-8", errors="replace"))
    )
    assert treffer == [], "Dropdown-Größe außerhalb des Pakets dropdown: " + ", ".join(treffer)


def test_menue_an_knopf_nur_ueber_dropdown_knopf():
    """setMenu/setPopupMode ruft nur das Paket dropdown auf."""
    import pathlib
    import re

    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "lunivo_writer"
    muster = re.compile(r"\.(setMenu|setPopupMode)\(")
    treffer = sorted(
        p.relative_to(wurzel).as_posix()
        for p in wurzel.rglob("*.py")
        if "ui/baukasten/dropdown/" not in p.as_posix()
        and muster.search(p.read_text(encoding="utf-8", errors="replace"))
    )
    assert treffer == [], "setMenu/setPopupMode außerhalb des Pakets dropdown: " + ", ".join(treffer)


def test_dropdown_farben_nur_im_thema():
    """Kein Stylesheet außerhalb von ui/theme.py färbt QMenu, QComboBox oder deren Listen."""
    import pathlib
    import re

    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "lunivo_writer"
    muster = re.compile(r"(QMenu|QComboBox)[^{\n]*\{[^}\n]*(background|color|border)")
    treffer = sorted(
        p.relative_to(wurzel).as_posix()
        for p in wurzel.rglob("*.py")
        if p.name != "theme.py"
        and muster.search(p.read_text(encoding="utf-8", errors="replace"))
    )
    assert treffer == [], "Dropdown-Farben außerhalb des Themas: " + ", ".join(treffer)


def test_popup_besitz_nur_ueber_den_baustein():
    """setParent(..., Qt.Popup) für Menüs gibt es nur im Paket dropdown."""
    import ast
    import pathlib

    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "lunivo_writer"
    treffer = []
    for p in wurzel.rglob("*.py"):
        if "ui/baukasten/dropdown/" in p.as_posix():
            continue
        baum = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        for knoten in ast.walk(baum):
            if not isinstance(knoten, ast.Call):
                continue
            if not isinstance(knoten.func, ast.Attribute) or knoten.func.attr != "setParent":
                continue
            if any("Popup" in ast.unparse(argument) for argument in knoten.args):
                treffer.append(f"{p.relative_to(wurzel).as_posix()}:{knoten.lineno}")
    assert treffer == [], "Popup-Besitz von Hand: " + ", ".join(treffer)


def test_keine_eigene_dropdown_klasse_ausserhalb_des_pakets():
    """Dropdown-Klassen werden über Auswahlfeld/Schriftauswahl/MenueListe abgeleitet."""
    import ast
    import pathlib

    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "lunivo_writer"
    unerlaubt = {"QComboBox", "QFontComboBox", "QMenu"}
    treffer = []
    for p in wurzel.rglob("*.py"):
        if "ui/baukasten/dropdown/" in p.as_posix():
            continue
        baum = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        for knoten in ast.walk(baum):
            if not isinstance(knoten, ast.ClassDef):
                continue
            basisklassen = {
                basis.id if isinstance(basis, ast.Name)
                else basis.attr if isinstance(basis, ast.Attribute)
                else ""
                for basis in knoten.bases
            }
            if basisklassen & unerlaubt:
                treffer.append(f"{p.relative_to(wurzel).as_posix()}:{knoten.lineno}")
    assert treffer == [], "eigene Dropdown-Klasse an der Baukasten-Basis vorbei: " + ", ".join(treffer)


def test_kein_menue_wird_aus_text_erzeugt():
    """addMenu("Titel") erzeugt kein rohes QMenu außerhalb von MenueListe."""
    import ast
    import pathlib

    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "lunivo_writer"
    treffer = []
    for p in wurzel.rglob("*.py"):
        if "ui/baukasten/dropdown/" in p.as_posix():
            continue
        baum = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        for knoten in ast.walk(baum):
            if not isinstance(knoten, ast.Call):
                continue
            if not isinstance(knoten.func, ast.Attribute) or knoten.func.attr != "addMenu":
                continue
            if knoten.args and isinstance(knoten.args[0], (ast.Constant, ast.JoinedStr)):
                treffer.append(f"{p.relative_to(wurzel).as_posix()}:{knoten.lineno}")
    assert treffer == [], "rohes QMenu über addMenu(Text): " + ", ".join(treffer)


def test_dropdown_hoehe_nur_im_baustein():
    """Die Höhe von Auswahlfeld/Schriftauswahl/DropdownTaste wird im Baustein festgelegt."""
    import ast
    import pathlib

    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "lunivo_writer"
    dropdown_typen = {"Auswahlfeld", "Schriftauswahl", "DropdownTaste"}
    setter = {"setMinimumHeight", "setFixedHeight"}
    treffer = []
    for p in wurzel.rglob("*.py"):
        if "ui/baukasten/dropdown/" in p.as_posix():
            continue
        baum = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        for knoten in ast.walk(baum):
            if not isinstance(knoten, ast.Call) or not isinstance(knoten.func, ast.Attribute):
                continue
            if knoten.func.attr not in setter:
                continue
            empfaenger = knoten.func.value
            if isinstance(empfaenger, ast.Call) and isinstance(empfaenger.func, ast.Name):
                if empfaenger.func.id in dropdown_typen:
                    treffer.append(f"{p.relative_to(wurzel).as_posix()}:{knoten.lineno}")
    assert treffer == [], "Dropdown-Höhe außerhalb des Bausteins: " + ", ".join(treffer)


def test_tastenkuerzel_fett(app, tmp_path):
    w = win(tmp_path)
    w.new_document()
    w.show()
    e = w.current_editor()
    e.setPlainText("abc")
    e.selectAll()
    e.setFocus()
    app.processEvents()

    assert w.a_bold.shortcut().toString() == "Ctrl+B"
    QTest.keyClick(e, Qt.Key_B, Qt.ControlModifier)
    app.processEvents()
    assert e.textCursor().charFormat().fontWeight() >= 600

    QTest.keyClick(e, Qt.Key_B, Qt.ControlModifier)
    app.processEvents()
    assert e.textCursor().charFormat().fontWeight() < 600
    _schliesse(w)


def test_bearbeitung_sperren_und_band_einklappen(app, tmp_path):
    w = win(tmp_path)
    w.new_document()
    w.befehle.bearbeitungSperren()
    assert w.current_editor().isReadOnly()
    w.befehle.bearbeitungSperren()
    assert not w.current_editor().isReadOnly()

    band = w.band
    band.einklappen_umschalten()
    assert band._eingeklappt and not band.stapel.isVisibleTo(band)
    band.einklappen_umschalten()
    assert band.stapel.isVisibleTo(band)
    _schliesse(w)


def test_zoom_skaliert_ansicht_nicht_dokument(app, tmp_path):
    w = win(tmp_path)
    w.new_document()
    w.resize(1200, 800)
    w.show()
    e = w.current_editor()
    e.insertPlainText("Hallo Welt " * 30)
    breite, hoehe = e.width(), e.document().size().height()
    schrift = e.document().defaultFont().pointSizeF()

    e.set_zoom(2.0)
    assert abs(e.width() - 2 * breite) <= 2
    assert e.document().size().height() > 1.8 * hoehe
    assert e.document().defaultFont().pointSizeF() == schrift
    assert w.lbl_zoom.text() == "200 %" and w.zoom_regler.value() == 200

    w.befehle.normal()
    assert e.zoom == 1.0 and e.width() == breite
    w.befehle.zoomBreite()
    tab = w.current_tab()
    assert abs(e.width() - (tab.viewport().width() - 24)) <= 4
    w.befehle.zoomSeite()
    assert 0 < e.zoom <= 1.5 and e.width() <= tab.viewport().width()
    _schliesse(w)


def test_lineale_zeigen_und_raender_ziehen(app, tmp_path):
    w = win(tmp_path)
    w.new_document()
    w.show()
    tab = w.current_tab()
    assert not tab.lineal_h.isVisibleTo(tab)

    w.befehle.linealZeigen()
    w.befehle.linealHochZeigen()
    assert tab.lineal_h.isVisibleTo(tab.widget()) and tab.lineal_v.isVisibleTo(tab.widget())
    assert w.befehle.an_linealZeigen() and w.befehle.an_linealHochZeigen()
    assert tab.lineal_h.width() == tab.viewport().width()
    assert tab.lineal_v.height() == tab.viewport().height()
    assert tab.lineal_h.geometry().bottom() < tab.viewport().geometry().top()

    tab.lineal_h.randGeaendert.emit("links", 20.0)
    tab.lineal_v.randGeaendert.emit("oben", 15.0)
    assert tab.page.margin_left_mm == 20.0 and tab.page.margin_top_mm == 15.0
    assert tab.editor.document().isModified()

    tab.editor.insertPlainText("Absatz")
    tab.lineal_h.einzugGeaendert.emit(10.0, 5.0, 8.0)
    bf = tab.editor.textCursor().blockFormat()
    assert abs(bf.leftMargin() / 3.7795 - 10) < 0.2
    assert abs(bf.textIndent() / 3.7795 - 8) < 0.2

    x_vorher = tab.lineal_h._marken()["links"]
    tab.editor.set_zoom(2.0)
    assert tab.lineal_h.width() == tab.viewport().width()
    assert tab.lineal_h._marken()["links"] > x_vorher
    _schliesse(w)


def test_ansichten_web_zwei_seiten_gliederung(app, tmp_path):
    w = win(tmp_path)
    w.new_document()
    w.resize(1200, 800)
    w.show()
    tab = w.current_tab()
    e = tab.editor
    e.insertPlainText("Kapitel\nText A\nText B")
    cursor = QTextCursor(e.document())
    e.setTextCursor(cursor)
    e.apply_style("Überschrift 1")

    w.befehle.w_setzeLayout(None, "web")
    assert e.web and e.width() <= tab.viewport().width()

    w.befehle.w_setzeLayout(None, "doppelt")
    assert tab.widget() is not tab._holder and tab.widget().seiten >= 1

    w.befehle.w_setzeLayout(None, "blatt")
    assert tab.widget() is tab._holder and not e.web
    assert abs(e.width() - e.page.width_mm * 96 / 25.4) <= 2

    w.befehle.gliederung()
    bloecke = [b.isVisible() for b in _bloecke(e.document())]
    assert bloecke == [True, False, False]
    e.set_gliederung(False)
    assert all(b.isVisible() for b in _bloecke(e.document()))
    _schliesse(w)


def _bloecke(doc):
    block = doc.firstBlock()
    while block.isValid():
        yield block
        block = block.next()


def test_neues_fenster_und_anordnen(app, tmp_path):
    vorher = {id(f) for f in MainWindow.alle_fenster()}
    w = win(tmp_path)
    w.new_document()
    w.current_editor().insertPlainText("Inhalt")
    ziel = str(tmp_path / "f.docx")
    w.show()
    assert w._write(w.current_tab(), ziel)
    w.current_tab().set_path(ziel)

    w2 = w.neues_fenster()
    assert w2 is not None and w2.current_tab().editor.toPlainText() == "Inhalt"
    fenster = MainWindow.alle_fenster()
    assert w in fenster and w2 in fenster
    assert {id(f) for f in fenster if id(f) not in vorher} >= {id(w), id(w2)}

    w.fenster_anordnen("nebeneinander")
    assert abs(w.width() - w2.width()) <= 10
    menue = w.fensterliste_menue()
    titel = [aktion.text() for aktion in menue.actions()]
    assert any("f.docx" in text for text in titel)

    _schliesse(w2)
    _schliesse(w)


def test_absatzdialog_und_objekte_waehlen(app, tmp_path):
    from lunivo_writer.ui.baukasten.formatierung.absatz_dialog import AbsatzDialog

    dialog = AbsatzDialog(
        None,
        {
            "ausr": "mitte",
            "einzug": 5,
            "erste": -8,
            "vor": 6,
            "nach": 12,
            "zeilen": 1.5,
            "umbruch": True,
            "tabs": [(30.0, "rechts")],
        },
    )
    assert dialog.ausr.currentData() == "mitte"
    assert dialog.umbruch.isChecked() and dialog.sonder.currentData() == "haengend"
    dialog.links.setValue(12)
    dialog.sonder.setCurrentIndex(1)
    dialog.zeilen_art.setCurrentIndex(2)

    genau = AbsatzDialog(None, {"zeilen_art": "genau", "zeilen_pt": 14})
    assert genau.werte()["zeilen_art"] == "genau" and genau.werte()["zeilen_pt"] == 14
    werte = dialog.werte()
    assert abs(werte["einzug"] - 12) < 1e-6
    assert abs(werte["erste"] - 8) < 1e-6
    assert werte["zeilen"] == 2.0 and werte["tabs"] == [(30.0, "rechts")]

    vorlage = AbsatzDialog(None, {"vor": 3}, umfang="vorlage")
    assert vorlage.reiter.count() == 2 and abs(vorlage.werte()["vor"] - 3) < 1e-6

    w = win(tmp_path)
    w.new_document()
    e = w.current_editor()
    e.insertPlainText("vorher ")
    from PySide6.QtGui import QImage, QTextImageFormat

    img = QImage(20, 20, QImage.Format_RGB32)
    img.fill(0xFF0000)
    e.document().addResource(3, "bild1", img)
    bildformat = QTextImageFormat()
    bildformat.setName("bild1")
    bildformat.setWidth(20)
    bildformat.setHeight(20)
    e.textCursor().insertImage(bildformat)
    e.insertPlainText(" nachher")
    cursor = e.textCursor()
    cursor.setPosition(0)
    e.setTextCursor(cursor)
    w.befehle.objekteWaehlen()
    assert e.textCursor().selectedText() == "￼"
    _schliesse(w)


def test_kommentar_note_verfolgen_ueber_befehle(app, tmp_path, monkeypatch):
    from lunivo_writer.ui.baukasten.dokument.eingabe_fenster import EingabeFenster

    w = win(tmp_path)
    w.new_document()
    w.show()
    e = w.current_editor()
    e.insertPlainText("Ein Satz zum Prüfen.")
    monkeypatch.setattr(
        EingabeFenster,
        "getMultiLineText",
        staticmethod(lambda *a, **k: ("Mein Text", True)),
    )

    e.select_range(0, 3)
    w.befehle.kommentar()
    assert w.navigation.isVisible() and not w.navigation.neu_feld.isHidden()
    w.navigation.neu_text.setPlainText("Mein Text")
    w.navigation.neu_ok.click()
    assert len(e.kommentare) == 1 and w.navigation.anzahl("kommentare") == 1

    cursor = e.textCursor()
    cursor.setPosition(e.document().characterCount() - 1)
    e.setTextCursor(cursor)
    w.befehle.fussnote()
    w.noten_feld.eingabe.setPlainText("Mein Text")
    w.navigation.aktualisieren()
    assert len(e.noten["f"]) == 1 and w.navigation.anzahl("noten") == 1

    assert not w.befehle.an_verfolgen()
    w.befehle.verfolgen()
    assert w.befehle.an_verfolgen()
    ziel = str(tmp_path / "k.docx")
    assert w._write(w.current_tab(), ziel)
    w.current_tab().editor.document().setModified(False)

    zweites_verzeichnis = tmp_path / "x"
    zweites_verzeichnis.mkdir()
    w2 = win(zweites_verzeichnis)
    assert w2.open_path(ziel)
    e2 = w2.current_editor()
    assert list(e2.kommentare.values())[0]["text"] == "Mein Text"
    assert list(e2.noten["f"].values())[0] == "Mein Text"
    _schliesse(w2)
    _schliesse(w)


def test_oberflaeche_wechseln_register_anpassen_symbole_tauschen(app, tmp_path):
    import json

    from lunivo_writer.ui.widgets import icons
    from lunivo_writer.ui.ribbon.toolbars import Symbolleisten
    from lunivo_writer.ui.ribbon.ribbon_bar import RegisterBand

    w = win(tmp_path)
    w.new_document()
    w.resize(1380, 860)
    w.show()
    assert isinstance(w.band, RegisterBand)
    assert [w.band.reiter.tabText(i) for i in range(8)][:3] == ["Datei", "Start", "Einfügen"]

    w.settings.set(
        "ui/register_plan",
        json.dumps({"reihenfolge": ["Datei", "Ansicht", "Start"], "versteckt": ["Verweise", "KI"]}),
    )
    w.neu_bauen_band()
    namen = [
        w.band.reiter.tabText(i)
        for i in range(w.band.reiter.count())
        if w.band.reiter.isTabVisible(i)
    ]
    assert namen[:2] == ["Ansicht", "Start"]
    assert "Datei" not in namen and "Verweise" not in namen and "KI" not in namen
    assert w.band.reiter.tabText(w.band.reiter.currentIndex()) == "Start"

    w.settings.set("ui/schnellzugriff", json.dumps(["speichern", "neu"]))
    w.neu_bauen_band()
    assert w.band.schnell.count() == 2

    w.oberflaeche_aendern("symbolleisten", True)
    assert isinstance(w.band, Symbolleisten) and w.menuBar().isVisible()
    assert w.sidebar.isVisible() and w.band.felder["font"] is not None
    w.befehle.fett()
    w.current_editor().insertPlainText("x")
    w.band.aktualisieren(True)
    w.oberflaeche_aendern("register", False)

    name = next(iter(icons.pfade_original()))
    try:
        icons.uebersteuern({name: "heart"})
        assert icons.pfade()[name] == icons.katalog()["heart"]
        assert icons.pfade_original()[name] != icons.katalog()["heart"]
    finally:
        icons.uebersteuern({})
    assert icons.pfade()[name] == icons.pfade_original()[name]
    _schliesse(w)


def test_symbolleisten_bauen_kein_verstecktes_register(app, tmp_path, monkeypatch):
    from lunivo_writer.ui.ribbon.ribbon_bar import RegisterBand
    from lunivo_writer.ui.ribbon.toolbars import Symbolleisten

    w = win(tmp_path)
    w.new_document()

    def register_nicht_bauen(*args, **kwargs):
        raise AssertionError("Symbolleisten dürfen kein Registerband erzeugen")

    with monkeypatch.context() as patch:
        patch.setattr(RegisterBand, "__init__", register_nicht_bauen)
        w.oberflaeche_aendern("symbolleisten", False)

    assert isinstance(w.band, Symbolleisten)
    assert w.band.daten["register"]
    assert not hasattr(w.band, "_reg")
    w.band.aktualisieren(True)
    _schliesse(w)


def test_linke_seitenleiste_suchen_kommentare_ueberschriften(app, tmp_path, monkeypatch):
    """Suchen/Ersetzen, Kommentare und Überschriften in der linken Seitenleiste."""
    w = win(tmp_path)
    w.new_document()
    w.show()
    e = w.current_editor()
    e.setPlainText("Kapitel Eins\nText hier und mehr Text zum Suchen.\nKapitel Zwei\nNoch Text.")
    for nummer in (0, 2):
        cursor = QTextCursor(e.document().findBlockByNumber(nummer))
        blockformat = cursor.blockFormat()
        blockformat.setHeadingLevel(1)
        cursor.setBlockFormat(blockformat)

    assert not w.navigation.isVisible()
    w._links_klick("kommentare")
    assert (
        w.navigation.isVisible()
        and w.navigation.aktuelle_seite == "kommentare"
        and w._links["kommentare"].isChecked()
    )
    w._links_klick("kommentare")
    assert not w.navigation.isVisible() and not w._links["kommentare"].isChecked()

    nav = w.navigation
    nav.suche_zeigen("Text")
    assert nav.aktuelle_seite == "suche"
    assert "3" in nav.treffer.text()
    assert len(e._such_bereiche) == 3
    nav.ersatzfeld.setText("Wort")
    nav._ersetzen_alle()
    assert "Text" not in e.toPlainText() and e.toPlainText().count("Wort") == 3
    nav.suchfeld.setText("gibtesnicht")
    assert nav.treffer.text() == "Keine Suchergebnisse" and not e._such_bereiche
    nav.suchfeld.setText("Wort")
    assert len(e._such_bereiche) == 3
    nav.hide()
    assert not e._such_bereiche
    nav.show()

    e.select_range(0, 7)
    e.kommentar_neu("Erster")
    e.select_range(13, 17)
    e.kommentar_neu("Zweiter")
    nav.zeige_tab("kommentare")
    assert nav.anzahl("kommentare") == 2

    def kommentartexte():
        return [e.kommentare[karte.kid]["text"] for karte in nav._karten]

    nav._sortieren("oben")
    assert kommentartexte() == ["Erster", "Zweiter"]
    nav._sortieren("unten")
    assert kommentartexte() == ["Zweiter", "Erster"]
    kid = int(nav._karten[0].kid)
    e.kommentar_geloest(kid, True)
    nav.aktualisieren()
    nav._anzeigen("offen")
    assert nav.anzahl("kommentare") == 1
    nav._anzeigen("geloest")
    assert nav.anzahl("kommentare") == 1
    nav._anzeigen("alle")
    assert nav.anzahl("kommentare") == 2

    nav.zeige_tab("ueberschriften")
    assert nav.baum.topLevelItemCount() == 2
    nav.baum.collapseAll()
    nav._ebene(2)
    nav._schrift("gross")
    assert nav.baum.font().pointSizeF() == 13.0
    nav._umbrechen(False)
    assert not nav.baum.wordWrap()
    _schliesse(w)


def test_kommentar_nachbearbeiten_und_schriftgroesse(app, tmp_path):
    """Kommentartext und Schriftgröße werden in Karte und Sprechblase aktualisiert."""
    from lunivo_writer.editor.objekte import sprechblasen as SB

    w = win(tmp_path)
    w.new_document()
    w.show()
    e = w.current_editor()
    e.setPlainText("Bewerbung als Änderungsschneider,")
    e.select_range(14, 32)
    kid = e.kommentar_neu("alter Text")
    nav = w.navigation
    nav.zeige_tab("kommentare")
    nav.show()
    assert nav.anzahl("kommentare") == 1

    e.kommentar_bearbeiten(kid)
    assert nav._bearbeite == kid and hasattr(nav._karten[0], "eingabe")
    nav._karten[0].eingabe.setPlainText("neuer Text")
    nav._bearbeiten_speichern(kid, "neuer Text")
    assert e.kommentare[kid]["text"] == "neuer Text"
    assert nav._bearbeite is None and not hasattr(nav._karten[0], "eingabe")
    assert any(blase.text == "neuer Text" for blase, _rechteck, _y in e.blasen_layout(300))

    vorher = SB.messen(next(iter(e.blasen_layout(300)))[0], 280, QFont("Sans", 10))
    nav._kommentar_schrift("gross")
    assert w.settings.get("kommentare/schrift") == "gross"
    assert SB.blasen_px("gross") > SB.blasen_px("mittel") > SB.blasen_px("klein")
    assert SB.karten_pt("gross") > SB.karten_pt("klein") and vorher > 0
    _schliesse(w)


def test_geoeffnetes_dokument_zeigt_kommentar_blasen_sofort(app, tmp_path):
    """Nach dem Wiederöffnen sind Kommentarblasen ohne weitere Änderung sichtbar."""
    w = win(tmp_path)
    w.new_document()
    w.show()
    e = w.current_editor()
    e.setPlainText("Bewerbung als Änderungsschneider,\nText hier.")
    e.select_range(14, 32)
    e.kommentar_neu("bleibt erhalten")
    pfad = str(tmp_path / "k.docx")
    assert w._write(w.current_tab(), pfad)
    w.open_path(pfad)

    editor = w.current_editor()
    assert len(editor.kommentare) == 1
    assert editor._blasen_flaeche is not None and editor._blasen_flaeche.isVisible()
    assert len(editor.blasen_layout(300)) == 1
    _schliesse(w)


def test_aenderungen_und_noten_im_feld_links_sind_echte_funktionen(app, tmp_path, monkeypatch):
    """Änderungen und Fuß-/Endnoten lassen sich über die linke Seitenleiste verwalten."""
    from lunivo_writer.ui.baukasten.dokument.eingabe_fenster import EingabeFenster

    w = win(tmp_path)
    w.new_document()
    w.show()
    e = w.current_editor()
    e.setPlainText("Ein Satz zum Prüfen.")
    nav = w.navigation
    monkeypatch.setattr(
        EingabeFenster,
        "getMultiLineText",
        staticmethod(lambda *a, **k: ("Notiztext", True)),
    )

    nav.zeige_tab("aenderungen")
    nav.show()
    assert nav.anzahl("aenderungen") == 0 and not nav._aend_leer.isHidden()
    nav.verfolgen_knopf.click()
    assert w.befehle.an_verfolgen() and nav.verfolgen_knopf.text() == "an"

    cursor = e.textCursor()
    cursor.setPosition(len("Ein Satz zum Prüfen."))
    e.setTextCursor(cursor)
    e.insertPlainText(" Neu dazu.")
    e.select_range(0, 3)
    e.insertPlainText("Das")
    nav.aktualisieren()
    assert nav.anzahl("aenderungen") >= 1

    erste = nav._aend_karten[0]
    anzahl = nav.anzahl("aenderungen")
    annehmen = [
        button
        for button in erste.findChildren(type(nav.verfolgen_knopf))
        if button.text() == "Annehmen"
    ][0]
    annehmen.click()
    assert nav.anzahl("aenderungen") == anzahl - 1
    nav._befehl("aenderungenUebernehmen")
    assert nav.anzahl("aenderungen") == 0

    nav.zeige_tab("noten")
    assert nav.anzahl("noten") == 0 and not nav._noten_leer.isHidden()
    cursor = e.textCursor()
    cursor.setPosition(3)
    e.setTextCursor(cursor)
    nav._befehl("fussnote")
    assert nav.anzahl("noten") == 1 and len(e.noten["f"]) == 1
    nav._befehl("endnote")
    assert nav.anzahl("noten") == 2

    karte = nav._noten_karten[0]
    loeschen = [
        button
        for button in karte.findChildren(type(nav.verfolgen_knopf))
        if button.text() == "Löschen"
    ][0]
    loeschen.click()
    assert nav.anzahl("noten") == 1
    _schliesse(w)


def test_tastenkuerzel_fuer_fussnote_und_endnote(app, tmp_path, monkeypatch):
    """Strg+Alt+F setzt eine Fußnote, Strg+Alt+D eine Endnote."""
    from lunivo_writer.ui.baukasten.dokument.eingabe_fenster import EingabeFenster

    w = win(tmp_path)
    w.new_document()
    w.show()
    e = w.current_editor()
    e.insertPlainText("Ein Satz mit Quelle.")
    e.setFocus()
    monkeypatch.setattr(
        EingabeFenster,
        "getMultiLineText",
        staticmethod(lambda *a, **k: ("Beleg", True)),
    )
    app.processEvents()

    QTest.keyClick(e, Qt.Key_F, Qt.ControlModifier | Qt.AltModifier)
    QTest.keyClick(e, Qt.Key_D, Qt.ControlModifier | Qt.AltModifier)
    app.processEvents()
    assert len(e.noten["f"]) == 1 and len(e.noten["e"]) == 1
    _schliesse(w)


def test_notenfeld_unten_schreibt_in_dieselbe_note_wie_das_feld_links(app, tmp_path):
    """Das untere Notenfeld und die linke Seitenleiste bearbeiten dieselbe Note."""
    w = win(tmp_path)
    w.new_document()
    w.show()
    e = w.current_editor()
    e.insertPlainText("Ein Satz mit Quelle.")
    w.befehle.fussnote()
    assert w.noten_feld.isVisible()
    assert w.noten_feld.titel.text() == "Fußnote 1"

    w.noten_feld.eingabe.setPlainText("Müller 2025, S. 4")
    assert list(e.noten["f"].values()) == ["Müller 2025, S. 4"]
    w.navigation.aktualisieren()
    assert w.navigation.anzahl("noten") == 1
    QTest.keyClick(w.noten_feld.eingabe, Qt.Key_Escape)
    assert not w.noten_feld.isVisible()
    assert list(e.noten["f"].values()) == ["Müller 2025, S. 4"]

    nid = next(iter(e.noten["f"]))
    e.noteAngeklickt.emit("f", nid)
    assert w.noten_feld.isVisible()
    assert w.noten_feld.eingabe.toPlainText() == "Müller 2025, S. 4"
    w.noten_feld.zumachen()
    w.befehle.note_bearbeiten("f", nid)
    assert w.noten_feld.isVisible()
    w.befehle.endnote()
    assert w.noten_feld.titel.text() == "Endnote i"
    _schliesse(w)


def test_ein_speichern_fenster_fuer_alle_formate(app, tmp_path, monkeypatch):
    """Speichern unter und Speichern unter ▸ Format verwenden dasselbe Fenster."""
    w = win(tmp_path)
    w.new_document()
    w.current_editor().insertPlainText("Hallo")
    gefragt = []

    def fenster(parent, titel, start, typen, vorwahl):
        gefragt.append((typen, vorwahl))
        return str(tmp_path / "brief"), ".txt"

    monkeypatch.setattr(FENSTER, fenster)
    assert w.save_as()
    assert w.save_as_format(".odt")
    (alle, v1), (alle2, v2) = gefragt
    assert alle == alle2 and v1 == ".docx" and v2 == ".odt"
    assert [endung for endung, _filter in alle] == [".docx", ".odt", ".rtf", ".txt", ".pdf"]
    assert (tmp_path / "brief.txt").read_text(encoding="utf-8") == "Hallo"
    _schliesse(w)


def test_speichern_fenster_dateityp_und_name(app, tmp_path, monkeypatch):
    """Dateityp, Endung, Ordnernavigation und Überschreibabbruch des eigenen Dateifensters."""
    from PySide6.QtWidgets import QMessageBox
    from lunivo_writer.ui.baukasten.dokument.speichern_fenster import SpeichernFenster

    typen = [
        (".docx", "Word-Dokument (*.docx)"),
        (".odt", "OpenDocument-Text (*.odt)"),
        (".pdf", "PDF-Dokument (*.pdf)"),
    ]
    (tmp_path / "unter").mkdir()
    f = SpeichernFenster(
        None, "Speichern unter", str(tmp_path / "Brief.docx"), typen, ".docx"
    )
    assert f.ordner == str(tmp_path)
    assert f.name.currentText() == "Brief.docx"
    assert f.typ.currentText() == "Word-Dokument (*.docx)"
    assert f.typ.isVisibleTo(f)
    f.typ.setCurrentIndex(1)
    assert f.name.currentText() == "Brief.odt"
    assert f.modell.nameFilters() == ["*.odt"]
    f.speichern()
    assert f.ergebnis() == (str(tmp_path / "Brief.odt"), ".odt")
    f.close()

    g = SpeichernFenster(
        None, "Speichern unter", str(tmp_path / "x.docx"), typen, ".docx"
    )
    g.name.setEditText("unter")
    g.speichern()
    assert g.ordner == str(tmp_path / "unter") and g.ergebnis() is None
    g.zurueck()
    assert g.ordner == str(tmp_path)
    g.close()

    (tmp_path / "da.pdf").write_bytes(b"%PDF")
    h = SpeichernFenster(None, "Exportieren", str(tmp_path / "da.pdf"), typen, ".pdf")
    monkeypatch.setattr(QMessageBox, "exec", lambda self: QMessageBox.Cancel)
    h.speichern()
    assert h.ergebnis() is None
    h.close()


def test_oeffnen_und_ordner_im_selben_fenster(app, tmp_path, monkeypatch):
    """Öffnen und Ordnerwahl verwenden dasselbe eigene Dateifenster."""
    from lunivo_writer.services import file_service as formats
    from lunivo_writer.ui.baukasten.dokument import speichern_fenster as SF

    (tmp_path / "a.docx").write_bytes(b"x")
    (tmp_path / "b.odt").write_bytes(b"x")
    (tmp_path / "unter").mkdir()
    gesehen = {}

    def exec_oeffnen(self):
        gesehen["knopf"] = self.k_speichern.text()
        gesehen["typ"] = self.typ.isVisibleTo(self)
        gesehen["filter"] = self.modell.nameFilters()
        self.name.setEditText('"a.docx" "b.odt"')
        self.speichern()
        return self.result()

    monkeypatch.setattr(SF.SpeichernFenster, "exec", exec_oeffnen)
    wahl = SF.datei_waehlen(None, "Öffnen", str(tmp_path), formats.OPEN_FILTER, mehrere=True)
    assert wahl == [str(tmp_path / "a.docx"), str(tmp_path / "b.odt")]
    assert gesehen["knopf"] == "Ö&ffnen" and gesehen["typ"]
    assert "*.odt" in gesehen["filter"]

    def exec_ordner(self):
        gesehen["ordnerknopf"] = self.k_speichern.text()
        self.name.setEditText(str(tmp_path / "unter"))
        self.speichern()
        return self.result()

    monkeypatch.setattr(SF.SpeichernFenster, "exec", exec_ordner)
    assert SF.ordner_waehlen(None, "Ordner", str(tmp_path)) == str(tmp_path / "unter")
    assert gesehen["ordnerknopf"] == "&Auswählen"

    w = win(tmp_path)
    geoeffnet = []
    monkeypatch.setattr(SF, "datei_waehlen", lambda *a, **k: [str(tmp_path / "a.docx")])
    monkeypatch.setattr(w, "open_path", lambda p: geoeffnet.append(p))
    w.open_dialog()
    assert geoeffnet == [str(tmp_path / "a.docx")]
    _schliesse(w)


def test_speichern_unter_pdf_behaelt_die_dokumentdatei(app, tmp_path, monkeypatch):
    w = win(tmp_path)
    w.new_document()
    w.current_editor().insertPlainText("Hallo")
    monkeypatch.setattr(FENSTER, lambda *a, **k: (str(tmp_path / "brief"), ".pdf"))
    assert w.save_as()
    assert os.path.getsize(tmp_path / "brief.pdf") > 500
    assert w.current_tab().path is None and w.current_editor().document().isModified()
    _schliesse(w)


def test_gewaehlter_dateityp_gilt_trotz_alter_endung(app, tmp_path, monkeypatch):
    """Der im Fenster gewählte Typ überschreibt eine alte oder abweichende Dateiendung."""
    w = win(tmp_path)
    w.new_document()
    monkeypatch.setattr(FENSTER, lambda *a, **k: (str(tmp_path / "brief.docx"), ".txt"))
    assert w._ask_path(w.current_tab(), "Speichern unter") == str(tmp_path / "brief.txt")
    monkeypatch.setattr(FENSTER, lambda *a, **k: (str(tmp_path / "brief.v2"), ".odt"))
    assert w._ask_path(w.current_tab(), "Speichern unter") == str(tmp_path / "brief.v2.odt")
    _schliesse(w)


def test_programm_symbol_fuer_fenster_und_leiste(app):
    """Das Fenster trägt Lunivos eigenes Symbol."""
    from lunivo_writer.core.application import programm_symbol

    icon = programm_symbol()
    assert not icon.isNull()
    assert {size.width() for size in icon.availableSizes()} >= {16, 32, 48, 256}


def test_kein_fremdes_dateifenster():
    """Überall dasselbe Datei-Fenster; kein QFileDialog außerhalb des eigenen Moduls."""
    wurzel = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "src", "lunivo_writer")
    )
    treffer = []
    for ordner, _unterordner, dateien in os.walk(wurzel):
        for name in dateien:
            if not name.endswith(".py") or name == "speichern_fenster.py":
                continue
            pfad = os.path.join(ordner, name)
            with open(pfad, encoding="utf-8", errors="replace") as datei:
                for nummer, zeile in enumerate(datei, 1):
                    if "QFileDialog" in zeile:
                        treffer.append(f"{os.path.relpath(pfad, wurzel)}:{nummer}")
    assert not treffer, "\n".join(treffer)


def test_dateifenster_speichern_mit_filter(app, tmp_path, monkeypatch):
    from lunivo_writer.ui.baukasten.dokument import speichern_fenster as SF

    gesehen = {}

    def exec_(self):
        gesehen["typ"] = self.typ.currentText()
        gesehen["name"] = self.name.currentText()
        self.speichern()
        return self.result()

    monkeypatch.setattr(SF.SpeichernFenster, "exec", exec_)
    pfad, _filter = SF.Dateifenster.getSaveFileName(
        None, "Sichern", str(tmp_path / "lunivo-sicherung.zip"), "ZIP (*.zip)"
    )
    assert pfad == str(tmp_path / "lunivo-sicherung.zip")
    assert gesehen == {"typ": "ZIP (*.zip)", "name": "lunivo-sicherung.zip"}


def test_dateifenster_spaltenkoepfe_deutsch(app, tmp_path):
    from PySide6.QtCore import Qt
    from lunivo_writer.ui.baukasten.dokument.speichern_fenster import SpeichernFenster

    f = SpeichernFenster(
        None,
        "Dateiobjekt einfügen",
        str(tmp_path / "a.docx"),
        [(".docx", "Word-Dokument (*.docx)")],
        ".docx",
    )
    koepfe = [f.modell.headerData(i, Qt.Horizontal) for i in range(4)]
    assert koepfe == ["Name", "Größe", "Typ", "Geändert"]
    f.close()


def test_suchoption_zaehlt_treffer_neu(app, tmp_path):
    w = win(tmp_path)
    w.new_document()
    w.show()
    e = w.current_editor()
    e.setPlainText("abc ABC abc Abc")
    nav = w.navigation
    nav.suche_zeigen("abc")
    vorher = nav.treffer.text()
    nav.gross.setChecked(True)
    assert nav.treffer.text() != vorher and "2" in nav.treffer.text()
    assert len(e._such_bereiche) == 2
    _schliesse(w)


def test_kommentar_im_leeren_absatz_erscheint_in_der_seitenleiste(app, tmp_path):
    w = win(tmp_path)
    w.new_document()
    w.show()
    e = w.current_editor()
    kid = e.kommentar_neu("Im leeren Absatz")
    assert kid is not None and e.kommentar_bereiche()
    w._links_klick("kommentare")
    assert w.navigation.anzahl("kommentare") == 1
    _schliesse(w)


def test_band_kompakt_umschalten(app, tmp_path):
    w = win(tmp_path)
    w.new_document()
    w.resize(1380, 860)
    w.show()
    assert w.band.kompakt and w.band.stapel.height() == w.band.BAND_HOEHE[True]
    w.settings.set("ui/band_kompakt", False)
    w.neu_bauen_band()
    assert not w.band.kompakt and w.band.stapel.height() == w.band.BAND_HOEHE[False]
    assert w.band.BAND_HOEHE[True] < w.band.BAND_HOEHE[False]
    _schliesse(w)


def test_band_hinweis_zeigt_kuerzel(app):
    from lunivo_writer.ui.ribbon.ribbon_bar import _mit_kuerzel

    assert _mit_kuerzel("Speichern") == "Speichern (Strg+S)"
    assert _mit_kuerzel("Unbekannt") == "Unbekannt"


def test_band_gruppen_klappen_nie_zusammen(app, tmp_path):
    w = win(tmp_path)
    w.new_document()
    w.resize(900, 600)
    w.show()
    band = w.band
    app.processEvents()
    assert not hasattr(band, "_gruppen_popup") and not hasattr(band, "_gruppen_anpassen")
    band.reiter.setCurrentIndex(1)
    app.processEvents()
    start = band.stapel.widget(1)
    assert start.horizontalScrollBar().maximum() > 0
    assert start.pfeile["rechts"].isVisible()
    _schliesse(w)


def test_dropdown_zeilen_und_menuemasse_nur_im_thema():
    """Dropdown-Zeilenabstand und Menümaße werden zentral im Thema festgelegt."""
    import pathlib
    import re

    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "lunivo_writer"
    muster = re.compile(
        r"setStyleSheet\([^\n]*(DROPDOWN_ZEILE_PADDING|PADDING_MENUE|QMenu::|PADDING_GALERIE_EINTRAG)"
    )
    treffer = sorted(
        p.relative_to(wurzel).as_posix()
        for p in wurzel.rglob("*.py")
        if p.name != "theme.py"
        and muster.search(p.read_text(encoding="utf-8", errors="replace"))
    )
    assert treffer == [], (
        "Dropdown-Zeilen-/Menümaß im Widget-Stylesheet statt im Thema: "
        + ", ".join(treffer)
    )


def test_dropdown_paket_ohne_eigene_stylesheets_und_menuepfeile_nur_im_thema():
    """Stylesheets und Menü-Pfeile werden außerhalb der Dropdown-Bausteine zentral gestaltet."""
    import pathlib
    import re

    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "lunivo_writer"
    paket = sorted(
        p.relative_to(wurzel).as_posix()
        for p in (wurzel / "ui" / "baukasten" / "dropdown").glob("*.py")
        if "setStyleSheet(" in p.read_text(encoding="utf-8", errors="replace")
    )
    assert paket == [], "Stylesheet im Dropdown-Paket: " + ", ".join(paket)

    pfeil = sorted(
        p.relative_to(wurzel).as_posix()
        for p in wurzel.rglob("*.py")
        if p.name != "theme.py"
        and re.search(
            r"::menu-(button|arrow)", p.read_text(encoding="utf-8", errors="replace")
        )
    )
    assert pfeil == [], "Menü-Knopf/-Pfeil außerhalb des Themas: " + ", ".join(pfeil)


def test_auswahlfelder_sehen_ueberall_gleich_aus(app):
    """Ein Auswahlfeld hat in allen UI-Kontexten und Themen dasselbe Aussehen."""
    from PySide6.QtWidgets import QVBoxLayout, QWidget
    from lunivo_writer.ui import theme
    from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld

    for modus in ("dark", "mint", "light"):
        theme.apply_theme(app, modus)
        bilder = []
        halter_fenster = []
        for kontext in ("fenster", "seitenkarte", "bandSeite"):
            halter = QWidget()
            halter_fenster.append(halter)
            layout = QVBoxLayout(halter)
            if kontext == "seitenkarte":
                halter.setProperty("seitenKarte", True)
            if kontext == "bandSeite":
                halter.setObjectName("bandSeite")
            feld = Auswahlfeld()
            feld.addItem("Standard")
            feld.setFixedWidth(160)
            layout.addWidget(feld)
            halter.show()
            app.processEvents()
            bilder.append((feld.height(), feld.grab().toImage()))

        for hoehe, bild in bilder[1:]:
            assert hoehe == bilder[0][0], f"Höhe verschieden im Thema {modus}"
            assert bild == bilder[0][1], f"Aussehen verschieden im Thema {modus}"
        for halter in halter_fenster:
            halter.close()
            halter.deleteLater()


def test_formular_gitter_gibt_dropdowns_die_dropdown_hoehe(app):
    """Ein Auswahlfeld im FormularGitter behält die zentrale Dropdown-Höhe."""
    from PySide6.QtWidgets import QWidget
    from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld
    from lunivo_writer.ui.baukasten.controls.formular_gitter import FormularGitter
    from lunivo_writer.ui.baukasten.basis.mass import DROPDOWN_HOEHE

    halter = QWidget()
    gitter = FormularGitter(halter)
    feld = Auswahlfeld()
    feld.addItem("Standard")
    gitter.zeile("Chatbot", feld)
    halter.resize(300, 200)
    halter.show()
    app.processEvents()
    assert feld.height() == DROPDOWN_HOEHE
    halter.close()
    halter.deleteLater()


def test_dropdown_breite_und_hoehe_nur_ueber_rolle():
    """Dropdown-Breite und -Höhe werden außerhalb des Dropdown-Pakets nicht von Hand gesetzt."""
    import ast
    import pathlib

    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "lunivo_writer"
    klassen = {
        "Auswahlfeld",
        "Schriftauswahl",
        "VorschauCombo",
        "VorschauFontCombo",
        "DropdownKnopf",
        "DropdownTaste",
    }
    verboten = {
        "setFixedWidth",
        "setFixedHeight",
        "setFixedSize",
        "setMinimumWidth",
        "setMinimumHeight",
        "setMinimumSize",
        "setMaximumWidth",
        "setMaximumHeight",
    }

    def name(knoten):
        if isinstance(knoten, ast.Name):
            return knoten.id
        if isinstance(knoten, ast.Attribute) and isinstance(knoten.value, ast.Name):
            if knoten.value.id == "self":
                return "self." + knoten.attr
        return None

    def ctor(knoten):
        return (
            isinstance(knoten, ast.Call)
            and isinstance(knoten.func, ast.Name)
            and knoten.func.id in klassen
        )

    treffer = []
    for p in wurzel.rglob("*.py"):
        if "ui/baukasten/dropdown/" in p.as_posix():
            continue
        baum = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        for funktion in (
            knoten
            for knoten in ast.walk(baum)
            if isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef))
        ):
            namen = set()
            for knoten in ast.walk(funktion):
                if isinstance(knoten, ast.Assign) and ctor(knoten.value):
                    namen.update(name(ziel) for ziel in knoten.targets if name(ziel))
                if (
                    isinstance(knoten, ast.Assign)
                    and isinstance(knoten.value, ast.Tuple)
                    and any(ctor(element) for element in knoten.value.elts)
                ):
                    for ziel in knoten.targets:
                        if isinstance(ziel, ast.Tuple):
                            namen.update(
                                name(ziel_element)
                                for ziel_element, element in zip(ziel.elts, knoten.value.elts)
                                if ctor(element) and name(ziel_element)
                            )
            for knoten in ast.walk(funktion):
                if (
                    isinstance(knoten, ast.Call)
                    and isinstance(knoten.func, ast.Attribute)
                    and knoten.func.attr in verboten
                    and (name(knoten.func.value) in namen or ctor(knoten.func.value))
                ):
                    treffer.append(f"{p.relative_to(wurzel).as_posix()}:{knoten.lineno} {knoten.func.attr}")

    assert sorted(set(treffer)) == [], (
        "Dropdown-Größe von Hand statt über rolle(): " + ", ".join(sorted(set(treffer)))
    )


def test_dropdown_paket_ohne_feste_farben_und_layoutzahlen():
    """Das Dropdown-Paket enthält keine festen Hexfarben oder Layoutzahlen."""
    import ast
    import pathlib
    import re

    wurzel = (
        pathlib.Path(__file__).resolve().parent.parent.parent
        / "src"
        / "lunivo_writer"
        / "ui"
        / "baukasten"
        / "dropdown"
    )
    treffer = []
    for p in sorted(wurzel.glob("*.py")):
        baum = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        for knoten in ast.walk(baum):
            if (
                isinstance(knoten, ast.Constant)
                and isinstance(knoten.value, str)
                and re.fullmatch(r"#[0-9a-fA-F]{6,8}", knoten.value)
            ):
                treffer.append(f"{p.name}:{knoten.lineno} Farbe {knoten.value}")
            if (
                isinstance(knoten, ast.Call)
                and isinstance(knoten.func, ast.Attribute)
                and knoten.func.attr in ("adjusted", "setContentsMargins", "setSpacing")
            ):
                zahlen = [
                    argument
                    for argument in knoten.args
                    if isinstance(argument, ast.Constant)
                    and isinstance(argument.value, (int, float))
                    and not isinstance(argument.value, bool)
                    and argument.value != 0
                ]
                if zahlen:
                    treffer.append(f"{p.name}:{knoten.lineno} {knoten.func.attr}")
    assert treffer == [], "feste Farbe/Layoutzahl im Dropdown-Paket: " + ", ".join(treffer)


def test_formular_gitter_setzt_dropdowns_keine_eigene_hoehe(app):
    """FormularGitter überschreibt Dropdown-Höhe nicht; Textfelder bekommen FELDHOEHE."""
    from PySide6.QtWidgets import QLineEdit, QWidget
    from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld
    from lunivo_writer.ui.baukasten.controls.formular_gitter import (
        FELDHOEHE,
        FormularGitter,
        felder_angleichen,
    )
    from lunivo_writer.ui.baukasten.basis.mass import DROPDOWN_HOEHE

    halter = QWidget()
    gitter = FormularGitter(halter)
    dropdown = Auswahlfeld()
    textfeld = QLineEdit()
    gitter.zeile("Chatbot", dropdown)
    gitter.zeile("Name", textfeld)
    felder_angleichen(halter)
    halter.resize(300, 200)
    halter.show()
    app.processEvents()
    assert dropdown.height() == DROPDOWN_HOEHE
    assert dropdown.minimumHeight() == DROPDOWN_HOEHE
    assert dropdown.maximumHeight() > DROPDOWN_HOEHE
    assert textfeld.height() == FELDHOEHE
    halter.close()
    halter.deleteLater()


def test_alle_dropdown_arten_haben_im_formular_gitter_dieselbe_hoehe(app):
    """Alle Dropdown-Arten im FormularGitter haben dieselbe zentrale Höhe."""
    from PySide6.QtWidgets import QWidget
    from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld
    from lunivo_writer.ui.baukasten.dropdown.auswahl.farbpalette import FarbFeld
    from lunivo_writer.ui.baukasten.dropdown.kopf_dropdown import KopfDropdown
    from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
    from lunivo_writer.ui.baukasten.dropdown.auswahl.strich_auswahl import StrichAuswahl
    from lunivo_writer.ui.baukasten.dropdown.teil_menue import TeilMenueKnopf
    from lunivo_writer.ui.baukasten.controls.formular_gitter import FormularGitter
    from lunivo_writer.ui.baukasten.basis.mass import DROPDOWN_HOEHE

    halter = QWidget()
    gitter = FormularGitter(halter)
    felder = [
        Auswahlfeld(),
        FarbFeld(),
        KopfDropdown(lambda parent: MenueListe(parent)),
        StrichAuswahl([]),
        TeilMenueKnopf(),
    ]
    for nummer, feld in enumerate(felder):
        gitter.zeile(f"Feld {nummer}", feld)
    halter.resize(300, 500)
    halter.show()
    app.processEvents()
    assert [feld.height() for feld in felder] == [DROPDOWN_HOEHE] * len(felder)
    halter.close()
    halter.deleteLater()


def test_band_dropdowns_start_seitenlayout_ueberpruefen_haben_dropdown_hoehe(app, tmp_path):
    """Sichtbare Dropdowns in Start, Seitenlayout und Überprüfen sind mindestens DROPDOWN_HOEHE hoch."""
    from PySide6.QtWidgets import QAbstractSpinBox, QComboBox
    from lunivo_writer.ui.baukasten.dropdown.dropdown_knopf import DropdownKnopf
    from lunivo_writer.ui.baukasten.basis.mass import DROPDOWN_HOEHE

    w = win(tmp_path)
    w.new_document()
    w.resize(1920, 1040)
    w.show()
    app.processEvents()
    register = w.band
    zu_niedrig = []

    for index in range(register.reiter.count()):
        reitername = register.reiter.tabText(index)
        if reitername not in ("Start", "Seitenlayout", "Überprüfen"):
            continue
        register.reiter.setCurrentIndex(index)
        app.processEvents()
        felder = (
            register.findChildren(QComboBox)
            + register.findChildren(QAbstractSpinBox)
            + [
                widget
                for widget in register.findChildren(DropdownKnopf)
                if widget.menu() is not None
            ]
        )
        for feld in felder:
            if feld.isVisibleTo(register) and feld.height() < DROPDOWN_HOEHE:
                zu_niedrig.append((reitername, type(feld).__name__, feld.height()))

    assert zu_niedrig == [], f"Dropdowns niedriger als DROPDOWN_HOEHE: {zu_niedrig}"
    _schliesse(w)


def test_band_massfelder_haben_den_hintergrund_der_dropdowns(app, tmp_path):
    """Die Maßfelder der Ränder haben denselben Hintergrund wie das Schrift-Dropdown."""
    from PySide6.QtWidgets import QAbstractSpinBox, QComboBox
    from lunivo_writer.ui import theme

    for modus in ("dark", "mint", "light"):
        theme.apply_theme(app, modus)
        w = win(tmp_path)
        w.new_document()
        w.resize(1920, 1040)
        w.show()
        app.processEvents()
        register = w.band
        farben = {}

        for index in range(register.reiter.count()):
            reitername = register.reiter.tabText(index)
            if reitername not in ("Start", "Seitenlayout"):
                continue
            register.reiter.setCurrentIndex(index)
            app.processEvents()
            felder = [
                feld
                for feld in (
                    register.findChildren(QComboBox)
                    + register.findChildren(QAbstractSpinBox)
                )
                if feld.isVisibleTo(register)
            ]
            assert felder, f"Kein sichtbares Maß-/Dropdownfeld im Reiter {reitername}"
            feld = felder[0]
            bild = feld.grab().toImage()
            farben[reitername] = bild.pixelColor(feld.width() // 2, 4).name()

        assert farben["Start"] == farben["Seitenlayout"], (
            f"Hintergrund verschieden im Thema {modus}: {farben}"
        )
        _schliesse(w)