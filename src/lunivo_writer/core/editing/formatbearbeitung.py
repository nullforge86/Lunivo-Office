"""Formatoperationen der Sitzung: Zeichen- und Absatzformat, Formatvorlagen, Listen und Nummerierung. Ohne Qt."""
from __future__ import annotations

import dataclasses

from lunivo_writer.core.document.dokument import AUFZAEHLUNGEN, LISTEN_EBENEN, ZAHLENARTEN, Absatz, Auswahl, Formatvorlage, ListenDefinition, ListenEbene, format_an, normalisiere, teile
from lunivo_writer.core.document.formate import pruefe, verschmelze
from lunivo_writer.core.document.formatvorlagen import vorlagenkette
from lunivo_writer.core.document.listen import listenmarken
from .verlauf import BearbeitungsFehler, schritt

# Absatzeigenschaften, die eine neu zugewiesene Formatvorlage nicht überschreibt (sie beschreiben den Ort, nicht das Aussehen)
BLEIBT_BEI_VORLAGE = ("seitenumbruch_vor", "spaltenumbruch_vor", "toc", "verzeichnis_art", "toc_opt", "beschriftung", "notenziel", "deckblatt",
                      "deckblatt_umbruch", "formular", "liste_start")


class FormatTeil:
    # ---- Zeichenformat -------------------------------------------------------------------------------------------------
    @schritt("Zeichenformat", "format")
    def zeichenformat_anwenden(self, aenderung: dict, auswahl: Auswahl | None = None, ersetzen: bool = False) -> None:
        """Setzt Eigenschaften im Bereich (``None`` als Wert entfernt eine). Ohne markierten Text gilt das Format für den Text, der
        als Nächstes getippt wird. ``ersetzen``: das Format wird nicht ergänzt, sondern ganz ersetzt."""
        aenderung = pruefe("zeichen", aenderung, leer_erlaubt=True)

        def neu(fmt: dict) -> dict:
            return verschmelze({}, aenderung) if ersetzen else verschmelze(fmt, aenderung)

        start, ende = self._bereich(auswahl)
        if start == ende:
            a = self._absatz(start.absatz_id)
            basis = self.tippformat if self.tippformat is not None and auswahl is None else format_an(a, start.versatz)
            fmt = neu(basis)
            if a.laenge == 0:
                self._attr(a, "zeichenformat", fmt)
                self._beruehrt(a.id)
            if auswahl is None:
                self.tippformat = fmt
            return
        stuecke = self._stuecke(start, ende)
        for n, (a, von, bis) in enumerate(stuecke):
            davor, rest = teile(a.inhalte, von)
            mitte, danach = teile(rest, bis - von)
            mitte = [dataclasses.replace(x, format=neu(x.format)) for x in mitte]
            self._attr(a, "inhalte", normalisiere(davor + mitte + danach))
            if a.laenge == 0 or (bis == a.laenge and n < len(stuecke) - 1):
                self._attr(a, "zeichenformat", neu(a.zeichenformat))
            self._beruehrt(a.id)

    def zeichenformat_bei(self, pos=None) -> dict:
        """Das Zeichenformat an der Schreibmarke (das Tippformat, wenn eines gesetzt ist)."""
        if pos is None:
            if self.tippformat is not None:
                return dict(self.tippformat)
            pos = self.auswahl.kopf
        pos = self._pruefe_position(pos)
        return dict(format_an(self._absatz(pos.absatz_id), pos.versatz))

    # ---- Absatzformat --------------------------------------------------------------------------------------------------
    @schritt("Absatzformat", "format")
    def absatzformat_anwenden(self, aenderung: dict, auswahl: Auswahl | None = None, absatz_ids=None, ersetzen: bool = False) -> None:
        aenderung = pruefe("absatz", aenderung, leer_erlaubt=True)
        for a in self._ziel_absaetze(auswahl, absatz_ids):
            self._attr(a, "format", verschmelze({} if ersetzen else a.format, aenderung))
            self._beruehrt(a.id)

    @schritt("Absatzmarke", "format")
    def absatz_zeichenformat_anwenden(self, aenderung: dict, auswahl: Auswahl | None = None, absatz_ids=None, ersetzen: bool = False) -> None:
        """Das Zeichenformat der Absatzmarke (gilt für Text, der in den leeren Absatz getippt wird)."""
        aenderung = pruefe("zeichen", aenderung, leer_erlaubt=True)
        for a in self._ziel_absaetze(auswahl, absatz_ids):
            self._attr(a, "zeichenformat", verschmelze({} if ersetzen else a.zeichenformat, aenderung))
            self._beruehrt(a.id)

    # ---- Formatvorlagen ------------------------------------------------------------------------------------------------
    @schritt("Formatvorlage", "vorlage")
    def vorlage_setzen(self, vorlage: Formatvorlage) -> None:
        """Legt eine Formatvorlage an oder ersetzt die gleichnamige."""
        if not vorlage.name.strip():
            raise BearbeitungsFehler("Eine Formatvorlage braucht einen Namen")
        if vorlage.art not in ("absatz", "zeichen", "tabelle"):
            raise BearbeitungsFehler(f"Unbekannte Art der Formatvorlage: {vorlage.art}")
        pruefe("zeichen", vorlage.zeichen); pruefe("absatz", vorlage.absatz)
        name = vorlage.basis
        gesehen = {vorlage.name}
        while name:
            if name in gesehen:
                raise BearbeitungsFehler("Formatvorlagen dürfen nicht im Kreis aufeinander aufbauen")
            gesehen.add(name)
            name = self.dokument.vorlagen[name].basis if name in self.dokument.vorlagen else ""
        self._dict(self.dokument.vorlagen, vorlage.name, vorlage)
        self._beruehrt(*self._absaetze_mit_vorlage(vorlage.name))

    @schritt("Formatvorlage löschen", "vorlage")
    def vorlage_loeschen(self, name: str) -> None:
        """Entfernt die Vorlage; Text, der sie trägt, fällt auf ihre Basisvorlage zurück."""
        vorlage = self.dokument.vorlagen.get(name)
        if vorlage is None:
            raise BearbeitungsFehler(f"Keine Formatvorlage „{name}“")
        self._vorlage_umhaengen(name, vorlage.basis or None)
        for v in list(self.dokument.vorlagen.values()):
            if v.name != name and (v.basis == name or v.folge == name):
                self._dict(self.dokument.vorlagen, v.name, dataclasses.replace(
                    v, basis=vorlage.basis if v.basis == name else v.basis, folge="" if v.folge == name else v.folge))
        self._dict(self.dokument.vorlagen, name)

    @schritt("Formatvorlage umbenennen", "vorlage")
    def vorlage_umbenennen(self, alt: str, neu: str) -> None:
        if alt not in self.dokument.vorlagen:
            raise BearbeitungsFehler(f"Keine Formatvorlage „{alt}“")
        if not neu.strip() or neu in self.dokument.vorlagen:
            raise BearbeitungsFehler(f"Der Name „{neu}“ ist leer oder schon vergeben")
        self._dict(self.dokument.vorlagen, neu, dataclasses.replace(self.dokument.vorlagen[alt], name=neu))
        self._dict(self.dokument.vorlagen, alt)
        for v in list(self.dokument.vorlagen.values()):
            if v.basis == alt or v.folge == alt:
                self._dict(self.dokument.vorlagen, v.name, dataclasses.replace(
                    v, basis=neu if v.basis == alt else v.basis, folge=neu if v.folge == alt else v.folge))
        self._vorlage_umhaengen(alt, neu)

    def _absaetze_mit_vorlage(self, name: str) -> list:
        return [a.id for a in self.dokument.absaetze()
                if any(v.name == name for v in vorlagenkette(self.dokument, a.format.get("vorlage", "")))
                or any(any(v.name == name for v in vorlagenkette(self.dokument, x.format.get("vorlage", "")))
                       for x in a.inhalte)]

    def _vorlage_umhaengen(self, alt: str, neu: str | None) -> None:
        for a in self.dokument.absaetze():
            if a.format.get("vorlage") == alt:
                self._attr(a, "format", verschmelze(a.format, {"vorlage": neu}))
                self._beruehrt(a.id)
            if any(x.format.get("vorlage") == alt for x in a.inhalte):
                self._attr(a, "inhalte", normalisiere([
                    dataclasses.replace(x, format=verschmelze(x.format, {"vorlage": neu})) if x.format.get("vorlage") == alt else x
                    for x in a.inhalte]))
                self._beruehrt(a.id)

    @schritt("Formatvorlage zuweisen", "format")
    def vorlage_anwenden(self, name: str, auswahl: Auswahl | None = None, absatz_ids=None) -> None:
        """Weist eine Vorlage zu. Absatzvorlage: das Absatzformat wird auf die Vorlage zurückgesetzt (Ortsangaben wie Seitenumbruch
        bleiben). Zeichenvorlage: gilt für den markierten Text. Leerer Name: Vorlage entfernen."""
        vorlage = self.dokument.vorlagen.get(name)
        if name and vorlage is None:
            raise BearbeitungsFehler(f"Keine Formatvorlage „{name}“")
        if vorlage is not None and vorlage.art == "zeichen":
            self.zeichenformat_anwenden({"vorlage": name}, auswahl)
            return
        zeichen_angaben: dict = {}
        for v in vorlagenkette(self.dokument, name):
            zeichen_angaben.update(v.zeichen)
        for a in self._ziel_absaetze(auswahl, absatz_ids):
            fmt = {k: v for k, v in a.format.items() if k in BLEIBT_BEI_VORLAGE}
            if name:
                fmt["vorlage"] = name
            self._attr(a, "format", fmt)
            self._attr(a, "format_aufgeloest", False)
            if zeichen_angaben:                                  # die Zeichenangaben der Vorlage gelten für den ganzen Absatz
                self._attr(a, "inhalte", normalisiere([dataclasses.replace(x, format=verschmelze(x.format, zeichen_angaben))
                                                       for x in a.inhalte]))
                self._attr(a, "zeichenformat", verschmelze(a.zeichenformat, zeichen_angaben))
            self._beruehrt(a.id)

    # ---- Listen --------------------------------------------------------------------------------------------------------
    @schritt("Liste anlegen", "liste")
    def liste_anlegen(self, ebenen, name: str = "") -> int:
        """Legt eine Listendefinition an. ``ebenen``: Liste von ``ListenEbene`` oder der Name einer Zahlen-/Aufzählungsart für eine
        einfache Liste. Gibt die Id zurück."""
        definition = ListenDefinition(self._id(), self._ebenen(ebenen), name)
        self._dict(self.dokument.listen, definition.id, definition)
        return definition.id

    def _ebenen(self, ebenen) -> list:
        if isinstance(ebenen, str):
            ebenen = [ListenEbene(stil=ebenen, einzug=6.3 * (i + 1), ausr=6.3 * i) for i in range(LISTEN_EBENEN)]
        ebenen = list(ebenen)
        if not ebenen or len(ebenen) > LISTEN_EBENEN:
            raise BearbeitungsFehler(f"Eine Liste hat 1 bis {LISTEN_EBENEN} Ebenen")
        for e in ebenen:
            if e.stil not in ZAHLENARTEN + AUFZAEHLUNGEN:
                raise BearbeitungsFehler(f"Unbekannte Listenart: {e.stil}")
        return ebenen

    @schritt("Liste ändern", "liste")
    def liste_aendern(self, liste_id: int, ebenen, name: str | None = None) -> None:
        alt = self._liste_holen(liste_id)
        self._dict(self.dokument.listen, liste_id, ListenDefinition(liste_id, self._ebenen(ebenen), alt.name if name is None else name))
        self._beruehrt(*(a.id for a in self.dokument.absaetze() if a.liste_id == liste_id))

    def _liste_holen(self, liste_id: int) -> ListenDefinition:
        if liste_id not in self.dokument.listen:
            raise BearbeitungsFehler(f"Keine Liste mit der Id {liste_id}")
        return self.dokument.listen[liste_id]

    @schritt("Liste", "liste")
    def liste_anwenden(self, liste_id: int, auswahl: Auswahl | None = None, absatz_ids=None, ebene: int | None = None) -> None:
        definition = self._liste_holen(liste_id)
        for a in self._ziel_absaetze(auswahl, absatz_ids):
            self._attr(a, "liste_id", liste_id)
            self._attr(a, "ebene", min(max(a.ebene if ebene is None else ebene, 0), len(definition.ebenen) - 1))
            self._beruehrt(a.id)

    @schritt("Liste entfernen", "liste")
    def liste_entfernen(self, auswahl: Auswahl | None = None, absatz_ids=None) -> None:
        for a in self._ziel_absaetze(auswahl, absatz_ids):
            self._attr(a, "liste_id", None); self._attr(a, "ebene", 0)
            if "liste_start" in a.format:
                self._attr(a, "format", verschmelze(a.format, {"liste_start": None}))
            self._beruehrt(a.id)

    @schritt("Listenebene", "liste")
    def listenebene_aendern(self, schritte: int, auswahl: Auswahl | None = None, absatz_ids=None) -> None:
        """Stuft Listenabsätze tiefer (``+1``) oder höher (``-1``)."""
        for a in self._ziel_absaetze(auswahl, absatz_ids):
            if a.liste_id is None:
                continue
            hoechste = len(self._liste_holen(a.liste_id).ebenen) - 1
            self._attr(a, "ebene", min(max(a.ebene + schritte, 0), hoechste))
            self._beruehrt(a.id)

    @schritt("Nummerierung neu beginnen", "liste")
    def liste_neu_beginnen(self, absatz_id: int, start: int | None = 1) -> None:
        """Die Zählung beginnt an diesem Absatz mit ``start``; ``None`` setzt die Zählung wieder fort."""
        a = self._absatz(absatz_id)
        if a.liste_id is None:
            raise BearbeitungsFehler("Der Absatz gehört zu keiner Liste")
        self._attr(a, "format", verschmelze(a.format, {"liste_start": start}))
        self._beruehrt(a.id)

    def listenmarken(self) -> dict:
        return listenmarken(self.dokument)
