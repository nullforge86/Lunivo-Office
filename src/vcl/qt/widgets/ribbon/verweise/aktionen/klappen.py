"""Klappen (Pfeilmenüs) der Knöpfe im Reiter „Verweise“: Klappe „Inhaltsverzeichnis“ mit der Gliederungsebene des Absatzes."""
from __future__ import annotations

from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe


class VerweiseKlappen:
    def menue_inhaltsverzeichnisKlappe(self):
        """Ebene 1–9 und Textkörper wie in der Vorlage. In Lunivo trägt die Ebene die Formatvorlage „Überschrift N“
        (Textkörper: „Standard“); das Inhaltsverzeichnis nimmt diese Absätze auf. Der Haken zeigt die Ebene am Zeiger."""
        m = MenueListe()
        eintraege = [m.eintrag(f"Ebene &{n}", lambda n=n: self.inhaltsEbene(None, n), haken=False) for n in range(1, 10)]
        eintraege.append(m.eintrag("Textkörper(&B)", lambda: self.inhaltsEbene(None, 0), haken=False))

        def auffrischen():
            fw = self._vw()
            jetzt = fw.gliederungsebene() if fw is not None else -1
            for i, a in enumerate(eintraege):
                a.setEnabled(fw is not None)
                a.setChecked((i + 1 if i < 9 else 0) == jetzt)
        m.aboutToShow.connect(auffrischen)
        return m
