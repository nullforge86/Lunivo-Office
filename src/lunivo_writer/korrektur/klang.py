"""Vorschläge für ein einzelnes Wort (Rechtsklick-Menü): Klangvergleich über die Kölner Phonetik und Rangfolge.

Das Wörterbuch und die Nachbarwörter liefert pruefung.py; es wird erst beim Aufruf geholt (keine Kreisimporte).
"""
from lunivo_writer.korrektur.haeufig import HAEUFIG
from lunivo_writer.korrektur.phonetik import abstand, de_schluessel, gleicher_anfang, ist_teilfolge, koelner_phonetik

_KLANGTAFEL = None


def _pruefung():
    from lunivo_writer.korrektur import pruefung
    return pruefung


def _klangtafel():
    global _KLANGTAFEL
    if _KLANGTAFEL is None:
        _KLANGTAFEL = {}
        for wort in _pruefung().lade_woerter():
            if len(wort) < 4:
                continue
            k = koelner_phonetik(wort)
            if k:
                _KLANGTAFEL.setdefault(k, []).append(wort)
    return _KLANGTAFEL


def _gewicht(w, k):
    return abstand(w, k) - (2 if k in HAEUFIG else 0)


def klingt_wie(wort, hoechstens=15):
    w = str(wort).lower()
    if len(w) < 4 or not _pruefung().lade_woerter():
        return []
    klang = koelner_phonetik(w)
    if not klang:
        return []
    gleiche = [k for k in _klangtafel().get(klang, []) if k != w]
    if len(gleiche) <= 1:
        return gleiche
    return sorted(gleiche, key=lambda k: (_gewicht(w, k), abs(len(k) - len(w)), de_schluessel(k)))[:hoechstens]


def _rang(w, k, eigen, klang_gleich):
    if k == eigen:
        return -1
    if k in klang_gleich and k in HAEUFIG:
        return 0
    if ist_teilfolge(w, k):
        return 0
    if ist_teilfolge(k, w):
        return 1
    return 1 if k in klang_gleich else 2


def _treffer_sammeln(w, woerter, gelernt):
    """Nachbarwörter, dann Klanggleiche, ein selbst Gelerntes zuvorderst. Liefert (Treffer, eigen)."""
    treffer = [k for k in _pruefung().nachbar_woerter(w) if k in woerter]
    for k in klingt_wie(w):
        if k not in treffer:
            treffer.append(k)
    eigen = ((gelernt or {}).get('woerter') or {}).get(w)
    if eigen and eigen not in treffer:
        treffer.insert(0, eigen)
    return treffer, eigen


def vorschlaege_fuer(wort, hoechstens=6, gelernt=None):
    woerter = _pruefung().lade_woerter()
    if not woerter:
        return []
    w = str(wort).lower()
    if len(w) < 2 or len(w) > 24 or w in woerter:
        return []
    treffer, eigen = _treffer_sammeln(w, woerter, gelernt)
    klang_gleich = set(klingt_wie(w))
    klang_nah = min((abstand(w, k) for k in klang_gleich), default=0) + 1

    def klang_vorn(k):
        # Wer so schreibt, wie er hört, meint meist das gleich klingende Wort — vor dem, das nur einen Buchstaben abweicht.
        return 0 if k in klang_gleich and abstand(w, k) <= klang_nah else 1

    treffer.sort(key=lambda k: (_rang(w, k, eigen, klang_gleich), klang_vorn(k), _gewicht(w, k),
                                -gleicher_anfang(k, w), len(k), de_schluessel(k)))
    return list(dict.fromkeys(treffer))[:hoechstens]
