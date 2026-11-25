"""Navigation hilfen: aus ``vcl.qt.widgets.dokumentansicht.dokumentfenster.navigation`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.farben.darstellung import eigenschaft, stufe_mit_farbe
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte
import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPlainTextEdit, QWidget
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil
from vcl.qt.widgets.bausteine.farben.karte import als_karte
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_label
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_STUFE, HOEHE_TEXT_NORMAL


SEITEN = ("suche", "kommentare", "ueberschriften", "aenderungen", "noten", "vorlesen")


def _datum(iso: str) -> str:
    try:
        return datetime.datetime.fromisoformat(iso).astimezone().strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return iso or ""


class KommentarKarte(QFrame):
    """Ein Kommentar: Verfasser, Datum, Text und Zeigen / Bearbeiten / Gelöst / Löschen; beim Bearbeiten steht der Text in einem Eingabefeld."""

    def __init__(self, b: dict, k: dict, ed, aktualisieren, pt: float = 11.5, bearbeiten: bool = False, speichern=None, abbrechen=None, bearbeite_los=None):
        super().__init__()
        from writer.anbindung.zusatz import kommentar_farbe
        self.setObjectName("kommentarKarte")
        geloest = bool(k.get("geloest"))
        farbe = kommentar_farbe(geloest)                                  # orange Kreis wie in der alten Fassung, gelöste grau
        als_karte(self, "kompakt")
        v = _spalte("panel", self)
        kopf = _reihe("inhalt")
        ini = QLabel((k.get("initialen") or (k.get("autor") or "?")[:1]).upper()[:2]); ini.setAlignment(Qt.AlignCenter); ini.setFixedSize(*GROESSE_STUFE)
        stufe_mit_farbe(ini, farbe)
        kopf.addWidget(ini)
        name = QLabel(k.get("autor", "?")); f = name.font(); f.setBold(True); f.setPointSizeF(pt); name.setFont(f)
        kopf.addWidget(name, 1)
        datum = hinweis_label(_datum(k.get("datum", "")), umbruch=False); fd = datum.font(); fd.setPointSizeF(max(8.0, pt - 3)); datum.setFont(fd)
        kopf.addWidget(datum)
        v.addLayout(kopf)
        kid = int(b["wert"])
        self.kid = kid
        if bearbeiten:
            self.eingabe = QPlainTextEdit(k.get("text", "")); self.eingabe.setMinimumHeight(HOEHE_TEXT_NORMAL)
            fe = self.eingabe.font(); fe.setPointSizeF(pt); self.eingabe.setFont(fe)
            v.addWidget(self.eingabe)
            z = _reihe("standard")
            ok = knopf("standard", "Speichern", aktion=lambda: speichern(kid, self.eingabe.toPlainText().strip()))
            ab = knopf("standard", "Abbrechen", aktion=lambda: abbrechen())
            z.addWidget(ok); z.addWidget(ab); z.addStretch(1)
            v.addLayout(z)
            return
        text = QLabel(k.get("text", "")); text.setWordWrap(True); text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        ft = text.font(); ft.setPointSizeF(pt); text.setFont(ft)
        if geloest:
            hinweis_stil(text, zusatz="text-decoration: line-through;")
        v.addWidget(text)
        feld = QWidget(); z = _reihe("standard", feld)                  # eine Zeile, die Knöpfe knapp geschnitten
        eigenschaft(feld, rolle="kompaktleiste")
        zeigen = knopf("standard", "Zeigen", aktion=lambda: (ed.select_range(b["von"], b["bis"]), ed.ensureCursorVisible(), ed.setFocus()))
        bearb = knopf("standard", "Bearbeiten", aktion=lambda: bearbeite_los(kid))
        loesen = knopf("standard", "Wieder öffnen" if geloest else "Gelöst", aktion=lambda: (ed.kommentar_geloest(kid, not geloest), aktualisieren()))
        weg = knopf("standard", "Löschen", aktion=lambda: (ed.kommentar_loeschen(kid), aktualisieren()))
        for b_ in (zeigen, bearb, loesen, weg):
            z.addWidget(b_)
        z.addStretch(1)
        v.addWidget(feld)
