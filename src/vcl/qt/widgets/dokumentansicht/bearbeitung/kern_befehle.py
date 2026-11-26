"""Bandbefehle des Editors für Absatz, Liste, Rahmen, Tabulator, Formatvorlage, Abschnitt, Verknüpfung und Ersetzen im Text.

Die Klasse ``KernBefehle`` gehört zu ``KernEditor`` (``kern_editor.py``) und übersetzt wie dieser Befehle der Oberfläche in Operationen der
Bearbeitungssitzung. Hier stehen die Befehle, die Wörterbücher und Listen aus den Dialogen der Oberfläche (Liste, Rahmen, Absatz,
Formatvorlage) in Formate des Dokumentmodells umsetzen und zurück.
"""
from __future__ import annotations

import dataclasses
import re

from PySide6.QtCore import Qt

from writer.werte import Bereich, Stelle
from writer.werte import mm_zu_px as mm_to_px, px_zu_mm as px_to_mm
from writer.funktionen import bearbeiten as _bearbeiten
from writer.anbindung import absatzoptionen as _absatzoptionen
from writer.anbindung import formatwerte as _formatwerte

PUNKTE = ("disc", "circle", "square")
ZAHLEN_TIEFER = ("dezimal", "klein", "roem_klein")
from vcl.qt.widgets.bausteine.farben.farben import GITTER_FARBE, TABELLENRAND_SCHWARZ, TABELLENRAND_STANDARD  # noqa: E402


from writer.anbindung.ki_markdown import markdown_bloecke  # noqa: E402,F401  (Qt-freie Zerlegung, hier weiter erreichbar)


