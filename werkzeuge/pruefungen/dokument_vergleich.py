"""Vergleichssystem für Dateiformate: Import-, Layout- und Exportfehler getrennt (zuerst DOCX).

    .venv/bin/python werkzeuge/pruefungen/dokument_vergleich.py [Datei oder Ordner ...] [--bestand] [--referenz-pdf ORDNER] [--libreoffice] [--bericht datei.md] [--max N]

Je Dokument drei getrennte Stufen — ein Fehler wird der Stufe zugeordnet, in der er entsteht:

* **Import**: Liest der native Leser (``docx_dokument_leser``) die Datei, oder fällt sie auf den bisherigen Weg zurück (mit Grund)? Steht jede Eigenschaft, die die Kompatibilitätsregeln als
  „erhalten“ führen (``core/document/kompatibilitaet.py``), mit gleicher Anzahl im Modell (``docx_roh``)? Elemente ohne Regel oder „außerhalb“ stehen als Importgrenze im Bericht.
* **Layout**: Legt die Layout-Engine das Modell ohne Fehler auf Seiten, und stimmt die Seitenzahl mit der Referenz überein? Die Referenz ist ein PDF, das jemand mit Word,
  LibreOffice oder ONLYOFFICE aus derselben Datei gemacht hat (``--referenz-pdf ORDNER``: gleicher Dateiname; oder ein PDF neben der Datei). Mit ``--libreoffice`` erzeugt das Werkzeug
  die Referenz selbst mit ``soffice --headless``. Ohne Referenz wird die Layout-Abweichung nicht beurteilt, nur der Lauf der Engine.
* **Export**: Schreibt ``docx_dokument_daten`` das Modell, und fehlt in der geschriebenen Datei Text oder ein Eigenschaftselement, das die Quelle hatte (nach Anzahl)?

Kein Teil der Anwendung. Das Werkzeug beurteilt nicht, was „richtig“ ist, sondern zeigt Unterschiede zwischen Quelle, Modell, Referenz und Ausgabe; ``--bestand`` nimmt den Referenzbestand
(``referenzbestand.py``) als Eingabe."""
from __future__ import annotations

import argparse
import collections
import glob
import io
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from lxml import etree  # noqa: E402

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
EIGENSCHAFTEN = ("rPr", "pPr", "tblPr", "trPr", "tcPr", "sectPr")
BEHAELTER = {"sdt", "pict", "txbxContent", "wsp", "wgp", "pgBorders", "framePr", "tbl", "drawing", "footnoteReference", "commentReference", "hyperlink", "bookmarkStart", "fldChar",
             "fldSimple", "ins", "del"}
GANZ_ERHALTEN = {"drawing", "pict", "AlternateContent"}          # als Ganzes erhalten: Eigenschaften darin zählen nicht einzeln


def _lokal(e) -> str:
    return etree.QName(e).localname


def _zaehlen(e, z: collections.Counter) -> None:
    for kind in e:
        if not isinstance(kind.tag, str):
            continue
        n = _lokal(kind)
        if etree.QName(e).namespace == W_NS and _lokal(e) in EIGENSCHAFTEN:
            z[f"{_lokal(e)}/{n}"] += 1
        if n in BEHAELTER:
            z[n] += 1
        if n in GANZ_ERHALTEN:
            continue
        _zaehlen(kind, z)


def inventar(xml: bytes) -> collections.Counter:
    """Zählt Eigenschaftselemente (``pPr/jc`` …) und einige Behälter (``sdt``, ``drawing`` …) einer XML-Datei; Zeichnungen und VML-Objekte zählen als Ganzes."""
    z: collections.Counter = collections.Counter()
    _zaehlen(etree.fromstring(xml), z)
    return z


def texte(xml: bytes) -> list[str]:
    """Der Text jedes Absatzes (``w:t``), leere Absätze weggelassen."""
    wurzel = etree.fromstring(xml)
    aus = []
    for p in wurzel.iter("{%s}p" % W_NS):
        t = "".join(x.text or "" for x in p.iter("{%s}t" % W_NS, "{%s}delText" % W_NS))
        if t.strip():
            aus.append(t)
    return aus


