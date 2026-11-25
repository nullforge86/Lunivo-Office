"""OOXML-Strukturanalyse: liest ein DOCX direkt auf ZIP-/XML-Ebene und liefert **Beobachtungen** (``analysiere``) sowie die daraus bewertete
Funktionsabdeckung gegen den Katalog (``bewerte``). Es wird nichts geöffnet, gerendert oder verändert; Word ist nicht nötig.

Beobachtet werden Elemente, Attribute samt Werten, Verschachtelungen, Beziehungen, Paketteile, Felder, Kompatibilitätseinstellungen, die Vererbung über
Formatvorlagen (``basedOn``-Ketten der tatsächlich benutzten Vorlagen) und alles, was der Katalog nicht kennt (unbekannte Elemente, Namensräume, Teile, Beziehungen).
"""
from __future__ import annotations

import fnmatch
import hashlib
import os
import re
import zipfile

from kompatibilitaetspruefer.pruefung import ooxml_katalog as KAT

MAX_TEIL = 96 * 1024 * 1024
WERTE_MAX = 40                                   # höchstens so viele verschiedene Werte je Element/Attribut
NUR_PRAESENZ = ("rsid", "paraId", "textId", "w:id", "r:id", "r:embed", "r:link", "r:pict", "w:date", "w14:paraId", "w14:textId", "w15:paraId", "w:author", "w16cid:")
INHALTSTEILE = re.compile(r"^word/(document\d*|header\d*|footer\d*|footnotes|endnotes|comments\w*)\.xml$")
DEFINITIONSTEILE = re.compile(r"^word/(styles|stylesWithEffects|numbering|settings|webSettings|fontTable)\.xml$")
ZEICHNUNGSTEILE = re.compile(r"^word/(charts|diagrams|drawings)/.*\.xml$")
NUR_ZEICHNUNG = ("c", "cx", "c14", "c15", "dgm", "dsp")
EIGENSCHAFTSCONTAINER = ("w:pPr", "w:rPr", "w:tblPr", "w:tcPr", "w:trPr")

_pfx_cache: dict[str, tuple[str, bool]] = {}
_ZAHL = re.compile(r"^-?\d+(\.\d+)?$")


def _name(tag: str, ns_unbekannt: set) -> str:
    """``{uri}lokal`` → ``praefix:lokal`` (Strict wird auf denselben Präfix abgebildet)."""
    if tag[:1] != "{":
        return tag
    z = _pfx_cache.get(tag)
    if z is None:
        uri, lokal = tag[1:].split("}", 1)
        p = KAT.NAMENSRAEUME.get(uri)
        z = (f"{p}:{lokal}", p is None)
        _pfx_cache[tag] = z
        if p is None:
            ns_unbekannt.add(uri)
    return z[0]


def _leer_bucket() -> dict:
    return {"elemente": {}, "werte": {}, "nest": set(), "viel": set()}


def _zaehle(b: dict, name: str, attribute: dict, anc: tuple, ns_unbekannt: set) -> None:
    b["elemente"][name] = b["elemente"].get(name, 0) + 1
    for a in anc:
        b["nest"].add(f"{name}<{a}")
    for k, v in attribute.items():
        key = f"{name}@{_name(k, ns_unbekannt)}"
        w = b["werte"].setdefault(key, set())
        if any(k_.startswith(n) for n in NUR_PRAESENZ for k_ in (_name(k, ns_unbekannt),)):
            continue
        if len(w) < WERTE_MAX and len(v) <= 48:
            w.add(v)
        elif v not in w:
            b["viel"].add(key)


