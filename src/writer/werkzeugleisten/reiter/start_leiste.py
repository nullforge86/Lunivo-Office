"""Kompakte Arbeitsleiste des Reiters „Start“: eine Zeile mit den häufigen Befehlen und zwei benannten Klappen „Zeichen“ und „Absatz“.

Die Leiste erfindet keinen Befehl: jeder Knopf ist der Knopf aus den Gruppen des Reiters (Zwischenablage, Schriftart, Absatz, Bearbeiten) mit seinem Befehl und
seiner Klappe. Die selteneren Befehle der Gruppen
„Schriftart“ und „Absatz“ stehen in der Klappe ihrer Gruppe, direkt hinter deren Knöpfen. Jeder Befehl steht nur einmal: ein Knopf, dessen Klappe
seinen Befehl schon enthält, ist im Menü eine einzige Zeile. „Mehr“ gibt es nur noch als Überlauf: es zeigt die Knöpfe der Zeile, die bei
schmalem Fenster ausgeblendet sind (``im_menue``)."""
from __future__ import annotations

from writer.werkzeugleisten.reiter.baustein import k as _k

TRENNER = {"trenner": True}
SCHRIFT, GROESSE = {"feld": "font"}, {"feld": "groesse"}
# Die Galerie aller Formatvorlagen: ein Knopf mit eigenem Symbol wie jeder andere der Zeile. Sie ist der einzige Zugang zu den Formatvorlagen;
# ein Auswahlfeld mit derselben Liste steht nicht daneben.
GALERIE = _k("stile", "Stile", "stileGalerie")
FORMAT, ZEICHEN, ABSATZ = {"sammel": "Format"}, {"sammel": "Zeichen"}, {"sammel": "Absatz"}        # mehrere Befehle hinter einem Knopf (``SAMMEL``)

# Die Zeile von links nach rechts; ein Name steht für den gleichnamigen Knopf des Reiters. Rückgängig, Wiederholen, Drucken, Zoom und Suchen
# stehen nicht hier: es gibt sie schon im Kopf des Fensters (Rückgängig, Wiederholen, Drucken), in der Statusleiste (Zoom) und in der linken
# Seitenleiste (Suchen, Ersetzen, Gehe zu).
ZEILE = (
    "Einfügen", FORMAT, "Auswählen", TRENNER,
    GALERIE, SCHRIFT, TRENNER,
    "Schrift verkleinern", GROESSE, "Schrift vergrößern", TRENNER,
    "Fett", "Kursiv", "Unterstrichen", "Schriftfarbe", "Hervorheben", ZEICHEN, TRENNER,
    "Linksbündig", "Zentriert", "Rechtsbündig", "Blocksatz", "Zeilenabstand", ABSATZ, TRENNER,
    "Aufzählung", "Nummerierung", "Einzug verringern", "Einzug vergrößern",
)

# Sammelknöpfe: Name → (Symbol, Befehle in der Reihenfolge des Menüs, Gruppe mit dem Fenster am Ende des Menüs, Zeile für dieses Fenster).
# Wie alle Knöpfe der Zeile zeigen sie nur ihr Symbol; der Name steht im Tooltip.
SAMMEL = {
    "Format": ("pinsel", ("Format übertragen", "Formatierung löschen"), None, ""),
    "Zeichen": ("schreibweise", ("Groß-/Kleinschreibung", "Durchgestrichen", "Hochgestellt", "Tiefgestellt", TRENNER,
                                       "Texteffekte", "Zeichenschattierung", "Zeichen-Layout"), "Schriftart", "Schriftart …"),
    "Absatz": ("steuerzeichen", ("Tabulatoren", "Verteilt", "Sortieren", "Textrichtung", TRENNER,
                                       "Absatzschattierung", "Absatzrahmen"), "Absatz", "Absatz …"),
}

# Befehle des Reiters, die an anderer Stelle stehen und deshalb weder in der Zeile noch in einer Klappe vorkommen:
# „Ausschneiden“ und „Kopieren“ (Rechtsklick und Tastatur), „Suchen oder ersetzen“ (linke Seitenleiste), „Wort-Extras“ (Reiter „Überprüfen“),
# „Einstellungen“ (die Fenster stehen am Ende der Klappen „Zeichen“ und „Absatz“ und in der Auswahl der Formatvorlagen).
VERLEGT = ("Ausschneiden", "Kopieren", "Suchen oder ersetzen", "Wort-Extras", "Einstellungen")

