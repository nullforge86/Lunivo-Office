"""RTF-Zerleger: zerlegt den Bytestrom in Tokens und führt Gruppenstapel, Textzeichen und Tabellenzeilen nach."""
from __future__ import annotations

import re

from lunivo_writer.core.dokument.seite import PageSettings
from lunivo_writer.core.dokument.bericht import DocumentIOError, IOReport
from lunivo_writer.dienste.rtf import bilder
from lunivo_writer.dienste.rtf.gruppen import gruppe_ende, gruppentext, ziel_beginnen
from lunivo_writer.dienste.rtf.modell import Ziel
from lunivo_writer.dienste.rtf.steuerwoerter import steuerwort

MAX_TIEFE = 2000
_TOKEN = re.compile(rb"\\([a-zA-Z]{1,32})(-?\d{1,10})? ?|\\'([0-9a-fA-F]{2})|\\(.)|([{}])|([^\\{}\r\n]+)|[\r\n]+", re.S)
_MODELL_STERN = ("annotation", "atnauthor", "atnid", "atndate", "atnref", "atrfstart", "atrfend")      # im Modellweg gelesene \\*-Ziele
_CHARSET_CP = {128: "cp932", 129: "cp949", 134: "cp936", 136: "cp950", 161: "cp1253", 162: "cp1254", 163: "cp1258", 177: "cp1255", 178: "cp1256",
               186: "cp1257", 204: "cp1251", 222: "cp874", 238: "cp1250"}
_SYMBOL = {"~": "\u00a0", "_": "\u2011", "-": "", "{": "{", "}": "}", "\\": "\\", "\n": None, "\r": None}


def _ersatzpaar(g: dict, wert: int) -> str:
    """Hälften eines UTF-16-Ersatzpaars (\\u-Paar für Zeichen außerhalb der BMP) zusammensetzen."""
    if 0xD800 <= wert <= 0xDBFF:
        g["hoch"] = wert
        return ""
    hoch = g.pop("hoch", None)
    if hoch is None:
        return "\ufffd"
    return chr(0x10000 + ((hoch - 0xD800) << 10) + (wert - 0xDC00))


def _unicode_zeichen(g: dict, zahl: int) -> str:
    wert = zahl + 65536 if zahl < 0 else zahl
    return chr(wert) if wert < 0xD800 or wert > 0xDFFF else _ersatzpaar(g, wert)


