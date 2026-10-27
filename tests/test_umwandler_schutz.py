"""Schutz beim Umwandeln über das Umwandlungsprogramm: Speichergrenze, Abbruch ohne zurückbleibende Prozesse.

Ein nachgebautes „soffice“ (Shell-Skript) ersetzt das echte Programm — die Tests laufen auch ohne LibreOffice."""
import os
import stat
import time

import pytest

from lunivo_writer.models.report import DocumentIOError
from lunivo_writer.services.integrations import libreoffice


def _falsches_soffice(tmp_path, monkeypatch, rumpf: str) -> None:
    skript = tmp_path / "soffice"
    skript.write_text("#!/bin/bash\n" + rumpf + "\n", encoding="utf-8")
    skript.chmod(skript.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setattr(libreoffice, "finde_soffice", lambda: str(skript))
    monkeypatch.setattr(libreoffice, "data_dir", lambda: str(tmp_path / "daten"))


def _laeuft(pid: int) -> bool:
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as fh:
            return fh.read().split()[2] != "Z"
    except FileNotFoundError:
        return False


def _kind_pid(tmp_path) -> int:
    datei = tmp_path / "kind.pid"
    for _ in range(100):
        if datei.exists() and datei.read_text().strip():
            return int(datei.read_text())
        time.sleep(0.02)
    raise AssertionError("Das nachgebaute Umwandlungsprogramm ist nicht gestartet.")


def test_speichergrenze_gilt_fuer_den_umwandler(tmp_path, monkeypatch):
    # das Skript schreibt seine Adressraum-Grenze (in KB) als „Ergebnisdatei“ — so wie soffice nach --outdir schreibt
    _falsches_soffice(tmp_path, monkeypatch, 'ulimit -v > "${@: -2:1}/q.odt"')
    (tmp_path / "q.docx").write_bytes(b"x")
    ziel = libreoffice.konvertiere(str(tmp_path / "q.docx"), "odt", str(tmp_path))
    assert int(open(ziel).read()) * 1024 == libreoffice.SPEICHER_GRENZE


def test_abbrechen_beendet_umwandler_samt_kindern(tmp_path, monkeypatch):
    # wie soffice → soffice.bin: der Startprozess hat ein Kind, das weiterliefe, wenn nur er beendet würde
    _falsches_soffice(tmp_path, monkeypatch, f'sleep 60 & echo $! > "{tmp_path}/kind.pid"; wait')
    aufrufe = []

    def warten():
        aufrufe.append(1)
        return len(aufrufe) < 3

    with pytest.raises(DocumentIOError, match="abgebrochen"):
        libreoffice.konvertiere(str(tmp_path / "q.docx"), "odt", str(tmp_path), warten)
    kind = _kind_pid(tmp_path)
    time.sleep(0.1)
    assert len(aufrufe) == 3 and not _laeuft(kind)


def test_zeitueberschreitung_beendet_umwandler(tmp_path, monkeypatch):
    _falsches_soffice(tmp_path, monkeypatch, f'sleep 60 & echo $! > "{tmp_path}/kind.pid"; wait')
    monkeypatch.setattr(libreoffice, "TIMEOUT_S", 0.3)
    with pytest.raises(DocumentIOError, match="zu lange"):
        libreoffice.konvertiere(str(tmp_path / "q.docx"), "odt", str(tmp_path))
    kind = _kind_pid(tmp_path)
    time.sleep(0.1)
    assert not _laeuft(kind)


def test_absturz_des_umwandlers_wird_gemeldet(tmp_path, monkeypatch):
    _falsches_soffice(tmp_path, monkeypatch, "kill -9 $$")
    with pytest.raises(DocumentIOError, match="zu wenig Speicher oder abgestürzt"):
        libreoffice.konvertiere(str(tmp_path / "q.docx"), "odt", str(tmp_path))
