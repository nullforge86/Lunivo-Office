# -*- coding: utf-8 -*-
"""
Die Prüfung ohne Internet: Regeln, Listen und Begründungen für Rechtschreibung, Grammatik und Zeichensetzung.

Übernommen aus dem Projekt „schreibhilfe“ (MIT, Kay Siebke).

Den Wortschatz trägt diese Datei nicht selbst: Er steht einmal in lunivo_writer/ressourcen/daten/regeln.json.
Was hier bleibt, sind die Regeln selbst; die tragen Baustücke als Code und lassen sich nicht als Daten hinschreiben.
"""

import json
import os
from lunivo_writer.modelle.korrektur import ProofingIssue
from lunivo_writer.kern import pfade
import re
from lunivo_writer.korrektur.phonetik import (  # noqa: F401
    DE_ERSATZ as _DE_ERSATZ, abstand, de_schluessel as _de_schluessel, gleicher_anfang, ist_teilfolge, koelner_phonetik)
from lunivo_writer.korrektur.haeufig import HAEUFIG



def daten_ordner():
    """Wo regeln.json und woerter.txt liegen.

    Reihenfolge: Umgebungsvariable LUNIVO_DATEN, dann lunivo_writer/ressourcen/daten.
    """
    kandidaten = [os.environ.get('LUNIVO_DATEN', ''),
                  os.path.join(pfade.RESSOURCEN, 'daten')]
    return [k for k in kandidaten if k]


def _lies_regeln():
    """Holt den gemeinsamen Wortschatz aus regeln.json.

    Fehlt die Datei, bricht das Laden ab — LAUT. Ein stilles Ausweichen auf leere Listen ließe die Prüfung
    scheinbar laufen und einfach nichts mehr finden.
    """
    kandidaten = [os.path.join(d, 'regeln.json') for d in daten_ordner()]
    for k in kandidaten:
        if not os.path.exists(k):
            continue
        with open(k, 'r', encoding='utf-8') as datei:
            return json.load(datei)
    raise IOError('Der gemeinsame Wortschatz fehlt. Gesucht wurde in:\n  %s'
                  % '\n  '.join(kandidaten))


_REGELN = _lies_regeln()

# --------------------------------------------------------------------------
# a) Wörter, die ein Rechtschreibprüfer NICHT finden kann
#    — weil beide Schreibweisen für sich genommen richtig sind.
#
# Die Wörter stehen in lunivo_writer/ressourcen/daten/regeln.json, zusammen mit dem übrigen
# Wortschatz und der Begründung zu jedem Eintrag.
# --------------------------------------------------------------------------

WOERTERBUCH = _REGELN['WOERTERBUCH']

WORT_MUSTER = re.compile(r'[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*')
GROSS_ANFANG = re.compile(r'^[A-ZÄÖÜ]')


def uebernimm_schreibweise(original, verbesserung):
    if GROSS_ANFANG.match(verbesserung):
        return verbesserung                                   # Hauptwort
    if original == original.upper() and len(original) > 1:
        return verbesserung.upper()
    if GROSS_ANFANG.match(original):
        return verbesserung[0].upper() + verbesserung[1:]
    return verbesserung


def mach_fund(von, bis, alt, neu, grund, art, wort_ebene=False) -> ProofingIssue:
    return ProofingIssue(von=von, bis=bis, alt=alt, neu=neu, grund=grund, art=art, wort_ebene=wort_ebene)


# --------------------------------------------------------------------------
# b) Wortgruppen für die Regeln
# --------------------------------------------------------------------------

_kette = lambda name: '|'.join(_REGELN[name])

FUERWOERTER = _kette('FUERWOERTER')
DENK_ZEITWOERTER = _kette('DENK_ZEITWOERTER')
DENK_ZEITWOERTER_ENG = _kette('DENK_ZEITWOERTER_ENG')
DASS_EIGENSCHAFTEN = _kette('DASS_EIGENSCHAFTEN')
ZEITANGABEN = _kette('ZEITANGABEN')
STEIGERUNGEN = _kette('STEIGERUNGEN')
FOLGT_NEBENSATZ = FUERWOERTER + '|' + _kette('FOLGT_NEBENSATZ_ZUSAETZLICH')

