"""KI-Datenschutz: Einwilligung je Anbieter und Umfang, Sperre an der Sendestelle, Widerruf, lokale Adressen."""
import pytest

from lunivo_writer.ai import ki as K


@pytest.fixture
def ki(tmp_path):
    k = K.KIKonfig(str(tmp_path / "ki.json"))
    k.setze("apiKey", "sk-test")
    k.setze("modell", "claude-opus-5")
    return K.KI(k)


@pytest.fixture
def netz(monkeypatch):
    """Jeder Versuch zu senden wird gezählt und scheitert."""
    gesendet = []

    def post(*a, **k):
        gesendet.append(a)
        raise OSError("kein Netz im Test")
    monkeypatch.setattr(K, "_post", post)
    return gesendet


def test_ohne_zustimmung_wird_nichts_gesendet(ki, netz):
    r = ki.anfrage("Korrigiere", "Hallo Welt")
    assert "keine Zustimmung" in r["fehler"] and not netz


def test_mit_zustimmung_wird_gesendet(ki, netz):
    ki.k.einwilligung_geben("Anthropic (Claude)", "auszug")
    ki.anfrage("Korrigiere", "Hallo Welt")
    assert netz


def test_chat_mit_dokument_braucht_umfang_dokument(ki, netz):
    ki.k.einwilligung_geben("Anthropic (Claude)", "auszug")
    r = ki.chat([{"rolle": "mensch", "text": "Frage"}], "Ganzes Dokument hier")
    assert "keine Zustimmung" in r["fehler"] and not netz
    ki.k.einwilligung_geben("Anthropic (Claude)", "dokument")
    ki.chat([{"rolle": "mensch", "text": "Frage"}], "Ganzes Dokument hier")
    assert netz


def test_dokument_schliesst_auszug_ein_nicht_umgekehrt(ki):
    k = ki.k
    k.einwilligung_geben("X", "auszug")
    assert k.hat_einwilligung("X", "auszug") and not k.hat_einwilligung("X", "dokument")
    k.einwilligung_geben("Y", "dokument")
    assert k.hat_einwilligung("Y", "auszug") and k.hat_einwilligung("Y", "dokument")


def test_alte_eintraege_werden_uebernommen_und_datum_gespeichert(tmp_path):
    k = K.KIKonfig(str(tmp_path / "a.json"))
    k.setze("einwilligungen", ["Alter Anbieter"])
    assert k.einwilligungen() == [{"anbieter": "Alter Anbieter", "umfang": "dokument", "seit": ""}]
    k.einwilligung_geben("Neu", "auszug")
    assert [e for e in K.KIKonfig(str(tmp_path / "a.json")).einwilligungen() if e["anbieter"] == "Neu"][0]["seit"]     # bleibt gespeichert


def test_widerruf_einzeln_und_alle(ki, netz):
    k = ki.k
    k.einwilligung_geben("Anthropic (Claude)", "dokument"); k.einwilligung_geben("B", "auszug")
    k.einwilligung_widerrufen("B")
    assert [e["anbieter"] for e in k.einwilligungen()] == ["Anthropic (Claude)"]
    k.einwilligung_widerrufen()
    assert k.einwilligungen() == [] and "keine Zustimmung" in ki.anfrage("a", "b")["fehler"] and not netz


def test_lokales_modell_braucht_keine_zustimmung(ki):
    ki.k.setze("modell", K.OLLAMA_MARKE + "llama")
    assert ki.zustimmung_fehlt() is None and ki.schickt_nach_aussen() is None


@pytest.mark.parametrize("url,lokal", [("http://localhost:11434/v1", True), ("http://127.0.0.1/v1", True), ("https://api.fremd.de", False),
                                       ("http://127.0.0.1:80@fremd.de/v1", False), ("http://localhost.fremd.de/", False), ("file:///etc/passwd", False), ("", False)])
def test_lokale_adresse_wird_aus_dem_rechnernamen_gelesen(url, lokal):
    assert K.ist_lokale_url(url) is lokal


def test_bild_url_nur_http(ki, monkeypatch):
    import json

    class R:
        def __enter__(s): return s
        def __exit__(s, *a): return False
        def read(s): return json.dumps({"data": [{"url": "file:///etc/passwd"}]}).encode()
    a = ki.k.anbieter_hinzufuegen("Lokal", "http://localhost:1/v1", "", "m", ["bilder"])
    ki.k.setze("aufgaben", {"bildgenerierung": K.EIGEN_MARKE + a["id"]})
    monkeypatch.setattr(K, "_post", lambda *a, **k: R())
    assert "unzulässige Bildadresse" in ki.bild_erzeugen("Katze")["fehler"]


def test_datenschutz_reiter_zeigt_und_widerruft(app, ki):
    from lunivo_writer.ui.dialogs.ki_dialoge import EinwilligungenPanel
    ki.k.einwilligung_geben("Anthropic (Claude)", "dokument")
    p = EinwilligungenPanel(ki.k)
    assert p.liste.count() == 1 and "Anthropic" in p.liste.item(0).text() and "ganzen Text" in p.liste.item(0).text()
    p.widerruf.click()
    assert ki.k.einwilligungen() == [] and not p.widerruf.isEnabled() and not p.alle.isEnabled()


@pytest.mark.parametrize("antwort", [b"", b"kein json", b"[]", b'{"content": "falsch"}', b'{"content": [{"type": "text"}]}', b'{"choices": []}', b"\xff\xfe"])
def test_fehlerhafte_ki_antworten_stuerzen_nicht_ab(ki, monkeypatch, antwort):
    class R:
        def __enter__(s): return s
        def __exit__(s, *a): return False
        def read(s): return antwort
    ki.k.einwilligung_geben("Anthropic (Claude)", "dokument")
    monkeypatch.setattr(K, "_post", lambda *a, **k: R())
    r = ki.anfrage("Korrigiere", "Hallo")
    assert isinstance(r, dict) and ("fehler" in r or "text" in r)
