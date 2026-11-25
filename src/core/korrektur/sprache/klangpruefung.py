"""Klangpruefung: aus ``core.korrektur.rechtschreibung.pruefung`` herausgelöst."""
import re
from core.korrektur.sprache.phonetik import DE_ERSATZ as _DE_ERSATZ, de_schluessel as _de_schluessel
from core.korrektur.woerterbuecher.haeufig import HAEUFIG
from core.korrektur.sprache.klang import klingt_wie
from core.korrektur.grammatik.zusammenschreibung import _ist_zusammensetzung, trenne_zusammen, verwechslungen
from core.korrektur.rechtschreibung.pruefung_hilfen import GROSS_ANFANG, SCHALTER_STANDARD, WOERTERBUCH, WORT_MUSTER, ist_adresse, lade_woerter, mach_fund, uebergehen, uebernimm_schreibweise, wort_abstand


# --------------------------------------------------------------------------
# Klang-Prüfer: schreiben, wie man hört (Legasthenie)
# --------------------------------------------------------------------------
HAUPTWORT_ENDUNGEN = ('ität', 'ung', 'heit', 'keit', 'schaft', 'tion', 'ismus', 'nis', 'tum')


def regel_varianten(wort):
    """Wörter, die eine feste Hörregel ergibt: b/d, p/q, schp→sp, scht→st, verdoppelter oder einfacher Mitlaut.
    Nur Treffer in der Wörterliste; das ist die sicherste Spur."""
    woerter = lade_woerter()
    w = wort.lower()
    v = set(verwechslungen(w))
    for alt, neu in (('schp', 'sp'), ('scht', 'st')):
        i = w.find(alt)
        while i >= 0:
            v.add(w[:i] + neu + w[i + len(alt):])
            i = w.find(alt, i + 1)
    for i, c in enumerate(w):
        if c not in 'aeiouäöüy':
            v.add(w[:i] + c + w[i:])                         # kome → komme
            if i + 1 < len(w) and w[i + 1] == c:
                v.add(w[:i] + w[i + 1:])                     # sonnne → sonne
    v.discard(w)
    return {k for k in v if k in woerter}


def _geruest(w):
    return re.sub(r'[aeiouäöüy]', '', w)


def _klang_kandidaten(w):
    woerter = lade_woerter()
    kandidaten = set(klingt_wie(w))
    kandidaten |= {k for k in verwechslungen(w) if k in woerter}
    return kandidaten


def _regel_vorschlag(w):
    """Feste Hörregeln: ein einziges Wort (Umlaut-Paare zählen als eins) ist die Antwort, sonst None."""
    regeln = {''.join(_DE_ERSATZ.get(c, c) for c in k): k for k in sorted(regel_varianten(w), reverse=True)}
    return next(iter(regeln.values())) if len(regeln) == 1 else None


def _klang_bewertet(w):
    """Kandidaten mit Abstand (höchstens 3) als [(d, k)]; None, wenn w selbst eine Zusammensetzung ist."""
    bewertet = []
    for k in _klang_kandidaten(w):
        if abs(len(k) - len(w)) > 2:
            continue
        # Nur andere Selbstlaute („Lunivo“/„Lenovo“, Beugung) ist kein Hörfehler
        if _geruest(k) == _geruest(w):
            continue
        if _ist_zusammensetzung(w):
            return None
        d = wort_abstand(w, k)
        if d <= 3:
            bewertet.append((d, k))
    return bewertet


def _klang_reihe(bewertet):
    """Nach Umlaut-Paaren zusammengefasst und gewichtet sortiert: [(Gewicht, Wort)]."""
    gruppen = {}
    for d, k in bewertet:
        g = ''.join(_DE_ERSATZ.get(c, c) for c in k)
        alt = gruppen.get(g)
        if alt is None or (d, _de_schluessel(k)) < (alt[0], _de_schluessel(alt[1])):
            gruppen[g] = (d, k)
    # Ein häufiges Wort zählt zwei Handgriffe weniger — „vielleicht“ schlägt „flicht“.
    reihe = sorted(((d - (2 if k in HAEUFIG else 0), k) for d, k in gruppen.values()),
                   key=lambda t: (t[0], _de_schluessel(t[1])))
    # Beugungsformen desselben Wortes (spiel/spiele) stören die Eindeutigkeit nicht.
    k0 = reihe[0][1]
    return [reihe[0]] + [t for t in reihe[1:] if not (t[1].startswith(k0[:-2]) and len(k0) > 4)]


