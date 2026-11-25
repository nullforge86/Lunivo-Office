"""Live-Vorschau: Beim Überfahren einer Formatvorlage, Schrift, Größe oder Farbe zeigt das Dokument das Ergebnis schon — ohne dass etwas
übernommen wird. Technik: Die Vorschau wird wirklich angewendet (ein Rückgängig-Schritt) und beim Verlassen wieder zurückgenommen;
Wiederholen-Schritte und der „geändert“-Zustand werden danach wiederhergestellt. Abschaltbar: Optionen ▸ Ansicht ▸ Live-Vorschau."""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject

from vcl.qt.widgets.bausteine.dropdown.auswahlfeld import Auswahlfeld, Schriftauswahl


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
        s = ed.sitzung
        self._vorher = s.verlauf_laenge
        self._ed, self._modified, self._format = ed, ed.document().isModified(), s.tippformat
        try:
            anwenden(ed)
        except Exception:                                    # noqa: BLE001 — eine Vorschau darf nie etwas kaputt machen
            self._schritte = max(0, s.verlauf_laenge - self._vorher)
            self.ende()
            return
        self._schritte = max(0, s.verlauf_laenge - self._vorher)

    def ende(self) -> None:
        ed, self._ed = self._ed, None
        if ed is None:
            return
        try:
            s = ed.sitzung
            if self._schritte:
                s.verlauf_zurueck_auf(self._vorher)             # der Stand vor der Vorschau; Wiederholen-Schritte der Vorschau fallen weg
                ed.ansicht.nach_aenderung()
            else:
                s.tippformat = self._format                     # ohne Markierung ändert die Vorschau nur das Format am Zeiger
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
