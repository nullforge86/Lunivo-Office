"""Erzeugung der Menüband-Knöpfe und ihrer Menüs."""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QFont

from lunivo_writer.ui.baukasten.dropdown.bild_diagramm_menues import KLAPPEN
from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.ui.baukasten.dropdown.dropdown_knopf import DropdownKnopf
from lunivo_writer.ui.widgets import icons
from lunivo_writer.ui.baukasten.mass import GROESSE_BANDKNOPF_ICON_KLEIN, ICON_GROSS

from lunivo_writer.ui.ribbon.ribbon_bausteine import _kurz, _mit_kuerzel, _zweizeilig

NICHT_DA = "{} — in der nativen Fassung noch nicht umgesetzt"


class BandKnopfBaustein:
    """Baut einzelne Menüband-Knöpfe, Klappen und Menüeinträge."""

    def _knopf(self, e: dict, gross: bool) -> QToolButton:
        name = e["name"]
        sym = e.get("symbol", "")
        k = DropdownKnopf()
        k.setAutoRaise(True)
        tun, klappe, menue = e.get("tun"), e.get("klappe"), e.get("menue")
        akt = QAction(k)
        akt.setText(sym if not icons.hat(sym) else _kurz(name))
        akt.setToolTip(_mit_kuerzel(name))
        if icons.hat(sym):
            gi = self.GROSS_ICON[self.kompakt]
            akt.setIcon(icons.icon(sym, gi if gross else 18))
            k.setIconSize(QSize(gi, gi) if gross else QSize(*GROESSE_BANDKNOPF_ICON_KLEIN))
        k.setDefaultAction(akt)
        k.setToolTip(_mit_kuerzel(name))
        k.setAccessibleName(name)                      # Screenreader lesen den vollen Namen, nicht den Kurztext
        self._tausch_rechtsklick(k, sym)
        if not icons.hat(sym):
            f = k.font()
            if sym == "F":
                f.setBold(True)
            if sym == "K":
                f.setItalic(True)
            if sym == "U":
                f.setUnderline(True)
            k.setFont(f)
        if gross:
            k.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            k.setText(_zweizeilig(_kurz(name)))
            akt.setText(_zweizeilig(_kurz(name)))               # der Knopf übernimmt später den Text der Aktion
            breit = max(k.fontMetrics().horizontalAdvance(z) for z in _zweizeilig(_kurz(name)).split("\n"))
            k.gross(breit, self.kompakt)
        elif icons.hat(sym) and e.get("text"):
            k.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            k.setText(_kurz(name))
        elif icons.hat(sym):
            k.setToolButtonStyle(Qt.ToolButtonIconOnly)
            k.groesse_rolle("symbol", "band")                           # Projektvorgabe: Knöpfe nicht schmaler als ~36 px
        else:
            k.groesse_rolle("menue" if (klappe or menue) else "symbol", "band")
        ok = False
        menu = None
        if menue:
            menu = MenueListe(k)
            ok = self._menue_fuellen(menu, menue)
            akt.triggered.connect(lambda _=False, kk=k: kk.showMenu())
        elif klappe and (menu := self._klappe(klappe)) is not None:
            if not tun:
                akt.triggered.connect(lambda _=False, kk=k: kk.showMenu())
            ok = True
        if menu is not None:
            k.menue_setzen(menu, geteilt=True, gross=gross, fuellend=not gross, besitzen=bool(klappe and not menue))         # Symbol und Pfeil getrennt; gestapelte Knöpfe füllen die Spalte
            if not gross:
                k.groesse_rolle("zeile", "band")                                                       # Dropdown-Knopf in einer Bandzeile: Höhe wie jedes Dropdown
        if tun:
            ok = ok or self.b.hat(tun)
            akt.triggered.connect(lambda _=False, t=tun, kk=k: (self.b.tun(t, kk), self.aktualisieren()))
        elif not menu:
            ok = False
        if tun and self.b.symbolname(tun) is not None:
            self.wechsler.append((k, tun))
            akt.setIcon(icons.icon(self.b.symbolname(tun), k.iconSize().width()))
        if e.get("haken") or (tun and self.b.zustand(tun) is not None):
            akt.setCheckable(True)
            self.schalter.append((k, tun))
        for n in (tun, klappe):
            if n and not self.b.hat(n) and not (n == klappe and (n in KLAPPEN or self.b.klappe(n) is not None)):
                self.fehlend.append(n)
        if not ok:
            k.setProperty("fehlt", True)
            k.setEnabled(False)
            k.setToolTip(NICHT_DA.format(name))
        self.knoepfe.append((k, tun, True))
        return k

    def _klappe(self, name: str):
        """Das Menü einer Klappe: erst die Bausteine der Oberfläche (``KLAPPEN``), sonst ``menue_<name>`` des Befehlsbausteins."""
        bau = KLAPPEN.get(name)
        return bau(self.b) if bau else self.b.klappe(name)

    def _menue_fuellen(self, menu: MenueListe, items: list) -> bool:
        ok = False
        for it in items:
            if it.get("trenner"):
                menu.trenner()
            elif it.get("menue"):
                sub = menu.untermenue(it["name"])
                ok |= self._menue_fuellen(sub, it["menue"])
            elif it.get("klappe"):                           # das vorhandene Klappmenü eines anderen Knopfes als Untermenü (mehrere Knöpfe hinter einem)
                sub = self._klappe(it["klappe"])
                if sub is not None:
                    menu.untermenue_einhaengen(sub, it["name"])
                    ok = True
                else:
                    self.fehlend.append(it["klappe"])
            elif it.get("name"):
                t = it.get("tun")
                if t and self.b.hat(t):
                    if it.get("haken"):
                        a = menu.eintrag(it["name"], lambda t=t, it=it: self.b.haken_wert(it) or self.b.tun(t), haken=False)
                        menu.aboutToShow.connect(lambda a=a, it=it: a.setChecked(bool(self.b.haken_wert(it))))
                    else:
                        menu.eintrag(it["name"], lambda t=t: self.b.tun(t))
                    ok = True
                else:
                    menu.eintrag(it["name"], aktiv=False, tip=NICHT_DA.format(it["name"]))
                    if t:
                        self.fehlend.append(t)
        return ok


