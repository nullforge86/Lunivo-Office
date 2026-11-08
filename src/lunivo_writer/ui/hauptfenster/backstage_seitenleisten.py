"""Steuerung der linken und rechten Backstage-Seitenleisten."""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QToolButton, QVBoxLayout

from lunivo_writer.ui.document.navigation import SEITEN, TITEL
from lunivo_writer.ui.widgets import icons
from lunivo_writer.ui.baukasten.basis.mass import (
    ABSTAND_NORMAL,
    BREITE_SCHIENE,
    BREITE_SCHIENE_BESCHRIFTET,
    GROESSE_KNOPF_SCHIENE,
    GROESSE_KNOPF_SCHIENE_TEXT,
    ICON_ASSISTENT,
    ICON_KNOPF_GROSS,
    ICON_LISTE,
    ICON_MITTEL,
    RAND_SCHIENE,
)


class BackstageSeitenleistenBaustein:
    """Baustein für die linken und rechten Backstage-Seitenleisten."""

    def _leiste_links(self):
        """Schmale Leiste links: Suchen, Kommentare, Überschriften, Änderungen, Noten, Vorlesen. Ein Klick öffnet das Feld, ein zweiter schließt es."""
        from PySide6.QtWidgets import QFrame, QToolButton, QVBoxLayout
        from lunivo_writer.ui.document.navigation import SEITEN, TITEL
        from lunivo_writer.ui.widgets import icons
        leiste = QFrame()
        leiste.setObjectName("leisteLinks")
        leiste.setFixedWidth(BREITE_SCHIENE)
        v = QVBoxLayout(leiste)
        v.setContentsMargins(*RAND_SCHIENE)
        v.setSpacing(ABSTAND_NORMAL)
        self._links = {}
        symbole = {"suche": "lupe", "kommentare": "notiz", "ueberschriften": "gliederung", "aenderungen": "verfolgt", "noten": "fussnote", "vorlesen": "vorlesen"}
        for key in SEITEN:
            b = QToolButton()
            icons.setze(b, symbole[key], ICON_MITTEL); b.setIconSize(QSize(ICON_MITTEL, ICON_MITTEL))
            b.setToolTip(TITEL[key]); b.setAccessibleName(TITEL[key])
            b.setCheckable(True)
            b.setFixedSize(*GROESSE_KNOPF_SCHIENE)
            b.clicked.connect(lambda _=False, k=key: self._links_klick(k))
            v.addWidget(b)
            self._links[key] = b
        v.addStretch(1)
        self.navigation.zustandGeaendert.connect(self._links_sync)
        self._links_sync()
        return leiste


    KURZTEXT_LINKS = {"suche": "Suchen", "kommentare": "Kommentare", "ueberschriften": "Gliederung", "aenderungen": "Änderungen", "noten": "Noten", "vorlesen": "Vorlesen"}

    def leisten_beschriften(self) -> None:
        """Option „Seitenleisten mit Text“: unter jedem Symbol der beiden Randleisten steht sein Name (breitere Leiste, kleinere Schrift)."""
        mit = self.settings.get_bool("ui/leisten_text", False)
        for leiste_name, knoepfe, kurz in (("leisteLinks", getattr(self, "_links", {}), self.KURZTEXT_LINKS),
                                           ("leisteRechts", getattr(self, "_rechts", {}), {})):
            leiste = self.findChild(QFrame, leiste_name)
            if leiste is None:
                continue
            leiste.setFixedWidth(BREITE_SCHIENE_BESCHRIFTET if mit else BREITE_SCHIENE)
            for key, b in knoepfe.items():
                if mit:
                    b.setText(kurz.get(key, key)); b.setToolTipDuration(-1)
                    f = b.font(); f.setPointSizeF(max(7.0, f.pointSizeF() * 0.85)); b.setFont(f)
                    b.setToolButtonStyle(Qt.ToolButtonTextUnderIcon); b.setFixedSize(*GROESSE_KNOPF_SCHIENE_TEXT)
                else:
                    name = kurz.get(key, key)
                    b.setText(""); b.setFont(self.font())
                    b.setAccessibleName(name)                                    # ohne Text unter dem Symbol: der Name bleibt als Tooltip und für die Bedienhilfe
                    if not b.toolTip():
                        b.setToolTip(name)
                    b.setToolButtonStyle(Qt.ToolButtonIconOnly); b.setFixedSize(*GROESSE_KNOPF_SCHIENE)

    def _links_klick(self, key: str):
        if self.navigation.isVisible() and self.navigation.aktuelle_seite == key:
            self.navigation.hide()
        else:
            self.navigation.show()
            if key == "suche":
                self.navigation.suche_zeigen()
            else:
                self.navigation.zeige_tab(key)
        self._links_sync()


    def _links_sync(self):
        sicht = self.navigation.isVisible()
        for key, b in self._links.items():
            b.setChecked(sicht and self.navigation.aktuelle_seite == key)


    def _leiste_rechts(self):
        """Schmale Leiste rechts: Die vier Reiter der Schreibhilfe (Prüfen, Lesen, Schreiben, KI) und der KI-Chat schalten die Seitenleiste um."""
        from PySide6.QtWidgets import QFrame, QToolButton, QVBoxLayout
        from lunivo_writer.ui.widgets import icons
        leiste = QFrame()
        leiste.setObjectName("leisteRechts")
        leiste.setFixedWidth(BREITE_SCHIENE)
        v = QVBoxLayout(leiste)
        v.setContentsMargins(*RAND_SCHIENE)
        v.setSpacing(ABSTAND_NORMAL)
        self._rechts = {}
        # gleiche sichtbare Symbolgröße wie links (dort füllen die Zeichnungen ~18 px von 22): Haken, KI-Plus und Chat sind kleiner gezeichnet und bekommen mehr Platz
        px_rechts = {"haken": ICON_KNOPF_GROSS, "assistent": ICON_ASSISTENT, "chat": ICON_LISTE, "brille": ICON_MITTEL, "stift": ICON_MITTEL}
        for name, sym, tip in (("Prüfen", "haken", "Prüfen — die Funde der Schreibhilfe"), ("Lesen", "brille", "Lesen — Lesehilfe, Vorlesen"),
                               ("Schreiben", "stift", "Schreiben — Schalter, Textbausteine, Sprache"), ("KI", "assistent", "KI — Korrektur, Übersetzen, Aktionen"),
                               ("Chat", "chat", "KI-Chat")):
            b = QToolButton()
            px = px_rechts.get(sym, ICON_MITTEL)
            icons.setze(b, sym, px); b.setIconSize(QSize(px, px))
            b.setToolTip(tip); b.setAccessibleName(name)
            b.setCheckable(True)
            b.setFixedSize(*GROESSE_KNOPF_SCHIENE)
            b.clicked.connect(lambda _=False, n=name: self._rechts_klick(n))
            if name == "Chat":
                v.addSpacing(8)
            v.addWidget(b)
            self._rechts[name] = b
        v.addStretch(1)
        self.sidebar.bereich_geaendert.connect(lambda _i: self._rechts_sync())
        self._rechts_sync()
        return leiste


    def _rechts_klick(self, name: str):
        """Ein Knopf der Leiste: öffnet die Seitenleiste auf dem Reiter; ein zweiter Klick auf denselben Reiter schließt sie wieder."""
        ist_chat = name == "Chat"
        schon_da = (not self.sidebar.isHidden() and ((ist_chat and self.sidebar.stapel.currentIndex() == 1)
                    or (not ist_chat and self.sidebar.stapel.currentIndex() == 0 and self.sidebar.aktueller_reiter == name)))
        if schon_da:
            self.toggle_sidebar()
        else:
            if self.sidebar.isHidden():
                self.toggle_sidebar()
            self.sidebar.zeige_bereich(1) if ist_chat else self.sidebar.zeige_reiter(name)
        self._rechts_sync()


    def _rechts_sync(self):
        sicht = not self.sidebar.isHidden()
        i = self.sidebar.stapel.currentIndex()
        for name, b in self._rechts.items():
            an = sicht and ((name == "Chat" and i == 1) or (name != "Chat" and i == 0 and self.sidebar.aktueller_reiter == name))
            b.setChecked(an)
