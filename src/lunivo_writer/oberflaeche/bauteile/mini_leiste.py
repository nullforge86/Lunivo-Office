"""Minisymbolleiste: schwebende Leiste mit den häufigsten Formaten über der Auswahl oder am Rechtsklick.

Optionen ▸ Ansicht: „Minisymbolleiste bei Auswahl“ und „Minisymbolleiste bei Rechtsklick“. Die Knöpfe rufen dieselben Befehle wie das Band.
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, QSize, QTimer, Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication, QComboBox, QFrame, QHBoxLayout, QMenu, QToolButton, QVBoxLayout, QWidget

from lunivo_writer.kern.tabellenaktionen import GRUPPEN
from lunivo_writer.editor.tabelle.tabellenzustand import EINZELZELLE_GANZ, GANZE_TABELLE, MEHRERE_ZELLEN, tabellenmodus, zustand
from lunivo_writer.oberflaeche.bauteile import symbole
from lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.oberflaeche.baukasten.basis.mass import (
    ABSTAND_ENG,
    ICON_KNOPF_GROSS,
    ICON_NORMAL,
    RAND_KEIN,
    RAND_MINILEISTE,
)
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld import Auswahlfeld
from lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf import DropdownKnopf

# Zwei Zeilen wie in der Vorlage, je Modus eine eigene Anordnung. Eintrag: Name -> (Tooltip, Art) — Art: "" (Knopf) · "klappe:…" (Pfeil mit Menü des Bandes)
# · "farbe:…" (Palette). Die Namen sind Befehle des Bandes (``fenster.befehle``); "schriftart" und "groesse" sind die beiden Auswahlfelder.
KNOEPFE = {"kopieren": ("Kopieren", ""), "einfuegen": ("Einfügen", "klappe:menue_einfuegenKlappe"), "ausschneiden": ("Ausschneiden", ""),
           "schriftGroesser": ("Schrift vergrößern", ""), "schriftKleiner": ("Schrift verkleinern", ""),
           "formatUebertragen": ("Format übertragen", ""), "fett": ("Fett", ""), "kursiv": ("Kursiv", ""), "unter": ("Unterstrichen", ""),
           "hervorhebenJetzt": ("Hervorheben", "farbe:menue_hervorhebenKlappe"), "schriftfarbeJetzt": ("Schriftfarbe", "farbe:menue_schriftfarbeKlappe"),
           "tabelleRahmen": ("Rahmen", "klappe:_rahmen_menue"), "tabelleSchattierung": ("Zellenschattierung", "farbe:menue_tabelleSchattierung"),
           "ausrichtung": ("Ausrichtung", "klappe:_ausrichtung_menue"), "zeilenabstand": ("Zeilenabstand", "klappe:menue_zeilenabstandKlappe")}
TEXT_MODUS = (("kopieren", "einfuegen", "schriftart", "groesse", "schriftGroesser", "schriftKleiner"),
              ("ausschneiden", "formatUebertragen", "fett", "kursiv", "unter", "hervorhebenJetzt", "schriftfarbeJetzt", "ausrichtung", "zeilenabstand"))
# Tabellenmodus (Vorlage): kein Kopieren/Ausschneiden/Einfügen vorn; Format übertragen ganz rechts; rechts daneben „Einfügen ▾“ und „Löschen ▾“
TABELLEN_MODUS = (("schriftart", "groesse", "schriftGroesser", "schriftKleiner", "zeilenabstand"),
                  ("fett", "kursiv", "unter", "hervorhebenJetzt", "schriftfarbeJetzt", "tabelleSchattierung", "tabelleRahmen", "ausrichtung",
                   "formatUebertragen"))
ICON = 18                      # Symbolgröße der Knöpfe (nie gestaucht)
GROESSEN = [8, 9, 10, 10.5, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]


def _symbole() -> dict[str, str]:
    from lunivo_writer.oberflaeche.band.band_leiste import lade_register
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
    out.setdefault("tabelleRahmen", "rahmen"); out.setdefault("tabelleSchattierung", "toenung")
    return out


class MiniLeiste(QFrame):
    def __init__(self, fenster):
        super().__init__(fenster, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowDoesNotAcceptFocus)
        self.w = fenster
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setObjectName("miniLeiste")
        self._stil_farbe = ""
        self._stil_setzen()
        aussen = QHBoxLayout(self)
        aussen.setContentsMargins(*RAND_MINILEISTE); aussen.setSpacing(ABSTAND_ENG)
        v = QVBoxLayout(); v.setSpacing(ABSTAND_ENG)
        aussen.addLayout(v)
        self.knoepfe: dict[str, QToolButton] = {}
        self._menues: dict[str, str] = {}
        sym = _symbole()
        self._felder: dict[str, QComboBox] = {}
        self._ikonen: dict[QToolButton, tuple[str, int]] = {}          # Symbolname und -größe je Knopf (Neuzeichnen nach Themenwechsel)
        self.schriftart = Auswahlfeld(); self.schriftart.setFocusPolicy(Qt.NoFocus); self.schriftart.rolle("schrift", "mini")     # Name bleibt lesbar (wie die Textleiste)
        self.schriftart.addItems(QFontDatabase.families())
        self.schriftart.textActivated.connect(lambda n: self._schrift(n))
        self.groesse = Auswahlfeld(); self.groesse.setFocusPolicy(Qt.NoFocus); self.groesse.rolle("groesse", "mini")
        self.groesse.addItems([f"{g:g}" for g in GROESSEN])
        self.groesse.textActivated.connect(lambda t: self._groesse(t))
        self._felder = {"schriftart": self.schriftart, "groesse": self.groesse}
        self._zeilen: list[QHBoxLayout] = []
        for _i in range(2):
            h = QHBoxLayout(); h.setSpacing(0)
            self._zeilen.append(h)
            v.addLayout(h)
        for tun, (tip, art) in KNOEPFE.items():
            b = DropdownKnopf()
            b.setIconSize(QSize(ICON, ICON))
            self._ikonen[b] = (sym.get(tun, ""), ICON)
            b.setIcon(symbole.icon(sym.get(tun, ""), ICON))
            if b.icon().isNull():                                  # Fett/Kursiv/Unterstrichen sind im Band Buchstaben, keine Symbole
                b.setText({"fett": "F", "kursiv": "K", "unter": "U"}.get(tun, tip[:1]))
                f = b.font()
                f.setBold(tun == "fett"); f.setItalic(tun == "kursiv"); f.setUnderline(tun == "unter")
                b.setFont(f)
                b.groesse_rolle("knopf", "mini")
            b.setToolTip(tip)
            b.setFocusPolicy(Qt.NoFocus)
            b.setCheckable(self.w.befehle.zustand(tun) is not None)
            if art:                                                # Pfeil mit Menü; Klick auf das Symbol wirkt wie im Band
                self._menues[tun] = art
                self._menue_setzen(b, tun)
            if tun in ("ausrichtung", "zeilenabstand", "tabelleSchattierung"):
                b.clicked.connect(lambda _=False, b=b: b.showMenu())
            else:
                b.clicked.connect(lambda _=False, tun=tun: self._tun(tun))
            self.knoepfe[tun] = b
            b.hide()
        self._ed = None
        self._per_griff = False
        self.tabellenzeile = self._tabellenzeile()
        aussen.addWidget(self.tabellenzeile)                           # rechts neben den zwei Zeilen
        self.tabellenzeile.hide()
        self._anordnen(False)

    def _stil_setzen(self) -> None:
        """Bei Themenwechsel Symbole und Menüs in der neuen Schriftfarbe neu zeichnen (Aussehen der Leiste: ``oberflaeche/thema.py``)."""
        farbe = self.palette().buttonText().color().name()
        if farbe != self._stil_farbe:
            alt, self._stil_farbe = self._stil_farbe, farbe
            if alt:                                                   # Themenwechsel: Symbole in der neuen Farbe zeichnen
                for b, (name, px) in self._ikonen.items():
                    if name:
                        b.setIcon(symbole.icon(name, px))
                for text, b in ((t, self.knoepfe["tabellen_" + t]) for t in GRUPPEN):
                    self._aktionsmenue(b, GRUPPEN[text])

    def _anordnen(self, tabelle: bool) -> None:
        """Die beiden Zeilen für den Text- oder den Tabellenmodus füllen (die Knöpfe sind dieselben, nur Auswahl und Reihenfolge wechseln)."""
        plan = TABELLEN_MODUS if tabelle else TEXT_MODUS
        for h in self._zeilen:
            while h.count():
                h.takeAt(0)
        benutzt = set()
        for h, namen in zip(self._zeilen, plan):
            for n in namen:
                w = self._felder.get(n) or self.knoepfe[n]
                h.addWidget(w); w.show(); benutzt.add(n)
            h.addStretch(1)
        for n, w in (*self._felder.items(), *self.knoepfe.items()):
            if n not in benutzt and not n.startswith("tabellen_"):
                w.hide()

    def _tabellenzeile(self) -> QWidget:
        """„Einfügen ▾“ und „Löschen ▾“ als große Symbolknöpfe mit Beschriftung darunter (wie in der Vorlage); Menüs aus ``kern/tabellenaktionen.py``."""
        z = QWidget()
        h = QHBoxLayout(z); h.setContentsMargins(*RAND_KEIN); h.setSpacing(0)
        sym = {"Einfügen": "tabelleEinfuegen", "Löschen": "tabelleLoeschen"}
        for text, aktionen in GRUPPEN.items():
            b = DropdownKnopf(); b.setText(text + " ▾"); b.setToolTip(text); b.setFocusPolicy(Qt.NoFocus)
            b.setToolButtonStyle(Qt.ToolButtonTextUnderIcon); b.setIconSize(QSize(ICON_KNOPF_GROSS, ICON_KNOPF_GROSS))
            self._ikonen[b] = (sym[text], 28)
            b.setIcon(symbole.icon(sym[text], ICON_KNOPF_GROSS))
            b.groesse_rolle("tabelle", "mini")
            self._aktionsmenue(b, aktionen)
            h.addWidget(b)
            self.knoepfe["tabellen_" + text] = b
        return z

    def _aktionsmenue(self, b: QToolButton, aktionen) -> None:
        m = MenueListe(b)
        for a in aktionen:
            m.eintrag(a.name, lambda bf=a.befehl: self._tun(bf), symbol=symbole.icon(a.symbol, ICON_NORMAL) if symbole.hat(a.symbol) else None)
        b.menue_setzen(m, geteilt=False)

    def tabellenmodus(self) -> bool:
        """Tabellenmodus (siehe ``editor/tabelle/tabellenzustand.py``): mehrere Zellen oder die ganze Tabelle markiert, über den Verschiebegriff gewählt oder
        Rechtsklick ohne Textmarkierung in einer Zelle. Text in nur einer Zelle oder außerhalb einer Tabelle: Textmodus."""
        return tabellenmodus(self._ed, self._rechtsklick, self._per_griff)

    def _modus_anwenden(self) -> bool:
        """Knöpfe des Modus anordnen; ``True``, wenn sich der Modus geändert hat (Größe und Platz müssen neu gesetzt werden)."""
        modus = self.tabellenmodus()
        alt = getattr(self, "_modus", None)
        self._modus = modus
        if alt != modus:
            self._anordnen(modus)
        self.tabellenzeile.setVisible(modus)
        return alt != modus

    def _ausrichtung_menue(self) -> QMenu:
        m = MenueListe()
        for text, tun in (("Linksbündig", "links"), ("Zentriert", "mitte"), ("Rechtsbündig", "rechts"), ("Blocksatz", "block")):
            m.eintrag(text, lambda t=tun: self._tun(t), symbol=symbole.icon(tun, ICON_NORMAL) if symbole.hat(tun) else None)
        return m

    def _rahmen_menue(self) -> QMenu:
        m = MenueListe()
        for text, tun in (("Rahmenlinien ein/aus", "tabelleRahmen"), ("Rahmen und Schattierung …", "tabelleRahmenSchattierung")):
            m.eintrag(text, lambda t=tun: self._tun(t), symbol=symbole.icon("rahmen", ICON_NORMAL))
        return m

    def _menue_setzen(self, b: QToolButton, tun: str) -> None:
        """Das Menü ist dasselbe wie im Band (Einfügen, Farbpaletten mit „Zuletzt benutzt“ und Vorschau, Zeilenabstand); es entsteht nach jeder Wahl neu."""
        art, _, name = self._menues[tun].partition(":")
        quelle = self if name.startswith("_") else self.w.befehle
        m = getattr(quelle, name)()
        alt = getattr(b, "_menue_obj", None)
        b._menue_obj = m                                              # sonst räumt Python das Menü ab, bevor es sich öffnet
        b.menue_setzen(m, geteilt=True)
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
        self._stil_setzen()
        self._per_griff = bool(getattr(editor, "mini_per_griff", False))          # vom Verschiebegriff der Tabelle gemeldet (``TabellenGriffe._waehlen``)
        editor.mini_per_griff = False
        self.aktualisieren()
        self._modus_anwenden()
        self._pos, self._menue_groesse = global_pos, menue
        self._platzieren()
        self.show()
        if not hasattr(editor, "_mini_filter"):
            editor._mini_filter = _Zu(self, editor)
            editor.installEventFilter(editor._mini_filter)
            editor.cursorPositionChanged.connect(lambda: self._pruefen(editor))
            editor.selectionChanged.connect(lambda: self._pruefen(editor))

    def _platzieren(self) -> None:
        """Größe neu messen und die Leiste über (bzw. am Rechtsklick neben) ``_pos`` setzen; überlappt das Menü nie."""
        global_pos, menue, rechtsklick, unter = self._pos, self._menue_groesse, self._rechtsklick, self._rechtsklick
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
        if not (self.isVisible() and self._ed is editor):
            return
        if not editor.textCursor().hasSelection() and not self._rechtsklick:
            self.hide()
            return
        if self._per_griff and zustand(editor) not in (MEHRERE_ZELLEN, GANZE_TABELLE, EINZELZELLE_GANZ):
            self._per_griff = False                                   # die Tabellenwahl über den Griff ist aufgehoben
        if self._modus_anwenden():                                  # Zelle ↔ mehrere Zellen ↔ außerhalb: sofort umschalten
            self._platzieren()

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
