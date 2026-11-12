"""Ein sicherer Schreibweg für alle Dokumentdateien (DOCX, ODT, DOC, RTF, TXT, PDF).

Ablauf je Speichervorgang:

1. Sperre auf die Zieldatei (im Programm und zwischen Lunivo-Fenstern über eine Sperrdatei, siehe ``plattform/sperre.py``).
2. Neue Fassung in eine Temp-Datei im *selben Ordner* schreiben (gleiches Dateisystem → Umbenennen ist atomar).
3. ``fsync`` der Temp-Datei, dann Strukturprüfung im jeweiligen Format (``pruefe_format``).
4. Sicherungskopie der bisherigen Fassung im Datenordner (begrenzt, siehe ``SICHERUNGEN_JE_DOKUMENT``).
5. Rechte der bisherigen Datei übernehmen, ``os.replace`` auf die Zieldatei, ``fsync`` des Ordners.

Scheitert ein Schritt, wird die Temp-Datei entfernt und die bisherige Datei bleibt unverändert.

Garantien der Plattform (Linux): ``rename``/``os.replace`` ist auf einem lokalen POSIX-Dateisystem (ext4, btrfs, xfs) atomar —
nach einem Absturz liegt entweder die alte oder die neue Fassung vollständig vor. Mit ``fsync`` von Datei und Ordner übersteht das
auch einen Stromausfall, sofern Datenträger und Treiber ``fsync`` ehrlich umsetzen. Auf Netz- und FUSE-Laufwerken (SMB, NFS, sshfs,
Cloud-Ordner über rclone o. Ä.) sind Atomarität und ``fsync`` nicht zugesichert; dort gilt nur „so gut wie das Laufwerk es kann“.
"""
from __future__ import annotations

import errno
import glob
import hashlib
import os
import shutil
import stat
import tempfile
import threading
import time
import zipfile
from contextlib import contextmanager
from typing import Callable, TypeVar
from xml.etree import ElementTree

from lunivo_writer.modelle.bericht import DocumentIOError
from lunivo_writer.plattform import dateisystem, sperre as _sperre
from lunivo_writer.dienste.einstellungen_dienst import data_dir

T = TypeVar("T")

SICHERUNGEN_JE_DOKUMENT = 5          # so viele Vorfassungen je Dokument bleiben erhalten
SICHERUNG_TAGE = 30                  # ältere Sicherungskopien werden entfernt
REST_ALTER_S = 600                   # eigene Temp-Reste (nach Absturz) werden nach dieser Zeit beim nächsten Speichern entfernt
ODT_MIMETYPE = b"application/vnd.oasis.opendocument.text"
OLE_KOPF = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

_im_programm: set[str] = set()
_im_programm_sperre = threading.Lock()


# ---- Hilfen ----------------------------------------------------------------------------------------------------------------------
def ziel(path: str) -> str:
    """Tatsächliche Zieldatei: Verknüpfungen werden aufgelöst, damit die Verknüpfung erhalten bleibt."""
    return os.path.realpath(path)


class SchreibKonflikt(DocumentIOError):
    """Die Zieldatei hat sich zwischen Öffnen (oder letztem Speichern) und jetzt verändert; es wurde nichts überschrieben."""


UNGEPRUEFT = object()          # ``erwartet`` nicht angegeben: kein Vergleich (z. B. beim Export in eine neue Datei)


def stand(path: str) -> tuple[int, int] | None:
    """(Änderungszeit in ns, Größe) der Datei oder None — zum Erkennen fremder Änderungen."""
    try:
        st = os.stat(path)
    except (OSError, ValueError):
        return None
    return st.st_mtime_ns, st.st_size


def fremd_geoeffnet(path: str) -> str | None:
    """Beschreibung des Programms, das die Datei laut Sperrdatei offen hat (andere Programme legen „.~lock.<name>#“ an), sonst None."""
    p = ziel(path)
    if os.path.exists(os.path.join(os.path.dirname(p), ".~lock." + os.path.basename(p) + "#")):
        return "einem anderen Office-Programm"
    return None


