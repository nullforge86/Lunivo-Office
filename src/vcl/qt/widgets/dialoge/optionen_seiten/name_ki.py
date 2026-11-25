"""Optionen: Name und KI, dazu die Werkzeug-Fenster (Menüband, Schnellzugriff, Kennwort, Änderungen verfolgen)."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte

from vcl.qt.widgets.bausteine.skalierung.daten import text as _t

from vcl.qt.widgets.bausteine.zustaende.geruest.module import anmelden

from PySide6.QtWidgets import QDialog, QScrollArea

from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import knopfzeile
from vcl.qt.widgets.dialoge.optionen_seiten.gemeinsam import _Seite
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FENSTER_NAME_KI, RAND_DIALOG_KI


anmelden("optionen", "ki", "optionen.seite.ki", "_name_ki", 60)

class NameKiSeiten:
    """Optionen: Name und KI. Baustein von ``OptionenAnsicht`` (siehe ``vcl/qt/widgets/dialoge/optionen.py``)."""

    # Werkzeuge, die keine Einstellung sind: eigenes Fenster statt eigener Seite in der Liste
    FENSTER = {"menueband": (_t("optionen.name_ki.menueband_anpassen"), "_menueband"), "schnellzugriff": (_t("optionen.name_ki.symbolleiste_fuer_den_schnellzugriff"), "_schnellzugriff"),
               "sicherheit": (_t("optionen.name_ki.kennwort_und_datenschutz"), "_sicherheit"), "verfolgen": (_t("optionen.name_ki.aenderungen_verfolgen"), "_verfolgen")}


    def _name_ki(self, titel):
        p = _Seite(self.w, titel)
        f = p.gruppe(_t("optionen.name_ki.wer_schreibt"))
        f.addRow(_t("optionen.name_ki.name"), p.eingabe("benutzer/name", _t("optionen.name_ki.name_autor_in_docx_dokumenten")))
        f.addRow(_t("optionen.name_ki.initialen"), p.eingabe("benutzer/initialen", _t("optionen.name_ki.z_b_ks")))
        p.haken(f, "benutzer/verwenden", _t("optionen.name_ki.diese_benutzerinformationen_verwenden"), True)
        e = p.mehr(_t("optionen.name_ki.adresse_fuer_briefe_und_datenschutz"))
        f = p.unter(e, _t("optionen.name_ki.adresse"))
        p.felder(f, [("benutzer/strasse", _t("optionen.name_ki.strasse_und_hausnummer")), ("benutzer/plz_ort", _t("optionen.name_ki.plz_und_ort")), ("benutzer/ort", _t("optionen.name_ki.ort_fuer_ort_datum")),
                     ("benutzer/telefon", _t("optionen.name_ki.telefon")), ("benutzer/mail", _t("optionen.name_ki.e_mail"))])
        p.zeile(f, _t("optionen.name_ki.bleibt_auf_diesem_rechner_und_geht_nie_m"))
        p.haken(f, "sicherheit/personendaten_weg", _t("optionen.name_ki.beim_speichern_persoenliche_daten_entfer"), False)
        e = p.mehr(_t("optionen.name_ki.ki_einrichten_schluessel_modelle_verbrau"))
        e.innen.addWidget(self._ki(""))
        e = p.mehr(_t("optionen.name_ki.was_zusaetzlich_geholt_wurde"))
        e.innen.addWidget(self._erweitert(""))
        p.abschluss()
        return p


    def _anpassen(self, key: str) -> None:
        """Eines der Werkzeuge als Fenster zeigen; das Band wird danach neu gebaut, wenn es sich geändert hat."""
        from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import ausfuehren
        titel, bauer = self.FENSTER[key]
        d = QDialog(self)
        d.setWindowTitle(titel)
        d.resize(*GROESSE_FENSTER_NAME_KI)
        v = _spalte("fenster", d)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setFrameShape(QScrollArea.NoFrame)
        sc.setWidget(getattr(self, bauer)(""))
        v.addWidget(sc, 1)
        v.addWidget(knopfzeile(d, ok_text=_t("optionen.name_ki.fertig"), nur_ok=True))
        ausfuehren(d)
        self._band_jetzt()
