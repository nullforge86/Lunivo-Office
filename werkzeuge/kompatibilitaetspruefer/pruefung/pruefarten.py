"""Die Prüfarten. Jede Funktion bekommt einen ``Kontext`` (eine Datei, ihre Referenz, die Konfiguration) und liefert ein Ergebnis mit Prüfpunkten.

Laufen im Prüfprozess (``arbeiter.py``); Laden, Speichern, Layout und Rendering kommen ausschließlich aus ``lunivo_zugang`` (also aus Lunivo selbst).
Ein Ergebnis ist nur ``bestanden``, wenn alle Prüfpunkte der Prüfart gemessen und gleich sind (siehe ``klassifikation``); was nicht gemessen wurde, steht in
``werte["nicht_geprueft"]`` und nie unter den bestandenen Punkten.
"""
from __future__ import annotations

import os
import time

from lunivo_writer.werkzeuge.kompatibilitaetspruefer.pruefung import klassifikation as K
from lunivo_writer.werkzeuge.kompatibilitaetspruefer.pruefung import lunivo_zugang as LZ
from lunivo_writer.werkzeuge.kompatibilitaetspruefer.pruefung.vergleiche import FORMATSCHLUESSEL, NICHT_GEPRUEFT_FORMAT, NICHT_GEPRUEFT_STRUKTUR, STRUKTURSCHLUESSEL, norm, vergleiche_texte, vergleiche_werte

MARKE = "LunivoPruefmarke"
ROUNDTRIP_ZIEL = {".docx": ".docx", ".dotx": ".docx", ".docm": ".docx", ".odt": ".odt", ".fodt": ".odt", ".rtf": ".rtf", ".txt": ".txt", ".text": ".txt", "": ".txt"}


class Kontext:
    def __init__(self, job: dict):
        self.job = job
        self.k = job["konfig"]
        self.pfad = job["arbeitskopie"]
        self.endung = job["datei"]["endung"]
        self.ref = job.get("referenz") or {}
        self.tmp = job["tmp"]
        self._geladen = None
        self._fehler = None
        self._layout = None
        self._metriken = None
        self._quelle = False

    def modell(self):
        """``(ModellGeladen, None)`` oder ``(None, Prüfpunkt des Fehlers)``. Der Import läuft nur einmal je Datei."""
        if self._geladen is None and self._fehler is None:
            try:
                self._geladen = LZ.lade(self.pfad, self.job.get("kennwort"))
            except BaseException as e:                                                       # noqa: BLE001 — jede Fehlerart wird als Ergebnis gemeldet
                if isinstance(e, KeyboardInterrupt):
                    raise
                self._fehler = import_fehler(e)
        return self._geladen, self._fehler

    def layout(self):
        if self._layout is None:
            self._layout = LZ.layout(self.modell()[0].document)
        return self._layout

    def metriken(self) -> dict:
        if self._metriken is None:
            self._metriken = LZ.metriken(self.modell()[0].document)
        return self._metriken

    def quelle(self):
        if self._quelle is False:
            from lunivo_writer.werkzeuge.kompatibilitaetspruefer.pruefung.quellzaehlung import zaehle
            try:
                self._quelle = zaehle(self.pfad, self.endung)
            except Exception as e:                                                           # noqa: BLE001
                self._quelle = {"fehler": f"{type(e).__name__}: {e}"}
        return self._quelle

    def bildordner(self) -> str:
        return self.job["bildordner"]


def import_fehler(e: BaseException) -> dict:
    from core.dokument.bericht import DocumentIOError, PasswortNoetig
    text = " ".join(str(e).split())[:300]
    if isinstance(e, PasswortNoetig):
        return K.nicht_pruefbar("Import", "Das Dokument ist durch ein Kennwort geschützt; ohne Kennwort ist es nicht prüfbar")
    if isinstance(e, MemoryError):
        return K.scheitert("Import", "Technischer Prüffehler", "Speichergrenze beim Import erreicht")
    if isinstance(e, DocumentIOError):
        return K.scheitert("Import", "Importfehler", f"Import fehlgeschlagen: {text}")
    return K.scheitert("Import", "Importfehler", f"Import mit Ausnahme abgebrochen ({type(e).__name__}): {text}")


