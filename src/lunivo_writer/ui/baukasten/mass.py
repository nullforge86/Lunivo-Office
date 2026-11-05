"""Zentrale Maße der gemeinsamen Bausteine und Fenster — benannte Konstanten nach Rolle, damit gleiche Werte nur einmal stehen.

Fensterteile (dialogs/, hauptfenster/, backstage.py) und Baukasten holen Radien, Symbolgrößen, Höhen, Breiten, Ränder und Abstände von hier."""
from __future__ import annotations

RADIUS_KLEIN = 4     # kleine Elemente
RADIUS_MITTEL = 8    # Zeilen, kompakte Karten
RADIUS_KARTE = 10    # Karte
RADIUS_CHIP = 11     # Auswahl-Chip, grüner Schalter-Chip

ICON_KLEIN = 14      # Aufklapp-Pfeile
ICON_NORMAL = 16     # Symbol in Panel-Knöpfen
ICON_GROSS = 18      # große Symbole

# Eckenradien (Fortsetzung)
RADIUS_MARKE = 3
RADIUS_EINTRAG = 5
RADIUS_FELD = 6
RADIUS_STUFE = 13
RADIUS_PILLE = 15

# Symbolgrößen (Fortsetzung)
ICON_MITTEL = 22
ICON_LISTE = 24
ICON_KNOPF_GROSS = 28
ICON_KACHEL = 32
ICON_ASSISTENT = 26   # KI-Plus in der rechten Schiene
ICON_VORSCHAU = 40    # Symbole in der Auswahl-Vorschau

HOEHE_ZEILE_SONDER = 27     # Zeile in den Sonderzeichen-Listen
HOEHE_ZELLE_SONDER = 30     # Zelle des Sonderzeichen-Rasters

# Schriftgrößen in pt (Stylesheets)
SCHRIFT_KLEIN = 8
SCHRIFT_HINWEIS = 9
SCHRIFT_LISTE = 11
SCHRIFT_UEBERSCHRIFT_KLEIN = 14
SCHRIFT_VORSCHAU = 15
SCHRIFT_UEBERSCHRIFT = 17

# Höhen (Felder, Knöpfe, Listen, Textbereiche)
HOEHE_FELD = 32
HOEHE_KNOPF = 34
HOEHE_KNOPF_GROSS = 36
HOEHE_KNOPF_HOCH = 40
HOEHE_WAHLKARTE = 48
HOEHE_ZEILE_ZULETZT = 56
HOEHE_TEXT_KURZ = 60
HOEHE_TEXT_MITTEL = 80
HOEHE_TEXT_NORMAL = 90
HOEHE_EINGABE_TEXT = 110
HOEHE_VORSCHAU_KLEIN = 120
HOEHE_BEREICH_MITTEL = 150
HOEHE_LISTE_KURZ = 160
HOEHE_LISTE_MITTEL = 180
HOEHE_LISTE_ZIEL = 190
HOEHE_LISTE_HOCH = 200
HOEHE_LISTE_ANBIETER = 240
HOEHE_LISTE_BEFEHLE = 250
HOEHE_LISTE_REITER = 260
HOEHE_LISTE_KNOEPFE = 280
HOEHE_VORSCHAU_DIAGRAMM = 330
HOEHE_LESEFELD = 360

# Breiten
BREITE_NUMMER = 20
BREITE_KNOPF_PFEIL = 34
BREITE_KNOPF_KLEIN = 36
BREITE_SCHIENE = 48
BREITE_REGLER_MIN = 60
BREITE_SCHIENE_BESCHRIFTET = 80
BREITE_LISTE_ARTEN = 180
BREITE_NAMENSFELD = 190
BREITE_NAVIGATION_OPTIONEN = 250
BREITE_NAVIGATION_BACKSTAGE = 310
BREITE_FELD_BACKSTAGE = 320
BREITE_SEITE_MIN = 520

BREITE_ZEILE_BACKSTAGE = 460   # alle Zeilen der Datei-Ansicht gleich breit
BREITE_KACHEL_VORSCHAU = 64   # Vorschaukachel (Einfügen)

# Feste Größen (Breite, Höhe)
GROESSE_STUFE = (26, 26)
GROESSE_KNOPF_QUADRAT = (34, 34)
GROESSE_KNOPF_SCHIENE = (38, 38)
GROESSE_PLAKETTE = (40, 26)
GROESSE_SYMBOL_JETZT = (40, 40)
GROESSE_KNOPF_SILBE = (44, 26)
GROESSE_KNOPF_KACHEL = (52, 52)
GROESSE_SCHALTER = (56, 30)
GROESSE_KNOPF_SCHIENE_TEXT = (72, 54)
GROESSE_VORSCHAU_QUADRAT = (96, 96)
GROESSE_KNOPF_MIN = (100, 34)
GROESSE_KACHEL_FOTO = (126, 76)   # Außenmaß einer Foto-Kachel (SmartArt)

# Zuschläge zu berechneten Größen
ZUGABE_KNOPF = 12
ZUGABE_RAHMEN = 2
ZUGABE_LISTE_ARTEN = 6
ZUGABE_KACHEL = 10
ZUGABE_LISTE = 8
ZUGABE_LISTE_SONDER = 4
ZUGABE_LISTE_KOPF = 24

