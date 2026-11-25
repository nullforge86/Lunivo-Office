"""Tür des Pakets ``writer.hauptfenster``. Aufrufer außerhalb des Pakets importieren nur von hier."""
from __future__ import annotations

from writer.hauptfenster.dokumente import (aktivieren, bearbeiter_setzen, bei_aenderung, bei_anzeige, bei_auswahl, layout_option_setzen, markup_an,
                                           markup_filter, markup_setzen, neu, nur_lesen_setzen, oeffnen_datei, schliessen)

__all__ = ["aktivieren", "bearbeiter_setzen", "bei_aenderung", "bei_anzeige", "bei_auswahl", "layout_option_setzen", "markup_an", "markup_filter",
           "markup_setzen", "neu", "nur_lesen_setzen", "oeffnen_datei",
           "schliessen"]
