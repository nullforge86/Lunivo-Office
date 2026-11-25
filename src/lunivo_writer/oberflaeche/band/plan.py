"""Die Reiterleiste nach der Struktur „LUNIVO WRITER“: Datei, Start, Einfügen, Seitenlayout, Verweise, Überprüfen,
Schreibhilfe, Ansicht (+ „Sendungen“ nach Register anpassen) und die Kontext-Reiter für Tabellen, Bilder/Formen, Kopf-/Fußzeile und Seriendruck („Mailings“).

Jeder Reiter hat sein Modul unter band/reiter/ bzw. kontext/; hier werden sie in der Reihenfolge der Struktur zusammengesetzt.
Die Prüfungen der Schreibhilfe stehen zusätzlich in der rechten Seitenleiste.
"""
from __future__ import annotations

from lunivo_writer.oberflaeche.kontext.diagramm_werkzeuge import DIAGRAMMTOOLS
from lunivo_writer.oberflaeche.funktionen.kopffuss.kontext_reiter import KOPFFUSS
from lunivo_writer.oberflaeche.funktionen.ansicht import reiter as ansicht_reiter
from lunivo_writer.oberflaeche.funktionen.sendungen import reiter as sendungen_reiter
from lunivo_writer.oberflaeche.funktionen.ueberpruefen import reiter as ueberpruefen_reiter
from lunivo_writer.oberflaeche.funktionen.verweise import reiter as verweise_reiter
from lunivo_writer.oberflaeche.funktionen.sendungen.kontext_reiter import SERIENDRUCK
from lunivo_writer.oberflaeche.kontext.bild_werkzeuge import BILDTOOLS, FORMTOOLS, SMARTARTTOOLS, ZEICHENTOOLS
from lunivo_writer.oberflaeche.kontext.tabellen_werkzeuge import TABELLENSTIL, TABELLENTOOLS
from lunivo_writer.oberflaeche.kontext.text_werkzeuge import TEXTTOOLS
from lunivo_writer.oberflaeche.band.reiter import ki_reiter, datei_reiter, start_reiter, einfuegen_reiter, layout_reiter, abschnitt_reiter


def plan(register: dict) -> list[dict]:
    """Die Reiter in der Reihenfolge der Struktur; Kontext-Register stehen am Ende (zunächst verborgen)."""
    start = start_reiter.bauen(next(t for t in register["register"] if t["name"] == "Start"))
    reiter = [datei_reiter.bauen(register), start, einfuegen_reiter.bauen(register), layout_reiter.bauen(register),
              verweise_reiter.bauen(register), ueberpruefen_reiter.bauen(register), ki_reiter.bauen(register), ansicht_reiter.bauen(register),
              abschnitt_reiter.bauen(register), sendungen_reiter.bauen(register)]
    return reiter + [TABELLENTOOLS, TABELLENSTIL, BILDTOOLS, FORMTOOLS, SMARTARTTOOLS, DIAGRAMMTOOLS, ZEICHENTOOLS, TEXTTOOLS, KOPFFUSS, SERIENDRUCK]
