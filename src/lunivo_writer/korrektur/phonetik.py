"""Lautvergleich für die Rechtschreibprüfung: Kölner Phonetik, Editierabstand, Wortvergleichs-Helfer.

Reine Funktionen ohne Wörterbuch; die Vorschlagslogik steht in klang.py und pruefung.py.
"""
import re

# Deutsche Sortierung: ä zählt wie a, ö wie o, ü wie u, ß wie ss. Pythons eigener Vergleich sortiert nach
# Zahlenwert und stellte alle Umlaute ans Ende.
DE_ERSATZ = {'ä': 'a', 'ö': 'o', 'ü': 'u', 'ß': 'ss'}

# Kölner Phonetik: Buchstabe -> Code, soweit er nicht von Nachbarbuchstaben abhängt (H hat keinen Code).
_KOELN_EINFACH = {
    **dict.fromkeys('AEIOUYJ', '0'), 'B': '1', **dict.fromkeys('FVW', '3'), **dict.fromkeys('GKQ', '4'),
    'L': '5', **dict.fromkeys('MN', '6'), 'R': '7', **dict.fromkeys('SZ', '8'),
}
_KOELN_VORBEREITUNG = (('Ä', 'A'), ('Ö', 'O'), ('Ü', 'U'), ('ß', 'SS'), ('QU', 'KW'), ('PH', 'F'))


def de_schluessel(wort):
    grob = ''.join(DE_ERSATZ.get(c, c) for c in wort)
    return (grob, wort)


def ist_teilfolge(kurz, lang):
    i = 0
    for c in lang:
        if i < len(kurz) and kurz[i] == c:
            i += 1
    return i == len(kurz)


def gleicher_anfang(a, b):
    i = 0
    while i < len(a) and i < len(b) and a[i] == b[i]:
        i += 1
    return i


def abstand(a, b):
    if a == b:
        return 0
    m, n = len(a), len(b)
    if not m:
        return n
    if not n:
        return m
    zeile = list(range(n + 1))
    for i in range(1, m + 1):
        vorherige = zeile[0]
        zeile[0] = i
        for j in range(1, n + 1):
            diagonal = vorherige
            vorherige = zeile[j]
            zeile[j] = min(zeile[j] + 1, zeile[j - 1] + 1, diagonal + (0 if a[i - 1] == b[j - 1] else 1))
    return zeile[n]


def _in(zeichen, menge):
    return bool(zeichen) and zeichen in menge


def _code_c(i, vor, nach):
    if i == 0:
        return '4' if _in(nach, 'AHKLOQRUX') else '8'
    if _in(vor, 'SZ'):
        return '8'
    return '4' if _in(nach, 'AHKOQUX') else '8'


def _koeln_code(c, i, vor, nach):
    """Code eines Buchstabens; abhängig von Vorgänger und Nachfolger bei P, D, T, C, X."""
    if c in _KOELN_EINFACH:
        return _KOELN_EINFACH[c]
    if c == 'P':
        return '3' if nach == 'H' else '1'
    if c in 'DT':
        return '8' if _in(nach, 'CSZ') else '2'
    if c == 'C':
        return _code_c(i, vor, nach)
    if c == 'X':
        return '8' if _in(vor, 'CKQ') else '48'
    return None


def koelner_phonetik(wort):
    w = str(wort).upper()
    for alt, neu in _KOELN_VORBEREITUNG:
        w = w.replace(alt, neu)
    w = re.sub(r'[^A-Z]', '', w)
    if not w:
        return ''
    aus = ''
    for i, c in enumerate(w):
        code = _koeln_code(c, i, w[i - 1] if i > 0 else '', w[i + 1] if i + 1 < len(w) else '')
        for z in code or '':
            if not aus or z != aus[-1]:
                aus += z
    return aus[0] + aus[1:].replace('0', '') if aus else ''
