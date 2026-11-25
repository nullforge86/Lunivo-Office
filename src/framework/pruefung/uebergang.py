"""Übergangsliste: Module, die noch gegen die Richtungstabelle (``architektur.py``) verstoßen und noch nicht umgestellt sind.

Diese Liste darf nur kleiner werden, nie größer. Neue Dateien kommen nie auf die Liste (wie ``HTML_NOCH_ERLAUBT``). Ein Eintrag verschwindet,
sobald das Modul keinen Verstoß mehr hat. Ist sie leer, ist der Importwächter (``importe.py``) ohne Ausnahmen scharf."""
from __future__ import annotations

_NAMEN = """
core.diagramme.diagramm core.diagramme.formatierung.diagramm_format core.diagramme.formatierung.diagramm_stile core.diagramme.daten.diagramm_teile
core.bearbeitung.einfuegen core.dokument.felder core.dokument.formular core.objekte.bilder.modell.bilddaten
core.objekte.bilder.modell.bild_einfuegen core.objekte.formeln.modell.formel_einfuegen core.objekte.formen.form_einfuegen core.objekte.wordart.wordart_einfuegen
core.objekte.bilder.modell.bildeffekte core.objekte.bilder.positionierung.bildlayout core.objekte.bilder.skalierung.bildwerkzeuge core.objekte.bilder.zuschneiden.bildzuschnitt
core.objekte.bilder.positionierung.freie_bilder core.objekte.formen.formen core.objekte.formen.formen_anpassen
core.objekte.formen.formen_katalog core.objekte.formen.formen_stile core.objekte.formen.freiform core.objekte.formen.linie
core.objekte.formen.sprechblasen core.objekte.basis.frei_objekt core.objekte.textfelder.modell.frei_objekt_text
core.objekte.smartart.smartart core.objekte.smartart.smartart_zeichnen core.dokument.abschnitte.deckblatt core.formatierung.rahmen.seitenrahmen
core.dokument.wasserzeichen.wasserzeichen core.formatierung.fuellung.muster core.formatierung.schrift.schreibweise core.formatierung.schrift.silbenfarben core.formatierung.effekte.texteffekt
core.objekte.wordart.textfx core.objekte.wordart.textfx_vorgaben core.objekte.wordart.textfx_zeichen core.formatierung.fuellung.textur core.barrierefreiheit.barrierefreiheit
core.korrektur.korrektur_dienst core.formatierung.schrift.datenbank framework.befehle.befehlsliste framework.befehle.hauptreiter.datei
framework.befehle.hauptreiter.einfuegen framework.befehle.hauptreiter.einfuegen_objekte framework.befehle.hauptreiter.ki
framework.befehle.hauptreiter.pruefen framework.befehle.hauptreiter.seite framework.befehle.hauptreiter.serien
framework.befehle.hauptreiter.text_absatz framework.befehle.hauptreiter.text_vorlagen framework.befehle.hauptreiter.text_zeichen
framework.befehle.hilfen framework.befehle.kontextreiter.bildtools framework.befehle.kontextreiter.diagrammtools
framework.befehle.kontextreiter.formtools framework.befehle.kontextreiter.kontext framework.befehle.kontextreiter.tabellen
framework.befehle.kontextreiter.tabellen_format framework.befehle.kontextreiter.texttools framework.befehle.kontextreiter.zeichentools
framework.dokumentverwaltung.ausgabe.bild_export framework.dokumentverwaltung.ausgabe.drucken framework.dokumentverwaltung.ausgabe.vektor_bilder
framework.ki.chat.ki_chat framework.ki.dienst.arbeitslauf framework.ki.dienst.ki_aktionen framework.ki.dienst.ki_anfragen
framework.ki.dienst.ki_dauerbetrieb framework.ki.dienst.ki_dienst vcl.qt.widgets.menues.backstage.backstage_dokument
vcl.qt.widgets.menues.backstage.backstage_fenster vcl.qt.widgets.menues.backstage.backstage_objektformat vcl.qt.fenster.dateien.dateien_drucken
vcl.qt.fenster.dateien.dateien_export vcl.qt.fenster.dateien.dateien_oeffnen vcl.qt.fenster.dateien.dateien_speichern
vcl.qt.fenster.dateien.dateien_vorlagen vcl.qt.fenster.fenster.anwendung vcl.qt.fenster.fenster.bearbeiten vcl.qt.fenster.fenster.dokument_sync
vcl.qt.fenster.fenster.programmfenster vcl.qt.fenster.fenster.reiter_zustand vcl.qt.rendering.formen.anzeige vcl.qt.rendering.formen.geometrie
vcl.qt.rendering.formen.pfad vcl.qt.rendering.formen.rendering vcl.qt.widgets.bausteine.rahmen.linien vcl.qt.widgets.bausteine.symbole.bauteile.mini_leiste
vcl.qt.widgets.bausteine.symbole.bauteile.symbole vcl.qt.widgets.seitenleisten.chat.chat_blase vcl.qt.widgets.seitenleisten.chat.chat_eingabe
vcl.qt.widgets.seitenleisten.chat.chat_leerzustand vcl.qt.widgets.seitenleisten.chat.chat_regler vcl.qt.widgets.objektwerkzeuge.diagramme.diagramm_format_bausteine
vcl.qt.widgets.objektwerkzeuge.diagramme.diagramm_format_panel vcl.qt.widgets.objektwerkzeuge.diagramme.diagramm_format_werte
vcl.qt.widgets.objektwerkzeuge.diagramme.diagramm_text_panel vcl.qt.widgets.objektwerkzeuge.diagramme.smartart_stil_kacheln
vcl.qt.widgets.dialoge.dokument.aenderungs_vorschau vcl.qt.widgets.dialoge.dokument.druck_dialog vcl.qt.widgets.dialoge.dokument.eingabe_fenster
vcl.qt.widgets.dialoge.dokument.layout_dialog vcl.qt.widgets.dialoge.dokument.liste_dialog vcl.qt.widgets.dialoge.dokument.pdf_export
vcl.qt.widgets.dialoge.dokument.sortieren_dialog vcl.qt.widgets.dialoge.dokument.tabstopp_dialog
vcl.qt.widgets.menues.dropdown.objektmenues.bild_diagramm_menues vcl.qt.widgets.menues.dropdown.objektmenues.diagramm_popups
vcl.qt.widgets.menues.dropdown.objektmenues.form_menues vcl.qt.widgets.menues.dropdown.objektmenues.fuell_voreinstellungen
vcl.qt.widgets.menues.dropdown.objektmenues.linien_voreinstellungen vcl.qt.widgets.menues.dropdown.objektmenues.objekt_menues
vcl.qt.widgets.menues.dropdown.objektmenues.smartart_menues vcl.qt.widgets.menues.dropdown.text_kopf_menue_mixin
vcl.qt.widgets.bausteine.interaktion.felder.auswahl_bereich vcl.qt.widgets.dialoge.formatierung.absatz_dialog
vcl.qt.widgets.dialoge.formatierung.formatvorlage_dialog vcl.qt.widgets.dialoge.formatierung.ruby_dialog
vcl.qt.widgets.dialoge.formatierung.schreibweise_dialog vcl.qt.widgets.dialoge.formatierung.schriftart_dialog
vcl.qt.widgets.dialoge.formatierung.text_format vcl.qt.widgets.dialoge.formatierung.text_fuellarten_mixin
vcl.qt.widgets.dialoge.formatierung.textfeld_abschnitt
vcl.qt.widgets.dialoge.dokument.gliederung_anpassen_dialog vcl.qt.widgets.dialoge.dokument.liste_dialog_hilfen
vcl.qt.widgets.dialoge.dokument.listen_dialog vcl.qt.widgets.dialoge.dokument.nummerierung_anpassen_dialog
vcl.qt.widgets.dialoge.einfuegen.baustein_dialog vcl.qt.widgets.dialoge.einfuegen.datum_dialog vcl.qt.widgets.dialoge.einfuegen.felder_dialog
vcl.qt.widgets.dialoge.einfuegen.form_dialog vcl.qt.widgets.dialoge.einfuegen.seitenzahl_dialog vcl.qt.widgets.dialoge.einfuegen.smart_art_dialog
vcl.qt.widgets.dialoge.einfuegen.sonderzeichen_dialog vcl.qt.widgets.dialoge.einfuegen.trenner_dialog vcl.qt.widgets.dialoge.einfuegen.word_art_dialog
vcl.qt.widgets.dialoge.formatierung.objekt_format_panel vcl.qt.widgets.dialoge.formatierung.objektformat_panel_hilfen
vcl.qt.widgets.dialoge.formatierung.polster_dialog vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung_dialog
vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung_hilfen vcl.qt.widgets.dialoge.formatierung.rahmen_seite
vcl.qt.widgets.dialoge.formatierung.schattierung_seite vcl.qt.widgets.dialoge.formatierung.seiten_optionen_dialog
vcl.qt.widgets.dialoge.formatierung.texteffekt_panel vcl.qt.widgets.dialoge.ki.dokumente_panel vcl.qt.widgets.dialoge.ki.einwilligungen_panel
vcl.qt.widgets.dialoge.ki.ki_einstellungen_panels_hilfen vcl.qt.widgets.dialoge.ki.ki_modelle_dialoge_hilfen vcl.qt.widgets.dialoge.ki.mcp_dialog
vcl.qt.widgets.dialoge.ki.mcp_liste vcl.qt.widgets.dialoge.ki.modell_liste vcl.qt.widgets.dialoge.ki.modell_zuweisung
vcl.qt.widgets.dialoge.ki.sprache_panel vcl.qt.widgets.dialoge.ki.websuche_panel vcl.qt.widgets.dialoge.tabellen_eigenschaften_dialog
vcl.qt.widgets.dokumentansicht.ansicht.lineal_h vcl.qt.widgets.dokumentansicht.ansicht.lineal_hilfen vcl.qt.widgets.dokumentansicht.ansicht.lineal_v
vcl.qt.widgets.dokumentansicht.dokumentfenster.navigation_hilfen vcl.qt.widgets.dokumentansicht.dokumentfenster.navigation_panel
vcl.qt.widgets.dialoge.formatierung.umschlossen_dialog vcl.qt.widgets.bausteine.symbole.medien.bild_export vcl.qt.widgets.bausteine.symbole.medien.datei_symbole
vcl.qt.widgets.bausteine.symbole.medien.design_bildchen vcl.qt.widgets.bausteine.symbole.medien.seiten_bildchen vcl.qt.widgets.bausteine.symbole.piktogramme.piktogramme
vcl.qt.widgets.seitenleisten.vorlagen.formatvorlagen_bereich vcl.qt.widgets.seitenleisten.vorlagen.vorlagen_galerie vcl.qt.widgets.dialoge.dokument_dialoge
vcl.qt.widgets.dialoge.einfuegen.diagramm_fenster vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge
vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster vcl.qt.widgets.dialoge.einfuegen.formular_dialog
vcl.qt.widgets.dialoge.einfuegen.wasserzeichen_fenster vcl.qt.widgets.dialoge.ki.ki_aktions_dialoge
vcl.qt.widgets.dialoge.ki.ki_modelle_dialoge vcl.qt.widgets.dialoge.lesen_hilfe.hilfe_dialoge vcl.qt.widgets.dialoge.lesen_hilfe.silben_dialog
vcl.qt.widgets.dialoge.optionen_seiten.befehle vcl.qt.widgets.dialoge.optionen_seiten.datei vcl.qt.widgets.dialoge.optionen_seiten.gemeinsam
vcl.qt.widgets.dialoge.optionen_seiten.lesen vcl.qt.widgets.dialoge.optionen_seiten.lunivo vcl.qt.widgets.dokumentansicht.ansicht.blasen_bedienung
vcl.qt.widgets.dokumentansicht.ansicht.dokument_ansicht vcl.qt.widgets.dokumentansicht.ansicht.eingabe
vcl.qt.widgets.dokumentansicht.ansicht.objekt_bedienung vcl.qt.widgets.dokumentansicht.ansicht.vorschau_ansicht
vcl.qt.widgets.dokumentansicht.bearbeitung.freie_bilder_geometrie vcl.qt.widgets.dokumentansicht.bearbeitung.freie_bilder_knoepfe
vcl.qt.widgets.dokumentansicht.bearbeitung.freie_bilder_knoten vcl.qt.widgets.dokumentansicht.bearbeitung.freiform_bedienung
vcl.qt.widgets.dokumentansicht.bearbeitung.kern_befehle vcl.qt.widgets.dokumentansicht.bearbeitung.kern_editor
vcl.qt.widgets.dokumentansicht.bearbeitung.kern_objekte vcl.qt.widgets.dokumentansicht.bearbeitung.objekt_texteingabe
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
core.aenderungsverfolgung.vergleich.vergleich core.aenderungsverfolgung.vergleich.vergleich_datum_kern core.barrierefreiheit.barrierefreiheit
core.bearbeitung.einfuegen core.diagramme.daten.diagramm_teile core.diagramme.daten.diagramm_zusatz core.diagramme.diagramm
core.diagramme.formatierung.diagramm_format core.diagramme.formatierung.diagramm_stile core.diagramme.typen.diagramm_typen
core.dokument.abschnitte.deckblatt core.dokument.felder core.dokument.felder_ergebnis_kern core.dokument.felder_text_kern core.dokument.formular
core.dokument.gehe_zu core.dokument.je_stand core.dokument.vorlagen core.dokument.wasserzeichen.wasserzeichen core.dokument.zusatz
core.formatierung.absatz.absatzopt core.formatierung.effekte.texteffekt core.formatierung.fuellung.muster core.formatierung.fuellung.textur
core.formatierung.rahmen.seitenrahmen core.formatierung.schrift.schreibweise core.formatierung.schrift.silbenfarben
core.formatierung.schrift.zeichenzusatz core.formatvorlagen.zeichen.designs core.formatvorlagen.zeichen.stile core.korrektur.fund
core.korrektur.inkrement core.korrektur.korrektur_dienst core.korrektur.rechtschreibung.autokorrektur core.korrektur.rechtschreibung.pruefung
core.korrektur.silbentrennung.silben_de core.korrektur.sprache.klang core.korrektur.sprache.phonetik core.korrektur.woerterbuecher.haeufig
core.korrektur.woerterbuecher.vorhersage core.layout.seitenumbruch.seitenplan core.layout.seitenumbruch.seitenplatz core.objekte.basis.frei_objekt
core.objekte.bilder.modell.bilddaten core.objekte.bilder.modell.bildeffekte core.objekte.bilder.positionierung.bildlayout
core.objekte.bilder.positionierung.freie_bilder core.objekte.bilder.skalierung.bildwerkzeuge core.objekte.bilder.zuschneiden.bildzuschnitt
core.objekte.formen.formen core.objekte.formen.formen_anpassen core.objekte.formen.formen_katalog core.objekte.formen.formen_stile
core.objekte.formen.freiform core.objekte.formen.linie core.objekte.formen.sprechblasen core.objekte.smartart.smartart
core.objekte.smartart.smartart_zeichnen core.objekte.textfelder.modell.frei_objekt_text core.objekte.wordart.textfx
core.objekte.wordart.textfx_vorgaben core.objekte.wordart.textfx_zeichen core.tabellen.formatierung.tabellenstil core.tabellen.modell.tabelle_text
core.tabellen.modell.tabelleneigenschaften core.tabellen.modell.tabellenzustand core.text.ki_markdown core.text.statistik core.text.wortextras
core.text.zahlformat
core.objekte.bilder.modell.bild_einfuegen core.objekte.formeln.modell.formel_einfuegen core.objekte.formen.form_einfuegen core.objekte.wordart.wordart_einfuegen
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
