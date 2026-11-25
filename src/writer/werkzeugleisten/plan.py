"""Die Reiterleiste nach der Struktur „LUNIVO WRITER“: Datei, Start, Einfügen, Seitenlayout, Verweise, Überprüfen,
Schreibhilfe, Ansicht (+ „Sendungen“ nach Register anpassen) und die Kontext-Reiter für Tabellen, Bilder/Formen, Kopf-/Fußzeile und Seriendruck („Mailings“).

Jeder Reiter hat sein Modul unter band/reiter/ bzw. kontext/; hier werden sie in der Reihenfolge der Struktur zusammengesetzt.
Die Prüfungen der Schreibhilfe stehen zusätzlich in der rechten Seitenleiste.
"""
from __future__ import annotations

from writer.kontextmenues.diagramm_werkzeuge import DIAGRAMMTOOLS
from writer.funktionen.kopffuss.band.kontext_reiter import KOPFFUSS
from writer.funktionen.ansicht.band import reiter as ansicht_reiter
from writer.funktionen.sendungen.band import reiter as sendungen_reiter
from writer.funktionen.ueberpruefen.band import reiter as ueberpruefen_reiter
from writer.funktionen.verweise.band import reiter as verweise_reiter
from writer.funktionen.sendungen.band.kontext_reiter import SERIENDRUCK
from writer.kontextmenues.bild_werkzeuge import BILDTOOLS, FORMTOOLS, SMARTARTTOOLS, ZEICHENTOOLS
from writer.kontextmenues.tabellen_werkzeuge import TABELLENSTIL, TABELLENTOOLS
from writer.kontextmenues.text_werkzeuge import TEXTTOOLS
from writer.werkzeugleisten.reiter import ki_reiter, datei_reiter, start_reiter, einfuegen_reiter, layout_reiter, abschnitt_reiter


def plan(register: dict) -> list[dict]:
    """Die Reiter in der Reihenfolge der Struktur; Kontext-Register stehen am Ende (zunächst verborgen)."""
    start = start_reiter.bauen(next(t for t in register["register"] if t["name"] == "Start"))
    reiter = [datei_reiter.bauen(register), start, einfuegen_reiter.bauen(register), layout_reiter.bauen(register),
              verweise_reiter.bauen(register), ueberpruefen_reiter.bauen(register), ki_reiter.bauen(register), ansicht_reiter.bauen(register),
              abschnitt_reiter.bauen(register), sendungen_reiter.bauen(register)]
    return reiter + [TABELLENTOOLS, TABELLENSTIL, BILDTOOLS, FORMTOOLS, SMARTARTTOOLS, DIAGRAMMTOOLS, ZEICHENTOOLS, TEXTTOOLS, KOPFFUSS, SERIENDRUCK]
