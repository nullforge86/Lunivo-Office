"""Schriftsuche ohne Qt und ohne fremde Programme: die Schriftdateien der üblichen Ordner werden mit FreeType gelesen (Familie, Schnitt) und nach
Familie, Gewicht und Kursiv gefunden. Fehlt eine Familie, gilt die Ersatzschrift, die Fontconfig wählen würde (``fontconfig.py``), sonst die Tabelle ``ERSATZ`` und die Standardschriften."""
from __future__ import annotations

import os
from dataclasses import dataclass

import freetype

SCHRIFT_ORDNER = ("/usr/share/fonts", "/usr/local/share/fonts", "~/.fonts", "~/.local/share/fonts")
ENDUNGEN = (".ttf", ".otf", ".ttc", ".otc")
# Familien, die es oft nicht gibt, und ihre metrisch gleichen Ersatzfamilien
ERSATZ = {
    "arial": "liberation sans", "helvetica": "liberation sans", "calibri": "carlito", "cambria": "caladea",
    "times new roman": "liberation serif", "times": "liberation serif", "courier new": "liberation mono", "courier": "liberation mono",
    "segoe ui": "dejavu sans", "tahoma": "dejavu sans", "verdana": "dejavu sans", "georgia": "dejavu serif",
}
STANDARD = ("liberation sans", "dejavu sans", "carlito")
# Qt-Wahl für Familien, die auf diesem System fehlen und die Fontconfig-Regeln nicht abdecken: so trifft der Kern dieselbe Ersatzschrift wie die Anzeige
QT_ERSATZ = {"book antiqua": "noto sans", "garamond": "noto serif", "bookman old style": "urw bookman", "palatino linotype": "p052"}


def ersatz_von_qt(familie: str) -> tuple[str, ...]:
    """Die Ersatzfamilie, die Qt für ``familie`` wählt (leer, wenn sie nicht in ``QT_ERSATZ`` steht)."""
    return (QT_ERSATZ[familie],) if familie in QT_ERSATZ else ()


@dataclass(frozen=True)
class Schnitt:
    familie: str
    pfad: str
    index: int
    fett: bool
    kursiv: bool
    gewicht: int = 400          # aus dem Namen des Schnitts geschätzt (Bold = 700), für die Wahl nach Gewicht


class SchriftDatenbank:
    def __init__(self, ordner: tuple[str, ...] = SCHRIFT_ORDNER):
        self._ordner = [os.path.expanduser(o) for o in ordner]
        self._schnitte: dict[str, list[Schnitt]] | None = None

    def _lesen(self) -> dict[str, list[Schnitt]]:
        if self._schnitte is not None:
            return self._schnitte
        res: dict[str, list[Schnitt]] = {}
        extra = os.environ.get("LUNIVO_SCHRIFTEN")
        for wurzel in self._ordner + ([extra] if extra else []):
            for d, _u, dateien in os.walk(wurzel):
                for name in dateien:
                    if not name.lower().endswith(ENDUNGEN):
                        continue
                    pfad = os.path.join(d, name)
                    try:
                        n = freetype.Face(pfad).num_faces
                    except Exception:
                        continue
                    for i in range(max(1, n)):
                        try:
                            f = freetype.Face(pfad, i)
                            fam, stil = (f.family_name or b"").decode("utf-8", "replace"), (f.style_name or b"").decode("utf-8", "replace").lower()
                            flags = f.style_flags
                        except Exception:
                            continue
                        if not fam:
                            continue
                        fett = bool(flags & freetype.FT_STYLE_FLAG_BOLD) or "bold" in stil
                        kursiv = bool(flags & freetype.FT_STYLE_FLAG_ITALIC) or "italic" in stil or "oblique" in stil
                        res.setdefault(fam.lower(), []).append(Schnitt(fam, pfad, i, fett, kursiv, 700 if fett else 400))
        self._schnitte = res
        return res

    def familien(self) -> list[str]:
        return sorted({s[0].familie for s in self._lesen().values()}, key=str.lower)

    def hat_familie(self, familie: str) -> bool:
        return familie.lower() in self._lesen()

    def finden(self, familie: str, gewicht: int = 400, kursiv: bool = False) -> Schnitt:
        """Der Schnitt, der Familie, Gewicht (ab 600 fett) und Kursiv am besten trifft; ohne die Familie ihr Ersatz, sonst die Standardschrift."""
        db = self._lesen()
        schluessel = familie.lower().strip()
        from lunivo_writer.core.textlayout.fontconfig import familien_liste
        for k in (*familien_liste(schluessel), *ersatz_von_qt(schluessel), ERSATZ.get(schluessel, ""), *STANDARD):
            if k in db:
                break
        else:
            if not db:
                raise LookupError("keine Schriftdateien gefunden")
            k = next(iter(db))
        fett = gewicht >= 600
        return min(db[k], key=lambda s: (s.fett != fett) * 2 + (s.kursiv != kursiv) + ("condensed" in s.pfad.lower() or "narrow" in s.pfad.lower()) * 0.5)


standard_datenbank = SchriftDatenbank()
