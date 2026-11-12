"""Testkorpus für DOCX: selbst erzeugte Dokumente (kein fremdes oder geschütztes Material, keine Personendaten) und der Roundtrip-Vergleich.

Verwendung:  python werkzeuge/pruefungen/docx_korpus.py [Ausgabedatei.md]   → schreibt den Bericht (Markdown) über Verluste und Abweichungen.
Die Tests (tests/dokument/formate/test_docx_korpus.py) benutzen dieselben Bausteine.

Ehrliche Grenze: Alle Dokumente stammen aus python-docx und eigenem XML, nicht aus Word, LibreOffice oder Google Docs. Dokumente aus
anderen Programmen müssen vom Eigentümer beigesteuert werden (Ordner ``tests/korpus_extern/``, wird automatisch mitgeprüft, wenn er existiert).
"""
from __future__ import annotations

import io
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import docx  # noqa: E402
from docx.enum.style import WD_STYLE_TYPE  # noqa: E402
from docx.opc.constants import RELATIONSHIP_TYPE as RT  # noqa: E402
from docx.opc.packuri import PackURI  # noqa: E402
from docx.opc.part import Part  # noqa: E402
from docx.oxml import OxmlElement, parse_xml  # noqa: E402
from docx.oxml.ns import nsdecls, qn  # noqa: E402
from docx.shared import Mm, Pt, RGBColor  # noqa: E402

W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def _png() -> io.BytesIO:
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QColor, QImage
    img = QImage(60, 30, QImage.Format_RGB32)
    img.fill(QColor("steelblue"))
    b = QBuffer(); b.open(QIODevice.WriteOnly); img.save(b, "PNG")
    return io.BytesIO(bytes(b.data()))


def _feld(p, anweisung: str, ergebnis: str) -> None:
    """Komplexes Feld (begin – instrText – separate – Ergebnis – end) an einen Absatz hängen."""
    def lauf(*kinder):
        r = OxmlElement("w:r")
        for k in kinder:
            r.append(k)
        p._p.append(r)

    def fc(art):
        e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), art); return e
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = f" {anweisung} "
    t = OxmlElement("w:t"); t.text = ergebnis
    lauf(fc("begin")); lauf(it); lauf(fc("separate")); lauf(t); lauf(fc("end"))


def tabelle_verbunden(d):
    d.add_paragraph("Tabelle mit verbundenen Zellen")
    t = d.add_table(rows=3, cols=3); t.style = "Table Grid"
    for i in range(3):
        for j in range(3):
            t.cell(i, j).text = f"z{i}{j}"
    t.cell(0, 0).merge(t.cell(0, 1))
    t.cell(1, 2).merge(t.cell(2, 2))


def kopf_fuss_abschnitte(d):
    d.sections[0].header.paragraphs[0].text = "Kopf eins"
    d.sections[0].footer.paragraphs[0].text = "Fuß eins"
    d.add_paragraph("Abschnitt eins")
    s2 = d.add_section()
    s2.header.is_linked_to_previous = False
    s2.header.paragraphs[0].text = "Kopf zwei"
    s2.orientation = 1
    s2.page_width, s2.page_height = s2.page_height, s2.page_width
    d.add_paragraph("Abschnitt zwei, quer")


def schwebendes_bild(d):
    d.add_paragraph("Text vor dem Bild, das im Text schwebt.")
    p = d.add_paragraph()
    p.add_run().add_picture(_png(), width=Mm(30))
    inline = p._p.xpath(".//wp:inline")[0]
    anker = parse_xml(
        '<wp:anchor xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" distT="0" distB="0" distL="114300" distR="114300" '
        'simplePos="0" relativeHeight="1" behindDoc="0" locked="0" layoutInCell="1" allowOverlap="1"><wp:simplePos x="0" y="0"/>'
        '<wp:positionH relativeFrom="column"><wp:posOffset>1000000</wp:posOffset></wp:positionH>'
        '<wp:positionV relativeFrom="paragraph"><wp:posOffset>100000</wp:posOffset></wp:positionV>'
        '<wp:wrapSquare wrapText="bothSides"/></wp:anchor>')
    for kind in list(inline):
        if kind.tag.endswith("}extent") or kind.tag.endswith("}docPr") or kind.tag.endswith("}graphic"):
            anker.insert(2 if kind.tag.endswith("}extent") else len(anker), kind)
    ext = anker.find("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent")
    if ext is not None:
        anker.remove(ext); anker.insert(3, ext)
    inline.getparent().replace(inline, anker)
    d.add_paragraph("Text nach dem Bild.")


def kommentare(d):
    p = d.add_paragraph("Ein Satz mit Kommentar am Wort.")
    d.add_comment(p.runs[0], text="Bitte prüfen.", author="Prüfer", initials="PR")


