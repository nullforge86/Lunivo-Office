from lunivo_writer.models.proofing import ProofingIssue
from lunivo_writer.proofing import fund, pruefung

TEXTE = [
    "Das ist ein Satz mit  zwei Leerzeichen und einem Tippfehler wie Fehlr .",
    "ich glaube das er kommt, aber  vieleicht nicht. Der Hund und die Katze ,sind da",
    "Wir haben gestern einen Test gemacht dass alles klappt. Dies ist ein sehr sehr langer Satz",
]


def _funde():
    alle = []
    for t in TEXTE:
        alle += pruefung.finde_probleme(t)
    return alle


def test_dict_hin_und_zurueck_ist_gleich():
    funde = _funde()
    assert funde, "Beispieltexte liefern keine Funde"
    for f in funde:
        assert ProofingIssue.von_dict(f).als_dict() == f


def test_markierte_und_aufgeloeste_funde_bleiben_erhalten():
    markiert = fund.markieren(_funde(), "eigen")
    for f in fund.loesen(markiert):
        assert ProofingIssue.von_dict(f).als_dict() == f


def test_unbekannte_schluessel_bleiben_erhalten_und_laenge():
    f = {"von": 2, "bis": 5, "alt": "abc", "neu": "abd", "grund": "x", "art": "tipp", "wortEbene": False, "regel": "R1"}
    p = ProofingIssue.von_dict(f)
    assert p.laenge == 3 and p.als_dict() == f
