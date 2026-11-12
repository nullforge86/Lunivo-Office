"""Fortlaufende Assistenten: reine Regeln (Drosselung, geänderter Absatz, leere Ergebnisse)."""
from lunivo_writer.ki import assistent_lauf as AL


def test_absatz_geaendert():
    assert AL.absatz_geaendert(None, "Das ist ein neuer Absatz.")
    assert not AL.absatz_geaendert("Das ist ein neuer Absatz.", " Das ist ein neuer Absatz. ")
    assert not AL.absatz_geaendert(None, "Kurz")
    assert AL.absatz_geaendert("Das ist ein Absatz.", "Das ist ein anderer Absatz.")


def test_ergebnis_wirkt_nicht_bei_leer_oder_gleich():
    assert not AL.ergebnis_wirkt("Hallo  Welt", "")
    assert not AL.ergebnis_wirkt("Hallo  Welt", "Hallo Welt\n")
    assert AL.ergebnis_wirkt("Hallo Welt", "Hallo, Welt")


def test_begruendung_trennen():
    assert AL.trenne_begruendung("Neu\n" + AL.BEGRUENDUNG_TRENNER + "\nWeil.") == ("Neu", "Weil.")
    assert AL.trenne_begruendung("Nur Text") == ("Nur Text", "")


def test_verzoegerung_grenzen():
    assert AL.verzoegerung_begrenzen(0) == AL.VERZOEGERUNG_MIN
    assert AL.verzoegerung_begrenzen(999) == AL.VERZOEGERUNG_MAX
    assert AL.verzoegerung_begrenzen("x") == AL.VERZOEGERUNG_VORGABE


def test_drossel_abstand_und_stundengrenze():
    t = [0.0]
    d = AL.Drossel(abstand=10, je_stunde=2, uhr=lambda: t[0])
    assert d.erlaubt()
    d.gesendet()
    t[0] = 4
    assert d.warten_noch() == 6
    t[0] = 11
    d.gesendet()
    t[0] = 30
    assert d.stundengrenze()
    t[0] = 3700
    assert d.erlaubt()
