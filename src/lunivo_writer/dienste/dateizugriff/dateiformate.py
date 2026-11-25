"""Dateiformat-Hilfen ohne Qt: Filtertexte, Kopfprüfung, Kennwort (Ent-/Verschlüsselung), DOTX/DOCM als DOCX, sicheres Schreiben fertiger DOCX-Bytes.

Aus ``datei_dienst`` herausgelöst, damit Laden und Speichern des Dokuments (``modell_laden``, ``modell_speichern``) keinerlei Qt-Abhängigkeit haben."""
from __future__ import annotations

import logging
import os

from lunivo_writer.dienste.dateizugriff import sicher_schreiben
from lunivo_writer.core.dokument.bericht import DocumentIOError, IOReport

_log = logging.getLogger("lunivo.dateien")
OPEN_FILTER = ("Dokumente (*.docx *.dotx *.docm *.odt *.fodt *.rtf *.txt);;DOCX-Dokument (*.docx);;OpenDocument-Text (*.odt);;"
               "Rich Text (*.rtf);;Textdatei (*.txt);;Alle Dateien (*)")
# Alle Formate liest und schreibt Lunivo selbst — kein fremdes Programm im Hintergrund.
NICHT_UNTERSTUETZT = {".doc": "Word 97–2003 (.doc)", ".dot": "Word-97–2003-Vorlage (.dot)", ".wps": "Textformat (.wps)"}
SAVE_FILTERS = {
    ".docx": "DOCX-Dokument (*.docx)",
    ".txt": "Textdatei (*.txt)",
    ".odt": "OpenDocument-Text (*.odt)",
    ".rtf": "Rich Text (*.rtf)",
}
PDF_FILTER = "PDF-Dokument (*.pdf)"


def endung_zum_filter(filter_text: str) -> str | None:
    """Filtertext aus dem Speichern-Fenster → Endung (z. B. „OpenDocument-Text (*.odt)“ → „.odt“)."""
    if filter_text == PDF_FILTER:
        return ".pdf"
    return next((e for e, f in SAVE_FILTERS.items() if f == filter_text), None)




def ext(path: str) -> str:
    return os.path.splitext(path)[1].lower()


def _verschluesselt(path: str) -> bool:
    try:
        with open(path, "rb") as fh:
            return fh.read(4) == b"\xd0\xcf\x11\xe0"
    except OSError:
        return False


def _entschluesseln(path: str, kennwort: str | None, ziel: str) -> None:
    from lunivo_writer.core.dokument.bericht import PasswortNoetig
    if not kennwort:
        raise PasswortNoetig()
    try:
        import msoffcrypto
    except ImportError as ex:
        raise DocumentIOError("Zum Öffnen kennwortgeschützter Dokumente wird das Paket „msoffcrypto-tool“ gebraucht "
                              "(pip install msoffcrypto-tool).") from ex
    try:
        with open(path, "rb") as fh, open(ziel, "wb") as out:
            f = msoffcrypto.OfficeFile(fh)
            f.load_key(password=kennwort)
            f.decrypt(out)
    except Exception as ex:                      # falsches Kennwort oder beschädigt
        _log.warning("Entschlüsseln fehlgeschlagen: %s", ex)
        raise PasswortNoetig(falsch=True) from ex


_MAGIC = {".odt": b"PK", ".dotx": b"PK", ".docm": b"PK", ".fodt": b"<?xml", ".rtf": b"{\\rtf"}


def _kopf_pruefen(path: str, e: str) -> None:
    """Ein falsch benanntes oder kaputtes Dokument wird als solches gemeldet, nicht „irgendwie“ geöffnet."""
    soll = _MAGIC.get(e)
    if not soll:
        return
    try:
        with open(path, "rb") as fh:
            kopf = fh.read(len(soll))
    except OSError as ex:
        raise DocumentIOError(f"Datei nicht lesbar: {ex.strerror or ex}") from ex
    if kopf != soll:
        raise DocumentIOError(f"Die Datei ist kein gültiges {e[1:].upper()}-Dokument oder beschädigt.")


def save_docx_daten(path: str, data: bytes, report: IOReport, meta: dict | None = None, sicherung: bool = True,
                    erwartet=sicher_schreiben.UNGEPRUEFT) -> IOReport:
    """Schreibt bereits gebaute DOCX-Bytes mit demselben Kennwort- und sicheren Austauschweg wie ``save``."""
    kw = (meta or {}).get("kennwort")
    if kw:
        data = _verschluesseln(data, kw)
    sicher_schreiben.bytes_schreiben(path, data, endung=".docx", sicherung=sicherung, erwartet=erwartet)
    return report


_DOCX_HAUPTTEIL = b"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"


def _als_docx(path: str, ziel: str) -> str:
    """DOTX (Vorlage) und DOCM (mit Makros) sind DOCX-Pakete mit anderem Inhaltstyp des Hauptteils; für den DOCX-Leser wird nur
    dieser Eintrag umgeschrieben und das Makroprojekt weggelassen."""
    import re
    import zipfile
    try:
        with zipfile.ZipFile(path) as z, zipfile.ZipFile(ziel, "w", zipfile.ZIP_DEFLATED) as aus:
            for info in z.infolist():
                if info.filename.lower().endswith("vbaproject.bin") or info.filename.lower().endswith("vbadata.xml"):
                    continue
                daten = z.read(info.filename)
                if info.filename == "[Content_Types].xml":
                    daten = re.sub(rb'application/vnd\.(?:openxmlformats-officedocument\.wordprocessingml\.template|'
                                   rb'ms-word\.(?:document|template)\.macroEnabled)(?:\.main)?\+xml', _DOCX_HAUPTTEIL, daten)
                aus.writestr(info, daten)
    except (zipfile.BadZipFile, OSError, KeyError) as ex:
        raise DocumentIOError("Die Datei ist kein gültiges DOCX-Dokument oder beschädigt.") from ex
    return ziel


def _verschluesseln(data: bytes, kennwort: str) -> bytes:
    try:
        import msoffcrypto
    except ImportError as ex:
        raise DocumentIOError("Zum Verschlüsseln wird das Paket „msoffcrypto-tool“ gebraucht.") from ex
    import io
    out = io.BytesIO()
    try:
        msoffcrypto.OfficeFile(io.BytesIO(data)).encrypt(kennwort, out)
    except Exception as ex:
        raise DocumentIOError(f"Das Dokument konnte nicht verschlüsselt werden: {ex}") from ex
    return out.getvalue()
