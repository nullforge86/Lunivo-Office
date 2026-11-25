"""Befehle: Kontext-Reiter „Tabellentools“, Aufbau: Zeilen/Spalten einfügen und löschen, Zellen verbinden/teilen, Tabelle teilen, Eigenschaften.

Ein Baustein von ``KontextBefehle`` (``kern/befehle/kontextreiter/kontext.py``) und damit von ``Befehle`` (siehe ``kern/befehlsliste.py``)."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.dokument.eingabe_fenster import EingabeFenster


class TabellenBefehle:
    # ==== Tabellentools (Kontext) ===================================================================================================
    def _tab(self):
        e = self.ed
        if not e:
            return None, None, None
        c = e.textCursor()
        t = None if e.isReadOnly() else c.currentTable()               # im Nur-Lesen-Modus gibt es keine Tabelle zum Ändern
        return (e, c, t) if t else (e, c, None)

    def tabelleZeileOben(self, k=None):
        e, c, t = self._tab()
        if t: e.tabelle_aktion("zeile_oben")

    def tabelleZeileUnten(self, k=None):
        e, c, t = self._tab()
        if t: e.tabelle_aktion("zeile_unten")

    def tabelleSpalteLinks(self, k=None):
        e, c, t = self._tab()
        if t: e.tabelle_aktion("spalte_links")

    def tabelleSpalteRechts(self, k=None):
        e, c, t = self._tab()
        if t: e.tabelle_aktion("spalte_rechts")

    def tabelleZeileLoeschen(self, k=None):
        e, c, t = self._tab()
        if t: e.tabelle_aktion("zeile_loeschen")

    def tabelleSpalteLoeschen(self, k=None):
        e, c, t = self._tab()
        if t: e.tabelle_aktion("spalte_loeschen")

    def tabelleLoeschen(self, k=None):
        e, c, t = self._tab()
        if t: e.tabelle_aktion("tabelle_loeschen")

    _ZELLEN_LOESCHEN = {"Ganze Zeile löschen": "zeile", "Ganze Spalte löschen": "spalte"}

    def tabelleZellenLoeschen(self, k=None):
        """Löschen ▸ Zellen löschen …: ganze Zeile oder Spalte der Zelle."""
        e, c, t = self._tab()
        if not t:
            return
        n, ok = EingabeFenster.getItem(self.w, "Zellen löschen", "Löschen:", list(self._ZELLEN_LOESCHEN), 0, False)
        if ok:
            e.tabelle_aktion("zeile_loeschen" if self._ZELLEN_LOESCHEN[n] == "zeile" else "spalte_loeschen")

    def tabelleVerbinden(self, k=None):
        e, c, t = self._tab()
        if t: e.zellen_verbinden()

    def tabelleTeilen(self, k=None):
        e, c, t = self._tab()
        if not t: return
        text, ok = EingabeFenster.getText(self.w, "Zellen teilen", "Spalten,Zeilen:", text="2,1")
        if not ok: return
        try:
            sp, ze = (int(x) for x in text.replace(";", ",").split(","))
            if not (1 <= sp <= 20 and 1 <= ze <= 20): raise ValueError
        except ValueError:
            self.w.lbl_msg.setText("Ungültige Eingabe: bitte „Spalten,Zeilen“ angeben, zum Beispiel 2,1.")
            return
        e.zelle_teilen(sp, ze)

    def tabelleTabelleTeilen(self, k=None):
        """Tabelle oberhalb der Zeile der Schreibmarke teilen: die Zeilen ab hier kommen in eine neue Tabelle darunter."""
        e, c, t = self._tab()
        if not t:
            return
        if not e.tabelle_teilen():
            self.w.lbl_msg.setText("Die Schreibmarke muss unterhalb der ersten Zeile stehen, damit die Tabelle geteilt werden kann.")

    def tabelleEigenschaften(self, k=None):
        e, c, t = self._tab()
        if not t:
            return
        from vcl.qt.widgets.bausteine.geruest.fenster_stapel import ausfuehren
        from vcl.qt.widgets.dialoge.dokument_dialoge import TabellenEigenschaftenDialog
        d = TabellenEigenschaftenDialog(self.w, werte={"kopf": bool(t.tabelle.format.get("kopfzeilen"))})
        if ausfuehren(d):
            e.tabellenformat({"kopfzeilen": 1 if d.kopf.isChecked() else None})

    def _tabellen_aktionsmenue(self, name: str):
        """Menü „Einfügen“ bzw. „Löschen“ aus der gemeinsamen Definition (``kern/tabellenaktionen.py``): Band, Mini-Leiste und Kontextmenü."""
        from framework.befehle_alt.tabellenaktionen import GRUPPEN
        from vcl.qt.widgets.bausteine.bauteile import symbole
        from vcl.qt.widgets.bausteine.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for a in GRUPPEN[name]:
            m.eintrag(a.name, lambda bf=a.befehl: self.tun(bf), symbol=symbole.icon(a.symbol, 16) if symbole.hat(a.symbol) else None)
        return m

    def menue_tabelleEinfuegenAktionen(self):
        return self._tabellen_aktionsmenue("Einfügen")

    def menue_tabelleLoeschenAktionen(self):
        return self._tabellen_aktionsmenue("Löschen")
