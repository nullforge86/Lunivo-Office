"""ODT und RTF liest und schreibt Lunivo selbst — über das Dokumentenmodell und ohne fremdes Programm im Hintergrund."""
import os
import subprocess
import sys
import time
import zipfile

import docx
import pytest

from lunivo_writer.core.document.dokument import Absatz, Auswahl, Lauf, Position, Tabelle
from lunivo_writer.core.document.formatvorlagen import ueberschriftsebene, wirksames_zeichenformat
from lunivo_writer.dienste import dateiformate
from lunivo_writer.dienste.modell_laden import lade_modell
from lunivo_writer.dienste.modell_speichern import speichere_modell
from lunivo_writer.modelle.bericht import DocumentIOError
from lunivo_writer.modelle.seite import HeaderFooter, PageSettings
from tests.hilfen_dokument import dokument, sitzung


def _beispiel(tmp_path):
    d = docx.Document()
    d.add_heading("Überschrift", 1)
    p = d.add_paragraph("Normaler Text mit "); r = p.add_run("Fett"); r.bold = True
    d.add_paragraph("Punkt", style="List Bullet")
    t = d.add_table(rows=1, cols=2); t.cell(0, 0).text = "A"; t.cell(0, 1).text = "B"
    f = tmp_path / "q.docx"; d.save(f)
    return str(f)


def _laeufe(dok):
    return [(a, x) for a in dok.absaetze() for x in a.inhalte if isinstance(x, Lauf)]


def _finde(dok, text):
    return next((a, x) for a, x in _laeufe(dok) if text in x.text)


@pytest.mark.parametrize("ext", [".odt", ".rtf"])
def test_roundtrip_ohne_umwandler(app, tmp_path, ext):
    g = lade_modell(_beispiel(tmp_path))
    out = str(tmp_path / ("x" + ext))
    rep = speichere_modell(out, g.document, g.page, g.meta)
    assert os.path.getsize(out) > 200 and not rep.warnings          # Speichern in ein anderes Format ohne Hinweisfenster
    back = lade_modell(out)
    txt = back.document.text()
    assert "Überschrift" in txt and "Normaler Text mit Fett" in txt and "Punkt" in txt and "A" in txt and "B" in txt
    assert not back.report.warnings
    a, x = _finde(back.document, "Fett")
    assert wirksames_zeichenformat(back.document, a, x.format).get("fett")
    assert ueberschriftsebene(back.document, next(iter(back.document.absaetze()))) == 1
    assert _finde(back.document, "Punkt")[0].liste_id is not None
    assert any(isinstance(b, Tabelle) for ab in back.document.abschnitte for b in ab.bloecke), "Tabelle fehlt"


@pytest.mark.parametrize("ext", [".odt", ".rtf"])
def test_seite_kopf_und_fusszeile(app, tmp_path, ext):
    page = PageSettings(width_mm=148, height_mm=210, margin_left_mm=20, margin_right_mm=15, margin_top_mm=30, margin_bottom_mm=28)
    page.header = HeaderFooter("Firma Muster", "right")
    page.footer = HeaderFooter("Seite {PAGE} von {PAGES}", "center")
    out = str(tmp_path / ("k" + ext))
    speichere_modell(out, dokument("Inhalt", page), page)
    p = lade_modell(out).page
    assert abs(p.width_mm - 148) < 0.5 and abs(p.height_mm - 210) < 0.5
    assert abs(p.margin_left_mm - 20) < 0.5 and abs(p.margin_right_mm - 15) < 0.5
    assert abs(p.margin_top_mm - 30) < 1 and abs(p.margin_bottom_mm - 28) < 1
    assert p.header.text == "Firma Muster" and p.header.align == "right"
    assert p.footer.text == "Seite {PAGE} von {PAGES}" and p.footer.align == "center"


