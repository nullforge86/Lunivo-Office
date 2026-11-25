"""Die einzige Stelle, die Lunivo-Komponenten aufruft: Laden, Speichern, Layout, Rendering. Hier steht keine eigene Dokumentlogik — alles geht über
``dienste.modell_laden``, ``dienste.modell_speichern``, ``core.layout.LayoutEngine`` und ``core.rendering.DokumentRenderer`` (dieselben Aufrufe wie der PDF-Export)."""
from __future__ import annotations

import hashlib
import os

OBJEKT_ZEICHEN = "￼"


def lunivo_version() -> str:
    """Kennung der geprüften Lunivo-Komponenten: Hash über Größe und Änderungszeit aller Quelldateien der beteiligten Pakete."""
    import lunivo_writer
    wurzel = os.path.dirname(lunivo_writer.__file__)
    h = hashlib.sha1()
    for paket in ("core", "dienste", "adapter", "modelle", "plattform"):
        for ordner, dirs, namen in os.walk(os.path.join(wurzel, paket)):
            dirs[:] = sorted(d for d in dirs if d != "__pycache__")
            for n in sorted(namen):
                if n.endswith(".py"):
                    st = os.stat(os.path.join(ordner, n))
                    h.update(f"{os.path.relpath(os.path.join(ordner, n), wurzel)}:{st.st_size}:{st.st_mtime_ns};".encode())
    return h.hexdigest()[:12]


def lade(pfad: str, kennwort: str | None = None):
    """Die tatsächliche Lunivo-Importfunktion. Wirft ``DocumentIOError``/``PasswortNoetig``."""
    from lunivo_writer.dienste.modell_laden import lade_modell
    return lade_modell(pfad, kennwort)


def speichere(geladen, pfad: str):
    """Die tatsächliche Lunivo-Speicherfunktion (ohne Sicherungskopie, in eine fremde Zieldatei). Liefert den ``IOReport``."""
    from lunivo_writer.dienste.modell_speichern import speichere_modell
    return speichere_modell(pfad, geladen.document, geladen.page, geladen.meta, sicherung=False)


def layout(dokument):
    """Layoutberechnung der Anwendung. → (LayoutEngine, Ergebnis)."""
    from lunivo_writer.kern.layout import LayoutEngine
    le = LayoutEngine(None)
    return le, le.berechnen(dokument)


def seite_mm(einrichtung) -> tuple[float, float]:
    return (float(einrichtung.width_mm), float(einrichtung.height_mm)) if einrichtung is not None else (210.0, 297.0)


def seitenbilder(dokument, le, erg, ordner: str, praefix: str, faktor: float = 1.0, max_seiten: int = 80) -> list[str]:
    """Rendert die Seiten mit dem Renderer der Anwendung nach PNG (96 dpi · ``faktor``). → Dateipfade."""
    from lunivo_writer.kern.layout import formatwerte as F
    from lunivo_writer.kern.rendering import DokumentRenderer
    from lunivo_writer.kern.rendering.bildeffekte import png_bytes
    from lunivo_writer.kern.rendering.rasterziel import RasterZiel
    os.makedirs(ordner, exist_ok=True)
    renderer = DokumentRenderer(le.engine)
    grund = F.schrift(dict(dokument.standardformat))
    pfade = []
    for seite in erg.seiten[:max_seiten]:
        bw, bh = seite_mm(seite.einrichtung)
        flaeche = RasterZiel(le.engine, bw * 96 / 25.4, bh * 96 / 25.4, faktor, (255, 255, 255, 255))            # Qt-freie Zeichenfläche des Kerns
        renderer.zeichne_seite(flaeche, dokument, erg, seite.index, grund)
        w, h, roh = flaeche.als_rgba()
        ziel = os.path.join(ordner, f"{praefix}_{seite.index + 1:04d}.png")
        with open(ziel, "wb") as f:
            f.write(png_bytes(w, h, roh))
        pfade.append(ziel)
    return pfade


