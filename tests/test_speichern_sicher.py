"""Speicher-Testsuite: sicherer Schreibweg, Formate, Fehlerfälle, Absturz und gleichzeitiges Speichern.

Alle Tests arbeiten in eigenen Testordnern (tmp_path) mit eigens erzeugten Dateien. Geprüft wird nicht nur, dass eine Datei da ist,
sondern ihre Struktur (``pruefe_format``) und ihr Inhalt nach erneutem Öffnen."""
import errno
import os
import signal
import subprocess
import sys
import threading
import time
import zipfile

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor, QImage, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument, QTextFormat, QTextImageFormat

from lunivo_writer.models.page import PageSettings
from lunivo_writer.models.report import DocumentIOError
from lunivo_writer.services import file_service as formats
from lunivo_writer.services import sicher_schreiben as S

ALS_ROOT = hasattr(os, "geteuid") and os.geteuid() == 0


@pytest.fixture(autouse=True)
def _eigene_sicherungen(tmp_path, monkeypatch):
    """Sicherungskopien landen im Testordner, nie im echten Datenordner."""
    monkeypatch.setattr(S, "sicherungs_ordner", lambda: str(tmp_path / "_sicherungen"))


def _doc(text: str = "Hallo Welt") -> QTextDocument:
    d = QTextDocument()
    QTextCursor(d).insertText(text)
    return d


def _text(path: str) -> str:
    return formats.load(path).doc.toPlainText()


def _temp_reste(ordner) -> list[str]:
    return [f for f in os.listdir(ordner) if f.endswith(".tmp")]


# ---- Speichern und erneut öffnen -------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("endung", [".docx", ".txt", ".odt", ".rtf"])
def test_neu_speichern_und_oeffnen(app, tmp_path, endung):
    p = str(tmp_path / ("neu" + endung))
    formats.save(p, _doc("Erste Zeile\nZweite Zeile"), PageSettings())
    S.pruefe_format(p, endung)
    assert _text(p).splitlines()[:2] == ["Erste Zeile", "Zweite Zeile"]
    assert not _temp_reste(tmp_path)


def test_odt_hat_seite_und_text(app, tmp_path):
    p = str(tmp_path / "eigen.odt")
    formats.save(p, _doc("Eigenes ODT"), PageSettings())
    S.pruefe_format(p, ".odt")
    with zipfile.ZipFile(p) as z:
        assert b"Eigenes ODT" in z.read("content.xml") and b"style:page-layout" in z.read("styles.xml")


def test_bestehendes_aendern_speichern_oeffnen(app, tmp_path):
    p = str(tmp_path / "brief.docx")
    formats.save(p, _doc("Fassung 1"), PageSettings())
    geladen = formats.load(p)
    QTextCursor(geladen.doc).movePosition(QTextCursor.End)
    c = QTextCursor(geladen.doc); c.movePosition(QTextCursor.End); c.insertText(" – ergänzt")
    formats.save(p, geladen.doc, geladen.page, geladen.meta)
    assert _text(p) == "Fassung 1 – ergänzt"


def test_mehrfach_speichern_und_begrenzte_sicherungen(app, tmp_path):
    p = str(tmp_path / "oft.docx")
    for i in range(8):
        formats.save(p, _doc(f"Fassung {i}"), PageSettings())
    assert _text(p) == "Fassung 7"
    kopien = S.sicherungen(p)
    assert len(kopien) == S.SICHERUNGEN_JE_DOKUMENT                 # nicht mehr als erlaubt
    assert _text(kopien[0]) == "Fassung 6"                           # neueste Sicherung = Vorfassung
    assert not _temp_reste(tmp_path)


def test_alte_sicherungen_werden_entfernt(app, tmp_path):
    p = str(tmp_path / "alt.docx")
    formats.save(p, _doc("a"), PageSettings())
    formats.save(p, _doc("b"), PageSettings())
    (kopie,) = S.sicherungen(p)
    alt = time.time() - (S.SICHERUNG_TAGE + 1) * 86400
    os.utime(kopie, (alt, alt))
    S.sicherungen_aufraeumen()
    assert S.sicherungen(p) == []


def test_speichern_unter_neuem_namen_laesst_original(app, tmp_path):
    a, b = str(tmp_path / "a.docx"), str(tmp_path / "b.docx")
    formats.save(a, _doc("Original"), PageSettings())
    formats.save(b, _doc("Neu"), PageSettings())
    assert _text(a) == "Original" and _text(b) == "Neu"


