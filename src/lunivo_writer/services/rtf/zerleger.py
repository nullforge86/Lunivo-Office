"""RTF-Zerleger: zerlegt den Bytestrom in Tokens und führt Gruppenstapel, Textzeichen und Tabellenzeilen nach."""
from __future__ import annotations

import re

from lunivo_writer.models.page import PageSettings
from lunivo_writer.models.report import DocumentIOError, IOReport
from lunivo_writer.services.rtf import bilder
from lunivo_writer.services.rtf.gruppen import gruppe_ende, gruppentext, ziel_beginnen
from lunivo_writer.services.rtf.modell import Ziel
from lunivo_writer.services.rtf.steuerwoerter import steuerwort

MAX_TIEFE = 2000
_TOKEN = re.compile(rb"\\([a-zA-Z]{1,32})(-?\d{1,10})? ?|\\'([0-9a-fA-F]{2})|\\(.)|([{}])|([^\\{}\r\n]+)|[\r\n]+", re.S)
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
    def __init__(self, daten: bytes):
        self.daten = daten
        self.report = IOReport()
        self.schriften: dict[int, str] = {}
        self.farben: list[str | None] = []
        self.stile: dict[int, int] = {}                     # \sN → Überschriftenebene
        self.codepage = "cp1252"
        self.standard_schrift = 0
        self.seite = PageSettings()
        self.titel_erste = False
        self.meta = {"title": "", "author": ""}
        self.haupt = Ziel(True)
        self.kopf_fuss: dict[str, tuple[Ziel, dict]] = {}
        # Laufzustand
        self._absatz: dict = {}
        self._g: dict = {}
        self._stapel: list[dict] = []
        self._cellx: list[int] = []
        self._ueberspringe = 0                              # noch zu überspringende Ersatzzeichen nach \uN
        self._stern = False
        self._pos = 0

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
        lauf = bilder.bild_lauf(b)
        if lauf is None:
            self.report.warn("Ein Bild aus der RTF-Datei hat ein nicht lesbares Format und wurde übersprungen.")
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
        s = roh.decode(self.codepage, errors="replace")
        if self._ueberspringe:
            weg = min(self._ueberspringe, len(s))
            s, self._ueberspringe = s[weg:], self._ueberspringe - weg
        gruppentext(self, g, s)

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
        if neu and self._stern and w not in ("shppict", "fldinst"):
            g["dest"] = "skip"
            self._stern = False
            return
        self._stern = False
        if dest == "skip":
            return
        if self._unicode_wort(g, w, z):
            return
        if neu and ziel_beginnen(self, g, w, z):
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
        elif w == "trowd":
            self._cellx = []
        elif w in ("row", "nestrow"):
            if w == "nestrow":
                self.report.warn("Verschachtelte Tabellen aus der RTF-Datei wurden vereinfacht übernommen.")
            g["ziel"].reihe_ende(self._cellx)
        else:
            return False
        return True
