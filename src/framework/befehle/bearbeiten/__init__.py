"""Tür des Pakets ``framework.befehle.bearbeiten``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "Angabe": ("vorlagenkatalog", "Angabe"),
    "Barrierebefund": ("abfragen", "Barrierebefund"),
    "BearbeitenBefehle": ("befehle", "BearbeitenBefehle"),
    "ELEMENTE": ("gehe_zu", "ELEMENTE"),
    "Katalogwert": ("formatvorlagen", "Katalogwert"),
    "MENUE": ("wortextras", "MENUE"),
    "Tabstopp": ("formatvorlagen", "Tabstopp"),
    "abfragen_aehnlich_formatiert": ("abfragen", "aehnlich_formatiert"),
    "abfragen_barrierefreiheit_befund": ("abfragen", "barrierefreiheit_befund"),
    "abfragen_objekte_nach_stelle": ("abfragen", "objekte_nach_stelle"),
    "abfragen_objektliste": ("abfragen", "objektliste"),
    "abfragen_rohtext": ("abfragen", "rohtext"),
    "abfragen_seitenzahl_setzen": ("abfragen", "seitenzahl_setzen"),
    "abfragen_seitenzahl_vorgabe_setzen": ("abfragen", "seitenzahl_vorgabe_setzen"),
    "abfragen_seitenzahlen_entfernen": ("abfragen", "seitenzahlen_entfernen"),
    "abfragen_silbentrennung_verfuegbar": ("abfragen", "silbentrennung_verfuegbar"),
    "abfragen_tab_abstand": ("abfragen", "tab_abstand"),
    "abfragen_tabellen_ohne_rahmen": ("abfragen", "tabellen_ohne_rahmen"),
    "abfragen_tabellenstellen": ("abfragen", "tabellenstellen"),
    "abfragen_toc_optionen": ("abfragen", "toc_optionen"),
    "abfragen_ueberschriften": ("abfragen", "ueberschriften"),
    "abfragen_ueberschriftsebene_an_marke": ("abfragen", "ueberschriftsebene_an_marke"),
    "abfragen_vorlesetext": ("abfragen", "vorlesetext"),
    "aendern": ("vorlagenkatalog", "aendern"),
    "als_json": ("vorlagenkatalog", "als_json"),
    "als_json_neu": ("vorlagenkatalog", "als_json_neu"),
    "anlegen": ("vorlagenkatalog", "anlegen"),
    "baustein_einfuegen": ("bausteine", "baustein_einfuegen"),
    "baustein_entfernen": ("bausteine", "baustein_entfernen"),
    "baustein_fuer_kuerzel": ("bausteine", "baustein_fuer_kuerzel"),
    "baustein_merken": ("bausteine", "baustein_merken"),
    "bausteine_eigene": ("bausteine", "bausteine_eigene"),
    "bausteine_standard": ("bausteine", "bausteine_standard"),
    "definition": ("vorlagenkatalog", "definition"),
    "design": ("vorlagenkatalog", "design"),
    "design_namen": ("vorlagenkatalog", "design_namen"),
    "effekte": ("vorlagenkatalog", "effekte"),
    "eigene_angaben": ("vorlagenkatalog", "eigene_angaben"),
    "eingabe_titel": ("gehe_zu", "eingabe_titel"),
    "eingebaute_namen": ("vorlagenkatalog", "eingebaute_namen"),
    "ergebnisse_ergebnis_einsetzen": ("ergebnisse", "ergebnis_einsetzen"),
    "ergebnisse_ergebnis_verwerfen": ("ergebnisse", "ergebnis_verwerfen"),
    "ergebnisse_fassung_laden": ("ergebnisse", "fassung_laden"),
    "ergebnisse_serienbrief_erzeugen": ("ergebnisse", "serienbrief_erzeugen"),
    "ergebnisse_serienbrief_gruppen": ("ergebnisse", "serienbrief_gruppen"),
    "ergebnisse_serienbriefe_speichern": ("ergebnisse", "serienbriefe_speichern"),
    "ergebnisse_texte_des_dokuments": ("ergebnisse", "texte_des_dokuments"),
    "ergebnisse_vergleichen": ("ergebnisse", "vergleichen"),
    "ergebnisse_zusammenfuehren": ("ergebnisse", "zusammenfuehren"),
    "farbschemen": ("vorlagenkatalog", "farbschemen"),
    "formatvorlage_abgleichen": ("formatvorlagen", "formatvorlage_abgleichen"),
    "formatvorlage_anwenden": ("formatvorlagen", "formatvorlage_anwenden"),
    "formatvorlage_aus_auswahl": ("formatvorlagen", "formatvorlage_aus_auswahl"),
    "fremdtext_datei_einfuegen": ("fremdtext", "datei_einfuegen"),
    "fremdtext_datei_laden": ("fremdtext", "datei_laden"),
    "fremdtext_datei_verwerfen": ("fremdtext", "datei_verwerfen"),
    "gehe_zu_element": ("gehe_zu", "gehe_zu_element"),
    "hat_elemente": ("gehe_zu", "hat_elemente"),
    "ist_eigen": ("vorlagenkatalog", "ist_eigen"),
    "laden": ("vorlagenkatalog", "laden"),
    "laden_neu": ("vorlagenkatalog", "laden_neu"),
    "listen_liste_setzen": ("listen", "liste_setzen"),
    "listen_liste_spec": ("listen", "liste_spec"),
    "loeschen": ("vorlagenkatalog", "loeschen"),
    "namen": ("vorlagenkatalog", "namen"),
    "pruefe_name": ("vorlagenkatalog", "pruefe_name"),
    "schriftpaare": ("vorlagenkatalog", "schriftpaare"),
    "Suchangabe": ("suche", "Suchangabe"),
    "suche_absaetze": ("suche", "absaetze"),
    "suche_alle_ersetzen": ("suche", "alle_ersetzen"),
    "suche_ersatz_text": ("suche", "ersatz_text"),
    "suche_gueltig": ("suche", "gueltig"),
    "suche_naechster": ("suche", "naechster"),
    "suche_treffer": ("suche", "treffer"),
    "suche_zeichenformate": ("suche", "zeichenformate"),
    "stellen_absatz_formatwert": ("stellen", "absatz_formatwert"),
    "stellen_absatz_laenge": ("stellen", "absatz_laenge"),
    "stellen_absatz_schriftgroesse": ("stellen", "absatz_schriftgroesse"),
    "stellen_absatzformat_von": ("stellen", "absatzformat_von"),
    "stellen_alles_auswaehlen": ("stellen", "alles_auswaehlen"),
    "stellen_ausschnitt_einsetzen": ("stellen", "ausschnitt_einsetzen"),
    "stellen_ausschnitt_gueltig": ("stellen", "ausschnitt_gueltig"),
    "stellen_ausschnitt_kopieren": ("stellen", "ausschnitt_kopieren"),
    "stellen_auswahl": ("stellen", "auswahl"),
    "stellen_auswahl_setzen": ("stellen", "auswahl_setzen"),
    "stellen_bereich": ("stellen", "bereich"),
    "stellen_gehen": ("stellen", "gehen"),
    "stellen_geruest_schreiben": ("stellen", "geruest_schreiben"),
    "stellen_lauf_format_bei": ("stellen", "lauf_format_bei"),
    "stellen_objekt_vorhanden": ("stellen", "objekt_vorhanden"),
    "stellen_sichtbare_zellen": ("stellen", "sichtbare_zellen"),
    "stellen_stelle_im_text": ("stellen", "stelle_im_text"),
    "stellen_stelle_von": ("stellen", "stelle_von"),
    "stellen_tabelle_teilen": ("stellen", "tabelle_teilen"),
    "stellen_tabellenmasse": ("stellen", "tabellenmasse"),
    "stellen_tabellenzellen": ("stellen", "tabellenzellen"),
    "stellen_wirksames_absatzformat": ("stellen", "wirksames_absatzformat"),
    "stellen_wirksames_zeichenformat": ("stellen", "wirksames_zeichenformat"),
    "stellen_zeichenformat_bei": ("stellen", "zeichenformat_bei"),
    "stellen_zelle_anfang": ("stellen", "zelle_anfang"),
    "tabs_als_text": ("formatvorlagen", "tabs_als_text"),
    "tabs_aus_text": ("formatvorlagen", "tabs_aus_text"),
    "ueberschrift_farbe": ("vorlagenkatalog", "ueberschrift_farbe"),
    "vorlage": ("vorlagenkatalog", "vorlage"),
    "wortextra_ausfuehren": ("wortextras", "wortextra_ausfuehren"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "abfragen":
        from . import abfragen as _datei
    elif datei == "bausteine":
        from . import bausteine as _datei
    elif datei == "befehle":
        from . import befehle as _datei
    elif datei == "formatvorlagen":
        from . import formatvorlagen as _datei
    elif datei == "gehe_zu":
        from . import gehe_zu as _datei
    elif datei == "ergebnisse":
        from . import ergebnisse as _datei
    elif datei == "fremdtext":
        from . import fremdtext as _datei
    elif datei == "listen":
        from . import listen as _datei
    elif datei == "stellen":
        from . import stellen as _datei
    elif datei == "suche":
        from . import suche as _datei
    elif datei == "vorlagenkatalog":
        from . import vorlagenkatalog as _datei
    elif datei == "wortextras":
        from . import wortextras as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
