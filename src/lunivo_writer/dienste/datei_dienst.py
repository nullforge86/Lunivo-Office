"""Eine Stelle für alle Dateiformate: laden und speichern nach Endung."""
from __future__ import annotations

import os
import tempfile
import logging
from dataclasses import dataclass

from PySide6.QtGui import QFont, QTextBlockFormat, QTextCursor, QTextDocument

from lunivo_writer.editor.text.fragmente import absatz_fragmente
from lunivo_writer.modelle.seite import PageSettings
from lunivo_writer.dienste import docx_leser, docx_schreiber
from lunivo_writer.dienste import sicher_schreiben
from lunivo_writer.modelle.bericht import DocumentIOError, IOReport
from lunivo_writer.core.document import Document

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


@dataclass
class Loaded:
    doc: QTextDocument
    page: PageSettings
    meta: dict
    report: IOReport
    modell: Document | None = None


def ext(path: str) -> str:
    return os.path.splitext(path)[1].lower()


def _verschluesselt(path: str) -> bool:
    try:
        with open(path, "rb") as fh:
            return fh.read(4) == b"\xd0\xcf\x11\xe0"
    except OSError:
        return False


def _entschluesseln(path: str, kennwort: str | None, ziel: str) -> None:
    from lunivo_writer.modelle.bericht import PasswortNoetig
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


def _docx_lesen(path: str):
    """DOCX → Qt-Dokument, Seiteneinrichtung, Metadaten, Bericht und optional das bereits gelesene Modell.
    Was der Modell-Leser noch nicht kann (Tabellen mit Textmaß, Felder mit Nachformatierung, Positionen), liest ``docx_leser.read_docx``."""
    from lunivo_writer.dienste import docx_modell_leser
    from lunivo_writer.adapter.qt.dokument import document_to_qt
    gelesen = docx_modell_leser.lese_docx_modell(path)
    if gelesen is None:
        return (*docx_leser.read_docx(path), None)
    modell, page, meta, rep = gelesen
    return document_to_qt(modell), page, meta, rep, modell


def _docx_laden(path: str, kennwort: str | None) -> Loaded:
    if _verschluesselt(path):
        with tempfile.TemporaryDirectory(prefix="lunivo-") as tmp:
            klar = os.path.join(tmp, "klar.docx")
            _entschluesseln(path, kennwort, klar)
            doc, page, meta, rep, modell = _docx_lesen(klar)
        meta["kennwort"] = kennwort
        return Loaded(doc, page, meta, rep, modell)
    doc, page, meta, rep, modell = _docx_lesen(path)
    return Loaded(doc, page, meta, rep, modell)


