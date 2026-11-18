"""Tabellenmodelle für Dateiliste und Ergebnisliste. Auch bei vielen tausend Zeilen flüssig: Die Daten stehen als Liste im Speicher, Sortieren und Filtern macht ein Proxy."""
from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtGui import QColor

from kompatibilitaetspruefer.pruefung.klassifikation import PRUEFART_NAMEN, SCHWERE_RANG, STATUS_NAMEN

FARBEN = {"bestanden": "#2e9d4f", "teilweise": "#c58a00", "auffaellig": "#d9722b", "fehlgeschlagen": "#d83b3b", "nicht_pruefbar": "#8a8f98", "abgebrochen": "#8a8f98",
          "offen": "#8a8f98", "kritisch": "#d83b3b", "schwer": "#d9722b", "mittel": "#c58a00", "gering": "#5d8fd1", "hinweis": "#8a8f98"}
REF_NAMEN = {"zugeordnet": "zugeordnet", "unvollstaendig": "nur erwartete Werte", "vorschlag": "Vorschlag (unbestätigt)", "mehrdeutig": "mehrdeutig", "fehlt": "fehlt",
             "defekt": "Datei fehlt", "keine": "fehlt", "strukturell": "nur erwartete Werte", "visuell": "zugeordnet"}
FORMAT_ZUSTAND = {"unterstuetzt": "", "nur_referenz": " (nur Referenz)", "nicht_unterstuetzt": " (nicht unterstützt)"}


class TabellenModell(QAbstractTableModel):
    """``spalten``: (Überschrift, Schlüssel). Der Schlüssel ``status``/``schwere`` färbt die Zelle."""

    def __init__(self, spalten: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        self.spalten = spalten
        self.zeilen: list[dict] = []

    def setze(self, zeilen: list[dict]) -> None:
        self.beginResetModel()
        self.zeilen = zeilen
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.zeilen)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.spalten)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.spalten[section][0]
        return None

    def anzeige(self, zeile: dict, schluessel: str) -> str:
        wert = zeile.get(schluessel, "")
        if schluessel == "status":
            return STATUS_NAMEN.get(wert, str(wert))
        if schluessel == "art":
            return PRUEFART_NAMEN.get(wert, str(wert))
        if schluessel == "referenz":
            return REF_NAMEN.get(wert, str(wert))
        if schluessel == "format":
            return str(wert)
        return "" if wert is None else str(wert)

    def sortwert(self, zeile: dict, schluessel: str):
        wert = zeile.get(schluessel, "")
        if schluessel == "schwere":
            return SCHWERE_RANG.get(wert, 9)
        return str(wert).casefold() if isinstance(wert, str) else (wert if wert is not None else 0)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        zeile = self.zeilen[index.row()]
        schluessel = self.spalten[index.column()][1]
        if role == Qt.DisplayRole:
            return self.anzeige(zeile, schluessel)
        if role == Qt.UserRole:
            return zeile
        if role == Qt.UserRole + 1:
            return self.sortwert(zeile, schluessel)
        if role == Qt.ForegroundRole and schluessel in ("status", "schwere"):
            f = FARBEN.get(zeile.get(schluessel))
            return QColor(f) if f else None
        if role == Qt.ToolTipRole:
            return zeile.get("beschreibung") or self.anzeige(zeile, schluessel)
        return None


class FilterProxy(QSortFilterProxyModel):
    """Filter: ``filter`` (Schlüssel → Wert; leer = ohne Filter), ``suche`` (Namensteil), ``nur_ohne_referenz``."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter: dict = {}
        self.suche = ""
        self.nur_ohne_referenz = False
        self.setSortRole(Qt.UserRole + 1)
        self.setDynamicSortFilter(False)

    def setze_filter(self, **kw) -> None:
        self.filter.update(kw)
        self.invalidateFilter()

    def setze_suche(self, text: str) -> None:
        self.suche = text.strip().casefold()
        self.invalidateFilter()

    def filterAcceptsRow(self, zeile: int, parent) -> bool:
        z = self.sourceModel().zeilen[zeile]
        for k, wert in self.filter.items():
            if wert in (None, ""):
                continue
            if z.get(k) != wert:
                return False
        if self.suche and self.suche not in z.get("name", "").casefold():
            return False
        if self.nur_ohne_referenz and z.get("referenz") not in ("fehlt", "keine", "mehrdeutig", "vorschlag", "defekt"):
            return False
        return True

    def zeilen_sichtbar(self) -> list[dict]:
        return [self.data(self.index(r, 0), Qt.UserRole) for r in range(self.rowCount())]