class Zerleger:
    def __init__(self, daten: bytes, modell: bool = False):
        self.daten = daten
        self.modell = modell
        self.report = IOReport()
        self.schriften: dict[int, str] = {}
        self.farben: list[str | None] = []
        self.stile: dict[int, int] = {}                     # \sN → Überschriftenebene
        self.codepage = "cp1252"
        self.standard_schrift = 0
        self.seite = PageSettings()
        self.listen_def: dict = {}                          # \listtable: Listen-Id → Ebenen ({"levelnfc", "levelstartat", …})
        self.list_ls: dict = {}                             # \listoverridetable: \lsN → Listen-Id
        self.font_charset: dict[int, int] = {}              # Schrift → \fcharsetN (bestimmt die Codepage der \'xx-Zeichen)
        self._cellbg: list = []                             # Zellschattierung (Farbindex) je Zelle der Zeile
        self._clbg = None
        self.sek: dict = {}                                 # Seiteneigenschaften des Abschnitts in Arbeit (\sectd …)
        self.sek_liste: list[dict] = []                     # je Abschnitt (in Reihenfolge) seine Eigenschaften
        self.titel_erste = False
        self.meta = {"title": "", "author": ""}
        self.haupt = Ziel(True)
        self.kopf_fuss: dict[str, tuple[Ziel, dict]] = {}
        # Laufzustand
        self._absatz: dict = {}
        self._g: dict = {}
        self._stapel: list[dict] = []
        self._cellx: list[int] = []
        self._merken: list[set] = []                       # Verbundmarken je Zelle der Zeile
        self._marke: set = set()
        self._ueberspringe = 0                              # noch zu überspringende Ersatzzeichen nach \uN
        self._stern = False
        self._pos = 0
        self.komm_offen: list[int] = []                    # offene Kommentarbereiche (\\atrfstart N … \\atrfend N)
        self.kommentare: dict[int, dict] = {}              # Nummer → Autor, Datum, Text
        self.komm_akt: dict = {}
        self.komm_ref: int | None = None

    def run(self) -> None:
        self._g = {"z": {"f": None, "fs": 24}, "a": self._absatz, "uc": 1, "ziel": self.haupt, "dest": None,
                   "puffer": None, "feld": None}
        n = len(self.daten)
        while self._pos < n:
            m = _TOKEN.match(self.daten, self._pos)
            if m is None:
                self._pos += 1
                continue
            self._pos = m.end()
            if self._token(*m.groups()):
                break
        self.haupt.abschliessen(self._absatz)
        from lunivo_writer.dienste.rtf.steuerwoerter import sek_fertig
        self.sek_liste.append(sek_fertig(self.sek))

    def _token(self, wort, zahl, hexwert, symbol, klammer, text) -> bool:
        """Ein Token verarbeiten; wahr, wenn die äußerste Gruppe geschlossen wurde (Ende des Dokuments)."""
        if klammer == b"{":
            self._gruppe_auf()
        elif klammer == b"}":
            return self._gruppe_zu()
        elif text is not None or hexwert is not None:
            self._textzeichen(hexwert, text)
        elif symbol is not None:
            self._symbol(symbol.decode("latin-1"))
        elif wort is not None:
            self._wort(wort.decode("ascii"), int(zahl) if zahl is not None else None)
        return False

    # ---- Gruppen --------------------------------------------------------------------------------------------------------
    def _gruppe_auf(self) -> None:
        g = self._g
        self._stapel.append(g)
        self._g = dict(g, z=dict(g["z"]), a=g["a"])
        self._g.pop("kf_wurzel", None)
        self._g.pop("notiz_wurzel", None)
        self._g["neu"] = True
        if len(self._stapel) > MAX_TIEFE:
            raise DocumentIOError("Die RTF-Datei ist zu tief verschachtelt und wird nicht geöffnet.")

    def _gruppe_zu(self) -> bool:
        alt = self._g
        gruppe_ende(self, alt)
        if not self._stapel:
            return True
        self._g = self._stapel.pop()
        if alt["dest"] == "pict" and alt.get("bild") is not None:
            self._bild_fertig(alt["bild"])
        return False

    def _bild_fertig(self, b: dict) -> None:
        """Ein ``\\pict`` ist zu Ende: Bild im Text, Bild einer Form (Bildrahmen, Füllung) oder — wenn kein Decoder es kennt — unverändert aufbewahrt."""
        lauf = bilder.bild_lauf_modell(b)
        shp = self._g.get("shp")
        in_form = shp is not None and self._g.get("dest") in ("sv", "sp", "shpinst")
        if lauf is None:
            daten = bilder.bilddaten(b)
            if not daten:                                                 # leere Bildgruppe (Platzhalter ohne Daten): nichts zu erhalten
                return
            roh = {"daten": daten, "blip": b.get("art") or "pngblip", "w": b.get("w"), "h": b.get("h"), "gw": b.get("gw"), "gh": b.get("gh")}
            self.report.warn("Ein Bild in einem Format, das Lunivo nicht darstellen kann, wurde unverändert aufbewahrt und beim Speichern als RTF wieder geschrieben.")
            if in_form:
                shp["roh_bild"] = roh
            else:
                self._g["ziel"].laeufe.append(("b_roh", roh))
            return
        if in_form:                                                       # Bild einer Form: gehört zur Form, nicht in den Text
            shp["bild"] = lauf
            return
        self._g["ziel"].laeufe.append(lauf)

    # ---- Text und Symbole -----------------------------------------------------------------------------------------------
    def _textzeichen(self, hexwert, text) -> None:
        g = self._g
        g.pop("neu", None)
        if hexwert is not None:
            roh = bytes([int(hexwert, 16)])
            if g["dest"] == "pict":
                return
        else:
            roh = text
        if g["dest"] == "pict":
            g["bild"]["hex"].append(roh)
            return
        s = roh.decode(self._codepage_fuer(g), errors="replace")
        if self._ueberspringe:
            weg = min(self._ueberspringe, len(s))
            s, self._ueberspringe = s[weg:], self._ueberspringe - weg
        gruppentext(self, g, s)

    def _codepage_fuer(self, g: dict) -> str:
        """Die Codepage für Bytes im Text: die des Zeichensatzes der aktuellen Schrift (``\\fcharset``), sonst die des Dokuments."""
        cs = self.font_charset.get(g["z"].get("f"))
        return _CHARSET_CP.get(cs, self.codepage)

    def _symbol(self, sym: str) -> None:
        g = self._g
        neu = g.pop("neu", False)
        if sym == "*":
            self._stern = True
            if neu:
                g["neu"] = True                              # das Steuerwort nach \* beginnt die Gruppe
        elif sym in "\n\r":
            steuerwort(self, g, "par", None)
        elif sym in _SYMBOL:
            gruppentext(self, g, _SYMBOL[sym] or "")

    # ---- Steuerwörter ---------------------------------------------------------------------------------------------------
    def _wort(self, w: str, z: int | None) -> None:
        g = self._g
        neu = g.pop("neu", False)
        dest = g["dest"]
        if w == "bin" and z:
            if dest == "pict":
                g["bild"]["bin"] = self.daten[self._pos:self._pos + z]
            self._pos += max(0, z)
            return
        if neu and self._stern and w not in ("shppict", "fldinst", "shpinst") and not (self.modell and w in _MODELL_STERN):
            g["dest"] = "skip"
            self._stern = False
            return
        self._stern = False
        if dest == "skip":
            return
        if dest == "notiz" and w == "ftnalt":
            g["notiz_art"] = "e"
        if self._unicode_wort(g, w, z):
            return
        if neu and ziel_beginnen(self, g, w, z):
            return
        if dest == "fonttbl" and w == "fcharset" and z is not None and "eintrag" in g:
            self.font_charset[g["eintrag"]] = z
            return
        if dest == "lst" and w == "listid" and z is not None:
            g["lst"]["id"] = z
            return
        if dest == "lstlevel" and w in ("levelnfc", "levelnfcn", "levelstartat", "leveljc") and z is not None:
            g["lvl"][w] = z
            return
        if dest == "lovr" and w in ("listid", "ls") and z is not None:
            g["lovr"][w] = z
            return
        if dest == "shpinst" and g.get("shp") is not None:                    # Geometrie der Form: \shpleft, \shptop, \shpright, \shpbottom, \shpwr, \shpbxpage …
            g["shp"]["geom"][w] = z
            return
        if dest == "pict":
            bilder.bild_wort(g["bild"], w, z)
        elif not self._tabellen_wort(g, w, z):
            steuerwort(self, g, w, z)

    def _unicode_wort(self, g: dict, w: str, z: int | None) -> bool:
        if z is None or w not in ("u", "uc"):
            return False
        if w == "uc":
            g["uc"] = max(0, z)
            return True
        gruppentext(self, g, _unicode_zeichen(g, z))
        self._ueberspringe = g["uc"]
        return True

    def _tabellen_wort(self, g: dict, w: str, z: int | None) -> bool:
        if w == "cellx" and z is not None:
            self._cellx.append(z)
            self._merken.append(self._marke)
            self._cellbg.append(self._clbg)
            self._marke, self._clbg = set(), None
        elif w == "clcbpat" and z is not None:
            self._clbg = z
        elif w in ("clmgf", "clmrg", "clvmgf", "clvmrg"):
            self._marke.add(w)
        elif w == "trowd":
            self._cellx, self._merken, self._marke, self._cellbg, self._clbg = [], [], set(), [], None
        elif w in ("row", "nestrow"):
            if w == "nestrow":
                self.report.warn("Verschachtelte Tabellen aus der RTF-Datei wurden vereinfacht übernommen.")
            g["ziel"].reihe_ende(self._cellx, self._merken, self._cellbg)
        else:
            return False
        return True