def _klang_eindeutig(reihe):
    if len(reihe) < 2:
        return True
    (d1, k1), (d2, k2) = reihe[0], reihe[1]
    return d2 - d1 >= 2 or (k1 in HAEUFIG and k2 not in HAEUFIG and d2 > d1)


def klang_vorschlag(wort):
    """Das eine Wort, das gemeint sein muss, oder None. Nur kleingeschrieben, ohne Rücksicht auf Satzstellung."""
    woerter = lade_woerter()
    w = wort.lower()
    if not woerter or w in woerter or not 4 <= len(w) <= 20:
        return None
    eindeutig = _regel_vorschlag(w)
    if eindeutig:
        return eindeutig
    if len(w) < 5:
        return None
    bewertet = _klang_bewertet(w)
    if not bewertet:
        return None
    reihe = _klang_reihe(bewertet)
    return reihe[0][1] if _klang_eindeutig(reihe) else None


def _klang_ausgeschlossen(text, m, gelernt, schalter):
    """Wörter, bei denen der Klang-Prüfer nicht rät (Name, Adresse, schon bekannt, zusammengeschrieben ...)."""
    wort = m.group(0)
    if '-' in wort or not 4 <= len(wort) <= 20 or re.search(r'[A-ZÄÖÜ]', wort[1:]):
        return True
    if uebergehen(wort, text, m.start(), schalter or SCHALTER_STANDARD) or ist_adresse(text, m.start()):
        return True
    w = wort.lower()
    gelernt = gelernt or {}
    if WOERTERBUCH.get(w) or w in (gelernt.get('woerter') or {}) or w in (gelernt.get('inRuhe') or {}):
        return True
    return not lade_woerter() or w in lade_woerter()


def _am_satzanfang(text, stelle):
    """Steht davor nur Leerraum oder ein Satzzeichen (. ! ? :) mit Leerraum? Schaut nur rückwärts bis zum ersten Zeichen, das kein Leerraum
    ist — nicht über den ganzen Text davor (das machte die Prüfung langer Dokumente quadratisch langsam)."""
    j = stelle
    while j > 0 and text[j - 1].isspace():
        j -= 1
    return j == 0 or (j < stelle and text[j - 1] in '.!?:')


def _klang_fund_wort(text, m, gelernt, schalter):
    """Die Verbesserung für das Wort, falls der Klang-Prüfer sicher genug ist, sonst None."""
    wort = m.group(0)
    if _klang_ausgeschlossen(text, m, gelernt, schalter):
        return None
    satz_anfang = _am_satzanfang(text, m.start())
    if GROSS_ANFANG.match(wort) and not satz_anfang:
        return None                                   # Name, Fachwort oder Hauptwort: nicht raten
    if trenne_zusammen(wort):
        return None
    vorschlag = klang_vorschlag(wort)
    if not vorschlag:
        return None
    if vorschlag.endswith(HAUPTWORT_ENDUNGEN):
        vorschlag = vorschlag[0].upper() + vorschlag[1:]
    neu = uebernimm_schreibweise(wort, vorschlag)
    if satz_anfang and not GROSS_ANFANG.match(neu):
        neu = neu[0].upper() + neu[1:]
    if neu == wort or neu.lower() == wort.lower():
        return None
    return neu


def pruefe_klang(text, funde, gelernt=None, schalter=None):
    for m in WORT_MUSTER.finditer(text):
        neu = _klang_fund_wort(text, m, gelernt, schalter)
        if not neu:
            continue
        wort = m.group(0)
        funde.append(mach_fund(m.start(), m.start() + len(wort), wort, neu,
                               'Klingt wie „%s“' % neu, 'tipp').ersetzt(konfidenz=0.7))