def teil(pfad_oder_bytes, name: str = "word/document.xml") -> bytes | None:
    try:
        with zipfile.ZipFile(io.BytesIO(pfad_oder_bytes) if isinstance(pfad_oder_bytes, (bytes, bytearray)) else pfad_oder_bytes) as z:
            return z.read(name)
    except (KeyError, zipfile.BadZipFile, OSError):
        return None


# ---- Stufe 1: Import --------------------------------------------------------------------------------------------------------------------------------
def modell_roh(dok) -> collections.Counter:
    """Zählt die erhaltenen Elemente im Modell (alle, auch die ohne sichtbare Wirkung), mit denselben Namen wie ``inventar``."""
    z: collections.Counter = collections.Counter()

    def zaehle(art: str, liste) -> None:
        for t in liste or ():
            z[f"{art}/{_lokal(etree.fromstring(t))}"] += 1

    from lunivo_writer.core.dokument.dokument import Lauf
    for ab in dok.abschnitte:
        zaehle("sectPr", ab.seite.docx_roh)
    for a in dok.absaetze():
        zaehle("pPr", a.format.get("docx_roh"))
        zaehle("rPr", a.zeichenformat.get("docx_roh"))
        for x in a.inhalte:
            if isinstance(x, Lauf):
                zaehle("rPr", x.format.get("docx_roh"))
    for t in dok.tabellen():
        zaehle("tblPr", t.format.get("docx_roh"))
        for liste in (t.format.get("docx_roh_zeilen") or {}).values():
            zaehle("trPr", liste)
        for zeile in t.zellen:
            for zelle in zeile:
                zaehle("tcPr", zelle.format.get("docx_roh"))
    return z


def _soll(schluessel: str, n: int) -> int:
    """Wie oft ein Element mindestens vorkommen muss: Läufe mit gleichem Format werden im Modell zusammengefasst, deshalb zählt bei Lauf-Eigenschaften nur, dass es vorkommt."""
    return min(n, 1) if schluessel.startswith("rPr/") else n


def importieren(pfad: str):
    """→ (Modell oder None, Befund). Befund: Liste von Texten der Stufe Import."""
    from lunivo_writer.dienste.docx.docx_dokument_leser import _Leser, _Nicht
    befund: list[str] = []
    try:
        gelesen = _Leser(pfad).lesen()
    except _Nicht as ex:
        return None, [f"Rückfall auf den bisherigen Leser: {ex}"]
    except Exception as ex:                                                              # noqa: BLE001 — im Bericht sichtbar machen
        return None, [f"FEHLER beim Lesen: {type(ex).__name__}: {str(ex)[:120]}"]
    from lunivo_writer.core.dokument import pruefung
    for f in pruefung.pruefe_dokument(gelesen[0])[:5]:
        befund.append(f"Aufbau des Modells: {f}")
    return gelesen, befund


def importpruefung(pfad: str, dok) -> list[str]:
    """Vergleicht die Eigenschaften der Quelle mit dem Modell nach den Kompatibilitätsregeln."""
    from lunivo_writer.core.dokument import kompatibilitaet as K
    xml = teil(pfad)
    if xml is None:
        return ["document.xml nicht lesbar"]
    quelle, im_modell = inventar(xml), modell_roh(dok)
    befund = []
    for schluessel, n in sorted(quelle.items()):
        if "/" not in schluessel:
            continue
        art, name = schluessel.split("/", 1)
        u = K.umgang(art, name)
        if u == K.ERHALTEN and im_modell.get(schluessel, 0) < _soll(schluessel, n):
            befund.append(f"IMPORTFEHLER: {schluessel} steht {n}× in der Datei, aber {im_modell.get(schluessel, 0)}× im Modell")
        elif u in (None, K.AUSSERHALB):
            befund.append(f"Importgrenze: {schluessel} ({n}×) {'ohne Regel' if u is None else 'außerhalb des Modells'}")
    return befund


