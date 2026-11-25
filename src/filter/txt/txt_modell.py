"""Qt-freie Ein- und Ausgabe einfacher Textdateien über das Dokumentmodell (``core.document.Dokument``)."""
from __future__ import annotations

from framework.dokumentverwaltung.dateizugriff.import_grenzen import pruefe_dateigroesse
from core.dokument.bericht import DocumentIOError


def textdatei_lesen(path: str) -> str:
    """UTF-8 (mit BOM), Windows-1252 oder Latin-1 wie der bisherige Textleser dekodieren."""
    pruefe_dateigroesse(path, "TXT")
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as ex:
        raise DocumentIOError(f"Datei nicht lesbar: {ex.strerror or ex}") from ex
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc).replace("\r\n", "\n")
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1").replace("\r\n", "\n")


def dokument_laden(path: str):
    """Eine Textdatei als ``Dokument`` (ein Abschnitt, ein Absatz je Zeile) laden → (Dokument, Seiteneinrichtung)."""
    from core.dokument.dokument import Absatz, Lauf, neues_dokument
    text = textdatei_lesen(path)
    dok = neues_dokument()
    dok.standardformat = {"schrift": "Liberation Sans", "groesse_pt": 11.0}
    dok.abschnitte[0].bloecke = [Absatz(dok.neue_id(), [Lauf(teil, {})] if teil else []) for teil in text.split("\n")]
    return dok, dok.abschnitte[0].seite


def dokument_als_text(dok, seite) -> tuple[bytes, list[str]]:
    """Das Dokument als UTF-8-Text (ein Absatz je Zeile) und die Hinweise, was dabei verloren geht."""
    from core.dokument.dokument import Tabelle
    hinweise: list[str] = []
    reich = bool(dok.listen or dok.objekte or len(dok.abschnitte) > 1)
    zeilen: list[str] = []
    for ab in dok.abschnitte:
        for b in ab.bloecke:
            if isinstance(b, Tabelle):
                reich = True
                for zeile in b.zellen:
                    zeilen.append("\t".join(" ".join(x.text() for x in z.bloecke if hasattr(x, "text")) for z in zeile))
                continue
            if not hasattr(b, "inhalte"):
                reich = True
                continue
            zeilen.append(b.text().replace("\u2028", "\n"))
            reich = reich or bool(b.format) or any(not hasattr(x, "text") or x.format for x in b.inhalte)
    if reich:
        hinweise.append("Als Textdatei gehen Formatierung, Listen, Tabellen und Bilder verloren.")
    if seite is not None and (not seite.header.is_empty() or not seite.footer.is_empty()):
        hinweise.append("Kopf- und Fußzeile werden in der Textdatei nicht gespeichert.")
    return "\n".join(zeilen).encode("utf-8"), hinweise
