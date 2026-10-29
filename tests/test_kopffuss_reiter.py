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


def test_kontext_reiter_ist_abgesetzt(app):
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow()
    band = w.band
    assert "kopffuss" in band.kontext_index
    for name, i in band.kontext_index.items():
        assert band.reiter.ist_kontext(i)
    assert not band.reiter.ist_kontext(band._start_index())
    i = band.kontext_index["kopffuss"]
    band.kontext("kopffuss", True)
    breit = band.reiter.tabSizeHint(i).width()
    assert breit >= band.reiter.fontMetrics().horizontalAdvance("Kopf- und Fußzeile") + 2 * band.reiter.LUECKE


def test_hoehenfelder_beschriftet_und_nicht_null(app):
    from PySide6.QtWidgets import QLabel
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow()
    w.new_document()
    w.befehle.tun("kopfFussZeigen")
    for schl, text in (("kopfHoehe", "Kopfzeilenhöhe:"), ("fussHoehe", "Fußzeilenhöhe:")):
        f = w.band.felder[schl]; f.neu_laden()
        assert text in [l.text() for l in f.findChildren(QLabel)]
        assert f.feld.feld.value() != 0
        assert "," in f.feld.feld.text() and f.feld.feld.text().endswith("mm")
