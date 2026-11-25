"""Befehle des Bandes: Aktionsname aus register.json → Funktion.

Ein Name, den es hier nicht gibt, bleibt im Band sichtbar, aber ausgegraut — mit dem Hinweis,
dass er in der nativen Fassung noch fehlt. So entsteht die Liste dessen, was noch zu tun ist,
von selbst (siehe `fehlende()`), und nichts steht als Attrappe da.

Konvention: Methode `name(self, knopf=None)`; `w.xyz` heißt `w_xyz`.
Zustand eines Schalters: Methode `an_name(self) -> bool`.
Klappe (Pfeilmenü): Methode `menue_name(self) -> QMenu`.
"""
from __future__ import annotations

import json
from PySide6.QtGui import QCursor
from vcl.qt.widgets.ribbon.ansicht.band.band_befehle import AnsichtBandBefehle
from vcl.qt.widgets.ribbon.bearbeiten.band.band_befehle import BearbeitenBandBefehle
from vcl.qt.fenster.befehle.hauptreiter.datei import DateiBefehle
from vcl.qt.fenster.befehle.hauptreiter.einfuegen import EinfuegenBefehle
from vcl.qt.fenster.befehle.hauptreiter.ki import KIBefehle
from vcl.qt.widgets.ribbon.ueberpruefen.band.band_befehle import UeberpruefenBandBefehle
from vcl.qt.widgets.ribbon.kopffuss.band.band_befehle import KopfFussBandBefehle
from vcl.qt.fenster.befehle.kontextreiter.kontext import KontextBefehle
from vcl.qt.fenster.befehle.hauptreiter.pruefen import PruefenBefehle
from vcl.qt.fenster.befehle.hauptreiter.seite import SeiteBefehle
from vcl.qt.fenster.befehle.hauptreiter.serien import SerienBefehle
from vcl.qt.fenster.befehle.hauptreiter.text import TextBefehle
from vcl.qt.fenster.befehle.kontextreiter.bildtools import BildToolsBefehle
from vcl.qt.fenster.befehle.kontextreiter.diagrammtools import DiagrammToolsBefehle
from vcl.qt.fenster.befehle.kontextreiter.formtools import FormToolsBefehle
from vcl.qt.fenster.befehle.kontextreiter.smartart_knoten_zustand import SmartArtKnotenZustand
from vcl.qt.fenster.befehle.kontextreiter.smartarttools import SmartArtToolsBefehle
from vcl.qt.fenster.befehle.kontextreiter.texttools import TextToolsBefehle

from vcl.qt.widgets.ribbon.verweise.band.band_befehle import VerweiseBandBefehle
from vcl.qt.fenster.befehle.hilfen import FreiMenue, _farbfeld  # noqa: F401  (andere Module holen sie hier)


class Befehle(AnsichtBandBefehle, BearbeitenBandBefehle, BildToolsBefehle, DateiBefehle, DiagrammToolsBefehle, EinfuegenBefehle, FormToolsBefehle, KIBefehle, UeberpruefenBandBefehle, KopfFussBandBefehle, KontextBefehle, PruefenBefehle, SeiteBefehle, SerienBefehle, SmartArtKnotenZustand, SmartArtToolsBefehle, TextBefehle, TextToolsBefehle, VerweiseBandBefehle):
    """Alle Befehle des Bandes. Die Grundfunktionen (Aktion suchen, ausführen, Zustand) stehen hier, die Befehle selbst in ``kern/befehle/*``."""

    def __init__(self, win):
        self.w = win


    # ---- Hilfen --------------------------------------------------------------------
    @property
    def ed(self):
        return self.w.current_editor()


    @staticmethod
    def _teile(name: str):
        """'w.setzePapier:["a4"]' → ('w_setzePapier', ['a4'])"""
        basis, _, rest = name.partition(":")
        return basis.replace(".", "_"), (json.loads(rest) if rest else [])


    def hat(self, name: str) -> bool:
        return callable(getattr(self, self._teile(name)[0], None))


    def tun(self, name: str, knopf=None):
        basis, args = self._teile(name)
        f = getattr(self, basis, None)
        if callable(f):
            return f(knopf, *args)


    def zustand(self, name: str):
        basis, _ = self._teile(name)
        f = getattr(self, "an_" + basis, None)
        return bool(f()) if callable(f) else None


    def kann(self, name: str):
        """Ob der Befehl gerade geht (Befehl ``kann_<name>``); ``None``: keine eigene Bedingung."""
        basis, _ = self._teile(name)
        f = getattr(self, "kann_" + basis, None)
        return bool(f()) if callable(f) else None


    def band_feld(self, name: str):
        """Ein Eingabefeld fürs Band (Befehl ``feld_<name>``), z. B. die Nummer des Datensatzes im Seriendruck."""
        f = getattr(self, "feld_" + name, None)
        return f() if callable(f) else None


    def symbolname(self, name: str) -> str | None:
        """Symbol, das ein Knopf nach seiner letzten Wahl zeigt (Befehl ``symbolname_<name>``); ``None``: der Knopf behält seins."""
        basis, _ = self._teile(name)
        f = getattr(self, "symbolname_" + basis, None)
        return f() if callable(f) else None


    def haken_wert(self, item: dict) -> bool | None:
        """Haken eines Menüpunkts: Zustandsfrage des Menüeintrags (z. B. w.randVorgabeJetzt) gegen sein Argument."""
        g = item.get("haken")
        if not isinstance(g, str):
            return None
        f = getattr(self, self._teile(g)[0], None)
        if not callable(f):
            return None
        wert = f()
        _, args = self._teile(item.get("tun", ""))
        n = item.get("name")
        if g.endswith("querJetzt"):
            return bool(wert) if n == "Querformat" else not wert
        return (wert == args[0]) if args else bool(wert)


    _TRAEGE_KLAPPEN = frozenset({"texteffekteKlappe"})       # Menüs mit vielen gerenderten Vorschauen: erst beim Aufklappen bauen

    def klappe(self, name: str):
        f = getattr(self, "menue_" + name.replace(".", "_"), None)
        if not callable(f):
            return None
        if name in self._TRAEGE_KLAPPEN:
            return self._traege_klappe(f)
        return f()

    @staticmethod
    def _traege_klappe(bauer):
        """Leeres Menü mit Platzhalterzeile; beim ersten Aufklappen wird es mit dem echten Inhalt gefüllt."""
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        huelle = MenueListe()
        huelle.addAction("…")

        def fuellen():
            huelle.aboutToShow.disconnect(fuellen)
            echt = bauer()
            huelle.clear()
            for a in echt.actions():
                huelle.addAction(a)
            huelle._echt = echt                               # hält die Untermenüs am Leben
        huelle.aboutToShow.connect(fuellen)
        return huelle


    def _popup(self, menue) -> None:
        """Menü an der Mausposition zeigen (eigene Stelle, damit Tests es abfangen können)."""
        menue.exec(QCursor.pos())


    def fehlende(self, namen) -> list[str]:
        return sorted(n for n in namen if not self.hat(n))

