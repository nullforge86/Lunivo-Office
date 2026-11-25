"""RTF-Gruppenziele: was eine ``{\\wort …}``-Gruppe bedeutet (Tabellen, Info, Kopf-/Fußzeile, Bild, Feld) und wie sie endet."""
from __future__ import annotations

import re

from lunivo_writer.dienste.rtf.bilder import neues_bild
from lunivo_writer.dienste.rtf.modell import Ziel

KOPF_FUSS = {"header": "header", "headerl": "header", "headerr": "header", "footer": "footer", "footerl": "footer",
             "footerr": "footer", "headerf": "first_header", "footerf": "first_footer"}
_OHNE_ZUSATZ = ("header", "footer", "headerf", "footerf")
UEBERSPRINGEN = {"info", "stylesheet", "fonttbl", "colortbl", "revtbl", "rsidtbl",
                 "generator", "xmlnstbl", "themedata", "colorschememapping", "latentstyles", "datastore", "fldinst",
                 "pnseclvl", "pn", "nonshppict", "object", "objdata", "template", "userprops", "docvar", "bkmkstart",
                 "bkmkend", "pgdsctbl", "filetbl", "mmathPr", "wgrffmtfilter", "listpicture", "ftnsep", "ftnsepc",
                 "aftnsep", "aftnsepc", "ftncn", "aftncn", "fontemb", "fontfile", "falt", "panose", "leveltext",
                 "levelnumbers", "comment", "keywords", "subject", "operator", "company", "manager", "category", "doccomm",
                 "hlinkbase", "creatim", "revtim", "printim", "buptim", "title", "author", "pict", "field", "fldrslt",
                 "shppict", "shprslt", "listtext", "pntext", "footnote", "annotation", "atnid", "atnauthor", "atndate", "atnref"}
_TABELLEN = ("fonttbl", "colortbl", "stylesheet", "info")
_PUFFER_ZIELE = ("sn", "sv", "fonttbl", "stylesheet", "info-title", "info-author", "listentext", "notiz", "kommentar", "atn-atnauthor", "atn-atnid", "atn-atndate", "atn-atnref", "atn-atrfstart", "atn-atrfend")
_WARNUNGEN = {
    "footnote": "Fuß- und Endnoten aus der RTF-Datei wurden nicht übernommen.",
    **dict.fromkeys(("annotation", "atnid", "atnauthor", "atndate", "atnref"),
                    "Kommentare aus der RTF-Datei wurden nicht übernommen."),
    "do": "Zeichnungen im alten Format (\\do) aus der RTF-Datei wurden nicht übernommen.",
}


def ziel_beginnen(z, g: dict, w: str, zahl: int | None) -> bool:
    """Wahr, wenn das Steuerwort am Gruppenanfang die Gruppe zu einem Ziel macht (es wird dann nicht weiter angewendet)."""
    if g["dest"] in ("fonttbl", "stylesheet") and w in ("f", "s") and zahl is not None:
        g["eintrag"] = zahl
    for stufe in (_tabellen_ziel, _info_ziel, _kopf_fuss_ziel, _inhalts_ziel, _feld_ziel, _notiz_ziel, _verworfenes_ziel):
        erg = stufe(z, g, w, zahl) if stufe is _notiz_ziel else stufe(z, g, w)
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
    elif w == "shp":                                                      # Form: Geometrie (\shpinst), Eigenschaften (\sp) und Text (\shptxt) sammeln
        g["dest"], g["shp"] = "shp", {"geom": {}, "eig": {}, "txt": None, "bild": None}
    elif w == "shpgrp":
        g["dest"] = "shpgrp"
    elif w == "listtable":                                                # Listendefinitionen: Ebenen mit Zahlenart (\\levelnfc) und Beginn
        g["dest"] = "listtbl"
    elif w == "listoverridetable":
        g["dest"] = "lovrtbl"
    elif w == "list" and g["dest"] == "listtbl":
        g["dest"], g["lst"] = "lst", {"id": None, "ebenen": []}
    elif w == "listlevel" and g["dest"] == "lst":
        g["dest"], g["lvl"] = "lstlevel", {}
    elif w == "listoverride" and g["dest"] == "lovrtbl":
        g["dest"], g["lovr"] = "lovr", {}
    elif w == "shpinst" and g.get("shp") is not None:
        g["dest"] = "shpinst"
    elif w == "sp" and g.get("shp") is not None:
        g["dest"] = "sp"
    elif w in ("sn", "sv") and g.get("shp") is not None:
        g["dest"], g["puffer"] = w, []
    elif w == "shptxt" and g.get("shp") is not None:
        ziel = Ziel(False)
        g["shp"]["txt"] = ziel
        g["ziel"], g["a"], g["kf_wurzel"], g["dest"] = ziel, {}, True, None
    else:
        return None
    return True