def _txt_laden(path: str) -> Loaded:
    from lunivo_writer.dienste.import_grenzen import pruefe_dateigroesse
    pruefe_dateigroesse(path, "TXT")
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as ex:
        raise DocumentIOError(f"Datei nicht lesbar: {ex.strerror or ex}") from ex
    for enc in ("utf-8-sig", "cp1252"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw.decode("latin-1")
    doc = QTextDocument()
    doc.setDocumentMargin(0)
    f = QFont("Liberation Sans")
    f.setPointSizeF(11)
    doc.setDefaultFont(f)
    QTextCursor(doc).insertText(text.replace("\r\n", "\n"))
    doc.setModified(False)
    return Loaded(doc, PageSettings(), {}, IOReport())


def load(path: str, kennwort: str | None = None) -> Loaded:
    if not os.path.isfile(path):
        raise DocumentIOError(f"Die Datei „{path}“ existiert nicht.")
    e = ext(path)
    if e == ".docx":
        return _docx_laden(path, kennwort)
    if e in (".txt", ".text", ""):
        return _txt_laden(path)
    if e in (".odt", ".fodt", ".rtf"):
        _kopf_pruefen(path, e)
        if e == ".rtf":
            from lunivo_writer.dienste.rtf import read_rtf
            doc, page, meta, rep = read_rtf(path)
        else:
            from lunivo_writer.dienste import odt_leser
            doc, page, meta, rep = (odt_leser.read_odt if e == ".odt" else odt_leser.read_fodt)(path)
        return Loaded(doc, page, meta, rep)
    if e in (".dotx", ".docm"):
        _kopf_pruefen(path, e)
        with tempfile.TemporaryDirectory(prefix="lunivo-") as tmp:
            doc, page, meta, rep = docx_leser.read_docx(_als_docx(path, os.path.join(tmp, "dokument.docx")))
        if e == ".docm":
            rep.warn("Makros aus der DOCM-Datei werden nicht ausgeführt und beim Speichern nicht übernommen.")
        return Loaded(doc, page, meta, rep)
    if e in NICHT_UNTERSTUETZT:
        raise DocumentIOError(f"Das alte Format {NICHT_UNTERSTUETZT[e]} wird nicht mehr unterstützt. Bitte die Datei im "
                              "ursprünglichen Programm als DOCX speichern und dann in Lunivo öffnen.")
    raise DocumentIOError(
        f"Das Format „{e or 'ohne Endung'}“ kann nicht geöffnet werden. Unterstützt: DOCX, ODT, RTF, TXT.")


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


def _has_rich_content(doc: QTextDocument) -> bool:
    b = doc.firstBlock()
    while b.isValid():
        if b.textList() is not None or b.blockFormat().headingLevel():
            return True
        for f in absatz_fragmente(b):
            cf = f.charFormat()
            if cf.isImageFormat() or cf.fontWeight() > 400 or cf.fontItalic() or cf.underlineStyle() != cf.UnderlineStyle.NoUnderline:
                return True
        b = b.next()
    return doc.rootFrame().childFrames() != []


def save(path: str, doc: QTextDocument, page: PageSettings, meta: dict | None = None, sicherung: bool = True, erwartet=sicher_schreiben.UNGEPRUEFT) -> IOReport:
    """Speichert nach Endung über den sicheren Schreibweg (``sicher_schreiben``): Temp-Datei, Prüfung, Sicherungskopie der
    Vorfassung (abschaltbar mit `sicherung=False`), atomares Ersetzen. Jedes Format schreibt Lunivo selbst."""
    from lunivo_writer.editor.seite import lese_zeilenluft
    if lese_zeilenluft.aktiv(doc):                       # der Zusatzabstand der Lesehilfe gehört nicht in die Datei
        doc = lese_zeilenluft.bereinigte_kopie(doc)
    from lunivo_writer.editor.seite import querblatt
    if querblatt.hat_zusatz(doc):                        # ebenso der Einzug, mit dem der Editor verschieden große Blätter zeigt
        doc = querblatt.bereinigte_kopie(doc)
    e = ext(path)
    if e == ".docx":
        data, rep = docx_schreiber.docx_daten(doc, page, meta)
        kw = (meta or {}).get("kennwort")
        if kw:
            data = _verschluesseln(data, kw)
        sicher_schreiben.bytes_schreiben(path, data, endung=".docx", sicherung=sicherung, erwartet=erwartet)
        return rep
    rep = IOReport()
    if e == ".txt":
        if _has_rich_content(doc):
            rep.warn("Als Textdatei gehen Formatierung, Listen, Tabellen und Bilder verloren.")
        if not page.header.is_empty() or not page.footer.is_empty():
            rep.warn("Kopf- und Fußzeile werden in der Textdatei nicht gespeichert.")
        sicher_schreiben.bytes_schreiben(path, doc.toPlainText().replace("\u2028", "\n").encode("utf-8"), sicherung=sicherung, erwartet=erwartet)
        return rep
    if e in (".odt", ".rtf"):
        if e == ".odt":
            from lunivo_writer.dienste.odt_schreiber import odt_daten as daten_bauen
        else:
            from lunivo_writer.dienste.rtf_schreiber import rtf_daten as daten_bauen
        data, rep = daten_bauen(doc, page, meta)
        sicher_schreiben.bytes_schreiben(path, data, endung=e, sicherung=sicherung, erwartet=erwartet)
        return rep
    raise DocumentIOError(f"Das Format „{e}“ kann nicht gespeichert werden.")


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