def fussnoten(d):
    p = d.add_paragraph("Satz mit Fußnote")
    inhalt = (f'<w:footnotes {W}><w:footnote w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:footnote>'
              f'<w:footnote w:type="continuationSeparator" w:id="0"><w:p><w:r><w:continuationSeparator/></w:r></w:p></w:footnote>'
              f'<w:footnote w:id="1"><w:p><w:r><w:footnoteRef/></w:r><w:r><w:t xml:space="preserve"> Text der Fußnote.</w:t></w:r></w:p></w:footnote></w:footnotes>')
    teil = Part(PackURI("/word/footnotes.xml"), "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml",
                inhalt.encode("utf-8"), d.part.package)
    d.part.relate_to(teil, RT.FOOTNOTES)
    r = OxmlElement("w:r"); ref = OxmlElement("w:footnoteReference"); ref.set(qn("w:id"), "1"); r.append(ref); p._p.append(r)
    p.add_run(" und weiter.")


def inhaltsverzeichnis_und_verweise(d):
    d.add_paragraph("Inhalt")
    toc = d.add_paragraph(); _feld(toc, 'TOC \\o "1-3" \\h', "Kapitel 1 ... 1")
    d.add_heading("Kapitel 1", 1)
    p = d.add_paragraph("Siehe ")
    lesezeichen = OxmlElement("w:bookmarkStart"); lesezeichen.set(qn("w:id"), "7"); lesezeichen.set(qn("w:name"), "ziel")
    ende = OxmlElement("w:bookmarkEnd"); ende.set(qn("w:id"), "7")
    ziel = d.add_paragraph(); ziel._p.append(lesezeichen); ziel.add_run("Zielstelle"); ziel._p.append(ende)
    _feld(p, "REF ziel \\h", "Zielstelle")
    seite = d.add_paragraph("Seite "); _feld(seite, "PAGE", "1")


def stile_vererbung(d):
    basis = d.styles.add_style("Basis Lunivo", WD_STYLE_TYPE.PARAGRAPH)
    basis.font.name = "DejaVu Serif"; basis.font.size = Pt(13); basis.font.bold = True
    abgeleitet = d.styles.add_style("Abgeleitet Lunivo", WD_STYLE_TYPE.PARAGRAPH)
    abgeleitet.base_style = basis; abgeleitet.font.italic = True; abgeleitet.font.size = Pt(15)
    d.add_paragraph("Absatz in der Basisvorlage", style=basis)
    p = d.add_paragraph("Abgeleitet mit ", style=abgeleitet)
    r = p.add_run("eigener Farbe"); r.font.color.rgb = RGBColor(0, 128, 0)


def schriften_und_sprachen(d):
    p = d.add_paragraph()
    for text, schrift, sprache in (("Deutsch ", "DejaVu Sans", "de-DE"), ("English ", "DejaVu Serif", "en-US"), ("Français ", "DejaVu Sans Mono", "fr-FR")):
        r = p.add_run(text); r.font.name = schrift
        lang = OxmlElement("w:lang"); lang.set(qn("w:val"), sprache); r._r.get_or_add_rPr().append(lang)


def ungewoehnlich(d):
    d.add_paragraph("Verschachtelt:")
    aussen = d.add_table(rows=1, cols=2); aussen.style = "Table Grid"
    aussen.cell(0, 0).text = "außen"
    innen = aussen.cell(0, 1).add_table(rows=2, cols=2)
    innen.cell(1, 1).text = "innen"
    d.add_paragraph("Rechts nach links: שלום مرحبا")
    d.add_paragraph("x" * 20000)
    d.add_paragraph("")
    d.add_paragraph("Zeichen: ​­   Ende")


KORPUS = {
    "tabelle_verbunden": tabelle_verbunden,
    "kopf_fuss_abschnitte": kopf_fuss_abschnitte,
    "schwebendes_bild": schwebendes_bild,
    "kommentare": kommentare,
    "fussnoten": fussnoten,
    "inhaltsverzeichnis_und_verweise": inhaltsverzeichnis_und_verweise,
    "stile_vererbung": stile_vererbung,
    "schriften_und_sprachen": schriften_und_sprachen,
    "ungewoehnlich": ungewoehnlich,
}


def bauen(name: str, ordner: str) -> str:
    d = docx.Document()
    KORPUS[name](d)
    pfad = os.path.join(ordner, name + ".docx")
    d.save(pfad)
    return pfad


