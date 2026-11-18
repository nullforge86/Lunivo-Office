"""Seitenaufteilung, PDF-Ausgabe und Drucken mit Kopf-/Fußzeile und Seitenzahlen.

Das Dokument wird bei 96 dpi gesetzt (wie im Editor); beim Ausgeben wird der
Maler auf die Auflösung des Ausgabegeräts hochgerechnet. So stimmt der
Seitenumbruch auf dem Bildschirm mit dem im PDF überein.
"""
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QByteArray, QMarginsF, QRectF, QSizeF, Qt
from PySide6.QtGui import (
    QColor, QFont, QImage, QPageLayout, QPageSize, QPainter, QPdfWriter, QPen, QTextCursor, QTextDocument, QTextFormat,
)
from PySide6.QtPrintSupport import QPrinter

from lunivo_writer.adapter.qt.rendering import QtRenderBackend
from lunivo_writer.core.geometry import Point, Rect
from lunivo_writer.core.rendering import RenderBackend, Style
from lunivo_writer.kern.farben import Farbe
from lunivo_writer.editor.seite import zeilennummern
from lunivo_writer.editor.seite.blasen_druck import blasen_geometrie, blasen_pro_seite, blasen_zeichnen
from lunivo_writer.editor.seite.fussnoten import fussnoten_am_fuss, fussnoten_am_seitenende, noten_anhaengen, notenlinks_sammeln
from lunivo_writer.editor.seite.seiten_aufteilung_deko import (
    _bf_ohne, _draw_hf, _druckmarken, _expand, _formularteile_ausblenden, _hf_effekt, _inhalt_zeichnen,
    _ohne_hervorhebungen, _ohne_hintergruende, _ohne_links, _text_schwarz, _textmarken_klammern,
    absatz_zusatz_zeichnen, frei_zeichnen, seiten_liste, seitenschmuck,
)
from lunivo_writer.editor.seite.pdf_struktur import gliederung_schreiben, kommentarstellen, lesezeichen_sammeln
from lunivo_writer.editor.seite.silbentrennung import silben_einfuegen
from lunivo_writer.modelle.seite import HeaderFooter, PageSettings, mm_to_px

# Wo die Namen früher standen: Aufrufer und Tests holen sie weiter aus diesem Modul.
from lunivo_writer.editor.seite.fussnoten import zeilenbereiche as _zeilenbereiche        # noqa: F401
from lunivo_writer.editor.seite.seiten_aufteilung_deko import absatzrahmen_zeichnen               # noqa: F401

KOPF_HOEHE_MM = 10                                   # Höhe der Kopf- und Fußzeile; der Abstand zum Blattrand kommt aus der Seite
FUSSNOTEN_TRENNLINIE = 0.33                                      # Länge des Trennstrichs über den Fußnoten (Teil der Textbreite)


_DEV = None


def layout_device() -> QImage:
    """Ein Gerät mit festen 96 dpi, an dem alle Dokumente gesetzt werden."""
    global _DEV
    if _DEV is None:
        _DEV = QImage(1, 1, QImage.Format_RGB32)
        _DEV.setDotsPerMeterX(round(96 / 0.0254))
        _DEV.setDotsPerMeterY(round(96 / 0.0254))
    return _DEV


_ZOOM_DEV: dict[int, QImage] = {}


def zoom_device(faktor: float) -> QImage:
    """Ein Gerät mit 96 dpi × Zoom: Text, Ränder, Tabellen und Bilder werden beim Setzen mitskaliert."""
    key = round(faktor * 1000)
    if key == 1000:
        return layout_device()
    d = _ZOOM_DEV.get(key)
    if d is None:
        d = QImage(1, 1, QImage.Format_RGB32)
        dpm = round(96 * key / 1000 / 0.0254)
        d.setDotsPerMeterX(dpm); d.setDotsPerMeterY(dpm)
        if len(_ZOOM_DEV) > 40:
            _ZOOM_DEV.clear()
        _ZOOM_DEV[key] = d
    return d


def bind_layout(qdoc: QTextDocument, faktor: float = 1.0) -> None:
    qdoc.documentLayout().setPaintDevice(zoom_device(faktor))


