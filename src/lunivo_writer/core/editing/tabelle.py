"""Tabellenstruktur ändern, ohne Qt: Zeilen und Spalten einfügen und löschen. Verbundene Zellen (``row_span``/``column_span``) werden mitgeführt: eine Zelle, die über die Einfügestelle
reicht, wird länger; eine, die über die gelöschte Zeile oder Spalte reicht, kürzer; eine, die in der gelöschten Zeile oder Spalte beginnt und darüber hinausreicht, beginnt in der nächsten.
Alle Funktionen liefern eine neue Tabelle, die übergebene bleibt unverändert."""
from __future__ import annotations

import copy

from lunivo_writer.core.document.model import CharacterFormat, Paragraph, ParagraphFormat, Table, TableCell, TableRow


def _leere_zelle(vorlage: TableCell | None, r: int, c: int) -> TableCell:
    props = copy.deepcopy(vorlage.properties) if vorlage is not None else {}
    return TableCell(r, c, 1, 1, props, [Paragraph(ParagraphFormat(char_format=CharacterFormat(copy.deepcopy(props))), [])])


def _zellen(tab: Table) -> list[TableCell]:
    return [z for zeile in tab.table_rows for z in zeile.cells]


def _aufbauen(tab: Table, zellen: list[TableCell], zeilen: int, spalten: int) -> Table:
    rows = [TableRow([]) for _ in range(zeilen)]
    for z in sorted(zellen, key=lambda z: (z.row, z.column)):
        rows[z.row].cells.append(z)
    return Table(zeilen, spalten, copy.deepcopy(tab.properties), rows)


def _zelle_an(zellen: list[TableCell], r: int, c: int) -> TableCell | None:
    return next((z for z in zellen if z.row <= r < z.row + z.row_span and z.column <= c < z.column + z.column_span), None)


def zeilen_einfuegen(tab: Table, index: int, anzahl: int = 1) -> Table:
    """``anzahl`` Zeilen vor Zeile ``index`` (``index == rows``: am Ende). Die neuen Zellen übernehmen das Format der Zelle in der Zeile darüber, bei ``index == 0`` der darunter."""
    zellen = copy.deepcopy(_zellen(tab))
    bezug_zeile = index - 1 if index > 0 else 0
    neue: list[TableCell] = []
    belegt: set[int] = set()
    for z in zellen:
        if z.row < index < z.row + z.row_span:                       # reicht über die Einfügestelle: wird länger
            z.row_span += anzahl
            belegt.update(range(z.column, z.column + z.column_span))
        elif z.row >= index:
            z.row += anzahl
    for c in range(tab.columns):
        if c in belegt:
            continue
        vorlage = _zelle_an(copy.deepcopy(_zellen(tab)), bezug_zeile, c)
        for k in range(anzahl):
            neue.append(_leere_zelle(vorlage, index + k, c))
    return _aufbauen(tab, zellen + neue, tab.rows + anzahl, tab.columns)


def zeilen_loeschen(tab: Table, index: int, anzahl: int = 1) -> Table:
    """Zeilen ``index`` bis ``index + anzahl - 1`` löschen."""
    ende = index + anzahl
    zellen = copy.deepcopy(_zellen(tab))
    rest: list[TableCell] = []
    for z in zellen:
        z_ende = z.row + z.row_span
        if z_ende <= index:
            rest.append(z)
        elif z.row >= ende:
            z.row -= anzahl
            rest.append(z)
        else:
            ueberlappt = min(z_ende, ende) - max(z.row, index)
            neu_span = z.row_span - ueberlappt
            if neu_span <= 0:
                continue                                              # liegt ganz in den gelöschten Zeilen
            z.row = min(z.row, index)                                  # beginnt vor oder in dem Bereich: ab jetzt an der Stelle des Bereichs
            z.row_span = neu_span
            rest.append(z)
    return _aufbauen(tab, rest, tab.rows - anzahl, tab.columns)


def spalten_einfuegen(tab: Table, index: int, anzahl: int = 1) -> Table:
    zellen = copy.deepcopy(_zellen(tab))
    bezug = index - 1 if index > 0 else 0
    neue: list[TableCell] = []
    belegt: set[int] = set()
    for z in zellen:
        if z.column < index < z.column + z.column_span:
            z.column_span += anzahl
            belegt.update(range(z.row, z.row + z.row_span))
        elif z.column >= index:
            z.column += anzahl
    for r in range(tab.rows):
        if r in belegt:
            continue
        vorlage = _zelle_an(copy.deepcopy(_zellen(tab)), r, bezug)
        for k in range(anzahl):
            neue.append(_leere_zelle(vorlage, r, index + k))
    return _aufbauen(tab, zellen + neue, tab.rows, tab.columns + anzahl)