def abschluss(art: str, befunde: list[dict], werte: dict | None = None, bilder: dict | None = None, dauer: float = 0.0) -> dict:
    status = K.ergebnisstatus(befunde)
    schlecht = [b for b in befunde if b["status"] == K.ABWEICHEND or b["schwere"] == "kritisch"]
    if schlecht:
        top = min(schlecht, key=lambda b: K.SCHWERE_RANG.get(b["schwere"], 9))
        beschreibung = top["beschreibung"] + (f" (+{len(schlecht) - 1} weitere Prüfpunkte)" if len(schlecht) > 1 else "")
    else:
        offen = [b for b in befunde if b["status"] != K.UEBEREINSTIMMEND]
        top = offen[0] if offen else None
        if top:
            beschreibung = top["beschreibung"]
        else:
            beschreibung = f"Alle {len(befunde)} Prüfpunkte übereinstimmend" if befunde else ""
    return {"art": art, "status": status, "fehlerart": K.haupt_fehlerart(befunde), "schwere": K.schlimmste_schwere(befunde), "beschreibung": beschreibung,
            "seite": top.get("seite") if top else None, "element": top.get("element", "") if top else "", "werte": werte or {}, "bilder": bilder or {},
            "befunde": befunde, "dauer": dauer}


def _warnungen(report, praefix: str, grenze: int = 25) -> list[dict]:
    """Meldungen des ``IOReport`` — das ist Lunivos eigene Angabe, was nicht übernommen wurde."""
    aus = []
    for w in list(getattr(report, "warnings", []))[:grenze]:
        aus.append(K.nicht_unterstuetzt(praefix, str(w)[:300]))
    return aus


# ---- Importprüfung ---------------------------------------------------------------------------------------------------
def pruefe_import(ctx: Kontext) -> dict:
    from kompatibilitaetspruefer.verwaltung.dateisuche import format_info
    g, fehler = ctx.modell()
    if fehler:
        return abschluss("import", [fehler])
    info = format_info(ctx.endung)
    m = ctx.metriken()["werte"]
    werte = {"format": info.name if info else ctx.endung, "endung": ctx.endung, **{k: m[k] for k in (
        "absaetze", "nichtleere_absaetze", "tabellen", "tabellenzellen", "bilder", "abschnitte", "fussnoten", "endnoten", "kommentare", "listen_absaetze",
        "objekte_frei", "formatvorlagen")}}
    b = [K.passt("Import", f"Erkannt als {werte['format']}; Import ohne Ausnahme abgeschlossen")]
    quelle = ctx.quelle()
    if quelle and "werte" in quelle:
        if quelle["werte"].get("nichtleere_absaetze", 0) > 0 and m["nichtleere_absaetze"] == 0:
            b.append(K.befund("Inhalt übernommen", K.ABWEICHEND, "Importfehler", "kritisch",
                              f"Die Quelle enthält {quelle['werte']['nichtleere_absaetze']} Absätze mit Text, das Modell keinen", quelle["werte"]["nichtleere_absaetze"], 0))
        else:
            b.append(K.passt("Inhalt übernommen", "Das Modell enthält Text, soweit die Quelle Text enthält (Inhaltstreue: siehe Strukturprüfung)"))
    elif ctx.ref.get("erwartet"):
        b.append(K.passt("Import", "Erwartete Strukturen liegen vor (Vergleich in der Strukturprüfung)"))
    else:
        b.append(K.fehlt("Inhaltstreue", "Keine Quellzählung und keine erwarteten Strukturen: Vollständigkeit der Übernahme wird nicht behauptet"))
    b += _warnungen(g.report, "Beim Import nicht übernommen")
    werte.update(ctx.metriken()["eigenschaften"])                      # erfasst und dokumentiert, nicht als Sollwert benutzt
    try:
        werte["seiten"] = len(ctx.layout()[1].seiten)
    except Exception as e:                                                                   # noqa: BLE001
        werte["seiten_fehler"] = f"{type(e).__name__}"
        b.append(K.scheitert("Layoutberechnung", "Layoutabweichung", f"Die Layout-Engine ist beim Erfassen der Seitenzahl abgebrochen ({type(e).__name__})", "schwer"))
    werte["nicht_geprueft"] = ["Vollständige Inhaltstreue (nur mit Referenzinformationen beurteilbar)", "Übernommene Werte werden nur dokumentiert, nicht gegen Lunivo-eigene Werte geprüft"]
    return abschluss("import", b, werte)


# ---- Strukturprüfung -------------------------------------------------------------------------------------------------
def _erwartet(ctx: Kontext, schluessel_ok: tuple, ausser: tuple = ()) -> tuple[dict, list[dict]]:
    """Erwartete Werte aus der Referenz: (Werte für bekannte Schlüssel, Prüfpunkte für unbekannte)."""
    soll, unbekannt = {}, []
    for k, v in (ctx.ref.get("erwartet") or {}).items():
        if k in ausser:
            continue
        if k in schluessel_ok:
            if isinstance(v, (int, float)):
                soll[k] = v
            else:
                unbekannt.append(K.nicht_pruefbar(k, f"Erwarteter Wert „{v}“ ist keine Zahl"))
    return soll, unbekannt


