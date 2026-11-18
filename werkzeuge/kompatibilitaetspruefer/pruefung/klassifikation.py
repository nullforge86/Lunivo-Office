"""Festgelegte Kriterien für Prüfstatus, Fehlerart und Schweregrad. Alle Einstufungen im Werkzeug laufen über diese Datei.

Prüfpunkt-Status (je einzelner Vergleich):
    uebereinstimmend   gemessen und gleich
    abweichend         gemessen und verschieden
    nicht_unterstuetzt Lunivo meldet die Eigenschaft ausdrücklich als nicht unterstützt
    nicht_pruefbar     die Messung war technisch nicht möglich (z. B. Format ohne Zählbarkeit)
    referenz_fehlt     es gibt nichts, womit verglichen werden könnte

Ergebnis-Status (je Datei und Prüfart), siehe ``ergebnisstatus``:
    bestanden        alle Prüfpunkte der Prüfart sind ``uebereinstimmend``
    teilweise        mindestens ein Prüfpunkt stimmt, der Rest konnte nicht beurteilt werden — zählt NICHT als bestanden
    auffaellig       mindestens ein Prüfpunkt ist ``abweichend``
    nicht_pruefbar   kein einziger Prüfpunkt konnte beurteilt werden
    fehlgeschlagen   Prüfung selbst fehlgeschlagen (Import-/Export-/Roundtrip-Ausnahme, Absturz, Zeitüberschreitung, Speichergrenze)
    abgebrochen      vom Benutzer abgebrochen — nie bestanden

Schweregrade (Kriterien):
    kritisch  Dokument kann nicht verarbeitet werden, oder das Modell enthält keinen Inhalt, obwohl die Referenz Inhalt hat
    schwer    Inhalt, Struktur oder Seitenzahl weicht deutlich ab (Verlust von Text/Absätzen/Tabellen/Bildern ≥ 50 %, geänderte Reihenfolge, Seitenzahl)
    mittel    erkennbare Abweichung: Verlust unter 50 %, Mehrinhalt, Formatverlust über 10 %, Positionsverschiebung über Toleranz, größere Bildabweichung
    gering    kleine Abweichung ohne nachgewiesenen Inhaltsverlust (Formatverlust bis 10 %, kleine Verschiebung, geringe Bildabweichung)
    hinweis   kein Fehler: fehlende Referenz, dokumentierte Nicht-Unterstützung, Information
"""
from __future__ import annotations

UEBEREINSTIMMEND, ABWEICHEND, NICHT_UNTERSTUETZT, NICHT_PRUEFBAR, REFERENZ_FEHLT = (
    "uebereinstimmend", "abweichend", "nicht_unterstuetzt", "nicht_pruefbar", "referenz_fehlt")
BESTANDEN, TEILWEISE, AUFFAELLIG, FEHLGESCHLAGEN, ABGEBROCHEN = "bestanden", "teilweise", "auffaellig", "fehlgeschlagen", "abgebrochen"
OFFEN = "offen"

FEHLERARTEN = ("Importfehler", "Strukturfehler", "Formatierungsfehler", "Layoutabweichung", "Renderingabweichung", "Exportfehler",
               "Roundtrip-Fehler", "Fehlende Referenz", "Nicht unterstützte Eigenschaft", "Technischer Prüffehler")
SCHWEREN = ("kritisch", "schwer", "mittel", "gering", "hinweis")
SCHWERE_RANG = {s: i for i, s in enumerate(SCHWEREN)}

PRUEFARTEN = ("import", "struktur", "format", "layout", "export", "roundtrip", "gesamt")
PRUEFART_NAMEN = {"import": "Importprüfung", "struktur": "Strukturprüfung", "format": "Formatierungsprüfung", "layout": "Layoutprüfung",
                  "export": "Exportprüfung", "roundtrip": "Roundtrip-Prüfung", "gesamt": "Gesamtprüfung"}
STATUS_NAMEN = {OFFEN: "offen", BESTANDEN: "bestanden", TEILWEISE: "teilweise geprüft", AUFFAELLIG: "auffällig", FEHLGESCHLAGEN: "fehlgeschlagen",
                "nicht_pruefbar": "nicht prüfbar", ABGEBROCHEN: "abgebrochen", "laeuft": "läuft"}
PUNKT_NAMEN = {UEBEREINSTIMMEND: "übereinstimmend", ABWEICHEND: "abweichend", NICHT_UNTERSTUETZT: "nicht unterstützt",
               NICHT_PRUEFBAR: "nicht prüfbar", REFERENZ_FEHLT: "Referenz fehlt"}


