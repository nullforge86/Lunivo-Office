"""RTF direkt lesen — ohne Umwandlungsprogramm (Microsoft RTF 1.9).

Aufbau: ``zerleger`` (Tokens, Gruppenstapel) → ``steuerwoerter`` (Zeichen, Absatz, Seite) und ``gruppen`` (Ziele wie Schrift-/
Farbtabelle, Kopf-/Fußzeile, Felder) → ``modell`` (Absätze, Tabellen) → ``aufbau`` (QTextDocument); ``bilder`` setzt ``\\pict`` um,
``leser`` ist der Einstieg. Übernommen: Absätze, Zeichenformat, Listen, Tabellen, Bilder (PNG, JPEG, EMF), Seitengröße und -ränder,
Kopf-/Fußzeile, Titel und Autor. Was fehlt (Fußnoten, Kommentare, Zeichnungen), meldet der Bericht. 15 Twip = 1 px bei 96 dpi.
"""
from lunivo_writer.services.rtf.leser import read_rtf

__all__ = ["read_rtf"]
