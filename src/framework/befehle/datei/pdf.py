"""PDF-Export eines Dokuments: Exportwahl anlegen und prüfen, die PDF-Datei sicher schreiben. Die Oberfläche gibt nur Kennung, Pfad und die Wahl."""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace

from framework.anbindung import Daten
from framework.sitzungen import sitzung as _steuerung


@dataclass(frozen=True)
class Pdfangabe:
    """Die Exportwahl für eine PDF als unveränderliche Angabe (Felder und Vorgaben wie die Exportwahl des PDF-Filters)."""
    pfad: str
    bereich: str                      # alles · aktuell · markierung · seiten
    von: int
    bis: int
    eigenschaften: bool               # Zusammenfassungsinformationen (Titel, Autor)
    kommentare: bool                  # Kommentare als PDF-Notizen
    hyperlinks: bool
    notenlinks: bool                  # Fußnotenzeichen springen zur Fußnote
    textmarken: bool                  # Textmarken als Lesezeichen
    ueberschriften: bool              # Überschriften als Lesezeichen
    andere: bool                      # Titel, Untertitel, Zitat als Lesezeichen
    eigene: bool                      # eigene Formatvorlagen als Lesezeichen
    verschluesseln: bool
    kennwort_rechte: str              # schützt die Berechtigungen
    kennwort_oeffnen: str             # ohne dieses Kennwort öffnet sich die Datei nicht
    aendern: bool
    kopieren: bool
    kommentieren: bool
    druck: str                        # frei · niedrig · kein
    schliessen: bool                  # Fenster nach dem Export schließen


def _filterwahl(wahl: Pdfangabe):
    from filter.pdf import PdfWahl
    return PdfWahl(**asdict(wahl))


def pdf_wahl(**felder: Daten) -> Pdfangabe:
    """Eine Exportwahl mit den angegebenen Feldern (alle übrigen mit ihren Vorgaben)."""
    from filter.pdf import PdfWahl
    return Pdfangabe(**asdict(PdfWahl(**felder)))


def pdf_wahl_mit(wahl: Pdfangabe, **felder: Daten) -> Pdfangabe:
    """Die Exportwahl mit geänderten Feldern (die Angabe selbst ist unveränderlich)."""
    return replace(wahl, **felder)


def pdf_druckrechte() -> tuple[tuple[str, str], ...]:
    """(Beschriftung, Wert) der Druckrechte einer geschützten PDF."""
    from filter.pdf import DRUCK
    return tuple((text, wert) for text, wert in DRUCK)


def pdf_kennwort_fehler(wahl: Pdfangabe, bestaetigt_rechte: str, bestaetigt_oeffnen: str) -> str:
    """Was an den Kennwörtern der Wahl nicht stimmt (leer: alles in Ordnung)."""
    from filter.pdf import kennwort_fehler
    return kennwort_fehler(_filterwahl(wahl), bestaetigt_rechte, bestaetigt_oeffnen)


def pdf_schreiben(kennung: int, pfad: str, wahl: Pdfangabe, titel: str, autor: str, aktuelle_seite: int) -> int:
    """Das Dokument ``kennung`` nach der Wahl als PDF nach ``pfad`` schreiben (sicher: erst vollständig, dann ersetzen); → Zahl der Seiten.
    Fehler beim Schreiben werden weitergereicht."""
    from filter.pdf import dokument_als_pdf, lesezeichen, nur_markierung, seiten, verschluesseln
    from framework.dokumentverwaltung.dateizugriff import schreiben
    sitzung = _steuerung._sitzungen[kennung].sitzung
    wahl = _filterwahl(wahl)
    erste, letzte = seiten(wahl, aktuelle_seite)
    dokument = sitzung.dokument
    if wahl.bereich == "markierung":
        dokument = nur_markierung(dokument, sitzung.auswahl)

    def erzeugen(tmp):
        struktur = {"lesezeichen": lesezeichen(wahl), "kommentare": wahl.kommentare, "hyperlinks": wahl.hyperlinks, "notenlinks": wahl.notenlinks}
        n = dokument_als_pdf(dokument, tmp, titel, autor=autor, erste=erste, letzte=letzte, struktur=struktur)
        verschluesseln(tmp, wahl)
        return n
    return schreiben(pfad, erzeugen, endung=".pdf")
