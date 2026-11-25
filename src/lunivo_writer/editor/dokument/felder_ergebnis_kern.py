"""Qt-freie Auswertung von Feldanweisungen.
Die benötigten Feldhelfer werden vom Adapter übergeben.
"""

def feld_ergebnis(anweisung: str, kontext: dict, *, _FELD_ERGEBNIS, _ohne_schalter, _schalter, formel, zahl_formatieren) -> str:
    """Das Feldergebnis jetzt. ``kontext`` aus ``kontext_sammeln`` (alle Angaben freiwillig)."""
    roh = anweisung.strip()
    if not roh:
        return ''
    if roh.startswith('='):
        try:
            return zahl_formatieren(formel(roh[1:], kontext), _schalter(roh, '#'))
        except ValueError:
            return '!Syntaxfehler'
    teile = _ohne_schalter(roh).split(None, 1)
    wort, rest = (teile[0].upper(), (teile[1] if len(teile) > 1 else '').strip().strip('"'))
    art = _schalter(roh, '*')
    art = art if art and art.upper() != 'MERGEFORMAT' else None
    fn = _FELD_ERGEBNIS.get(wort)
    return fn(wort, roh, rest, art, kontext) if fn else ''
