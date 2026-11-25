"""Pruefung hilfen: aus ``core.korrektur.rechtschreibung.pruefung`` herausgelöst."""
import json
import os
from core.korrektur.korrektur import ProofingIssue
from system.plattform import ressourcen_pfade as pfade
import re


def daten_ordner():
    """Wo regeln.json und woerter.txt liegen.

    Reihenfolge: Umgebungsvariable LUNIVO_DATEN, dann system/ressourcen/daten.
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


# Gefragt wird das WORT an dieser Stelle, nicht die Nachbarschaft.
ADR_A = re.compile(r'[@]|https?:|^www\.', re.I)


ADR_B = re.compile(r'[A-Za-zÄÖÜäöü0-9_-]/[A-Za-zÄÖÜäöü0-9_-]')


ADR_C = re.compile(r'\.(de|com|org|net|eu|git|io|dev)\b', re.I)


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


FORM_ZU_ZEITWORT = {}


TRENN_KURZ = set(_REGELN['TRENN_KURZ'])


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
