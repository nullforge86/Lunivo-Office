"""RTF-Gruppenziele: was eine ``{\\wort …}``-Gruppe bedeutet (Tabellen, Info, Kopf-/Fußzeile, Bild, Feld) und wie sie endet."""
from __future__ import annotations

import re

from lunivo_writer.services.rtf.bilder import neues_bild
from lunivo_writer.services.rtf.modell import Ziel

KOPF_FUSS = {"header": "header", "headerl": "header", "headerr": "header", "footer": "footer", "footerl": "footer",
             "footerr": "footer", "headerf": "first_header", "footerf": "first_footer"}
_OHNE_ZUSATZ = ("header", "footer", "headerf", "footerf")
UEBERSPRINGEN = {"info", "stylesheet", "fonttbl", "colortbl", "listtable", "listoverridetable", "revtbl", "rsidtbl",
                 "generator", "xmlnstbl", "themedata", "colorschememapping", "latentstyles", "datastore", "fldinst",
                 "pnseclvl", "pn", "nonshppict", "object", "objdata", "template", "userprops", "docvar", "bkmkstart",
                 "bkmkend", "pgdsctbl", "filetbl", "mmathPr", "wgrffmtfilter", "listpicture", "ftnsep", "ftnsepc",
                 "aftnsep", "aftnsepc", "ftncn", "aftncn", "fontemb", "fontfile", "falt", "panose", "leveltext",
                 "levelnumbers", "comment", "keywords", "subject", "operator", "company", "manager", "category", "doccomm",
                 "hlinkbase", "creatim", "revtim", "printim", "buptim", "title", "author", "pict", "field", "fldrslt",
                 "shppict", "listtext", "pntext", "footnote", "annotation", "atnid", "atnauthor", "atndate", "atnref"}
_TABELLEN = ("fonttbl", "colortbl", "stylesheet", "info")
_PUFFER_ZIELE = ("fonttbl", "stylesheet", "info-title", "info-author", "listentext")
_WARNUNGEN = {
    "footnote": "Fuß- und Endnoten aus der RTF-Datei wurden nicht übernommen.",
    **dict.fromkeys(("annotation", "atnid", "atnauthor", "atndate", "atnref"),
                    "Kommentare aus der RTF-Datei wurden nicht übernommen."),
    **dict.fromkeys(("shp", "shpgrp", "do"), "Zeichnungen und Formen aus der RTF-Datei wurden nicht übernommen."),
}


def ziel_beginnen(z, g: dict, w: str, zahl: int | None) -> bool:
    """Wahr, wenn das Steuerwort am Gruppenanfang die Gruppe zu einem Ziel macht (es wird dann nicht weiter angewendet)."""
    if g["dest"] in ("fonttbl", "stylesheet") and w in ("f", "s") and zahl is not None:
        g["eintrag"] = zahl
    for stufe in (_tabellen_ziel, _info_ziel, _kopf_fuss_ziel, _inhalts_ziel, _feld_ziel, _verworfenes_ziel):
        erg = stufe(z, g, w)
        if erg is not None:
            return erg
    return False


def _tabellen_ziel(z, g, w) -> bool | None:
    if w not in _TABELLEN:
        return None
    g["dest"] = w
    g["puffer"] = []
    if w == "colortbl":
        g["farbe"] = [None, None, None]
    return True


def _info_ziel(z, g, w) -> bool | None:
    dest = g["dest"]
    if dest == "info" and w in ("title", "author"):
        g["dest"] = "info-" + w
        g["puffer"] = []
        return True
    if dest in ("info", "info-title", "info-author") and w not in ("title", "author"):
        if dest == "info":
            g["dest"] = "skip"
        return g["dest"] == "skip"
    return None


def _kopf_fuss_ziel(z, g, w) -> bool | None:
    if w not in KOPF_FUSS:
        return None
    ziel = Ziel(False)
    z.kopf_fuss[KOPF_FUSS[w] + ("" if w in _OHNE_ZUSATZ else "?" + w)] = (ziel, {})
    g["ziel"], g["a"], g["kf_wurzel"] = ziel, {}, True
    return True


def _inhalts_ziel(z, g, w) -> bool | None:
    """Bild und Listentext: die Gruppe sammelt Daten bzw. Text."""
    if w == "pict":
        g["dest"], g["bild"] = "pict", neues_bild()
    elif w in ("listtext", "pntext"):
        g["dest"], g["puffer"] = "listentext", []
    elif w == "shppict":
        pass
    else:
        return None
    return True


def _feld_ziel(z, g, w) -> bool | None:
    if w == "field":
        g["feld"] = {"inst": []}
    elif w == "fldinst":
        g["dest"] = "fldinst"
    elif w == "fldrslt":
        anw = "".join((g.get("feld") or {"inst": []})["inst"]).strip().upper()
        if not g["ziel"].haupt and (anw.startswith("NUMPAGES") or anw.startswith("PAGE")):
            g["ziel"].text("{PAGES}" if anw.startswith("NUMPAGES") else "{PAGE}", g["z"])
            g["dest"] = "skip"
    else:
        return None
    return True


def _verworfenes_ziel(z, g, w) -> bool | None:
    if w in _WARNUNGEN:
        z.report.warn(_WARNUNGEN[w])
    elif w not in UEBERSPRINGEN or w in ("title", "author"):
        return None
    g["dest"] = "skip"
    return True


def gruppe_ende(z, g: dict) -> None:
    dest = g["dest"]
    if dest in ("fonttbl", "stylesheet") and g.get("puffer") is not None and "eintrag" in g:
        name = "".join(g["puffer"]).split(";")[0].strip()
        if dest == "fonttbl" and name:
            z.schriften[g["eintrag"]] = name
        elif dest == "stylesheet":
            m = re.match(r"(?:heading|überschrift|berschrift)\s*(\d)", name, re.I)
            if m and g["eintrag"] not in z.stile:
                z.stile[g["eintrag"]] = int(m.group(1))
    elif dest in ("info-title", "info-author"):
        z.meta["title" if dest == "info-title" else "author"] = "".join(g["puffer"]).strip()
    elif dest == "listentext":
        t = "".join(g["puffer"]).strip()
        g["ziel"].liste = "zahl" if re.match(r"^[\w]+[.)]?$", t) and t[:1].isalnum() else "punkt"
    if g.get("kf_wurzel") and g["ziel"].laeufe:
        g["ziel"].absatz(g["a"])


def gruppentext(z, g: dict, s: str) -> None:
    """Text innerhalb einer Gruppe: in den Haupttext, in einen Puffer, in die Farbtabelle oder in die Feldanweisung."""
    dest = g["dest"]
    if dest is None:
        g["ziel"].text(s, g["z"])
    elif dest in _PUFFER_ZIELE:
        g["puffer"].append(s)
    elif dest == "colortbl":
        for ch in s:
            if ch == ";":
                r, gr, b = g["farbe"]
                z.farben.append(None if r is None and gr is None and b is None
                                else "#%02x%02x%02x" % (r or 0, gr or 0, b or 0))
                g["farbe"] = [None, None, None]
    elif dest == "fldinst" and g.get("feld") is not None:
        g["feld"]["inst"].append(s)
