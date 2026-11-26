"""Ausrichtung und Zeichenformat der Zeile im Feld (Kopf- oder Fußzeile auf dem Blatt): setzt im Eingabefeld um, was die Seiteneinrichtung vorgibt,
und nimmt die Änderungen der Start-Werkzeuge an (Schrift, Größe, Fett, Kursiv, Unterstrichen, Durchgestrichen, Farbe, Hervorheben, Hoch/Tief).

Welche Eigenschaft der Werkzeuge welcher Eigenschaft der Zeile entspricht, steht in ``writer`` (``blattformat``)."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor

from writer.funktionen.kopffuss import blattformat
from vcl.qt.widgets.bausteine.abstaende import KOPFFUSS_SCHRIFT_PT

AUSRICHTUNG = {"left": Qt.AlignLeft, "center": Qt.AlignHCenter, "right": Qt.AlignRight}
STELLUNG = {"sup": QTextCharFormat.AlignSuperScript, "sub": QTextCharFormat.AlignSubScript}


def basis_format(fmt: dict, zoom: float = 1.0) -> QTextCharFormat:
    """Das Zeichenformat der Zeile aus dem Format der Seiteneinrichtung; die Größe wird mit dem Zoom des Editors skaliert."""
    f = QTextCharFormat()
    if fmt.get("family"):
        f.setFontFamilies([fmt["family"]])
    if fmt.get("size_pt"):
        f.setFontPointSize(float(fmt["size_pt"]) * zoom)
    f.setFontWeight(QFont.Bold if fmt.get("bold") else QFont.Normal)
    f.setFontItalic(bool(fmt.get("italic")))
    f.setFontUnderline(bool(fmt.get("underline")))
    f.setFontStrikeOut(bool(fmt.get("strike")))
    f.setVerticalAlignment(STELLUNG.get(fmt.get("script"), QTextCharFormat.AlignNormal))
    if fmt.get("color"):
        f.setForeground(QColor(fmt["color"]))
    if fmt.get("highlight"):
        f.setBackground(QColor(fmt["highlight"]))
    return f


class ZeilenformatTeil:
    """Baustein des ``KopfFussBearbeiter``: Ausrichtung und Schrift der Zeile im Feld."""

    def _ausrichten(self, zone: str, ausrichtung: str) -> None:
        feld = self.felder[zone]
        flagge = AUSRICHTUNG.get(ausrichtung, Qt.AlignLeft)
        wahl = feld.document().defaultTextOption()
        wahl.setAlignment(flagge | Qt.AlignVCenter)
        feld.document().setDefaultTextOption(wahl)
        c = feld.textCursor()
        c.select(QTextCursor.SelectionType.Document)
        absatz = c.blockFormat()
        absatz.setAlignment(flagge)
        alt, self._laedt = self._laedt, True                    # die Ausrichtung ist kein Schritt des Textes
        c.joinPreviousEditBlock()
        c.setBlockFormat(absatz)
        c.endEditBlock()
        self._laedt = alt

    def _basis_anwenden(self, zone: str, zeile=None) -> None:
        feld = self.felder[zone]
        zeile = zeile or self.hf(None, zone)
        alt, self._laedt = self._laedt, True
        feld.basis_setzen(basis_format(zeile.fmt, self.ed.zoom))
        feld.zoom_basis = self.ed.zoom
        self._laedt = alt

    def _zeile_ausrichten(self) -> None:
        """Die wirksame Ausrichtung der aktiven Zeile aus dem Dokument ins Feld übernehmen."""
        kopf, _fuss, _nummer, kopf_ausrichtung, fuss_ausrichtung = self._blatt_zeilen()
        self._ausrichten(self.zone, kopf_ausrichtung if self._feldname() == kopf else fuss_ausrichtung)

    def ausrichtung_setzen(self, ausrichtung: str) -> None:
        feldname = self._feldname()
        vorher = self._stand()

        def setze(seite) -> None:
            setattr(seite, feldname, getattr(seite, feldname).kopie(align=ausrichtung))
        self.aendern(setze, neu_laden=False)
        self._zeile_ausrichten()
        self._merken(vorher)

    # ---- Start-Werkzeuge ---------------------------------------------------------------------------------------------------------------------
    def _format_setzen(self, fmt: dict) -> None:
        """Das Zeichenformat der aktiven Zeile ersetzen (ein Schritt für Rückgängig) und im Feld zeigen."""
        feldname = self._feldname()
        vorher = self._stand()

        def setze(seite) -> None:
            zeile = getattr(seite, feldname).kopie()
            zeile.fmt, zeile.runs = dict(fmt), []               # das Format gilt für die ganze Zeile
            setattr(seite, feldname, zeile)
        self.aendern(setze, neu_laden=False)
        self._basis_anwenden(self.zone)
        self._merken(vorher)
        QTimer.singleShot(0, self.feld.setFocus)                # die Werkzeuge geben den Fokus an den Editor zurück: wieder ins Feld

    def format_anwenden(self, aenderung: dict) -> None:
        """Eine Änderung der Start-Werkzeuge (Namen des Zeichenformats im Text) auf die aktive Zeile anwenden."""
        if self.aktiv:
            self._format_setzen(blattformat.aendern(self.hf().fmt, aenderung))

    def format_loeschen(self) -> None:
        """„Formatierung löschen“: Schrift, Größe, F/K/U, Farbe der aktiven Zeile zurück auf die Vorgabe (die Seitenzahl-Felder bleiben)."""
        if self.aktiv and self.hf().fmt:
            self._format_setzen({})

    def format_lesen(self) -> dict:
        """Das Zeichenformat der aktiven Zeile mit den Namen der Start-Werkzeuge (für deren Schalterstellung)."""
        zeichen = blattformat.als_zeichenformat(self.hf().fmt, KOPFFUSS_SCHRIFT_PT)
        zeichen.setdefault("schrift", self.ed.document().standardschrift()[0])     # ohne eigene Schrift gilt die Standardschrift des Dokuments
        return zeichen
