"""ODT schreiben: ``styles.xml`` — Standardschrift, Seitenvorlage (Größe, Ränder, Hintergrund), Kopf- und Fußzeile samt Bildern.

Kopf und Fuß laufen über dieselbe Tabelle ``_KOPF_FUSS``; „außen“/„innen“ wird als gespiegelte linke Seite geschrieben.
"""
from __future__ import annotations

from xml.sax.saxutils import escape

from PySide6.QtGui import QTextDocument

from lunivo_writer.models.page import HeaderFooter, PageSettings
from lunivo_writer.services.odt_schreiben_basis import _NS, _frei_rahmen, _frei_stil, _mm

_AUSRICHTUNG = {"left": "start", "center": "center", "right": "end", "justify": "justify"}
ODF_ZAHL = {"dezimal": "1", "klein": "a", "gross": "A", "roem_klein": "i", "roem_gross": "I"}       # Zahlenart der Seitenzahl
_FELDER = ("{PAGE}", "{PAGES}")
_FELD_XML = {"{PAGE}": '<text:page-number text:select-page="current">1</text:page-number>', "{PAGES}": "<text:page-count>1</text:page-count>"}
_BILD_ORTE = ("kopf", "fuss", "kopf1", "fuss1")
# (ODF-Name, Seitenattribut, Stilname-Anfang, Ort der Bilder, Ort der Bilder auf der ersten Seite, Randseite des Abstands)
_KOPF_FUSS = (("header", "header", "Kopf", "kopf", "kopf1", "bottom"),
              ("footer", "footer", "Fuss", "fuss", "fuss1", "top"))
# Absatzstile je Zeile: (Namensende, Präfix des Seitenattributs, Seitenart 1 = rechts/ungerade, 2 = links/gerade)
_STIL_ARTEN = (("", "", 1), ("Erste", "first_", 1), ("Links", "", 2), ("Gerade", "even_", 2))
_PUFFER_MM = 5                                 # Abstand zwischen Kopf-/Fußzeilenbereich und Text


def _absatz(hf: HeaderFooter, stil: str, rahmen: str = "") -> str:
    """Kopf-/Fußzeilentext als ODF-Absätze; {PAGE} und {PAGES} werden zu Feldern. ``rahmen`` (frei positionierte Bilder) hängt am
    ersten Absatz."""
    zeilen = []
    for zeile in hf.text.split("\n"):
        teile, rest = [], zeile
        while rest:
            pos = [(rest.find(t), t) for t in _FELDER if rest.find(t) >= 0]
            if not pos:
                teile.append(escape(rest))
                break
            i, t = min(pos)
            teile.append(escape(rest[:i]))
            teile.append(_FELD_XML[t])
            rest = rest[i + len(t):]
        zeilen.append(f'<text:p text:style-name="{stil}">{"" if zeilen else rahmen}{"".join(teile)}</text:p>')
    return "".join(zeilen)


def _standard(doc: QTextDocument | None) -> str:
    """Standardschrift des Dokuments als Vorgabe für alle Absätze, dazu die Vorlage „Standard“."""
    f = doc.defaultFont() if doc is not None else None
    name = escape(f.family(), {'"': "&quot;"}) if f is not None else "Liberation Sans"
    groesse = (f.pointSizeF() if f is not None and f.pointSizeF() > 0 else 11.0)
    return (f'<style:default-style style:family="paragraph"><style:text-properties style:font-name="{name}" fo:font-family="{name}" '
            f'fo:font-size="{groesse:g}pt"/></style:default-style>'
            '<style:style style:name="Standard" style:family="paragraph" style:class="text"/>')


def _bilder_rahmen(page: PageSettings, bilder: dict[str, bytes]) -> tuple[dict[str, str], list[str]]:
    """Bilder in Kopf-/Fußzeile → (Rahmen-XML je Ort, Rahmenvorlagen); die Bilddaten kommen nach ``bilder``."""
    rahmen: dict[str, str] = {}
    rahmen_stile: list[str] = []
    for a in page.bilder or []:
        if a.get("bild") is None or a.get("bild").isNull() or a.get("ort") not in _BILD_ORTE:
            continue
        nr = len(rahmen_stile) + 1
        rahmen_stile.append(_frei_stil(f"KF{nr}", a))
        rahmen[a["ort"]] = rahmen.get(a["ort"], "") + _frei_rahmen(a, a["bild"], 100 + nr, f"KF{nr}", bilder)
    return rahmen, rahmen_stile


def _hat_inhalt(hf: HeaderFooter, ort: str, rahmen: dict[str, str]) -> bool:
    return not hf.is_empty() or ort in rahmen


def _aktiv(page: PageSettings, rahmen: dict[str, str], art: tuple) -> bool:
    """Gibt es irgendwo (normal, erste Seite, gerade Seiten) einen Kopf bzw. Fuß?"""
    _tag, attr, _stil, ort, ort1, _kante = art
    return (_hat_inhalt(getattr(page, attr), ort, rahmen)
            or (page.diff_first and _hat_inhalt(getattr(page, "first_" + attr), ort1, rahmen))
            or (page.diff_even and not getattr(page, "even_" + attr).is_empty()))