NEBENSATZ_WOERTER = [tuple(e) for e in _REGELN['NEBENSATZ_WOERTER']]
KEIN_KOMMA_DAVOR = set(_REGELN['KEIN_KOMMA_DAVOR'])
KEIN_HAUPTWORT = set(_REGELN['KEIN_HAUPTWORT'])

ABKUERZUNG = re.compile(
    r'(?:^|[\s(„"])(?:[A-Za-zÄÖÜäöüß]|ca|bzw|usw|evtl|ggf|inkl|exkl|vgl|bspw|'
    r'Nr|Dr|Prof|Abs|Mio|Mrd|Tel|Str)\.$')
# Gefragt wird das WORT an dieser Stelle, nicht die Nachbarschaft.
ADR_A = re.compile(r'[@]|https?:|^www\.', re.I)
ADR_B = re.compile(r'[A-Za-zÄÖÜäöü0-9_-]/[A-Za-zÄÖÜäöü0-9_-]')
ADR_C = re.compile(r'\.(de|com|org|net|eu|git|io|dev)\b', re.I)


def ist_abkuerzung(text, punkt):
    return bool(ABKUERZUNG.search(text[max(0, punkt - 9):punkt + 1]))


def wort_um(text, stelle):
    a = b = stelle
    while a > 0 and not text[a - 1].isspace():
        a -= 1
    while b < len(text) and not text[b].isspace():
        b += 1
    return text[a:b]


def ist_adresse(text, stelle):
    wort = wort_um(text, stelle)
    return bool(ADR_A.search(wort) or ADR_B.search(wort) or ADR_C.search(wort))


def gross_dahinter(m, text):
    return bool(re.match(r'^[ \t]+[A-ZÄÖÜ]', text[m.end():]))


# --------------------------------------------------------------------------
# c) Der Regelmotor
#
#    Eine Regel: Muster, Bauplan für den Ersatz, Begründung. Dazu drei
#    Schalter — pruefe (verwirft einen Treffer nachträglich), gruppe (grenzt
#    den Fund auf eine Klammer ein), art.
# --------------------------------------------------------------------------

def regel(muster, bau, grund, art='fehler', gruppe=None, pruefe=None, flags=0):
    return {'muster': re.compile(muster, flags), 'bau': bau, 'grund': grund,
            'art': art, 'gruppe': gruppe, 'pruefe': pruefe}


def wende_regeln_an(text, regeln, funde):
    for r in regeln:
        for m in r['muster'].finditer(text):
            if r['pruefe'] and not r['pruefe'](m, text):
                continue
            gruppe = r['gruppe']
            # „gruppe“ heißt: Das Muster darf die Umgebung mitlesen, gemeint ist
            # nur diese Klammer. Der Versatz ist die Länge alles Vorherigen.
            versatz = sum(len(m.group(i) or '') for i in range(1, gruppe)) if gruppe else 0
            alt = m.group(gruppe) if gruppe else m.group(0)
            neu = r['bau'](m)
            if neu == alt:
                continue
            von = m.start() + versatz
            funde.append(mach_fund(von, von + len(alt), alt, neu, r['grund'], r['art']))


