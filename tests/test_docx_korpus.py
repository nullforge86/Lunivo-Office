"""DOCX-Korpus: jedes Dokument übersteht Einlesen → Speichern → Einlesen ohne Abweichung in Text, Zeichenformat, Tabellenstruktur, Bildern;
nicht Unterstütztes steht im Bericht (siehe werkzeug/docx_korpus.py)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "werkzeug"))
import docx_korpus as K  # noqa: E402

EXTERN = K.externe()


@pytest.mark.parametrize("name", sorted(K.KORPUS))
def test_roundtrip_ohne_abweichung(app, tmp_path, name):
    r = K.roundtrip(K.bauen(name, str(tmp_path)))
    assert r["abweichungen"] == [], f"{name}: {r['abweichungen']}"


@pytest.mark.parametrize("name", sorted(EXTERN))
def test_externe_dokumente(app, name):
    r = K.roundtrip(EXTERN[name])
    assert r["abweichungen"] == [], f"{name}: {r['abweichungen']} (Hinweise: {r['bericht_lesen']})"


def test_verbundene_zellen_bleiben_verbunden(app, tmp_path):
    r = K.roundtrip(K.bauen("tabelle_verbunden", str(tmp_path)))
    zeile, spalte, zeilen_span, spalten_span = r["zweit"]["tabellen"][0][2][0]
    assert (zeile, spalte, zeilen_span, spalten_span) == (0, 0, 1, 2)                       # waagerecht verbunden
    assert (1, 2, 2, 1) in r["zweit"]["tabellen"][0][2]                                     # senkrecht verbunden


def test_bild_und_schrift_bleiben(app, tmp_path):
    assert K.roundtrip(K.bauen("schwebendes_bild", str(tmp_path)))["zweit"]["bilder"] == 1
    laeufe = K.roundtrip(K.bauen("schriften_und_sprachen", str(tmp_path)))["zweit"]["laeufe"]
    assert {l[1] for l in laeufe} >= {"DejaVu Sans", "DejaVu Serif", "DejaVu Sans Mono"}


def test_nicht_unterstuetztes_steht_im_bericht(app, tmp_path):
    assert any("Verschachtelte Tabellen" in w for w in K.roundtrip(K.bauen("ungewoehnlich", str(tmp_path)))["bericht_lesen"])