# Ränder (links, oben, rechts, unten)  —  setContentsMargins(*RAND_…)
RAND_ABSCHNITT = (0, 6, 0, 8)   # Abschnitt einer Optionsseite
RAND_BACKSTAGE_SEITE = (44, 36, 44, 24)   # Seite der Backstage
RAND_BOX = (8, 8, 8, 8)   # Box mit gleichmäßigem Rand
RAND_BOX_KOMPAKT = (8, 6, 8, 6)   # kompakte Box
RAND_DIALOG_KI = (12, 12, 12, 8)   # Seite Name und KI
RAND_ERWEITERUNG_KARTE = (12, 10, 14, 10)   # Karte der Erweiterungen
RAND_FUSS_BACKSTAGE = (14, 8, 14, 12)   # Fußzeile der Backstage
RAND_FUSS_RECHTS = (24, 10, 24, 14)   # Fuß rechts (Backstage)
RAND_GITTER = (4, 4, 4, 4)   # Gitter mit kleinem Rand
RAND_HILFE_DIALOG = (24, 22, 24, 18)   # Hilfedialog
RAND_HILFE_FUSS = (12, 0, 12, 10)   # Fußleiste im Hilfefenster
RAND_HILFE_SEITE = (12, 0, 12, 0)   # Seitenränder im Hilfefenster
RAND_KARTE_ZEILE = (12, 10, 12, 10)   # Karte/Seite mit Innenrand
RAND_KEIN = (0, 0, 0, 0)   # kein Rand
RAND_KOPF_LINKS = (14, 10, 14, 10)   # Kopf der linken Fläche (Backstage)
RAND_LISTENKOPF = (0, 10, 0, 10)   # Kopf der Backstage-Liste
RAND_OBEN_KLEIN = (0, 4, 0, 0)   # kleiner Abstand oben
RAND_OBEN_SEITE = (0, 8, 0, 0)   # Abstand über dem Seiteninhalt
RAND_PANEL_KLEIN = (6, 6, 6, 6)   # kleines Panel
RAND_SCHIENE = (4, 8, 4, 8)   # Schiene links in der Datei-Ansicht
RAND_SEITE_TITEL = (24, 16, 24, 16)   # Optionsseite mit Titel
RAND_UNTEN = (0, 0, 0, 8)   # Abstand unten
RAND_ZEILE = (0, 4, 0, 4)   # Zeile/Gruppe mit Luft oben und unten
RAND_OPTIONEN_GRUPPE = (9, 9, 9, 9)   # Innenrand einer Optionen-Gruppe (Stilvorgabe des früheren Formulars)
RAND_ZEILE_BACKSTAGE = (22, 14, 22, 14)   # Zeile in der Backstage
RAND_ZEILE_ENG = (0, 2, 0, 2)   # enge Zeile
RAND_ZEILE_KARTE = (12, 8, 12, 8)   # Karte mit Texten (Hilfe)
RAND_ZEILE_LOCKER = (0, 6, 0, 6)   # Zeile, großzügiger
RAND_ZEILE_PAAR = (0, 2, 0, 6)   # Zeile mit Wertepaar
RAND_ZEILE_SPALTEN = (0, 4, 0, 6)   # Zeile mit Spalten
RAND_ZULETZT_ZEILE = (52, 6, 12, 6)   # Zeile der Zuletzt-Liste

# Abstände zwischen Elementen (Layout.setSpacing)
ABSTAND_KEIN = 0
ABSTAND_ENG = 2
ABSTAND_ZEILE = 3
ABSTAND_KLEIN = 4
ABSTAND_NORMAL = 6
ABSTAND_MITTEL = 8
ABSTAND_GROSS = 10
ABSTAND_BLOCK = 12
ABSTAND_SPALTE = 14
ABSTAND_PAAR = 18
ABSTAND_SPALTEN = 24

# Fenstergrößen, Raster und weitere Maße der Fenster (Breite, Höhe) bzw. Einzelwerte
BREITE_FELD_ORT = 380
BREITE_FELD_ZEICHENCODE = 120
BREITE_SEITENLEISTE = 300
BREITE_SEITE_MAX = 860
BREITE_VORSCHAU_DIAGRAMM = 620
BREITE_VORSCHAU_DIAGRAMM_SCHMAL = 390
BREITE_ZEILENHINWEIS = 10   # Breitenangabe im Größenhinweis von Listenzeilen (die Liste bestimmt die Breite)
GROESSE_BILD_DIAGRAMM = (84, 64)
GROESSE_BILD_DIAGRAMM_SCHMAL = (70, 54)
GROESSE_FENSTER_ANBIETER = (444, 560)
GROESSE_FENSTER_AUSWAHL = (520, 520)
GROESSE_FENSTER_EINFUEGEN_GROSS = (840, 600)
GROESSE_FENSTER_HANDBUCH = (460, 780)
GROESSE_FENSTER_KI = (620, 520)
GROESSE_FENSTER_MCP = (444, 360)
GROESSE_FENSTER_NAME_KI = (920, 660)
GROESSE_FENSTER_OPTIONEN = (1000, 680)
GROESSE_FENSTER_SENDUNG = (560, 420)
GROESSE_FENSTER_SERIENBRIEF = (720, 440)
GROESSE_FENSTER_SONDERZEICHEN = (444, 560)
GROESSE_FENSTER_TABELLE = (520, 360)
GROESSE_FENSTER_VERWEIS = (560, 420)
GROESSE_FENSTER_VORLAGEN = (560, 460)
GROESSE_MINIATUR_LAYOUT = (360, 240)
GROESSE_RASTER_DATEIEN = (140, 26)
GROESSE_RASTER_SYMBOLE = (90, 70)
HOEHE_ABSTAND_LISTE = 54
HOEHE_LISTE_AUSWAHL = 130
HOEHE_NAVIGATION_HILFE = 210
BREITE_NAVIGATION_HILFE = 290   # Themenliste links im breiten Handbuch
HOEHE_TRENNER_LISTE = 16
HOEHE_ZEILE_ABSCHNITT = 30
HOEHE_ZEILE_ERWEITERUNG_KOPF = 52

# Eckenradien nach Rolle
RADIUS_LEISTENKNOPF = 2   # Eckenrundung flacher Werkzeugknöpfe (Tabellengriffe, Kopf-/Fußzeilen-Leiste)
RADIUS_RUNDE_OPTION = 7   # Auswahlkreis der Optionsknöpfe im Kopf-/Fußzeilen-Panel
RADIUS_ZAHLENFELD_KLEIN = 2   # Zahlenfeld der Seitenzahl-Zeile (Kopf-/Fußzeile)
RADIUS_REGLER_RINNE = 2   # Rinne der Schieberegler
RADIUS_REGLER_GRIFF = 7   # Griff der Schieberegler (rund)

