"""Übergangsliste: Module, die noch gegen die Richtungstabelle (``architektur.py``) verstoßen und noch nicht umgestellt sind.

Diese Liste darf nur kleiner werden, nie größer. Neue Dateien kommen nie auf die Liste (wie ``HTML_NOCH_ERLAUBT``). Ein Eintrag verschwindet,
sobald das Modul keinen Verstoß mehr hat. Ist sie leer, ist der Importwächter (``importe.py``) ohne Ausnahmen scharf."""
from __future__ import annotations

_NAMEN = """
core.editor.diagramme.diagramm core.editor.diagramme.diagramm_format core.editor.diagramme.diagramm_stile core.editor.diagramme.diagramm_teile
core.editor.dokument.einfuegen core.editor.dokument.felder core.editor.dokument.formular core.editor.objekte.bild.bilddaten
core.editor.objekte.bild.bildeffekte core.editor.objekte.bild.bildlayout core.editor.objekte.bild.bildwerkzeuge core.editor.objekte.bild.bildzuschnitt
core.editor.objekte.bild.freie_bilder core.editor.objekte.formen.formen core.editor.objekte.formen.formen_anpassen
core.editor.objekte.formen.formen_katalog core.editor.objekte.formen.formen_stile core.editor.objekte.formen.freiform core.editor.objekte.formen.linie
core.editor.objekte.formen.sprechblasen core.editor.objekte.frei.frei_objekt core.editor.objekte.frei.frei_objekt_text
core.editor.objekte.smartart.smartart core.editor.objekte.smartart.smartart_zeichnen core.editor.seite.deckblatt core.editor.seite.seitenrahmen
core.editor.seite.wasserzeichen core.editor.text.muster core.editor.text.schreibweise core.editor.text.silbenfarben core.editor.text.texteffekt
core.editor.text.textfx core.editor.text.textfx_vorgaben core.editor.text.textfx_zeichen core.editor.text.textur core.korrektur.barrierefreiheit
core.korrektur.korrektur_dienst core.schrift.datenbank framework.befehle_alt.befehlsliste framework.befehle_alt.hauptreiter.datei
framework.befehle_alt.hauptreiter.einfuegen framework.befehle_alt.hauptreiter.einfuegen_objekte framework.befehle_alt.hauptreiter.ki
framework.befehle_alt.hauptreiter.pruefen framework.befehle_alt.hauptreiter.seite framework.befehle_alt.hauptreiter.serien
framework.befehle_alt.hauptreiter.text_absatz framework.befehle_alt.hauptreiter.text_vorlagen framework.befehle_alt.hauptreiter.text_zeichen
framework.befehle_alt.hilfen framework.befehle_alt.kontextreiter.bildtools framework.befehle_alt.kontextreiter.diagrammtools
framework.befehle_alt.kontextreiter.formtools framework.befehle_alt.kontextreiter.kontext framework.befehle_alt.kontextreiter.tabellen
framework.befehle_alt.kontextreiter.tabellen_format framework.befehle_alt.kontextreiter.texttools framework.befehle_alt.kontextreiter.zeichentools
framework.dokumentverwaltung.ausgabe.bild_export framework.dokumentverwaltung.ausgabe.drucken framework.dokumentverwaltung.ausgabe.vektor_bilder
framework.ki.chat.ki_chat framework.ki.dienst.arbeitslauf framework.ki.dienst.ki_aktionen framework.ki.dienst.ki_anfragen
framework.ki.dienst.ki_dauerbetrieb framework.ki.dienst.ki_dienst vcl.qt.fenster.backstage.backstage_dokument
vcl.qt.fenster.backstage.backstage_fenster vcl.qt.fenster.backstage.backstage_objektformat vcl.qt.fenster.dateien.dateien_drucken
vcl.qt.fenster.dateien.dateien_export vcl.qt.fenster.dateien.dateien_oeffnen vcl.qt.fenster.dateien.dateien_speichern
vcl.qt.fenster.dateien.dateien_vorlagen vcl.qt.fenster.fenster.anwendung vcl.qt.fenster.fenster.bearbeiten vcl.qt.fenster.fenster.dokument_sync
vcl.qt.fenster.fenster.programmfenster vcl.qt.fenster.fenster.reiter_zustand vcl.qt.rendering.zeichnen.anzeige vcl.qt.rendering.zeichnen.geometrie
vcl.qt.rendering.zeichnen.pfad vcl.qt.rendering.zeichnen.rendering vcl.qt.widgets.bausteine.basis.linien vcl.qt.widgets.bausteine.bauteile.mini_leiste
vcl.qt.widgets.bausteine.bauteile.symbole vcl.qt.widgets.bausteine.chat.chat_blase vcl.qt.widgets.bausteine.chat.chat_eingabe
vcl.qt.widgets.bausteine.chat.chat_leerzustand vcl.qt.widgets.bausteine.chat.chat_regler vcl.qt.widgets.bausteine.diagramme.diagramm_format_bausteine
vcl.qt.widgets.bausteine.diagramme.diagramm_format_panel vcl.qt.widgets.bausteine.diagramme.diagramm_format_werte
vcl.qt.widgets.bausteine.diagramme.diagramm_text_panel vcl.qt.widgets.bausteine.diagramme.smartart_stil_kacheln
vcl.qt.widgets.bausteine.dokument.aenderungs_vorschau vcl.qt.widgets.bausteine.dokument.druck_dialog vcl.qt.widgets.bausteine.dokument.eingabe_fenster
vcl.qt.widgets.bausteine.dokument.layout_dialog vcl.qt.widgets.bausteine.dokument.liste_dialog vcl.qt.widgets.bausteine.dokument.pdf_export
vcl.qt.widgets.bausteine.dokument.sortieren_dialog vcl.qt.widgets.bausteine.dokument.tabstopp_dialog
vcl.qt.widgets.bausteine.dropdown.objektmenues.bild_diagramm_menues vcl.qt.widgets.bausteine.dropdown.objektmenues.diagramm_popups
vcl.qt.widgets.bausteine.dropdown.objektmenues.form_menues vcl.qt.widgets.bausteine.dropdown.objektmenues.fuell_voreinstellungen
vcl.qt.widgets.bausteine.dropdown.objektmenues.linien_voreinstellungen vcl.qt.widgets.bausteine.dropdown.objektmenues.objekt_menues
vcl.qt.widgets.bausteine.dropdown.objektmenues.smartart_menues vcl.qt.widgets.bausteine.dropdown.text_kopf_menue_mixin
vcl.qt.widgets.bausteine.felder.auswahl_bereich vcl.qt.widgets.bausteine.formatierung.absatz_dialog
vcl.qt.widgets.bausteine.formatierung.formatvorlage_dialog vcl.qt.widgets.bausteine.formatierung.objektformat_panel
vcl.qt.widgets.bausteine.formatierung.rahmen_schattierung vcl.qt.widgets.bausteine.formatierung.ruby_dialog
vcl.qt.widgets.bausteine.formatierung.schreibweise_dialog vcl.qt.widgets.bausteine.formatierung.schriftart_dialog
vcl.qt.widgets.bausteine.formatierung.text_format vcl.qt.widgets.bausteine.formatierung.text_fuellarten_mixin
vcl.qt.widgets.bausteine.formatierung.texteffekt_dialog vcl.qt.widgets.bausteine.formatierung.textfeld_abschnitt
vcl.qt.widgets.bausteine.formatierung.umschlossen_dialog vcl.qt.widgets.bausteine.medien.bild_export vcl.qt.widgets.bausteine.medien.datei_symbole
vcl.qt.widgets.bausteine.medien.design_bildchen vcl.qt.widgets.bausteine.medien.seiten_bildchen vcl.qt.widgets.bausteine.piktogramme.piktogramme
vcl.qt.widgets.bausteine.vorlagen.formatvorlagen_bereich vcl.qt.widgets.bausteine.vorlagen.vorlagen_galerie vcl.qt.widgets.dialoge.dokument_dialoge
vcl.qt.widgets.dialoge.einfuegen.diagramm_fenster vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge
vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster vcl.qt.widgets.dialoge.einfuegen.formular_dialog vcl.qt.widgets.dialoge.einfuegen.sonderzeichen
vcl.qt.widgets.dialoge.einfuegen.wasserzeichen_fenster vcl.qt.widgets.dialoge.ki.ki_aktions_dialoge vcl.qt.widgets.dialoge.ki.ki_einstellungen_panels
vcl.qt.widgets.dialoge.ki.ki_modelle_dialoge vcl.qt.widgets.dialoge.lesen_hilfe.hilfe_dialoge vcl.qt.widgets.dialoge.lesen_hilfe.silben_dialog
vcl.qt.widgets.dialoge.optionen_seiten.befehle vcl.qt.widgets.dialoge.optionen_seiten.datei vcl.qt.widgets.dialoge.optionen_seiten.gemeinsam
vcl.qt.widgets.dialoge.optionen_seiten.lesen vcl.qt.widgets.dialoge.optionen_seiten.lunivo vcl.qt.widgets.dokumentansicht.ansicht.blasen_bedienung
vcl.qt.widgets.dokumentansicht.ansicht.dokument_ansicht vcl.qt.widgets.dokumentansicht.ansicht.eingabe vcl.qt.widgets.dokumentansicht.ansicht.lineal
vcl.qt.widgets.dokumentansicht.ansicht.objekt_bedienung vcl.qt.widgets.dokumentansicht.ansicht.vorschau_ansicht
vcl.qt.widgets.dokumentansicht.bearbeitung.freie_bilder_geometrie vcl.qt.widgets.dokumentansicht.bearbeitung.freie_bilder_knoepfe
vcl.qt.widgets.dokumentansicht.bearbeitung.freie_bilder_knoten vcl.qt.widgets.dokumentansicht.bearbeitung.freiform_bedienung
vcl.qt.widgets.dokumentansicht.bearbeitung.kern_befehle vcl.qt.widgets.dokumentansicht.bearbeitung.kern_editor
vcl.qt.widgets.dokumentansicht.bearbeitung.kern_objekte vcl.qt.widgets.dokumentansicht.bearbeitung.objekt_texteingabe
vcl.qt.widgets.dokumentansicht.dokumentfenster.dokument_bereich vcl.qt.widgets.dokumentansicht.dokumentfenster.navigation
vcl.qt.widgets.dokumentansicht.dokumentfenster.suchen_feld vcl.qt.widgets.dokumentansicht.kopffuss.noten_feld vcl.qt.widgets.ribbon.band_gruppen
vcl.qt.widgets.ribbon.band_leiste vcl.qt.widgets.ribbon.band_stile vcl.qt.widgets.seitenleisten.panels.ki_panel
vcl.qt.widgets.seitenleisten.panels.schreib_panel vcl.qt.widgets.seitenleisten.seitenleiste vcl.rendering.zeichnen.pdf_ausgabe
writer.baukasten.basis.daten writer.baukasten.bauteile.symbole_hybrid
""".split()

NOCH_NICHT_UMGESTELLT: frozenset[str] = frozenset(_NAMEN)

# Die Übergangsliste der Darstellung (Bausteine, Farben, Maße, Schriften, Stile) steht beim Wächter selbst:
# ``writer/baukasten/pruefung/darstellung_waechter.py`` (``DARSTELLUNG_NOCH_NICHT_UMGESTELLT``, Datei → Anzahl; darf nur kleiner werden).

# Schnittstellen, die noch ``object`` oder fehlende Typangaben enthalten (die Editor-Fassade gibt dort noch Objekte des Kerns weiter). Auch diese Liste darf nur
# kleiner werden; sie ist leer, wenn das Farmwork die Dokumente selbst hält und nur eigene ``frozen``-Datentypen herausgibt.
NOCH_NICHT_UMGESTELLT_TYPEN: frozenset[str] = frozenset("framework.schnittstellen." + n for n in (
    "dokument", "seiten_port", "aenderungs_port", "vorschau"))
