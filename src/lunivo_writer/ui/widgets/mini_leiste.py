"""Minisymbolleiste: schwebende Leiste mit den häufigsten Formaten über der Auswahl oder am Rechtsklick.

Optionen ▸ Ansicht: „Minisymbolleiste bei Auswahl“ und „Minisymbolleiste bei Rechtsklick“. Die Knöpfe rufen dieselben Befehle wie das Band.
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, QSize, QTimer, Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication, QComboBox, QFrame, QHBoxLayout, QMenu, QToolButton, QVBoxLayout, QWidget

from lunivo_writer.ui.widgets import icons

# Zwei Zeilen wie in der Vorlage. Eintrag: (Befehl, Tooltip, Art) — Art: "" (Knopf) · "klappe" (Pfeil mit Menü des Bandes) · "farbe" (Palette)
ZEILE1 = [("kopieren", "Kopieren", ""), ("einfuegen", "Einfügen", "klappe:menue_einfuegenKlappe"), "schriftart", "groesse",
          ("schriftGroesser", "Schrift vergrößern", ""), ("schriftKleiner", "Schrift verkleinern", "")]
ZEILE2 = [("ausschneiden", "Ausschneiden", ""), ("formatUebertragen", "Format übertragen", ""),
          ("fett", "Fett", ""), ("kursiv", "Kursiv", ""), ("unter", "Unterstrichen", ""),
          ("hervorhebenJetzt", "Hervorheben", "farbe:menue_hervorhebenKlappe"), ("schriftfarbeJetzt", "Schriftfarbe", "farbe:menue_schriftfarbeKlappe"),
          ("ausrichtung", "Ausrichtung", "klappe:_ausrichtung_menue"), ("zeilenabstand", "Zeilenabstand", "klappe:menue_zeilenabstandKlappe")]
# Dritte Zeile, nur wenn die Schreibmarke in einer Tabelle steht: Menüs „Einfügen“ und „Löschen“ (Name, Befehl des Bandes) und „Eigenschaften …“
TABELLE_MENUES = (("Einfügen", (("Zeile oberhalb", "tabelleZeileOben"), ("Zeile unterhalb", "tabelleZeileUnten"),
                                ("Spalte links", "tabelleSpalteLinks"), ("Spalte rechts", "tabelleSpalteRechts"))),
                  ("Löschen", (("Zeile", "tabelleZeileLoeschen"), ("Spalte", "tabelleSpalteLoeschen"), ("Tabelle", "tabelleLoeschen"))))
GROESSEN = [8, 9, 10, 10.5, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]


def _symbole() -> dict[str, str]:
    from lunivo_writer.ui.ribbon.ribbon_bar import lade_register
    out = {}

    def lauf(o):
        if isinstance(o, dict):
            if isinstance(o.get("tun"), str) and o.get("symbol"):
                out.setdefault(o["tun"], o["symbol"])
            if isinstance(o.get("klappe"), str) and o.get("symbol"):
                out.setdefault(o["klappe"].replace("Klappe", ""), o["symbol"])
            for v in o.values():
                lauf(v)
        elif isinstance(o, list):
            for x in o:
                lauf(x)
    lauf(lade_register())
    out.setdefault("einfuegen", "kleben"); out.setdefault("kopieren", "kopie"); out.setdefault("ausschneiden", "schere")
    out.setdefault("formatUebertragen", "pinsel"); out.setdefault("ausrichtung", "links")
    return out


class MiniLeiste(QFrame):
    def __init__(self, fenster):
        super().__init__(fenster, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowDoesNotAcceptFocus)
        self.w = fenster
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setObjectName("miniLeiste")
        self.setStyleSheet("#miniLeiste { background: palette(window); border: 1px solid palette(mid); border-radius: 6px; }"
                           "QToolButton { border: none; border-radius: 4px; padding: 3px; }"
                           "QToolButton:hover { background: palette(midlight); }"
                           "QToolButton:checked { background: palette(highlight); }")
        v = QVBoxLayout(self)
        v.setContentsMargins(5, 4, 5, 4); v.setSpacing(2)
        self.knoepfe: dict[str, QToolButton] = {}
        self._menues: dict[str, str] = {}
        sym = _symbole()
        for zeile in (ZEILE1, ZEILE2):
            h = QHBoxLayout(); h.setSpacing(1)
            for k in zeile:
                if k == "schriftart":
                    self.schriftart = QComboBox(); self.schriftart.setFocusPolicy(Qt.NoFocus); self.schriftart.setFixedWidth(128)
                    self.schriftart.addItems(QFontDatabase.families()); self.schriftart.setMaxVisibleItems(18)
                    self.schriftart.textActivated.connect(lambda n: self._schrift(n))
                    h.addWidget(self.schriftart); continue
                if k == "groesse":
                    self.groesse = QComboBox(); self.groesse.setFocusPolicy(Qt.NoFocus); self.groesse.setFixedWidth(58)
                    self.groesse.addItems([f"{g:g}" for g in GROESSEN]); self.groesse.setMaxVisibleItems(16)
                    self.groesse.textActivated.connect(lambda t: self._groesse(t))
                    h.addWidget(self.groesse); continue
                tun, tip, art = k
                b = QToolButton()
                b.setIcon(icons.icon(sym.get(tun, ""), 18))
                if b.icon().isNull():                                  # Fett/Kursiv/Unterstrichen sind im Band Buchstaben, keine Symbole
                    b.setText({"fett": "F", "kursiv": "K", "unter": "U"}.get(tun, tip[:1]))
                    f = b.font()
                    f.setBold(tun == "fett"); f.setItalic(tun == "kursiv"); f.setUnderline(tun == "unter")
                    b.setFont(f)
                    b.setMinimumWidth(26)
                b.setToolTip(tip)
                b.setFocusPolicy(Qt.NoFocus)
                b.setCheckable(self.w.befehle.zustand(tun) is not None)
                if art:                                                # Pfeil mit Menü; Klick auf das Symbol wirkt wie im Band
                    b.setPopupMode(QToolButton.MenuButtonPopup)
                    self._menues[tun] = art
                    self._menue_setzen(b, tun)
                if tun in ("ausrichtung", "zeilenabstand"):
                    b.clicked.connect(lambda _=False, b=b: b.showMenu())
                else:
                    b.clicked.connect(lambda _=False, tun=tun: self._tun(tun))
                h.addWidget(b)
                self.knoepfe[tun] = b
            h.addStretch(1)
            v.addLayout(h)
        self._ed = None
        self.tabellenzeile = self._tabellenzeile()
        v.addWidget(self.tabellenzeile)
        self.tabellenzeile.hide()

    def _tabellenzeile(self) -> QWidget:
        """„Einfügen ▾“, „Löschen ▾“ und „Eigenschaften …“ für die Tabelle der Schreibmarke; dieselben Befehle wie im Band."""
        z = QWidget()
        h = QHBoxLayout(z); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(1)
        for text, eintraege in TABELLE_MENUES:
            b = QToolButton(); b.setText(text); b.setToolTip(text); b.setFocusPolicy(Qt.NoFocus)
            b.setPopupMode(QToolButton.InstantPopup); b.setMinimumWidth(78)
            m = QMenu(b)
            for name, befehl in eintraege:
                m.addAction(name, lambda _=False, bf=befehl: self._tun(bf))
            b.setMenu(m); h.addWidget(b)
            self.knoepfe["tabellen_" + text] = b
        e = QToolButton(); e.setText("Eigenschaften …"); e.setToolTip("Tabelleneigenschaften"); e.setFocusPolicy(Qt.NoFocus)
        e.clicked.connect(lambda: self._tun("tabelleEigenschaften")); h.addWidget(e)
        h.addStretch(1)
        return z

    def _in_tabelle(self) -> bool:
        return self._ed is not None and self._ed.textCursor().currentTable() is not None

    def _ausrichtung_menue(self) -> QMenu:
        m = QMenu()
        for text, tun in (("Linksbündig", "links"), ("Zentriert", "mitte"), ("Rechtsbündig", "rechts"), ("Blocksatz", "block")):
            m.addAction(text, lambda _=False, t=tun: self._tun(t))
        return m

    def _menue_setzen(self, b: QToolButton, tun: str) -> None:
        """Das Menü ist dasselbe wie im Band (Einfügen, Farbpaletten mit „Zuletzt benutzt“ und Vorschau, Zeilenabstand); es entsteht nach jeder Wahl neu."""
        art, _, name = self._menues[tun].partition(":")
        quelle = self if name.startswith("_") else self.w.befehle
        m = getattr(quelle, name)()
        alt = getattr(b, "_menue_obj", None)
        b._menue_obj = m                                              # sonst räumt Python das Menü ab, bevor es sich öffnet
        b.setMenu(m)
        if alt is not None:
            alt.deleteLater()
        if hasattr(m, "gewaehlt"):
            m.gewaehlt.connect(lambda _c: self._nach_farbe(b, tun))
        m.aboutToHide.connect(lambda: QTimer.singleShot(0, lambda: self._menue_setzen(b, tun)))

    def _nach_farbe(self, b: QToolButton, tun: str) -> None:
        if self._ed is not None:
            self._ed.setFocus()

    def _schrift(self, name: str) -> None:
        if self._ed is not None:
            self._ed.set_font_family(name); self._ed.setFocus()

    def _groesse(self, text: str) -> None:
        try:
            if self._ed is not None:
                self._ed.set_font_size(float(text.replace(",", "."))); self._ed.setFocus()
        except ValueError:
            pass

    def _tun(self, tun: str) -> None:
        self.w.befehle.tun(tun)
        self.aktualisieren()
        if self._ed is not None:
            self._ed.setFocus()

    def aktualisieren(self) -> None:
        for tun, b in self.knoepfe.items():
            z = self.w.befehle.zustand(tun) if not tun.startswith("tabellen_") else None
            if z is not None:
                b.setChecked(bool(z))
        if self._ed is not None:                                      # Schrift und Größe an der Schreibmarke / in der Auswahl
            cf = self._ed.textCursor().charFormat()
            fam = (cf.fontFamilies() or [self._ed.document().defaultFont().family()])
            fam = fam[0] if isinstance(fam, list) else fam
            pt = cf.fontPointSize() or self._ed.document().defaultFont().pointSizeF()
            self.schriftart.blockSignals(True); self.groesse.blockSignals(True)
            i = self.schriftart.findText(str(fam))
            self.schriftart.setCurrentIndex(i) if i >= 0 else self.schriftart.setEditText(str(fam)) if self.schriftart.isEditable() else None
            self.groesse.setCurrentText(f"{pt:g}")
            self.schriftart.blockSignals(False); self.groesse.blockSignals(False)

    def zeigen(self, editor, global_pos: QPoint, rechtsklick: bool = False, menue: QSize | None = None) -> None:
        """Über global_pos zeigen; am Rechtsklick richtet sich die Leiste nach dem Menü (menue = dessen Größe) und überlappt es nie.
        Verschwindet bei Tastendruck oder Auswahlende."""
        unter = rechtsklick
        self._rechtsklick = rechtsklick
        self._ed = editor
        self.aktualisieren()
        self.tabellenzeile.setVisible(self._in_tabelle())
        self.layout().invalidate(); self.adjustSize()
        w, h = self.width(), self.height()
        x = global_pos.x() - w // 2
        y = global_pos.y() + (18 if unter else -h - 8)
        scr = QApplication.screenAt(global_pos) or QApplication.primaryScreen()
        g = scr.availableGeometry() if scr is not None else None
        if rechtsklick and menue is not None and g is not None:
            x, y = self._neben_menue(global_pos, menue, g)
        elif g is not None:
            x = max(g.left(), min(x, g.right() - w))
            y = max(g.top(), min(y, g.bottom() - h))
        self.move(x, y)
        self.show()
        if not hasattr(editor, "_mini_filter"):
            editor._mini_filter = _Zu(self, editor)
            editor.installEventFilter(editor._mini_filter)
            editor.cursorPositionChanged.connect(lambda: self._pruefen(editor))
            editor.selectionChanged.connect(lambda: self._pruefen(editor))

    def _neben_menue(self, p: QPoint, menue: QSize, g: QRect) -> tuple[int, int]:
        """Platz für die Leiste um das Kontextmenü: über dem Klickpunkt, sonst unter, sonst neben dem Menü; nie überlappend."""
        w, h = self.width(), self.height()
        mw, mh = menue.width(), menue.height()
        mx = p.x() - mw if p.x() + mw > g.right() + 1 else p.x()               # Qt klappt das Menü am Rand nach links / oben auf
        nach_oben = p.y() + mh > g.bottom() + 1
        my = max(g.top(), p.y() - mh if nach_oben else p.y())
        m = QRect(mx, my, mw, mh)
        cx = max(g.left(), min(p.x() - w // 2, g.right() - w + 1))
        k = []
        if nach_oben:
            k.append((cx, p.y() + 4))                                          # Menü steht über dem Klickpunkt: Leiste darunter
        else:
            k.append((cx, p.y() - h - 8))                                      # Leiste über dem Klickpunkt, Menü darunter
        k.append((cx, m.bottom() + 5))                                         # unter dem Menü
        k.append((cx, m.top() - h - 5))                                        # über dem Menü
        k.append((m.right() + 5, max(g.top(), min(p.y(), g.bottom() - h + 1))))   # rechts neben dem Menü
        k.append((m.left() - w - 5, max(g.top(), min(p.y(), g.bottom() - h + 1))))  # links neben dem Menü
        for x, y in k:
            r = QRect(x, y, w, h)
            if g.contains(r) and not r.intersects(m):
                return x, y
        x, y = k[0]                                                            # Notlösung: am Bildschirm halten, dann vom Menü wegschieben
        x = max(g.left(), min(x, g.right() - w + 1)); y = max(g.top(), min(y, g.bottom() - h + 1))
        if QRect(x, y, w, h).intersects(m):
            x = max(g.left(), m.left() - w - 5) if m.left() - w - 5 >= g.left() else min(g.right() - w + 1, m.right() + 5)
        return x, y

    def _pruefen(self, editor) -> None:
        if self.isVisible() and self._ed is editor and not editor.textCursor().hasSelection() and not self._rechtsklick:
            self.hide()

    _rechtsklick = False


class _Zu(QObject):
    """Schließt die Leiste bei Tastendruck, Mausrad und Fokusverlust des Editors."""

    def __init__(self, leiste: MiniLeiste, editor):
        super().__init__(editor)
        self.l = leiste

    def eventFilter(self, o, e):
        if e.type() == QEvent.FocusOut and e.reason() in (Qt.PopupFocusReason, Qt.ActiveWindowFocusReason):
            return False                                           # Palette der Leiste oder das Werkzeugfenster der Leiste selbst ging auf: sie bleibt
        if e.type() in (QEvent.KeyPress, QEvent.Wheel, QEvent.FocusOut, QEvent.Hide) and self.l.isVisible():
            self.l.hide()
        return False
