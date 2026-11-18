"""RTF-Import: ``read_rtf`` — Datei prüfen, zerlegen, QTextDocument, Seiteneinstellungen und Kopf-/Fußzeilen übernehmen."""
from __future__ import annotations

from lunivo_writer.modelle.seite import HeaderFooter
from lunivo_writer.modelle.bericht import DocumentIOError
from lunivo_writer.dienste.rtf.zerleger import Zerleger

GRENZE_BYTES = 512 * 1024 * 1024


def _daten_lesen(path: str) -> bytes:
    try:
        with open(path, "rb") as fh:
            daten = fh.read(GRENZE_BYTES + 1)
    except OSError as e:
        raise DocumentIOError(f"Datei nicht lesbar: {e.strerror or e}") from e
    if len(daten) > GRENZE_BYTES:
        raise DocumentIOError("Die RTF-Datei ist zu groß, um sie sicher zu öffnen.")
    if not daten.lstrip().startswith(b"{\\rtf"):
        raise DocumentIOError("Die Datei ist kein gültiges RTF-Dokument oder beschädigt.")
    return daten


def _dokument_bauen(z: Zerleger) -> "QTextDocument":
    from PySide6.QtGui import QFont, QTextCursor, QTextDocument
    from lunivo_writer.dienste.rtf.aufbau import Bauer
    doc = QTextDocument()
    doc.setDocumentMargin(0)
    df = QFont(z.schriften.get(z.standard_schrift) or "Liberation Serif")
    df.setPointSizeF(12.0)
    doc.setDefaultFont(df)
    Bauer(z, doc).teile(z.haupt.teile, QTextCursor(doc))
    return doc


def _seite_fertig(z: Zerleger):
    from lunivo_writer.dienste.rtf.aufbau import kopf_fuss_text
    page = z.seite
    for schl, (ziel, _a) in z.kopf_fuss.items():
        if "?" in schl:                                       # linke/rechte Seiten: nur, wenn es keine allgemeine gibt
            basis = schl.split("?")[0]
            if basis in z.kopf_fuss:
                continue
            schl = basis
        setattr(page, schl, kopf_fuss_text(ziel, z.report))
    page.diff_first = z.titel_erste
    if not z.titel_erste:
        page.first_header, page.first_footer = HeaderFooter(), HeaderFooter()
    return page


def read_rtf(path: str):
    """→ (QTextDocument, PageSettings, meta-dict, IOReport). Wirft DocumentIOError."""
    z = Zerleger(_daten_lesen(path))
    z.run()
    doc = _dokument_bauen(z)
    page = _seite_fertig(z)
    from lunivo_writer.editor.dokument.zusatz import leere_meta
    meta = dict(z.meta)
    meta.update(leere_meta())
    doc.setModified(False)
    return doc, page, meta, z.report