@pytest.mark.parametrize("endung", [".docx", ".txt", ".odt", ".rtf"])
def test_unicode_in_text_und_dateiname(app, tmp_path, endung):
    text = "Grüße aus Köln – „Ärger“ 𝄞 ✓ 日本語 Ωmega"
    p = str(tmp_path / f"Übersicht ß – 日本 ✓{endung}")
    formats.save(p, _doc(text), PageSettings())
    assert _text(p) == text


@pytest.mark.parametrize("endung", [".docx", ".txt", ".odt", ".rtf"])
def test_leeres_dokument(app, tmp_path, endung):
    p = str(tmp_path / ("leer" + endung))
    formats.save(p, QTextDocument(), PageSettings())
    S.pruefe_format(p, endung)
    assert _text(p) == ""


@pytest.mark.parametrize("endung", [".docx", ".odt", ".rtf"])
def test_grosses_dokument_mit_tabelle_bild_format_umbruch(app, tmp_path, endung):
    d = QTextDocument(); c = QTextCursor(d)
    fett = QTextCharFormat(); fett.setFontWeight(700)
    c.insertText("Fetter Anfang", fett); c.insertText("\n", QTextCharFormat())
    for i in range(3000):
        c.insertText(f"Absatz {i}: Lorem ipsum dolor sit amet, äöü ß.\n")
    umbruch = QTextBlockFormat(); umbruch.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore)
    c.insertBlock(umbruch); c.insertText("Nach dem Umbruch")
    c.insertBlock(QTextBlockFormat())
    t = c.insertTable(2, 2)
    for r in range(2):
        for s in range(2):
            t.cellAt(r, s).firstCursorPosition().insertText(f"Z{r}S{s}")
    c.movePosition(QTextCursor.End)
    bild = QImage(40, 30, QImage.Format_RGB32); bild.fill(QColor("red"))
    d.addResource(QTextDocument.ImageResource, "mem://rot.png", bild)
    fmt = QTextImageFormat(); fmt.setName("mem://rot.png"); fmt.setWidth(40); fmt.setHeight(30)
    c.insertBlock(); c.insertImage(fmt)
    p = str(tmp_path / ("gross" + endung))
    formats.save(p, d, PageSettings())
    S.pruefe_format(p, endung)
    back = formats.load(p).doc
    txt = back.toPlainText()
    assert "Absatz 2999" in txt and "Nach dem Umbruch" in txt and "Z1S1" in txt
    assert back.find("Fetter Anfang").charFormat().fontWeight() >= 600
    assert back.findBlock(back.find("Nach dem Umbruch").position()).blockFormat().pageBreakPolicy() & QTextFormat.PageBreak_AlwaysBefore
    bilder = []
    b = back.begin()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            if it.fragment().charFormat().isImageFormat():
                bilder.append(it.fragment().charFormat().toImageFormat())
            it += 1
        b = b.next()
    assert len(bilder) == 1 and round(bilder[0].width()) == 40               # das Bild kommt wieder an


# ---- Beschädigte Quelldateien ----------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("name,inhalt", [
    ("leer.docx", b""), ("zufall.docx", os.urandom(2000)), ("text.docx", b"Das ist kein Word-Dokument"),
    ("kaputt.odt", b"PK\x03\x04 abgeschnitten"), ("leer.rtf", b""),
])
def test_beschaedigte_quelldatei_wird_gemeldet(app, tmp_path, name, inhalt):
    p = tmp_path / name; p.write_bytes(inhalt)
    with pytest.raises(DocumentIOError):
        formats.load(str(p))