@pytest.mark.parametrize("ext", [".odt", ".rtf"])
def test_zeichenformat_umlaute_und_liste(app, tmp_path, ext):
    s = sitzung()
    s.text_einfuegen("Rot kursiv äöü ß € 𝄞", format={"kursiv": True, "farbe": "#c00000", "groesse_pt": 16.0})
    s.text_einfuegen("\nNormal\nErstens\nZweitens")
    a = list(s.dokument.absaetze())
    lid = s.liste_anlegen("dezimal")
    s.liste_anwenden(lid, Auswahl(Position(a[2].id, 0), Position(a[3].id, 8)))
    out = str(tmp_path / ("z" + ext))
    speichere_modell(out, s.dokument, PageSettings())
    back = lade_modell(out).document
    absatz, lauf = _finde(back, "Rot kursiv")
    z = wirksames_zeichenformat(back, absatz, lauf.format)
    assert z.get("kursiv") and str(z.get("farbe", "")).lower()[:7] == "#c00000" and round(z.get("groesse_pt") or 0) == 16
    assert "Rot kursiv äöü ß € 𝄞" in back.text()
    erstens, zweitens = _finde(back, "Erstens")[0], _finde(back, "Zweitens")[0]
    assert zweitens.liste_id is not None and zweitens.liste_id == erstens.liste_id
    assert back.listen[zweitens.liste_id].ebenen[0].stil == "dezimal"


def test_odt_paket_ist_gueltig(app, tmp_path):
    out = str(tmp_path / "p.odt")
    speichere_modell(out, dokument("x"), PageSettings())
    with zipfile.ZipFile(out) as z:
        erster = z.infolist()[0]
        assert erster.filename == "mimetype" and erster.compress_type == zipfile.ZIP_STORED
        assert {"content.xml", "styles.xml", "META-INF/manifest.xml"} <= set(z.namelist())
        assert b"styles.xml" in z.read("META-INF/manifest.xml")


def test_fremdes_rtf_lesen(app, tmp_path):
    """Ein RTF, wie es Word schreibt: Codepage, \\u-Zeichen, Felder, Tabelle, Kopfzeile, Fußnote."""
    rtf = (rb"{\rtf1\ansi\ansicpg1252\deff0{\fonttbl{\f0\froman Times New Roman;}{\f1\fswiss Arial;}}"
           rb"{\colortbl;\red255\green0\blue0;}{\stylesheet{\s0 Normal;}{\s1 heading 1;}}"
           rb"{\info{\title Mein Titel}{\author Kay}}\paperw11906\paperh16838\margl1134\margr1134\margt1417\margb1134"
           rb"{\header\pard\qr Kopf\par}{\footer\pard\qc Seite {\field{\*\fldinst PAGE}{\fldrslt 1}}\par}"
           rb"\pard\s1\outlinelevel0\f1\fs32\b Titel\b0\par"
           rb"\pard\plain\f0\fs24 Gr\'fc\'dfe \u8364? und {\cf1 rot}{\footnote\pard Fu\'dfnote}.\par"
           rb"{\field{\*\fldinst HYPERLINK \"https://x\"}{\fldrslt Verweis}}\par"
           rb"\trowd\cellx3000\cellx6000\pard\intbl A1\cell B1\cell\row"
           rb"\pard Ende\par}")
    p = tmp_path / "word.rtf"; p.write_bytes(rtf)
    g = lade_modell(str(p))
    t = g.document.text()
    assert "Titel" in t and "Grüße € und rot." in t and "Verweis" in t and "A1" in t and "B1" in t and "Ende" in t
    assert any(n.text == "Fußnote" for n in g.document.noten["f"].values()) or any("Endnoten" in w for w in g.report.warnings)
    a, x = _finde(g.document, "rot")
    assert str(wirksames_zeichenformat(g.document, a, x.format).get("farbe", "")).lower()[:7] == "#ff0000"
    assert ueberschriftsebene(g.document, next(iter(g.document.absaetze()))) == 1
    assert g.page.header.text == "Kopf" and g.page.header.align == "right" and g.page.footer.text == "Seite {PAGE}"
    assert abs(g.page.margin_left_mm - 20) < 0.1 and g.meta["title"] == "Mein Titel"


def test_doc_wird_klar_abgelehnt(app, tmp_path):
    p = tmp_path / "alt.doc"; p.write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\0" * 600)
    with pytest.raises(DocumentIOError, match="nicht mehr unterstützt.*DOCX"):
        lade_modell(str(p))
    assert ".doc" not in dateiformate.SAVE_FILTERS


