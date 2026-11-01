"""Kompatibilitätsmodul für den sicheren Schreibweg.

Die Implementierung liegt in core.document_manager. Dieses Modul bleibt als
alter Importpfad erhalten, damit bestehende Dienste und Tests kompatibel sind.
"""
import sys
from lunivo_writer.core import document_manager as _implementation

# Den Modulnamen auf dieselbe Modulinstanz legen: Monkeypatches und interne
# Modulzustände (z. B. Sicherungsordner) wirken damit auch auf die Implementierung.
sys.modules[__name__] = _implementation
