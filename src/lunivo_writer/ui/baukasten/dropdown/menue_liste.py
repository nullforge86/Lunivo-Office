"""Menü-Liste: Zeilen mit Symbol, Text, Tastenkürzel, Haken und Untermenü — überall dieselbe Gestalt."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
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

    def untermenue(self, text: str, symbol: QIcon | None = None, aktiv: bool = True, *, wert: str = "", tip: str = "") -> "MenueListe":
        """Untermenü-Zeile. ``wert``: aktueller Wert, rechts in der Zeile vor dem Pfeil (wie ein Kürzel). ``tip``: Hinweis, auch bei grauer Zeile."""
        m = MenueListe(text + ("\t" + wert.replace("&", "&&") if wert else ""), self)
        if symbol is not None:
            m.setIcon(symbol)
        m.setEnabled(aktiv)
        if tip:
            m.menuAction().setToolTip(tip)
        self.addMenu(m)
        return m

    def untermenue_einhaengen(self, sub: "MenueListe", titel: str | None = None) -> "MenueListe":
        """Ein vorhandenes Menü (z. B. das Klappmenü eines anderen Knopfes) als Untermenü übernehmen; es gehört danach diesem Menü."""
        if titel is not None:
            sub.setTitle(titel)
        sub.setParent(self, Qt.WindowType.Popup)
        self.addMenu(sub)
        return sub

    def widget(self, w: QWidget) -> QWidgetAction:
        """Ein eingebautes Bedienfeld (Raster, Reiter, Zeile) als einzige Zeile des Menüs oder zwischen anderen Zeilen."""
        a = QWidgetAction(self); a.setDefaultWidget(w); self.addAction(a)
        return a

    def schalter(self, text: str, an: bool, aktion: Callable[[bool], None] | None = None, *, symbol: QIcon | None = None):
        """Zeile mit kleinem Kippschalter (z. B. „Websuche“). ``aktion(an)`` läuft beim Umschalten; zurückgegeben wird die ``SchalterZeile``
        (``an_setzen`` zieht den Zustand von außen nach)."""
        from lunivo_writer.ui.baukasten.dropdown.schalter_zeile import SchalterZeile
        z = SchalterZeile(text, an, symbol)
        if aktion is not None:
            z.umgeschaltet.connect(aktion)
        self.widget(z)
        return z

    def kompakt(self) -> "MenueListe":
        """Layoutvariante „kompakt“ (schmalere Zeilen) — für das Tabellenmenü; die übrigen Menüs behalten das Standardmaß.
        Die Maße stehen im Thema (``QMenu[variante="kompakt"]`` in ``ui/theme.py``), nicht hier."""
        self.setProperty("variante", "kompakt")
        self.style().unpolish(self); self.style().polish(self)
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