# Symbolgrößen nach Rolle
ICON_TEXTFORMATLEISTE = 20   # Symbole der Textformat-Leiste (Zeilenabstand, Einzug, Aktionen)
ICON_FORMENLISTE = 20   # Symbole der Formenliste im Dialog „Umschlossene Zeichen“
ICON_FREIBILD_BEDIENUNG = 20   # Bedienknöpfe auf freien Bildern
ICON_SPEICHERN_KACHEL = 40   # Symbole der Kachelansicht im Speichern-Fenster
ICON_SPEICHERN_WERKZEUG = 20   # Werkzeugknöpfe im Speichern-Fenster
ICON_SPEICHERN_ORT = 20   # Symbole der Orte-Liste im Speichern-Fenster
ICON_PFADTRENNER = 12   # Pfeil zwischen den Pfadteilen im Speichern-Fenster
ICON_VORLAGE_PLATZHALTER = 56   # Platzhalter-Symbol einer leeren Vorlagenkachel
ICON_SCHWEBKNOPF = 26   # Symbol des schwebenden Knopfs
ICON_TAB_GEAENDERT = 10   # Änderungspunkt im Tab-Titel

# Schriftgrößen in pt nach Rolle
SCHRIFT_BANDGRUPPE_TITEL = 7   # Gruppenbeschriftung im Band
SCHRIFT_LESEENDEKNOPF = 12   # Beschriftung des Lesemodus-Beenden-Knopfs
SCHRIFT_BANDKNOPF = 16   # Beschriftung der Bandknöpfe

# Höhen nach Rolle
HOEHE_NOTENFELD = 84   # Eingabefeld der Notenzeile
HOEHE_EINGABEFELD = 30   # Eingabefeld im Eingabefenster
HOEHE_KOPFDROPDOWN = 30   # Kopf-Auswahlknopf (Symbol mit Pfeil)
HOEHE_LESEENDE_KNOPF = 30   # Lesemodus-Beenden-Knopf in der Statusleiste
HOEHE_LINIENZEILE = 30   # Zeile mit Linienart-Auswahl
HOEHE_TABSTOPP_LISTE_MAX = 72   # Höchsthöhe der Tabstopp-Liste
HOEHE_POPUP_SEITE = 340   # Bildlauffläche der Seiten in den Diagramm-Popups (Farben, Vorlagen)
HOEHE_SUCHOPTION = 28   # Optionsfelder der Suchleiste
HOEHE_THEMAKNOPF = 24   # Themenknopf in der Statusleiste
HOEHE_LISTENZEILEN_KNOPF = 22   # Mindesthöhe von Knöpfen in Listenzeilen (Stylesheet)
HOEHE_TRENNLINIE_MAX = 1   # Höchsthöhe waagerechter Trennlinien (Stylesheet)
HOEHE_BANDREITER_KNOPF = 24   # Mindesthöhe der Knöpfe in der Bandreiter-Leiste (Stylesheet)
HOEHE_LISTENVORSCHAU = 84   # Vorschaufläche im Listen-Dialog
HOEHE_BAND_GRUPPENKNOPF = 62   # Gruppenknopf im Band: Höhe
HOEHE_BAND_GRUPPENKNOPF_KOMPAKT = 56   # Gruppenknopf im Band: Höhe, kompakt

# Breiten nach Rolle
BREITE_AB_ZWEISPALTER = 760   # Ab dieser Breite stehen die zwei Spalten eines Zweispalters nebeneinander
BREITE_ABSTANDSFELD = 100   # Abstandsfeld der Symbolleiste
BREITE_BEREICHSLISTE_POPUP = 330   # Mindestbreite der Bereichsliste im Diagramm-Popup
BREITE_EINHEITENAUSWAHL = 46   # Einheitenauswahl neben dem Maßfeld
BREITE_SCHRIFTAUSWAHL_LEISTE = 160   # Schriftauswahl in der Symbolleiste
BREITE_SCHRIFTGROESSE_MINILEISTE = 50   # Schriftgrößenauswahl der Mini-Leiste
BREITE_GRUPPENTRENNER = 3   # Trennstrich zwischen Bandgruppen
BREITE_GALERIE_HINWEIS_MIN = 120   # Mindestbreite des Hinweistexts am Fuß der Vorlagengalerie
BREITE_MASSFELD_BAND = 64   # Maßfeld im Band
BREITE_RANDFELD_BAND = 72   # Randfeld im Band
BREITE_DRUCKVORSCHAU_SYMBOLKNOPF = 32   # Symbolknopf der Druckvorschau
BREITE_LEISTENKNOPF_MIN = 28   # Mindestbreite der Knöpfe in Symbolleisten
BREITE_KOPFDROPDOWN = 64   # Mindestbreite des Kopf-Auswahlknopfs
BREITE_ZOOMANZEIGE = 52   # Zoomanzeige in der Statusleiste
BREITE_MEHRKNOPF = 16   # Mehr-Knopf der Bandgruppe
BREITE_MENUETAFEL = 330   # Breite der Menütafel
BREITE_SEITENZAHL_FELD = 64   # Startnummernfeld der Seitenzahl-Zeile
BREITE_MINILEISTE_KNOPF = 26   # Mindestbreite der Mini-Leisten-Knöpfe
BREITE_ORDNERNAME_DIALOG = 440   # Mindestbreite der Abfrage „Ordnername“
BREITE_AUFKLAPPPFEIL = 18   # Aufklapp-Pfeil der Bandknöpfe
BREITE_SCHMAL_BESCHRIFTUNG = 40   # Mindestbreite der Beschriftung in schmalen Zeilen
BREITE_SCHREIBHILFE_MIN = 300   # Mindestbreite der Schreibhilfe-Seitenleiste
BREITE_SCHREIBHILFE_MAX = 420   # Höchstbreite der Schreibhilfe-Seitenleiste
BREITE_SCHRIFTAUSWAHL_MINILEISTE = 128   # Schriftauswahl der Mini-Leiste
BREITE_SPEICHERN_KNOPF = 120   # Mindestbreite der Speichern-/Abbrechen-Knöpfe
BREITE_FORMATVORLAGE_BAND = 150   # Formatvorlagenfeld im Band
BREITE_VORLAGEN_AKTUALISIEREN = 84   # Knopf „Formatvorlagen aktualisieren“ im Band
BREITE_FORMATVORLAGE_LEISTE = 130   # Formatvorlagenfeld der Symbolleiste
BREITE_VORLAGENSUCHE = 420   # Suchfeld der Vorlagengalerie
BREITE_FUNKTIONSSYMBOL = 22   # Symbolspalte der Funktionszeile
BREITE_FELDKNOPF_MIN = 72   # Mindestbreite der Feldknöpfe (Stylesheet)
BREITE_BANDREITER_KNOPF = 24   # Mindestbreite der Knöpfe in der Bandreiter-Leiste (Stylesheet)
BREITE_UMBRUCHTEXT_MIN = 40   # Mindestbreite umbrechender Texte in schmalen Zeilen
BREITE_VERFOLGEN_KNOPF = 64   # Knopf „Änderungen verfolgen“
BREITE_LISTENVORSCHAU = 200   # Vorschaufläche im Listen-Dialog
BREITE_DRUCKVORSCHAU_ZOOMKNOPF = 30   # Zoomknopf der Druckvorschau
BREITE_ZOOM_REGLER = 120   # Zoomregler der Statusleiste
BREITE_EINGABEFENSTER = 300   # Breite des Eingabefensters
BREITE_BAND_GRUPPENKNOPF = 84   # Gruppenknopf im Band: Breite