ZEICHEN_REGELN = [
    regel(r' {2,}', lambda m: ' ', 'Mehrere Leerzeichen hintereinander'),
    regel(r'[ \t]+([,.;:!?])', lambda m: m.group(1),
          'Vor dem Satzzeichen gehört kein Leerzeichen'),
    regel(r'([,;:])([A-Za-zÄÖÜäöüß])', lambda m: m.group(1) + ' ' + m.group(2),
          'Nach dem Satzzeichen fehlt ein Leerzeichen'),
    regel(r'([A-Za-zÄÖÜäöüß]{2}[.!?])([A-Za-zÄÖÜäöüß])',
          lambda m: m.group(1) + ' ' + m.group(2),
          'Nach dem Satzzeichen fehlt ein Leerzeichen',
          pruefe=lambda m, t: not ist_adresse(t, m.start())
                              and not ist_abkuerzung(t, m.start() + 2)),
    regel(r',{2,}', lambda m: ',', 'Das Komma steht doppelt da'),
    regel(r'([;:!?])\1+', lambda m: m.group(1), 'Das Satzzeichen steht doppelt da'),
    regel(r'\b([A-Za-zÄÖÜäöüß]+)([ \t]+)\1\b', lambda m: m.group(1),
          'Das Wort steht doppelt da', flags=re.I),
    regel(r'\b([A-ZÄÖÜ][A-Za-zÄÖÜäöüß]{1,})[\'’´`]s\b', lambda m: m.group(1) + 's',
          'Vor dem Genitiv-s steht im Deutschen kein Apostroph.', art='tipp'),
]

GROSS_REGELN = [
    regel(r'(^[ \t]*)([a-zäöüß])', lambda m: m.group(2).upper(),
          'Satzanfang großschreiben', gruppe=2),
    regel(r'([.!?]+["»›)]?\s+)([a-zäöüß])', lambda m: m.group(2).upper(),
          'Satzanfang großschreiben', gruppe=2,
          pruefe=lambda m, t: not re.match(r'^\.{2,}', m.group(1))
                              and not ist_abkuerzung(t, m.start())
                              and not ist_adresse(t, m.start() + len(m.group(1)))),
    regel(r'\b(beim|zum|vom|ans|aufs)([ \t]+)([a-zäöüß]{3,}en)\b',
          lambda m: m.group(3)[0].upper() + m.group(3)[1:],
          'Nach „beim/zum/vom“ wird aus dem Tunwort ein Hauptwort.',
          art='tipp', gruppe=3, flags=re.I,
          pruefe=lambda m, t: m.group(3).lower() not in KEIN_HAUPTWORT
                              and not re.search(r'sten$', m.group(3), re.I)
                              and not gross_dahinter(m, t)),
]

GRAMMATIK_REGELN = [
    regel(r'\b(' + DENK_ZEITWOERTER + r')(,?)([ \t]+)das\b'
          r'(?=[ \t]+(?:' + FUERWOERTER + r')\b)',
          lambda m: m.group(1) + ',' + m.group(3) + 'dass',
          'Hier leitet „dass“ den Nebensatz ein – mit Komma davor.',
          art='tipp', flags=re.I),
    regel(r'\b(' + DENK_ZEITWOERTER_ENG + r')(,?)([ \t]+)das\b'
          r'(?=[ \t]+(?:' + FOLGT_NEBENSATZ + r')\b)',
          lambda m: m.group(1) + ',' + m.group(3) + 'dass',
          'Hier leitet „dass“ den Nebensatz ein – mit Komma davor.',
          art='tipp', flags=re.I),
    regel(r'\b(' + DASS_EIGENSCHAFTEN + r')(,?)([ \t]+)das\b'
          r'(?=[ \t]+(?:' + FOLGT_NEBENSATZ + r')\b)',
          lambda m: m.group(1) + ',' + m.group(3) + 'dass',
          'Hier leitet „dass“ den Nebensatz ein – mit Komma davor.',
          art='tipp', flags=re.I),
    regel(r'\bseid([ \t]+)(?=(?:' + ZEITANGABEN + r')\b)',
          lambda m: 'seit' + m.group(1),
          'Bei Zeitangaben heißt es „seit“ – „seid“ nur bei „ihr seid“.',
          flags=re.I),
    regel(r'\bseit([ \t]+)ihr\b', lambda m: 'seid' + m.group(1) + 'ihr',
          '„ihr seid“ – hier gehört ein d ans Ende.', flags=re.I,
          pruefe=lambda m, t: not gross_dahinter(m, t)),
    regel(r'\bihr([ \t]+)seit\b(?![ \t]+(?:' + ZEITANGABEN + r')\b)',
          lambda m: 'ihr' + m.group(1) + 'seid',
          '„ihr seid“ – hier gehört ein d ans Ende.', flags=re.I),
    regel(r'\bseit([ \t]+)(ruhig|still|nett|lieb|vorsichtig|ehrlich|froh|'
          r'gegrüßt|willkommen|gespannt|unbesorgt|bereit)\b',
          lambda m: 'seid' + m.group(1) + m.group(2),
          'Aufforderung an mehrere: „seid ruhig“ mit d.', flags=re.I),
    regel(r'\b(' + STEIGERUNGEN + r')([ \t]+)wie\b',
          lambda m: m.group(1) + m.group(2) + 'als',
          'Nach der Steigerung heißt es „als“: größer als, lieber als.',
          flags=re.I),
    regel(r'\bals([ \t]+)wie\b', lambda m: 'als',
          '„als wie“ ist doppelt gemoppelt – „als“ reicht.', flags=re.I),
]

