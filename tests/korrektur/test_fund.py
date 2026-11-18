from lunivo_writer.modelle.korrektur import ProofingIssue
from lunivo_writer.korrektur import fund, pruefung

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


def test_pruefer_liefern_issues_und_dict_wandlung_ist_verlustfrei():
    funde = _funde()
    assert funde and all(isinstance(f, ProofingIssue) for f in funde), "Prüfer müssen ProofingIssue liefern"
    for f in funde:
        assert ProofingIssue.von_dict(f.als_dict()) == f


def test_markierte_und_aufgeloeste_funde_bleiben_erhalten():
    markiert = fund.markieren(_funde(), "eigen")
    assert all(isinstance(f, ProofingIssue) and f.quelle == "eigen" and f.konfidenz is not None for f in markiert)
    for f in fund.loesen(markiert):
        assert ProofingIssue.von_dict(f.als_dict()) == f


def test_unbekannte_schluessel_bleiben_erhalten_und_laenge():
    f = {"von": 2, "bis": 5, "alt": "abc", "neu": "abd", "grund": "x", "art": "tipp", "wortEbene": False, "regel": "R1"}
    p = ProofingIssue.von_dict(f)
    assert p.laenge == 3 and p.als_dict() == f


def test_vertrag_verwirft_ungueltige_funde_und_behaelt_gueltige(caplog):
    from lunivo_writer.modelle.korrektur import bereinigen
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
    assert r == [ProofingIssue.von_dict(gut)]
    assert "verworfen" in caplog.text and "bim" not in caplog.text           # Zahl und Grund, nie der Text


def test_vertrag_gilt_am_eingang_der_pipeline():
    from lunivo_writer.korrektur import fund
    r = fund.markieren([{"von": 0, "bis": 3, "alt": "abc", "neu": "d", "grund": "", "art": "tipp"},
                        {"von": 2, "bis": 99, "alt": "c", "neu": "", "grund": "", "art": "tipp"}], "eigen", 5)
    assert len(r) == 1 and r[0].quelle == "eigen" and r[0].konfidenz is not None


def _f(quelle, neu="X", konf=0.7, art="fehler", alt="Wort", von=0, bis=4):
    return ProofingIssue(von, bis, alt, neu, "g", art, quelle=quelle, konfidenz=konf)


def test_abstimmen_gleiches_neu_bestaetigt_und_ist_idempotent():
    g = fund.loesen([_f("eigen", konf=0.8), _f("languagetool", konf=0.7)])
    a = fund.abstimmen(g)
    assert len(a) == 1 and a[0].bestaetigt_von == ("languagetool",) and a[0].konfidenz > 0.8
    assert fund.abstimmen(a) == a


def test_abstimmen_verschiedenes_neu_senkt_fehler_auf_tipp():
    a = fund.abstimmen(fund.loesen([_f("eigen", "A", 0.8), _f("languagetool", "B", 0.7)]))
    assert len(a) == 1 and a[0].art == "tipp" and a[0].verdraengt


def test_abstimmen_in_ruhe_und_selbst():
    funde = [_f("languagetool")]
    assert fund.abstimmen(funde, in_ruhe={"wort": True}) == []
    assert fund.abstimmen(funde, in_ruhe={"wort": True}, selbst={"wort": "x"}) == funde


def test_abstimmen_gegenprobe_nur_auf_wunsch():
    funde = [_f("eigen", konf=0.8)]
    gp = {"languagetool": [(0, 100)]}
    assert fund.abstimmen(funde, geprueft=gp) == funde
    assert fund.abstimmen(funde, geprueft=gp, gegenprobe=True)[0].art == "tipp"
    assert fund.abstimmen([_f("eigen", konf=0.9)], geprueft=gp, gegenprobe=True)[0].art == "fehler"
    assert fund.abstimmen(funde, geprueft={"eigen": [(0, 100)]}, gegenprobe=True) == funde
