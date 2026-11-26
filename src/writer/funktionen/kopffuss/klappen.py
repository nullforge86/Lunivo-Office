"""Die Einträge der Klappen an den Knöpfen auf dem Blatt (Kopf- und Fußzeile) als Daten: (Schlüssel, Beschriftung).

Die Oberfläche zeigt sie nur an und meldet den gewählten Schlüssel an den Bearbeiter; welche Schlüssel es gibt, steht allein hier."""
from __future__ import annotations

# „Seitenzahlenformat“: Zahlenart der Seitennummer
FORMATE = (("dezimal", "1, 2, 3 …"), ("klein", "a, b, c …"), ("gross", "A, B, C …"), ("roem_klein", "i, ii, iii …"), ("roem_gross", "I, II, III …"))

# „Seitenzahl löschen“: wo die Seitenzahl entfernt wird
LOESCHEN = (("aktuelle", "Aktuelle Seite"), ("dokument", "Gesamtes Dokument"), ("auf", "Auf aktuelle Seite"), ("von", "Von aktueller Seite"),
            ("abschnitt", "Aktueller Abschnitt"))

# „Seitenzahl einfügen“: Position als Kacheln, je Tupel eine Reihe
POSITIONEN = ((("left", "Links"), ("center", "Zentriert"), ("right", "Rechts")), (("aussen", "Außen"), ("innen", "Innen")))
POSITION_VORGABE = "center"

# „Seitenzahl einfügen“: wofür die Seitenzahl übernommen wird
BEREICHE = (("dokument", "Gesamtes Dokument"), ("seite", "Von aktueller Seite"), ("abschnitt", "Aktueller Abschnitt"))
BEREICH_VORGABE = "dokument"

# Absatz-Symbol links vom Feld
ABSATZ = (("zuruecksetzen", "Absatzformat zurücksetzen"), ("ausblenden", "Symbol vom Absatz-Layout ausblenden"))
AUSRICHTUNG_VORGABE = "center"                # „Absatzformat zurücksetzen“ stellt diese Ausrichtung wieder her
