"""Objektoperationen der Sitzung: Bilder, Formen, Textfelder und andere grafische Objekte — im Text oder frei positioniert —
sowie Textrahmen im Fluss. Ohne Qt."""
from __future__ import annotations

import dataclasses

from core.dokument.dokument import OBJEKT_ARTEN, UMBRUCH_ARTEN, Absatz, FreiesObjekt, InlineObjekt, Position, Rahmen, normalisiere
from core.dokument.formate import pruefe, verschmelze
from core.bearbeitung.texteingabe import alle_absaetze
from core.bearbeitung.verlauf import BearbeitungsFehler, schritt

_FELDER_INLINE = {f.name for f in dataclasses.fields(InlineObjekt)} - {"id"}
_FELDER_FREI = {f.name for f in dataclasses.fields(FreiesObjekt)} - {"id"}


class ObjektTeil:
    # ---- Ressourcen (Bilddaten) ------------------------------------------------------------------------------------------
    @schritt("Bilddaten", "objekt")
    def ressource_setzen(self, schluessel: str, daten: bytes | None) -> None:
        """Legt Bilddaten unter einem Schlüssel ab; ``None`` entfernt sie."""
        if daten is None:
            if schluessel in self.dokument.ressourcen:
                self._dict(self.dokument.ressourcen, schluessel)
            return
        if not isinstance(daten, (bytes, bytearray)):
            raise BearbeitungsFehler("Bilddaten müssen Bytes sein")
        self._dict(self.dokument.ressourcen, schluessel, bytes(daten))

    @schritt("Bilddaten aufräumen", "objekt")
    def ressourcen_bereinigen(self) -> int:
        """Entfernt Bilddaten, auf die kein Objekt mehr verweist. Gibt die Zahl der entfernten Einträge zurück."""
        benutzt = {o.ressource for o in self.dokument.objekte.values()}
        benutzt |= {x.ressource for a in self.dokument.absaetze() for x in a.inhalte if isinstance(x, InlineObjekt)}
        for o in [*self.dokument.objekte.values(), *(x for a in self.dokument.absaetze() for x in a.inhalte if isinstance(x, InlineObjekt))]:
            benutzt |= {str(o.daten.get("orig") or ""), str((o.daten.get("fuell") or {}).get("n", "") if isinstance(o.daten.get("fuell"), dict) else "")}
        for abschnitt in self.dokument.abschnitte:
            benutzt |= {str(b.get("ressource", "")) for b in abschnitt.seite.bilder if isinstance(b, dict)}
        ueber = [k for k in self.dokument.ressourcen if k not in benutzt]
        for k in ueber:
            self._dict(self.dokument.ressourcen, k)
        return len(ueber)

    def _pruefe_objekt(self, art: str, breite: float, hoehe: float, ressource: str) -> None:
        if art not in OBJEKT_ARTEN:
            raise BearbeitungsFehler(f"Unbekannte Objektart: {art}")
        if breite < 0 or hoehe < 0:
            raise BearbeitungsFehler("Breite und Höhe dürfen nicht negativ sein")
        if ressource and ressource not in self.dokument.ressourcen:
            raise BearbeitungsFehler(f"Keine Bilddaten unter „{ressource}“")

    def _ablegen(self, objekt_id: int, bilddaten) -> str:
        schluessel = f"objekt-{objekt_id}"
        self._dict(self.dokument.ressourcen, schluessel, bytes(bilddaten))
        return schluessel

    # ---- Objekte im Text --------------------------------------------------------------------------------------------------
    @schritt("Objekt einfügen", "objekt")
    def objekt_einfuegen(self, art: str = "bild", breite: float = 0.0, hoehe: float = 0.0, pos: Position | None = None, *,
                         ressource: str = "", bilddaten: bytes | None = None, daten: dict | None = None, alt_text: str = "",
                         format: dict | None = None) -> int:
        """Fügt ein Objekt wie ein Zeichen in den Text ein. ``bilddaten`` werden als Ressource abgelegt. Gibt die Objekt-Id zurück."""
        if pos is None:
            if not self.auswahl.leer:
                self.loeschen()
            pos = self.auswahl.kopf
        pos = self._pruefe_position(pos)
        oid = self._id()
        if bilddaten is not None:
            ressource = self._ablegen(oid, bilddaten)
        self._pruefe_objekt(art, breite, hoehe, ressource)
        o = InlineObjekt(oid, art, float(breite), float(hoehe), ressource, dict(daten or {}), alt_text, pruefe("zeichen", format or {}))
        self._einsetzen(self._absatz(pos.absatz_id), pos.versatz, [o])
        self._setze(Position(pos.absatz_id, pos.versatz + 1))
        return oid

    def objekt(self, objekt_id: int):
        """Das Objekt mit dieser Id — ``InlineObjekt`` oder ``FreiesObjekt``; ``None``, wenn es keines gibt."""
        if objekt_id in self.dokument.objekte:
            return self.dokument.objekte[objekt_id]
        f = self._inline(objekt_id)
        return f[2] if f else None

    def objekt_position(self, objekt_id: int) -> Position | None:
        """Die Textstelle vor einem Objekt im Text; bei einem freien Objekt der Anfang seines Ankerabsatzes."""
        if objekt_id in self.dokument.objekte:
            return Position(self.dokument.objekte[objekt_id].anker, 0)
        f = self._inline(objekt_id)
        return Position(f[0].id, f[1]) if f else None

    def _inline(self, objekt_id: int):
        for a in self.dokument.absaetze():
            versatz = 0
            for x in a.inhalte:
                if isinstance(x, InlineObjekt):
                    if x.id == objekt_id:
                        return a, versatz, x
                    versatz += 1
                else:
                    versatz += len(x.text)
        return None

    @schritt("Objekt ändern", "objekt")
    def objekt_aendern(self, objekt_id: int, **felder) -> None:
        """Ändert Eigenschaften eines Objekts (Größe, Daten, Alternativtext, bei freien Objekten auch Lage, Umbruch, Anker …).
        ``bilddaten=…`` tauscht das Bild aus."""
        bilddaten = felder.pop("bilddaten", None)
        if bilddaten is not None:
            felder["ressource"] = self._ablegen(objekt_id, bilddaten)
        if objekt_id in self.dokument.objekte:
            alt = self.dokument.objekte[objekt_id]
            fremd = set(felder) - _FELDER_FREI
            if fremd:
                raise BearbeitungsFehler(f"Unbekannte Eigenschaft: {', '.join(sorted(fremd))}")
            neu = dataclasses.replace(alt, **felder)
            self._pruefe_objekt(neu.art, neu.breite, neu.hoehe, neu.ressource)
            if neu.umbruch not in UMBRUCH_ARTEN:
                raise BearbeitungsFehler(f"Unbekannter Textumbruch: {neu.umbruch}")
            self._absatz(neu.anker)
            self._dict(self.dokument.objekte, objekt_id, neu)
            self._beruehrt(alt.anker, neu.anker)
            return
        f = self._inline(objekt_id)
        if f is None:
            raise BearbeitungsFehler(f"Kein Objekt mit der Id {objekt_id}")
        a, _versatz, alt = f
        fremd = set(felder) - _FELDER_INLINE
        if fremd:
            raise BearbeitungsFehler(f"Unbekannte Eigenschaft: {', '.join(sorted(fremd))}")
        if "format" in felder:
            felder["format"] = pruefe("zeichen", felder["format"])
        neu = dataclasses.replace(alt, **felder)
        self._pruefe_objekt(neu.art, neu.breite, neu.hoehe, neu.ressource)
        self._attr(a, "inhalte", [neu if x is alt else x for x in a.inhalte])
        self._beruehrt(a.id)

    @schritt("Objekt entfernen", "objekt")
    def objekt_entfernen(self, objekt_id: int) -> None:
        if objekt_id in self.dokument.objekte:
            self._beruehrt(self.dokument.objekte[objekt_id].anker)
            self._dict(self.dokument.objekte, objekt_id)
            return
        f = self._inline(objekt_id)
        if f is None:
            raise BearbeitungsFehler(f"Kein Objekt mit der Id {objekt_id}")
        a, versatz, alt = f
        self._attr(a, "inhalte", normalisiere([x for x in a.inhalte if x is not alt]))
        self._beruehrt(a.id)
        self._verwaiste_entfernen([alt])
        self._auswahl_retten(Position(a.id, versatz))

    # ---- Frei positionierte Objekte ---------------------------------------------------------------------------------------
    @schritt("Objekt einfügen", "objekt")
    def objekt_frei_einfuegen(self, art: str = "bild", breite: float = 0.0, hoehe: float = 0.0, anker: int | None = None, *,
                              bilddaten: bytes | None = None, **felder) -> int:
        """Legt ein frei positioniertes Objekt an, verankert am Absatz ``anker`` (sonst am Absatz der Schreibmarke)."""
        fremd = set(felder) - _FELDER_FREI
        if fremd:
            raise BearbeitungsFehler(f"Unbekannte Eigenschaft: {', '.join(sorted(fremd))}")
        anker = self.auswahl.kopf.absatz_id if anker is None else anker
        self._absatz(anker)
        oid = self._id()
        if bilddaten is not None:
            felder["ressource"] = self._ablegen(oid, bilddaten)
        o = FreiesObjekt(oid, anker, art, float(breite), float(hoehe), **felder)
        self._pruefe_objekt(o.art, o.breite, o.hoehe, o.ressource)
        if o.umbruch not in UMBRUCH_ARTEN:
            raise BearbeitungsFehler(f"Unbekannter Textumbruch: {o.umbruch}")
        if "ebene" not in felder:
            o.ebene = max((x.ebene for x in self.dokument.objekte.values()), default=0) + 1
        self._dict(self.dokument.objekte, oid, o)
        self._beruehrt(anker)
        return oid

    @schritt("Textumbruch", "objekt")
    def objekt_zu_frei(self, objekt_id: int, umbruch: str = "quadrat", **felder) -> int:
        """Löst ein Objekt aus dem Text und positioniert es frei (Textumbruch). Die Id bleibt."""
        f = self._inline(objekt_id)
        if f is None:
            raise BearbeitungsFehler(f"Kein Objekt im Text mit der Id {objekt_id}")
        a, _versatz, alt = f
        self.objekt_entfernen(objekt_id)
        o = FreiesObjekt(objekt_id, a.id, alt.art, alt.breite, alt.hoehe, umbruch=umbruch, ressource=alt.ressource, daten=dict(alt.daten),
                         alt_text=alt.alt_text, ebene=max((x.ebene for x in self.dokument.objekte.values()), default=0) + 1)
        fremd = set(felder) - _FELDER_FREI
        if fremd or umbruch not in UMBRUCH_ARTEN:
            raise BearbeitungsFehler("Unbekannte Eigenschaft oder unbekannter Textumbruch")
        self._dict(self.dokument.objekte, objekt_id, dataclasses.replace(o, **felder))
        return objekt_id

    @schritt("Textumbruch", "objekt")
    def objekt_zu_inline(self, objekt_id: int, pos: Position | None = None) -> int:
        """Setzt ein frei positioniertes Objekt wie ein Zeichen in den Text (an ``pos``, sonst an den Anfang seines Ankerabsatzes)."""
        alt = self.dokument.objekte.get(objekt_id)
        if alt is None:
            raise BearbeitungsFehler(f"Kein frei positioniertes Objekt mit der Id {objekt_id}")
        pos = self._pruefe_position(Position(alt.anker, 0) if pos is None else pos)
        self._dict(self.dokument.objekte, objekt_id)
        o = InlineObjekt(objekt_id, alt.art, alt.breite, alt.hoehe, alt.ressource, dict(alt.daten), alt.alt_text)
        self._einsetzen(self._absatz(pos.absatz_id), pos.versatz, [o])
        return objekt_id

    @schritt("Reihenfolge", "objekt")
    def objekt_ebene(self, objekt_id: int, wohin: str) -> None:
        """Stapelreihenfolge: ``vorn``, ``hinten``, ``vor`` (eine Ebene nach vorn), ``zurueck``."""
        alt = self.dokument.objekte.get(objekt_id)
        if alt is None:
            raise BearbeitungsFehler(f"Kein frei positioniertes Objekt mit der Id {objekt_id}")
        ebenen = [o.ebene for o in self.dokument.objekte.values()]
        ziel = {"vorn": max(ebenen) + 1, "hinten": min(ebenen) - 1, "vor": alt.ebene + 1, "zurueck": alt.ebene - 1}.get(wohin)
        if ziel is None:
            raise BearbeitungsFehler(f"Unbekannte Richtung: {wohin}")
        if wohin in ("vor", "zurueck"):                  # mit dem Objekt tauschen, das dort steht
            for o in list(self.dokument.objekte.values()):
                if o.id != objekt_id and o.ebene == ziel:
                    self._dict(self.dokument.objekte, o.id, dataclasses.replace(o, ebene=alt.ebene))
        self._dict(self.dokument.objekte, objekt_id, dataclasses.replace(alt, ebene=ziel))
        self._beruehrt(alt.anker)

    def objekte_an(self, absatz_id: int) -> list:
        """Die frei positionierten Objekte, die an diesem Absatz verankert sind, in Stapelreihenfolge."""
        return sorted((o for o in self.dokument.objekte.values() if o.anker == absatz_id), key=lambda o: o.ebene)

    # ---- Textrahmen im Fluss ------------------------------------------------------------------------------------------------
    def _rahmen(self, rahmen_id: int) -> Rahmen:
        f = self.dokument.finde(rahmen_id)
        if f is None or not isinstance(f[3], Rahmen):
            raise BearbeitungsFehler(f"Kein Rahmen mit der Id {rahmen_id}")
        return f[3]

    @schritt("Rahmen einfügen", "tabelle")
    def rahmen_einfuegen(self, format: dict | None = None, pos: Position | None = None) -> int:
        """Fügt einen leeren Textrahmen ein — am Absatzanfang vor dem Absatz, sonst wird der Absatz geteilt. Die Schreibmarke steht
        danach im Rahmen. Gibt die Id des Rahmens zurück."""
        pos = self._pruefe_position(self.auswahl.kopf if pos is None else pos)
        _bes, bloecke, i, _a = self.dokument.finde(pos.absatz_id)
        if pos.versatz > 0:
            self._teilen(pos)
            i += 1
        r = Rahmen(self._id(), [Absatz(self._id())], pruefe("rahmen", format or {}))
        self._liste(bloecke, i, 0, [r])
        self._beruehrt(r.id)
        self._setze(Position(r.bloecke[0].id, 0))
        return r.id

    @schritt("Rahmen löschen", "tabelle")
    def rahmen_loeschen(self, rahmen_id: int) -> None:
        """Entfernt den Rahmen samt Inhalt."""
        r = self._rahmen(rahmen_id)
        _bes, bloecke, i, _r = self.dokument.finde(rahmen_id)
        weg = [x for a in alle_absaetze([r]) for x in a.inhalte]
        self._bloecke_entfernen(bloecke, i, 1)
        self._verwaiste_entfernen(weg)
        self._auswahl_retten(self.dokument.anfang())

    @schritt("Rahmenformat", "tabelle")
    def rahmenformat_anwenden(self, rahmen_id: int, aenderung: dict, ersetzen: bool = False) -> None:
        r = self._rahmen(rahmen_id)
        self._attr(r, "format", verschmelze({} if ersetzen else r.format, pruefe("rahmen", aenderung, leer_erlaubt=True)))
        self._beruehrt(r.id)