def _sha(pfad: str) -> str:
    h = hashlib.sha256()
    with open(pfad, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def analysiere(pfad: str) -> dict:
    """Beobachtungen zu einer DOCX-Datei (JSON-fähig). Wirft nicht; Fehler stehen in ``fehler``/``beschaedigt``/``verschluesselt``."""
    ns_unbekannt: set = set()
    b = {"pfad": os.path.abspath(pfad), "name": os.path.basename(pfad), "groesse": os.path.getsize(pfad), "sha256": _sha(pfad), "fehler": "",
         "beschaedigt": False, "verschluesselt": False, "strict": False}
    try:
        with open(pfad, "rb") as f:
            kopf = f.read(8)
    except OSError as e:
        b.update(beschaedigt=True, fehler=f"nicht lesbar: {e}")
        return b
    if not zipfile.is_zipfile(pfad):
        if kopf.startswith(b"\xd0\xcf\x11\xe0"):
            b["verschluesselt"] = True
            b["fehler"] = "kein ZIP-Paket (OLE-Container: verschlüsseltes oder altes .doc)"
        else:
            b.update(beschaedigt=True, fehler="kein gültiges ZIP-Paket")
        return b
    try:
        from filter.formate.import_grenzen import pruefe_paket, sicheres_xml
        pruefe_paket(pfad, "DOCX")
    except Exception as e:                                   # noqa: BLE001 - Importgrenzen von Lunivo überschritten oder Paket beschädigt
        b.update(beschaedigt=True, fehler=str(e))
        return b
    inhalt, definition = _leer_bucket(), _leer_bucket()
    felder: dict[str, int] = {}
    unbek_el: dict[str, str] = {}
    sdt_klassen: set[str] = set()
    tiefen = {"w:tbl": 0, "w:sdt": 0, "wpg:grpSp": 0}
    tab_zeilen = 0
    absatz_paare: set[str] = set()
    paare = {(r[1], r[2]) for r in (k[3] for k in KAT.KATALOG) if r and r[0] == "absatz_mit"}
    verschachtelt = False
    text = {"zeichen": 0, "hoch": False}
    rels: dict[str, int] = {}
    rels_extern: dict[str, list] = {}
    unbek_rel: set[str] = set()
    ign: set[str] = set()
    fehlerhaft: list[str] = []
    styles: dict[str, dict] = {}
    standard_ids: set[str] = set()
    doc_defaults = []
    erzeuger: dict[str, str] = {}
    kompat = {"modus": None, "einstellungen": {}, "optionen": []}
    ct = {"overrides": 0, "haupt": ""}
    haupt = "word/document.xml"
    with zipfile.ZipFile(pfad) as z:
        namen = [i.filename for i in z.infolist() if not i.is_dir()]
        b["teile"] = namen
        b["unbekannte_teile"] = [n for n in namen if not any(fnmatch.fnmatchcase(n.lower(), m.lower()) for m in KAT.BEKANNTE_TEILE)]

        def xml(n: str):
            if n not in namen or z.getinfo(n).file_size > MAX_TEIL:
                return None
            try:
                return sicheres_xml(z.read(n))
            except Exception as e:                           # noqa: BLE001
                fehlerhaft.append(f"{n}: {e}")
                return None

        w = _name  # Kürzel
        # Beziehungen
        for n in [n for n in namen if n.endswith(".rels")]:
            r = xml(n)
            if r is None:
                continue
            for el in r:
                typ = el.get("Type", "")
                kurz = typ.rsplit("/", 1)[-1]
                rels[kurz] = rels.get(kurz, 0) + 1
                if kurz not in KAT.BEKANNTE_BEZIEHUNGEN:
                    unbek_rel.add(typ)
                if el.get("TargetMode") == "External":
                    rels_extern.setdefault(kurz, []).append(el.get("Target", "")[:200])
                if n == "_rels/.rels" and kurz == "officeDocument":
                    haupt = el.get("Target", "word/document.xml").lstrip("/")
        r = xml("[Content_Types].xml")
        if r is not None:
            for el in r:
                if el.tag.endswith("Override"):
                    ct["overrides"] += 1
                    if el.get("PartName", "").lstrip("/") == haupt:
                        ct["haupt"] = el.get("ContentType", "")
        for n, tag in (("docProps/core.xml", "core"), ("docProps/app.xml", "app")):
            r = xml(n)
            if r is not None:
                for el in r:
                    lokal = el.tag.rsplit("}", 1)[-1]
                    if lokal in ("title", "creator", "Application", "AppVersion", "Template", "created") and (el.text or "").strip():
                        erzeuger[lokal] = el.text.strip()[:80]
        # Inhalt und Definitionen
        wurzel_styles = None
        W = lambda x: "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}" + x     # noqa: E731
        W_S = lambda x: "{http://purl.oclc.org/ooxml/wordprocessingml/main}" + x               # noqa: E731
        for n in namen:
            if not n.endswith(".xml"):
                continue
            inh = bool(INHALTSTEILE.match(n)) or n == haupt
            dfn = bool(DEFINITIONSTEILE.match(n))
            zch = bool(ZEICHNUNGSTEILE.match(n))
            if not (inh or dfn or zch):
                continue
            wurzel = xml(n)
            if wurzel is None:
                continue
            ziel = inhalt if (inh or zch) else definition
            feld_tiefe = 0
            stapel = [(wurzel, (), None, 0)]
            while stapel:
                el, anc, eltern, tbl_t = stapel.pop()
                name = _name(el.tag, ns_unbekannt)
                praef = name.split(":", 1)[0]
                if el.tag[:1] == "{" and "purl.oclc.org" in el.tag:
                    b["strict"] = True
                if zch and praef not in NUR_ZEICHNUNG and name != "mc:AlternateContent":
                    for k in reversed(list(el)):
                        stapel.append((k, anc, name, tbl_t))
                    continue
                if praef == "w" and name[2:] not in KAT.BEKANNT_W and name not in unbek_el:
                    unbek_el[name] = n
                _zaehle(ziel, name, el.attrib, anc, ns_unbekannt)
                if name == "w:style" and n.endswith("styles.xml") or name == "w:style" and "styles" in n:
                    sid = el.get(W("styleId")) or el.get(W_S("styleId"))
                    if sid:
                        styles[sid] = {"el": el, "basis": None, "standard": el.get(W("default")) in ("1", "true", "on")}
                        for k in el:
                            if k.tag.endswith("}basedOn"):
                                styles[sid]["basis"] = k.get(W("val")) or k.get(W_S("val"))
                        if styles[sid]["standard"]:
                            standard_ids.add(sid)
                if name == "w:docDefaults":
                    doc_defaults.append(el)
                if name == "w:t" or name == "w:delText":
                    t = el.text or ""
                    text["zeichen"] += len(t.strip())
                    if any(ord(c) > 0xFFFF for c in t):
                        text["hoch"] = True
                if name in ("w:instrText", "w:delInstrText") and el.text:
                    m = re.match(r"\s*([A-Za-z=]+)", el.text)
                    if m:
                        felder[m.group(1).upper()] = felder.get(m.group(1).upper(), 0) + 1
                elif name == "w:fldSimple":
                    m = re.match(r"\s*([A-Za-z=]+)", el.get(W("instr")) or "")
                    if m:
                        felder[m.group(1).upper()] = felder.get(m.group(1).upper(), 0) + 1
                elif name == "w:fldChar":
                    art = el.get(W("fldCharType")) or el.get(W_S("fldCharType"))
                    if art == "begin":
                        if feld_tiefe:
                            verschachtelt = True
                        feld_tiefe += 1
                    elif art == "end":
                        feld_tiefe = max(0, feld_tiefe - 1)
                elif name == "w:sdt":
                    sdt_klassen.add({"w:tbl": "zeile", "w:tr": "zelle", "w:p": "inline", "w:hyperlink": "inline", "w:smartTag": "inline"}.get(eltern or "", "block"))
                elif name == "w:tbl":
                    tab_zeilen = max(tab_zeilen, sum(1 for k in el if k.tag.endswith("}tr")))
                elif name == "w:p" and paare:
                    namen_in = {_name(d.tag, ns_unbekannt) for d in el.iter()}
                    for a_, b_ in paare:
                        if a_ in namen_in and b_ in namen_in:
                            absatz_paare.add(f"{a_}|{b_}")
                elif name == "mc:AlternateContent":
                    pass
                if name == "w:document" or name == "w:hdr" or name == "w:ftr":
                    v = el.get("{http://schemas.openxmlformats.org/markup-compatibility/2006}Ignorable")
                    if v:
                        ign.update(v.split())
                for t_ in tiefen:
                    if name == t_:
                        tbl_t_neu = tbl_t + 1 if t_ == "w:tbl" else tbl_t
                        tiefen[t_] = max(tiefen[t_], tbl_t_neu if t_ == "w:tbl" else tiefen[t_])
                anc_neu = anc + (name,) if name in KAT.VORFAHREN else anc
                tbl_k = tbl_t + 1 if name == "w:tbl" else tbl_t
                if name == "w:tbl":
                    tiefen["w:tbl"] = max(tiefen["w:tbl"], tbl_k)
                for k in reversed(list(el)):
                    stapel.append((k, anc_neu, name, tbl_k))
            if n == "word/settings.xml" or (dfn and n.endswith("settings.xml")):
                for el in wurzel.iter():
                    nm = _name(el.tag, ns_unbekannt)
                    if nm == "w:compatSetting":
                        wert = el.get(W("val"))
                        kompat["einstellungen"][el.get(W("name"), "?")] = wert
                        if el.get(W("name")) == "compatibilityMode":
                            try:
                                kompat["modus"] = int(wert)
                            except (TypeError, ValueError):
                                pass
                    elif nm.startswith("w:") and nm[2:] in KAT.BEKANNT_W and any(nm == f"w:{x}" for x in _KOMPAT_ELEMENTE):
                        kompat["optionen"].append(nm)
            if n == "word/settings.xml" and kompat["modus"] is None and any(True for _ in [0]):
                pass
    # Vererbung: benutzte Vorlagen samt basedOn-Kette; deren Eigenschaften wirken wie direkte Formatierung
    benutzt = set()
    for key in ("w:pStyle@w:val", "w:rStyle@w:val", "w:tblStyle@w:val"):
        benutzt |= inhalt["werte"].get(key, set())
    vererbt: set[str] = set()
    kette_max = 0
    wirksam = set(benutzt) | standard_ids
    for sid in list(benutzt):
        stufen, cur, gesehen = 0, sid, set()
        while cur and cur in styles and cur not in gesehen:
            gesehen.add(cur)
            stufen += 1
            wirksam.add(cur)
            cur = styles[cur]["basis"]
        kette_max = max(kette_max, stufen)
    for sid in wirksam:
        st = styles.get(sid)
        if st is None:
            continue
        stapel = [(st["el"], ())]
        while stapel:
            el, anc = stapel.pop()
            name = _name(el.tag, ns_unbekannt)
            if name != "w:style":
                _zaehle(inhalt, name, el.attrib, anc, ns_unbekannt)
                if sid in benutzt or any(sid == x for x in _benutzte_basen(styles, benutzt)):
                    if name in KAT.VERERBBAR:
                        vererbt.add(name)
            for k in el:
                stapel.append((k, anc + (name,) if name in KAT.VORFAHREN else anc))
    for el in doc_defaults:
        for d in el.iter():
            _zaehle(inhalt, _name(d.tag, ns_unbekannt), d.attrib, (), ns_unbekannt)
    stilnamen = definition["werte"].get("w:name@w:val", set())
    b.update({
        "hauptteil": haupt, "strict": b["strict"], "ns": sorted({k.split(":", 1)[0] for bk in (inhalt, definition) for k in bk["elemente"] if ":" in k}),
        "ns_unbekannt": sorted(ns_unbekannt), "inhalt": _bucket_json(inhalt), "definition": _bucket_json(definition),
        "felder": felder, "feld_verschachtelt": verschachtelt, "sdt_klassen": sorted(sdt_klassen), "tiefe": tiefen, "tabellen_max_zeilen": tab_zeilen,
        "absatz_paare": sorted(absatz_paare), "kette": kette_max, "vererbt": sorted(vererbt), "benutzte_vorlagen": sorted(benutzt),
        "kompat": kompat, "text": text, "rels": rels, "rels_extern": {k: v[:20] for k, v in rels_extern.items()},
        "ct": ct, "erzeuger": erzeuger, "mc_ignorable": sorted(ign), "unbekannte_elemente": unbek_el, "unbekannte_beziehungen": sorted(unbek_rel),
        "xml_fehler": fehlerhaft, "stilnamen_fremd": bool(stilnamen & {"Überschrift 1", "Titre 1", "Título 1", "Titolo 1", "Kop 1", "Rubrik 1", "Nagłówek 1"}),
    })
    return b


_KOMPAT_ELEMENTE = ("useWord97LineBreakRules", "noTabHangInd", "lineWrapLikeWord6", "doNotExpandShiftReturn", "usePrinterMetrics", "suppressSpBfAfterPgBrk",
                    "wpJustification", "splitPgBreakAndParaMark", "doNotUseHTMLParagraphAutoSpacing", "noLeading", "spaceForUL", "noColumnBalance",
                    "useSingleBorderforContiguousCells", "truncateFontHeightsLikeWP6", "mwSmallCaps", "wrapTrailSpaces", "footnoteLayoutLikeWW8")


def _benutzte_basen(styles: dict, benutzt: set) -> set:
    aus = set()
    for sid in benutzt:
        cur, gesehen = sid, set()
        while cur and cur in styles and cur not in gesehen:
            gesehen.add(cur)
            aus.add(cur)
            cur = styles[cur]["basis"]
    return aus


def _bucket_json(bk: dict) -> dict:
    return {"elemente": bk["elemente"], "werte": {k: sorted(v) for k, v in bk["werte"].items() if v}, "nest": sorted(bk["nest"]), "viel": sorted(bk["viel"]),
            "attribute": sorted(k for k in bk["werte"])}


# ---- Bewertung gegen den Katalog -------------------------------------------------------------------------------------------
NUR_INHALT = {KAT.ZEICHEN, KAT.ABSATZ, KAT.TABELLE, KAT.GRAFIK}


class _Kontext:
    def __init__(self, beob: dict):
        self.b = beob
        i, d = beob.get("inhalt") or {}, beob.get("definition") or {}
        self.inh, self.dfn = i, d
        self.teile_klein = [t.lower() for t in beob.get("teile", [])]
        self.fertig: dict[str, bool] = {}

    def sicht(self, nur_inhalt: bool):
        if nur_inhalt:
            return self.inh
        z: dict = {"elemente": dict(self.dfn.get("elemente", {})), "werte": {}, "nest": set(self.dfn.get("nest", [])) | set(self.inh.get("nest", [])),
                   "attribute": set(self.dfn.get("attribute", [])) | set(self.inh.get("attribute", []))}
        for k, v in self.inh.get("elemente", {}).items():
            z["elemente"][k] = z["elemente"].get(k, 0) + v
        for src in (self.dfn.get("werte", {}), self.inh.get("werte", {})):
            for k, v in src.items():
                z["werte"].setdefault(k, set()).update(v)
        return z


def _el(s, t):
    return t in s["elemente"]


def _werte(s, key):
    v = s["werte"].get(key)
    return set(v) if v else set()


def _attr(s, t, a, v):
    key = f"{t}@{a}"
    if v is None:
        return key in s["werte"] or key in set(s.get("attribute", ()))
    return v in _werte(s, key)


def _regel(r: tuple, k: _Kontext, s: dict, bereich: str) -> bool:
    b = k.b
    art = r[0]
    if art == "el":
        return _el(s, r[1])
    if art == "attr":
        return _attr(s, r[1], r[2], r[3] if len(r) > 3 else None)
    if art in ("in", "kombi_in"):
        return f"{r[1]}<{r[2]}" in set(s.get("nest", ()))
    if art == "any":
        return any(_regel(x, k, s, bereich) for x in r[1:])
    if art == "teil":
        return any(fnmatch.fnmatchcase(t, r[1].lower()) for t in k.teile_klein)
    if art == "ns":
        return r[1] in b.get("ns", ()) or any(x.split(":", 1)[0] == r[1] for x in k.inh.get("elemente", {})) or r[1] in _praefixe_attribute(k)
    if art == "min":
        return s["elemente"].get(r[1], 0) >= r[2]
    if art == "vielfalt":
        return len(_werte(s, f"{r[1]}@{r[2]}")) >= r[3]
    if art == "vielfalt_el":
        return sum(1 for t in r[1] if t in s["elemente"]) >= r[2]
    if art == "hoeher":
        for v in _werte(s, f"{r[1]}@{r[2]}"):
            try:
                if int(v) >= r[3]:
                    return True
            except ValueError:
                pass
        return False
    if art == "kette":
        return b.get("kette", 0) >= r[1]
    if art == "tiefe":
        return b.get("tiefe", {}).get(r[1], 0) >= r[2]
    if art == "tabellenzeilen":
        return b.get("tabellen_max_zeilen", 0) >= r[1]
    if art == "feld":
        return r[1] in b.get("felder", {})
    if art == "feldvielfalt":
        return len(b.get("felder", {})) >= r[1]
    if art == "feld_verschachtelt":
        return bool(b.get("feld_verschachtelt"))
    if art == "rel_extern":
        return r[1] in b.get("rels_extern", {})
    if art == "rel_extern_irgendwas":
        return bool(b.get("rels_extern"))
    if art == "sdt_ebenen":
        return len(b.get("sdt_klassen", ())) >= 3
    if art == "vererbt_irgendwas":
        return bool(b.get("vererbt"))
    if art == "wasserzeichen":
        return any(v.startswith("PowerPlusWaterMarkObject") or v.startswith("WordPictureWatermark") for key in ("v:shape@id", "wp:docPr@name", "v:shape@o:spid") for v in _werte(k.sicht(False), key))
    if art == "leer":
        return b.get("text", {}).get("zeichen", 0) == 0 and s["elemente"].get("w:p", 0) <= 1
    if art == "gross":
        return b.get("groesse", 0) >= 5 * 1024 * 1024 or k.inh.get("elemente", {}).get("w:p", 0) >= 1000
    if art == "unicode_hoch":
        return bool(b.get("text", {}).get("hoch"))
    if art == "kompat_modus":
        m = b.get("kompat", {}).get("modus")
        if m is None and r[1] == 0:
            return bool(b.get("kompat", {}).get("optionen"))         # ohne Angabe gilt Word 2003 (Modus 11)
        return m is not None and r[1] <= m <= r[2]
    if art == "unbekannt_ns":
        return bool(b.get("ns_unbekannt"))
    if art == "ct_override":
        return b.get("ct", {}).get("overrides", 0) > 0
    if art == "ct":
        return r[1] in (b.get("ct", {}).get("haupt", "")).lower()
    if art == "verschluesselt":
        return bool(b.get("verschluesselt"))
    if art == "beschaedigt":
        return bool(b.get("beschaedigt") or b.get("xml_fehler"))
    if art == "strict":
        return bool(b.get("strict"))
    if art == "transitional":
        return not b.get("strict") and not b.get("beschaedigt") and not b.get("verschluesselt")
    if art == "stilname_fremd":
        return bool(b.get("stilnamen_fremd"))
    if art == "absatz_mit":
        return f"{r[1]}|{r[2]}" in b.get("absatz_paare", ())
    if art in ("kombi", "all"):
        return all(k.fertig.get(x, False) for x in r[1:])
    return False


def _praefixe_attribute(k: _Kontext) -> set:
    aus = set()
    for bk in (k.inh, k.dfn):
        for key in bk.get("attribute", ()):
            a = key.split("@", 1)[-1]
            if ":" in a:
                aus.add(a.split(":", 1)[0])
    aus.update(x.split(":", 1)[0] for x in k.b.get("mc_ignorable", ()))
    aus.update(x for x in k.b.get("mc_ignorable", ()))
    return aus


def bewerte(beob: dict) -> list[str]:
    """Kennungen aller Katalogfunktionen, die das Dokument nachweislich benutzt."""
    if beob.get("beschaedigt") and not beob.get("inhalt"):
        k = _Kontext({**beob, "inhalt": {"elemente": {}, "werte": {}, "nest": []}})
    else:
        k = _Kontext(beob)
    ids = []
    spaeter = []
    for kid, bereich, _n, regel, _e in KAT.KATALOG:
        if regel[0] in ("kombi", "all"):
            spaeter.append((kid, bereich, regel))
            continue
        ok = _regel(regel, k, k.sicht(bereich in NUR_INHALT and not _braucht_definition(regel)), bereich) if beob.get("inhalt") or regel[0] in ("beschaedigt", "verschluesselt", "teil") else False
        k.fertig[kid] = ok
    for _ in range(3):                                               # Kombinationen dürfen auf Kombinationen verweisen
        for kid, bereich, regel in spaeter:
            k.fertig[kid] = _regel(regel, k, {"elemente": {}}, bereich)
    return [kid for kid, *_ in KAT.KATALOG if k.fertig.get(kid)]


def _braucht_definition(regel: tuple) -> bool:
    """Regeln, die nur Paketteile, Beziehungen oder Einstellungen betreffen, brauchen die Gesamtsicht."""
    return regel[0] in ("teil", "ns", "kompat_modus", "strict", "transitional", "any") and regel[0] != "any" or (
        regel[0] == "any" and any(_braucht_definition(x) for x in regel[1:]))


def eigenschaftswerte(beob: dict, grenze: int = 400) -> dict:
    """Verwendete Eigenschaften mit Werten, z. B. ``{"w:jc@w:val": ["both", "center"]}`` (nur Inhalt inkl. Vererbung)."""
    werte = (beob.get("inhalt") or {}).get("werte", {})
    return dict(sorted(werte.items())[:grenze])
