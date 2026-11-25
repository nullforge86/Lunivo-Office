"""Klappen (Pfeilmenüs) im Bereich „Bearbeiten“: Einfügen, Suchen oder Ersetzen, Auswählen."""
from __future__ import annotations

from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
from vcl.qt.widgets.bausteine.symbole.bauteile import symbole


class BearbeitenKlappen:
    def menue_einfuegenKlappe(self):
        """Wie in der Vorlage: mit Formatierung, passend zum Ziel formatiert, als unformatierter Text, „Inhalte einfügen …“ und
        „Standard zum Einfügen festlegen …“ (Optionen ▸ Schreiben ▸ Bearbeiten und Einfügen)."""
        m = MenueListe()
        m.eintrag("Formatierter Text", self.einfuegen, symbol=symbole.icon("einfFormatiert", 16))
        m.eintrag("Passend formatiert einfügen", self.einfuegenOhne, symbol=symbole.icon("einfPassend", 16))
        m.eintrag("Unformatierter Text", self.einfuegenUnformatiert, symbol=symbole.icon("einfUnformatiert", 16), kuerzel="Strg+Alt+T")
        m.trenner()
        m.eintrag("Inhalte einfügen …", self.inhalteEinfuegen, symbol=symbole.icon("einfInhalte", 16), kuerzel="Strg+Alt+V")
        m.eintrag("Standard zum Einfügen festlegen …", lambda: self.w.show_options("bearbeiten"), symbol=symbole.icon("einfStandard", 16))
        return m

    def menue_suchenKlappe(self):
        """„Suchen oder ersetzen“: Suchen, Ersetzen, Gehe zu — alle im Feld der linken Seitenleiste."""
        m = MenueListe()
        m.eintrag("Suchen …", self.suchen, symbol=symbole.icon("lupe", 16), kuerzel="Strg+F")
        m.eintrag("Ersetzen …", self.ersetzen, symbol=symbole.icon("ersetzen", 16), kuerzel="Strg+H")
        m.eintrag("Gehe zu …", self.geheZu, symbol=symbole.icon("gehezu", 16), kuerzel="Strg+G")
        return m

    def menue_auswaehlenKlappe(self):
        """„Auswählen“ wie in der Vorlage."""
        m = MenueListe()
        m.eintrag("Alles auswählen", self.allesMarkieren, symbol=symbole.icon("allesmark", 16), kuerzel="Strg+A")
        m.eintrag("Objekte auswählen", self.objekteWaehlen, symbol=symbole.icon("objekte", 16))
        m.eintrag("Tabelle mit gestricheltem Rahmen auswählen", self.tabelleOhneRahmen, symbol=symbole.icon("tabelleWahl", 16))
        m.eintrag("Text mit ähnlicher Formatierung auswählen", self.aehnlicheFormatierung, symbol=symbole.icon("aehnlich", 16))
        m.eintrag("Auswahlbereich …", self.auswahlbereich, symbol=symbole.icon("auswahlbereich", 16))
        return m
