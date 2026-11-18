"""Kommentare, Fuß-/Endnoten, nachverfolgte Änderungen und Textmarken: DOCX-Rundlauf über das Dokumentenmodell."""
import os
import zipfile

import pytest

from lunivo_writer.core.document.dokument import Auswahl, Kommentar, Lauf, Note, Position
from tests.hilfen_dokument import docx_rundlauf, sitzung


def _dokument(geloest: bool = False):
    s = sitzung("Hallo Welt, gelöscht neu Ziel 1 hier")
    #            0         10        20        30
    a = next(iter(s.dokument.absaetze()))

    def fmt(von, bis, **f):
        s.zeichenformat_anwenden(f, Auswahl(Position(a.id, von), Position(a.id, bis)))
    fmt(0, 5, kommentar=7)
    fmt(12, 20, aenderung="del", autor="Ann", datum="2026-01-02T03:04:05Z")
    fmt(21, 24, aenderung="ins", autor="Bob")
    fmt(25, 29, anker=["ziel"])
    s.text_einfuegen("1", pos=Position(a.id, 30), format={"hoch_tief": "hoch", "note": "f:5"})
    s.dokument.kommentare[7] = Kommentar(7, "Ann", "AN", "2026-01-02T03:04:05+00:00", "Bitte prüfen\nZweite Zeile", geloest)
    s.dokument.noten["f"][5] = Note(5, "f", "Eine Fußnote.")
    return s.dokument


def _formate(d):
    return [x.format for a in d.absaetze() for x in a.inhalte if isinstance(x, Lauf)]


def test_zusatz_rundlauf(app, tmp_path):
    gelesen, schreib, lese, pfad = docx_rundlauf(_dokument(), tmp_path, "z.docx")
    z = zipfile.ZipFile(pfad)
    assert "word/footnotes.xml" in z.namelist() and "word/comments.xml" in z.namelist()
    xml = z.read("word/document.xml").decode()
    assert "<w:del " in xml and "<w:delText" in xml and "<w:ins " in xml and "w:footnoteReference" in xml
    assert 'w:name="ziel"' in xml and "commentRangeStart" in xml
    assert not lese.warnings and not schreib.warnings
    kommentare = list(gelesen.kommentare.values())
    assert len(kommentare) == 1 and kommentare[0].text.startswith("Bitte prüfen") and kommentare[0].autor == "Ann"
    assert [n.text for n in gelesen.noten["f"].values()] == ["Eine Fußnote."]
    text = gelesen.text()
    assert "gelöscht" in text and "neu" in text           # gelöschter Text bleibt als solcher erhalten
    formate = _formate(gelesen)
    dele = [f for f in formate if f.get("aenderung") == "del"]
    ins = [f for f in formate if f.get("aenderung") == "ins"]
    assert dele and dele[0]["autor"] == "Ann" and dele[0]["datum"].startswith("2026-01-02") and ins and ins[0]["autor"] == "Bob"
    assert any(f.get("kommentar") is not None for f in formate)
    assert any("ziel" in (f.get("anker") or ()) for f in formate)
    assert any(str(f.get("note", "")).startswith("f:") for f in formate)


def test_zusatz_datei_oeffnet_in_fremdem_office(app, tmp_path):
    import shutil
    soffice = shutil.which("soffice")      # nur Prüfwerkzeug: öffnet ein fremdes Office die Datei?
    if not soffice:
        pytest.skip("Fremdes Office-Programm nicht installiert")
    _gelesen, _s, _l, out = docx_rundlauf(_dokument(), tmp_path, "z.docx")
    pdf = str(tmp_path / "z.pdf")
    import subprocess
    r = subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(tmp_path), str(out)], capture_output=True, timeout=120)
    assert os.path.exists(pdf), r.stderr
    import pypdf
    txt = " ".join(pypdf.PdfReader(pdf).pages[0].extract_text().split())
    assert "Eine Fußnote." in txt


def test_geloester_kommentar_ueberlebt_docx(app, tmp_path):
    """„Gelöst“ wird als commentsExtended (w15:done) gespeichert und beim Öffnen wieder gelesen; offene Kommentare bleiben offen."""
    gelesen, _s, _l, pfad = docx_rundlauf(_dokument(True), tmp_path, "g.docx")
    z = zipfile.ZipFile(pfad)
    assert "word/commentsExtended.xml" in z.namelist() and 'done="1"' in z.read("word/commentsExtended.xml").decode()
    assert next(iter(gelesen.kommentare.values())).geloest is True
    offen, _s2, _l2, pfad2 = docx_rundlauf(_dokument(False), tmp_path, "o.docx")
    assert "word/commentsExtended.xml" not in zipfile.ZipFile(pfad2).namelist()
    assert not any(k.geloest for k in offen.kommentare.values())