# Fehlernummer(n) -> Meldung (Name, Ordner)
_FEHLERTEXTE = (
    ((errno.ENOSPC, errno.EDQUOT), lambda n, o: "Auf dem Datenträger ist nicht genug Platz."),
    ((errno.EACCES, errno.EPERM), lambda n, o: f"Keine Schreibrechte für „{n}“ im Ordner „{o}“."),
    ((errno.EROFS,), lambda n, o: "Der Datenträger ist schreibgeschützt."),
    ((errno.ENAMETOOLONG,), lambda n, o: "Der Dateiname oder Pfad ist zu lang."),
    ((errno.ENOENT, errno.ENOTDIR), lambda n, o: f"Der Ordner „{o}“ existiert nicht (mehr)."),
    ((errno.EISDIR,), lambda n, o: f"„{n}“ ist ein Ordner."),
    ((errno.EBUSY, errno.ETXTBSY), lambda n, o: f"„{n}“ ist gerade in Benutzung."),
    ((errno.EIO,), lambda n, o: "Ein-/Ausgabefehler beim Schreiben. Bitte den Datenträger prüfen."),
)


def fehlertext(e: BaseException, path: str, vorhanden: bool) -> str:
    """Verständliche Meldung für einen Fehler beim Schreiben."""
    name = os.path.basename(path) or path
    ordner = os.path.dirname(path) or "."
    nr = getattr(e, "errno", None)
    if isinstance(e, ValueError):
        text = f"Der Dateiname „{name}“ ist ungültig."
    else:
        text = next((f(name, ordner) for nummern, f in _FEHLERTEXTE if nr in nummern),
                    f"Speichern nicht möglich: {getattr(e, 'strerror', None) or e}")
    return text + (" Die bisherige Datei ist unverändert." if vorhanden else "")


def _umask() -> int:
    try:
        with open("/proc/self/status", encoding="ascii") as fh:
            for zeile in fh:
                if zeile.startswith("Umask:"):
                    return int(zeile.split()[1], 8)
    except (OSError, ValueError):
        pass
    return 0o022


def _fsync_datei(path: str) -> None:
    fd = dateisystem.fsync_oeffnen(path)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _fsync_ordner(ordner: str) -> None:
    try:
        fd = dateisystem.ordner_oeffnen(ordner)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:                                      # manche Netz-/FUSE-Laufwerke kennen kein fsync auf Ordnern
        pass
    finally:
        os.close(fd)


def _rest_muster(real: str) -> str:
    return os.path.join(os.path.dirname(real), "." + glob.escape(os.path.basename(real)[:100]) + ".lunivo-*.tmp")


def _reste_aufraeumen(real: str) -> None:
    """Entfernt eigene Temp-Reste früherer, abgebrochener Speichervorgänge derselben Datei."""
    grenze = time.time() - REST_ALTER_S
    for rest in glob.glob(_rest_muster(real)):
        try:
            if os.path.getmtime(rest) < grenze:
                os.remove(rest)
        except OSError:
            pass


# ---- Sperre ----------------------------------------------------------------------------------------------------------------------
@contextmanager
def sperre(path: str):
    """Verhindert, dass dieselbe Datei gleichzeitig zweimal gespeichert wird (im Programm und zwischen Lunivo-Fenstern)."""
    real = ziel(path)
    name = os.path.basename(real)
    with _im_programm_sperre:
        if real in _im_programm:
            raise DocumentIOError(f"„{name}“ wird gerade schon gespeichert. Bitte kurz warten und erneut speichern.")
        _im_programm.add(real)
    fd = None
    try:
        try:
            fd = _sperre.sperre_oeffnen(os.path.join(_sperre.sperr_ordner(),
                                                     hashlib.sha256(real.encode("utf-8", "surrogateescape")).hexdigest() + ".lock"))
        except _sperre.SperreBelegt as e:
            raise DocumentIOError(f"„{name}“ wird gerade von einem anderen Lunivo-Fenster gespeichert. "
                                  "Bitte kurz warten und erneut speichern.") from e
        except OSError:                                  # ohne Sperrordner trotzdem speichern; die Sperre im Programm gilt weiter
            fd = None
        yield real
    finally:
        if fd is not None:
            _sperre.sperre_freigeben(fd)
        with _im_programm_sperre:
            _im_programm.discard(real)