KOMMA_REGELN = [
    regel(r'\b([A-Za-zÄÖÜäöüß]{2,})([ \t]+)(' + wort + r')\b'
          + (r'(?=[ \t]+(?:' + FUERWOERTER + r')\b)' if nur_vor_fuerwort else ''),
          lambda m: m.group(1) + ',' + m.group(2) + m.group(3),
          'Vor „' + wort + '“ beginnt ein Nebensatz – da gehört ein Komma hin.',
          art='tipp', flags=re.I,
          pruefe=lambda m, t: m.group(1).lower() not in KEIN_KOMMA_DAVOR)
    for wort, nur_vor_fuerwort in NEBENSATZ_WOERTER
] + [
    regel(r'\b([A-Za-zÄÖÜäöüß]{2,})([ \t]+)(aber|sondern|denn)\b'
          r'(?=[ \t]+(?:' + FUERWOERTER + r')\b)',
          lambda m: m.group(1) + ',' + m.group(2) + m.group(3),
          'Hier stoßen zwei Sätze aneinander – davor gehört ein Komma.',
          art='tipp', flags=re.I,
          pruefe=lambda m, t: m.group(1).lower() not in KEIN_KOMMA_DAVOR),
]


# --------------------------------------------------------------------------
# d) Zeitwort und Fürwort müssen zueinander passen
# --------------------------------------------------------------------------

ZEITWOERTER = _REGELN['ZEITWOERTER']
SPALTE = _REGELN['SPALTE']
FORM_ZU_ZEITWORT = {}
for _zeile in ZEITWOERTER:
    for _form in _zeile.values():
        FORM_ZU_ZEITWORT[_form] = _zeile

KONGRUENZ_MUSTER = [
    (re.compile(r'\b(ich|du|er|man|wir)([ \t]+)([a-zäöüß]+)\b', re.I), 1, 3),
    (re.compile(r'\b([a-zäöüß]+)([ \t]+)(ich|du|er|man|wir)\b', re.I), 3, 1),
]


def pruefe_kongruenz(text, funde):
    for muster, nr_fuerwort, nr_form in KONGRUENZ_MUSTER:
        for m in muster.finditer(text):
            fuerwort = m.group(nr_fuerwort)
            form = m.group(nr_form)
            zeile = FORM_ZU_ZEITWORT.get(form.lower())
            if not zeile:
                continue
            richtig = zeile.get(SPALTE.get(fuerwort.lower(), ''))
            if not richtig or richtig == form.lower():
                continue
            alt = m.group(0)
            if nr_form == 1:
                neu = uebernimm_schreibweise(form, richtig) + m.group(2) + fuerwort
            else:
                neu = fuerwort + m.group(2) + uebernimm_schreibweise(form, richtig)
            funde.append(mach_fund(
                m.start(), m.start() + len(alt), alt, neu,
                'So passt das Zeitwort zum Fürwort: „%s %s“.'
                % (fuerwort.lower(), richtig), 'fehler'))


