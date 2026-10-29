"""Struktur des Kontext-Reiters „Kopf- und Fußzeile“: Knöpfe und Befehlsnamen in der WPS-Reihenfolge."""
from lunivo_writer.ui.contextual.header_footer_tools import KOPFFUSS


def test_kopffuss_reiter_reihenfolge():
    assert KOPFFUSS["name"] == "Kopf- und Fußzeile" and KOPFFUSS["kontext"] == "kopffuss"
    ids = []
    for g in KOPFFUSS["gruppen"]:
        for e in g["knoepfe"]:
            ids.append(e.get("feld") or e.get("klappe") or e.get("tun"))
    assert ids == ["kfGruppeKlappe", "kopfzeileKlappe", "fusszeileKlappe", "seitenzahlKlappe", "kopfLinieKlappe",
                   "datumUhrzeit", "bildKlappe", "felder",
                   "kfWechseln", "kfVorige", "kfNaechste", "kfVerknuepfen",
                   "kfOptionen", "kfTabstopp", "kopfHoehe", "fussHoehe",
                   "kfEinstellungenKlappe", "kopfFussSchliessen"]