def _bereich_stil(page: PageSettings, art: tuple, aktiv: bool, rand: float, seitenrand: float) -> str:
    """``style:header-style`` bzw. ``style:footer-style``: Mindesthöhe = Rest zwischen Rand und Text."""
    tag, _attr, _stil, _ort, _ort1, kante = art
    if not aktiv:
        return f"<style:{tag}-style/>"
    return (f'<style:{tag}-style><style:header-footer-properties fo:min-height="{_mm(seitenrand - rand - _PUFFER_MM)}" '
            f'fo:margin-{kante}="{_PUFFER_MM}mm"/></style:{tag}-style>')


def _ausrichtungs_stile(page: PageSettings) -> list[str]:
    """Absatzvorlagen der Kopf-/Fußzeilen. „außen“/„innen“: rechte (ungerade) Seiten in style:header, linke (gerade) in
    style:header-left mit gespiegelter Ausrichtung."""
    from lunivo_writer.editor.seite import seitenzahl as SZ
    stile = []
    for ende, vorsatz, n in _STIL_ARTEN:
        for _tag, attr, stilname, _ort, _ort1, _kante in _KOPF_FUSS:
            hf = getattr(page, vorsatz + attr)
            stile.append(f'<style:style style:name="Lunivo{stilname}{ende}" style:family="paragraph"><style:paragraph-properties '
                         f'fo:text-align="{_AUSRICHTUNG.get(SZ.ausrichtung(hf.align, n), "center")}"/></style:style>')
    return stile


def _gespiegelt(hf: HeaderFooter) -> bool:
    return hf.align in ("aussen", "innen") and not hf.is_empty()


def _master_teile(page: PageSettings, rahmen: dict[str, str], art: tuple, aktiv: bool) -> list[str]:
    """Die Elemente ``header``/``header-left``/``header-first`` (bzw. ``footer…``) der Seitenvorlage."""
    tag, attr, stil, ort, ort1, _kante = art
    hf, gerade, erste = getattr(page, attr), getattr(page, "even_" + attr), getattr(page, "first_" + attr)
    teile = []
    if _hat_inhalt(hf, ort, rahmen):
        teile.append(f"<style:{tag}>{_absatz(hf, 'Lunivo' + stil, rahmen.get(ort, ''))}</style:{tag}>")
    if page.diff_even and not gerade.is_empty():
        teile.append(f"<style:{tag}-left>{_absatz(gerade, 'Lunivo' + stil + 'Gerade', '')}</style:{tag}-left>")
    elif _gespiegelt(hf):
        teile.append(f"<style:{tag}-left>{_absatz(hf, 'Lunivo' + stil + 'Links', rahmen.get(ort, ''))}</style:{tag}-left>")
    if page.diff_first and aktiv:
        teile.append(f"<style:{tag}-first>{_absatz(erste, 'Lunivo' + stil + 'Erste', rahmen.get(ort1, ''))}</style:{tag}-first>")
    return teile


def _seitenlayout(page: PageSettings, rand_oben: float, rand_unten: float, kopf_stil: str, fuss_stil: str) -> str:
    hintergrund = f' fo:background-color="{escape(page.color)}"' if page.color else ""
    return (f'<style:page-layout style:name="LunivoSeite">'
            f'<style:page-layout-properties fo:page-width="{_mm(page.width_mm)}" fo:page-height="{_mm(page.height_mm)}" '
            f'style:print-orientation="{"landscape" if page.landscape else "portrait"}" '
            f'fo:margin-top="{_mm(rand_oben)}" fo:margin-bottom="{_mm(rand_unten)}" '
            f'fo:margin-left="{_mm(page.margin_left_mm)}" fo:margin-right="{_mm(page.margin_right_mm)}"{hintergrund}'
            f' style:num-format="{ODF_ZAHL.get(page.seiten_format, "1")}"/>'
            f"{kopf_stil}{fuss_stil}</style:page-layout>")


def _styles_xml(page: PageSettings, doc: QTextDocument | None = None, bilder: dict[str, bytes] | None = None) -> str:
    bilder = {} if bilder is None else bilder
    rahmen, rahmen_stile = _bilder_rahmen(page, bilder)
    kopf, fuss = (_aktiv(page, rahmen, art) for art in _KOPF_FUSS)
    # ODF misst den oberen Rand bis zur Kopfzeile; Lunivo bis zum Text. Mit Kopfzeile: Rand = Kopfabstand,
    # Kopfzeilenbereich = Rest bis zum Text.
    rand_oben = min(page.kopf_abstand_mm, page.margin_top_mm) if kopf else page.margin_top_mm
    rand_unten = min(page.fuss_abstand_mm, page.margin_bottom_mm) if fuss else page.margin_bottom_mm
    kopf_stil = _bereich_stil(page, _KOPF_FUSS[0], kopf, rand_oben, page.margin_top_mm)
    fuss_stil = _bereich_stil(page, _KOPF_FUSS[1], fuss, rand_unten, page.margin_bottom_mm)
    seite = [t for art, aktiv in zip(_KOPF_FUSS, (kopf, fuss)) for t in _master_teile(page, rahmen, art, aktiv)]
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            f'<office:document-styles {_NS} office:version="1.3">'
            f'<office:styles>{_standard(doc)}{"".join(_ausrichtungs_stile(page))}</office:styles>'
            f'<office:automatic-styles>{"".join(rahmen_stile)}{_seitenlayout(page, rand_oben, rand_unten, kopf_stil, fuss_stil)}'
            "</office:automatic-styles>"
            '<office:master-styles><style:master-page style:name="Standard" style:page-layout-name="LunivoSeite">'
            f'{"".join(seite)}</style:master-page></office:master-styles></office:document-styles>')
