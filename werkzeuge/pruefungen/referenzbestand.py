"""Referenzbestand für das Vergleichssystem: welche Dokumente es gibt, wie viele davon gebraucht werden und was fehlt.

    .venv/bin/python werkzeuge/pruefungen/referenzbestand.py [Quellordner] [--liste docx|odt|rtf|txt|weitere]

Sollumfang (rund 1.000 Dokumente): 450 DOCX, 250 ODT, 150 RTF, 75 TXT, 75 weitere von der Anwendung geöffnete Formate (FODT, DOTX, DOCM).
Quelle ist die vorhandene Prüfdatenbank (Vorgabe ``~/Lunivo-Testdateien``; die Dateien liegen nicht im Projekt). Die Auswahl ist festgelegt und wiederholbar: Aus jeder Teilsammlung
wird reihum genommen, innerhalb der Sammlung nach dem SHA-1 des relativen Pfads. So gleicht die Auswahl bei jedem Lauf und mischt Sammlungen statt eine auszuschöpfen.

Das Werkzeug erfindet keine Dokumente: Was die Prüfdatenbank nicht hergibt, steht im Bericht als Lücke (``Ist`` kleiner als ``Soll``) und muss mit echten Dokumenten aus Word,
LibreOffice oder ONLYOFFICE aufgefüllt werden. Das Werkzeug kennt nur die Dateiendung, nicht die Herkunft eines Dokuments; die Angabe, mit welchem Programm es entstand, gehört
in den Namen der Teilsammlung."""
from __future__ import annotations

import hashlib
import os
import sys

SOLL = {"docx": 450, "odt": 250, "rtf": 150, "txt": 75, "weitere": 75}
ENDUNGEN = {"docx": (".docx",), "odt": (".odt",), "rtf": (".rtf",), "txt": (".txt",), "weitere": (".fodt", ".dotx", ".docm")}
VORGABE = "~/Lunivo-Testdateien"
AUSGELASSEN = {"node_modules", ".git", "__pycache__", "05_Fehlerfaelle", "06_NichtUnterstuetzt"}          # Fehlerfälle und Nichtunterstütztes prüft eine eigene Reihe, nicht dieser Bestand


def kandidaten(quelle: str = VORGABE) -> dict[str, dict[str, list[str]]]:
    """Kategorie → Teilsammlung → Pfade, so wie sie die Prüfdatenbank hergibt (ohne Auswahl)."""
    wurzel = os.path.expanduser(quelle)
    aus: dict[str, dict[str, list[str]]] = {k: {} for k in SOLL}
    if not os.path.isdir(wurzel):
        return aus
    nach_endung = {e: k for k, es in ENDUNGEN.items() for e in es}
    for ordner, unter, dateien in os.walk(wurzel):
        unter[:] = sorted(d for d in unter if d not in AUSGELASSEN)
        for f in sorted(dateien):
            kategorie = nach_endung.get(os.path.splitext(f)[1].lower())
            if kategorie is None:
                continue
            rel = os.path.relpath(os.path.join(ordner, f), wurzel)
            sammlung = rel.split(os.sep)[0]
            aus[kategorie].setdefault(sammlung, []).append(os.path.join(ordner, f))
    return aus


def _schluessel(pfad: str, wurzel: str) -> str:
    return hashlib.sha1(os.path.relpath(pfad, wurzel).encode("utf-8")).hexdigest()


def auswahl(quelle: str = VORGABE) -> dict[str, list[str]]:
    """Die feste Auswahl je Kategorie, höchstens ``SOLL`` Dateien; reihum aus den Teilsammlungen."""
    wurzel = os.path.expanduser(quelle)
    gewaehlt: dict[str, list[str]] = {}
    for kategorie, sammlungen in kandidaten(quelle).items():
        reihen = [sorted(p, key=lambda x: _schluessel(x, wurzel)) for _n, p in sorted(sammlungen.items())]
        aus: list[str] = []
        i = 0
        while len(aus) < SOLL[kategorie] and any(i < len(r) for r in reihen):
            aus += [r[i] for r in reihen if i < len(r)][:SOLL[kategorie] - len(aus)]
            i += 1
        gewaehlt[kategorie] = aus
    return gewaehlt


def bericht(quelle: str = VORGABE) -> str:
    wahl, alle = auswahl(quelle), kandidaten(quelle)
    zeilen = [f"Referenzbestand aus `{quelle}`", "", "| Kategorie | Soll | Ist (ausgewählt) | Lücke | in der Prüfdatenbank | Teilsammlungen |", "|---|---|---|---|---|---|"]
    for k, soll in SOLL.items():
        ist = len(wahl[k])
        vorhanden = sum(len(p) for p in alle[k].values())
        zeilen.append(f"| {k} | {soll} | {ist} | {max(0, soll - ist)} | {vorhanden} | {', '.join(f'{n} ({len(p)})' for n, p in sorted(alle[k].items())) or '–'} |")
    luecke = sum(max(0, s - len(wahl[k])) for k, s in SOLL.items())
    zeilen += ["", f"Gesamt: {sum(len(v) for v in wahl.values())} von {sum(SOLL.values())}; Lücke {luecke}."]
    if luecke:
        zeilen.append("Die Lücke wird nicht mit selbst erzeugten Dokumenten gefüllt: Sie braucht echte Dokumente aus Word, LibreOffice oder ONLYOFFICE.")
    return "\n".join(zeilen)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    quelle = args[0] if args and args[0] not in SOLL else VORGABE
    if "--liste" in sys.argv:
        art = sys.argv[sys.argv.index("--liste") + 1]
        print("\n".join(auswahl(quelle).get(art, [])))
    else:
        print(bericht(quelle))