def pruefe_struktur(ctx: Kontext) -> dict:
    g, fehler = ctx.modell()
    if fehler:
        return abschluss("struktur", [fehler])
    m = ctx.metriken()
    b: list[dict] = []
    quelle = ctx.quelle()
    soll_erw, unb = _erwartet(ctx, STRUKTURSCHLUESSEL)
    bekannt = set(STRUKTURSCHLUESSEL) | set(FORMATSCHLUESSEL) | {"seiten"}
    b += unb + [K.nicht_pruefbar(k, "Unbekannter Schlüssel in den erwarteten Strukturen") for k in (ctx.ref.get("erwartet") or {}) if k not in bekannt]
    if quelle and "werte" in quelle:
        schluessel = [k for k in STRUKTURSCHLUESSEL if k in quelle["werte"] and k != "verschachtelte_tabellen"]
        if quelle["werte"].get("verschachtelte_tabellen"):
            b.append(K.nicht_unterstuetzt("Verschachtelte Tabellen", f"Die Quelle enthält {quelle['werte']['verschachtelte_tabellen']} verschachtelte Tabellen; Lunivo unterstützt sie laut Formatverzeichnis nicht"))
        b += vergleiche_werte(quelle["werte"], m["werte"], schluessel, "Strukturfehler", soll_name="Quelle")
        b += vergleiche_texte(quelle["texte"], m["texte"], "Strukturfehler", "Quelle")
        werte_quelle = quelle["quelle"]
    else:
        werte_quelle = ""
        if quelle and "fehler" in quelle:
            b.append(K.nicht_pruefbar("Quellzählung", f"Quelle konnte nicht gezählt werden: {quelle['fehler']}"))
        elif not soll_erw:
            b.append(K.fehlt("Quellzählung", f"Für {ctx.endung} gibt es keine Quellzählung, und es sind keine erwarteten Strukturen zugeordnet"))
    if soll_erw:
        b += vergleiche_werte(soll_erw, m["werte"], list(soll_erw), "Strukturfehler", soll_name="Erwartet")
    return abschluss("struktur", b, {"modell": m["werte"], "quelle": (quelle or {}).get("werte") if quelle and "werte" in quelle else None, "referenzart": werte_quelle,
                                     "nicht_geprueft": list(NICHT_GEPRUEFT_STRUKTUR)})


# ---- Formatierungsprüfung --------------------------------------------------------------------------------------------
def pruefe_format(ctx: Kontext) -> dict:
    g, fehler = ctx.modell()
    if fehler:
        return abschluss("format", [fehler])
    m = ctx.metriken()["werte"]
    b: list[dict] = []
    quelle = ctx.quelle()
    soll_erw, unb = _erwartet(ctx, FORMATSCHLUESSEL)
    b += unb
    if ctx.endung in (".txt", ".text", ""):
        b.append(K.nicht_unterstuetzt("Formatierung", "TXT enthält keine Formatierungsinformationen"))
    elif quelle and quelle.get("format"):
        # Gezählt wird nur direkte Formatierung der Quelle; das Modell darf mehr enthalten (Formatvorlagen), aber nicht weniger.
        b += vergleiche_werte(quelle["format"], m, FORMATSCHLUESSEL, "Formatierungsfehler", format_=True, nur_verlust=True, soll_name="Quelle")
    elif not soll_erw:
        b.append(K.fehlt("Formatierung", f"Keine Formatzählung der Quelle für {ctx.endung} und keine erwarteten Formatwerte zugeordnet"))
    if soll_erw:
        b += vergleiche_werte(soll_erw, m, list(soll_erw), "Formatierungsfehler", format_=True, soll_name="Erwartet")
    if ctx.endung not in (".txt", ".text", ""):
        b += _warnungen(g.report, "Beim Import nicht übernommen (Formatierung)", 10)
    return abschluss("format", b, {"modell": {k: m[k] for k in FORMATSCHLUESSEL}, "quelle": (quelle or {}).get("format"), "nicht_geprueft": list(NICHT_GEPRUEFT_FORMAT)})


# ---- Layoutprüfung ---------------------------------------------------------------------------------------------------
def _fehlende_schriften(dokument) -> list[str]:
    """Wirklich fehlende Schriften. Metrisch kompatible Ersatzschriften (z. B. Carlito für Calibri) zählen nicht als fehlend: gleiche Zeichenbreiten, gleiche Umbrüche."""
    from kompatibilitaetspruefer.verwaltung.schriftpruefung import bewerte
    benutzt = {str(dokument.standardformat.get("schrift", ""))}
    for a in dokument.absaetze():
        for x in a.inhalte:
            f = getattr(x, "format", None)
            if f and f.get("schrift"):
                benutzt.add(str(f["schrift"]))
    return bewerte(benutzt)[0]


