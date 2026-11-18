import pytest

from lunivo_writer.dienste.modell_laden import lade_modell
from lunivo_writer.dienste.modell_speichern import speichere_modell
from lunivo_writer.modelle.bericht import DocumentIOError
from lunivo_writer.modelle.seite import PageSettings
from tests.hilfen_dokument import dokument, sitzung


def test_txt_roundtrip_with_umlaute(app, tmp_path):
    p = tmp_path / "a.txt"
    p.write_bytes("Grüße\nzweite Zeile ß€".encode("utf-8"))
    g = lade_modell(str(p))
    assert g.document.text() == "Grüße\nzweite Zeile ß€"
    q = tmp_path / "b.txt"
    speichere_modell(str(q), g.document, g.page)
    assert q.read_bytes() == p.read_bytes()


def test_txt_cp1252_fallback(app, tmp_path):
    p = tmp_path / "c.txt"; p.write_bytes("Käse".encode("cp1252"))
    assert lade_modell(str(p)).document.text() == "Käse"


def test_txt_save_warns_on_data_loss(app, tmp_path):
    s = sitzung()
    s.text_einfuegen("fett", format={"fett": True})
    rep = speichere_modell(str(tmp_path / "x.txt"), s.dokument, PageSettings())
    assert rep and "Formatierung" in rep.warnings[0]


def test_odt_export_is_valid_zip(app, tmp_path):
    import zipfile
    out = tmp_path / "x.odt"
    rep = speichere_modell(str(out), dokument("Hallo ODT"), PageSettings())
    assert not rep.warnings                                   # Lunivo schreibt ODT selbst, mit Seite und Kopf-/Fußzeile
    with zipfile.ZipFile(out) as z:
        assert b"Hallo ODT" in z.read("content.xml")


def test_missing_and_unknown(app, tmp_path):
    with pytest.raises(DocumentIOError):
        lade_modell(str(tmp_path / "nicht-da.docx"))
    p = tmp_path / "x.xyz"; p.write_text("a")
    with pytest.raises(DocumentIOError):
        lade_modell(str(p))


def test_save_to_unwritable_folder(app, tmp_path):
    with pytest.raises(DocumentIOError):
        speichere_modell("/proc/nicht/möglich.docx", dokument("x"), PageSettings())


def test_kennwort_roundtrip(app, tmp_path):
    pytest.importorskip("msoffcrypto")
    from lunivo_writer.modelle.bericht import PasswortNoetig
    d = dokument("Streng geheim äöü")
    p = str(tmp_path / "g.docx")
    speichere_modell(p, d, PageSettings(), {"kennwort": "pw1"})
    with pytest.raises(PasswortNoetig):
        lade_modell(p)
    with pytest.raises(PasswortNoetig) as ei:
        lade_modell(p, "falsch")
    assert ei.value.falsch
    g = lade_modell(p, "pw1")
    assert "Streng geheim äöü" in g.document.text() and g.meta["kennwort"] == "pw1"
    with pytest.raises(DocumentIOError):                         # Webseiten werden nicht geschrieben
        speichere_modell(str(tmp_path / "x.html"), d, PageSettings())


def test_formatverzeichnis_stimmt_mit_dem_ablauf_ueberein():
    """Was gespeichert und geöffnet werden kann, steht im Verzeichnis (und umgekehrt); Paketformate sind als solche gekennzeichnet."""
    from lunivo_writer.dienste import dateiformate as fs, formate
    assert set(fs.SAVE_FILTERS) <= set(formate.speicherbar())
    assert {e for e in formate.speicherbar() if e != ".pdf"} == set(fs.SAVE_FILTERS)
    for e in (".docx", ".odt", ".rtf", ".txt", ".dotx", ".docm", ".fodt"):
        assert formate.finde(e).lesen, e
    assert all(formate.finde(e).paket for e in (".docx", ".dotx", ".docm", ".odt")) and not formate.finde(".rtf").paket
    assert formate.finde(".DOCX").name == "DOCX-Dokument" and formate.finde(".xyz") is None
    assert "| DOCX-Dokument (`.docx`) | ja | ja |" in formate.als_markdown()
