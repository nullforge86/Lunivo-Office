"""Befehle: Kontext-Reiter „Tabellentools“, Gestaltung: Rahmen, Schattierung, Vorlagen, Optionen, Zellausrichtung, Maße, Gitternetz, Textrichtung.

Ein Baustein von ``KontextBefehle`` (``kern/befehle/kontextreiter/kontext.py``); nutzt ``_tab`` aus ``TabellenBefehle`` (``tabellen.py``).
Alle Befehle wirken über den ``KernEditor`` auf das Dokumentmodell (Tabellen- und Zellformate)."""
from __future__ import annotations

from vcl.qt.widgets.dialoge.dokument.eingabe_fenster import EingabeFenster
from core.formatierung.farben.farben import Farbe
from vcl.qt.fenster.befehle.hilfen import _farbfeld


class TabellenFormatBefehle:
    def tabelleRahmen(self, k=None):
        e, c, t = self._tab()
        if t:
            e.tabelle_rahmen_umschalten()

    def an_tabelleRahmen(self):
        e, c, t = self._tab()
        return bool(t) and e.tabelle_rahmen_an()

    def tabelleRahmenSchattierung(self, k=None):
        """Rechtsklick ▸ Rahmen und Schattierung: der Baustein-Dialog (ohne Reiter Seitenrand), vorbelegt aus Tabelle und Zelle."""
        e, c, t = self._tab()
        if not t:
            return
        from vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung_dialog import RahmenSchattierungDialog
        from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import ausfuehren
        d = RahmenSchattierungDialog(self.w, rahmen=e.tabelle_rahmen_lesen(), fuell=e.zell_fuellung(), mit_seitenrand=False, innen_h=False, fuer=["Tabelle"])
        if ausfuehren(d):
            self._tabelle_rahmen_schattierung_anwenden(e, d.rahmen(), d.schattierung()[0])

    def _tabelle_rahmen_schattierung_anwenden(self, e, linie, fuell) -> None:
        """Rahmen der Tabelle (Linie oder None = ohne) und Füllfarbe der markierten Zellen bzw. der Zelle der Schreibmarke."""
        with e.sitzung.gruppe("Rahmen und Schattierung"):
            e.tabelle_rahmen_linie(linie)
            e.zellformat({"hintergrund": fuell or None})

    def tabelleBeschriftung(self, k=None, oben: bool = False):
        """„Beschriftung …“ für die Tabelle der Schreibmarke: dasselbe Fenster wie Verweise ▸ Beschriftung (``BeschriftungDialog``),
        Bezeichnung „Tabelle“ vorbelegt, Lage über/unter der Tabelle wählbar (``oben`` stellt „Über“ voreingestellt ein)."""
        import json
        e, c, t = self._tab()
        if not t:
            return
        from core.verzeichnisse.abbildungsverzeichnis import beschriftung
        from vcl.qt.widgets.dialoge.verweise.beschriftung_dialog import BeschriftungDialog
        try:
            eigene = [str(x) for x in json.loads(self.w.settings.get("verweise/beschriftungen", "[]") or "[]")]
        except (ValueError, TypeError):
            eigene = []
        d = BeschriftungDialog(self.w, eigene, lambda label, zahl: beschriftung.naechste_nummer(e, label, zahl), objekt=True, label="Tabelle")
        d.pos.setCurrentIndex(1 if oben else 0)
        ok = d.exec()
        if d.eigene != eigene:
            self.w.settings.set("verweise/beschriftungen", json.dumps(d.eigene, ensure_ascii=False))
        if ok:
            r = d.ergebnis()
            beschriftung.beschriftung_einfuegen(e, r["label"], "", r["oben"], nach=r["nach"], ohne_bezeichnung=r["ohne"], zahl=r["zahl"])

    def menue_tabelleSchattierung(self):
        def setze(col):
            e, c, t = self._tab()
            if t:
                e.zellformat({"hintergrund": col.name() if col else None})
        return self._farbmenue(setze, "Keine Schattierung")

    # Tabellenformatvorlagen und Formatoptionen
    def menue_tabelleVorlagen(self):
        from core.tabellen.formatierung import tabellenstil as TS
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for n, (kopf, _s, streifen, _r) in TS.VORLAGEN.items():
            m.eintrag(n, lambda n=n: self._tabelle_vorlage(n), symbol=_farbfeld(kopf or streifen or Farbe.WEISS))
        return m

    def _tabelle_vorlage(self, name):
        """Vorlage auf die Tabelle der Schreibmarke anwenden; Kopfzeile/Streifen/Erste Spalte stehen je Tabelle."""
        e, c, t = self._tab()
        if t:
            o = e.tabelle_optionen()
            if not o["gesetzt"]:                                  # noch nie gestaltet: wie bisher Kopfzeile und Streifen an
                o.update(kopf=True, streifen=True, spalte=False)
            e.tabelle_vorlage_anwenden(name, o["kopf"], o["streifen"], o["spalte"])

    def _tabellen_option(self, key):
        """Option (kopf/streifen/spalte) der Tabelle der Schreibmarke umschalten; ist eine Vorlage gesetzt, wird sie neu angewendet."""
        e, c, t = self._tab()
        if t:
            e.tabelle_option_umschalten(key)

    def tabelleKopfzeile(self, k=None): self._tabellen_option("kopf")

    def tabelleStreifen(self, k=None): self._tabellen_option("streifen")

    def tabelleErsteSpalte(self, k=None): self._tabellen_option("spalte")

    def _an_tabellen_option(self, key):
        e, c, t = self._tab()
        return bool(t) and e.tabelle_optionen()[key]

    def an_tabelleKopfzeile(self): return self._an_tabellen_option("kopf")

    def an_tabelleStreifen(self): return self._an_tabellen_option("streifen")

    def an_tabelleErsteSpalte(self): return self._an_tabellen_option("spalte")

    def _zelle_ausrichten(self, wo):
        e, c, t = self._tab()
        if t:
            e.zell_senkrecht(wo)

    def zelleOben(self, k=None): self._zelle_ausrichten("oben")

    def zelleMitte(self, k=None): self._zelle_ausrichten("mitte")

    def zelleUnten(self, k=None): self._zelle_ausrichten("unten")

    def _zelle_waagrecht(self, wo):
        e, c, t = self._tab()
        if t:
            e.zell_waagrecht(wo)

    def zelleLinks(self, k=None): self._zelle_waagrecht("links")

    def zelleZentriert(self, k=None): self._zelle_waagrecht("mitte")

    def zelleRechts(self, k=None): self._zelle_waagrecht("rechts")

    def menue_tabelleAutoAnpassen(self):
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("An Inhalt anpassen", lambda: self._tabelle_anpassen("inhalt"))
        m.eintrag("An Fenster anpassen", lambda: self._tabelle_anpassen("fenster"))
        m.eintrag("Spalten gleichmäßig verteilen", lambda: self._tabelle_anpassen("spalten_gleich"))
        m.eintrag("Zeilen gleichmäßig verteilen", lambda: self._tabelle_anpassen("zeilen_gleich"))
        m.eintrag("Feste Spaltenbreite", lambda: self._tabelle_anpassen("fest"))
        m.eintrag("Spaltenbreite festlegen …", self.tabelleBreite)
        return m

    def _tabelle_anpassen(self, art):
        e, c, t = self._tab()
        if t:
            e.tabelle_anpassen(art)

    def tabelleBreite(self, k=None):
        """Breite der Spalte der Schreibmarke in cm festlegen (Eingabe; gesetzt über ``tabelleMasse``)."""
        e, c, t = self._tab()
        if not t:
            return
        txt, ok = EingabeFenster.getText(self.w, "Spaltenbreite", "Breite in cm:", "3,0")
        try:
            cm = float(txt.replace(",", "."))
        except ValueError:
            return
        if ok and cm > 0:
            self.tabelleMasse(breite_mm=cm * 10)

    def tabelleMasse(self, breite_mm=None, hoehe_mm=None):
        """Band-Zahlenfelder der Tabellentools: Spaltenbreite der Schreibmarke und/oder Mindesthöhe ihrer Zeile in mm setzen."""
        e, c, t = self._tab()
        if not t:
            return
        with e.sitzung.gruppe("Tabellenmaße"):
            if breite_mm is not None and breite_mm > 0:
                e.spalte_breite_setzen(float(breite_mm))
            if hoehe_mm is not None and hoehe_mm > 0:
                e.zeile_hoehe_setzen(float(hoehe_mm))

    def tabelleMasseLesen(self):
        """(Breite der Spalte, Höhe der Zeile) der Schreibmarke in mm für die Zahlenfelder des Bandes; ``None`` außerhalb einer Tabelle."""
        from core.geometrie import px_to_mm
        e, c, t = self._tab()
        if not t:
            return None
        gemessen = e.zellmasse()
        if gemessen is None:
            return None
        z, sp = t.tabelle.anker(t.zeile, t.spalte)
        breite = t.tabelle.spaltenbreiten[sp] if t.tabelle.spaltenbreiten[sp] > 0 else gemessen[0]
        return px_to_mm(breite), px_to_mm(gemessen[1])

    def an_tabelleGitternetz(self):
        e, c, t = self._tab()
        return bool(t) and e.tabelle_gitternetz_an()

    def tabelleGitternetz(self, k=None):
        """Gitternetzlinien umschalten: hellgraue gestrichelte Zellränder; wirkt nur bei Tabellen ohne Rahmen."""
        e, c, t = self._tab()
        if not t:
            return
        if e.tabelle_rahmen_an():
            self.w.lbl_msg.setText("Das Gitternetz wird nur bei Tabellen ohne Rahmen angezeigt.")
            return
        e.tabelle_gitternetz()

    def menue_tabelleTextrichtung(self):
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Waagrecht (links nach rechts)", lambda: self._tabelle_richtung("ltr"))
        m.eintrag("Rechts nach links", lambda: self._tabelle_richtung("rtl"))
        return m

    def tabelleTextrichtung(self, k=None):
        """Auswahl der Textrichtung der Zelle (waagrecht / rechts nach links)."""
        e, c, t = self._tab()
        if not t:
            return
        namen = ["Waagrecht (links nach rechts)", "Rechts nach links"]
        n, ok = EingabeFenster.getItem(self.w, "Textrichtung", "Richtung:", namen, 0, False)
        if ok:
            self._tabelle_richtung("ltr" if n == namen[0] else "rtl")

    def _tabelle_richtung(self, richtung):
        """Textrichtung der Zelle der Schreibmarke bzw. aller markierten Zellen setzen."""
        e, c, t = self._tab()
        if t:
            e.zell_richtung(richtung)
