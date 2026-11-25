"""Die Schriftdatenbank des Kerns: Sie ist die einzige Quelle dafür, welche Schriften es gibt und welche Datei zu einer Familie, einem Gewicht und Kursiv gehört.

Die Schriftdateien der üblichen Ordner werden einmal mit FreeType gelesen. Jeder Schnitt ist unter allen Namen auffindbar, unter denen Auswahllisten ihn führen:
Familie, Typografie-Familie, Voll-Name und „Familie Schnitt“ (zum Beispiel „Inter Light“). Die Auswahl der Oberfläche zeigt ``familien()``; was dort steht, kann der Kern
setzen und zeichnen. Fehlt eine Familie, gilt ihr Ersatz (``ersatz.py``)."""
from __future__ import annotations

import os
from dataclasses import dataclass

import freetype

from lunivo_writer.infrastruktur.schriften.schriften import schrift_ordner

from .ersatz import ersatzfamilien

ENDUNGEN = (".ttf", ".otf", ".ttc", ".otc")
_STILWOERTER_OHNE_BEDEUTUNG = ("regular", "normal", "italic", "oblique", "bold", "roman", "book")
_NAMEN_IDS = (1, 4, 16)                         # Familie, Voll-Name, Typografie-Familie


@dataclass(frozen=True)
class Schnitt:
    """Ein Schnitt einer Familie in einer Schriftdatei."""
    familie: str
    pfad: str
    index: int
    fett: bool
    kursiv: bool
    gewicht: int = 400


def _namen_der_schrift(face) -> list[str]:
    """Die Namen aus der Namenstabelle, unter denen die Schrift in Listen stehen kann."""
    namen: list[str] = []
    try:
        for k in range(face.sfnt_name_count):
            eintrag = face.get_sfnt_name(k)
            if eintrag.name_id not in _NAMEN_IDS:
                continue
            try:
                text = eintrag.string.decode("utf-16-be" if eintrag.platform_id in (0, 3) else "latin-1", "replace").strip()
            except Exception:
                continue
            if text and text not in namen:
                namen.append(text)
    except Exception:
        pass
    return namen


def _schnitte_der_datei(pfad: str):
    """Alle Schnitte einer Schriftdatei als ``(Schnitt, weitere Namen)``; nicht lesbare Dateien liefern nichts."""
    try:
        anzahl = freetype.Face(pfad).num_faces
    except Exception:
        return
    for index in range(max(1, anzahl)):
        try:
            face = freetype.Face(pfad, index)
            familie = (face.family_name or b"").decode("utf-8", "replace")
            stil = (face.style_name or b"").decode("utf-8", "replace").lower()
            flags = face.style_flags
        except Exception:
            continue
        if not familie:
            continue
        fett = bool(flags & freetype.FT_STYLE_FLAG_BOLD) or "bold" in stil
        kursiv = bool(flags & freetype.FT_STYLE_FLAG_ITALIC) or "italic" in stil or "oblique" in stil
        schnitt = Schnitt(familie, pfad, index, fett, kursiv, 700 if fett else 400)
        namen = _namen_der_schrift(face)
        zusatz = " ".join(w for w in stil.split() if w not in _STILWOERTER_OHNE_BEDEUTUNG)
        if zusatz:
            namen.append(f"{familie} {zusatz}")
        yield schnitt, namen


class SchriftDatenbank:
    def __init__(self, ordner: tuple[str, ...] | None = None):
        self._ordner = [os.path.expanduser(o) for o in (schrift_ordner() if ordner is None else ordner)]
        self._index: dict[str, list[Schnitt]] | None = None

    def _gelesen(self) -> dict[str, list[Schnitt]]:
        if self._index is not None:
            return self._index
        index: dict[str, list[Schnitt]] = {}
        zusatz = os.environ.get("LUNIVO_SCHRIFTEN")
        for wurzel in self._ordner + ([zusatz] if zusatz else []):
            for ordner, _unterordner, dateien in os.walk(wurzel):
                for datei in dateien:
                    if not datei.lower().endswith(ENDUNGEN):
                        continue
                    for schnitt, namen in _schnitte_der_datei(os.path.join(ordner, datei)):
                        for name in (schnitt.familie, *namen):
                            liste = index.setdefault(name.lower(), [])
                            if schnitt not in liste:
                                liste.append(schnitt)
        self._index = index
        return index

    def familien(self) -> list[str]:
        """Die Familien aller gefundenen Schriften, alphabetisch: das, was die Auswahl der Oberfläche anbietet."""
        return sorted({s.familie for liste in self._gelesen().values() for s in liste}, key=str.lower)

    def hat_familie(self, familie: str) -> bool:
        return self._schluessel(familie) in self._gelesen()

    def _schluessel(self, familie: str) -> str:
        schluessel = familie.lower().strip()
        if schluessel not in self._gelesen() and schluessel.endswith("]") and "[" in schluessel:        # „Nimbus Sans [urw]“: Herstellerzusatz mancher Listen
            schluessel = schluessel[:schluessel.rindex("[")].strip()
        return schluessel

    def finden(self, familie: str, gewicht: int = 400, kursiv: bool = False) -> Schnitt:
        """Der Schnitt, der Familie, Gewicht (ab 600 fett) und Kursiv am besten trifft; ohne die Familie ihr Ersatz."""
        index = self._gelesen()
        if not index:
            raise LookupError("keine Schriftdateien gefunden")
        name = next((k for k in ersatzfamilien(self._schluessel(familie)) if k in index), None) or next(iter(index))
        fett = gewicht >= 600
        return min(index[name], key=lambda s: (s.fett != fett) * 2 + (s.kursiv != kursiv) + ("condensed" in s.pfad.lower() or "narrow" in s.pfad.lower()) * 0.5)


standard_datenbank = SchriftDatenbank()
