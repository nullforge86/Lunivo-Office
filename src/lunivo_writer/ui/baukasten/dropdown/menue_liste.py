"""Menü-Liste: Zeilen mit Symbol, Text, Tastenkürzel, Haken und Untermenü — überall dieselbe Gestalt."""
from __future__ import annotations

from typing import Callable

from PySide6.QtGui import QAction, QActionGroup, QIcon, QKeySequence
from PySide6.QtWidgets import QMenu, QWidget, QWidgetAction

from lunivo_writer.ui.baukasten.dropdown.popup_lage import PopupVerhalten


class MenueListe(PopupVerhalten, QMenu):
    """Ein Menü, das Zeilen einheitlich aufbaut. Nicht Mögliches bleibt grau sichtbar statt zu fehlen."""

    def eintrag(self, text: str, aktion: Callable | None = None, *, symbol: QIcon | None = None, kuerzel: str = "",
                haken: bool | None = None, aktiv: bool = True, tip: str = "", daten=None, echt: bool = False,
                gruppe: QActionGroup | None = None) -> QAction:
        """``kuerzel`` (Text oder ``QKeySequence``) wird nur angezeigt; mit ``echt=True`` ist es ein wirkliches Tastenkürzel
        (``setShortcut``, im Kontextmenü sichtbar). ``gruppe``: die Zeile gehört zu dieser (z. B. exklusiven) ``QActionGroup``."""
        if echt and kuerzel:
            a = QAction(text, self)
            a.setShortcut(kuerzel if isinstance(kuerzel, QKeySequence) else QKeySequence(kuerzel))
            a.setShortcutVisibleInContextMenu(True)
        else:
            a = QAction(text + ("\t" + (kuerzel.toString(QKeySequence.NativeText) if isinstance(kuerzel, QKeySequence) else kuerzel) if kuerzel else ""), self)
        if symbol is not None:
            a.setIcon(symbol)
        if haken is not None:
            a.setCheckable(True); a.setChecked(haken)
        a.setEnabled(aktiv)
        if tip:
            a.setToolTip(tip)
        if daten is not None:
            a.setData(daten)
        if aktion is not None:
            a.triggered.connect(lambda _c=False, f=aktion: f())
        if gruppe is not None:
            gruppe.addAction(a)
        self.addAction(a)
        return a

    def vorhanden(self, a: QAction) -> QAction:
        """Eine schon bestehende Aktion (z. B. aus der Hauptfenster-Aktionstabelle) als Zeile übernehmen."""
        self.addAction(a)
        return a

    def einhaengen(self, text: str, menue: QMenu, symbol: QIcon | None = None) -> QAction:
        """Ein fertiges Menü (z. B. ein Raster) als Untermenü-Zeile mit ``text`` einhängen."""
        a = self.addAction(text); a.setMenu(menue)
        if symbol is not None:
            a.setIcon(symbol)
        return a

    def untermenue(self, text: str, symbol: QIcon | None = None, aktiv: bool = True) -> "MenueListe":
        m = MenueListe(text, self)
        if symbol is not None:
            m.setIcon(symbol)
        m.setEnabled(aktiv)
        self.addMenu(m)
        return m

    def widget(self, w: QWidget) -> QWidgetAction:
        """Ein eingebautes Bedienfeld (Raster, Reiter, Zeile) als einzige Zeile des Menüs oder zwischen anderen Zeilen."""
        a = QWidgetAction(self); a.setDefaultWidget(w); self.addAction(a)
        return a

    def kompakt(self) -> "MenueListe":
        """Schmalere Zeilen (Symbolspalte, Text, Kürzel dicht) — für das Tabellenmenü; die übrigen Menüs behalten das Standardmaß."""
        from lunivo_writer.ui.baukasten.mass import PADDING_LINKS_MENUESYMBOL, PADDING_MENUE, PADDING_MENUEEINTRAG
        self.setStyleSheet("QMenu { padding: " f"{PADDING_MENUE}" "; } QMenu::item { padding: " f"{PADDING_MENUEEINTRAG}" "; } "
                           "QMenu::icon { padding-left: " f"{PADDING_LINKS_MENUESYMBOL}" "; }")
        return self

    _STANDARD_DE = {"&Undo": "Rückgängig", "&Redo": "Wiederholen", "Cu&t": "Ausschneiden", "&Copy": "Kopieren", "&Paste": "Einfügen",
                    "Delete": "Löschen", "Select All": "Alles auswählen", "Copy &Link Location": "Link kopieren"}

    @classmethod
    def standard(cls, widget, parent=None) -> "MenueListe":
        """Das Standard-Kontextmenü eines Qt-Textfeldes (``createStandardContextMenu``) als Menüliste, mit deutschen Texten."""
        q = widget.createStandardContextMenu()
        m = cls(parent or widget)
        m._quelle = q                                   # hält die übernommenen Aktionen am Leben
        for a in q.actions():
            if a.isSeparator():
                m.trenner(); continue
            neu = m.eintrag(cls._STANDARD_DE.get(a.text().split("\t")[0], a.text().split("\t")[0].replace("&", "")),
                            symbol=a.icon() if not a.icon().isNull() else None, aktiv=a.isEnabled())
            neu.triggered.connect(lambda _c=False, a=a: a.trigger())
            sk = a.shortcut()
            if not sk.isEmpty():
                neu.setText(neu.text() + "\t" + sk.toString(QKeySequence.NativeText))
        return m

    @classmethod
    def in_leiste(cls, leiste, titel: str) -> "MenueListe":
        """Ein Menü der Menüleiste (``QMenuBar``) mit dem Titel ``titel``."""
        m = cls(titel, leiste)
        leiste.addMenu(m)
        return m

    def trenner(self):
        return self.addSeparator()

    @classmethod
    def aus_liste(cls, zeilen, parent=None) -> "MenueListe":
        """Baut ein Menü aus einer Beschreibung: ``"-"`` = Trennlinie, sonst ein Wörterbuch mit text, aktion, symbol,
        kuerzel, haken, aktiv, tip und optional ``untermenue`` (wieder eine Liste)."""
        m = cls(parent)
        m._fuellen(zeilen)
        return m

    def _fuellen(self, zeilen) -> None:
        for z in zeilen:
            if z == "-":
                self.trenner(); continue
            z = dict(z)
            if "untermenue" in z:
                self.untermenue(z["text"], z.get("symbol"), z.get("aktiv", True))._fuellen(z["untermenue"])
            else:
                self.eintrag(z["text"], z.get("aktion"), symbol=z.get("symbol"), kuerzel=z.get("kuerzel", ""),
                             haken=z.get("haken"), aktiv=z.get("aktiv", True), tip=z.get("tip", ""), daten=z.get("daten"))