def _versatztext(res: dict, tol: float) -> str:
    """Beschreibung eines messbaren Versatzes über der Verschiebungstoleranz (leer, wenn keiner vorliegt)."""
    rand = res["rand_abweichung_mm"]
    if rand and max(abs(v) for v in rand.values()) > tol:
        teile = ", ".join(f"{n} {v:+.1f}" for n, v in rand.items() if abs(v) > tol)
        return f"Inhaltsrahmen verschoben ({teile} mm; + = Lunivo weiter innen bzw. weiter unten/rechts)"
    if res["vertikaler_versatz_mm"] is not None and abs(res["vertikaler_versatz_mm"]) > tol:
        return f"Inhalt in Lunivo um {res['vertikaler_versatz_mm']:+.1f} mm vertikal verschoben (Zeilenprofil)"
    return ""


def _element_an(ctx: Kontext, erg, seite: int, bereich: dict, faktor: float) -> str:
    cx, cy = (bereich["x"] + bereich["w"] / 2) / faktor, (bereich["y"] + bereich["h"] / 2) / faktor
    nummern = None
    for p in erg.seiten[seite].plaetze:
        r = p.rect
        if r.x <= cx <= r.x + r.width and r.y <= cy <= r.y + r.height:
            if p.art == "zeile":
                if nummern is None:
                    nummern = ctx.modell()[0].document.reihenfolge()
                nr = nummern.get(p.block_id)
                return f"Absatz {nr + 1 if nr is not None else '?'} (Id {p.block_id}), Zeile {p.zeile + 1}"
            if p.art == "zelle":
                return f"Tabelle (Id {p.block_id}), Zeile {p.zeile + 1}, Spalte {p.spalte + 1}"
            return f"{p.art} (Id {p.block_id})"
    return ""


