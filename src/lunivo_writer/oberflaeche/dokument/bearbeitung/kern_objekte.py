"""Objekte im Editor: Auswahl, Angaben und Ändern von Bildern, Formen, Textfeldern, Diagrammen und SmartArt — frei positioniert oder im Text.

``KernObjekte`` gehört zu ``KernEditor`` (``kern_editor.py``). Die Bild-, Form- und Layoutfunktionen in ``editor/objekte/`` arbeiten mit einer „Angabe“
(Wörterbuch mit den Schlüsseln ``b``, ``h``, ``bh``, ``xh``, ``ah``, ``bv``, ``yv``, ``av``, ``hinter``, ``n``, ``dreh``, ``fuell``, ``rand``, ``fx`` …). Hier wird
diese Angabe aus einem Objekt des Dokumentmodells gebildet und nach dem Ändern über die Bearbeitungssitzung (ein Rückgängig-Schritt) zurückgeschrieben.

Ziel eines Bildbefehls (``z``): ``("frei", ("o", Id), Angabe, Bild)`` für ein frei positioniertes Objekt, ``("text", InlineObjekt)`` für eines im Text.
"""
from __future__ import annotations

import dataclasses

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRectF
from PySide6.QtGui import QImage

from lunivo_writer.core.document.dokument import UMBRUCH_ARTEN, Auswahl, InlineObjekt, Position

ANGABE_FELDER = {"b", "h", "bh", "xh", "ah", "bv", "yv", "av", "hinter", "art", "n", "alt", "umbruch"}


def angabe_von(o) -> dict:
    """Die Angabe eines frei positionierten Objekts (``FreiesObjekt``)."""
    d = {k: v for k, v in o.daten.items() if k != "daten"}
    d.update(art=o.art, b=o.breite, h=o.hoehe, bh=o.bezug_h, xh=o.x, ah=o.ausr_h, bv=o.bezug_v, yv=o.y, av=o.ausr_v, hinter=o.umbruch == "hinter",
             n=o.ressource, alt=o.alt_text, umbruch=o.umbruch)
    if isinstance(o.daten.get("daten"), dict):
        d["daten"] = dict(o.daten["daten"])
    return d


def felder_aus_angabe(a: dict) -> dict:
    """Die Felder des ``FreiesObjekt``, die eine (geänderte) Angabe beschreibt, für ``objekt_aendern``."""
    umbruch = a.get("umbruch") if a.get("umbruch") in UMBRUCH_ARTEN and a.get("umbruch") not in ("hinter", "vor") else ("hinter" if a.get("hinter") else "vor")
    daten = {k: v for k, v in a.items() if k not in ANGABE_FELDER and k != "daten" and not k.startswith("_")}
    if a.get("daten"):
        daten["daten"] = dict(a["daten"])
    return {"breite": float(a.get("b", 0.0)), "hoehe": float(a.get("h", 0.0)), "bezug_h": a.get("bh", "spalte"), "x": float(a.get("xh", 0.0)),
            "ausr_h": a.get("ah") or "", "bezug_v": a.get("bv", "absatz"), "y": float(a.get("yv", 0.0)), "ausr_v": a.get("av") or "", "umbruch": umbruch,
            "ressource": a.get("n", ""), "alt_text": a.get("alt", ""), "daten": daten}


class _BildFormat:
    """Maße eines Bildes im Text (die Fenster fragen ``width()``, ``height()`` und ``name()``)."""

    def __init__(self, o: InlineObjekt):
        self._o = o

    def width(self) -> float:
        return self._o.breite

    def height(self) -> float:
        return self._o.hoehe

    def name(self) -> str:
        return self._o.ressource


