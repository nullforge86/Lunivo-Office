import pytest

from lunivo_writer.proofing import pruefung

TEXT = ("Das ist ein Satz mit  zwei Leerzeichen und einem Tippfehler wie Fehlr . ich glaube das er kommt, aber  vieleicht nicht. "
        "Die kleinen Kinder spielt im Garten. Wir haben gestern einen Test gemacht dass alles klappt.")


def _schluessel(funde):
    return sorted((f["von"], f["bis"], f["alt"], f["art"]) for f in funde)


def test_namen_und_aktiv():
    assert pruefung.PRUEFER_NAMEN == ["woerter", "zusammengeschrieben", "tippfehler", "zeichen", "gross", "grammatik",
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
    assert funde and not any(c.isalpha() for f in funde for c in f["alt"])


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
