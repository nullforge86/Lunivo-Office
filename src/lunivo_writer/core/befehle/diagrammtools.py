"""Befehle: Kontext-Reiter „Diagrammtools“ für das Diagramm als freies Objekt (``editor/frei_objekt.py``, Art ``diagramm``).

Alle ``diagramm…``-Befehle ändern die Daten des gewählten Diagramms über ``FO.aendern`` und zeichnen es neu (``editor/diagramm.py``).
Gespeichert sind: ``art`` (Diagrammart), ``titel``, ``kategorien``, ``reihen``, ``kombi``, ``farben`` sowie die Darstellung
``titel_an``, ``legende``, ``legende_pos``, ``labels`` und ``stil`` (fehlt eine Angabe, gilt der Standard).
Ein Baustein von ``Befehle`` (siehe ``core/commands.py``)."""
from __future__ import annotations

from PySide6.QtWidgets import QMenu

from lunivo_writer.core.befehle.hilfen import _farbfeld
from lunivo_writer.editor import diagramm_zusatz as Z

# Schnelllayouts: (Name, Angaben) — jedes setzt Titel, Legende und Beschriftungen zugleich
SCHNELLLAYOUTS = [
    ("Layout 1: Titel, Legende unten", {"titel_an": True, "legende": True, "legende_pos": "unten", "labels": False}),
    ("Layout 2: Titel, Legende rechts", {"titel_an": True, "legende": True, "legende_pos": "rechts", "labels": False}),
    ("Layout 3: Titel, Legende oben", {"titel_an": True, "legende": True, "legende_pos": "oben", "labels": False}),
    ("Layout 4: Datenbeschriftungen, ohne Legende", {"titel_an": True, "legende": False, "legende_pos": "unten", "labels": True}),
    ("Layout 5: Legende links, Datenbeschriftungen", {"titel_an": True, "legende": True, "legende_pos": "links", "labels": True}),
    ("Layout 6: nur das Diagramm", {"titel_an": False, "legende": False, "legende_pos": "unten", "labels": False}),
]
LEGENDEN_LAGEN = (("oben", "Oben"), ("unten", "Unten"), ("links", "Links"), ("rechts", "Rechts"))
# Angaben der Darstellung, die „Zurücksetzen“ entfernt (None = Standard); Daten, Diagrammart und Alternativtext bleiben
DARSTELLUNG = ("farben", "titel_an", "legende", "legende_pos", "labels", "stil", "elemente", "ausgeblendet", "teil_format", "teil")


def _nummer(k, nr) -> int:
    """Bandbefehle mit Angabe (``diagrammStil:[2]``) bekommen (Knopf, Nummer); direkte Aufrufe dürfen die Nummer als erstes Argument geben."""
    return int(nr if nr is not None else (k if isinstance(k, int) else 0))


