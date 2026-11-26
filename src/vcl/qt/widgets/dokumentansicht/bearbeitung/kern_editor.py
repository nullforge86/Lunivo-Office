from __future__ import annotations
import dataclasses
import logging
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QColor
from writer import hauptfenster as _dokumente
from writer.funktionen import bearbeiten as _bearbeiten
from writer.werte import Bereich, Punkt
from writer.werte import mm_zu_px as mm_to_px
from writer.anbindung import formatwerte as _formatwerte
from vcl.qt.widgets.dokumentansicht.ansicht.dokument_ansicht import DokumentAnsicht
from vcl.qt.widgets.dokumentansicht.bearbeitung.freie_bilder_knoepfe import FreieBilderKnoepfeMixin
from vcl.qt.widgets.dokumentansicht.bearbeitung.freie_bilder_knoten import FreieBilderKnotenMixin
from vcl.qt.widgets.dokumentansicht.bearbeitung.kern_objekte import KernObjekte
from vcl.qt.widgets.dokumentansicht.bearbeitung.kern_befehle import KernBefehle
from writer import vorlagenkatalog as stile
from vcl.qt.widgets.bausteine.farben.farben import TABELLENRAND_SCHWARZ
from vcl.qt.widgets.dokumentansicht.bearbeitung.kern_cursor import KernCursor
from vcl.qt.widgets.dokumentansicht.kopffuss import KopfFussBearbeiter


log = logging.getLogger(__name__)


STYLES = dict.fromkeys(stile.eingebaute_namen())         # Namen der eingebauten Formatvorlagen (selbst angelegte: ``stile.namen()``)


EINFUEGE_MODI = ["Quellformatierung beibehalten", "Zielformatierung verwenden", "Nur Text"]


INS_STILE = ["Unterstrichen", "Doppelt unterstrichen", "Fett", "Kursiv", "Keine"]


DEL_STILE = ["Durchgestrichen", "Fett", "Kursiv", "Keine"]


nicht_angebunden: set = set()                       # Namen der Befehle, die der Editor noch nicht kennt (für die Aufgabenliste)


STANDARD_PT = 11.0


LISTEN_ART = {"bullet": "disc", "number": "dezimal"}


def _hex(farbe) -> str | None:
    """``QColor`` oder Farbtext als ``#rrggbb``; ungültig oder ``None``: ``None`` (Eigenschaft entfernen)."""
    if farbe is None:
        return None
    c = QColor(farbe)
    return c.name() if c.isValid() else None


class KernDokument(QObject):
    """Der Teil der Dokumentschnittstelle, den Fenster und Statusleiste abfragen (Änderungsstatus, Zeichenzahl, Signal bei Änderung)."""
    contentsChanged = Signal()
    contentsChange = Signal(int, int, int)       # Stelle, entfernte und hinzugekommene Zeichen: nach einer Änderung gilt der ganze Text als ersetzt
    modificationChanged = Signal(bool)

    def __init__(self, editor: "KernEditor"):
        super().__init__(editor)
        self._editor = editor
        self._erzwungen = False
        self._zuletzt = False
        self._laenge = len(_bearbeiten.dok_dokumenttext(editor.kennung))

    def isModified(self) -> bool:
        return self._erzwungen or _bearbeiten.dokument_geaendert(self._editor.kennung)

    def setModified(self, an: bool) -> None:
        self._erzwungen = bool(an)
        if not an:
            _bearbeiten.als_gespeichert_merken(self._editor.kennung)
        self.melde_status()

    def melde_status(self) -> None:
        """Meldet ``modificationChanged``, wenn sich der Änderungsstatus seit der letzten Meldung geändert hat."""
        jetzt = self.isModified()
        if jetzt != self._zuletzt:
            self._zuletzt = jetzt
            self.modificationChanged.emit(jetzt)

    def revision(self) -> int:
        """Zählt jede Änderung des Dokuments (auch Rückgängig und Wiederholen); gleiche Zahl heißt gleicher Inhalt."""
        return self._editor.revision

    def standardschrift(self) -> tuple[str, float]:
        """Familie und Größe (Punkt) der Grundschrift des Dokuments, so wie der Kern sie führt."""
        sf = _bearbeiten.dok_standardformat(self._editor.kennung)
        return str(sf.get("schrift") or _formatwerte.standard_familie()), float(sf.get("groesse_pt") or STANDARD_PT)

    def toPlainText(self) -> str:
        return _bearbeiten.dok_dokumenttext(self._editor.kennung)

    def resource(self, _art, url):
        """Das Bild einer Ressource (für die Bildfunktionen); ``None`` ohne eine solche."""
        return self._editor.bild_ressource(url.toString() if hasattr(url, "toString") else str(url))

    def addResource(self, _art, url, bild) -> None:
        self._editor.bild_ressource_neu(bild, url.toString() if hasattr(url, "toString") else str(url))

    def blockCount(self) -> int:
        return len(_bearbeiten.dok_absatzlaengen(self._editor.kennung))

    def characterCount(self) -> int:
        return len(self.toPlainText()) + 1


class KernTabelle:
    """Die Tabelle an der Schreibmarke: Id, Zeile und Spalte; Maße über Zeilen- und Spaltenzahl."""

    def __init__(self, tabelle, zeile: int, spalte: int):
        self.tabelle, self.zeile, self.spalte = tabelle, zeile, spalte
        self.id = tabelle.id

    def rows(self) -> int:
        return self.tabelle.zeilen

    def columns(self) -> int:
        return self.tabelle.spalten


class KernListe:
    """Die Liste des Absatzes an der Schreibmarke; ``stil`` ist die Aufzählungs- oder Zahlenart (Name im Dokumentenmodell)."""

    def __init__(self, definition, ebene: int):
        self.definition, self.ebene = definition, ebene

    @property
    def stil(self) -> str:
        """Art der Liste auf der Ebene des Absatzes: ``disc``, ``circle``, ``square``, ``dezimal``, ``klein``, ``gross`` …"""
        return self.definition.ebenen[min(self.ebene, len(self.definition.ebenen) - 1)].stil


