"""Zusammenschreibung: aus ``core.korrektur.rechtschreibung.pruefung`` herausgelöst."""
import re
from core.korrektur.rechtschreibung.pruefung_hilfen import GROSS_ANFANG, TRENN_KURZ, WORT_MUSTER, lade_woerter, mach_fund


def trenne_zusammen(wort):
    woerter = lade_woerter()
    if not woerter:
        return None
    w = wort.lower()
    if len(w) < 6 or w in woerter:
        return None
    # Ab dem ZWEITEN Zeichen — sonst bleiben „ambesten“, „esgibt“, „zuviel“
    # liegen. Zwei-Zeichen-Teile nur aus TRENN_KURZ, die große Liste wäre
    # hier zu großzügig.
    for i in range(2, len(w) - 1):
        vorn, hinten = w[:i], w[i:]
        if vorn not in woerter or hinten not in woerter:
            continue
        if len(vorn) < 3 and vorn not in TRENN_KURZ:
            continue
        if len(hinten) < 3 and hinten not in TRENN_KURZ:
            continue
        if vorn not in TRENN_KURZ and hinten not in TRENN_KURZ:
            continue
        return vorn + ' ' + hinten
    return None


def pruefe_zusammengeschrieben(text, funde):
    for m in WORT_MUSTER.finditer(text):
        wort = m.group(0)
        getrennt = trenne_zusammen(wort)
        if not getrennt:
            continue
        davor = text[:m.start()]
        satz_anfang = davor.strip() == '' or bool(re.search(r'[.!?]\s+$', davor))
        gross = bool(GROSS_ANFANG.match(wort)) or satz_anfang
        neu = (getrennt[0].upper() + getrennt[1:]) if gross else getrennt
        funde.append(mach_fund(m.start(), m.start() + len(wort), wort, neu,
                               'Zwei Wörter ohne Lücke', 'wort'))


_VERWECHSLUNG = (('b', 'd'), ('p', 'q'))


def verwechslungen(wort):
    """Wörter, bei denen genau ein Buchstabe gegen sein Spiegelbild getauscht ist (b/d, p/q). Eigene Hilfe, die
    Kölner Phonetik kennt diese Paare nicht (sie klingen verschieden, sehen aber gleich aus)."""
    w = wort.lower()
    aus = set()
    for i, c in enumerate(w):
        for a, b in _VERWECHSLUNG:
            if c == a:
                aus.add(w[:i] + b + w[i + 1:])
            elif c == b:
                aus.add(w[:i] + a + w[i + 1:])
    return aus


def _ist_zusammensetzung(w):
    """Zwei bekannte Wörter (mindestens vier Buchstaben), auch mit Fugen-s: „Wortabstand“."""
    woerter = lade_woerter()
    for i in range(4, len(w) - 3):
        hinten = w[i:]
        if w[:i] in woerter and hinten in woerter:
            return True
        if w[i - 1] == 's' and i > 4 and w[:i - 1] in woerter and hinten in woerter:
            return True
    return False