def externe(ordner: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests", "korpus_extern")) -> dict[str, str]:
    """Vom Eigentümer beigesteuerte Dokumente aus anderen Programmen (nur wenn der Ordner existiert)."""
    if not os.path.isdir(ordner):
        return {}
    return {os.path.splitext(f)[0]: os.path.join(ordner, f) for f in sorted(os.listdir(ordner)) if f.lower().endswith(".docx")}


# ---- Vergleich -----------------------------------------------------------------------------------------------------------------
def abbild(qdoc) -> dict:
    """Was beim Roundtrip erhalten bleiben soll: Text, Zeichenformat-Läufe, Tabellenstruktur, Bilder."""
    from PySide6.QtGui import QTextFrame, QTextTable
    laeufe, bilder, tabellen = [], 0, []
    b = qdoc.begin()
    while b.isValid():
        for fr in b.textFormats() if hasattr(b, "textFormats") else []:
            pass
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid():
                cf = f.charFormat()
                if cf.isImageFormat():
                    bilder += 1
                elif f.text().strip():
                    laeufe.append((f.text(), cf.fontFamilies()[0] if cf.fontFamilies() else cf.fontFamily(), round(cf.fontPointSize()), cf.fontWeight() >= 600,
                                   cf.fontItalic()))
            it += 1
        b = b.next()
    def alle_tabellen(frame):
        for kind in frame.childFrames():
            if isinstance(kind, QTextTable):
                spans = sorted((kind.cellAt(r, c).row(), kind.cellAt(r, c).column(), kind.cellAt(r, c).rowSpan(), kind.cellAt(r, c).columnSpan())
                               for r in range(kind.rows()) for c in range(kind.columns()))
                tabellen.append((kind.rows(), kind.columns(), tuple(sorted(set(spans)))))
            alle_tabellen(kind)
    alle_tabellen(qdoc.rootFrame())
    # Leere Absätze zählen nicht: Word verlangt einen Absatz am Ende einer Zelle, auch nach einer verschachtelten Tabelle.
    text = "\n".join(z for z in qdoc.toPlainText().split("\n") if z.strip())
    return {"text": text, "laeufe": laeufe, "bilder": bilder, "tabellen": tabellen}


def roundtrip(pfad: str) -> dict:
    """Einlesen → ohne Änderung speichern → erneut einlesen. → Ergebnis mit beiden Abbildern, den Berichten und den Abweichungen."""
    from lunivo_writer.dienste.docx_leser import read_docx
    from lunivo_writer.dienste.docx_schreiber import write_docx
    qd1, page1, meta1, rep1 = read_docx(pfad)
    with tempfile.TemporaryDirectory(prefix="korpus-") as tmp:
        aus = os.path.join(tmp, "zurueck.docx")
        rep_w = write_docx(aus, qd1, page1, meta1)
        qd2, page2, meta2, rep2 = read_docx(aus)
    a, b = abbild(qd1), abbild(qd2)
    abw = [k for k in a if a[k] != b[k]]
    kopf = (page1.header.text, page1.footer.text), (page2.header.text, page2.footer.text)
    if kopf[0] != kopf[1]:
        abw.append("kopf_fuss")
    return {"erst": a, "zweit": b, "bericht_lesen": list(rep1.warnings), "bericht_schreiben": list(getattr(rep_w, "warnings", []) or []),
            "bericht_zweit": list(rep2.warnings), "abweichungen": abw}


def bericht(pfad_aus: str) -> None:
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])
    zeilen = ["# DOCX-Korpus: Roundtrip-Bericht", "",
              "Jedes Dokument: einlesen → ohne Änderung speichern → erneut einlesen; verglichen werden Text, Zeichenformat-Läufe, Tabellenstruktur, Bilder, Kopf-/Fußzeile.",
              "Alle Dokumente sind selbst erzeugt (python-docx und eigenes XML), keine aus Word, LibreOffice oder Google Docs — siehe Grenze in `werkzeuge/pruefungen/docx_korpus.py`.", "",
              "| Dokument | Abweichungen nach Roundtrip | Hinweise beim Lesen |", "|---|---|---|"]
    with tempfile.TemporaryDirectory(prefix="korpus-") as tmp:
        quellen = {n: bauen(n, tmp) for n in KORPUS}
        quellen.update({"extern/" + n: p for n, p in externe().items()})
        for n, p in quellen.items():
            try:
                r = roundtrip(p)
                zeilen.append(f"| `{n}` | {', '.join(r['abweichungen']) or 'keine'} | {'; '.join(r['bericht_lesen']) or '–'} |")
            except Exception as e:                                  # im Bericht sichtbar machen, nicht verschlucken
                zeilen.append(f"| `{n}` | **Fehler: {type(e).__name__}: {str(e)[:80]}** | – |")
    with open(pfad_aus, "w", encoding="utf-8") as fh:
        fh.write("\n".join(zeilen) + "\n")


if __name__ == "__main__":
    bericht(sys.argv[1] if len(sys.argv) > 1 else "dokumentation/berichte/docx-korpus-bericht.md")
    print("Bericht geschrieben.")
