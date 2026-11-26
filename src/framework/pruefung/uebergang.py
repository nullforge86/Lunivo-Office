"""Übergangsliste: Module, die noch gegen die Richtungstabelle (``architektur.py``) verstoßen und noch nicht umgestellt sind.

Diese Liste darf nur kleiner werden, nie größer. Neue Dateien kommen nie auf die Liste (wie ``HTML_NOCH_ERLAUBT``). Ein Eintrag verschwindet,
sobald das Modul keinen Verstoß mehr hat. Ist sie leer, ist der Importwächter (``importe.py``) ohne Ausnahmen scharf."""
from __future__ import annotations

_NAMEN = """
vcl.qt.rendering.diagramme.diagramm_format 
vcl.qt.rendering.textfelder.felder vcl.qt.rendering.formen.bilddaten

vcl.qt.rendering.formen.bildeffekte 
vcl.qt.rendering.formen.formen 

vcl.qt.rendering.formen.frei_objekt 

vcl.qt.rendering.formen.muster vcl.qt.rendering.wordart.texteffekt

vcl.qt.eingabe.korrektur_dienst










vcl.qt.eingabe.ki_dienst 


vcl.qt.fenster.fenster.anwendung 


vcl.qt.widgets.bausteine.symbole.bauteile.symbole 





























vcl.qt.widgets.bausteine.symbole.medien.datei_symbole
vcl.qt.widgets.bausteine.symbole.piktogramme.piktogramme




vcl.qt.widgets.dialoge.lesen_hilfe.hilfe_dialoge
vcl.qt.widgets.dialoge.optionen_seiten.gemeinsam
vcl.qt.widgets.dialoge.optionen_seiten.lunivo 
vcl.qt.widgets.dokumentansicht.ansicht.eingabe






vcl.qt.widgets.ribbon.band_gruppen
vcl.qt.widgets.ribbon.band_leiste vcl.qt.widgets.ribbon.band_stile 
vcl.rendering.seitenlayout.pdf_ausgabe
vcl.qt.widgets.bausteine.skalierung.daten vcl.qt.widgets.bausteine.symbole.bauteile.symbole_hybrid
""".split()

NOCH_NICHT_UMGESTELLT: frozenset[str] = frozenset(_NAMEN)

# Übergangsmodule im Kern: ehemals ``editor`` und ``korrektur``, jetzt in den Fachordnern von ``core/``. Sie dürfen weiter ``system`` und sich gegenseitig importieren
# (Schicht ``uebergang`` in ``architektur.py``). Auch diese Liste darf nur kleiner werden; ein Modul verlässt sie, sobald es nur noch ``core`` importiert.
ALT_MODULE_KERN: frozenset[str] = frozenset("""
core.aenderungsverfolgung.vergleich.vergleich core.aenderungsverfolgung.vergleich.vergleich_datum_kern 
core.diagramme.daten.diagramm_zusatz 
vcl.qt.rendering.diagramme.diagramm_format core.diagramme.typen.diagramm_typen
vcl.qt.rendering.textfelder.felder core.dokument.felder_text_kern 
core.dokument.gehe_zu core.dokument.je_stand core.dokument.vorlagen core.dokument.zusatz
core.formatierung.absatz.absatzopt vcl.qt.rendering.wordart.texteffekt vcl.qt.rendering.formen.muster 

core.formatierung.schrift.zeichenzusatz core.formatvorlagen.zeichen.designs core.formatvorlagen.zeichen.stile core.korrektur.fund
core.korrektur.inkrement vcl.qt.eingabe.korrektur_dienst core.korrektur.rechtschreibung.autokorrektur core.korrektur.rechtschreibung.pruefung
core.korrektur.silbentrennung.silben_de core.korrektur.sprache.klang core.korrektur.sprache.phonetik core.korrektur.woerterbuecher.haeufig
core.korrektur.woerterbuecher.vorhersage core.layout.seitenumbruch.seitenplan core.layout.seitenumbruch.seitenplatz vcl.qt.rendering.formen.frei_objekt
vcl.qt.rendering.formen.bilddaten vcl.qt.rendering.formen.bildeffekte 

vcl.qt.rendering.formen.formen 


core.tabellen.formatierung.tabellenstil core.tabellen.modell.tabelle_text
core.tabellen.modell.tabelleneigenschaften core.tabellen.modell.tabellenzustand core.text.ki_markdown core.text.statistik core.text.wortextras
core.text.zahlformat

core.tabellen.modell.tabelle_einfuegen core.bearbeitung.einfuegen_hilfen core.korrektur.rechtschreibung.pruefung_hilfen core.korrektur.sprache.klangpruefung
core.korrektur.grammatik.satzbau core.korrektur.grammatik.zusammenschreibung core.korrektur.rechtschreibung.pruefung
framework.serienbriefe.datenquellen.serienquelle framework.serienbriefe.erstellung.etiketten framework.serienbriefe.erstellung.serienbrief
framework.serienbriefe.erstellung.umschlag framework.serienbriefe.platzhalter.konstanten framework.serienbriefe.platzhalter.serienfelder
""".split())

# Die Übergangsliste der Darstellung (Bausteine, Farben, Maße, Schriften, Stile) steht beim Wächter selbst:
# ``writer/baukasten/pruefung/darstellung_waechter.py`` (``DARSTELLUNG_NOCH_NICHT_UMGESTELLT``, Datei → Anzahl; darf nur kleiner werden).

# Schnittstellen, die noch ``object`` oder fehlende Typangaben enthalten (die Editor-Fassade gibt dort noch Objekte des Kerns weiter). Auch diese Liste darf nur
# kleiner werden; sie ist leer, wenn das Farmwork die Dokumente selbst hält und nur eigene ``frozen``-Datentypen herausgibt.
NOCH_NICHT_UMGESTELLT_TYPEN: frozenset[str] = frozenset("framework.schnittstellen." + n for n in (
    "dokument", "seiten_port", "aenderungs_port"))
