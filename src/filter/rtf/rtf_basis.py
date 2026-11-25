"""Gemeinsame Bausteine zum Schreiben von RTF aus dem Dokumentmodell — ohne Qt: Maße, Textmaskierung, Schrift- und Farbtabelle, Seite, Kopf- und Fußzeile.

Die Umrechnung der Bildpunkte (96 dpi) in Twip steht hier einmal; ``rtf_modell_schreiber`` baut darauf auf."""
from __future__ import annotations

from core.dokument.bericht import IOReport
from core.dokument.seite import HeaderFooter, PageSettings

TWIP_PRO_MM = 1440 / 25.4
TWIP_PRO_PX = 15
_AUSRICHTUNG = {"left": r"\ql", "center": r"\qc", "right": r"\qr", "justify": r"\qj"}


def _mm(wert: float) -> int:
    return round(max(0.0, float(wert)) * TWIP_PRO_MM)


def _px(wert: float) -> int:
    return round(float(wert) * TWIP_PRO_PX)


def _text(s: str) -> str:
    """Text RTF-sicher: Steuerzeichen maskiert, alles außerhalb von ASCII als \\uN? (UTF-16, mit Ersatzpaaren)."""
    out = []
    for ch in s:
        o = ord(ch)
        if ch in "\\{}":
            out.append("\\" + ch)
        elif ch == "\t":
            out.append(r"\tab ")
        elif ch in "\u2028\n":
            out.append(r"\line ")
        elif ch == "\u00a0":
            out.append(r"\~")
        elif 32 <= o < 128:
            out.append(ch)
        elif o < 32:
            continue
        else:
            for einheit in ch.encode("utf-16-le").hex(" ", 2).split():
                wert = int(einheit[2:4] + einheit[0:2], 16)
                out.append(f"\\u{wert - 65536 if wert > 32767 else wert}?")
    return "".join(out)


def _ausrichtung_seite(align: str, n: int) -> str:
    """„außen“: ungerade (rechte) Seiten rechts, gerade links; „innen“ umgekehrt. Andere Werte bleiben."""
    if align == "aussen":
        return "right" if n % 2 else "left"
    if align == "innen":
        return "left" if n % 2 else "right"
    return align


def verluste_melden(rep: IOReport, page: PageSettings, fmt: str) -> None:
    """Was das Schreiben nach ``fmt`` (RTF, ODT) nicht mitnimmt — damit nichts still verloren geht."""
    verluste = ((page.watermark, f"Das Wasserzeichen wird in {fmt} nicht gespeichert."),
                (page.border, f"Der Seitenrahmen wird in {fmt} nicht gespeichert."),
                (int(page.spalten or 1) > 1, f"Textspalten werden in {fmt} nicht gespeichert."),
                (page.bilder and fmt != "ODT", f"Bilder in Kopf- und Fußzeile werden in {fmt} nicht gespeichert."))
    for betroffen, text in verluste:
        if betroffen:
            rep.warn(text)


class RtfBasis:
    """Zustand und Tabellen eines RTF-Schreibers (Schriften, Farben, Bericht) sowie Seite, Kopf- und Fußzeile."""
    page: PageSettings

    def _warn(self, text: str) -> None:
        if text not in self._gemeldet:
            self._gemeldet.add(text)
            self.report.warn(text)

    def schrift(self, name: str) -> int:
        name = name or "Liberation Sans"
        if name not in self.schriften:
            self.schriften.append(name)
        return self.schriften.index(name)

    def kopf_fuss(self, art: str, hf: HeaderFooter, seite: int = 1) -> str:
        """``seite`` 2 für die Kopf-/Fußzeile linker (gerader) Seiten: „außen“/„innen“ werden dort gespiegelt."""
        if hf.is_empty():
            return ""
        zeilen = []
        for zeile in hf.text.split("\n"):
            t = _text(zeile).replace("{PAGES}", r"{\field{\*\fldinst NUMPAGES}{\fldrslt 1}}").replace("{PAGE}", r"\chpgn ")
            zeilen.append(t)
        return ("{\\" + art + r"\pard\plain" + _AUSRICHTUNG.get(_ausrichtung_seite(hf.align, seite), r"\qc") + " " + r"\par ".join(zeilen) + r"\par}" + "\n")

    def _seite_rtf(self) -> str:
        """Seitengröße, Ränder, Nummernformat und Startnummer."""
        p = self.page
        seite = (f"\\paperw{_mm(p.width_mm)}\\paperh{_mm(p.height_mm)}\\margl{_mm(p.margin_left_mm)}\\margr{_mm(p.margin_right_mm)}"
                 f"\\margt{_mm(p.margin_top_mm)}\\margb{_mm(p.margin_bottom_mm)}\\headery{_mm(p.kopf_abstand_mm)}"
                 f"\\footery{_mm(p.fuss_abstand_mm)}" + (r"\landscape" if p.landscape else "")
                 + (r"\titlepg" if p.diff_first else ""))
        seite += {"klein": r"\pgnlcltr", "gross": r"\pgnucltr", "roem_klein": r"\pgnlcrm", "roem_gross": r"\pgnucrm"}.get(p.seiten_format, "")
        if p.seiten_start:
            seite += f"\\pgnstarts{int(p.seiten_start)}\\pgnrestart"
        return seite

    def _kopf_rtf(self, seite: str) -> tuple:
        """→ (Seitenangaben, Kopf- und Fußzeilen); bei „außen/innen“ rechte (ungerade) und linke (gerade) Seiten getrennt."""
        p = self.page
        if any(h.align in ("aussen", "innen") and not h.is_empty() for h in (p.header, p.footer)):
            seite = r"\facingp" + seite
            kopf = (self.kopf_fuss("headerr", p.header) + self.kopf_fuss("headerl", p.header, 2)
                    + self.kopf_fuss("footerr", p.footer) + self.kopf_fuss("footerl", p.footer, 2))
        else:
            kopf = self.kopf_fuss("header", p.header) + self.kopf_fuss("footer", p.footer)
        if p.diff_first:
            kopf += self.kopf_fuss("headerf", p.first_header) + self.kopf_fuss("footerf", p.first_footer)
        return seite, kopf

    def _tabellen_rtf(self) -> tuple:
        """→ (Schriftentabelle, Farbtabelle, Überschriftenstile)."""
        schriften = "".join(f"{{\\f{i}\\fnil\\fcharset0 {_text(n)};}}" for i, n in enumerate(self.schriften or ["Liberation Sans"]))
        farben = ";" + "".join(f"\\red{int(c[1:3], 16)}\\green{int(c[3:5], 16)}\\blue{int(c[5:7], 16)};" for c in self.farben)
        stile = "".join(f"{{\\s{n}\\outlinelevel{n - 1} heading {n};}}" for n in range(1, 10))
        return schriften, farben, stile