# Feste Größen nach Rolle (Breite, Höhe): Fenster, Knöpfe, Kacheln, Bilder
GROESSE_FENSTER_ABSATZ = (574, 560)   # Fenstergröße Absatz
GROESSE_RAHMENART_BILD = (150, 16)   # Linienart-Bilder der Rahmenartenliste
GROESSE_LINIENART_AUSWAHL_BILD = (44, 14)   # Bild in der Linienart-Auswahl
GROESSE_LINIENBREITE_BILD = (40, 12)   # Linienbreite-Bilder der Auswahl
GROESSE_FENSTER_DRUCKEN = (444, 820)   # Fenstergröße Drucken
GROESSE_FENSTER_DRUCKVORSCHAU = (1100, 800)   # Fenstergröße Druckvorschau
GROESSE_EINFUEGKNOPF = (92, 80)   # Einfügeknopf im Kopf-/Fußzeilen-Panel
GROESSE_EINFUEGKNOPF_BILD = (40, 50)   # Bild des Einfügeknopfs
GROESSE_FARBFLAECHE = (285, 215)   # Farbfläche des Farbwählers
GROESSE_FENSTER_FORMATVORLAGE = (614, 520)   # Fenstergröße Formatvorlage
GROESSE_EBENENZEILE = (30, 28)   # Zeile der Ebenenliste im Gliederungs-Dialog
GROESSE_FENSTER_GLIEDERUNG_ANPASSEN = (718, 348)   # Fenstergröße Gliederung anpassen
GROESSE_GRUPPEN_STARTER = (14, 14)   # Dialogstarter-Knopf der Bandgruppe
GROESSE_SPEICHERN_KACHEL = (110, 90)   # Rasterzelle der Kachelansicht im Speichern-Fenster
GROESSE_EXPORTKARTE = (124, 120)   # Vorschaukarte im Bildexport
GROESSE_PANELKNOPF = (30, 30)   # Knopf im Kopf von Seitenpanels
GROESSE_SPEICHERN_WERKZEUGKNOPF = (36, 34)   # Werkzeugknopf im Speichern-Fenster
GROESSE_WINKELKNOPF = (36, 36)   # Knopf des Winkelfelds
GROESSE_SCHLIESSEN_KNOPF = (28, 28)   # Schließen-Knopf im Panelkopf
GROESSE_TEXTEFFEKT_LINIENART_BILD = (86, 14)   # Linienart-Bilder im Texteffekt-Fenster
GROESSE_FARBREGLER = (26, 215)   # Helligkeitsleiste des Farbwählers
GROESSE_LESEENDEKNOPF = (240, 48)   # Lesemodus-Beenden-Knopf
GROESSE_FENSTER_LISTE = (694, 435)   # Fenstergröße Nummerierung und Aufzählung
GROESSE_FENSTER_NUMMERIERUNG_ANPASSEN = (359, 403)   # Fenstergröße Nummerierung anpassen
GROESSE_ORDNERNAME_KNOPF = (120, 36)   # Knöpfe der Abfrage „Ordnername“
GROESSE_FENSTER_RAHMENABSTAND = (345, 328)   # Fenstergröße Rahmen-Abstände (Polster)
GROESSE_FARBPROBE = (72, 56)   # Farbprobe im Farbwähler
GROESSE_FENSTER_RAHMEN_SCHATTIERUNG = (783, 481)   # Fenstergröße Rahmen und Schattierung
GROESSE_RAHMENSEITE_KNOPF = (40, 38)   # Kantenknopf der Rahmenseite
GROESSE_FARBRING = (270, 250)   # Farbring des Farbwählers
GROESSE_FENSTER_PHONETISCH = (430, 420)   # Fenstergröße Phonetische Hilfe
GROESSE_FENSTER_SCHRIFTART = (504, 560)   # Fenstergröße Schriftart
GROESSE_SCHWEBKNOPF = (48, 48)   # Schwebender Knopf
GROESSE_FENSTER_SEITENRAND = (635, 478)   # Fenstergröße Seitenrand-Optionen
GROESSE_SCHNELLLAYOUT_KNOPF = (100, 92)   # Knopf der Schnelllayout-Auswahl
GROESSE_SCHNELLLAYOUT_BILD = (92, 84)   # Bild im Schnelllayout-Knopf
GROESSE_FENSTER_SPEICHERN = (1040, 660)   # Fenstergröße Speichern
GROESSE_TABELLENKNOPF_MINILEISTE = (50, 54)   # Tabellenknöpfe der Mini-Leiste
GROESSE_FENSTER_TABSTOPP = (550, 340)   # Fenstergröße Tabstopps
GROESSE_FENSTER_TASTENKOMBINATION = (311, 122)   # Fenstergröße Tastenkombination
GROESSE_TEILMENUEKNOPF = (36, 32)   # Knopf „Diagrammteil wählen“
GROESSE_FENSTER_TEXTEFFEKT = (422, 558)   # Fenstergröße Texteffekt
GROESSE_UMSCHLOSSEN_VORLAGENBILD = (56, 40)   # Vorlagenbild im Dialog „Umschlossene Zeichen“
GROESSE_UNTERSTREICHUNG_BILD = (70, 14)   # Unterstreichungsbild der Schriftart-Auswahl (zunächst)
GROESSE_UNTERSTREICHUNG_BILD_HOCH = (70, 16)   # Unterstreichungsbild der Schriftart-Auswahl (endgültig)
GROESSE_RAHMENVORSCHAU = (190, 130)   # Vorschau im Rahmen-Dialog
GROESSE_ABSCHLUSS_KACHEL = (40, 40)   # Kachel im Menü „Abschluss“
GROESSE_LINIENART_BILD = (56, 14)   # Standardbild einer Linienart
GROESSE_STRICHART_MENUEBILD = (120, 16)   # Strichart-Bild im Objektmenü
GROESSE_SMARTART_STIL_BAND = (70, 48)   # Stilkachel im Band
GROESSE_SMARTART_LAYOUT_MINIATUR = (28, 20)   # Miniatur eines SmartArt-Layouts
GROESSE_LINIENBREITE_BILD_STANDARD = (74, 12)   # Standardbild einer Linienbreite
GROESSE_FORMSTIL_KACHEL = (50, 34)   # Formstil-Kachel
GROESSE_FORMBILD_KACHEL = (28, 28)   # Formbild im Bild-Menü
GROESSE_VERLAUF_KACHEL = (34, 24)   # Verlaufskachel
GROESSE_TEXTUR_MUSTER_KACHEL = (30, 30)   # Textur- und Musterkachel
GROESSE_MUSTER_KACHEL = (18, 18)   # Musterkachel der Füllvorgaben
GROESSE_FUELLVORGABE_KACHEL = (16, 16)   # Füllvorgabe-Kachel
GROESSE_GALERIE_KACHEL = (78, 56)   # Kachel der Galerieauswahl
GROESSE_VORGABEMENUE_RAND = (10, 8)   # Zuschlag zur Kachel des Voreinstellungsmenüs
GROESSE_FENSTER_STAPEL = (830, 670)   # Größe des Fensterstapels
GROESSE_FORMLINIE_KACHEL = (26, 22)   # Linienkachel im Formenmenü
GROESSE_KACHELFELD_STANDARD = (44, 44)   # Standardkachel des Kachelfelds
GROESSE_LAYOUTOPTIONEN_KACHEL = (40, 40)   # Kachel der Layoutoptionen
GROESSE_SPALTENRASTER_KACHEL = (46, 32)   # Kachel des Spaltenrasters im Objektmenü
GROESSE_RASTER_STANDARD_KACHEL = (56, 56)   # Standardkachel der Rasterauswahl
GROESSE_SMARTART_MINIATUR = (64, 48)   # Standardminiatur im SmartArt-Menü
GROESSE_RASTERKACHEL_RAND = (10, 10)   # Zuschlag zur Kachel der Rasterauswahl
GROESSE_BANDKNOPF_ICON_KLEIN = (18, 18)   # Kleines Symbol der Bandknöpfe
GROESSE_STRICHART_MENUESYMBOL = (16, 16)   # Symbol des Menüs „Strichart“
GROESSE_OBJEKTLAYOUT_KACHEL = (50, 50)   # Kachel der Objekt-Layoutoptionen
GROESSE_LINIENVORGABE_KACHEL = (100, 26)   # Linienvorgabe-Kachel
GROESSE_LISTENSTIL_KACHEL = (144, 102)   # Listenstil-Kachel
GROESSE_RAHMENKANTEN_MIN = (60, 44)   # Mindestgröße der Rahmenkanten-Vorschau
GROESSE_SMARTART_STIL_POPUP = (70, 48)   # Stilkachel im Popup
GROESSE_STILKACHEL_RAND = (14, 12)   # Zuschlag zur Stilkachel im Popup
GROESSE_KOPFDROPDOWN_WUNSCH = (88, 30)   # Wunschgröße des Kopf-Auswahlknopfs
GROESSE_RAHMENKANTEN_WUNSCH = (220, 160)   # Wunschgröße der Rahmenkanten-Vorschau
GROESSE_DIAGRAMMSTIL_KACHEL = (88, 56)   # Diagrammstil-Kachel
GROESSE_SMARTART_STIL_GALERIE = (56, 34)   # Stilkachel der SmartArt-Galerie
GROESSE_DIAGRAMMSTIL_POPUP = (136, 80)   # Stilkachel im Diagramm-Popup
GROESSE_SMARTART_STIL_MENUE = (46, 40)   # Stilkachel im SmartArt-Menü
GROESSE_STRICHART_KACHEL = (150, 22)   # Strichart-Kachel
GROESSE_KOPFDROPDOWN_SYMBOL = (64, 16)   # Symbol des Kopf-Auswahlknopfs
GROESSE_VORGABEMENUE_KACHEL = (52, 40)   # Standardkachel des Voreinstellungsmenüs
GROESSE_VORLAGE_KACHEL = (186, 243)   # Vorlagenkachel
GROESSE_TEXTVERFORMUNG_KACHEL = (48, 36)   # Textverformungs-Kachel

