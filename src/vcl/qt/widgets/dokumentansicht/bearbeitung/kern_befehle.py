"""Bandbefehle des Editors für Absatz, Liste, Rahmen, Tabulator, Formatvorlage, Abschnitt, Verknüpfung und Ersetzen im Text.

Die Klasse ``KernBefehle`` gehört zu ``KernEditor`` (``kern_editor.py``) und übersetzt wie dieser Befehle der Oberfläche in Operationen der
Bearbeitungssitzung. Hier stehen die Befehle, die Wörterbücher und Listen aus den Dialogen der Oberfläche (Liste, Rahmen, Absatz,
Formatvorlage) in Formate des Dokumentmodells umsetzen und zurück.
"""
from __future__ import annotations

import dataclasses
import re

from PySide6.QtCore import Qt

from core.bearbeitung.suche import offset_zu_position
from core.dokument.dokument import AUFZAEHLUNGEN, LISTEN_EBENEN, Auswahl, Formatvorlage, ListenEbene, Position
from core.dokument.listen import PLATZHALTER, ZEICHEN_DER_AUFZAEHLUNG
from core.geometrie import mm_to_px, px_to_mm
from core.layout import formatwerte as F

PUNKTE = ("disc", "circle", "square")
ZAHLEN_TIEFER = ("dezimal", "klein", "roem_klein")
TAB_NAME = {0: "links", 1: "rechts", 2: "mitte", 3: "dezimal"}
from vcl.qt.widgets.bausteine.basis.farben import GITTER_FARBE, TABELLENRAND_STANDARD  # noqa: E402


# ---- Listen: Beschreibung der Oberfläche ↔ Ebenen des Modells -------------------------------------------------------------------------------------
def spec_zu_ebenen(spec: dict) -> list:
    """Die 9 Ebenen einer Liste des Modells für die Beschreibung, die die Listenfenster liefern (einfache Liste oder Gliederung)."""
    if "ebenen" in spec:
        aus = []
        for x in spec["ebenen"][:LISTEN_EBENEN]:
            zusatz = {k: x[k] for k in ("tab", "ausr_art", "danach", "neu", "norm", "vorlage") if x.get(k)}
            if x.get("zeichen"):
                zusatz["zeichenformat"] = dict(x["zeichen"])
            fmt, stil = x.get("format", ""), x.get("stil", "dezimal")
            if stil in PUNKTE:
                aus.append(ListenEbene(stil=stil, ausr=x["ausr"], einzug=x["einzug"], zusatz=zusatz))
            elif not any(ch in fmt for ch in PLATZHALTER):
                aus.append(ListenEbene(stil="zeichen", zeichen=fmt or "•", ausr=x["ausr"], einzug=x["einzug"], zusatz=zusatz))
            else:
                aus.append(ListenEbene(stil=stil, format=fmt, start=int(x.get("start", 1)), ausr=x["ausr"], einzug=x["einzug"], zusatz=zusatz))
        while len(aus) < LISTEN_EBENEN:
            i = len(aus)
            aus.append(dataclasses.replace(aus[-1], ausr=aus[-1].ausr + 6.3, einzug=aus[-1].einzug + 6.3) if aus else ListenEbene(ausr=6.3 * i, einzug=6.3 * (i + 1)))
        return aus
    pos = spec.get("pos") or {}
    stil = spec["stil"]
    zusatz_pos = {k: pos[k] for k in ("tab", "ausr_art", "danach") if pos.get(k)}
    ebenen = []
    for i in range(LISTEN_EBENEN):
        ausr, einzug = pos.get("ausr", 0.0) + 6.3 * i, pos.get("einzug", 6.3) + 6.3 * i
        zusatz = dict(zusatz_pos)
        if spec.get("zeichen"):
            zusatz["zeichenformat"] = dict(spec["zeichen"])
        if stil in PUNKTE:
            rest = [s for s in PUNKTE if s != stil]
            ebenen.append(ListenEbene(stil=([stil] + rest)[i % 3], ausr=ausr, einzug=einzug, zusatz=zusatz))
        else:
            art = stil if i == 0 else ZAHLEN_TIEFER[i % 3]
            ebenen.append(ListenEbene(stil=art, format=spec.get("praefix", "") + PLATZHALTER[i] + spec.get("suffix", "."), start=int(spec.get("start", 1)) if i == 0 else 1,
                                      ausr=ausr, einzug=einzug, zusatz=zusatz))
    return ebenen


def ebenen_zu_spec(ebenen: list) -> dict:
    """Das Gegenstück: die Beschreibung der Liste für die Listenfenster (einfach, wenn sie genau so entstanden sein kann, sonst Gliederung)."""
    from core.funktionen.absatz import listen as L
    from core.funktionen.absatz import mehrstufig as M
    if ebenen and all(e.stil in PUNKTE for e in ebenen) and spec_zu_ebenen(L.liste(ebenen[0].stil)) == ebenen:
        return L.liste(ebenen[0].stil)
    e0 = ebenen[0]
    if e0.stil in ("dezimal", "klein", "gross", "roem_klein", "roem_gross") and e0.format.count(PLATZHALTER[0]) == 1 and not e0.zusatz:
        vor, _s, nach = e0.format.partition(PLATZHALTER[0])
        einfach = L.liste(e0.stil, vor, nach, e0.start)
        if spec_zu_ebenen(einfach) == ebenen:
            return einfach
    aus = []
    for e in ebenen:
        mehr = {k: e.zusatz[k] for k in ("tab", "ausr_art", "danach", "neu", "norm", "vorlage") if e.zusatz.get(k)}
        if e.stil in AUFZAEHLUNGEN:
            zeichen = e.zeichen or ZEICHEN_DER_AUFZAEHLUNG.get(e.stil, "•")
            aus.append(M.ebene("dezimal", zeichen, 1, e.ausr, e.einzug, e.zusatz.get("zeichenformat"), **mehr))
        else:
            aus.append(M.ebene(e.stil, e.format or PLATZHALTER[len(aus)] + ".", e.start, e.ausr, e.einzug, e.zusatz.get("zeichenformat"), **mehr))
    return {"ebenen": aus}


