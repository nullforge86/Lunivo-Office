"""Grenzen für fremde Dokumente: ZIP-Bomben, zu viele Teile, DTD/Entitäten, tiefe Schachtelung, kaputte Pakete, große Bilder."""
import zipfile

import pytest

from lunivo_writer.models.report import DocumentIOError
from lunivo_writer.services import import_grenzen as G
from lunivo_writer.services.import_grenzen import MB


def paket(pfad, teile, stufe=zipfile.ZIP_DEFLATED):
    with zipfile.ZipFile(pfad, "w", stufe) as z:
        for n, d in teile.items():
            z.writestr(n, d)
    return str(pfad)


@pytest.fixture
def klein(monkeypatch):
    """Grenzen herabsetzen, statt riesige Dateien zu bauen."""
    g = G.Grenzen(entpackt_gesamt=2 * MB, xml_eintrag=1 * MB, bild_eintrag=1 * MB, verhaeltnis_ab=MB // 2, eintraege=20)
    monkeypatch.setattr(G, "GRENZEN", g)
    return g


def test_gutes_paket_wird_angenommen(tmp_path, klein):
    G.pruefe_paket(paket(tmp_path / "a.docx", {"word/document.xml": "<a/>", "x.png": b"\x89PNG" * 10}), "DOCX")


def test_zip_bombe_wird_abgelehnt(tmp_path, klein):
    p = paket(tmp_path / "b.docx", {"word/document.xml": b"0" * (3 * MB)})
    with pytest.raises(DocumentIOError, match="zu groß"):
        G.pruefe_paket(p, "DOCX")


def test_summe_mehrerer_teile_wird_gezaehlt(tmp_path, klein):
    p = paket(tmp_path / "c.docx", {f"m{i}.bin": b"1" * (700 * 1024) for i in range(4)}, zipfile.ZIP_STORED)
    with pytest.raises(DocumentIOError, match="entpackt größer"):
        G.pruefe_paket(p, "DOCX")


def test_kompressionsverhaeltnis(tmp_path, klein):
    p = paket(tmp_path / "d.docx", {"m.bin": b"\0" * (1 * MB)})
    with pytest.raises(DocumentIOError, match="stark komprimiert"):
        G.pruefe_paket(p, "DOCX")


def test_zu_viele_teile(tmp_path, klein):
    p = paket(tmp_path / "e.docx", {f"t{i}.txt": "x" for i in range(30)})
    with pytest.raises(DocumentIOError, match="Teile"):
        G.pruefe_paket(p, "DOCX")


def test_dtd_und_entitaeten_im_paket(tmp_path, klein):
    xml = '<?xml version="1.0"?><!DOCTYPE a [<!ENTITY x "y">]><a>&x;</a>'
    with pytest.raises(DocumentIOError, match="DTD"):
        G.pruefe_paket(paket(tmp_path / "f.docx", {"word/document.xml": xml}), "DOCX")


def test_kein_zip_und_abgeschnittenes_zip(tmp_path, klein):
    kaputt = tmp_path / "g.docx"; kaputt.write_bytes(b"PK\x03\x04 nur Muell")
    with pytest.raises(DocumentIOError, match="kein gültiges DOCX"):
        G.pruefe_paket(str(kaputt), "DOCX")
    ganz = paket(tmp_path / "h.docx", {"word/document.xml": "<a>" + "x" * 5000 + "</a>"})
    roh = open(ganz, "rb").read()
    mitte = tmp_path / "i.docx"; mitte.write_bytes(roh[:len(roh) // 2])
    with pytest.raises(DocumentIOError):
        G.pruefe_paket(str(mitte), "DOCX")


def test_dateigroesse(tmp_path, monkeypatch):
    f = tmp_path / "j.rtf"; f.write_bytes(b"x" * 2000)
    monkeypatch.setattr(G, "GRENZEN", G.Grenzen(text_bytes=1000))
    with pytest.raises(DocumentIOError, match="größer als die zulässigen"):
        G.pruefe_dateigroesse(str(f), "RTF")


def test_sicheres_xml_lehnt_entitaeten_und_tiefe_ab(monkeypatch):
    assert G.sicheres_xml(b"<a><b/></a>").tag == "a"
    with pytest.raises(DocumentIOError, match="DTD"):
        G.sicheres_xml(b'<?xml version="1.0"?><!DOCTYPE a [<!ENTITY x "y">]><a>&x;</a>')
    with pytest.raises(DocumentIOError, match="fehlerhaftes XML"):
        G.sicheres_xml(b"<a><b></a>")
    monkeypatch.setattr(G, "GRENZEN", G.Grenzen(xml_tiefe=50))
    with pytest.raises(DocumentIOError, match="tief verschachtelt"):
        G.sicheres_xml(b"<a>" * 60 + b"</a>" * 60)


def test_leser_pruefen_vor_dem_verarbeiten(tmp_path, klein, monkeypatch):
    """Bei Überschreitung beginnt weder python-docx noch der ODT-Leser mit der Arbeit."""
    import docx
    from lunivo_writer.services import docx_reader, odt_reader
    monkeypatch.setattr(docx, "Document", lambda *_a, **_k: pytest.fail("Dokument wurde trotz Überschreitung verarbeitet"))
    bombe = paket(tmp_path / "k.docx", {"word/document.xml": b"0" * (3 * MB)})
    with pytest.raises(DocumentIOError, match="zu groß"):
        docx_reader.read_docx(bombe)
    odt = paket(tmp_path / "l.odt", {"content.xml": b"0" * (3 * MB)})
    with pytest.raises(DocumentIOError, match="zu groß"):
        odt_reader.read_odt(odt)


def test_odt_mit_entitaet_wird_abgelehnt(tmp_path):
    from lunivo_writer.services import odt_reader
    xml = '<?xml version="1.0"?><!DOCTYPE a [<!ENTITY x "y">]><office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">&x;</office:document-content>'
    with pytest.raises(DocumentIOError, match="DTD"):
        odt_reader.read_odt(paket(tmp_path / "m.odt", {"content.xml": xml, "META-INF/manifest.xml": "<a/>"}))


def test_zu_grosses_bild_wird_nicht_dekodiert(app, monkeypatch):
    from PySide6.QtCore import QBuffer, QByteArray, QIODevice
    from PySide6.QtGui import QImage
    from lunivo_writer.editor.objekte import freie_bilder
    puffer = QByteArray(); b = QBuffer(puffer); b.open(QIODevice.WriteOnly)
    QImage(40, 40, QImage.Format_RGB32).save(b, "PNG")
    blob = bytes(puffer)
    assert not freie_bilder.bild_aus_daten(blob).isNull()
    monkeypatch.setattr(freie_bilder, "MAX_BILDPUNKTE", 100)
    assert freie_bilder.bild_aus_daten(blob).isNull()