# Ränder nach Rolle (links, oben, rechts, unten)
RAND_EXPORT_ABSCHNITT = (0, 8, 0, 8)   # Abschnitt der PDF-Export-Ansicht
RAND_DIALOG_GRUPPE = (0, 6, 0, 2)   # Gruppenfeld (Gruppenrahmen) in Dialogen
RAND_DRUCK_SPALTEN = (0, 14, 0, 0)   # Randspalten des Drucken-Fensters (breit)
RAND_DRUCKVORSCHAU_SEITEN = (20, 20, 20, 20)   # Seitenbereich der Druckvorschau
RAND_MINILEISTE = (3, 3, 3, 3)   # Außenrand der Mini-Leiste
RAND_EXPORT_BILD = (16, 20, 16, 16)   # Bildexport-Ansicht
RAND_FORMATSEITE = (0, 10, 0, 6)   # Seiten der Formatpanels (Diagramm, Texteffekt, Füllung)
RAND_DOKUMENTREITER = (6, 3, 6, 8)   # Leiste der Dokumentreiter
RAND_DOKUMENTFLAECHE = (12, 12, 12, 12)   # Dokumentfläche
RAND_FENSTER_DRUCKEN = (0, 0, 0, 12)   # Drucken-Fenster
RAND_DRUCK_SEITE = (16, 6, 16, 12)   # Seiten (Drucker, Programm, Standard) im Drucken-Fenster
RAND_EINFUEGEN_PANEL = (10, 8, 10, 10)   # Einfügen-Panel der Kopf-/Fußzeile
RAND_FENSTERSTAPEL_KOPF = (10, 6, 10, 6)   # Kopf des Fensterstapels
RAND_FORMATIERUNG_SEITENLEISTE = (20, 8, 20, 12)   # Formatierungsbereich der Seitenleiste
RAND_FUNDKARTE = (14, 12, 12, 12)   # Fundstellen-Karte der Schreibhilfe
RAND_FUNKTIONSZEILE = (8, 3, 8, 3)   # Zeile der Funktionsliste
RAND_POPUP_FUSS = (0, 2, 0, 0)   # Fußzeile der Diagramm-Popups
RAND_DRUCK_FUSS = (14, 8, 14, 0)   # Fußbereich des Drucken-Fensters
RAND_RASTER_FUSS = (0, 0, 0, 4)   # Fußbereich der Rasterauswahl
RAND_VORLAGEN_FUSS = (0, 8, 0, 12)   # Fußzeile der Vorlagengalerie
RAND_TEXTEFFEKT_GITTER = (0, 0, 0, 6)   # Gitter im Texteffekt-Fenster
RAND_KARTE_NAVIGATION = (10, 8, 10, 8)   # Karten der Navigation (Kommentare, Überschriften)
RAND_BANDGALERIE = (3, 3, 3, 3)   # Galerie im Band
RAND_MENUE_KOPF = (6, 4, 6, 4)   # Kopf der Bild-/Diagramm-Menüs
RAND_POPUP_KOPF = (6, 2, 6, 0)   # Kopf der Diagramm-Popups
RAND_LAYOUTOPTIONEN = (10, 8, 10, 8)   # Fenster Layoutoptionen
RAND_SEITENLEISTE_TABS = (10, 8, 10, 0)   # Reiterleiste der Seitenleiste
RAND_FENSTER_LISTE = (10, 10, 10, 10)   # Fenster Nummerierung und Aufzählung
RAND_SEITENZAHL_ZEILE = (8, 4, 8, 4)   # Seitenzahl-Zeile der Kopf-/Fußzeile
RAND_ORDNERNAME_DIALOG = (24, 20, 24, 20)   # Abfrage „Ordnername“
RAND_EXPORT_WEITERE = (8, 2, 0, 2)   # Weitere Einstellungen der PDF-Export-Ansicht
RAND_SPEICHERN_PFAD = (4, 1, 4, 1)   # Pfadleiste im Speichern-Fenster
RAND_PFADTRENNER = (2, 0, 2, 0)   # Pfeil zwischen Pfadteilen
RAND_RAHMEN_SEITE = (10, 8, 10, 6)   # Seite „Rahmen“
RAND_BANDREITER = (6, 2, 6, 0)   # Reiterkopf des Bands
RAND_EXPORT_FENSTER = (16, 20, 16, 16)   # Fensterrand der PDF-Export-Ansicht
RAND_SCHATTIERUNG_SEITE = (10, 10, 10, 10)   # Seite „Schattierung“
RAND_EXPORT_SCHUTZ = (0, 2, 0, 4)   # Schutzbereich der PDF-Export-Ansicht
RAND_FARBWAEHLER_SEITE = (6, 8, 6, 6)   # Seite des Farbwählers
RAND_SEITENBILDER = (16, 16, 16, 16)   # Seitenbilder-Ansicht
RAND_EXPORT_SEITENZEILE = (25, 0, 0, 0)   # Seitenbereichszeile der PDF-Export-Ansicht
RAND_POPUP_SEITE = (8, 4, 8, 6)   # Seiten der Diagramm-Popups (Farben, Filter, Namen, Vorlagen)
RAND_POPUP_FILTERGRUPPE = (18, 0, 0, 4)   # Gruppe der Filterseite
RAND_ZUSATZPANEL_SEITE = (12, 8, 12, 10)   # Seite des Zusatzpanels
RAND_SPEICHERN_LINKS = (18, 22, 12, 12)   # Linke Spalte des Speichern-Fensters
RAND_SPEICHERN_RECHTS = (16, 14, 16, 16)   # Rechte Spalte des Speichern-Fensters
RAND_ETIKETT = (6, 2, 6, 2)   # Etiketten im Kopf-/Fußzeilen-Panel
RAND_STATUSLEISTE = (10, 0, 10, 0)   # Statusleiste
RAND_POPUP_UNTERTEXT = (26, 0, 0, 2)   # Untertext eingerückter Popup-Einträge
RAND_SYMBOLLEISTE = (6, 2, 6, 2)   # Symbolleisten
RAND_FARBWAEHLER_TRANSPARENZ = (6, 0, 6, 0)   # Transparenzzeile des Farbwählers
RAND_VORLAGENGALERIE = (36, 28, 36, 0)   # Vorlagengalerie
RAND_VORSCHLAGKARTE = (10, 6, 8, 6)   # Vorschlagskarte der Schreibhilfe
RAND_SCHREIBHILFE_BANNER = (0, 0, 0, 6)   # KI-Banner der Seitenleiste
RAND_ZELLENRASTER = (8, 6, 8, 8)   # Zellenraster
RAND_ZUSCHNEIDEN_KACHELN = (6, 0, 6, 0)   # Kachelgitter des Zuschneiden-Menüs
RAND_ZUSCHNEIDEN_LISTE = (6, 4, 6, 4)   # Liste des Zuschneiden-Menüs