class KernObjekte:
    """Gemischt in ``KernEditor``."""

    # ---- Auswahl ---------------------------------------------------------------------------------------------------------------------------
    @property
    def _frei_sel(self):
        oid = self.ansicht.gewaehltes_objekt
        return ("o", oid) if oid is not None and oid in self.sitzung.dokument.objekte else None

    @_frei_sel.setter
    def _frei_sel(self, wert) -> None:
        neu = wert[1] if wert else None
        if neu != self.ansicht.gewaehltes_objekt:
            self.ansicht.gewaehltes_objekt = neu
            self.ansicht.update()
            self.freiAuswahlGeaendert.emit()

    def inline_gewaehlt(self):
        """Das Objekt im Text, das die Auswahl genau umfasst (ein Zeichen), sonst ``None``."""
        s = self.sitzung
        if s.auswahl.leer:
            return None
        von, bis = s._bereich()
        if von.absatz_id != bis.absatz_id or bis.versatz - von.versatz != 1:
            return None
        versatz = 0
        for x in s._absatz(von.absatz_id).inhalte:
            if isinstance(x, InlineObjekt):
                if versatz == von.versatz:
                    return x
                versatz += 1
            else:
                versatz += len(x.text)
        return None

    def objekt_ziel(self):
        """Das Ziel der Bildbefehle: gewähltes freies Objekt oder gewähltes Objekt im Text; sonst ``None``."""
        o = self.objekt_gewaehlt()
        if o is not None:
            return ("frei", ("o", o.id), angabe_von(o), self.objekt_bild(o) or QImage())
        i = self.inline_gewaehlt()
        return ("text", i) if i is not None else None

    def objekt_art(self) -> str | None:
        o = self.objekt_gewaehlt()
        return o.art if o is not None else None

    def bild_format(self):
        """Maße des gewählten Bildes im Text (``None``, wenn die Auswahl kein solches Objekt ist)."""
        i = self.inline_gewaehlt()
        return _BildFormat(i) if i is not None else None

    def _bild_cursor(self):
        return self.inline_gewaehlt()

    def _frei_liste(self) -> list:
        """[(Schlüssel, Angabe, Bild, Rechteck in Koordinaten der Ansicht, hinten, Seite)] der frei positionierten Objekte in Dokumentreihenfolge."""
        aus = []
        erg = self.ansicht.ergebnis()
        for oid, o in self.sitzung.dokument.objekte.items():
            seite, r = erg.objekte.get(oid, (0, None))
            blatt, z = self.ansicht.blatt(seite), self.ansicht.zoom
            rect = QRectF(blatt.left() + r.x * z, blatt.top() + r.y * z, r.width * z, r.height * z) if r is not None else QRectF()
            aus.append((("o", oid), angabe_von(o), self.objekt_bild(o) or QImage(), rect, o.umbruch == "hinter", seite))
        return aus

    # ---- Ändern ----------------------------------------------------------------------------------------------------------------------------
    def angabe_speichern(self, objekt_id: int, angabe: dict) -> bool:
        """Schreibt die Angabe eines freien Objekts zurück (mit den Bildern, die ``addResource`` des Dokuments gesammelt hat) in einem Schritt."""
        wartend, self._wartende_bilder = dict(getattr(self, "_wartende_bilder", {})), {}

        def f(s):
            with s.gruppe("Objekt ändern"):
                for name, daten in wartend.items():
                    s.ressource_setzen(name, daten)
                s.objekt_aendern(objekt_id, **felder_aus_angabe(angabe))
        ok = self.ansicht._aendern(f)
        self.ansicht.update()
        return ok

    def inline_aendern(self, objekt_id: int, **felder) -> bool:
        """Ändert ein Objekt im Text (Größe, Daten, Bild …); neue Bilder aus ``bild_ressource_neu`` kommen im selben Schritt ins Dokument."""
        wartend, self._wartende_bilder = dict(getattr(self, "_wartende_bilder", {})), {}

        def f(s):
            with s.gruppe("Objekt ändern"):
                for name, daten in wartend.items():
                    s.ressource_setzen(name, daten)
                s.objekt_aendern(objekt_id, **felder)
        return self.ansicht._aendern(f)

    def bild_setzen(self, width: float | None = None, height: float | None = None, alt: str | None = None, dekor: bool | None = None) -> bool:
        """Größe, Alternativtext und „dekorativ“ des gewählten Bildes im Text."""
        i = self.inline_gewaehlt()
        if i is None:
            return False
        felder: dict = {}
        if width is not None:
            felder["breite"] = float(width)
        if height is not None:
            felder["hoehe"] = float(height)
        if alt is not None:
            felder["alt_text"] = alt
        if dekor is not None:
            felder["daten"] = {**i.daten, "dekor": bool(dekor)}
        return bool(felder) and self.inline_aendern(i.id, **felder)

    def bild_im_text_einfuegen(self, img: QImage, alt: str = "", art: str | None = None, daten: dict | None = None) -> bool:
        """Fügt ein Bild (Form, WordArt, Diagramm, Datei …) wie ein Zeichen an der Schreibmarke ein, auf die Inhaltsbreite begrenzt."""
        b, h = float(img.width()), float(img.height())
        maxb = self.page.content_width_px
        if b > maxb:
            h, b = h * maxb / b, maxb
        d = {"daten": dict(daten)} if daten else {}
        png = self._png(img)
        return self.ansicht._aendern(lambda s: s.objekt_einfuegen(art or "bild", b, h, bilddaten=png, daten=d, alt_text=alt))

    def inline_daten(self, art: str | None = None) -> dict | None:
        """Die Parameter des gewählten Objekts im Text (Kopie); mit ``art`` nur, wenn es von dieser Art ist."""
        i = self.inline_gewaehlt()
        if i is None or (art is not None and i.art != art):
            return None
        return dict(i.daten.get("daten") or {})

    def inline_neu_zeichnen(self, img: QImage, daten: dict, breite: float | None = None, hoehe: float | None = None, alt: str | None = None) -> bool:
        """Das gewählte Objekt im Text bekommt ein neues Bild und neue Parameter (Breite bleibt, Höhe folgt dem Seitenverhältnis, wenn nichts angegeben ist)."""
        i = self.inline_gewaehlt()
        if i is None:
            return False
        b = breite if breite is not None else (i.breite or float(img.width()))
        h = hoehe if hoehe is not None else b * img.height() / max(1, img.width())
        felder = {"ressource": self.bild_ressource_neu(img), "breite": b, "hoehe": h, "daten": {**i.daten, "daten": dict(daten)}}
        if alt is not None:
            felder["alt_text"] = alt
        return self.inline_aendern(i.id, **felder)

    def inline_objekte_der_auswahl(self) -> list | None:
        """Die Objekte im Text, wenn die Auswahl nur aus Objekten (und Leerraum) besteht; sonst ``None``."""
        s = self.sitzung
        if s.auswahl.leer:
            return None
        von, bis = s._bereich()
        if von.absatz_id != bis.absatz_id:
            return None
        aus, versatz = [], 0
        for x in s._absatz(von.absatz_id).inhalte:
            n = 1 if isinstance(x, InlineObjekt) else len(x.text)
            if versatz + n > von.versatz and versatz < bis.versatz:
                if isinstance(x, InlineObjekt):
                    aus.append(x)
                elif x.text.strip():
                    return None
            versatz += n
        return aus

    def bild_ressource(self, name: str):
        """Das Bild einer Ressource (auch eines, das noch nicht gespeichert ist) oder ``None``."""
        roh = getattr(self, "_wartende_bilder", {}).get(name) or self.sitzung.dokument.ressourcen.get(name)
        if not roh:
            return None
        img = QImage()
        return img if img.loadFromData(bytes(roh)) else None

    def bild_ressource_neu(self, img: QImage, name: str | None = None) -> str:
        """Legt ein Bild für die nächste Angabe bereit; → sein Name (er gehört dann in ``n`` bzw. ``fuell['n']`` der Angabe)."""
        if name is None:
            n = 1
            while self.bild_ressource(f"frei-{n}") is not None:
                n += 1
            name = f"frei-{n}"
        if not hasattr(self, "_wartende_bilder"):
            self._wartende_bilder = {}
        self._wartende_bilder[name] = self._png(img)
        return name

    def objekt_inline_rechteck(self, objekt_id: int):
        """(Seite, Rechteck) eines Objekts im Text in Seitenkoordinaten oder ``None``."""
        pos = self.sitzung.objekt_position(objekt_id)
        if pos is None:
            return None
        erg = self.ansicht.ergebnis()
        von, bis = erg.cursor(pos.absatz_id, pos.versatz), erg.cursor(pos.absatz_id, pos.versatz + 1)
        if von is None or bis is None:
            return None
        o = self.sitzung._inline(objekt_id)[2]
        from lunivo_writer.core.geometry import Rect
        return von[0], Rect(von[1].x, von[1].y, max(bis[1].x - von[1].x, 1.0), o.hoehe)

    def inline_bei(self, ziel: Position, punkt) -> int | None:
        """Id des Objekts im Text, das an der Stelle ``ziel`` getroffen ist (Klick auf das Zeichen), sonst ``None``."""
        a = self.sitzung._absatz(ziel.absatz_id)
        versatz = 0
        for x in a.inhalte:
            if isinstance(x, InlineObjekt):
                if versatz in (ziel.versatz, ziel.versatz - 1):
                    r = self.objekt_inline_rechteck(x.id)
                    if r is not None and r[1].x - 2 <= punkt[0] <= r[1].right + 2:
                        return x.id
                versatz += 1
            else:
                versatz += len(x.text)
        return None

    def inline_waehlen(self, objekt_id: int) -> None:
        pos = self.sitzung.objekt_position(objekt_id)
        if pos is not None:
            self.sitzung.setze_auswahl(pos, Position(pos.absatz_id, pos.versatz + 1))
            self.ansicht.gewaehltes_objekt = None
            self.ansicht.nach_bewegung()

    # ---- Befehle ---------------------------------------------------------------------------------------------------------------------------
    def objekt_drehen(self, grad: float) -> bool:
        o = self.objekt_gewaehlt()
        if o is None:
            return False
        return self.objekt_setzen(o.id, daten={**o.daten, "dreh": (float(o.daten.get("dreh", 0.0)) + grad) % 360.0})

    def objekt_spiegeln(self, waagerecht: bool) -> bool:
        o = self.objekt_gewaehlt()
        if o is None:
            return False
        schl = "flipH" if waagerecht else "flipV"
        return self.objekt_setzen(o.id, daten={**o.daten, schl: not o.daten.get(schl)})

    def objekt_umbruch(self, art: str) -> bool:
        """Textumbruch des gewählten Objekts: ``textfluss`` (im Text), ``quadrat``, ``eng``, ``durch``, ``oben_unten``, ``hinter``, ``vor``."""
        o = self.objekt_gewaehlt()
        i = self.inline_gewaehlt()
        if art == "textfluss":
            if o is None:
                return False
            return self.ansicht._aendern(lambda s: s.objekt_zu_inline(o.id))
        if o is not None:
            return self.objekt_setzen(o.id, umbruch=art)
        if i is not None:
            def f(s):
                with s.gruppe("Textumbruch"):
                    s.objekt_zu_frei(i.id, art)
            ok = self.ansicht._aendern(f)
            if ok:
                self.ansicht.gewaehltes_objekt = i.id
                self.freiAuswahlGeaendert.emit()
            return ok
        return False

    # ---- Anbindung der Zeichenfläche -------------------------------------------------------------------------------------------------------
    def objekte_verbinden(self) -> None:
        """Belegt die Rückrufe der Zeichenfläche (Auswahl, Ziehen, Drehen, Schaltflächen, Doppelklick) mit den Operationen des Editors."""
        a = self.ansicht
        a.objekt_geaendert = self.objekt_verschieben
        a.objekt_gedreht = self.objekt_gedreht
        a.inline_gewaehlt_id = lambda: (lambda i: i.id if i is not None else None)(self.inline_gewaehlt())
        a.inline_rechteck = self.objekt_inline_rechteck
        a.inline_bei = self.inline_bei
        a.inline_waehlen = self.inline_waehlen
        a.inline_groesse = self.inline_groesse
        a.objekt_art_von = self.objekt_art_von
        a.objekt_doppelklick = self.objekt_doppelklick
        a.zuschnitt_aktiv = lambda: bool(self.__dict__.get("_frei_zuschnitt"))
        a.zuschnitt_geaendert = self.objekt_zuschneiden
        a.zuschnitt_lesen = self.zuschnitt_lesen
        a.objektKnopf.connect(self._frei_knopf)
        a.freiform_hook = self.freiform_ereignis
        a.objekt_teil_klick = self.teil_klick
        a.freiform_taste = self.freiform_taste
        a.nach_zeichnen = self.freiform_zeichnen

        def nachfuehren(*_):
            if getattr(self, "_frei_edit", None) is not None:
                from lunivo_writer.editor.objekte import frei_objekt as FO
                FO.edit_platzieren(self)
        a.zoomChanged.connect(nachfuehren)
        a.geaendert.connect(nachfuehren)

    @property
    def _frei_treffer(self) -> list:
        """[(Schlüssel, Angabe, Rechteck in der Ansicht, hinten, Seite)] — wie ``_frei_liste`` ohne Bild (für Diagramm-, SmartArt- und Freiformbedienung)."""
        return [(k, a, r, h, n) for k, a, _b, r, h, n in self._frei_liste()]

    _frei_vorlaeufig: dict = {}

    def _frei_angabe(self):
        """Die Angabe des gewählten freien Objekts oder ``None``."""
        o = self.objekt_gewaehlt()
        return angabe_von(o) if o is not None else None

    @staticmethod
    def _frei_abbilden(r, a: dict, rr):
        from lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_geometrie import abbilden
        return abbilden(r, a, rr)

    def window(self):
        return self.fenster

    def teil_klick(self, pos) -> None:
        """Klick in das gewählte Diagramm oder SmartArt: wählt den Teil bzw. Knoten darunter."""
        a = self._frei_angabe()
        if a is not None and a.get("art") in ("diagramm", "smartart"):
            self._frei_teil_klick(pos, a)

    def freiform_ereignis(self, art: str, ev) -> bool:
        """Maus im Punktebearbeitungsmodus der Freiform (Zeichentools ▸ Form bearbeiten); ``True``, wenn das Ereignis dazu gehört."""
        from lunivo_writer.oberflaeche.dokument.bearbeitung import freiform_bedienung as FB
        return FB.aktiv(self) and FB.maus(self, ev, art)

    def freiform_taste(self, ev) -> bool:
        from lunivo_writer.oberflaeche.dokument.bearbeitung import freiform_bedienung as FB
        return FB.taste(self, ev)

    def freiform_zeichnen(self, p) -> None:
        from lunivo_writer.oberflaeche.dokument.bearbeitung import freiform_bedienung as FB
        if FB.aktiv(self):
            t = FB._eintrag(self)
            if t is not None:
                FB.zeichnen(self, p, t[2], t[1])

    def objekt_gedreht(self, objekt_id: int, winkel: float) -> None:
        o = self.sitzung.dokument.objekte.get(objekt_id)
        if o is not None:
            self.objekt_setzen(objekt_id, daten={**o.daten, "dreh": float(winkel) % 360.0})

    def inline_groesse(self, objekt_id: int, breite: float, hoehe: float) -> None:
        self.inline_aendern(objekt_id, breite=breite, hoehe=hoehe)

    def objekt_art_von(self, art: str, objekt_id: int):
        if art == "frei":
            o = self.sitzung.dokument.objekte.get(objekt_id)
            return o.art if o is not None else None
        f = self.sitzung._inline(objekt_id)
        return f[2].art if f else None

    def objekt_doppelklick(self, objekt_id: int) -> None:
        """Doppelklick auf ein freies Objekt: Text in Form, Textfeld und WordArt bearbeiten, sonst das Layoutfenster."""
        o = self.sitzung.dokument.objekte.get(objekt_id)
        if o is None:
            return
        if o.art == "smartart":
            if not self.frei_knoten_edit_starten():
                self.bild_layout_dialog()
            return
        if o.art in ("form", "textfeld", "wordart"):
            from lunivo_writer.editor.objekte import frei_objekt as FO
            FO.bearbeiten_starten(self)
        else:
            self.bild_layout_dialog()

    def zuschnitt_lesen(self, objekt_id: int) -> tuple:
        """Der Zuschnitt (links, oben, rechts, unten) als Anteile des freien Objekts."""
        from lunivo_writer.editor.objekte import bildzuschnitt as BZ
        o = self.sitzung.dokument.objekte.get(objekt_id)
        return BZ.lesen(angabe_von(o)) if o is not None else (0.0, 0.0, 0.0, 0.0)

    def objekt_zuschneiden(self, objekt_id: int, seite: int, rect, zu: tuple) -> None:
        """Zuschneiden-Modus: die Kanten sind gezogen; das Objekt bekommt den neuen sichtbaren Ausschnitt und seine Lage (ein Schritt)."""
        from lunivo_writer.editor.objekte import bildzuschnitt as BZ
        with self.sitzung.gruppe("Zuschneiden"):
            self.objekt_verschieben(objekt_id, seite, rect)
            BZ.setzen(self, self.objekt_ziel(), zu=tuple(zu), b=float(rect.width), h=float(rect.height))
