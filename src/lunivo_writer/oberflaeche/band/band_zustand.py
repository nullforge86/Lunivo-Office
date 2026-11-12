"""Zustandsaktualisierung für das Menüband."""
from __future__ import annotations

from lunivo_writer.oberflaeche.bauteile import symbole


class BandZustandBaustein:
    """Hält Knöpfe und Felder des Menübandes mit dem Dokumentzustand synchron."""

    def aktualisieren(self, hat_dokument: bool | None = None):
        if hat_dokument is not None:
            self._hat_dok = hat_dokument
        self._wechsler_auffrischen()
        self._schalter_auffrischen()
        self._knoepfe_auffrischen(hat_dokument)
        self._felder_auffrischen()

    def _wechsler_auffrischen(self) -> None:
        """Symbole der Wechsler (z. B. Ansicht) nach dem Zustand."""
        for k, name in self.wechsler:
            n = self.b.symbolname(name)
            if n:
                k.defaultAction().setIcon(symbole.icon(n, k.iconSize().width()))

    def _schalter_auffrischen(self) -> None:
        """Angekreuzt, wenn der Zustand des Befehls gilt; ohne Signal, damit nichts ausgelöst wird."""
        for k, name in self.schalter:
            z = self.b.zustand(name) if name else None
            a = k.defaultAction()
            a.blockSignals(True)
            a.setChecked(bool(z))
            a.blockSignals(False)

    def _knoepfe_auffrischen(self, hat_dokument: bool | None) -> None:
        """Knöpfe, die ein Dokument brauchen, und Knöpfe, deren Befehl im Augenblick nicht frei ist."""
        if hat_dokument is not None:
            for k, name, braucht in self.knoepfe:
                if braucht and not k.property("fehlt"):
                    k.setEnabled(hat_dokument)
        for k, name, _braucht in self.knoepfe:
            if name and not k.property("fehlt"):
                frei = self.b.kann(name)
                if frei is not None:
                    k.setEnabled(bool(frei) and hat_dokument is not False)

    def _felder_auffrischen(self) -> None:
        for f in self.felder.values():
            auf = getattr(f, "auffrischen", None)
            if callable(auf):
                auf()
