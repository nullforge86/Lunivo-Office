"""Diagrammarten: Katalog der Untertypen (Gruppen der linken Liste im Fenster), Kombinationen, Vorlagen, Altnamen, Beispieldaten.
Keine Oberfläche, kein Zeichnen — ``diagramm.py`` gibt die Namen unverändert weiter (``diagramm.TYPEN`` usw.)."""
from __future__ import annotations

# (Gruppe, Symbol aus symbole.json, [(Untertyp, Name)])
TYPEN = [
    ("Säule", "saeule", [("saeule_gruppiert", "Gruppierte Säule"), ("saeule_gestapelt", "Gestapelte Säule"),
                         ("saeule_100", "100 % gestapelte Säule")]),
    ("Linie", "linie", [("linie", "Linie"), ("linie_gestapelt", "Gestapelte Linie"), ("linie_100", "100 % gestapelte Linie"),
                        ("linie_punkte", "Linie mit Datenpunkten"), ("linie_punkte_gestapelt", "Gestapelte Linie mit Datenpunkten"),
                        ("linie_punkte_100", "100 % gestapelte Linie mit Datenpunkten")]),
    ("Kreis", "kreis", [("kreis", "Kreis"), ("kreis_3d", "3D-Kreis"), ("kreis_von_kreis", "Kreis von Kreis"),
                        ("kreis_balken", "Balken von Kreis"), ("ring", "Ring")]),
    ("Balken", "balkenquer", [("balken_gruppiert", "Gruppierte Balken"), ("balken_gestapelt", "Gestapelte Balken"),
                              ("balken_100", "100 % gestapelte Balken")]),
    ("Fläche", "flaeche", [("flaeche", "Fläche"), ("flaeche_gestapelt", "Gestapelte Fläche"), ("flaeche_100", "100 % gestapelte Fläche")]),
    ("X Y (Punkt)", "punktwolke", [("punkte", "Punkte"), ("punkte_glatt_punkte", "Punkt mit geglätteten Linien und Datenpunkten"),
                                   ("punkte_glatt", "Punkt mit geglätteten Linien"), ("punkte_gerade_punkte", "Punkt mit geraden Linien und Datenpunkten"),
                                   ("punkte_gerade", "Punkt mit geraden Linien"), ("punkte_blase", "Blase"), ("punkte_blase_3d", "3D-Blase")]),
    ("Kurs", "kurs", [("kurs_hts", "Höchst-Tiefst-Schluss"), ("kurs_ohts", "Eröffnung-Höchst-Tiefst-Schluss"),
                      ("kurs_vhts", "Volumen-Höchst-Tiefst-Schluss"), ("kurs_vohts", "Volumen-Eröffnung-Höchst-Tiefst-Schluss")]),
    ("Netz", "netz", [("netz", "Netz"), ("netz_punkte", "Netz mit Datenpunkten"), ("netz_gefuellt", "Gefülltes Netz")]),
    ("Kombination", "kombination", [("kombination", "Gruppierte Säulenlinie"),
                                    ("kombi_sekundaer", "Gruppierte Säule - Linie auf Sekundärachse"),
                                    ("kombi_flaeche", "Gestapelte Fläche - Gruppierte Säule"),
                                    ("kombi_eigen", "Benutzerdefinierte Kombination")]),
]
# Reihentypen der Kombination (Spalte „Diagrammtyp“ im Fenster)
KOMBI_TYPEN = [("saeule", "Gruppierte Säule"), ("saeule_gestapelt", "Gestapelte Säule"), ("linie", "Linie"),
               ("linie_punkte", "Linie mit Datenpunkten"), ("flaeche", "Fläche"), ("flaeche_gestapelt", "Gestapelte Fläche")]
