"""Befehle: Zwischenablage und Bearbeiten."""
from __future__ import annotations

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication, QMenu
from lunivo_writer.ui.baukasten.dialog_rahmen import knopfzeile


class BearbeitenBefehle:
    """Befehle des Bandes: Zwischenablage und Bearbeiten. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``)."""


    # ---- Zwischenablage ------------------------------------------------------------------
    def einfuegen(self, k=None):
        if self.ed: self.ed.paste()


    def einfuegenOhne(self, k=None):
        self.w.paste_plain()


    def menue_einfuegenKlappe(self):
        """Wie in der Vorlage: mit Formatierung, passend zum Ziel formatiert, als unformatierter Text, „Inhalte einfügen …“ und
        „Standard zum Einfügen festlegen …“ (Optionen ▸ Schreiben ▸ Bearbeiten und Einfügen)."""
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        from lunivo_writer.ui.widgets import icons
        m = MenueListe()
        m.eintrag("Formatierter Text", self.einfuegen, symbol=icons.icon("einfFormatiert", 16))
        m.eintrag("Passend formatiert einfügen", self.einfuegenOhne, symbol=icons.icon("einfPassend", 16))
        m.eintrag("Unformatierter Text", self.einfuegenUnformatiert, symbol=icons.icon("einfUnformatiert", 16), kuerzel="Strg+Alt+T")
        m.trenner()
        m.eintrag("Inhalte einfügen …", self.inhalteEinfuegen, symbol=icons.icon("einfInhalte", 16), kuerzel="Strg+Alt+V")
        m.eintrag("Standard zum Einfügen festlegen …", lambda: self.w.show_options("bearbeiten"), symbol=icons.icon("einfStandard", 16))
        return m


    def einfuegenUnformatiert(self, k=None):
        """Nur der Text der Zwischenablage, ohne jede Formatierung (auch nicht die der Einfügestelle): Schrift und Größe des Dokuments."""
        if not self.ed:
            return
        from PySide6.QtGui import QTextCharFormat
        t = QApplication.clipboard().text()
        if t:
            self.ed.textCursor().insertText(t.replace("\r\n", "\n"), QTextCharFormat())


    def inhalteEinfuegen(self, k=None):
        """„Inhalte einfügen …“: aus den Formaten der Zwischenablage eines wählen (mit Formatierung, nur Text, Bild)."""
        if not self.ed:
            return
        from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QListWidget, QVBoxLayout, QLabel
        md = QApplication.clipboard().mimeData()
        optionen = []
        if md.hasText() or md.hasUrls() or md.formats():
            optionen.append(("Mit Formatierung", "formatiert"))
        if md.hasText():
            optionen.append(("Unformatierter Text", "text"))
        if md.hasImage():
            optionen.append(("Bild", "bild"))
        if not optionen:
            return
        d = QDialog(self.w); d.setWindowTitle("Inhalte einfügen"); d.resize(320, 220)
        v = QVBoxLayout(d); v.addWidget(QLabel("Als:"))
        liste = QListWidget(); v.addWidget(liste, 1)
        for text, art in optionen:
            liste.addItem(text); liste.item(liste.count() - 1).setData(0x100, art)
        liste.setCurrentRow(0); liste.itemDoubleClicked.connect(lambda _: d.accept())
        bb = knopfzeile(d); v.addWidget(bb)
        if not d.exec() or liste.currentItem() is None:
            return
        art = liste.currentItem().data(0x100)
        if art == "text":
            self.w.paste_plain()
        elif art == "bild":
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QTextDocument, QTextImageFormat
            img = QApplication.clipboard().image()
            name = f"einfuegen-{id(img)}"
            self.ed.document().addResource(QTextDocument.ImageResource, QUrl(name), img)
            f = QTextImageFormat(); f.setName(name); f.setWidth(min(img.width(), 480)); f.setHeight(img.height() * min(img.width(), 480) / max(1, img.width()))
            self.ed.textCursor().insertImage(f)
        else:
            self.ed.paste()


    def ausschneiden(self, k=None):
        if self.ed: self.ed.cut()


    def kopieren(self, k=None):
        if self.ed: self.ed.copy()


    # ---- Bearbeiten -----------------------------------------------------------------------------------------
    def suchen(self, k=None, *_):
        self.w.find_dialog_show()


    def menue_suchenKlappe(self):
        """„Suchen oder ersetzen“: Suchen, Ersetzen, Gehe zu — alle im Feld der linken Seitenleiste."""
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        from lunivo_writer.ui.widgets import icons
        m = MenueListe()
        m.eintrag("Suchen …", self.suchen, symbol=icons.icon("lupe", 16), kuerzel="Strg+F")
        m.eintrag("Ersetzen …", self.ersetzen, symbol=icons.icon("ersetzen", 16), kuerzel="Strg+H")
        m.eintrag("Gehe zu …", self.geheZu, symbol=icons.icon("gehezu", 16), kuerzel="Strg+G")
        return m


    def ersetzen(self, k=None, *_):
        self.w.find_dialog_show("Ersetzen")

    w_sucheZeigen = suchen


    def allesMarkieren(self, k=None):
        if self.ed: self.ed.selectAll()


    def menue_auswaehlenKlappe(self):
        """„Auswählen“ wie in der Vorlage."""
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        from lunivo_writer.ui.widgets import icons
        m = MenueListe()
        m.eintrag("Alles auswählen", self.allesMarkieren, symbol=icons.icon("allesmark", 16), kuerzel="Strg+A")
        m.eintrag("Objekte auswählen", self.objekteWaehlen, symbol=icons.icon("objekte", 16))
        m.eintrag("Tabelle mit gestricheltem Rahmen auswählen", self.tabelleOhneRahmen, symbol=icons.icon("tabelleWahl", 16))
        m.eintrag("Text mit ähnlicher Formatierung auswählen", self.aehnlicheFormatierung, symbol=icons.icon("aehnlich", 16))
        m.eintrag("Auswahlbereich …", self.auswahlbereich, symbol=icons.icon("auswahlbereich", 16))
        return m


    def tabelleOhneRahmen(self, k=None):
        """Die nächste Tabelle ohne sichtbaren Rahmen (im Text nur gestrichelt angedeutet) ganz markieren."""
        from lunivo_writer.editor import auswahl
        if self.ed and not auswahl.tabelle_ohne_rahmen(self.ed):
            self.w.statusBar().showMessage("Im Dokument gibt es keine Tabelle mit gestricheltem Rahmen.", 4000)


    def aehnlicheFormatierung(self, k=None):
        """Alle Stellen mit derselben Zeichenformatierung wie an der Schreibmarke farbig hinterlegen; die erste wird markiert."""
        from lunivo_writer.editor import auswahl
        if not self.ed:
            return
        bereiche = auswahl.aehnlich_formatiert(self.ed)
        self.ed.set_suchtreffer(bereiche)
        if bereiche:
            self.ed.select_range(*bereiche[0])
        self.w.statusBar().showMessage(f"{len(bereiche)} Stelle(n) mit derselben Formatierung hervorgehoben.", 6000)


    def auswahlbereich(self, k=None):
        """Der Bereich „Auswahl“: alle Bilder, Formen und Tabellen des Dokuments in einer Liste; ein Klick markiert das Objekt."""
        if not self.ed:
            return
        from lunivo_writer.ui.baukasten.auswahl_bereich import AuswahlBereich
        from lunivo_writer.ui.baukasten.fenster_stapel import ausfuehren
        ausfuehren(AuswahlBereich(self.w, self.ed))
