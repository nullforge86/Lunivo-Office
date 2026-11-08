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


def test_schwaerzen_entfernt_schluessel_und_kennwoerter():
    t = protokoll.schwaerzen('Fehler bei apiKey=sk-ant-abcdef123456 und Authorization: Bearer abc.def-123456789, "password": "geheim1", x-api-key: AAAA1111')
    for geheim in ("sk-ant-abcdef123456", "abc.def-123456789", "geheim1", "AAAA1111"):
        assert geheim not in t
    assert "Fehler bei" in t and t.count("***") >= 4
    assert protokoll.schwaerzen("Ganz normaler Satz.") == "Ganz normaler Satz."


def test_drei_fehlerarten_und_schutz_in_der_datei(app):
    import threading
    pfad = protokoll.einrichten()
    log = logging.getLogger("lunivo.fehlerarten")
    protokoll.benutzerfehler(log, ValueError("Datei fehlt"))
    protokoll.technischer_fehler(log, "Speichern", OSError(28, "Platte voll"))
    try:
        {}["x"]
    except KeyError as e:
        protokoll.unerwartet(log, "Probe mit sk-test-1234567890abcdef", e)
    log.error("Ausnahme", exc_info=(RuntimeError, RuntimeError("password=hunter2xyz"), None))
    for h in logging.getLogger("lunivo").handlers:
        h.flush()
    with open(pfad, encoding="utf-8") as fh:
        inhalt = fh.read()
    assert "Hinweis an den Benutzer: Datei fehlt" in inhalt and "Speichern: OSError (errno 28)" in inhalt
    assert "Unerwarteter Fehler bei" in inhalt and "Traceback" in inhalt and "KeyError" in inhalt and "PySide6" in inhalt
    assert "sk-test-1234567890abcdef" not in inhalt and "hunter2xyz" not in inhalt
    assert threading.excepthook is not threading.__excepthook__                          # Fehler in Arbeitsfäden werden ebenfalls protokolliert