class KernBefehle:
    """Gemischt in ``KernEditor``: nutzt ``self.kennung`` und ``self.ansicht`` des Editors."""

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
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_format_uebertragen(self.kennung, probe["zeichen"], probe["absatz"]))

    # ---- Absatz ----------------------------------------------------------------------------------------------------------------------------
    def set_indents(self, links_mm: float, rechts_mm: float, erste_mm: float) -> None:
        self._af({"einzug_links": mm_to_px(links_mm) or None, "einzug_rechts": mm_to_px(rechts_mm) or None, "einzug_erste": mm_to_px(erste_mm) or None})

    def absatz_option(self, name: str):
        """Eine Absatzoption (``editor/seite/absatzopt.py``) des Absatzes an der Schreibmarke."""
        roh = _bearbeiten.wirksames_absatzformat(self.kennung).get("optionen")
        return _absatzoptionen.aus_text(roh if isinstance(roh, str) else "").get(name, _absatzoptionen.vorgabe().get(name))

    def absatz_option_setzen(self, name: str, wert) -> None:
        roh = _bearbeiten.wirksames_absatzformat(self.kennung).get("optionen")
        w = _absatzoptionen.aus_text(roh if isinstance(roh, str) else "")
        w[name] = wert
        self._af({"optionen": _absatzoptionen.als_text(w) or None})

    def set_absatzopt(self, opt) -> None:
        text = opt if isinstance(opt, str) else _absatzoptionen.als_text(opt or {})
        self._af({"optionen": text or None})

    def set_tabstopps(self, stopps) -> None:
        """Tabstopps als Liste aus (Millimeter, Ausrichtung, Füllzeichen)."""
        liste = [[mm_to_px(m), art, ""] for m, art, _f in stopps]
        fuell = ";".join(f"{mm_to_px(m):.2f}:{f}" for m, _a, f in stopps if f)
        self._af({"tabstopps": liste or None, "tabfuell": fuell or None})

    def standard_tab_mm(self) -> float:
        return round(px_to_mm(_bearbeiten.tab_abstand(self.kennung)), 2)

    def set_standard_tab_mm(self, mm: float) -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_eigenschaft_setzen(self.kennung, "tab_abstand", mm_to_px(mm)))

    def toggle_rtl(self) -> None:
        a = _bearbeiten.wirksames_absatzformat(self.kennung)
        self._af({"richtung": "ltr" if _formatwerte.richtung(a) == "rtl" else "rtl", "ausrichtung": None if a.get("ausrichtung") in (None, "links", "rechts") else a["ausrichtung"]})

    def absatzrahmen(self):
        from vcl.qt.rendering.formen import Linie
        return Linie.aus_text(_bearbeiten.wirksames_absatzformat(self.kennung).get("rahmen"))

    def set_absatzrahmen(self, text) -> None:
        self._af({"rahmen": text or None})

    def absatzschatten(self) -> tuple:
        a = _bearbeiten.wirksames_absatzformat(self.kennung)
        return a.get("hintergrund"), a.get("muster")

    def set_absatzschatten(self, fuell=None, muster=None, musterfarbe=None) -> None:
        if hasattr(fuell, "name") and callable(fuell.name):
            fuell = fuell.name()
        self._af({"hintergrund": fuell or None, "muster": (f"{muster}|{musterfarbe}" if musterfarbe else str(muster)) if muster else None})

    # ---- Listen -----------------------------------------------------------------------------------------------------------------------------
    def liste_spec(self):
        """Beschreibung der Liste am Absatz der Schreibmarke (für die Listenfenster), ``None`` ohne Liste."""
        return _bearbeiten.liste_spec(self.kennung)

    def set_liste(self, spec) -> None:
        """Wendet die Liste auf die Absätze der Auswahl an (``None``: Liste entfernen). Folgt sie unmittelbar auf eine gleiche Liste, zählt sie weiter."""
        if not spec:
            self.ansicht._befehl(lambda: _bearbeiten.aenderung_liste_entfernen(self.kennung))
            return
        self.ansicht._befehl(lambda: _bearbeiten.liste_setzen(self.kennung, spec))

    def liste_neu_beginnen(self, start: int = 1) -> None:
        a = self._absatz_an_marke()
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_liste_neu_beginnen(self.kennung, a.id, start))

    # ---- Formatvorlagen -----------------------------------------------------------------------------------------------------------------
    def stil_aus_auswahl(self) -> dict:
        """Die Werte des Absatzes an der Schreibmarke als Vorgabe für „Neue Formatvorlage“ (aus dem Framework; die Liste ergänzt der Editor)."""
        werte = dict(_bearbeiten.formatvorlage_aus_auswahl(self.kennung))
        spec = self.liste_spec()
        if spec:
            from writer.anbindung import mehrstufig as _mehrstufig
            werte["liste"] = _mehrstufig.liste_als_text(spec)
        return {k: v for k, v in werte.items() if v not in (None, "", 0, 0.0, False)}

    def stil_neu_anwenden(self, name: str) -> None:
        """Nach dem Ändern einer Vorlage im Katalog: das Dokument übernimmt die neue Definition (über das Framework)."""
        _bearbeiten.formatvorlage_abgleichen(self.kennung, name)

    def stil_entfernen(self, name: str) -> None:
        if _bearbeiten.dok_vorlage_vorhanden(self.kennung, name):
            self.ansicht._befehl(lambda: _bearbeiten.aenderung_vorlage_loeschen(self.kennung, name))

    def stil_tasten(self) -> None:
        """Tastenkombinationen der Formatvorlagen (``taste`` im Katalog) auf der Zeichenfläche setzen."""
        from PySide6.QtGui import QKeySequence, QShortcut
        from writer import vorlagenkatalog as stile
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
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_design_anwenden(self.kennung, text_schrift, kopf_schrift, farbe))

    def abschnitt_einfuegen(self, art: str = "naechste") -> int:
        nr = [0]

        def f() -> bool:
            neu = _bearbeiten.aenderung_abschnitt_einfuegen(self.kennung, art)
            nr[0] = neu if neu is not None else 0
            return neu is not None
        self.ansicht._befehl(f)
        return nr[0]

    def abschnitt_entfernen(self) -> bool:
        n = self.abschnitt_nr()
        if n < 1:
            return False
        return self.ansicht._befehl(lambda: _bearbeiten.aenderung_abschnitt_entfernen(self.kennung, n, "vorher"))

    def abschnitt_gehe(self, n: int) -> None:
        erster = _bearbeiten.dok_abschnitt_erster_absatz(self.kennung, n)
        if erster is not None:
            _bearbeiten.auswahl_setzen(self.kennung, Stelle(erster, 0), Stelle(erster, 0))
            self.ansicht.nach_bewegung()

    def seite_letzter_block(self):
        """Der letzte Absatz des Haupttextes (für Seiten, die am Ende des Dokuments eingefügt werden)."""
        return _bearbeiten.dok_absatz(self.kennung, _bearbeiten.dok_letzter_absatz(self.kennung))

    # ---- Verknüpfung ---------------------------------------------------------------------------------------------------------------------
    def insert_link(self, href: str, text: str | None = None, tipp: str = "") -> None:
        """Verknüpfung auf die Auswahl; ohne Auswahl und mit ``text`` wird der Text eingefügt, sonst gilt sie für das Wort an der Schreibmarke."""
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_link_setzen(self.kennung, href, text, tipp))

    # ---- Noten -------------------------------------------------------------------------------------------------------------------------------
    def note_loeschen(self, art: str, note_id: int) -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_note_loeschen(self.kennung, art, note_id))

    # ---- Ersetzen im Rohtext ---------------------------------------------------------------------------------------------------------------
    def rohtext(self) -> str:
        """Der Text des Dokuments mit U+2029 zwischen den Absätzen (Stellen wie bei ``textCursor().position()``)."""
        return _bearbeiten.rohtext(self.kennung)

    def replace_range(self, von: int, bis: int, neu: str, erwartet: str | None = None, markdown: bool = False) -> bool:
        """Ersetzt [von, bis) des Rohtextes durch ``neu``; mit ``erwartet`` nur, wenn dort noch dieser Text steht. ``markdown``: Auszeichnungen
        (Überschriften, Listen, Fett) werden als Formate umgesetzt."""
        roh = _bearbeiten.rohtext(self.kennung)
        if erwartet is not None and roh[von:bis] != erwartet:
            return False
        if markdown:
            return self._markdown_ersetzen(von, bis, neu)
        self.ersetze_roh(von, bis, neu)
        return True

    def _markdown_ersetzen(self, von: int, bis: int, neu: str) -> bool:
        bloecke = markdown_bloecke(neu)
        anfang = _bearbeiten.stelle_von(self.kennung, von)
        for b in bloecke:
            if b["vorlage"]:
                self.stil_neu_anwenden(b["vorlage"])

        return self.ansicht._befehl(lambda: _bearbeiten.aenderung_markdown_ersetzen(self.kennung, von, bis, bloecke, (anfang.absatz_id, anfang.versatz)))

    def ersetze_verfolgt(self, von: int, bis: int, neu: str, autor: str = "") -> bool:
        """Wie ``replace_range``, aber als nachverfolgte Änderung des Bearbeiters ``autor``."""
        return self.ansicht._befehl(lambda: _bearbeiten.aenderung_ersetzen_verfolgt(self.kennung, von, bis, neu, autor))

    # ---- Tabellen: Gestaltung ---------------------------------------------------------------------------------------------------------------
    def _zellen_der_auswahl(self):
        """(Tabelle, [(Zeile, Spalte)]) der Zellen der Auswahl (sonst der Zelle der Schreibmarke); ``None`` außerhalb einer Tabelle."""
        r = self.zellen_im_bereich()
        if r is None:
            return None
        tabelle = _bearbeiten.dok_tabelle(self.kennung, r[0])
        return tabelle, [(z, s) for z, s in r[1] if tabelle.zellen[z][s].verdeckt_von is None]

    @staticmethod
    def _absaetze_der_zelle(zelle) -> list:
        return list(zelle.absatz_ids)

    def tabelle_rahmen_umschalten(self) -> bool:
        t = self.tabelle_an_marke()
        if t is None:
            return False
        an = float(t.tabelle.format.get("rahmen_breite") or 0) > 0
        return self.tabellenformat({"rahmen_breite": None if an else 1.0, "rahmen_farbe": None if an else TABELLENRAND_STANDARD, "rahmen_art": None if an else "einfach"})

    def tabelle_rahmen_an(self) -> bool:
        t = self.tabelle_an_marke()
        return t is not None and float(t.tabelle.format.get("rahmen_breite") or 0) > 0

    def tabelle_ist_frei(self) -> bool:
        """Ob die Tabelle an der Schreibmarke frei platziert ist (am Verschiebegriff versetzt)."""
        t = self.tabelle_an_marke()
        return t is not None and ("frei_x" in t.tabelle.format or "frei_y" in t.tabelle.format)

    def tabelle_in_textfluss(self) -> bool:
        """Die frei platzierte Tabelle steht wieder im Textfluss, an der Stelle ihres Ankers."""
        return self.tabelle_ist_frei() and self.tabellenformat({"frei_x": None, "frei_y": None})

    def tabelle_rahmen_linie(self, linie) -> bool:
        """Rahmen der Tabelle aus einer ``Linie`` (``None`` = ohne Rahmen)."""
        if linie is None:
            return self.tabellenformat({"rahmen_breite": None, "rahmen_farbe": None, "rahmen_art": None})
        return self.tabellenformat({"rahmen_breite": max(1.0, linie.breite_pt / 0.75), "rahmen_farbe": linie.farbe, "rahmen_art": linie.art})

    def tabelle_rahmen_lesen(self):
        from vcl.qt.rendering.formen import Linie
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
        from writer.anbindung import tabellenstil as _tabellenstil
        t = self.tabelle_an_marke()
        if t is None or name not in _tabellenstil.vorlagen():
            return False
        tid = t.id
        return self.ansicht._befehl(lambda: _bearbeiten.aenderung_tabellenvorlage_anwenden(self.kennung, tid, name, kopf, streifen, spalte, TABELLENRAND_STANDARD))

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
        return bool(ids) and self.ansicht._befehl(lambda: _bearbeiten.aenderung_absatzformat_anwenden(self.kennung, {"ausrichtung": ausrichtung}, absatz_ids=ids))

    def zell_richtung(self, richtung: str) -> bool:
        r = self._zellen_der_auswahl()
        if r is None:
            return False
        ids = [i for z, s in r[1] for i in self._absaetze_der_zelle(r[0].zellen[z][s])]

        return self.ansicht._befehl(lambda: _bearbeiten.aenderung_zell_richtung(self.kennung, r[0].id, r[1], ids, richtung))

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
        return self.ansicht._befehl(lambda: _bearbeiten.aenderung_zellformat_anwenden(self.kennung, t.id, {f"rahmen_{k}": kante for k in ("oben", "unten", "links", "rechts")}, alle))

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
        return self.ansicht._befehl(lambda: _bearbeiten.aenderung_spaltenbreiten_setzen(self.kennung, t.id, breiten))

    def zeile_hoehe_setzen(self, mm: float) -> bool:
        t = self.tabelle_an_marke()
        if t is None or mm <= 0:
            return False
        return self.ansicht._befehl(lambda: _bearbeiten.aenderung_zeilenhoehen_setzen(self.kennung, t.id, {t.tabelle.anker(t.zeile, t.spalte)[0]: mm_to_px(mm)}))

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
            return self.ansicht._befehl(lambda: _bearbeiten.aenderung_tabelle_an_inhalt(self.kennung, t.id, n, t.tabelle.zeilen))
        if art == "fenster":
            breite = self.page.content_width_px
            return self.ansicht._befehl(lambda: _bearbeiten.aenderung_tabelle_an_fenster(self.kennung, t.id, n, breite))
        if art == "spalten_gleich":
            breiten = self._spaltenbreiten_gemessen(t)
            return self.ansicht._befehl(lambda: _bearbeiten.aenderung_spaltenbreiten_setzen(self.kennung, t.id, [sum(breiten) / n] * n))
        if art == "zeilen_gleich":
            hoehen = [p.rect.height for seite in self.ansicht.ergebnis().seiten for p in seite.plaetze
                      if p.art == "zelle" and p.block_id == t.id and not p.kopie and p.spalte == 0]
            return bool(hoehen) and self.ansicht._befehl(lambda: _bearbeiten.aenderung_zeilen_gleich(self.kennung, t.id, max(hoehen)))
        if art == "fest":
            breiten = self._spaltenbreiten_gemessen(t)
            return self.ansicht._befehl(lambda: _bearbeiten.aenderung_spaltenbreiten_setzen(self.kennung, t.id, breiten))
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
        from vcl.qt.widgets.bausteine.symbole.bauteile.kontextmenue import menue_bauen
        if self.objekt_gewaehlt() is not None:
            from vcl.qt.widgets.bausteine.symbole.bauteile.kontextmenue import objektmenue_bauen
            m = objektmenue_bauen(self, self.fenster)
        else:
            m = menue_bauen(self, self.fenster)
            if callable(self.kontext_hook):
                self.kontext_hook(m, self.textCursor().position())
        if callable(self.mini_hook) and not self.isReadOnly() and self.objekt_art() not in ("diagramm", "smartart"):     # dort gilt das Objektmenü, nicht die Textleiste
            self.mini_hook(self, pos, True, m.sizeHint())
        m.exec(pos)
        m.deleteLater()
        if callable(self.mini_hook):
            self.mini_hook(None, None)

    def verknuepfung_folgen(self, ziel: str) -> None:
        """Strg+Klick auf eine Verknüpfung: ``#Name`` springt zur Textmarke, sonst öffnet das System die Adresse."""
        if ziel.startswith("#"):
            if _bearbeiten.textmarke_anspringen(self.kennung, ziel[1:]):
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
        t = _bearbeiten.dok_tabelle(self.kennung, tid)
        von = _bearbeiten.zelle_anfang(self.kennung, tid, 0, 0)
        letzte = t.zellen[-1][-1]
        letzte = t.zellen[t.anker(t.zeilen - 1, t.spalten - 1)[0]][t.anker(t.zeilen - 1, t.spalten - 1)[1]]
        ids = list(letzte.absatz_ids)
        bis = Stelle(ids[-1], _bearbeiten.absatz_laenge(self.kennung, ids[-1])) if ids else von
        _bearbeiten.auswahl_setzen(self.kennung, von, bis)
        self.ansicht.nach_bewegung()
        if callable(self.mini_hook):
            self.mini_per_griff = True
            from PySide6.QtGui import QCursor
            self.mini_hook(self, QCursor.pos())

    def tabelle_maus_aendern(self, art: str, tid: int, wert) -> None:
        t = _bearbeiten.dok_tabelle(self.kennung, tid)
        if art == "spalte_plus":
            self.ansicht._befehl(lambda: _bearbeiten.aenderung_spalten_einfuegen(self.kennung, tid, t.spalten))
        elif art == "zeile_plus":
            self.ansicht._befehl(lambda: _bearbeiten.aenderung_zeilen_einfuegen(self.kennung, tid, t.zeilen))
        elif art == "loeschen":
            self.ansicht._befehl(lambda: _bearbeiten.aenderung_tabelle_loeschen(self.kennung, tid))
        elif art == "versetzen":                         # frei platzieren: Blattkoordinaten → Lage ab der oberen linken Ecke des Satzspiegels
            seite, x, y, absatz_id = wert
            e = self.ansicht.ergebnis().seiten[seite].einrichtung
            links, oben = (mm_to_px(e.margin_left_mm), mm_to_px(e.margin_top_mm)) if e is not None else (0.0, 0.0)
            self.ansicht._befehl(lambda: _bearbeiten.aenderung_tabelle_frei_setzen(self.kennung, tid, x - links, y - oben, absatz_id))
        elif art == "skalieren":
            breiten = tuple(self._spaltenbreiten_gemessen(_TabellenRef(t)))          # automatische Spalten und Zeilen haben keine Vorgabe: Ausgangswert ist das gemessene Maß
            hoehen = tuple(self._zeilenhoehe_gemessen(tid, z) for z in range(t.zeilen))
            self.ansicht._befehl(lambda: _bearbeiten.aenderung_tabelle_skalieren(self.kennung, tid, wert[0], wert[1], breiten, hoehen))
        elif art == "spalte":                               # Rand rechts der Spalte ``index`` um ``delta`` verschieben: die Nachbarspalte gibt ab oder bekommt
            index, delta = wert
            breiten = self._spaltenbreiten_gemessen(self.tabelle_an_marke() if self.tabelle_an_marke() and self.tabelle_an_marke().id == tid else _TabellenRef(t))
            if index + 1 < len(breiten):
                delta = max(-(breiten[index] - 12.0), min(breiten[index + 1] - 12.0, delta))
                breiten[index] += delta
                breiten[index + 1] -= delta
            else:
                breiten[index] = max(12.0, breiten[index] + delta)
            self.ansicht._befehl(lambda: _bearbeiten.aenderung_spaltenbreiten_setzen(self.kennung, tid, breiten))
        elif art == "zeile":
            index, delta = wert
            aktuell = t.zeilenhoehen[index] or self._zeilenhoehe_gemessen(tid, index)
            self.ansicht._befehl(lambda: _bearbeiten.aenderung_zeilenhoehen_setzen(self.kennung, tid, {index: max(8.0, aktuell + delta)}))

    def _zeilenhoehe_gemessen(self, tid: int, zeile: int) -> float:
        for seite in self.ansicht.ergebnis().seiten:
            for p in seite.plaetze:
                if p.art == "zelle" and p.block_id == tid and not p.kopie and p.zeile == zeile:
                    return p.rect.height
        return 20.0

    def tabelle_zeichnen_an(self, stelle, zeilen: int, spalten: int, breite: float = 0.0) -> None:
        """Tabelle mit dem Stift gezeichnet: sie entsteht an der Stelle, an der das Ziehen begann, mit Tabellenraster (wie ``insert_table``) und der
        aufgezogenen Breite (Bildpunkte bei 100 %)."""
        form = {"rahmen_breite": 1.0, "rahmen_farbe": TABELLENRAND_SCHWARZ}
        if breite > 0:
            form.update({"breite": float(breite), "breite_art": "fest"})
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_tabelle_einfuegen(self.kennung, zeilen, spalten, form, (stelle[0], stelle[1])))

    def tabelle_zellen_vereinen(self, tid: int, a: tuple, b: tuple) -> None:
        """Radiergummi: die Zellen ``a`` und ``b`` (Anker) werden zu einer Zelle verbunden, wenn sie ein Rechteck bilden."""
        t = _bearbeiten.dok_tabelle(self.kennung, tid)
        za, zb = t.zellen[a[0]][a[1]], t.zellen[b[0]][b[1]]
        z1, s1 = min(a[0], b[0]), min(a[1], b[1])
        z2 = max(a[0] + za.zeilenspanne, b[0] + zb.zeilenspanne)
        s2 = max(a[1] + za.spaltenspanne, b[1] + zb.spaltenspanne)
        flaeche = za.zeilenspanne * za.spaltenspanne + zb.zeilenspanne * zb.spaltenspanne
        if flaeche != (z2 - z1) * (s2 - s1):
            return
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_zellen_verbinden(self.kennung, tid, z1, s1, z2 - z1, s2 - s1))


    # ---- Quellen, Zitierweise, Seitenzahlen ------------------------------------------------------------------------------------------
    @property
    def quellen(self) -> list:
        """Die Literaturquellen des Dokuments (Kopie; ändern über ``quelle_hinzufuegen`` und ``quelle_entfernen``)."""
        return [dict(q) for q in _bearbeiten.dok_quellen(self.kennung)]

    @property
    def zitierweise(self) -> str:
        return str(_bearbeiten.dok_eigenschaft(self.kennung, "zitierweise") or "APA")

    @zitierweise.setter
    def zitierweise(self, name: str) -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_eigenschaft_setzen(self.kennung, "zitierweise", name))

    def quelle_hinzufuegen(self, q: dict) -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_quelle_setzen(self.kennung, q))

    def quelle_entfernen(self, tag: str) -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_quelle_loeschen(self.kennung, tag))

    def seiten_von(self, offsets: list) -> list:
        """Die angezeigten Seitenzahlen der Stellen im Rohtext (``"?"``, wenn eine Stelle nirgends steht)."""
        erg = self.ansicht.ergebnis()
        aus = []
        for o in offsets:
            seite = erg.seite_von(_bearbeiten.stelle_von(self.kennung, o).absatz_id)
            aus.append(str(erg.seiten[seite].nummer or seite + 1) if seite is not None else "?")
        return aus


    def _formular_klick(self, pos: int) -> bool:
        """Klick auf ein Formularfeld (Kontrollkästchen, Auswahl, Datum, Text, Schaltfläche)."""
        from vcl.qt.rendering import textfelder as formular
        return formular.klick(self, pos, self.fenster)


    # ---- Abschnitte: Seiteneinrichtung je Abschnitt -----------------------------------------------------------------------------------
    def abschnitt_seite(self, nr: int | None = None):
        """Die Seiteneinrichtung des Abschnitts ``nr`` (ohne Angabe: an der Schreibmarke) als Kopie zum Ändern."""
        n = self.abschnitt_nr() if nr is None else nr
        return _bearbeiten.seite_des_abschnitts(self.kennung, n)

    def abschnitt_seite_setzen(self, nr: int, seite) -> None:
        self._seite_ersetzen(nr, seite)
        self.pageApplied.emit()

    def abschnitte_anzahl(self) -> int:
        return _bearbeiten.dok_abschnitte_anzahl(self.kennung)

    def abschnitt_beginn(self, nr: int) -> str:
        return _bearbeiten.dok_abschnitt_beginn(self.kennung, nr)

    def abschnitt_beginn_setzen(self, nr: int, art: str) -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_abschnitt_beginn_setzen(self.kennung, nr, art))

    def seitenzahl_anwenden(self, w: dict) -> None:
        """Seitenzahl nach den Werten des Fensters: für das ganze Dokument, ab der aktuellen Seite (neuer Abschnitt) oder den aktuellen Abschnitt."""
        erster, abschnitt = None, 0
        if w["bereich"] == "seite":
            erg = self.ansicht.ergebnis()
            seite = max(0, self.current_page() - 1)
            erster = next((p.block_id for p in erg.seiten[seite].plaetze if p.art == "zeile"), None)
        elif w["bereich"] != "dokument":
            abschnitt = self.abschnitt_nr()
        self.ansicht._befehl(lambda: _bearbeiten.seitenzahl_setzen(self.kennung, w["bereich"], erster, abschnitt, w["ort"], w["ausrichtung"], w["muster"], w["format"],
                                                                 w["start"], w["kapitel"], True))
        self.pageApplied.emit()


    def seite_letzter_block(self):
        """Der letzte Absatz des Haupttextes, der auf der Seite der Schreibmarke beginnt."""
        erg = self.ansicht.ergebnis()
        seite = erg.seite_von(_bearbeiten.auswahl(self.kennung).kopf.absatz_id)
        aus = None
        im_text = {aid for aid, _laenge in _bearbeiten.dok_absatzlaengen(self.kennung)}
        for aid in erg.reihenfolge:
            if erg.seite_von(aid) == seite and aid in im_text:
                aus = aid
        return _bearbeiten.dok_absatz(self.kennung, aus if aus is not None else _bearbeiten.auswahl(self.kennung).kopf.absatz_id)

    def leere_seite(self, quer: bool | None = None) -> None:
        """Ein neues, leeres Blatt hinter der Seite der Schreibmarke; der Text wird nicht geteilt. Hat das Blatt eine andere Ausrichtung als der
        Abschnitt, bekommt es einen eigenen Abschnitt (der Text danach geht in der alten Ausrichtung weiter)."""
        einrichtung = self.abschnitt_seite()
        eigene = quer is not None and bool(quer) != einrichtung.landscape

        letzter = self.seite_letzter_block().id
        blatt = None
        if eigene:
            blatt = einrichtung.copy()
            blatt.set_orientation(bool(quer))
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_leere_seite(self.kennung, letzter, None if blatt is None else blatt.als_felder(),
                                                                       einrichtung.als_felder()))


    def note_text_setzen(self, art: str, note_id: int, text: str) -> None:
        """Ändert den Text einer Fuß- oder Endnote (tippt das Feld „Noten“, ein Rückgängig-Schritt je Pause)."""
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_note_aendern(self.kennung, art, note_id, text))
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
        erster, abschnitt = None, 0
        if bereich == "seite":
            erg = self.ansicht.ergebnis()
            erster = next((p.block_id for p in erg.seiten[max(0, self.current_page() - 1)].plaetze if p.art == "zeile"), None)
        elif bereich != "dokument":
            abschnitt = self.abschnitt_nr()
        self.ansicht._befehl(lambda: _bearbeiten.seitenzahl_setzen(self.kennung, bereich, erster, abschnitt, zone, ausr, muster, zahl))
        self.pageApplied.emit()


    def gliederung_ebene(self, delta: int) -> None:
        """Gliederungsansicht: Überschrift des Absatzes um ``delta`` Ebenen herauf- (−1) oder herabstufen (+1); Ebene 0 ist Fließtext."""
        neu = max(0, min(9, _bearbeiten.ueberschriftsebene_an_marke(self.kennung) + delta))
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
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
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
        alle = _bearbeiten.tabellen_ohne_rahmen(self.kennung)
        if not alle:
            return False
        hier = self.textCursor().selectionEnd()
        p, tid = next(((p, tid) for p, tid in alle if p >= hier), alle[0])
        self.select_range(p, p)
        self.tabelle_ganz_waehlen(tid)
        self.ensureCursorVisible()
        return True

    def aehnlich_formatiert(self) -> list:
        """Alle Strecken (Stellen im Rohtext) mit derselben Zeichenformatierung wie das Zeichen an der Schreibmarke."""
        return _bearbeiten.aehnlich_formatiert(self.kennung)

    def naechstes_objekt_waehlen(self) -> bool:
        """Springt zum nächsten Objekt (im Text oder frei positioniert) hinter der Schreibmarke und wählt es (am Ende geht es vorn weiter)."""
        liste = _bearbeiten.objekte_nach_stelle(self.kennung)
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
