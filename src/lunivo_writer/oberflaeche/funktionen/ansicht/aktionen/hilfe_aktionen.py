"""Aktionen der Hilfe-Knöpfe in der Ansicht: Handbuch, Tastenkürzel, Erweiterungen, Lesehilfe, Silbeneinstellungen. Nur Fenster öffnen."""
from __future__ import annotations


class HilfeAktionen:
    def handbuch(self, k=None):
        from lunivo_writer.oberflaeche.dialoge.lesen_hilfe import hilfe_dialoge
        hilfe_dialoge.handbuch(self.w).exec()

    def tastenHilfe(self, k=None):
        from lunivo_writer.oberflaeche.dialoge.lesen_hilfe import hilfe_dialoge
        hilfe_dialoge.tastenkuerzel(self.w).exec()

    def erweiterungen(self, k=None):
        from lunivo_writer.oberflaeche.dialoge.lesen_hilfe import hilfe_dialoge
        hilfe_dialoge.erweiterungen(self.w).exec()

    def lesehilfe(self, k=None):
        from lunivo_writer.oberflaeche.dialoge.lesen_hilfe.lesehilfe_dialog import LesehilfeDialog
        d = LesehilfeDialog(self.w)
        self._lh = d
        d.zeige(k if hasattr(k, "mapToGlobal") else None)

    def silbenEinstellen(self, k=None):
        from lunivo_writer.oberflaeche.dialoge.lesen_hilfe.silben_dialog import SilbenDialog
        SilbenDialog(self.w).exec()
