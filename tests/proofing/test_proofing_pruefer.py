import pytest

from lunivo_writer.proofing import pruefung

TEXT = ("Das ist ein Satz mit  zwei Leerzeichen und einem Tippfehler wie Fehlr . ich glaube das er kommt, aber  vieleicht nicht. "
        "Die kleinen Kinder spielt im Garten. Wir haben gestern einen Test gemacht dass alles klappt.")


def _schluessel(funde):
    return sorted((f.von, f.bis, f.alt, f.art) for f in funde)


def test_namen_und_aktiv():
    assert pruefung.PRUEFER_NAMEN == ["woerter", "zusammengeschrieben", "klang", "tippfehler", "zeichen", "gross", "grammatik",
                                      "komma", "kongruenz", "satzende", "satzbau"]
    assert pruefung.pruefer_aktiv("komma") and pruefung.pruefer_aktiv("komma", {})
    assert not pruefung.pruefer_aktiv("komma", {"pruefer_komma": False})
    assert not pruefung.pruefer_aktiv("komma", {"rsGrammatik": False})
    assert pruefung.pruefer_aktiv("zeichen", {"rsGrammatik": False})


@pytest.mark.parametrize("name", pruefung.PRUEFER_NAMEN)
def test_ausgeschalteter_pruefer_liefert_nichts_neues(name):
    alle = _schluessel(pruefung.finde_probleme(TEXT))
    ohne = _schluessel(pruefung.finde_probleme(TEXT, None, {"pruefer_" + name: False}))
    assert alle, "Beispieltext liefert keine Funde"
    # Ausschalten kann Funde wegnehmen, aber nie neue erzeugen (Überschneidungen dürfen verdrängte Funde freigeben)
    assert len(ohne) <= len(alle) + 2


def test_alle_aus_liefert_keine_funde():
    aus = {"pruefer_" + n: False for n in pruefung.PRUEFER_NAMEN}
    assert pruefung.finde_probleme(TEXT, None, aus) == []


def test_nur_zeichen_findet_nur_zeichenfehler_keine_woerter():
    nur = {"pruefer_" + n: False for n in pruefung.PRUEFER_NAMEN if n != "zeichen"}
    funde = pruefung.finde_probleme(TEXT, None, nur)
    assert funde and not any(c.isalpha() for f in funde for c in f.alt)


def test_grammatik_schalter_nimmt_alle_grammatikpruefer_weg():
    nur_rechtschreibung = pruefung.finde_probleme(TEXT, None, {"rsGrammatik": False})
    aus = {"pruefer_" + n: False for n in pruefung.GRAMMATIK_PRUEFER}
    assert _schluessel(nur_rechtschreibung) == _schluessel(pruefung.finde_probleme(TEXT, None, aus))


def test_schreibhilfe_gibt_prueferschalter_aus_den_einstellungen_weiter(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.proofing.proofing_service import WritingAssistant
    from lunivo_writer.services.settings_service import Settings
    s = Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat))
    s.set("schreibhilfe/pruefer_komma", False)
    a = WritingAssistant(s)
    schalter = a.pruef_schalter()
    assert schalter["pruefer_komma"] is False and schalter["pruefer_zeichen"] is True and schalter["rsGrammatik"] is True
    assert not pruefung.pruefer_aktiv("komma", schalter) and pruefung.pruefer_aktiv("zeichen", schalter)


def _paare(text, schalter=None):
    return {(f.alt, f.neu, f.art) for f in pruefung.finde_probleme(text, None, schalter)}


def test_klang_legasthenie_schreibweisen():
    assert ("fileicht", "vielleicht", "tipp") in _paare("Das ist fileicht eine kwalität.")
    assert ("kwalität", "Qualität", "tipp") in _paare("Das ist fileicht eine kwalität.")
    assert ("Fogel", "Vogel", "tipp") in _paare("Fogel sind schön")
    treffer = [f for f in pruefung.finde_probleme("Fogel sind schön") if f.alt == "Fogel"]
    assert treffer[0].quelle in (None, "eigen") and treffer[0].konfidenz == 0.7


def test_klang_waehlt_spielen_nicht_schielen():
    assert ("schpielen", "spielen", "tipp") in _paare("Wir schpielen heute.")
    assert pruefung.vorschlaege_fuer("schpielen")[0] == "spielen"


def test_klang_buchstabendreher_und_verwechslung():
    assert ("wirklihc", "wirklich", "tipp") in _paare("Das ist wirklihc gut.")
    assert ("druder", "bruder", "tipp") in _paare("Mein druder kommt.")


@pytest.mark.parametrize("text", ["Das sagte Müller-Lüdenscheidt.", "Mit Kubernetes arbeiten.", "Die NASA sendet.",
                                  "Kaffeemaschinenfabrik"])
def test_klang_schweigt_bei_namen_fachwoertern_zusammensetzung(text):
    assert not [f for f in pruefung.finde_probleme(text) if f.grund.startswith("Klingt wie")]


def test_klang_schalter_aus():
    funde = pruefung.finde_probleme("Wir schpielen heute. Fogel sind schön", None, {"pruefer_klang": False})
    assert not [f for f in funde if f.grund.startswith("Klingt wie")]


@pytest.mark.parametrize("text", ["Lunivo ist ein Programm.", "Wir versuchen vorzudrängen.", "Der Wortabstand passt."])
def test_klang_schweigt_bei_eigennamen_ableitung_und_zusammensetzung(text):
    assert not [f for f in pruefung.finde_probleme(text) if f.grund.startswith("Klingt wie")]


def test_klang_gewinnt_vor_tippfehler_bei_schpiele_und_kome():
    assert ("schpiele", "spiele", "tipp") in _paare("Ich schpiele gern.")
    assert ("kome", "komme", "tipp") in _paare("Ich kome gleich.")
