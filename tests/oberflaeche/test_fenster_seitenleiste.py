"""Die Fenster der Reiter Einfügen, Verweise, Mailings und Überprüfen öffnen sich in der rechten Seitenleiste (``PanelFaehig``), nicht frei
über dem Text, und passen dort in die Breite (Kay, 2026-10-28: Fenstersteuerung über die Seitenleiste, wie die übrigen Zusatzfenster)."""
from __future__ import annotations

import pytest
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QTabWidget, QTextEdit, QWidget

from lunivo_writer.editor.dokument.verzeichnis import TOC_VORGABE
from lunivo_writer.oberflaeche.baukasten.dokument.aenderungs_fenster import AenderungsFenster
from lunivo_writer.oberflaeche.baukasten.formatierung.absatz_dialog import AbsatzDialog
from lunivo_writer.oberflaeche.baukasten.felder.auswahl_bereich import AuswahlBereich
from lunivo_writer.oberflaeche.baukasten.formatierung.schriftart_dialog import SchriftartDialog
from lunivo_writer.oberflaeche.baukasten.dokument.sortieren_dialog import SortierenDialog, SortierOptionenDialog
from lunivo_writer.oberflaeche.baukasten.dokument.tabstopp_dialog import TabstoppDialog
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig, ZusatzPanel
from lunivo_writer.oberflaeche.dialoge.einfuegen import einfuegen_dialoge as ED
from lunivo_writer.oberflaeche.dialoge.einfuegen import einfuegen_fenster as EF
from lunivo_writer.oberflaeche.dialoge.sendungen import serien_fenster as SF
from lunivo_writer.oberflaeche.dialoge import ueberpruefen_fenster as UF
from lunivo_writer.oberflaeche.dialoge.verweise import verweise_fenster as VF

class _KiDienst(QObject):
    """Kleiner Ersatz für den KI-Dienst: nur, was das Vorher/Nachher-Fenster liest."""
    chatGeaendert, kontextGeaendert = Signal(), Signal()

    def antwort_index(self, nr):
        return 0

    def antwort_lage(self, index):
        ok = (True, "")
        return {"gueltig": True, "nr": 1, "vorher": "Alt A. Gleich.", "nachher": "Neu B. Gleich.", "einfuegen": ok, "ersetzen": (False, "Grund"),
                "stuecke": [("entfernt", "Alt A."), ("neu", "Neu B."), ("gleich", " Gleich.")]}


FENSTER = {
    "Änderung der KI": lambda: AenderungsFenster(_KiDienst(), 1),
    # Reiter Start
    "Absatz": lambda: AbsatzDialog(None), "Sortieren": lambda: SortierenDialog(None, ["a;b", "c;d"]), "Sortieroptionen": lambda: SortierOptionenDialog(None),
    "Schriftart": lambda: SchriftartDialog(None), "Tabstopps": lambda: TabstoppDialog(None, []), "Auswahlbereich": lambda: AuswahlBereich(None, QTextEdit()),
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
    "Vergrößern": lambda: __import__("lunivo_writer.oberflaeche.baukasten.medien.bild_zoom", fromlist=["x"]).BildZoomFenster(None, __import__("PySide6.QtGui", fromlist=["x"]).QImage(500, 300, __import__("PySide6.QtGui", fromlist=["x"]).QImage.Format_ARGB32)),
    "Symbol": lambda: __import__("lunivo_writer.oberflaeche.dialoge.einfuegen.sonderzeichen", fromlist=["x"]).SonderzeichenDialog(None, lambda z: None),
    "Wasserzeichen": lambda: __import__("lunivo_writer.oberflaeche.dialoge.einfuegen.wasserzeichen_fenster", fromlist=["x"]).WasserzeichenDialog(None, None),
}


def _in_eigenem_rollbereich(c, d) -> bool:
    """Inhalt eines Rollbereichs im Fenster (zum Beispiel die Bildansicht von „Vergrößern“) darf breiter sein: er rollt."""
    from PySide6.QtWidgets import QAbstractScrollArea
    w = c.parentWidget()
    while w is not None and w is not d:
        if isinstance(w, QAbstractScrollArea):
            return True
        w = w.parentWidget()
    return False


@pytest.mark.parametrize("breite", [444, 300])
@pytest.mark.parametrize("name", list(FENSTER))
def test_fenster_in_der_seitenleiste_und_passt(app, name, breite):
    """Auch in der schmalsten Seitenleiste (300 px) ragt nichts links oder rechts hinaus (Kay, 2026-10-28)."""
    p = ZusatzPanel(); p.verfuegbar, p.verfuegbar_hoehe = breite, 587; p.resize(breite + 36, 727)
    d = FENSTER[name]()
    assert isinstance(d, PanelFaehig), name
    p.oeffne(d); p.show(); app.processEvents(); app.processEvents()
    reiter = [w for w in d.findChildren(QTabWidget)]
    seiten = max([r.count() for r in reiter], default=1)
    for i in range(seiten):                                           # alle Reiter durchschalten: jeder muss passen
        for r in reiter:
            if i < r.count():
                r.setCurrentIndex(i)
        app.processEvents(); app.processEvents()
        vp = p.stapel.currentWidget().sa.viewport()
        zu = [type(c).__name__ for c in d.findChildren(QWidget) if c.isVisible() and c.width() > 0 and not _in_eigenem_rollbereich(c, d)
              and (c.mapTo(vp, c.rect().topLeft()).x() < -1 or c.mapTo(vp, c.rect().topRight()).x() > vp.width())]
        assert not zu, (name, breite, i, zu)
    p.close()
