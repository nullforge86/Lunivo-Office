"""Lokale Übersetzung (Argos) und Betriebsart „Automatisch“ — Argos wird ersetzt, nichts installiert, kein Netz."""
import pytest

from lunivo_writer.ki import argos
from lunivo_writer.ki import ki as K


@pytest.fixture
def ki(tmp_path):
    k = K.KIKonfig(str(tmp_path / "ki.json"))
    k.setze("apiKey", "sk-test")
    k.setze("modell", "claude-opus-5")
    return K.KI(k)


@pytest.fixture
def lokal(monkeypatch):
    aufrufe = []

    def fake(text, sprache, quelle=None):
        aufrufe.append((text, sprache))
        return {"text": "LOKAL:" + text, "methode": "Lokal"}
    monkeypatch.setattr(argos, "uebersetze", fake)
    return aufrufe


def test_sprache_zu_code():
    assert argos.code_fuer("Deutsch") == "de" and argos.code_fuer("Ukrainisch") == "uk"
    assert argos.code_fuer("Klingonisch") is None
    assert argos.erkenne_sprache("Das ist ein Haus und ich bin nicht da") == "de"
    assert argos.erkenne_sprache("The house is on the hill and it was big") == "en"
    assert argos.erkenne_sprache("") == "de"


def test_fehlendes_paket_gibt_verstaendliche_meldung(monkeypatch):
    monkeypatch.setattr(argos, "_bibliothek", lambda: None)
    r = argos.uebersetze("Hallo", "Englisch")
    assert "fehler" in r and "argostranslate" in r["fehler"]
    assert "fehler" in argos.uebersetze("Hallo", "Klingonisch")


def test_argos_schickt_nichts_nach_aussen(ki):
    assert ki.schickt_nach_aussen("argos:") is None


def test_auto_ohne_ki_geht_lokal(ki, lokal):
    ki.k.setze("apiKey", "")
    ki.k.setze("aufgaben", {"uebersetzung": K.AUTO_MARKE})
    assert ki.schickt_nach_aussen(K.AUTO_MARKE) is None
    r = ki.uebersetzen("Hallo", "Englisch")
    assert r["methode"] == "Lokal" and lokal


def test_auto_ohne_einwilligung_geht_lokal(ki, lokal, monkeypatch):
    monkeypatch.setattr(K, "_post", lambda *a, **k: pytest.fail("gesendet"))
    ki.k.setze("aufgaben", {"uebersetzung": K.AUTO_MARKE})
    assert ki.uebersetzen("Hallo", "Englisch")["methode"] == "Lokal"


def test_auto_ki_fehler_einmal_lokal(ki, lokal, monkeypatch):
    ki.k.einwilligung_geben("Anthropic (Claude)", "auszug")
    ki.k.setze("aufgaben", {"uebersetzung": K.AUTO_MARKE})
    n = []
    monkeypatch.setattr(K, "_post", lambda *a, **k: n.append(1) or (_ for _ in ()).throw(OSError("aus")))
    r = ki.uebersetzen("Hallo", "Englisch")
    assert r["methode"] == "Lokal" and len(lokal) == 1 and n


def test_auto_ki_ok_nennt_ki(ki, lokal, monkeypatch):
    ki.k.einwilligung_geben("Anthropic (Claude)", "auszug")
    ki.k.setze("aufgaben", {"uebersetzung": K.AUTO_MARKE})
    monkeypatch.setattr(ki, "anfrage", lambda *a, **k: {"ergebnis": "Hello"})
    r = ki.uebersetzen("Hallo", "Englisch")
    assert r["text"] == "Hello" and r["methode"] == "KI" and not lokal


def test_auto_ablehnung_der_einwilligung_geht_lokal(ki, lokal, monkeypatch):
    """Ohne Einwilligung (Benutzer lehnt ab) wird nichts gesendet und lokal übersetzt."""
    ki.k.setze("aufgaben", {"uebersetzung": K.AUTO_MARKE})
    assert ki.schickt_nach_aussen(K.AUTO_MARKE) == "Anthropic (Claude)"      # die Rückfrage kommt weiterhin
    monkeypatch.setattr(K, "_post", lambda *a, **k: pytest.fail("gesendet"))
    assert ki.uebersetzen("Hallo", "Englisch")["methode"] == "Lokal"


class _Paket:
    def __init__(self, von, nach, groesse=None):
        self.from_code, self.to_code, self.package_size = von, nach, groesse

    def download(self):
        return "/tmp/x.argosmodel"


class _FakePackage:
    def __init__(self, netz=True):
        self.netz, self.installiert = netz, []

    def update_package_index(self):
        if not self.netz:
            raise OSError("kein Netz")

    def get_available_packages(self):
        return [_Paket("en", "de", 100e6), _Paket("en", "fr", 90e6)]

    def get_installed_packages(self):
        return [_Paket("en", "de")]

    def install_from_path(self, p):
        self.installiert.append(p)


def test_sprachpakete_verwalten(monkeypatch):
    fp = _FakePackage()
    monkeypatch.setattr(argos, "_bibliothek", lambda: (fp, None))
    monkeypatch.setattr(argos, "_mitgelieferte_installieren", lambda p: None)
    assert argos.installierte_richtungen()[0]["name"] == "Englisch → Deutsch"
    r = argos.verfuegbare_richtungen()["richtungen"]
    assert [(x["von"], x["nach"]) for x in r] == [("en", "fr")] and r[0]["groesse_mb"] == 90
    assert argos.richtung_installieren("en", "fr")["ok"] and fp.installiert
    assert "fehler" in argos.richtung_installieren("en", "xx")


def test_sprachpakete_netzfehler_verstaendlich(monkeypatch):
    monkeypatch.setattr(argos, "_bibliothek", lambda: (_FakePackage(netz=False), None))
    r = argos.richtung_installieren("en", "fr")
    assert "Internetverbindung" in r["fehler"]
    assert "Internetverbindung" in argos.verfuegbare_richtungen()["fehler"]