def metriken(dokument) -> dict:
    """Zählwerte und Formatsummen des Dokumentmodells (nur Lesen)."""
    from lunivo_writer.kern.dokument.dokument import InlineObjekt, Lauf, Tabelle
    m = {"absaetze": 0, "nichtleere_absaetze": 0, "zeichen": 0, "woerter": 0, "listen_absaetze": 0, "ueberschriften": 0,
         "fett_zeichen": 0, "kursiv_zeichen": 0, "unterstrichen_zeichen": 0, "mitte_absaetze": 0, "rechts_absaetze": 0, "block_absaetze": 0,
         "bilder": 0}
    texte: list[str] = []
    schriften: dict[str, int] = {}
    for a in dokument.absaetze():
        t = a.text()
        texte.append(t)
        m["absaetze"] += 1
        sauber = t.replace(OBJEKT_ZEICHEN, "")
        if sauber.strip():
            m["nichtleere_absaetze"] += 1
            m["woerter"] += len(sauber.split())
        m["zeichen"] += len("".join(sauber.split()))
        if a.liste_id is not None:
            m["listen_absaetze"] += 1
        vorlage = dokument.vorlagen.get(a.format.get("vorlage", "")) if a.format.get("vorlage") else None
        if vorlage is not None and getattr(vorlage, "ebene", 0) > 0:
            m["ueberschriften"] += 1
        ausr = a.format.get("ausrichtung")
        if ausr in ("mitte", "rechts", "block"):
            m[f"{ausr}_absaetze"] += 1
        for x in a.inhalte:
            if isinstance(x, Lauf):
                if x.format.get("schrift"):
                    schriften[str(x.format["schrift"])] = schriften.get(str(x.format["schrift"]), 0) + 1
                n = len("".join(x.text.replace(OBJEKT_ZEICHEN, "").split()))
                if x.format.get("fett"):
                    m["fett_zeichen"] += n
                if x.format.get("kursiv"):
                    m["kursiv_zeichen"] += n
                if x.format.get("unterstrichen"):
                    m["unterstrichen_zeichen"] += n
            elif isinstance(x, InlineObjekt) and x.art == "bild":
                m["bilder"] += 1
    m["bilder"] += sum(1 for o in dokument.objekte.values() if o.art == "bild")
    oberste = [b for ab in dokument.abschnitte for b in ab.bloecke if isinstance(b, Tabelle)]
    alle = list(dokument.tabellen())
    m["tabellen"] = len(oberste)
    m["verschachtelte_tabellen"] = len(alle) - len(oberste)
    m["tabellenzellen"] = sum(1 for t in alle for z in t.zellen for c in z if c.verdeckt_von is None)
    m["abschnitte"] = len(dokument.abschnitte)
    m["fussnoten"] = len(dokument.noten.get("f", {}))
    m["endnoten"] = len(dokument.noten.get("e", {}))
    m["kommentare"] = len(dokument.kommentare)
    m["objekte_frei"] = len(dokument.objekte)
    m["formatvorlagen"] = len(dokument.vorlagen)
    m["listen_definitionen"] = len(dokument.listen)
    kopf = fuss = 0
    for ab in dokument.abschnitte:
        sp = ab.seite
        kopf += sum(1 for n in ("header", "first_header", "even_header") if getattr(getattr(sp, n, None), "text", ""))
        fuss += sum(1 for n in ("footer", "first_footer", "even_footer") if getattr(getattr(sp, n, None), "text", ""))
    if dokument.standardformat.get("schrift"):
        schriften.setdefault(str(dokument.standardformat["schrift"]), 0)
    # Von Lunivo gemessen und nur dokumentiert — nie als Sollwert verwendet.
    return {"werte": m, "texte": texte, "eigenschaften": {"schriftarten": sorted(schriften), "kopfzeilen": kopf, "fusszeilen": fuss}}