# ---- Stufe 2: Layout --------------------------------------------------------------------------------------------------------------------------------
def referenz_pdf(pfad: str, ordner: str | None, libreoffice: bool, tmp: str) -> str | None:
    stamm = os.path.splitext(os.path.basename(pfad))[0]
    kandidaten = [os.path.splitext(pfad)[0] + ".pdf"] + ([os.path.join(ordner, stamm + ".pdf")] if ordner else [])
    for k in kandidaten:
        if os.path.isfile(k):
            return k
    if libreoffice and shutil.which("soffice"):
        try:
            subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, pfad], check=True, capture_output=True, timeout=180)
        except (subprocess.SubprocessError, OSError):
            return None
        erzeugt = os.path.join(tmp, stamm + ".pdf")
        return erzeugt if os.path.isfile(erzeugt) else None
    return None


def seiten_im_pdf(pfad: str) -> int | None:
    try:
        from pypdf import PdfReader
        return len(PdfReader(pfad).pages)
    except Exception:                                                                    # noqa: BLE001
        return None


def layoutpruefung(dok, referenz: str | None) -> tuple[int | None, list[str]]:
    from lunivo_writer.core.layout import LayoutEngine
    befund = []
    try:
        erg = LayoutEngine().berechnen(dok)
    except Exception as ex:                                                              # noqa: BLE001
        return None, [f"LAYOUTFEHLER: {type(ex).__name__}: {str(ex)[:120]}"]
    seiten = len(erg.seiten)
    for h in getattr(erg, "hinweise", ()) or ():
        befund.append(f"Layout-Hinweis: {h}")
    if referenz:
        soll = seiten_im_pdf(referenz)
        if soll is None:
            befund.append("Referenz-PDF nicht lesbar")
        elif soll != seiten and abs(soll - seiten) > max(1, round(soll * 0.1)):
            befund.append(f"LAYOUTABWEICHUNG: {seiten} Seiten, Referenz {soll}")
        elif soll != seiten:
            befund.append(f"Layout: {seiten} Seiten, Referenz {soll} (innerhalb 10 %)")
    return seiten, befund


# ---- Stufe 3: Export --------------------------------------------------------------------------------------------------------------------------------
def exportpruefung(pfad: str, gelesen) -> list[str]:
    from lunivo_writer.dienste.docx.docx_modell_schreiber import docx_dokument_daten
    dok, page, meta, _rep = gelesen
    try:
        r = docx_dokument_daten(dok, page, meta)
    except Exception as ex:                                                              # noqa: BLE001
        return [f"EXPORTFEHLER: {type(ex).__name__}: {str(ex)[:120]}"]
    if r is None:
        return ["Der native Schreiber lehnt das Modell ab (Rückfall auf den bisherigen Weg)"]
    daten = r[0]
    aus, quelle = teil(daten), teil(pfad)
    if aus is None or quelle is None:
        return ["document.xml nicht lesbar"]
    befund = []
    t_quelle, t_aus = texte(quelle), texte(aus)
    if t_quelle != t_aus:
        i = next((k for k, (a, b) in enumerate(zip(t_quelle, t_aus)) if a != b), min(len(t_quelle), len(t_aus)))
        befund.append(f"EXPORTFEHLER Text: erster Unterschied im {i + 1}. Absatz ({len(t_quelle)} Absätze in der Quelle, {len(t_aus)} in der Ausgabe)")
    iq, ia = inventar(quelle), inventar(aus)
    for schluessel, n in sorted(iq.items()):
        if ia.get(schluessel, 0) < _soll(schluessel, n):
            befund.append(f"EXPORTVERLUST: {schluessel} {n}× in der Quelle, {ia.get(schluessel, 0)}× in der Ausgabe")
    return befund


