# -*- coding: utf-8 -*-
import re
from core.korrektur.sprache.phonetik import de_schluessel as _de_schluessel, gleicher_anfang, ist_teilfolge
from core.korrektur.grammatik.satzbau import pruefe_kongruenz, pruefe_satzbau, pruefe_satzende
from core.korrektur.grammatik.zusammenschreibung import pruefe_zusammengeschrieben, trenne_zusammen
from core.korrektur.rechtschreibung.pruefung_hilfen import FORM_ZU_ZEITWORT, GROSS_ANFANG, SCHALTER_STANDARD, TRENN_KURZ, WOERTERBUCH, WORT_MUSTER, _REGELN, ist_adresse, lade_woerter, mach_fund, uebergehen, uebernimm_schreibweise, wort_abstand
from core.korrektur.sprache.klangpruefung import _klang_fund_wort, pruefe_klang


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


def ist_abkuerzung(text, punkt):
    return bool(ABKUERZUNG.search(text[max(0, punkt - 9):punkt + 1]))


def gross_dahinter(m, text):
    return bool(re.match(r'^[ \t]+[A-ZÄÖÜ]', text[m.end():]))


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


ZEITWOERTER = _REGELN['ZEITWOERTER']


for _zeile in ZEITWOERTER:
    for _form in _zeile.values():
        FORM_ZU_ZEITWORT[_form] = _zeile


ABC = 'abcdefghijklmnopqrstuvwxyzäöüß'


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


def ist_korrektur(falsch, richtig):
    """Sieht die Verbesserung dem Wort überhaupt ähnlich? Ein Rechtschreib-
    prüfer, der ein Wort nicht kennt, rät — und dann kommt für
    „Zahnriemenspanner-Kettenrolle“ eben „Unannehmlichkeiten“ heraus."""
    a, b = str(falsch).lower(), str(richtig).lower()
    if not a or not b or a == b:
        return False
    erlaubt = max(2, min(len(a), len(b)) // 3)
    return wort_abstand(a, b) <= erlaubt


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
