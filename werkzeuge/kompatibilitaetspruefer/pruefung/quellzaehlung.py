"""Zählung in der Quelldatei — die unabhängige Messlatte für Struktur- und Formatierungsvergleich.

Das ist **kein Import**: Es wird kein Dokument aufgebaut, nichts gesetzt und nichts gerendert. Das Modul zählt nur Elemente und Zeichen im XML der Quelldatei (DOCX, ODT) beziehungsweise
Zeilen (TXT) und liefert Rohtexte der Absätze für den Textvergleich. Die Zählung ist bewusst vorsichtig: Sie erfasst nur, was in der Datei **ausdrücklich** steht (direkte Formatierung, keine
Vererbung aus Formatvorlagen). Daraus folgt, dass nur Verlust beurteilt werden kann, nicht Mehrung. Pakete werden vorher mit den Importgrenzen von Lunivo geprüft; es wird nichts ausgeführt.
"""
from __future__ import annotations

import re
import zipfile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A_BLIP = "{http://schemas.openxmlformats.org/drawingml/2006/main}blip"
T_NS = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
TB_NS = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
D_NS = "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}"
O_NS = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}"
AUS = ("0", "false", "off", "none")


def zaehle(pfad: str, endung: str) -> dict | None:
    """``{"quelle", "werte", "texte", "format"}`` oder ``None``, wenn das Format keine Rohzählung erlaubt (RTF und weitere)."""
    endung = endung.lower()
    if endung in (".docx", ".dotx", ".docm"):
        return _docx(pfad)
    if endung in (".odt", ".fodt"):
        return _odt(pfad, endung == ".fodt")
    if endung in (".txt", ".text", ""):
        return _txt(pfad)
    return None


def _norm(s: str) -> str:
    return re.sub(r"[\s​￼ ]+", "", s)


def _zip_xml(pfad: str, name: str):
    from framework.dokumentverwaltung.dateizugriff.import_grenzen import pruefe_paket, sicheres_xml
    pruefe_paket(pfad, "DOCX")
    with zipfile.ZipFile(pfad) as z:
        try:
            daten = z.read(name)
        except KeyError:
            return None
    return sicheres_xml(daten)


# ---- DOCX -----------------------------------------------------------------------------------------------------------
def _docx(pfad: str) -> dict | None:
    wurzel = _zip_xml(pfad, "word/document.xml")
    if wurzel is None:
        return None
    w = {"absaetze": 0, "tabellen": 0, "verschachtelte_tabellen": 0, "bilder": 0, "abschnitte": 0}
    texte: list[str] = []
    fmt = {"fett_zeichen": 0, "kursiv_zeichen": 0, "unterstrichen_zeichen": 0, "mitte_absaetze": 0, "rechts_absaetze": 0, "block_absaetze": 0}
    stapel = [(wurzel, 0, False)]
    while stapel:
        el, tiefe, verdeckt = stapel.pop()
        tag = el.tag
        if tag == W + "p":
            if p_hat_abschnitt(el):
                w["abschnitte"] += 1
            if not verdeckt:
                w["absaetze"] += 1
                texte.append(_docx_absatz(el, w, fmt))
            continue
        if tag == W + "tbl":
            w["tabellen" if tiefe == 0 else "verschachtelte_tabellen"] += 1
            tiefe += 1
        elif tag == W + "sectPr":
            w["abschnitte"] += 1
            continue
        elif tag == W + "tc":
            vm = el.find(f"{W}tcPr/{W}vMerge")
            verdeckt = vm is not None and vm.get(W + "val", "continue") != "restart"
        elif tag in (W + "pPrChange", W + "del"):
            continue
        for kind in reversed(list(el)):
            stapel.append((kind, tiefe, verdeckt))
    # Abschnitte: das letzte sectPr steht im Body; jedes sectPr in einem Absatz beendet einen Abschnitt — beides ist je ein Abschnitt
    werte = {**w, "nichtleere_absaetze": sum(1 for t in texte if _norm(t)), "zeichen": sum(len(_norm(t)) for t in texte)}
    for teil, schluessel, tag in (("word/footnotes.xml", "fussnoten", "footnote"), ("word/endnotes.xml", "endnoten", "endnote"),
                                  ("word/comments.xml", "kommentare", "comment")):
        r = _zip_xml(pfad, teil)
        werte[schluessel] = 0 if r is None else sum(1 for n in r.iter(W + tag) if n.get(W + "type") in (None, "normal"))
    return {"quelle": "Quelldatei (XML-Rohzählung, direkte Formatierung)", "werte": werte, "texte": texte, "format": fmt}


def p_hat_abschnitt(p) -> bool:
    return p.find(f"{W}pPr/{W}sectPr") is not None