# ---- Sicherungskopien ------------------------------------------------------------------------------------------------------------
def sicherungs_ordner() -> str:
    return os.path.join(data_dir(), "sicherungen")


def _dokument_ordner(real: str) -> str:
    return os.path.join(sicherungs_ordner(), hashlib.sha256(real.encode("utf-8", "surrogateescape")).hexdigest()[:16])


def sicherungskopie(real: str) -> str | None:
    """Kopiert die bisherige Fassung in den Sicherungsordner und räumt alte Kopien weg. → Pfad der Kopie."""
    if not os.path.isfile(real):
        return None
    ordner = _dokument_ordner(real)
    os.makedirs(ordner, mode=0o700, exist_ok=True)
    with open(os.path.join(ordner, "pfad.txt"), "w", encoding="utf-8", errors="surrogateescape") as fh:
        fh.write(real + "\n")
    kopie = os.path.join(ordner, f"{time.strftime('%Y%m%d-%H%M%S')}-{time.time_ns() % 1_000_000_000:09d}-{os.path.basename(real)}")
    shutil.copy2(real, kopie)
    sicherungen_aufraeumen(ordner)
    return kopie


def sicherungen(path: str) -> list[str]:
    """Sicherungskopien einer Datei, neueste zuerst."""
    ordner = _dokument_ordner(ziel(path))
    if not os.path.isdir(ordner):
        return []
    return sorted((os.path.join(ordner, f) for f in os.listdir(ordner) if f != "pfad.txt"), reverse=True)


def _ordner_aufraeumen(ordner: str, grenze: float) -> None:
    """Zu viele oder zu alte Kopien eines Dokument-Ordners entfernen; ein leerer Ordner verschwindet."""
    if not os.path.isdir(ordner):
        return
    kopien = sorted((f for f in os.listdir(ordner) if f != "pfad.txt"), reverse=True)
    for i, f in enumerate(kopien):
        p = os.path.join(ordner, f)
        try:
            if i >= SICHERUNGEN_JE_DOKUMENT or os.path.getmtime(p) < grenze:
                os.remove(p)
        except OSError:
            pass
    try:
        if not [f for f in os.listdir(ordner) if f != "pfad.txt"]:
            shutil.rmtree(ordner)
    except OSError:
        pass


def sicherungen_aufraeumen(nur_ordner: str | None = None) -> None:
    """Hält je Dokument höchstens SICHERUNGEN_JE_DOKUMENT Kopien und entfernt Kopien älter als SICHERUNG_TAGE."""
    wurzel = sicherungs_ordner()
    if not os.path.isdir(wurzel):
        return
    grenze = time.time() - SICHERUNG_TAGE * 86400
    ordner_liste = [nur_ordner] if nur_ordner else [os.path.join(wurzel, d) for d in os.listdir(wurzel)]
    for ordner in ordner_liste:
        _ordner_aufraeumen(ordner, grenze)


# ---- Strukturprüfung -------------------------------------------------------------------------------------------------------------
def _defekt(grund: str) -> DocumentIOError:
    return DocumentIOError(f"Die geschriebene Datei ist unvollständig oder beschädigt ({grund}).")


def _zip_pruefen(path: str, pflicht: tuple[str, ...]) -> zipfile.ZipFile:
    try:
        z = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, OSError) as e:
        raise _defekt("kein gültiges ZIP-Paket") from e
    try:
        kaputt = z.testzip()
    except Exception as e:                               # zlib.error u. a. bei abgeschnittenen Daten
        z.close()
        raise _defekt("Prüfsumme im Paket falsch") from e
    if kaputt is not None:
        z.close()
        raise _defekt(f"Prüfsumme von „{kaputt}“ falsch")
    namen = set(z.namelist())
    for n in pflicht:
        if n not in namen:
            z.close()
            raise _defekt(f"„{n}“ fehlt")
        if n.endswith(".xml"):
            try:
                ElementTree.fromstring(z.read(n))
            except ElementTree.ParseError as e:
                z.close()
                raise _defekt(f"„{n}“ ist kein gültiges XML") from e
    return z


