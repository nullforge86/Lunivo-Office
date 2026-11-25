"""Übergangsliste: Module, die noch gegen die Richtungstabelle (``architektur.py``) verstoßen und noch nicht umgestellt sind.

Diese Liste darf nur kleiner werden, nie größer. Neue Dateien kommen nie auf die Liste (wie ``HTML_NOCH_ERLAUBT``). Ein Eintrag verschwindet,
sobald das Modul keinen Verstoß mehr hat. Ist sie leer, ist der Importwächter (``importe.py``) ohne Ausnahmen scharf."""
from __future__ import annotations

_NAMEN = """
vcl.qt.rendering.diagramme.diagramm vcl.qt.rendering.diagramme.diagramm_format vcl.qt.rendering.diagramme.diagramm_stile vcl.qt.rendering.diagramme.diagramm_teile
vcl.qt.rendering.formen.einfuegen vcl.qt.rendering.textfelder.felder vcl.qt.rendering.textfelder.formular vcl.qt.rendering.formen.bilddaten
vcl.qt.rendering.formen.bild_einfuegen vcl.qt.rendering.textfelder.formel_einfuegen vcl.qt.rendering.formen.form_einfuegen vcl.qt.rendering.wordart.wordart_einfuegen
vcl.qt.rendering.formen.bildeffekte vcl.qt.rendering.formen.bildlayout vcl.qt.rendering.formen.bildwerkzeuge vcl.qt.rendering.formen.bildzuschnitt
vcl.qt.rendering.formen.freie_bilder vcl.qt.rendering.formen.formen vcl.qt.rendering.formen.formen_anpassen
vcl.qt.rendering.formen.formen_katalog vcl.qt.rendering.formen.formen_stile vcl.qt.rendering.formen.freiform vcl.qt.rendering.formen.linie
vcl.qt.rendering.formen.sprechblasen vcl.qt.rendering.formen.frei_objekt vcl.qt.rendering.textfelder.frei_objekt_text
vcl.qt.rendering.smartart.smartart vcl.qt.rendering.smartart.smartart_zeichnen vcl.qt.rendering.textfelder.deckblatt vcl.qt.rendering.formen.seitenrahmen
vcl.qt.rendering.textfelder.wasserzeichen vcl.qt.rendering.formen.muster vcl.qt.schrift.schreibweise vcl.qt.rendering.wordart.texteffekt
vcl.qt.rendering.wordart.textfx vcl.qt.rendering.wordart.textfx_vorgaben vcl.qt.rendering.wordart.textfx_zeichen vcl.qt.rendering.formen.textur vcl.qt.eingabe.barrierefreiheit
vcl.qt.eingabe.korrektur_dienst


vcl.qt.fenster.befehle.hauptreiter.einfuegen vcl.qt.fenster.befehle.hauptreiter.einfuegen_objekte 
vcl.qt.fenster.befehle.hauptreiter.pruefen vcl.qt.fenster.befehle.hauptreiter.seite 
vcl.qt.fenster.befehle.hauptreiter.text_zeichen
vcl.qt.fenster.befehle.kontextreiter.diagrammtools

vcl.qt.fenster.befehle.kontextreiter.tabellen_format vcl.qt.fenster.befehle.kontextreiter.texttools 
vcl.qt.drucken.drucken 
vcl.qt.eingabe.ki.ki_chat 
vcl.qt.eingabe.ki_dienst vcl.qt.widgets.menues.backstage.backstage_dokument

vcl.qt.fenster.dateien.dateien_export vcl.qt.fenster.dateien.dateien_oeffnen vcl.qt.fenster.dateien.dateien_speichern
vcl.qt.fenster.dateien.dateien_vorlagen vcl.qt.fenster.fenster.anwendung vcl.qt.fenster.fenster.dokument_sync
vcl.qt.rendering.formen.anzeige vcl.qt.rendering.formen.geometrie
vcl.qt.rendering.formen.pfad vcl.qt.rendering.formen.rendering vcl.qt.widgets.bausteine.rahmen.linien vcl.qt.widgets.bausteine.symbole.bauteile.mini_leiste
vcl.qt.widgets.bausteine.symbole.bauteile.symbole vcl.qt.widgets.seitenleisten.chat.chat_blase 


vcl.qt.widgets.objektwerkzeuge.diagramme.diagramm_text_panel
vcl.qt.widgets.dialoge.dokument.aenderungs_vorschau 
vcl.qt.widgets.dialoge.dokument.liste_dialog vcl.qt.widgets.dialoge.dokument.pdf_export
vcl.qt.widgets.dialoge.dokument.tabstopp_dialog
vcl.qt.widgets.menues.dropdown.objektmenues.diagramm_popups

vcl.qt.widgets.menues.dropdown.objektmenues.objekt_menues

vcl.qt.widgets.bausteine.interaktion.felder.auswahl_bereich vcl.qt.widgets.dialoge.formatierung.absatz_dialog
vcl.qt.widgets.dialoge.formatierung.formatvorlage_dialog vcl.qt.widgets.dialoge.formatierung.ruby_dialog

vcl.qt.widgets.dialoge.formatierung.text_format 
vcl.qt.widgets.dialoge.dokument.gliederung_anpassen_dialog vcl.qt.widgets.dialoge.dokument.liste_dialog_hilfen
vcl.qt.widgets.dialoge.dokument.listen_dialog vcl.qt.widgets.dialoge.dokument.nummerierung_anpassen_dialog

vcl.qt.widgets.dialoge.einfuegen.seitenzahl_dialog 
vcl.qt.widgets.dialoge.einfuegen.sonderzeichen_dialog vcl.qt.widgets.dialoge.einfuegen.trenner_dialog 
vcl.qt.widgets.dialoge.formatierung.objekt_format_panel 

vcl.qt.widgets.dialoge.formatierung.rahmen_seite




vcl.qt.widgets.dialoge.tabellen_eigenschaften_dialog
vcl.qt.widgets.dokumentansicht.ansicht.lineal_h 
vcl.qt.widgets.dokumentansicht.dokumentfenster.navigation_hilfen vcl.qt.widgets.dokumentansicht.dokumentfenster.navigation_panel
vcl.qt.widgets.dialoge.formatierung.umschlossen_dialog vcl.qt.widgets.bausteine.symbole.medien.datei_symbole
vcl.qt.widgets.bausteine.symbole.piktogramme.piktogramme
vcl.qt.widgets.seitenleisten.vorlagen.vorlagen_galerie vcl.qt.widgets.dialoge.dokument_dialoge

vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster 
vcl.qt.widgets.dialoge.einfuegen.wasserzeichen_fenster 
vcl.qt.widgets.dialoge.lesen_hilfe.hilfe_dialoge
vcl.qt.widgets.dialoge.optionen_seiten.datei vcl.qt.widgets.dialoge.optionen_seiten.gemeinsam
vcl.qt.widgets.dialoge.optionen_seiten.lesen vcl.qt.widgets.dialoge.optionen_seiten.lunivo vcl.qt.widgets.dokumentansicht.ansicht.blasen_bedienung
vcl.qt.widgets.dokumentansicht.ansicht.dokument_ansicht vcl.qt.widgets.dokumentansicht.ansicht.eingabe
vcl.qt.widgets.dokumentansicht.ansicht.objekt_bedienung vcl.qt.widgets.dokumentansicht.ansicht.vorschau_ansicht


vcl.qt.widgets.dokumentansicht.bearbeitung.kern_befehle vcl.qt.widgets.dokumentansicht.bearbeitung.kern_editor
vcl.qt.widgets.dokumentansicht.bearbeitung.kern_objekte 
vcl.qt.widgets.dokumentansicht.dokumentfenster.dokument_bereich
vcl.qt.widgets.dokumentansicht.dokumentfenster.suchen_feld vcl.qt.widgets.dokumentansicht.kopffuss.noten_feld vcl.qt.widgets.ribbon.band_gruppen
vcl.qt.widgets.ribbon.band_leiste vcl.qt.widgets.ribbon.band_stile vcl.qt.widgets.seitenleisten.ki_panel
vcl.qt.widgets.seitenleisten.schreib_panel vcl.qt.widgets.seitenleisten.seitenleiste vcl.rendering.seitenlayout.pdf_ausgabe
vcl.qt.widgets.bausteine.skalierung.daten vcl.qt.widgets.bausteine.symbole.bauteile.symbole_hybrid
""".split()