def test_dotx_vorlage_oeffnen(app, tmp_path):
    q = _beispiel(tmp_path)
    ziel = tmp_path / "vorlage.dotx"
    with zipfile.ZipFile(q) as z, zipfile.ZipFile(ziel, "w") as aus:
        for i in z.infolist():
            daten = z.read(i.filename)
            if i.filename == "[Content_Types].xml":
                daten = daten.replace(b"wordprocessingml.document.main+xml", b"wordprocessingml.template.main+xml")
            aus.writestr(i, daten)
    assert "Normaler Text mit Fett" in lade_modell(str(ziel)).document.text()


def test_kaputte_dateien(app, tmp_path):
    for name, inhalt in (("kaputt.odt", b"kein odt"), ("leer.odt", b"PK\x05\x06" + b"\0" * 18), ("kein.rtf", b"Hallo"),
                         ("kaputt.fodt", b"<?xml version='1.0'?><kaputt")):
        p = tmp_path / name; p.write_bytes(inhalt)
        with pytest.raises(DocumentIOError):
            lade_modell(str(p))


def test_kein_fremdes_programm_beim_speichern_und_oeffnen(app, tmp_path, monkeypatch):
    """Weder beim Speichern noch beim Öffnen startet Lunivo einen anderen Prozess."""
    def verboten(*a, **k):
        raise AssertionError(f"Fremdes Programm gestartet: {a[:1]}")
    monkeypatch.setattr(subprocess, "Popen", verboten)
    monkeypatch.setattr(subprocess, "run", verboten)
    for ext in (".odt", ".rtf", ".docx", ".txt"):
        out = str(tmp_path / ("f" + ext))
        speichere_modell(out, dokument("ohne Umweg"), PageSettings())
        assert "ohne Umweg" in lade_modell(out).document.text()


@pytest.mark.parametrize("ext", [".odt", ".rtf"])
def test_schnell_auch_bei_grossem_dokument(app, tmp_path, ext):
    s = sitzung("\n".join(f"Absatz {i} mit etwas Text, fett" for i in range(3000)))
    for a in s.dokument.absaetze():
        n = a.laenge
        s.zeichenformat_anwenden({"fett": True}, Auswahl(Position(a.id, n - 4), Position(a.id, n)))
    out = str(tmp_path / ("gross" + ext))
    t0 = time.monotonic()
    speichere_modell(out, s.dokument, PageSettings())
    gespeichert = time.monotonic() - t0
    back = lade_modell(out)
    gesamt = time.monotonic() - t0
    assert "Absatz 2999" in back.document.text()
    assert gespeichert < 5 and gesamt < 15, (gespeichert, gesamt)
    print(f"{ext}: speichern {gespeichert:.2f} s, mit Öffnen {gesamt:.2f} s", file=sys.stderr)


def test_odt_freie_bilder_kopf_fuss(app, tmp_path):
    """Bilder in Kopf- und Fußzeile gehen in ODT mit, ohne Hinweisfenster."""
    logo = bytes.fromhex("89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6360f8cfc0f01f0005000201a3e2f1650000000049454e44ae426082")
    p = PageSettings(); p.header = HeaderFooter("Kopf", "center")
    p.bilder = [{"ort": "kopf", "bild": logo, "b": 60, "h": 60, "bh": "seite", "bv": "seite", "ah": "right", "av": "", "xh": 0, "yv": 20},
                {"ort": "fuss", "bild": logo, "b": 30, "h": 30, "bh": "rand", "bv": "seite", "ah": "center", "av": "bottom", "xh": 0, "yv": 0}]
    out = str(tmp_path / "bilder.odt")
    assert not speichere_modell(out, dokument("Brief", p), p, {}).warnings
    back = lade_modell(out)
    assert not back.report.warnings
    orte = sorted((a["ort"], a["ah"], a["av"]) for a in back.page.bilder)
    assert orte == [("fuss", "center", "bottom"), ("kopf", "right", "")]
    assert all(bytes(a["bild"]) == logo for a in back.page.bilder)