def pruefe_layout(ctx: Kontext) -> dict:
    from PySide6.QtGui import QImage
    from lunivo_writer.werkzeuge.kompatibilitaetspruefer.pruefung import bildvergleich, referenzbilder
    g, fehler = ctx.modell()
    if fehler:
        return abschluss("layout", [fehler])
    k = ctx.k
    b: list[dict] = []
    try:
        le, erg = ctx.layout()
    except Exception as e:                                                                  # noqa: BLE001
        return abschluss("layout", [K.scheitert("Layoutberechnung", "Layoutabweichung", f"Die Layout-Engine ist abgebrochen ({type(e).__name__}): {' '.join(str(e).split())[:300]}")])
    seiten = len(erg.seiten)
    werte: dict = {"seiten": seiten, "hinweise_engine": [str(h)[:200] for h in list(erg.hinweise)[:10]]}
    fehlt_schrift = _fehlende_schriften(g.document)
    if fehlt_schrift:
        werte["fehlende_schriften"] = fehlt_schrift[:20]
        b.append(K.nicht_pruefbar("Schriftarten", "Nicht installiert: " + ", ".join(fehlt_schrift[:8]) + (" …" if len(fehlt_schrift) > 8 else "") +
                                  " — Zeilenumbrüche und Seitenzahl sind nur eingeschränkt mit der Referenz vergleichbar"))
    try:
        refseiten = referenzbilder.referenzseiten(ctx.ref, ctx.bildordner(), k["max_seiten"], k["rendern_dpi_faktor"]) if ctx.ref else None
    except referenzbilder.ReferenzFehler as e:
        refseiten = None
        b.append(K.fehlt("Referenzdarstellung", f"Referenz unbrauchbar: {e}"))
    erwartet = ctx.ref.get("seiten_erwartet") or (ctx.ref.get("erwartet") or {}).get("seiten")
    soll_seiten = refseiten["seiten"] if refseiten else erwartet
    if soll_seiten is None:
        b.append(K.fehlt("Seitenanzahl", "Keine Referenz (PDF, Seitenbilder oder erwartete Seitenanzahl) zugeordnet"))
    elif soll_seiten == seiten:
        b.append(K.passt("Seitenanzahl", f"{seiten} Seiten", soll_seiten, seiten))
    else:
        b.append(K.befund("Seitenanzahl", K.ABWEICHEND, "Layoutabweichung", "schwer", f"Referenz {soll_seiten} Seiten, Lunivo {seiten} Seiten", soll_seiten, seiten))
    if refseiten is None:
        b.append(K.fehlt("Visueller Vergleich", "Keine Referenzdarstellung (PDF oder Seitenbilder) zugeordnet — Lage und Darstellung werden nicht beurteilt"))
        return abschluss("layout", b, werte)
    faktor = k["rendern_dpi_faktor"]
    lun = LZ.seitenbilder(g.document, le, erg, ctx.bildordner(), "lun", faktor, k["max_seiten"])
    bilder = {"referenz": refseiten["pfade"], "lunivo": lun, "referenz_quelle": refseiten["quelle"]}
    werte["verglichene_seiten"] = min(len(lun), len(refseiten["pfade"]))
    if refseiten["groessen_mm"]:
        for i, (rw, rh) in enumerate(refseiten["groessen_mm"][:len(erg.seiten)]):
            lw, lh = LZ.seite_mm(erg.seiten[i].einrichtung)
            if abs(rw - lw) > 1.5 or abs(rh - lh) > 1.5:
                b.append(K.befund("Seitenformat", K.ABWEICHEND, "Layoutabweichung", "mittel", f"Seite {i + 1}: Referenz {rw:.0f}×{rh:.0f} mm, Lunivo {lw:.0f}×{lh:.0f} mm", seite=i + 1))
                break
        else:
            b.append(K.passt("Seitenformat", "Seitengrößen stimmen überein (±1,5 mm)"))
    mm_px = 25.4 / 96.0 / faktor
    seitenwerte, ok, abw = [], 0, 0
    for i in range(werte["verglichene_seiten"]):
        r_img, l_img = QImage(refseiten["pfade"][i]), QImage(lun[i])
        if r_img.isNull() or l_img.isNull():
            b.append(K.nicht_pruefbar(f"Seite {i + 1}", "Bild konnte nicht geladen werden"))
            continue
        res = bildvergleich.vergleiche(r_img, l_img, k["zellanteil"], mm_px, k["verschiebung_mm"])
        seitenwerte.append({"seite": i + 1, **{x: res[x] for x in ("anteil", "tintenverhaeltnis", "rand_abweichung_mm", "vertikaler_versatz_mm", "zellen_abweichend", "zellen_abweichend_ohne_toleranz", "zellen_mit_inhalt")},
                            "bereiche": res["bereiche"][:25]})
        if res["anteil"] <= k["seitenanteil"]:
            versatz = _versatztext(res, k["verschiebung_mm"])
            if not versatz:
                ok += 1
                continue
            abw += 1                                                   # Raster innerhalb der Toleranz, aber der Inhalt steht messbar versetzt: geringe Abweichung, nicht „bestanden“
            if abw <= 30:
                b.append(K.befund(f"Seite {i + 1}", K.ABWEICHEND, "Layoutabweichung", "gering",
                                  f"Seite {i + 1}: {versatz}; Rasterzellen innerhalb der Toleranz ({res['anteil'] * 100:.1f} %, strenger Zellvergleich ohne Verschiebungstoleranz: "
                                  f"{res['zellen_abweichend_ohne_toleranz']} von {res['zellen_mit_inhalt']})", k["seitenanteil"], res["anteil"], seite=i + 1))
            continue
        abw += 1
        tol = k["verschiebung_mm"]
        rand = res["rand_abweichung_mm"]
        tv = res["tintenverhaeltnis"]
        if rand and max(abs(v) for v in rand.values()) > tol:
            teile = ", ".join(f"{n} {v:+.1f}" for n, v in rand.items() if abs(v) > tol)
            fehlerart, text = "Layoutabweichung", f"Inhaltsrahmen weicht aus ({teile} mm; + = Lunivo weiter innen bzw. weiter unten/rechts)"
        elif res["vertikaler_versatz_mm"] is not None and abs(res["vertikaler_versatz_mm"]) > tol:
            fehlerart, text = "Layoutabweichung", f"Inhalt in Lunivo um {res['vertikaler_versatz_mm']:+.1f} mm vertikal verschoben (Zeilenprofil)"
        elif tv is not None and (tv < 0.85 or tv > 1.15):
            fehlerart, text = "Layoutabweichung", f"Tintenmenge Lunivo = {tv * 100:.0f} % der Referenz (Inhalt fehlt oder ist zusätzlich vorhanden)"
        else:
            fehlerart, text = "Renderingabweichung", "Bildabweichung ohne messbare Verschiebung; die Ursache ist aus den Messwerten nicht bestimmbar"
        gross = res["bereiche"][0] if res["bereiche"] else None
        element = _element_an(ctx, erg, i, gross, faktor) if gross else ""
        zusatz = f" — größter Bereich: {gross['art']} bei x={gross['mm'][0]} mm, y={gross['mm'][1]} mm" if gross else ""
        if abw <= 30:
            b.append(K.befund(f"Seite {i + 1}", K.ABWEICHEND, fehlerart, K.schwere_bild(res["anteil"], k["seitenanteil"]),
                              f"Seite {i + 1}: {res['zellen_abweichend']} von {res['zellen_mit_inhalt']} Rasterzellen abweichend ({res['anteil'] * 100:.1f} %, nach Abzug von Versätzen bis {k['verschiebung_mm']:g} mm); {text}{zusatz}",
                              k["seitenanteil"], res["anteil"], seite=i + 1, element=element))
    if abw > 30:
        b.append(K.befund("Weitere Seiten", K.ABWEICHEND, "Layoutabweichung", "mittel", f"Weitere {abw - 30} Seiten weichen ab (Einzelbefunde gekürzt; alle Werte unter „werte“)"))
    if ok:
        b.append(K.passt("Bildvergleich", f"{ok} von {werte['verglichene_seiten']} verglichenen Seiten innerhalb der Toleranz ({k['seitenanteil'] * 100:.0f} % abweichende Rasterzellen)"))
    if soll_seiten and soll_seiten > k["max_seiten"]:
        b.append(K.nicht_pruefbar("Seitenbegrenzung", f"Nur die ersten {k['max_seiten']} Seiten wurden bildlich verglichen"))
    werte["seitenwerte"] = seitenwerte
    werte["nicht_geprueft"] = ["Ursache einzelner Abweichungen (nur Messwerte)", "Seiten ab der Seitenbegrenzung"] if soll_seiten and soll_seiten > k["max_seiten"] else ["Ursache einzelner Abweichungen (nur Messwerte)"]
    return abschluss("layout", b, werte, bilder)


