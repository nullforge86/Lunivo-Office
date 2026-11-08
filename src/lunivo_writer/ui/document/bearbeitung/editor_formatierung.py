"""Formatierungsfunktionen des Dokumenteditors, zusammengesetzt aus Fach-Mixins."""
from __future__ import annotations

from lunivo_writer.ui.document.bearbeitung.editor_zeichenformat import ZeichenformatMixin
from lunivo_writer.ui.document.bearbeitung.editor_absatzformat import AbsatzformatMixin
from lunivo_writer.ui.document.bearbeitung.editor_stilformat import StilformatMixin
from lunivo_writer.ui.document.bearbeitung.editor_werkzeuge import EditorWerkzeugeMixin


class FormatierungBaustein(ZeichenformatMixin, AbsatzformatMixin, StilformatMixin, EditorWerkzeugeMixin):
    """Kompatible Fassade für die bisherigen Formatierungsfunktionen."""