def test_abgeschnittene_docx_wird_gemeldet(app, tmp_path):
    p = str(tmp_path / "ganz.docx")
    formats.save(p, _doc("x" * 5000), PageSettings())
    daten = open(p, "rb").read()
    halb = tmp_path / "halb.docx"; halb.write_bytes(daten[: len(daten) // 2])
    with pytest.raises(DocumentIOError):
        formats.load(str(halb))


# ---- Strukturprüfung vor dem Ersetzen --------------------------------------------------------------------------------------------
@pytest.mark.parametrize("endung,daten", [
    (".docx", b"PK\x03\x04kaputt"), (".odt", b""), (".pdf", b"%PDF-1.7\nohne Ende"), (".rtf", b"{\\rtf1 offen"),
    (".txt", b"\xff\xfe\xfa"),
])
def test_ungueltige_neue_fassung_ersetzt_nichts(tmp_path, endung, daten):
    p = tmp_path / ("ziel" + endung); p.write_bytes(b"BISHER")
    with pytest.raises(DocumentIOError, match="unverändert"):
        S.bytes_schreiben(str(p), daten)
    assert p.read_bytes() == b"BISHER" and not _temp_reste(tmp_path)


# ---- Schreib- und Dateisystemfehler ----------------------------------------------------------------------------------------------
def test_speicherplatz_voll(app, tmp_path):
    p = tmp_path / "voll.docx"
    formats.save(str(p), _doc("gut"), PageSettings())
    vorher = p.read_bytes()

    def voll(tmp):
        with open(tmp, "wb") as fh:
            fh.write(b"PK halb")
        raise OSError(errno.ENOSPC, "No space left on device")

    with pytest.raises(DocumentIOError, match="nicht genug Platz.*unverändert"):
        S.schreiben(str(p), voll)
    assert p.read_bytes() == vorher and not _temp_reste(tmp_path)


def test_fehler_beim_anlegen_der_tempdatei(tmp_path, monkeypatch):
    p = tmp_path / "x.txt"; p.write_text("alt")
    monkeypatch.setattr(S.tempfile, "mkstemp", lambda **k: (_ for _ in ()).throw(OSError(errno.EACCES, "Permission denied")))
    with pytest.raises(DocumentIOError, match="Keine Schreibrechte"):
        S.bytes_schreiben(str(p), b"neu")
    assert p.read_text() == "alt"


def test_fehler_beim_ersetzen(tmp_path, monkeypatch):
    p = tmp_path / "x.txt"; p.write_text("alt")
    monkeypatch.setattr(S.os, "replace", lambda a, b: (_ for _ in ()).throw(OSError(errno.EBUSY, "busy")))
    with pytest.raises(DocumentIOError, match="in Benutzung"):
        S.bytes_schreiben(str(p), b"neu")
    assert p.read_text() == "alt" and not _temp_reste(tmp_path)


@pytest.mark.skipif(ALS_ROOT, reason="als root greifen Dateirechte nicht")
def test_fehlende_schreibrechte(tmp_path):
    ordner = tmp_path / "nur_lesen"; ordner.mkdir()
    p = ordner / "x.txt"; p.write_text("alt")
    ordner.chmod(0o500)
    try:
        with pytest.raises(DocumentIOError, match="Keine Schreibrechte"):
            S.bytes_schreiben(str(p), b"neu")
        assert p.read_text() == "alt"
    finally:
        ordner.chmod(0o700)


def test_ordner_fehlt_und_ungueltiger_name(tmp_path):
    with pytest.raises(DocumentIOError, match="existiert nicht"):
        S.bytes_schreiben(str(tmp_path / "gibtsnicht" / "x.txt"), b"x")
    with pytest.raises(DocumentIOError, match="ungültig"):
        S.bytes_schreiben(str(tmp_path / "a\0b.txt"), b"x")
    (tmp_path / "ordner.txt").mkdir()
    with pytest.raises(DocumentIOError, match="ist ein Ordner"):
        S.bytes_schreiben(str(tmp_path / "ordner.txt"), b"x")


def test_rechte_und_verknuepfung_bleiben(tmp_path):
    echt = tmp_path / "echt.txt"; echt.write_text("alt"); echt.chmod(0o640)
    link = tmp_path / "link.txt"; link.symlink_to(echt)
    S.bytes_schreiben(str(link), "neu".encode())
    assert link.is_symlink() and echt.read_text() == "neu" and (echt.stat().st_mode & 0o777) == 0o640


def test_neue_datei_folgt_umask(tmp_path):
    p = tmp_path / "neu.txt"
    S.bytes_schreiben(str(p), b"x")
    assert (p.stat().st_mode & 0o777) == 0o666 & ~S._umask()


# ---- Abbruch während des Schreibens ----------------------------------------------------------------------------------------------
ABBRUCH_SKRIPT = r"""
import sys, time
sys.path.insert(0, sys.argv[2])
from lunivo_writer.services import sicher_schreiben as S
def langsam(tmp):
    with open(tmp, "wb") as fh:
        fh.write(b"PK halb geschrieben")
        fh.flush()
        print("SCHREIBT", flush=True)
        time.sleep(60)
S.schreiben(sys.argv[1], langsam, sicherung=False)
"""


def test_prozessabbruch_waehrend_des_schreibens(app, tmp_path, monkeypatch):
    p = tmp_path / "wichtig.docx"
    formats.save(str(p), _doc("Gute Fassung"), PageSettings())
    vorher = p.read_bytes()
    src = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
    kind = subprocess.Popen([sys.executable, "-c", ABBRUCH_SKRIPT, str(p), src], stdout=subprocess.PIPE, text=True,
                            env={**os.environ, "QT_QPA_PLATFORM": "offscreen"})
    assert kind.stdout.readline().strip() == "SCHREIBT"
    kind.send_signal(signal.SIGKILL); kind.wait()                     # wie Absturz oder Stromausfall mitten im Schreiben
    assert p.read_bytes() == vorher and _text(str(p)) == "Gute Fassung"
    assert len(_temp_reste(tmp_path)) == 1                            # der Rest ist eine versteckte eigene Temp-Datei
    monkeypatch.setattr(S, "REST_ALTER_S", 0)
    time.sleep(0.01)
    formats.save(str(p), _doc("Nächste Fassung"), PageSettings())     # das nächste Speichern räumt ihn weg
    assert _text(str(p)) == "Nächste Fassung" and not _temp_reste(tmp_path)


# ---- Gleichzeitiges Speichern ----------------------------------------------------------------------------------------------------
def test_gleichzeitiges_speichern_im_programm(tmp_path):
    p = str(tmp_path / "parallel.txt")
    drin, weiter = threading.Event(), threading.Event()
    fehler = []

    def langsam(tmp):
        with open(tmp, "wb") as fh:
            fh.write("erster".encode())
        drin.set(); weiter.wait(5)

    t = threading.Thread(target=lambda: S.schreiben(p, langsam)); t.start()
    assert drin.wait(5)
    try:
        S.bytes_schreiben(p, b"zweiter")
    except DocumentIOError as e:
        fehler.append(str(e))
    weiter.set(); t.join(5)
    assert fehler and "gerade schon gespeichert" in fehler[0]
    assert open(p).read() == "erster"
    S.bytes_schreiben(p, b"danach")                                    # nach dem Ende ist die Sperre frei
    assert open(p).read() == "danach"


SPERR_SKRIPT = r"""
import sys, time
sys.path.insert(0, sys.argv[2])
from lunivo_writer.services import sicher_schreiben as S
with S.sperre(sys.argv[1]):
    print("GESPERRT", flush=True)
    time.sleep(60)
"""


def test_gleichzeitiges_speichern_aus_anderem_fenster(tmp_path):
    p = tmp_path / "geteilt.txt"; p.write_text("alt")
    src = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
    kind = subprocess.Popen([sys.executable, "-c", SPERR_SKRIPT, str(p), src], stdout=subprocess.PIPE, text=True,
                            env={**os.environ, "QT_QPA_PLATFORM": "offscreen"})
    try:
        assert kind.stdout.readline().strip() == "GESPERRT"
        with pytest.raises(DocumentIOError, match="anderen Lunivo-Fenster"):
            S.bytes_schreiben(str(p), b"neu")
        assert p.read_text() == "alt"
    finally:
        kind.kill(); kind.wait()
    S.bytes_schreiben(str(p), b"neu")
    assert p.read_text() == "neu"


def test_libreoffice_sperrdatei_wird_erkannt(tmp_path):
    p = tmp_path / "offen.odt"; p.write_bytes(b"x")
    assert S.fremd_geoeffnet(str(p)) is None
    (tmp_path / ".~lock.offen.odt#").write_text("kay,host,...")
    assert S.fremd_geoeffnet(str(p)) == "einem anderen Office-Programm"


# ---- Oberfläche: fremde Änderung (Synchronisierung), PDF, Statusmeldung ---------------------------------------------------------
def _fenster(tmp_path):
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    return MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))


