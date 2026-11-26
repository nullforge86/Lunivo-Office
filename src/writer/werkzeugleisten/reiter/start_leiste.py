"""Kompakte Arbeitsleiste des Reiters „Start“: eine Zeile mit den häufigen Befehlen, alles Übrige im Menü „Mehr“.

Die Leiste erfindet keinen Befehl: jeder Knopf ist der Knopf aus den Gruppen des Reiters (Zwischenablage, Schriftart, Absatz, Bearbeiten) mit seinem
Befehl und seiner Klappe; dazu Rückgängig, Wiederholen, Drucken und Zoom mit den Befehlen, die sie überall haben. Was nicht in der Zeile steht,
bleibt über „Mehr“ erreichbar – ebenso jeder Knopf der Zeile, der bei schmalem Fenster ausgeblendet wird (``im_menue``)."""
from __future__ import annotations

from writer.werkzeugleisten.reiter.baustein import k as _k

TRENNER = {"trenner": True}
STIL, SCHRIFT, GROESSE, GALERIE = {"feld": "stil"}, {"feld": "font"}, {"feld": "groesse"}, {"stile": True}

# Die Zeile von links nach rechts; ein Name steht für den gleichnamigen Knopf des Reiters.
ZEILE = (
    "Suchen oder ersetzen", TRENNER,
    _k("zurueck", "Rückgängig", "rueckgaengig"), _k("vor", "Wiederholen", "wiederholen"), _k("drucken", "Drucken", "drucken"), TRENNER,
    _k("Prozent", "Zoom", "zoomStufe"), TRENNER,
    STIL, GALERIE, SCHRIFT, TRENNER,
    "Schrift verkleinern", GROESSE, "Schrift vergrößern", TRENNER,
    "Fett", "Kursiv", "Unterstrichen", "Schriftfarbe", "Hervorheben", TRENNER,
    "Linksbündig", "Zentriert", "Rechtsbündig", "Blocksatz", "Zeilenabstand", TRENNER,
    "Aufzählung", "Nummerierung", "Einzug verringern", "Einzug vergrößern", "Formatierung löschen",
)

# Befehle, die einen Zustand anzeigen (im Menü mit Haken)
UMSCHALTER = ("Fett", "Kursiv", "Unterstrichen", "Durchgestrichen", "Hochgestellt", "Tiefgestellt", "Zeichenschattierung",
              "Linksbündig", "Zentriert", "Rechtsbündig", "Blocksatz", "Verteilt", "Aufzählung", "Nummerierung")
AUSWAHL = " – Auswahl"                                 # Zusatz für die Klappe eines Knopfes, der auch einen eigenen Befehl hat


def im_menue(knopf: dict) -> list[dict]:
    """Derselbe Knopf als Menüzeilen: sein Befehl, seine Klappe als Untermenü oder sein eigenes Menü."""
    name = knopf["name"]
    if knopf.get("menue"):
        return [{"name": name, "menue": knopf["menue"]}]
    zeilen = []
    if knopf.get("tun"):
        zeilen.append({"name": name, "tun": knopf["tun"], **({"haken": True} if name in UMSCHALTER else {})})
    if knopf.get("klappe"):
        zeilen.append({"name": name + (AUSWAHL if knopf.get("tun") else ""), "klappe": knopf["klappe"]})
    return zeilen


def _knoepfe(gruppe: dict) -> list[dict]:
    return [e for e in gruppe.get("knoepfe", []) if e.get("name") and not e.get("zeilenumbruch")]


def arbeitsleiste(gruppen: list[dict]) -> dict:
    """``zeile``: die Einträge der Leiste (Knöpfe mit ``im_menue``, Felder, Trenner); ``mehr``: der Menüknopf mit allen übrigen Befehlen des Reiters."""
    nach_namen = {e["name"]: e for g in gruppen for e in _knoepfe(g)}
    zeile, benutzt = [], set()
    for eintrag in ZEILE:
        if isinstance(eintrag, str):
            benutzt.add(eintrag)
            eintrag = dict(nach_namen[eintrag], gross=False, text=False)
        if eintrag.get("name"):
            eintrag = dict(eintrag, im_menue=im_menue(eintrag))
        zeile.append(eintrag)
    uebrige = []
    for g in gruppen:
        rest = [zeile_ for e in _knoepfe(g) if e["name"] not in benutzt for zeile_ in im_menue(e)]
        if g.get("pfeil"):
            rest.append({"name": g["name"] + " – Einstellungen", "tun": g["pfeil"]})
        if rest:
            uebrige += ([TRENNER] if uebrige else []) + rest
    ueberlauf = [zeile_ for e in zeile for zeile_ in e.get("im_menue", [])]
    mehr = {"symbol": "mehr", "name": "Mehr", "gross": False, "text": True, "menue": ueberlauf + [TRENNER] + uebrige}
    return {"zeile": zeile, "mehr": mehr}
