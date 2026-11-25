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


_DRAW = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
         'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"')


def _wps(nummer: int, textfeld: bool, text: str, fuell: str | None, linie: str | None, anker: bool, geometrie: str = "rect") -> str:
    """Eine Zeichnung mit ``wps:wsp`` (Textfeld oder Form), im Text oder verankert."""
    cx, cy = 2160000, 720000
    fuellung = f'<a:solidFill><a:srgbClr val="{fuell}"/></a:solidFill>' if fuell else "<a:noFill/>"
    kontur = f'<a:ln w="19050"><a:solidFill><a:srgbClr val="{linie}"/></a:solidFill></a:ln>' if linie else "<a:ln><a:noFill/></a:ln>"
    inhalt = (f'<wps:txbx><w:txbxContent><w:p><w:r><w:rPr><w:sz w:val="22"/></w:rPr><w:t>{text}</w:t></w:r></w:p></w:txbxContent></wps:txbx>' if text else "")
    figur = (f'<a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"><wps:wsp><wps:cNvSpPr{" txBox=\"1\"" if textfeld else ""}/>'
             f'<wps:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="{geometrie}"><a:avLst/></a:prstGeom>{fuellung}{kontur}</wps:spPr>'
             f'{inhalt}<wps:bodyPr/></wps:wsp></a:graphicData></a:graphic>')
    kopf = f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
    if anker:
        huelle = (f'<wp:anchor distT="0" distB="0" distL="114300" distR="114300" simplePos="0" relativeHeight="{nummer}" behindDoc="0" locked="0" layoutInCell="1" allowOverlap="1">'
                  f'<wp:simplePos x="0" y="0"/><wp:positionH relativeFrom="column"><wp:posOffset>1500000</wp:posOffset></wp:positionH>'
                  f'<wp:positionV relativeFrom="paragraph"><wp:posOffset>200000</wp:posOffset></wp:positionV>{kopf}<wp:wrapSquare wrapText="bothSides"/>'
                  f'<wp:docPr id="{nummer}" name="Objekt {nummer}"/><wp:cNvGraphicFramePr/>{figur}</wp:anchor>')
    else:
        huelle = f'<wp:inline distT="0" distB="0" distL="0" distR="0">{kopf}<wp:docPr id="{nummer}" name="Objekt {nummer}"/><wp:cNvGraphicFramePr/>{figur}</wp:inline>'
    return f'<w:drawing {_DRAW}>{huelle}</w:drawing>'


def formen_und_textfelder(d):
    d.add_paragraph("Textfeld im Text, danach eine Form, dann ein verankertes Textfeld.")
    p = d.add_paragraph("Zeile mit Textfeld: ")
    p.add_run()._r.append(parse_xml(_wps(11, True, "Text im Textfeld", None, "1F3864", False)))
    q = d.add_paragraph("Zeile mit Ellipse: ")
    q.add_run()._r.append(parse_xml(_wps(12, False, "", "F4A259", "9C4F0A", False, "ellipse")))
    r = d.add_paragraph("Absatz mit verankertem Textfeld, das der Text umfließt. " * 6)
    r.add_run()._r.append(parse_xml(_wps(13, True, "Verankert", "FFF3BF", "E67700", True)))


def seitenrahmen_und_wasserzeichen(d):
    d.add_paragraph("Seite mit Rahmen und Wasserzeichen im Kopf.")
    sp = d.sections[0]._sectPr
    rahmen = parse_xml(f'<w:pgBorders {W} w:offsetFrom="page">' + "".join(f'<w:{k} w:val="single" w:sz="12" w:space="24" w:color="1F3864"/>' for k in ("top", "left", "bottom", "right")) + "</w:pgBorders>")
    sp.insert_element_before(rahmen, "w:lnNumType", "w:pgNumType", "w:cols", "w:formProt", "w:vAlign", "w:noEndnote", "w:titlePg", "w:textDirection", "w:bidi", "w:rtlGutter", "w:docGrid")
    kopf = d.sections[0].header
    kopf.is_linked_to_previous = False
    lauf = parse_xml(f'<w:r {W} xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office"><w:pict>'
                     '<v:shape id="PowerPlusWaterMarkObject1" o:spid="_x0000_s2049" type="#_x0000_t136" style="position:absolute;width:412pt;height:80pt;rotation:315;z-index:-251658752;'
                     'mso-position-horizontal:center;mso-position-horizontal-relative:margin;mso-position-vertical:center;mso-position-vertical-relative:margin" fillcolor="silver" stroked="f">'
                     '<v:fill opacity=".5"/><v:textpath style="font-family:&quot;Calibri&quot;;font-size:1pt" string="ENTWURF"/></v:shape></w:pict></w:r>')
    kopf.paragraphs[0]._p.append(lauf)


