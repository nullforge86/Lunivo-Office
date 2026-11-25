"""Übergangsliste: Module, die noch gegen die Richtungstabelle (``architektur.py``) verstoßen und noch nicht umgestellt sind.

Diese Liste darf nur kleiner werden, nie größer. Neue Dateien kommen nie auf die Liste (wie ``HTML_NOCH_ERLAUBT``). Ein Eintrag verschwindet,
sobald das Modul keinen Verstoß mehr hat. Ist sie leer, ist der Importwächter (``importe.py``) ohne Ausnahmen scharf."""
from __future__ import annotations

_NAMEN = """
dienste.bild_export dienste.drucken dienste.vektor_bilder
editor.diagramme.diagramm editor.diagramme.diagramm_format editor.diagramme.diagramm_stile editor.diagramme.diagramm_teile
editor.dokument.einfuegen editor.dokument.felder editor.dokument.formular editor.dokument.zusatz editor.objekte.bilddaten
editor.objekte.bildeffekte editor.objekte.bildlayout editor.objekte.bildwerkzeuge editor.objekte.bildzuschnitt editor.objekte.formen
editor.objekte.formen_anpassen editor.objekte.formen_katalog editor.objekte.formen_stile editor.objekte.frei_objekt
editor.objekte.frei_objekt_text editor.objekte.freie_bilder editor.objekte.freiform editor.objekte.linie editor.objekte.smartart
editor.objekte.smartart_zeichnen editor.objekte.sprechblasen editor.seite.deckblatt editor.seite.seitenrahmen
editor.seite.wasserzeichen editor.tabelle.tabellenstil editor.text.muster editor.text.schreibweise editor.text.silbenfarben
editor.text.texteffekt editor.text.textfx editor.text.textfx_vorgaben editor.text.textfx_zeichen editor.text.textur
farmwork.befehle_alt.befehlsliste
farmwork.befehle_alt.hauptreiter.datei farmwork.befehle_alt.hauptreiter.einfuegen farmwork.befehle_alt.hauptreiter.einfuegen_objekte
farmwork.befehle_alt.hauptreiter.ki farmwork.befehle_alt.hauptreiter.pruefen
farmwork.befehle_alt.hauptreiter.seite farmwork.befehle_alt.hauptreiter.serien farmwork.befehle_alt.hauptreiter.text_absatz
farmwork.befehle_alt.hauptreiter.text_vorlagen farmwork.befehle_alt.hauptreiter.text_zeichen
farmwork.befehle_alt.hilfen
farmwork.befehle_alt.kontextreiter.bildtools farmwork.befehle_alt.kontextreiter.diagrammtools farmwork.befehle_alt.kontextreiter.formtools
farmwork.befehle_alt.kontextreiter.kontext farmwork.befehle_alt.kontextreiter.tabellen farmwork.befehle_alt.kontextreiter.tabellen_format
farmwork.befehle_alt.kontextreiter.texttools farmwork.befehle_alt.kontextreiter.zeichentools
ki.arbeitslauf ki.ki_aktionen ki.ki_anfragen ki.ki_chat ki.ki_dauerbetrieb ki.ki_dienst
korrektur.barrierefreiheit korrektur.korrektur_dienst kern.dokument.seite kern.schrift.datenbank
oberflaeche.band.band_gruppen oberflaeche.band.band_leiste oberflaeche.band.band_stile
oberflaeche.baukasten.basis.daten oberflaeche.baukasten.basis.linien
oberflaeche.baukasten.chat.chat_blase oberflaeche.baukasten.chat.chat_eingabe oberflaeche.baukasten.chat.chat_leerzustand
oberflaeche.baukasten.chat.chat_regler oberflaeche.baukasten.diagramme.diagramm_format_bausteine
oberflaeche.baukasten.diagramme.diagramm_format_panel oberflaeche.baukasten.diagramme.diagramm_format_werte
oberflaeche.baukasten.diagramme.diagramm_text_panel oberflaeche.baukasten.diagramme.smartart_stil_kacheln
oberflaeche.baukasten.dokument.aenderungs_vorschau oberflaeche.baukasten.dokument.druck_dialog
oberflaeche.baukasten.dokument.eingabe_fenster oberflaeche.baukasten.dokument.layout_dialog oberflaeche.baukasten.dokument.liste_dialog
oberflaeche.baukasten.dokument.pdf_export oberflaeche.baukasten.dokument.sortieren_dialog oberflaeche.baukasten.dokument.tabstopp_dialog
oberflaeche.baukasten.dropdown.objektmenues.bild_diagramm_menues oberflaeche.baukasten.dropdown.objektmenues.diagramm_popups
oberflaeche.baukasten.dropdown.objektmenues.form_menues oberflaeche.baukasten.dropdown.objektmenues.fuell_voreinstellungen
oberflaeche.baukasten.dropdown.objektmenues.linien_voreinstellungen oberflaeche.baukasten.dropdown.objektmenues.objekt_menues
oberflaeche.baukasten.dropdown.objektmenues.smartart_menues oberflaeche.baukasten.dropdown.text_kopf_menue_mixin
oberflaeche.baukasten.felder.auswahl_bereich oberflaeche.baukasten.formatierung.absatz_dialog
oberflaeche.baukasten.formatierung.formatvorlage_dialog oberflaeche.baukasten.formatierung.objektformat_panel
oberflaeche.baukasten.formatierung.rahmen_schattierung oberflaeche.baukasten.formatierung.ruby_dialog
oberflaeche.baukasten.formatierung.schreibweise_dialog oberflaeche.baukasten.formatierung.schriftart_dialog
oberflaeche.baukasten.formatierung.text_format oberflaeche.baukasten.formatierung.text_fuellarten_mixin
oberflaeche.baukasten.formatierung.texteffekt_dialog oberflaeche.baukasten.formatierung.textfeld_abschnitt
oberflaeche.baukasten.formatierung.umschlossen_dialog oberflaeche.baukasten.medien.bild_export oberflaeche.baukasten.medien.datei_symbole
oberflaeche.baukasten.medien.design_bildchen oberflaeche.baukasten.medien.seiten_bildchen
oberflaeche.baukasten.piktogramme.piktogramme oberflaeche.baukasten.vorlagen.formatvorlagen_bereich
oberflaeche.baukasten.vorlagen.vorlagen_galerie oberflaeche.bauteile.mini_leiste oberflaeche.bauteile.symbole
oberflaeche.bauteile.symbole_hybrid oberflaeche.dialoge.dokument_dialoge oberflaeche.dialoge.einfuegen.diagramm_fenster
oberflaeche.dialoge.einfuegen.einfuegen_dialoge oberflaeche.dialoge.einfuegen.einfuegen_fenster
oberflaeche.dialoge.einfuegen.formular_dialog oberflaeche.dialoge.einfuegen.sonderzeichen
oberflaeche.dialoge.einfuegen.wasserzeichen_fenster oberflaeche.dialoge.ki.ki_aktions_dialoge
oberflaeche.dialoge.ki.ki_einstellungen_panels oberflaeche.dialoge.ki.ki_modelle_dialoge oberflaeche.dialoge.lesen_hilfe.hilfe_dialoge
oberflaeche.dialoge.lesen_hilfe.silben_dialog oberflaeche.dialoge.optionen_seiten.befehle oberflaeche.dialoge.optionen_seiten.datei
oberflaeche.dialoge.optionen_seiten.gemeinsam oberflaeche.dialoge.optionen_seiten.lesen oberflaeche.dialoge.optionen_seiten.lunivo
oberflaeche.dokument.ansicht.blasen_bedienung oberflaeche.dokument.ansicht.dokument_ansicht oberflaeche.dokument.ansicht.eingabe
oberflaeche.dokument.ansicht.lineal oberflaeche.dokument.ansicht.objekt_bedienung oberflaeche.dokument.ansicht.vorschau_ansicht
oberflaeche.dokument.bearbeitung.freie_bilder_geometrie oberflaeche.dokument.bearbeitung.freie_bilder_knoepfe
oberflaeche.dokument.bearbeitung.freie_bilder_knoten oberflaeche.dokument.bearbeitung.freiform_bedienung
oberflaeche.dokument.bearbeitung.kern_befehle oberflaeche.dokument.bearbeitung.kern_editor oberflaeche.dokument.bearbeitung.kern_objekte
oberflaeche.dokument.bearbeitung.objekt_texteingabe oberflaeche.dokument.dokumentfenster.dokument_bereich
oberflaeche.dokument.dokumentfenster.navigation oberflaeche.dokument.dokumentfenster.suchen_feld oberflaeche.dokument.kopffuss.noten_feld
oberflaeche.hauptfenster.backstage_dokument oberflaeche.hauptfenster.backstage_fenster oberflaeche.hauptfenster.backstage_objektformat
oberflaeche.hauptfenster.bearbeiten oberflaeche.hauptfenster.dateien_drucken oberflaeche.hauptfenster.dateien_export
oberflaeche.hauptfenster.dateien_oeffnen oberflaeche.hauptfenster.dateien_speichern oberflaeche.hauptfenster.dateien_vorlagen
oberflaeche.hauptfenster.anwendung oberflaeche.hauptfenster.dokument_sync oberflaeche.hauptfenster.programmfenster oberflaeche.hauptfenster.reiter_zustand
oberflaeche.seitenleiste.panels.ki_panel oberflaeche.seitenleiste.panels.schreib_panel oberflaeche.seitenleiste.seitenleiste
oberflaeche.zeichnen.anzeige oberflaeche.zeichnen.geometrie oberflaeche.zeichnen.pdf_ausgabe oberflaeche.zeichnen.pfad
oberflaeche.zeichnen.rendering
""".split()

NOCH_NICHT_UMGESTELLT: frozenset[str] = frozenset("lunivo_writer." + n for n in _NAMEN)

# Schnittstellen, die noch ``object`` oder fehlende Typangaben enthalten (die Editor-Fassade gibt dort noch Objekte des Kerns weiter). Auch diese Liste darf nur
# kleiner werden; sie ist leer, wenn das Farmwork die Dokumente selbst hält und nur eigene ``frozen``-Datentypen herausgibt.
NOCH_NICHT_UMGESTELLT_TYPEN: frozenset[str] = frozenset("lunivo_writer.farmwork.schnittstellen." + n for n in (
    "dokument", "seiten_port", "aenderungs_port", "vorschau"))
