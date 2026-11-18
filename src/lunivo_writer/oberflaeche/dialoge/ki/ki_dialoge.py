"""KI-Konfiguration: Aufgaben-Modellzuweisung, Liste der KI-Modelle, „Eigenen Anbieter hinzufügen“.

Der Anbieter wird hier festgelegt — in „KI-Konfiguration“ (Reiter Schreibhilfe/KI) oder in den Optionen.
"""
from __future__ import annotations


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QSizePolicy, QDialog, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel import zeige_unter
from lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen import knopfzeile
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig


from lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste import HAUPT, FlacheReiterLeiste
from lunivo_writer.oberflaeche.baukasten.basis.mass import (
    GROESSE_FENSTER_KI,
    RAND_OBEN_SEITE,
)
from lunivo_writer.oberflaeche.dialoge.ki.ki_modelle_dialoge import (  # noqa: F401  (auch hier importierbar)
    AnbieterDialog, KIKonfigurationDialog, ModellListe, ModellListeDialog,
    ModellZuweisung, _Antwort, _tags_text, modell_combo,
    modell_felder_fuellen, modell_passt,
)

REITER = ("KI-Modelle", "Modellzuweisung", "Sprache", "KI-Werkzeuge", "Websuche", "Datenschutz", "Assistenten", "Dokumente")


from lunivo_writer.oberflaeche.dialoge.ki.ki_einstellungen_panels import (  # noqa: F401  (auch hier importierbar)
    DokumentePanel, EinwilligungenPanel, McpDialog, McpListe, OfflineSprachen, SprachePanel, WebsuchePanel,
)
from lunivo_writer.oberflaeche.dialoge.ki.ki_aktions_dialoge import (  # noqa: F401  (auch hier importierbar)
    AKTION_TEXTE, ASSISTENT_DATENSCHUTZ, AUSLOESER_TEXTE, ERGEBNIS_ARTEN, TEXTE_AKTION, TEXTE_ASSISTENT, UMFANG_TEXTE, VORLAGEN_AKTION,
    ErgebnisseDialog, KIAssistentDialog, SchnelleAktionDialog,
)


