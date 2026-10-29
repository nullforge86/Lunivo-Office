#!/usr/bin/env python3
"""Klickt die Seitenleiste „Formatierung“ automatisch durch, wie ein Tester es von Hand täte, und schreibt auf, was wirklich passiert.

    .venv/bin/python werkzeug/seitenleistenpruefung.py [--panel diagramm|objekt] [--teile titel,legende,...] [--arten saeule,linie,kreis]
                                                       [--limit 300] [--behalten ORDNER] [--ziel docs/seitenleistenstand.md]

Läuft ohne Bildschirm (QT_QPA_PLATFORM=offscreen). Ein Dokument mit einem Diagramm (Säulen: 3 Reihen, 4 Rubriken) wird angelegt; dann wird
nacheinander jeder wählbare Teil (``diagrammTeilWaehlen``) gewählt, das Panel geöffnet und für jeden Teil jeder Haupt- und Icon-Reiter angewählt,
jeder Abschnitt aufgeklappt und jedes Steuerelement bedient (gefunden über die Qt-Widget-Struktur, nie über Pixelkoordinaten): Auswahlpunkte und Haken
werden umgeschaltet, Auswahllisten und Voreinstellungsmenüs Eintrag für Eintrag gewählt, Regler und Zahlfelder auf Minimum, Maximum und Mitte gestellt,
Farbfelder auf eine Testfarbe, Textfelder mit Testtext gefüllt. Vor jedem Steuerelement wird das Format des Teils zurückgesetzt. Nach der Bedienung wird gemessen:

  Datenwert   hat sich der gespeicherte Wert geändert (``teil_format``, ``elemente``, ``fx``, Größe, Drehung …)
  Bild        hat sich das gezeichnete Bild des Objekts geändert (Pixelvergleich)
  Rundweg     liest das Panel den Wert beim erneuten Befüllen (wie beim Teilwechsel) wieder zurück
  Fehler      kam ein Python-Fehler

Ergebnis je Steuerelement:

  wirkt              Wert gespeichert und Bild verändert
  nur Daten          Wert gespeichert, Bild unverändert (bei Teilen, die nicht sichtbar sind, kann das in Ordnung sein)
  keine Wirkung      weder Wert noch Bild haben sich geändert
  liest nicht zurück gespeichert, aber das Panel zeigt den Wert nach dem erneuten Befüllen nicht mehr
  Fehler             Python-Fehler beim Bedienen (mit Zeile)
  übersprungen       verborgen, deaktiviert oder Zeitlimit (Grund steht dabei)

Zeitlimits: je Steuerelement 5 s, je Teil 60 s, insgesamt ``--limit`` Sekunden; danach wird der Bericht mit dem bis dahin Geprüften geschrieben. Hängt Qt
selbst (ein Aufruf kehrt nie zurück), schreibt ein Wächter-Faden den Bericht und beendet das Programm. Aufgehende Dialoge und Menüs werden geschlossen
(``pruefhilfen.DialogWaechter``, derselbe wie in ``funktionspruefung.py``). Die Bilder (Panel je Teil und Reiter, Diagramm davor/danach bei sichtbarer
Wirkung) liegen in einem temporären Ordner, der am Ende gelöscht wird; mit ``--behalten ORDNER`` bleiben sie, und der Bericht nennt die Dateien.

Neues Panel = ein Eintrag in ``PANELS`` (Klasse mit denselben Methoden wie ``DiagrammAnbindung``).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import time
import traceback

from pruefhilfen import (WURZEL, DialogWaechter, app_starten, fenster_bauen, fenster_schliessen, md_tabelle, md_zelle)  # noqa: E402  (setzt auch Pfad und Umgebung)

from PySide6.QtCore import QEventLoop, QRect, Qt, QTimer  # noqa: E402
from PySide6.QtGui import QColor, QImage  # noqa: E402
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QLabel, QLineEdit, QPlainTextEdit,  # noqa: E402
                               QMenu, QPushButton, QRadioButton, QScrollArea, QWidgetAction, QSlider, QSpinBox, QTextEdit, QToolButton, QWidget)

from lunivo_writer.ui.baukasten.mass_feld import EinheitFeld  # noqa: E402
from lunivo_writer.ui.baukasten.farbpalette import FarbFeld  # noqa: E402
from lunivo_writer.ui.baukasten.schiebe_feld import SchiebeFeld, SchrittFeld  # noqa: E402
from lunivo_writer.ui.baukasten.texteffekt_dialog import Abschnitt  # noqa: E402

LIMIT_ELEMENT, LIMIT_TEIL = 5.0, 60.0
TESTFARBE = "#12ab34"
TESTTEXT = "Testtext ÄÖÜ 123"
URTEILE = ("wirkt", "nur Daten", "keine Wirkung", "liest nicht zurück", "Fehler", "übersprungen")
MAX_FOTOS = 220                                              # so viele Bilddateien höchstens bei --behalten (der Eigentümer hat wenig Platz)
BREITE_PANEL, BREITE_BILD = 300, 640

DIAGRAMM_DATEN = {
    "saeule": {"art": "saeule_gruppiert", "titel": "Umsatz", "kategorien": ["Q1", "Q2", "Q3", "Q4"],
               "reihen": {"Nord": [12, 18, 9, 15], "Süd": [8, 14, 17, 11], "West": [15, 7, 12, 19]}},
    "linie": {"art": "linie_punkte", "titel": "Verlauf", "kategorien": ["Q1", "Q2", "Q3", "Q4"],
              "reihen": {"Nord": [12, 18, 9, 15], "Süd": [8, 14, 17, 11], "West": [15, 7, 12, 19]}},
    "kreis": {"art": "kreis", "titel": "Anteile", "kategorien": ["Q1", "Q2", "Q3", "Q4"], "reihen": {"Nord": [12, 18, 9, 15]}},
}
# Reihenfolge der Teile: erst je ein Vertreter jeder Sorte, dann die übrigen gleichartigen (Reihe 2, 3, Legendeneinträge …)
TEIL_RANG = ["diagrammbereich", "titel", "legende", "achse_vertikal", "achse_horizontal", "reihe_0", "zeichnungsbereich", "datenbeschriftung", "legendeneintrag_0"]


class Zeitlimit(BaseException):
    """Ein Zeitlimit ist abgelaufen (Steuerelement, Teil oder Gesamtlauf)."""

    def __init__(self, ebene: str):
        super().__init__(ebene)
        self.ebene = ebene


# ---- Zeit und Wächter --------------------------------------------------------------------------------------------------------------------
class Uhr:
    """Die drei Zeitlimits. ``pruefen()`` wird zwischen den Einzelschritten aufgerufen und wirft ``Zeitlimit``."""

    def __init__(self, gesamt: float):
        self.start = time.monotonic()
        self.gesamt = gesamt
        self.teil_ab = self.element_ab = self.start
        self.herzschlag = self.start                       # letzte Rückmeldung für den Wächter-Faden
        self.aktuell = "Start"

    def vergangen(self) -> float:
        return time.monotonic() - self.start

    def pruefen(self) -> None:
        jetzt = time.monotonic()
        self.herzschlag = jetzt
        if jetzt - self.start > self.gesamt:
            raise Zeitlimit("gesamt")
        if jetzt - self.teil_ab > LIMIT_TEIL:
            raise Zeitlimit("teil")
        if jetzt - self.element_ab > LIMIT_ELEMENT:
            raise Zeitlimit("element")


def warte(ms: int) -> None:
    schleife = QEventLoop(); QTimer.singleShot(ms, schleife.quit); schleife.exec()


def ereignisse(n: int = 3) -> None:
    for _ in range(n):
        QApplication.instance().processEvents()


# ---- Anbindung: Panel → Öffner, Teile, Messpunkte -------------------------------------------------------------------------------------
class Anbindung:
    """Was das Werkzeug von einem Panel wissen muss. Neue Panels erben und füllen die Methoden."""
    name = "?"

    def __init__(self, w, arten: list[str]):
        self.w, self.arten = w, arten
        self.panel = None
        self.teil = None

    @property
    def ed(self):
        return self.w.current_editor()

    # ---- Aufbau: eine Liste (Gruppe, Teile) — je Gruppe ein eigenes Dokument
    def gruppen(self) -> list[tuple[str, str]]:
        raise NotImplementedError

    def aufbauen(self, gruppe: str) -> list[tuple[str, str]]:           # → [(Schlüssel, Name)]
        raise NotImplementedError

    def waehlen(self, schluessel: str) -> None:                         # Teil wählen und Panel öffnen
        raise NotImplementedError

    def neu_laden(self) -> None:                                        # das Panel aus dem Modell füllen (wie beim Teilwechsel)
        raise NotImplementedError

    def zuruecksetzen(self) -> None:
        raise NotImplementedError

    def momentaufnahme(self) -> str:                                    # alle Datenwerte als Text
        raise NotImplementedError

    def objekt_rechteck(self):                                          # QRectF des Objekts im Editor
        z = [x for x in self.ed._frei_liste() if x[0] == self.ed._frei_sel]
        return z[0][3] if z else None

    def bild(self) -> QImage:
        """Das gezeichnete Objekt, so wie es im Editor steht (mit Effekten außerhalb des Bildes)."""
        r = self.objekt_rechteck()
        if r is None:
            return QImage()
        rr = r.toAlignedRect().adjusted(-24, -24, 24, 24).intersected(self.ed.viewport().rect())
        return self.ed.viewport().grab(QRect(rr)).toImage()

    def hauptreiter(self):
        """[(Name, Knopf, IconReiter)] — die Hauptreiter des Panels mit ihren Icon-Reitern."""
        p = self.panel
        return [(k.text().replace("\n", " "), k, r) for k, r in zip(p.umschalter.buttons(), (p.reiter, p.text_panel.reiter))]

    def haupt_waehlen(self, i: int) -> None:
        self.panel.optionen_waehlen(i)


def _json(x) -> str:
    return json.dumps(x, sort_keys=True, default=str, ensure_ascii=False)


class DiagrammAnbindung(Anbindung):
    name = "diagramm"

    def gruppen(self):
        return [(a, {"saeule": "Säulendiagramm", "linie": "Liniendiagramm", "kreis": "Kreisdiagramm"}[a]) for a in self.arten]

    def aufbauen(self, gruppe: str):
        from lunivo_writer.editor import diagramm as D
        from lunivo_writer.editor import frei_objekt as FO
        ed = self.ed
        ed.clear()
        self.daten0 = dict(DIAGRAMM_DATEN[gruppe])
        FO.einfuegen(ed, "diagramm", dict(self.daten0), 400, 260)
        self.w._sync_format()
        ereignisse()
        z = FO.ziel(ed)
        self.b0, self.h0 = float(z[3]["b"]), float(z[3]["h"])
        return D.teile(FO.daten_lesen(ed, "diagramm"))

    def waehlen(self, schluessel: str) -> None:
        self.teil = schluessel
        self.w.befehle.diagrammTeilWaehlen(None, schluessel)
        if self.panel is None or not self.panel.isVisible():
            self.w.diagrammformat_seitenleiste()
            self.panel = self.w.sidebar.diagramm_panel
        else:
            self.w.diagrammformat_folgen()
        self.neu_laden()

    def neu_laden(self) -> None:
        werte = self.w._diagramm_werte(self.ed)
        if werte is not None:
            self.panel.setze(werte)
        ereignisse()

    def zuruecksetzen(self) -> None:
        from lunivo_writer.editor import bildlayout as BL
        from lunivo_writer.editor import frei_objekt as FO
        w, ed = self.w, self.ed
        w.befehle.diagrammZuruecksetzen()
        FO.aendern(ed, "diagramm", breite=self.b0, hoehe=self.h0, alt_titel=None, alt_beschreibung=None)
        BL.frei_aendern(ed, BL.ziel(ed), dreh=0.0)
        w.befehle.diagrammTeilWaehlen(None, self.teil)
        self.neu_laden()

    def momentaufnahme(self) -> str:
        from lunivo_writer.editor import frei_objekt as FO
        z = FO.ziel(self.ed)
        if z is None:
            return ""
        a = z[3]
        daten = {k: v for k, v in z[1].items() if k != "teil"}
        return _json({"daten": daten, "fx": a.get("fx"), "b": round(float(a["b"]), 2), "h": round(float(a["h"]), 2), "dreh": a.get("dreh", 0)})

    def bild_roh(self) -> QImage:
        from lunivo_writer.editor import frei_objekt as FO
        z = FO.ziel(self.ed)
        return z[4] if z is not None else QImage()


class ObjektAnbindung(Anbindung):
    """Objektformat (Seitenleiste „Formatierung“ für ein freies Bild und eine Form): ``--panel objekt``."""
    name = "objekt"

    def gruppen(self):
        return [("form", "Form"), ("bild", "Freies Bild")]

    def aufbauen(self, gruppe: str):
        from lunivo_writer.editor import frei_objekt as FO
        ed = self.ed
        ed.clear()
        if gruppe == "form":
            FO.einfuegen(ed, "form", {"form": "Raute", "fuell": "#4a8fd8", "linie": "#1f3864", "strich": 2.0, "text": ""}, 200, 140)
        else:
            img = QImage(160, 100, QImage.Format_ARGB32); img.fill(QColor("#e8a33d"))
            FO.bild_einfuegen(ed, img, 160, 100)
        self.w._sync_format()
        ereignisse()
        from lunivo_writer.editor import bildlayout as BL
        self.a0 = json.loads(_json({k: v for k, v in BL.ziel(ed)[2].items() if k in ("fuell", "rand", "fx", "dreh")}))
        return [(gruppe, "Form" if gruppe == "form" else "Freies Bild")]

    def waehlen(self, schluessel: str) -> None:
        self.teil = schluessel
        self.w.objektformat_seitenleiste()
        self.panel = self.w.sidebar.objekt_panel
        self.neu_laden()

    def neu_laden(self) -> None:
        from lunivo_writer.editor import bildlayout as BL
        werte = BL.format_lesen(self.ed, BL.ziel(self.ed))
        if werte is not None:
            self.panel.setze(werte)
        ereignisse()

    def zuruecksetzen(self) -> None:
        from lunivo_writer.editor import bildlayout as BL
        BL.frei_aendern(self.ed, BL.ziel(self.ed), **{k: None for k in ("fuell", "rand", "fx")}, dreh=0)
        BL.frei_aendern(self.ed, BL.ziel(self.ed), **{k: v for k, v in self.a0.items() if v is not None})
        self.neu_laden()

    def momentaufnahme(self) -> str:
        from lunivo_writer.editor import bildlayout as BL
        z = BL.ziel(self.ed)
        a = z[2] if z and z[0] == "frei" else {}
        return _json({k: a.get(k) for k in ("fuell", "rand", "fx", "dreh")})

    def bild_roh(self) -> QImage:
        from lunivo_writer.editor import bildlayout as BL
        z = BL.ziel(self.ed)
        return z[3] if z and z[0] == "frei" else QImage()


PANELS = {"diagramm": DiagrammAnbindung, "objekt": ObjektAnbindung}


# ---- Steuerelemente finden und bedienen -----------------------------------------------------------------------------------------------
_VERBUND = (SchiebeFeld, SchrittFeld, EinheitFeld, QComboBox, QAbstractSpinBox, QPlainTextEdit, QTextEdit)


SIG: list = [None]                                             # die Messfunktion des Prüfers (für Vorbereitungen, die eine Änderung brauchen)
FANG: list = []                                                # Menüs, die ein Knopf aufklappen wollte (``QMenu.exec`` ist unten umgebogen)


def _menue_fangen(selbst, *args, **kw):
    """Statt ein Menü modal zu zeigen (das Programm stünde still), merkt sich das Werkzeug es und bedient seine Einträge selbst."""
    FANG.append(selbst)
    return None


def _menues_umbiegen() -> None:
    """``QMenu.exec`` lässt sich bei Shiboken nicht für alle Unterklassen umbiegen; die Python-Unterklassen der Oberfläche einzeln."""
    from lunivo_writer.ui.baukasten.farbpalette import FarbPalette
    from lunivo_writer.ui.baukasten.voreinstellung_menue import VoreinstellungMenue
    for k in (VoreinstellungMenue, FarbPalette):
        k.exec = _menue_fangen


_menues_umbiegen()


class Element:
    """Ein bedienbares Steuerelement mit seinen Schritten und einer Lesefunktion. ``nach`` (optional) liefert nach dem ersten Schritt weitere Schritte
    (die Einträge eines Menüs, das der erste Klick aufgeklappt hat)."""

    def __init__(self, widget: QWidget, art: str, name: str, abschnitt: str, schritte: list, lesen, vorbereiten=None, warten: int = 0):
        self.widget, self.art, self.name, self.abschnitt = widget, art, name, abschnitt
        self.schritte, self.lesen, self.vorbereiten, self.warten = schritte, lesen, vorbereiten, warten
        self.nach = None


def _stichprobe(werte: list, n: int = 7) -> list:
    if len(werte) <= n:
        return werte
    return [werte[round(i * (len(werte) - 1) / (n - 1))] for i in range(n)]


def _drei(lo: float, hi: float) -> list[float]:
    """Minimum, Mitte, Maximum; bei Winkelbereichen (360° und mehr) auch ein Viertel, denn 0°, 180° und 360° sehen gleich aus."""
    werte = {lo, hi, (lo + hi) / 2}
    if hi - lo >= 360:
        werte.add(lo + (hi - lo) / 4)
    return sorted(werte)


def namen_sammeln(*eigner) -> dict[int, str]:
    """Attributname jedes Widgets im Panel (zum Benennen im Bericht), auch aus Listen und Wörterbüchern."""
    out: dict[int, str] = {}
    for o in eigner:
        for k, v in vars(o).items():
            if isinstance(v, QWidget):
                out.setdefault(id(v), k)
                if type(v).__module__.startswith("lunivo_writer") is False:
                    continue
                for kk, vv in vars(v).items():                  # zusammengesetzte Felder (Haken + Zahl): auch ihre Teile benennen
                    try:
                        if isinstance(vv, QWidget) and vv is not v and vv.parentWidget() is v:
                            out.setdefault(id(vv), f"{k}.{kk}")
                    except RuntimeError:                      # das Qt-Objekt dahinter ist schon gelöscht
                        pass
            elif isinstance(v, dict):
                for kk, vv in v.items():
                    if isinstance(vv, QWidget):
                        out.setdefault(id(vv), f"{k}[{kk}]")
            elif isinstance(v, (list, tuple)):
                for i, vv in enumerate(v):
                    if isinstance(vv, QWidget):
                        out.setdefault(id(vv), f"{k}[{i}]")
    return out


def _abschnitt_von(x: QWidget) -> str:
    p = x.parentWidget()
    while p is not None:
        if isinstance(p, Abschnitt):
            return p.knopf.text().capitalize()
        p = p.parentWidget()
    return ""


def _im_verbund(x: QWidget, seite: QWidget) -> bool:
    p = x.parentWidget()
    while p is not None and p is not seite:
        if isinstance(p, _VERBUND) or isinstance(p, FarbFeld):
            return True
        p = p.parentWidget()
    return False


def elemente_finden(seite: QWidget, namen: dict[int, str]) -> tuple[list[Element], list[tuple[str, str]]]:
    """Alle Steuerelemente einer Seite. → (bedienbare Elemente, [(Name, Grund)] der verborgenen oder deaktivierten)."""
    etiketten = {id(l.buddy()): l.text().rstrip(":") for l in seite.findChildren(QLabel) if l.buddy() is not None}
    elemente: list[Element] = []
    uebersprungen: list[tuple[str, str]] = []
    gesehen: set[int] = set()
    for x in seite.findChildren(QWidget):
        if id(x) in gesehen or _im_verbund(x, seite):
            continue
        art = None
        if isinstance(x, SchiebeFeld):
            art = "Regler"
        elif isinstance(x, SchrittFeld):
            art = "Zahlfeld"
        elif isinstance(x, EinheitFeld):
            art = "Maßfeld"
        elif isinstance(x, FarbFeld):
            art = "Farbfeld"
        elif isinstance(x, QRadioButton):
            art = "Auswahlpunkt"
        elif isinstance(x, QCheckBox):
            art = "Haken"
        elif isinstance(x, QComboBox):
            art = "Auswahlliste"
        elif isinstance(x, (QSpinBox, QDoubleSpinBox)):
            art = "Zahlfeld"
        elif isinstance(x, QLineEdit):
            art = "Textfeld"
        elif isinstance(x, QPlainTextEdit):
            art = "Textfeld (mehrzeilig)"
        elif isinstance(x, QSlider):
            art = "Regler"
        elif isinstance(x, (QToolButton, QPushButton)):
            if isinstance(x.parentWidget(), Abschnitt) and x.parentWidget().knopf is x:
                continue
            art = "Knopf"
        if art is None:
            continue
        gesehen.add(id(x))
        attr = namen.get(id(x), type(x).__name__)
        text = (x.text() if hasattr(x, "text") and not isinstance(x, (QLineEdit, QPlainTextEdit)) else "") or etiketten.get(id(x), "")
        name = f"{attr} ({text.strip()[:30]})" if text.strip() and text.strip() != attr else attr
        name = name.replace("\n", " ")
        unbenannt = id(x) not in namen and art != "Knopf"
        if unbenannt:
            name += " [ohne Attributnamen: vielleicht von einem gleichnamigen Attribut überdeckt]"
        if not x.isVisibleTo(seite):
            uebersprungen.append((name, "verborgen")); continue
        # eine Zahl, die erst nach „Auto“ bedienbar ist (Minimum/Maximum/Intervall): zuerst den Haken wegnehmen
        vorb = None
        if not x.isEnabled():
            p = x.parentWidget()
            auto = getattr(p, "auto", None)
            if isinstance(auto, QCheckBox):
                vorb = lambda a=auto: a.setChecked(False)
            else:
                uebersprungen.append((name, "deaktiviert")); continue
        e = _element(x, art, name, _abschnitt_von(x), vorb)
        if e is None:
            uebersprungen.append((name, "nicht bedienbar (Art unbekannt)")); continue
        elemente.append(e)
    return elemente, uebersprungen


def _element(x: QWidget, art: str, name: str, abschnitt: str, vorb) -> Element | None:
    E = lambda schritte, lesen, **kw: Element(x, art, name, abschnitt, schritte, lesen, vorb, **kw)
    if isinstance(x, QRadioButton):
        def vorbereiten():
            if vorb:
                vorb()
            if x.isChecked():                                  # schon gewählt: zuerst einen Nachbarn wählen, der etwas ändert, damit das Wählen eine Änderung ist
                vor = SIG[0]()[0] if SIG[0] else None
                for r in x.parentWidget().findChildren(QRadioButton):
                    if r is x or not r.isEnabled() or not r.isVisibleTo(x.parentWidget()):
                        continue
                    r.click(); ereignisse()
                    if SIG[0] is None or SIG[0]()[0] != vor:
                        break
        return Element(x, art, name, abschnitt, [("wählen", x.click)], x.isChecked, vorbereiten)
    if isinstance(x, QCheckBox):
        return E([("an/aus", x.click), ("zurück", x.click)], x.isChecked)
    if isinstance(x, QComboBox):
        n = x.count()
        if n == 0:
            return None
        idx = [i for i in _stichprobe(list(range(n))) if i != x.currentIndex()] or [0]
        return E([(f"Eintrag {x.itemText(i)[:24]!r}", (lambda i=i: x.setCurrentIndex(i))) for i in idx], x.currentIndex)
    if isinstance(x, SchiebeFeld):
        lo, hi = x.regler.minimum(), x.regler.maximum()
        return E([(f"{v / x._f:g}", (lambda v=v: x.regler.setValue(int(v)))) for v in _drei(lo, hi)], x.value)
    if isinstance(x, SchrittFeld):
        return E([(f"{v:g}", (lambda v=v: x.feld.setValue(v))) for v in _drei(x.feld.minimum(), x.feld.maximum())], x.value)
    if isinstance(x, EinheitFeld):
        return E([(f"{v:g}", (lambda v=v: x.zahl.setValue(v))) for v in _drei(x.zahl.minimum(), x.zahl.maximum())], x.value)
    if isinstance(x, (QSpinBox, QDoubleSpinBox)):
        return E([(f"{v:g}", (lambda v=v: x.setValue(v))) for v in _drei(x.minimum(), x.maximum())], x.value)
    if isinstance(x, QSlider):
        return E([(f"{v:g}", (lambda v=v: x.setValue(int(v)))) for v in _drei(x.minimum(), x.maximum())], x.value)
    if isinstance(x, FarbFeld):
        return E([(TESTFARBE, lambda: x._uebernehmen(QColor(TESTFARBE)))], lambda: x.farbe)
    if isinstance(x, QLineEdit):
        return E([("Testtext", lambda: x.setText(TESTTEXT))], x.text, warten=550)
    if isinstance(x, QPlainTextEdit):
        return E([("Testtext", lambda: x.setPlainText(TESTTEXT + "\nzweite Zeile"))], x.toPlainText, warten=550)
    if isinstance(x, (QToolButton, QPushButton)):
        menue = x.menu()
        if menue is not None:
            akt = [a for a in menue.actions() if not a.isSeparator() and a.isEnabled() and a.text().strip() and a.menu() is None]
            if not akt:
                return None
            return E([(f"Eintrag {a.text().replace('&', '')[:24]!r}", a.trigger) for a in _stichprobe(akt, 8)], lambda: None)
        if x.isCheckable():
            return E([("an/aus", x.click), ("zurück", x.click)], x.isChecked)
        def klick():
            FANG.clear(); x.click()

        def nach():
            if not FANG:
                return None
            m = FANG[-1]
            eintraege = [(f"Eintrag {a.text().replace('&', '')[:24]!r}", a.trigger) for a in m.actions()
                         if not a.isSeparator() and a.isEnabled() and a.text().strip() and a.menu() is None]
            for a in m.actions():                                  # Voreinstellungsmenü: die Kacheln liegen in einem Widget
                if isinstance(a, QWidgetAction) and a.defaultWidget() is not None:
                    eintraege += [(f"Kachel {(k.toolTip() or k.text())[:24]!r}", k.click) for k in a.defaultWidget().findChildren(QToolButton) if k.isEnabled()]
            return _stichprobe(eintraege, 9)
        el = E([("klicken", klick)], lambda: None)
        el.nach = nach
        return el
    return None


def gleich(a, b) -> bool:
    if isinstance(a, float) or isinstance(b, float):
        try:
            return abs(float(a) - float(b)) < 1e-6 or abs((float(a) - float(b)) % 360.0) < 1e-6      # 360° und 0° sind derselbe Winkel
        except (TypeError, ValueError):
            pass
    return a == b


# ---- Der Prüfer --------------------------------------------------------------------------------------------------------------------------
class Pruefer:
    def __init__(self, tmp: str, panel: str, arten: list[str], nur_teile: set[str], gesamt: float, behalten: str | None):
        self.tmp = tmp
        self.uhr = Uhr(gesamt)
        self.waechter = DialogWaechter(); self.waechter.starten()
        self.fehler_log: list[str] = []
        SIG[0] = self.signatur
        sys.excepthook = lambda t, v, tb: self.fehler_log.append(self._ort(t, v, tb))
        self.w = fenster_bauen(tmp)
        self.an = PANELS[panel](self.w, arten)
        self.nur_teile = nur_teile
        self.fotos = behalten
        self.foto_zahl = 0
        self.zeilen: list[dict] = []                       # je Steuerelement
        self.seiten: list[dict] = []                       # je Teil und Reiter: Foto, verborgene Elemente
        self.teile_log: list[dict] = []                    # je Teil: Name, Zeit, Zahl, Abbruchgrund
        self.abbruch = ""                                  # Grund, falls der Lauf vorzeitig endete
        self.schmutzig = False
        self.laufend = ""                                  # was gerade geprüft wird (für den Wächter-Faden)

    @staticmethod
    def _ort(t, v, tb) -> str:
        zeile = ""
        for f in reversed(traceback.extract_tb(tb)):
            zeile = f"{os.path.basename(f.filename)}:{f.lineno}"
            if "lunivo_writer" in f.filename:
                break
        return f"{t.__name__}: {v} ({zeile})"

    # ---- Fotos
    def foto(self, bild: QImage, name: str, breite: int) -> str:
        if not self.fotos or bild.isNull() or self.foto_zahl >= MAX_FOTOS:
            return ""
        if bild.width() > breite:
            bild = bild.scaledToWidth(breite, mode=Qt.SmoothTransformation)
        pfad = os.path.join(self.fotos, name)
        bild.save(pfad, "PNG")
        self.foto_zahl += 1
        return name

    # ---- Messung
    @staticmethod
    def _hash(img: QImage) -> str:
        if img.isNull():
            return ""
        img = img.convertToFormat(QImage.Format_ARGB32)
        return hashlib.md5(bytes(img.constBits())).hexdigest()

    def signatur(self) -> tuple[str, str, str]:
        an = self.an
        return (an.momentaufnahme(), self._hash(an.bild()), self._hash(an.bild_roh()))

    def element_pruefen(self, e: Element, teil: str, haupt: str, reiter: str, nr: str) -> dict:
        an = self.an
        z = {"teil": teil, "haupt": haupt, "reiter": reiter, "abschnitt": e.abschnitt, "name": e.name, "art": e.art, "urteil": "", "hinweis": "", "foto": ""}
        self.uhr.element_ab = time.monotonic()
        n_fehler = len(self.fehler_log)
        n_fenster = len(self.waechter.fenster_log)
        daten = bild = mit_menue = False
        schritte = list(e.schritte)
        daten_schritte, bild_schritte = [], []
        fehler = ""
        vorher_bild = nachher_bild = QImage()
        try:
            if self.schmutzig:                               # Daten verändert: Format zurücksetzen; sonst genügt es, das Panel neu zu füllen
                an.zuruecksetzen()
            else:                                            # (das Steuerelement kann seinen Zustand ohne Datenänderung verstellt haben)
                an.neu_laden()
            self.schmutzig = False
            if e.vorbereiten is not None:
                e.vorbereiten(); ereignisse(); self.uhr.pruefen()
            sig = self.signatur()
            vorher_bild = an.bild()
            schritte = list(e.schritte)
            nr_s = 0
            while nr_s < len(schritte):
                beschr, fn = schritte[nr_s]
                nr_s += 1
                self.uhr.pruefen()
                try:
                    fn()
                except Exception as ex:                    # noqa: BLE001
                    fehler = f"{type(ex).__name__}: {ex} ({self._ort(type(ex), ex, ex.__traceback__).rsplit('(', 1)[-1]}"
                    break
                ereignisse()
                if nr_s == 1 and e.nach is not None:
                    try:
                        extra = e.nach()
                    except Exception as ex:                # noqa: BLE001
                        extra = None; fehler = f"{type(ex).__name__}: {ex}"
                    if extra:
                        schritte += extra
                        mit_menue = True
                if e.warten:
                    warte(e.warten)
                neu = self.signatur()
                if neu[0] != sig[0]:
                    daten = True; daten_schritte.append(beschr)
                if neu[1] != sig[1] or neu[2] != sig[2]:
                    bild = True; bild_schritte.append(beschr)
                    if nachher_bild.isNull():
                        nachher_bild = an.bild()
                if neu[0] != sig[0]:
                    self.schmutzig = True
                sig = neu
            if len(self.fehler_log) > n_fehler and not fehler:
                fehler = self.fehler_log[-1]
            # Rundweg: der Wert, den das Steuerelement jetzt zeigt, muss nach dem erneuten Befüllen derselbe sein
            rund_ok = True
            if daten and not fehler:
                v1 = e.lesen()
                an.neu_laden()
                v2 = e.lesen()
                rund_ok = gleich(v1, v2)
                if not rund_ok:
                    z["hinweis"] = f"zeigt {v1!r}, nach erneutem Befüllen {v2!r}"
        except Zeitlimit as t:
            if t.ebene != "element":
                raise
            z["urteil"] = "übersprungen"; z["hinweis"] = f"Zeitlimit {LIMIT_ELEMENT:g} s je Steuerelement"
            self.schmutzig = True
            return z
        if self.waechter.fenster_log[n_fenster:]:
            z["hinweis"] = (z["hinweis"] + "; " if z["hinweis"] else "") + "Fenster: " + "; ".join(self.waechter.fenster_log[n_fenster:])[:100]
        if fehler:
            z["urteil"] = "Fehler"; z["hinweis"] = fehler[:200]
        elif daten and not rund_ok:
            z["urteil"] = "liest nicht zurück"
        elif daten and bild:
            z["urteil"] = "wirkt"
        elif daten:
            z["urteil"] = "nur Daten"
        elif bild:
            z["urteil"] = "wirkt"; z["hinweis"] = (z["hinweis"] + "; " if z["hinweis"] else "") + "Bild ohne Datenänderung"
        else:
            z["urteil"] = "keine Wirkung"
        zu_pruefen = schritte[1:] if mit_menue else schritte
        if len(zu_pruefen) > 1 and z["urteil"] in ("wirkt", "nur Daten", "liest nicht zurück") and len([b for b in daten_schritte if b in {x for x, _f in zu_pruefen}]) < len(zu_pruefen):
            fehlt = [b for b, _f in zu_pruefen if b not in daten_schritte]
            z["hinweis"] = (z["hinweis"] + "; " if z["hinweis"] else "") + f"{len(zu_pruefen) - len(fehlt)} von {len(zu_pruefen)} Einträgen/Schritten ändern den Wert (ohne: {', '.join(fehlt)[:80]})"
        if bild and not vorher_bild.isNull():
            ids = f"{nr}"
            a = self.foto(vorher_bild, f"{ids}_davor.png", BREITE_BILD)
            b = self.foto(nachher_bild, f"{ids}_danach.png", BREITE_BILD)
            z["foto"] = f"{a}, {b}" if a and b else ""
        return z

    # ---- Durchgang
    def expandieren(self, seite: QWidget) -> None:
        for a in seite.findChildren(Abschnitt):
            if a.isVisibleTo(seite) and not a.knopf.isChecked():
                a.knopf.setChecked(True)
        ereignisse()

    def teil_pruefen(self, schluessel: str, name: str, gruppe: str) -> None:
        an = self.an
        an.waehlen(schluessel)
        self.schmutzig = False
        panel = an.panel
        namen = namen_sammeln(panel, panel.text_panel)
        tk = f"{gruppe}_{schluessel}"
        for hnr, (hname, hknopf, reiter) in enumerate(an.hauptreiter()):
            hname = re.sub(r"\s+", " ", hname.strip().title())
            if not hknopf.isEnabled():
                self.seiten.append({"teil": name, "haupt": hname, "reiter": "", "info": "Hauptreiter deaktiviert", "foto": "", "uebersprungen": []})
                continue
            an.haupt_waehlen(hnr)
            ereignisse()
            for i in range(reiter.count()):
                self.uhr.pruefen()
                rk = reiter.tabKnopf(i)
                rname = re.sub(r"\s+", " ", rk.text().replace("\n", " ")).strip().title()
                if not rk.isVisibleTo(reiter):
                    self.seiten.append({"teil": name, "haupt": hname, "reiter": rname, "info": "Reiter für diesen Teil nicht sichtbar", "foto": "", "uebersprungen": []})
                    continue
                reiter.setCurrentIndex(i)
                seite = reiter.widget(i)
                self.expandieren(seite)
                ereignisse()
                self.laufend = f"{name} ▸ {hname} ▸ {rname}"
                foto = self.foto(panel.grab().toImage(), f"{tk}_{hname}_{rname}_panel.png".replace(" ", "-"), BREITE_PANEL)
                elemente, uebersprungen = elemente_finden(seite, namen)
                self.seiten.append({"teil": name, "haupt": hname, "reiter": rname, "info": "", "foto": foto, "uebersprungen": uebersprungen, "anzahl": len(elemente)})
                for k, e in enumerate(elemente):
                    self.uhr.pruefen()
                    self.laufend = f"{name} ▸ {hname} ▸ {rname} ▸ {e.name}"
                    nr = re.sub(r"[^A-Za-z0-9_-]", "", f"{tk}_{hname}_{rname}_{k}".replace(" ", "-"))
                    z = self.element_pruefen(e, name, hname, rname, nr)
                    if z["urteil"] in ("keine Wirkung", "liest nicht zurück"):
                        andere = [o for o in elemente if o is not e and o.abschnitt == e.abschnitt and o.art in ("Regler", "Zahlfeld", "Maßfeld")]
                        if andere:
                            erst = z["urteil"]
                            alt_vorb = e.vorbereiten
                            e.vorbereiten = lambda alt_vorb=alt_vorb, andere=andere: ((alt_vorb or (lambda: None))(), [o.schritte[-1][1]() for o in andere], ereignisse())
                            z2 = self.element_pruefen(e, name, hname, rname, nr)
                            e.vorbereiten = alt_vorb
                            if z2["urteil"] in ("wirkt", "nur Daten"):
                                z2["hinweis"] = (z2["hinweis"] + "; " if z2["hinweis"] else "") + f"erst mit Vorbedingung wirksam (andere Regler des Abschnitts auf Maximum); allein: {erst}"
                                z = z2
                    self.zeilen.append(z)
                    # nach einem Teilwechsel/Neuaufbau durch das Steuerelement: Reiter wieder dort, wo er war
                    if not seite.isVisible() and reiter.currentIndex() != i:
                        reiter.setCurrentIndex(i)
                if self.schmutzig:                              # Seite zu Ende: das Format zurücksetzen, damit die nächste frisch beginnt
                    an.zuruecksetzen(); self.schmutzig = False
                    ereignisse()

    def durchgehen(self, panel_name: str) -> None:
        an = self.an
        ersten = True
        for gruppe, gname in an.gruppen():
            teile = an.aufbauen(gruppe)
            wahl = [t for t in teile if not self.nur_teile or t[0] in self.nur_teile or t[1] in self.nur_teile]
            wahl.sort(key=lambda t: (TEIL_RANG.index(t[0]) if t[0] in TEIL_RANG else len(TEIL_RANG), t[0]) if an.name == "diagramm" else (0, t[0]))
            fehlend = [t for t in self.nur_teile if t not in {x[0] for x in teile} | {x[1] for x in teile}]
            if fehlend and not wahl:
                self.teile_log.append({"gruppe": gname, "teil": ", ".join(fehlend), "info": "in dieser Diagrammart nicht vorhanden", "zeit": 0, "n": 0})
            for schluessel, name in wahl:
                self.uhr.teil_ab = time.monotonic()
                n0, t0 = len(self.zeilen), time.monotonic()
                info = ""
                try:
                    an.aufbauen(gruppe)                            # frisches Diagramm je Teil: die Bildressourcen des Dokuments wachsen sonst mit jeder Änderung
                    self.teil_pruefen(schluessel, f"{gname} ▸ {name}", gruppe)
                except Zeitlimit as t:
                    if t.ebene == "gesamt":
                        info = "Gesamtlimit erreicht"
                        self.teile_log.append({"gruppe": gname, "teil": name, "info": info, "zeit": time.monotonic() - t0, "n": len(self.zeilen) - n0})
                        self.abbruch = f"Gesamtlimit von {self.uhr.gesamt:g} s erreicht (Teil „{name}“ unvollständig; weitere Teile nicht geprüft)"
                        self._log_teil(gname, name, t0, n0, info)
                        return
                    info = f"Teilimit {LIMIT_TEIL:g} s erreicht" if t.ebene == "teil" else f"Zeitlimit ({t.ebene})"
                self.schmutzig = True
                if len(self.teile_log) == 0 or self.teile_log[-1].get("teil") != name or self.teile_log[-1].get("gruppe") != gname:
                    self._log_teil(gname, name, t0, n0, info)
                try:
                    self.an.zuruecksetzen(); self.schmutzig = False
                except Exception:                              # noqa: BLE001
                    pass
            ersten = False

    def _log_teil(self, gname: str, name: str, t0: float, n0: int, info: str) -> None:
        e = self.zeilen[n0:]
        z = {u: sum(1 for x in e if x["urteil"] == u) for u in URTEILE}
        self.teile_log.append({"gruppe": gname, "teil": name, "info": info, "zeit": time.monotonic() - t0, "n": len(e), "z": z})
        print(f"{gname} ▸ {name}: {len(e)} Steuerelemente in {time.monotonic() - t0:.1f} s — "
              f"wirkt {z['wirkt']}, nur Daten {z['nur Daten']}, keine Wirkung {z['keine Wirkung']}, liest nicht zurück {z['liest nicht zurück']}, Fehler {z['Fehler']}, "
              f"übersprungen {z['übersprungen']}" + (f" [{info}]" if info else ""), flush=True)


# ---- Bericht --------------------------------------------------------------------------------------------------------------------------
def bericht(p: Pruefer, panel: str, dauer: float, behalten: str | None, unvollstaendig: str = "") -> str:
    alle = p.zeilen
    zaehl = {u: sum(1 for z in alle if z["urteil"] == u) for u in URTEILE}
    verborgen = sum(len(s.get("uebersprungen", [])) for s in p.seiten)
    t = [f"# Stand der Seitenleiste „Formatierung“ ({panel})", "",
         "Geschrieben von `werkzeug/seitenleistenpruefung.py`: jedes Steuerelement jedes Reiters jedes Teils wird bedient; danach wird gemessen, ob sich der "
         "Datenwert geändert hat, ob sich das gezeichnete Bild geändert hat und ob das Panel den Wert beim erneuten Befüllen zurückliest. Vor jedem Steuerelement "
         "wird das Format zurückgesetzt. Bei „nur Daten“ kann es in Ordnung sein, wenn der Teil im Bild nicht zu sehen ist.", "",
         f"Lauf: {dauer:.0f} s, {len(alle)} Steuerelemente bedient, {verborgen} verborgen oder deaktiviert (nur gemeldet)."]
    if p.abbruch or unvollstaendig:
        t += ["", f"**Unvollständig:** {p.abbruch or unvollstaendig}"]
    t += ["", "## Zusammenfassung", ""] + md_tabelle(["Ergebnis", "Anzahl"], [[u, n] for u, n in zaehl.items()]) + [""]
    probleme = [z for z in alle if z["urteil"] in ("Fehler", "liest nicht zurück", "keine Wirkung")]
    t += ["## Problemfälle", ""]
    if not probleme:
        t += ["Keine.", ""]
    for u in ("Fehler", "liest nicht zurück", "keine Wirkung"):
        sub = [z for z in probleme if z["urteil"] == u]
        if not sub:
            continue
        t += [f"### {u} ({len(sub)})", ""]
        # gleiche Steuerelemente in gleichartigen Teilen (Reihe 1/2/3) zusammenfassen
        gruppen: dict[tuple, list[str]] = {}
        for z in sub:
            gruppen.setdefault((z["haupt"], z["reiter"], z["name"], z["hinweis"]), []).append(z["teil"])
        for (h, r, n, hw), teile in gruppen.items():
            kurz = teile[0] if len(teile) == 1 else f"{teile[0]} und {len(teile) - 1} weitere Teile"
            t.append(f"- {kurz} ▸ {h} ▸ {r} ▸ {n}" + (f" — {hw}" if hw else ""))
        t.append("")
    t += ["## Teile", ""] + md_tabelle(["Teil", "Steuerelemente", "Zeit", "wirkt", "nur Daten", "keine Wirkung", "liest nicht zurück", "Fehler", "übersprungen", "Hinweis"],
                                      [[x["gruppe"] + " ▸ " + x["teil"], x["n"], f"{x['zeit']:.0f} s"] + [x.get("z", {}).get(u, "") for u in URTEILE[:6]] + [x["info"]]
                                       for x in p.teile_log if x["n"] or x["info"]]) + [""]
    t += ["## Alles im Einzelnen", "",
          "Ein Steuerelement je Zeile; steht beim Ergebnis nur ein Wort, gilt es für alle geprüften Teile, sonst steht dahinter, für welche Teile welches Ergebnis gilt.", ""]
    teile_alle = list(dict.fromkeys(z["teil"] for z in alle))

    def kurz(teil: str) -> str:
        return teil.split(" ▸ ", 1)[-1] if len({x.split(" ▸ ", 1)[0] for x in teile_alle}) == 1 else teil.replace("diagramm ▸ ", ": ").replace(" ▸ ", ": ")
    zeilen: dict[tuple, dict] = {}
    for z in alle:
        k = (z["haupt"], z["reiter"], z["abschnitt"], re.sub(r" \[ohne Attributnamen.*$", "", z["name"]), z["art"])
        e = zeilen.setdefault(k, {"u": {}, "h": [], "unbenannt": "[ohne Attributnamen" in z["name"]})
        e["u"].setdefault(z["urteil"], []).append(z["teil"])
        if z["hinweis"] and z["hinweis"] not in e["h"]:
            e["h"].append(z["hinweis"])
    tab = []
    for (haupt, reiter, abschnitt, name, art), e in zeilen.items():
        if len(e["u"]) == 1:
            u, ts = next(iter(e["u"].items()))
            erg = u if len(ts) == len(teile_alle) else f"{u}: " + ", ".join(kurz(x) for x in ts)
        else:
            erg = "; ".join(f"{u}: " + ", ".join(kurz(x) for x in ts) for u, ts in e["u"].items())
        hinweis = " · ".join(e["h"][:2]) + (" · ohne Attributnamen (vielleicht überdeckt)" if e["unbenannt"] else "")
        tab.append([f"{haupt} ▸ {reiter}", abschnitt, name, art, erg, hinweis])
    t += md_tabelle(["Reiter", "Abschnitt", "Steuerelement", "Art", "Ergebnis", "Hinweis"], tab) + [""]
    # verborgene, deaktivierte und fehlende Reiter: je Reiter einmal
    ue: dict[tuple, dict] = {}
    for sx in p.seiten:
        e = ue.setdefault((sx["haupt"], sx["reiter"]), {"info": set(), "skip": {}, "teile": 0})
        e["teile"] += 1
        if sx.get("info"):
            e["info"].add(sx["info"])
        for n, g in sx.get("uebersprungen", []):
            e["skip"].setdefault(f"{n} ({g})", 0)
            e["skip"][f"{n} ({g})"] += 1
    notiz = []
    for (haupt, reiter), e in ue.items():
        if e["info"] or e["skip"]:
            notiz.append(f"- {haupt} ▸ {reiter}: " + "; ".join(sorted(e["info"]) + (["nicht bedient: " + ", ".join(f"{n}" for n in e["skip"])] if e["skip"] else [])))
    if notiz:
        t += ["### Nicht bedient (verborgen, deaktiviert oder Reiter nicht vorhanden)", ""] + notiz + [""]
    if behalten:
        t += ["### Bilder", ""] + [f"- {sx['teil']} ▸ {sx['haupt']} ▸ {sx['reiter']}: `{sx['foto']}`" for sx in p.seiten if sx.get("foto")]
        t += [f"- {z['teil']} ▸ {z['name']}: `{z['foto']}` (Objekt davor, danach)" for z in alle if z["foto"]]
        t += ["", f"Bilder liegen in `{behalten}` ({p.foto_zahl} Dateien).", ""]
    return "\n".join(t)


def bericht_schreiben(p: Pruefer, panel: str, ziel: str, behalten: str | None, unvollstaendig: str = "") -> str:
    text = bericht(p, panel, p.uhr.vergangen(), behalten, unvollstaendig)
    os.makedirs(os.path.dirname(os.path.abspath(ziel)), exist_ok=True)
    with open(ziel, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    return text


def waechter_faden(p: Pruefer, panel: str, ziel: str, behalten: str | None, bilder_dir: str | None, loeschen: bool) -> threading.Thread:
    """Hängt Qt (kein Herzschlag seit 20 s), schreibt dieser Faden den Bericht und beendet das Programm hart."""
    def lauf():
        while True:
            time.sleep(1.0)
            seit = time.monotonic() - p.uhr.herzschlag
            if seit > LIMIT_ELEMENT + 15 or p.uhr.vergangen() > p.uhr.gesamt + 40:
                grund = f"Qt hat seit {seit:.0f} s nicht geantwortet bei „{p.laufend}“ (Lauf abgebrochen)"
                if p.uhr.vergangen() > p.uhr.gesamt + 40:
                    grund = f"Gesamtlimit überschritten, Qt kehrte nicht zurück bei „{p.laufend}“"
                p.zeilen.append({"teil": p.laufend.split(" ▸ ")[0], "haupt": "", "reiter": "", "abschnitt": "", "name": p.laufend, "art": "", "urteil": "Fehler",
                                 "hinweis": "hängt", "foto": ""})
                print("ABBRUCH:", grund, flush=True)
                try:
                    p.abbruch = grund
                    bericht_schreiben(p, panel, ziel, behalten)
                finally:
                    if loeschen and bilder_dir:
                        shutil.rmtree(bilder_dir, ignore_errors=True)
                    os._exit(3)
    th = threading.Thread(target=lauf, daemon=True)
    th.start()
    return th


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--panel", default="diagramm", choices=sorted(PANELS), help="welches Panel (Standard: diagramm)")
    ap.add_argument("--teile", default="", help="nur diese Teile (Schlüssel oder Name, Komma getrennt, z. B. titel,legende,reihe_0)")
    ap.add_argument("--arten", default="saeule", help="Diagrammarten (saeule,linie,kreis; Standard: saeule)")
    ap.add_argument("--limit", type=float, default=300.0, help="Sekunden insgesamt (Standard 300)")
    ap.add_argument("--behalten", default="", help="Ordner, in dem die Bilder bleiben (sonst temporär und gelöscht)")
    ap.add_argument("--ziel", default=os.path.join(WURZEL, "docs", "seitenleistenstand.md"))
    wahl = ap.parse_args()
    arten = [a.strip() for a in wahl.arten.split(",") if a.strip() in DIAGRAMM_DATEN] or ["saeule"]
    nur = {t.strip() for t in wahl.teile.split(",") if t.strip()}
    app_starten()
    bilder = os.path.abspath(wahl.behalten) if wahl.behalten else tempfile.mkdtemp(prefix="seitenleiste-")
    os.makedirs(bilder, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="seitenleiste-ini-")
    p = None
    code = 0
    try:
        p = Pruefer(tmp, wahl.panel, arten, nur, wahl.limit, bilder)
        waechter_faden(p, wahl.panel, wahl.ziel, bilder if wahl.behalten else None, bilder, not wahl.behalten)
        try:
            p.durchgehen(wahl.panel)
        except Zeitlimit as t:
            p.abbruch = p.abbruch or f"Zeitlimit ({t.ebene}) erreicht"
        except BaseException:                                 # noqa: BLE001 — der eigene excepthook würde es verschlucken
            traceback.print_exc()
            p.abbruch = "Abbruch durch Python-Fehler: " + traceback.format_exc().strip().splitlines()[-1]
            code = 1
        p.waechter.uhr.stop()
        text = bericht_schreiben(p, wahl.panel, wahl.ziel, bilder if wahl.behalten else None)
        kopf = text.split("## Problemfälle")[0]
        print(kopf)
        print(f"Bericht: {wahl.ziel}")
        try:
            fenster_schliessen(p.w)
        except Exception:                                      # noqa: BLE001
            pass
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        if not wahl.behalten:
            shutil.rmtree(bilder, ignore_errors=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