# Befehle, die einen Zustand anzeigen (im Menü mit Haken)
UMSCHALTER = ("Fett", "Kursiv", "Unterstrichen", "Hochgestellt", "Tiefgestellt", "Zeichenschattierung",
              "Linksbündig", "Zentriert", "Rechtsbündig", "Blocksatz", "Verteilt", "Aufzählung", "Nummerierung")
# Knöpfe, deren Klappe den eigenen Befehl schon enthält: im Menü eine Zeile statt zwei
NUR_KLAPPE = ("Einfügen", "Groß-/Kleinschreibung", "Durchgestrichen", "Texteffekte", "Schriftfarbe", "Hervorheben")
AUSWAHL = " – Art"                                     # Zusatz für die Klappe eines Knopfes, dessen Befehl ein Umschalter mit eigener Zeile bleibt


def im_menue(knopf: dict) -> list[dict]:
    """Derselbe Knopf als Menüzeilen: sein Befehl, seine Klappe als Untermenü oder sein eigenes Menü."""
    name, tun, klappe = knopf["name"], knopf.get("tun"), knopf.get("klappe")
    if knopf.get("menue"):
        return [{"name": name, "menue": knopf["menue"]}]
    if klappe and (not tun or name in NUR_KLAPPE):
        return [{"name": name, "klappe": klappe}]
    zeilen = []
    if tun:
        zeilen.append({"name": name, "tun": tun, **({"haken": True} if name in UMSCHALTER else {})})
    if klappe:
        zeilen.append({"name": name + AUSWAHL, "klappe": klappe})
    return zeilen


def _knoepfe(gruppe: dict) -> list[dict]:
    return [e for e in gruppe.get("knoepfe", []) if e.get("name") and not e.get("zeilenumbruch")]


def _sammelknopf(name: str, nach_namen: dict, nach_gruppe: dict, benutzt: set) -> dict:
    """Mehrere Befehle des Reiters hinter einem Knopf der Zeile; bei „Zeichen“ und „Absatz“ am Ende das Fenster der Gruppe."""
    symbol, befehle, gruppenname, fenster = SAMMEL[name]
    gruppe = nach_gruppe.get(gruppenname, {})
    menue = []
    for eintrag in befehle:
        if isinstance(eintrag, str):
            benutzt.add(eintrag)
            menue += im_menue(nach_namen[eintrag])
        else:
            menue.append(eintrag)
    if gruppe.get("pfeil"):
        menue += [TRENNER, {"name": fenster, "tun": gruppe["pfeil"]}]
    return _k(symbol, name, menue=menue)


def arbeitsleiste(gruppen: list[dict]) -> dict:
    """``zeile``: die Einträge der Leiste (Knöpfe mit ``im_menue``, Felder, Trenner); ``mehr``: der Überlaufknopf für ausgeblendete Knöpfe;
    ``mehr_immer``: ob „Mehr“ auch bei voller Breite Befehle enthält (nur wenn ein Knopf des Reiters sonst nirgends stünde)."""
    nach_namen = {e["name"]: e for g in gruppen for e in _knoepfe(g)}
    nach_gruppe = {g["name"]: g for g in gruppen}
    zeile, benutzt = [], set(VERLEGT)
    for eintrag in ZEILE:
        if isinstance(eintrag, str):
            benutzt.add(eintrag)
            eintrag = dict(nach_namen[eintrag], gross=False, text=False)
        elif eintrag.get("sammel"):
            eintrag = _sammelknopf(eintrag["sammel"], nach_namen, nach_gruppe, benutzt)
        if eintrag.get("name"):
            eintrag = dict(eintrag, im_menue=im_menue(eintrag))
        zeile.append(eintrag)
    uebrige = [zeile_ for g in gruppen for e in _knoepfe(g) if e["name"] not in benutzt for zeile_ in im_menue(e)]     # damit keine Funktion verloren geht
    ueberlauf = [zeile_ for e in zeile for zeile_ in e.get("im_menue", [])]
    mehr = {"symbol": "mehr", "name": "Mehr", "gross": False, "text": True, "menue": ueberlauf + ([TRENNER] + uebrige if uebrige else [])}
    return {"zeile": zeile, "mehr": mehr, "mehr_immer": bool(uebrige)}