def katalog_zu_vorlage(name: str, d: dict) -> Formatvorlage:
    """Eine Formatvorlage des Katalogs (``editor/text/stile.py``) als Vorlage des Dokumentmodells."""
    zeichen = {}
    for k, v in (("groesse_pt", float(d["groesse"]) if d.get("groesse") else None), ("fett", True if d.get("fett") else None),
                 ("kursiv", True if d.get("kursiv") else None), ("farbe", d.get("farbe") or None), ("schrift", d.get("schrift") or None),
                 ("durchgestrichen", True if d.get("durch") else None), ("doppelt_durch", True if d.get("doppelt") else None),
                 ("hoch_tief", "hoch" if d.get("hoch") else "tief" if d.get("tief") else None),
                 ("kapitaelchen", True if d.get("kapital") else None), ("grossbuchstaben", True if d.get("gross") else None),
                 ("versteckt", True if d.get("versteckt") else None), ("zeichenabstand", float(d["abstand"]) if d.get("abstand") else None),
                 ("skalierung", float(d["skala"]) if d.get("skala") and float(d["skala"]) != 100.0 else None),
                 ("versatz_pt", float(d["position"]) if d.get("position") else None), ("unterstrichen", True if d.get("unter") else None),
                 ("unter_farbe", d.get("unterfarbe") or None), ("betonung", d.get("betonung") or None), ("effekt", d.get("effekt") or None)):
        if v is not None:
            zeichen[k] = v
    absatz = {}
    zeilen_art = d.get("zeilen_art", "faktor")
    for k, v in (("abstand_vor", d["vor"] / 0.75 if d.get("vor") else None), ("abstand_nach", d["nach"] / 0.75 if d.get("nach") else None),
                 ("ausrichtung", d.get("ausr") or None),
                 ("zeilenabstand_art", ("vielfach" if zeilen_art == "faktor" else zeilen_art) if (d.get("zeilen") or zeilen_art != "faktor") else None),
                 ("zeilenabstand", d["zeilen"] * 100.0 if zeilen_art == "faktor" and d.get("zeilen") else d["zeilen_pt"] / 0.75 if zeilen_art != "faktor" and d.get("zeilen_pt") else None),
                 ("einzug_links", mm_to_px(d["einzug"]) if d.get("einzug") else None), ("einzug_rechts", mm_to_px(d["rechts"]) if d.get("rechts") else None),
                 ("einzug_erste", mm_to_px(d["erste"]) if d.get("erste") else None), ("seitenumbruch_vor", True if d.get("umbruch") else None),
                 ("gliederungsebene", int(d["gliederung"]) if d.get("gliederung") else None), ("richtung", "rtl" if d.get("rtl") else None),
                 ("rahmen", d.get("rahmen") or None), ("hintergrund", d.get("fuell") or None),
                 ("muster", (d["muster"] + ("|" + d["musterfarbe"] if d.get("musterfarbe") else "")) if d.get("muster") else None),
                 ("optionen", d.get("opt") or None)):
        if v is not None:
            absatz[k] = v
    if d.get("tabs"):
        from vcl.qt.widgets.bausteine.dokument.tabstopp_dialog import aus_text
        stopps = aus_text(d["tabs"])
        absatz["tabstopps"] = [[mm_to_px(m), art, ""] for m, art, _f in stopps]
        fuell = ";".join(f"{mm_to_px(m):.2f}:{f}" for m, _a, f in stopps if f)
        if fuell:
            absatz["tabfuell"] = fuell
    zusatz = {k: d[k] for k in ("taste", "key", "liste") if d.get(k)}
    return Formatvorlage(name, "absatz", d.get("basis") or ("" if name == "Standard" else "Standard"), d.get("folge") or ("Standard" if d.get("ebene") else ""),
                         int(d.get("ebene") or 0), zeichen, absatz, zusatz)


def vorlage_zu_katalog(v: Formatvorlage) -> dict:
    """Die Felder einer Katalogvorlage (``stile.VORLAGE``), soweit das Modell sie führt — für das Fenster „Formatvorlage“."""
    z, a = v.zeichen, v.absatz
    d = {"ebene": v.ebene, "groesse": z.get("groesse_pt") or 0, "fett": bool(z.get("fett")), "kursiv": bool(z.get("kursiv")), "farbe": z.get("farbe", ""),
         "schrift": z.get("schrift", "") if isinstance(z.get("schrift", ""), str) else "", "vor": round(a.get("abstand_vor", 0) * 0.75, 1),
         "nach": round(a.get("abstand_nach", 0) * 0.75, 1), "ausr": a.get("ausrichtung", ""), "einzug": round(px_to_mm(a.get("einzug_links", 0)), 1),
         "rechts": round(px_to_mm(a.get("einzug_rechts", 0)), 1), "erste": round(px_to_mm(a.get("einzug_erste", 0)), 1),
         "rtl": a.get("richtung") in ("rtl", 1), "umbruch": bool(a.get("seitenumbruch_vor")), "gliederung": a.get("gliederungsebene", 0),
         "rahmen": a.get("rahmen", ""), "fuell": a.get("hintergrund", ""), "durch": bool(z.get("durchgestrichen")), "versteckt": bool(z.get("versteckt")),
         "hoch": z.get("hoch_tief") == "hoch", "tief": z.get("hoch_tief") == "tief", "kapital": bool(z.get("kapitaelchen")), "gross": bool(z.get("grossbuchstaben"))}
    art = a.get("zeilenabstand_art")
    if art == "vielfach":
        d["zeilen"] = a.get("zeilenabstand", 100.0) / 100.0
    elif art in ("genau", "mindestens"):
        d.update(zeilen_art=art, zeilen_pt=a.get("zeilenabstand", 0.0) * 0.75)
    if isinstance(a.get("optionen"), str):
        d["opt"] = a["optionen"]
    return d


from core.editor.text.ki_markdown import markdown_bloecke  # noqa: E402,F401  (Qt-freie Zerlegung, hier weiter erreichbar)