def ausgabe_seiten(logisch: int, page: PageSettings) -> int:
    """Seiten der Ausgabe: bei mehreren Spalten füllen je so viele „logische“ Spaltenseiten eine Blattseite."""
    return max(1, -(-max(1, logisch) // max(1, int(page.spalten))))


def paginated_copy(qdoc: QTextDocument, page: PageSettings, noten: dict | None = None, silben: bool | None = None,
                   einspaltig: bool = False, versteckt: bool = False, fussnoten: bool | str = True, lese_luft: bool = False,
                   blaetter: bool = False) -> QTextDocument:
    """``blaetter``: das ganze Dokument in Blattkoordinaten setzen (Seitenlauf mit allen Abschnitten), statt im Textfluss eines Abschnitts."""
    d = qdoc.clone()
    from lunivo_writer.editor.layout.seitenlauf import LAUF_STANDARD, Seitenlauf
    if blaetter:
        d.setDocumentLayout(Seitenlauf(d, page, 1.0, fluss=False, lazy=True))
    elif LAUF_STANDARD:
        d.setDocumentLayout(Seitenlauf(d, page, 1.0, fluss=True, lazy=True))           # dieselbe Anordnung wie im Editor, in den Koordinaten des Textflusses
    from lunivo_writer.editor.seite import querblatt
    querblatt.zuruecknehmen(d)                          # der Zusatz für verschieden große Blätter gilt nur in der Anzeige
    if not lese_luft:                                   # Druck, PDF, Seitenzahl: ohne den Zusatzabstand der Lesehilfe (nur die Anzeige im Editor behält ihn)
        from lunivo_writer.editor.seite import lese_zeilenluft
        lese_zeilenluft.zuruecknehmen(d)
    bind_layout(d)
    if not versteckt:                                   # ausgeblendeter Text zählt weder für Seiten noch für den Druck
        from lunivo_writer.editor.seite.anzeige_extra import versteckte_entfernen
        versteckte_entfernen(d)
    am_fuss = (True if blaetter else fussnoten) and fussnoten_am_fuss(page, noten)
    if blaetter and am_fuss:
        d.documentLayout().fussnoten = dict(noten.get("f") or {})        # der Seitenlauf lässt unten Platz für sie
    noten_anhaengen(d, noten, ("e",) if am_fuss else ("f", "e"))
    if (page.silbentrennung if silben is None else silben):
        silben_einfuegen(d, page.silben_sprache)
    _abschnittsbeginn_markieren(d)
    root = d.rootFrame()
    ff = root.frameFormat()
    ff.setMargin(0)
    ff.setTopMargin(page.erste_seite_versatz_px())         # lange Kopfzeile: Text der ersten Seite beginnt darunter
    root.setFrameFormat(ff)
    d.setDocumentMargin(0)
    root.setFrameFormat(ff)                               # setDocumentMargin setzt den Rahmen zurück: danach wieder setzen
    d.setPageSize(QSizeF(page.content_width_px if einspaltig else page.spalten_breite_px, page.content_height_px))
    if am_fuss and not blaetter and fussnoten != "spaeter":                 # „spaeter“: render() ruft es nach den übrigen Änderungen selbst auf
        fussnoten_am_seitenende(d, page, noten)
    if blaetter:
        return d                                              # Umbruchregeln und Abstände am Seitenanfang kennt der Seitenlauf selbst
    from lunivo_writer.editor.seite import seitenfluss
    seitenfluss.anwenden(d, page.content_height_px)        # Umbruchregeln und kein Abstand am Seitenanfang, auch für Dokumente, die nie im Editor lagen
    return d


def _abschnittsbeginn_markieren(d: QTextDocument) -> None:
    """Nur in der Kopie: Der Absatz nach einem Abschnittsumbruch („nächste/gerade/ungerade Seite“) beginnt eine neue Seite."""
    from lunivo_writer.editor.seite import abschnitte as AB
    b = d.firstBlock()
    while b.isValid():
        e = AB.lesen(b.blockFormat())
        n = b.next()
        if e and e[0] != "fortlaufend" and n.isValid():
            c = QTextCursor(n)
            bf = c.blockFormat(); bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore); c.setBlockFormat(bf)
        b = n


def page_count(qdoc: QTextDocument, page: PageSettings) -> int:
    return ausgabe_seiten(paginated_copy(qdoc, page).pageCount(), page)


def _start_nummer(page: PageSettings) -> int:
    """Angezeigte Seitennummer vor der ersten Seite: „Beginnen mit“ der Einrichtung."""
    return page.seiten_start - 1 if page.seiten_start > 0 else 0


def _kapitel_liste(d: QTextDocument, page: PageSettings) -> list[str]:
    """Kapitelnummer je Seite für Kopf-/Fußzeile; leer ohne Kapitelebene."""
    if not page.kapitel_ebene:
        return []
    from lunivo_writer.editor.seite import seitenzahl as SZ
    return SZ.kapitel_je_seite(d, page.kapitel_ebene, SZ.seitenwechsel(d, page.content_height_px))


def _kapitel_von(kapitel: list[str], n: int, spalten: int) -> str:
    return kapitel[min(len(kapitel) - 1, n * spalten - 1)] if kapitel else ""


def _nur_formular(page: PageSettings, opt: dict) -> tuple[PageSettings, dict]:
    """Nur die Feldinhalte (für vorgedruckte Formulare): kein Seitenschmuck, keine Kopf-/Fußzeile."""
    page = page.copy()
    page.border = None; page.watermark = None; page.color = ""
    page.header = HeaderFooter(); page.footer = HeaderFooter(); page.first_header = HeaderFooter(); page.first_footer = HeaderFooter()
    page.even_header = HeaderFooter(); page.even_footer = HeaderFooter()
    return page, dict(opt, hintergrund=False, textgrenzen=False, zuschnitt=False, balken=None, blasen=None)


def _inhalt_anpassen(d: QTextDocument, opt: dict) -> None:
    """Inhalt der Ausgabekopie nach den Optionen: Formulardaten, Feldcodes, Zeichnungen, Lücken."""
    from lunivo_writer.editor.seite import anzeige_extra as AX
    if opt.get("nur_formular"):
        from lunivo_writer.editor.dokument.formular import nur_formulardaten
        nur_formulardaten(d)
    if opt.get("felder_code"):
        AX.feldcodes_einsetzen(d)
    if opt.get("zeichnungen") is False:
        AX.zeichnungen_entfernen(d)
    if opt.get("luecken", True):
        from lunivo_writer.editor.dokument.vorlagen import luecken_entfernen
        luecken_entfernen(d)


def _darstellung_anpassen(d: QTextDocument, opt: dict) -> None:
    """Darstellung der Ausgabekopie nach den Optionen: Hintergründe, Steuerelemente, Farben, Hervorhebungen, Verweise."""
    if opt.get("hintergrund") is False:
        _ohne_hintergruende(d)
    if opt.get("steuerelemente") is False or opt.get("platzhalter") is False:
        _formularteile_ausblenden(d, opt.get("steuerelemente") is False, opt.get("platzhalter") is False)
    if opt.get("schwarz"):
        _text_schwarz(d)
    if opt.get("hervorhebungen") is False:
        _ohne_hervorhebungen(d)
    if opt.get("textmarken"):
        _textmarken_klammern(d)
    if opt.get("hyperlinks") is False:
        _ohne_links(d)


def _ausgabekopie(qdoc: QTextDocument, page: PageSettings, opt: dict):
    """Die gesetzte Kopie für Druck/PDF mit allen Optionen; → (Kopie, Silbenfarben). Die Silbenfarben müssen bis zum Zeichnen leben."""
    d = paginated_copy(qdoc, page, opt.get("noten"), versteckt=bool(opt.get("versteckt")), fussnoten="spaeter")
    _inhalt_anpassen(d, opt)
    _darstellung_anpassen(d, opt)
    silbenfarben = None
    if opt.get("silbenfarben"):
        from lunivo_writer.editor.text.silbenfarben import SilbenFarben
        silbenfarben = SilbenFarben(d, opt["silbenfarben"])
    if fussnoten_am_fuss(page, opt.get("noten")):
        fussnoten_am_seitenende(d, page, opt["noten"])
    return d, silbenfarben


def _seitenliste(d: QTextDocument, page: PageSettings, total: int, first: int, last: int, opt: dict) -> list[int]:
    liste = seiten_liste(total, first, last, opt)
    if opt.get("nur_seiten") is not None:
        liste = [n for n in liste if n in opt["nur_seiten"]]
    if opt.get("leere") is False:
        leer = _leere_seiten(d, page, total)
        liste = [n for n in liste if n not in leer] or liste[:1]
    return liste


@dataclass
class _Lauf:
    """Was für jede Seite der Ausgabe gleich bleibt."""
    d: QTextDocument
    page: PageSettings
    total: int
    base: QFont
    opt: dict
    ab: dict
    spalten: int
    skala: float
    balken: tuple | None
    nr: int
    geo: dict | None
    blasen: dict
    kapitel: list


def _lauf_vorbereiten(d: QTextDocument, page: PageSettings, total: int, liste: list[int], base: QFont, skala: float, opt: dict) -> _Lauf:
    from lunivo_writer.editor.seite import anzeige_extra as AX
    ab = opt.get("abschnitt") or {}
    balken = None
    if opt.get("balken") in ("links", "rechts", "außen") and d.characterCount() < 400000:
        balken = (opt["balken"], AX.aenderungszeilen(d))
    geo = blasen_geometrie(page, opt)
    # angezeigte Seitennummer: im Abschnitt fortlaufend („nummer“) oder ab „Beginnen mit“
    return _Lauf(d, page, total, base, opt, ab, max(1, int(page.spalten)), skala, balken,
                 ab["nummer"] if "nummer" in ab else _start_nummer(page), geo,
                 blasen_pro_seite(d, page, liste, opt["blasen"]) if geo else {}, _kapitel_liste(d, page))


def _seite_ausgeben(p: QPainter, lauf: _Lauf, n: int) -> None:
    opt, geo, page = lauf.opt, lauf.geo, lauf.page
    p.save()
    p.scale(lauf.skala, lauf.skala)
    if geo:                                              # Seite verkleinert neben die Blasen setzen
        p.save()
        p.translate(geo["x_page"], 0)
        p.scale(geo["f"], geo["f"])
    zeichne_seite(p, lauf.d, page, n, lauf.total, lauf.base, opt.get("hintergrund") is not False, lauf.balken, lauf.nr,
                  lauf.ab.get("gesamt"), _kapitel_von(lauf.kapitel, n, lauf.spalten))
    if opt.get("textgrenzen") or opt.get("zuschnitt"):
        _druckmarken(p, page, bool(opt.get("textgrenzen")), bool(opt.get("zuschnitt")))
    if geo:
        p.restore()
        blasen_zeichnen(p, lauf.blasen.get(n, []), geo)
    p.restore()


def _pdf_ergebnisse(opt: dict, d: QTextDocument, page: PageSettings, liste: list[int], spalten: int, ort=None) -> None:
    """Stellen für Lesezeichen, Kommentar-Notizen und Sprungverweise der PDF (``export_pdf`` trägt sie danach ein)."""
    ch = page.content_height_px
    if opt.get("lesezeichen") is not None:
        opt["lesezeichen_ergebnis"] = lesezeichen_sammeln(d, ch, liste, opt["lesezeichen"], spalten, ort)
    if opt.get("kommentare"):
        opt["kommentare_ergebnis"] = kommentarstellen(d, ch, liste, opt["kommentare"], spalten, ort)
    if opt.get("notenlinks"):
        opt["notenlinks_ergebnis"] = notenlinks_sammeln(d, page, liste, ort)


def render(qdoc: QTextDocument, page: PageSettings, device, first: int = 1, last: int | None = None,
           dpi: int | None = None, opt: dict | None = None) -> int:
    """Zeichnet die Seiten first..last auf device (QPdfWriter/QPrinter). → Anzahl Seiten."""
    opt = opt or {}
    if opt.get("nur_formular"):
        page, opt = _nur_formular(page, opt)
    d, _silbenfarben = _ausgabekopie(qdoc, page, opt)
    total = ausgabe_seiten(d.pageCount(), page)
    if opt.get("nur_zaehlen"):
        return total
    last = total if last is None else min(last, total)
    p = opt.get("painter") or QPainter(device)
    liste = _seitenliste(d, page, total, first, last, opt)
    lauf = _lauf_vorbereiten(d, page, total, liste, qdoc.defaultFont(), (dpi or device.logicalDpiX()) / 96.0, opt)
    erste = not lauf.ab.get("weiter")
    for n in liste:
        if not erste:
            device.newPage()
        erste = False
        _seite_ausgeben(p, lauf, n)
    opt["_gedruckt"] = len(liste)
    if not opt.get("painter"):
        p.end()
    _pdf_ergebnisse(opt, d, page, liste, lauf.spalten)
    return total


def _leerseite_davor(i: int, typ: str, gesamt: int) -> int:
    """1, wenn vor dem Abschnitt i eine Leerseite nötig ist („gerade/ungerade Seite“), sonst 0."""
    return 1 if i and ((typ == "gerade" and (gesamt + 1) % 2 == 1) or (typ == "ungerade" and (gesamt + 1) % 2 == 0)) else 0


def _leerseiten_plan(typen: list[str], zaehl: list[int]) -> tuple[list[int], list[int], int]:
    """([Seitenzahl vor dem Abschnitt einschließlich Leerseite], [Leerseite davor 0/1], Seiten insgesamt)."""
    offsets, leer, gesamt = [], [], 0
    for i, (typ, z) in enumerate(zip(typen, zaehl)):
        b = _leerseite_davor(i, typ, gesamt)
        offsets.append(gesamt + b); leer.append(b)
        gesamt += b + z
    return offsets, leer, gesamt


def _erste_nummern(teile: list, zaehl: list[int], leer: list[int]) -> list[int]:
    """Angezeigte Nummer vor dem ersten Blatt je Abschnitt: „Beginnen mit“ setzt neu an, sonst geht es nach dem vorigen Teil weiter."""
    nummern: list[int] = []
    for i, (_d, ps, _t) in enumerate(teile):
        weiter = nummern[-1] + zaehl[i - 1] + leer[i] if i else 0
        nummern.append(ps.seiten_start - 1 if ps.seiten_start > 0 else weiter)
    return nummern


def _startteil(zaehl: list[int], offsets: list[int], leer: list[int], first: int, last: int) -> int:
    """Erster Abschnitt, der wirklich gedruckt wird: sein Papier gilt schon beim Start."""
    for i, z in enumerate(zaehl):
        if max(1, first - offsets[i]) <= min(z, last - offsets[i]) or (leer[i] and first <= offsets[i] <= last):
            return i
    return 0


_VERSCHIEBER = {                                         # PDF-Ergebnisse eines Abschnitts um die schon gedruckten Seiten verschieben
    "lesezeichen_ergebnis": lambda e, g: (e[0], e[1], e[2] + g),
    "kommentare_ergebnis": lambda e, g: (e[0] + g, e[1], e[2]),
    "notenlinks_ergebnis": lambda e, g: dict(e, seite=e["seite"] + g, ziel_seite=e["ziel_seite"] + g),
}


@dataclass
class _Folge:
    """Stand beim Ausgeben mehrerer Abschnitte hintereinander."""
    device: object
    painter: QPainter
    layout: object
    opt: dict
    first: int
    last: int
    dpi: int | None
    gesamt: int
    start: int
    leer: list[int]
    gedruckt: int = 0
    sammlung: dict = None


def _papier_wechseln(f: _Folge, i: int, ps: PageSettings) -> None:
    """Das Papier eines Abschnitts gilt erst ab seiner ersten gedruckten Seite (der erste Teil ist schon eingestellt)."""
    if f.layout and i != f.start:
        f.layout(ps)


def _abschnitt_drucken(f: _Folge, i: int, d: QTextDocument, ps: PageSettings, o: int, z: int, nummer: int) -> None:
    """Leerseite vor dem Abschnitt (falls nötig) und seine Seiten im gewünschten Bereich."""
    if f.leer[i] and f.first <= o <= f.last:
        _papier_wechseln(f, i, ps)
        if f.gedruckt:
            f.device.newPage()
        f.gedruckt += 1
    lo, hi = max(1, f.first - o), min(z, f.last - o)
    if lo > hi:
        return
    _papier_wechseln(f, i, ps)
    sub = dict(f.opt, painter=f.painter, abschnitt={"offset": o, "nummer": nummer, "gesamt": f.gesamt, "weiter": f.gedruckt > 0})
    if f.opt.get("nur_seiten") is not None:
        sub["nur_seiten"] = {n - o for n in f.opt["nur_seiten"]}
    render(d, ps, f.device, lo, hi, f.dpi, sub)
    for k, verschieben in _VERSCHIEBER.items():
        f.sammlung[k].extend(verschieben(e, f.gedruckt) for e in sub.get(k) or [])
    f.gedruckt += sub.get("_gedruckt", 0)


def render_dokument(qdoc: QTextDocument, page: PageSettings, device, first: int = 1, last: int | None = None, dpi: int | None = None,
                    opt: dict | None = None, layout=None) -> int:
    """Wie render(), aber mit mehreren Abschnitten: jeder Abschnitt wird mit seiner eigenen Seitengröße, seinen Rändern, Spalten und
    Kopf-/Fußzeilen gesetzt; die Seitennummern laufen durch. `layout(PageSettings)` stellt das Papier des Geräts um (QPdfWriter/QPrinter).
    → Seitenzahl der gesamten Ausgabe (mit eingeschobenen Leerseiten bei „gerade/ungerade Seite“)."""
    from lunivo_writer.editor.seite import abschnitte as AB
    opt = opt if opt is not None else {}
    teile, hinweise = AB.teile(qdoc, page)
    opt["abschnitts_hinweise"] = hinweise
    if _blattweise():
        return render_blaetter(qdoc, page, device, first, last, dpi, opt, layout)
    if len(teile) == 1:
        return render(qdoc, page, device, first, last, dpi, opt)
    zaehl = [render(d, ps, device, opt=dict(opt, nur_zaehlen=True)) for d, ps, _t in teile]
    offsets, leer, gesamt = _leerseiten_plan([t for _d, _ps, t in teile], zaehl)
    nummern = _erste_nummern(teile, zaehl, leer)
    last = gesamt if last is None else min(last, gesamt)
    start = _startteil(zaehl, offsets, leer, first, last)
    if layout:
        layout(teile[start][1])
    f = _Folge(device, QPainter(device), layout, opt, first, last, dpi, gesamt, start, leer, sammlung={k: [] for k in _VERSCHIEBER})
    for i, (d, ps, _typ) in enumerate(teile):
        _abschnitt_drucken(f, i, d, ps, offsets[i], zaehl[i], nummern[i])
    f.painter.end()
    opt.update({k: v for k, v in f.sammlung.items() if v})
    return gesamt


# Optionen, die der direkte Blattweg (``render_blaetter``) noch nicht kennt: dann bleibt es beim Weg je Abschnitt.
def _blattweise(qdoc: QTextDocument | None = None, page: PageSettings | None = None, teile: list | None = None, opt: dict | None = None) -> bool:
    """Druck, PDF, Seitenzahl und Seitenbilder gehen über den Seitenlauf (``render_blaetter``); der Weg je Abschnitt bleibt nur als Rückfall, wenn
    der Seitenlauf ausgeschaltet ist (``LUNIVO_SEITENLAUF=0``)."""
    from lunivo_writer.editor.layout.seitenlauf import LAUF_STANDARD
    return bool(LAUF_STANDARD)


def _blatt_zeichnen(p: QPainter, d: QTextDocument, bl, n: int, total: int, nummer: int, base: QFont, frei_alle: dict, opt: dict) -> None:
    """Ein Blatt des Seitenlaufs (Nummer n, 1-basiert; angezeigt als ``nummer``) mit Schmuck, Bildern, Kopf-/Fußzeile, Zeilennummern, Spaltenlinie
    und Text; Ursprung links oben, 96 dpi. Eine Leerseite bleibt weiß."""
    from lunivo_writer.editor.objekte import freie_bilder as FB
    lay = d.documentLayout()
    ps = bl.seite
    blatt = QRectF(bl.x, bl.oben, bl.breite, bl.hoehe)
    if bl.leer:
        return
    p.save()
    p.translate(-bl.x, -bl.oben)                                   # ab hier: Blatt mit Ursprung links oben
    p.save(); p.translate(bl.x, bl.oben)
    seitenschmuck(p, ps, opt.get("hintergrund") is not False, None, "hinten")
    frei = FB.objekte_der_seite(ps, d, n, {n: frei_alle.get(n, [])})
    frei_zeichnen(p, frei, True)
    _kopf_fuss_zeichnen(p, ps, n, nummer - n, total, opt.get("_gesamt"), base, "")
    p.restore()
    info = lay.erg.fussnoten.get(bl.index)
    if info:
        p.save(); p.translate(bl.text_links, bl.oben + bl.text_oben)
        cw = ps.content_width_px
        y0 = bl.text_hoehe - info["hoehe"] + 6
        _fussnoten_trennlinie(QtRenderBackend(p), y0, cw)
        for y, nd, _nid in info["noten"]:
            p.save(); p.translate(0, y); _inhalt_zeichnen(p, nd, QRectF(0, 0, cw, nd.size().height())); p.restore()
        p.restore()
    if ps.zeilennummern:
        p.save()
        f = QFont(base); f.setPixelSize(9)
        rb = QtRenderBackend(p)
        for k, y, h, nr in opt["_zeilennummern"]:
            if k == bl.index:
                rb.draw_text_box(str(nr), Rect(bl.text_links - 48, y, 42, h), f, ZEILENNUMMER_STIL, align="right", wrap=False)
        p.restore()
    p.save(); p.setClipRect(blatt)
    _inhalt_zeichnen(p, d, blatt)
    absatz_zusatz_zeichnen(p, d)
    if opt.get("_balken"):
        _balken_blatt(QtRenderBackend(p), opt["_balken"], bl, n)
    p.restore()
    p.save(); p.translate(bl.x, bl.oben)
    frei_zeichnen(p, frei, False)
    seitenschmuck(p, ps, False, None, "vorn", False)
    sp = lay.plan.bereiche[bl.bereich].spalten
    if ps.spalten_linie and len(sp) > 1:
        rb = QtRenderBackend(p)
        for a, c in zip(sp, sp[1:]):
            x = int(mm_to_px(ps.margin_left_mm) + (a.x + a.breite + c.x) / 2)
            rb.draw_line(Point(x, int(mm_to_px(ps.margin_top_mm))), Point(x, int(mm_to_px(ps.margin_top_mm) + ps.content_height_px)), SPALTENLINIE_STIL)
    if opt.get("textgrenzen") or opt.get("zuschnitt"):
        _druckmarken(p, ps, bool(opt.get("textgrenzen")), bool(opt.get("zuschnitt")))
    p.restore()
    p.restore()


def _gesetzt(qdoc: QTextDocument, page: PageSettings, opt: dict):
    """Das ganze Dokument im Seitenlauf gesetzt: (Kopie, gedruckte Blätter, Index der freien Bilder)."""
    d = paginated_copy(qdoc, page, opt.get("noten"), versteckt=bool(opt.get("versteckt")), blaetter=True)
    _inhalt_anpassen(d, opt)
    _darstellung_anpassen(d, opt)
    if opt.get("silbenfarben"):
        from lunivo_writer.editor.text.silbenfarben import SilbenFarben
        d._silbenfarben = SilbenFarben(d, opt["silbenfarben"])        # muss bis zum Zeichnen leben
    lay = d.documentLayout()
    lay._sicher()
    blaetter = lay.blaetter
    if not d.rootFrame().childFrames():                               # ein Blatt, auf dem nur leere Absätze am Ende stehen, wird nicht gedruckt
        mit_inhalt = [k for n, k in lay.erg.block_blatt.items() if d.findBlockByNumber(n).text().strip(" \t\n")]
        if mit_inhalt:
            blaetter = blaetter[:max(mit_inhalt) + 1]
    return d, blaetter, lay.frei_index()


def _blatt_liste(d: QTextDocument, blaetter: list, total: int, first: int, last: int, opt: dict) -> list[int]:
    """Die Blätter, die ausgegeben werden: Bereich, Auswahl („nur_seiten“), Leerseiten weglassen."""
    liste = seiten_liste(total, first, last, opt)
    if opt.get("nur_seiten") is not None:
        liste = [n for n in liste if n in opt["nur_seiten"]]
    if opt.get("leere") is False:
        lay = d.documentLayout()
        mit_text = {k + 1 for nr, k in lay.erg.block_blatt.items() if d.findBlockByNumber(nr).text().strip(chr(0xfffc) + " \t\n")}
        liste = [n for n in liste if n in mit_text] or liste[:1]
    return liste


def render_blaetter(qdoc: QTextDocument, page: PageSettings, device, first: int, last: int | None, dpi: int | None, opt: dict, layout=None) -> int:
    """Druck/PDF direkt nach den Blättern des Seitenlaufs: das ganze Dokument wird einmal gesetzt (Abschnitte können auf derselben Seite
    weiterlaufen), jedes Blatt mit Schmuck, Bildern, Kopf-/Fußzeile und dem Text in seinen Spalten gezeichnet. → Seitenzahl."""
    if opt.get("nur_formular"):
        page, opt = _nur_formular(page, opt)
    d, blaetter, frei_alle = _gesetzt(qdoc, page, opt)
    total = len(blaetter)
    if opt.get("nur_zaehlen"):
        return total
    last = total if last is None else min(last, total)
    skala = (dpi or device.logicalDpiX()) / 96.0
    p = QPainter(device)
    lay = d.documentLayout()
    geo = blasen_geometrie(page, opt)
    if opt.get("balken") in ("links", "rechts", "außen") and d.characterCount() < 400000:
        from lunivo_writer.editor.seite import anzeige_extra as AX
        opt["_balken"] = (opt["balken"], AX.aenderungszeilen(d))
    gewaehlt0 = _blatt_liste(d, blaetter, total, first, last, opt)
    blasen = blasen_pro_seite(d, page, gewaehlt0, opt["blasen"], lay.ort) if geo else {}
    nummern = lay.seitennummern(_start_nummer(page))
    opt["_zeilennummern"] = list(lay.zeilennummern(page.zeilennummern_neu)) if any(b.seite.zeilennummern for b in blaetter) else []
    base, davor, gedruckt = qdoc.defaultFont(), None, 0
    gewaehlt = gewaehlt0
    for k, bl in enumerate(blaetter):
        n = k + 1
        if n not in gewaehlt:
            continue
        ps = bl.seite
        if gedruckt:
            if layout and ps != davor:
                layout(ps)
            device.newPage()
        elif layout:
            layout(ps)
        davor, gedruckt = ps, gedruckt + 1
        p.save()
        p.scale(skala, skala)
        if geo:                                                  # Blatt verkleinert neben die Blasen setzen
            p.save(); p.translate(geo["x_page"], 0); p.scale(geo["f"], geo["f"])
        _blatt_zeichnen(p, d, bl, n, total, nummern[k], base, frei_alle, opt)
        if geo:
            p.restore()
            blasen_zeichnen(p, blasen.get(n, []), geo)
        p.restore()
    p.end()
    opt["_gedruckt"] = gedruckt
    _pdf_ergebnisse(opt, d, page, gewaehlt, 1, lay.ort)
    return total


def _frei_index(d: QTextDocument, page: PageSettings) -> dict:
    """Index der freien Bilder im Fluss (je Kopie einmal berechnet)."""
    from lunivo_writer.editor.objekte import freie_bilder as FB
    idx = getattr(d, "_frei_idx", None)
    if idx is None:
        idx = d._frei_idx = FB.koerper_index(d, page.content_height_px, max(1, int(page.spalten)))
    return idx


def _kopf_fuss_zeichnen(p: QPainter, page: PageSettings, n: int, nr_offset: int, total: int, gesamt: int | None, base: QFont,
                        kapitel: str) -> None:
    ml, cw = mm_to_px(page.margin_left_mm), page.content_width_px
    ph = mm_to_px(page.height_mm)
    angezeigt = n + nr_offset
    kopf, fuss = page.kopf_fuss(n, angezeigt)
    _draw_hf(p, kopf, QRectF(ml, mm_to_px(page.kopf_abstand_mm), cw, mm_to_px(KOPF_HOEHE_MM)), angezeigt, gesamt or total, base, page, kapitel)
    _draw_hf(p, fuss, QRectF(ml, ph - mm_to_px(page.fuss_abstand_mm), cw, mm_to_px(KOPF_HOEHE_MM)), angezeigt, gesamt or total, base, page, kapitel)


def _zeilennummern_zeichnen(p: QPainter, d: QTextDocument, page: PageSettings, n: int, base: QFont) -> None:
    ch = page.content_height_px
    p.save()
    p.translate(mm_to_px(page.margin_left_mm), mm_to_px(page.margin_top_mm))
    p.translate(0, -(n - 1) * ch)
    zeilennummern.zeichnen(p, d, n, ch, base, page.zeilennummern_neu)
    p.restore()


def _fussnoten_zeichnen(p: QPainter, d: QTextDocument, page: PageSettings, n: int) -> None:
    """Fußnoten am Seitenfuß, mit kurzem Trennstrich."""
    fuss = getattr(d, "_fussnoten", None)
    if not (fuss and n in fuss and int(page.spalten) <= 1):
        return
    cw, ch = page.content_width_px, page.content_height_px
    p.save()
    p.translate(mm_to_px(page.margin_left_mm), mm_to_px(page.margin_top_mm))
    info = fuss[n]
    y0 = ch - info["hoehe"] + 6
    _fussnoten_trennlinie(QtRenderBackend(p), y0, cw)
    for y, nd, _nid in info["noten"]:
        p.save()
        p.translate(0, y)
        _inhalt_zeichnen(p, nd, QRectF(0, 0, cw, nd.size().height()))
        p.restore()
    p.restore()


def _spalte_zeichnen(p: QPainter, d: QTextDocument, page: PageSettings, lp: int, x: float) -> None:
    """Die logische Spaltenseite ``lp`` an Stelle ``x`` der Blattseite."""
    cb, ch = page.spalten_breite_px, page.content_height_px
    p.save()
    p.translate(x, mm_to_px(page.margin_top_mm))
    p.setClipRect(QRectF(-10, 0, cb + 20, ch))
    p.translate(0, -(lp - 1) * ch)
    _inhalt_zeichnen(p, d, QRectF(0, (lp - 1) * ch, cb, ch))
    absatz_zusatz_zeichnen(p, d)
    p.restore()


SPALTENLINIE_STIL = Style(color=(0x88, 0x88, 0x88, 255), width=0.6)
FUSSNOTEN_LINIE_STIL = Style(color=(0x55, 0x55, 0x55, 255), width=0.6)
ZEILENNUMMER_STIL = Style(color=QColor(Qt.gray).getRgb())


def _fussnoten_trennlinie(backend: RenderBackend, y0: float, breite: float) -> None:
    """Kurzer Trennstrich über den Fußnoten."""
    backend.draw_line(Point(0, int(y0)), Point(int(breite * FUSSNOTEN_TRENNLINIE), int(y0)), FUSSNOTEN_LINIE_STIL)


def _balken_stil() -> Style:
    """Stil der Änderungsbalken: Farbe aus dem Thema (Farbe.ROT), Strichstärke 1,4."""
    return Style(color=QColor(Farbe.ROT).getRgb(), width=1.4)


def _aenderungsbalken(backend: RenderBackend, balken: tuple, page: PageSettings, n: int, lp: int, x_spalte: float) -> None:
    """Änderungsbalken neben den Zeilen mit verfolgten Änderungen."""
    seite_b, zeilen = balken
    cb, ch, mt = page.spalten_breite_px, page.content_height_px, mm_to_px(page.margin_top_mm)
    rechts = seite_b == "rechts" or (seite_b == "außen" and n % 2 == 0)
    x = x_spalte + (cb + 6 if rechts else -6)
    stil = _balken_stil()
    for t, u in zeilen:
        if int((t + 0.5) // ch) == lp - 1:
            y0 = mt + t - (lp - 1) * ch
            backend.draw_line(Point(int(x), int(y0)), Point(int(x), int(mt + min(u, lp * ch) - (lp - 1) * ch)), stil)


def _balken_blatt(backend: RenderBackend, balken: tuple, bl, n: int) -> None:
    """Änderungsbalken neben den Zeilen des Blattes, die verfolgte Änderungen tragen (Koordinaten des Laufs)."""
    seite_b, zeilen = balken
    rechts = seite_b == "rechts" or (seite_b == "außen" and n % 2 == 0)
    x = (bl.text_links + bl.seite.content_width_px + 6) if rechts else (bl.text_links - 6)
    stil = _balken_stil()
    for t, u in zeilen:
        if bl.oben <= t + 0.5 < bl.oben + bl.hoehe:
            backend.draw_line(Point(int(x), int(t)), Point(int(x), int(min(u, bl.oben + bl.hoehe))), stil)


def _spaltenlinien_zeichnen(backend: RenderBackend, page: PageSettings, n_sp: int) -> None:
    cb, ch = page.spalten_breite_px, page.content_height_px
    ml, mt, luecke = mm_to_px(page.margin_left_mm), mm_to_px(page.margin_top_mm), mm_to_px(page.spalten_abstand_mm)
    stil = SPALTENLINIE_STIL
    for j in range(1, n_sp):
        x = int(ml + j * (cb + luecke) - luecke / 2)
        backend.draw_line(Point(x, int(mt)), Point(x, int(mt + ch)), stil)


def zeichne_seite(p: QPainter, d: QTextDocument, page: PageSettings, n: int, total: int, base: QFont,
                  hintergrund: bool = True, balken: tuple | None = None, nr_offset: int = 0, gesamt: int | None = None,
                  kapitel: str = "") -> None:
    """Eine Seite (Nummer n, 1-basiert) mit Seitenschmuck, Kopf-/Fußzeile und Text; Maßstab 96 dpi, Ursprung links oben.
    ``nr_offset`` verschiebt die angezeigte Seitennummer, ``kapitel`` ist die Kapitelnummer davor."""
    from lunivo_writer.editor.objekte import freie_bilder as FB
    seitenschmuck(p, page, hintergrund, None, "hinten")
    frei = FB.objekte_der_seite(page, d, n, _frei_index(d, page))
    frei_zeichnen(p, frei, True)                                    # Bilder hinter dem Text (zum Beispiel ein Band im Briefkopf)
    _kopf_fuss_zeichnen(p, page, n, nr_offset, total, gesamt, base, kapitel)
    if page.zeilennummern and page.spalten <= 1:
        _zeilennummern_zeichnen(p, d, page, n, base)
    _fussnoten_zeichnen(p, d, page, n)
    n_sp = max(1, int(page.spalten))
    ml, luecke = mm_to_px(page.margin_left_mm), mm_to_px(page.spalten_abstand_mm)
    for j in range(n_sp):
        lp = (n - 1) * n_sp + j + 1                      # logische Spaltenseite, die in Spalte j dieser Blattseite steht
        if lp > d.pageCount():
            break
        x = ml + j * (page.spalten_breite_px + luecke)
        _spalte_zeichnen(p, d, page, lp, x)
        if j == n_sp - 1:                                    # der Seitenrahmen „im Vordergrund“ liegt über dem Text der Seite
            frei_zeichnen(p, frei, False)                    # Bilder vor dem Text (Foto, Unterschrift)
            seitenschmuck(p, page, False, None, "vorn", False)
        if balken:
            _aenderungsbalken(QtRenderBackend(p), balken, page, n, lp, x)
    if n_sp > 1 and page.spalten_linie:
        _spaltenlinien_zeichnen(QtRenderBackend(p), page, n_sp)


def seite_als_bild(qdoc: QTextDocument, page: PageSettings, n: int, faktor: float = 1.0, d: QTextDocument | None = None,
                   noten: dict | None = None, nr_offset: int | None = None, gesamt: int | None = None) -> QImage:
    """Seite n als Bild (für die Zwei-Seiten-Ansicht und „Als Bild exportieren“). Ohne ``nr_offset`` gilt „Beginnen mit“ der Einrichtung."""
    d = d or paginated_copy(qdoc, page, noten)
    if nr_offset is None:
        nr_offset = _start_nummer(page)
    total = ausgabe_seiten(d.pageCount(), page)
    w, h = int(mm_to_px(page.width_mm) * faktor), int(mm_to_px(page.height_mm) * faktor)
    img = QImage(w, h, QImage.Format_RGB32)
    img.fill(Qt.white)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.TextAntialiasing)
    p.scale(faktor, faktor)
    kap = _kapitel_von(_kapitel_liste(d, page), n, max(1, int(page.spalten)))
    zeichne_seite(p, d, page, n, total, qdoc.defaultFont(), nr_offset=nr_offset, gesamt=gesamt, kapitel=kap)
    p.end()
    return img


def seitenzahl(qdoc: QTextDocument, page: PageSettings, noten: dict | None = None) -> int:
    """Seiten der Ausgabe über alle Abschnitte (einschließlich Leerseiten vor „gerade/ungerade Seite“)."""
    from lunivo_writer.editor.seite import abschnitte as AB
    teile, _h = AB.teile(qdoc, page)
    if _blattweise():
        return len(_gesetzt(qdoc, page, {"noten": noten})[1])
    zaehl = [ausgabe_seiten(paginated_copy(d, ps, noten, silben=False).pageCount(), ps) for d, ps, _t in teile]
    return _leerseiten_plan([t for _d, _ps, t in teile], zaehl)[2]


def seiten_bilder(qdoc: QTextDocument, page: PageSettings, noten: dict | None = None, faktor: float = 1.0):
    """Alle Seiten der Ausgabe als (Nummer, Bild, Seiteneinrichtung) — mit mehreren Abschnitten je Abschnitt in der eigenen Größe."""
    from lunivo_writer.editor.seite import abschnitte as AB
    teile, _hinweise = AB.teile(qdoc, page)
    if _blattweise():
        d, blaetter, frei_alle = _gesetzt(qdoc, page, {"noten": noten})
        nummern = d.documentLayout().seitennummern(_start_nummer(page))
        o = {"_zeilennummern": list(d.documentLayout().zeilennummern(page.zeilennummern_neu))}
        for k, bl in enumerate(blaetter):
            img = QImage(int(bl.breite * faktor), int(bl.hoehe * faktor), QImage.Format_RGB32)
            img.fill(Qt.white)
            p = QPainter(img)
            p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.TextAntialiasing)
            p.scale(faktor, faktor)
            _blatt_zeichnen(p, d, bl, k + 1, len(blaetter), nummern[k], qdoc.defaultFont(), frei_alle, o)
            p.end()
            yield k + 1, img, bl.seite
        return
    kopien = [paginated_copy(d, ps, noten) for d, ps, _t in teile]
    zaehl = [ausgabe_seiten(k.pageCount(), ps) for k, (_d, ps, _t) in zip(kopien, teile)]
    offsets, leer, gesamt = _leerseiten_plan([t for _d, _ps, t in teile], zaehl)
    for (d, ps, _t), k, z, offset, davor in zip(teile, kopien, zaehl, offsets, leer):
        if davor:
            img = QImage(int(mm_to_px(ps.width_mm) * faktor), int(mm_to_px(ps.height_mm) * faktor), QImage.Format_RGB32)
            img.fill(Qt.white)
            yield offset, img, ps
        for n in range(1, z + 1):
            yield offset + n, seite_als_bild(d, ps, n, faktor, k, noten, offset, gesamt), ps


