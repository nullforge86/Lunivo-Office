"""Zwischenspeicher je Dokumentstand: Ergebnisse, die nur vom Inhalt des Dokuments abhängen, einmal je Änderung berechnen.

Gebraucht beim Zeichnen: Druck und PDF zeichnen jede Seite einzeln, und was dabei das ganze Dokument durchläuft (Rahmengruppen, Nummern
mehrstufiger Listen, Absätze mit Effekten), liefe sonst für jede Seite erneut durch alle Absätze."""
from __future__ import annotations


def je_stand(doc, name: str, bauen):
    """``bauen(doc)``, gemerkt am Dokument unter ``name``, bis sich das Dokument ändert (Qt vergibt dann eine neue Revision)."""
    rev = doc.revision()
    zw = getattr(doc, name, None)
    if zw is not None and zw[0] == rev:
        return zw[1]
    wert = bauen(doc)
    setattr(doc, name, (rev, wert))
    return wert


def im_blick(p, b) -> bool:
    """Liegt der Absatz ``b`` im Ausschnitt, den der Maler ``p`` gerade zeichnet? Ohne Ausschnitt (ganzes Dokument): immer."""
    sicht = p.clipBoundingRect()
    if sicht.isEmpty():
        return True
    tl = b.layout()
    return tl is not None and sicht.intersects(tl.boundingRect().translated(tl.position()))
