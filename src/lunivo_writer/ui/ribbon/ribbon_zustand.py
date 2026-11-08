"""Zustandsaktualisierung für das Menüband."""
from __future__ import annotations

from lunivo_writer.ui.widgets import icons


class BandZustandBaustein:
    """Hält Knöpfe und Felder des Menübandes mit dem Dokumentzustand synchron."""

    def aktualisieren(self, hat_dokument: bool | None = None):
        if hat_dokument is not None:
            self._hat_dok = hat_dokument
        for k, name in self.wechsler:
            n = self.b.symbolname(name)
            if n:
                k.defaultAction().setIcon(icons.icon(n, k.iconSize().width()))
        for k, name in self.schalter:
            z = self.b.zustand(name) if name else None
            a = k.defaultAction()
            a.blockSignals(True)
            a.setChecked(bool(z))
            a.blockSignals(False)
        if hat_dokument is not None:
            for k, name, braucht in self.knoepfe:
                if braucht and not k.property("fehlt"):
                    k.setEnabled(hat_dokument)
        for k, name, _braucht in self.knoepfe:
            if name and not k.property("fehlt"):
                frei = self.b.kann(name)
                if frei is not None:
                    k.setEnabled(bool(frei) and hat_dokument is not False)
        for f in self.felder.values():
            auf = getattr(f, "auffrischen", None)
            if callable(auf):
                auf()