# ---- Exportprüfung ---------------------------------------------------------------------------------------------------
def _gleich_nach_speichern(m1: dict, m2: dict, fehlerart: str, soll_name: str, ist_name: str) -> list[dict]:
    schluessel = [k for k in STRUKTURSCHLUESSEL if k not in ("formatvorlagen", "listen_definitionen", "objekte_frei", "verschachtelte_tabellen", "tabellenzellen")] + list(FORMATSCHLUESSEL)
    b = vergleiche_werte(m1["werte"], m2["werte"], schluessel, fehlerart, soll_name=soll_name, ist_name=ist_name)
    b += vergleiche_texte(m1["texte"], m2["texte"], fehlerart, soll_name, ist_name)
    return b


def pruefe_export(ctx: Kontext) -> dict:
    from kompatibilitaetspruefer.verwaltung.dateisuche import lesbare_endungen, speicherbare_endungen
    from lunivo_writer.werkzeuge.kompatibilitaetspruefer.pruefung.referenzbilder import ReferenzFehler, pdf_info
    g, fehler = ctx.modell()
    if fehler:
        return abschluss("export", [fehler])
    m1 = ctx.metriken()
    b: list[dict] = []
    formate = [f.lower().lstrip(".") for f in ctx.k["exportformate"]]
    speicherbar = {e.lstrip(".") for e in speicherbare_endungen()}
    lesbar = lesbare_endungen()
    werte = {"formate": {}}
    for fmt in formate:
        punkt = f"Export {fmt.upper()}"
        if fmt not in speicherbar:
            b.append(K.nicht_unterstuetzt(punkt, f"Lunivo kann nicht als {fmt.upper()} speichern"))
            continue
        ziel = os.path.join(ctx.tmp, f"export.{fmt}")
        try:
            report = LZ.speichere(g, ziel)
        except BaseException as e:                                                           # noqa: BLE001
            if isinstance(e, KeyboardInterrupt):
                raise
            b.append(K.scheitert(punkt, "Exportfehler", f"Speichern als {fmt.upper()} fehlgeschlagen ({type(e).__name__}): {' '.join(str(e).split())[:300]}"))
            continue
        groesse = os.path.getsize(ziel) if os.path.isfile(ziel) else 0
        if groesse == 0:
            b.append(K.befund(punkt, K.ABWEICHEND, "Exportfehler", "kritisch", f"Die {fmt.upper()}-Datei wurde nicht oder leer geschrieben"))
            continue
        werte["formate"][fmt] = {"groesse": groesse}
        b.append(K.passt(punkt, f"Geschrieben ({groesse} Byte)"))
        b += _warnungen(report, f"Beim Export nach {fmt.upper()} nicht übernommen", 10)
        if fmt == "pdf":
            try:
                n = pdf_info(ziel)["seiten"]
            except ReferenzFehler as e:
                b.append(K.befund("PDF lesbar", K.ABWEICHEND, "Exportfehler", "schwer", f"Die geschriebene PDF lässt sich nicht öffnen: {e}"))
                continue
            soll = len(ctx.layout()[1].seiten)
            if n == soll:
                b.append(K.passt("PDF-Seitenanzahl", f"{n} Seiten wie im Layout", soll, n))
            else:
                b.append(K.befund("PDF-Seitenanzahl", K.ABWEICHEND, "Exportfehler", "schwer", f"PDF hat {n} Seiten, das Layout {soll}", soll, n))
            continue
        if "." + fmt not in lesbar:
            b.append(K.nicht_pruefbar(f"Wiedereinlesen {fmt.upper()}", "Lunivo kann dieses Format nicht lesen"))
            continue
        try:
            g2 = LZ.lade(ziel)
            m2 = LZ.metriken(g2.document)
        except BaseException as e:                                                           # noqa: BLE001
            if isinstance(e, KeyboardInterrupt):
                raise
            b.append(K.scheitert(f"Wiedereinlesen {fmt.upper()}", "Exportfehler", f"Die geschriebene {fmt.upper()}-Datei lässt sich nicht wieder öffnen ({type(e).__name__}): {' '.join(str(e).split())[:200]}"))
            continue
        pruef = _gleich_nach_speichern(m1, m2, "Exportfehler", "Original-Import", f"aus {fmt.upper()}")
        for p in pruef:
            p["punkt"] = f"{fmt.upper()}: {p['punkt']}"
        if fmt == "txt":                                                                      # TXT hat keine Formatierung: Formatzähler sind erwartbar leer
            pruef = [p for p in pruef if not any(x in p["punkt"] for x in ("Fette", "Kursive", "Unterstrichene", "Zentrierte", "Rechtsbündige", "Blocksatz", "Tabellen", "Bilder"))]
            b.append(K.nicht_unterstuetzt("TXT-Export", "TXT speichert keine Formatierung, Tabellen und Bilder"))
        b += pruef
    werte["hinweis"] = "Ein erfolgreicher Export und Wiedereinlesen in Lunivo belegt nicht die Kompatibilität mit Word oder anderen Programmen."
    werte["nicht_geprueft"] = ["Öffnen der Ausgabe in Fremdprogrammen", "Darstellung der Ausgabe"]
    return abschluss("export", b, werte)


