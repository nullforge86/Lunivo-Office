"""Export der tatsächlich gespeicherten Ergebnisse (CSV, JSON, PDF). Exportiert wird nur, was in der Datenbank steht; nichts wird ergänzt oder geschätzt."""
from __future__ import annotations

import csv
import json
import os
import time

from kompatibilitaetspruefer.pruefung.klassifikation import PRUEFART_NAMEN, STATUS_NAMEN
from kompatibilitaetspruefer.verwaltung.datenbank import Datenbank

REFERENZ_NAMEN = {"keine": "keine Referenz", "strukturell": "nur erwartete Werte", "visuell": "PDF/Seitenbilder"}
SPALTEN = ("Dokument", "Pfad", "Dateiformat", "Ursprungsprogramm", "Prüfart", "Ergebnis", "Fehlerart", "Schweregrad", "Beschreibung", "Referenzstatus", "Seite", "Element",
           "Prüfkonfiguration", "Lunivo-Version", "Zeitpunkt")


def _zeile(r: dict) -> list:
    return [r["name"], r["pfad"], r["endung"], r["programm"], PRUEFART_NAMEN.get(r["art"], r["art"]), STATUS_NAMEN.get(r["status"], r["status"]), r["fehlerart"], r["schwere"],
            r["beschreibung"], REFERENZ_NAMEN.get(r["referenz"], r["referenz"]), r["seite"] or "", r["element"], r["konfig_hash"], r["lunivo_version"],
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r["zeit"])) if r["zeit"] else ""]


def _sicher(x):
    """Zellen, die ein Tabellenprogramm als Formel deuten würde, werden entschärft."""
    return "'" + x if isinstance(x, str) and x[:1] in ("=", "+", "-", "@", "\t", "\r") else x


def exportiere(db: Datenbank, pfad: str, format_: str, zeilen: list[dict] | None = None) -> int:
    """Schreibt die Ergebnisse (``zeilen`` aus ``db.ergebniszeilen()``, ggf. gefiltert) nach ``pfad``. → Anzahl der Zeilen."""
    zeilen = db.ergebniszeilen() if zeilen is None else zeilen
    format_ = format_.lower()
    tmp = pfad + ".tmp"
    if format_ == "csv":
        with open(tmp, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(SPALTEN)
            for r in zeilen:
                w.writerow([_sicher(x) for x in _zeile(r)])
    elif format_ == "json":
        aus = []
        for r in zeilen:
            ergebnis = dict(zip(SPALTEN, _zeile(r)))
            ergebnis["Prüfpunkte"] = [{"Punkt": b["punkt"], "Status": b["status"], "Fehlerart": b["fehlerart"], "Schweregrad": b["schwere"], "Beschreibung": b["beschreibung"],
                                      "Referenzwert": b["soll"], "Lunivo-Wert": b["ist"], "Seite": b["seite"], "Element": b["element"]} for b in db.befunde(r["ergebnis_id"])]
            aus.append(ergebnis)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"erzeugt": time.strftime("%Y-%m-%d %H:%M:%S"), "anzahl": len(aus), "ergebnisse": aus}, f, ensure_ascii=False, indent=1)
    elif format_ == "pdf":
        _pdf(tmp, zeilen)
    else:
        raise ValueError(f"Unbekanntes Exportformat: {format_}")
    os.replace(tmp, pfad)
    return len(zeilen)


def _pdf(pfad: str, zeilen: list[dict]) -> None:
    from html import escape
    from PySide6.QtCore import QMarginsF
    from PySide6.QtGui import QPageLayout, QPageSize, QPdfWriter, QTextDocument
    teile = ["<h2>Lunivo Compatibility Tester — Ergebnisse</h2>", f"<p>{len(zeilen)} Ergebnisse · {escape(time.strftime('%Y-%m-%d %H:%M'))}</p>",
             "<table border='1' cellspacing='0' cellpadding='3' width='100%'><tr>" + "".join(f"<th>{escape(h)}</th>" for h in ("Dokument", "Prüfart", "Ergebnis", "Fehlerart", "Schwere", "Beschreibung", "Referenz")) + "</tr>"]
    for r in zeilen:
        z = _zeile(r)
        teile.append("<tr>" + "".join(f"<td>{escape(str(x))}</td>" for x in (z[0], z[4], z[5], z[6], z[7], z[8], z[9])) + "</tr>")
    teile.append("</table>")
    w = QPdfWriter(pfad)
    w.setPageLayout(QPageLayout(QPageSize(QPageSize.A4), QPageLayout.Landscape, QMarginsF(12, 12, 12, 12)))
    doc = QTextDocument()
    doc.setHtml("".join(teile))
    doc.print_(w)
