"""Ersetzen ganzer Absatzfolgen und der Zusatzdaten als je ein Schritt (Übernahme von Ergebnissen, die außerhalb der Sitzung entstehen: Lesen einer
Datei, Ersetzen durch ein Programm, Assistent). ``dokument_ersetzen`` steht in ``bearbeitungssitzung.py``. Ohne Qt."""
from __future__ import annotations

import dataclasses

from core.dokument.dokument import Absatz, InlineObjekt, ListenDefinition, Position
from core.bearbeitung.verlauf import BearbeitungsFehler, schritt


class ErsatzTeil:
    @schritt("Eingabe", "text")
    def absatzfolge_ersetzen(self, erste_id: int, anzahl: int, neue: list, listen: dict | None = None, ressourcen: dict | None = None,
                             tippen: bool = False, anhaengen: bool = False, objekte: list | None = None) -> dict:
        """Ersetzt ``anzahl`` aufeinanderfolgende Absätze ab ``erste_id`` (im selben Textfluss) durch ``neue``.

        Neue Absätze mit Id 0 bekommen die Ids der ersetzten (der Reihe nach), darüber hinaus frische; ebenso Objekte im Text.
        ``listen`` (Zwischen-Id < 0 → ListenDefinition) und ``ressourcen`` (Name → Bytes) sind das, was die neuen Absätze neu mitbringen.
        ``tippen``: kurze Eingaben werden im Rückgängig-Verlauf zusammengefasst; ``objekte``: ``[(Index in neue, FreiesObjekt)]`` — die frei positionierten Objekte der neuen Absätze;
        sie ersetzen alle bisher an diesen Absätzen verankerten (``None``: nur die an weggefallenen Absätzen fallen weg). ``anhaengen``: die Änderung (reine
        Automatik wie Umbruchmarken) gehört zum vorigen Schritt und hat kein eigenes Rückgängig. Gibt die Zuordnung Zwischen-Id → Listen-Id zurück."""
        f = self.dokument.finde(erste_id)
        if f is None or not isinstance(f[3], Absatz):
            raise BearbeitungsFehler(f"Kein Absatz mit der Id {erste_id}")
        _bes, bloecke, i, _b = f
        alt = bloecke[i:i + anzahl]
        if len(alt) != anzahl or anzahl < 1 or any(not isinstance(b, Absatz) for b in alt):
            raise BearbeitungsFehler("Die zu ersetzenden Absätze liegen nicht nebeneinander im selben Textfluss")
        if not neue or any(not isinstance(n, Absatz) for n in neue):
            raise BearbeitungsFehler("Es müssen Absätze eingesetzt werden")
        self._offen.tippen = bool(tippen) and self._tiefe == 1
        self._offen.anhaengen = bool(anhaengen) and self._tiefe == 1
        zuordnung: dict = {}
        for zwischen, definition in (listen or {}).items():
            lid = self._id()
            zuordnung[zwischen] = lid
            self._dict(self.dokument.listen, lid, ListenDefinition(lid, definition.ebenen, definition.name))
        for name, daten in (ressourcen or {}).items():
            if self.dokument.ressourcen.get(name) != daten:
                self._dict(self.dokument.ressourcen, name, daten)
        for k, n in enumerate(neue):
            n.id = n.id or (alt[k].id if k < len(alt) else self._id())
            if n.liste_id is not None and n.liste_id < 0:
                n.liste_id = zuordnung[n.liste_id]
            n.inhalte = [dataclasses.replace(x, id=self._id()) if isinstance(x, InlineObjekt) and not x.id else x for x in n.inhalte]
        entfallen = {a.id for a in alt} - {n.id for n in neue}
        for oid, o in list(self.dokument.objekte.items()):
            if o.anker in entfallen:
                self._dict(self.dokument.objekte, oid)
        if objekte is not None:
            betroffen = {a.id for a in alt} | {n.id for n in neue}
            for oid, o in list(self.dokument.objekte.items()):
                if o.anker in betroffen:
                    self._dict(self.dokument.objekte, oid)
            for index, o in objekte:
                neu_objekt = dataclasses.replace(o, id=self._id(), anker=neue[index].id)
                self._dict(self.dokument.objekte, neu_objekt.id, neu_objekt)
        alte_inhalte = [x for a in alt for x in a.inhalte]
        self._liste(bloecke, i, anzahl, neue)
        self._beruehrt(*(a.id for a in alt), *(n.id for n in neue))
        self._verwaiste_entfernen(alte_inhalte)
        self._auswahl_retten(Position(neue[0].id, 0))
        return zuordnung

    @schritt("Zusatzdaten", "zusatz")
    def zusatzdaten_ersetzen(self, kommentare: dict, noten: dict, quellen: list, eigenschaften: dict, anhaengen: bool = False) -> None:
        """Setzt Kommentare, Noten, Quellen und Dokumenteigenschaften (so wie sie die Oberfläche in ihrem Meta-Wörterbuch führt).
        ``anhaengen``: gehört zum vorigen Schritt, kein eigenes Rückgängig."""
        self._offen.anhaengen = bool(anhaengen) and self._tiefe == 1
        d = self.dokument
        for name, neu in (("kommentare", kommentare), ("noten", noten), ("quellen", quellen), ("eigenschaften", eigenschaften)):
            if getattr(d, name) != neu:
                self._attr(d, name, neu)