# ---- Roundtrip-Prüfung -----------------------------------------------------------------------------------------------
def pruefe_roundtrip(ctx: Kontext) -> dict:
    g, fehler = ctx.modell()
    if fehler:
        return abschluss("roundtrip", [fehler])
    ziel_endung = ROUNDTRIP_ZIEL.get(ctx.endung)
    if ziel_endung is None:
        return abschluss("roundtrip", [K.nicht_pruefbar("Roundtrip", f"Für {ctx.endung} gibt es kein Speicherformat; der Roundtrip ist nicht möglich")])
    b: list[dict] = []
    werte = {"zielformat": ziel_endung}
    ziel = os.path.join(ctx.tmp, "roundtrip" + ziel_endung)
    try:
        report = LZ.speichere(g, ziel)
    except BaseException as e:                                                               # noqa: BLE001
        if isinstance(e, KeyboardInterrupt):
            raise
        return abschluss("roundtrip", [K.scheitert("Speichern", "Roundtrip-Fehler", f"Speichern als {ziel_endung} fehlgeschlagen ({type(e).__name__}): {' '.join(str(e).split())[:300]}")])
    b.append(K.passt("Speichern", f"Kopie als {ziel_endung} geschrieben"))
    b += _warnungen(report, "Beim Speichern nicht übernommen", 15)
    try:
        g2 = LZ.lade(ziel)
        m2 = LZ.metriken(g2.document)
    except BaseException as e:                                                               # noqa: BLE001
        if isinstance(e, KeyboardInterrupt):
            raise
        b.append(K.scheitert("Wiedereinlesen", "Roundtrip-Fehler", f"Die gespeicherte Kopie lässt sich nicht wieder öffnen ({type(e).__name__}): {' '.join(str(e).split())[:300]}"))
        return abschluss("roundtrip", b, werte)
    b.append(K.passt("Wiedereinlesen", "Kopie ohne Ausnahme geöffnet"))
    m1 = ctx.metriken()
    pruef = _gleich_nach_speichern(m1, m2, "Roundtrip-Fehler", "Original-Import", "nach Roundtrip")
    if ziel_endung == ".txt":
        pruef = [p for p in pruef if not any(x in p["punkt"] for x in ("Fette", "Kursive", "Unterstrichene", "Zentrierte", "Rechtsbündige", "Blocksatz"))]
    b += pruef
    try:
        s1, s2 = len(ctx.layout()[1].seiten), len(LZ.layout(g2.document)[1].seiten)
        b.append(K.passt("Seitenanzahl", f"{s1} Seiten", s1, s2) if s1 == s2 else
                 K.befund("Seitenanzahl", K.ABWEICHEND, "Roundtrip-Fehler", "mittel", f"Layout: Original-Import {s1} Seiten, nach Roundtrip {s2}", s1, s2))
    except Exception as e:                                                                   # noqa: BLE001
        b.append(K.nicht_pruefbar("Seitenanzahl", f"Layout nicht berechenbar: {type(e).__name__}"))
    if ctx.k.get("roundtrip_bearbeitung"):
        b += _roundtrip_bearbeitung(ctx, ziel_endung)
    werte["hinweis"] = "Ein erfolgreicher Roundtrip innerhalb von Lunivo ist kein Nachweis für die Kompatibilität mit Microsoft Word oder anderen Programmen."
    werte["nicht_geprueft"] = ["Kompatibilität mit Fremdprogrammen", "Darstellung nach dem Roundtrip"]
    return abschluss("roundtrip", b, werte)


