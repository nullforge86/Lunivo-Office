"""Satzbau: aus ``core.korrektur.rechtschreibung.pruefung`` herausgelöst."""
from core.korrektur.korrektur import ProofingIssue
import re
from core.korrektur.rechtschreibung.pruefung_hilfen import FORM_ZU_ZEITWORT, _REGELN, mach_fund, uebernimm_schreibweise


SPALTE = _REGELN['SPALTE']


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