# --------------------------------------------------------------------------
# e) Die große Wörterliste — für Trennen und Tippfehler
# --------------------------------------------------------------------------

TRENN_KURZ = set(_REGELN['TRENN_KURZ'])

ABC = 'abcdefghijklmnopqrstuvwxyzäöüß'

_WOERTER = None


def lade_woerter(pfad=None):
    """Liest die deutsche Wörterliste. Sie liegt neben dieser Datei; fehlt sie,
    wird die des Systems genommen. Ohne Liste arbeiten Trennen und
    Tippfehler-Vorschläge einfach nicht — der Rest läuft weiter."""
    global _WOERTER
    if _WOERTER is not None:
        return _WOERTER
    kandidaten = [pfad] if pfad else []
    kandidaten += [os.path.join(d, 'woerter.txt') for d in daten_ordner()]
    kandidaten += ['/usr/share/dict/ngerman', '/usr/share/dict/german']
    for k in kandidaten:
        if not k or not os.path.exists(k):
            continue
        try:
            with open(k, 'r', encoding='utf-8', errors='ignore') as datei:
                _WOERTER = {z.strip().lower() for z in datei if z.strip()}
            return _WOERTER
        except OSError:
            continue
    _WOERTER = set()
    return _WOERTER


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


# --------------------------------------------------------------------------
# Klang-Prüfer: schreiben, wie man hört (Legasthenie)
# --------------------------------------------------------------------------
HAUPTWORT_ENDUNGEN = ('ität', 'ung', 'heit', 'keit', 'schaft', 'tion', 'ismus', 'nis', 'tum')
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


def nachbar_woerter(w):
    """Alle Wörter, die genau einen Handgriff entfernt sind."""
    aus = set()
    for i in range(len(w) + 1):
        if i < len(w):
            aus.add(w[:i] + w[i + 1:])                          # Buchstabe weg
            for c in ABC:
                aus.add(w[:i] + c + w[i + 1:])                  # ersetzt
            if i < len(w) - 1:
                aus.add(w[:i] + w[i + 1] + w[i] + w[i + 2:])    # vertauscht
        for c in ABC:
            aus.add(w[:i] + c + w[i:])                          # eingefügt
    return aus


def _tippfehler_treffer(w, woerter):
    treffer = []
    for k in nachbar_woerter(w):
        if k not in woerter:
            continue
        # Stummel (unter vier Buchstaben für ein längeres Wort) und abgeschnittener Anfang sind keine Tippfehler
        if len(k) < 4 and len(w) >= 4:
            continue
        if k == w[1:]:
            continue
        treffer.append(k)
    return treffer


_TIPP_ZW = [None, {}]                # [Wörterliste, {wort: Vorschlag}] — dasselbe unbekannte Wort kommt in langen Texten oft wieder
_TIPP_ZW_GRENZE = 20000


def tippfehler_vorschlag(wort):
    woerter = lade_woerter()
    if not woerter:
        return None
    w = wort.lower()
    if len(w) < 4 or len(w) > 20 or w in woerter:
        return None
    if _TIPP_ZW[0] is not woerter or len(_TIPP_ZW[1]) > _TIPP_ZW_GRENZE:
        _TIPP_ZW[0], _TIPP_ZW[1] = woerter, {}
    zw = _TIPP_ZW[1]
    if w not in zw:
        zw[w] = _tippfehler_berechnen(w, woerter)
    return zw[w]


def _tippfehler_berechnen(w, woerter):
    treffer = _tippfehler_treffer(w, woerter)
    if not treffer:
        return None

    def rang(k):
        return 0 if ist_teilfolge(w, k) else (1 if ist_teilfolge(k, w) else 2)

    treffer.sort(key=lambda k: (rang(k), -gleicher_anfang(k, w),
                                0 if k in TRENN_KURZ else 1,
                                len(k), _de_schluessel(k)))
    return treffer[0]


