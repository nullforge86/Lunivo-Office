"""Befehle der Funktion „Bearbeiten“: Zwischenablage (einfügen, ausschneiden, kopieren) und Auswahl (alles, Tabelle ohne Rahmen, ähnliche Formatierung).

Der Editor kommt über den ``EditorPort`` herein; Meldungen gehen als Ereignis an den ``Melder``. Die Zwischenablage selbst (Formate, Bild) ist Sache der Oberfläche."""
from __future__ import annotations

from framework.datentypen.ereignisdaten import Art, Ereignis
from framework.schnittstellen.dokument import EditorPort
from framework.steuerung.ereignissteuerung import Melder


class BearbeitenBefehle:
    def __init__(self, editor: EditorPort, melder: Melder):
        self._e = editor
        self._melder = melder

    def _melden(self, text: str, dauer_ms: int = 4000) -> None:
        self._melder.melden(Ereignis(Art.MELDUNG, text, {"dauer_ms": dauer_ms}))

    # ---- Zwischenablage -----------------------------------------------------------------------------------------------------------
    def einfuegen(self) -> None:
        kf = self._e._kf()
        if kf is not None:
            kf.feld.paste()
        else:
            self._e.paste()

    def einfuegen_formatiert(self) -> None:
        """Mit der Formatierung der Zwischenablage einfügen (Fenster „Inhalte einfügen“)."""
        self._e.paste()

    def ausschneiden(self) -> None:
        kf = self._e._kf()
        if kf is not None:
            kf.feld.cut()
        else:
            self._e.cut()

    def kopieren(self) -> None:
        kf = self._e._kf()
        if kf is not None:
            kf.feld.copy()
        else:
            self._e.copy()

    # ---- Auswahl ------------------------------------------------------------------------------------------------------------------
    def alles_markieren(self) -> None:
        self._e.selectAll()

    def tabelle_ohne_rahmen_waehlen(self) -> None:
        """Die nächste Tabelle ohne sichtbaren Rahmen (im Text nur gestrichelt angedeutet) ganz markieren."""
        if not self._e.tabelle_ohne_rahmen_waehlen():
            self._melden("Im Dokument gibt es keine Tabelle mit gestricheltem Rahmen.")

    def aehnliche_formatierung(self) -> None:
        """Alle Stellen mit derselben Zeichenformatierung wie an der Schreibmarke farbig hinterlegen; die erste wird markiert."""
        bereiche = self._e.aehnlich_formatiert()
        self._e.set_suchtreffer(bereiche)
        if bereiche:
            self._e.select_range(*bereiche[0])
        self._melden(f"{len(bereiche)} Stelle(n) mit derselben Formatierung hervorgehoben.", 6000)