# Vorlagen: fertige Farbreihen zu einer Diagrammart. Nicht mehr in ``TYPEN`` (die Gruppe „Vorlagen“ im Fenster ist eine eigene, später
# benutzerverwaltete Liste); die feste Liste bleibt für ältere Dokumente und das Menü „Diagrammstile ▸ Vorlagen“.
VORLAGEN = {
    "vorlage_klar": ("saeule_gruppiert", ["#4a8fd8", "#ef8a3c", "#9aa0a6", "#f2b705", "#2f6fb5", "#5aa454"]),
    "vorlage_blau": ("saeule_gruppiert", ["#1c4f8c", "#3a7bd5", "#7fb0ea", "#b9d4f5", "#0e2f57", "#5c93d8"]),
    "vorlage_gruen": ("linie_punkte", ["#2b7a3d", "#5aa454", "#9bcf8b", "#1d4f28", "#77b86a", "#c4e3b9"]),
    "vorlage_warm": ("balken_gruppiert", ["#c0392b", "#e67e22", "#f1c40f", "#d35400", "#e74c3c", "#f39c12"]),
    "vorlage_grau": ("flaeche", ["#3c4043", "#80868b", "#bdc1c6", "#5f6368", "#9aa0a6", "#dadce0"]),
    "vorlage_kreis": ("kreis", ["#4a8fd8", "#ef8a3c", "#5aa454", "#f2b705", "#9b59b6", "#e74c3c"]),
}
NAMEN = {u: n for _g, _s, unter in TYPEN for u, n in unter}
NAMEN["linie_glatt"] = "Geglättete Linie"          # versteckter Altname: wird gezeichnet, steht aber nicht mehr im Fenster
# Beispieldaten, mit denen das Fenster öffnet (wie in der Vorlage: vier Rubriken, drei Datenreihen)
BEISPIEL_KATEGORIEN = ["Rubrik 1", "Rubrik 2", "Rubrik 3", "Rubrik 4"]
BEISPIEL_REIHEN = {"Datenreihe 1": [4.1, 2.8, 3.3, 4.6], "Datenreihe 2": [2.6, 4.2, 1.7, 2.9], "Datenreihe 3": [1.9, 2.2, 3.1, 4.8]}
FARBEN = ["#4a8fd8", "#ef8a3c", "#9aa0a6", "#f2b705", "#2f6fb5", "#5aa454"]
# frühere Namen (gespeicherte Diagramme, ältere Aufrufe)
ALT = {"Säulen": "saeule_gruppiert", "Balken": "balken_gruppiert", "Linie": "linie", "Kreis": "kreis",
       "punkte_linien": "punkte_gerade_punkte"}       # „Punkt mit Linien“ (Punkte und gerade Linien)


def ist_kreis(u: str) -> bool:
    """Alle Kreisarten (Kreis, 3D-Kreis, Kreis/Balken von Kreis, Ring)."""
    return u.startswith("kreis") or u == "ring"


def hat_linien(u: str) -> bool:
    """Arten mit Linienreihen (Pfeile, Linienformat)."""
    return u.startswith(("linie", "punkte_gerade", "punkte_glatt"))


def beispiel(untertyp: str) -> tuple[str, list[str], dict[str, list[float]]]:
    """Beispieldaten für die Vorschau im Fenster nach Art des Untertyps (wie die Vorlage): (Titel, Rubriken, Reihen)."""
    u = ALT.get(untertyp, untertyp)
    if u.startswith("kreis") or u == "ring":
        return "Vertrieb", ["1. Quartal", "2. Quartal", "3. Quartal", "4. Quartal"], {"Vertrieb": [8.2, 3.2, 1.4, 1.2]}
    datum = ["05/01/2002", "06/01/2002", "07/01/2002", "08/01/2002"]
    if u.startswith("kurs_v"):
        r = {"Volumen": [4500.0, 6800.0, 5200.0, 7400.0]}
    elif u.startswith("kurs"):
        r = {}
    elif u.startswith(("flaeche", "netz")):
        return "Diagrammtitel", datum, dict(BEISPIEL_REIHEN)
    else:
        return "Diagrammtitel", list(BEISPIEL_KATEGORIEN), dict(BEISPIEL_REIHEN)
    r.update({"Eröffnung": [44.0, 25.0, 38.0, 50.0], "Höchst": [55.0, 57.0, 57.0, 58.0], "Tiefst": [11.0, 12.0, 13.0, 11.0],
              "Schluss": [25.0, 38.0, 50.0, 34.0]} if "o" in u.split("_")[1] else {"Höchst": [55.0, 57.0, 57.0, 58.0], "Tiefst": [11.0, 12.0, 13.0, 11.0],
                                                                                    "Schluss": [25.0, 38.0, 50.0, 34.0]})
    return "Diagrammtitel", datum, r


def kombi_vorgabe(untertyp: str, anzahl: int) -> list[tuple[str, bool]]:
    """Belegung der Kombinationstabelle für eine fertige Kombination (die letzte Reihe ist Linie bzw. Säule)."""
    if anzahl <= 0:
        return []
    if untertyp == "kombi_flaeche":
        return [("flaeche_gestapelt", False)] * max(1, anzahl - 1) + [("saeule", False)] * (anzahl > 1)
    letzte = ("linie", untertyp == "kombi_sekundaer")
    return [("saeule", False)] * max(1, anzahl - 1) + [letzte] * (anzahl > 1)


def _art(daten: dict) -> str:
    u = daten.get("art", "saeule_gruppiert")
    return ALT.get(VORLAGEN[u][0] if u in VORLAGEN else u, VORLAGEN[u][0] if u in VORLAGEN else u)