def _roundtrip_bearbeitung(ctx: Kontext, ziel_endung: str) -> list[dict]:
    """Gezielte Bearbeitung: Marke am Dokumentanfang einfügen (über die Bearbeitungssitzung), speichern, neu öffnen, Text vergleichen."""
    from core.bearbeitung import Bearbeitungssitzung
    punkt = "Roundtrip mit Bearbeitung"
    try:
        g = LZ.lade(ctx.pfad, ctx.job.get("kennwort"))
        sitzung = Bearbeitungssitzung(g.document)
        sitzung.text_einfuegen(MARKE, g.document.anfang())
        erwartet = [a.text() for a in g.document.absaetze()]
        ziel = os.path.join(ctx.tmp, "bearbeitet" + ziel_endung)
        LZ.speichere(g, ziel)
        g2 = LZ.lade(ziel)
        gelesen = [a.text() for a in g2.document.absaetze()]
    except BaseException as e:                                                               # noqa: BLE001
        if isinstance(e, KeyboardInterrupt):
            raise
        return [K.scheitert(punkt, "Roundtrip-Fehler", f"Bearbeitung/Speichern/Öffnen fehlgeschlagen ({type(e).__name__}): {' '.join(str(e).split())[:300]}")]
    b = []
    if sum(t.count(MARKE) for t in gelesen) == 1:
        b.append(K.passt(f"{punkt}: Marke", "Die eingefügte Marke steht genau einmal in der gespeicherten Datei"))
    else:
        b.append(K.befund(f"{punkt}: Marke", K.ABWEICHEND, "Roundtrip-Fehler", "schwer", f"Eingefügte Marke {sum(t.count(MARKE) for t in gelesen)}× statt 1× nach dem Speichern"))
    for p in vergleiche_texte(erwartet, gelesen, "Roundtrip-Fehler", "bearbeitetes Modell", "nach Speichern"):
        p["punkt"] = f"{punkt}: {p['punkt']}"
        b.append(p)
    return b


# ---- Darstellung (ohne Beurteilung, für den Vergleichsbereich) ---------------------------------------------------------
def erzeuge_darstellung(ctx: Kontext) -> dict:
    from lunivo_writer.werkzeuge.kompatibilitaetspruefer.pruefung import referenzbilder
    g, fehler = ctx.modell()
    if fehler:
        return abschluss("darstellung", [fehler])
    le, erg = ctx.layout()
    lun = LZ.seitenbilder(g.document, le, erg, ctx.bildordner(), "lun", ctx.k["rendern_dpi_faktor"], ctx.k["max_seiten"])
    bilder = {"lunivo": lun, "referenz": []}
    b = [K.passt("Darstellung", f"{len(lun)} Seiten dargestellt")]
    try:
        r = referenzbilder.referenzseiten(ctx.ref, ctx.bildordner(), ctx.k["max_seiten"], ctx.k["rendern_dpi_faktor"]) if ctx.ref else None
        if r:
            bilder["referenz"] = r["pfade"]
    except referenzbilder.ReferenzFehler as e:
        b.append(K.fehlt("Referenzdarstellung", str(e)))
    return abschluss("darstellung", b, {"seiten": len(erg.seiten)}, bilder)


ARTEN = {"import": pruefe_import, "struktur": pruefe_struktur, "format": pruefe_format, "layout": pruefe_layout, "export": pruefe_export,
         "roundtrip": pruefe_roundtrip, "darstellung": erzeuge_darstellung}


def verfuegbarkeit(art: str, endung: str, ref: dict | None, zustand: str) -> tuple[bool, str]:
    """Ob eine Prüfart für eine Datei sinnvoll ausführbar ist und, wenn nicht oder nur eingeschränkt, warum. ``zustand``: Formatzustand der Datei."""
    if zustand != "unterstuetzt":
        return False, "Format wird von Lunivo nicht gelesen" if zustand == "nicht_unterstuetzt" else "PDF ist nur Referenz bzw. Ausgabe, kein Importformat"
    if art == "roundtrip" and ROUNDTRIP_ZIEL.get(endung) is None:
        return False, f"Kein Speicherformat für {endung}"
    sichtbar = bool(ref and (ref.get("pdf") or ref.get("bilder")))
    if art == "layout" and not sichtbar:
        return True, "nur Lauf der Layout-Engine; ohne Referenz-PDF/Seitenbilder kein visueller Vergleich"
    if art == "struktur" and endung not in (".docx", ".dotx", ".docm", ".odt", ".fodt", ".txt", ".text", "") and not (ref and ref.get("erwartet")):
        return True, "ohne Quellzählung für dieses Format nur mit erwarteten Strukturen beurteilbar"
    if art == "format" and endung not in (".docx", ".dotx", ".docm") and not (ref and ref.get("erwartet")):
        return True, "Formatzählung der Quelle nur für DOCX; sonst nur mit erwarteten Werten beurteilbar"
    return True, ""
