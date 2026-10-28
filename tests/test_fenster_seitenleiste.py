"""Die Fenster der Reiter Einfügen, Verweise, Mailings und Überprüfen öffnen sich in der rechten Seitenleiste (``PanelFaehig``), nicht frei
über dem Text, und passen dort in die Breite (Kay, 2026-10-28: Fenstersteuerung über die Seitenleiste, wie die übrigen Zusatzfenster)."""
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QWidget

from lunivo_writer.editor.verzeichnis import TOC_VORGABE
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig, ZusatzPanel
from lunivo_writer.ui.dialogs import einfuegen_dialoge as ED
from lunivo_writer.ui.dialogs import einfuegen_fenster as EF
from lunivo_writer.ui.dialogs import serien_fenster as SF
from lunivo_writer.ui.dialogs import ueberpruefen_fenster as UF
from lunivo_writer.ui.dialogs import verweise_fenster as VF

FENSTER = {
    "Zahl": lambda: EF.ZahlDialog(None), "Felder": lambda: EF.FelderDialog(None, {}), "AutoText": lambda: EF.AutoTextDialog(None, "x"),
    "Trenner": lambda: EF.TrennerDialog(None, zu_tabelle=True, texte=["a;b"]), "Seitenzahl": lambda: EF.SeitenzahlDialog(None),
    "Hyperlink": lambda: EF.HyperlinkDialog(None), "Objekt": lambda: EF.ObjektDialog(None),
    "Inhaltsverzeichnis": lambda: VF.InhaltsverzeichnisDialog(None, dict(TOC_VORGABE)), "Index": lambda: VF.IndexeintragDialog(None, "Apfel", []),
    "Nummerierung": lambda: VF.NummerierungDialog(None, "1, 2, 3"), "Beschriftung": lambda: VF.BeschriftungDialog(None, [], lambda a, b: "1"),
    "Querverweis": lambda: VF.QuerverweisDialog(None, []),
    "Empfänger": lambda: SF.EmpfaengerDialog(None, ["Vorname", "Stadt"], [{"Vorname": "Anna", "Stadt": "Kiel"}]),
    "Feld": lambda: SF.FeldDialog(None, ["Vorname"]), "Zuordnen": lambda: SF.ZuordnenDialog(None, ["Name"], ["Vorname"]),
    "Wörter": lambda: UF.WoerterDialog(None, {}), "Schutz": lambda: UF.SchutzDialog(None),
    "Form": lambda: ED.FormDialog(None), "SmartArt": lambda: ED.SmartArtDialog(None), "WordArt": lambda: ED.WordArtDialog(None),
    "Diagramm": lambda: ED.DiagrammDialog(None), "Piktogramm": lambda: ED.PiktogrammDialog(None), "Formel": lambda: ED.FormelDialog(None),
    "Deckblatt": lambda: ED.DeckblattDialog(None, "Kay"),
    "Wasserzeichen": lambda: __import__("lunivo_writer.ui.dialogs.wasserzeichen_fenster", fromlist=["x"]).WasserzeichenDialog(None, None),
}


@pytest.mark.parametrize("breite", [444, 300])
@pytest.mark.parametrize("name", list(FENSTER))
def test_fenster_in_der_seitenleiste_und_passt(app, name, breite):
    """Auch in der schmalsten Seitenleiste (300 px) ragt nichts links oder rechts hinaus (Kay, 2026-10-28)."""
    p = ZusatzPanel(); p.verfuegbar, p.verfuegbar_hoehe = breite, 587; p.resize(breite + 36, 727)
    d = FENSTER[name]()
    assert isinstance(d, PanelFaehig), name
    p.oeffne(d); p.show(); app.processEvents(); app.processEvents()
    sa = p.stapel.currentWidget().sa
    vp = sa.viewport()
    zu = [type(c).__name__ for c in d.findChildren(QWidget) if c.isVisible() and c.width() > 0
          and (c.mapTo(vp, c.rect().topLeft()).x() < -1 or c.mapTo(vp, c.rect().topRight()).x() > vp.width())]
    assert not zu, (name, breite, zu)
    p.close()