class KIEinstellungenDialog(PanelFaehig, QDialog):
    """Das eine Fenster für alles zur KI: verbundene Modelle, Modellzuweisung, MCP-Server und Websuche.

    Dieselbe Konfiguration (``KIKonfig``) wie in der Seitenleiste der Schreibhilfe, im KI-Chat und in den Optionen. """

    def __init__(self, fenster, start: int = 0):
        super().__init__(fenster)
        from PySide6.QtWidgets import QStackedWidget
        self.fenster = fenster
        self.k = fenster.ki.konfig
        self.setWindowTitle("KI-Einstellungen")
        self.resize(*GROESSE_FENSTER_KI)
        v = QVBoxLayout(self)
        self.reiter = FlacheReiterLeiste(HAUPT)                  # der Baustein für flache Reiter: Beschriftung bricht um, nichts wird abgeschnitten
        for n in REITER:
            self.reiter.addTab(n)
        v.addWidget(self.reiter)
        self.stapel = QStackedWidget()
        v.addWidget(self.stapel, 1)
        # 1 KI-Modelle
        seite = QWidget(); sv = QVBoxLayout(seite); sv.setContentsMargins(*RAND_OBEN_SEITE)
        sv.addWidget(QLabel("Verbinden Sie Ihre eigene KI-Quelle — entweder über den API-Schlüssel eines Anbieters oder ein lokal gehostetes Modell."))
        self.liste = ModellListe(fenster, self.k)
        sv.addWidget(self.liste, 1)
        neu = QPushButton("Neues KI-Modell verbinden …"); neu.clicked.connect(self.neues_modell)
        sv.addWidget(neu, 0, Qt.AlignLeft)
        self.stapel.addWidget(seite)
        # 2 Modellzuweisung
        z = QWidget(); zv = QVBoxLayout(z); zv.setContentsMargins(*RAND_OBEN_SEITE)
        self.zuweisung = ModellZuweisung(fenster)
        zv.addWidget(self.zuweisung)
        from lunivo_writer.oberflaeche.baukasten.chat.chat_regler import ChatReglerBlock
        self.chat_regler = ChatReglerBlock(self.k)                 # Länge, Temperatur, Top P, Stoppfolgen, direkt einfügen (zugeklappt)
        zv.addWidget(self.chat_regler)
        self.stapel.addWidget(z)
        # 3 Sprache, 4 MCP-Server, 5 Websuche
        self.sprache = SprachePanel(fenster)
        self.stapel.addWidget(self.sprache)
        self.mcp = McpListe(fenster, self.k)
        self.stapel.addWidget(self.mcp)
        self.websuche = WebsuchePanel(self.k)
        self.stapel.addWidget(self.websuche)
        self.datenschutz = EinwilligungenPanel(self.k)
        self.stapel.addWidget(self.datenschutz)
        from lunivo_writer.oberflaeche.baukasten.felder.assistenten_liste import AssistentenListe
        seite = QWidget(); av = QVBoxLayout(seite); av.setContentsMargins(*RAND_OBEN_SEITE)
        self.assistenten = AssistentenListe(fenster)
        av.addWidget(self.assistenten); av.addStretch(1)
        self.stapel.addWidget(seite)
        self.dokumente = DokumentePanel(self.k)
        self.dokumente.werkzeug_eingetragen.connect(self.mcp.fuellen)
        self.stapel.addWidget(self.dokumente)
        v.addWidget(knopfzeile(self, bei_ok=self._ok))
        self.reiter.currentChanged.connect(self.stapel.setCurrentIndex)
        self.freischalten()
        self.reiter.setCurrentIndex(start if self.reiter.isTabEnabled(start) else 0)

    def kompakt_machen(self) -> None:
        """In der Seitenleiste: kurze Reiternamen (die langen stehen im Tipp), damit alle fünf nebeneinander passen."""
        for i, (kurz, voll) in enumerate((("Modelle", "KI-Modelle"), ("Zuweisung", "Modellzuweisung"), ("Sprache", "Sprache"), ("Werkzeuge", "KI-Werkzeuge"),
                                          ("Websuche", "Websuche"), ("Daten", "Datenschutz"), ("Assistenten", "Assistenten"), ("Dokumente", "Dokumente"))):
            self.reiter.setTabText(i, kurz)
            if self.reiter.isTabEnabled(i):
                self.reiter.setTabToolTip(i, voll)
                self.reiter.setProperty("kompakt", True)                              # schmaler Innenabstand, damit alle Reiter in die Seitenleiste passen
        self.reiter.style().unpolish(self.reiter); self.reiter.style().polish(self.reiter)
        self.liste.setMinimumSize(0, 0)
        for l in self.stapel.widget(0).findChildren(QLabel):
            l.setWordWrap(True)
        self.sprache.kompakt_machen()

        def hoehe_der_seite(i: int) -> None:                                  # nur die gewählte Seite bestimmt die Höhe, die anderen zählen nicht mit
            for k in range(self.stapel.count()):
                w = self.stapel.widget(k); sp = w.sizePolicy()
                sp.setVerticalPolicy(QSizePolicy.Preferred if k == i else QSizePolicy.Ignored); w.setSizePolicy(sp)
            self.stapel.updateGeometry()
            e = self.stapel.parentWidget()
            while e is not None:
                if e.layout() is not None:
                    e.layout().invalidate()
                e = e.parentWidget()
        self.reiter.currentChanged.connect(hoehe_der_seite)
        hoehe_der_seite(self.reiter.currentIndex())
        self.setMinimumSize(0, 0)

    def freischalten(self) -> None:
        """Alle Reiter sind immer anklickbar; Sprache, MCP und Websuche brauchen kein Modell, die Zuweisung zeigt ohne Modell eine leere Auswahl."""
        for i in range(self.reiter.count()):
            self.reiter.setTabEnabled(i, True)
            self.reiter.setTabToolTip(i, "")

    def neues_modell(self) -> None:
        def fertig():
            self.liste._fuellen()
            self.zuweisung.aufbauen()
            self.fenster.ki.geaendert.emit()
            self.freischalten()
        zeige_unter(self, AnbieterDialog(self.fenster, self.k), fertig)

    def _ok(self) -> None:
        self.zuweisung.uebernehmen()
        self.sprache.uebernehmen()
        self.websuche.uebernehmen()
        self.dokumente.uebernehmen()
        self.accept()
