"""Aufklappbare Abschnitte als Gruppe: höchstens einer ist offen.

    EinzelOffen(abschnitt_a, abschnitt_b, …)      # Abschnitt = ``texteffekt_dialog.Abschnitt`` (Pfeilknopf ``knopf``, ``toggled``)
    gruppe.schliesse_alle()                        # alle zuklappen (ohne Rückmeldung nach außen)

Beim Aufklappen eines Abschnitts (``knopf.toggled``) klappt die Gruppe die anderen zu. Zuklappen ändert die anderen nicht.
Die Gruppe merkt sich nichts außer den Abschnitten; wer sie anlegt, hält sie (z. B. als Attribut).
"""
from __future__ import annotations


class EinzelOffen:
    def __init__(self, *abschnitte) -> None:
        self._abschnitte = list(abschnitte)
        for a in self._abschnitte:
            a.knopf.toggled.connect(lambda an, a=a: self._geoeffnet(a) if an else None)

    def _geoeffnet(self, offen) -> None:
        for a in self._abschnitte:
            if a is not offen and a.knopf.isChecked():
                a.knopf.setChecked(False)

    def schliesse_alle(self) -> None:
        for a in self._abschnitte:
            if a.knopf.isChecked():
                a.knopf.setChecked(False)