NOCH_NICHT_UMGESTELLT: frozenset[str] = frozenset(_NAMEN)

# Übergangsmodule im Kern: ehemals ``editor`` und ``korrektur``, jetzt in den Fachordnern von ``core/``. Sie dürfen weiter ``system`` und sich gegenseitig importieren
# (Schicht ``uebergang`` in ``architektur.py``). Auch diese Liste darf nur kleiner werden; ein Modul verlässt sie, sobald es nur noch ``core`` importiert.
ALT_MODULE_KERN: frozenset[str] = frozenset("""
core.aenderungsverfolgung.vergleich.vergleich core.aenderungsverfolgung.vergleich.vergleich_datum_kern vcl.qt.eingabe.barrierefreiheit
vcl.qt.rendering.formen.einfuegen vcl.qt.rendering.diagramme.diagramm_teile core.diagramme.daten.diagramm_zusatz vcl.qt.rendering.diagramme.diagramm
vcl.qt.rendering.diagramme.diagramm_format vcl.qt.rendering.diagramme.diagramm_stile core.diagramme.typen.diagramm_typen
vcl.qt.rendering.textfelder.deckblatt vcl.qt.rendering.textfelder.felder core.dokument.felder_ergebnis_kern core.dokument.felder_text_kern vcl.qt.rendering.textfelder.formular
core.dokument.gehe_zu core.dokument.je_stand core.dokument.vorlagen vcl.qt.rendering.textfelder.wasserzeichen core.dokument.zusatz
core.formatierung.absatz.absatzopt vcl.qt.rendering.wordart.texteffekt vcl.qt.rendering.formen.muster vcl.qt.rendering.formen.textur
vcl.qt.rendering.formen.seitenrahmen vcl.qt.schrift.schreibweise
core.formatierung.schrift.zeichenzusatz core.formatvorlagen.zeichen.designs core.formatvorlagen.zeichen.stile core.korrektur.fund
core.korrektur.inkrement vcl.qt.eingabe.korrektur_dienst core.korrektur.rechtschreibung.autokorrektur core.korrektur.rechtschreibung.pruefung
core.korrektur.silbentrennung.silben_de core.korrektur.sprache.klang core.korrektur.sprache.phonetik core.korrektur.woerterbuecher.haeufig
core.korrektur.woerterbuecher.vorhersage core.layout.seitenumbruch.seitenplan core.layout.seitenumbruch.seitenplatz vcl.qt.rendering.formen.frei_objekt
vcl.qt.rendering.formen.bilddaten vcl.qt.rendering.formen.bildeffekte vcl.qt.rendering.formen.bildlayout
vcl.qt.rendering.formen.freie_bilder vcl.qt.rendering.formen.bildwerkzeuge vcl.qt.rendering.formen.bildzuschnitt
vcl.qt.rendering.formen.formen vcl.qt.rendering.formen.formen_anpassen vcl.qt.rendering.formen.formen_katalog vcl.qt.rendering.formen.formen_stile
vcl.qt.rendering.formen.freiform vcl.qt.rendering.formen.linie vcl.qt.rendering.formen.sprechblasen vcl.qt.rendering.smartart.smartart
vcl.qt.rendering.smartart.smartart_zeichnen vcl.qt.rendering.textfelder.frei_objekt_text vcl.qt.rendering.wordart.textfx
vcl.qt.rendering.wordart.textfx_vorgaben vcl.qt.rendering.wordart.textfx_zeichen core.tabellen.formatierung.tabellenstil core.tabellen.modell.tabelle_text
core.tabellen.modell.tabelleneigenschaften core.tabellen.modell.tabellenzustand core.text.ki_markdown core.text.statistik core.text.wortextras
core.text.zahlformat
vcl.qt.rendering.formen.bild_einfuegen vcl.qt.rendering.textfelder.formel_einfuegen vcl.qt.rendering.formen.form_einfuegen vcl.qt.rendering.wordart.wordart_einfuegen
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
    "dokument", "seiten_port", "aenderungs_port", "vorschau"))
