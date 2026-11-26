"""Live-Vorschau: Beim Überfahren einer Formatvorlage, Schrift, Größe oder Farbe zeigt das Dokument das Ergebnis schon — ohne dass etwas
übernommen wird. Technik: Die Vorschau wird wirklich angewendet (ein Rückgängig-Schritt) und beim Verlassen wieder zurückgenommen;
Wiederholen-Schritte und der „geändert“-Zustand werden danach wiederhergestellt. Abschaltbar: Optionen ▸ Ansicht ▸ Live-Vorschau."""
from __future__ import annotations
from writer.funktionen import bearbeiten as _bearbeiten

from PySide6.QtCore import QEvent, QObject

from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.menues.dropdown.schriftauswahl import Schriftauswahl


class LiveVorschau:
    def __init__(self, fenster):
        self.w = fenster
        self._ed = None
        self._schritte = 0
        self._vorher = 0
        self._modified = False
        self._format = None

    @property
    def aktiv(self) -> bool:
        return self._ed is not None

    def zeigen(self, anwenden) -> None:
        """anwenden(editor) wendet das Format an; es wird beim nächsten `ende()` zurückgenommen."""
        if not self.w.settings.get_bool("ui/live_vorschau", True):
            return
        self.ende()
        ed = self.w.current_editor()
        if ed is None or ed.isReadOnly():
            return
        _bearbeiten.vorschau_beginnen(ed.kennung)
        self._ed, self._modified = ed, ed.document().isModified()
        try:
            anwenden(ed)
        except Exception:                                    # noqa: BLE001 — eine Vorschau darf nie etwas kaputt machen
            self._schritte = _bearbeiten.vorschau_schritte(ed.kennung)
            self.ende()
            return
        self._schritte = _bearbeiten.vorschau_schritte(ed.kennung)

    def ende(self) -> None:
        ed, self._ed = self._ed, None
        if ed is None:
            return
        try:
            _bearbeiten.vorschau_beenden(ed.kennung, self._schritte)     # mit Schritten der Stand davor, sonst nur das Format am Zeiger
            if self._schritte:
                ed.ansicht.nach_aenderung()
            ed.document().setModified(self._modified)
        except RuntimeError:                                         # Editor schon geschlossen
            pass
        self._schritte = 0


class Ueberfahren(QObject):
    """Event-Filter: Zeiger über dem Knopf → Vorschau, Zeiger weg oder Klick → Vorschau beenden."""

    def __init__(self, vorschau: LiveVorschau, anwenden):
        super().__init__()
        self.v, self.f = vorschau, anwenden

    def eventFilter(self, o, e):
        t = e.type()
        if t == QEvent.Enter:
            self.v.zeigen(self.f)
        elif t in (QEvent.Leave, QEvent.MouseButtonPress, QEvent.Hide):
            self.v.ende()
        return False


class VorschauCombo(Auswahlfeld):
    """Auswahlfeld, dessen Einträge beim Überfahren (highlighted) als Vorschau gezeigt werden."""

    def __init__(self, vorschau_fn, ende_fn, parent=None):
        super().__init__(parent)
        self._ende = ende_fn
        self.highlighted.connect(lambda i: vorschau_fn(self.itemText(i)))

    def hidePopup(self) -> None:
        self._ende()
        super().hidePopup()


class VorschauFontCombo(Schriftauswahl):
    def __init__(self, vorschau_fn, ende_fn, parent=None):
        super().__init__(parent)
        self._ende = ende_fn
        self.highlighted.connect(lambda i: vorschau_fn(self.itemText(i)))

    def hidePopup(self) -> None:
        self._ende()
        super().hidePopup()