def _txt_pruefen(path: str) -> None:
    try:
        with open(path, "rb") as fh:
            fh.read().decode("utf-8")
    except UnicodeDecodeError as e:
        raise _defekt("kein gültiges UTF-8") from e


def _odt_pruefen(path: str) -> None:
    z = _zip_pruefen(path, ("content.xml", "META-INF/manifest.xml"))
    try:
        erster = z.infolist()[0]
        if erster.filename != "mimetype" or erster.compress_type != zipfile.ZIP_STORED \
                or z.read("mimetype").strip() != ODT_MIMETYPE:
            raise _defekt("„mimetype“ fehlt am Anfang oder ist falsch")
    finally:
        z.close()


def _rtf_pruefen(path: str) -> None:
    with open(path, "rb") as fh:
        daten = fh.read()
    if not daten.startswith(b"{\\rtf"):
        raise _defekt("RTF-Kopf fehlt")
    tiefe, i = 0, 0
    while i < len(daten):
        c = daten[i]
        if c == 0x5C:                                # Backslash: das nächste Zeichen ist maskiert
            i += 2
            continue
        if c == 0x7B:
            tiefe += 1
        elif c == 0x7D:
            tiefe -= 1
            if tiefe < 0:
                break
        i += 1
    if tiefe != 0:
        raise _defekt("Klammern nicht ausgeglichen")


def _pdf_pruefen(kopf: bytes, ende: bytes) -> None:
    if not kopf.startswith(b"%PDF-"):
        raise _defekt("PDF-Kopf fehlt")
    if b"%%EOF" not in ende:
        raise _defekt("PDF-Abschluss fehlt")


def _docx_pruefen(path: str, kopf: bytes) -> None:
    if kopf == OLE_KOPF:                             # mit Kennwort verschlüsselt: OLE-Container statt ZIP
        return
    _zip_pruefen(path, ("[Content_Types].xml", "word/document.xml")).close()


def _kopf_ende_lesen(path: str) -> tuple[int, bytes, bytes]:
    """(Größe, erste 8 Bytes, letztes KiB) der Datei."""
    try:
        groesse = os.path.getsize(path)
        with open(path, "rb") as fh:
            kopf = fh.read(8)
            fh.seek(max(0, groesse - 1024))
            ende = fh.read()
    except OSError as e:
        raise _defekt(os.strerror(e.errno) if e.errno else str(e)) from e
    return groesse, kopf, ende


def pruefe_format(path: str, endung: str) -> None:
    """Strukturprüfung der geschriebenen Datei. Wirft DocumentIOError, wenn sie nicht vollständig oder nicht gültig ist.

    Geprüft wird der Aufbau, den das Format verlangt — keine vollständige Schemaprüfung nach ECMA-376 bzw. ODF."""
    endung = endung.lower()
    groesse, kopf, ende = _kopf_ende_lesen(path)
    if endung == ".txt":
        _txt_pruefen(path)
        return
    if groesse == 0:
        raise _defekt("die Datei ist leer")
    if endung in (".docx", ".dotx", ".docm"):
        _docx_pruefen(path, kopf)
    elif endung == ".odt":
        _odt_pruefen(path)
    elif endung == ".rtf":
        _rtf_pruefen(path)
    elif endung == ".pdf":
        _pdf_pruefen(kopf, ende)