def formulare_und_steuerelemente(d):
    d.add_paragraph("Inhaltssteuerelemente:")
    p = d.add_paragraph("Name: ")
    p._p.append(parse_xml(f'<w:sdt {W}><w:sdtPr><w:alias w:val="Name"/><w:tag w:val="name"/><w:text/></w:sdtPr><w:sdtContent><w:r><w:t>Max Muster</w:t></w:r></w:sdtContent></w:sdt>'))
    d.element.body.insert(len(d.element.body) - 1, parse_xml(
        f'<w:sdt {W}><w:sdtPr><w:alias w:val="Block"/><w:tag w:val="block"/></w:sdtPr><w:sdtContent><w:p><w:r><w:t>Absatz im Steuerelement</w:t></w:r></w:p>'
        '<w:p><w:r><w:t>Zweiter Absatz im Steuerelement</w:t></w:r></w:p></w:sdtContent></w:sdt>'))


def absatzrahmen_und_ruhende_eigenschaften(d):
    p = d.add_paragraph("Absatz mit Rahmen")
    p._p.get_or_add_pPr().append(parse_xml(f'<w:pBdr {W}>' + "".join(f'<w:{k} w:val="single" w:sz="8" w:space="4" w:color="000000"/>' for k in ("top", "left", "bottom", "right")) + "</w:pBdr>"))
    q = d.add_paragraph("Absatz im Textrahmen")
    q._p.get_or_add_pPr().insert(0, parse_xml(f'<w:framePr {W} w:w="3000" w:hSpace="180" w:wrap="around" w:vAnchor="text" w:hAnchor="page" w:x="1000" w:y="1"/>'))
    r = d.add_paragraph("Absatz mit Unbekanntem: zusammenhalten und mit Folgeabsatz")
    r.paragraph_format.keep_with_next = True
    r.paragraph_format.keep_together = True
    lauf = r.add_run(" gesperrt")
    lauf._r.get_or_add_rPr().append(parse_xml(f'<w:spacing {W} w:val="40"/>'))


def zeichen_und_tabellenvorlagen(d):
    zv = d.styles.add_style("Betont Lunivo", WD_STYLE_TYPE.CHARACTER)
    zv.font.bold = True
    zv.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
    p = d.add_paragraph("Text mit ")
    r = p.add_run("Zeichenvorlage")
    r.style = zv
    tv = d.styles.add_style("Tabelle Lunivo", WD_STYLE_TYPE.TABLE)
    tv.base_style = d.styles["Normal Table"]
    tab = d.add_table(rows=2, cols=2)
    tab.style = tv
    tab.cell(0, 0).text = "a"
    tab.cell(1, 1).text = "b"


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


# Dokumente für den nativen Leser und Schreiber (``docx_dokument_leser``/``docx_modell_schreiber``) und das Vergleichssystem (``dokument_vergleich.py``). Sie stehen nicht in
# ``KORPUS``: Dokumente mit Formen, Rahmen, Wasserzeichen und Steuerelementen; sie laufen über denselben Rundlauf des Dokumentenmodells.
KORPUS_NATIV = {
    "formen_und_textfelder": formen_und_textfelder,
    "seitenrahmen_und_wasserzeichen": seitenrahmen_und_wasserzeichen,
    "formulare_und_steuerelemente": formulare_und_steuerelemente,
    "absatzrahmen_und_ruhende_eigenschaften": absatzrahmen_und_ruhende_eigenschaften,
    "zeichen_und_tabellenvorlagen": zeichen_und_tabellenvorlagen,
}


