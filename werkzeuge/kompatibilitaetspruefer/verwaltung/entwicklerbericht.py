"""Aufbereitung der Fehlergruppen für die Entwickler-KI: strukturierter JSON-Bericht, lesbarer Arbeitsauftrag und übertragbares Fehlerpaket (ZIP).

Alle Angaben stammen aus gespeicherten Prüfergebnissen; nichts wird ergänzt oder erfunden. Der Ursachenbereich bleibt eine Vermutung, solange er nicht ausdrücklich bestätigt wurde.
Nichts wird automatisch übertragen: Bericht, Arbeitsauftrag und Paket werden nur lokal erzeugt und vom Benutzer weitergegeben. Dokumentdateien kommen nur ins Paket, wenn der Benutzer
das ausdrücklich wählt; Dokumenttexte sind nie Teil des Berichts.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import zipfile

from kompatibilitaetspruefer.pruefung.klassifikation import PRUEFART_NAMEN
from kompatibilitaetspruefer.verwaltung.fehlerverlauf import STATUS_NAMEN, UNBEARBEITET, URSACHE_NAMEN

BERICHTSVERSION = "1.0"
AUSWAHL_MODI = (("alle", "Alle Fehlergruppen"), ("kritisch", "Nur kritische Fehler"), ("docx", "Nur DOCX-Fehler"), ("odt", "Nur ODT-Fehler"), ("rtf", "Nur RTF-Fehler"),
                ("ausgewaehlt", "Nur ausgewählte Fehlergruppen"), ("unbearbeitet", "Nur bisher unbearbeitete Fehler"))
PFADMODI = (("name", "Nur Dateinamen (empfohlen)"), ("anonym", "Anonymisiert (Dokument-001, …)"), ("voll", "Vollständige Pfade"))

ARBEITSAUFTRAG_KOPF = (
    "Untersuche die folgenden tatsächlich festgestellten Kompatibilitätsabweichungen in Lunivo Office.\n"
    "Beginne mit den schwerwiegendsten und am häufigsten auftretenden Fehlergruppen.\n"
    "Ermittle die tatsächlichen Ursachen im bestehenden Quellcode.\n"
    "Behebe die Ursachen innerhalb der vorhandenen Architektur.\n"
    "Erstelle keine zweite Dokument-Engine.\n"
    "Verändere keine unabhängigen Funktionen ohne Notwendigkeit.\n"
    "Führe keine automatischen Tests ohne meine ausdrückliche Freigabe aus.\n"
    "Dokumentiere, welche Fehlergruppen durch welche Codeänderungen bearbeitet wurden.\n"
    "Behaupte keine erfolgreiche Fehlerbehebung, solange diese nicht durch eine genehmigte erneute Prüfung bestätigt wurde.")


def auswahl_filtern(gruppen: list[dict], modus: str, ausgewaehlt: set[str] | None = None) -> list[dict]:
    """Die zu übergebenden Fehlergruppen nach Auswahlmodus (siehe ``AUSWAHL_MODI``)."""
    if modus == "kritisch":
        return [g for g in gruppen if g["schwere"] == "kritisch"]
    if modus in ("docx", "odt", "rtf"):
        return [g for g in gruppen if g["format"] == modus]
    if modus == "ausgewaehlt":
        return [g for g in gruppen if g["gruppe_id"] in (ausgewaehlt or set())]
    if modus == "unbearbeitet":
        return [g for g in gruppen if g["status"] in UNBEARBEITET]
    return list(gruppen)


def zaehlung(gruppen: list[dict]) -> dict:
    """Vorschau vor dem Export: Anzahl Fehlergruppen und betroffener Dokumente."""
    return {"gruppen": len(gruppen), "dokumente": len({d for g in gruppen for d in g["dokumente"]})}


class _Namen:
    """Dokumentbezeichnungen im Bericht nach Datenschutzmodus; gleiche Namen verschiedener Ordner bleiben unterscheidbar."""

    def __init__(self, modus: str, pfade):
        self.modus = modus
        self.pfade = sorted(set(pfade))
        zaehl: dict[str, int] = {}
        for p in self.pfade:
            n = os.path.basename(p)
            zaehl[n] = zaehl.get(n, 0) + 1
        self._zaehl = zaehl
        self._index = {p: i for i, p in enumerate(self.pfade, 1)}

    def index_von(self, pfad: str) -> int:
        return self._index.get(pfad, 0)

    def __call__(self, pfad: str) -> str:
        if self.modus == "voll":
            return pfad
        if self.modus == "anonym":
            return f"Dokument-{self._index.get(pfad, 0):03d}" + os.path.splitext(pfad)[1].lower()
        n = os.path.basename(pfad)
        if self._zaehl.get(n, 0) > 1:
            return f"{n} [{hashlib.sha1(pfad.encode('utf-8')).hexdigest()[:4]}]"
        return n


def _zeit_text(z) -> str | None:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(z)) if z else None


def _kurz(text: str, n: int = 300) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= n else text[: n - 1] + "…"


def _sicher_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text)[:60] or "datei"


def _archivname(namen: "_Namen", pfad: str) -> str:
    """Eindeutiger, kurzer Dateiname im Paket mit erhaltener Endung. Nie ein ganzer Pfad; im anonymen Modus nie der echte Dateiname."""
    endung = os.path.splitext(pfad)[1].lower()
    nr = namen.index_von(pfad)
    if namen.modus == "anonym":
        return f"{nr:04d}_Dokument{endung}"
    stamm = os.path.splitext(os.path.basename(pfad))[0]
    return f"{nr:04d}_{_sicher_name(stamm)[:50]}{endung}"


def bericht_erstellen(gruppen: list[dict], kontext: dict, optionen: dict) -> tuple[dict, list[tuple[str, str]], list[tuple[str, str]]]:
    """→ (Bericht als dict, Nachweisdateien [(Archivname, Quellpfad)], Originaldokumente [(Archivname, Quellpfad)]).

    ``kontext``: ``datenquelle`` (Text), ``datensaetze``, ``konfig``, ``lunivo_version``, ``dateiliste`` (Sitzungsdateien mit ``pfad`` und ``referenz`` — ``None`` bei
    gespeichertem Verlauf), ``zeit``. ``optionen``: ``pfade`` (name | anonym | voll), ``bilder`` (bool), ``originale`` (bool)."""
    alle_pfade = {d for g in gruppen for d in g["dokumente"]} | {r["pfad"] for r in kontext["datensaetze"]} | {f["pfad"] for f in (kontext.get("dateiliste") or [])}
    namen = _Namen(optionen.get("pfade", "name"), alle_pfade)
    lookup = {(r["pfad"], r["art"]): r for r in kontext["datensaetze"]}
    nachweise: list[tuple[str, str]] = []
    originale: list[tuple[str, str]] = []
    eintraege = []
    for g in gruppen:
        dateien_g: list[str] = []
        if optionen.get("bilder"):
            for d in g["dokumentliste"][:3]:
                rec = lookup.get((d["pfad"], g["art"])) or {}
                for art_ in ("lunivo", "referenz"):
                    vorhanden = [x for x in rec.get("bilder", {}).get(art_, []) if isinstance(x, str) and os.path.isfile(x)]
                    for i, p in enumerate(vorhanden[:3], 1):
                        arch = f"nachweise/{g['gruppe_id']}/{os.path.splitext(_archivname(namen, d['pfad']))[0]}_{art_}_{i}{os.path.splitext(p)[1].lower()}"
                        nachweise.append((arch, p))
                        dateien_g.append(arch)
        alle_namen = [namen(d["pfad"]) for d in g["dokumentliste"]]
        eintraege.append({
            "id": g["gruppe_id"], "rang": g["rang"], "prioritaet": g["prioritaet"], "prioritaet_begruendung": g["prioritaet_gruende"],
            "dateiformat": g["format"].upper(), "pruefart": PRUEFART_NAMEN.get(g["art"], g["art"]), "fehlerart": g["fehlerart"], "pruefpunkt": g["punkt"],
            "beobachteter_fehler": f"{g['fehlerart']} beim Prüfpunkt „{g['punkt']}“ in der {PRUEFART_NAMEN.get(g['art'], g['art'])}",
            "vermuteter_ursachenbereich": g["bereich"],
            "bestaetigte_ursache": (g["notiz"] or "vom Benutzer als bestätigt markiert (ohne Notiz)") if g["ursache"] == "bestaetigt" else None,
            "ursachenstatus": URSACHE_NAMEN.get(g["ursache"], g["ursache"]),
            "schweregrad": g["schwere"], "bearbeitungsstatus": STATUS_NAMEN.get(g["status"], g["status"]),
            "anzahl_dokumente": g["anzahl"], "dokumente": alle_namen[:300], "weitere_dokumente_nicht_aufgelistet": max(0, len(alle_namen) - 300),
            "beispielhafte_seiten": sorted(g["seiten"])[:10],
            "vergleichsdaten": {"mit_referenz_pdf_oder_seitenbildern": g["referenzen"].get("visuell", 0), "nur_erwartete_werte": g["referenzen"].get("strukturell", 0),
                                "ohne_referenz": g["referenzen"].get("keine", 0)},
            "einzelne_nachweise": [{"dokument": namen(b["pfad"]), "seite": b["seite"], "element": b["element"], "soll": b["soll"], "ist": b["ist"], "schweregrad": b["schwere"],
                                    "beschreibung": _kurz(b["beschreibung"])} for b in g["beispiele"]],
            "dateien": dateien_g,
            "bekannte_korrekturversuche": [{"zeitpunkt": _zeit_text(k["zeit"]), "beschreibung": k["beschreibung"], "betroffene_module": k["module"], "lunivo_kennung": k["lunivo_version"],
                                            "quelle": k["quelle"], "status_erneute_pruefung": k["pruefstatus"], "als_tatsache_nachgewiesen": k["pruefstatus"].startswith("durch erneute")}
                                           for k in g["korrekturen"]]})
    if optionen.get("originale"):
        for p in sorted({d["pfad"] for g in gruppen for d in g["dokumentliste"]}):
            if os.path.isfile(p):
                originale.append((f"originale/{_archivname(namen, p)}", p))
    dl = kontext.get("dateiliste")
    verwertbar = {r["pfad"] for r in kontext["datensaetze"] if r["status"] not in ("offen", "abgebrochen", "nicht_pruefbar")}
    geprueft = sorted({namen(p) for p in verwertbar})
    nicht_geprueft: list[dict] = []
    ohne_ref: list[str] = []
    if dl is not None:
        for f in dl:
            if f["pfad"] not in verwertbar:
                nicht_geprueft.append({"dokument": namen(f["pfad"]), "grund": "kein verwertbares Prüfergebnis (nicht geprüft, abgebrochen oder nicht prüfbar)"})
            if f.get("referenz") in ("keine", "fehlt"):
                ohne_ref.append(namen(f["pfad"]))
    else:
        ohne_ref = [namen(p) for p in {r["pfad"] for r in kontext["datensaetze"] if r.get("referenz") == "keine"}]
    hinweise = ["Ursachenbereiche sind technische Vermutungen des Testers und keine Diagnose, solange „bestaetigte_ursache“ leer ist.",
                "Korrekturversuche stammen aus Meldungen und gelten erst nach einer durchgeführten erneuten Prüfung als bestätigt."]
    if dl is None:
        hinweise.append("Datenquelle ist ein gespeicherter Prüflauf: nicht geprüfte Dokumente der damaligen Sitzung sind nicht bekannt.")
    bericht = {
        "berichtsversion": BERICHTSVERSION, "erstellt": _zeit_text(time.time()), "datenquelle": kontext["datenquelle"], "pruefzeitpunkt": _zeit_text(kontext.get("zeit")),
        "lunivo_komponenten": {"kennung": kontext.get("lunivo_version", ""), "bedeutung": "Hashwert über Größe und Änderungszeit der Quelldateien der geprüften Lunivo-Pakete"},
        "pruefkonfiguration": kontext.get("konfig", {}),
        "datenschutz": {"pfadangaben": dict(PFADMODI).get(optionen.get("pfade", "name")), "enthaelt_dokumenttexte": False,
                        "enthaelt_originaldokumente": bool(optionen.get("originale")), "enthaelt_vergleichsbilder": bool(optionen.get("bilder"))},
        "dokumente": {"geprueft": geprueft, "nicht_geprueft": nicht_geprueft, "ohne_referenz": sorted(set(ohne_ref)),
                      "originale_im_paket": {namen(p): arch for arch, p in ((a, q) for a, q in originale)}},
        "fehlergruppen": eintraege, "zusammenfassung": zaehlung(gruppen), "hinweise": hinweise}
    return bericht, nachweise, originale


def arbeitsauftrag(bericht: dict) -> str:
    """Lesbarer Arbeitsauftrag für die Entwickler-KI aus genau den Daten des Berichts."""
    z = []
    z.append("ARBEITSAUFTRAG FÜR DIE ENTWICKLER-KI — Lunivo Office: Kompatibilitätsabweichungen")
    z.append(f"Erstellt vom Lunivo Compatibility Tester am {bericht['erstellt']} (Berichtsversion {bericht['berichtsversion']})")
    z.append("")
    z.append(ARBEITSAUFTRAG_KOPF)
    z.append("")
    z.append("HINWEISE ZU DEN DATEN")
    z.append("- Alle Angaben stammen aus gespeicherten Prüfergebnissen des Testers. Nichts wurde ergänzt; fehlt eine Angabe, ist sie nicht bekannt.")
    z.append("- „Vermuteter Ursachenbereich“ ist eine technische Vermutung, keine Diagnose. Ermittle die tatsächliche Ursache im Quellcode selbst.")
    z.append("- Die Fehlergruppen-IDs (FG-…) sind im strukturierten Bericht (bericht.json) identisch. Nenne diese IDs bei jeder Rückmeldung.")
    z.append(f"- Dokumentangaben: {bericht['datenschutz']['pfadangaben']}. Der Bericht enthält keine Dokumenttexte.")
    z.append("")
    d = bericht["dokumente"]
    z.append("PRÜFUMFANG")
    z.append(f"Datenquelle: {bericht['datenquelle']}")
    z.append(f"Prüfzeitpunkt: {bericht['pruefzeitpunkt'] or 'unbekannt'}")
    z.append(f"Lunivo-Kennung der geprüften Komponenten: {bericht['lunivo_komponenten']['kennung'] or 'unbekannt'}")
    z.append(f"Geprüfte Dokumente: {len(d['geprueft'])} · nicht geprüft: {len(d['nicht_geprueft'])} · ohne Referenz: {len(d['ohne_referenz'])}")
    z.append(f"Übergebene Fehlergruppen: {bericht['zusammenfassung']['gruppen']} (betroffene Dokumente: {bericht['zusammenfassung']['dokumente']})")
    z.append("")
    z.append("FEHLERGRUPPEN (nach Priorität)")
    if not bericht["fehlergruppen"]:
        z.append("(keine Fehlergruppen in der Auswahl)")
    for g in bericht["fehlergruppen"]:
        z.append("")
        z.append(f"{g['rang']}. {g['id']} — Schweregrad {g['schweregrad']} · {g['dateiformat']} · {g['pruefart']} · {g['fehlerart']}")
        z.append(f"   Beobachteter Fehler: {g['beobachteter_fehler']}")
        z.append(f"   Betroffene Dokumente ({g['anzahl_dokumente']}): " + ", ".join(g["dokumente"][:10]) +
                 (f" … (+{g['anzahl_dokumente'] - 10} weitere)" if g["anzahl_dokumente"] > 10 else ""))
        if g["beispielhafte_seiten"]:
            z.append("   Beispielhafte Seiten: " + ", ".join(str(s) for s in g["beispielhafte_seiten"]))
        v = g["vergleichsdaten"]
        z.append(f"   Vergleichsdaten: {v['mit_referenz_pdf_oder_seitenbildern']} Dokumente mit Referenz-PDF/Seitenbildern, {v['nur_erwartete_werte']} mit nur erwarteten Werten, "
                 f"{v['ohne_referenz']} ohne Referenz")
        for b in g["einzelne_nachweise"][:5]:
            teile = [b["dokument"] + (f", Seite {b['seite']}" if b["seite"] else "") + (f", {b['element']}" if b["element"] else "")]
            if b["soll"] or b["ist"]:
                teile.append(f"Soll: {b['soll'] or '–'} / Ist: {b['ist'] or '–'}")
            if b["beschreibung"]:
                teile.append(b["beschreibung"])
            z.append("     - " + " — ".join(teile))
        if g["bestaetigte_ursache"]:
            z.append(f"   Ursache: vom Benutzer bestätigt — {g['bestaetigte_ursache']} (Bereich: {g['vermuteter_ursachenbereich']})")
        else:
            z.append(f"   Vermuteter Ursachenbereich: {g['vermuteter_ursachenbereich']} (nur vermutet, nicht bestätigt)")
        z.append(f"   Priorität {g['prioritaet']}: " + "; ".join(g["prioritaet_begruendung"]))
        z.append(f"   Bearbeitungsstatus: {g['bearbeitungsstatus']}")
        for k in g["bekannte_korrekturversuche"]:
            z.append(f"   Bisheriger Korrekturversuch ({k['zeitpunkt']}, {k['quelle']}): {k['beschreibung'] or '(ohne Beschreibung)'}"
                     f" — Module: {k['betroffene_module'] or 'nicht angegeben'} — erneute Prüfung: {k['status_erneute_pruefung']}")
        if g["dateien"]:
            z.append("   Nachweisdateien im Paket: " + ", ".join(g["dateien"]))
    z.append("")
    z.append("RÜCKMELDUNG")
    z.append("Nenne nach deiner Arbeit je Fehlergruppen-ID die geänderten Module und eine kurze Beschreibung der Änderung, damit sie im Tester als „Korrektur gemeldet“ erfasst "
             "werden kann. Ob eine Gruppe behoben ist, entscheidet erst eine vom Benutzer gestartete erneute Prüfung.")
    return "\n".join(z) + "\n"


def paket_schreiben(pfad: str, bericht: dict, text: str, nachweise: list[tuple[str, str]], originale: list[tuple[str, str]]) -> int:
    """Schreibt das Fehlerpaket (ZIP) atomar. → Anzahl der Dateien im Paket."""
    tmp = pfad + ".tmp"
    n = 2
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("bericht.json", json.dumps(bericht, ensure_ascii=False, indent=2, default=str))
        z.writestr("arbeitsauftrag.txt", text)
        for arch, quelle in nachweise + originale:
            z.write(quelle, arch)
            n += 1
    os.replace(tmp, pfad)
    return n


def json_schreiben(pfad: str, bericht: dict) -> None:
    tmp = pfad + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(bericht, f, ensure_ascii=False, indent=2, default=str)
    os.replace(tmp, pfad)