# Abstände zwischen Elementen nach Rolle
ABSTAND_EXPORT_ABSCHNITT = 5   # Elemente im Exportabschnitt
ABSTAND_DRUCKVORSCHAU_SEITEN = 16   # Seiten der Druckvorschau
ABSTAND_DICHT = 1   # Dichte Stapelung (1 px) in Band und Popups
ABSTAND_KARTENZEILE = 5   # Knöpfe in der Kartenzeile der Navigation
ABSTAND_SEITENBILDER = 16   # Seitenbilder

# Innenabstände in Stylesheets nach Rolle
PADDING_ABSCHNITTSBAND = '5px 8px'   # Titelband eines Abschnitts
PADDING_SCHALTER_CHIP = '3px 12px'   # Schalter-Chip
PADDING_PLAKETTE = '3px'   # Plakette (Badge) im Startbereich
PADDING_RASTER_FUSSKNOPF = '6px 8px'   # Fußknopf der Rasterauswahl
PADDING_GALERIE_TITEL = '0 2px'   # Titel der Galerieauswahl
PADDING_GRUPPENTITEL = '0 8px 0 0'   # Titel der Gruppenrahmen im Zusatzpanel
PADDING_HANDBUCH_NAVIGATION = '6px 4px'   # Navigationsliste des Handbuchs
PADDING_HILFE_CHIP = '3px 10px'   # Chip im Hilfe-Auswahldialog
PADDING_HINWEIS = '8px'   # Hinweistexte (Leer-, Prüf- und Statushinweise)
PADDING_MARKE = '2px 8px'   # Beschriftungsmarke (Chip)
PADDING_MENUEEINTRAG = '5px 14px 5px 6px'   # Eintrag des Kontextmenüs
PADDING_VORGABEMENUE_KOPF = '3px 2px'   # Kopfzeile des Voreinstellungsmenüs
PADDING_KOPFFUSS_ABSATZKNOPF = '2px 6px'   # Absatzknöpfe der Kopf-/Fußzeilen-Leiste
PADDING_KOPFFUSS_PANELKNOPF = '3px'   # Knöpfe im Kopf-/Fußzeilen-Panel
PADDING_KOPFFUSS_PANELTASTE = '3px 22px'   # Tasten im Kopf-/Fußzeilen-Panel
PADDING_LINKS_MENUESYMBOL = '2px'   # Symbol im Menüeintrag (links)
PADDING_LINKS_BACKSTAGE_LISTE = '18px'   # Einzug der Backstage-Listeneinträge (links)
PADDING_LINKS_OPTIONEN_HINWEIS = '26px'   # Einzug des Optionen-Hinweises (links)
PADDING_LINKS_SPEICHERN_ORT = '10px'   # Einzug der Orte-Liste (links)
PADDING_LESEENDEKNOPF = '8px 24px'   # Lesemodus-Beenden-Knopf
PADDING_HANDBUCH_EINTRAG = '4px 10px'   # Eintrag der Handbuch-Navigation
PADDING_KI_ANBIETER_EINTRAG = '11px 14px'   # Anbieter-Eintrag im KI-Dialog
PADDING_KI_LISTENEINTRAG = '6px 12px'   # Listeneintrag im KI-Dialog
PADDING_MENUE = '3px'   # Kontextmenü
PADDING_MENUETAFEL_KNOPF = '5px 8px'   # Knöpfe der Menütafel
PADDING_ZAHLENFELD_KOPFFUSS = '1px 2px'   # Zahlenfeld der Seitenzahl-Zeile
PADDING_POPUP_LINKKNOPF = '0 6px'   # Unterstrichener Mehr-Knopf der Popups
PADDING_GALERIE_EINTRAG = '6px 8px'   # Eintrag der Galerieauswahl
PADDING_STARTKNOPF_LINK = '4px 0'   # Textknopf im Startbereich
PADDING_NAVIGATION_KNOPF = '4px 8px'   # Zeilenknopf der Navigation
PADDING_SEITENLEISTE_REITER = '4px 6px'   # Reiterknopf der Seitenleiste
PADDING_RECHTS_MENUEKNOPF = '12px'   # Rechter Rand von Knöpfen mit Menü (Stylesheet)
PADDING_SEITENLEISTE_WARNUNG = '5px 0'   # Warnhinweis der Seitenleiste
PADDING_LESEENDE_STATUS = '4px 16px'   # Lesemodus-Knopf der Statusleiste
PADDING_NAVIGATION_EINTRAG = '8px 10px'   # Datei-Eintrag der Backstage bzw. Navigationseintrag der Optionen
PADDING_BACKSTAGE_ZURUECK = '4px 6px'   # Zurück-Knopf der Backstage
PADDING_BACKSTAGE_FERTIG = '9px 30px'   # Knopf „Fertig“
PADDING_BACKSTAGE_KNOPF = '9px 12px'   # Aktionsknopf der Backstage
PADDING_OPTIONEN_GRUPPE = '8px 10px 8px 10px'   # Gruppenrahmen der Optionen
PADDING_OPTIONEN_ERKLAERUNG = '12px 24px'   # Erklärung der Optionen
PADDING_OPTIONEN_VORSCHAU = '16px 20px'   # Vorschau der Optionen
PADDING_OPTIONEN_WAHL = '8px 14px'   # Wahlknopf der Optionen
PADDING_SPEICHERN_TITEL = '4px 6px 14px 6px'   # Titel des Speichern-Fensters
PADDING_SPEICHERN_PFADKNOPF = '2px 4px'   # Pfadknöpfe des Speichern-Fensters
PADDING_SPEICHERN_HAUPTKNOPF = '6px 28px'   # Speichern-Knopf
PADDING_SPEICHERN_DATEIZEILE = '4px 2px'   # Zeile der Dateiliste
PADDING_ZUSATZ_REITER = '5px 10px'   # Reiter des Zusatzpanels
PADDING_WERKZEUGKNOPF_GLOBAL = '2px'   # Werkzeugknöpfe und Schließen-Knöpfe (Stylesheet)
PADDING_KNOPF_GLOBAL = '5px 14px'   # Druckknöpfe (Stylesheet)
PADDING_REITER_GLOBAL = '6px 12px 7px 12px'   # Reiter (Stylesheet)
PADDING_BANDREITER = '6px 14px 4px 14px'   # Reiter des Bands (Stylesheet)
PADDING_BANDREITER_KOMPAKT = '4px 9px 2px 9px'   # Reiter des Bands, kompakt
PADDING_DOKUMENTREITER = '7px 14px'   # Reiter der Dokumente
PADDING_LISTENZEILE_GLOBAL = '4px 6px'   # Listenzeilen-Knöpfe und Kurzinfos (Stylesheet)
PADDING_FELDKNOPF = '3px 10px'   # Feldknöpfe (Stylesheet)
PADDING_EINGABEFELD_GLOBAL = '3px 6px'   # Eingabefelder (Stylesheet)
PADDING_MENUE_GLOBAL = '5px'   # Menüs (Stylesheet)
PADDING_MENUEEINTRAG_GLOBAL = '6px 26px 6px 12px'   # Menüeinträge (Stylesheet)
PADDING_OPTIONSKNOPF_GLOBAL = '3px 0'   # Optionsknöpfe (Stylesheet)
PADDING_GRUPPENTITEL_GLOBAL = '0 4px'   # Gruppentitel (Stylesheet)
PADDING_BAUMEINTRAG_GLOBAL = '4px'   # Einträge von Baum- und Listenansichten (Stylesheet)
PADDING_LAYOUTOPTIONEN_TITEL = '3px 6px'   # Titel der Layoutoptionen
PADDING_ABSCHNITT_KNOPF = '4px 6px'   # Knöpfe der Abschnittsköpfe
PADDING_BACKSTAGE_STEUERKNOPF = '4px 12px'   # Knöpfe der Backstage-Steuerung
PADDING_EDITOR_KNOPF = '2px 6px'   # Knöpfe im Dokumenteditor
PADDING_KOPFFUSS_WERKZEUG = '1px 4px'   # Werkzeugknöpfe der Kopf-/Fußzeilen-Leiste
PADDING_MINILEISTE_KNOPF = '3px'   # Knöpfe der Mini-Leiste
PADDING_BANDKNOPF = '0 3px'   # Bandknöpfe
PADDING_GRUPPE_OBEN = '8px'   # Oberer Innenabstand von Gruppenrahmen
PADDING_PALETTE_TITEL_OBEN = '2px'   # Oberer Abstand der Palettentitel
PADDING_LESEN_VORSCHAU = '16px 20px'   # Vorschau im Lesemodus
PADDING_MENUETAFEL_UNTEREINTRAG = '4px 8px'   # Untereintrag der Menütafel
PADDING_MENUETAFEL_ZULETZT = '3px 6px'   # Zuletzt-Eintrag der Menütafel
PADDING_TASTENKUERZEL = '0 5px'   # Tastenkürzel-Marke im Hilfe-Dialog
PADDING_ZUSCHNEIDEN_KNOPF = '4px 24px'   # Zuschneiden-Menü, Kacheln
PADDING_ZUSCHNEIDEN_ZEILE = '4px 10px'   # Zuschneiden-Menü, Listenzeilen