def _feld_ziel(z, g, w) -> bool | None:
    if w == "field":
        g["feld"] = {"inst": []}
    elif w == "fldinst":
        g["dest"] = "fldinst"
    elif w == "fldrslt":
        inst = "".join((g.get("feld") or {"inst": []})["inst"]).strip()
        if inst.upper().startswith("HYPERLINK"):                          # Verweis: der Text des Feldergebnisses trägt das Ziel
            marke = re.search(r'\\l\s+"([^"]*)"', inst)
            url = re.search(r'"([^"]*)"', inst)
            ziel_link = ("#" + marke.group(1)) if marke else (url.group(1) if url else "")
            if ziel_link:
                g["z"]["link"] = ziel_link
        anw = inst.upper()
        if not g["ziel"].haupt and (anw.startswith("NUMPAGES") or anw.startswith("PAGE")):
            g["ziel"].text("{PAGES}" if anw.startswith("NUMPAGES") else "{PAGE}", g["z"])
            g["dest"] = "skip"
    else:
        return None
    return True


def _notiz_ziel(z, g, w, zahl=None) -> bool | None:
    """Nur im Modellweg: Fuß-/Endnoten und Kommentare (mit Textbereich) werden gelesen; sonst fallen sie unter die verworfenen Ziele."""
    if not z.modell:
        return None
    if w == "footnote":
        g["dest"], g["puffer"], g["a"], g["notiz_art"], g["notiz_wurzel"] = "notiz", [], {}, "f", True
    elif w == "annotation":
        g["dest"], g["puffer"], g["a"], g["notiz_wurzel"] = "kommentar", [], {}, True
    elif w in ("atnauthor", "atnid", "atndate", "atnref", "atrfstart", "atrfend"):      # Angaben stehen als Text in der Gruppe (``{\*\atnref 5}``)
        g["dest"], g["puffer"], g["notiz_wurzel"] = "atn-" + w, [], True
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
    elif dest in ("notiz", "kommentar", "atn-atnauthor", "atn-atnid", "atn-atndate", "atn-atnref", "atn-atrfstart", "atn-atrfend") and g.get("notiz_wurzel"):
        text = "".join(g["puffer"]).strip()
        zahl = int(text) if text.lstrip("-").isdigit() else None
        if dest == "notiz":
            g["ziel"].laeufe.append(("n", g.get("notiz_art", "f"), text))
        elif dest == "kommentar":
            nr = z.komm_ref if z.komm_ref is not None else len(z.kommentare) + 1
            z.kommentare[nr] = {"autor": z.komm_akt.get("atnauthor", ""), "datum": z.komm_akt.get("atndate", ""), "text": text}
            z.komm_ref, z.komm_akt = None, {}
        elif dest == "atn-atnref":
            z.komm_ref = zahl
        elif dest == "atn-atrfstart":
            if zahl is not None:
                z.komm_offen.append(zahl)
        elif dest == "atn-atrfend":
            if zahl in z.komm_offen:
                z.komm_offen.remove(zahl)
        else:
            z.komm_akt[dest[4:]] = text
    elif dest == "lstlevel" and g.get("lst") is not None:
        g["lst"]["ebenen"].append(g["lvl"])
    elif dest == "lst" and g["lst"]["id"] is not None:
        z.listen_def[g["lst"]["id"]] = g["lst"]["ebenen"]
    elif dest == "lovr" and g["lovr"].get("ls") is not None:
        z.list_ls[g["lovr"]["ls"]] = g["lovr"].get("listid")
    elif dest == "sn" and g.get("shp") is not None:
        g["shp"]["_n"] = "".join(g["puffer"]).strip()
    elif dest == "sv" and g.get("shp") is not None:
        n = g["shp"].pop("_n", None)
        if n:
            g["shp"]["eig"][n] = "".join(g["puffer"]).strip()
    elif dest == "shp" and g.get("shp") is not None:
        from lunivo_writer.dienste.rtf.formen import form_aus_shp
        d = form_aus_shp(z, g["shp"])
        if d is not None:
            lg = d["lage"]
            if "SHAPE" in "".join((g.get("feld") or {"inst": []})["inst"]).upper() and abs(lg["x"]) <= 1.0 and abs(lg["y"] + d["hoehe"]) <= 4.0:
                lg["imtext"] = True                                    # Form im ``SHAPE``-Feld, die mit ihrer Unterkante auf der Grundlinie sitzt: Objekt im Text (so schreiben LibreOffice und Word Formen „als Zeichen“); eine schwebende bleibt frei
            g["ziel"].laeufe.append(("shape", d))
    if g.get("kf_wurzel") and g["ziel"].laeufe:
        g["ziel"].absatz(g["a"])


def gruppentext(z, g: dict, s: str) -> None:
    """Text innerhalb einer Gruppe: in den Haupttext, in einen Puffer, in die Farbtabelle oder in die Feldanweisung."""
    dest = g["dest"]
    if dest is None:
        g["ziel"].text(s, {**g["z"], "komm": z.komm_offen[-1]} if z.komm_offen else g["z"])
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