def befund(punkt: str, status: str, fehlerart: str = "", schwere: str = "hinweis", beschreibung: str = "", soll=None, ist=None,
           seite: int | None = None, element: str = "") -> dict:
    """Ein Prüfpunkt. ``soll`` ist der Referenzwert, ``ist`` der von Lunivo gemessene."""
    return {"punkt": punkt, "status": status, "fehlerart": fehlerart, "schwere": schwere, "beschreibung": beschreibung,
            "soll": soll, "ist": ist, "seite": seite, "element": element}


def scheitert(punkt: str, fehlerart: str, beschreibung: str, schwere: str = "kritisch", **zusatz) -> dict:
    """Ein Verarbeitungsschritt ist fehlgeschlagen (Ausnahme, Absturz, Grenze): Das Ergebnis der Prüfart ist ``fehlgeschlagen``."""
    b = befund(punkt, ABWEICHEND, fehlerart, schwere, beschreibung, **zusatz)
    b["abbruch"] = True
    return b


def passt(punkt: str, beschreibung: str = "", soll=None, ist=None) -> dict:
    return befund(punkt, UEBEREINSTIMMEND, "", "hinweis", beschreibung, soll, ist)


def fehlt(punkt: str, grund: str, fehlerart: str = "Fehlende Referenz") -> dict:
    return befund(punkt, REFERENZ_FEHLT, fehlerart, "hinweis", grund)


def nicht_pruefbar(punkt: str, grund: str) -> dict:
    return befund(punkt, NICHT_PRUEFBAR, "", "hinweis", grund)


def nicht_unterstuetzt(punkt: str, text: str) -> dict:
    return befund(punkt, NICHT_UNTERSTUETZT, "Nicht unterstützte Eigenschaft", "hinweis", text)


def schwere_menge(soll: float, ist: float) -> str:
    """Schweregrad für eine Mengenabweichung (Absätze, Tabellen, Bilder, Zeichen …)."""
    if soll > 0 and ist <= 0:
        return "kritisch"
    if ist < soll:
        return "schwer" if (soll - ist) / soll >= 0.5 else "mittel"
    return "mittel"                                                    # Mehrinhalt


def schwere_format(soll: float, ist: float) -> str:
    """Schweregrad für Formatverlust (Quelle hat ``soll`` formatierte Zeichen, Modell ``ist``)."""
    if soll <= 0:
        return "gering"
    verlust = (soll - ist) / soll
    return "schwer" if verlust > 0.5 else "mittel" if verlust > 0.1 else "gering"


def schwere_bild(anteil: float, toleranz_anteil: float) -> str:
    """Schweregrad für Bildabweichung nach dem Anteil abweichender Bildzellen."""
    if anteil <= toleranz_anteil:
        return "gering"
    return "schwer" if anteil > 0.30 else "mittel"


def ergebnisstatus(befunde: list[dict]) -> str:
    """Gesamtstatus einer Prüfart aus ihren Prüfpunkten (Kriterien siehe Modulkopf)."""
    if not befunde:
        return "nicht_pruefbar"
    status = [b["status"] for b in befunde]
    if any(b.get("abbruch") for b in befunde):
        return FEHLGESCHLAGEN
    if ABWEICHEND in status:
        return AUFFAELLIG
    beurteilt = status.count(UEBEREINSTIMMEND)
    if beurteilt == 0:
        return "nicht_pruefbar"
    if beurteilt == len(status):
        return BESTANDEN
    # Nicht unterstützte Eigenschaften sind dokumentierte Grenzen, aber keine bestandene Prüfung
    return TEILWEISE


def schlimmste_schwere(befunde: list[dict]) -> str:
    rest = [b["schwere"] for b in befunde if b["status"] in (ABWEICHEND, "fehlgeschlagen") or b["schwere"] == "kritisch"]
    return min(rest, key=SCHWERE_RANG.get) if rest else "hinweis"


def haupt_fehlerart(befunde: list[dict]) -> str:
    """Fehlerart des schwersten abweichenden Prüfpunkts; sonst die der Hinweise (fehlende Referenz, nicht unterstützt)."""
    abw = [b for b in befunde if b["status"] == ABWEICHEND or b["schwere"] == "kritisch"]
    if abw:
        return min(abw, key=lambda b: SCHWERE_RANG.get(b["schwere"], 9))["fehlerart"]
    for art in ("Fehlende Referenz", "Nicht unterstützte Eigenschaft"):
        if any(b["fehlerart"] == art for b in befunde):
            return art
    return ""


def schwerer(a: str, b: str) -> str:
    return a if SCHWERE_RANG.get(a, 9) <= SCHWERE_RANG.get(b, 9) else b


def gesamt_status(stati: list[str]) -> str:
    """Status einer Datei über mehrere Prüfarten (der ungünstigste zählt; ohne Ergebnis: offen)."""
    if not stati:
        return OFFEN
    for s in (FEHLGESCHLAGEN, ABGEBROCHEN, AUFFAELLIG, TEILWEISE, "nicht_pruefbar"):
        if s in stati:
            return s
    return BESTANDEN