class DiagrammToolsBefehle:
    # ==== Hilfen =====================================================================================================================
    def _dg(self) -> dict | None:
        """Die Daten des gewählten Diagramms (Kopie) oder None."""
        from lunivo_writer.editor import frei_objekt as FO
        return FO.daten_lesen(self.ed, "diagramm") if self.ed else None

    def _dg_set(self, **kw) -> bool:
        """Daten des gewählten Diagramms ändern (None entfernt die Angabe) und neu zeichnen; ohne Diagramm ein Hinweis in der Statuszeile."""
        from lunivo_writer.editor import frei_objekt as FO
        if not (self.ed and self._dg() is not None and FO.aendern(self.ed, "diagramm", **kw)):
            self.w.lbl_msg.setText("Bitte zuerst ein Diagramm auswählen.")
            return False
        self.w.band.aktualisieren()
        return True

    # ==== Daten und Diagrammart ======================================================================================================
    def diagrammDatenBearbeiten(self, k=None):
        """Titel, Rubriken und Datenreihen des gewählten Diagramms im vorhandenen Datenfenster bearbeiten."""
        d = self._dg()
        if d is None:
            self._dg_set()
            return
        from lunivo_writer.editor import diagramm as D
        from lunivo_writer.ui.dialogs.einfuegen_dialoge import DiagrammDatenDialog
        dlg = DiagrammDatenDialog(self.w, d.get("titel", ""), list(d.get("kategorien") or D.BEISPIEL_KATEGORIEN),
                                  dict(d.get("reihen") or D.BEISPIEL_REIHEN))
        if dlg.exec():
            titel, kategorien, reihen = dlg.daten()
            kombi = [list(x) for x in (d.get("kombi") or [])][:len(reihen)]
            self._dg_set(titel=titel, kategorien=kategorien, reihen=reihen, kombi=kombi or None)

    def diagrammTypAendern(self, k=None, untertyp=None):
        """Mit ``untertyp`` (``diagrammTypAendern:["linie"]``, Namen aus ``diagramm.TYPEN``) wird die Diagrammart direkt gesetzt; ohne Angabe öffnet
        das Fenster „Diagramm“ mit den Daten und der aktuellen Art vorgewählt, die gewählte Art wird übernommen."""
        d = self._dg()
        if d is None:
            self._dg_set()
            return
        from lunivo_writer.editor import diagramm as D
        if untertyp:
            if untertyp not in D.NAMEN:
                return False
            return self._dg_set(untertyp=untertyp, **({} if untertyp == "kombi_eigen" else {"kombi": None}))
        from lunivo_writer.ui.dialogs.diagramm_fenster import DiagrammDialog
        dlg = DiagrammDialog(self.w, d)
        dlg.setWindowTitle("Diagrammart ändern")
        if dlg.exec():
            neu = dlg.daten()
            kw = {"untertyp": neu["art"], "titel": neu["titel"], "kategorien": neu["kategorien"], "reihen": neu["reihen"],
                  "kombi": neu.get("kombi")}
            if "farben" in neu:
                kw["farben"] = neu["farben"]
            self._dg_set(**kw)

    def menue_diagrammTyp(self, symbol: str):
        """Klappe eines Typ-Knopfes: die Untertypen der Gruppe (``diagramm.TYPEN``) mit Haken beim aktuellen (beim Öffnen aufgefrischt);
        Klick ändert die Diagrammart direkt."""
        from lunivo_writer.editor import diagramm as D
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        for _g, sym, unter in D.TYPEN:
            if sym == symbol:
                for u, name in unter:
                    m.eintrag(name, lambda u=u: self.diagrammTypAendern(None, u), haken=False, daten=u)

        def auffrischen() -> None:
            art = (self._dg() or {}).get("art", "")
            for a in m.actions():
                a.setChecked(a.data() == art)
        m.aboutToShow.connect(auffrischen)
        auffrischen()
        return m

    # ==== Schnelllayout, Farben, Elemente, Stile =====================================================================================
    def menue_diagrammSchnelllayout(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        for name, kw in SCHNELLLAYOUTS:
            m.eintrag(name, lambda kw=kw: self._dg_set(**kw))
        return m

    def diagrammSchnelllayout(self, k=None, nr=None):
        """Schnelllayout Nummer ``nr`` (0 bis 5) anwenden — für Kacheln der Schnellleiste."""
        nr = _nummer(k, nr)
        self._dg_set(**SCHNELLLAYOUTS[max(0, min(int(nr), len(SCHNELLLAYOUTS) - 1))][1])

    def menue_diagrammFarben(self):
        """Die Farbreihen der Diagrammvorlagen (``diagramm.VORLAGEN``), je mit der ersten Farbe als Muster."""
        from lunivo_writer.editor import diagramm as D
        m = QMenu()
        for schl, (_typ, farben) in D.VORLAGEN.items():
            m.addAction(_farbfeld(farben[0]), D.NAMEN.get(schl, schl), lambda _=False, f=list(farben): self._dg_set(farben=f))
        return m

    def diagrammFarben(self, k=None, nr=None):
        """Farbzeile Nummer ``nr`` aus ``diagramm.farbschemen_flach()`` (Gruppen „Farbig“ dann „Monochrom“) anwenden — für Kacheln der Schnellleiste."""
        nr = _nummer(k, nr)
        from lunivo_writer.editor import diagramm as D
        reihen = D.farbschemen_flach()
        self._dg_set(farben=list(reihen[max(0, min(int(nr), len(reihen) - 1))][1]))

    def menue_diagrammElement(self):
        """Diagrammelemente an/aus: Titel, Legende (mit Lage), Datenbeschriftungen, Achsen, Achsentitel, Gitternetzlinien, Datentabelle,
        Fehlerindikatoren, Trendlinie."""
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        d = self._dg() or {}
        m = MenueListe()
        m.eintrag("Diagrammtitel", self.diagrammTitel, haken=d.get("titel_an", True))
        m.eintrag("Legende", self.diagrammLegende, haken=d.get("legende", True))
        lage = m.untermenue("Legende – Lage")
        for schl, name in LEGENDEN_LAGEN:
            lage.eintrag(name, lambda s=schl: self._dg_set(legende=True, legende_pos=s), haken=d.get("legende_pos", "unten") == schl)
        m.eintrag("Datenbeschriftungen", self.diagrammBeschriftungen, haken=bool(d.get("labels", False)))
        for name in ("achsen", "achsentitel", "gitter", "datentabelle", "fehlerindikatoren", "trendlinie"):
            m.eintrag(Z.ELEMENT_NAMEN[name], lambda n=name: self.diagrammElement(None, n), haken=bool(Z.elemente_wirksam(d)[name]))
        return m

    # ---- Diagrammelemente (Liste mit Haken) ------------------------------------------------------------------------------------------
    def diagrammElement(self, k=None, name=None, wert=None):
        """Ein Diagrammelement umschalten (``diagrammElement:["achsen"]``) oder setzen (``wert`` True/False, bei ``legende`` auch die Lage
        ``oben``/``unten``/``links``/``rechts`` oder ``aus``). Namen: ``Z.ELEMENTE`` (achsen, achsentitel, titel, datenbeschriftung, datentabelle,
        fehlerindikatoren, gitter, legende, trendlinie). Zustand: ``an_diagrammElement_<name>``."""
        d = self._dg()
        if d is None:
            return self._dg_set()
        if name not in Z.ELEMENTE:
            return False
        ist = Z.elemente_wirksam(d)[name]
        if name == "legende":
            if wert in Z.LEGENDEN_LAGEN:
                return self._dg_set(legende=True, legende_pos=wert)
            neu = (ist == "aus") if wert is None else bool(wert) and wert != "aus"
            return self._dg_set(legende=neu)
        neu = (not ist) if wert is None else bool(wert)
        if name == "titel":
            return self._dg_set(titel_an=neu)
        if name == "datenbeschriftung":
            return self._dg_set(labels=neu)
        return self._dg_set(elemente={**(d.get("elemente") or {}), name: neu})

    def _element_an(self, name: str) -> bool:
        w = Z.elemente_wirksam(self._dg() or {})[name]
        return w != "aus" if name == "legende" else bool(w)

    def diagrammElementListe(self, k=None) -> list[tuple[str, str, bool]]:
        """Für die Liste „Diagrammelemente“: [(Name, Anzeigename, Haken)] in der Reihenfolge der Vorlage."""
        return [(n, Z.ELEMENT_NAMEN[n], self._element_an(n)) for n in Z.ELEMENTE]

    def diagrammTitel(self, k=None): self._dg_set(titel_an=not (self._dg() or {}).get("titel_an", True))

    def an_diagrammTitel(self): return bool((self._dg() or {}).get("titel_an", True))

    def diagrammLegende(self, k=None): self._dg_set(legende=not (self._dg() or {}).get("legende", True))

    def an_diagrammLegende(self): return bool((self._dg() or {}).get("legende", True))

    def diagrammBeschriftungen(self, k=None): self._dg_set(labels=not (self._dg() or {}).get("labels", False))

    def an_diagrammBeschriftungen(self): return bool((self._dg() or {}).get("labels", False))

    def diagrammStil(self, k=None, nr=None):
        """Diagrammstil ``nr`` (Nummer in ``diagramm.STILE``, Liste: ``diagramm.stile_liste()``)."""
        nr = _nummer(k, nr)
        from lunivo_writer.editor import diagramm as D
        self._dg_set(stil=max(0, min(int(nr), len(D.STILE) - 1)))

    def diagrammZuruecksetzen(self, k=None):
        """Farben, Titel/Legende/Beschriftungen, Elemente, Filter, Teilformate und Stil auf den Standard zurück; Daten, Diagrammart und Alternativtext bleiben."""
        self._dg_set(**{schl: None for schl in DARSTELLUNG}, form_effekt=None)          # auch die Effekte des Diagrammbereichs (am Objekt)

    # ==== Diagrammteile, Filter, Formate, Alternativtext =============================================================================
    def diagrammTeile(self, k=None) -> list[tuple[str, str]]:
        """Die wählbaren Teile des gewählten Diagramms [(Schlüssel, Anzeigename)] für das Feld „Diagrammbereich“ (leer ohne Diagramm)."""
        from lunivo_writer.editor import diagramm as D
        d = self._dg()
        return D.teile(d) if d is not None else []

    def diagrammTeilWaehlen(self, k=None, schluessel=None):
        """Einen Diagrammteil wählen (``diagrammTeilWaehlen:["reihe_0"]``; ohne Schlüssel: Auswahl aufheben). Zeichnet nicht neu."""
        from lunivo_writer.editor import diagramm_teile as T
        if self._dg() is None:
            return self._dg_set()
        return T.teil_waehlen(self.ed, schluessel)

    def feld_diagrammTeil(self) -> str:
        """Anzeigename des gewählten Teils fürs Feld „Diagrammbereich“ (ohne Auswahl: „Diagrammbereich“)."""
        from lunivo_writer.editor import diagramm_teile as T
        return (T.teil_name(self.ed) if self.ed else "") or "Diagrammbereich"

    def diagrammTeilFormat(self, k=None, angaben=None, **kw):
        """Format des gewählten Teils ändern: ``fuell`` (Farbe oder Wörterbuch), ``linie``, ``schatten``, ``reflektion``, ``leuchten``, ``weich``, ``d3``, ``drehung``,
        ``text``, ``achse``, ``reihe`` (Aufbau in ``editor/diagramm_format.py``); ``teil`` wählt einen anderen Teil. Als Bandbefehl: ``diagrammTeilFormat:[{"fuell": "#ff0000"}]``. Lesen:
        ``editor.diagramm_teile.diagramm_teil_format_lesen(ed)``."""
        from lunivo_writer.editor import diagramm_teile as T
        if self._dg() is None:
            return self._dg_set()
        ok = T.diagramm_teil_format_setzen(self.ed, **{**(angaben or {}), **kw})
        if ok:
            self.w.band.aktualisieren()
        return ok

    def diagrammFilterDaten(self, k=None) -> dict:
        """Für das Popup „Diagrammfilter“: {"reihen": [(Name, Haken)], "rubriken": [(Name, Haken)]} — Haken = sichtbar."""
        from lunivo_writer.editor import diagramm as D
        d = self._dg()
        if d is None:
            return {"reihen": [], "rubriken": []}
        aus = d.get("ausgeblendet") or {}
        return {"reihen": [(n, n not in (aus.get("reihen") or [])) for n in (d.get("reihen") or D.BEISPIEL_REIHEN)],
                "rubriken": [(n, n not in (aus.get("rubriken") or [])) for n in (d.get("kategorien") or D.BEISPIEL_KATEGORIEN)]}

    def diagrammFilterSetzen(self, k=None, ausgeblendet=None):
        """„Übernehmen“: {"reihen": [Namen], "rubriken": [Namen]} = die ausgeblendeten Einträge (leer/None = alles zeigen)."""
        aus = {k2: list(v) for k2, v in (ausgeblendet or {}).items() if k2 in ("reihen", "rubriken") and v}
        return self._dg_set(ausgeblendet=aus or None, teil=None)

    def diagrammNamenSetzen(self, k=None, namen=None):
        """Reihen/Rubriken umbenennen: {"reihen": [(alt, neu)], "rubriken": [(alt, neu)]}. Leere oder doppelte neue Namen bleiben beim alten Namen;
        Filter („ausgeblendet“) wandert mit."""
        from lunivo_writer.editor import diagramm as D
        d = self._dg()
        if d is None:
            return self._dg_set()
        namen = namen or {}

        def umbenennen(alte: list[str], paare) -> dict[str, str]:
            neu = dict(paare)
            wunsch = {a: ((neu.get(a) or a).strip() or a) for a in alte}
            for a in alte:                                                  # ein Name, den eine andere Reihe/Rubrik schon trägt, bleibt beim alten
                if wunsch[a] in [wunsch[x] for x in alte if x != a]:
                    wunsch[a] = a
            return wunsch
        reihen = dict(d.get("reihen") or D.BEISPIEL_REIHEN)
        kats = list(d.get("kategorien") or D.BEISPIEL_KATEGORIEN)
        rn, kn = umbenennen(list(reihen), namen.get("reihen") or []), umbenennen(kats, namen.get("rubriken") or [])
        aus = d.get("ausgeblendet") or {}
        aus_neu = {"reihen": [rn.get(x, x) for x in aus.get("reihen") or []], "rubriken": [kn.get(x, x) for x in aus.get("rubriken") or []]}
        aus_neu = {k2: v for k2, v in aus_neu.items() if v}
        return self._dg_set(reihen={rn[a]: v for a, v in reihen.items()}, kategorien=[kn[a] for a in kats], ausgeblendet=aus_neu or None)

    def diagrammAltText(self, k=None, titel=None, beschreibung=None):
        """Alternativtext des Diagramms (``alt_titel``, ``alt_beschreibung``; in DOCX steht die Beschreibung als ``descr``); ``""`` löscht."""
        return self._dg_set(**{n: (v or None) for n, v in (("alt_titel", titel), ("alt_beschreibung", beschreibung)) if v is not None})


def _element_befehle() -> None:
    """Je Element ``an_diagrammElement_<name>`` (Haken) und ``diagrammElement_<name>`` (Umschalten) — für Knöpfe, die keine Angabe mitgeben."""
    for name in Z.ELEMENTE:
        setattr(DiagrammToolsBefehle, "an_diagrammElement_" + name, lambda self, n=name: self._element_an(n))
        setattr(DiagrammToolsBefehle, "diagrammElement_" + name, lambda self, k=None, n=name: self.diagrammElement(k, n))


_element_befehle()


def _typ_klappen() -> None:
    """Je Typ-Knopf des Reiters eine Klappe ``menue_diagrammTyp_<symbol>`` (Untertypen der Gruppe)."""
    for sym in ("saeule", "kombination", "balkenquer", "flaeche", "linie", "kreis", "netz", "kurs", "punktwolke"):
        setattr(DiagrammToolsBefehle, "menue_diagrammTyp_" + sym, lambda self, s=sym: self.menue_diagrammTyp(s))


_typ_klappen()
