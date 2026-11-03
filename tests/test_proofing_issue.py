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


def test_vertrag_verwirft_ungueltige_funde_und_behaelt_gueltige(caplog):
    from lunivo_writer.models.proofing import bereinigen
    gut = {"von": 0, "bis": 3, "alt": "bim", "neu": "bin", "grund": "x", "art": "fehler", "wortEbene": True}
    schlecht = [{"von": 5, "bis": 5, "alt": "", "neu": None, "grund": "", "art": "fehler"},          # leer
                {"von": 8, "bis": 20, "alt": "x", "grund": "", "art": "fehler"},                       # hinter dem Text
                {"von": -1, "bis": 2, "alt": "x", "art": "fehler"},
                {"von": "1", "bis": 2, "alt": "x", "art": "fehler"},
                {"von": 0, "bis": 2, "alt": "x", "art": "gefährlich"},
                {"von": 0, "bis": 2, "alt": "x", "art": "tipp", "quelle": "fremd"},
                {"von": 0, "bis": 2, "alt": "x", "art": "tipp", "konfidenz": 7},
                {"bis": 2, "alt": "x"}, "kein dict", {"von": 0, "bis": 2, "alt": 5, "art": "tipp"}]
    with caplog.at_level("WARNING", logger="lunivo.schreibhilfe"):
        r = bereinigen([gut] + schlecht, text_laenge=10)
    assert r == [ProofingIssue.von_dict(gut).als_dict()]
    assert "verworfen" in caplog.text and "bim" not in caplog.text           # Zahl und Grund, nie der Text


def test_vertrag_gilt_am_eingang_der_pipeline():
    from lunivo_writer.proofing import fund
    r = fund.markieren([{"von": 0, "bis": 3, "alt": "abc", "neu": "d", "grund": "", "art": "tipp"},
                        {"von": 2, "bis": 99, "alt": "c", "neu": "", "grund": "", "art": "tipp"}], "eigen", 5)
    assert len(r) == 1 and r[0]["quelle"] == "eigen" and r[0]["konfidenz"] is not None
