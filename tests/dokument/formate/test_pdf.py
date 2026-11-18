"""PDF-Ausgabe des Dokumentenmodells: Seitenzahl, Kopf- und Fußzeile, Seitengröße, Querformat, Schriftgröße, Seitenfarbe und Wasserzeichen."""
import pypdf

from lunivo_writer.modelle.seite import HeaderFooter, PageSettings
from tests.hilfen_dokument import als_pdf, dokument, seitenzahl, sitzung


def norm(s):
    return " ".join(s.split())


def test_pdf_seiten_kopf_und_fusszeile(app, tmp_path):
    page = PageSettings(); page.header = HeaderFooter("Kopf", "center"); page.footer = HeaderFooter("Seite {PAGE} von {PAGES}", "right")
    d = sitzung("\n".join(f"Zeile {i} " + "Wort " * 12 for i in range(200)), page).dokument
    n = seitenzahl(d)
    assert n >= 3
    out = tmp_path / "t.pdf"
    assert als_pdf(d, out, "T") == n
    r = pypdf.PdfReader(str(out))
    assert len(r.pages) == n
    t0 = norm(r.pages[0].extract_text())
    assert "Zeile 0" in t0 and "Kopf" in t0 and f"Seite 1 von {n}" in t0
    assert f"Seite {n} von {n}" in norm(r.pages[-1].extract_text())
    box = r.pages[0].mediabox
    assert abs(float(box.width) / 72 * 25.4 - 210) < 1 and abs(float(box.height) / 72 * 25.4 - 297) < 1


def test_pdf_querformat_und_seitenumbruch(app, tmp_path):
    page = PageSettings(); page.set_orientation(True)
    s = sitzung("Eins\nZwei", page)
    s.absatzformat_anwenden({"seitenumbruch_vor": True}, absatz_ids=[list(s.dokument.absaetze())[1].id])
    d = s.dokument
    out = tmp_path / "l.pdf"
    assert als_pdf(d, out) == 2
    r = pypdf.PdfReader(str(out))
    assert float(r.pages[0].mediabox.width) > float(r.pages[0].mediabox.height)
    assert "Eins" in r.pages[0].extract_text() and "Zwei" in r.pages[1].extract_text()


def test_schriftgroesse_im_pdf(app, tmp_path):
    """12 pt im Dokument müssen im PDF als 12 pt ankommen."""
    s = sitzung("")
    s.text_einfuegen("Größentest", format={"groesse_pt": 12.0})
    out = tmp_path / "s.pdf"
    als_pdf(s.dokument, out)
    sizes = []

    def visitor(text, cm, tm, fd, fs):
        if "Größentest" in text:
            sizes.append(fs * abs(tm[3]) * abs(cm[3]) if cm else fs)
    pypdf.PdfReader(str(out)).pages[0].extract_text(visitor_text=visitor)
    assert sizes and abs(sizes[0] - 12) < 0.8, sizes


def test_pdf_mit_seitenfarbe_und_wasserzeichen(app, tmp_path):
    pg = PageSettings(color="#ffeecc", watermark={"text": "ENTWURF", "farbe": "#c0c0c0", "winkel": -45, "groesse_pt": 80},
                      border={"art": "einfach", "farbe": "#000000", "breite_pt": 1.0, "abstand_mm": 8.0})
    out = tmp_path / "w.pdf"
    als_pdf(dokument("Inhalt", pg), out, "t")
    txt = pypdf.PdfReader(str(out)).pages[0].extract_text()
    assert "Inhalt" in txt and "ENTWURF" in " ".join(txt.split())