# ---- Schreiben -------------------------------------------------------------------------------------------------------------------
def _ziel_pruefen(path: str) -> tuple[str, str, str, bool]:
    """Vor dem Schreiben: (Zieldatei, Ordner, Endung-Vorgabe, vorhanden); wirft DocumentIOError bei ungültigem Ziel."""
    try:
        real = ziel(path)
    except ValueError as e:
        raise DocumentIOError(fehlertext(e, path, False)) from e
    ordner = os.path.dirname(real) or "."
    if os.path.isdir(real):
        raise DocumentIOError(fehlertext(OSError(errno.EISDIR, "Ordner"), real, False))
    if not os.path.isdir(ordner):
        raise DocumentIOError(fehlertext(OSError(errno.ENOENT, "fehlt"), real, False))
    return real, ordner, os.path.splitext(real)[1].lower(), os.path.lexists(real)


def _stand_pruefen(real: str, erwartet) -> os.stat_result | None:
    """Zustand der Zieldatei in der Sperre; weicht er vom erwarteten Stand ab: SchreibKonflikt."""
    try:
        alt = os.stat(real)                          # erst jetzt, in der Sperre: der Zustand von vorhin kann überholt sein
    except OSError:
        alt = None
    if erwartet is not UNGEPRUEFT and ((alt.st_mtime_ns, alt.st_size) if alt else None) != erwartet:
        raise SchreibKonflikt(f"„{os.path.basename(real)}“ wurde seit dem Öffnen oder letzten Speichern von einem anderen Programm "
                              f"{'geändert' if alt is not None else 'gelöscht oder verschoben'}. Es wurde nichts überschrieben.")
    return alt


def _tmp_entfernen(tmp: str | None) -> None:
    if tmp is not None:
        try:
            os.remove(tmp)
        except OSError:
            pass


def schreiben(path: str, erzeugen: Callable[[str], T], *, endung: str | None = None, sicherung: bool = True, erwartet=UNGEPRUEFT) -> T:
    """Schreibt eine Datei sicher: `erzeugen(temp_pfad)` legt die neue Fassung an, der Rest geschieht hier.

    `endung` bestimmt die Strukturprüfung (Vorgabe: Endung des Ziels). → Rückgabewert von `erzeugen`.

    `erwartet`: der ``stand()`` der Zieldatei, den der Aufrufer zuletzt gesehen hat (None = die Datei soll noch nicht da sein). Der Vergleich
    geschieht *innerhalb der Sperre* und unmittelbar vor dem Ersetzen; weicht der Stand ab, wirft die Funktion ``SchreibKonflikt`` und die
    Zieldatei bleibt unberührt."""
    real, ordner, ziel_endung, vorhanden = _ziel_pruefen(path)
    endung = (endung or ziel_endung).lower()
    with sperre(real):
        _reste_aufraeumen(real)
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(dir=ordner, prefix="." + os.path.basename(real)[:100] + ".lunivo-", suffix=".tmp")
            os.close(fd)
            ergebnis = erzeugen(tmp)
            _fsync_datei(tmp)
            pruefe_format(tmp, endung)
            alt = _stand_pruefen(real, erwartet)
            vorhanden = alt is not None
            os.chmod(tmp, stat.S_IMODE(alt.st_mode) if alt else 0o666 & ~_umask())
            if sicherung and alt is not None:
                try:
                    sicherungskopie(real)
                except OSError:                          # eine fehlende Sicherungskopie verhindert das Speichern nicht
                    pass
            os.replace(tmp, real)
            tmp = None
            _fsync_ordner(ordner)
            return ergebnis
        except (OSError, ValueError) as e:
            raise DocumentIOError(fehlertext(e, real, vorhanden)) from e
        except SchreibKonflikt:
            raise
        except DocumentIOError as e:
            if vorhanden and "unverändert" not in str(e):
                raise DocumentIOError(f"{e} Die bisherige Datei ist unverändert.") from e
            raise
        finally:
            _tmp_entfernen(tmp)


def bytes_schreiben(path: str, daten: bytes, *, endung: str | None = None, sicherung: bool = True, erwartet=UNGEPRUEFT) -> None:
    def erzeugen(tmp: str) -> None:
        with open(tmp, "wb") as fh:
            fh.write(daten)
    schreiben(path, erzeugen, endung=endung, sicherung=sicherung, erwartet=erwartet)
