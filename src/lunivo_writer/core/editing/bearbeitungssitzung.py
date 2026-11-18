"""Die zentrale Bearbeitungssitzung — der eine Weg, auf dem ein ``Dokument`` fachlich geändert wird. Ohne Qt.

Sie hält das Dokument, Schreibmarke und Auswahl, führt jede Operation als Schritt mit Rückgängig/Wiederholen aus (``verlauf.py``),
meldet Änderungen an Beobachter und prüft die Angaben. Die Operationen stehen nach Gebiet getrennt:

* ``texteingabe.TextTeil`` — Text einfügen, löschen, ersetzen; Absätze; Suche
* ``zwischenablage.ZwischenablageTeil`` — Ausschnitte kopieren und einfügen
* ``formatbearbeitung.FormatTeil`` — Zeichen- und Absatzformat, Formatvorlagen, Listen und Nummerierung
* ``tabellenbearbeitung.TabellenTeil`` — Tabellen, Zeilen, Spalten, Zellen verbinden und teilen, Tabelle ↔ Text
* ``objektbearbeitung.ObjektTeil`` — Bilder, Formen, Textfelder, grafische Objekte (im Text oder frei positioniert), Textrahmen
* ``abschnittsbearbeitung.AbschnittTeil`` — Abschnitte, Seiteneinrichtung, Kopf- und Fußzeilen, Dokumenteigenschaften
* ``zusatzbearbeitung.ZusatzTeil`` — Kommentare, Noten, Textmarken, Felder, Verweise, Verzeichnisse, nachverfolgte Änderungen
* ``ersatzbearbeitung.ErsatzTeil`` — Absatzfolgen und Zusatzdaten als ein Schritt ersetzen

Die Klasse ersetzt die ältere ``Sitzung`` (``sitzung.py``) und übernimmt deren Namen, sobald deren Aufrufstellen umgestellt sind.

Beispiel::

    s = Bearbeitungssitzung()
    s.text_einfuegen("Hallo Welt")
    s.zeichenformat_anwenden({"fett": True}, Auswahl(Position(a, 0), Position(a, 5)))
    s.rueckgaengig()
"""
from __future__ import annotations

from ..document.dokument import Auswahl, Dokument, neues_dokument
from ..document.pruefung import pruefe_dokument
from .abschnittsbearbeitung import AbschnittTeil
from .auswahl import AuswahlTeil
from .ersatzbearbeitung import ErsatzTeil
from .formatbearbeitung import FormatTeil
from .objektbearbeitung import ObjektTeil
from .suche import SuchTeil
from .tabellenbearbeitung import TabellenTeil
from .texteingabe import TextTeil
from .verlauf import Verlauf, schritt
from .zusatzbearbeitung import ZusatzTeil
from .zwischenablage import ZwischenablageTeil

_FELDER = ("abschnitte", "vorlagen", "listen", "kommentare", "noten", "objekte", "ressourcen", "quellen", "eigenschaften", "standardformat")


class Bearbeitungssitzung(TextTeil, SuchTeil, ZwischenablageTeil, FormatTeil, TabellenTeil, ObjektTeil, AbschnittTeil, ZusatzTeil, ErsatzTeil, AuswahlTeil, Verlauf):
    def __init__(self, dokument: Dokument | None = None):
        self.dokument = dokument or neues_dokument()
        anfang = self.dokument.anfang()
        self._auswahl = Auswahl(anfang, anfang)
        Verlauf.__init__(self)

    def pruefe(self) -> list:
        """Prüft den Aufbau des Dokuments; gibt die gefundenen Fehler als Texte zurück (leer = in Ordnung)."""
        return pruefe_dokument(self.dokument)

    @schritt("Dokument ersetzen", "text")
    def dokument_ersetzen(self, neu: Dokument) -> None:
        """Setzt den ganzen Inhalt des Dokuments (Abschnitte, Vorlagen, Listen, Zusatzdaten …) auf den von ``neu`` — etwa nach dem
        Laden einer Datei. Ein Schritt; der alte Inhalt bleibt für Rückgängig unverändert erhalten."""
        for name in _FELDER:
            self._attr(self.dokument, name, getattr(neu, name))
        self._attr(self.dokument, "naechste_id", max(self.dokument.naechste_id, neu.naechste_id))
        self._offen.struktur = self._offen.neu_struktur = True
        alle = {"abschnitt", "liste", "tabelle", "objekt", "seite", "zusatz", "vorlage", "meta"}
        self._offen.bereiche.update(alle)
        self._offen.neu_bereiche.update(alle)
        self._setze(self.dokument.anfang())