class KernEditor(KernBefehle, KernObjekte, FreieBilderKnoepfeMixin, FreieBilderKnotenMixin, QObject):
    pageInfoChanged = Signal(int, int)       # aktuelle Seite, Seitenzahl
    formatChanged = Signal()                 # Format an der Schreibmarke hat sich geändert
    zoomChanged = Signal(float)
    freiAuswahlGeaendert = Signal()
    pageApplied = Signal()
    leseschutzGeaendert = Signal(bool)
    selectionChanged = Signal()
    cursorPositionChanged = Signal()
    textChanged = Signal()
    zusatzGeaendert = Signal()               # Kommentare, Noten oder Änderungen haben sich geändert
    noteAngeklickt = Signal(str, int)        # Art und Id der Note, deren Zeichen angeklickt wurde

    def __init__(self, kennung: int, parent=None):
        super().__init__(parent)
        self.kennung = kennung
        self.meta = _bearbeiten.dokument_metadaten(kennung)
        self.ansicht = DokumentAnsicht(self.kennung, True)
        self._dok = KernDokument(self)
        self.revision = 0
        self.ansicht.zoomChanged.connect(self.zoomChanged)
        self.ansicht.geaendert.connect(self._geaendert)
        self.ansicht.cursorBewegt.connect(self._bewegt)
        self.ansicht.layoutOptionGeaendert.connect(lambda name, wert: _dokumente.layout_option_setzen(self.kennung, name, wert))
        self.ansicht.vor_aenderung = self.vor_aenderung
        self.objekte_verbinden()
        self.tabellen_verbinden()
        self.ansicht.formular_hook = self._formular_klick
        self.ansicht.gliederung_hook = lambda d: self.gliederung and self.gliederung_ebene(d)
        from vcl.qt.widgets.dokumentansicht.ansicht.absatz_symbol import AbsatzSymbol
        self._absatz_symbol = AbsatzSymbol(self)
        self.ansicht.freiAuswahlGeaendert.connect(self.freiAuswahlGeaendert)
        self.ansicht.noteAngeklickt.connect(self.noteAngeklickt)
        self.ansicht.linkAngeklickt.connect(self.verknuepfung_folgen)
        self.ansicht.kontextGewuenscht.connect(self.kontextmenue_zeigen)
        self.ansicht.auswahlBeendet.connect(self.mini_zeigen)
        self.fenster = None                  # das Hauptfenster; setzt der Dokument-Tab beim Anschließen
        self._kopffuss = None                # Bearbeiter für Kopf- und Fußzeile auf der Seite (``kopffuss()``)
        self.mini_hook = None
        self.kontext_hook = None
        abmelden = _dokumente.bei_aenderung(self._im_framework_geaendert)    # Rückweg: das Framework meldet, die Ansicht zeichnet neu
        abmelden_auswahl = _dokumente.bei_auswahl(self._im_framework_bewegt)
        abmelden_anzeige = _dokumente.bei_anzeige(self._im_framework_anzeige)
        self.destroyed.connect(lambda *_: (abmelden(), abmelden_auswahl(), abmelden_anzeige()))

    def _im_framework_bewegt(self, kennung: int) -> None:
        if kennung == self.kennung:
            self.ansicht.nach_bewegung()

    def _im_framework_geaendert(self, kennung: int) -> None:
        if kennung == self.kennung:
            self.ansicht.nach_aenderung()
            self.zusatzGeaendert.emit()                  # Kommentare, Noten, Änderungen: die Seitenleisten lesen neu
            self.pageApplied.emit()                      # Seiteneinrichtung (Umschlag, Etiketten …): das Lineal folgt

    # ---- Signale der Ansicht ----------------------------------------------------------------------------------------------------
    def _geaendert(self) -> None:
        self.revision += 1
        self._dok.melde_status()
        neu = len(_bearbeiten.dok_dokumenttext(self.kennung))
        self._dok.contentsChange.emit(0, self._dok._laenge, neu)
        self._dok._laenge = neu
        self._dok.contentsChanged.emit()
        self.textChanged.emit()
        self.formatChanged.emit()
        self._seite_melden()

    def _bewegt(self) -> None:
        self.cursorPositionChanged.emit()
        self.selectionChanged.emit()
        self.formatChanged.emit()
        self._seite_melden()

    def _seite_melden(self) -> None:
        self.pageInfoChanged.emit(self.current_page(), self.page_count)

    # ---- Allgemeines ------------------------------------------------------------------------------------------------------------------
    def document(self) -> KernDokument:
        return self._dok

    def textCursor(self) -> KernCursor:
        return KernCursor(self)

    def setTextCursor(self, c: KernCursor) -> None:
        """Setzt Anker und Kopf der Auswahl auf die Stellen des Zeigers."""
        k = self.kennung
        _bearbeiten.auswahl_setzen(k, _bearbeiten.stelle_von(k, c.anchor()), _bearbeiten.stelle_von(k, c.position()))
        self.ansicht.nach_bewegung()

    def widget(self):
        return self.ansicht

    def setFocus(self) -> None:
        self.ansicht.setFocus()

    def viewport(self):
        return self.ansicht

    def setReadOnly(self, an: bool) -> None:
        alt = self.ansicht.isReadOnly()
        self.ansicht.setReadOnly(an)
        _dokumente.nur_lesen_setzen(self.kennung, bool(an))
        if alt != bool(an):
            self.leseschutzGeaendert.emit(bool(an))

    def isReadOnly(self) -> bool:
        return self.ansicht.isReadOnly()

    def set_formatzeichen(self, absatz: bool, leer: bool) -> None:
        self.ansicht.set_formatzeichen(absatz, leer)

    def opt(self, schluessel: str, standard=None):
        """Eine Einstellung des Hauptfensters (``ui/…``, ``bearbeiten/…``); ohne Hauptfenster oder Eintrag der Standardwert."""
        einst = getattr(self.fenster, "settings", None)
        return einst.get(schluessel, standard) if einst is not None else standard

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        if name not in nicht_angebunden:
            nicht_angebunden.add(name)
            log.warning("Editor-Befehl „%s“ ist noch nicht an den Dokumentenkern angebunden", name)
        return lambda *a, **k: None

    # ---- Zustand --------------------------------------------------------------------------------------------------------------------------
    @property
    def zoom(self) -> float:
        return self.ansicht.zoom

    def set_zoom(self, faktor: float) -> None:
        self.ansicht.set_zoom(faktor)

    def current_page(self) -> int:
        erg = self.ansicht.ergebnis()
        s = erg.seite_von(_bearbeiten.auswahl(self.kennung).kopf.absatz_id)
        return (s if s is not None else 0) + 1

    @property
    def page_count(self) -> int:
        return self.ansicht.seitenzahl()

    def word_count(self) -> int:
        return len(_bearbeiten.dok_dokumenttext(self.kennung).split())

    def tabelle_an_marke(self):
        """``KernTabelle`` der Tabelle, in der die Schreibmarke steht (sonst ``None``)."""
        stelle = _bearbeiten.dok_tabelle_von(self.kennung, _bearbeiten.auswahl(self.kennung).kopf.absatz_id)
        return KernTabelle(*stelle) if stelle is not None else None

    def tabelle_sortieren(self, tabellen_id: int, spalte: int, aufsteigend: bool = True) -> None:
        """Sortiert die Zeilen der Tabelle nach einer Spalte (zentrale Bearbeitung ``tabelle_sortieren``)."""
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_tabelle_sortieren(self.kennung, tabellen_id, spalte, aufsteigend))

    def liste_an_marke(self):
        a = self._absatz_an_marke()
        d = _bearbeiten.dok_liste(self.kennung, a.liste_id)
        return KernListe(d, a.ebene) if d is not None and d.ebenen else None

    def _recount(self) -> None:
        self._seite_melden()

    def _kf(self):
        """Der Kopf-/Fußzeilen-Bearbeiter, solange die Schreibmarke dort steht (dann wirken die Start-Werkzeuge auf die Zeile), sonst ``None``."""
        kf = self._kopffuss
        return kf if kf is not None and kf.aktiv and kf.im_feld else None

    def position_im_text(self, pos) -> int:
        """Die Zeichenstelle im Gesamttext (Absätze durch je ein Zeichen getrennt)."""
        n = 0
        for aid, laenge in _bearbeiten.dok_absatzlaengen(self.kennung):
            if aid == pos.absatz_id:
                return n + pos.versatz
            n += laenge + 1
        return n

    @property
    def noten(self) -> dict:
        return _bearbeiten.dok_noten(self.kennung)

    @property
    def kommentare(self) -> dict:
        return _bearbeiten.dok_kommentare(self.kennung)

    # ---- Format an der Schreibmarke ------------------------------------------------------------------------------------------------------
    def _absatz_an_marke(self):
        return _bearbeiten.dok_absatz_an_marke(self.kennung)

    def _zeichen(self) -> dict:
        """Das wirksame Zeichenformat an der Schreibmarke (am Anfang einer Auswahl: das erste Zeichen); im Kopf-/Fußfeld das Format der Zeile."""
        kf = self._kf()
        if kf is not None:
            return kf.format_lesen()
        return _bearbeiten.wirksames_zeichenformat(self.kennung)

    def zeichenformat(self) -> dict:
        """Das wirksame Zeichenformat an der Schreibmarke (Modellnamen, Wörterbuch)."""
        return self._zeichen()

    def absatzformat(self) -> dict:
        """Das wirksame Absatzformat des Absatzes an der Schreibmarke (Modellnamen, Wörterbuch)."""
        return _bearbeiten.wirksames_absatzformat(self.kennung)

    def current_style(self) -> str:
        return self._absatz_an_marke().format.get("vorlage") or "Standard"

    # ---- Zeichenformat ----------------------------------------------------------------------------------------------------------------------
    def _zf(self, aenderung: dict) -> None:
        kf = self._kf()
        if kf is not None:                                      # die Schreibmarke steht im Kopf-/Fußfeld: das Format gilt der Zeile
            kf.format_anwenden(aenderung)
            return
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_zeichenformat_anwenden(self.kennung, aenderung))

    def toggle_bold(self, an: bool) -> None:
        self._zf({"fett": True if an else None, "gewicht": None})

    def toggle_italic(self, an: bool) -> None:
        self._zf({"kursiv": True if an else None})

    def toggle_underline(self, an: bool) -> None:
        self._zf({"unterstrichen": True if an else None, "unter_art": None})

    def toggle_strike(self, an: bool) -> None:
        self._zf({"durchgestrichen": True if an else None})

    def set_script(self, art) -> None:
        self._zf({"hoch_tief": {"sup": "hoch", "sub": "tief"}.get(art)})

    def set_font_family(self, familie: str) -> None:
        self._zf({"schrift": familie})

    def set_font_size(self, pt: float) -> None:
        if pt > 0:
            self._zf({"groesse_pt": float(pt)})

    def grow_font(self, delta: float) -> None:
        aktuell = float(self._zeichen().get("groesse_pt") or STANDARD_PT)
        self.set_font_size(max(1.0, min(400.0, aktuell + delta)))

    def set_text_color(self, farbe) -> None:
        self._zf({"farbe": _hex(farbe)})

    def set_highlight(self, farbe) -> None:
        self._zf({"marker": _hex(farbe)})

    def set_capitalization(self, art: str) -> None:
        """Schreibweise der Buchstaben als Zeichenformat des Kerns: ``"kapitaelchen"``, ``"gross"`` (Großbuchstaben) oder ``"normal"``."""
        self._zf({"kapitaelchen": True if art == "kapitaelchen" else None, "grossbuchstaben": True if art == "gross" else None})

    def set_letter_spacing(self, px: float) -> None:
        self._zf({"zeichenabstand": float(px) if px else None, "zeichenabstand_art": 1 if px else None})

    def clear_formatting(self) -> None:
        kf = self._kf()
        if kf is not None:
            kf.format_loeschen()
            return
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_zeichenformat_anwenden(self.kennung, {}, ersetzen=True))

    def change_case(self, art) -> None:
        """Groß-/Kleinschreibung des markierten Textes ändern (``art``: „gross“, „klein“, „wortanfang“, „satzanfang“)."""
        anker, kopf = _bearbeiten.auswahl(self.kennung)
        if anker == kopf:
            return
        text = _bearbeiten.auswahl_text(self.kennung)
        neu = {"gross": text.upper(), "klein": text.lower(), "wortanfang": text.title(), "satzanfang": text[:1].upper() + text[1:].lower()}.get(art)
        if neu is not None and neu != text:
            self.ansicht._befehl(lambda: _bearbeiten.aenderung_ersetzen(self.kennung, neu))

    # ---- Absatzformat -------------------------------------------------------------------------------------------------------------------------
    def _af(self, aenderung: dict) -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_absatzformat_anwenden(self.kennung, aenderung))

    def set_alignment(self, al) -> None:
        wert = al if isinstance(al, str) else ("block" if al & Qt.AlignJustify else "mitte" if al & Qt.AlignHCenter else "rechts" if al & Qt.AlignRight else "links")
        wert = {"left": "links", "center": "mitte", "right": "rechts", "justify": "block"}.get(wert, wert)
        kf = self._kf()
        if kf is not None:                                      # im Kopf-/Fußfeld: die Zeile ausrichten (Blocksatz gibt es dort nicht)
            kf.ausrichtung_setzen({"mitte": "center", "rechts": "right"}.get(wert, "left"))
            return
        self._af({"ausrichtung": wert})

    def change_indent(self, delta_mm: float) -> None:
        aktuell = float(self._absatz_formatwert("einzug_links"))
        self._af({"einzug_links": max(0.0, aktuell + mm_to_px(delta_mm)) or None})

    def _absatz_formatwert(self, name: str) -> float:
        return _bearbeiten.absatz_formatwert(self.kennung, name)

    def set_line_spacing(self, faktor: float) -> None:
        self._af({"zeilenabstand_art": "vielfach", "zeilenabstand": faktor * 100.0})

    def set_line_height(self, art: str, wert: float) -> None:
        """Zeilenabstand: ``faktor`` (Vielfaches), ``mindestens`` oder ``genau`` (Punkt)."""
        if art == "faktor":
            self.set_line_spacing(wert)
        else:
            self._af({"zeilenabstand_art": art, "zeilenabstand": wert / 0.75})

    def set_paragraph_spacing(self, davor_pt: float, danach_pt: float) -> None:
        self._af({"abstand_vor": davor_pt / 0.75 or None, "abstand_nach": danach_pt / 0.75 or None})

    def set_page_break_before(self, an: bool) -> None:
        self._af({"seitenumbruch_vor": True if an else None})

    def apply_style(self, name: str) -> None:
        """Formatvorlage ``name`` auf die Auswahl anwenden – das Framework holt sie aus dem Katalog ins Dokument."""
        _bearbeiten.formatvorlage_anwenden(self.kennung, name)

    def toggle_list(self, art: str, stil=None) -> None:
        a = self._absatz_an_marke()
        gewuenscht = LISTEN_ART.get(art, "disc")
        liste = _bearbeiten.dok_liste(self.kennung, a.liste_id)
        if liste is not None and liste.ebenen and liste.ebenen[0].stil == gewuenscht:
            self.ansicht._befehl(lambda: _bearbeiten.aenderung_liste_entfernen(self.kennung))
            return

        self.ansicht._befehl(lambda: _bearbeiten.aenderung_liste_anlegen_anwenden(self.kennung, gewuenscht))

    def list_level(self, schritte: int) -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_listenebene_aendern(self.kennung, schritte))

    # ---- Einfügen ---------------------------------------------------------------------------------------------------------------------------------
    def insert_table(self, zeilen: int, spalten: int) -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_tabelle_einfuegen(self.kennung, zeilen, spalten, format={"rahmen_breite": 1.0, "rahmen_farbe": TABELLENRAND_SCHWARZ}))      # wie in Word: Tabellenraster

    def insert_page_break(self) -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_umbruch_einfuegen(self.kennung, "seite"))

    def insert_column_break(self) -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_umbruch_einfuegen(self.kennung, "spalte"))

    def insertPlainText(self, text: str) -> None:
        self.ansicht.einfuegen(text)

    # ---- Bearbeiten ---------------------------------------------------------------------------------------------------------------------------------
    def undo(self) -> None:
        self.ansicht.rueckgaengig()

    def redo(self) -> None:
        self.ansicht.wiederholen()

    def cut(self) -> None:
        self.ansicht.ausschneiden()

    def copy(self) -> None:
        self.ansicht.kopieren()

    def paste(self) -> None:
        self.ansicht.einsetzen()

    def selectAll(self) -> None:
        self.ansicht.alles_auswaehlen()

    def toPlainText(self) -> str:
        return _bearbeiten.dok_dokumenttext(self.kennung)

    # ---- Seiteneinrichtung ------------------------------------------------------------------------------------------------------------------------
    def abschnitt_nr(self) -> int:
        return _bearbeiten.dok_abschnitt_index(self.kennung, _bearbeiten.auswahl(self.kennung).kopf.absatz_id)

    def abschnitt_seite(self):
        """Die Seiteneinrichtung des Abschnitts an der Schreibmarke (eine Kopie zum Ändern)."""
        return _bearbeiten.seite_des_abschnitts(self.kennung, self.abschnitt_nr())

    @property
    def page(self):
        """Die Seiteneinrichtung des Abschnitts an der Schreibmarke zum Lesen (zum Ändern: ``abschnitt_seite``); je Stand des Dokuments einmal geholt."""
        schluessel = (getattr(self, "revision", 0), self.abschnitt_nr())
        gemerkt = getattr(self, "_seite_gemerkt", None)
        if gemerkt is None or gemerkt[0] != schluessel:
            gemerkt = self._seite_gemerkt = (schluessel, _bearbeiten.seite_des_abschnitts(self.kennung, schluessel[1]))
        return gemerkt[1]

    def _seite_ersetzen(self, index: int, seite) -> bool:
        """Die Seiteneinrichtung des Abschnitts ersetzen: ihre Felder gehen als Wörterbuch an das Framework."""
        return self.ansicht._befehl(lambda: _bearbeiten.aenderung_seite_ersetzen(self.kennung, index, seite.als_felder()))

    def page_settings_changed(self, seite) -> None:
        index = self.abschnitt_nr()
        self._seite_ersetzen(index, seite)
        self.pageApplied.emit()

    def kopffuss_zeile_setzen(self, zeile: str, text: str, ausrichtung: str) -> None:
        """Kopf- oder Fußzeile (``header``, ``footer``, ``first_header``, ``first_footer``) des Abschnitts an der Schreibmarke durch Text ersetzen."""
        index = self.abschnitt_nr()
        self.ansicht._befehl(lambda: _bearbeiten.kopffuss_zeile_setzen(self.kennung, index, zeile, text, ausrichtung))
        self.pageApplied.emit()

    def seitenzahl_einfuegen(self) -> None:
        """Die Seitenzahl in die Fußzeile des Abschnitts an der Schreibmarke setzen."""
        index = self.abschnitt_nr()
        self.ansicht._befehl(lambda: _bearbeiten.seitenzahl_einfuegen(self.kennung, index))
        self.pageApplied.emit()

    def apply_page(self, seite) -> None:
        self._seite_ersetzen(0, seite)
        self.pageApplied.emit()

    def set_zeilennummern(self, an: bool, neu: str = "") -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_seite_setzen(self.kennung, self.abschnitt_nr(), zeilennummern=bool(an), zeilennummern_neu=neu))

    # ---- Vorlagen ---------------------------------------------------------------------------------------------------------------------------------
    def geruest_aufbauen(self, zeilen: list, benutzer: dict, heute: str) -> None:
        """Schreibt das Gerüst einer Dokumentvorlage in das (leere) Dokument: Absätze, Auszeichnungen und die Lücken « … » zum Ausfüllen."""
        self.ansicht._befehl(lambda: _bearbeiten.geruest_schreiben(self.kennung, zeilen, benutzer, heute))
        self._dok.setModified(True)

    # ---- Suchen und Ersetzen ---------------------------------------------------------------------------------------------------------------------
    def select_range(self, von: int, bis: int) -> None:
        """Wählt die Stellen [von, bis) des Rohtextes (Absätze durch ein Zeichen getrennt) aus."""
        k = self.kennung
        _bearbeiten.auswahl_setzen(k, _bearbeiten.stelle_von(k, von), _bearbeiten.stelle_von(k, bis))
        self.ansicht.nach_bewegung()

    def ensureCursorVisible(self) -> None:
        self.ansicht._sichtbar_machen()

    def set_wellen(self, funde: list) -> None:
        """Zeigt die Funde der Schreibhilfe als Wellenlinien unter dem Text."""
        self.ansicht.set_wellen(funde)

    def set_suchtreffer(self, treffer: list) -> None:
        """Hebt die Fundstellen (Rohtext-Stellen) in der Zeichenfläche hervor; eine leere Liste nimmt sie weg."""
        self.ansicht.set_suchtreffer(treffer)

    def ersetze_roh(self, von: int, bis: int, neu: str, zeichen: dict | None = None, absatz: dict | None = None, vorlage: str | None = None) -> None:
        """Ersetzt eine Fundstelle; die Schreibmarke steht danach hinter dem eingesetzten Text."""
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_fundstelle_ersetzen(self.kennung, von, bis, neu, zeichen, absatz, vorlage))

    def alle_ersetzen_roh(self, auftrag, ersatz: str, von: int = 0, bis: int | None = None, zeichen: dict | None = None, absatz: dict | None = None,
                          vorlage: str | None = None, zwischenablage: str = "") -> int:
        zaehler = [0]

        def f() -> bool:
            n = _bearbeiten.suche_alle_ersetzen(self.kennung, auftrag, ersatz, von, bis, zeichen, absatz, zwischenablage)
            zaehler[0] = max(n, 0)
            return n >= 0
        self.ansicht._befehl(f)
        return zaehler[0]

    # ---- Kommentare, Noten und nachverfolgte Änderungen --------------------------------------------------------------------------------------------
    def _bereiche_offsets(self, bereiche, wert) -> list:
        """Die ``bereiche`` als Liste von {"von", "bis", "wert"} mit Stellen im Rohtext (Absätze durch ein Zeichen getrennt)."""
        k = self.kennung
        return [{"von": _bearbeiten.stelle_im_text(k, b.anker), "bis": _bearbeiten.stelle_im_text(k, b.kopf), "wert": w, "auswahl": b}
                for b in bereiche for w in [wert(self._format_bei(b.anker))]]

    def _format_bei(self, pos) -> dict:
        return _bearbeiten.lauf_format_bei(self.kennung, pos)

    def _springe(self, bereiche: list, delta: int):
        """Wählt den nächsten (``delta`` 1) oder vorigen (-1) Bereich hinter bzw. vor der Schreibmarke (mit Umlauf); ``None``, wenn es keinen gibt."""
        if not bereiche:
            return None
        pos = self.textCursor().selectionEnd() if delta > 0 else self.textCursor().selectionStart()
        if delta > 0:
            ziel = next((b for b in bereiche if b["von"] >= pos), bereiche[0])
        else:
            ziel = next((b for b in reversed(bereiche) if b["bis"] <= pos or b["von"] < pos), bereiche[-1])
        self.select_range(ziel["von"], ziel["bis"])
        return ziel

    def _markup_vorgabe(self) -> dict:
        """Der Markup-Filter des Dokuments (Zustand im Framework)."""
        return dict(_dokumente.markup_filter(self.kennung))

    @property
    def markup(self) -> bool:
        return _dokumente.markup_an(self.kennung)

    def set_markup(self, an: bool) -> None:
        """Markup zeigen oder ausblenden: das Framework hält den Zustand, die Ansicht folgt auf dessen Meldung."""
        _dokumente.markup_setzen(self.kennung, bool(an))

    def _im_framework_anzeige(self, kennung: int) -> None:
        if kennung == self.kennung:
            self.ansicht.set_markup(_dokumente.markup_an(self.kennung))
            self.zusatzGeaendert.emit()

    @property
    def verfolgen(self) -> bool:
        return _bearbeiten.nachverfolgen(self.kennung)

    def set_verfolgen(self, an: bool) -> None:
        _bearbeiten.nachverfolgen_setzen(self.kennung, bool(an))
        self.zusatzGeaendert.emit()

    def bearbeiter_melden(self) -> None:
        """Den Namen des Bearbeiters (Einstellungen) ans Framework geben: er steht an Änderungen und Kommentaren, die das Framework ausführt."""
        angaben = self.autor() if callable(getattr(self, "autor", None)) else ("", "")
        _dokumente.bearbeiter_setzen(self.kennung, angaben[0] if angaben else "")

    def vor_aenderung(self) -> None:
        """Vor jeder Änderung: Bearbeiter und Zeit für nachverfolgte Änderungen und Kommentare setzen."""
        angaben = self.autor() if callable(getattr(self, "autor", None)) else ("", "")
        autor = angaben[0] if angaben else ""
        _bearbeiten.bearbeiter_stempeln(self.kennung, autor)
        _dokumente.bearbeiter_setzen(self.kennung, autor)

    def kommentar_bereiche(self) -> list:
        return self._bereiche_offsets(_bearbeiten.dok_bereiche_mit(self.kennung, "kommentar"), lambda f: f.get("kommentar"))

    def kommentar_neu(self, text: str):
        """Kommentiert die Auswahl (ohne Auswahl das Wort an der Schreibmarke); gibt die Kommentar-Id zurück, ``None`` wenn es nicht geht."""
        angaben = self.autor() if callable(getattr(self, "autor", None)) else ("", "")
        ergebnis = []

        def f() -> bool:
            kid = _bearbeiten.aenderung_kommentar_einfuegen(self.kennung, text, angaben[0] if angaben else "", angaben[1] if len(angaben) > 1 else "")
            if kid is not None:
                ergebnis.append(kid)
            return kid is not None
        if not self.ansicht._befehl(f):
            return None
        self.zusatzGeaendert.emit()
        return ergebnis[0] if ergebnis else None

    def kommentar_text_setzen(self, kid: int, text: str) -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_kommentar_aendern(self.kennung, kid, text=text))
        self.zusatzGeaendert.emit()

    def kommentar_geloest(self, kid: int, geloest: bool) -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_kommentar_aendern(self.kennung, kid, geloest=geloest))
        self.zusatzGeaendert.emit()

    def kommentar_loeschen(self, kid: int | None = None) -> None:
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_kommentar_loeschen(self.kennung, kid))
        self.zusatzGeaendert.emit()

    def kommentare_alle_loeschen(self) -> None:
        self.kommentar_loeschen(None)

    def kommentar_springen(self, delta: int):
        return self._springe(self.kommentar_bereiche(), delta)

    def kommentar_am_cursor(self):
        p = self.textCursor().position()
        for b in self.kommentar_bereiche():
            if b["von"] <= p <= b["bis"]:
                return int(b["wert"])
        return None

    def aenderungen(self) -> list:
        """Die nachverfolgten Änderungen: {"von", "bis", "wert" ("ins"/"del"), "autor", "datum"}."""
        aus = []
        for b in self._bereiche_offsets(_bearbeiten.dok_aenderungsbereiche(self.kennung), lambda f: (f["aenderung"], f.get("autor", ""), f.get("datum", ""))):
            art, autor, datum = b["wert"]
            aus.append({"von": b["von"], "bis": b["bis"], "wert": art, "autor": autor, "datum": datum})
        return aus

    def aenderung_am_cursor(self):
        p, q = self.textCursor().selectionStart(), self.textCursor().selectionEnd()
        return next((b for b in self.aenderungen() if b["von"] <= p < b["bis"] or (q > b["von"] and p < b["bis"])), None)

    def aenderung_springen(self, delta: int):
        return self._springe(self.aenderungen(), delta)

    def aenderung_annehmen(self, b: dict, annehmen: bool = True) -> None:
        bereich = Bereich(_bearbeiten.stelle_von(self.kennung, b["von"]), _bearbeiten.stelle_von(self.kennung, b["bis"]))
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_aenderungen_entscheiden(self.kennung, annehmen, bereich))
        self.zusatzGeaendert.emit()

    def alle_aenderungen(self, annehmen: bool) -> int:
        n = len(self.aenderungen())
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_aenderungen_entscheiden(self.kennung, annehmen))
        self.zusatzGeaendert.emit()
        return n

    def aenderung_sichtbar(self, b: dict) -> bool:
        """Ob eine Änderung zum gewählten Markup gehört (Bearbeiter, Tag)."""
        f = self._markup_vorgabe()
        if not f["einfuegungen"]:
            return False
        if f["bearbeiter"] is not None and b["autor"] not in f["bearbeiter"]:
            return False
        return f["zeit"] is None or b["datum"][:10] == f["zeit"]

    def angezeigte_aenderungen(self, annehmen: bool) -> int:
        n = 0
        for b in reversed(self.aenderungen()):
            if self.aenderung_sichtbar(b):
                self.aenderung_annehmen(b, annehmen)
                n += 1
        return n

    def noten_stellen(self) -> list:
        k = self.kennung
        aus = []
        for b in _bearbeiten.dok_notenbereiche(self.kennung):
            art, _, nid = self._format_bei(b.anker)["note"].partition(":")
            aus.append({"von": _bearbeiten.stelle_im_text(k, b.anker), "bis": _bearbeiten.stelle_im_text(k, b.kopf), "art": art, "id": int(nid)})
        return aus

    def note_neu(self, art: str, text: str) -> int:
        ergebnis = []

        def f() -> bool:
            nid = _bearbeiten.aenderung_note_einfuegen(self.kennung, text, art)
            if nid is not None:
                ergebnis.append(nid)
            return nid is not None
        self.ansicht._befehl(f)
        self.zusatzGeaendert.emit()
        return ergebnis[0] if ergebnis else 0

    def note_springen(self, delta: int, art: str | None = None):
        return self._springe([n for n in self.noten_stellen() if art is None or n["art"] == art], delta)

    # ---- Kopf- und Fußzeilen ----------------------------------------------------------------------------------------------------------------------------
    def kopffuss(self) -> KopfFussBearbeiter:
        """Der Bearbeiter für Kopf- und Fußzeile direkt auf der Seite (wird beim ersten Aufruf angelegt)."""
        if self._kopffuss is None:
            self._kopffuss = KopfFussBearbeiter(self)
        return self._kopffuss

    def felder_aktualisieren(self) -> None:
        """Rechnet die Felder neu, deren Ergebnis das Dokument selbst bestimmt (Nummern der Beschriftungen)."""
        self.ansicht._befehl(lambda: _bearbeiten.aenderung_beschriftungen_nummerieren(self.kennung))

    # ---- Tabellen ------------------------------------------------------------------------------------------------------------------------------------------
    def tabelle_aktion(self, art: str) -> bool:
        """Zeilen und Spalten einfügen und löschen, ganze Tabelle löschen — an der Zelle der Schreibmarke. ``False``, wenn keine Tabelle gewählt ist."""
        t = self.tabelle_an_marke()
        if t is None:
            return False
        z, sp, tid = t.zeile, t.spalte, t.id
        k, B = self.kennung, _bearbeiten
        wirkt = {"zeile_oben": lambda: B.aenderung_zeilen_einfuegen(k, tid, z),
                 "zeile_unten": lambda: B.aenderung_zeilen_einfuegen(k, tid, z + t.tabelle.zellen[z][sp].zeilenspanne
                                                                     if t.tabelle.zellen[z][sp].verdeckt_von is None else z + 1),
                 "spalte_links": lambda: B.aenderung_spalten_einfuegen(k, tid, sp), "spalte_rechts": lambda: B.aenderung_spalten_einfuegen(k, tid, sp + 1),
                 "zeile_loeschen": lambda: B.aenderung_zeilen_loeschen(k, tid, z), "spalte_loeschen": lambda: B.aenderung_spalten_loeschen(k, tid, sp),
                 "tabelle_loeschen": lambda: B.aenderung_tabelle_loeschen(k, tid)}.get(art)
        if wirkt is None:
            return False
        return self.ansicht._befehl(wirkt)

    def zellen_im_bereich(self):
        """(Tabelle, [(Zeile, Spalte)]) der Zellen, die die Auswahl überstreicht; ohne Auswahl die Zelle der Schreibmarke."""
        r = _bearbeiten.dok_zellen_im_bereich(self.kennung)
        if r is not None:
            return r[0], list(r[1])
        t = self.tabelle_an_marke()
        return (t.id, [(t.zeile, t.spalte)]) if t is not None else None

    def zellen_verbinden(self) -> bool:
        """Verbindet die überstrichenen Zellen zu einer; ``False``, wenn nichts zu verbinden ist."""
        r = _bearbeiten.dok_zellen_im_bereich(self.kennung)
        if r is None or len(r[1]) < 2:
            return False
        tid, zellen = r
        tabelle = _bearbeiten.dok_tabelle(self.kennung, tid)
        z1, z2 = min(z for z, _ in zellen), max(z + tabelle.zellen[z][s].zeilenspanne - 1 for z, s in zellen)
        s1, s2 = min(s for _, s in zellen), max(s + tabelle.zellen[z][s].spaltenspanne - 1 for z, s in zellen)
        return self.ansicht._befehl(lambda: _bearbeiten.aenderung_zellen_verbinden(self.kennung, tid, z1, s1, z2 - z1 + 1, s2 - s1 + 1))

    def zelle_teilen(self, spalten: int, zeilen: int) -> bool:
        t = self.tabelle_an_marke()
        return t is not None and self.ansicht._befehl(lambda: _bearbeiten.aenderung_zelle_teilen(self.kennung, t.id, t.zeile, t.spalte, zeilen, spalten))

    def tabelle_teilen(self) -> bool:
        """Teilt die Tabelle oberhalb der Zeile der Schreibmarke: Die Zeilen ab hier bilden eine neue Tabelle darunter."""
        t = self.tabelle_an_marke()
        if t is None or t.zeile < 1:
            return False
        return self.ansicht._befehl(lambda: _bearbeiten.tabelle_teilen(self.kennung, t.tabelle.id, t.zeile))

    def zellformat(self, aenderung: dict) -> bool:
        """Wendet ein Zellformat auf die überstrichenen Zellen (sonst die der Schreibmarke) an."""
        r = self.zellen_im_bereich()
        return r is not None and self.ansicht._befehl(lambda: _bearbeiten.aenderung_zellformat_anwenden(self.kennung, r[0], aenderung, r[1]))

    def tabellenformat(self, aenderung: dict) -> bool:
        t = self.tabelle_an_marke()
        return t is not None and self.ansicht._befehl(lambda: _bearbeiten.aenderung_tabellenformat_anwenden(self.kennung, t.id, aenderung))

    # ---- Objekte ---------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _png(img) -> bytes:
        """Die Bytes des Bildes fürs Dokument: ein Rasterbild aus einer Datei (JPEG, GIF …) bleibt im Original, sonst PNG."""
        from vcl.qt.rendering import formen as BD
        q = BD.quelle_zu(img)
        if q is not None and q.format in ("jpeg", "gif", "bmp", "tiff", "webp"):
            return q.daten
        from PySide6.QtCore import QBuffer, QIODevice
        puffer = QBuffer()
        puffer.open(QIODevice.WriteOnly)
        img.save(puffer, "PNG")
        return bytes(puffer.data())

    def objekt_frei_einfuegen(self, art: str, daten: dict, breite: float, hoehe: float, bild, alt: str = "") -> int | None:
        """Legt ein frei positioniertes Objekt am Absatz der Schreibmarke an (ein Bild als Darstellung) und wählt es aus; → Id des Objekts."""
        maxb = self.page.content_width_px
        if breite > maxb:
            hoehe, breite = hoehe * maxb / breite, maxb
        ergebnis: list = []
        png = self._png(bild)

        def f() -> bool:
            oid = _bearbeiten.aenderung_objekt_frei_einfuegen(self.kennung, art, breite, hoehe, png, dict(daten or {}), alt)
            if oid is not None:
                ergebnis.append(oid)
            return oid is not None
        ok = self.ansicht._befehl(f)
        if not ok or not ergebnis:
            return None
        self.ansicht.gewaehltes_objekt = ergebnis[0]
        self.ansicht.update()
        self.freiAuswahlGeaendert.emit()
        return ergebnis[0]

    def insert_image(self, pfad: str) -> bool:
        """Fügt ein Bild aus einer Datei wie ein Zeichen in den Text ein, auf die Inhaltsbreite begrenzt. Solange Kopf- oder Fußzeile bearbeitet wird,
        kommt das Bild frei platziert dorthin und steht auf jedem Blatt des Abschnitts."""
        from PySide6.QtGui import QImage
        if self._kopffuss is not None and self._kopffuss.aktiv:
            return self._kopffuss.bild_einfuegen(pfad)
        try:
            with open(pfad, "rb") as f:
                roh = f.read()
        except OSError:
            return False
        img = QImage()
        if not img.loadFromData(roh):
            return False
        b, h = float(img.width()), float(img.height())
        maxb = self.page.content_width_px
        if b > maxb:
            h, b = h * maxb / b, maxb
        return self.ansicht._befehl(lambda: _bearbeiten.aenderung_objekt_einfuegen(self.kennung, "bild", b, h, bilddaten=roh, alt_text=""))

    def objekt_gewaehlt(self):
        """Das gewählte frei positionierte Objekt (``FreiesObjekt``) oder ``None``."""
        return _bearbeiten.dok_objekt(self.kennung, self.ansicht.gewaehltes_objekt)

    def objekt_bild(self, objekt):
        """Das Darstellungsbild eines Objekts (Ressource) als ``QImage``; ``None`` ohne Bilddaten."""
        from PySide6.QtGui import QImage
        roh = _bearbeiten.dok_ressource(self.kennung, objekt.ressource)
        img = QImage()
        return img if roh and img.loadFromData(roh) else None

    def objekt_setzen(self, objekt_id: int, **felder) -> bool:
        """Ändert Felder eines frei positionierten Objekts (``daten``, ``breite``, ``hoehe``, ``bilddaten`` …) in einem Schritt."""
        return self.ansicht._befehl(lambda: _bearbeiten.aenderung_objekt_aendern(self.kennung, objekt_id, **felder))

    # ---- Freie Objekte: Rückrufe der Kerndaten (der Kern kennt die Zeichenfunktionen nicht) ------------------------------------------------------------
    def frei_daten_lesen(self, art: str) -> dict | None:
        """Die Daten des gewählten freien Objekts dieser Art (WordArt, Form, SmartArt …) oder ``None``."""
        from vcl.qt.rendering import formen as FO
        return FO.daten_lesen(self, art)

    def frei_daten_still(self, art: str, **kw) -> bool:
        """Daten des gewählten freien Objekts ändern, ohne das Bild neu zu zeichnen."""
        from vcl.qt.rendering import formen as FO
        return FO.daten_still(self, art, **kw)

    def frei_einfuegen(self, art: str, daten: dict):
        """Ein freies Objekt dieser Art mit diesen Daten einfügen und auswählen. → Id."""
        from vcl.qt.rendering import formen as FO
        return FO.frei_objekt_einfuegen(self, art, daten)

    # ---- Ansicht ---------------------------------------------------------------------------------------------------------------------------------------
    autor = None                             # Rückruf des Hauptfensters: (Name, Initialen) des Benutzers

    @property
    def web(self) -> bool:
        return self.ansicht.seitenansicht == "web"

    def set_web(self, an: bool) -> None:
        self.ansicht.set_seitenansicht("web" if an else "einzeln")

    marken = False
    gitter = False
    zeilenfokus = False
    gliederung = False

    def set_gliederung(self, an: bool) -> None:
        """Gliederungsansicht: nur die Überschriften des Dokuments."""
        self.gliederung = bool(an)
        self.ansicht.set_ansicht(gliederung=self.gliederung)

    def set_marken(self, an: bool) -> None:
        self.marken = bool(an)
        self.ansicht.set_ansicht(textgrenzen=self.marken)

    def set_gitter(self, an: bool) -> None:
        self.gitter = bool(an)
        self.ansicht.set_ansicht(gitter=self.gitter)

    def set_zeilenfokus(self, an: bool) -> None:
        self.zeilenfokus = bool(an)
        self.ansicht.set_ansicht(zeilenfokus=self.zeilenfokus)

    def set_lesehilfe(self, papier, buchstaben: float = 0.0, wort: float = 0.0) -> None:
        """Lesehilfe: Blattfarbe sowie zusätzlicher Buchstaben- und Wortabstand (Bildpunkte)."""
        self.ansicht.set_ansicht(papier=str(papier), buchstaben=float(buchstaben), wort=float(wort))

    def set_zeilenluft(self, faktor: float) -> None:
        self.ansicht.set_ansicht(zeilenluft=float(faktor))

    def set_versteckt_zeigen(self, an: bool) -> None:
        self.ansicht.set_ansicht(versteckt=bool(an))

    def setAcceptDrops(self, an: bool) -> None:
        self.ansicht.setAcceptDrops(bool(an))

    def set_silbenfarben(self, k) -> None:
        """Lesehilfe „Silbenfarben“ (``k``: ``SilbenEinstellung`` vom Framework): reine Anzeige, das Dokument bleibt unverändert."""
        if not k or not k.an:
            self.ansicht.set_silben(None)
            return
        self.ansicht.set_silben(k)

    def set_lesefokus(self, groesser: float = 1.0, zurueck: float = 1.0) -> None:
        """Lesehilfe: Alles außer dem Absatz der Schreibmarke tritt zurück (``zurueck`` kleiner als 1 = blasser)."""
        self.ansicht.set_ansicht(lesefokus=float(zurueck))

    def objekt_verschieben(self, objekt_id: int, seite: int, rect) -> None:
        """Setzt ein frei positioniertes Objekt an das Rechteck ``rect`` (Seitenkoordinaten der Seite ``seite``): Es hängt danach am Absatz, der dort
        steht, und ist auf dem Blatt festgelegt; Größe folgt dem Rechteck."""
        erg = self.ansicht.ergebnis()
        o = _bearbeiten.dok_objekt(self.kennung, objekt_id)
        anker = o.anker
        treffer = erg.treffer(seite, Punkt(rect.x + 1, rect.y + 1))
        if treffer is not None and erg.seite_von(treffer[0]) == seite:
            anker = treffer[0]
        self.objekt_setzen(objekt_id, anker=anker, bezug_h="seite", x=float(rect.x), ausr_h="", bezug_v="seite", y=float(rect.y), ausr_v="",
                           breite=float(rect.width), hoehe=float(rect.height))

    def objekt_ebene(self, wohin: str) -> bool:
        """Stapelreihenfolge des gewählten Objekts: ``vorn``, ``hinten``, ``vor``, ``zurueck``."""
        oid = self.ansicht.gewaehltes_objekt
        return oid is not None and self.ansicht._befehl(lambda: _bearbeiten.aenderung_objekt_ebene(self.kennung, oid, wohin))

    def objekt_loeschen(self) -> bool:
        oid = self.ansicht.gewaehltes_objekt
        if oid is None:
            i = self.inline_gewaehlt()
            return i is not None and self.ansicht._befehl(lambda: _bearbeiten.aenderung_objekt_entfernen(self.kennung, i.id))
        ok = self.ansicht._befehl(lambda: _bearbeiten.aenderung_objekt_entfernen(self.kennung, oid))
        self.ansicht.gewaehltes_objekt = None
        self.freiAuswahlGeaendert.emit()
        return ok
