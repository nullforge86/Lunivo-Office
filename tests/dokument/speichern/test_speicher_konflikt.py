"""Speichern: Änderungen anderer Programme werden in der Sperre erkannt, parallele Schreibvorgänge zerstören nichts."""
import multiprocessing
import os
import threading
import time

import pytest

from lunivo_writer.modelle.bericht import DocumentIOError
from lunivo_writer.dienste import sicher_schreiben as S


def lesen(p):
    with open(p, "rb") as fh:
        return fh.read()


def test_unveraenderte_datei_wird_geschrieben(tmp_path):
    p = tmp_path / "a.txt"; p.write_bytes(b"alt")
    S.bytes_schreiben(str(p), b"neu", sicherung=False, erwartet=S.stand(str(p)))
    assert lesen(p) == b"neu"


def test_fremde_aenderung_wird_erkannt_und_nicht_ueberschrieben(tmp_path):
    p = tmp_path / "b.txt"; p.write_bytes(b"alt")
    gesehen = S.stand(str(p))
    time.sleep(0.01); p.write_bytes(b"von einem anderen Programm geaendert")
    with pytest.raises(S.SchreibKonflikt, match="geändert"):
        S.bytes_schreiben(str(p), b"meine Fassung", sicherung=False, erwartet=gesehen)
    assert lesen(p) == b"von einem anderen Programm geaendert"
    assert not [f for f in os.listdir(tmp_path) if f.endswith(".tmp")]          # keine Reste


def test_aenderung_zwischen_erzeugen_und_ersetzen_wird_erkannt(tmp_path):
    """Die Lücke zwischen Prüfung in der Oberfläche und Schreiben: der Vergleich geschieht erst unmittelbar vor dem Ersetzen."""
    p = tmp_path / "c.txt"; p.write_bytes(b"alt")
    gesehen = S.stand(str(p))

    def erzeugen(tmp):
        with open(tmp, "wb") as fh:
            fh.write(b"meine")
        time.sleep(0.01); p.write_bytes(b"fremd dazwischen")                     # ein anderer Prozess schreibt jetzt
    with pytest.raises(S.SchreibKonflikt):
        S.schreiben(str(p), erzeugen, sicherung=False, erwartet=gesehen)
    assert lesen(p) == b"fremd dazwischen"


def test_geloeschte_datei_ist_ein_konflikt_neue_datei_nicht(tmp_path):
    p = tmp_path / "d.txt"; p.write_bytes(b"x")
    gesehen = S.stand(str(p)); p.unlink()
    with pytest.raises(S.SchreibKonflikt, match="gelöscht"):
        S.bytes_schreiben(str(p), b"y", sicherung=False, erwartet=gesehen)
    assert not p.exists()
    S.bytes_schreiben(str(p), b"neu", sicherung=False, erwartet=None)               # None: sie sollte noch nicht da sein – ist sie auch nicht
    with pytest.raises(S.SchreibKonflikt):
        S.bytes_schreiben(str(p), b"zweite", sicherung=False, erwartet=None)         # inzwischen angelegt
    assert lesen(p) == b"neu"


def test_ohne_erwartung_wird_wie_bisher_geschrieben(tmp_path):
    p = tmp_path / "e.txt"; p.write_bytes(b"x")
    S.bytes_schreiben(str(p), b"y", sicherung=False)
    assert lesen(p) == b"y"
    assert issubclass(S.SchreibKonflikt, DocumentIOError)


def test_parallele_schreibvorgaenge_im_programm(tmp_path):
    """Zehn Threads speichern gleichzeitig: jeder gelingt vollständig oder meldet sauber; die Datei ist am Ende eine ganze Fassung."""
    p = tmp_path / "f.txt"; p.write_bytes(b"start")
    ergebnisse, start = [], threading.Barrier(10)

    def lauf(i):
        start.wait()
        try:
            S.bytes_schreiben(str(p), (f"fassung{i}" * 2000).encode(), sicherung=False)
            ergebnisse.append("ok")
        except DocumentIOError as e:
            ergebnisse.append(str(e))
    ts = [threading.Thread(target=lauf, args=(i,)) for i in range(10)]
    [t.start() for t in ts]; [t.join() for t in ts]
    inhalt = lesen(p).decode()
    assert "ok" in ergebnisse and any(inhalt == f"fassung{i}" * 2000 for i in range(10))
    assert all(r == "ok" or "gerade" in r for r in ergebnisse)
    assert not [f for f in os.listdir(tmp_path) if f.endswith(".tmp")]


def _prozess(pfad, i):
    from lunivo_writer.dienste import sicher_schreiben as s
    for _ in range(20):
        try:
            s.bytes_schreiben(pfad, (f"p{i}" * 3000).encode(), sicherung=False)
        except Exception:
            pass


def test_parallele_schreibvorgaenge_zwischen_prozessen(tmp_path):
    p = tmp_path / "g.txt"; p.write_bytes(b"start")
    ctx = multiprocessing.get_context("spawn")
    ps = [ctx.Process(target=_prozess, args=(str(p), i)) for i in range(3)]
    [x.start() for x in ps]; [x.join(60) for x in ps]
    inhalt = lesen(p).decode()
    assert any(inhalt == f"p{i}" * 3000 for i in range(3))                            # nie eine Mischung zweier Fassungen
    assert not [f for f in os.listdir(tmp_path) if f.endswith(".tmp")]