def spalten_loeschen(tab: Table, index: int, anzahl: int = 1) -> Table:
    ende = index + anzahl
    zellen = copy.deepcopy(_zellen(tab))
    rest: list[TableCell] = []
    for z in zellen:
        z_ende = z.column + z.column_span
        if z_ende <= index:
            rest.append(z)
        elif z.column >= ende:
            z.column -= anzahl
            rest.append(z)
        else:
            ueberlappt = min(z_ende, ende) - max(z.column, index)
            neu_span = z.column_span - ueberlappt
            if neu_span <= 0:
                continue
            z.column = min(z.column, index)
            z.column_span = neu_span
            rest.append(z)
    return _aufbauen(tab, rest, tab.rows, tab.columns - anzahl)


def zellen_verbinden(tab: Table, zeile: int, spalte: int, zeilen: int, spalten: int) -> Table:
    """Die Zellen im Rechteck (``zeile``, ``spalte``, ``zeilen`` × ``spalten``) zu einer Zelle verbinden: sie behält Format und Inhalt der Zelle oben links; die nicht leeren Absätze der übrigen
    Zellen werden angehängt. Zellen, die aus dem Rechteck herausragen, vergrößern es (wie bei Qt)."""
    zellen = copy.deepcopy(_zellen(tab))
    r1, c1 = zeile + zeilen, spalte + spalten
    while True:                                                       # das Rechteck so lange erweitern, bis keine Zelle mehr hinausragt
        for z in zellen:
            schneidet = z.row < r1 and z.row + z.row_span > zeile and z.column < c1 and z.column + z.column_span > spalte
            if schneidet:
                zeile, spalte = min(zeile, z.row), min(spalte, z.column)
                r1, c1 = max(r1, z.row + z.row_span), max(c1, z.column + z.column_span)
        if all(not (z.row < r1 and z.row + z.row_span > zeile and z.column < c1 and z.column + z.column_span > spalte) or
               (z.row >= zeile and z.column >= spalte and z.row + z.row_span <= r1 and z.column + z.column_span <= c1) for z in zellen):
            break
    innen = sorted((z for z in zellen if z.row >= zeile and z.column >= spalte and z.row + z.row_span <= r1 and z.column + z.column_span <= c1), key=lambda z: (z.row, z.column))
    erste = innen[0]
    for z in innen[1:]:
        erste.content += [b for b in z.content if not (isinstance(b, Paragraph) and not b.runs)]
    erste.row, erste.column, erste.row_span, erste.column_span = zeile, spalte, r1 - zeile, c1 - spalte
    rest = [z for z in zellen if z not in innen] + [erste]
    return _aufbauen(tab, rest, tab.rows, tab.columns)


def zelle_teilen(tab: Table, zeile: int, spalte: int, spalten: int, zeilen: int) -> Table | None:
    """Die einfache Zelle (``zeile``, ``spalte``) in ``spalten`` × ``zeilen`` Zellen teilen. Die übrigen Zeilen und Spalten behalten ihr Aussehen: ihre Zellen werden breiter bzw. höher
    (verbunden), statt leere Zellen zu bekommen. ``None``, wenn die Zelle selbst schon verbunden ist (dann teilt die Oberfläche wie bisher)."""
    z = _zelle_an(_zellen(tab), zeile, spalte)
    if z is None or z.row_span != 1 or z.column_span != 1:
        return None
    neu = tab
    if spalten > 1:
        neu = spalten_einfuegen(neu, spalte + 1, spalten - 1)
        neu = _neue_aufnehmen(neu, spalte, spalten - 1, "spalte", zeile)
    if zeilen > 1:
        neu = zeilen_einfuegen(neu, zeile + 1, zeilen - 1)
        neu = _neue_aufnehmen(neu, zeile, zeilen - 1, "zeile", spalte, spalten if spalten > 1 else 1)
    return neu


def _neue_aufnehmen(tab: Table, index: int, anzahl: int, art: str, ausser: int, breite: int = 1) -> Table:
    """Nach dem Einfügen von ``anzahl`` Spalten (Zeilen) hinter ``index``: außerhalb der geteilten Zelle (Zeile ``ausser`` bzw. Spalten ``ausser`` bis ``ausser + breite``) nehmen die Zellen
    davor die neuen leeren Zellen auf (werden entsprechend länger)."""
    zellen = copy.deepcopy(_zellen(tab))
    neue_von, neue_bis = index + 1, index + anzahl
    weg: list[TableCell] = []
    for z in zellen:
        liegt_neu = (neue_von <= z.column <= neue_bis) if art == "spalte" else (neue_von <= z.row <= neue_bis)
        in_geteilt = (z.row == ausser) if art == "spalte" else (ausser <= z.column < ausser + breite)
        if not liegt_neu or in_geteilt or (z.column_span if art == "spalte" else z.row_span) != 1:
            continue
        if art == "spalte":
            vorn = next((a for a in zellen if a.row <= z.row < a.row + a.row_span and a.column + a.column_span == z.column), None)
        else:
            vorn = next((a for a in zellen if a.column <= z.column < a.column + a.column_span and a.row + a.row_span == z.row), None)
        if vorn is not None:
            if art == "spalte":
                vorn.column_span += 1
            else:
                vorn.row_span += 1
            weg.append(z)
    return _aufbauen(tab, [z for z in zellen if z not in weg], tab.rows, tab.columns)