def bauen(name: str, ordner: str) -> str:
    d = docx.Document()
    (KORPUS.get(name) or KORPUS_NATIV[name])(d)
    pfad = os.path.join(ordner, name + ".docx")
    d.save(pfad)
    return pfad


def externe(ordner: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests", "korpus_extern")) -> dict[str, str]:
    """Vom Eigentümer beigesteuerte Dokumente aus anderen Programmen (nur wenn der Ordner existiert)."""
    if not os.path.isdir(ordner):
        return {}
    return {os.path.splitext(f)[0]: os.path.join(ordner, f) for f in sorted(os.listdir(ordner)) if f.lower().endswith(".docx")}


# ---- Vergleich -----------------------------------------------------------------------------------------------------------------
def abbild(dok) -> dict:
    """Was beim Roundtrip erhalten bleiben soll: Text, Zeichenformat-Läufe, Tabellenstruktur, Bilder (aus dem Dokumentenmodell ``core.document.Dokument``)."""
    from core.dokument.dokument import InlineObjekt, Lauf, Tabelle
    from core.dokument.formatvorlagen import wirksames_zeichenformat
    laeufe, tabellen = [], []
    bilder = sum(1 for o in dok.objekte.values() if getattr(o, "art", "") in ("bild", "roh"))              # frei positionierte Bilder
    for a in dok.absaetze():
        for x in a.inhalte:
            if isinstance(x, InlineObjekt):
                bilder += x.art in ("bild", "roh")
            elif isinstance(x, Lauf) and x.text.strip():
                z = wirksames_zeichenformat(dok, a, x.format)
                fam = z.get("schrift")
                standard = "Liberation Sans"                       # ohne ausdrückliche Schrift gilt die Standardschrift (das Speichern schreibt sie als Dokumentvorgabe)
                laeufe.append((x.text, (fam[0] if isinstance(fam, (list, tuple)) and fam else fam) or standard, round(z.get("groesse_pt") or 0), bool(z.get("fett")), bool(z.get("kursiv"))))

    def alle_tabellen(bloecke):
        for blk in bloecke:
            if isinstance(blk, Tabelle):
                spans = sorted((r, c, blk.zellen[r][c].zeilenspanne, blk.zellen[r][c].spaltenspanne) for r in range(blk.zeilen) for c in range(blk.spalten)
                               if blk.zellen[r][c].verdeckt_von is None)
                tabellen.append((blk.zeilen, blk.spalten, tuple(spans)))
                for zeile in blk.zellen:
                    for zelle in zeile:
                        alle_tabellen(zelle.bloecke)
    for abschnitt in dok.abschnitte:
        alle_tabellen(abschnitt.bloecke)
    # Leere Absätze zählen nicht: Word verlangt einen Absatz am Ende einer Zelle, auch nach einer verschachtelten Tabelle.
    text = "\n".join(z for z in dok.text().split("\n") if z.strip())
    return {"text": text, "laeufe": laeufe, "bilder": bilder, "tabellen": tabellen}


def roundtrip(pfad: str) -> dict:
    """Einlesen → ohne Änderung speichern → erneut einlesen (alles über das Dokumentenmodell). → Ergebnis mit beiden Abbildern, den Berichten und den Abweichungen."""
    from filter.docx.docx_modell_schreiber import docx_dokument_daten
    from framework.dokumentverwaltung.dateizugriff.modell_laden import lade_modell
    g1 = lade_modell(pfad)
    with tempfile.TemporaryDirectory(prefix="korpus-") as tmp:
        aus = os.path.join(tmp, "zurueck.docx")
        daten, rep_w = docx_dokument_daten(g1.document, g1.page, g1.meta)
        with open(aus, "wb") as f:
            f.write(daten)
        g2 = lade_modell(aus)
    a, b = abbild(g1.document), abbild(g2.document)
    abw = [k for k in a if a[k] != b[k]]
    kopf = (g1.page.header.text, g1.page.footer.text), (g2.page.header.text, g2.page.footer.text)
    if kopf[0] != kopf[1]:
        abw.append("kopf_fuss")
    return {"erst": a, "zweit": b, "bericht_lesen": list(g1.report.warnings), "bericht_schreiben": list(getattr(rep_w, "warnings", []) or []),
            "bericht_zweit": list(g2.report.warnings), "abweichungen": abw}


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
