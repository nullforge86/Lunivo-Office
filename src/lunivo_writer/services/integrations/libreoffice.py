"""LibreOffice als Umwandler (Adapter) — nur über die dokumentierte Kommandozeile.

    soffice --headless --convert-to <format> --outdir <ordner> <datei>

Das ist KEINE Einbettung und kein Zugriff auf Interna: LibreOffice wird als eigenes Programm gerufen, wenn
es installiert ist. Fehlt es, bleibt alles andere nutzbar (DOCX, TXT, ODT-Export über Qt).
"""
from __future__ import annotations

import os
import resource
import shutil
import signal
import subprocess
import tempfile
import time
from typing import Callable

from lunivo_writer.models.report import DocumentIOError
from lunivo_writer.services.settings_service import data_dir

TIMEOUT_S = 180
# Obergrenze für den Adressraum des Umwandlers: Läuft er bei einer Datei aus dem Ruder, scheitert die Umwandlung —
# statt dass er den ganzen Arbeitsspeicher belegt und den Desktop mitreißt. Übliche Dokumente brauchen weit unter 1 GB.
SPEICHER_GRENZE = 4 * 1024 ** 3
TAKT_S = 0.05
# Endung → Filtername für --convert-to
FILTER = {"docx": "docx:MS Word 2007 XML", "odt": "odt:writer8", "doc": "doc:MS Word 97",
          "rtf": "rtf:Rich Text Format", "txt": "txt:Text (encoded):UTF8"}


def finde_soffice() -> str | None:
    return shutil.which("soffice") or shutil.which("libreoffice")


def verfuegbar() -> bool:
    return finde_soffice() is not None


def _begrenzen() -> None:                        # läuft im Kindprozess vor dem Start des Umwandlers
    resource.setrlimit(resource.RLIMIT_AS, (SPEICHER_GRENZE, SPEICHER_GRENZE))


def _beenden(lauf: subprocess.Popen) -> None:
    """Beendet den Umwandler samt Kindern (soffice startet soffice.bin als eigenen Prozess)."""
    try:
        os.killpg(lauf.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        lauf.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass


def konvertiere(quelle: str, ziel_ext: str, ordner: str, warten: Callable[[], bool] | None = None) -> str:
    """Wandelt `quelle` nach `ziel_ext` um (Ergebnis liegt in `ordner`). → Pfad der neuen Datei.

    `warten` wird während der Umwandlung regelmäßig gerufen (die Oberfläche bleibt so bedienbar);
    gibt es False zurück, wird abgebrochen."""
    soffice = finde_soffice()
    if not soffice:
        raise DocumentIOError("Das Umwandlungsprogramm ist nicht installiert. Dieses Format braucht es "
                              "(Installation: sudo apt install libreoffice-writer).")
    profil = os.path.join(data_dir(), "lo-profil")
    os.makedirs(profil, exist_ok=True)
    try:
        lauf = subprocess.Popen(
            [soffice, "-env:UserInstallation=file://" + profil, "--headless", "--norestore",
             "--convert-to", FILTER.get(ziel_ext, ziel_ext), "--outdir", ordner, quelle],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding="utf-8", errors="replace", start_new_session=True, preexec_fn=_begrenzen)
    except OSError as e:
        raise DocumentIOError(f"Das Umwandlungsprogramm ließ sich nicht starten: {e.strerror or e}") from e
    ende = time.monotonic() + TIMEOUT_S
    try:
        while True:
            try:
                ausgabe, fehler = lauf.communicate(timeout=TAKT_S)
                break
            except subprocess.TimeoutExpired:
                pass
            if time.monotonic() > ende:
                raise DocumentIOError("Das Umwandlungsprogramm hat zu lange gebraucht und wurde abgebrochen.")
            if warten is not None and not warten():
                raise DocumentIOError("Die Umwandlung wurde abgebrochen.")
    finally:
        if lauf.poll() is None:
            _beenden(lauf)
    ziel = os.path.join(ordner, os.path.splitext(os.path.basename(quelle))[0] + "." + ziel_ext)
    if not os.path.isfile(ziel):
        hinweis = (fehler or ausgabe or "").strip().splitlines()
        if lauf.returncode and lauf.returncode < 0:
            hinweis.append("Das Umwandlungsprogramm wurde beendet (zu wenig Speicher oder abgestürzt).")
        raise DocumentIOError("Die Umwandlung ergab nichts"
                              + (f": {hinweis[-1]}" if hinweis else "."))
    return ziel


def in_docx(pfad: str) -> tuple[str, tempfile.TemporaryDirectory]:
    """Datei → temporäre DOCX. Der Aufrufer behält das Verzeichnisobjekt, bis er fertig gelesen hat."""
    tmp = tempfile.TemporaryDirectory(prefix="lunivo-")
    return konvertiere(pfad, "docx", tmp.name), tmp


def aus_docx(docx_pfad: str, ziel_pfad: str, warten: Callable[[], bool] | None = None) -> None:
    """DOCX → ODT/DOC/RTF nach `ziel_pfad` (atomar kopiert)."""
    ext = os.path.splitext(ziel_pfad)[1].lstrip(".").lower()
    with tempfile.TemporaryDirectory(prefix="lunivo-") as tmp:
        fertig = konvertiere(docx_pfad, ext, tmp, warten)
        folder = os.path.dirname(os.path.abspath(ziel_pfad))
        try:
            fd, t = tempfile.mkstemp(dir=folder, suffix=".tmp")
            os.close(fd)
            shutil.copyfile(fertig, t)
            os.replace(t, ziel_pfad)
        except OSError as e:
            raise DocumentIOError(f"Speichern nicht möglich: {e.strerror or e}") from e
