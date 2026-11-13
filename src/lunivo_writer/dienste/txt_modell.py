"""Qt-freie Ein- und Ausgabe einfacher Textdateien über ``core.document``."""
from __future__ import annotations

from lunivo_writer.core.document import CharacterFormat, Document, Paragraph, ParagraphFormat, Section, TextRun
from lunivo_writer.dienste.import_grenzen import pruefe_dateigroesse
from lunivo_writer.modelle.bericht import DocumentIOError
from lunivo_writer.modelle.seite import PageSettings


def textdatei_lesen(path: str) -> str:
    """UTF-8 (mit BOM), Windows-1252 oder Latin-1 wie der bisherige Textleser dekodieren."""
    pruefe_dateigroesse(path, "TXT")
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as ex:
        raise DocumentIOError(f"Datei nicht lesbar: {ex.strerror or ex}") from ex
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc).replace("\r\n", "\n")
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1").replace("\r\n", "\n")


def modell_laden(path: str) -> tuple[Document, PageSettings]:
    """Eine Textdatei direkt als Modell mit denselben Standardwerten wie der Qt-TXT-Leser laden."""
    text = textdatei_lesen(path)
    grund = CharacterFormat({"FontFamilies": ("Liberation Sans",), "FontPointSize": 11.0}, family="Liberation Sans", size_pt=11.0)
    bloecke = [Paragraph(ParagraphFormat(), [TextRun(teil, CharacterFormat())] if teil else []) for teil in text.split("\n")]
    seite = PageSettings()
    return Document([Section("naechste", seite, bloecke)], default_format=grund, document_margin=0.0), seite


def text_aus_modell(modell: Document) -> tuple[bytes, bool] | None:
    """Einfache Absätze als UTF-8 serialisieren; ``None`` signalisiert komplexe Blöcke für den vollständigen Qt-Rückfall."""
    absatztexte = []
    reich = (bool(modell.lists) or len(modell.sections) > 1 or modell.document_margin != 0.0)
    reich |= any(abschnitt.kind != "naechste" for abschnitt in modell.sections)
    for abschnitt in modell.sections:
        for block in abschnitt.content:
            if not isinstance(block, Paragraph) or any(not isinstance(lauf, TextRun) for lauf in block.runs):
                return None
            absatztexte.append("".join(lauf.text for lauf in block.runs).replace("\u2028", "\n"))
            f = block.format
            reich |= bool(f.properties or f.list_id is not None or f.alignment is not None or f.line_spacing is not None
                          or any(getattr(f, name) is not None for name in ("space_before_px", "space_after_px", "left_indent_px",
                                                                            "right_indent_px", "first_line_indent_px")))
            reich |= f.char_format != CharacterFormat()
            reich |= any(lauf.format != CharacterFormat() for lauf in block.runs)
    return "\n".join(absatztexte).encode("utf-8"), reich
