import logging

from lunivo_writer.plattform import protokoll


def test_einrichten_schreibt_in_logdatei_und_ist_wiederholbar(app):
    pfad = protokoll.einrichten()
    assert pfad == protokoll.einrichten()
    log = logging.getLogger("lunivo.test")
    log.error("Probe-Eintrag")
    for h in logging.getLogger("lunivo").handlers:
        h.flush()
    with open(pfad, encoding="utf-8") as fh:
        assert "Probe-Eintrag" in fh.read()
