"""Befehle der Funktion „Kopf- und Fußzeile“: annehmen, prüfen, den Kern aufrufen, Ergebnis oder Ereignis melden.

Die Oberfläche ruft diese Klasse auf und abonniert die Ereignisse beim ``Melder``. Der Editor kommt über den ``SeitenPort`` herein (die Oberfläche
setzt ihn um). Nach außen gehen nur Grundtypen und die Datentypen aus ``typen.py``; die Seiteneinrichtung des Kerns bleibt im Framework."""
from __future__ import annotations

from framework.schnittstellen.seiten_port import SeitenPort
from framework.datentypen.ereignisdaten import Art, Ereignis
from framework.steuerung.ereignissteuerung import Melder
from framework.funktionen.kopffuss import menues
from framework.funktionen.kopffuss.typen import KopfFussOptionen, MenueEintrag
from core.funktionen.kopffuss import optionen as kern_optionen

KEIN_VORGAENGER = "Der erste Abschnitt hat keinen Vorgänger."
KEINE_VORIGE = "Es gibt keine vorige Kopfzeile."
KEINE_NAECHSTE = "Es gibt keine nächste Kopfzeile."


class KopfFussBefehle:
    def __init__(self, editor: SeitenPort, melder: Melder):
        self._editor = editor
        self._melder = melder

    # ---- Bearbeiter (Bearbeiten direkt auf der Seite) ------------------------------------------------------------------------------
    def _bearbeiter(self):
        b = self._editor.kopffuss()
        return b if b is not None and b.aktiv else None

    def bearbeitung_aktiv(self) -> bool:
        return self._bearbeiter() is not None

    def _melden(self, text: str) -> None:
        self._melder.melden(Ereignis(Art.MELDUNG, text, {"dauer_ms": 4000}))

    def _oeffnen(self, was: str, **daten) -> None:
        self._melder.melden(Ereignis(Art.OEFFNEN, was, daten))

    # ---- Menüs als Daten -----------------------------------------------------------------------------------------------------------
    def menue_gruppe(self) -> tuple[MenueEintrag, ...]:
        return menues.gruppe(self.bearbeitung_aktiv())

    def menue_zone(self, zone: str) -> tuple[MenueEintrag, ...]:
        return menues.zone(zone)

    def menue_linie(self) -> tuple[MenueEintrag, ...]:
        return menues.linie()

    def menue_einstellungen(self) -> tuple[MenueEintrag, ...]:
        return menues.einstellungen()

    def ausfuehren(self, aktion: str) -> None:
        """Führt eine Aktion aus einem Menüeintrag aus (``bearbeiten:kopf``, ``ausrichten:fuss:left``, ``leeren:header,footer`` …)."""
        name, *teile = aktion.split(":")
        if name == "bearbeiten":
            self.bearbeiten_starten(teile[0])
        elif name == "ausrichten":
            self.ausrichten(teile[0], teile[1])
        elif name == "leeren":
            self.leeren(tuple(teile[0].split(",")))
        elif name == "wechseln":
            self.wechseln()
        elif name == "optionen_dialog":
            self._oeffnen("optionen")
        elif name == "seite_einrichten":
            self._oeffnen("seite_einrichten")
        elif name == "schliessen":
            self.schliessen()

    # ---- Befehle -------------------------------------------------------------------------------------------------------------------
    def bearbeiten_starten(self, zone: str) -> None:
        self._oeffnen("bearbeiten", zone=zone)

    def ausrichten(self, zone: str, ausrichtung: str) -> None:
        b = self._bearbeiter()
        if b is None:
            self.bearbeiten_starten(zone)
            b = self._bearbeiter()
        if b is not None:
            if b.zone != zone:
                b.starte(zone, b.blatt)
            b.ausrichtung_setzen(ausrichtung)

    def leeren(self, felder: tuple[str, ...]) -> None:
        b = self._bearbeiter()
        if b is not None:
            b.speichern()
        seite = self._editor.abschnitt_seite()
        kern_optionen.leeren(seite, felder)
        self._editor.page_settings_changed(seite)
        if b is not None:
            b._laden()

    def schliessen(self) -> None:
        b = self._bearbeiter()
        if b is not None:
            b.beende()

    def wechseln(self) -> None:
        b = self._bearbeiter()
        if b is not None:
            b.wechseln()

    def springen(self, richtung: int) -> None:
        b = self._bearbeiter()
        if b is not None and not b.abschnitt_springen(richtung):
            self._melden(KEINE_VORIGE if richtung < 0 else KEINE_NAECHSTE)

    def tabstopp_einfuegen(self) -> None:
        b = self._bearbeiter()
        if b is not None:
            b.tabstopp_einfuegen()

    # ---- Optionen: erste Seite anders, gerade/ungerade, Abstand ---------------------------------------------------------------
    def optionen(self) -> KopfFussOptionen:
        seite = self._editor.abschnitt_seite()
        return KopfFussOptionen(bool(seite.diff_first), bool(seite.diff_even), kern_optionen.abstand_mm(seite, "kopf"),
                                kern_optionen.abstand_mm(seite, "fuss"))

    def erste_seite_anders(self) -> bool:
        return bool(self._editor.abschnitt_seite().diff_first)

    def gerade_ungerade(self) -> bool:
        return bool(self._editor.abschnitt_seite().diff_even)

    def erste_seite_anders_umschalten(self) -> None:
        seite = self._editor.abschnitt_seite()
        kern_optionen.erste_seite_anders_umschalten(seite)
        self._editor.page_settings_changed(seite)

    def gerade_ungerade_umschalten(self) -> None:
        seite = self._editor.abschnitt_seite()
        kern_optionen.gerade_ungerade_umschalten(seite)
        self._editor.page_settings_changed(seite)
        b = self._bearbeiter()
        if b is not None:
            b._laden()

    def optionen_setzen(self, erste_seite_anders: bool, gerade_ungerade: bool) -> None:
        """Übernimmt die Werte des Optionenfensters: nur was sich ändert, wird umgeschaltet; danach lädt ein aktiver Bearbeiter neu."""
        if erste_seite_anders != self.erste_seite_anders():
            self.erste_seite_anders_umschalten()
        if gerade_ungerade != self.gerade_ungerade():
            self.gerade_ungerade_umschalten()
        b = self._bearbeiter()
        if b is not None:
            b._laden()

    def abstand_setzen(self, zone: str, mm: float) -> None:
        seite = self._editor.abschnitt_seite()
        kern_optionen.abstand_setzen(seite, zone, mm)
        self._editor.page_settings_changed(seite)

    # ---- Verknüpfung mit dem vorherigen Abschnitt ---------------------------------------------------------------------------------
    def verknuepfung_moeglich(self) -> bool:
        """Grau im ersten Abschnitt: dort gibt es keinen Vorgänger."""
        return self._editor.abschnitt_nr() > 0

    def verknuepft(self, was: str) -> bool:
        return self.verknuepfung_moeglich() and kern_optionen.verknuepft(self._editor.abschnitt_seite(), was)

    def verknuepfung_umschalten(self, was: str) -> bool:
        """Schaltet die Verknüpfung von ``kopf`` oder ``fuss`` um; ohne Vorgänger gibt es eine Meldung (Rückgabe ``False``)."""
        if not self.verknuepfung_moeglich():
            self._melden(KEIN_VORGAENGER)
            return False
        seite = self._editor.abschnitt_seite()
        kern_optionen.verknuepfung_setzen(seite, was, not kern_optionen.verknuepft(seite, was))
        self._editor.page_settings_changed(seite)
        return True

    def bearbeiter_verknuepfen(self) -> None:
        """Schalter „Mit vorheriger verknüpfen“ im Reiter: wirkt auf die Zone des aktiven Bearbeiters."""
        b = self._bearbeiter()
        if b is None:
            return
        self.verknuepfung_umschalten("kopf" if b.zone == "kopf" else "fuss")
        b._laden()

    def bearbeiter_verknuepft(self) -> bool:
        b = self._bearbeiter()
        return bool(b is not None and self.verknuepft("kopf" if b.zone == "kopf" else "fuss"))