def _tippfehler_fund(text, m, gelernt, schalter, klang_an):
    wort = m.group(0)
    # Hat der Klang-Prüfer das Wort schon, bleibt es bei ihm.
    if klang_an and _klang_fund_wort(text, m, gelernt, schalter):
        return None
    # Was eine andere Regel schon anfasst, bleibt hier außen vor.
    if WOERTERBUCH.get(wort.lower()) or trenne_zusammen(wort):
        return None
    # In Adressen und Pfaden steht kein Deutsch — dort nichts vorschlagen.
    if ist_adresse(text, m.start()):
        return None
    vorschlag = tippfehler_vorschlag(wort)
    if not vorschlag:
        return None
    neu = (vorschlag[0].upper() + vorschlag[1:]) if GROSS_ANFANG.match(wort) else vorschlag
    if neu == wort:
        return None
    return mach_fund(m.start(), m.start() + len(wort), wort, neu, 'Tippfehler? Ein Buchstabe daneben', 'tipp')


def pruefe_tippfehler(text, funde, gelernt=None, schalter=None):
    klang_an = pruefer_aktiv("klang", schalter)
    for m in WORT_MUSTER.finditer(text):
        fund = _tippfehler_fund(text, m, gelernt, schalter, klang_an)
        if fund:
            funde.append(fund)


def wort_abstand(a, b):
    """Wie viele Handgriffe liegen zwischen zwei Wörtern? Zwei vertauschte
    Buchstaben zählen als EINER — „shcon“ ist ein Vertipper, kein anderes
    Wort."""
    zeilen = [list(range(len(b) + 1))]
    for i in range(1, len(a) + 1):
        zeile = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            kosten = 0 if a[i - 1] == b[j - 1] else 1
            zeile[j] = min(zeilen[i - 1][j] + 1,
                           zeile[j - 1] + 1,
                           zeilen[i - 1][j - 1] + kosten)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                zeile[j] = min(zeile[j], zeilen[i - 2][j - 2] + 1)
        zeilen.append(zeile)
    return zeilen[len(a)][len(b)]