class KernBefehle:
    """Gemischt in ``KernEditor``: nutzt ``self.sitzung`` und ``self.ansicht`` des Editors."""

    # ---- Zeichen ----------------------------------------------------------------------------------------------------------------------
    def set_outline(self, an: bool) -> None:
        self._zf({"effekt": {"kontur": True} if an else None})

    def ist_versteckt(self) -> bool:
        return bool(self._zeichen().get("versteckt"))

    def set_versteckt(self, an: bool) -> None:
        self._zf({"versteckt": True if an else None})

    def format_aufnehmen(self) -> dict:
        """Zeichen- und Absatzformat an der Schreibmarke für „Format übertragen“."""
        a = self._absatz_an_marke()
        z = {k: v for k, v in self._zeichen().items() if k in ("schrift", "groesse_pt", "fett", "kursiv", "unterstrichen", "durchgestrichen", "farbe",
                                                               "marker", "hoch_tief", "kapitaelchen", "grossbuchstaben", "zeichenabstand", "effekt")}
        return {"zeichen": z, "absatz": dict(a.format)}

    def format_uebertragen(self, probe: dict) -> None:
        """Das aufgenommene Format auf die Auswahl legen (Zeichen) — bei leerer Auswahl auf den Absatz."""
        def f(s):
            with s.gruppe("Format übertragen"):
                alle = {k: probe["zeichen"].get(k) for k in ("schrift", "groesse_pt", "fett", "kursiv", "unterstrichen", "durchgestrichen", "farbe", "marker",
                                                              "hoch_tief", "kapitaelchen", "grossbuchstaben", "zeichenabstand", "effekt")}
                s.zeichenformat_anwenden(alle)
                if s.auswahl.leer:
                    s.absatzformat_anwenden({k: v for k, v in probe["absatz"].items() if k not in ("seitenumbruch_vor", "seitenumbruch_nach")}, ersetzen=True)
        self.ansicht._aendern(f)

    # ---- Absatz ----------------------------------------------------------------------------------------------------------------------------
    def set_indents(self, links_mm: float, rechts_mm: float, erste_mm: float) -> None:
        self._af({"einzug_links": mm_to_px(links_mm) or None, "einzug_rechts": mm_to_px(rechts_mm) or None, "einzug_erste": mm_to_px(erste_mm) or None})

    def absatz_option(self, name: str):
        """Eine Absatzoption (``editor/seite/absatzopt.py``) des Absatzes an der Schreibmarke."""
        from core.editor.seite import absatzopt
        roh = F.absatzformat(self.sitzung.dokument, self._absatz_an_marke()).get("optionen")
        return absatzopt.aus_text(roh if isinstance(roh, str) else "").get(name, absatzopt.VORGABE.get(name))

    def absatz_option_setzen(self, name: str, wert) -> None:
        from core.editor.seite import absatzopt
        roh = F.absatzformat(self.sitzung.dokument, self._absatz_an_marke()).get("optionen")
        w = absatzopt.aus_text(roh if isinstance(roh, str) else "")
        w[name] = wert
        self._af({"optionen": absatzopt.als_text(w) or None})

    def set_absatzopt(self, opt) -> None:
        from core.editor.seite import absatzopt
        text = opt if isinstance(opt, str) else absatzopt.als_text(opt)
        self._af({"optionen": text or None})

    def set_tabstopps(self, stopps) -> None:
        """Tabstopps als Liste aus (Millimeter, Ausrichtung, Füllzeichen)."""
        liste = [[mm_to_px(m), art, ""] for m, art, _f in stopps]
        fuell = ";".join(f"{mm_to_px(m):.2f}:{f}" for m, _a, f in stopps if f)
        self._af({"tabstopps": liste or None, "tabfuell": fuell or None})

    def standard_tab_mm(self) -> float:
        return round(px_to_mm(F._zahl(self.sitzung.dokument.eigenschaften.get("tab_abstand"), 48.0)), 2)

    def set_standard_tab_mm(self, mm: float) -> None:
        self.ansicht._aendern(lambda s: s.eigenschaft_setzen("tab_abstand", mm_to_px(mm)))

    def toggle_rtl(self) -> None:
        a = F.absatzformat(self.sitzung.dokument, self._absatz_an_marke())
        self._af({"richtung": "ltr" if F.richtung(a) == "rtl" else "rtl", "ausrichtung": None if a.get("ausrichtung") in (None, "links", "rechts") else a["ausrichtung"]})

    def absatzrahmen(self):
        from core.editor.objekte.formen.linie import Linie
        return Linie.aus_text(F.absatzformat(self.sitzung.dokument, self._absatz_an_marke()).get("rahmen"))

    def set_absatzrahmen(self, text) -> None:
        self._af({"rahmen": text or None})

    def absatzschatten(self) -> tuple:
        a = F.absatzformat(self.sitzung.dokument, self._absatz_an_marke())
        return a.get("hintergrund"), a.get("muster")

    def set_absatzschatten(self, fuell=None, muster=None, musterfarbe=None) -> None:
        if hasattr(fuell, "name") and callable(fuell.name):
            fuell = fuell.name()
        self._af({"hintergrund": fuell or None, "muster": (f"{muster}|{musterfarbe}" if musterfarbe else str(muster)) if muster else None})

    # ---- Listen -----------------------------------------------------------------------------------------------------------------------------
    def liste_spec(self):
        """Beschreibung der Liste am Absatz der Schreibmarke (für die Listenfenster), ``None`` ohne Liste."""
        d = self.sitzung.dokument
        a = self._absatz_an_marke()
        definition = d.listen.get(a.liste_id) if a.liste_id is not None else None
        return ebenen_zu_spec(definition.ebenen) if definition is not None and definition.ebenen else None

    def set_liste(self, spec) -> None:
        """Wendet die Liste auf die Absätze der Auswahl an (``None``: Liste entfernen). Folgt sie unmittelbar auf eine gleiche Liste, zählt sie weiter."""
        if not spec:
            self.ansicht._aendern(lambda s: s.liste_entfernen())
            return
        ebenen = spec_zu_ebenen(spec)

        def f(s):
            with s.gruppe("Liste"):
                absaetze = list(s.dokument.absaetze())
                start, _ende = s._bereich()
                i = next((k for k, a in enumerate(absaetze) if a.id == start.absatz_id), 0)
                davor = absaetze[i - 1] if i > 0 else None
                alt = s.dokument.listen.get(davor.liste_id) if davor is not None and davor.liste_id is not None else None
                lid = alt.id if alt is not None and alt.ebenen == ebenen else s.liste_anlegen(ebenen)
                s.liste_anwenden(lid)
        self.ansicht._aendern(f)

    def liste_neu_beginnen(self, start: int = 1) -> None:
        a = self._absatz_an_marke()
        self.ansicht._aendern(lambda s: s.liste_neu_beginnen(a.id, start))

    # ---- Formatvorlagen -----------------------------------------------------------------------------------------------------------------
    def stil_aus_auswahl(self) -> dict:
        """Die Werte des Absatzes an der Schreibmarke als Vorgabe für „Neue Formatvorlage“."""
        d = self.sitzung.dokument
        a = self._absatz_an_marke()
        z = self._zeichen()
        af = F.absatzformat(d, a)
        probe = Formatvorlage("", "absatz", "", "", 0, {k: v for k, v in z.items() if k != "vorlage"}, {k: v for k, v in af.items() if k != "vorlage"})
        werte = vorlage_zu_katalog(probe)
        werte["basis"] = a.format.get("vorlage") or "Standard"
        spec = self.liste_spec()
        if spec:
            from core.funktionen.absatz import listen as L
            werte["liste"] = L.als_text(spec)
        if af.get("tabstopps"):
            from vcl.qt.widgets.bausteine.dokument.tabstopp_dialog import als_text
            fuell = F.tabfuellung(af)
            werte["tabs"] = als_text([(round(px_to_mm(t[0]), 1), TAB_NAME.get(t[1], "links"), next((k for k, v in F.FUELLZEICHEN.items() for p, z in fuell.items() if abs(p - t[0]) < 0.05 and z == v), ""))
                                      for t in F.tabstopps(af, d)[0]])
        return {k: v for k, v in werte.items() if v not in (None, "", 0, 0.0, False)}

    def _vorlage_abgleichen(self, name: str) -> None:
        """Legt die Vorlage des Katalogs im Dokument an oder aktualisiert sie, wenn sie dort anders steht."""
        from core.editor.text import stile
        if name not in stile.namen():
            return
        neu = katalog_zu_vorlage(name, stile.definition(name))
        if self.sitzung.dokument.vorlagen.get(name) != neu:
            self.ansicht._aendern(lambda s: s.vorlage_setzen(neu))

    def stil_neu_anwenden(self, name: str) -> None:
        """Nach dem Ändern einer Vorlage im Katalog: das Dokument übernimmt die neue Definition."""
        self._vorlage_abgleichen(name)

    def stil_entfernen(self, name: str) -> None:
        if name in self.sitzung.dokument.vorlagen:
            self.ansicht._aendern(lambda s: s.vorlage_loeschen(name))

    def stil_tasten(self) -> None:
        """Tastenkombinationen der Formatvorlagen (``taste`` im Katalog) auf der Zeichenfläche setzen."""
        from PySide6.QtGui import QKeySequence, QShortcut
        from core.editor.text import stile
        for k in getattr(self, "_stil_kuerzel", []):
            k.setParent(None)
            k.deleteLater()
        self._stil_kuerzel = []
        for name in stile.namen():
            taste = stile.definition(name).get("taste")
            if taste:
                sc = QShortcut(QKeySequence(taste), self.ansicht)
                sc.activated.connect(lambda n=name: self.apply_style(n))
                self._stil_kuerzel.append(sc)

    # ---- Abschnitte -------------------------------------------------------------------------------------------------------------------------
    def apply_design(self, text_schrift: str | None, kopf_schrift: str | None, farbe: str | None) -> None:
        """Dokumentdesign (Entwurf ▸ Design): Schrift des Fließtextes, Schrift und Farbe der Überschriften — über die Formatvorlagen des Dokuments."""
        def f(s):
            with s.gruppe("Design"):
                for name, v in list(s.dokument.vorlagen.items()):
                    z = dict(v.zeichen)
                    if v.ebene > 0:
                        if kopf_schrift:
                            z["schrift"] = kopf_schrift
                        if farbe:
                            z["farbe"] = farbe
                    elif text_schrift and name == "Standard":
                        z["schrift"] = text_schrift
                    if z != v.zeichen:
                        s.vorlage_setzen(dataclasses.replace(v, zeichen=z))
        self.ansicht._aendern(f)

    def abschnitt_einfuegen(self, art: str = "naechste") -> int:
        nr = [0]

        def f(s):
            nr[0] = s.abschnitt_einfuegen(beginn=art)
        self.ansicht._aendern(f)
        return nr[0]

    def abschnitt_entfernen(self) -> bool:
        n = self.abschnitt_nr()
        if n < 1:
            return False
        return self.ansicht._aendern(lambda s: s.abschnitt_entfernen(n, "vorher"))

    def abschnitt_gehe(self, n: int) -> None:
        d = self.sitzung.dokument
        if 0 <= n < len(d.abschnitte):
            erster = next((b for b in d.abschnitte[n].bloecke if hasattr(b, "inhalte")), None)
            if erster is not None:
                self.sitzung.setze_auswahl(Position(erster.id, 0))
                self.ansicht.nach_bewegung()

    def seite_letzter_block(self):
        """Der letzte Absatz des Haupttextes (für Seiten, die am Ende des Dokuments eingefügt werden)."""
        return list(self.sitzung.dokument.absaetze())[-1]

    # ---- Verknüpfung ---------------------------------------------------------------------------------------------------------------------
    def insert_link(self, href: str, text: str | None = None, tipp: str = "") -> None:
        """Verknüpfung auf die Auswahl; ohne Auswahl und mit ``text`` wird der Text eingefügt, sonst gilt sie für das Wort an der Schreibmarke."""
        def f(s):
            with s.gruppe("Hyperlink"):
                if s.auswahl.leer and text:
                    s.link_setzen(href, None, text)
                else:
                    s.link_setzen(href)
                if tipp:
                    s.zeichenformat_anwenden({"tooltip": tipp}, s.auswahl if not s.auswahl.leer else None)
        self.ansicht._aendern(f)

    # ---- Noten -------------------------------------------------------------------------------------------------------------------------------
    def note_loeschen(self, art: str, note_id: int) -> None:
        self.ansicht._aendern(lambda s: s.note_loeschen(art, note_id))

    # ---- Ersetzen im Rohtext ---------------------------------------------------------------------------------------------------------------
    def rohtext(self) -> str:
        """Der Text des Dokuments mit U+2029 zwischen den Absätzen (Stellen wie bei ``textCursor().position()``)."""
        from core.bearbeitung.suche import roh_text
        return roh_text(self.sitzung.dokument)

    def replace_range(self, von: int, bis: int, neu: str, erwartet: str | None = None, markdown: bool = False) -> bool:
        """Ersetzt [von, bis) des Rohtextes durch ``neu``; mit ``erwartet`` nur, wenn dort noch dieser Text steht. ``markdown``: Auszeichnungen
        (Überschriften, Listen, Fett) werden als Formate umgesetzt."""
        from core.bearbeitung.suche import roh_text
        roh = roh_text(self.sitzung.dokument)
        if erwartet is not None and roh[von:bis] != erwartet:
            return False
        if markdown:
            return self._markdown_ersetzen(von, bis, neu)
        self.ersetze_roh(von, bis, neu)
        return True

    def _markdown_ersetzen(self, von: int, bis: int, neu: str) -> bool:
        from core.bearbeitung.suche import offset_zu_position
        bloecke = markdown_bloecke(neu)
        anfang = offset_zu_position(self.sitzung.dokument, von)
        for b in bloecke:
            if b["vorlage"]:
                self._vorlage_abgleichen(b["vorlage"])

        def f(s):
            with s.gruppe("Ersetzen"):
                ende = s.ersetzen_durch(von, bis, "\u2029".join(b["text"] for b in bloecke), None, None)
                absaetze = list(s.dokument.absaetze())
                letzter = next(k for k, a in enumerate(absaetze) if a.id == ende.absatz_id)
                ziele = absaetze[letzter - len(bloecke) + 1:letzter + 1]
                for k, (b, a) in enumerate(zip(bloecke, ziele)):
                    basis = anfang.versatz if k == 0 and a.id == anfang.absatz_id else 0
                    if b["vorlage"] and basis == 0:
                        s.vorlage_anwenden(b["vorlage"], absatz_ids=[a.id])
                    if b["liste"] and basis == 0:
                        s.liste_anwenden(s.liste_anlegen(b["liste"]), absatz_ids=[a.id])
                    for st, en, fmt in b["laeufe"]:
                        s.zeichenformat_anwenden(fmt, Auswahl(Position(a.id, basis + st), Position(a.id, basis + en)))
        return self.ansicht._aendern(f)

    def ersetze_verfolgt(self, von: int, bis: int, neu: str, autor: str = "") -> bool:
        """Wie ``replace_range``, aber als nachverfolgte Änderung des Bearbeiters ``autor``."""
        s = self.sitzung
        vorher = (s.nachverfolgen, getattr(s, "autor", ""))
        s.nachverfolgen = True
        try:
            ok = self.ansicht._aendern(lambda sitz: (setattr(sitz, "autor", autor or sitz.autor), sitz.ersetzen_durch(von, bis, neu, None, None)))
        finally:
            s.nachverfolgen = vorher[0]
        return ok

    # ---- Tabellen: Gestaltung ---------------------------------------------------------------------------------------------------------------
    def _zellen_der_auswahl(self):
        """(Tabelle, [(Zeile, Spalte)]) der Zellen der Auswahl (sonst der Zelle der Schreibmarke); ``None`` außerhalb einer Tabelle."""
        r = self.zellen_im_bereich()
        if r is None:
            return None
        tabelle = self.sitzung._tabelle(r[0])
        return tabelle, [(z, s) for z, s in r[1] if tabelle.zellen[z][s].verdeckt_von is None]

    @staticmethod
    def _absaetze_der_zelle(zelle) -> list:
        return [b.id for b in zelle.bloecke if hasattr(b, "inhalte")]

    def tabelle_rahmen_umschalten(self) -> bool:
        t = self.tabelle_an_marke()
        if t is None:
            return False
        an = float(t.tabelle.format.get("rahmen_breite") or 0) > 0
        return self.tabellenformat({"rahmen_breite": None if an else 1.0, "rahmen_farbe": None if an else TABELLENRAND_STANDARD, "rahmen_art": None if an else "einfach"})

    def tabelle_rahmen_an(self) -> bool:
        t = self.tabelle_an_marke()
        return t is not None and float(t.tabelle.format.get("rahmen_breite") or 0) > 0

    def tabelle_rahmen_linie(self, linie) -> bool:
        """Rahmen der Tabelle aus einer ``Linie`` (``None`` = ohne Rahmen)."""
        if linie is None:
            return self.tabellenformat({"rahmen_breite": None, "rahmen_farbe": None, "rahmen_art": None})
        return self.tabellenformat({"rahmen_breite": max(1.0, linie.breite_pt / 0.75), "rahmen_farbe": linie.farbe, "rahmen_art": linie.art})

    def tabelle_rahmen_lesen(self):
        from core.editor.objekte.formen.linie import Linie
        t = self.tabelle_an_marke()
        f = t.tabelle.format if t is not None else {}
        if float(f.get("rahmen_breite") or 0) <= 0:
            return None
        return Linie(f.get("rahmen_farbe") or TABELLENRAND_STANDARD, round(f["rahmen_breite"] * 0.75, 2), f.get("rahmen_art") or "einfach", "tblr")

    def zell_fuellung(self):
        r = self._zellen_der_auswahl()
        return r[0].zellen[r[1][0][0]][r[1][0][1]].format.get("hintergrund") if r and r[1] else None

    def tabelle_optionen(self) -> dict:
        """Kopfzeile, Streifen, erste Spalte und Vorlage der Tabelle an der Schreibmarke."""
        t = self.tabelle_an_marke()
        f = t.tabelle.format if t is not None else {}
        bits = int(f.get("optionen") or 0)
        return {"gesetzt": "optionen" in f or "vorlage" in f, "kopf": bool(bits & 1), "streifen": bool(bits & 2), "spalte": bool(bits & 4), "vorlage": f.get("vorlage", "")}

    def tabelle_vorlage_anwenden(self, name: str, kopf: bool, streifen: bool, spalte: bool) -> bool:
        """Wendet eine Tabellenvorlage (Füllungen, Fettdruck, Rahmen) auf die Zellen an; die Optionen bleiben an der Tabelle gespeichert."""
        from core.editor.tabelle import tabellenstil as TS
        t = self.tabelle_an_marke()
        if t is None or name not in TS.VORLAGEN:
            return False
        kopf_fill, kopf_schrift, streifen_fill, rahmen = TS.VORLAGEN[name]
        tid = t.id

        def f(s):
            with s.gruppe("Tabellenformatvorlage"):
                tab = s._tabelle(tid)
                s.tabellenformat_anwenden(tid, {"vorlage": name, "optionen": (1 if kopf else 0) | (2 if streifen else 0) | (4 if spalte else 0) or None,
                                                "kopfzeilen": 1 if kopf else None, "rahmen_breite": 1.0 if rahmen else None,
                                                "rahmen_farbe": TABELLENRAND_STANDARD if rahmen else None, "rahmen_art": "einfach" if rahmen else None})
                for z in range(tab.zeilen):
                    for sp in range(tab.spalten):
                        zelle = tab.zellen[z][sp]
                        if zelle.verdeckt_von is not None:
                            continue
                        grund = TS._zeilengrund(z, kopf, kopf_fill, streifen_fill if streifen else "") or None
                        s.zellformat_anwenden(tid, {"hintergrund": grund}, [(z, sp)])
                        ist_kopf = kopf and z == 0
                        fett = ist_kopf or (spalte and sp == 0)
                        ids = self._absaetze_der_zelle(zelle)
                        if ids and (fett or sp == 0 or z == 0):
                            farbe = kopf_schrift if ist_kopf and kopf_fill else None
                            ende = s._absatz(ids[-1]).laenge
                            s.zeichenformat_anwenden({"fett": True if fett else None, "farbe": farbe}, Auswahl(Position(ids[0], 0), Position(ids[-1], ende)))
        return self.ansicht._aendern(f)

    def tabelle_option_umschalten(self, schluessel: str) -> None:
        o = self.tabelle_optionen()
        o[schluessel] = not o[schluessel]
        if o["vorlage"]:
            self.tabelle_vorlage_anwenden(o["vorlage"], o["kopf"], o["streifen"], o["spalte"])
        else:
            self.tabellenformat({"optionen": (1 if o["kopf"] else 0) | (2 if o["streifen"] else 0) | (4 if o["spalte"] else 0) or None,
                                 "kopfzeilen": 1 if o["kopf"] else None})

    def zell_senkrecht(self, wo: str) -> bool:
        return self.zellformat({"vertikal": wo})

    def zell_waagrecht(self, ausrichtung: str) -> bool:
        r = self._zellen_der_auswahl()
        if r is None:
            return False
        ids = [i for z, s in r[1] for i in self._absaetze_der_zelle(r[0].zellen[z][s])]
        return bool(ids) and self.ansicht._aendern(lambda s: s.absatzformat_anwenden({"ausrichtung": ausrichtung}, absatz_ids=ids))

    def zell_richtung(self, richtung: str) -> bool:
        r = self._zellen_der_auswahl()
        if r is None:
            return False
        ids = [i for z, s in r[1] for i in self._absaetze_der_zelle(r[0].zellen[z][s])]

        def f(s):
            with s.gruppe("Textrichtung"):
                s.zellformat_anwenden(r[0].id, {"textrichtung": richtung}, r[1])
                if ids:
                    s.absatzformat_anwenden({"richtung": richtung}, absatz_ids=ids)
        return self.ansicht._aendern(f)

    def tabelle_gitternetz_an(self) -> bool:
        t = self.tabelle_an_marke()
        return t is not None and str(t.tabelle.zellen[0][0].format.get("rahmen_oben", "")).startswith(GITTER_FARBE)

    def tabelle_gitternetz(self) -> bool:
        t = self.tabelle_an_marke()
        if t is None:
            return False
        an = not self.tabelle_gitternetz_an()
        kante = f"{GITTER_FARBE}|0.75|gestrichelt" if an else None
        alle = [(z, s) for z in range(t.tabelle.zeilen) for s in range(t.tabelle.spalten) if t.tabelle.zellen[z][s].verdeckt_von is None]
        return self.ansicht._aendern(lambda s: s.zellformat_anwenden(t.id, {f"rahmen_{k}": kante for k in ("oben", "unten", "links", "rechts")}, alle))

    def zellmasse(self):
        """(Breite, Höhe) der Zelle an der Schreibmarke in Bildpunkten, wie sie das Layout setzt; ``None`` außerhalb einer Tabelle."""
        t = self.tabelle_an_marke()
        if t is None:
            return None
        for seite in self.ansicht.ergebnis().seiten:
            for p in seite.plaetze:
                if p.art == "zelle" and p.block_id == t.id and not p.kopie and p.zeile == t.zeile and p.spalte == t.tabelle.anker(t.zeile, t.spalte)[1]:
                    return p.rect.width, p.rect.height
        return None

    def spalte_breite_setzen(self, mm: float) -> bool:
        t = self.tabelle_an_marke()
        if t is None or mm <= 0:
            return False
        sp = t.tabelle.anker(t.zeile, t.spalte)[1]
        breiten = self._spaltenbreiten_gemessen(t)
        breiten[sp] = mm_to_px(mm)
        return self.ansicht._aendern(lambda s: s.spaltenbreiten_setzen(t.id, breiten))

    def zeile_hoehe_setzen(self, mm: float) -> bool:
        t = self.tabelle_an_marke()
        if t is None or mm <= 0:
            return False
        return self.ansicht._aendern(lambda s: s.zeilenhoehen_setzen(t.id, {t.tabelle.anker(t.zeile, t.spalte)[0]: mm_to_px(mm)}))

    def _spaltenbreiten_gemessen(self, t) -> list:
        """Breiten aller Spalten: die gesetzten, sonst die vom Layout gemessenen."""
        breiten = list(t.tabelle.spaltenbreiten)
        if all(b > 0 for b in breiten):
            return breiten
        gemessen = {}
        for seite in self.ansicht.ergebnis().seiten:
            for p in seite.plaetze:
                if p.art == "zelle" and p.block_id == t.id and not p.kopie and p.spalte >= 0:
                    gemessen.setdefault(p.spalte, p.rect.width)
        return [b if b > 0 else gemessen.get(i, 96.0) for i, b in enumerate(breiten)]

    def tabelle_anpassen(self, art: str) -> bool:
        """``inhalt``, ``fenster``, ``spalten_gleich``, ``zeilen_gleich``, ``fest``."""
        t = self.tabelle_an_marke()
        if t is None:
            return False
        n = t.tabelle.spalten
        if art == "inhalt":
            return self.ansicht._aendern(lambda s: (s.spaltenbreiten_setzen(t.id, [0.0] * n), s.zeilenhoehen_setzen(t.id, [0.0] * t.tabelle.zeilen),
                                                    s.tabellenformat_anwenden(t.id, {"breite_art": "auto", "breite": None})))
        if art == "fenster":
            breite = self.page.content_width_px
            return self.ansicht._aendern(lambda s: (s.spaltenbreiten_setzen(t.id, [breite / n] * n), s.tabellenformat_anwenden(t.id, {"breite_art": "prozent", "breite": 100.0})))
        if art == "spalten_gleich":
            breiten = self._spaltenbreiten_gemessen(t)
            return self.ansicht._aendern(lambda s: s.spaltenbreiten_setzen(t.id, [sum(breiten) / n] * n))
        if art == "zeilen_gleich":
            hoehen = [p.rect.height for seite in self.ansicht.ergebnis().seiten for p in seite.plaetze
                      if p.art == "zelle" and p.block_id == t.id and not p.kopie and p.spalte == 0]
            return bool(hoehen) and self.ansicht._aendern(lambda s: s.zeilen_gleich(t.id, max(hoehen)))
        if art == "fest":
            breiten = self._spaltenbreiten_gemessen(t)
            return self.ansicht._aendern(lambda s: s.spaltenbreiten_setzen(t.id, breiten))
        return False

    # ---- Menüs, Minileiste, Verknüpfungen ---------------------------------------------------------------------------------------------------
    def installEventFilter(self, filter_) -> None:
        """Ereignisfilter (Minileiste) gehören an die Zeichenfläche, auf der Tasten und Maus ankommen."""
        self.ansicht.installEventFilter(filter_)

    def canPaste(self) -> bool:
        from PySide6.QtGui import QGuiApplication
        m = QGuiApplication.clipboard().mimeData()
        return m is not None and (m.hasText() or m.hasImage() or m.hasFormat("application/x-lunivo-ausschnitt") or m.hasHtml())

    def mini_zeigen(self, pos) -> None:
        """Minileiste über der Auswahl (nach dem Auswählen mit der Maus)."""
        if callable(self.mini_hook) and not self.isReadOnly():
            self.mini_hook(self, pos)

    def kontextmenue_zeigen(self, pos) -> None:
        """Das Rechtsklickmenü an der Stelle zeigen (Text, Tabelle oder gewähltes Objekt); die Schreibhilfe ergänzt Vorschläge, die Minileiste steht daneben."""
        if self.fenster is None:
            return
        from vcl.qt.widgets.bausteine.bauteile.kontextmenue import menue_bauen
        if self.objekt_gewaehlt() is not None:
            from vcl.qt.widgets.bausteine.bauteile.kontextmenue import objektmenue_bauen
            m = objektmenue_bauen(self, self.fenster)
        else:
            m = menue_bauen(self, self.fenster)
            if callable(self.kontext_hook):
                self.kontext_hook(m, self.textCursor().position())
        if callable(self.mini_hook) and not self.isReadOnly():
            self.mini_hook(self, pos, True, m.sizeHint())
        m.exec(pos)
        m.deleteLater()
        if callable(self.mini_hook):
            self.mini_hook(None, None)

    def verknuepfung_folgen(self, ziel: str) -> None:
        """Strg+Klick auf eine Verknüpfung: ``#Name`` springt zur Textmarke, sonst öffnet das System die Adresse."""
        if ziel.startswith("#"):
            marken = self.sitzung.textmarken()
            if ziel[1:] in marken:
                self.sitzung.setze_auswahl(marken[ziel[1:]].anker, marken[ziel[1:]].kopf)
                self.ansicht.nach_bewegung()
            return
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        QDesktopServices.openUrl(QUrl(ziel if "://" in ziel or ziel.startswith("mailto:") else "https://" + ziel))

    # ---- Tabellen: Maus (Griffe, Ränder, Stift, Radiergummi) ---------------------------------------------------------------------------------
    def tabellen_verbinden(self) -> None:
        """Belegt die Rückrufe der Zeichenfläche für die Tabellenbedienung."""
        a = self.ansicht
        a.tabelle_aktiv = lambda: (lambda t: t.id if t is not None else None)(self.tabelle_an_marke())
        a.tabelle_aendern = self.tabelle_maus_aendern
        a.tabelle_waehlen = self.tabelle_ganz_waehlen
        a.tabelle_zeichnen = self.tabelle_zeichnen_an
        a.tabelle_linie_loeschen = self.tabelle_zellen_vereinen

    def tabelle_ganz_waehlen(self, tid: int) -> None:
        """Wählt die ganze Tabelle (von der ersten bis zur letzten Zelle) und zeigt die Minileiste."""
        t = self.sitzung._tabelle(tid)
        von = self.sitzung.zelle_anfang(tid, 0, 0)
        letzte = t.zellen[-1][-1]
        letzte = t.zellen[t.anker(t.zeilen - 1, t.spalten - 1)[0]][t.anker(t.zeilen - 1, t.spalten - 1)[1]]
        ids = [b.id for b in letzte.bloecke if hasattr(b, "inhalte")]
        bis = Position(ids[-1], self.sitzung._absatz(ids[-1]).laenge) if ids else von
        self.sitzung.setze_auswahl(von, bis)
        self.ansicht.nach_bewegung()
        if callable(self.mini_hook):
            self.mini_per_griff = True
            from PySide6.QtGui import QCursor
            self.mini_hook(self, QCursor.pos())

    def tabelle_maus_aendern(self, art: str, tid: int, wert) -> None:
        t = self.sitzung._tabelle(tid)
        if art == "spalte_plus":
            self.ansicht._aendern(lambda s: s.spalten_einfuegen(tid, t.spalten))
        elif art == "zeile_plus":
            self.ansicht._aendern(lambda s: s.zeilen_einfuegen(tid, t.zeilen))
        elif art == "skalieren":
            self.ansicht._aendern(lambda s: s.tabelle_skalieren(tid, wert[0], wert[1]))
        elif art == "spalte":                               # Rand rechts der Spalte ``index`` um ``delta`` verschieben: die Nachbarspalte gibt ab oder bekommt
            index, delta = wert
            breiten = self._spaltenbreiten_gemessen(self.tabelle_an_marke() if self.tabelle_an_marke() and self.tabelle_an_marke().id == tid else _TabellenRef(t))
            if index + 1 < len(breiten):
                delta = max(-(breiten[index] - 12.0), min(breiten[index + 1] - 12.0, delta))
                breiten[index] += delta
                breiten[index + 1] -= delta
            else:
                breiten[index] = max(12.0, breiten[index] + delta)
            self.ansicht._aendern(lambda s: s.spaltenbreiten_setzen(tid, breiten))
        elif art == "zeile":
            index, delta = wert
            aktuell = t.zeilenhoehen[index] or self._zeilenhoehe_gemessen(tid, index)
            self.ansicht._aendern(lambda s: s.zeilenhoehen_setzen(tid, {index: max(8.0, aktuell + delta)}))

    def _zeilenhoehe_gemessen(self, tid: int, zeile: int) -> float:
        for seite in self.ansicht.ergebnis().seiten:
            for p in seite.plaetze:
                if p.art == "zelle" and p.block_id == tid and not p.kopie and p.zeile == zeile:
                    return p.rect.height
        return 20.0

    def tabelle_zeichnen_an(self, stelle, zeilen: int, spalten: int) -> None:
        """Tabelle mit dem Stift gezeichnet: sie entsteht an der Stelle, an der das Ziehen begann."""
        def f(s):
            with s.gruppe("Tabelle zeichnen"):
                s.setze_auswahl(stelle)
                s.tabelle_einfuegen(zeilen, spalten)
        self.ansicht._aendern(f)

    def tabelle_zellen_vereinen(self, tid: int, a: tuple, b: tuple) -> None:
        """Radiergummi: die Zellen ``a`` und ``b`` (Anker) werden zu einer Zelle verbunden, wenn sie ein Rechteck bilden."""
        t = self.sitzung._tabelle(tid)
        za, zb = t.zellen[a[0]][a[1]], t.zellen[b[0]][b[1]]
        z1, s1 = min(a[0], b[0]), min(a[1], b[1])
        z2 = max(a[0] + za.zeilenspanne, b[0] + zb.zeilenspanne)
        s2 = max(a[1] + za.spaltenspanne, b[1] + zb.spaltenspanne)
        flaeche = za.zeilenspanne * za.spaltenspanne + zb.zeilenspanne * zb.spaltenspanne
        if flaeche != (z2 - z1) * (s2 - s1):
            return
        self.ansicht._aendern(lambda s: s.zellen_verbinden(tid, z1, s1, z2 - z1, s2 - s1))


    # ---- Quellen, Zitierweise, Seitenzahlen ------------------------------------------------------------------------------------------
    @property
    def quellen(self) -> list:
        """Die Literaturquellen des Dokuments (Kopie; ändern über ``quelle_hinzufuegen`` und ``quelle_entfernen``)."""
        return [dict(q) for q in self.sitzung.dokument.quellen]

    @property
    def zitierweise(self) -> str:
        return str(self.sitzung.dokument.eigenschaften.get("zitierweise") or "APA")

    @zitierweise.setter
    def zitierweise(self, name: str) -> None:
        self.ansicht._aendern(lambda s: s.eigenschaft_setzen("zitierweise", name))

    def quelle_hinzufuegen(self, q: dict) -> None:
        self.ansicht._aendern(lambda s: s.quelle_setzen(q))

    def quelle_entfernen(self, tag: str) -> None:
        self.ansicht._aendern(lambda s: s.quelle_loeschen(tag))

    def seiten_von(self, offsets: list) -> list:
        """Die angezeigten Seitenzahlen der Stellen im Rohtext (``"?"``, wenn eine Stelle nirgends steht)."""
        erg = self.ansicht.ergebnis()
        d = self.sitzung.dokument
        aus = []
        for o in offsets:
            seite = erg.seite_von(offset_zu_position(d, o).absatz_id)
            aus.append(str(erg.seiten[seite].nummer or seite + 1) if seite is not None else "?")
        return aus


    def _formular_klick(self, pos: int) -> bool:
        """Klick auf ein Formularfeld (Kontrollkästchen, Auswahl, Datum, Text, Schaltfläche)."""
        from core.editor.dokument import formular
        return formular.klick(self, pos, self.fenster)


    # ---- Abschnitte: Seiteneinrichtung je Abschnitt -----------------------------------------------------------------------------------
    def abschnitt_seite(self, nr: int | None = None):
        """Die Seiteneinrichtung des Abschnitts ``nr`` (ohne Angabe: an der Schreibmarke) als Kopie zum Ändern."""
        n = self.abschnitt_nr() if nr is None else nr
        return self.sitzung.dokument.abschnitte[n].seite.copy()

    def abschnitt_seite_setzen(self, nr: int, seite) -> None:
        self.ansicht._aendern(lambda s: s.seite_ersetzen(nr, seite))
        self.pageApplied.emit()

    def abschnitte_anzahl(self) -> int:
        return len(self.sitzung.dokument.abschnitte)

    def abschnitt_beginn(self, nr: int) -> str:
        return self.sitzung.dokument.abschnitte[nr].beginn

    def abschnitt_beginn_setzen(self, nr: int, art: str) -> None:
        self.ansicht._aendern(lambda s: s.abschnitt_beginn_setzen(nr, art))

    def seitenzahl_anwenden(self, w: dict) -> None:
        """Seitenzahl nach den Werten des Fensters: für das ganze Dokument, ab der aktuellen Seite (neuer Abschnitt) oder den aktuellen Abschnitt."""
        from core.funktionen.kopffuss import seitenzahl as SZ

        def f(s):
            with s.gruppe("Seitenzahl"):
                if w["bereich"] == "dokument":
                    ziele = list(range(len(s.dokument.abschnitte)))
                elif w["bereich"] == "seite":
                    erg = self.ansicht.ergebnis()
                    seite = max(0, self.current_page() - 1)
                    erster = next((p.block_id for p in erg.seiten[seite].plaetze if p.art == "zeile"), s.auswahl.kopf.absatz_id)
                    ziele = [s.abschnitt_einfuegen(Position(erster, 0), "naechste")]
                else:
                    ziele = [self.abschnitt_nr()]
                for i, nr in enumerate(ziele):
                    ps = SZ.seitenzahl_setzen(s.dokument.abschnitte[nr].seite.copy(), w["ort"], w["ausrichtung"], w["muster"], w["format"],
                                              w["start"] if i == 0 else 0, w["kapitel"])
                    s.seite_ersetzen(nr, ps)
        self.ansicht._aendern(f)
        self.pageApplied.emit()


    def seite_letzter_block(self):
        """Der letzte Absatz des Haupttextes, der auf der Seite der Schreibmarke beginnt."""
        erg = self.ansicht.ergebnis()
        seite = erg.seite_von(self.sitzung.auswahl.kopf.absatz_id)
        aus = None
        for aid in erg.reihenfolge:
            if erg.seite_von(aid) == seite and aid in {a.id for a in self.sitzung.dokument.absaetze()}:
                aus = aid
        return self.sitzung._absatz(aus if aus is not None else self.sitzung.auswahl.kopf.absatz_id)

    def leere_seite(self, quer: bool | None = None) -> None:
        """Ein neues, leeres Blatt hinter der Seite der Schreibmarke; der Text wird nicht geteilt. Hat das Blatt eine andere Ausrichtung als der
        Abschnitt, bekommt es einen eigenen Abschnitt (der Text danach geht in der alten Ausrichtung weiter)."""
        einrichtung = self.abschnitt_seite()
        eigene = quer is not None and bool(quer) != einrichtung.landscape

        def f(s):
            with s.gruppe("Leere Seite"):
                letzter = self.seite_letzter_block()
                absaetze = list(s.dokument.absaetze())
                nach = next((absaetze[i + 1] for i, a in enumerate(absaetze) if a.id == letzter.id and i + 1 < len(absaetze)), None)
                neu = s.absatz_teilen(Position(letzter.id, letzter.laenge))
                s.absatzformat_anwenden({"seitenumbruch_vor": True, "seitenumbruch_nach": True}, absatz_ids=[neu.absatz_id])
                if eigene:
                    blatt = einrichtung.copy()
                    blatt.set_orientation(bool(quer))
                    s.abschnitt_einfuegen(Position(neu.absatz_id, 0), "naechste", blatt)
                    if nach is not None:
                        s.abschnitt_einfuegen(Position(nach.id, 0), "naechste", einrichtung)
                s.setze_auswahl(Position(neu.absatz_id, 0))
        self.ansicht._aendern(f)


    def note_text_setzen(self, art: str, note_id: int, text: str) -> None:
        """Ändert den Text einer Fuß- oder Endnote (tippt das Feld „Noten“, ein Rückgängig-Schritt je Pause)."""
        self.ansicht._aendern(lambda s: s.note_aendern(art, note_id, text))
        self.zusatzGeaendert.emit()


    # ---- Lage der Blätter (für Kopf- und Fußzeilenfelder über dem Blatt) -------------------------------------------------------------
    def _blatt(self, i: int) -> dict:
        """Lage des Blattes ``i`` in der Ansicht: ``x`` links, ``H`` Höhe, ``ml`` linker Rand und ``cw`` Textbreite (Bildpunkte der Ansicht)."""
        erg = self.ansicht.ergebnis()
        i = max(0, min(i, len(erg.seiten) - 1))
        r, e, z = self.ansicht.blatt(i), erg.seiten[i].einrichtung, self.ansicht.zoom
        return {"x": r.left(), "H": r.height(), "ml": mm_to_px(e.margin_left_mm) * z if e is not None else 0.0,
                "cw": e.content_width_px * z if e is not None else r.width()}

    def blatt_oben(self, i: int) -> float:
        return self.ansicht.blatt(max(0, min(i, len(self.ansicht.ergebnis().seiten) - 1))).top()

    def _blatt_bei_y(self, y: float) -> int:
        from PySide6.QtCore import QPointF
        return self.ansicht._naechstes_blatt(QPointF(0.0, y))

    def cursorRect(self):
        r = self.ansicht.cursor_flaeche()
        return r.toRect() if r is not None else self.ansicht.rect()

    def seitenzahl_zone(self, bereich: str, zone: str, ausr: str, muster: str, zahl: str) -> None:
        """Seitenzahl in Kopf- oder Fußzeile (``zone``) für das Dokument, ab der aktuellen Seite (neuer Abschnitt) oder den aktuellen Abschnitt."""
        from core.funktionen.kopffuss import seitenzahl as SZ

        def f(s):
            with s.gruppe("Seitenzahl"):
                if bereich == "dokument":
                    ziele = list(range(len(s.dokument.abschnitte)))
                elif bereich == "seite":
                    erg = self.ansicht.ergebnis()
                    erster = next((p.block_id for p in erg.seiten[max(0, self.current_page() - 1)].plaetze if p.art == "zeile"), s.auswahl.kopf.absatz_id)
                    ziele = [s.abschnitt_einfuegen(Position(erster, 0), "naechste")]
                else:
                    ziele = [self.abschnitt_nr()]
                for nr in ziele:
                    s.seite_ersetzen(nr, SZ.seitenzahl_setzen(s.dokument.abschnitte[nr].seite.copy(), zone, ausr, muster, zahl))
        self.ansicht._aendern(f)
        self.pageApplied.emit()


    def gliederung_ebene(self, delta: int) -> None:
        """Gliederungsansicht: Überschrift des Absatzes um ``delta`` Ebenen herauf- (−1) oder herabstufen (+1); Ebene 0 ist Fließtext."""
        from core.dokument.formatvorlagen import ueberschriftsebene
        a = self._absatz_an_marke()
        neu = max(0, min(9, ueberschriftsebene(self.sitzung.dokument, a) + delta))
        self.apply_style("Standard" if neu == 0 else f"Überschrift {neu}")


    # ---- Sprechblasen ------------------------------------------------------------------------------------------------------------------
    def blasen_setzen(self, konfig: dict | None, schrift: str = "mittel") -> None:
        """Einstellungen der Sprechblasen im Seitenrand (``sprechblasen.konfig_lesen``) übernehmen und neu setzen."""
        a = self.ansicht
        a.blasen_konfig, a.blasen_schrift = konfig, schrift
        a.blasen_hook = self._blase_aktion
        a._groesse_setzen()
        a.update()

    def _blase_aktion(self, art: str, kid: int, pos) -> None:
        if art == "bearbeiten":
            self.kommentar_bearbeiten(kid)
            return
        from vcl.qt.widgets.bausteine.dropdown.menue_liste import MenueListe
        k = self.kommentare.get(kid, {})
        geloest = bool(k.get("geloest"))
        m = MenueListe(self.widget())
        m.eintrag("Bearbeiten", lambda: self.kommentar_bearbeiten(kid))
        m.eintrag("Wieder öffnen" if geloest else "Als gelöst markieren", lambda: self.kommentar_geloest(kid, not geloest))
        m.trenner()
        m.eintrag("Löschen", lambda: self.kommentar_loeschen(kid))
        m.exec(pos)

    def kommentar_bearbeiten(self, kid: int) -> None:
        """Fragt den neuen Text des Kommentars und setzt ihn."""
        from PySide6.QtWidgets import QInputDialog
        alt = self.kommentare.get(kid, {}).get("text", "")
        text, ok = QInputDialog.getMultiLineText(self.widget(), "Kommentar bearbeiten", "Kommentar:", alt)
        if ok:
            self.kommentar_text_setzen(kid, text)
            self.zusatzGeaendert.emit()


    # ---- Auswählen ---------------------------------------------------------------------------------------------------------------------
    def tabelle_ohne_rahmen_waehlen(self) -> bool:
        """Markiert die nächste Tabelle ohne Rahmen hinter der Schreibmarke (am Ende geht es vorn weiter). → ``False``, wenn es keine gibt."""
        from core.editor.dokument import gehe_zu as G
        dok = self.sitzung.dokument
        stellen = G._stellen(dok)
        alle = sorted((p, t) for a in dok.abschnitte for t, p in G._tabellen(a.bloecke, stellen) if float(t.format.get("rahmen_breite") or 0) <= 0)
        if not alle:
            return False
        hier = self.textCursor().selectionEnd()
        p, t = next(((p, t) for p, t in alle if p >= hier), alle[0])
        self.select_range(p, p)
        self.tabelle_ganz_waehlen(t.id)
        self.ensureCursorVisible()
        return True

    def aehnlich_formatiert(self) -> list:
        """Alle Strecken (Stellen im Rohtext) mit derselben Zeichenformatierung wie das Zeichen an der Schreibmarke."""
        merkmale = ("schrift", "groesse_pt", "fett", "kursiv", "unterstrichen", "durchgestrichen", "farbe", "marker", "hoch_tief", "kapitaelchen", "grossbuchstaben")
        dok = self.sitzung.dokument
        soll = tuple(self._zeichen().get(k) for k in merkmale)
        aus, n = [], 0
        for a in dok.absaetze():
            versatz = 0
            for x in a.inhalte:
                laenge = len(x.text) if hasattr(x, "text") else 1
                if hasattr(x, "text") and x.text.strip():
                    fmt = F.zeichenformat(dok, a, x.format)
                    if tuple(fmt.get(k) for k in merkmale) == soll:
                        v, e = n + versatz, n + versatz + laenge
                        if aus and aus[-1][1] == v:
                            aus[-1] = (aus[-1][0], e)
                        else:
                            aus.append((v, e))
                versatz += laenge
            n += a.laenge + 1
        return aus

    def naechstes_objekt_waehlen(self) -> bool:
        """Springt zum nächsten Objekt (im Text oder frei positioniert) hinter der Schreibmarke und wählt es (am Ende geht es vorn weiter)."""
        from core.dokument.dokument import InlineObjekt
        from core.editor.dokument import gehe_zu as G
        dok = self.sitzung.dokument
        stellen = G._stellen(dok)
        liste = []
        for a in dok.absaetze():
            versatz = 0
            for x in a.inhalte:
                if isinstance(x, InlineObjekt):
                    liste.append((stellen[a.id] + versatz, "text", x.id))
                    versatz += 1
                else:
                    versatz += len(x.text)
        liste += [(stellen.get(o.anker, 0), "frei", o.id) for o in dok.objekte.values()]
        liste.sort()
        if not liste:
            return False
        hier = self.textCursor().selectionEnd()
        _p, art, oid = next((x for x in liste if x[0] >= hier), liste[0])
        if art == "frei":
            self.ansicht.gewaehltes_objekt = oid
            self.freiAuswahlGeaendert.emit()
            self.ansicht.update()
        else:
            self.inline_waehlen(oid)
        self.setFocus()
        return True


class _TabellenRef:
    """Wie ``KernTabelle``, wenn die Tabelle nicht an der Schreibmarke steht (nur Id und Tabelle)."""

    def __init__(self, tabelle):
        self.tabelle, self.id = tabelle, tabelle.id