# ---- Lauf -------------------------------------------------------------------------------------------------------------------------------------------
def pruefen(pfad: str, ordner_pdf: str | None, libreoffice: bool) -> dict:
    ergebnis = {"datei": pfad, "import": [], "layout": [], "export": [], "seiten": None}
    gelesen, befund = importieren(pfad)
    ergebnis["import"] = befund
    if gelesen is None:
        return ergebnis
    ergebnis["import"] += importpruefung(pfad, gelesen[0])
    with tempfile.TemporaryDirectory(prefix="vergleich-") as tmp:
        ref = referenz_pdf(pfad, ordner_pdf, libreoffice, tmp)
        ergebnis["seiten"], ergebnis["layout"] = layoutpruefung(gelesen[0], ref)
        ergebnis["referenz"] = bool(ref)
    ergebnis["export"] = exportpruefung(pfad, gelesen)
    return ergebnis


def sammeln(pfade: list[str]) -> list[str]:
    dateien: list[str] = []
    for p in pfade:
        p = os.path.expanduser(p)
        dateien += sorted(glob.glob(os.path.join(p, "**", "*.docx"), recursive=True)) if os.path.isdir(p) else [p]
    return dateien


def bericht(ergebnisse: list[dict]) -> str:
    n = len(ergebnisse)
    fehler = {s: sum(1 for e in ergebnisse if any(b.startswith(("IMPORTFEHLER", "FEHLER", "LAYOUTFEHLER", "LAYOUTABWEICHUNG", "EXPORTFEHLER", "EXPORTVERLUST")) for b in e[s]))
              for s in ("import", "layout", "export")}
    rueckfall = sum(1 for e in ergebnisse if any(b.startswith("Rückfall") for b in e["import"]))
    zeilen = ["# Dokumentvergleich", "",
              f"{n} Dokumente. Rückfall auf den bisherigen Leser: {rueckfall}. Mit Fehlern oder Abweichungen — Import: {fehler['import']}, Layout: {fehler['layout']}, Export: {fehler['export']}.",
              "Layout wird nur gegen Referenz-PDFs beurteilt (siehe Kopf von `dokument_vergleich.py`).", "",
              "| Datei | Import | Layout | Export |", "|---|---|---|---|"]
    for e in ergebnisse:
        def zelle(s):
            return "<br>".join(x.replace("|", "\\|") for x in e[s][:6]) or "–"
        zeilen.append(f"| `{os.path.basename(e['datei'])}` | {zelle('import')} | {zelle('layout')} | {zelle('export')} |")
    return "\n".join(zeilen) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Import, Layout und Export von DOCX-Dateien getrennt vergleichen")
    ap.add_argument("pfade", nargs="*")
    ap.add_argument("--bestand", action="store_true", help="den Referenzbestand (referenzbestand.py) prüfen")
    ap.add_argument("--referenz-pdf", default=None, help="Ordner mit Referenz-PDFs (gleicher Dateiname)")
    ap.add_argument("--libreoffice", action="store_true", help="Referenz-PDF mit LibreOffice erzeugen, wenn keine vorhanden ist")
    ap.add_argument("--bericht", default=None, help="Bericht (Markdown) in diese Datei schreiben")
    ap.add_argument("--max", type=int, default=0, help="höchstens so viele Dateien")
    a = ap.parse_args()
    pfade = list(a.pfade)
    if a.bestand:
        import referenzbestand
        pfade += [p for p in referenzbestand.auswahl().get("docx", [])]
    dateien = sammeln(pfade)
    if a.max:
        dateien = dateien[:a.max]
    if not dateien:
        print("Keine DOCX-Dateien angegeben.")
        return
    from PySide6.QtGui import QGuiApplication
    QGuiApplication.instance() or QGuiApplication([])
    ergebnisse = [pruefen(d, a.referenz_pdf, a.libreoffice) for d in dateien]
    text = bericht(ergebnisse)
    if a.bericht:
        with open(a.bericht, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Bericht geschrieben: {a.bericht}")
    else:
        print(text)


if __name__ == "__main__":
    main()