def _leere_seiten(d: QTextDocument, page: PageSettings, total: int) -> set[int]:
    from lunivo_writer.editor.seite.seitenzahl import absatz_oben
    ch = page.content_height_px
    mit_text = set()
    b = d.firstBlock()
    lay = d.documentLayout()
    while b.isValid():
        if b.text().strip(chr(0xfffc) + " \t\n") or b.text():
            mit_text.add(int((absatz_oben(lay, b) + 0.5) // ch) // max(1, int(page.spalten)) + 1)
        b = b.next()
    return {n for n in range(1, total + 1) if n not in mit_text}


def _page_layout(page: PageSettings, quer: bool = False) -> QPageLayout:
    size = QPageSize(QSizeF(min(page.width_mm, page.height_mm), max(page.width_mm, page.height_mm)),
                     QPageSize.Millimeter)
    orient = QPageLayout.Landscape if (page.landscape or quer) else QPageLayout.Portrait
    return QPageLayout(size, orient, QMarginsF(0, 0, 0, 0), QPageLayout.Millimeter)


def _quer(geo: dict | None) -> bool:
    return bool(geo and geo["quer"])


def _xmp_autor(author: str) -> QByteArray:
    esc = author.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return QByteArray(("<x:xmpmeta xmlns:x=\"adobe:ns:meta/\"><rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">"
                       "<rdf:Description xmlns:dc=\"http://purl.org/dc/elements/1.1/\"><dc:creator><rdf:Seq><rdf:li>"
                       + esc + "</rdf:li></rdf:Seq></dc:creator></rdf:Description></rdf:RDF></x:xmpmeta>").encode("utf-8"))


def _pdf_schreiber(path: str, page: PageSettings, geo: dict | None, title: str, author: str) -> QPdfWriter:
    w = QPdfWriter(path)
    w.setResolution(300)
    w.setPageLayout(_page_layout(page, _quer(geo)))
    if title:
        w.setTitle(title)
    w.setCreator("Lunivo Writer")
    if author:
        w.setDocumentXmpMetadata(_xmp_autor(author))
    return w


def export_pdf(path: str, qdoc: QTextDocument, page: PageSettings, title: str = "", author: str = "", noten: dict | None = None,
               lesezeichen: dict | None = None, silben: dict | None = None, kommentare: list | None = None,
               extra: dict | None = None, erste: int = 1, letzte: int | None = None) -> int:
    """Schreibt die Seiten ``erste`` bis ``letzte`` (``None``: bis zum Ende) als PDF. → Seitenzahl des Dokuments."""
    optionen = extra or {}
    # Die Modell-Ausgabe kennt Seitenbereiche und normale Dokumentformate. PDF-Anmerkungen, Sonderdruckoptionen
    # und aktive Links brauchen weiterhin den vorhandenen Qt-Ausgabepfad.
    links_aktiv = False
    if optionen.get("hyperlinks"):
        b = qdoc.begin()
        while b.isValid() and not links_aktiv:
            it = b.begin()
            while not it.atEnd():
                fmt = it.fragment().charFormat()
                if fmt.isAnchor() and fmt.anchorHref():
                    links_aktiv = True
                    break
                it += 1
            b = b.next()
    modelloptionen = {k: v for k, v in optionen.items() if k not in ("hyperlinks", "notenlinks") and v}
    if not noten and not lesezeichen and not silben and not kommentare and not modelloptionen and not links_aktiv:
        from lunivo_writer.adapter.qt.dokument import NichtUebertragbar, document_from_qt
        try:
            modell = document_from_qt(qdoc, page)
        except NichtUebertragbar:
            pass                                      # aktive Formate ohne Modellabbildung rendert weiter der Qt-Pfad
        else:
            from lunivo_writer.adapter.qt.pdf_modell import modell_als_pdf
            return modell_als_pdf(modell, path, title, autor=author, erste=erste, letzte=letzte)
    geo = blasen_geometrie(page, extra)
    w = _pdf_schreiber(path, page, geo, title, author)
    opt = {"noten": noten} if noten else {}
    opt.update(extra or {})
    opt.update({k: v for k, v in (("lesezeichen", lesezeichen), ("silbenfarben", silben), ("kommentare", kommentare)) if v})
    n = render_dokument(qdoc, page, w, erste, letzte, opt=opt, layout=lambda ps: w.setPageLayout(_page_layout(ps, _quer(geo))))
    if opt.get("lesezeichen_ergebnis") or opt.get("kommentare_ergebnis") or opt.get("notenlinks_ergebnis"):
        del w                                  # Datei schließen, bevor sie noch einmal geöffnet wird
        gliederung_schreiben(path, opt.get("lesezeichen_ergebnis") or [], opt.get("kommentare_ergebnis"), page,
                             opt.get("notenlinks_ergebnis"))
    return n


def print_document(printer: QPrinter, qdoc: QTextDocument, page: PageSettings, opt: dict | None = None) -> int:
    geo = blasen_geometrie(page, opt)
    printer.setPageLayout(_page_layout(page, _quer(geo)))
    first, last = 1, None
    if printer.printRange() == QPrinter.PageRange and printer.fromPage():
        first, last = printer.fromPage(), printer.toPage() or None
    optionen = opt or {}
    druckoptionen = {
        "nur_seiten", "duplex", "umgekehrt", "hintergrund", "leere", "hervorhebungen", "textmarken", "textgrenzen",
        "zuschnitt", "silbenfarben", "versteckt", "felder_code", "zeichnungen", "balken", "notenlinks", "blasen",
        "nur_formular", "noten", "platzhalter", "steuerelemente", "schwarz",
    }
    noten_opt = optionen.get("noten")
    noten_modellgeeignet = not noten_opt or (
        isinstance(noten_opt, dict) and all(k in ("f", "e") and isinstance(v, dict)
                                            for k, v in noten_opt.items())
    )
    modellgeeignet = set(optionen) <= druckoptionen and noten_modellgeeignet and not any(optionen.get(k) for k in (
        "blasen", "kommentare", "silbenfarben", "versteckt", "felder_code", "textmarken",
        "textgrenzen", "zuschnitt", "schwarz", "platzhalter", "nur_formular",
    )) and not any(optionen.get(k) is False for k in (
        "hintergrund", "zeichnungen", "steuerelemente", "hervorhebungen", "leere",
    ))
    if modellgeeignet and optionen.get("balken"):
        from lunivo_writer.editor.seite.anzeige_extra import aenderungszeilen
        modellgeeignet = not aenderungszeilen(qdoc)
    if modellgeeignet:
        from lunivo_writer.adapter.qt.dokument import NichtUebertragbar, document_from_qt
        try:
            modell = document_from_qt(qdoc, page)
        except NichtUebertragbar:
            pass                                  # nicht übertragbare Formate bleiben beim bestehenden Seitenlauf
        else:
            if noten_opt:
                from lunivo_writer.core.document import Footnote
                modell.notes = [Footnote(int(nid), kind, str(text))
                                for kind, eintraege in noten_opt.items() for nid, text in eintraege.items()]
            from lunivo_writer.adapter.qt.seitenbild import grundschrift, seite_malen
            from lunivo_writer.core.layout import umbrechen
            from lunivo_writer.dienste.textsatz import standard_engine
            engine = standard_engine()
            erg = umbrechen(modell, engine)
            total = len(erg.seiten)
            ende = total if last is None else min(last, total)
            seiten = seiten_liste(total, max(1, first), ende, optionen) if first <= ende else []
            if optionen.get("nur_seiten") is not None:
                seiten = [n for n in seiten if n in optionen["nur_seiten"]]
            if seiten:
                einr = erg.seiten[seiten[0] - 1].einrichtung or page
                printer.setPageLayout(_page_layout(einr, _quer(geo)))
                p = QPainter(printer)
                p.scale((printer.logicalDpiX() or printer.resolution()) / 96.0,
                        (printer.logicalDpiY() or printer.resolution()) / 96.0)
                grund = grundschrift(modell)
                for i, nr in enumerate(seiten):
                    if i:
                        einr = erg.seiten[nr - 1].einrichtung or page
                        printer.setPageLayout(_page_layout(einr, _quer(geo)))
                        printer.newPage()
                    seite_malen(p, modell, erg, nr - 1, engine, grund)
                p.end()
            return total
    return render_dokument(qdoc, page, printer, first, last, opt=opt,
                           layout=lambda ps: printer.setPageLayout(_page_layout(ps, _quer(geo))))