def ist_korrektur(falsch, richtig):
    """Sieht die Verbesserung dem Wort überhaupt ähnlich? Ein Rechtschreib-
    prüfer, der ein Wort nicht kennt, rät — und dann kommt für
    „Zahnriemenspanner-Kettenrolle“ eben „Unannehmlichkeiten“ heraus."""
    a, b = str(falsch).lower(), str(richtig).lower()
    if not a or not b or a == b:
        return False
    erlaubt = max(2, min(len(a), len(b)) // 3)
    return wort_abstand(a, b) <= erlaubt


# Was gar nicht erst geprüft wird (Optionen ▸ Rechtschreibprüfung; Vorgabe: alle drei an)
SCHALTER_STANDARD = {'rsGrossIgnorieren': True, 'rsZahlenIgnorieren': True, 'rsPfadeIgnorieren': True}


def uebergehen(wort, text, stelle, schalter):
    if schalter.get('rsGrossIgnorieren', True) and len(wort) > 1 and wort == wort.upper() \
            and re.search(r'[A-ZÄÖÜ]', wort):
        return True
    if schalter.get('rsZahlenIgnorieren', True) and re.search(r'\d', wort):
        return True
    if schalter.get('rsPfadeIgnorieren', True) and ist_adresse(text, stelle):
        return True
    return False


def _wort_fund(wort, stelle, eigene):
    """Fund für ein Wort aus der mitgelieferten Liste oder aus selbst Gelerntem, sonst None."""
    aus_liste = WOERTERBUCH.get(wort.lower())
    selbst = None if aus_liste else eigene.get(wort.lower())
    richtig = aus_liste or selbst
    # Selbst Gelerntes muss dem Wort ähnlich sehen, sonst war es nie eine Korrektur.
    if not richtig or (selbst and not ist_korrektur(wort, selbst)):
        return None
    ersatz = uebernimm_schreibweise(wort, richtig)
    if ersatz == wort:
        return None
    # Was aus der mitgelieferten Liste kommt, ist sicher falsch. Was dieser
    # Mensch selbst beigebracht hat, kam aus EINEM Antippen — ein guter
    # Hinweis, keine Gewissheit.
    return mach_fund(stelle, stelle + len(wort), wort, ersatz,
                     'So hast du es schon einmal geändert' if selbst else 'Schreibweise',
                     'tipp' if selbst else 'fehler')


def pruefe_woerter(text, funde, gelernt=None, schalter=None):
    eigene = (gelernt or {}).get('woerter', {})
    schalter = schalter or SCHALTER_STANDARD
    for m in WORT_MUSTER.finditer(text):
        wort = m.group(0)
        if uebergehen(wort, text, m.start(), schalter):
            continue
        fund = _wort_fund(wort, m.start(), eigene)
        if fund:
            funde.append(fund)


def pruefe_satzende(text, funde):
    bis_ende = re.sub(r'\s+$', '', text)
    if not bis_ende or re.search(r'[.!?:…»"\'\)\]]$', bis_ende):
        return
    woerter = bis_ende[bis_ende.rfind('\n') + 1:].strip().split()
    if len(woerter) < 5:
        return
    letztes = woerter[-1]
    if not re.search(r'[A-Za-zÄÖÜäöüß0-9]$', letztes):
        return
    von = len(bis_ende) - len(letztes)
    funde.append(mach_fund(von, len(bis_ende), letztes, letztes + '.',
                           'Am Ende fehlt der Punkt.', 'tipp'))


def mach_hinweis(von, bis, grund, stelle) -> ProofingIssue:
    return ProofingIssue(von=von, bis=bis, alt='', neu='', grund=grund, art='hinweis', stelle=stelle)


def pruefe_satzbau(text, hinweise):
    for m in re.finditer(r'[^.!?\n]+', text):
        roh = m.group(0)
        satz = roh.strip()
        if not satz:
            continue
        anfang = m.start() + roh.index(satz[0])
        anzahl = len(satz.split())
        binder = len(re.findall(r'\b(und|oder|aber|dann|weil)\b', satz, re.I))
        if anzahl > 25:
            hinweise.append(mach_hinweis(
                anfang, anfang + len(satz),
                'Langer Satz: %d Wörter. Zwei kürzere Sätze liest man leichter.' % anzahl,
                satz))
        elif anzahl >= 12 and binder >= 3:
            hinweise.append(mach_hinweis(
                anfang, anfang + len(satz),
                'Der Satz hängt an vielen Bindewörtern. Ein Punkt dazwischen tut ihm gut.',
                satz))

    for auf, zu, name in (('(', ')', 'Klammern'), ('„', '“', 'Anführungszeichen')):
        offen, geschlossen = text.count(auf), text.count(zu)
        if offen != geschlossen:
            hinweise.append(mach_hinweis(
                len(text), len(text),
                '%s: %d-mal geöffnet, %d-mal geschlossen.' % (name, offen, geschlossen), ''))

    if text.count('"') % 2 == 1:
        hinweise.append(mach_hinweis(len(text), len(text),
                                     'Ein Anführungszeichen steht allein da.', ''))


# --------------------------------------------------------------------------
# f) Überschneidungen auflösen und alles zusammenführen
# --------------------------------------------------------------------------

def ohne_ueberschneidung(funde):
    """Zwei Funde an derselben Stelle gehen nicht — die erste Änderung ließe
    die zweite ins Leere laufen. Wort-Funde haben Vorrang: Ein falsch
    geschriebenes Wort wiegt schwerer als ein fehlendes Komma daneben."""
    belegt = []

    def passt(f):
        return all(f.bis <= b.von or f.von >= b.bis for b in belegt)

    def nach_stelle(f):
        return f.stellenschluessel

    for durchgang in ([f for f in funde if f.wort_ebene],
                      [f for f in funde if not f.wort_ebene]):
        for fund in sorted(durchgang, key=nach_stelle):
            if passt(fund):
                belegt.append(fund)
    return sorted(belegt, key=nach_stelle)


# Die einzelnen Prüfer. Jeder hat einen Namen und lässt sich über `schalter["pruefer_<name>"] = False` ausschalten;
# die mit GRAMMATIK_PRUEFER hängen zusätzlich an „Grammatik mitprüfen“ (rsGrammatik).
# Reihenfolge = Reihenfolge der Auswertung (Überschneidungen werden danach in ohne_ueberschneidung aufgelöst).
WORT_PRUEFER = [
    ("woerter", lambda t, k, g, s: pruefe_woerter(t, k, g, s)),
    ("zusammengeschrieben", lambda t, k, g, s: pruefe_zusammengeschrieben(t, k)),
    ("klang", lambda t, k, g, s: pruefe_klang(t, k, g, s)),
    ("tippfehler", lambda t, k, g, s: pruefe_tippfehler(t, k, g, s)),
]
REGEL_PRUEFER = [
    ("zeichen", lambda t, k: wende_regeln_an(t, ZEICHEN_REGELN, k)),
    ("gross", lambda t, k: wende_regeln_an(t, GROSS_REGELN, k)),
    ("grammatik", lambda t, k: wende_regeln_an(t, GRAMMATIK_REGELN, k)),
    ("komma", lambda t, k: wende_regeln_an(t, KOMMA_REGELN, k)),
    ("kongruenz", lambda t, k: pruefe_kongruenz(t, k)),
    ("satzende", lambda t, k: pruefe_satzende(t, k)),
]
HINWEIS_PRUEFER = [("satzbau", lambda t, h: pruefe_satzbau(t, h))]
GRAMMATIK_PRUEFER = {"grammatik", "komma", "kongruenz", "satzbau"}
PRUEFER_NAMEN = [n for n, _ in WORT_PRUEFER] + [n for n, _ in REGEL_PRUEFER] + [n for n, _ in HINWEIS_PRUEFER]


def pruefer_aktiv(name, schalter=None):
    """Ist der Prüfer eingeschaltet? Ohne Angabe sind alle an."""
    if not schalter:
        return True
    if name in GRAMMATIK_PRUEFER and not schalter.get("rsGrammatik", True):
        return False
    return bool(schalter.get("pruefer_" + name, True))


def finde_probleme(text, gelernt=None, schalter=None):
    """Alle Stellen, die auffällig sind — in derselben Reihenfolge wie am Handy."""
    gelernt = gelernt or {'woerter': {}, 'inRuhe': {}}

    korrekturen = []
    for name, lauf in WORT_PRUEFER:
        if pruefer_aktiv(name, schalter):
            lauf(text, korrekturen, gelernt, schalter)
    korrekturen = [fund.ersetzt(wort_ebene=True) for fund in korrekturen]

    # Wörter auf der Ruhe-Liste sind so gewollt.
    in_ruhe = gelernt.get('inRuhe', {})
    eigene = gelernt.get('woerter', {})
    korrekturen = [f for f in korrekturen
                   if not (in_ruhe.get(f.alt.lower())
                           and not eigene.get(f.alt.lower()))]

    for name, lauf in REGEL_PRUEFER:
        if pruefer_aktiv(name, schalter):
            lauf(text, korrekturen)

    hinweise = []
    for name, lauf in HINWEIS_PRUEFER:
        if pruefer_aktiv(name, schalter):
            lauf(text, hinweise)

    # Erst das zum Ändern, danach das zum Nachdenken.
    return ohne_ueberschneidung(korrekturen) + hinweise


# --------------------------------------------------------------------------
# Vorschläge für ein einzelnes Wort (Rechtsklick-Menü): Phonetik in phonetik.py, Rangfolge in klang.py.
# Hier unten eingebunden, weil klang.py das Wörterbuch (lade_woerter, nachbar_woerter) von hier holt.
# --------------------------------------------------------------------------
from lunivo_writer.korrektur.klang import klingt_wie, vorschlaege_fuer  # noqa: E402,F401
