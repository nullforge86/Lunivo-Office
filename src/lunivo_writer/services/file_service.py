"""Eine Stelle für alle Dateiformate: laden und speichern nach Endung."""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass

from PySide6.QtGui import QFont, QTextBlockFormat, QTextCursor, QTextDocument

from lunivo_writer.models.page import PageSettings
from lunivo_writer.services import docx_reader, docx_writer
from lunivo_writer.models.report import DocumentIOError, IOReport

OPEN_FILTER = ("Dokumente (*.docx *.dotx *.docm *.odt *.fodt *.rtf *.txt);;Word-Dokument (*.docx);;OpenDocument-Text (*.odt);;"
               "Rich Text (*.rtf);;Textdatei (*.txt);;Alle Dateien (*)")
# Alle Formate liest und schreibt Lunivo selbst — kein fremdes Programm im Hintergrund.
NICHT_UNTERSTUETZT = {".doc": "Word 97–2003 (.doc)", ".dot": "Word-97–2003-Vorlage (.dot)", ".wps": "Microsoft Works (.wps)"}
SAVE_FILTERS = {
    ".docx": "Word-Dokument (*.docx)",
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


def ext(path: str) -> str:
    return os.path.splitext(path)[1].lower()


def _verschluesselt(path: str) -> bool:
    try:
        with open(path, "rb") as fh:
            return fh.read(4) == b"\xd0\xcf\x11\xe0"
    except OSError:
        return False


def _entschluesseln(path: str, kennwort: str | None, ziel: str) -> None:
    from lunivo_writer.models.report import PasswortNoetig
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
        raise PasswortNoetig(falsch=True) from ex


def load(path: str, kennwort: str | None = None) -> Loaded:
    if not os.path.isfile(path):
        raise DocumentIOError(f"Die Datei „{path}“ existiert nicht.")
    e = ext(path)
    if e == ".docx":
        if _verschluesselt(path):
            with tempfile.TemporaryDirectory(prefix="lunivo-") as tmp:
                klar = os.path.join(tmp, "klar.docx")
                _entschluesseln(path, kennwort, klar)
                doc, page, meta, rep = docx_reader.read_docx(klar)
            meta["kennwort"] = kennwort
            return Loaded(doc, page, meta, rep)
        doc, page, meta, rep = docx_reader.read_docx(path)
        return Loaded(doc, page, meta, rep)
    if e in (".txt", ".text", ""):
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
    if e in (".odt", ".fodt", ".rtf"):
        _kopf_pruefen(path, e)
        if e == ".rtf":
            from lunivo_writer.services.rtf_reader import read_rtf
            doc, page, meta, rep = read_rtf(path)
        else:
            from lunivo_writer.services import odt_reader
            doc, page, meta, rep = (odt_reader.read_odt if e == ".odt" else odt_reader.read_fodt)(path)
        return Loaded(doc, page, meta, rep)
    if e in (".dotx", ".docm"):
        _kopf_pruefen(path, e)
        with tempfile.TemporaryDirectory(prefix="lunivo-") as tmp:
            doc, page, meta, rep = docx_reader.read_docx(_als_docx(path, os.path.join(tmp, "dokument.docx")))
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
        it = b.begin()
        while not it.atEnd():
            cf = it.fragment().charFormat()
            if cf.isImageFormat() or cf.fontWeight() > 400 or cf.fontItalic() or cf.underlineStyle() != cf.UnderlineStyle.NoUnderline:
                return True
            it += 1
        b = b.next()
    return doc.rootFrame().childFrames() != []


def save(path: str, doc: QTextDocument, page: PageSettings, meta: dict | None = None, sicherung: bool = True) -> IOReport:
    """Speichert nach Endung über den sicheren Schreibweg (``sicher_schreiben``): Temp-Datei, Prüfung, Sicherungskopie der
    Vorfassung (abschaltbar mit `sicherung=False`), atomares Ersetzen. Jedes Format schreibt Lunivo selbst."""
    from lunivo_writer.editor import lese_zeilenluft
    from lunivo_writer.services import sicher_schreiben
    if lese_zeilenluft.aktiv(doc):                       # der Zusatzabstand der Lesehilfe gehört nicht in die Datei
        doc = lese_zeilenluft.bereinigte_kopie(doc)
    e = ext(path)
    if e == ".docx":
        data, rep = docx_writer.docx_daten(doc, page, meta)
        kw = (meta or {}).get("kennwort")
        if kw:
            data = _verschluesseln(data, kw)
        sicher_schreiben.bytes_schreiben(path, data, endung=".docx", sicherung=sicherung)
        return rep
    rep = IOReport()
    if e == ".txt":
        if _has_rich_content(doc):
            rep.warn("Als Textdatei gehen Formatierung, Listen, Tabellen und Bilder verloren.")
        if not page.header.is_empty() or not page.footer.is_empty():
            rep.warn("Kopf- und Fußzeile werden in der Textdatei nicht gespeichert.")
        sicher_schreiben.bytes_schreiben(path, doc.toPlainText().replace("\u2028", "\n").encode("utf-8"), sicherung=sicherung)
        return rep
    if e in (".odt", ".rtf"):
        if e == ".odt":
            from lunivo_writer.services.odt_writer import odt_daten as daten_bauen
        else:
            from lunivo_writer.services.rtf_writer import rtf_daten as daten_bauen
        data, rep = daten_bauen(doc, page, meta)
        sicher_schreiben.bytes_schreiben(path, data, endung=e, sicherung=sicherung)
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
        raise DocumentIOError("Die Datei ist kein gültiges Word-Dokument oder beschädigt.") from ex
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
