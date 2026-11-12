"""Editor-Seite von Kommentaren, Fuß-/Endnoten und Änderungsverfolgung (Mixin für DocumentEditor)."""
from __future__ import annotations

import datetime
import hashlib

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor, QTextFormat
from PySide6.QtWidgets import QTextEdit

from lunivo_writer.editor.dokument.zusatz import P_AENDERUNG, P_AUTOR, P_DATUM, P_KOMMENTAR, P_NOTE, neue_id, roemisch, AUTOR_FARBEN



from lunivo_writer.editor.text.fragmente import dokument_fragmente
from lunivo_writer.kern.farben import Farbe
FESTE_FARBEN = {"Rot": Farbe.ROT, "Blau": "#1971c2", "Grün": Farbe.GRUEN, "Schwarz": "#222222", "Violett": "#7048a8"}
INS_STILE = ["Unterstrichen", "Doppelt unterstrichen", "Fett", "Kursiv", "Keine"]
DEL_STILE = ["Durchgestrichen", "Fett", "Kursiv", "Keine"]


def autor_farbe(autor: str) -> QColor:
    h = int(hashlib.md5((autor or "?").encode()).hexdigest(), 16)
    return QColor(AUTOR_FARBEN[h % len(AUTOR_FARBEN)])


class ZusatzMixin:
    zusatzGeaendert = Signal()
    noteAngeklickt = Signal(str, int)      # Art („f“/„e“) und Nummer der Note, deren Zeichen im Text angeklickt wurde

    def _zusatz_init(self) -> None:
        self.kommentare: dict = {}
        self.noten: dict = {"f": {}, "e": {}}
        self.quellen: list = []
        self.zitierweise = "APA"
        self._meta: dict = {}
        self.verfolgen = False
        self.markup = True
        # Was das Markup zeigt (Überprüfen ▸ Markup anzeigen / Überprüfen): nur Anzeige, ändert das Dokument nicht
        self.markup_filter: dict = {"kommentare": True, "einfuegungen": True, "bearbeiter": None, "zeit": None}
        self.autor = lambda: ("Unbekannt", "")
        self._zus_intern = False
        self._hat_zusatz = False
        self._zus_timer = QTimer(self)
        self._zus_timer.setSingleShot(True)
        self._zus_timer.setInterval(200)
        self._zus_timer.timeout.connect(self._overlays_neu)
        self.document().contentsChange.connect(self._inhalt_geaendert)

    def zusatz_binden(self, meta: dict) -> None:
        """Meta-Daten des Dokuments (Kommentartexte, Noten) mit dem Editor teilen."""
        self.kommentare = meta.setdefault("kommentare", {})
        self.noten = meta.setdefault("noten", {"f": {}, "e": {}})
        self.noten.setdefault("f", {}); self.noten.setdefault("e", {})
        self.quellen = meta.setdefault("quellen", [])
        self.zitierweise = meta.setdefault("zitierweise", "APA")
        self._meta = meta
        self._hat_zusatz = bool(self.kommentare or self.noten["f"] or self.noten["e"]) or bool(self.aenderungen())
        self._overlays_neu()
        if hasattr(self, "_blasen_da") and self._blasen_da() != bool(getattr(self, "_blasen_extra", 0)):
            self.apply_page(self.page)                  # ein geöffnetes Dokument mit Kommentaren zeigt die Blasen am Rand gleich, nicht erst nach der ersten Änderung

    # ---- Suchen von Bereichen ----------------------------------------------------------------
    def _fragmente(self):
        return dokument_fragmente(self.document())

    def _bereiche(self, prop, schluessel=None) -> list[dict]:
        """Zusammenhängende Textstücke mit gleicher Eigenschaft: [{von, bis, wert, cf}]."""
        doc = self.document()
        zw = getattr(self, "_bereiche_zw", None)
        if zw is None or zw[0] is not doc or zw[1] != doc.revision():
            zw = self._bereiche_zw = (doc, doc.revision(), {})      # je Dokumentrevision nur einmal über alle Textstücke laufen
        if prop in zw[2]:
            return [dict(x) for x in zw[2][prop]]
        aus: list[dict] = []
        for f in self._fragmente():
            cf = f.charFormat()
            if not cf.hasProperty(prop):
                continue
            wert = cf.property(prop)
            key = schluessel(cf) if schluessel else wert
            v, bis = f.position(), f.position() + f.length()
            if aus and aus[-1]["bis"] == v and aus[-1]["key"] == key:
                aus[-1]["bis"] = bis
            else:
                aus.append({"von": v, "bis": bis, "wert": wert, "key": key, "cf": cf})
        zw[2][prop] = aus
        return [dict(x) for x in aus]

    def kommentar_bereiche(self) -> list[dict]:
        return self._bereiche(P_KOMMENTAR)

    def aenderungen(self) -> list[dict]:
        return self._bereiche(P_AENDERUNG, lambda cf: (cf.stringProperty(P_AENDERUNG), cf.stringProperty(P_AUTOR),
                                                       cf.stringProperty(P_DATUM)))

    def noten_stellen(self) -> list[dict]:
        out = []
        for f in self._fragmente():
            cf = f.charFormat()
            if cf.hasProperty(P_NOTE):
                art, _, nid = cf.stringProperty(P_NOTE).partition(":")
                out.append({"von": f.position(), "bis": f.position() + f.length(), "art": art, "id": int(nid)})
        return out

    # ---- Eigenschaften setzen / entfernen -----------------------------------------------------
    def _bereich_format(self, von: int, bis: int, props: dict) -> None:
        c = QTextCursor(self.document())
        c.setPosition(von); c.setPosition(bis, QTextCursor.KeepAnchor)
        f = QTextCharFormat()
        for k, v in props.items():
            f.setProperty(k, v)
        self._zus_intern = True
        try:
            c.mergeCharFormat(f)
        finally:
            self._zus_intern = False

    def _eigenschaft_weg(self, prop, pred=lambda cf: True, von: int = 0, bis: int | None = None) -> None:
        doc = self.document()
        bis = doc.characterCount() if bis is None else bis
        stuecke = [(f.position(), f.position() + f.length(), f.charFormat()) for f in self._fragmente()
                   if f.charFormat().hasProperty(prop) and pred(f.charFormat()) and f.position() < bis and f.position() + f.length() > von]
        c = QTextCursor(doc)
        c.beginEditBlock()
        self._zus_intern = True
        try:
            for a, b, cf in reversed(stuecke):
                neu = QTextCharFormat(cf)
                neu.clearProperty(prop)
                if prop == P_AENDERUNG:
                    neu.clearProperty(P_AUTOR); neu.clearProperty(P_DATUM)
                c.setPosition(a); c.setPosition(b, QTextCursor.KeepAnchor)
                c.setCharFormat(neu)
        finally:
            self._zus_intern = False
            c.endEditBlock()

    # ---- Kommentare -------------------------------------------------------------------------------
    def kommentar_neu(self, text: str, autor: str | None = None) -> int | None:
        c = self.textCursor()
        if not c.hasSelection():
            c.select(QTextCursor.WordUnderCursor)
        if not c.hasSelection():                                      # kein Wort: das Zeichen daneben trägt den Kommentar
            c = self.textCursor()
            if not c.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor) or c.selectedText() == "\u2029":
                c = self.textCursor()
                if not c.movePosition(QTextCursor.PreviousCharacter, QTextCursor.KeepAnchor) or c.selectedText() == "\u2029":
                    c = self.textCursor()                             # leerer Absatz (wie in der Vorlage: Kommentar an der Schreibmarke)
                    c.insertText("\u200b")                           # unsichtbarer Anker
                    c.movePosition(QTextCursor.PreviousCharacter, QTextCursor.KeepAnchor)
        kid = neue_id(self.kommentare)
        name, init = self.autor()
        if autor:                                                     # z. B. der Name eines KI-Assistenten
            name, init = autor, "".join(w[0] for w in autor.split()[:2]).upper()
        self.kommentare[kid] = {"autor": name, "initialen": init, "datum": datetime.datetime.now(datetime.timezone.utc)
                                .replace(microsecond=0).isoformat(), "text": text}
        self._bereich_format(c.selectionStart(), c.selectionEnd(), {P_KOMMENTAR: kid})
        self.document().setModified(True)
        self._hat_zusatz = True
        self._zus_geaendert()
        return kid

    def set_suchtreffer(self, bereiche: list) -> None:
        """Alle Treffer der Suche farbig hinterlegen (leere Liste nimmt die Markierung weg)."""
        self._such_bereiche = list(bereiche)
        self._overlays_neu()

    def kommentar_text_setzen(self, kid: int, text: str) -> None:
        """Den Text eines Kommentars ändern; Blase und Karte zeigen ihn sofort neu."""
        k = self.kommentare.get(kid)
        if k is None or text == k.get("text"):
            return
        k["text"] = text
        self._blasen_cache = (None, [])
        self.document().setModified(True)
        self._zus_geaendert()
        self.viewport().update()

    def kommentar_geloest(self, kid: int, geloest: bool = True) -> None:
        """Einen Kommentar als gelöst markieren (oder wieder öffnen); er bleibt im Dokument."""
        k = self.kommentare.get(kid)
        if k is None:
            return
        k["geloest"] = bool(geloest)
        self.document().setModified(True)
        self._zus_geaendert()

    def kommentar_loeschen(self, kid: int) -> None:
        self._eigenschaft_weg(P_KOMMENTAR, lambda cf: int(cf.property(P_KOMMENTAR)) == kid)
        self.kommentare.pop(kid, None)
        self.document().setModified(True)
        self._zus_geaendert()

    def kommentare_alle_loeschen(self) -> None:
        self._eigenschaft_weg(P_KOMMENTAR)
        self.kommentare.clear()
        self.document().setModified(True)
        self._zus_geaendert()

    def _springe(self, bereiche: list[dict], delta: int) -> dict | None:
        if not bereiche:
            return None
        pos = self.textCursor().selectionStart() if delta > 0 else self.textCursor().selectionStart()
        if delta > 0:
            kand = [b for b in bereiche if b["von"] > pos] or bereiche[:1]
            ziel = kand[0]
        else:
            kand = [b for b in bereiche if b["von"] < pos] or bereiche[-1:]
            ziel = kand[-1]
        self.select_range(ziel["von"], ziel["bis"])
        self.ensureCursorVisible()
        return ziel

    def kommentar_springen(self, delta: int):
        return self._springe(self.kommentar_bereiche(), delta)

    def kommentar_am_cursor(self) -> int | None:
        c = self.textCursor()
        for b in self.kommentar_bereiche():
            if b["von"] <= c.position() <= b["bis"]:
                return int(b["wert"])
        return None

    # ---- Fuß- und Endnoten -----------------------------------------------------------------------------
    def note_neu(self, art: str, text: str) -> int:
        nid = neue_id(self.noten[art])
        self.noten[art][nid] = text
        c = self.textCursor()
        c.clearSelection()
        f = QTextCharFormat()
        f.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        f.setProperty(P_NOTE, f"{art}:{nid}")
        c.insertText("?", f)
        self.setTextCursor(c)
        self._hat_zusatz = True
        self.noten_neu_nummerieren()
        self.document().setModified(True)
        self._zus_geaendert()
        return nid

    def noten_neu_nummerieren(self) -> None:
        stellen = self.noten_stellen()
        zaehler = {"f": 0, "e": 0}
        aenderungen = []
        for s in stellen:
            zaehler[s["art"]] += 1
            soll = str(zaehler[s["art"]]) if s["art"] == "f" else roemisch(zaehler[s["art"]])
            aenderungen.append((s, soll))
        doc = self.document()
        c = QTextCursor(doc)
        c.beginEditBlock()
        self._zus_intern = True
        try:
            for s, soll in reversed(aenderungen):
                c.setPosition(s["von"]); c.setPosition(s["bis"], QTextCursor.KeepAnchor)
                if c.selectedText() != soll:
                    fmt = c.charFormat()
                    c.insertText(soll, fmt)
        finally:
            self._zus_intern = False
            c.endEditBlock()

    def note_loeschen(self, art: str, nid: int) -> None:
        for s in reversed(self.noten_stellen()):
            if s["art"] == art and s["id"] == nid:
                c = QTextCursor(self.document())
                c.setPosition(s["von"]); c.setPosition(s["bis"], QTextCursor.KeepAnchor)
                c.removeSelectedText()
        self.noten[art].pop(nid, None)
        self.noten_neu_nummerieren()
        self.document().setModified(True)
        self._zus_geaendert()

    def note_an(self, pos: int):
        """(Art, Id) der Note, deren Zeichen an Stelle `pos` liegt (oder direkt davor), sonst None."""
        for s in self.noten_stellen():
            if s["von"] <= pos <= s["bis"]:
                return s["art"], s["id"]
        return None

    def notentext_geaendert(self) -> None:
        """Der Text einer Note wurde im Notenfeld geändert: Seitenansicht und Karten links ziehen nach (gebündelt, nicht bei jedem Zeichen)."""
        self.zusatzGeaendert.emit()
        if not hasattr(self, "_noten_timer"):
            from PySide6.QtCore import QTimer
            self._noten_timer = QTimer(self); self._noten_timer.setSingleShot(True); self._noten_timer.setInterval(400)
            self._noten_timer.timeout.connect(lambda: self._recount() if hasattr(self, "_recount") else None)
        self._noten_timer.start()

    def note_springen(self, delta: int, art: str | None = None):
        """Zur nächsten (delta 1) oder vorigen (-1) Note springen; ``art`` "f" oder "e" nur Fuß- bzw. Endnoten."""
        return self._springe([n for n in self.noten_stellen() if art is None or n["art"] == art], delta)

    # ---- Änderungsverfolgung -----------------------------------------------------------------------------
    def set_verfolgen(self, an: bool) -> None:
        self.verfolgen = an
        self._zus_geaendert()

    def _markiere_geloescht(self, von: int, bis: int, autor: str | None = None) -> None:
        """Statt zu löschen als gelöscht kennzeichnen — eigener, noch nicht angenommener Einfügetext verschwindet wirklich. ``autor``: Name statt des Nutzers (z. B. KI)."""
        name = autor or self.autor()[0]
        c = QTextCursor(self.document())
        c.beginEditBlock()
        stuecke = [(f.position(), f.position() + f.length(), f.charFormat()) for f in self._fragmente()
                   if f.position() < bis and f.position() + f.length() > von]
        for a, b, cf in reversed(stuecke):
            a, b = max(a, von), min(b, bis)
            if cf.hasProperty(P_AENDERUNG) and cf.stringProperty(P_AENDERUNG) == "ins" and cf.stringProperty(P_AUTOR) == name:
                c.setPosition(a); c.setPosition(b, QTextCursor.KeepAnchor)
                self._zus_intern = True
                c.removeSelectedText()
                self._zus_intern = False
            elif not cf.hasProperty(P_AENDERUNG):
                self._bereich_format(a, b, {P_AENDERUNG: "del", P_AUTOR: name, P_DATUM: self._jetzt()})
        c.endEditBlock()
        self._hat_zusatz = True
        self._zus_geaendert()

    def ersetze_verfolgt(self, von: int, bis: int, neu: str, autor: str | None = None) -> bool:
        """Als nachverfolgte Änderung ersetzen: das Alte bleibt als „del“ stehen, ``neu`` kommt direkt dahinter als „ins“ (Autor ``autor`` oder der Nutzer).
        Das Neue übernimmt das Zeichenformat des Alten. Die Einstellung ``verfolgen`` bleibt unberührt. Absatzgrenzen im Alten bleiben stehen, nur die Zeichen
        beider Absätze werden als „del“ gekennzeichnet. Reine Einfügung (von == bis) und reine Löschung (``neu`` leer) gehen auch. → False bei ungültigem Bereich."""
        doc = self.document()
        if not 0 <= von <= bis <= doc.characterCount() - 1:
            return False
        name = autor or self.autor()[0]
        c = QTextCursor(doc)
        c.setPosition(von); c.setPosition(bis, QTextCursor.KeepAnchor)
        fmt = QTextCharFormat(c.charFormat())                 # wie replace_range: Format vor dem Ändern lesen, ohne Verfolgungskennzeichen
        for p in (P_AENDERUNG, P_AUTOR, P_DATUM):
            fmt.clearProperty(p)
        c.beginEditBlock()
        try:
            davor = doc.characterCount()
            if bis > von:
                self._markiere_geloescht(von, bis, name)
            ende = bis - (davor - doc.characterCount())       # eigene „ins“-Stücke des Autors verschwinden dabei wirklich
            if neu:
                c.setPosition(ende)
                n0 = doc.characterCount()
                self._zus_intern = True
                try:
                    c.insertText(neu, fmt)
                finally:
                    self._zus_intern = False
                self._bereich_format(ende, ende + doc.characterCount() - n0, {P_AENDERUNG: "ins", P_AUTOR: name, P_DATUM: self._jetzt()})
        finally:
            c.endEditBlock()
            self._bereiche_zw = None                          # Zwischenspeicher aus dem offenen Edit-Block verwerfen
        self._hat_zusatz = True
        self._zus_geaendert()
        return True

    def _loesche_verfolgt(self, von: int, bis: int, ende: bool) -> bool:
        txt = self.document().toPlainText()[von:bis]
        if "\u2029" in txt or "\n" in txt or bis <= von:
            return False                          # über Absatzgrenzen: normal löschen
        self._markiere_geloescht(von, bis)
        c = self.textCursor()
        c.setPosition(bis if ende else von)
        self.setTextCursor(c)
        return True

    def _verfolgte_taste(self, e) -> bool:
        k = e.key()
        c = self.textCursor()
        if k in (Qt.Key_Backspace, Qt.Key_Delete) and not (e.modifiers() & (Qt.ControlModifier | Qt.AltModifier)):
            if c.hasSelection():
                return self._loesche_verfolgt(c.selectionStart(), c.selectionEnd(), ende=(k == Qt.Key_Delete))
            p = c.position()
            if k == Qt.Key_Backspace and p > 0:
                return self._loesche_verfolgt(p - 1, p, ende=False)
            if k == Qt.Key_Delete and p < self.document().characterCount() - 1:
                return self._loesche_verfolgt(p, p + 1, ende=True)
            return False
        if c.hasSelection() and e.text() and e.text().isprintable() and not (e.modifiers() & Qt.ControlModifier):
            a, b = c.selectionStart(), c.selectionEnd()
            if self._loesche_verfolgt(a, b, ende=True):
                return False                      # danach normal tippen: Text kommt hinter die gelöschte Stelle
        return False

    @staticmethod
    def _jetzt() -> str:
        return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _inhalt_geaendert(self, pos: int, entfernt: int, hinzu: int) -> None:
        if self._zus_intern:
            return
        if self.verfolgen and hinzu > 0 and entfernt == 0:
            name, _ = self.autor()
            doc = self.document()
            c = QTextCursor(doc)
            bis = min(pos + hinzu, doc.characterCount() - 1)
            if bis > pos:
                c.setPosition(pos); c.setPosition(bis, QTextCursor.KeepAnchor)
                cf = c.charFormat()
                eigen = cf.stringProperty(P_AENDERUNG) == "ins" and cf.stringProperty(P_AUTOR) == name
                if not eigen and not cf.hasProperty(P_NOTE):     # auch hinter fremder Einfügung oder in einer Löschung: neue Einfügung
                    c.joinPreviousEditBlock()
                    self._bereich_format(pos, bis, {P_AENDERUNG: "ins", P_AUTOR: name, P_DATUM: self._jetzt()})
                    c.endEditBlock()
                    self._hat_zusatz = True
        neu_luecke = 0 < hinzu < 60 and any(self.document().characterAt(i) in "«»" for i in range(pos, pos + hinzu))
        if self._hat_zusatz or getattr(self, "_luecken_da", False) or neu_luecke or entfernt:
            self._zus_timer.start()
        if self._hat_zusatz:
            QTimer.singleShot(0, self.zusatzGeaendert.emit)

    def aenderung_annehmen(self, b: dict, annehmen: bool = True) -> None:
        art = b["wert"]
        loeschen = (art == "del") == annehmen          # angenommene Löschung / abgelehnte Einfügung entfernen Text
        c = QTextCursor(self.document())
        c.beginEditBlock()
        if loeschen:
            self._zus_intern = True
            c.setPosition(b["von"]); c.setPosition(b["bis"], QTextCursor.KeepAnchor)
            c.removeSelectedText()
            self._zus_intern = False
        else:
            self._eigenschaft_weg(P_AENDERUNG, von=b["von"], bis=b["bis"])
        c.endEditBlock()
        self.document().setModified(True)
        self._zus_geaendert()

    def alle_aenderungen(self, annehmen: bool) -> int:
        n = 0
        for b in reversed(self.aenderungen()):
            self.aenderung_annehmen(b, annehmen)
            n += 1
        return n

    def aenderung_sichtbar(self, b: dict) -> bool:
        """Ob eine Änderung zum gewählten Markup gehört (Bearbeiter, Tag)."""
        f = self.markup_filter
        if not f["einfuegungen"]:
            return False
        if f["bearbeiter"] is not None and b["cf"].stringProperty(P_AUTOR) not in f["bearbeiter"]:
            return False
        return f["zeit"] is None or b["cf"].stringProperty(P_DATUM)[:10] == f["zeit"]

    def angezeigte_aenderungen(self, annehmen: bool) -> int:
        """Nur die Änderungen annehmen oder ablehnen, die das Markup gerade zeigt."""
        n = 0
        for b in reversed(self.aenderungen()):
            if self.aenderung_sichtbar(b):
                self.aenderung_annehmen(b, annehmen)
                n += 1
        return n

    def markup_filter_setzen(self, **werte) -> None:
        self.markup_filter.update(werte)
        if hasattr(self, "apply_page"):
            self.apply_page(self.page)                      # die Blasenfläche kommt oder geht mit dem, was gezeigt wird
        self._overlays_neu()

    def aenderung_springen(self, delta: int):
        return self._springe(self.aenderungen(), delta)

    def aenderung_am_cursor(self) -> dict | None:
        p = self.textCursor().selectionStart()
        q = self.textCursor().selectionEnd()
        for b in self.aenderungen():
            if b["von"] <= p < b["bis"] or (q > b["von"] and p < b["bis"]):
                return b
        return None

    # ---- Anzeige --------------------------------------------------------------------------------------------
    def _zus_geaendert(self) -> None:
        self._overlays_neu()
        self.zusatzGeaendert.emit()
        if hasattr(self, "_blasen_da") and self._blasen_da() != bool(getattr(self, "_blasen_extra", 0)):
            self.apply_page(self.page)                  # die Blasenfläche erscheint mit dem ersten Kommentar
        elif getattr(self, "_blasen_flaeche", None) is not None:
            self._blasen_flaeche.update()

    def set_markup(self, an: bool) -> None:
        self.markup = an
        self._overlays_neu()

    @staticmethod
    def _zusatzauswahl(doc, von: int, bis: int, fmt: QTextCharFormat):
        """Eine Zusatzauswahl (nur Anzeige) von ``von`` bis ``bis``."""
        c = QTextCursor(doc)
        c.setPosition(von); c.setPosition(bis, QTextCursor.KeepAnchor)
        e = QTextEdit.ExtraSelection(); e.cursor = c; e.format = fmt
        return e

    @staticmethod
    def _hintergrund(farbe: QColor) -> QTextCharFormat:
        fmt = QTextCharFormat(); fmt.setBackground(farbe)
        return fmt

    def _overlays_neu(self) -> None:
        """Wellenlinien der Schreibhilfe plus Markup (Kommentare, Änderungen) als Zusatzauswahl — nichts davon landet im Format."""
        sel = self._lese_blasse_auswahl() if hasattr(self, "_lese_blasse_auswahl") else []      # zuerst: alles Übrige tritt zurück
        doc = self.document()
        sel += self._overlay_wellen(doc)
        sel += self._overlay_luecken(doc)
        sel += self._overlay_felder(doc)
        sel += self._overlay_formular(doc)
        if self.markup and (self._hat_zusatz or self.verfolgen):
            sel += self._overlay_kommentare(doc)
            sel += self._overlay_aenderungen(doc)
        for von, bis in getattr(self, "_such_bereiche", ()):                     # alle Treffer des Feldes „Suchen und ersetzen“
            sel.append(self._zusatzauswahl(doc, von, min(bis, doc.characterCount() - 1), self._hintergrund(QColor(255, 176, 46, 130))))
        self.setExtraSelections(sel)
        fl = getattr(self, "_blasen_flaeche", None)
        if fl is not None and fl.isVisible():
            fl.update()

    def _overlay_wellen(self, doc) -> list:
        n = doc.characterCount()
        out = []
        for f in getattr(self, "_wellen", []):
            if f.bis > n or f.von >= f.bis:
                continue
            fmt = QTextCharFormat()
            fmt.setUnderlineStyle(QTextCharFormat.WaveUnderline)
            fmt.setUnderlineColor(QColor(self.WELLE.get(f.art, Farbe.GRAU)))
            out.append(self._zusatzauswahl(doc, f.von, f.bis, fmt))
        return out

    def _overlay_luecken(self, doc) -> list:
        """Lücken «…» der Vorlagen und Textbausteine: gelb nur in der Ansicht, nie in der Datei."""
        if doc.characterCount() >= 300000:
            return []
        from lunivo_writer.editor.dokument.vorlagen import LUECKE, LUECKE_FARBE
        text = doc.toPlainText()
        self._luecken_da = "«" in text
        if not self._luecken_da:
            return []
        fmt = self._hintergrund(QColor(LUECKE_FARBE))
        return [self._zusatzauswahl(doc, m.start(), m.end(), fmt) for m in LUECKE.finditer(text)]

    def _overlay_felder(self, doc) -> list:
        modus = self.opt_text("ui/feldschattierung", "Bei Auswahl") if hasattr(self, "opt_text") else "Nie"
        if modus == "Nie":
            return []
        from lunivo_writer.editor.seite.anzeige_extra import feldbereiche
        pos = self.textCursor().position()
        return [self._zusatzauswahl(doc, von, bis, self._hintergrund(QColor(150, 160, 175, 70)))
                for von, bis in feldbereiche(doc) if modus == "Immer" or von <= pos <= bis]

    def _overlay_formular(self, doc) -> list:
        if not self.opt("ui/formular_schattierung", True):
            return []
        from lunivo_writer.editor.dokument.formular import bereiche as form_bereiche
        return [self._zusatzauswahl(doc, von, bis, self._hintergrund(QColor(76, 110, 245, 38))) for von, bis, _m in form_bereiche(doc)]

    def _overlay_kommentare(self, doc) -> list:
        out = []
        for b in (self.kommentar_bereiche() if self.markup_filter["kommentare"] else []):
            geloest = bool((self.kommentare.get(int(b["wert"])) or {}).get("geloest"))
            farbe = QColor(173, 181, 189, 90) if geloest else QColor(255, 236, 153, 140)            # gelb; gelöst: grau
            out.append(self._zusatzauswahl(doc, b["von"], b["bis"], self._hintergrund(farbe)))
        return out

    @staticmethod
    def _aenderung_format(stil: str, farbe: QColor) -> QTextCharFormat:
        """Darstellung einer verfolgten Änderung nach der gewählten Stilart."""
        fmt = QTextCharFormat()
        fmt.setForeground(farbe)
        if stil == "Durchgestrichen":
            fmt.setFontStrikeOut(True)
        elif stil == "Unterstrichen":
            fmt.setUnderlineStyle(QTextCharFormat.SingleUnderline); fmt.setUnderlineColor(farbe)
        elif stil == "Doppelt unterstrichen":
            fmt.setUnderlineStyle(QTextCharFormat.SingleUnderline); fmt.setUnderlineColor(farbe)
            fmt.setFontOverline(True); fmt.setProperty(QTextFormat.TextUnderlineColor, farbe)
        elif stil == "Fett":
            fmt.setFontWeight(QFont.Bold)
        elif stil == "Kursiv":
            fmt.setFontItalic(True)
        return fmt

    def _overlay_aenderungen(self, doc) -> list:
        ins_stil = self.opt_text("aenderungen/ins_stil", "Unterstrichen")
        del_stil = self.opt_text("aenderungen/del_stil", "Durchgestrichen")
        farb_wahl = self.opt_text("aenderungen/farbe", "Nach Autor")
        out, ende = [], -1
        for b in self.aenderungen():
            stil = del_stil if b["wert"] == "del" else ins_stil
            if not self.aenderung_sichtbar(b) or stil == "Keine":
                continue
            farbe = autor_farbe(b["cf"].stringProperty(P_AUTOR))
            if farb_wahl in FESTE_FARBEN:
                farbe = QColor(FESTE_FARBEN[farb_wahl])
            fmt = self._aenderung_format(stil, farbe)
            if b["von"] == ende:                              # stößt direkt an die vorige Änderung (ersetztes Wort: „del“ + „ins“): ohne eigenen
                fmt.setBackground(QColor(0, 0, 0, 0))         # (durchsichtigen) Hintergrund zeichnet Qt die zweite Zusatzauswahl nicht
            ende = b["bis"]
            out.append(self._zusatzauswahl(doc, b["von"], b["bis"], fmt))
        return out