def _docx_absatz(p, w: dict, fmt: dict) -> str:
    text: list[str] = []
    jc = p.find(f"{W}pPr/{W}jc")
    if jc is not None:
        v = jc.get(W + "val", "")
        for schl, namen in (("mitte_absaetze", ("center",)), ("rechts_absaetze", ("right", "end")), ("block_absaetze", ("both", "distribute"))):
            if v in namen:
                fmt[schl] += 1
    stapel = [(p, False)]
    while stapel:
        el, _ = stapel.pop()
        tag = el.tag
        if tag in (W + "txbxContent", W + "del", W + "instrText", W + "pPr", W + "delText", W + "rPrChange"):
            continue
        if tag.endswith("}AlternateContent"):                            # nur eine Fassung zählen (Choice, sonst Fallback)
            wahl = [k for k in el if k.tag.endswith("}Choice")] or [k for k in el if k.tag.endswith("}Fallback")]
            for k in wahl[:1]:
                stapel.append((k, False))
            continue
        if tag == A_BLIP or tag.endswith("}imagedata"):
            w["bilder"] += 1
            continue
        if tag == W + "r":
            lauf = _docx_lauf(el)
            text.append(lauf)
            if lauf and not lauf.isspace():
                rpr = el.find(W + "rPr")
                if rpr is not None:
                    n = len(_norm(lauf))
                    for kuerzel, schl in (("b", "fett_zeichen"), ("i", "kursiv_zeichen")):
                        e = rpr.find(W + kuerzel)
                        if e is not None and e.get(W + "val", "1").lower() not in AUS:
                            fmt[schl] += n
                    u = rpr.find(W + "u")
                    if u is not None and u.get(W + "val", "single").lower() not in AUS:
                        fmt["unterstrichen_zeichen"] += n
            for kind in reversed(list(el)):                              # Bilder liegen in w:drawing/w:pict im Lauf
                stapel.append((kind, False))
            continue
        for kind in reversed(list(el)):
            stapel.append((kind, False))
    return "".join(text)


def _docx_lauf(r) -> str:
    teile = []
    for k in r:
        if k.tag == W + "t":
            teile.append(k.text or "")
        elif k.tag in (W + "tab", W + "br", W + "cr"):
            teile.append(" ")
    return "".join(teile)


# ---- ODT / FODT -----------------------------------------------------------------------------------------------------
def _odt(pfad: str, flach: bool) -> dict | None:
    if flach:
        from framework.dokumentverwaltung.dateizugriff.import_grenzen import pruefe_dateigroesse, sicheres_xml
        pruefe_dateigroesse(pfad, "FODT")
        with open(pfad, "rb") as f:
            wurzel = sicheres_xml(f.read())
    else:
        wurzel = _zip_xml(pfad, "content.xml")
    if wurzel is None:
        return None
    w = {"absaetze": 0, "tabellen": 0, "verschachtelte_tabellen": 0, "bilder": 0, "fussnoten": 0, "endnoten": 0, "kommentare": 0}
    texte: list[str] = []
    stapel = [(wurzel, 0, False)]
    while stapel:
        el, tiefe, ausserhalb = stapel.pop()
        tag = el.tag
        if tag in (T_NS + "p", T_NS + "h"):
            if not ausserhalb:
                w["absaetze"] += 1
                texte.append(_odt_text(el))
            continue
        if tag in (TB_NS + "covered-table-cell", O_NS + "master-styles", O_NS + "styles", O_NS + "automatic-styles", O_NS + "font-face-decls"):
            continue
        if tag == TB_NS + "table":
            w["tabellen" if tiefe == 0 else "verschachtelte_tabellen"] += 1 if not ausserhalb else 0
            tiefe += 1
        elif tag == D_NS + "image" and not ausserhalb:
            w["bilder"] += 1
        elif tag == T_NS + "note":
            w["endnoten" if el.get(T_NS + "note-class") == "endnote" else "fussnoten"] += 1
            continue
        elif tag in (O_NS + "annotation", O_NS + "annotation-end"):
            if tag == O_NS + "annotation":
                w["kommentare"] += 1
            continue
        elif tag == D_NS + "text-box":
            ausserhalb = True
        for kind in reversed(list(el)):
            stapel.append((kind, tiefe, ausserhalb))
    werte = {**w, "nichtleere_absaetze": sum(1 for t in texte if _norm(t)), "zeichen": sum(len(_norm(t)) for t in texte)}
    return {"quelle": "Quelldatei (XML-Rohzählung)", "werte": werte, "texte": texte, "format": None}


def _odt_text(el) -> str:
    teile = []
    stapel = [el]
    while stapel:
        e = stapel.pop()
        if e is not el and e.tag in (D_NS + "text-box", T_NS + "note", O_NS + "annotation"):
            continue
        if e is not el:
            pass
        teile.append(e.text or "")
        kinder = list(e)
        # Text nach einem Kindelement (tail) gehört in die richtige Reihenfolge
        for k in reversed(kinder):
            stapel.append(_Tail(k.tail or ""))
            stapel.append(k)
    return "".join(teile)


class _Tail:
    """Platzhalter, der nur den Resttext (tail) eines Elements in die Lesereihenfolge einreiht."""
    tag = ""

    def __init__(self, text: str):
        self.text = text

    def __iter__(self):
        return iter(())


# ---- TXT -----------------------------------------------------------------------------------------------------------
def _txt(pfad: str) -> dict | None:
    from framework.dokumentverwaltung.dateizugriff.import_grenzen import pruefe_dateigroesse
    pruefe_dateigroesse(pfad, "TXT")
    with open(pfad, "rb") as f:
        roh = f.read()
    try:
        s = roh.decode("utf-8-sig")
    except UnicodeDecodeError:
        s = roh.decode("cp1252", errors="replace")
    texte = s.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if texte and texte[-1] == "":
        texte.pop()
    werte = {"absaetze": len(texte), "nichtleere_absaetze": sum(1 for t in texte if _norm(t)), "zeichen": sum(len(_norm(t)) for t in texte)}
    return {"quelle": "Quelldatei (Textzeilen)", "werte": werte, "texte": texte, "format": None}
