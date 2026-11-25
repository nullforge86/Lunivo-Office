"""Anwendungskern: Befehle (commands), Pfade — ohne Oberflächenlogik."""
from framework.dokumentverwaltung import kernorte as _kernorte

_kernorte.anmelden()                                   # der Kern bekommt seine Orte vom Framework, nicht aus ``system``