# Außenabstände in Stylesheets nach Rolle
MARGIN_RECHTS_ZUSATZ_REITER = '2px'   # Abstand zwischen den Reitern des Zusatzpanels
MARGIN_RECHTS_REITER = '2px'   # Abstand zwischen Reitern (Stylesheet)
MARGIN_NAVIGATION_EINTRAG = '1px 8px 1px 0'   # Abstand der Navigationseinträge in den Optionen
MARGIN_MENUETRENNER = '5px 8px'   # Trennlinien in Menüs
MARGIN_SCROLLBALKEN_GRIFF = '2px'   # Griff der Bildlaufleisten
MARGIN_BANDREITER = '0 2px'   # Reiter des Bands
MARGIN_REITER_KOMPAKT = '0 1px'   # Kompakte Reiter (Band, Dokumente)
MARGIN_OBEN_GRUPPE_ZUSATZ = '10px'   # Oberer Abstand der Gruppenrahmen im Zusatzpanel
MARGIN_OBEN_OPTIONEN_GRUPPE = '26px'   # Oberer Abstand der Gruppenrahmen in den Optionen
MARGIN_OBEN_GRUPPE = '12px'   # Oberer Abstand der Gruppenrahmen (Stylesheet)

# Seitenleisten-Panels: EINE Breite für alle Felder links und rechts (Kommentare, Gliederung, Schreibhilfe, KI, Formatierung …)
BREITE_SEITENLEISTE_PANEL = 340

# Kleiner Gruppentitel über Kacheln/Rastern/Paletten (Pixel, wie bisher in Galerie, Raster und Farbpalette)
SCHRIFT_GRUPPENTITEL_PX = 11

# Aktionsknöpfe in Reihe (Prüfen · KI-Korrektur · Vorschläge): Mindestbreite je Knopf, damit alle drei in die Seitenleiste in einer Zeile passen
BREITE_AKTIONSKNOPF_MIN = 100