def test_fremde_aenderung_wird_nicht_still_ueberschrieben(app, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    p = tmp_path / "sync.docx"
    formats.save(str(p), _doc("Vom Rechner"), PageSettings())
    w = _fenster(tmp_path)
    assert w.open_path(str(p))
    w.current_editor().insertPlainText("Lokal ")
    time.sleep(0.01)
    formats.save(str(p), _doc("Vom Sync-Dienst"), PageSettings())      # z. B. Nextcloud spielt eine neuere Fassung ein
    gefragt = []
    monkeypatch.setattr(QMessageBox, "exec", lambda self: gefragt.append(self.text()) or 0)
    assert w.save() is False
    assert gefragt and "außerhalb von Lunivo geändert" in gefragt[0]
    assert _text(str(p)) == "Vom Sync-Dienst" and w.current_editor().document().isModified()


def test_fremde_aenderung_auf_wunsch_ueberschreiben(app, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    p = tmp_path / "sync2.docx"
    formats.save(str(p), _doc("Alt"), PageSettings())
    w = _fenster(tmp_path)
    assert w.open_path(str(p))
    w.current_editor().setPlainText("Meine Fassung")
    time.sleep(0.01)
    formats.save(str(p), _doc("Fremd"), PageSettings())

    def ueberschreiben(box):
        knopf = next(b for b in box.buttons() if b.text() == "Trotzdem überschreiben")
        box.clickedButton = lambda: knopf
        return 0

    monkeypatch.setattr(QMessageBox, "exec", ueberschreiben)
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    assert w.save()
    assert _text(str(p)) == "Meine Fassung"
    assert _text(S.sicherungen(str(p))[0]) == "Fremd"                  # die fremde Fassung liegt in den Sicherungskopien
    assert w.save()                                                     # danach ist der Stand wieder bekannt: keine Frage mehr


def test_fehler_meldet_kein_gespeichert_und_dokument_bleibt_bearbeitbar(app, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    p = tmp_path / "f.docx"
    formats.save(str(p), _doc("alt"), PageSettings())
    w = _fenster(tmp_path)
    assert w.open_path(str(p))
    w.current_editor().insertPlainText("neu ")
    meldungen = []
    monkeypatch.setattr(QMessageBox, "critical", lambda *a, **k: meldungen.append(a[2]))
    monkeypatch.setattr(S.os, "replace", lambda a, b: (_ for _ in ()).throw(OSError(errno.ENOSPC, "voll")))
    assert w.save() is False
    assert meldungen and "nicht genug Platz" in meldungen[0]
    assert "Gespeichert" not in w.statusBar().currentMessage()
    assert w.current_editor().document().isModified() and not w.current_editor().isReadOnly()
    assert _text(str(p)) == "alt"


def test_pdf_export_ersetzt_alte_pdf_erst_nach_erfolg(app, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    from lunivo_writer.ui.hauptfenster import dateien
    alt = tmp_path / "x.pdf"; alt.write_bytes(b"%PDF-1.4\nalte Fassung\n%%EOF\n")
    w = _fenster(tmp_path); w.new_document(); w.current_editor().insertPlainText("PDF-Text")

    def bricht_ab(pfad, *a, **k):
        open(pfad, "wb").write(b"%PDF-1.4\nhalb")
        raise RuntimeError("Abbruch beim Rendern")

    monkeypatch.setattr(dateien, "export_pdf", bricht_ab)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a, **k: None)
    assert w._pdf_schreiben(w.current_tab(), str(alt)) is False
    assert alt.read_bytes().startswith(b"%PDF-1.4\nalte Fassung") and not _temp_reste(tmp_path)


# ---- Prüfprotokoll-Werkzeug ------------------------------------------------------------------------------------------------------
def test_pruefprotokoll_ohne_dokumentinhalte(app, tmp_path):
    import importlib.util
    import sqlite3
    pfad = os.path.join(os.path.dirname(os.path.dirname(__file__)), "werkzeug", "speicherpruefung.py")
    spec = importlib.util.spec_from_file_location("speicherpruefung", pfad)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    db = str(tmp_path / "p.sqlite3")
    zeilen = mod.pruefen([".txt", ".docx"], db)
    assert len(zeilen) == 10 and all(z[5] == 1 and z[6] == 1 and z[7] == 1 and z[8] == 1 for z in zeilen)
    with sqlite3.connect(db) as con:
        alles = " ".join(str(v) for row in con.execute("SELECT * FROM pruefung") for v in row)
    assert "Lorem ipsum" not in alles and "Grüße" not in alles and len(zeilen[0][10]) == 64
