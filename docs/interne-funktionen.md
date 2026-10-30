# Interne Funktionen — Inventar

Vollständiges Inventar der Module, Klassen, Funktionen und Methoden von `src/lunivo_writer`. Erzeugt mit `werkzeug/inventar-bauen.py` aus dem Quelltext (`ast`, ohne Import); nicht von Hand ändern, sondern neu erzeugen. Die Beschreibung stammt aus der ersten Docstring-Zeile.

Stand: 303 Module, 326 Klassen, 4492 Funktionen und Methoden.

## Inhalt

- `(Wurzel)` — 3 Module
- `ai` — 5 Module
- `core` — 6 Module
- `core/befehle` — 22 Module
- `editor` — 67 Module
- `models` — 3 Module
- `proofing` — 10 Module
- `services` — 16 Module
- `services/integrations` — 3 Module
- `ui` — 7 Module
- `ui/baukasten` — 62 Module
- `ui/contextual` — 7 Module
- `ui/dialogs` — 22 Module
- `ui/dialogs/optionen_seiten` — 8 Module
- `ui/document` — 24 Module
- `ui/hauptfenster` — 6 Module
- `ui/ribbon` — 6 Module
- `ui/ribbon/tabs` — 12 Module
- `ui/sidebar` — 2 Module
- `ui/sidebar/panels` — 3 Module
- `ui/statusbar` — 2 Module
- `ui/widgets` — 7 Module

## `(Wurzel)`

### `__init__.py`

Lunivo Writer — native Textverarbeitung (Python 3, PySide6/Qt Widgets).


### `__main__.py`


### `app.py`

Einstieg: python -m lunivo_writer [Datei …]

- `main(argv)`

## `ai`

### `ai/__init__.py`

KI-Ebene: Anbieter, Aufgaben, Dienst.


### `ai/ai_service.py`

KI im Programm: Anfragen im Hintergrund, Zustimmung vor jedem Weg nach außen, Ergebnis ins Dokument.

- **class `_Sig`**(QObject)
- **class `_Lauf`**(QRunnable)
  - `__init__(auftrag, arbeit, sig)`
  - `run()`
- **class `KIDienst`**(QObject)
  - `__init__(assistant, fenster, parent)`
  - `_werkzeug_erlaubt(name, argumente, server)` — Aus dem Arbeitsfaden: fragt im Hauptfenster, ob die KI das Werkzeug aufrufen darf, und wartet auf die Antwort.
  - `_werkzeug_fragen(name, argumente, server)`
  - `_hinweis_fenster(titel, text)` — Ein Hinweis, den man nicht übersehen kann (statt nur einer Zeile in der Statusleiste).
  - `merke_ergebnis(titel, text, vorlage)`
  - `verfuegbar()`
  - `zettel(text)`
  - `_einwilligung(modell)`
  - `_eingabe()`
  - `starte(meldung, arbeit, danach, eing)` — arbeit(text) → Ergebnisdict (im Hintergrund); danach(ergebnis, eingabe) im Hauptthread.
  - `_fertig(auftrag, r)`
  - `bild_aus_text(beschreibung)` — Markierter Text (oder der übergebene) ist die Bildbeschreibung; das Bild tritt an die Stelle der Markierung.
  - `_bild_fertig(r, eing)`
  - `_preis(cent)`
  - `_einsetzen(r, eing, ganz_text, markiert_text)`
  - `_anhaengen(r, eing, name)` — Das Ergebnis hinter die Markierung (ohne Markierung: ans Ende des Textes) setzen — als ein Schritt für Rückgängig.
  - `korrigieren()`
  - `uebersetzen(sprache, modus)` — Übersetzen in die gewählte Sprache. ``modus``: „ersetzen“ setzt die Übersetzung an die Stelle der Markierung, „zeigen“ zeigt sie in der Schreibhilfe
  - `text_aktion(aktion)`
  - `assistent(a)` — Schnelle KI-Aktion (Eigener Assistent): ein Name und ein Prompt. Wirkung „ersetzen“ wie Korrigieren, „anhaengen“ hinter den Text, „hinweis“ wie
  - `zusammenfassen()`
  - `analyse()`
  - `vorschlaege_holen()`
  - `thesaurus(danach)` — Synonyme zum Wort am Zeiger; danach(wort, woerter, von, bis) im Hauptthread.
  - `satz_vorschlag(fund, danach)` — Zu einem Hinweis („Langer Satz …“) einen Umschreibe-Vorschlag holen; ``danach(vorschlag)`` bekommt {alt, neu, grund} im Hauptthread.
  - `vorschlag_einsetzen(v)`
  - `chat(verlauf)`

### `ai/ki.py`

Die KI-Ebene: Korrigieren, Vorschläge, Übersetzen, Zusammenfassen, Text bearbeiten, Chat.

- **class `KIKonfig`**
  - `__init__(pfad)`
  - `speichern()`
  - `__getitem__(k)`
  - `setze(k, v)`
  - `anbieter_holen(id_)`
  - `anbieter_hinzufuegen(name, url, schluessel, modell, verwendung)`
  - `anbieter_aktualisieren(id_, name, url, schluessel, modell, verwendung)`
  - `chat_optionen()` — Die erweiterten Einstellungen des KI-Chats (Länge, Temperatur, Top P, Stoppfolgen, Antwort direkt einfügen) mit ihren Vorgaben.
  - `websuche_optionen()`
  - `websuche_setzen(**teile)`
  - `mcp_speichern(id_, name, befehl, an)` — MCP-Server anlegen (``id_`` None) oder ändern.
  - `mcp_entfernen(id_)`
  - `chat_setzen(**teile)`
  - `aufgabe_setzen(aufgabe, modell)`
  - `assistent_hinzufuegen(name, prompt, modus, zugriff)` — Eine „Schnelle KI-Aktion“: ``modus`` = ersetzen \| anhaengen \| hinweis; ``zugriff`` = kontext (Rechtsklick-Menü) \| schnell (Schnellzugriffsleiste).
  - `assistent_entfernen(id_)`
  - `anbieter_entfernen(id_)`
  - `alle_modelle()` — Eine Liste für alle Felder „welches Modell?“: Claude, eigene Anbieter (mit Fähigkeiten und ‚lokal‘).
- `ist_lokale_url(url)`
- `_zettel(z)`
- `steckbrief(gelernt)`
- `anweisung_korrektur(k, gelernt)`
- `anweisung_uebersetzung(sprache)`
- `anweisung_vorschlaege(k)`
- `anweisung_text_aktion(k, aktion)`
- `_nachrichten(text)`
- `ohne_gruebeln(roh)`
- `cent_fuer(modell, verbrauch)`
- `als_geld(cent)`
- `_post(url, kopf, body, timeout)`
- **class `KI`**
  - `__init__(konfig, gelernt)`
  - `modell(aufgabe)`
  - `verfuegbar()`
  - `schickt_nach_aussen(modell)` — Name des Empfängers, wenn der Text das Gerät verlässt — sonst None.
  - `anfrage(anweisung, text, bauplan, modell, optionen)`
  - `_stopp(optionen)`
  - `_claude(anweisung, text, bauplan, modell, optionen)`
  - `_ollama(anweisung, text, bauplan, modell, optionen)`
  - `_eigen(a, anweisung, text, bauplan, optionen)`
  - `_text(anweisung, text, aufgabe, optionen)`
  - `_kosten(cent)`
  - `korrigieren(text)`
  - `uebersetzen(text, sprache)`
  - `zusammenfassen(text)`
  - `text_analyse(text)`
  - `eigener_assistent(text, prompt)`
  - `satz_umschreiben(satz, grund)` — Ein zu langer oder verschachtelter Satz in kürzere Sätze — der Sinn bleibt, nichts kommt dazu.
  - `text_aktion(text, aktion)`
  - `chat(verlauf, dokumenttext)`
  - `_chat_werkzeuge(system, verlauf, server, modell, optionen)` — Chat mit MCP-Werkzeugen über die OpenAI-kompatible Schnittstelle (Ollama und eigene Anbieter): das Modell darf Werkzeuge verlangen; jeder
  - `vorschlaege(text)`
  - `synonyme(wort, umgebung)` — Wörter, die statt `wort` an dieser Stelle stehen könnten (Thesaurus — geht nur mit KI).
  - `bild_erzeugen(beschreibung)` — Bild aus Text: nur eigene Anbieter mit „Bilder“, OpenAI-Schnittstelle POST <URL>/images/generations.
  - `ollama_modelle()`
- `anbieter_modelle(url, schluessel)` — GET <URL>/models — so fragen OpenAI und die meisten OpenAI-kompatiblen Dienste (auch Ollama unter /v1).
- `aenderungen(alt, neu)` — Welche Wörter haben sich geändert? → [{von, bis, text}] in „alt"-Zeichenstellen; None, wenn zu groß.
- `ersetze_ergebnis(alt, neu)` — → (liste_von_ersetzungen (von, bis, text) von hinten nach vorn, ganz: bool, absaetze).

### `ai/mcp.py`

MCP-Server (Model Context Protocol) über die Standard-Ein-/Ausgabe: Werkzeuge auflisten und aufrufen.

- **class `McpFehler`**(Exception)
- **class `McpClient`**
  - `__init__(befehl)`
  - `_neu()`
  - `_lesen()`
  - `_senden(nachricht)`
  - `_antwort(nr)`
  - `werkzeuge()` — [{name, description, inputSchema}] des Servers.
  - `aufrufen(name, argumente)`
  - `schliessen()`
- `pruefen(befehl)` — Verbindung testen: die Werkzeuge des Servers (für „Testen“ im Fenster KI-Einstellungen).

### `ai/websuche.py`

Websuche für den KI-Chat: Treffer holen und als Quellenliste an die Frage hängen.

- `suche(einst, frage, zeit)` — [{titel, url, text}] zur Frage; Fehler werden als Ausnahme gemeldet (OSError, ValueError).
- `als_text(treffer)` — Die Treffer als Quellenliste für die Anweisung an die KI.

## `core`

### `core/__init__.py`

Anwendungskern: Befehle (commands), Pfade — ohne Oberflächenlogik.


### `core/application.py`

Anwendungsstart: QApplication einrichten, Einstellungen und Theme laden, Hauptfenster zeigen, sauber beenden.

- `programm_symbol()` — Lunivos Programmsymbol (assets/symbole/varianten/Abstrakt) in allen vorhandenen Größen.
- **class `LunivoApplication`**
  - `__init__(argv)`
  - `start()`
  - `_abbauen()` — Fenster vor dem Interpreter-Ende abbauen: PySide räumt sonst in falscher Reihenfolge ab (Heap-Fehler beim Beenden).

### `core/commands.py`

Befehle des Bandes: Aktionsname aus register.json → Funktion.

- **class `Befehle`**(AnsichtBefehle, BearbeitenBefehle, BildToolsBefehle, DateiBefehle, DiagrammToolsBefehle, EinfuegenBefehle, ExternBefehle, FormToolsBefehle, KIBefehle, KommentarBefehle, KopfFussBefehle, KontextBefehle, PruefenBefehle, SeiteBefehle, SerienBefehle, SmartArtToolsBefehle, TextBefehle, TextToolsBefehle, UeberpruefenBefehle, VerweiseBefehle) — Alle Befehle des Bandes. Die Grundfunktionen (Aktion suchen, ausführen, Zustand) stehen hier, die Befehle selbst in ``core/befehle/*``.
  - `__init__(win)`
  - `ed()`
  - `_teile(name)` — 'w.setzePapier:["a4"]' → ('w_setzePapier', ['a4'])
  - `hat(name)`
  - `tun(name, knopf)`
  - `zustand(name)`
  - `kann(name)` — Ob der Befehl gerade geht (Befehl ``kann_<name>``); ``None``: keine eigene Bedingung.
  - `band_feld(name)` — Ein Eingabefeld fürs Band (Befehl ``feld_<name>``), z. B. die Nummer des Datensatzes im Seriendruck.
  - `symbolname(name)` — Symbol, das ein Knopf nach seiner letzten Wahl zeigt (Befehl ``symbolname_<name>``); ``None``: der Knopf behält seins.
  - `haken_wert(item)` — Haken eines Menüpunkts: Zustandsfrage des Menüeintrags (z. B. w.randVorgabeJetzt) gegen sein Argument.
  - `klappe(name)`
  - `_popup(menue)` — Menü an der Mausposition zeigen (eigene Stelle, damit Tests es abfangen können).
  - `fehlende(namen)`
  - `_fmt()`

### `core/document_manager.py`

Dokumentverwaltung ohne Oberfläche: Laden, Speichern, automatische Sicherung, Wiederherstellung, zuletzt benutzte Dateien.

- **class `DocumentManager`**
  - `__init__(settings)`
  - `laden(path, kennwort)` — Liest eine Datei; Fehler (DocumentIOError, PasswortNoetig) gehen an den Aufrufer.
  - `meta_fuer_speichern(meta)` — Dokument-Metadaten plus Einstellungen: Verfasser (Benutzername oder gelöscht).
  - `speichern(path, dokument, seite, meta)` — Schreibt das Dokument; gibt den Bericht über nicht Übernommenes zurück.
  - `zuletzt()`
  - `gelesen(path)`
  - `vergessen(path)`
  - `sichern(tabs)` — Automatische Sicherung aller geänderten Dokumente. Fehler stören die Arbeit nie.
  - `wiederherstellbar(offene_token)`
  - `verwerfen(token)`

### `core/farben.py`

Die Grundfarben des Programms mit Namen — der eine Ort, an dem ein Farbwert steht.

- **class `Farbe`**

### `core/paths.py`

Orte der Programmdaten: Ressourcen im Paket, Symbole/Bilder/Schriften unter assets/.


## `core/befehle`

### `core/befehle/__init__.py`

Die Befehle des Bandes, nach Aufgaben in Bausteine (Mixins) geteilt; ``core/commands.py`` setzt sie zu ``Befehle`` zusammen.


### `core/befehle/ansicht.py`

Befehle: Ansicht, Fenster, Zoom.

- **class `AnsichtBefehle`** — Befehle des Bandes: Ansicht, Fenster, Zoom. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `handbuch(k)`
  - `tastenHilfe(k)`
  - `erweiterungen(k)`
  - `vorlagenWaehlen(k)`
  - `vorlagenOrdner(k)`
  - `menueleisteZeigen(k)`
  - `an_menueleisteZeigen()`
  - `registerAnpassen(k)`
  - `schnellzugriffAnpassen(k)`
  - `symbolTauschen(k, name)` — Symbol austauschen (Ansicht ▸ Oberfläche, Optionen — und Rechtsklick auf einen Knopf, dann mit dessen Symbol).
  - `benutzeroberflaeche(k)`
  - `leistenZeigen(k)`
  - `an_leistenZeigen()`
  - `vorlagenZurueck(k)`
  - `neuesFenster(k)`
  - `fensterNebeneinander(k)`
  - `fensterUntereinander(k)`
  - `fensterKacheln(k)`
  - `fensterListe(k)`
  - `w_setzeLayout(k, art)`
  - `w_layoutJetzt(k)`
  - `gliederung(k)`
  - `an_gliederung()`
  - `linealZeigen(k)`
  - `linealHochZeigen(k)`
  - `an_linealZeigen()`
  - `an_linealHochZeigen()`
  - `_zoom_um(faktor)`
  - `groesser(k)`
  - `kleiner(k)`
  - `normal(k)`
  - `zoomBreite(k)`
  - `zoomSeite(k)`
  - `zoomStufe(k)`
  - `lesehilfe(k)`
  - `ausblenden(k)` — Markierten Text als „ausgeblendet“ formatieren (Strg+Umschalt+H).
  - `an_ausblenden()`
  - `versteckteZeigen(k)`
  - `an_versteckteZeigen()`
  - `silbenfarben(k)`
  - `an_silbenfarben()`
  - `silbenEinstellen(k)`
  - `markenZeigen(k)`
  - `an_markenZeigen()`
  - `navigation(k)`
  - `an_navigation()`

### `core/befehle/bearbeiten.py`

Befehle: Zwischenablage und Bearbeiten.

- **class `BearbeitenBefehle`** — Befehle des Bandes: Zwischenablage und Bearbeiten. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `einfuegen(k)`
  - `einfuegenOhne(k)`
  - `menue_einfuegenKlappe()` — Wie in der Vorlage: mit Formatierung, passend zum Ziel formatiert, als unformatierter Text, „Inhalte einfügen …“ und
  - `einfuegenUnformatiert(k)` — Nur der Text der Zwischenablage, ohne jede Formatierung (auch nicht die der Einfügestelle): Schrift und Größe des Dokuments.
  - `inhalteEinfuegen(k)` — „Inhalte einfügen …“: aus den Formaten der Zwischenablage eines wählen (mit Formatierung, nur Text, Bild).
  - `ausschneiden(k)`
  - `kopieren(k)`
  - `suchen(k, *_)`
  - `menue_suchenKlappe()` — „Suchen oder ersetzen“: Suchen, Ersetzen, Gehe zu — alle im Feld der linken Seitenleiste.
  - `ersetzen(k, *_)`
  - `allesMarkieren(k)`
  - `menue_auswaehlenKlappe()` — „Auswählen“ wie in der Vorlage.
  - `tabelleOhneRahmen(k)` — Die nächste Tabelle ohne sichtbaren Rahmen (im Text nur gestrichelt angedeutet) ganz markieren.
  - `aehnlicheFormatierung(k)` — Alle Stellen mit derselben Zeichenformatierung wie an der Schreibmarke farbig hinterlegen; die erste wird markiert.
  - `auswahlbereich(k)` — Der Bereich „Auswahl“: alle Bilder, Formen und Tabellen des Dokuments in einer Liste; ein Klick markiert das Objekt.

### `core/befehle/bildtools.py`

Befehle: Kontext-Reiter „Bildtools“ für frei positionierte Bilder (Datei, Bildschirmfoto, Piktogramm): Zuschneiden, Größe, Farbe.

- **class `BildToolsBefehle`**
  - `_bz()` — Das gewählte freie Bild (``bildlayout``-Ziel) oder None (dann Hinweis in der Statuszeile).
  - `bildZuschneidenModus(k)` — Zuschneiden ein/aus: schwarze Eckwinkel und Kantenstriche; Ziehen schneidet ab (der Zuschnitt wird als Anteil gespeichert).
  - `an_bildZuschneidenModus()`
  - `bildZuschneidenForm(k, name)` — Nach Form zuschneiden: ``name`` ist eine Form des Formenkatalogs (zum Beispiel „Ellipse“, „Herz“).
  - `bildZuschneidenSkala(k, verhaeltnis)` — Nach Skala zuschneiden: Seitenverhältnis wie ``"16:9"``, ``"4:3"``, ``"1:1"`` (mittiger Ausschnitt).
  - `bildZuschneidenZuruecksetzen(k)` — Form und Größe zurücksetzen: Maske und Zuschnitt entfernen, das ganze Bild im ursprünglichen Seitenverhältnis.
  - `menue_bildZuschneiden()` — Klappe „Zuschneiden“: Zuschneiden, Nach Form zuschneiden (Katalog, ohne Linien), Nach Skala zuschneiden, Form und Größe zurücksetzen.
  - `bildGroesseZuruecksetzen(k)` — Größe zurücksetzen: Originalgröße des sichtbaren Ausschnitts in Bildpunkten.
  - `bildSeitenverhaeltnis(k)` — Seitenverhältnis sperren ein/aus (auch Ziehen an den Kanten hält es dann).
  - `an_bildSeitenverhaeltnis()`
  - `bildTransparent(k, toleranz)` — Transparente Farbe: eine Farbe des Bildes wählen (Farbfenster), alle gleichen Bildpunkte werden durchsichtig.
  - `bildVergroessern(k)` — Lupe der Schnellleiste: das Bild in seiner Auflösung in der Seitenleiste zeigen, Zoom per Regler oder Mausrad (nur ansehen).
  - `bildHelligkeit(k, schritt)` — Heller (+10) oder dunkler (-10): Helligkeit des Bildes um ``schritt`` Prozent ändern (-100 bis 100). Nicht zerstörend: der Wert steht als
  - `bildKontrast(k, schritt)` — Kontrast erhöhen (+10) oder verringern (-10) um ``schritt`` Prozent (Angabe ``kontrast``, nicht zerstörend).
  - `bildAendern(k, pfad)` — Bild ändern: eine andere Bilddatei an die Stelle des Bildes setzen (Größe, Lage und Rahmen bleiben).
  - `bildKomprimieren(k)` — Bilder komprimieren: weggeschnittene Bereiche löschen und auf 144 dpi (Anzeigegröße) verkleinern.
  - `bildZuruecksetzen(k)` — Bild zurücksetzen: Zuschnitt, Farbe, Rahmen, Füllung, Effekte und Drehung zurück (Lage und Alternativtext bleiben).

### `core/befehle/datei.py`

Befehle: Datei, Vorlagen, Schutz.

- **class `DateiBefehle`** — Befehle des Bandes: Datei, Vorlagen, Schutz. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `neu(k)`
  - `oeffnen(k)`
  - `speichern(k)`
  - `speichernUnter(k)`
  - `w_speichernAls(k, ext)`
  - `speichernPdf(k)`
  - `drucken(k)`
  - `vorschau(k)`
  - `eigenschaften(k)`
  - `umbenennen(k)`
  - `schliessen(k)`
  - `beenden(k)`
  - `ueber(k)`
  - `rueckgaengig(k)`
  - `wiederholen(k)`
  - `neuAusVorlage(k)`
  - `vorlagenDurchsuchen(k)`
  - `dokumentSchuetzen(k)`
  - `exportierenPng(k)` — Öffnet den Bildexport in der rechten Spalte des Datei-Menüs.
  - `kopieSpeichern(k)`
  - `exportierenDocx(k)`
  - `exportierenOdt(k)`
  - `exportierenTxt(k)`
  - `druckerWaehlen(k)`
  - `menue_zuletzt()`

### `core/befehle/diagrammtools.py`

Befehle: Kontext-Reiter „Diagrammtools“ für das Diagramm als freies Objekt (``editor/frei_objekt.py``, Art ``diagramm``).

- `_nummer(k, nr)` — Bandbefehle mit Angabe (``diagrammStil:[2]``) bekommen (Knopf, Nummer); direkte Aufrufe dürfen die Nummer als erstes Argument geben.
- **class `DiagrammToolsBefehle`**
  - `_dg()` — Die Daten des gewählten Diagramms (Kopie) oder None.
  - `_dg_set(**kw)` — Daten des gewählten Diagramms ändern (None entfernt die Angabe) und neu zeichnen; ohne Diagramm ein Hinweis in der Statuszeile.
  - `diagrammDatenBearbeiten(k)` — Titel, Rubriken und Datenreihen des gewählten Diagramms im vorhandenen Datenfenster bearbeiten.
  - `diagrammTypAendern(k, untertyp)` — Mit ``untertyp`` (``diagrammTypAendern:["linie"]``, Namen aus ``diagramm.TYPEN``) wird die Diagrammart direkt gesetzt; ohne Angabe öffnet
  - `menue_diagrammTyp(symbol)` — Klappe eines Typ-Knopfes: die Untertypen der Gruppe (``diagramm.TYPEN``) mit Haken beim aktuellen (beim Öffnen aufgefrischt);
  - `menue_diagrammSchnelllayout()`
  - `diagrammSchnelllayout(k, nr)` — Schnelllayout Nummer ``nr`` (0 bis 5) anwenden — für Kacheln der Schnellleiste.
  - `menue_diagrammFarben()` — Die Farbreihen der Diagrammvorlagen (``diagramm.VORLAGEN``), je mit der ersten Farbe als Muster.
  - `diagrammFarben(k, nr)` — Farbzeile Nummer ``nr`` aus ``diagramm.farbschemen_flach()`` (Gruppen „Farbig“ dann „Monochrom“) anwenden — für Kacheln der Schnellleiste.
  - `menue_diagrammElement()` — Diagrammelemente an/aus: Titel, Legende (mit Lage), Datenbeschriftungen, Achsen, Achsentitel, Gitternetzlinien, Datentabelle,
  - `diagrammElement(k, name, wert)` — Ein Diagrammelement umschalten (``diagrammElement:["achsen"]``) oder setzen (``wert`` True/False, bei ``legende`` auch die Lage
  - `_element_an(name)`
  - `diagrammElementListe(k)` — Für die Liste „Diagrammelemente“: [(Name, Anzeigename, Haken)] in der Reihenfolge der Vorlage.
  - `diagrammTitel(k)`
  - `an_diagrammTitel()`
  - `diagrammLegende(k)`
  - `an_diagrammLegende()`
  - `diagrammBeschriftungen(k)`
  - `an_diagrammBeschriftungen()`
  - `diagrammStil(k, nr)` — Diagrammstil ``nr`` (Nummer in ``diagramm.STILE``, Liste: ``diagramm.stile_liste()``).
  - `diagrammZuruecksetzen(k)` — Farben, Titel/Legende/Beschriftungen, Elemente, Filter, Teilformate und Stil auf den Standard zurück; Daten, Diagrammart und Alternativtext bleiben.
  - `diagrammTeile(k)` — Die wählbaren Teile des gewählten Diagramms [(Schlüssel, Anzeigename)] für das Feld „Diagrammbereich“ (leer ohne Diagramm).
  - `diagrammTeilWaehlen(k, schluessel)` — Einen Diagrammteil wählen (``diagrammTeilWaehlen:["reihe_0"]``; ohne Schlüssel: Auswahl aufheben). Zeichnet nicht neu.
  - `feld_diagrammTeil()` — Anzeigename des gewählten Teils fürs Feld „Diagrammbereich“ (ohne Auswahl: „Diagrammbereich“).
  - `diagrammTeilFormat(k, angaben, **kw)` — Format des gewählten Teils ändern: ``fuell`` (Farbe oder Wörterbuch), ``linie``, ``schatten``, ``reflektion``, ``leuchten``, ``weich``, ``d3``, ``drehung``,
  - `diagrammFilterDaten(k)` — Für das Popup „Diagrammfilter“: {"reihen": [(Name, Haken)], "rubriken": [(Name, Haken)]} — Haken = sichtbar.
  - `diagrammFilterSetzen(k, ausgeblendet)` — „Übernehmen“: {"reihen": [Namen], "rubriken": [Namen]} = die ausgeblendeten Einträge (leer/None = alles zeigen).
  - `diagrammNamenSetzen(k, namen)` — Reihen/Rubriken umbenennen: {"reihen": [(alt, neu)], "rubriken": [(alt, neu)]}. Leere oder doppelte neue Namen bleiben beim alten Namen;
  - `diagrammAltText(k, titel, beschreibung)` — Alternativtext des Diagramms (``alt_titel``, ``alt_beschreibung``; in DOCX steht die Beschreibung als ``descr``); ``""`` löscht.
- `_element_befehle()` — Je Element ``an_diagrammElement_<name>`` (Haken) und ``diagrammElement_<name>`` (Umschalten) — für Knöpfe, die keine Angabe mitgeben.
- `_typ_klappen()` — Je Typ-Knopf des Reiters eine Klappe ``menue_diagrammTyp_<symbol>`` (Untertypen der Gruppe).

### `core/befehle/einfuegen.py`

Befehle: Einfügen.

- **class `EinfuegenBefehle`** — Befehle des Bandes: Einfügen. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `seitenumbruch(k)`
  - `tabelleRaster(k)`
  - `tabelleZeichnen(k)` — Stift: Rechteck aufziehen, die Tabelle kommt dorthin (siehe ``ui/document/tabelle_stift.py``).
  - `bild(k)`
  - `hyperlink(k)` — Fenster „Hyperlink“ (Datei oder Webseite, Aktuelles Dokument, E-Mail-Adresse).
  - `objekt(k, als_symbol)` — Fenster „Objekt einfügen“: Inhalt einer Datei (Text, Bild) oder ein Dateisymbol mit Link.
  - `_datei_einsetzen(pfad, art)` — Bild ins Dokument, Text (DOCX, ODT, RTF, TXT, MD) mit seinem Inhalt, alles andere als Dateisymbol mit Link.
  - `dateiObjekt(k)` — „Datei-Objekt“ wie in WPS: gleich das Fenster „Dateiobjekt einfügen“ (Lunivos Dateifenster); die gewählte Datei kommt
  - `menue_objektKlappe()`
  - `kopfFussZeigen(k)`
  - `menue_seitenzahlKlappe()` — Seitenzahl wie in WPS: zehn Vorgaben (Kopf-/Fußzeile links, Mitte, rechts, außen, innen), darunter Einfügen … und Entfernen.
  - `_seitenzahl_vorgabe(schl)`
  - `seitenzahlEinfuegen(k)` — Fenster „Seitenzahl einfügen“; „Übernehmen für“ entscheidet, welche Abschnitte es trifft. „Von aktueller Seite“ beginnt am
  - `seitenzahlenEntfernen(k)`
  - `_eigene_wasserzeichen()` — Eigene Wasserzeichen (Text oder Bild) aus den Einstellungen.
  - `menue_wasserzeichenKlappe()` — Wasserzeichen wie in WPS: „Benutzerdefiniert“ (eigene + Hinzufügen), „Voreinstellung“, darunter Einfügen … und Entfernen.
  - `seitenzahlKlappe(k)`
  - `leereSeite(k, quer)` — Leere Seite: ein neues Blatt hinter der Seite der Schreibmarke (Vertikal/Horizontal; ohne Angabe wie die Seite davor).
  - `sonderzeichen(k)` — Fenster „Symbol“ (Weitere Symbole …) in der Seitenleiste; „Einfügen“ setzt das Zeichen an die Schreibmarke.
  - `_symbol_daten()` — Die eine Datenbasis von Klappe und Fenster „Symbol“: zuletzt verwendet, benutzerdefinierte Liste, Tastenkombinationen.
  - `symbol_tasten_anwenden()` — Tastenkombinationen der benutzerdefinierten Symbole als Kürzel des Hauptfensters setzen (alte werden ersetzt).
  - `_sym(name)`
  - `menue_umbruecheKlappe()` — Umbrüche wie in WPS: Seite, Spalte, Textfluss, dann die vier Abschnittsumbrüche.
  - `menue_leereSeiteKlappe()`
  - `menue_tabelleKlappe()` — Tabelle wie in WPS: 10 × 10 Zellen (fügt an der Schreibmarke ein), darunter Einfügen, Zeichnen, Text ↔ Tabelle;
  - `menue_bildKlappe()`
  - `menue_textfeldKlappe()`
  - `textfeldVertikal(k)` — Textfeld mit senkrecht laufendem Text: dasselbe freie Objekt wie das waagerechte (Rahmen, Griffe, Schnellleiste), Richtung vertikal.
  - `textfeldMehrzeilig(k)`
  - `menue_schnellbausteineKlappe()` — Schnellbausteine wie in WPS: AutoText-Liste ▸ und Felder …
  - `_bausteine_fuellen(m)` — AutoText-Liste wie in der Vorlage: die vier Seitenzahl-Texte, dann die eigenen und mitgelieferten Bausteine, zuletzt
  - `_autotext_seite(teile)`
  - `autotextHinzufuegen(k)` — Die Markierung als AutoText (Textbaustein) speichern; der Name kommt aus dem Fenster „AutoText erstellen“.
  - `schnellbausteine(k)`
  - `felder(k)` — Fenster „Felder“ (Schnellbausteine ▸ Felder …). TOC fügt ein echtes Inhaltsverzeichnis ein, TC einen ausgeblendeten
  - `menue_symbolKlappe()` — Symbol wie in WPS: zuletzt verwendete und benutzerdefinierte Symbole als Kacheln, darunter „Weitere Symbole …“.
  - `_symbole_zuletzt()`
  - `_symbol_merken(z)`
  - `_symbol_einfuegen(z)`
  - `symbol(k)`
  - `zahl(k)`
  - `textInTabelle(k)`
  - `tabelleInText(k)`
  - `inhaltsverzeichnis(k)` — Fenster „Inhaltsverzeichnis“ (Füllzeichen, Ebenen, Seitenzahlen, Verknüpfungen); OK fügt es ein oder schreibt das
  - `verzeichnisseAktualisieren(k)`
  - `_bild_einfuegen(img, alt, art, daten)`
  - `formenGalerie(k)`
  - `menue_formenKlappe()` — Formen wie in WPS: Gruppen (Linie, Rechteck, Standardformen, Blockpfeile, …) mit kleinen Umrissbildern.
  - `formEinfuegen(k, name)` — Die Form ``name`` (Katalog ``formen_katalog``, auch Linien und Pfeile) einfügen: im Zeichenbereich dort, sonst als freies Objekt.
  - `zeichenbereich(k)` — Einfügen ▸ Formen ▸ Neuer Zeichenbereich (siehe ``editor/formen.py``).
  - `zeichnen(k)`
  - `smartart(k)`
  - `smartartText(k)`
  - `menue_smartartLayout()`
  - `menue_smartartFarben()`
  - `wordart(k)`
  - `wordartVorgabe(k, nr)` — WordArt aus der Galerie: fügt sofort „Hier Text einfügen“ im gewählten Stil als freies Objekt ein — ausgewählt (Rahmen, acht Griffe,
  - `wordartBearbeiten(k)` — Text und Stil des gewählten WordArt-Objekts im Fenster „WordArt“ ändern.
  - `textfeldBearbeiten(k)` — Im gewählten Textfeld direkt schreiben (Doppelklick, Enter oder F2 auf das Textfeld).
  - `menue_wordartKlappe()` — Galerie „Formatvorlage“: 15 Stile als „A“ auf hellem Kachelgrund (wie in WPS, auch im dunklen Thema gut zu erkennen).
  - `menue_gleichungKlappe()` — Gleichung wie in WPS: eingebaute Gleichungen als große Kacheln mit Namen, darunter „Neue Gleichung einfügen …“.
  - `menue_deckblattKlappe()` — Deckblätter wie in der Vorlage: Kopf „Stil“ mit Hochformat/Querformat, darunter die Gestaltungen als Seitenbilder in vier Spalten
  - `deckblattVorlage(k, vorlage, quer)` — Aus der Galerie (``gewaehlt`` liefert den Namen als ``k``) oder als Befehl ``deckblattVorlage:["Sonne"]``.
  - `menue_diagrammKlappe()` — Klappe am Diagramm-Knopf: Diagramm … (Fenster) und Neuer Zeichenbereich.
  - `diagramm(k)`
  - `piktogramm(k)`
  - `screenshot(k)`
  - `_aufnehmen(nur_bereich)`
  - `_bereich_fertig(pm)`
  - `_foto_einfuegen(pm)`
  - `textfeld(k)`
  - `initiale(k)`
  - `textAusDatei(k)`
  - `formel(k)`
  - `schnelltabelle(k)`
  - `deckblatt(k)`
  - `datumUhrzeit(k)`
  - `textbaustein(k)`
  - `textbausteine(k)`
  - `schnellbaustein(k)` — F3: steht vor der Schreibmarke ein Kürzel, kommt der Baustein sofort; sonst die Liste aller Bausteine zum Auswählen.

### `core/befehle/extern.py`

Befehle: Externe Programme.

- **class `ExternBefehle`** — Befehle des Bandes: Externe Programme. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `_extern(fn, name)`
  - `mitWpsOeffnen(k)`

### `core/befehle/formtools.py`

Befehle zu Formen als freie Objekte (Zeichentools): Formstil-Raster, Füllungs-Palette, Anpassungsgriff, Form tauschen, Punkte bearbeiten.

- **class `FormToolsBefehle`**
  - `_form()`
  - `_form_hinweis()`
  - `formstileRaster(k)` — Daten der Galerie „Formstile“: 6 Zeilen × 7 Spalten (``editor/formen_stile.formstile_raster``).
  - `formStilRaster(k, zeile, spalte)` — Stil (Zeile, Spalte) des Rasters auf die gewählte Form: Füllung, Verlaufsart, Linie, Strichbreite und Effekt.
  - `zeichenFuellungDaten(k)` — Daten des Füllungs-Popups aus dem Baustein ``ui/baukasten/farben.py``: {"thema": Zeilen × 10 Spalten, "standard": [Farben],
  - `formAnpassen(k, wert, index)` — Parameter ``index`` des Anpassungsgriffs der gewählten Form auf ``wert`` setzen (``formen.anpass_setzen``).
  - `kann_formAnpassen()`
  - `formAendern(k, name)` — „Form bearbeiten ▸ Form ändern“: die gewählte Form durch ``name`` (Katalogname) ersetzen; Größe, Füllung und Kontur bleiben.
  - `formPunkteBearbeiten(k)` — „Punkte bearbeiten“: die gewählte Form wird zur Freiform (``editor/freiform.py``, Punktliste in ``daten["punkte"]``) und zeigt ihre
  - `kann_formPunkteBearbeiten()`

### `core/befehle/hilfen.py`

Gemeinsame Kleinigkeiten der Befehls-Bausteine.

- **class `FreiMenue`** — Die Menüs des Reiters Zeichentools: dieselben Baukasten-Menüs wie neben dem Bild, wirken aber auf den Editor, der bei der Wahl aktuell ist.
  - `formstile(cmd)`
  - `fuell(cmd)`
  - `kontur(cmd)`

### `core/befehle/ki.py`

Befehle: KI, Vorlesen.

- **class `KIBefehle`** — Befehle des Bandes: KI, Vorlesen. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `w_assistentErstellen(k)` — „Schnelle KI-Aktion erstellen“ — dasselbe wie „Eigenen Assistenten erstellen“: ein Eintrag in der Liste der Assistenten.
  - `menue_assistenten()` — Das Menü „KI-Aktionen“: die eigenen Schnellen KI-Aktionen, neue anlegen, entfernen und alle bisherigen Ergebnisse.
  - `menue_silbenTrennungMenue()` — Zur Silbentrennung: wo man die Trennstriche sieht (die Bearbeitungsansicht zeigt sie nicht) und die Einstellungen.
  - `silbentrennungVorschau(k)`
  - `menue_silbenMenue()`
  - `vorlesen(k)`
  - `vorlesenAbSatz(k)`
  - `vorlesenStopp(k)`
  - `stimmeWaehlen(k)`
  - `kiKorrektur(k)`
  - `kiVorschlaege(k)`
  - `kiUmformulieren(k)`
  - `kiZusammenfassen(k)`
  - `w_kiUebersetzen(k)`
  - `w_kiUebersetzenErsetzen(k)`
  - `w_kiUebersetzenZeigen(k)`
  - `menue_uebersetzenMenue()`
  - `kiEntwerfen(k)`
  - `w_chatUmschalten(k)`
  - `_ki_einstellungen(reiter)`
  - `w_kiEinstellungen(k)`
  - `w_kiKonfiguration(k)`
  - `w_kiSprache(k)`
  - `w_eigenenAnbieterHinzufuegen(k)`
  - `w_kiErgebnisse(k)`
  - `kiTextInBild(k)`
  - `kiTextAktion(k, aktion)`

### `core/befehle/kommentare.py`

Befehle: Kommentare, Noten, Änderungen.

- **class `KommentarBefehle`** — Befehle des Bandes: Kommentare, Noten, Änderungen. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `_text_abfragen(titel, frage, vorgabe)`
  - `kommentar(k)` — Neuer Kommentar wie in WPS: das Feld „Kommentare“ links öffnet sich mit dem Eingabefeld — Knopf und Seitenleiste
  - `kommentarWeiter(k)`
  - `kommentarZurueck(k)`
  - `kommentarWeg(k)`
  - `kommentareAlleWeg(k)`
  - `_note(art, titel)` — Neue Note: das Zeichen kommt in den Text, unten öffnet sich das Notenfeld mit dem Cursor darin.
  - `fussnote(k)`
  - `endnote(k)`
  - `noteWeiter(k)`
  - `noteZurueck(k)`
  - `notenZeigen(k)`
  - `note_bearbeiten(art, nid)`
  - `_geschuetzt(*arten)` — Steht ein Dokumentschutz dieser Art (Überprüfen ▸ Bearbeitung einschränken), Hinweis in der Statusleiste und True.
  - `verfolgen(k)`
  - `an_verfolgen()`
  - `markupUmschalten(k)`
  - `an_markupUmschalten()`
  - `ueberarbeitungsbereich(k)`
  - `aenderungAnnehmen(k)`
  - `aenderungAblehnen(k)`
  - `_aend_am_cursor(annehmen)`
  - `aenderungWeiter(k)`
  - `aenderungZurueck(k)`
  - `aenderungenUebernehmen(k)`
  - `aenderungenVerwerfen(k)`

### `core/befehle/kontext.py`

Befehle: Kontext-Reiter: Tabelle, Bild, Formen, Zeichnen.

- **class `KontextBefehle`** — Befehle des Bandes: Kontext-Reiter: Tabelle, Bild, Formen, Zeichnen. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `_bild_frei()` — (Editor, Ziel) des gewählten frei positionierten Bildes (Datei, Bildschirmfoto, Piktogramm …) oder (Editor, None).
  - `bildFarbe(k)`
  - `bildZuschneiden(k)`
  - `objektDrehen(k)`
  - `objektAusrichten(k)`
  - `_tab()`
  - `tabelleZeileOben(k)`
  - `tabelleZeileUnten(k)`
  - `tabelleSpalteLinks(k)`
  - `tabelleSpalteRechts(k)`
  - `tabelleZeileLoeschen(k)`
  - `tabelleSpalteLoeschen(k)`
  - `tabelleLoeschen(k)`
  - `tabelleVerbinden(k)`
  - `tabelleTeilen(k)`
  - `tabelleRahmen(k)`
  - `an_tabelleRahmen()`
  - `menue_tabelleSchattierung()`
  - `menue_tabelleVorlagen()`
  - `_tabelle_vorlage(name)`
  - `_tabellen_option(key)`
  - `tabelleKopfzeile(k)`
  - `tabelleStreifen(k)`
  - `tabelleErsteSpalte(k)`
  - `an_tabelleKopfzeile()`
  - `an_tabelleStreifen()`
  - `an_tabelleErsteSpalte()`
  - `_zelle_ausrichten(wo)`
  - `zelleOben(k)`
  - `zelleMitte(k)`
  - `zelleUnten(k)`
  - `_bild()`
  - `_form_farbe(feld, titel)`
  - `_form_aendern(**kw)`
  - `menue_formFuellung()`
  - `menue_formKontur()`
  - `menue_formVorlagen()`
  - `_form_vorlage(name)`
  - `formText(k)`
  - `_zeichen()` — (Editor, Ziel) des markierten Bildes oder (Editor, None).
  - `_zeichen_edit()`
  - `menue_zeichenFormstile()`
  - `menue_zeichenFuellung()`
  - `menue_zeichenGliederung()`
  - `menue_zeichenAusrichten()`
  - `menue_zeichenDrehen()`
  - `menue_zeichenEbene()`
  - `wortExtras(k)` — Wort-Extras: Absätze aufräumen (Markierung, sonst das ganze Dokument).
  - `menue_wortExtrasKlappe()` — Das Menü „Wort-Extras“ wie in der Vorlage, mit dem Untermenü „Löschen“; jeder Eintrag ist ein Schritt für Rückgängig.
  - `_wort_extra(text, f)`
  - `zeichenEffekte(k)`
  - `zeichenFormatUebertragen(k)`
  - `zeichenAusrichten(k, wie)`
  - `zeichenDrehen(k, grad)`
  - `zeichenEbene(k, wo)`
  - `zeichenVorn(k)`
  - `zeichenHinten(k)`
  - `zeichenUmbruch(k)`
  - `zeichenLayout(k)`
  - `zeichenMasse(breite_mm, hoehe_mm)`
  - `gruppieren(k)`
  - `gruppeAufheben(k)`
  - `bildGroesse(k)`
  - `bildBreite(k)`
  - `anordnen(k)` — Textumbruch / Position: Bild mit Text in der Zeile oder links/rechts vom Text umflossen.
  - `bildOriginal(k)`
  - `bildAltText(k)`
  - `bildEntfernen(k)`
  - `exportierenRtf(k)`

### `core/befehle/kopffuss.py`

Befehle: Kontext-Reiter „Kopf- und Fußzeile“ (Bearbeiten direkt auf der Seite, siehe ``ui/document/kopffuss_bearbeiter.py``).

- **class `KopfFussBefehle`** — Befehle des Bandes: Kopf- und Fußzeile. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `_kf()` — Der Bearbeiter des aktuellen Editors, nur wenn er gerade bearbeitet.
  - `_kf_start(zone)`
  - `menue_kfGruppeKlappe()`
  - `_hf_klappe(zone)`
  - `menue_kopfzeileKlappe()`
  - `menue_fusszeileKlappe()`
  - `menue_kopfLinieKlappe()`
  - `menue_kfEinstellungenKlappe()`
  - `_kf_ausrichten(zone, ausr)`
  - `_kf_leeren(felder)`
  - `kopfFussSchliessen(k)`
  - `kfWechseln(k)`
  - `kfVorige(k)`
  - `kfNaechste(k)`
  - `kfVerknuepfen(k)`
  - `kann_kfVerknuepfen()` — Grau auf der ersten Seite/im ersten Abschnitt: dort gibt es keinen Vorgänger.
  - `an_kfVerknuepfen()`
  - `kfTabstopp(k)`
  - `kfOptionen(k)` — Seitenleistenfenster: Erste Seite anders; Gerade und ungerade Seiten unterschiedlich.
  - `_kf_abstand(attr, name, symbol)`
  - `feld_kopfHoehe()`
  - `feld_fussHoehe()`

### `core/befehle/pruefen.py`

Befehle: Überprüfen, Schreibhilfe, Vergleichen.

- **class `PruefenBefehle`** — Befehle des Bandes: Überprüfen, Schreibhilfe, Vergleichen. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `woerterZaehlen(k)` — Wörter zählen wie in der Vorlage: Statistiken des Dokuments, auf Wunsch samt Fuß- und Endnoten.
  - `_jetzt_pruefen()` — Prüfen (F7): ohne Text eine deutliche Rückmeldung statt einer leeren Seitenleiste.
  - `rechtschreibung(k)`
  - `w_pruefen(k)`
  - `gruendlichPruefen(k)`
  - `wellen(k)` — Rote Wellenlinien beim Schreiben an/aus (derselbe Schalter wie „We“ in der Seitenleiste und in „Welche Hilfe wann“).
  - `an_wellen()`
  - `vorhersage(k)`
  - `an_vorhersage()`
  - `autokorrektur(k)`
  - `an_autokorrektur()`
  - `tafelZeigen(k)`
  - `welcheHilfe(k)`
  - `w_optionenOeffnen(k, seite)`
  - `zeilenfokus(k)`
  - `an_zeilenfokus()`
  - `bearbeitungSperren(k)`
  - `an_bearbeitungSperren()`
  - `lesemodus(k)`
  - `an_lesemodus()`
  - `_fassung_laden(pfad)`
  - `_ergebnis_blatt(titel, ziel, page)`
  - `dokumenteVergleichen(k)`
  - `dokumenteZusammenfuehren(k)`
  - `_neues_blatt(titel)`
  - `umschlag(k)`
  - `etiketten(k)`
  - `seriendruckfeld(k)`
  - `adressblock(k)`
  - `seriendruckregel(k)`
  - `seriendruck(k)`
  - `_form_dialog(art)`
  - `formTextfeld(k)`
  - `formAuswahl(k)`
  - `tabstopps(k)`
  - `geheZu(k, art)` — „Gehe zu“ (Strg+G): der Reiter im Feld „Suchen und ersetzen“ der linken Seitenleiste.
  - `vollbild(k)`
  - `an_vollbild()`
  - `formDatum(k)`
  - `formKasten(k)`
  - `formKnopf(k)`
  - `formLeeren(k)`
  - `thesaurus(k)`
  - `_wie_geschrieben(alt, neu)`
  - `barrierefrei(k)`
  - `pruefsprache(k)`
  - `pruefsprache_aktuell()`
  - `pruefsprache_setzen(kennung)` — Die Sprache des Dokuments für die Korrekturhilfen (wird in der Datei vermerkt) — vom Band und vom Fenster „KI-Einstellungen“ benutzt.

### `core/befehle/seite.py`

Befehle: Seite, Abschnitte, Spalten.

- **class `SeiteBefehle`** — Befehle des Bandes: Seite, Abschnitte, Spalten. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `seitenraenderRahmen(k, *_)`
  - `w_setzeRandVorgabe(k, art)`
  - `w_randVorgabeJetzt()`
  - `seitenraender(k, *_)`
  - `spaltenSetzen(k, n)`
  - `w_spaltenJetzt()`
  - `spalten(k)`
  - `spaltenumbruch(k)` — Der Text danach beginnt in der nächsten Spalte (bei einer Spalte: auf der nächsten Seite).
  - `w_setzePapier(k, art)`
  - `w_papierJetzt()`
  - `w_querJetzt()`
  - `w_setzeQuer(k, quer)` — Hochformat (False) oder Querformat (True) für den Abschnitt am Zeiger.
  - `querformat(k)`
  - `w_setzeThema(k, wahl)`
  - `w_themaJetzt()`
  - `_haken_auffrischen(m, jetzt)` — Vor dem Aufklappen die aktuelle Kachel markieren (die Menüs werden nur einmal gebaut).
  - `menue_raenderKlappe()`
  - `menue_ausrichtungKlappe()`
  - `menue_groesseKlappe()`
  - `menue_spaltenKlappe()`
  - `menue_textrichtungKlappe()` — Textrichtung wie in der Vorlage. Lunivo setzt Text nur waagerecht; die senkrechten Richtungen bleiben grau.
  - `menue_zeilennummernKlappe()`
  - `zeilennummernArt(k, art)` — ``art``: None = keine, "" = fortlaufend, "seite" = jede Seite neu.
  - `_ohne_zeilennr()`
  - `zeilennummernUnterdruecken(k)` — Der Absatz an der Schreibmarke (oder die markierten) bekommt keine Zeilennummern — oder wieder welche.
  - `menue_ausrichtenKlappe()` — Ausrichten wie in der Vorlage: die Form oder das freie Bild am Blatt ausrichten; was eine Mehrfachauswahl braucht, bleibt grau.
  - `_seite_aendern(**felder)`
  - `menue_seitenfarbe()`
  - `menue_seitenfarbeKlappe()` — Seitenfarbe wie in der Vorlage: Palette, darunter Hintergrundbild und anderer Hintergrund (in Lunivo noch grau) und das
  - `seitenfarbe(k)`
  - `wasserzeichen(k)`
  - `_wasserzeichen_setzen(w, bereich)` — Wasserzeichen für das ganze Dokument oder nur den Abschnitt mit der Schreibmarke („Übernehmen für“).
  - `seitenrahmen(k)`
  - `netzlinien(k)`
  - `an_netzlinien()`
  - `absatzabstand(k)`
  - `_abstand_setzen(vor, nach)`
  - `zeilennummern(k)`
  - `an_zeilennummern()`
  - `silbentrennung(k)`
  - `an_silbentrennung()`
  - `textrichtung(k)`
  - `textrichtungLinks(k)`
  - `textrichtungRechts(k)`
  - `zeilenumbruch(k)` — Zeilenumbruch ohne neuen Absatz (Umschalt+Enter).
  - `an_textrichtung()`
  - `menue_designsKlappe()`
  - `designSetzen(k, name)` — Design: Schrift der Überschriften und des Textes, Farbe der Überschriften — für das ganze Dokument (ein Schritt).
  - `menue_farbenKlappe()`
  - `farbschemaSetzen(k, name)`
  - `_farbe_eigen()`
  - `menue_schriftartenKlappe()`
  - `schriftpaarSetzen(k, name)`
  - `menue_effekteKlappe()`
  - `effektSetzen(k, name)` — Effekt an die markierte Form bzw. das markierte freie Bild; ist nichts markiert, an alle im Dokument.
  - `designs(k)`
  - `farbschema(k)`
  - `designSchriften(k)`
  - `designEffekte(k)`
  - `abschnittsumbruch(k, art)`
  - `abschnittLoeschen(k)`
  - `abschnittVorher(k)`
  - `abschnittNaechster(k)`
  - `abschnittNavigation(k)`
  - `abschnittEinstellungen(k)`
  - `_kopf_link(was, an)`
  - `kopfVerknuepfen(k)`
  - `fussVerknuepfen(k)`
  - `an_kopfVerknuepfen()`
  - `an_fussVerknuepfen()`
  - `schriftartMehr(k)`
  - `papierformatFenster(k)`
  - `fusszeileBearbeiten(k)`
  - `ersteSeiteAnders(k)`
  - `geradeUngerade(k)` — „Gerade und ungerade Seiten sind unterschiedlich“: gerade Seiten bekommen eine eigene Kopf-/Fußzeile (zuerst eine Kopie der gewöhnlichen).
  - `an_geradeUngerade()`
  - `an_ersteSeiteAnders()`
  - `tabelleEigenschaften(k)`
  - `tabelleSortieren(k)`

### `core/befehle/serien.py`

Befehle: Seriendruck (Reiter „Mailings“ nach der WPS-Vorlage).

- **class `SerienBefehle`** — Befehle des Kontext-Reiters „Mailings“. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `_serie()`
  - `_hat_quelle()`
  - `_gewaehlte()` — Die angehakten Sätze, mit den Namen der Felder im Text.
  - `an_serienVorschau()`
  - `an_serienHervorheben()`
  - `serienReiter(k)` — Verweise ▸ Seriendruck: den Reiter „Mailings“ zeigen und dorthin wechseln.
  - `serienSchliessen(k)`
  - `serienQuelle(k)` — Datenquelle öffnen: eine Empfängerliste als Text (CSV mit ; , oder Tabulator; erste Zeile = Spaltennamen).
  - `_quelle_setzen(pfad, spalten, saetze)`
  - `serienQuelleSchliessen(k)`
  - `menue_serienQuelleKlappe()`
  - `serienEmpfaenger(k)`
  - `serienFeld(k)`
  - `serienNaechster(k)`
  - `serienHervorheben(k)` — Seriendruckfelder hervorheben: der farbige Hintergrund der Felder an oder aus (nur Anzeige, ändert den Text nicht).
  - `serienZuordnen(k)`
  - `_briefe()`
  - `_vorschau_auffrischen()`
  - `serienVorschau(k)` — Seriendruck-Vorschau an/aus: zeigt den Brief des gewählten Datensatzes; die Vorlage bleibt unverändert.
  - `_gehe_satz(wohin)`
  - `serienErster(k)`
  - `serienVorheriger(k)`
  - `serienNaechsterSatz(k)`
  - `serienLetzter(k)`
  - `feld_datensatz()` — Das Feld zwischen „Vorheriger“ und „Nächster Datensatz“: Nummer des gezeigten Datensatzes (Eingabe springt dorthin).
  - `_datensatz_anzeigen()`
  - `serienNeuesDokument(k)` — In neuem Dokument zusammenführen: alle Briefe hintereinander, je Brief eine neue Seite.
  - `serienEinzeln(k)` — In anderem neuen Dokument zusammenführen: jeder Brief als eigene DOCX-Datei in einem Ordner.
  - `serienDrucker(k)` — An Drucker zusammenführen: die Briefe in ein neues Dokument und gleich das Druckfenster.

### `core/befehle/smartarttools.py`

Befehle: Kontext-Reiter „WPSArt-Design“ für das SmartArt als freies Objekt (``editor/frei_objekt.py``, Art ``smartart``).

- **class `SmartArtToolsBefehle`**
  - `_sa()`
  - `_sa_hinweis()`
  - `_sa_tun(f, *args)`
  - `smartartKnotenWaehlen(k, ident)` — Knoten wählen (``smartartKnotenWaehlen:["k2"]``; ohne Id: Auswahl aufheben). Zeichnet nicht neu.
  - `smartartKnotenText(k, ident, text)` — Den Text eines Knotens setzen (Eintippen im Knoten).
  - `smartartFormEinfuegen(k, wie)` — „Form einfügen“: ``nach`` \| ``vor`` \| ``unter`` \| ``ueber`` \| ``assistent`` relativ zum gewählten Knoten (ohne Auswahl: hinter den letzten);
  - `smartartLevel(k, richtung)` — „Level erhöhen“ (``erhoehen``) / „Level reduzieren“ (``reduzieren``): der gewählte Knoten samt Unterknoten.
  - `smartartLevelErhoehen(k)`
  - `smartartLevelReduzieren(k)`
  - `smartartVerschieben(k, richtung)` — „Vorwärts“ (``vor``) / „Rückwärts“ (``zurueck``): den Knoten unter seinen Geschwistern verschieben.
  - `smartartVorwaerts(k)`
  - `smartartRueckwaerts(k)`
  - `smartartAufzaehlung(k)` — „Aufzählungszeichen einfügen“: ein Aufzählungspunkt „Text“ unter dem gewählten Knoten.
  - `smartartRechtsLinks(k)` — „Layout von rechts nach links“ umschalten (``rtl``); Zustand: ``an_smartartRechtsLinks``.
  - `an_smartartRechtsLinks()`
  - `smartartHierarchie(k, art)` — Organigramm-Variante: ``standard`` \| ``beide`` \| ``haengend_links`` \| ``haengend_rechts`` (nur bei den Layouts Organigramm/Hierarchie).
  - `smartartStil(k, nr)` — Formenstil 0 bis 4 (``SA.STILE``: Flach, Einfach, Hell, Kräftig, 3D).
  - `smartartLayout(k, name)` — Layout wechseln (Schlüssel aus ``SA.LAYOUTS``); Knoten und Farben bleiben.
  - `_sa_kann(was, richtung)`
  - `kann_smartartKnotenWaehlen()`
  - `kann_smartartFormEinfuegen()`
  - `kann_smartartAufzaehlung()`
  - `kann_smartartLevelErhoehen()`
  - `kann_smartartLevelReduzieren()`
  - `kann_smartartVorwaerts()`
  - `kann_smartartRueckwaerts()`
  - `kann_smartartHierarchie()`
  - `kann_smartartRechtsLinks()`
  - `kann_smartartStil()`

### `core/befehle/text.py`

Befehle: Zeichen und Absatz.

- **class `TextBefehle`** — Befehle des Bandes: Zeichen und Absatz. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `schriftGroesser(k)`
  - `schriftKleiner(k)`
  - `schlicht(k)`
  - `fett(k)`
  - `an_fett()`
  - `kursiv(k)`
  - `an_kursiv()`
  - `unter(k)`
  - `an_unter()`
  - `menue_unterstrichKlappe()` — Wie in der Vorlage: die Linienarten als Bild, „Mehr Unterstreichungen …“ (Fenster Schriftart) und „Unterstreichungsfarbe“ mit der
  - `_unterfarbe(farbe)` — Farbe der Unterstreichung; ist der Text noch nicht unterstrichen, wird er es einfach (wie in der Vorlage).
  - `durchJetzt(k)`
  - `an_durchJetzt()`
  - `symbolname_durchJetzt()`
  - `menue_durchKlappe()`
  - `_durch_waehlen(art)`
  - `betonung(k)` — Betonungszeichen (Punkt über jedem Buchstaben) an- oder ausschalten; andere Zeichen wählt das Fenster „Schriftart“.
  - `an_betonung()`
  - `menue_einstellungenKlappe()` — Knopf „Einstellungen“ wie in der Vorlage: die Fenster des Reiters Start.
  - `formatvorlagenBereich(k)` — „Formatvorlagen und Formatierung“: die Liste aller Formatvorlagen in der rechten Seitenleiste (wie der Bereich der Vorlage).
  - `objekteWaehlen(k)` — Springt zum nächsten Bild im Text und markiert es (dann erscheinen die Bildtools).
  - `zeichenumriss(k)`
  - `an_zeichenumriss()`
  - `texteffekte(k)` — „Texteffekte formatieren“ in der rechten Seitenleiste: die Änderungen wirken sofort an der Markierung, solange der Bereich offen ist.
  - `_effekt_setzen(**teile)` — Einen Teil der Texteffekte der Markierung ersetzen (Wert ``None`` nimmt ihn weg); die übrigen Effekte bleiben.
  - `menue_texteffekteKlappe()` — Menü am Knopf „Texteffekte“ wie in der Vorlage: WordArt, Schatten, Spiegelung, Leuchteffekt (je mit Bildchen zum Anklicken), 3D-Drehung und
  - `texteffekteFenster(k)` — Dasselbe als eigenes Fenster (mit „OK“), wie es das Schriftart-Fenster und die Formatvorlage benutzen.
  - `effekt(k)`
  - `durch(k)`
  - `an_durch()`
  - `hoch(k)`
  - `an_hoch()`
  - `tief(k)`
  - `an_tief()`
  - `schreibweise(k)`
  - `symbolname_schreibweise()`
  - `_aa_waehlen(wahl)`
  - `menue_schreibweiseKlappe()`
  - `schreibweiseFenster(k)` — Das Fenster „Groß-/Kleinschreibung“ (Zusatzfenster in der Seitenleiste).
  - `umschlosseneZeichen(k)` — Das Fenster „Eingeschlossene Zeichen“: der gewählte Text bekommt Kreis, Quadrat, Dreieck oder Raute.
  - `phonetischesLeitzeichen(k)` — Das Fenster „Phonetisches Leitzeichen“: Leittext über dem gewählten Text.
  - `_farbmenue(setzen, ohne_text, vorschau)` — Die gemeinsame Farbpalette; ``setzen`` bekommt eine QColor oder None („keine“).
  - `schriftfarbeJetzt(k)`
  - `menue_schriftfarbeKlappe()`
  - `hervorhebenJetzt(k)`
  - `menue_hervorhebenKlappe()`
  - `punkte(k)`
  - `an_punkte()`
  - `zahlen(k)`
  - `an_zahlen()`
  - `_listenraster(art, titel)` — Auswahl der Aufzählungs- bzw. Nummerierungsarten: dieselben Kacheln und Listen wie im Fenster „Nummerierung und Aufzählungszeichen“.
  - `_liste_setzen(spec)`
  - `listeDialog(seite)` — Fenster „Nummerierung und Aufzählungszeichen“ (Baukasten); das Ergebnis gilt für den Absatz an der Schreibmarke.
  - `menue_aufzaehlungKlappe()`
  - `menue_nummerierungKlappe()`
  - `einzugMehr(k)`
  - `einzugWeniger(k)`
  - `einzugGenau(k)`
  - `ebeneHoeher(k)`
  - `ebeneTiefer(k)`
  - `links(k)`
  - `an_links()`
  - `mitte(k)`
  - `an_mitte()`
  - `rechts(k)`
  - `an_rechts()`
  - `block(k)`
  - `an_block()`
  - `menue_zeilenabstandKlappe()`
  - `steuerzeichenZeigen(k)`
  - `an_steuerzeichenZeigen()`
  - `verteilt(k)`
  - `formatUebertragen(k)`
  - `an_formatUebertragen()`
  - `sortieren(k)` — Sortiert die markierten Absätze (ohne Markierung das ganze Dokument); „Text sortieren“ fragt Schlüssel, Typ und Richtung,
  - `menue_absatzSchattierung()`
  - `menue_absatzRahmen()`
  - `_rahmen_seite(schluessel)` — Eintrag des Rahmen-Menüs: einzelne Seiten ein-/ausschalten, alle, außen oder keine.
  - `absatzRahmen(k, seite)` — Fenster „Rahmen und Schattierung“ (Reiter Rahmen · Seitenrand · Schattierung); ``seite`` wählt den Reiter.
  - `_stile_fertig()` — Nach jeder Änderung an den Vorlagen: Galerie neu füllen, Tastenkombinationen der Vorlagen in allen Dokumenten neu setzen.
  - `_taste_belegt(taste, eigene)` — Name dessen, was die Tastenkombination schon hat (Befehl im Fenster oder andere Vorlage), sonst None.
  - `neueFormatvorlage(k)` — Fenster „Neue Formatvorlage“ (Baukasten); die Werte kommen vom Absatz an der Schreibmarke.
  - `formatvorlageAendern(name)` — Rechtsklick auf eine Vorlage in der Galerie ▸ Ändern …: dasselbe Fenster, der Name steht fest.
  - `formatvorlageLoeschen(name)`

### `core/befehle/texttools.py`

Befehle: Kontext-Reiter „Texttools“ (und die Galerien von „Zeichentools“) für die freien Objekte WordArt und Textfeld.

- **class `TextToolsBefehle`**
  - `tt_art()` — Welches freie Textobjekt ist markiert? ``wordart`` \| ``textfeld`` \| None.
  - `_wa()`
  - `_wa_set(**kw)` — Angaben des markierten WordArt/Textfelds ändern; ohne Auswahl ein Hinweis in der Statuszeile.
  - `ttSchriftart(name)`
  - `ttGroesse(pt)`
  - `_tt_pt(delta)`
  - `ttGroesser(k)`
  - `ttKleiner(k)`
  - `ttSchlicht(k)` — Formatierung löschen: Schrift, Auszeichnungen, Hervorhebung, Effekte, Liste und Absatzwerte zurück auf die Vorgabe der Vorlage.
  - `_tt_umschalten(schl, standard)`
  - `ttFett(k)`
  - `an_ttFett()`
  - `ttKursiv(k)`
  - `an_ttKursiv()`
  - `ttUnter(k)`
  - `an_ttUnter()`
  - `ttDurch(k)`
  - `an_ttDurch()`
  - `ttHoch(k)`
  - `an_ttHoch()`
  - `ttTief(k)`
  - `an_ttTief()`
  - `menue_ttUnter()` — Wie bei Start: die Linienarten als Bild, „Mehr Unterstreichungen …“ und die Unterstreichungsfarbe; wirkt auf das Objekt.
  - `_tt_unter_dialog()` — Das Fenster „Schriftart“ mit der Unterstreichung des Objekts; übernommen werden Art und Farbe der Linie.
  - `menue_ttDurch()`
  - `ttHervorJetzt(k)`
  - `menue_ttHervor()`
  - `ttSchriftfarbeJetzt(k)`
  - `menue_ttSchriftfarbe()`
  - `_tt_liste_setzen(spec)` — Aufzählung/Nummerierung des Objekts: dieselben Angaben wie im Start-Reiter (``editor/listen``), ``None`` = keine Liste.
  - `_tt_liste_ist(aufzaehlung)`
  - `ttPunkte(k)`
  - `an_ttPunkte()`
  - `ttZahlen(k)`
  - `an_ttZahlen()`
  - `_tt_listenraster(art, titel)` — Dieselbe Auswahl wie bei Start (alle Aufzählungszeichen und Nummerierungen), gilt für den Text im Objekt.
  - `_tt_listendialog(seite)`
  - `menue_ttPunkte()`
  - `menue_ttZahlen()`
  - `ttEinzugMehr(k)`
  - `ttEinzugWeniger(k)`
  - `ttSortieren(k)` — Zeilen des WordArt-Textes sortieren (A–Z, beim nächsten Mal Z–A).
  - `menue_ttTextrichtung()` — Textrichtung wie in WPS (dieselben sechs Einträge mit Bildchen wie bei Start), wirkt auf den Text im Objekt.
  - `_tt_ausr(wie)`
  - `ttLinks(k)`
  - `ttMitte(k)`
  - `ttRechts(k)`
  - `ttBlock(k)`
  - `ttVerteilt(k)`
  - `an_ttLinks()`
  - `an_ttMitte()`
  - `an_ttRechts()`
  - `an_ttBlock()`
  - `an_ttVerteilt()`
  - `menue_ttZeilenabstand()`
  - `ttStil(nr)` — WordArt-Formatvorlage (0–14) auf das markierte WordArt anwenden; die Textfüllung, Kontur und Effekte setzen sich neu.
  - `galerie_ttWordartStile()`
  - `_wa_kachel(i)`
  - `menue_ttStile()` — Alle 15 Stile als „A“ auf hellem Grund (wie das Menü neben Einfügen ▸ WordArt), wirkt auf das markierte WordArt.
  - `menue_ttTextfuellung()`
  - `menue_ttTextkontur()`
  - `menue_ttTexteffekte()`
  - `_wa_effekt(**teile)`
  - `_effekt_menue(setzen, _schl)` — Schatten, Spiegelung und Leuchteffekt mit Bildchen (wie bei Start ▸ Texteffekte); ``setzen(**teil)`` schreibt den Teil.
  - `ttFormstil(schl)`
  - `galerie_ttFormstile()` — Die drei Kacheln „Abc“ im Band (schwarzer, blauer, oranger Rand) und das Menü mit allen 42 Formstilen.
  - `menue_ttFormFuellung()`
  - `menue_ttFormKontur()`
  - `ttFormEffekte(k)` — Weitere Formeffekte: die Seitenleiste „Formatierung“ auf dem Reiter Effekte (Schatten, Reflektion, Leuchten, Weiche Kanten).
  - `menue_ttFormEffekte()` — Schatten, Spiegelung und Leuchteffekt der Form (wie die Voreinstellungen der Seitenleiste), darunter „Weitere Effekte …“.
  - `ttFormatUebertragen(k)` — Format des markierten WordArt/Textfelds (Schrift, Auszeichnungen, Farben, Effekte, Form) aufnehmen; beim nächsten markierten Objekt
  - `an_ttFormatUebertragen()`
  - `_tt_felder()` — Die Textfelder, mit denen das markierte verknüpft werden kann (Schlüssel, Anzeigename): nicht es selbst, keins mit Vorgänger.
  - `menue_ttVerknuepfung()` — Das markierte Textfeld mit einem anderen verknüpfen (der Text läuft weiter) oder die Verknüpfung lösen.
  - `ttVerknuepfen(k, ziel)` — Das markierte Textfeld mit ``ziel`` verknüpfen: was nicht mehr hineinpasst, läuft dort weiter.
  - `ttVerknuepfungLoesen(k)`
  - `menue_ttEinstellungen()` — Einstellungen wie in WPS: die Fenster zum markierten Objekt (Seitenleiste „Formatierung“, Layout, Text).
  - `ttTextBearbeiten(k)`
  - `_tt_gehe(richtung)` — Das vorige/nächste WordArt oder Textfeld des Dokuments markieren (am Ende springt es an den Anfang).
  - `ttVoriges(k)`
  - `ttNaechstes(k)`

### `core/befehle/ueberpruefen.py`

Befehle: Reiter „Überprüfen“ nach den Vorlagen (ueberpruefen/01–10) — Klappen, Anzeige der Fassung, Markup-Auswahl,

- **class `UeberpruefenBefehle`** — Befehle des Reiters „Überprüfen“. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `_sym(name)`
  - `_hat_kommentare()`
  - `_hat_aenderungen()`
  - `_schutz()`
  - `_darf_aendern()` — Annehmen und Ablehnen: nicht, solange ein Dokumentschutz steht.
  - `an_bearbeitungEinschraenken()`
  - `menue_rechtschreibKlappe()`
  - `menue_kommentarLoeschenKlappe()`
  - `menue_verfolgenKlappe()`
  - `_anzeige_index()`
  - `ueberpruefenAnzeige(k, index)` — Was das Dokumentfenster zeigt: mit oder ohne Markup, oder das Original ohne die verfolgten Änderungen (schreibgeschützt).
  - `feld_anzeige()` — Die Auswahl über „Markup anzeigen“ wie in der Vorlage: die Fassung, darunter das Markup-Menü.
  - `_filter_setzen(**werte)`
  - `_bearbeiter_fuellen(m)`
  - `_zeiten_fuellen(m)`
  - `menue_markupKlappe()`
  - `menue_ueberpruefenKlappe()`
  - `_angezeigte(annehmen)`
  - `_entscheiden_menue(annehmen)`
  - `menue_annehmenKlappe()`
  - `menue_ablehnenKlappe()`
  - `menue_vergleichenKlappe()`
  - `bearbeitungEinschraenken(k)` — Seitenleiste „Bearbeitung einschränken“: Schreibgeschützt, nur nachverfolgte Änderungen oder nur Kommentare.
  - `schutz_setzen(t, art)`

### `core/befehle/verweise.py`

Befehle: Verweise.

- **class `VerweiseBefehle`** — Befehle des Bandes: Verweise. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).
  - `beschriftung(k)` — Fenster „Beschriftung“: die Nummer steht schon im Feld („Tabelle 1“), dahinter schreibt man weiter. Eigene Bezeichnungen
  - `_verzeichnis(art, titel, leer)`
  - `abbildungsverzeichnis(k)`
  - `stichwortverzeichnis(k)`
  - `literaturverzeichnis(k)`
  - `textmarke(k)`
  - `querverweis(k)` — Fenster „Querverweis“: „Einfügen“ setzt den Verweis an die Schreibmarke, das Fenster bleibt offen.
  - `indexEintrag(k)` — Fenster „Indexeintrag festlegen“: „Markieren“ setzt den Eintrag an die Markierung, „Alles markieren“ an jede Stelle
  - `indexAktualisieren(k)`
  - `inhaltsverzeichnisAktualisieren(k)`
  - `menue_inhaltsverzeichnisKlappe()` — Ebene 1–9 und Textkörper wie in der Vorlage. In Lunivo trägt die Ebene die Formatvorlage „Überschrift N“
  - `inhaltsEbene(k, ebene)`
  - `_note_gehe(delta, art, titel)`
  - `fussnoteZurueck(k)`
  - `fussnoteWeiter(k)`
  - `endnoteZurueck(k)`
  - `endnoteWeiter(k)`
  - `quelleNeu(k)`
  - `quellenVerwalten(k)`
  - `zitat(k)`
  - `zitierweise(k)`

## `editor`

### `editor/__init__.py`

Dokumentlogik rund um QTextDocument: Seiten, Umbruch, Fußnoten, Formeln, Stile, Formularfelder, Ausgabe.


### `editor/absatzopt.py`

Absatzoptionen des Absatz-Fensters (Reiter „Zeilen- und Seitenumbruch“ und die Raster-Haken): Vorgaben, Speichern am Absatz, DOCX.

- `lesen(bf)` — Alle Absatzoptionen eines Absatzformats (Vorgabe, wo nichts gesetzt ist).
- `setzen(bf, w)`
- `als_text(w)` — Die Abweichungen von der Vorgabe als ``Schlüssel=Wert;…`` (für eine Formatvorlage; leer = nur Vorgaben).
- `aus_text(text)`
- `in_ppr(ppr, w)` — Abweichungen von der Vorgabe als Elemente an ``w:pPr`` schreiben (in der Reihenfolge, die das Schema verlangt).
- `aus_ppr(ppr)` — Das Gegenstück zu ``in_ppr``: die Absatzoptionen aus ``w:pPr`` (nur, was gesetzt ist).

### `editor/abschnitte.py`

Abschnitte: Seiteneinrichtung, die mitten im Dokument wechseln kann.

- `seite_zu_dict(ps)`
- `seite_aus_dict(d)`
- `eintrag(typ, ps)`
- `lesen(blockformat)`
- `umbrueche(doc)` — [(Blocknummer, Beginn, Einrichtung des folgenden Abschnitts)] in Dokumentreihenfolge.
- `anzahl(doc)`
- `index_bei(doc, position)` — Nummer (0-basiert) des Abschnitts, in dem die Position liegt.
- `einrichtung(doc, basis, index)` — Einrichtung des Abschnitts `index` (0 = Dokumenteinrichtung); verknüpfte Kopf-/Fußzeilen werden vom Vorgänger übernommen.
- `alle_einrichtungen(doc, basis)` — [(Beginn, Einrichtung)] für jeden Abschnitt (der erste mit Beginn „naechste“).
- `beginn(doc, index)` — Zeichenposition, an der Abschnitt `index` beginnt.
- `ende(doc, index)`
- `_setze(cursor, wert)`
- `einfuegen(doc, cursor, typ, basis)` — Abschnittsumbruch an der Schreibmarke: der Absatz wird geteilt, der erste Teil beschließt den Abschnitt.
- `einfuegen_an(doc, position, typ, basis)` — Abschnitt ab ``position`` beginnen lassen (z. B. am Anfang der aktuellen Seite). Steht die Stelle am Anfang eines Absatzes, beschließt
- `entfernen(doc, index)` — Den Umbruch am Ende von Abschnitt `index` entfernen (ist es der letzte, den davor): die beiden Abschnitte werden einer
- `setzen(doc, index, ps, typ)` — Einrichtung (und Beginn) eines Abschnitts ab dem zweiten ändern; für den ersten gilt `ed.page`.
- `_gleiche_geometrie(a, b)`
- `teile(qdoc, basis)` — Für Seitenansicht, Druck und PDF: [(Dokument, Einrichtung, Beginn)] je Abschnitt und Hinweise.

### `editor/anzeige_extra.py`

Anzeige- und Druckhilfen: ausgeblendeter Text, Feldschattierung, Feldcodes, Zeichnungsobjekte, geänderte Zeilen, Objektanker.

- **class `VersteckterText`**(QSyntaxHighlighter) — Ausgeblendeter Text (Eigenschaft P_VERSTECKT) wird nur in der Anzeige unsichtbar gemacht (winzige, durchsichtige Schrift)
  - `__init__(doc, zeigen)`
  - `setze_zeigen(an)`
  - `highlightBlock(text)`
- `_bereiche(d, prop)` — [(von, bis, wert)] zusammenhängender Zeichenbereiche mit der Eigenschaft prop.
- `versteckte_entfernen(d)` — Löscht den ausgeblendeten Text aus der KOPIE (Druck, PDF, Seitenzählung). → Anzahl gelöschter Bereiche.
- `feldcodes_einsetzen(d)` — „Feldfunktionen drucken“: an die Stelle des Ergebnisses tritt der Feldcode in geschweiften Klammern.
- `feldbereiche(d)`
- `zeichnungen_entfernen(d)` — „Zeichnungsobjekte drucken“ aus: Formen, WordArt, Diagramme und SmartArt (Bilder mit P_OBJEKT) fehlen im Ausdruck.
- `aenderungszeilen(d)` — Senkrechte Bereiche (oben, unten) in Dokumentkoordinaten aller Zeilen, in denen verfolgte Änderungen stehen.

### `editor/auswahl.py`

Auswählen (Start ▸ Auswählen): Tabellen ohne sichtbaren Rahmen finden und Stellen mit gleicher Zeichenformatierung sammeln — ohne Oberfläche.

- `_tabellen(rahmen)`
- `ohne_rahmen(t)`
- `tabelle_ohne_rahmen(ed)` — Markiert die nächste Tabelle ohne Rahmen hinter der Schreibmarke (am Ende geht es vorn weiter). → False, wenn es keine gibt.
- `_merkmale(cf)`
- `aehnlich_formatiert(ed)` — Alle Strecken mit derselben Zeichenformatierung wie das Zeichen an der Schreibmarke (je Absatz zusammengefasst).

### `editor/bildeffekte.py`

Effekte für Bilder und Formen, die Lunivo selbst zeichnet: Schatten, Reflektion (Spiegelung), Leuchten, Weiche Kanten, 3D-Format (Tiefe)

- `_merken(schluessel, bauen)`
- `_maske(bild, groesse, ellipse)` — Die Form des Bildes (Alpha) in der gewünschten Größe: das Bild selbst, in einer Ellipse beschnitten, wenn ``ellipse``.
- `_getoent(maske, farbe)`
- `_weich(img, radius)` — Weichzeichnen durch Verkleinern und Vergrößern (billig und gleichmäßig); der Rand muss vorher frei sein.
- `weiche_kanten(bild, r, ellipse, radius_pt)` — Das Bild mit weich auslaufendem Rand (Alpha nimmt zum Rand hin ab), in der Größe ``r``.
- `_schatten_bild(bild, w, h, ellipse, farbe, weich_px, faktor)` — (Bild des Schattens mit Rand ringsum, Randbreite): die getönte Form, um ``faktor`` skaliert und weichgezeichnet.
- `unter_zeichnen(p, bild, r, ellipse, fx)` — Leuchten, Schatten und Reflektion hinter dem Bild (in der Reihenfolge der Schichten: Leuchten zuerst).
- `_stufenfarbe(basis, material, licht, t)` — Farbe der Tiefe in Stufe ``t`` (0 = vorn, 1 = hinten) nach Material und Beleuchtung (dieselben Namen wie bei den Texteffekten).
- `tiefe_richtung(dreh)` — Einheitsvektor, in dem die Tiefe nach hinten läuft: schräg nach rechts unten, bei gedrehtem Objekt (3D-Drehung X/Y) entsprechend verschoben.
- `extrusion_zeichnen(p, bild, r, ellipse, d3, dreh)` — 3D-Format: die Form des Bildes (Alpha) als Tiefe nach hinten gestapelt (``tiefe`` pt, Farbe, Material, Beleuchtung), dazu eine Kontur
- `_dreht(dreh)`
- `hat_drehung(fx)` — True, wenn ``fx["drehung"]`` das Bild dreht (``drehung_3d``).
- `hat_nachbearbeitung(fx)` — True, wenn das Bild vor dem Zeichnen mit ``bild_nachbearbeiten`` verändert werden muss (gedreht oder mit oberem Abschluss).
- `hat_abschluss(fx)`
- `bild_nachbearbeiten(bild, r, ellipse, fx)` — Das Bild für das Zeichnen vorbereiten: oberer Abschluss des 3D-Formats eingearbeitet, dann im Raum gedreht (3D-Drehung). Die Form ist danach
- `_projektion(w, h, dreh)` — (Zielviereck, Faktor) der gedrehten Bildfläche: Drehung um X, Y, Z und Perspektive (Sichtwinkel ``persp``, 0 = parallel), eingepasst in ``w`` × ``h``.
- `drehung_3d(bild, r, ellipse, dreh)` — Das Bild (Größe ``r``) im Raum gedreht (``x``, ``y``, ``z`` Grad, ``persp``); dieselbe Größe, die Fläche passt vollständig hinein.
- `_erodiert(m, rad)` — Die Form um ``rad`` px nach innen verkleinert (Schnitt der in acht Richtungen verschobenen Form).
- `_band(aussen, innen)`
- `_licht(band, art, st, umgekehrt)` — Das Band mit Licht von links oben: hell oben links, dunkel unten rechts (``st`` = Stärke 0…1).
- `abschluss_oben(bild, r, ellipse, ab)` — Oberer Abschluss: ein Rand der Breite ``breite`` pt rundum, von links oben beleuchtet; ``hoehe`` pt bestimmt die Stärke von Licht und Schatten.
- `abschluss_symbol(art, groesse)` — Bildchen für die Auswahl der Abschlussart: eine graue Fläche mit dem Abschluss.

### `editor/bildlayout.py`

Das Fenster „Layout“ (ui/baukasten/layout_dialog.py) mit einem Bild verbinden: Werte vom Bild lesen, die Wahl auf das Bild anwenden.

- `ziel(ed)` — („frei“, Schlüssel, Angabe, Bild) oder („text“, Cursor) für das markierte Bild; sonst None.
- `_achse_lesen(a, waagerecht, seite_mm)`
- `lesen(ed, z)`
- `_box(page, bezug, waagerecht)`
- `_achse_schreiben(a, w, page, waagerecht)`
- `_mass(w, page, waagerecht, alt)`
- `anwenden(ed, z, werte)` — Schreibt die Wahl des Fensters (oder eines Teils davon: nur die genannten Schlüssel) auf das Bild.
- `_abstand_setzen(ed, abstand)` — „Abstand zum Text“ (oben/unten/links/rechts, mm): die Ränder des Rahmens, in dem das umflossene Bild schwebt.
- `_speichern_frei(ed, key, neu)`
- `_text_zu_frei(ed, c, w, hinter)` — Ein Bild im Text wird frei: es verlässt die Zeile und liegt, wo der Absatz beginnt (dort lässt es sich ziehen).
- `_frei_zu_text(ed, key, a, bild, w)` — Ein freies Bild kommt in den Text: es steht am Anfang seines Absatzes (in der Zeile, links/rechts umflossen oder allein).
- `format_lesen(ed, z)` — Füllung, Kontur und Effekte des markierten freien Bildes im Format des Panels (``ObjektFormatPanel``); sonst None.
- `fx_alle(ed, fx)` — Seitenlayout ▸ Effekte: dieselben Effekte an alle frei liegenden Bilder und Formen des Dokuments (``{}`` nimmt sie weg). → Anzahl.
- `format_aus_panel(ed, z, werte)` — Wendet die Werte des Panels an: Füllung, Kontur und alle Effekte (fehlende Effekte sind ausgeschaltet).
- `format_setzen(ed, z, fuell, rand, rand_teil, fx)` — Füllung (``fuell``: Wörterbuch oder None) und/oder Kontur (``rand``: Wörterbuch oder None; ``rand_teil`` ändert nur einzelne Angaben der
- `fuellbild_setzen(ed, z, bild)` — „Füllung ▸ Bild“: das Bild als Füllung; im Text liegt es als Ressource des Dokuments, in der Kopfzeile am Bild selbst.
- `frei_aendern(ed, z, **teile)` — Einzelne Angaben des markierten freien Bildes ersetzen (Schlüssel der Angabe: ``dreh``, ``hinter`` …).
- `ausrichten(ed, z, wie)` — Das freie Bild am Blatt ausrichten (links/mitte/rechts, oben/mittig/unten).
- `drehen(ed, z, grad)`
- `ebene(ed, z, vorn)` — „Eine Ebene nach vorne/hinten“: das Bild liegt vor oder hinter dem Text (frei positioniert).
- `masse_lesen(ed, z)` — Breite und Höhe des markierten Bildes in mm.
- `masse_setzen(ed, z, breite_mm, hoehe_mm)`
- `format_merken(z)` — Füllung, Kontur und Effekte des markierten freien Bildes zum „Format übertragen“.
- `format_uebertragen(ed, z, merk)`
- `_hoehe_je_breite(img, a)` — Höhe je Breite des sichtbaren Ausschnitts von ``img`` (mit Zuschnitt ``zu`` der Angabe).
- `frei_bild_ersetzen(ed, z, wandle)` — ``wandle(QImage) → QImage``: das Bild des markierten freien Bildes wird durch das Ergebnis ersetzt (Anzeigebreite bleibt, die Höhe
- `frei_original(ed, z)` — Farbänderung und Zuschnitt zurücknehmen (das ursprüngliche Bild, gleiche Anzeigebreite).
- `frei_original_groesse(ed, z)` — Das Bild in seiner Pixelgröße.
- `frei_entfernen(ed)` — Das gewählte freie Bild löschen (wie die Entf-Taste).

### `editor/bildwerkzeuge.py`

Weitere Bildtools für frei positionierte Bilder (Datei, Bildschirmfoto, Piktogramm): Seitenverhältnis sperren, transparente Farbe,

- `frei_bild(ed)` — Das gewählte freie Bild (Datei, Bildschirmfoto, Piktogramm) als Ziel für ``bildlayout``, sonst None.
- `sperre(z)`
- `sperre_umschalten(ed, z, an)` — Seitenverhältnis sperren: Ziehen an den Kanten hält es dann auch, die Größen-Eingabe ebenfalls.
- `farbe_transparent(img, farbe, toleranz)` — Alle Bildpunkte, die ``farbe`` (innerhalb der Toleranz je Farbkanal) gleichen, werden durchsichtig.
- `transparent(ed, z, farbe, toleranz)`
- `aendern(ed, z, bild, alt)` — Bild ändern: ``bild`` ersetzt den Inhalt; Größe, Lage, Rahmen, Füllung und Effekte bleiben, Zuschnitt und Farbänderung entfallen.
- `aus_datei(ed, z, pfad)`
- `komprimieren(ed, z, beschnitt_loeschen)` — Bild komprimieren: weggeschnittene Bereiche löschen (wenn ``beschnitt_loeschen``) und auf ``KOMPRIMIEREN_FAKTOR`` × Anzeigegröße
- `werte(a)` — (Helligkeit, Kontrast) in Prozent aus der Angabe des Bildes.
- `korrigiert(bild, hell, kontrast)` — Das Bild mit Helligkeit und Kontrast (Prozent): Kontrast streckt die Werte um die Mitte, Helligkeit verschiebt sie; Alpha bleibt.
- `korrektur_setzen(ed, z, hell, kontrast)` — Helligkeit und/oder Kontrast (begrenzt auf -100 bis 100) des freien Bildes setzen; 0 entfernt die Angabe.
- `korrektur_schritt(ed, z, hell, kontrast)` — Helligkeit/Kontrast um die Schritte ``hell``/``kontrast`` (Prozent) ändern.
- `zuruecksetzen(ed, z)` — Bild zurücksetzen: ursprüngliches Bild (vor Farbänderungen), kein Zuschnitt, keine Maske, Rahmen, Füllung, Effekte und Drehung weg;

### `editor/bildzuschnitt.py`

Zuschneiden frei positionierter Bilder — nicht zerstörend (die Bilddaten bleiben unverändert).

- `formen_kategorien()` — Die Formen zum Zuschneiden: (Kategorie, [Formnamen]) aus dem Formenkatalog, ohne Linien — für die Galerie.
- `lesen(a)` — (links, oben, rechts, unten) als Anteile; ohne Zuschnitt (0, 0, 0, 0).
- `hat(a)`
- `anzeige(bild, a)` — Der sichtbare Ausschnitt von ``bild`` (mit Formmaske); ohne Zuschnitt und Maske das Bild selbst. Zwischengespeichert.
- `_quelle(ed, a)`
- `_skalen(a)` — Anzeigepunkte je Anteil des ganzen Bildes (waagerecht, senkrecht).
- `setzen(ed, z, zu, maske, b, h)` — Zuschnitt ``zu`` = (links, oben, rechts, unten) als Anteile (None: Zuschnitt entfernen) und/oder Formmaske (``""``: entfernen); was nicht
- `skala(ed, z, breite, hoehe)` — Nach Skala (Seitenverhältnis) zuschneiden: der größte mittige Ausschnitt mit diesem Verhältnis; die Breite des Rahmens bleibt.
- `skala_text(ed, z, text)` — ``"16:9"`` (oder ``(16, 9)``) → ``skala``.
- `form(ed, z, name)` — Nach Form zuschneiden: der Ausschnitt wird in die Form (Name aus dem Formenkatalog) eingepasst; Zuschnitt bleibt.
- `zuruecksetzen(ed, z)` — Form und Größe zurücksetzen: Maske und Zuschnitt weg, das ganze Bild in der bisherigen Breite im ursprünglichen Seitenverhältnis.
- `aus_ziehen(a0, neu, griff)` — Zuschneiden durch Ziehen an einem Griff: ``a0`` die Angabe vor dem Ziehen, ``neu`` die mit der gezogenen Größe (``b``, ``h``).

### `editor/deckblatt.py`

Deckblätter (Einfügen ▸ Deckblatt): 17 Gestaltungen in den Gruppen der Vorlage (Artikel, Firma, Lebenslauf, Abschlussarbeit), je im

- **class `Feld`** — Ein Platzhalter-Absatz: ``y`` = Oberkante als Anteil der Blatthöhe, ``x`` = linker Rand als Anteil der Blattbreite (bei links).
- **class `Gestaltung`**
- `_kontakt(y, farbe, x, ausrichtung, abstand)`
- `_arbeit(y, farbe)`
- `gestaltung(name)`
- `_verlauf(r, farben, senkrecht)`
- `_wolken(p, r, y, farbe, n)`
- `_segelboot(p, x, y, s)`
- `_puzzle(p, x, y, s, farbe)`
- `_blume(p, cx, cy, s)`
- `_grafik(p, name, r)` — Die Grafik einer Gestaltung (ohne Text) auf das Blatt ``r``.
- `_schrift(f, blatt_hoehe_px, quer)` — Schrift eines Feldes im Maßstab des Blattes (Original: A4 hoch = 1123 Bildpunkte; quer etwas kleiner).
- `zeichnen(p, name, r, mit_text)` — Gestaltung ``name`` auf das Blatt ``r`` (weißer Grund, Grafik, auf Wunsch die Platzhalter): für die Galerie.
- `grafik_bild(name, breite_px, hoehe_px)`
- `hat_deckblatt(doc)`
- `entfernen(ed)` — Das Deckblatt (erster Abschnitt mit ``B_DECKBLATT``) herausnehmen; das Dokument bekommt die Einrichtung des zweiten Abschnitts.
- `einfuegen(ed, name, quer)` — Deckblatt ``name`` als ersten Abschnitt an den Anfang setzen (ersetzt ein vorhandenes).
- `_bild_text(img)`

### `editor/designs.py`

Designs des Reiters Seitenlayout: Farbschemen, Schriftpaare, Effekte und die Designs, die alles drei bündeln. Keine Oberfläche.

- `ueberschrift_farbe(schema)` — Die Farbe der Überschriften eines Farbschemas: Akzent 1.
- `design(name)` — Was ein Design setzt: {"kopf", "text", "farbe", "farben"} (Schriften, Überschriftfarbe, das ganze Farbschema).

### `editor/diagramm.py`

Diagramme als Bild (Einfügen ▸ Diagramm), gezeichnet mit QtCharts. Keine Oberfläche.

- `_farbe(i)`
- `kombi_vorgabe(untertyp, anzahl)` — Belegung der Kombinationstabelle für eine fertige Kombination (die letzte Reihe ist Linie bzw. Säule).
- `_art(daten)`
- `_filtern(kategorien, reihen, ausgeblendet)` — Diagrammfilter: → (Stellen der sichtbaren Reihen, Stellen der sichtbaren Rubriken, Rubriken, Reihen) ohne die ausgeblendeten.
- `bild(untertyp, titel, kategorien, reihen, b, h, legende, kombi, farben, kachel, titel_an, legende_pos, labels, stil, skala, elemente, ausgeblendet, teil_format, geo)` — ``skala``: Bild in dieser Auflösung (Maße ``b``/``h`` logisch, das Bild ist ``skala``-mal so groß, Schrift bleibt scharf).
- `bild_aus_daten(d, b, h, skala, geo)` — Das Diagramm aus den gespeicherten Daten (``a["daten"]``) in b × h Bildpunkten.
- `_bild(untertyp, titel, kategorien, reihen, b, h, legende, kombi, kachel, legende_pos, labels, stil, skala, opt)`
- `stile_liste()` — Alle Formatvorlagen (Diagrammstile) für die Galerie: {nr, name, grund, schrift, raster, **Zusätze}.
- `_monochrom(basis)` — Sechs Töne einer Farbe, vom dunklen zum hellen.
- `farbschemen_gruppen()` — Die Gruppen „Farbig“ und „Monochrom“ mit ihren Farbzeilen (Kopie von ``FARBSCHEMEN``).
- `farbschemen_flach()` — Alle Farbzeilen hintereinander (Nummer = Argument von ``diagrammFarben``).
- `_stil_anwenden(ch, stil, kachel, gitter)` — Schrift- und Rasterfarben des Stils. Den Grund malt ``_bild`` selbst (das Diagramm liegt auf einer durchsichtigen Ebene).
- `_elemente_anwenden(ch, u, el, werte, namen, nummern, tf)` — Achsen, Achsentitel, Trendlinien und die Schrift-/Linienformate der Teile (``teil_format``).
- `_text_fuer(tf, teil)` — Das Textformat eines Teils: die Angaben des Diagrammbereichs gelten für alle, der Teil überschreibt sie.
- `_eigene_texte(p, ch, g, tf, titel, standard, legende_an)` — Titel und Legende mit Textfüllung (Verlauf, Keine), Kontur und Effekten: QtCharts zeichnet sie durchsichtig, hier kommt der Text selbst darüber.
- `_pfeile(p, ch, u, kategorien, werte, namen, nummern, tf)` — Pfeile und Linienenden an Linien- und Kurvenreihen (``linie.pfeil_anfang`` / ``pfeil_ende``).
- `_kombination(ch, kombi, namen, werte, kategorien)` — Jede Reihe mit eigenem Typ; Reihen mit Sekundärachse an einer zweiten Werteachse rechts.
- `_legenden_namen(u, namen, kategorien)`
- `teile(daten)` — Die wählbaren Teile des Diagramms (Schlüssel, Anzeigename), in der Reihenfolge des Feldes „Diagrammbereich“: Diagrammbereich,
- `teil_geo(daten, b, h)` — Wie ``teil_rechtecke``, aber mit allen Angaben der Geometrie (auch ``balken_<n>`` = Liste der einzelnen Balken einer Reihe).
- `teil_rechtecke(daten, b, h)` — Schlüssel (siehe ``teile``) → QRectF in Bildpunkten des gezeichneten Bildes (b × h, logische Maße) — zum Anklicken. Die Lage kommt

### `editor/diagramm_format.py`

Formate der Diagrammteile (``daten["teil_format"][teil]``): Füllung, Linie, Effekte, Text und Optionen von Achse und Reihe. Keine Oberfläche.

- `fuell_dict(f)` — Die Füllung als Wörterbuch; None bei Automatisch (nicht gesetzt) und bei „Keine Füllung“ (``""``).
- `ist_keine(f)`
- `hauptfarbe(f)` — Die Farbe, mit der eine Reihe (Legende, Linien, Kreisstücke) gezeichnet wird, wenn der Pinsel selbst nicht möglich ist.
- `bild_kodieren(img, laengste_seite)` — Ein Füllbild für die Daten des Diagramms: höchstens ``laengste_seite`` Bildpunkte, PNG, als Text (steckt im „lunivo:“-Titel der DOCX-Datei).
- `bild_dekodieren(text)`
- `pinsel(fuell, r)` — (Pinsel, Deckkraft 0…1) der Füllung; ``r`` ist das Rechteck, das gefüllt wird (ohne: der Pinsel gilt für das jeweils gezeichnete Objekt,
- `flaeche_zeichnen(p, r, fuell)`
- `flaeche_bild(fuell, w, h, aufl)` — Die Füllung als Bild (für die Effekte, die mit einem Bild arbeiten).
- `linie_keine(linie)`
- `stift(linie, standard_farbe, r)` — Der Stift einer ``linie`` (Breite in pt): Strichart über ``freie_bilder._stift``, dazu Transparenz, Abschluss, Verknüpfung und Farbverlauf.
- `_verlauf_pinsel(v, r, alpha)`
- `rahmen_zeichnen(p, r, linie)` — Die Linie um ein Rechteck; ``kombiniert`` (Doppelt, Dick–dünn) zeichnet die Konturformen von ``textfx``, ``rund`` rundet die Ecken.
- `fx_normal(fmt)` — Die Effekte eines Teils im Format von ``bildeffekte`` (``True`` und ältere Angaben ergänzt).
- `teil_zeichnen(p, r, fmt, grund, nur_hinter)` — Füllung und Effekte eines Teils unter dem Diagramm. Ohne Füllung brauchen die Effekte eine Fläche: dann dient ``grund`` (Hintergrund des Stils).
- `feld_von(t)`
- `textwinkel(t)` — Der Winkel des Textes in Grad (im Uhrzeigersinn): Textrichtung und benutzerdefinierter Winkel zusammen.
- `effekt_von(t)`
- `text_eigen(t)` — Muss der Text selbst gezeichnet werden (QtCharts kann Verläufe, Kontur, Schatten … nicht)? Gilt für Titel und Legende.
- `textfarbe(t, standard)` — Farbe des Textes mit Transparenz; „Keine Füllung“ ist ganz durchsichtig.
- `schrift_aus(basis, t)`
- `box_rect(teil, r, t, gesamt_breite)` — Das Feld des Teils um den Text: ohne „Größe der Form dem Text anpassen“ ist der Titel so breit wie das Diagramm; die Ränder liegen außen herum.
- `text_feld(box, t)` — Der Platz für den Text im Feld des Teils (``box_rect`` ohne die Ränder).
- `_umbrechen(text, fm, breite)`
- `text_zeichnen(p, feld, text, font, t, standard, umbrechbar)` — Text mit Textfüllung, -kontur und Effekten (Schatten, Spiegelung, Leuchten, 3D) in ``feld``: waagerecht mittig, senkrecht nach ``vertikal``,
- `achse_anwenden(achse, opt, wert)` — Die Optionen einer Achse (``achse`` im Teilformat) auf die QtCharts-Achse. ``wert``: Wertachse (Minimum, Maximum, Hauptintervall).
- `luecke_zu_breite(prozent)` — Lückenbreite in Prozent der Säulenbreite → ``barWidth`` der Serie (Anteil der Kategorie, den die Säulen füllen).
- `pfeil_zeichnen(p, spitze, von, art, breite_pt, groesse, farbe)` — Ein Linienende an ``spitze``; ``von`` ist der benachbarte Punkt der Linie (gibt die Richtung).

### `editor/diagramm_geo.py`

Lage der Diagrammteile im gezeichneten Bild (aus der QtCharts-Geometrie nach dem Layout). Keine Oberfläche.

- `_serie(ch, name)` — Die Serie zur Datenreihe ``name`` (bei Säulen/Balken der Satz in der Serie); → (Serie, Satz oder None).
- `punkte(ch, u, kategorien, werte, namen)` — Je Reihe die Punkte (x, y, Wert) in Bildpunkten, Säulen/Balken in der Mitte ihres Balkens. Gestapelte Typen: Oberkante des Stapels.
- `_balken(ch, u, punkte_, i, m, n)` — Die einzelnen Balken einer Reihe (nur Säulen/Balken).
- `legenden_items(ch)` — Je Eintrag der Legende (Rechteck des Eintrags, Rechteck des Beschriftungstextes) aus den Grafikelementen von QtCharts, in Bildpunkten;
- `titel_rect(ch)` — Das Rechteck des Titeltextes (QtCharts-Element), sonst None.
- `_legendeneintraege(ch, namen, r)` — Die Einträge der Legende: aus den Grafikelementen von QtCharts; ohne sie eine Näherung (nebeneinander oben/unten, untereinander links/rechts).
- `geometrie(ch, u, kategorien, werte, namen, nummern, b, h, titel, legende_an, achsen_an, legenden_namen)` — Alle Teile → Rechteck (siehe Kopf); ``nummern`` = Stelle jeder sichtbaren Reihe in den gespeicherten Daten.
- `_vereinigung(rects)`
- `_umhuellung(pts, pa)`

### `editor/diagramm_teile.py`

Diagrammteile am gewählten Diagramm (freies Objekt): Auswahl, Treffer beim Mausklick und Formate je Teil. Keine Oberfläche.

- `teil_gewaehlt(ed)` — Schlüssel des gewählten Diagrammteils des gewählten Diagramms oder None (auch wenn der Teil inzwischen fehlt).
- `teil_name(ed)` — Anzeigename des gewählten Teils (Feld „Diagrammbereich“ in den Diagrammtools); leer, wenn keiner gewählt ist.
- `teil_waehlen(ed, schluessel)` — Einen Teil wählen (None: Auswahl aufheben). Das Bild wird nicht neu gezeichnet.
- `_geo(ed, d, b, h)` — Geometrie der Teile, zwischengemerkt, bis sich Daten oder Größe ändern.
- `teil_bei(ed, pos)` — Der Diagrammteil unter ``pos`` (QPointF im Editor, dieselben Koordinaten wie die Rechtecke von ``ed._frei_liste()``) für das gewählte
- `diagramm_teil_format_lesen(ed, teil)` — Das Format des gewählten Teils (oder von ``teil``) als Kopie; leer, wenn nichts gesetzt ist oder kein Diagramm gewählt ist. Beim Diagrammbereich
- `_ohne_leer(w)`
- `diagramm_teil_format_setzen(ed, teil, **kw)` — Format des gewählten Teils (``teil`` nennt einen anderen) ändern und das Diagramm neu zeichnen. ``fuell`` (Farbe, Wörterbuch, ``""`` = keine

### `editor/diagramm_zusatz.py`

Diagramm: Elemente (Diagrammelemente-Liste), Teilformate und Zusätze, die QtCharts nicht selbst zeichnet. Keine Oberfläche.

- `elemente_wirksam(d)` — Alle neun Elemente mit ihrem Wert: Wahrheitswerte, bei ``legende`` die Lage (``oben`` … ``rechts``) oder ``aus``.
- `trend(werte)` — Lineare Regression y = a + b·x über x = 0 … n-1 → (a, b).
- `stift(linie, standard_farbe)` — Stift aus {farbe, breite (Bildpunkte), art}; die Strichart kommt aus ``freie_bilder._stift`` (dieselbe wie bei Bildern und Formen).
- `schrift_aus(basis, text)`
- `hintergruende(p, geo, tf, grund)` — Füllung und Effekte von Diagrammbereich, Zeichnungsbereich, Titel, Legende und Reihen — unter dem Diagramm (``diagramm_format``).
- `linien(p, geo, tf)` — Die Linien (Rahmen) der Teile mit ``linie`` — über dem Diagramm.
- `fehlerindikatoren(p, ch, u, pts, hoechst, farbe)` — Feste Balken ± ``FEHLER_ANTEIL`` des Höchstwerts an jedem Punkt (nicht bei Balken, Kreis, Netz und gestapelten Typen).
- `tabelle(p, r, kategorien, namen, werte, farben, schrift)` — Datentabelle: Kopfzeile mit den Rubriken, darunter je Reihe ein Farbfeld, der Name und die Werte.

### `editor/druck.py`

Drucken nach den Einstellungen des Druckfensters: Seitenauswahl, Blattseiten, mehrere Seiten pro Blatt, anderes Papier.

- `papier_name(b_mm, h_mm)` — „A4“ für 210 × 297 (mit 2 mm Toleranz, in beiden Lagen), sonst „Benutzerdefiniert“.
- `bereich_lesen(text, gesamt)` — „1-3, 5“ → [1, 2, 3, 5]. Seiten außerhalb 1..gesamt fallen weg; ungültige Eingabe oder nichts Übriges → None.
- `seiten_nach_wahl(ein, gesamt)` — Welche Seiten das Druckfenster meint (aufsteigend); ohne gültigen Bereich alle.
- `blatt_zeichnen(p, rect, bilder, pro_blatt, rand)` — Setzt die Seitenbilder in einem Raster auf das Blatt; jedes wird ins eigene Feld eingepasst (Seitenverhältnis bleibt).
- `optionen_aus(opt, ein, noten)` — Die Ausgabeoptionen der Einstellungen, ergänzt um die Wahl im Druckfenster.
- `zwischen_pdf(qdoc, page, opt, noten, pfad)`
- `pdf_seiten_bilder(pfad, breite_px, nummern)` — Rastert Seiten (Nummern ab 1 in der Zwischen-PDF) auf die gewünschte Breite.
- `vorschau_bild(qdoc, page, opt, noten, nummern, breite_px)` — Die Seiten `nummern` (der Ausgabe, ab 1) so, wie die Optionen sie ausgeben — für die Vorschau.
- `drucken(printer, qdoc, page, opt, ein, noten)` — Druckt nach den Einstellungen `ein` (Ergebnis des Druckfensters). → Zahl der gedruckten Seiten.
- **class `Zwischenseiten`** — Das Dokument einmal als Zwischen-PDF ausgegeben und geladen; jede Seite lässt sich in beliebiger Größe rastern (Druckvorschau).
  - `__init__(qdoc, page, opt, noten)`
  - `anzahl()`
  - `groesse_px(n, zoom)` — Größe der Seite n bei 96 dpi mal Zoom.
  - `bild(n, zoom)`
  - `schliessen()`

### `editor/einfuegen.py`

Einfügen: Formen, WordArt, Diagramme, Piktogramme, Formeln, Schnelltabellen, Deckblätter, Text aus Datei.

- `qimage_einfuegen(ed, img, alt, art, daten)` — Bild an der Schreibmarke einfügen. art/daten (Form, WordArt, Diagramm, …) bleiben am Bild, damit es sich wieder bearbeiten
- `_leer(w, h)`
- `form_pinsel(fuell, art, r)` — Füllung einer Form: ``art`` leer = einfarbig, ``verlauf`` (hell nach Farbe), ``abgestuft`` (drei Stufen), ``glanz`` (obere Hälfte heller).
- `form_bild(art, breite, hoehe, fuell, linie, strich, text, skala, adj, fuell_art, punkte)` — ``skala``: Bild in dieser Auflösung (Maße und Strich bleiben logisch, das Bild ist ``skala``-mal so groß) — für scharfe freie Formen.
- `wordart_vorlage_bild(text, nr, schrift, pt)` — WordArt nach einem der 15 Stile der Galerie: Füllverlauf, Kontur und Schatten.
- `wordart_bild(text, stil, schrift, pt, farbe, vorlage)`
- `diagramm_bild(art, titel, kategorien, reihen, b, h)` — ``art``: Untertyp aus ``editor.diagramm.TYPEN`` oder einer der früheren Namen (Säulen, Balken, Linie, Kreis).
- `piktogramm_bild(name, px, farbe)`
- `formel_teile(text)` — Einfache Schreibweise → [(Text, "normal"\|"hoch"\|"tief")]:  a^2  x_{12}  sqrt(x)  frac(a,b)  \alpha
- `formel_bild(text, pt, farbe)` — Die Formel als Bild (Vorschau im Fenster „Formel“ und in der Gleichungsgalerie).
- `formel_einfuegen(ed, text)`
- `_tabelle(ed, zeilen, kopf, breit)`
- `schnelltabelle(ed, name)`
- `deckblatt_einfuegen(ed, vorlage, titel, untertitel, autor, datum)`
- `datei_symbol_bild(name, symbol, breite)` — Dateisymbol mit Namen darunter (Einfügen ▸ Objekt ▸ Als Symbol anzeigen).
- `text_aus_datei(ed, pfad)`
- `datum_feldanweisung(fmt)` — Qt-Datumsformat → Word-Feld (DATE, bei reinen Uhrzeiten TIME) für „Automatisch aktualisieren“.
- `datum_text(fmt, sprache)`
- `initiale(ed, zeilen)` — Erster Buchstabe des Absatzes groß (Hängende Initiale ist mit Qt nicht möglich — er steht in der Zeile).
- `textfeld(ed, text, breite)` — Ein Textfeld als einzellige Tabelle mit Rahmen (frei schwebende Textfelder kennt Qt nicht).
- `_bild_cursor(ed)`
- `bild_ersetzen(ed, wandle)` — wandle(QImage) → QImage; das Bild im Text wird durch das Ergebnis ersetzt (Anzeigebreite bleibt, Seitenverhältnis folgt).
- `bild_original(ed)`
- `farbe_anwenden(img, modus)`
- `zuschneiden(img, links, oben, rechts, unten)`
- `drehen(img, art)`

### `editor/fassungen.py`

Fassungen eines Dokuments mit verfolgten Änderungen, für die Anzeige „Original“: eine Kopie, in der jede Einfügung fehlt und jede

- `_stuecke(doc)`
- `original(doc)`
- `bearbeiter(doc)`
- `zeiten(doc)`

### `editor/felder.py`

Felder einfügen (Einfügen ▸ Schnellbausteine ▸ Felder …) wie in der WPS-Vorlage: Feldnamen, Feldfunktionen und Assistent.

- `vorgabe(name)`
- `_schalter(anweisung, zeichen)`
- `_ohne_schalter(anweisung)`
- `schreibweise(n, art)`
- `zahl_formatieren(wert, muster)` — Zahl nach einem Muster wie ``#.##0,00``, ``0 %`` (deutsche Schreibweise); ohne Muster so kurz wie möglich.
- `ergebnis(anweisung, kontext)` — Das Feldergebnis jetzt. ``kontext`` aus ``kontext_sammeln`` (alle Angaben freiwillig).
- `formel(text, kontext)` — Ausdruck rechnen; ValueError bei Fehlern. Bereiche (ABOVE …) kommen aus ``kontext["bereiche"]``, Textmarken aus
- `_funktion(n, w)`
- `_zahl(text)`
- `tabellen_bereiche(ed)` — Zahlen über, unter, links und rechts der Zelle an der Schreibmarke (leer außerhalb von Tabellen).
- `kontext_sammeln(ed, autor, pfad)`
- `feld_einfuegen(ed, anweisung, text, versteckt)` — ``versteckt``: ausgeblendeter Text (TC-Einträge stehen wie in Word unsichtbar im Text).

### `editor/formen.py`

Formen nachträglich ändern (Füllung, Kontur, Vorlage, Größe) und Formen zu einer Gruppe zusammenfassen.

- `objekt(f)`
- `ist_form(f)`
- `form_daten(o, breite, hoehe)`
- `_zeichnen(d)`
- `_gruppe_zeichnen(kinder)`
- `_ersetzen(ed, c, img, o, f, breite, hoehe)`
- `frei_daten(ed)` — Die Parameter der gewählten Form als freies Objekt (Kopie) oder None.
- `aendern(ed, **felder)` — Parameter der markierten Form ändern (fuell, linie, strich, text, form, breite, hoehe) und neu zeichnen. Eine als freies Objekt
- `vorlage(ed, name)`
- `_auswahl_formen(ed)` — Alle Formbilder der Markierung (Position, Format); nur wenn die Markierung sonst leer ist.
- `gruppieren(ed)` — → '' bei Erfolg, sonst die Begründung.
- `gruppe_aufheben(ed)`
- `zeichenbereich_bild(d)`
- `zeichenbereich_einfuegen(ed)`
- `in_zeichenbereich(ed, form)` — Form in den markierten Zeichenbereich setzen; False, wenn keiner markiert ist (dann kommt die Form in den Text).
- `E_ist_linie(form)`
- `wordart_daten(ed)` — Die Parameter des gewählten WordArt (Kopie) oder None.
- `wordart_aendern(ed, **kw)` — Parameter des gewählten WordArt ändern (None entfernt den Schlüssel) und neu zeichnen; ``form_fuell``/``form_linie``/``form_strich``/
- `anpass_griffe(form, rect, adj)` — Lage aller Anpassungsgriffe der Form im Rechteck ``rect`` (QRectF, beliebiges Koordinatensystem; Ergebnis im selben) — leer, wenn die Form
- `anpass_griff(form, rect, adj, index)` — Lage des Griffs ``index`` (QPointF) oder None, wenn die Form keinen hat.
- `anpassen(form, wert, adj, index)` — Neue Parameterliste für ``daten["adj"]``: Parameter ``index`` = ``wert`` (begrenzt), die übrigen bleiben; leer bei einer Form ohne Griff.
- `anpass_wert(form, rect, punkt, index)` — Der Parameter, den der gezogene Griff ``index`` an ``punkt`` ergibt (für das Ziehen mit der Maus; mit ``anpassen`` speichern).
- `anpass_setzen(ed, wert, index)` — Parameter ``index`` der gewählten freien Form setzen und neu zeichnen.
- `form_wechseln(ed, name)` — Die gewählte freie Form durch ``name`` ersetzen; Größe, Füllung und Kontur bleiben, die Anpassung (``adj``) fällt weg.

### `editor/formen_anpassen.py`

Anpassungsgriffe der Formen (die gelbe Raute): welche Form welche Parameter hat, wie der Pfad daraus entsteht und wo der Griff liegt.

- `_poly_pfad(punkte, r)`
- `_pt(r, x, y)`
- `_anteil(r, p)`
- `_rund(standard)`
- `_stern(zacken, innen)`
- `_pfeil(richtung, schaft, kopf)` — [Schaft (Dicke als Anteil der Quermaße), Kopf (Länge des Kopfes als Anteil der Längsmaße)].
- `_doppelpfeil(waagrecht, schaft, kopf)` — [Schaft, Kopf (je Seite, Anteil der Längsmaße 0 … 0.5)].
- `_fuenfeckpfeil(kopf)`
- `_kreuz(arm)` — [Armdicke] als Anteil von Breite und Höhe.
- `_trapez(neigung)` — [Neigung] = Versatz der kurzen Seite als Anteil der Breite (0 … 0.5).
- `_parallelogramm(neigung)`
- `_dreieck(spitze)` — [Lage der Spitze] als Anteil der Breite (0 … 1).
- `_ring(dicke)` — [Dicke] des Rings als Anteil der kürzeren Seite (0.05 … 0.5).
- `anpassbar(name)`
- `standard(name)`
- `_voll(name, adj)` — Die Parameter mit Standardwerten für fehlende Stellen, auf die Grenzen begrenzt.
- `pfad(name, r, adj)`
- `griffe(name, r, adj)` — Die Lage der Anpassungsgriffe (je Parameter einer) im selben Koordinatensystem wie ``r``.
- `setzen(name, wert, adj, index)` — Neue Parameterliste: Parameter ``index`` = ``wert`` (auf die Grenzen begrenzt), die anderen bleiben.
- `wert_aus_punkt(name, r, punkt, index)` — Der Parameter ``index``, wenn der Griff an ``punkt`` gezogen wird (auf die Grenzen begrenzt).

### `editor/formen_katalog.py`

Die Formen der Galerie Einfügen ▸ Formen, nach Gruppen wie in der Vorlage: Linie, Rechteck, Standardformen, Blockpfeile, Formelformen,

- `_poly(*punkte)` — Vieleck aus Anteilen (0…1) der Breite und Höhe.
- `_vieleck(n, drehung)`
- `_stern(zacken, innen)`
- `_linie(*punkte, pfeil_ende, pfeil_anfang)`
- `_kurve(pfeil_ende, pfeil_anfang)` — S-förmige Kurvenverbindung von links oben nach rechts unten (waagerechte Enden), auf Wunsch mit Pfeilspitzen.
- `_bogen(start, spanne)`
- `_abgerundet(radius)`
- `_ellipse(r)`
- `_ring(r)`
- `_zylinder(r)`
- `_herz(r)`
- `_mond(r)`
- `_smiley(r)`
- `_wolke(r)`
- `_dokument(r)`
- `_welle(r)`
- `_legende(form)`
- `_rechteck(r)`
- `namen()`
- `hat(name)`
- `ist_linie(name)`
- `anpassbar(name)` — Hat die Form Anpassungsgriffe (siehe ``formen_anpassen``)?
- `pfad(name, r, adj)` — Der Pfad der Form in ``r``; ``adj`` = Parameter der Anpassungsgriffe (fehlt er oder hat die Form keine, gilt die Standardform).

### `editor/formen_stile.py`

Formstil-Raster (Zeichentools ▸ Formstile „Abc“): sechs Zeilen (Umriss, Voll, Verlauf hell, Abgestuft, Glanz, 3D) zu sieben Farben

- `formstil(zeile, spalte)` — Die Werte des Stils: {"fuell": Farbe oder "" (keine), "fuell_art": "" \| verlauf \| abgestuft \| glanz, "linie": Farbe, "strich": pt,
- `formstile_raster()` — Das Raster für die Galerie: [Zeile][Spalte] = {"zeile", "spalte", "name" (z. B. „Voll – Blau“), **Werte von ``formstil``}.

### `editor/formular.py`

Formularfelder (Inhaltssteuerelemente): Textfeld, Auswahlliste, Datum, Kontrollkästchen, Schaltfläche.

- `meta(art, name, **kw)`
- `meta_text(m)`
- `meta_lesen(s)`
- `_format(m, leer)`
- `einfuegen(ed, m, wert)` — Feld an der Schreibmarke (oder anstelle der Markierung) einfügen.
- `bereiche(doc)` — [(von, bis, Feld-Daten)] aller Felder; zusammenhängende Stücke mit gleichen Daten sind ein Feld.
- `feld_an(doc, pos)`
- `_ersetzen(ed, v, e, m, text, leer)`
- `wert_von(doc, v, e)`
- `klick(ed, pos, fenster)` — Klick in ein Feld: Kontrollkästchen wechselt, Auswahl zeigt die Liste, Text und Datum fragen nach dem Wert, die Schaltfläche löst
- `_c(ed, pos)`
- `_ist_leer(doc, pos)`
- `_knopf_aktion(ed, m, fenster)`
- `alle_zuruecksetzen(ed)` — Alle Felder auf ihren Anfangswert (Platzhalter, leeres Kästchen) zurücksetzen.
- `daten(doc)` — [(Name, Wert)] aller Felder mit Wert (ohne Platzhalter und Schaltflächen).
- `nur_formulardaten(d)` — „Nur Formulardaten drucken“ in der KOPIE: Text außerhalb der Felder wird unsichtbar, Bilder und Hintergründe entfallen.

### `editor/frei_objekt.py`

Freie Objekte mit Parametern (WordArt, Textfeld): EIN gemeinsamer Baustein.

- `listenmarken(liste, anzahl)` — Die Marke jeder Zeile (mit Leerzeichen dahinter): Aufzählungszeichen oder Nummer nach dem Listenwert aus ``editor/listen.py``
- `richtung_anwenden(img, richtung, zeilenbaender)` — Die Textrichtung am fertigen (waagerecht gesetzten) Bild: senkrecht_rl und dreh90 laufen von oben nach unten (Zeilen von rechts nach links),
- `_gedreht(richtung)`
- `effekte_auf_text(img, ef, text_hoehe, farbe)` — Leuchten und Spiegelung am fertig gezeichneten Text (durchsichtiges Bild in doppelter Auflösung).
- `anzeige_laeufe(d)` — Die Läufe, die das Objekt zeigt: ``[{"t": Text, <Zeichenschlüssel>…}]`` (Schlüssel, die fehlen, gelten für das ganze Objekt).
- `laeufe_text(laeufe)`
- `laeufe_ab(laeufe, von, bis)` — Der Ausschnitt ``[von, bis)`` des Gesamttextes mit seinen Formaten.
- `laeufe_zusammen(laeufe)` — Benachbarte Läufe mit gleichem Format zu einem verbinden (leere fallen weg).
- `_zeilen_laeufe(laeufe)` — Läufe in Zeilen (Absätze) teilen.
- `wordart_zeichnen(d)`
- `_zeichenformat(d, lauf, vorlage, farbe_ueber)` — Das Zeichenformat eines Laufs: seine eigenen Angaben, sonst die des Objekts.
- `_textdoc(d, laeufe, b, h, farbe_ueber)` — Das Textdokument eines Textfelds (Klartext mit Zeichenformaten) für die Läufe; → (Dokument, innere Breite, innere Höhe).
- `_text_passt(d, laeufe, b, h)` — Wie viele Zeichen der Läufe im Feld ``b`` x ``h`` stehen (Anfang der ersten Zeile, die nicht mehr passt) — für verknüpfte Textfelder.
- `textfeld_zeichnen(d, b, h)` — Nur der Text (durchsichtig); Füllung und Rand legt die Angabe des Bildes darum (so wirken Füllung und Kontur der Schnellleiste).
- `_form_zeichnen(d, b, h)` — Eine Form (``editor/formen.py``/``einfuegen.py``) in b × h Bildpunkten, in doppelter Auflösung.
- `_diagramm_zeichnen(d, b, h)` — Ein Diagramm (``editor/diagramm.py``) aus den gespeicherten Daten, in b × h Bildpunkten, in doppelter Auflösung.
- `_smartart_zeichnen(d, _b, _h)`
- `_piktogramm_zeichnen(d, _b, _h)`
- `zeichnen(art, d, b, h)`
- `_anzeige_mass(art, img, b, h)` — Größe auf dem Blatt in Bildpunkten: WordArt aus dem Bild (ohne Überbreite), SmartArt wie das Bild (sofern keine Größe vorgegeben),
- `einfuegen(ed, art, daten, b, h)` — Fügt das Objekt als freies Bild am Absatz der Schreibmarke ein (steht dort Text, in einem neuen Absatz darunter), wählt es aus —
- `bild_einfuegen(ed, img, bb, hh, art, daten, alt)` — Der gemeinsame Weg aller freien Bilder: ``img`` als Ressource, die Angabe am Absatz der Schreibmarke (steht dort Text, in einem neuen
- `ziel(ed)` — (Art, Daten, Schlüssel, Angabe, Bild) des gewählten Objekts (WordArt, Textfeld, Form, Diagramm, SmartArt) oder None.
- `art_gewaehlt(ed)`
- `daten_lesen(ed, art)`
- `aendern(ed, art, **kw)` — Parameter des gewählten Objekts ändern (siehe ``_aendern_innen``). Schreibt der Benutzer gerade im Objekt und hat Text markiert, gelten
- `_aendern_innen(ed, art, **kw)` — Parameter des gewählten Objekts ändern und neu zeichnen. ``breite``/``hoehe`` (px) ändern die Größe; ``form_fuell`` (Farbe oder ``""``)
- `daten_still(ed, art, **kw)` — Daten des gewählten Objekts ändern, ohne das Bild neu zu zeichnen (z. B. die Auswahl eines Diagrammteils); None entfernt den Schlüssel.
- `nach_groesse(ed, neu)` — Nach dem Ziehen der Griffe: Textfeld, Form und Diagramm werden in der neuen Größe frisch gezeichnet (Zeilenumbruch folgt der Breite,
- `text_bereich(a, bild)` — Wo der Text im Objekt liegt, als Anteil (0..1) von Breite/Höhe — für die graue Textmarkierung wie in WPS (nur WordArt).
- `_format_aus_kw(kw)` — Zeichenformat für das Eingabefeld aus Schlüsseln der Texttools (nur die genannten).
- `_lauf_aus_format(cf, basis)` — Die Zeichenschlüssel, die ein Format ausdrücklich setzt und die vom Objekt abweichen.
- `_basis(d, art)`
- `_widget_laeufe(w, d, art)` — Die Läufe aus dem Eingabefeld; ``None``, wenn der ganze Text ohne eigene Formate ist.
- `_edit_laden(ed)` — Das Eingabefeld mit den Läufen des Objekts füllen (Auswahl bleibt erhalten).
- `_edit_stil(ed)` — Schrift, Farbe und Ausrichtung des Eingabefeldes folgen den Parametern des Objekts (auch nach einem Knopf der Texttools).
- `edit_platzieren(ed)` — Das Eingabefeld deckt das Objekt (folgt dem Blatt beim Scrollen und Zoomen).
- `bearbeiten_starten(ed)` — Schreibt direkt im gewählten Objekt (WordArt oder Textfeld): ein Eingabefeld über dem Text. Eingabe, Markieren, Rückschritt und Enter
- `auswahl_daten(ed)` — Die Zeichenformate der Markierung (oder der Schreibmarke) im Eingabefeld — wirksame Werte, auch die des Objekts. Für den Zustand der
- `edit_uebernehmen(ed)` — Der eingegebene Text mit seinen Formaten kommt ins Objekt (ohne das Feld zu schließen).
- `bearbeiten_beenden(ed)`
- `text_werte_lesen(ed)` — Die Textoptionen (Format von ``texteffekt.py``) des gewählten Objekts.
- `text_werte_anwenden(ed, werte)` — Die Textoptionen der Seitenleiste wirken auf den Text im gewählten Objekt: Füllung (Farbe, Transparenz), Kontur (Farbe, Breite).
- `_textfelder(ed)` — Alle Textfelder des Textes: (Schlüssel, Angabe) — frisch aus den Absätzen gelesen.
- `_speichern_angabe(ed, key, a)`
- `_neu_setzen(ed, key, a)` — Das Bild des Textfelds aus seinen Daten neu zeichnen und die Angabe sichern.
- `verknuepfen(ed, von_key, nach_key)` — Textfeld ``von`` mit Textfeld ``nach`` verknüpfen: was in ``von`` nicht mehr passt, läuft in ``nach`` weiter (wie „Verknüpfung erstellen“ in
- `loesen(ed, key)` — Die Verknüpfung des Textfelds zu seinem Nachfolger lösen (steht ``key`` am Ende einer Kette, die zu seinem Vorgänger): der Nachfolger
- `ist_verknuepft(ed, key)`
- `kette_aktualisieren(ed)` — Jede Kette neu verteilen: der Text des ersten Feldes (mit seinen Zeichenformaten) füllt ein Feld nach dem anderen; geändert werden nur

### `editor/freie_bilder.py`

Frei positionierte Bilder: Bilder, die nicht im Text stehen, sondern an einer Stelle des Blattes (DOCX ``wp:anchor`` ohne Umbruch).

- `emu_zu_px(emu)`
- `aus_absatz(bf)`
- `an_absatz(cursor, angabe)` — Hängt die Angabe an den Absatz des Cursors (mehrere Bilder an einem Absatz sind möglich).
- `hat_bilder(doc)` — Gibt es im Text überhaupt einen Absatz mit frei positionierten Bildern? (billig genug für jeden Zeichenvorgang des Editors)
- `bild_im_dokument(doc, name)`
- `neuer_name(doc)`
- `bild_aus_daten(blob)` — Ein Bild aus Dateidaten. Qt kennt kein EMF; viele Word-Bilder (eingescannte Unterschriften) sind aber EMF-Hüllen um ein Bitmap
- `farbe_aus_element(el, ns)` — Eine DrawingML-Farbe (srgbClr, prstClr, schemeClr) mit lumMod, lumOff, satMod, tint und shade. ``ns``: Namensräume für XPath.
- `duoton(img, dunkel, hell)` — Das Bild in zwei Farben: Schwarz wird ``dunkel``, Weiß wird ``hell``, dazwischen Verlauf (DrawingML ``a:duotone``). Durchsicht bleibt.
- `rechteck(a, blatt_b, blatt_h, ml, mt, inhalt_b, inhalt_h, absatz_y, spalte_x, seite)` — Das Rechteck des Bildes auf dem Blatt. ``absatz_y``: oberer Rand des Absatzes (Blattkoordinate), ``spalte_x``: linker Rand der Spalte.
- `fuell_pinsel(fuell, r, fuellbild)` — Der Pinsel für die Füllung eines Bildes (hinter durchsichtigen Stellen): ``farbe``, ``verlauf``, ``graduell`` (zwei Farben), ``muster``,
- `_stift(rand)` — Die Kontur eines Bildes als Stift (Stärke in Bildpunkten, Art wie bei den Linien).
- `bild_zeichnen(p, bild, r, ellipse, rand, dreh, fuell, fuellbild, fx)` — Bild in ``r``; ``ellipse``: in einer Ellipse beschnitten; ``rand``: {"b": px, "farbe": "#rrggbb", "art": Linienart} eine Linie um die Form;
- `koerper_index(d, ch, ncol)` — {Blatt (1-basiert): [(Angabe, y des Absatzes in der Spalte, Spalte)]} für die Bilder im Text. ``d`` ist der Textfluss
- `objekte_der_seite(page, d, n, index)` — Alle frei positionierten Bilder des Blattes ``n`` (1-basiert) mit ihrem Rechteck, in Blattkoordinaten (px).
- `versatz_fuer(a, r, page, n)` — Die Angaben ``xh``/``yv`` (ohne Ausrichtung), mit denen das Bild im Rechteck ``r`` steht — zum Verschieben und Verändern der Größe.
- `ohne_hilfsangaben(a)`
- `vorne_hinten(objekte, hinter)`

### `editor/freiform.py`

Freiform: die Punkte einer Form (Zeichentools ▸ Form bearbeiten ▸ Punkte bearbeiten). Keine Oberfläche.

- `innen(daten, b, h)` — Das Zeichenrechteck der Form im Bild von b × h Bildpunkten (wie in ``einfuegen.form_bild``).
- `aus_pfad(pfad, r)` — Die Elemente des Pfads, auf das Rechteck ``r`` bezogen (Anteil 0..1). Ein Teilpfad, der zum Anfang zurückkehrt, wird mit ``Z`` geschlossen.
- `aus_form(daten, b, h)` — Die Punktliste der gewählten Form in ihrer Größe (Pfeilspitzen der Linien werden zu eigenen Teilpfaden).
- `pfad(punkte, r)` — Der Pfad der Punktliste im Rechteck ``r``.
- `geschlossen(punkte)` — Gibt es einen geschlossenen Teilpfad (dann wird gefüllt, sonst nur die Linie gezeichnet)?
- `rollen(punkte)` — Je Element: ``"knoten"`` (Punkt), ``"steuer"`` (Kurven-Steuerpunkt) oder ``"zu"`` (Schließen).
- `knoten(punkte)`
- `_teil(punkte, i)` — Anfang und Ende (einschließlich) des Teilpfads, zu dem Element ``i`` gehört.
- `verschieben(punkte, i, x, y)` — Element ``i`` an (x, y) setzen; ein Punkt nimmt seine Steuerpunkte mit.
- `loeschen(punkte, i)` — Punkt ``i`` entfernen (die Nachbarn verbinden sich); None, wenn es kein Punkt ist oder der Teilpfad zu klein würde
- `_kubisch(p0, p1, p2, p3, t)`
- `_kanten(punkte)` — Alle Kanten als (Index des Elements, Art, Stützpunkte): Art ``"L"`` (p0, p1), ``"C"`` (p0, c1, c2, p1) oder ``"Z"`` (letzter Punkt → Anfang).
- `naechste_kante(punkte, x, y, b, h)` — Die Kante, die (x, y) (Anteile) am nächsten liegt: (Abstand in Bildpunkten b × h, Index, Art, Stützpunkte, t) oder None.
- `einfuegen(punkte, x, y, b, h, toleranz)` — Einen Punkt auf der nächsten Kante einfügen (bei einer Kurve wird sie dort geteilt, ihre Form bleibt). → (neue Liste, Index des

### `editor/gehe_zu.py`

„Gehe zu“: Sprungziele im Dokument — Seite, Zeile (Absatz), Überschrift, Textmarke, Kommentar, Fußnote, Endnote, Tabelle, Bild,

- `_kurz(t, n)`
- `_fragmente(doc)`
- `_tabellen(rahmen)`
- `maximum(ed, art)` — Obergrenze für Seite und Zeile.
- `seitenstart(ed, n)`
- `zeilenstart(ed, n)`
- `ziele(ed, art)` — [(Beschriftung, Position)] für die Listen-Arten.
- `springen(ed, pos)`
- `_objekte(doc, nur_art)`
- `positionen(ed, element)` — Die Anfänge aller Elemente einer Art, der Reihe nach.
- `ziel(ed, element, eingabe, richtung)` — Wohin „Weiter“ (``richtung`` 1) oder „Zurück“ (-1) springt. ``eingabe``: leer = nächstes/voriges Element, „4“ = das vierte,

### `editor/indexeintrag.py`

Indexeinträge wie das Word-Feld XE: Haupt- und Untereintrag, Lesung, „Siehe …“, Seitenbereich über eine Textmarke, fette oder

- **class `Eintrag`**
  - `text()`
  - `schalter()`
  - `sortierung()`
- `aus_text(text, schalter)` — Eintrag aus ``P_INDEX`` und ``P_INDEX_OPT``.
- `feld(e)`
- `aus_feld(anweisung)` — Eintrag aus einer Feldanweisung ``XE "…" …``; None, wenn es kein XE-Feld ist.

### `editor/leere_seite.py`

Einfügen ▸ Leere Seite: ein neues, leeres Blatt HINTER der Seite der Schreibmarke. Der vorhandene Text wird nicht geteilt.

- `_umbruch_davor(block)`
- `leere_seite(doc, letzter, einrichtung, quer)`

### `editor/lese_zeilenluft.py`

Zeilenluft der Lesehilfe: mehr Platz zwischen den Zeilen — nur in der Anzeige beim Bearbeiten, nie im Dokument.

- `_markiert(bf)`
- `aktiv(doc)` — Trägt ein Absatz des Dokuments noch den Zusatzabstand der Lesehilfe?
- `_zuruecksetzen(bf)`
- `_durchlaufen(doc, aendern)`
- `zuruecknehmen(doc)` — Jedem Absatz den ursprünglichen Zeilenabstand zurückgeben (ohne Rückgängig-Schritt, wenn das Dokument sonst nichts mehr davon weiß).
- `bereinigte_kopie(doc)` — Eine Kopie ohne den Zusatzabstand zum Speichern oder Ausgeben; das bearbeitete Dokument bleibt unberührt.
- `anwenden(doc, faktor)` — Zeilenluft ``faktor`` (1,0 = normal) für alle Absätze setzen; vorherige Werte werden zuerst zurückgenommen. Ändert nichts, wenn nichts zu tun ist.

### `editor/linie.py`

Eine Linie als Wert: Farbe, Stärke, Art und (für Absatzrahmen) die Seiten, auf denen sie steht.

- `_bauen()` — Die Linienarten der Auswahl „Formatvorlage“: Schlüssel → (Name, Strichart, DOCX-Wert, Bahnen, wellig).
- `docx_wert(art)` — Wert von ``w:val`` für eine Linienart (unbekannt: einfach).
- `art_aus_docx(wert)`
- **class `Linie`**
  - `text()`
  - `polster()` — (oben, unten, links, rechts) in pt, wenn ein eigener Abstand gesetzt ist.
  - `aus_text(text)`
  - `mit_seiten(seiten)`
  - `stift(massstab)` — QPen der Linie (bei Mehrfachlinien die Gesamtbreite); ``massstab`` rechnet pt in Bildpunkte um (96/72 am Bildschirm, mal Zoom).
  - `_bahn_stift(w, dicke, strich)`
  - `zeichne(p, x1, y1, x2, y2, massstab)` — Eine einzelne Linie in ihrer Art: einfach, gestrichelt, mehrfach (Bahnen nebeneinander) oder wellig.
  - `rahmen_zeichnen(p, r, massstab, innen_y)` — Zeichnet die gemeinten Seiten eines Rechtecks in der Linienart. ``innen_y``: Höhen der Linien zwischen Absätzen

### `editor/listen.py`

Aufzählungen und Nummerierungen: die Arten, die Lunivo zeichnet und in DOCX schreibt, und ihre Beschreibung als kleines Wörterbuch.

- `zeichen_filtern(w)` — Aus den Werten eines Schriftart-Fensters nur das, was für Nummern gilt und gesetzt ist.
- `liste(stil, praefix, suffix, start, zeichen, pos)` — ``pos``: eigene Position der Nummer (``ausr``, ``ausr_art``, ``tab``, ``einzug`` in mm) — dann zeichnet Lunivo die Nummer selbst.
- `marke(spec)` — Zeichenfolge für ``liste_zeichner`` (Vorschaubild) dieser Liste.
- `zu_format(spec, einzug)`
- `aus_format(f)`
- `als_text(spec)`
- `aus_text(text)`

### `editor/literatur.py`

Quellen und Zitierweisen (APA, Harvard, IEEE, Chicago, DIN ISO 690).

- `_nachname(autor)`
- `_autoren(autor)`
- `zitat(q, weise, nr)`
- `eintrag(q, weise, nr)`
- `literaturverzeichnis(quellen, weise)`

### `editor/mehrstufig.py`

Mehrstufige Nummerierung („Gliederung nummeriert“: 1. / 1.1. / 1.1.1.), von Lunivo selbst gezeichnet.

- `nummer_text(stil, n)` — Die Zahl ``n`` in der Zahlenart ``stil`` (dezimal, klein, gross, roem_klein, roem_gross).
- `ebene(stil, format, start, ausr, einzug, zeichen, **mehr)`
- `ebene_aus(x)` — Eine Ebene aus einem Wörterbuch (JSON, Dialog) mit allen bekannten Feldern neu aufbauen.
- `aufzaehlung(zeichen)` — Aufzählung mit einem Zeichen (◆ ✤ ➤ ✓ ✧ …), das Lunivo selbst zeichnet; Ebenen wie bei einer Gliederung eingerückt.
- `ist_aufzaehlung(defn)` — Gliederung ohne einen einzigen Platzhalter für Nummern: eine Aufzählung mit eigenem Zeichen.
- `als_mehrstufig(spec)` — Eine einfache Liste (``editor.listen``) mit eigener Position als Gliederung: Ebene 1 ist die Liste, tiefere Ebenen zählen für sich.
- `gliederung(stile, formate)` — 9 Ebenen aus je einer Zahlenart und einem Zahlenformat; Ausrichtung und Einzug wachsen mit der Ebene.
- `_alle(zahlenart, formate)` — Ebene n zeigt die Nummern aller Ebenen davor (``①.②.``); ``formate`` bestimmt, ob Ebene 1, 2 und tiefer mit Punkt enden (``"."``) oder nicht (``""``).
- `als_text(defn)`
- `aus_text(text)`
- `block_wert(ebene_nr, defn)`
- `aus_block(text)`
- `nummer_der_ebene(defn, zaehler, ebene_nr)` — Die Nummer als Text für einen Absatz der Ebene ``ebene_nr`` (1…9) bei diesen Zählerständen.
- `zaehlen(zaehler, defn, ebene_nr)` — Zählerstand nach einem Absatz der Ebene ``ebene_nr``: diese Ebene weiter, tiefere neu.
- `nummern(d)` — [(Block, Nummerntext, Ebene, Beschreibung der Ebene)] aller Absätze mit ``B_MEHRSTUFIG`` in Dokumentreihenfolge.
- `_marker_font(b, e)` — Schrift und Farbe der Nummer: die des Absatzes, mit den Änderungen der Ebene („Schriftart …“).
- `_text_breite(text, f, geraet)`
- `einrichten_alle(d)` — Einzug aller Absätze mehrstufiger Listen setzen: Text ab „Einzug bei“, erste Zeile ab „Tabstopp-Leerstelle“ — oder direkt nach der
- `nummern_zeichnen(p, d, faktor)` — Die Nummern der mehrstufigen Listen vor die Absätze zeichnen. Koordinaten: Dokument (wie ``absatzrahmen_zeichnen``).

### `editor/muster.py`

Schattierungsmuster (Rahmen und Schattierung ▸ Muster): Prozentraster und Linienmuster, wie Word und WPS sie kennen.

- `_pct_name(p)`
- `name_von(schluessel)`
- `ooxml_von(schluessel)`
- `schluessel_von_ooxml(wert)`
- `_an(schluessel, x, y)` — Ist das Bildelement (x, y) der 8 × 8-Kachel in der Musterfarbe?
- `kachel(schluessel, muster, fuell)` — Eine 8 × 8-Kachel des Musters; ohne Füllfarbe bleibt der Grund durchsichtig.
- `pinsel(schluessel, muster, fuell)` — Der Pinsel für den Hintergrund eines Absatzes (Muster über Füllfarbe).
- `als_text(schluessel, muster, fuell)`
- `aus_text(text)`

### `editor/pagination.py`

Seitenaufteilung, PDF-Ausgabe und Drucken mit Kopf-/Fußzeile und Seitenzahlen.

- `layout_device()` — Ein Gerät mit festen 96 dpi, an dem alle Dokumente gesetzt werden.
- `zoom_device(faktor)` — Ein Gerät mit 96 dpi × Zoom: Text, Ränder, Tabellen und Bilder werden beim Setzen mitskaliert.
- `bind_layout(qdoc, faktor)`
- `noten_anhaengen(d, noten, arten)` — Fuß- und Endnoten gesammelt am Textende (nur in der Kopie für Seitenzählung, PDF und Druck). Fußnoten stehen bei einer
- `_trenner(sprache)` — pyphen-Wörterbuch (zwischengespeichert); None, wenn pyphen oder die Sprache fehlt.
- `silben_einfuegen(d, sprache)` — Fügt in einer KOPIE des Dokuments weiche Trennstriche (U+00AD) in lange Wörter ein; Qt bricht dort um und zeigt „-“.
- `ausgabe_seiten(logisch, page)` — Seiten der Ausgabe: bei mehreren Spalten füllen je so viele „logische“ Spaltenseiten eine Blattseite.
- `paginated_copy(qdoc, page, noten, silben, einspaltig, versteckt, fussnoten, lese_luft)`
- `_abschnittsbeginn_markieren(d)` — Nur in der Kopie: Der Absatz nach einem Abschnittsumbruch („nächste/gerade/ungerade Seite“) beginnt eine neue Seite.
- `_fussnoten_am_fuss(page, noten)` — Fußnoten am Seitenfuß gibt es bei einer Spalte; bei mehreren Spalten stehen sie gesammelt am Textende.
- `_fussnoten_stellen(d)` — [(Zeichenstelle, Fußnoten-Id, Länge)] in Textreihenfolge.
- `_zeilenbereiche(d)` — [(oben, unten, Zeichenstelle des Zeilenanfangs, Blocknummer)] aller Zeilen in Dokumentreihenfolge.
- `fussnoten_am_seitenende(d, page, noten)` — Fußnoten unten auf der Seite, auf der ihre Marke steht (nur in der Kopie für Seitenzählung, Seitenansicht, PDF und Druck).
- `page_count(qdoc, page)`
- `_expand(text, n, total, page, kapitel)`
- `_draw_hf(p, hf, rect, n, total, base, page, kapitel)` — Kopf- oder Fußzeile einer Seite; ``n`` ist die angezeigte Seitennummer (bestimmt auch „außen“/„innen“).
- `_ohne_hintergruende(d)`
- `_text_schwarz(d)` — „Text schwarz drucken“ in der Kopie: jede Schriftfarbe wird schwarz (Verknüpfungen und Platzhalter eingeschlossen).
- `_formularteile_ausblenden(d, steuer, platzhalter)` — Steuerelemente (Felder mit Wert, Schaltflächen, Kästchen) und/oder Platzhaltertexte leerer Felder werden in der Kopie unsichtbar.
- `_ohne_hervorhebungen(d)` — Nur die Texthervorhebung (Marker) entfällt; Absatz- und Tabellenhintergründe bleiben.
- `_ohne_links(d)` — PDF ohne Hyperlinks: der Text bleibt, nur das Linkziel entfällt (Qt schreibt sonst für jedes Linkziel einen PDF-Link).
- `_textmarken_klammern(d)` — „Textmarken drucken“: jede Textmarke steht in eckigen Klammern im Ausdruck.
- `_bf_ohne(bf)`
- `seitenschmuck(p, page, hintergrund, flaeche, rahmen, wasserzeichen)` — Seitenfarbe, Seitenrahmen und Wasserzeichen. Koordinaten: Seite in 96-dpi-Bildpunkten, Ursprung links oben.
- `seiten_liste(total, first, last, opt)` — Welche Seiten in welcher Reihenfolge gedruckt werden (Duplex, umgekehrte Reihenfolge).
- `render(qdoc, page, device, first, last, dpi, opt)` — Zeichnet die Seiten first..last auf device (QPdfWriter/QPrinter). → Anzahl Seiten.
- `render_dokument(qdoc, page, device, first, last, dpi, opt, layout)` — Wie render(), aber mit mehreren Abschnitten: jeder Abschnitt wird mit seiner eigenen Seitengröße, seinen Rändern, Spalten und
- `notenlinks_sammeln(d, page, liste)` — Sprungverweise für die PDF: Marke → Note und Note → Marke (Fußnoten am Seitenfuß, Endnoten und gesammelte Noten am Textende).
- `kommentarstellen(d, ch, liste, kommentare, spalten)` — [(Seitenindex, y in px auf der Textfläche, Text)] für die PDF-Notizen. `kommentare` = {Kommentar-Id: Text}; die Stelle
- `lesezeichen_sammeln(d, ch, liste, was, spalten)` — [(Ebene, Titel, Seitenindex 0-basiert)] für die PDF-Gliederung: Überschriften und/oder Textmarken.
- `gliederung_schreiben(pfad, eintraege, kommentare, page, links)` — Schreibt Lesezeichen und Kommentare in die fertige PDF (QPdfWriter kann das nicht selbst) — mit pypdf.
- `_druckmarken(p, page, grenzen, zuschnitt)` — Textbegrenzungen (gestrichelter Rahmen um die Textfläche) und Zuschnittsmarken (Ecken) auf der gedruckten Seite.
- `_inhalt_zeichnen(p, d, rect)` — Wie ``QTextDocument.drawContents``, aber mit schwarzer Grundschrift: Text ohne eigene Farbe nähme sonst die Textfarbe des
- `zeichne_seite(p, d, page, n, total, base, hintergrund, balken, nr_offset, gesamt, kapitel)` — Eine Seite (Nummer n, 1-basiert) mit Seitenschmuck, Kopf-/Fußzeile und Text; Maßstab 96 dpi, Ursprung links oben.
- `absatz_zusatz_zeichnen(p, d, faktor)` — Was an den Absätzen nicht von Qt kommt: Rahmen und die Nummern mehrstufiger Listen.
- `absatzrahmen_zeichnen(p, d, faktor, polster)` — Rahmen um zusammenhängende Absätze mit gleichem B_RAHMEN. Koordinaten: Dokument (Layoutgerät); faktor = Zoom.
- `_zeilennummern(p, d, n, ch, base, art)` — Zeilennummern am linken Rand der Seite n (Koordinaten: Textfläche, auf die Seite verschoben).
- `seite_als_bild(qdoc, page, n, faktor, d, noten, nr_offset, gesamt)` — Seite n als Bild (für die Zwei-Seiten-Ansicht und „Als Bild exportieren“). Ohne ``nr_offset`` gilt „Beginnen mit“ der Einrichtung.
- `seitenzahl(qdoc, page, noten)` — Seiten der Ausgabe über alle Abschnitte (einschließlich Leerseiten vor „gerade/ungerade Seite“).
- `seiten_bilder(qdoc, page, noten, faktor)` — Alle Seiten der Ausgabe als (Nummer, Bild, Seiteneinrichtung) — mit mehreren Abschnitten je Abschnitt in der eigenen Größe.
- `_leere_seiten(d, page, total)`
- `blasen_geometrie(page, opt)` — Platz für Sprechblasen beim Drucken: Die Seite wird verkleinert, daneben stehen die Blasen. → None ohne Blasen.
- `_blasen_pro_seite(d, page, liste, bd)` — {Blattseite (1-basiert): [(Blase, y in px auf der Textfläche)]} — die Blasen stammen aus der Kopie selbst.
- `_blasen_zeichnen(p, eintraege, geo)`
- `_page_layout(page, quer)`
- `export_pdf(path, qdoc, page, title, author, noten, lesezeichen, silben, kommentare, extra, erste, letzte)` — Schreibt die Seiten ``erste`` bis ``letzte`` (``None``: bis zum Ende) als PDF. → Seitenzahl des Dokuments.
- `print_document(printer, qdoc, page, opt)`

### `editor/querblatt.py`

Blätter verschiedener Größe im Editor (z. B. ein Querformat-Blatt zwischen Hochformat-Blättern) — nur in der Anzeige beim Bearbeiten.

- `rechts_px(bf)` — Der rechte Einzug, wie ihn der Benutzer eingestellt hat (ohne den Zusatz der Anzeige).
- `rechts_setzen(bf, px)` — Rechten Einzug setzen; die Anzeige rechnet ihren Zusatz danach neu hinzu.
- `_geometrie(p)`
- `einrichtungen(doc, page)`
- `aktiv(doc, page)`
- `masse(doc, page)` — (größte Textbreite, größte Texthöhe) aller Abschnitte in Bildpunkten (ohne Zoom).
- `_abschnitt_je_block(doc, eins)` — (Block, Einrichtung) für jeden Absatz in Textreihenfolge.
- `_setzen(doc, aendern)`
- `breite_anwenden(doc, page, zoom, an)` — Den Absätzen und Tabellen schmalerer Abschnitte den Zusatz geben (``an=False``: überall wegnehmen). → True bei Änderung.
- `zuruecknehmen(doc)` — Den Zusatz überall wegnehmen (für Kopien zum Speichern, Drucken, PDF).
- `bereinigte_kopie(doc)`
- `hat_zusatz(doc)`
- `blattplan(doc, page, ch)` — Einrichtung jeder Seite des Textflusses (Seiten der Höhe ``ch`` im Layout): die des Abschnitts, dessen Text oben auf der Seite steht.
- `grenzen(doc, page, ch, zoom)` — Absätze, vor die ein eigener Seitenumbruch gehört: der erste Absatz eines Abschnitts mit anderer Blattgröße, wenn er nicht oben auf

### `editor/schreibweise.py`

Groß-/Kleinschreibung und Sortierreihenfolge als reine Textfunktionen (ohne Oberfläche, einzeln testbar).

- `umwandeln(text, art)`
- `_zahl(t)` — Die erste Zahl im Text (Komma oder Punkt als Dezimalzeichen); ohne Zahl ganz vorn.
- `_datum(t)`
- `sortiert(texte, *, absteigend, typ, gross_klein)` — Die Texte in der gewünschten Reihenfolge. ``typ``: ``text``, ``zahl`` (erste Zahl im Text) oder ``datum`` (TT.MM.JJJJ).
- `felder(text, trenner)` — Die Felder eines Absatzes (getrennt durch Tab, Komma oder ein anderes Zeichen).
- `feldzahl(texte, trenner)`
- `reihenfolge(texte, schluessel, *, trenner, gross_klein, sprache, kopfzeile)` — Neue Reihenfolge der Absätze (Indizes). ``schluessel``: bis zu drei (Feld oder None für den ganzen Absatz, Typ, absteigend) — der erste
- `absaetze(doc, von, bis)` — Die Absätze zwischen ``von`` und ``bis`` (ohne Angabe: das ganze Dokument). → [] wenn eine Tabelle dazwischenliegt.
- `umstellen(doc, bloecke, ordnung)` — Stellt die (aufeinanderfolgenden) Absätze ``bloecke`` in die Reihenfolge ``ordnung`` — mit Absatz- und Zeichenformat, als ein Rückgängig-Schritt.

### `editor/seitenfluss.py`

Umbruchregeln am Seitenende: „Diesen Absatz zusammenhalten“, „Nicht vom nächsten Absatz trennen“ und die Absatzkontrolle

- `ist_manuell(bf)` — Ein Seitenumbruch oberhalb, den der Benutzer gesetzt hat (kein von Lunivo eingefügter).
- `_zeilen(b, ch)` — (Seite, oben, unten) jeder Zeile des Absatzes.
- `_verletzt(b, naechster, ch, w)`
- `_seitenanfang(doc, ch)` — Am Anfang einer Seite, die durch den Textfluss entsteht, entfällt der Abstand vor dem Absatz (wie in Word und LibreOffice). Nach einem
- `anwenden(doc, ch, weitere)` — Umbruchregeln auf das Dokument anwenden (``ch`` = Höhe der Textfläche einer Seite in Bildpunkten). → True, wenn sich etwas geändert hat.

### `editor/seitenrahmen.py`

Der Rahmen um die Seite („Rahmen und Schattierung“ ▸ Seitenrand): Lage, Abstände, Kunstrahmen.

- `abstaende_pt(b)` — (oben, unten, links, rechts) in pt.
- `rechteck(b, page, seite)` — Das Rechteck des Rahmens in Bildpunkten, auf einer Seite mit dem Rechteck ``seite``.
- `_figur(art, mitte, groesse)`
- `kunst_zeichnen(p, rect, art, breite_px, farbe)` — Einen Kunstrahmen entlang der Kanten: Figuren in regelmäßigem Abstand (Zickzack als Linienzug).
- `zeichnen(p, b, page, seite)` — Den Seitenrahmen auf eine Seite zeichnen (Linie in ihrer Art oder Kunstrahmen).

### `editor/seitenzahl.py`

Seitenzahlen in Kopf- oder Fußzeile setzen und entfernen (Einfügen ▸ Seitenzahl). Arbeitet auf ``PageSettings``; keine Oberfläche.

- `_ohne_zahl(text)`
- `seitenzahl_setzen(page, ort, ausrichtung, muster, format, start, kapitel)` — Seitenzahl in Kopf- (``ort="kopf"``) oder Fußzeile setzen. Eine vorhandene Seitenzahl dort wird ersetzt, übriger Text bleibt;
- `seitenzahlen_entfernen(page)` — Seitenzahl (mit „Seite … von …“) aus Kopf- und Fußzeile entfernen. → ob es eine gab.
- `seitenzahl_loeschen_bereich(page, art, blatt)` — Seitenzahl nur auf einem Teil der Seiten eines Abschnitts entfernen (Seitenzahl löschen ▾ in der Kopf-/Fußzeilenleiste).
- `nummer(n, page, kapitel)` — Die Seitennummer ``n`` in der Zahlenart der Einrichtung, mit Kapitelnummer davor („2-1“).
- `text(vorlage, n, gesamt, page, kapitel)`
- `ausrichtung(align, n)` — „außen“: ungerade (rechte) Seiten rechts, gerade links; „innen“ umgekehrt. Andere Werte bleiben.
- `erste_nummer(page)` — Nummer der ersten Seite eines Abschnitts, wenn er nicht fortsetzt (sonst 1).
- `seitenwechsel(d, seitenhoehe)` — Zeichenstellen, an denen eine neue Seite beginnt (erste Zeile der Seiten 2, 3, …), nach der Höhe einer Seite im Layout.
- `_kapitel_nummer(b, mehr)`
- `kapitel_je_seite(d, ebene, wechsel)` — Kapitelnummer jeder Seite (Index 0 = Seite 1): die Nummer der letzten Überschrift der Ebene ``ebene``, die auf der Seite oder

### `editor/sendungen.py`

Sendungen: Umschlag, Etiketten, Seriendruck (mit Feldern, Adressblock, Regeln), Formularfelder.

- `umschlag_aufbauen(ed, format_name, absender, empfaenger)`
- `etiketten_aufbauen(ed, bogen, text, gleich)`
- `tabelle_lesen(roh)`
- `felder_im_text(doc)`
- `feld_einfuegen(ed, name)`
- `adressblock_einfuegen(ed, was)`
- `regel_einfuegen(ed, feld, wert, dann, sonst)`
- `_satz_einsetzen(doc, satz, von_bis)` — Felder und Regeln mit den Werten von ``satz`` füllen (``von_bis``: nur in diesem Bereich).
- `brief_fuer(vorlage, satz)` — Ein Brief. Steht „Nächster Datensatz“ im Text, gilt hinter jeder solchen Stelle der nächste Satz der Liste ``satz``.
- `saetze_je_brief(vorlage)` — Wie viele Datensätze ein Brief verbraucht (1 + Zahl der Felder „Nächster Datensatz“).
- `gruppen(vorlage, saetze)`
- `serienbrief_erzeugen(quelle, saetze, ziel)` — Alle Briefe in EIN Dokument, durch Seitenumbrüche getrennt. → Zahl der Briefe.
- `quelle_lesen(pfad)` — Empfängerliste aus einer Textdatei (CSV mit ; oder , oder Tabulator; erste Zeile = Spaltennamen). → (Spalten, Sätze) oder None.
- `zugeordnet(satz, zuordnung)` — Satz mit den Namen der Felder im Text: ``zuordnung`` {Feld im Text: Spalte der Quelle}; ohne Eintrag gilt der gleiche Name.
- `felder_hervorheben(doc, an)` — Hintergrund der Felder {{…}} an oder aus. Gehört zum letzten Bearbeitungsschritt und lässt „geändert“ wie es war.
- `naechster_einfuegen(ed)` — Feld „Nächster Datensatz“: dahinter füllt der nächste Satz die Felder (z. B. mehrere Etiketten auf einem Blatt).
- `_ressourcen(quelle, ziel)`
- `form_textfeld(ed, text)`
- `form_kasten(ed, beschriftung)`
- `form_knopf(ed, aufschrift)`
- `kasten_umschalten(ed, pos)` — Klick auf ein Kontrollkästchen ☐/☒ wechselt den Zustand.

### `editor/silbenfarben.py`

Silben farbig: Lesehilfe für Menschen mit Legasthenie.

- `konfig_lesen(settings)` — Die Einstellungen (settings: Settings des Programms) als Wörterbuch mit allen Schlüsseln.
- `konfig_speichern(settings, k)`
- `farben(k)`
- `verfuegbar(sprache)` — Die Regeln brauchen nichts außer Python; pyphen verbessert nur die Wortgrenzen in Zusammensetzungen.
- `silben(wort, sprache)` — Das Wort in deutsche Sprechsilben (ein Eintrag, wenn es sich nicht teilen lässt).
- `_formate(k)`
- **class `SilbenFarben`**(QSyntaxHighlighter) — Färbt die Silben im Anzeige-Layout des Dokuments ein; verändert weder Text noch Formatierung.
  - `__init__(doc, konfig, aktueller_block)`
  - `highlightBlock(text)`
  - `neu_konfigurieren(konfig)`

### `editor/smartart.py`

SmartArt: Listen, Prozesse, Hierarchien (Organigramm), Zyklen und Pyramiden aus einem Baum von Knoten.

- `punkte(text)` — [(Ebene, Text)] — die Ebene ergibt sich aus der Einrückung (je zwei Leerzeichen oder ein Tabulator).
- `knoten_aus_text(text)` — Der Knotenbaum (flach, in Reihenfolge) aus dem eingerückten Text; Zeilen mit „• “ werden Aufzählungspunkte des Knotens davor.
- `_glatt(kn)` — Ebenen so begrenzen, dass kein Knoten mehr als eine Ebene unter seinem Vorgänger steht (der erste steht auf Ebene 0).
- `knoten_von(daten)` — Die Knoten des SmartArt als Kopie: aus ``daten["knoten"]``, sonst aus ``daten["text"]``.
- `text_aus_knoten(kn)` — Der eingerückte Text zu den Knoten (Aufzählungspunkte als „• “-Zeilen eine Ebene tiefer).
- `_knotentext(k)`
- `_neue_id(kn)`
- `_index(kn, ident)`
- `_ende(kn, i)` — Index hinter dem letzten Nachkommen von Knoten ``i`` (Ende seines Teilbaums).
- `_geschwister(kn, i, richtung)` — Beginn des vorigen (-1) bzw. nächsten (+1) Geschwisters von ``i`` (gleiche Ebene, gleicher Elternknoten) oder None.
- `form_einfuegen(kn, ident, wie, text)` — Neuen Knoten einfügen relativ zu ``ident`` (ohne gültige Auswahl: hinter den letzten obersten Knoten): ``nach`` (Geschwister dahinter), ``vor``
- `kann_level(kn, ident, richtung)` — Ob ``level(..., "erhoehen")`` bzw. ``"reduzieren"`` für den Knoten geht (der erste Knoten und Knoten, die schon Kind ihres Vorgängers sind,
- `level(kn, ident, richtung)` — Knoten samt Teilbaum eine Ebene tiefer (``erhoehen``) oder höher (``reduzieren``); None, wenn es nicht geht.
- `kann_verschieben(kn, ident, richtung)`
- `verschieben(kn, ident, richtung)` — Knoten samt Teilbaum vor das vorige (``vor``) bzw. hinter das nächste (``zurueck``) Geschwister; None, wenn keins da ist.
- `aufzaehlung(kn, ident, text)` — Einen Aufzählungspunkt an den Knoten hängen.
- `_format_von(nr)` — Das Format des Knotens Nummer ``nr`` (Format wie ``teil_format`` des Diagramms): das des Knotens über dem von allen Knoten (``daten["format"]``).
- `_spiegel(r)`
- `_merke(i, r)` — Rechteck des Knotens Nummer ``i`` (Stelle in der Knotenliste) für ``knoten_rechtecke`` merken.
- `_farbe(daten, ebene)`
- `_stilfarbe(c)` — Die Füllfarbe, die der Formenstil aus der Farbe macht (für den Textkontrast).
- `_text_farbe(c)`
- `_fuellen(p, c, r)` — Stift und Pinsel nach dem Formenstil: 0 flach (ohne Rand), 1 einfach, 2 hell (Farbrand), 3 kräftig (dicker dunkler Rand), 4 3D (Verlauf).
- `_text_zeichnen(p, r, flags, t)` — Text immer ungespiegelt (auch bei „von rechts nach links“, wo die Formen gespiegelt werden).
- `_schrift(p, text, groesse)`
- `_kasten(p, r, text, c, rund, nr)`
- `_pfeil(p, a, b, c)`
- `_bild(b, h)`
- `_text(p, r, t, c, groesse)`
- `_gruppen(pts)` — Oberste Ebene als Überschrift, alles Eingerückte darunter als Unterpunkte: [(Nr. der Überschrift, Text, [(Nr., Unterpunkt)])].
- `_bunt(daten, i)`
- `_spalten(daten, pts, b)`
- `_gruppenliste(daten, pts, b)`
- `_matrix(daten, pts, b)`
- `_chevron(daten, pts, b)`
- `_radial(daten, pts, b)`
- `_zielscheibe(daten, pts, b)`
- `_trichter(daten, pts, b)`
- `_zeitachse(daten, pts, b)`
- `_stufen(daten, pts, b)`
- `_baum(pts)` — Die Wurzeln des Knotenbaums; jeder Knoten {i (Nr.), t (Text), e (Ebene), k (Kinder), a (Assistent)}.
- `_alle(n)`
- `_standard_baum(daten, wurzeln, b)` — Blätter nebeneinander, Eltern mittig über ihren Kindern; Assistenten stehen eine Zeile unter dem Eltern, die übrigen Kinder darunter.
- `_haengend_baum(daten, wurzeln, b, variante)` — Hängende Layouts: die Kinder stehen untereinander neben einer senkrechten Linie unter dem Eltern (links, rechts oder abwechselnd beidseits).
- `_organigramm(daten, pts, b)`
- `_liste(daten, pts, b)`
- `_prozess(daten, pts, b)`
- `_zyklus(daten, pts, b)`
- `_pyramide(daten, pts, b)`
- `_eintraege(pts)` — Oberste Ebene als Eintrag: [(Nr., Überschrift, Textzeilen (Aufzählungspunkte und Unterpunkte), [Nr. der Unterpunkte])].
- `_merke_mehrere(nummern, r)`
- `_zeilen(p, r, zeilen, grund, kopf)` — Aufzählungszeilen linksbündig in ``r`` (Textfarbe nach dem Untergrund ``grund``); ``kopf`` steht vorweg, wenn gegeben.
- `_blockraster(daten, pts, b)`
- `_punktliste(daten, pts, b)`
- `_balkenliste(daten, pts, b)`
- `_beschreibungsliste(daten, pts, b)`
- `_spaltenrahmen(daten, pts, b)`
- `_bildliste(daten, pts, b)`
- `_perspektive(daten, pts, b)`
- `_konvergenz(daten, pts, b)`
- `_kartenprozess(daten, pts, b)`
- `_kreisbeziehung(daten, pts, b)`
- `_segmentzyklus(daten, pts, b)`
- `zeichnen_mit_knoten(daten)` — Das SmartArt als Bild und dazu die Rechtecke aller Knoten (id → QRectF in Bildpunkten dieses Bildes).
- `zeichnen(daten)`
- `knoten_rechtecke(daten, b, h)` — id → QRectF der Knoten aus dem Zeichnen. Mit ``b``/``h`` (Größe des Objekts auf dem Blatt) umgerechnet in dessen Bildpunkte, sonst in
- `katalogeintrag(schluessel)`
- `neue_daten(eintrag, farben)` — Daten eines neuen SmartArt aus einem Katalogeintrag (oder dessen Schlüssel); ohne Angabe das Standard-Layout (Organigramm) mit Mustertext.
- `einfuegen(ed, daten)` — Fügt das SmartArt als freies Objekt ein (``editor/frei_objekt.py``): Rahmen, Griffe und Schnellleiste wie bei WordArt. ``daten`` = Daten
- `_inline_daten(ed)` — Daten eines älteren, im Text sitzenden SmartArt-Bildes (aus vorhandenen Dokumenten).
- `daten_der_auswahl(ed)` — Daten des gewählten SmartArt: zuerst das freie Objekt, sonst ein älteres Bild im Text.
- `aendern(ed, **felder)` — Daten des gewählten SmartArt ändern und neu zeichnen (Breite bleibt, Seitenverhältnis folgt). Ein neuer ``text`` (anders als der zu den
- `knoten_gewaehlt(ed)` — Id des gewählten Knotens des gewählten SmartArt (freies Objekt) oder None.
- `knoten_waehlen(ed, ident)` — Knoten wählen (None: Auswahl aufheben). Das Bild wird nicht neu gezeichnet.
- `knoten_bei(ed, pos)` — Die Id des Knotens unter ``pos`` (QPointF im Editor, dieselben Koordinaten wie die Rechtecke von ``ed._frei_liste()``) im gewählten SmartArt;
- `knoten_text(ed, ident)` — Der Text des Knotens (ohne Aufzählungspunkte) oder None.
- `knoten_text_setzen(ed, ident, text)` — Den Text eines Knotens setzen (Eintippen im Knoten) und neu zeichnen.
- `_knoten_schreiben(ed, kn, auswahl)`
- `_format_mischen(fmt, kw)` — Angaben in ein Format einarbeiten: None/False entfernt, ``linie``/``text`` werden mit den vorhandenen Angaben zusammengeführt.
- `format_lesen(ed)` — Werte für die Seitenleiste: ``{"format": …, "gewaehlt": Id \| None}`` — das Format des gewählten Knotens, ohne Auswahl das von allen Knoten.
- `format_setzen(ed, **kw)` — Format des gewählten Knotens (ohne Auswahl: aller Knoten) ändern; ``kw`` wie ``teil_format`` des Diagramms (``fuell``, ``linie``, ``schatten`` …, ``text``).
- `befehl_form(ed, wie)` — ``smartartFormEinfuegen``: neuen Knoten relativ zum gewählten (``wie`` siehe ``form_einfuegen``); der neue Knoten wird gewählt.
- `befehl_level(ed, richtung)`
- `befehl_verschieben(ed, richtung)`
- `befehl_aufzaehlung(ed)`
- `kann(ed, was, richtung)` — Ob ein Knotenbefehl gerade geht (zum Ausgrauen): ``level`` (erhoehen/reduzieren), ``verschieben`` (vor/zurueck), ``knoten`` (ein Knoten ist

### `editor/sprechblasen.py`

Sprechblasen: Kommentare und verfolgte Änderungen als Blasen im Seitenrand, mit Verbindungslinien zum Text.

- `konfig_lesen(settings)`
- `breite_mm(k)`
- `aktiv(k)`
- **class `Blase`**
- `autor_farbe(autor)`
- `_kuerzen(t, n)`
- `sammeln(doc, kommentare, verwenden)` — Alle Blasen des Dokuments in Textreihenfolge.
- `_kopf(bl)`
- `blasen_px(key)`
- `karten_pt(key)`
- `messen(bl, breite, font)` — Höhe der Blase bei gegebener Breite (alles in Bildpunkten des Zeichengeräts).
- `stapeln(anker_y, hoehen, unten, abstand)` — Obere Kanten der Blasen: so nah wie möglich an ihrem Anker, ohne sich zu überlappen (und nicht unter `unten`).
- `_ortszeit(iso)` — „2026-10-22 12:11“ in der Ortszeit (die Datei speichert UTC; die Karte links zeigt auch Ortszeit).
- `menue_rect(r)` — Die Fläche des Menüzeichens „☰“ oben rechts in der Blase (für den Klick).
- `zeichnen(p, bl, r, font, druck)` — Eine Blase zeichnen wie eine Karte: Kreis mit Initial, Name fett, Datum, Menüzeichen, darunter der Text — Farben des Designs, Kreis in der Farbe des Kommentars.
- `verbindung(p, bl, x_text, y_text, r, rechts)` — Linie vom Text zur Blase: waagerecht aus dem Seitenrand, dann zur Mitte der Kopfzeile.

### `editor/statistik.py`

Wörter zählen wie das Fenster der Vorlage: Seiten, Wörter, Zeichen mit und ohne Leerzeichen, Absätze, nicht-asiatische Wörter,

- `texte_des_dokuments(doc)`
- `zaehlen(texte, seiten)` — ``texte``: ein Eintrag je Absatz (auch Noten und Textfelder, wenn sie mitzählen sollen).

### `editor/stile.py`

Formatvorlagen des Katalogs (Start ▸ Stile) — Vorgaben und eigene Änderungen (Start ▸ Stile ▸ ↘ Formatvorlagen verwalten).

- `namen()`
- `ist_eigen(name)`
- `laden_neu(text)`
- `_meta(x)` — „basiert auf“, „folgender Absatz“ und die Abweichungen von der Basis (nur bei Vorlagen mit Basis).
- `als_json_neu()`
- `pruefe_name(name)` — Darf eine neue Vorlage so heißen? → None, sonst der Grund.
- `anlegen(name, *, basis, folge, **felder)` — Neue Vorlage anlegen. → None bei Erfolg, sonst der Grund (Name leer oder schon vergeben).
- `loeschen(name)`
- `laden(text)`
- `als_json()`
- `definition(name, _tiefe)`
- `aendern(name, **felder)`
- `zuruecksetzen(name)`
- `name_zu_key(name)`
- `key_zu_name(key)`

### `editor/suche.py`

Suchen und Ersetzen wie im Fenster der Vorlage: Sonderzeichen (^p, ^t, ^? …), Platzhalter, Präfix/Suffix, Satzzeichen und Leerzeichen

- **class `Suchauftrag`**
  - `hat_format()`
  - `leer()`
- `roh_text(doc)` — Der Text des Dokuments, eine Stelle je Position, mit Kennzeichen für Noten, Felder, Grafiken und Umbrüche.
- `_woertlich(text)` — Suchtext ohne Platzhalter → Liste von Regex-Stücken (ein Stück je Zeichen oder Sonderzeichen).
- `_platzhalter(text)` — Platzhalter wie in Word: ? ein Zeichen, * beliebig viele, [abc] [a-z] [!x] eines davon/keines, {n,m} Wiederholung, @ eins oder mehr,
- `muster(a)` — Der reguläre Ausdruck des Auftrags; ``None`` bei leerem Text (dann sucht nur die Formatierung) oder ungültigen Platzhaltern.
- `gueltig(a)`
- `_zeichen_passen(doc, von, bis, a)`
- `_nur_format(doc, a, von, bis)` — Ohne Suchtext: jede zusammenhängende Strecke mit der gesuchten Formatierung (je Absatz).
- `treffer(doc, a, von, bis, grenze)` — Alle Treffer im Bereich [von, bis) als (von, bis).
- `naechster(doc, a, ab, rueckwaerts, von, bis, umlauf)` — Der nächste Treffer hinter (oder vor) ``ab``; mit ``umlauf`` geht es am Ende vorn weiter (und umgekehrt).
- `ersatz_text(a, ersatz, gefunden, zwischenablage)` — Der Ersatztext mit seinen Sonderzeichen: ^p Absatz, ^t Tab, ^l Zeilenumbruch, ^m Seiten-, ^n Spaltenumbruch, ^& der gefundene Text,
- `ersetzen(doc, von, bis, neu, format_, absatz_format)` — Den Bereich durch ``neu`` ersetzen (Text mit Kennzeichen aus ``ersatz_text``). Die Formatierung des ersetzten Textes bleibt,
- `_umbruch_weg(doc, pos, art)`
- `alle_ersetzen(doc, a, ersatz, von, bis, format_, absatz_format, zwischenablage)` — Alle Treffer im Bereich ersetzen, als ein Schritt für Rückgängig. → Zahl der Ersetzungen.

### `editor/tabelle_text.py`

Text in Tabelle umwandeln und zurück (Einfügen ▸ Tabelle). Keine Oberfläche; jede Umwandlung ist ein Rückgängig-Schritt.

- `markierte_absaetze(ed)` — Die Absätze der Markierung (ganz, auch wenn die Markierung mitten im Absatz beginnt).
- `zellen(texte, trenner)` — Absätze in Zeilen und Zellen teilen. Bei „Absatzmarken“ wird jeder Absatz eine Zeile mit einer Zelle.
- `text_zu_tabelle(ed, trenner, spalten)`
- `_zelle_text(zelle, trenner, geschachtelt, bleiben)` — Text einer Zelle. Eine Tabelle darin wird mit umgewandelt (``geschachtelt``) oder als Kopie in ``bleiben`` gemerkt und
- `_tabelle_zeilen(t, trenner, geschachtelt, bleiben)`
- `tabelle_zu_text(ed, trenner, geschachtelt)` — Die Tabelle an der Schreibmarke zu Text. ``geschachtelt``: Tabellen in Zellen ebenfalls zu Text; sonst bleiben sie Tabellen

### `editor/tabellenstil.py`

Tabellenformatvorlagen und Formatoptionen (Kopfzeile, gebänderte Zeilen, erste Spalte).

- `_zellen(t)`
- `_fett(cell, an, farbe)`
- `anwenden(t, name, kopf, streifen, spalte)`

### `editor/tabfuell.py`

Füllzeichen vor Tabstopps (Punkte, Striche, Linie): Qt kennt sie nicht, Lunivo zeichnet sie selbst.

- `lesen(bf)` — Position (px) → Füllzeichen-Schlüssel eines Absatzformats.
- `setzen(bf, fuell)`
- `aus_docx(wert)`
- `zeichnen(p, d)` — Füllzeichen in die Tabstrecken der Absätze zeichnen. Koordinaten: Dokument.

### `editor/textdaten.py`

Formatierten Text als einfache Daten (Absätze aus Textstücken) ablegen und wieder einfügen — für Textbausteine und Ähnliches.

- `_stueck(f)`
- `fragment_zu_daten(fragment)`
- `daten_zu_fragment(absaetze)`

### `editor/texteffekt.py`

Texteffekte, die Lunivo zeichnet: Füllung des Textes (Farbe, Transparenz) und Kontur (Farbe, Breite, Linienart).

- `strich_setzen(pen, art)` — Strichart (Muster oder Qt-Stil) in einen Stift schreiben.
- `zu_format(w)` — Zeichenformat, das den Effekt zeichnet (zum Anwenden im Editor und für Vorschauen).
- `aus_format(cf)`
- `als_text(w)` — Nur Transparenz und Kontur; ``""`` wenn weder noch.
- `aus_text(text, farbe)`
- `_q(name)`
- `_farbelement(eltern, hexwert, alpha_pct)`
- `_verlauf_element(eltern, v)`
- `in_rpr(rpr, cf)` — Texteffekte des Zeichenformats als w14-Elemente an ``w:rPr`` schreiben, in der Reihenfolge des Schemas (nichts, wenn es keinen Effekt gibt).
- `_wert(e, name, vorgabe)`
- `_farbe_aus(e)` — (Farbe, Transparenz in %) eines Elements mit w14:srgbClr darunter.
- `_verlauf_aus(g)`
- `aus_rpr(rpr, cf)` — Das Gegenstück zu ``in_rpr``: die w14-Elemente von ``w:rPr`` ins Zeichenformat lesen.

### `editor/textfx.py`

Texteffekte, die Qt am Text nicht kennt und die Lunivo über den Umrissen der Buchstaben selbst zeichnet: Farbverlauf in Füllung und Kontur,

- `_farbe(hexwert, transparenz)`
- `hat_effekt(fx)`
- `als_text(fx)` — Nur die Teile, die Lunivo selbst zeichnet, als JSON für das Zeichenformat (leer = keiner).
- `aus_text(text)`
- `_verlauf(rect, v)`
- `_weich(p, pfad, farbe, radius, ausserhalb)` — Pfad mit weichem Rand: gefüllt, dazu Striche in wachsender Breite und sinkender Deckkraft.
- `_richtung(winkel)`
- `_helligkeit(c, f)`
- `_kontur_pfade(pfad, breite, form, art)` — Die Flächen einer Konturlinie: einfach ein Strich, doppelt zwei Streifen mit Lücke, dick–dünn ein dicker und ein dünner.
- `fx_zeichnen(p, pfad, fx, grundlinie, schrift_px, basis_farbe, kontur)` — Die Effekte zu einem Textstück zeichnen. ``pfad``: Umrisse in Zeichenkoordinaten, ``grundlinie``: y der Schriftlinie, ``schrift_px``: Schriftgröße.
- `_woerter(text)` — Die Wörter eines Textes als (Anfang, Ende); Leerzeichen bleiben frei („Nur Wörter“).
- `_unterstrich(p, strecken, art, grundlinie, groesse, farbe)` — Unterstreichungen, die Qt nicht kennt: doppelt, dick, lang gestrichelt, Wellen in zwei Stärken, nur Wörter.
- `unter_zeichnen(p, x0, y, x1, art, farbe, groesse)` — Eine Unterstreichungsart als Linie von ``x0`` bis ``x1`` in Höhe ``y`` (für Auswahllisten wie das Menü am Knopf „Unterstrichen“).
- `unter_symbol(art, groesse, farbe)` — Bildchen einer Unterstreichungsart für Auswahllisten (dieselbe Zeichnung wie im Text).
- `_doppelt_durch(p, rect, grundlinie, groesse, farbe)` — Die zweite Durchstreichlinie (die erste zeichnet Qt): zwei Linien in Höhe der Kleinbuchstaben.
- `_betonung(p, glyphen, art, grundlinie, groesse, farbe)` — Betonungszeichen: ein Punkt, Kreis oder Komma über (oder ein Punkt unter) jedem Buchstaben.
- `text_pfad(text, font, ursprung)` — Umrisse eines Textes (für Vorschauen); → (Pfad, y der Grundlinie).
- `vorschau_zeichnen(p, rect, text, font, fx, farbe, kontur)` — Text mit Effekt zentriert in ein Rechteck zeichnen (Kacheln und Vorschau der Fenster); der Text selbst wird hier mitgezeichnet.
- `absaetze_zeichnen(p, d)` — Die Effekte aller Textstücke des Dokuments zeichnen (Textstücke mit ``P_EFFEKT``). Koordinaten: Dokument.
- `_P(name)`
- `hat_zeichen_effekt(cf)` — Hat dieses Zeichenformat etwas, das Lunivo selbst zeichnet: Effekte, doppelt durchgestrichen oder Betonungszeichen?
- `_stueck(p, b, tl, von, laenge, cf, fx)`
- `_umschlossen(p, kasten, wie, farbe, groesse)` — Die Form um die Zeichen: „reduzieren“ legt sie eng an, „erweitern“ lässt dem Symbol Raum.
- `_ruby(p, x0, x1, grundlinie, groesse, ruby, farbe)` — Der Leittext über dem Basistext, in kleinerer Schrift, nach der gewählten Ausrichtung.
- `schatten_vorgaben()` — [(Abschnitt, Name, Schatten)] — Außen, Innen (je 9) und Perspektive (5).
- `reflektion_vorgaben()` — 9 Spiegelungen: drei Größen (eng, halb, voll) mal drei Abstände.
- `leuchten_vorgaben()` — 24 Leuchtvarianten: sechs Farben mal vier Größen.
- `voreinstellung_icon(fx, groesse, text, farbe)` — Kachelbild einer Voreinstellung: ein „A“ mit dem Effekt auf weißem Grund.
- `wordart_vorgaben()` — Die 15 Formatvorlagen im Menü „Texteffekte ▸ WordArt“: Füllung, Kontur, Schatten (vollständige Effekte, ersetzen die bisherigen).
- `wordart_icon(w, groesse)` — Kachelbild einer WordArt-Formatvorlage.

### `editor/umbruch.py`

Textumbruch um Bilder: Bilder, die links oder rechts stehen und vom Text umflossen werden.

- `_rahmen(frame)`
- `schwebende_rahmen(doc)` — {Position des Bildzeichens: Rahmen} für alle schwebenden Bilder des Dokuments.
- `schwebend(doc, pos)` — „links“ / „rechts“, wenn das Bild an Position pos schwebt; sonst None (Bild steht in der Zeile).
- `bild_im_rahmen(rahmen)` — Das Bild, das in einem schwebenden Rahmen steht.
- `ist_anker(blk)`
- `schwebend_einfuegen(doc, blockpos, f, seite)` — Fügt das Bild f vor dem Absatz bei blockpos als schwebendes Bild ein (seite: „links“ \| „rechts“).
- `absatz_nach_rahmen(doc, bildpos)` — Der Absatz, zu dem das schwebende Bild bei bildpos gehört (er folgt dem Rahmen).
- `schwebend_entfernen(doc, pos)` — Nimmt das schwebende Bild bei pos samt Rahmen und Anker aus dem Dokument. Gibt die Stelle zurück, an der der Absatz
- `umbruch_setzen(ed, modus)` — Das markierte Bild: modus „zeile“ (mit Text in Zeile), „links“ oder „rechts“ (vom Text umflossen).

### `editor/vergleich.py`

Dokumente vergleichen und zusammenführen — das Ergebnis sind verfolgte Änderungen (einfügen/löschen, mit Autor und Datum).

- `_absaetze(doc)`
- `ops_bestimmen(basis, andere, autor)` — Änderungen von `basis` nach `andere` als Operationen auf den Absätzen von `basis`.
- `_bereich(op, ta_len)`
- `zusammenlegen(listen)` — Operationen mehrerer Autoren vereinen; überschneidende Löschungen verschiedener Autoren → die erste gilt, die andere ist Konflikt.
- `_jetzt()`
- `_markieren(doc, von, bis, art, autor, datum)`
- `anwenden(ziel, ops, datum)` — Operationen als verfolgte Änderungen in `ziel` schreiben (von hinten nach vorn, damit die Stellen stimmen).
- `vergleichen(basis, andere, autor)`
- `zusammenfuehren(basis, fassungen)`

### `editor/verweise.py`

Beschriftungen, Textmarken, Querverweise, Stichwörter und Zitate — Funktionen am Editor.

- `seq_format(anweisung)` — Zahlschreibweise aus einer Feldanweisung ``SEQ Abbildung \* ROMAN`` (Vorgabe arabisch).
- `naechste_nummer(ed, label, zahl)` — Nummer, die eine neue Beschriftung ``label`` an der Schreibmarke bekäme (für die Anzeige im Fenster).
- `beschriftung_einfuegen(ed, label, text, oben, *, nach, ohne_bezeichnung, zahl)` — Beschriftung „Abbildung 1: Text“ unter (``oben``: über) dem Objekt oder Absatz. ``nach`` ersetzt „: Text“ durch genau diesen
- `beschriftungen_nummerieren(ed)`
- `beschriftungen_liste(ed)`
- `lesezeichen_liste(ed, versteckte)` — [{name, von, bis}] — zusammenhängende Textstücke mit demselben Namen. ``versteckte=False`` lässt die Marken weg, die mit
- `lesezeichen_name_gueltig(name)`
- `lesezeichen_setzen(ed, name)`
- `lesezeichen_loeschen(ed, name)`
- `lesezeichen_gehe(ed, name)`
- `intern_springen(ed, href)`
- `verweisen_auf(art)`
- `querverweis_ziele(ed)` — Mögliche Ziele: nummerierte Absätze, Überschriften, Textmarken, Fuß- und Endnoten, Beschriftungen.
- `_seq_fragment(blk)`
- `_bezeichnung_nummer(blk)` — „Abbildung 2“ — der Text der Beschriftung bis einschließlich der Nummer.
- `_beschriftungstext(blk)` — Der Text hinter der Nummer, ohne Doppelpunkt.
- `marke_sichern(ed, ziel)` — Name der Textmarke am Ziel. Fehlt eine, bekommt der Bereich des Ziels eine verborgene Textmarke „_Ref…“ (wie in Word).
- `querverweis_text(ed, ziel, wie, oben_unten)` — Der Text, den der Querverweis zeigt. wie: "text", "nummer", "nur_text", "seite" oder "obenunten".
- `querverweis_einfuegen(ed, ziel, wie, *, link, oben_unten)` — Querverweis an der Schreibmarke (siehe ``querverweis_text``); ``link`` macht ihn zum internen Hyperlink (Strg+Klick).
- `index_eintragen(ed, e, alle)` — Indexeintrag ``e`` (``editor.indexeintrag.Eintrag``) an die Markierung setzen (ohne Markierung: das Wort an der
- `index_markieren(ed, term)`
- `zitat_einfuegen(ed, q)`
- `quelle_tag(quellen, q)` — Eindeutiger Kurzname wie in Word (Nachname + Jahr).

### `editor/verzeichnis.py`

Verzeichnisse: Inhalt, Abbildungen, Tabellen, Stichwörter, Literatur.

- `toc_opt_text(opt)`
- `toc_opt_lesen(text)`
- `toc_optionen(doc)` — Einstellungen des ersten Inhaltsverzeichnisses im Dokument (None, wenn es keines gibt).
- `_ueberschriften(doc, ebenen)`
- `_toc_marke(doc, pos, vergeben)` — Name der verborgenen Textmarke an der Überschrift bei ``pos``; fehlt sie, wird sie gesetzt.
- `_alle_toc_marken(doc)`
- `_beschriftungen(doc, label)`
- `_stichwoerter(doc)` — [(Eintrag, Position)] aus den markierten Textstellen (eine Stelle je zusammenhängender Markierung).
- `_index_zeilen(editor)` — Zeilen des Stichwortverzeichnisses: Haupteinträge, darunter eingerückt die Untereinträge; „Siehe …“ statt Seitenzahl,
- `_seiten(editor, positionen)`
- `zeilen_fuer(editor, art, opt)` — → [(Ebene, Text, Seitenangabe)]; beim Inhaltsverzeichnis mit Verknüpfungen (``opt["links"]``) als viertes die Textmarke.
- `_schreibe(cur, editor, art, zeilen, neuer_block, opt)`
- `verzeichnis_einfuegen(editor, art, opt)` — Verzeichnis an der Schreibmarke einfügen. Gibt es schon ein Inhaltsverzeichnis, wird es mit ``opt`` neu geschrieben.
- `_bereiche(doc)` — [(Art, erste Blockposition, letzte Blockposition)] zusammenhängender Verzeichnisblöcke.
- `verzeichnis_aktualisieren(editor, nur)` — Alle Verzeichnisse (oder nur die der Art ``nur``) neu schreiben; gibt die Zahl der Zeilen zurück.
- `vorhanden(doc, art)`
- `_neu_schreiben(editor, nur, opt_neu)`

### `editor/vorlagen.py`

Die mitgelieferten Gerüste (Brief, Bewerbung, Lebenslauf …) und eigene Vorlagen.

- `muster()`
- `_benutzer_zeilen(b, mit_name)`
- `_ersetze(text, b)`
- `aufbauen(ed, zeilen, benutzer, heute)` — Schreibt das Gerüst in den (leeren) Editor und hebt die Lücken hervor.
- `naechste_luecke(doc, von)`
- `luecken_entfernen(doc)` — Für den Druck: Lücken « … » verschwinden samt Klammern.
- `vorlagenordner(settings)`
- `rubriken(ordner)` — Der Vorlagenordner nach Rubriken: jeder Unterordner ist eine Rubrik (Name → Dateien); lose Dateien liegen im Ordner selbst.
- `eigene_vorlagen(ordner)`

### `editor/wasserzeichen.py`

Wasserzeichen einer Seite: Text oder Bild, mit Lage, Größe und Transparenz (Einfügen ▸ Wasserzeichen). Keine Oberfläche.

- `da(w)` — Ob das Wasserzeichen etwas zeigt (Text oder Bild).
- `bild_zu_text(img)`
- `bild_aus_text(text)`
- `ausgewaschen(img)` — „Auswaschen“ wie in Textverarbeitungen: hell und kontrastarm (85 % zum Weiß hin).
- `_deckkraft(w)`
- `_lage(w, r, b, h)` — Mittelpunkt des Wasserzeichens (Breite b, Höhe h) im Seitenrechteck r.
- `schrift(w, r)` — Schrift des Textwasserzeichens; „automatisch“ füllt die Seite (waagerecht 80 % der Breite, schräg 78 % der Diagonale).
- `zeichnen(p, w, r)` — Das Wasserzeichen ``w`` auf die Seite ``r`` (96-dpi-Bildpunkte) zeichnen.

### `editor/wortextras.py`

Wort-Extras: Absätze aufräumen — über die Markierung, ohne Markierung über das ganze Dokument. Jede Handlung ist ein Schritt für Rückgängig.

- `_bloecke(ed)` — Die Absätze der Markierung (ohne Markierung: alle) außerhalb von Tabellen, in Dokumentreihenfolge.
- `_leer(b)` — Ein Absatz ohne Zeichen und ohne Bild.
- `_schritt(ed, arbeit)` — Führt ``arbeit(doc, bloecke)`` als einen Rückgängig-Schritt aus. → Zahl der Änderungen.
- `leere_loeschen(ed)`
- `leere_einfuegen(ed)`
- `zeilenumbruch_in_return(ed)`
- `absaetze_neu_anordnen(ed)` — Absätze, die mitten im Satz enden (hartes Return in einem Satz, etwa aus PDF-Text), werden zu einem Absatz.
- `leerzeichen_bereinigen(ed)` — Doppelte Leerzeichen und Leerzeichen am Anfang und Ende der Absätze entfernen.
- `einzug_zwei_zeichen(ed)` — Erstzeileneinzug um zwei Zeichen der Schriftgröße des Absatzes.
- `smart_anordnen(ed)` — Leerzeichen bereinigen, leere Absätze löschen, Erstzeileneinzug um zwei Zeichen.
- `fuehrende_leerzeichen_loeschen(ed)` — Leerzeichen und Tabs am Anfang der Absätze entfernen.
- `zeilenumbrueche_loeschen(ed)` — Manuelle Zeilenumbrüche (Umschalt+Enter) entfernen; die Zeilen laufen zusammen, zwischen zwei Wörtern bleibt ein Leerzeichen.
- `leerabsatz_modus_wechseln(ed)` — Trennung durch leere Absätze umschalten: Stehen zwischen den Absätzen leere Absätze, verschwinden sie; sonst kommt zwischen
- `einzug_in_leerzeichen(ed)` — Den Erstzeileneinzug eines Absatzes in Leerzeichen am Absatzanfang umwandeln (gleich breit), der Einzug selbst wird 0.

### `editor/zahlformat.py`

Zahlen in anderer Schreibweise (Einfügen ▸ Zahl): 1,2,3 · A,B,C · I,II,III · eingekreist · Zahlwort. Keine Oberfläche.

- `_buchstaben(n)` — 1 → A, 26 → Z, 27 → AA (wie Listen in Word).
- `_unter_tausend(n)`
- `zahlwort(n)` — Deutsches Zahlwort bis 999 999 („einundzwanzig“, „eintausend“).
- `grenzen(typ)` — Kleinste und größte Zahl, die der Typ darstellen kann.
- `zahl_text(n, typ)` — Die Zahl im gewählten Typ; liegt sie außerhalb der Grenzen, ``ValueError``.

### `editor/zeichenzusatz.py`

Zeichenzusätze der Gruppe „Schriftart“ ▸ Groß-/Kleinschreibung: Eingeschlossene Zeichen und Phonetisches Leitzeichen.

- `umschlossen_text(form, vorlage)`
- `umschlossen_lesen(text)`
- `ruby_text(ruby, ausrichtung, abstand, groesse)`
- `ruby_lesen(text)`

### `editor/zeilennummern.py`

Zeilennummern (Seitenlayout ▸ Zeilennummern): welche Zeile welche Nummer trägt. Keine Oberfläche — Editor, Druck und PDF zeichnen damit.

- `unterdrueckt(block)`
- `nummern(doc, ch, art)` — (Absatz, Zeile, y im Textfluss, Nummer) für jede nummerierte Zeile; ``ch``: Höhe des Textbereichs einer Seite im Fluss.

### `editor/zusatz.py`

Zusatzdaten am Text: Kommentare, Fuß-/Endnoten, nachverfolgte Änderungen.

- `roemisch(n)`
- `neue_id(vorhanden)`
- `leere_meta()`
- `abstand_davor_px(bf)` — Der Abstand vor dem Absatz, wie ihn der Benutzer eingestellt hat — auch wenn Lunivo ihn am Seitenanfang gerade unterdrückt.
- `kommentar_farbe(geloest)`

## `models`

### `models/__init__.py`

Datenmodelle: Seiteneinrichtung, Berichte.


### `models/page.py`

Seiteneinrichtung: Papier, Ränder, Ausrichtung, Kopf- und Fußzeile.

- `mm_to_px(mm)`
- `px_to_mm(px)`
- **class `HeaderFooter`** — Text mit Platzhalter {PAGE} und {PAGES}. Ausrichtung: left\|center\|right, dazu aussen\|innen (ungerade Seiten rechts bzw. links,
  - `is_empty()`
- **class `PageSettings`**
  - `landscape()`
  - `set_orientation(landscape)`
  - `set_paper(name)`
  - `paper_name()`
  - `content_width_px()`
  - `content_height_px()`
  - `kopf_fuss_art(blatt, nummer)` — Welche Kopf-/Fußzeile ein Blatt trägt: "first" (Blatt 1 bei „Erste Seite anders“), "even" (gerade angezeigte Seitenzahl bei
  - `kopf_fuss(blatt, nummer)` — (Kopfzeile, Fußzeile) für das Blatt, siehe ``kopf_fuss_art``.
  - `erste_seite_versatz_px()` — Wie weit der Text der ersten Seite nach unten rückt, weil die Kopfzeile länger ist als der obere Rand: Der Text beginnt erst unter der
  - `copy()`
  - `spalten_breite_px()` — Breite einer Textspalte (bei einer Spalte: die ganze Textbreite).

### `models/report.py`

Bericht über das, was beim Öffnen/Speichern nicht verlustfrei ging.

- **class `IOReport`**
  - `warn(text)`
  - `__bool__()`
- **class `DocumentIOError`**(Exception) — Datei nicht lesbar oder nicht schreibbar — Text ist für Anwender gedacht.
- **class `PasswortNoetig`**(DocumentIOError) — Das Dokument ist verschlüsselt; ohne (richtiges) Kennwort lässt es sich nicht öffnen.
  - `__init__(falsch)`

## `proofing`

### `proofing/__init__.py`

Schreibhilfe: Prüfregeln, Vorhersage, Autokorrektur, Barrierefreiheit, Silben.


### `proofing/autokorrektur.py`

AutoKorrektur beim Tippen. Greift erst, wenn ein Wort abgeschlossen ist.

- `_ordnung(m)`
- `korrigiere(text, an)`
- `kleinste_aenderung(alt, neu)` — → (von, bis, ersatz): nur der Abschnitt, der sich wirklich ändert — Formatierung bleibt sonst unberührt.

### `proofing/barrierefreiheit.py`

Barrierefreiheit prüfen — was Menschen mit Sehbehinderung den Text unlesbar macht.

- `_hell(c)`
- `kontrast(vorne, hinten)`
- `pruefe(editor)`
- `_tabellen(doc)`

### `proofing/fund.py`

Herkunft und Sicherheit eines Fundes; Auflösung, wenn mehrere Quellen dieselbe Stelle melden.

- `klemmen(wert, vorgabe)`
- `markieren(funde, quelle)` — Quelle und – falls nicht vorhanden – Standard-Konfidenz eintragen (liefert Kopien).
- `_rang(f)`
- `loesen(funde)` — Überschneidende Funde auflösen: der beste bleibt, die unterlegenen werden nicht angezeigt, aber als `verdraengt` vermerkt.

### `proofing/haeufig.py`

Häufige deutsche Wörter.


### `proofing/inkrement.py`

Inkrementelle Prüfung: nur die geänderte Stelle (plus Sicherheitsbereich) neu prüfen, den Rest verschieben und behalten.

- `verschieben(funde, pos, entfernt, hinzu)` — Funde nach einer Änderung (pos, entfernt, hinzugefügt) umrechnen. Betroffene Funde entfallen.
- `schmutz_abbilden(bereich, pos, entfernt, hinzu)` — Den bisher ungeprüften Bereich in die neuen Positionen umrechnen und um die neue Änderung erweitern.
- `pruefbereich(text, a, b, absaetze)` — Den geänderten Bereich auf ganze Absätze samt Sicherheitsbereich erweitern.
- `lohnt(laenge, von, bis)`
- `einsetzen(alt, von, bis, neue_relativ)` — Funde im Bereich [von, bis) durch die neuen (Positionen relativ zum Bereich) ersetzen.

### `proofing/proofing_service.py`

Die Schreibhilfe: prüft im Hintergrund, hält den Stand, setzt Korrekturen ein.

- `zeige_leer(s)` — Leerzeichen und Zeilenumbrüche in Worten statt in Symbolen: „2 Leerzeichen“, „Zeilenumbruch“ (auch gut vorlesbar).
- **class `_Signale`**(QObject)
- **class `_Lauf`**(QRunnable)
  - `__init__(rev, text, gelernt, signale, schalter)`
  - `run()`
- **class `WritingAssistant`**(QObject)
  - `__init__(settings, gelernt, parent)`
  - `an(name)`
  - `setze(name, wert)`
  - `setze_thema(name)`
  - `ak_an(name)`
  - `attach(editor)`
  - `_geaendert(pos, entfernt, hinzu)` — Bereichs-Invalidierung: Funde hinter der Änderung verschieben, Funde an der Änderung verwerfen, Bereich merken.
  - `dokument_geaendert()`
  - `pruefen(zaehlen, voll)` — zaehlen=True nur bei ausdrücklichem Prüfen (Knopf): dann zählt das Gedächtnis mit und es wird alles geprüft.
  - `_fertig(rev, roh)`
  - `_key(f)`
  - `_zeigen(meldung)`
  - `anzeigen(funde)`
  - `funde_an(pos)`
  - `erweitere_menue(menu, pos)` — Ein Kopf, ein Vorschlag je Möglichkeit, drei Aktionen — wie im Prüfbogen (Kontextmenü für Fehler-Aktionen).
  - `_wort_an(pos)` — (Wort, von, bis), wenn an der Stelle ein Wort steht, das das Wörterbuch nicht kennt.
  - `alle_ignorieren(wort)`
  - `zum_woerterbuch(wort)`
  - `ignorierte_wieder_pruefen()`
  - `gruendlich()`
  - `_lt_fertig(rev, funde)`
  - `aendern(fund)`
  - `lassen(fund)`
  - `alle_aendern()`
  - `vorschlaege(anfang)`
  - `autokorr(text_vor_cursor)`

### `proofing/pruefung.py`

Die Prüfung ohne Internet: Regeln, Listen und Begründungen für Rechtschreibung, Grammatik und Zeichensetzung.

- `daten_ordner()` — Wo regeln.json und woerter.txt liegen.
- `_lies_regeln()` — Holt den gemeinsamen Wortschatz aus regeln.json.
- `uebernimm_schreibweise(original, verbesserung)`
- `mach_fund(von, bis, alt, neu, grund, art, wort_ebene)`
- `ist_abkuerzung(text, punkt)`
- `wort_um(text, stelle)`
- `ist_adresse(text, stelle)`
- `gross_dahinter(m, text)`
- `regel(muster, bau, grund, art, gruppe, pruefe, flags)`
- `wende_regeln_an(text, regeln, funde)`
- `pruefe_kongruenz(text, funde)`
- `lade_woerter(pfad)` — Liest die deutsche Wörterliste. Sie liegt neben dieser Datei; fehlt sie,
- `trenne_zusammen(wort)`
- `pruefe_zusammengeschrieben(text, funde)`
- `nachbar_woerter(w)` — Alle Wörter, die genau einen Handgriff entfernt sind.
- `_de_schluessel(wort)`
- `tippfehler_vorschlag(wort)`
- `pruefe_tippfehler(text, funde, gelernt)`
- `wort_abstand(a, b)` — Wie viele Handgriffe liegen zwischen zwei Wörtern? Zwei vertauschte
- `ist_korrektur(falsch, richtig)` — Sieht die Verbesserung dem Wort überhaupt ähnlich? Ein Rechtschreib-
- `uebergehen(wort, text, stelle, schalter)`
- `pruefe_woerter(text, funde, gelernt, schalter)`
- `pruefe_satzende(text, funde)`
- `mach_hinweis(von, bis, grund, stelle)`
- `pruefe_satzbau(text, hinweise)`
- `ohne_ueberschneidung(funde)` — Zwei Funde an derselben Stelle gehen nicht — die erste Änderung ließe
- `finde_probleme(text, gelernt, schalter)` — Alle Stellen, die auffällig sind — in derselben Reihenfolge wie am Handy.
- `abstand(a, b)`
- `koelner_phonetik(wort)`
- `_klangtafel()`
- `klingt_wie(wort, hoechstens)`
- `vorschlaege_fuer(wort, hoechstens, gelernt)`

### `proofing/silben_de.py`

Deutsche Sprechsilben — für „Silben farbig“ (Lesehilfe für Legasthenie).

- `_einheiten(w)` — Zerlegt in Buchstabeneinheiten: Vokalkerne (V…), Konsonanteneinheiten (K…). → Liste von (art, text).
- `_wortende(w)` — Zusätzliche Grenzen am Wortende für getrennt gesprochene Vokale: Ide-en, Mu-se-um, Fami-li-en, Fa-mi-li-e.
- `_stueck(w)` — Silbengrenzen (Indizes in w) innerhalb eines Wortstücks nach den Regeln der Sprechsilben.
- `_pyphen()`
- `_hat_kern(s)`
- `_hinweis_ok(w, p)` — Ist die von pyphen vorgeschlagene Stelle p ein Wortbaustein-Rand und keine bloße Zeilenumbruch-Stelle?
- `silben(wort)` — Das Wort in Sprechsilben. Wörter mit Ziffern/Sonderzeichen und ganz in Großbuchstaben bleiben ungeteilt.

### `proofing/vorhersage.py`

Wortvorhersage und Themenwörter (daten/themenwoerter.json).

- `themenwoerter()` — Liest daten/themenwoerter.json: je Empfänger eine Liste von Wörtern.
- `thema_woerter(name)`
- `thema_aufnehmen(woerter)` — Themenwörter sind richtig geschrieben und bekommen keine Wellenlinie.
- `_liste()`
- `faengt_an_mit(anfang, hoechstens, gelernt, thema)`

## `services`

### `services/__init__.py`

Dienste: Dateien (DOCX/ODT/…), Einstellungen, Wiederherstellung, Bausteine, Vorlesen, Anbindungen.


### `services/bausteine.py`

Textbausteine: markierter Text mit Formatierung unter einem Namen merken und später einfügen.

- `_pfad()`
- `laden()`
- `speichern(liste)`
- `standard()` — Die mitgelieferten Bausteine (Briefe, Bewerbungen …); sie lassen sich einfügen, aber nicht ändern.
- `alle()` — Mitgelieferte und eigene Bausteine (Eigene zuletzt).
- `finde_kuerzel(kuerzel)` — Der Baustein zu einem Kürzel (Eigene gehen vor den mitgelieferten).
- `hinzufuegen(name, fragment, kuerzel)`
- `entfernen(name)`
- `einfuegen(cursor, baustein)` — Fügt den Baustein mit seiner Formatierung ein; ein alter Eintrag ohne Absatzdaten kommt als einfacher Text.

### `services/bild_export.py`

Das Dokument als Bild schreiben: jede Seite als eigene Datei oder alle Seiten untereinander als ein langes Bild.

- **class `BildWahl`**
- `_frei(pfad)` — Ein Dateiname, den es noch nicht gibt (nichts Vorhandenes wird überschrieben): „Brief (2).png“.
- `wasserzeichen(img, text)` — Den Text schräg und blass über das ganze Bild legen.
- `_speichern(img, pfad, fmt)`
- `bilder_schreiben(doc, page, noten, name, wahl)` — Schreibt die Bilder nach ``wahl.ordner``. → die geschriebenen Dateien.

### `services/docx_reader.py`

DOCX → QTextDocument (python-docx).

- `_xp(el, ausdruck)` — XPath mit den Namensräumen von python-docx — auch für Elemente, deren Klasse kein eigenes xpath mit Namensräumen hat.
- `_emu_to_px(v)`
- `_pt_to_px(v)`
- `_style_chain(style)`
- `_doc_defaults(document)`
- **class `_Reader`**
  - `__init__(path)`
  - `_laden_zusatz()` — Kommentare (python-docx) und Fuß-/Endnoten (Teile footnotes.xml / endnotes.xml) einlesen.
  - `_kommentare_geloest_lesen()` — Welche Kommentare Word als gelöst markiert hat (Teil commentsExtended: w15:done je Absatzkennung).
  - `_quellen_lesen()` — Literaturquellen aus dem Word-Bibliografieteil (customXml, Namensraum …/bibliography).
  - `_standard_stil(art)`
  - `_ps(para)` — Absatzvorlage (mit Zwischenspeicher).
  - `_rs(run)`
  - `_kette(style)`
  - `_style_attr(style, getter)`
  - `_stil_font(style, attr)`
  - `_font_name(run, para)`
  - `_font_size_pt(run, para)`
  - `_flag(run, para, attr)`
  - `_heading_level(para)`
  - `_char_format(run, para)`
  - `_schrift_zusatz(rpr, f)` — Schrift für asiatische und komplexe Zeichen, Betonungszeichen und doppeltes Durchstreichen (Fenster „Schriftart“).
  - `_highlight(run)`
  - `_ausrichtung(para, st)` — w:jc roh lesen — python-docx kennt „start“/„end“ nicht und bricht sonst ab.
  - `_block_format(para)`
  - `_list_info(para)` — → (numId, ilvl, 'bullet'\|'decimal'\|…) oder None.
  - `_num_format(num_id, ilvl)`
  - `_start_block(bfmt, cfmt, cursor, reuse)`
  - `add_paragraph(para, cursor, reuse, in_table)`
  - `_laufe(eltern, para, cursor, href)` — Kinder eines Absatzes der Reihe nach: Läufe, Links, nachverfolgte Änderungen, Kommentar- und Textmarkenbereiche.
  - `_feld_ende()`
  - `_form_meta(sdt)` — Inhaltssteuerelement → Formularfeld-Daten (JSON); eigene Felder tragen sie im Tag, fremde (Word) werden aus der Art abgeleitet.
  - `_zusatz_formate(cfmt)`
  - `_block_zusatz(bfmt, para)` — Verzeichnis- und Beschriftungsabsätze an ihrer Formatvorlage wiedererkennen; Absatzrahmen aus w:pBdr.
  - `_flush_break(cursor)`
  - `_add_run(run, para, cursor, href)` — → True, wenn Text oder Bild eingefügt wurde.
  - `_note_marke(art, n)`
  - `_effekte_lesen(drawing)` — ``a:effectLst`` am Bild → ``fx`` (Schatten, Leuchten, Spiegelung, weiche Kanten) in den Werten des Programms.
  - `_frei(drawing, teil, inline_ok)` — Ein Bild, das frei auf dem Blatt liegt (wp:anchor ohne Textumbruch) → (Angabe, QImage); ``False``, wenn es nicht darstellbar ist
  - `_frei_maske(drawing)` — Die Zuschneideform eines Bildes (``{"maske": …}`` im Titel, „lunivo:“), sonst leer.
  - `_frei_objekt_daten(drawing)` — (Art, Daten) eines freien Objekts Form, Diagramm oder SmartArt aus dem Titel („lunivo:“) des Bildes, sonst None.
  - `_textfeld_daten(drawing, wsp)` — Die Parameter eines Textfelds (``editor/frei_objekt.py``): genau die gespeicherten aus dem Titel („lunivo:“), sonst aus dem Text des
  - `_ketten_bereinigen()` — Nach dem Lesen: Verweise auf Folgefelder, die es nicht gibt, entfernen.
  - `_add_image(drawing, cursor, cfmt)`
  - `_umbruch_seite(drawing, breite_px)` — „links“/„rechts“, wenn das Bild den Text umfließt (wrapSquare/Tight/Through); sonst leer.
  - `_eigene_vorlage(st, b)` — Eine selbst angelegte Absatzvorlage des Dokuments: der Absatz behält ihren Namen; fehlt sie im Katalog, wird sie übernommen.
  - `_zelle_format(qcell, cell)` — Zellenschattierung (w:shd) und senkrechte Ausrichtung (w:vAlign) aus der DOCX-Zelle.
  - `add_table(table)`
  - `read_page()` — Einrichtung des ERSTEN Abschnitts; weitere Abschnitte stehen als Umbrüche im Text (siehe editor/abschnitte.py).
  - `_section_page(s, erster, basis)`
  - `_hf_bilder(teil, ort, s, ps)` — Frei positionierte Bilder einer Kopf- oder Fußzeile (zum Beispiel ein Band über dem Briefkopf). „Am Absatz“ wird auf das Blatt
  - `_abschnitt_beginn(s)`
  - `_seitenschmuck(ps, sect)`
  - `_aussen_innen(s, ps)` — Gerade Seiten mit gespiegelter Ausrichtung bei gleichem Text: das ist „außen“ (ungerade rechts) bzw. „innen“ (ungerade links).
  - `_seitenzahl_art(s, ps)` — w:pgNumType: Zahlenart, „Beginnen mit“, Kapitelnummer.
  - `_hf(part)`
  - `run()`
- **class `_NoRun`** — Platzhalter, um Absatz-Standardwerte ohne Run aufzulösen.
- `_schriften_ersatz()` — Word-Schriften ohne Entsprechung im System ersetzt Qt sonst durch irgendeine breite Schrift (so wurde aus „Calibri Light“ Noto Sans).
- `read_docx(path)` — → (QTextDocument, PageSettings, meta-dict, IOReport). Wirft DocumentIOError.

### `services/docx_writer.py`

QTextDocument → DOCX (python-docx).

- `_has(fmt, prop)`
- `_rpr_einfuegen(rpr, el)` — Ein Element an ``w:rPr`` in der Reihenfolge einfügen, die das Schema verlangt.
- `absatzopt_prop()`
- **class `_Writer`**
  - `__init__(qdoc, page, meta)`
  - `_clear_body()`
  - `write_page()` — Dokumentweite Einstellungen (Hintergrund, Silbentrennung) und der letzte Abschnitt in der Schlusseinrichtung des Textes.
  - `write_section(s, p, typ, nr)` — Einen Abschnitt (python-docx Section) nach Einrichtung p schreiben; nr = Nummer des Abschnitts (für verknüpfte Kopfzeilen).
  - `_seitenzahl_art(s, p)` — Zahlenart, „Beginnen mit“ und Kapitelnummer der Seitenzahl als w:pgNumType.
  - `_abschnitt_ende(para)` — Am Ende des Absatzes, der einen Abschnitt beschließt: dessen Einrichtung als w:sectPr in den Absatz schreiben.
  - `_standard_tabstopp()` — Die Standardtabstopps des Dokuments als w:defaultTabStop (Twips) in die Einstellungen schreiben.
  - `_dokument_ebene(p)`
  - `_seitenschmuck(sect, p)`
  - `_text_with_fields(para, text)`
  - `_field(para, name)`
  - `_sprache()`
  - `write_defaults()`
  - `write_frame(frame, container)`
  - `_eigener_stil(name)` — Selbst angelegte Formatvorlage als echte Word-Absatzvorlage (Schrift, Größe, Farbe, Abstände, Ausrichtung).
  - `write_block(blk, para)`
  - `_stil(name)`
  - `_fldchar(para, typ)`
  - `_instr(para, text)`
  - `_apply_list(para, lst)`
  - `_new_num_instance(para)` — Eigene Zählung je Liste, damit „1.“ neu beginnt.
  - `write_fragment(frag, para, in_head)`
  - `_textmarken(para, namen)` — Offene Textmarken schließen, neue öffnen — je Name genau ein bookmarkStart/-End-Paar.
  - `_note_verweis(run, note)`
  - `_zusatz_anwenden(run, cf)` — Kommentarbereich merken, nachverfolgte Änderung als w:ins / w:del um den Lauf legen.
  - `_steuerelement(form, wert)` — w:sdt für ein Formularfeld: Art (Text, Liste, Datum, Kontrollkästchen), Name als Titel, unsere Daten im Tag.
  - `_make_run(parent, para)`
  - `_hyperlink(para, href, tipp)`
  - `_format_run(run, cf, in_head, is_link)`
  - `_kompatibilitaet()`
  - `_image(imf, para, seite)`
  - `_frei_bild(para, a, img)` — Ein frei positioniertes Bild (siehe editor/freie_bilder.py) als wp:anchor ohne Umbruch in den Absatz schreiben.
  - `_textfeld_ketten()` — {id des Textfelds: (Kettennummer, Stelle in der Kette)} — die Verknüpfungen aller Textfelder des Dokuments (``wps:linkedTxbx``).
  - `_textfeld_xml(run, a)` — Das Bild des Textfelds wird zur Form mit Text (``wps:wsp`` mit ``wps:txbx``/``w:txbxContent``), in „Alternativer Inhalt“ wie bei Word.
  - `_txbx_inhalt(inhalt, d)` — Absätze und Läufe des Textfelds (Text mit Zeichenformaten) als ``w:p``/``w:r`` in ``w:txbxContent``.
  - `_effekte_element(fx)` — Schatten, Leuchten, Spiegelung und weiche Kanten als ``a:effectLst`` (Längen in Punkt → EMU, Winkel in 1/60000 Grad).
  - `_verankern(run, ausrichtung)` — Macht aus dem Bild im Text (wp:inline) ein umflossenes Bild (wp:anchor, Umbruch „Quadrat“, links/rechts).
  - `write_table(qt, container)`
  - `_zelle_format(dcell, cf)` — Zellenschattierung (w:shd) und senkrechte Ausrichtung (w:vAlign) der Qt-Zelle übernehmen.
  - `run()`
  - `_kommentare_schreiben()`
  - `_komm_erweitert(kennungen)` — Teil word/commentsExtended.xml: Die Kommentare mit diesen Absatzkennungen sind gelöst (w15:done), wie Word es speichert.
  - `_quellen_schreiben()`
  - `_noten_schreiben()`
  - `_trim_trailing_empty()`
- `_split(text)`
- `_rstyle_hyperlink(d)`
- **class `_Body`**
  - `__init__(d)`
  - `add_paragraph()`
  - `add_table(r, c)`
- **class `_CellBox`**
  - `__init__(cell)`
  - `first_paragraph()`
  - `add_paragraph()`
  - `add_table(r, c)`
- `docx_daten(qdoc, page, meta)` — Baut die DOCX-Datei im Speicher. → (Inhalt, Bericht). Wirft DocumentIOError.
- `write_docx(path, qdoc, page, meta, sicherung)` — Schreibt über den sicheren Schreibweg (Temp-Datei, Prüfung, Umbenennen). Wirft DocumentIOError.

### `services/file_service.py`

Eine Stelle für alle Dateiformate: laden und speichern nach Endung.

- `endung_zum_filter(filter_text)` — Filtertext aus dem Speichern-Fenster → Endung (z. B. „OpenDocument-Text (*.odt)“ → „.odt“).
- **class `Loaded`**
- `ext(path)`
- `_verschluesselt(path)`
- `_entschluesseln(path, kennwort, ziel)`
- `load(path, kennwort)`
- `_kopf_pruefen(path, e)` — Ein falsch benanntes oder kaputtes Dokument wird als solches gemeldet, nicht „irgendwie“ geöffnet.
- `_has_rich_content(doc)`
- `save(path, doc, page, meta, sicherung)` — Speichert nach Endung über den sicheren Schreibweg (``sicher_schreiben``): Temp-Datei, Prüfung, Sicherungskopie der
- `_als_docx(path, ziel)` — DOTX (Vorlage) und DOCM (mit Makros) sind DOCX-Pakete mit anderem Inhaltstyp des Hauptteils; für den DOCX-Leser wird nur
- `_verschluesseln(data, kennwort)`

### `services/gelernt.py`

Das Gedächtnis der Prüfung: was dieser Mensch korrigiert oder stehen gelassen hat.

- **class `Gelernt`**
  - `__init__(pfad)`
  - `laden()`
  - `speichern()`
  - `wort_ebene(fund)`
  - `gewaehlt(fund)`
  - `merke_gezeigt(funde)` — Beim ausdrücklichen Prüfen: wer denselben Fund fünfmal stehen lässt, meint es so (Wort kommt in Ruhe).
  - `ki_vermerken(vorschlag, angenommen)` — Die Sicherheit (konfidenz) eines KI-Vorschlags und ob er angenommen wurde — für die Trefferquote je Sicherheitsstufe.
  - `ki_trefferquote(stufe)`
  - `vergessen()`

### `services/odt_reader.py`

ODT und FODT (OpenDocument-Text) direkt lesen — ohne Umwandlungsprogramm.

- `_q(name)`
- `_px(wert, standard)`
- `_pt(wert)`
- `_text_von(el)` — Reiner Text eines Elements samt Kindern (für Kopf- und Fußzeilen); Seitenzahl-Felder werden zu {PAGE}/{PAGES}.
- **class `_Stile`** — Vorlagen und automatische Formate mit Vererbung (style:parent-style-name) und Standardformat je Familie.
  - `__init__()`
  - `lesen(wurzel)`
  - `eigenschaften(familie, name, art)` — Aufgelöste Eigenschaften (lokale Attributnamen mit Präfix, z. B. „fo:font-weight“) aus `style:<art>-properties`.
  - `liste_von(absatz_stil)`
- `_kurz(attr)`
- `_zeichenformat(p, stile)`
- `_absatzformat(p)`
- **class `_Ort`** — Wohin der nächste Absatz kommt: ein Cursor und ob dessen Block noch leer und frei ist.
  - `__init__(cur, frei)`
- **class `_Leser`**
  - `__init__(inhalt, stil_wurzel, meta, bilder)`
  - `absatz(el, ort, liste)`
  - `inline(el, cur, eltern)`
  - `_bild_laden(bild)`
  - `_frei_angabe(frame)` — Ein Rahmen am Absatz oder an der Seite, den kein Text umfließt → Angabe wie in editor/freie_bilder.py, sonst None.
  - `rahmen(frame, cur)`
  - `listenpunkt(cur, listen, stil, ebene)`
  - `_listenart(stil, ebene)`
  - `liste(el, ort, listen, stil, ebene)`
  - `tabelle(el, ort)`
  - `bereich(kinder, ort)`
  - `seite()`
  - `_kopf_fuss(el)`
  - `run()`
- `_xml(daten)`
- `read_odt(path)` — → (QTextDocument, PageSettings, meta-dict, IOReport). Wirft DocumentIOError.
- `read_fodt(path)` — Flaches ODT (eine XML-Datei).

### `services/odt_writer.py`

ODT (OpenDocument-Text) direkt schreiben — ohne Umwandlungsprogramm.

- `_mm(wert)`
- `_absatz(hf, stil, rahmen)` — Kopf-/Fußzeilentext als ODF-Absätze; {PAGE} und {PAGES} werden zu Feldern. ``rahmen`` (frei positionierte Bilder) hängt am
- `_styles_xml(page, doc, bilder)`
- `_standard(doc)` — Standardschrift des Dokuments als Vorgabe für alle Absätze, dazu die Vorlage „Standard“.
- `_manifest(namen)`
- `bild_aus_format(doc, cf)` — Das Bild hinter einem Bildformat (Ressource im Dokument oder Datei), sonst None.
- `spannweite(t, r, c)` — Wie viele Spalten und Zeilen die Zelle mit Ursprung (r, c) überdeckt (gezählt, nicht columnSpan(): das liefert für
- `_png(img)`
- `_odf(element, attr, inhalt)` — Ein Element des ODF-Tabellenmodells (Namensraum ``table:``) als XML-Text.
- `_laenge(px)`
- `_frei_stil(name, a)` — Rahmenvorlage (Familie „graphic“) für ein frei positioniertes Bild: ohne Textumfluss, vor oder hinter dem Text.
- `_frei_rahmen(a, img, nr, stil, bilder)` — Ein frei positioniertes Bild als draw:frame am Absatz; die Bilddaten kommen nach ``bilder`` (Pictures/…).
- **class `_Inhalt`** — Baut content.xml aus dem QTextDocument: Absätze, Überschriften, Zeichenformat, Listen, Tabellen, Bilder.
  - `__init__(doc, rep)`
  - `_absatz_stil(bf)`
  - `_text_stil(cf)`
  - `_listen_stil(liste)`
  - `_text(s)`
  - `_bild(cf)`
  - `_freie_bilder(bf)`
  - `absatz(block)`
  - `tabelle(t)`
  - `_rahmen_inhalt(it)`
  - `xml()`
- `_meta_xml(meta)`
- `odt_daten(doc, page, meta)` — Baut die ODT-Datei im Speicher. → (Inhalt, Bericht über nicht Übernommenes).
- `_verluste_melden(rep, page, meta, fmt)` — Was der direkte ODT-/RTF-Weg nicht mitnimmt — damit nichts still verloren geht.

### `services/pdf_export.py`

PDF exportieren nach der Wahl im Fenster „PDF-Datei exportieren“: Seitenbereich, Exportoptionen, Berechtigungen und Kennwörter.

- **class `PdfWahl`**
- `seiten(wahl, aktuelle)` — (erste, letzte) Seite für ``export_pdf``; ``None`` = bis zum Ende.
- `lesezeichen(wahl)`
- `nur_markierung(qdoc, anfang, ende)` — Eine Kopie des Dokuments, in der nur der markierte Teil steht (Bilder und Formate bleiben, das Original bleibt unberührt).
- `berechtigungen(wahl)` — Die Rechte als PDF-Bits (ISO 32000, Tabelle 22).
- `kennwort_fehler(wahl, bestaetigt_rechte, bestaetigt_oeffnen)` — Leer, wenn die Kennwörter passen; sonst der Hinweis für das Fenster.
- `verschluesseln(pfad, wahl)` — Die fertige PDF an Ort und Stelle verschlüsseln. Ohne Kennwort für die Berechtigungen gilt das Kennwort zum Öffnen auch dafür.

### `services/recovery.py`

Automatische Wiederherstellung.

- `recovery_dir()`
- **class `RecoveryEntry`**
  - `meta_path()`
- `new_token()`
- `paths(token)`
- `write_meta(token, original, title)`
- `discard(token)`
- `pending(exclude)`
- `zwischenstand(token, title, tage)` — Legt eine Kopie der Sicherung unter staende/ ab und löscht Kopien, die älter als `tage` sind.

### `services/rtf_reader.py`

RTF direkt lesen — ohne Umwandlungsprogramm.

- **class `_Absatz`**
  - `__init__(props, laeufe, liste)`
- **class `_Tabelle`**
  - `__init__()`
- **class `_Ziel`** — Sammelt Absätze und Tabellen — für den Haupttext und je Kopf-/Fußzeile.
  - `__init__(haupt)`
  - `text(s, zeichen)`
  - `absatz(absatz)`
  - `zelle_ende(absatz)`
  - `reihe_ende(cellx)`
  - `abschliessen(absatz)`
- **class `_Zerleger`**
  - `__init__(daten)`
  - `run()`
  - `_ziel_beginnen(g, w, z)`
  - `_gruppe_ende(g)`
  - `_text(g, s)`
  - `_steuer(g, w, z, neu)`
  - `_bild_wort(b, w, z)`
  - `_bild_fertig(b, g)`
  - `zeichenformat(schl)`
  - `_farbe(i)`
- `_ersatzpaar(g, wert)` — Hälften eines UTF-16-Ersatzpaars (\u-Paar für Zeichen außerhalb der BMP) zusammensetzen.
- `_absatzformat(a)`
- **class `_Bauer`**
  - `__init__(z, doc)`
  - `absatz(a, cur, frei, liste_vorher)`
  - `teile(teile, cur)`
- `_kopf_fuss_text(ziel, z)`
- `read_rtf(path)` — → (QTextDocument, PageSettings, meta-dict, IOReport). Wirft DocumentIOError.

### `services/rtf_writer.py`

RTF direkt schreiben — ohne Umwandlungsprogramm.

- `_mm(wert)`
- `_px(wert)`
- `_text(s)` — Text RTF-sicher: Steuerzeichen maskiert, alles außerhalb von ASCII als \uN? (UTF-16, mit Ersatzpaaren).
- **class `_Rtf`**
  - `__init__(doc, page)`
  - `_warn(text)`
  - `schrift(name)`
  - `farbe(c)`
  - `zeichen(cf)`
  - `bild(cf)`
  - `absatz(block, in_tabelle)`
  - `tabelle(t)`
  - `rahmen(frame)`
  - `kopf_fuss(art, hf, seite)` — ``seite`` 2 für die Kopf-/Fußzeile linker (gerader) Seiten: „außen“/„innen“ werden dort gespiegelt.
  - `run()`
- `_bloecke(frame)`
- `rtf_daten(doc, page, meta)` — Baut die RTF-Datei im Speicher. → (Inhalt, Bericht über nicht Übernommenes).

### `services/settings_service.py`

Einstellungen und Pfade (XDG, über QStandardPaths). Nichts liegt im Programmordner.

- `data_dir()`
- **class `Settings`** — Dünne Hülle um QSettings mit festen Schlüsseln und Vorgaben.
  - `__init__(qsettings)`
  - `get(key, default)`
  - `set(key, value)`
  - `remove(key)`
  - `get_bool(key, default)`
  - `get_int(key, default)`
  - `recent()`
  - `add_recent(path)`
  - `remove_recent(path)`
  - `clear_recent()`

### `services/sicher_schreiben.py`

Ein sicherer Schreibweg für alle Dokumentdateien (DOCX, ODT, DOC, RTF, TXT, PDF).

- `ziel(path)` — Tatsächliche Zieldatei: Verknüpfungen werden aufgelöst, damit die Verknüpfung erhalten bleibt.
- `stand(path)` — (Änderungszeit in ns, Größe) der Datei oder None — zum Erkennen fremder Änderungen.
- `fremd_geoeffnet(path)` — Beschreibung des Programms, das die Datei laut Sperrdatei offen hat (LibreOffice legt „.~lock.<name>#“ an), sonst None.
- `fehlertext(e, path, vorhanden)` — Verständliche Meldung für einen Fehler beim Schreiben.
- `_umask()`
- `_fsync_datei(path)`
- `_fsync_ordner(ordner)`
- `_rest_muster(real)`
- `_reste_aufraeumen(real)` — Entfernt eigene Temp-Reste früherer, abgebrochener Speichervorgänge derselben Datei.
- `_sperr_ordner()`
- `sperre(path)` — Verhindert, dass dieselbe Datei gleichzeitig zweimal gespeichert wird (im Programm und zwischen Lunivo-Fenstern).
- `sicherungs_ordner()`
- `_dokument_ordner(real)`
- `sicherungskopie(real)` — Kopiert die bisherige Fassung in den Sicherungsordner und räumt alte Kopien weg. → Pfad der Kopie.
- `sicherungen(path)` — Sicherungskopien einer Datei, neueste zuerst.
- `sicherungen_aufraeumen(nur_ordner)` — Hält je Dokument höchstens SICHERUNGEN_JE_DOKUMENT Kopien und entfernt Kopien älter als SICHERUNG_TAGE.
- `_defekt(grund)`
- `_zip_pruefen(path, pflicht)`
- `pruefe_format(path, endung)` — Strukturprüfung der geschriebenen Datei. Wirft DocumentIOError, wenn sie nicht vollständig oder nicht gültig ist.
- `schreiben(path, erzeugen, *, endung, sicherung)` — Schreibt eine Datei sicher: `erzeugen(temp_pfad)` legt die neue Fassung an, der Rest geschieht hier.
- `bytes_schreiben(path, daten, *, endung, sicherung)`

### `services/vorlesen.py`

Vorlesen: Piper (offline, gute Stimme) wenn eingerichtet, sonst speech-dispatcher (spd-say).

- **class `VorlesenFehler`**(Exception)
- `piper_programm()`
- `piper_stimmen()`
- `_abspieler()`
- `piper_da()`
- `spd_da()`
- `verfuegbar()`
- `tempo_piper(tempo)`
- `stimmen()` — Alle wählbaren Stimmen: zuerst Piper, dann die deutschen des Sprachdienstes.
- `beenden()`
- `lies_vor(text, stimme, tempo)`

## `services/integrations`

### `services/integrations/__init__.py`

Optionale Anbindungen: LanguageTool, WPS.


### `services/integrations/languagetool.py`

LanguageTool als zweite Meinung (eigener Java-Prozess, nur auf diesem Rechner, 127.0.0.1).

- **class `LanguageToolFehler`**(Exception)
- `ordner()`
- `laeuft(port)`
- `jar_finden()`
- `verfuegbar(port)`
- `starten(port, warte_s)`
- `pruefe(text, sprache, port)` — → Funde im selben Format wie die eigene Prüfung (von, bis, alt, neu, grund, art).
- `beenden()`

### `services/integrations/wps.py`

WPS Office — nur die ehrliche Stufe: ein installiertes Programm aufrufen.

- `finde_wps()`
- `verfuegbar()`
- `oeffnen(pfad)` — Öffnet die Datei in WPS Writer (eigener Prozess). False, wenn WPS nicht installiert ist.

## `ui`

### `ui/__init__.py`

Oberfläche (Qt-Widgets): Hauptfenster, Menüband, Dokumentbereich, Seitenleiste, Dialoge.


### `ui/backstage.py`

Backstage-Ansicht des Reiters „Datei“: links die Befehlsliste, rechts die Seite zum gewählten Befehl (wie in ONLYOFFICE).

- `symbol(name, px)`
- **class `_Zeile`**(QStyledItemDelegate) — Zeichnet die Trennlinien quer über die Liste und den kleinen Pfeil rechts bei Einträgen mit eigener Seite.
  - `paint(p, opt, idx)`
- **class `Backstage`**(QWidget)
  - `__init__(fenster)`
  - `oeffnen(seite, unter)` — ``unter``: bei „optionen“ die Seite der Optionen, die gleich offen sein soll (z. B. „ki“).
  - `optionen_seite()` — Schlüssel der Optionenseite, die gerade offen ist (z. B. „ansicht“).
  - `_optionen()` — Platzhalter: die Optionen werden erst gebaut, wenn die Seite zum ersten Mal gezeigt wird.
  - `_optionen_zeigen()`
  - `_zeigen(schl)`
  - `_gewaehlt(it)`
  - `_speicherort()`
  - `_seite(titel)`
  - `_gruppe(v, text, hinweis)`
  - `_knopf(v, text, befehl, icon, schliessen, datei)`
  - `_zuletzt()` — Rechts neben dem Menü: die zuletzt verwendeten Dateien (Name, Ordner, Datum; ✕ nimmt sie aus der Liste).
  - `_speichern_als()`
  - `_vorlage()` — Platzhalter: die Galerie mit den Vorschauen wird erst gebaut, wenn die Seite gezeigt wird.
  - `_vorlage_zeigen()`
  - `_drucken()` — Platzhalter: das Druckfenster samt Vorschau wird erst gebaut, wenn die Seite gezeigt wird.
  - `_pdf()` — Platzhalter für den eingebetteten PDF-Export, frisch je Öffnen des Datei-Menüs.
  - `_pdf_zeigen()`
  - `_bild()` — Platzhalter für den Bildexport in der rechten Menüspalte.
  - `_bild_zeigen()`
  - `_drucken_zeigen()`
  - `_hilfe()`
  - `_schuetzen()`
  - `_info()`
  - `_meta_setzen(t, schl, wert)`
  - `_zeile(v, name, feld)`
  - `_oeffnen_mit()`

### `ui/kuerzel.py`

Tastenkürzel — eine Tabelle für die Hilfe und für die Kürzel, die nicht an einer Aktion des Fensters hängen.

- `als_markdown()` — Die Tabelle als Markdown — das zeigt der Hilfe-Dialog über ``QTextBrowser.setMarkdown``.

### `ui/lesestufen.py`

Die drei Lesestufen der Lesehilfe — gemeinsam für die Optionen und die rechte Seitenleiste.

- `aktuell(s)` — Name der Stufe, auf der die Einstellungen gerade stehen, oder „“ (eigene Einstellung).
- `setze(s, name)` — Schreibt die Werte der Stufe in die Einstellungen (angewendet wird mit ``MainWindow.lesehilfe_anwenden``).

### `ui/main_window.py`

Hauptfenster: Menüleiste, Schnellzugriff, Ribbon, Dokumentreiter, Statusleiste.

- **class `MainWindow`**(DateienBaustein, BearbeitenBaustein, OberflaecheBaustein, BackstageBaustein, QMainWindow)
  - `__init__(settings)`
  - `_act(text, slot, shortcut, checkable, tip, symbol)`
  - `_build_actions()`
  - `_build_menu()`
  - `_fill_recent()`
  - `_clear_recent()`
  - `_build_status()`
  - `current_tab()`
  - `current_editor()`
  - `_ed(fn)`
  - `_doc_tabs()`
  - `_tab_title(tab)`
  - `_update_tab_titles()`
  - `_update_window_title()`
  - `_tab_changed(_i)`
  - `_refresh_ui()`
  - `_regler_bewegt(v)`
  - `_zoom_anzeigen(f)`
  - `_connect_tab(tab)`
  - `_sync_later()`
  - `_sync_format()`
  - `_sync_status()`
  - `_verbinde_felder()`
  - `stil_anwenden(name)`
  - `_size_chosen(*_)`
  - `alle_fenster()`
  - `neues_fenster()` — Das aktuelle Dokument in einem zweiten Fenster öffnen (eigene Kopie, keine Synchronisation).
  - `fenster_anordnen(art)`
  - `fensterliste_menue()`
  - `closeEvent(ev)`
  - `word_count()` — Wörter zählen (Fenster wie Überprüfen ▸ Wörter zählen).
  - `show_info()`
  - `show_options(seite)` — Die Optionen stehen in der Datei-Ansicht („☰ Menü ▸ Optionen“); ohne Register-Band als Fenster.
  - `toggle_fullscreen(on)`
  - `about()`

### `ui/schreibhilfe_katalog.py`

Alle Funktionen der Schreibhilfe an einer Stelle: Wo sie in der Seitenleiste („Werkbank“) und im Band stehen und welcher Befehl dahinter hängt.

- **class `Funktion`**
- `fuer_reiter(reiter)`
- `fuer_gruppe(gruppe)`

### `ui/theme.py`

Hell/Dunkel über Qt-Paletten (Stil „Fusion“) — keine Stylesheets für das Grundlayout.

- `apply_theme(app, mode)`
- `_ist_dunkel(app)`
- `_pfeile(farbe)` — Dropdown-Pfeile aus dem zentralen Lucide-Katalog für Qt-Stylesheets.
- `_kreuz(farbe)`
- `_stil(app)`
- `_setze(app, mode)`
- `_helle_palette()` — Feste helle Grundpalette (wie Fusion hell), unabhängig von der Palette des Plattformdesigns.
- `_hell_feinschliff(app)` — Helle Palette: Fläche um das Blatt; mit „Weichem Kontrast“ warme Töne.
- `Qt_white()`

## `ui/baukasten`

### `ui/baukasten/__init__.py`

Wiederverwendbare Bausteine der Oberfläche — Farben, Linien, Menüs, Raster, Maße, Dialoggerüst.


### `ui/baukasten/absatz_dialog.py`

Das Fenster „Absatz“ (Einzüge und Abstände, Zeilen- und Seitenumbruch) als Baustein.

- `aus_block(bf)` — Die Werte eines Absatzformats für das Fenster (Gegenstück zu ``werte()``): Einzüge in mm, Abstände in pt, Zeilenabstand.
- **class `AbsatzDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, werte, *, umfang)`
  - `setze(w)`
  - `_zeilenart(*_)`
  - `_neu()`
  - `werte()`
  - `_opt()`
  - `_tabstopps()`
  - `_male(p, rect)` — Vorhergehender Absatz (grau), der eigene mit Einzügen und Abständen, folgender Absatz (grau).

### `ui/baukasten/aktionen_leiste.py`

„Meine Aktionen“: die Schnellen KI-Aktionen (Eigene Assistenten) als Knöpfe — in der Seitenleiste der Schreibhilfe und im KI-Chat dieselbe Leiste.

- **class `AktionenLeiste`**(QWidget)
  - `__init__()`
  - `verbinde(dienst, fenster)`
  - `fuellen()` — Die Knöpfe neu aufbauen: je Aktion einer, dazu „＋ Neue Aktion“.
  - `zustand()` — Die Aktionen laufen nur mit verbundenem Modell und nicht, solange die KI schon arbeitet; „Neue Aktion“ geht immer.

### `ui/baukasten/auswahl_bereich.py`

Der Bereich „Auswahl“ (Start ▸ Auswählen ▸ Auswahlbereich) als Baustein: alle Bilder, Formen, Diagramme und Tabellen des Dokuments in einer

- `objekte(ed)` — [(Beschriftung, von, bis)] aller Objekte in Dokumentreihenfolge.
- **class `AuswahlBereich`**(PanelFaehig, QDialog)
  - `__init__(parent, ed)`
  - `fuellen()`
  - `_markieren(it)`

### `ui/baukasten/beschriftung.py`

Beschriftungen ohne Auszeichnungssprache: Text mit Schrifteigenschaften oder Markdown (`Qt.MarkdownText`).

- `md_escape(text)` — Sonderzeichen eines Textes für Markdown unschädlich machen (z. B. wenn er in `**…**` eingebettet wird).
- `text_label(text, *, fett, pt, durchgestrichen, umbruch, auswaehlbar)` — Beschriftung aus reinem Text; Zeilenumbrüche des Textes bleiben erhalten.
- `md_label(markdown, *, umbruch)` — Beschriftung aus Markdown (fett, durchgestrichen, Absätze) — Qt zeigt es selbst an.

### `ui/baukasten/bild_diagramm_menues.py`

Menüs und Galerien der Reiter „Bildtools“ und „Diagrammtools“ (nur Aussehen; jede Wahl ruft einen Befehl des Bandes).

- `_form_bild(name)`
- `_skala_bild(b, h)`
- `_abschnittsleiste(text)`
- `zuschneiden_menue(b)` — Die Klappe „Zuschneiden“ nach der Vorlage; ``b`` ist der Befehlsbaustein (``bildZuschneidenForm/Skala/Zuruecksetzen``).
- `stil_bild(nr, groesse)` — Vorschau des Diagrammstils ``nr`` (``diagramm.STILE``): Grund, Raster und Schrift wie im fertigen Diagramm, mit drei Säulenreihen.
- `_stilname(nr)`
- `diagramm_stile_menue(b)` — Alle Diagrammstile als Kacheln (Name im Tipp); die Wahl ist ``diagrammStil``.
- `diagramm_stile_galerie(b)` — Die Galerie im Band: eine Kachel je Stil und das Menü mit allen (Aufbau wie ``galerie_ttFormstile``).

### `ui/baukasten/bild_export.py`

„Als Bild exportieren“: die Bildlayoutkarten und Einstellungen in der rechten Spalte des Datei-Menüs.

- **class `_Karte`**(QAbstractButton) — Eine wählbare Karte mit Bildchen und Beschriftung; gewählt mit blauem Rand und Haken in der Ecke.
  - `__init__(text, lang)`
  - `sizeHint()`
  - `paintEvent(_e)`
  - `_bildchen(p, dunkel)`
- **class `BildExportAnsicht`**(QWidget) — Bildexport als Seite in der zweiten Spalte des Datei-Menüs.
  - `__init__(parent, startordner, dpi, exportieren, zurueck)`
  - `_ordner_waehlen()`
  - `_exportieren()`
  - `_erstes_bild_oeffnen()`
  - `_zielordner_oeffnen()`
- `_abschnitt(titel, hilfe, layout)`
- `_bilder_ordner()`

### `ui/baukasten/bild_zoom.py`

Das Fenster „Vergrößern“ (Lupe in der Schnellleiste am Bild): das Bild in seiner Auflösung ansehen, mit Regler und Mausrad zoomen.

- **class `_Ansicht`**(QScrollArea) — Rollbereich, dessen Mausrad (mit oder ohne Strg) den Zoom ändert.
  - `__init__(bei_zoom)`
  - `wheelEvent(e)`
- **class `BildZoomFenster`**(PanelFaehig, QDialog)
  - `__init__(parent, bild, titel)`
  - `aktualisieren(_w)` — Das Bild im gewählten Maßstab zeigen.

### `ui/baukasten/datei_symbole.py`

Lokale, vollständige Dateityp-Symbole aus der zentralen Iconsammlung.

- `icon_namen(name)` — Liefert den passenden lokalen Dateityp und den generischen Rückfall.
- `datei_symbol(name)` — Rendert ein vollständiges farbiges Dateiblatt aus einem gebündelten SVG.

### `ui/baukasten/design_bildchen.py`

Bildchen für die Galerien Designs, Farben, Schriftarten und Effekte (Reiter Seitenlayout). Jede Funktion gibt einen Zeichner

- `_text(p, r, text, familie, px, ausr, fett, farbe)`
- `design_zeichner(farben, kopf)` — Weiße Karte mit „Aa“ in der Überschriftschrift und den sechs Akzentfarben als Band.
- `farbreihe_zeichner(farben, name)` — Eine Zeile der Liste „Farben“: acht Farbfelder, rechts daneben der Name.
- `schriftpaar_zeichner(name, kopf, text)` — Eine Zeile der Liste „Schriftarten“: Kästchen „Aa“, darüber der Name, dann die Überschrift- und die Textschrift in sich selbst.
- `effekt_zeichner(fx)` — Blauer Blockpfeil auf hellem Feld, mit dem Effekt gezeichnet (wie er an Formen erscheint).

### `ui/baukasten/diagramm_format_panel.py`

„Formatierung“ für einen Teil des Diagramms in der rechten Seitenleiste (nach der Vorlage).

- `_optionen_name(teil)`
- `_text_teil(teil)`
- `_combo(eintraege)`
- `_still(x, wert, setter)`
- **class `_AutoWert`**(QWidget) — Eine Zahl, die „Automatisch“ sein kann (Minimum, Maximum, Hauptintervall der Achse): Haken + Feld. ``wert()`` ist None bei Automatisch.
  - `__init__(vorgabe)`
  - `wert()`
  - `setze(w)`
- **class `DiagrammTextPanel`**(_TextPanel) — Textfüllung und -kontur, Effekte (wie bei den Texteffekten) und „Textfeld“. ``werte()`` ist das Textformat des Teils (``diagramm_format``: ``text``).
  - `__init__(parent, werte)`
  - `_setze(w)`
  - `werte()`
- **class `DiagrammFormatPanel`**(ObjektFormatPanel)
  - `__init__(parent, werte)`
  - `_zusatz_radios(abschnitt)`
  - `_zusatz_felder(abschnitt, a)`
  - `_bild_waehlen()`
  - `fuellung_waehlen(art)`
  - `_farbe_waehlen()`
  - `_linie_waehlen()`
  - `_seite_fuellung(w)`
  - `_seite_optionen()`
  - `_achse_melden()`
  - `_reihe_melden()`
  - `_seite_eigenschaften()`
  - `_groesse_melden(hoehe)`
  - `_alt_start()`
  - `_melde(**kw)`
  - `_melden()`
  - `werte()` — Füllung, Linie und Effekte im Format des Teilformats (``None`` = entfernen).
  - `_fuell_wert()`
  - `_linie_wert()`
  - `_setze(w)`
  - `_setze_fuellung(w)`
  - `setze(werte)` — Die Felder mit dem Format des Teils füllen; meldet nichts.
  - `_teile_zeigen(werte)` — Die Liste „Teil“ mit den Teilen des Diagramms (``werte["teile"]``, sonst nur der gewählte) und dem gewählten Eintrag.
  - `_teil_einrichten(werte)`
  - `_setze_optionen(werte, f)`

### `ui/baukasten/diagramm_popups.py`

Popups der Schnellleiste am Diagramm und die Klappen der Diagrammtools — ein Baustein, damit Band und Schnellleiste dasselbe zeigen.

- `_dg(b)`
- `_kopfknopf(text, i, gruppe)`
- `_linie()`
- `_ueberschrift(text)`
- `layout_bild(nr, groesse)` — Schematisches Bild von „Layout 1 bis 6“: Titel oben, Legende (Lage), Datenbeschriftungen (Punkte auf den Säulen).
- `_farbzeile(farben, gewaehlt, klick)`
- **class `DiagrammPopup`**(QMenu) — Ein Popup mit Reitern; ``art``: ``elemente``, ``stile`` oder ``filter``; ``reiter``: der zuerst gezeigte Reiter.
  - `__init__(b, art, reiter, parent)`
  - `waehle(i)`
  - `neu_lesen()` — Beim Öffnen: den Reiter zeigen, den der Aufrufer wollte, mit frisch gelesenen Daten.
  - `_fuellen(i)`
  - `_seite_elemente()`
  - `_seite_schnelllayout()`
  - `_seite_vorlagen()`
  - `_seite_farben()`
  - `_seite_filter()`
  - `_seite_namen()` — Reiter „Name“: Reihen und Rubriken umbenennen; „Übernehmen“ schreibt über ``diagrammNamenSetzen`` in die Diagrammdaten.
  - `_namen_uebernehmen()`
  - `_hoehe()`
  - `_uebernehmen()`
- `elemente_popup(b)`
- `schnelllayout_popup(b)`
- `stile_popup(b)`
- `farben_popup(b)`
- `filter_popup(b)`
- `diagramm_bereich_feld(b)` — Auswahlfeld „Diagrammbereich“ der Diagrammtools: oben die Liste der Teile (zeigt den gewählten), darunter „Formatieren“ und

### `ui/baukasten/dialog_rahmen.py`

Grundgerüst für kleine Dialoge: Formular, optionale Vorschau, OK/Abbrechen und Zusatzknöpfe wie „Entfernen“.

- **class `_KnopfLayout`**(QLayout) — Zusatzknöpfe links, „Abbrechen“ und „OK“ rechts — in einer Zeile, wenn sie nebeneinander passen; sonst stehen die Zusatzknöpfe (umbrechend) darüber.
  - `__init__()`
  - `extra(widget)`
  - `haupt(widget)`
  - `addItem(item)`
  - `count()`
  - `itemAt(i)`
  - `takeAt(i)`
  - `hasHeightForWidth()`
  - `sizeHint()`
  - `minimumSize()`
  - `heightForWidth(w)`
  - `setGeometry(r)`
  - `_plan(w)`
- **class `Knopfzeile`**(QWidget) — Die Knopfzeile unten in jedem Fenster — der einzige Ort, der sie baut: links Zusatzknöpfe, rechts „Abbrechen“ und „OK“ (gleich breit).
  - `__init__(dialog, *links, bei_ok, ok_text, abbrechen_text, nur_ok, schliessen)`
  - `zusatz_knopf(k)`
  - `zusatz(text, aktion, *, schliesst)` — Knopf neben OK/Abbrechen (z. B. „Entfernen“); ``schliesst`` beendet das Fenster mit OK.
- `knopfzeile(dialog, *links, **kw)` — Eine Knopfzeile für ``dialog`` (zum Einsetzen in ein Layout); Wahlmöglichkeiten wie bei ``Knopfzeile``.
- `fussleiste(dialog, layout, *links, bei_ok, ok_text, abbrechen_text, nur_ok)` — Knopfzeile unten ins ``layout`` setzen. Gibt den OK-Knopf zurück (``bei_ok`` ersetzt ``accept``, z. B. zum Prüfen vor dem Schließen).
- `_symbol(art)` — Lucide-Symbol für Abbrechen oder Bestätigen.
- **class `VorschauFlaeche`**(QWidget) — Weißes Blatt, auf das der Dialog mit ``zeichne(painter, rect)`` seine Vorschau malt.
  - `__init__(zeichne, hoehe, flaeche)` — ``flaeche=False``: kein weißes Feld mit Rand; ``zeichne`` malt direkt auf den Fensterhintergrund (z. B. ein einzelnes Blatt).
  - `paintEvent(e)`
- **class `DialogRahmen`**(QDialog) — Unterklassen füllen ``self.form`` (``zeile(...)``) und liefern ``ergebnis()``. Wer sich ändert, ruft ``aktualisieren()``.
  - `__init__(parent, titel, vorschau)`
  - `zeile(beschriftung, widget)`
  - `zusatzknopf(text, aktion, *, schliesst)` — Knopf neben OK/Abbrechen (z. B. „Entfernen“); ``schliesst`` beendet den Dialog mit OK.
  - `aktualisieren(*_)`
  - `ergebnis()`

### `ui/baukasten/druck_dialog.py`

Das Druckfenster: links die Vorschau des Blattes, rechts die Reiter „Standard“, „Lunivo-Office“ und „Drucker“.

- `_kopf(text)`
- `_drucker_liste()`
- `_combo(eintraege, aktuell)`
- **class `DruckAnsicht`**(QWidget) — Vorschau links, Reiter rechts. ``geaendert`` kommt bei jeder Änderung der Wahl.
  - `__init__(seiten, papier_mm, quer, start, *, auswahl, vorschau, parent)`
  - `_standard(s, hoch, quer, auswahl)`
  - `_papier_combo(aktuell)`
  - `_programm(s)`
  - `_druckerseite(s)`
  - `_verdrahten()`
  - `_gleich(von, nach)`
  - `_drucker_gewaehlt(*_)`
  - `drucker_setzen(kopien, beidseitig)` — Nach den Einstellungen des Systems: Kopien und Beidseitig übernehmen.
  - `ergebnis()`
  - `gueltig()` — Ein eigener Seitenbereich muss mindestens eine Seite treffen.
  - `_blatt_mm()`
  - `_blaetter()`
  - `_aenderung()`
  - `_gehe(i)`
  - `_neu_laden()`
  - `_zeichnen(p, r)`
- **class `DruckDialog`**(QDialog) — Das Druckfenster mit Knopfzeile: Hilfe links, „Abbrechen“ und „Drucken“ rechts.
  - `__init__(parent, seiten, papier_mm, quer, start, *, auswahl, vorschau, hilfe)`
  - `_pruefen()`
  - `ergebnis()`

### `ui/baukasten/druckvorschau.py`

Die Druckvorschau als ganzes Fenster: oben Drucken…, Blattwechsel, Ansicht (Eine/Zwei/Alle Seiten), Zoom, Einpassen, Vorschau schließen.

- **class `DruckVorschau`**(QDialog)
  - `__init__(parent, quelle)`
  - `_zoomknopf(text, tip, faktor)`
  - `_schritt()`
  - `showEvent(e)`
  - `einpassen()` — Zoom, bei dem die Seiten der Ansicht ganz ins Fenster passen (bei „Alle Seiten“ die Breite einer Seite).
  - `_zoom_setzen(z)`
  - `_gehe(n)`
  - `_aufbauen()`

### `ui/baukasten/eingabe_fenster.py`

Kleine Abfrage in der Seitenleiste: eine Frage, darunter eine Auswahl oder ein Textfeld, unten „Abbrechen“ und „OK“.

- **class `EingabeFenster`**(PanelFaehig, QDialog) — Frage mit Auswahlliste (``eintraege``) oder, ohne Einträge, mit einem Textfeld.
  - `__init__(parent, titel, frage, eintraege, aktuell, text, kennwort, mehrzeilig, datum)`
  - `wert()` — Der gewählte Eintrag oder der getippte Text.
  - `getItem(parent, titel, frage, eintraege, aktuell, bearbeitbar)` — Wie ``QInputDialog.getItem``; (``bearbeitbar`` gibt es nicht — Auswahl nur aus der Liste).
  - `getText(parent, titel, frage, text, kennwort)` — Wie ``QInputDialog.getText``; ``kennwort=True`` zeigt Punkte statt der Zeichen.
  - `getMultiLineText(parent, titel, frage, text)` — Wie ``QInputDialog.getMultiLineText``.
  - `getDatum(parent, titel, frage, datum)` — Ein Datum aus dem Kalender wählen; Rückgabe ``(QDate, ok)``.

### `ui/baukasten/einklappgruppe.py`

Eingeklappte Gruppe („Weitere Einstellungen“): ein Knopf mit Pfeil, darunter der Inhalt, der erst auf Wunsch aufgeht.

- **class `EinklappGruppe`**(QWidget) — Knopf plus Inhalt. Der Inhalt kommt in ``innen`` (ein ``QVBoxLayout``).
  - `__init__(titel, parent)`
  - `_zeigen(offen)`
  - `ausklappen(offen)`
  - `ist_offen()`

### `ui/baukasten/farben.py`

Farbdaten für jede Palette im Programm: Themenfarben mit Abstufungen, Standardfarben, zuletzt benutzte.

- `mische(a, b, anteil)` — Mischt Farbe a zum Anteil (0…1) mit Farbe b.
- `abstufungen(farbe)` — Fünf Abstufungen einer Themenfarbe, von hell nach dunkel (Weiß geht nur nach Grau, Schwarz nur nach Grau).
- `thema_raster()` — Zeilen der Themenfarben: erst die Grundfarben, darunter die fünf Abstufungen.
- `zuletzt_laden()`
- `zuletzt_merken(farbe)`

### `ui/baukasten/farbpalette.py`

Die eine Farbpalette des Programms: Popup, Farbfeld für Dialoge und geteilter Knopf fürs Band.

- `weitere_farben(parent, start, titel)` — „Weitere Farben …“: das Fenster „Farben“ (Standard · Benutzerdefiniert · Erweitert). Gibt die Farbe zurück oder ``None`` bei Abbruch.
- `weitere_farben_unter(parent, fertig, start, titel)` — Wie ``weitere_farben``, aber als Unterfenster: Liegt ``parent`` in einem ``FensterStapel``, öffnet sich „Farben“ als Seite im selben Fenster;
- `farb_symbol(farbe, groesse)`
- **class `_Kachel`**(QWidget) — Ein Farbfeld der Palette; meldet Überfahren und Klick an die Palette.
  - `__init__(palette, farbe, seite)`
  - `enterEvent(e)`
  - `leaveEvent(e)`
  - `mouseReleaseEvent(e)`
  - `paintEvent(e)`
- **class `_VerlaufKachel`**(_Kachel) — Kachel der Zeile „Graduelle Füllung“: ein Farbverlauf von hell nach dunkel in der Farbe; ein Klick meldet die Farbe als Verlauf.
  - `mouseReleaseEvent(e)`
  - `paintEvent(e)`
- **class `FarbPalette`**(QMenu) — Popup mit „Keine Farbe“, Themenfarben (Grundfarben + Abstufungen), Standardfarben, zuletzt Benutzten, „Weitere Farben …“.
  - `__init__(parent, *, keine_text, start, titel, zuletzt, weitere, verlauf, verlauf_titel, weitere_text, automatisch, pipette, standard)`
  - `zusatz_eintrag(text, aktion)` — Ein weiterer Eintrag unter „Weitere Farben …“ (z. B. „Rahmen und Schattierung …“); schließt die Palette und ruft ``aktion``.
  - `_titel_zeile(text)`
  - `_keine_symbol()`
  - `_raster(zeilen)`
  - `waehle(farbe)` — Farbe übernehmen: merken, melden, Popup schließen.
  - `_pipette()` — „Pipette“: eine Farbe vom Bildschirm aufnehmen.
  - `_weitere()`
- **class `FarbFeld`**(QPushButton) — Knopf für Dialoge, der seine Farbe zeigt; ein Klick öffnet die Palette. ``farbe`` ist ein Hex-Text ('' = keine).
  - `__init__(farbe, titel, keine_text, parent, verlauf)`
  - `setFarbe(farbe)`
  - `_waehle()`
  - `_zeige_popup(pal)`
  - `_uebernehmen(c)`
  - `_zeige()` — Ruhig und sachlich: ein kleines Farbfeld mit Rand und der Name daneben — kein Knopf, der selbst bunt wird.
- **class `FarbKnopf`**(QToolButton) — Geteilter Knopf fürs Band: Klick auf das Symbol wendet die letzte Farbe an, der Pfeil klappt die Palette auf.
  - `__init__(symbol, text, farbe, *, keine_text, titel, parent)`
  - `menu_neu()`
  - `_gewaehlt(c)`
  - `_balken()`

### `ui/baukasten/farbwaehler.py`

„Weitere Farben …“: das Fenster „Farben“ mit den Karteireitern Standard, Benutzerdefiniert und Erweitert.

- **class `Modell`**(QObject) — Die gewählte Farbe, als Farbton/Sättigung/Wert gehalten (der Farbton geht bei Grau nicht verloren).
  - `__init__(start)`
  - `farbe()`
  - `setze(c, melden)`
  - `setze_deckkraft(prozent)`
  - `setze_hsv(h, s, v)`
- **class `_Kacheln`**(QWidget) — Rundes Kachelraster: Farbton quer, oben hell und blass, unten dunkel; ganz unten die Graustufen.
  - `__init__(modell)`
  - `skaliere(zelle)` — Die Kacheln in dieser Größe (Bildpunkte) neu legen: so groß, wie Breite und Höhe der Seitenleiste es zulassen.
  - `_feld(s, z)`
  - `_bei(pos)`
  - `paintEvent(_e)`
  - `mousePressEvent(e)`
  - `mouseDoubleClickEvent(e)`
- **class `_Flaeche`**(QWidget) — Farbton quer, Sättigung von oben (voll) nach unten (grau).
  - `__init__(modell)`
  - `setGroesse(b, h)` — Größe ändern und das Farbbild neu rechnen.
  - `paintEvent(_e)`
  - `_setze(pos)`
  - `mousePressEvent(e)`
  - `mouseMoveEvent(e)`
- **class `_Leiste`**(QWidget) — Helligkeit (Wert): oben hell, unten dunkel, mit Pfeil am rechten Rand.
  - `__init__(modell)`
  - `paintEvent(_e)`
  - `_setze(pos)`
  - `mousePressEvent(e)`
  - `mouseMoveEvent(e)`
- **class `_Ring`**(QWidget) — Farbring (Farbton) mit Dreieck (Sättigung und Wert). Das Dreieck dreht mit: Die reine Farbe zeigt auf ihren Farbton.
  - `__init__(modell)`
  - `skaliere(k)` — Ring und Dreieck im Maßstab ``k`` (1,0 = 270 × 250 Bildpunkte).
  - `_ecken()`
  - `paintEvent(_e)`
  - `_schwerpunkt(q, a, b, c)`
  - `_wirke(pos)`
  - `mousePressEvent(e)`
  - `mouseMoveEvent(e)`
  - `mouseReleaseEvent(_e)`
- **class `_Regler`**(QWidget) — Farbmodell (RGB, HSV, HSL), drei Zahlenfelder und die Schreibweise #rrggbb — gleich in allen Karteireitern.
  - `__init__(modell)`
  - `_modus(text)`
  - `_modus_zeigen()`
  - `werte()`
  - `auffrischen()`
  - `_tippen()`
  - `_hex()`
- **class `_Proben`**(QWidget) — Eine Fläche, oben „Neu“, unten „Aktuell“.
  - `__init__(modell, aktuell)`
  - `paintEvent(_e)`
- **class `FarbenDialog`**(PanelFaehig, QDialog) — Das Fenster „Farben“ (öffnet sich in der Seitenleiste). ``farbe()`` gibt nach OK die gewählte Farbe zurück.
  - `__init__(parent, start, titel)`
  - `_transparenz_zeile()` — „Transparenz“: Schieber und Zahlenfeld in Prozent (100 % = deckend) — beide halten dieselbe Zahl.
  - `_deckkraft_zeigen()`
  - `passe_an(breite, hoehe)` — Das Standard-Raster so groß machen, wie die Seitenleiste Platz hat (Breite für 17 Spalten, Höhe für 18 Zeilen samt Reitern und Probe).
  - `farbe()` — Die gewählte Farbe samt Transparenz (Alpha); ohne Änderung am Schieber ist sie deckend.
  - `deckkraft()`

### `ui/baukasten/fenster_stapel.py`

Fenster in einem Fenster: Unterfenster öffnen sich als Seite im selben Fenster statt als neues Fenster darüber.

- **class `FensterStapel`**(QDialog)
  - `__init__(wurzel, parent)`
  - `oeffne(d, fertig)` — Ein Fenster als oberste Seite einlegen; ``fertig()`` wird nach „OK“ gerufen.
  - `_beendet(d, ergebnis)`
  - `_zurueck()`
  - `_kopf_neu()`
- `ausfuehren(d)` — ``d`` als oberstes Fenster eines Stapels zeigen und warten (wie ``d.exec()``): seine Unterfenster öffnen sich als Seiten im selben Fenster.
- `stapel_von(w)`
- `zeige_unter(elter, d, fertig)` — ``d`` als Unterfenster von ``elter`` zeigen; ``fertig()`` läuft nach „OK“. Im ``FensterStapel`` als Seite, sonst als Fenster mit ``exec``.

### `ui/baukasten/form_menues.py`

Menüs und Galerie des Reiters „Zeichentools“ für Formen: „Form bearbeiten“ und die Stilgalerie „Abc“ (nur Aussehen; jede Wahl ruft einen Befehl).

- `form_bearbeiten_menue(b)`
- `formstile_galerie(b)`
- `linien_galerie(b)` — Linien und Pfeile als Kacheln im Band (zwei Reihen, ``zeilen`` der Gruppe); Klick fügt die Linie ein (``formEinfuegen``).

### `ui/baukasten/formatvorlage_dialog.py`

„Neue Formatvorlage“ als Baustein: Eigenschaften (Name, Typ, basiert auf, folgender Absatz), die Formatierungsleiste aus dem Band

- **class `FormatvorlageDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, *, start, vorlagen, name, basis, aendern, belegt, standard_tab_mm)` — ``aendern``: Name einer vorhandenen Vorlage — dann ist es das Fenster „Formatvorlage ändern“ (Name fest).
  - `_freier_name(wunsch)`
  - `_felder()`
  - `_neu(*_)`
  - `_male(p, rect)` — Vorhergehender Absatz (grau), Beispieltext in der Vorlage, folgender Absatz (grau).
  - `_basis_geaendert()` — Eine andere Basis: ihre Werte sind der neue Ausgangspunkt, was man vorher selbst geändert hat, bleibt dabei nicht stehen.
  - `_pruefen(*_)`
  - `_schriftart()` — Format ▸ Schriftart …: dasselbe Fenster wie im Band, mit allen Feldern; die Vorlage merkt sie sich.
  - `_absatz()` — Format ▸ Absatz …: dasselbe Fenster wie im Band, mit beiden Reitern; die Vorlage merkt sich alle Felder (auch Tabstopps und Umbruchregeln).
  - `_rahmen()` — Format ▸ Rahmen …: das Fenster „Rahmen und Schattierung“ ohne den Reiter Seitenrand (der gehört nicht zu einer Vorlage).
  - `_liste()` — Format ▸ Nummerierung …: dasselbe Fenster wie im Band; die Vorlage merkt sich die gewählte Liste.
  - `_effekte()` — Format ▸ Texteffekte …: Füllung (Farbe der Vorlage, Transparenz) und Kontur.
  - `_tabs()` — Format ▸ Tabstopps …: dasselbe Fenster wie im Absatz; die Vorlage merkt sich die Tabstopps.
  - `_verknuepfung()` — Format ▸ Verknüpfung …: die Tastenkombination, die die Vorlage auf den Absatz anwendet.
  - `_ok()`
  - `ergebnis()` — Name, Basis, folgender Absatz und alle Felder der Vorlage.

### `ui/baukasten/formatvorlagen_bereich.py`

Der Bereich „Formatvorlagen und Formatierung“ (Start ▸ Einstellungen) als Baustein — wie der Bereich der Vorlage in der rechten Seitenleiste:

- `vorlagen_namen(art, ed)` — Die Namen für die Liste: gültige (Katalog und eigene), verwendete (im Dokument) oder alle.
- `vorlagen_schrift(name, vorschau)` — Die Schrift, in der eine Vorlage in Listen erscheint (Größe gedämpft, damit die Liste ruhig bleibt).
- **class `_Absatzmarke`**(QStyledItemDelegate) — Zeile der Liste mit dem Zeichen ↵ rechts (Absatzvorlage), wie in der Vorlage; etwas Luft über und unter dem Namen.
  - `sizeHint(option, index)`
  - `paint(p, option, index)`
- **class `FormatvorlagenBereich`**(PanelFaehig, QDialog)
  - `__init__(parent, get_editor, anwenden, neu)`
  - `_stil_jetzt()`
  - `fuellen()`
  - `waehle(name)`
  - `_neu_vorlage()`
  - `_formatierung_loeschen()`

### `ui/baukasten/formular_gitter.py`

Formular, das sich der Breite anpasst — der Baustein für Felder in Zusatzfenstern (Seitenleiste) und in breiten Fenstern.

- **class `UmbruchSchalter`**(QCheckBox) — Ankreuzfeld, dessen Text bei Platzmangel umbricht (``QCheckBox`` selbst kann das nicht).
  - `__init__(text, parent)`
  - `_indikator()`
  - `hasHeightForWidth()`
  - `heightForWidth(breite)`
  - `sizeHint()`
  - `minimumSizeHint()`
  - `paintEvent(ev)`
- **class `FlussLayout`**(QLayout) — Zeile, die umbricht (wie Text): Beschriftung und das Feld dahinter bleiben beisammen.
  - `__init__(abstand)`
  - `addItem(item)`
  - `count()`
  - `itemAt(i)`
  - `takeAt(i)`
  - `hasHeightForWidth()`
  - `heightForWidth(breite)`
  - `setGeometry(rect)`
  - `sizeHint()`
  - `minimumSize()`
  - `_gruppen()` — Beschriftung + nächstes Feld sind eine Einheit, alles andere steht für sich.
  - `_lege(rect, setzen)`
- `abschnittstitel(text)` — Die Überschrift eines Abschnitts: klein, gedämpft, Großbuchstaben — überall gleich (Gruppen, Spalten, Bereiche in Fenstern).
- `reiter_knopf_stil(knopf)` — Der Reiterknopf (``QToolButton``, ``checkable``) mit Unterstrich in der Hervorhebungsfarbe — für selbst gebaute Reiterleisten.
- `abschnittsband(text)` — Eine Überschrift als graues Band über einer Gruppe von Kacheln (Menüs mit mehreren Gruppen); Schriftgröße der Oberfläche.
- `mittig(widget)` — Ein Element fester Größe (Vorschau, Farbraster …) in der Mitte der Breite.
- **class `_Einheit`** — Ein Paar (Beschriftung + Feld) oder ein breites Element.
  - `__init__(beschriftung, feld, reihe, gewichte)`
- `_hoehe_bei(item, breite)`
- `_natuerlich(item)`
- **class `FormularGitter`**(QLayout)
  - `__init__(parent)`
  - `_nimm(objekt)`
  - `zeile(beschriftung, feld)` — Beschriftung (Text oder Widget) und das Feld (Widget oder Layout) dahinter.
  - `breit(objekt)`
  - `reihe(*paare, gewichte)` — Mehrere Felder nebeneinander, jedes mit der Beschriftung darüber: ``reihe(("Schriftart:", a), ("Größe:", b), gewichte=(3, 1))``.
  - `addItem(item)`
  - `count()`
  - `itemAt(i)`
  - `takeAt(i)`
  - `hasHeightForWidth()`
  - `sizeHint()`
  - `minimumSize()`
  - `heightForWidth(breite)`
  - `setGeometry(rect)`
  - `_reihe_legen(e, breite, y, out)`
  - `_plan(breite)` — → ([(Element, x, y, Breite, Höhe)], Gesamthöhe) bei dieser Breite.
- **class `AngepassteReiter`**(QTabWidget) — Reiter, deren Höhe dem gewählten Reiter folgt (ein ``QTabWidget`` richtet sich sonst nach dem höchsten und lässt kürzeren Reitern leeren Platz).
  - `__init__(parent)`
  - `_aktuelle_seite(_i)` — Nur die gewählte Seite bestimmt die Höhe: die anderen zählen für das Layout nicht mit (sonst bleibt unter kürzeren Reitern leerer Platz).
  - `tabInserted(index)`
  - `_mass(minimum)`
  - `hasHeightForWidth()`
  - `heightForWidth(breite)` — Die Höhe der gewählten Seite bei dieser Breite (Seiten aus ``FormularGitter`` brechen um): so bleibt unter kürzeren Reitern kein leerer Platz.
  - `sizeHint()`
  - `minimumSizeHint()`

### `ui/baukasten/galerie_auswahl.py`

Galerie-Popup: Kacheln mit einer Textprobe in der jeweiligen Schrift und dem Namen darunter (Formatvorlagen, später Tabellen-

- **class `_Kachel`**(QWidget)
  - `__init__(schluessel, name, probe, schrift, farbe, groesse, aktuell, tipp)`
  - `enterEvent(e)`
  - `leaveEvent(e)`
  - `contextMenuEvent(e)`
  - `mouseReleaseEvent(e)`
  - `paintEvent(_e)`
- **class `GalerieAuswahl`**(QMenu) — Meldet den Schlüssel der gewählten Kachel.
  - `__init__(parent, *, titel, spalten, kachel, zeilen_sichtbar)`
  - `kachel(schluessel, name, schrift, *, probe, farbe, aktuell, tipp)`
  - `aktion(text, fn, symbol, *, haken, aktiv)` — Zeile unter der Galerie (z. B. „Neue Formatvorlage …“); schließt das Popup und ruft ``fn``.
  - `_haken_symbol()`

### `ui/baukasten/kachel_feld.py`

Beschriftete Kacheln zum Anklicken, immer genau eine gewählt (zum Beispiel die Umbruchart eines Bildes).

- **class `KachelFeld`**(QWidget)
  - `__init__(parent, *, spalten, groesse, mit_text)`
  - `hinzu(schluessel, text, bild)`
  - `setze(schluessel, melden)`
  - `aktuell()`

### `ui/baukasten/layout_dialog.py`

Das Fenster „Layout“ für Bilder und Formen: Position, Textumbruch, Größe — nach der Vorlage (WPS).

- `_combo(eintraege, aktuell)`
- `_zeile(g, _r, radio, *rest)` — Eine Wahlzeile: der Knopf mit seinem Feld, dahinter (falls da) „Beschriftung + Feld“ — nebeneinander oder untereinander, je nach Breite.
- **class `LayoutDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, werte)`
  - `_achse(titel, w, waagerecht)`
  - `_achse_ein(f)` — Nur die Felder der gewählten Zeile sind bedienbar (wie in der Vorlage).
  - `_position(w)`
  - `_umbruch(w)`
  - `_mass(titel, w)`
  - `_groesse(w)`
  - `_orig_anzeigen()`
  - `_skal_nachziehen()` — Die Skalierung in Prozent aus der aktuellen Größe im Verhältnis zur Originalgröße.
  - `_skal_bezug()` — Wovon die Prozente gelten: die Originalgröße des Bildes — oder die Größe beim Öffnen, wenn „Relativ zur Originalbildgröße“ aus ist.
  - `_groesse_geaendert(hoehe)` — Höhe oder Breite getippt: bei gesperrtem Seitenverhältnis zieht das andere Maß mit.
  - `_skal_geaendert(hoehe)`
  - `_zuruecksetzen()`
  - `_pruefen()` — Zeilenumbruch und Abstand zum Text gelten nur bei Quadrat, Passend und Transparent.
  - `_achse_lesen(f)`
  - `_mass_lesen(f)`
  - `werte()`

### `ui/baukasten/layout_optionen.py`

Das kleine Popup „Layoutoptionen“ neben einem markierten Bild: Umbruchart per Klick, „Mit Text verschieben“ oder „Fester Text“, „Mehr anzeigen“.

- **class `LayoutOptionen`**(QFrame)
  - `__init__(parent, art, mit_text)`
  - `_titel(text)`
  - `_klick(art)`
  - `setze(art)`
  - `zeigen_bei(pos)`

### `ui/baukasten/linien.py`

Linien: Stärke, Art, Farbe — als Wert, als Auswahlzeile für Dialoge und als Rahmen-Menü (unten, oben, links, rechts …).

- `linien_symbol(art, groesse, farbe, breite_pt)`
- **class `LinienZeile`**(QWidget) — Eine Zeile in einem Menü: links ein Text (kann leer sein), rechts die Linie in ihrer Art und Stärke — wie die Auswahl „Linienart“ und
  - `__init__(text, art, breite_pt, farbe, parent, maler)` — ``maler(painter, x0, y, x1, farbe)`` zeichnet statt einer Rahmenlinie etwas anderes, zum Beispiel eine Unterstreichungsart.
  - `enterEvent(e)`
  - `leaveEvent(e)`
  - `mouseReleaseEvent(e)`
  - `paintEvent(e)`
- `linien_menue_zeile(menue, text, art, breite_pt, aktion, maler)` — Hängt eine ``LinienZeile`` als Eintrag in ein Menü; ein Klick ruft ``aktion`` und schließt das Menü.
- **class `LinienWahl`**(QWidget) — Eine Zeile aus Art, Stärke und Farbe. Meldet jede Änderung als ``Linie``.
  - `__init__(linie, *, arten, breiten, frei, parent)` — ``frei``: eine Stärke, die nicht in der Liste steht, kommt als eigener Eintrag dazu (statt auf die nächste zu runden).
  - `setLinie(linie)`
  - `linie()`
  - `_aend()`
- **class `RahmenSeiten`**(Flag)
- `rahmen_symbol(seiten, groesse)` — Kleines Quadrat, in dem nur die gemeinten Linien kräftig sind.
- **class `RahmenMenue`**(MenueListe) — Das Rahmen-Menü (Unten, Oben, Links, Rechts, Kein, Alle, Außen, Innen). Meldet die gewählten Seiten.
  - `__init__(parent, *, innen, mehr_text, mehr)` — ``innen``: True = beide inneren Linien (Tabelle), ``"h"`` = nur die waagerechte (Absätze), False = keine.

### `ui/baukasten/liste_dialog.py`

Die Fenster „Nummerierung und Aufzählungszeichen“ und „Nummerierung anpassen“ als Bausteine.

- `benutzerlisten()`
- `_merke(listen)`
- `_rahmen(p, groesse)`
- `_bild(spec, groesse)`
- `_raster(eintraege, bild)`
- **class `_Zahlenformat`**(QWidget) — Zahlenformat, Zahlenart, Startzahl und „Schriftart …“ der Nummer — gemeinsam für „Nummerierung anpassen“ und „Gliederung anpassen“.
  - `__init__(tipp, breit)` — ``breit``: die Anordnung der Gliederung (Zahlenformat und Vorlage über die ganze Breite, „Beginnen mit“ in einer eigenen Zeile;
  - `setze(format, stil, start, zeichen)`
  - `_schriftart()`
- **class `_Positionen`**(QWidget) — Nummernposition (Ausrichtung der Nummer, Abstand) und Textposition (Tabstopp-Leerstelle nach, Einzug bei) — gemeinsam für
  - `__init__()`
  - `setze(ausr, art, tab, einzug)`
  - `werte()`
- **class `NummerierungAnpassenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, spec)`
  - `_erweitern(an)`
  - `_pos_neu()`
  - `spec()`
  - `_zeichen()`
  - `_zeichen(w)`
  - `_neu()`
  - `_male(p, rect)` — Vorschau wie in der Vorlage: oben und unten graue Balken, dazwischen drei Nummern mit je zwei schwarzen Zeilen.
- `_gl_bild(defn, groesse)` — Kachel einer Gliederung: die Ebenen 1 bis 3 mit ihren Nummern.
- **class `GliederungAnpassenDialog`**(PanelFaehig, QDialog) — „Gliederung anpassen“ (auch „Aufzählungszeichen anpassen“): je Ebene Zahlenformat, Zahlenart, Startzahl, Schriftart, Position und Text,
  - `__init__(parent, defn, *, titel)`
  - `_erweitern(an)`
  - `_wechsel(i)`
  - `_lesen()`
  - `_vorher_gewaehlt(_i)`
  - `_pruefen()`
  - `defn()`
  - `_male(p, rect)` — Die neun Ebenen mit ihren Nummern; die gewählte Ebene hat schwarze Linien, die anderen graue (wie in der Vorlage).
- **class `_KachelFueller`**(QObject) — Ein Kachelraster füllt seine Breite mit drei Kacheln je Zeile (Größe folgt der Breite) und ist genau so hoch wie seine Zeilen.
  - `__init__(raster, spalten)`
  - `eventFilter(obj, ev)`
  - `_anpassen()`
- **class `ListenDialog`**(PanelFaehig, QDialog)
  - `kompakt_machen()` — Für die schmale Seitenleiste: kleinere Kacheln (drei je Zeile), Reiter zum Rollen, Fenster ohne feste Größe.
  - `passe_an(breite, hoehe)` — Je breiter die Seitenleiste, desto mehr Kacheln je Zeile (vier bis sechs), damit die Auswahl ohne Rollen auskommt.
  - `__init__(parent, aktuell, *, seite)`
  - `_fuelle_benutzer()`
  - `_male(p, rect)`
  - `_eintragen(s)` — Ein selbst angepasstes Format kommt in den Reiter „Nummerierung“ und in die Liste der eigenen Formate.
  - `_eintragen_gl(d, raster)`
  - `_aktuell()`
  - `_auswahl()`
  - `_knoepfe(*_)`
  - `_anpassen()`
  - `_loeschen()`
  - `ergebnis()` — Die gewählte Liste, oder None bei „Kein“.
- `kachel_bild(spec, groesse)` — Dieselbe Kachel wie im Fenster „Nummerierung und Aufzählungszeichen“, verkleinert für die Auswahl im Band.
- `aufzaehlungen()` — Die Aufzählungsarten der Auswahl: Punkt, Quadrat und die Zeichen ◆ ✤ ➤ ✓ ✧ (wie im Fenster).
- `nummerierungen()`

### `ui/baukasten/listen_symbole.py`

Kleine Vorschaubilder für Aufzählungs- und Nummerierungsarten (drei Zeilen mit Zeichen davor).

- `liste_zeichner(marke)` — ``marke``: 'disc', 'circle', 'square' oder die Zeichenfolge der ersten drei Nummern (z. B. '1.\|2.\|3.'); None = Keine.

### `ui/baukasten/mass_feld.py`

Zahlenfeld mit Maßeinheit: intern immer Millimeter, angezeigt in der gewählten Einheit (Optionen ▸ Speichern).

- `set_einheit(name)`
- `einheit()`
- **class `MassSpin`**(QDoubleSpinBox) — Wert in mm, Anzeige in der gewählten Maßeinheit; wer „mm“ eingibt oder „2 cm“ tippt, wird verstanden.
  - `textFromValue(v)`
  - `valueFromText(text)`
  - `validate(text, pos)`
- `spin(value, lo, hi, suffix, step, decimals)`
- **class `EinheitFeld`**(QWidget) — Zahlenfeld mit Einheiten-Auswahl daneben (wie „0 char ▾“ im WPS): der Wert ist immer in Millimetern, angezeigt wird er in der
  - `__init__(wert_mm, lo, hi, einheiten, start, leer_bei_null)`
  - `_faktor()`
  - `_zeige()`
  - `_gelesen(v)`
  - `value()`
  - `setValue(mm)`
- `einheit_name()` — Kürzel der Maßeinheit der Oberfläche (Optionen ▸ Speichern) als Schlüssel von ``FELD_EINHEITEN``.

### `ui/baukasten/menue_liste.py`

Menü-Liste: Zeilen mit Symbol, Text, Tastenkürzel, Haken und Untermenü — überall dieselbe Gestalt.

- **class `MenueListe`**(QMenu) — Ein Menü, das Zeilen einheitlich aufbaut. Nicht Mögliches bleibt grau sichtbar statt zu fehlen.
  - `eintrag(text, aktion, *, symbol, kuerzel, haken, aktiv, tip, daten)`
  - `untermenue(text, symbol, aktiv)`
  - `trenner()`
  - `aus_liste(zeilen, parent)` — Baut ein Menü aus einer Beschreibung: ``"-"`` = Trennlinie, sonst ein Wörterbuch mit text, aktion, symbol,
  - `_fuellen(zeilen)`

### `ui/baukasten/objekt_menues.py`

Die Popups für ein markiertes Bild oder eine Form: Formstile, Füllung, Kontur (wie in der Vorlage).

- `_linien_symbol(art, breite, groesse)`
- `_textur(name, groesse)` — Eine kleine, selbst gezeichnete Textur (Vorschau und Füllung): ``papier``, ``granit``, ``holz``, ``stoff``, ``marmor``, ``sand``.
- `graduell_pixmap(dunkel, hell, w, h)`
- **class `FuellMenue`**(FarbPalette) — Füllung wie in der Vorlage: Keine Farbe · Thema-Farben · Standard-Farben · Farbverlauf · Automatisch · Weitere Füllfarben · Pipette ·
  - `__init__(parent, start)`
  - `_raster_untermenue(text, art, weitere, kacheln, groesse, spalten, gewaehlt)` — Ein Untermenü mit Kacheln (Graduell, Textur, Muster) und darunter „Weitere …“, das die Seitenleiste „Formatierung“ öffnet.
  - `_untermenue(text, icon)`
  - `_einsetzen(menue, inhalt)` — Das Raster steht als Inhalt des Untermenüs.
- **class `KonturMenue`**(FarbPalette) — Kontur wie in der Vorlage: Keine Linie · Thema-Farben · Standard-Farben · Farbverlauf · Weitere Linienfarben · Pipette · Linienart ▸ · Strichart ▸ · Pfeilart ▸.
  - `__init__(parent, start)`
- `formstil_werte(schluessel)` — Füllung und Kontur des Stils ``z{Zeile}{Spalte}`` für Bilder und Textfelder: {"fuell": …, "rand": …} (``None`` = keine). Die Werte kommen aus
- `formstil_zeichner(schluessel)` — Zeichnet die Kachel „Abc“ des Stils: Füllung (auch Verlauf), Rand und Schrift in passender Farbe.
- `formstile(parent)` — Das Popup „Formstile“: sechs Zeilen zu sieben Stilen; ``gewaehlt`` meldet ``z{Zeile}{Spalte}`` (Namen im Tipp). Darunter steht „Weitere Effekte …“.

### `ui/baukasten/objektformat_panel.py`

„Formatierung“ für ein Bild, eine Form, ein Textfeld oder WordArt in der rechten Seitenleiste (nach der Vorlage).

- **class `_Felder`**(QWidget) — Eine Gruppe von Feldern im ``FormularGitter`` (Beschriftung über dem Feld), die nur bei passender Füllungs- oder Linienart zu sehen ist.
  - `__init__()`
  - `zeile(text, widget)`
  - `breit(widget)`
- **class `_DreiDUntereinander`** — Für beide Seiten der Effekte (Objekt und Text): Zahlenfelder als Regler mit Wert darüber (ein Schrittfeld zeigt seine Zahl im dunklen Thema nicht)
  - `_schritt_feld(lo, hi, suffix, schritt, nk)`
  - `_seite_effekte(w)`
  - `_abschluss_menue(k)`
  - `_abschluss_setzen(k, art)`
  - `_abschluss_regler(k)` — Wer Breite oder Höhe bewegt, schaltet den Abschluss ein (Rund), wenn er aus war.
  - `_setze_effekte(w)`
  - `_werte_effekte()`
- **class `_TextPanel`**(_DreiDUntereinander, TexteffektPanel) — Die Textoptionen: das Panel der Texteffekte mit dem schmalen 3D-Format.
- **class `ObjektFormatPanel`**(_DreiDUntereinander, TexteffektPanel)
  - `__init__(parent, werte)`
  - `optionen_waehlen(i)` — 0 = Formoptionen (Füllung und Linie, Effekte des Objekts), 1 = Textoptionen (Text im Objekt).
  - `setze_text(werte)` — Die Textoptionen mit den Werten des Textes im Objekt füllen (meldet nichts).
  - `text_werte()`
  - `_tab_icon(t, unterstrichen)` — Die Reiter-Symbole aus dem Katalog (gut sichtbar in beiden Designs): Farbeimer (Füllung und Linie) und Funken (Effekte).
  - `_zusatz_radios(abschnitt)` — Weitere Auswahlpunkte am Ende der Liste („fuell“ oder „linie“).
  - `_zusatz_felder(abschnitt, a)` — Weitere Felder am Ende des Abschnitts („fuell“ oder „linie“).
  - `_seite_fuellung(w)`
  - `_farbe_gewaehlt(c)` — „Keine Farbe“ in der Palette wählt die Füllungsart ohne Farbe (Keine bzw. Automatische Füllung).
  - `_k_breite()`
  - `_k_breite_setzen(pt)`
  - `fuellung_waehlen(art)` — Die Füllungsart wählen („verlauf“, „textur“, „muster“, „bild“ …); die Füllung gilt sofort, die Felder dazu sind bedienbar.
  - `_neu(*_)`
  - `_felder_zeigen()` — Nur die Felder zur gewählten Füllungs- und Linienart zeigen (Keine und Automatisch haben keine weiteren Felder).
  - `_setze_fuellung(w)`
  - `_werte_fuellung()`
  - `_seite_effekte(w)`
  - `_drehung_zuruecksetzen()`
  - `_weich_einschalten()`
  - `_weich_symbol(radius)` — Das Bildchen der Liste: ein Quadrat, dessen Rand mit der Größe weicher wird.
  - `_weich_menue()` — Voreinstellungen als Liste mit Bild und Text: Keine weichen Kanten · 1 · 2,5 · 5 · 10 · 25 · 50 Punkt.
  - `_setze_effekte(w)`
  - `_werte_effekte()`

### `ui/baukasten/panel_rahmen.py`

Rahmen eines Feldes in einer Seitenleiste: Titel, davor/dahinter Knöpfe, ein Menü (⋯ oder ⚙) und ✕ zum Schließen; darunter der Inhalt.

- `_knopf(symbol, tipp)`
- **class `PanelRahmen`**(QWidget)
  - `__init__(titel, menue_zeichen, menue, knoepfe)` — ``knoepfe``: Folge von (Lucide-Name, Tooltip, Funktion) — stehen vor dem Menü.

### `ui/baukasten/pdf_export.py`

Eingebettete, schrittweise PDF-Exportansicht für Lunivos Datei-Menü.

- `_abschnitt(titel, hilfe, layout)`
- `_einklappen(titel, beschreibung, inhalt, offen)`
- `_kennwort()`
- **class `PdfExportAnsicht`**(QWidget) — PDF-Export als dauerhaft sichtbare zweite Menüspalte, keine separates Dialogfenster.
  - `__init__(parent, start, seiten, aktuelle, markierung, exportieren, zurueck)`
  - `_schutz(s)`
  - `_kennwort_zeile(g, row, feld, bestaetigen, text, text2)`
  - `_seiten_schalten(an)`
  - `_durchsuchen()`
  - `ergebnis()`
  - `_ok()`
  - `wahl()`

### `ui/baukasten/pipette.py`

Die Pipette: eine Farbe vom Bildschirm aufnehmen.

- **class `_Pipette`**(QWidget)
  - `__init__(bild, geometrie)`
  - `_tick()`
  - `_fokus_pruefen()`
  - `_zustand(zustand)`
  - `focusOutEvent(e)`
  - `_ende(farbe)`
  - `_farbe_bei(p)`
  - `paintEvent(_e)`
  - `mouseMoveEvent(e)`
  - `mouseReleaseEvent(e)`
  - `keyPressEvent(e)`
- `farbe_vom_bildschirm(parent)` — Die Farbe unter dem nächsten Linksklick (blockiert höchstens ``ZEIT_S`` Sekunden); None bei Abbruch, Zeitablauf oder wenn der Bildschirm nicht aufnehmbar ist.

### `ui/baukasten/rahmen_schattierung.py`

„Rahmen und Schattierung“ als Baustein: das Fenster mit den Karteireitern Rahmen, Seitenrand und Schattierung.

- `_kopf(text)` — Kleine Überschrift über einem Feld — der Baustein ``abschnittstitel``.
- `_einstellung_symbol(art, px)` — Kleines Blatt mit Textzeilen und dem Rahmen, den die Einstellung setzt.
- `_stil_symbol(art, groesse)` — Probe einer Linienart für die Liste „Formatvorlage“.
- `_breite_symbol(pt, groesse)`
- `_muster_symbol(schluessel, px)`
- **class `_Vorschau`**(QWidget) — Blatt mit zwei Absätzen aus grauen Zeilen; zeigt Rahmen und Füllung und schaltet Kanten per Klick.
  - `__init__(kanten_klick)`
  - `_feld()`
  - `paintEvent(_e)`
  - `_luecke(f)`
  - `mousePressEvent(e)`
- **class `_RahmenSeite`**(QWidget) — Einstellung · Linienart · Farbe · Breite · Vorschau mit Kantenknöpfen · Übernehmen für.
  - `__init__(linie, *, seitenrand, innen_h, fuer, abstand_mm)`
  - `linie_wert()`
  - `_setze_einstellung(art)`
  - `_kante(k, an)`
  - `_zeige_seiten(von_knopf)`
  - `_neu()`
  - `_abstand_vorschau()` — Der Abstand, den die Vorschau des Seitenrahmens zeigt (in mm).
  - `_optionen()`
- `_blatt_vorschau(p, rect)` — Das Blatt der Optionen-Fenster: oben weiß, nach unten vom Feld abgeschnitten, darauf ein Textblock (die erste Zeile eingerückt).
- **class `_PolsterDialog`**(QDialog) — „Optionen …“ am Absatzrahmen: Abstand des Rahmens vom Text, oben, unten, links und rechts (mit Einheit), dazu eine Vorschau.
  - `__init__(parent, werte, linie)`
  - `werte()`
  - `_male(p, rect)` — Ein Blatt mit Textzeilen; der Rahmen um den Absatz hat die eingestellten Abstände zum Text.
- **class `_SeitenOptionenDialog`**(QDialog) — „Optionen …“ am Seitenrand: Abstand (vom Text oder vom Seitenrand), „Gemessen von“, die vier Optionen und eine Vorschau der Seite.
  - `__init__(parent, w, linie)`
  - `_messen(*_)`
  - `werte()`
  - `_male(p, rect)` — Ein Blatt mit Text; der Rahmen liegt je nach „Gemessen von“ um den Text oder am Blattrand.
- **class `_AbstandDialog`**(QDialog) — „Optionen …“ am Seitenrand: Abstand des Rahmens vom Seitenrand.
  - `__init__(parent, mm)`
  - `wert()`
- **class `_SchattierungSeite`**(QWidget) — Ausfüllen (Farbe) · Muster (Art, Farbe) · Vorschau · Übernehmen für.
  - `__init__(fuell, muster, fuer)`
  - `werte()`
  - `_neu()`
- **class `RahmenSchattierungDialog`**(PanelFaehig, QDialog) — Das Fenster „Rahmen und Schattierung“. Die Reiter und ihre Werte stehen oben in der Beschreibung des Bausteins.
  - `__init__(parent, *, rahmen, fuell, muster, seitenrand, mit_seitenrand, fuer, innen_h, seite)`
  - `passe_an(breite, hoehe)` — Vorschau so groß, wie die Seitenleiste Platz hat (neben ihr stehen Farbe und Breite).
  - `rahmen()`
  - `schattierung()` — (Füllfarbe oder None, (Musterschlüssel, Musterfarbe) oder None).
  - `seitenrand()`

### `ui/baukasten/raster_auswahl.py`

Kachel-Auswahl: ein Popup mit Bildchen im Raster und einem „Mehr …“-Fuß (Aufzählung, Vorlagen, Ränder, Deckblätter …).

- `_symbol(bild, groesse, blass)` — Aus QIcon, QPixmap oder einer Zeichenfunktion ``f(QPainter, QRectF)`` ein Symbol machen; ``blass``: für Graues (nicht möglich).
- `textkachel(text, pixel)` — Zeichenfunktion für eine Kachel, die nur ein Zeichen oder kurzes Wort zeigt (Symbole, Einheiten).
- `zeilenkachel(bild, titel, angaben, spalten, bild_breite)` — Zeichenfunktion für eine Listenzeile: links ein Bildchen (Zeichner), daneben der Titel fett und darunter die Angaben,
- **class `RasterAuswahl`**(QMenu) — Meldet den Schlüssel der gewählten Kachel.
  - `__init__(parent, *, titel, spalten, groesse, beschriftet, hoehe_max)` — ``beschriftet``: der Name steht unter dem Bild (Seitenzahl-, Wasserzeichen-, Gleichungsgalerie), sonst nur im Tipp.
  - `_rollen_masse()`
  - `kachel(schluessel, beschriftung, bild, *, aktuell, aktiv)` — ``aktiv=False``: die Kachel bleibt sichtbar, aber grau (blass gezeichnet) und nicht wählbar.
  - `bild_setzen(schluessel, bild, beschriftung)` — Bild und Tipp einer vorhandenen Kachel wechseln (z. B. „zuletzt verwendet“ vor dem Aufklappen).
  - `abschnitt(titel)` — Neuer Abschnitt mit eigener Überschrift und eigenem Raster darunter (z. B. „Benutzerdefinierte Symbole:“).
  - `kacheln(eintraege, aktuell)` — ``eintraege``: Liste aus (schluessel, beschriftung, bild).
  - `fuss(text, aktion)` — Zeile unter dem Raster, z. B. „Weitere Aufzählungszeichen …“.
  - `trenner()` — Dünne Linie im Fuß (vor „Benutzerdefinierte Seitenränder …“ u. ä.).
  - `kopf(widget)` — Eine Leiste über den Kacheln (z. B. „Stil \| Hochformat \| Querformat“ bei den Deckblättern).
  - `leeren(groesse)` — Alle Kacheln entfernen (auf Wunsch mit neuer Kachelgröße), um sie neu zu füllen; Kopf und Fuß bleiben.
  - `neu_messen()` — Nach ``leeren`` und neuem Füllen bei offenem Menü: Größe an die neuen Kacheln anpassen.
  - `_klick(schluessel)`

### `ui/baukasten/ruby_dialog.py`

Das Fenster „Phonetisches Leitzeichen“ als Baustein: der Text in Teilen (je eine Zeile), zu jedem Teil sein Leittext, dazu Ausrichtung, Abstand, Schrift und Größe.

- **class `RubyDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, teile, schrift)`
  - `_zeile_anhaengen(basis, ruby, wie, an)`
  - `_gewaehlt()`
  - `_gruppieren()`
  - `_mono()`
  - `_alle_weg()`
  - `_standard()`
  - `_alles()`
  - `_zeile_gewaehlt(r, _c, _vr, _vc)`
  - `_feld_geaendert(*_)`
  - `_malen(p, rect)`
  - `zeilen()`

### `ui/baukasten/schiebe_feld.py`

Regler und Schrittfeld für Dialoge.

- `_knopf(text)`
- **class `SchrittFeld`**(QWidget)
  - `__init__(lo, hi, suffix, schritt, nachkomma, wert)`
  - `value()`
  - `setValue(v)`
- **class `SchiebeFeld`**(QWidget)
  - `__init__(lo, hi, suffix, schritt, nachkomma, wert)`
  - `_zeige(w, melden)`
  - `value()`
  - `setValue(v, melden)`

### `ui/baukasten/schmal.py`

Ein Fenster auf eine schmale Breite bringen (Seitenleiste), ohne dass etwas abgeschnitten wird oder seitlich gerollt werden muss.

- `_alle_layouts(w)`
- `_breite(l)`
- `_zeile_zu_fluss(l)`
- `_tabelle_umbrechen(g, avail)`
- **class `_Umbruchtext`**(QLabel) — Der Text neben einem Ankreuzfeld, mit Zeilenumbruch; ein Klick darauf schaltet das Feld wie sonst der Text.
  - `__init__(knopf, text)`
  - `eventFilter(obj, ev)`
  - `mouseReleaseEvent(ev)`
- `_knopf_umbrechen(l, k)`
- `_nein(l)` — Ein Layout (oder eines darüber), das nicht umbrechen soll: ``layout.setProperty("schmal_nein", True)``.
- `schmal_machen(d, breite)` — Alles in ``d``, was breiter als ``breite`` Pixel ist, umbrechen.
- `_breite_gitter(g)`

### `ui/baukasten/schreibweise_dialog.py`

Das Fenster „Groß-/Kleinschreibung“ als Baustein: eine der fünf Arten wählen.

- **class `SchreibweiseDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, art)`
  - `art()`

### `ui/baukasten/schriftart_dialog.py`

Das Fenster „Schriftart“ (Karteireiter Schriftart und Zeichenabstand) als Baustein.

- `zeichen_waehlen(parent, zeichen)` — Das Schriftart-Fenster für Nummern und Vorlagen. → die gewählten Werte (alle Felder von ``ZEICHEN``) oder None bei „Abbrechen“.
- `_schrift_combo(thema)` — Schriftauswahl; ``thema``: Einträge wie „+Textkörper“ davor (die Vorgabe des Dokuments, hier: keine bestimmte Schrift).
- `_schnitt_combo()`
- `_ueberschrift(text)`
- **class `SchriftartDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, werte, *, umfang)`
  - `_schnitt_setzen(c, fett, kursiv)`
  - `_schnitt_lesen(t)`
  - `_groesse_lesen(t)`
  - `_groesse_setzen(c, g)`
  - `setze(w)`
  - `werte()`
  - `_texteffekte()`
  - `_standard()` — „Standard …“: diese Schrift gilt künftig für neue Dokumente (der Aufrufer speichert sie).
  - `_neu()`
  - `_male(p, rect)`

### `ui/baukasten/seiten_bildchen.py`

Kleine Seitenbilder für Galerien (Einfügen ▸ Seitenzahl, Wasserzeichen, Deckblatt). Jede Funktion gibt einen Zeichner

- `_blatt(p, r, verhaeltnis)` — Ein weißes Hochformat-Blatt mittig in ``r``; gibt das Blattrechteck zurück.
- `_zeilen(p, r, n)`
- `seitenzahl_zeichner(ort, ausrichtung)` — ``ort``: "kopf" \| "fuss"; ``ausrichtung``: "left" \| "center" \| "right" \| "aussen" \| "innen" (zwei Seiten nebeneinander).
- `wasserzeichen_vorschau(w)` — Blatt mit einem beliebigen Wasserzeichen (Text oder Bild, Lage, Transparenz) wie in der Ausgabe (``editor/wasserzeichen.py``).
- `wasserzeichen_zeichner(text, winkel, farbe)`
- `plus_zeichner(beschriftung)` — Kachel „Hinzufügen“: großes graues Plus auf hellem Feld.
- `deckblatt_zeichner(vorlage)` — Die Deckblätter aus ``editor.einfuegen.DECKBLATT_VORLAGEN`` im Kleinen: Titel als dicker Balken, Angaben als dünne Zeilen.
- `raender_zeichner(oben, unten, links, rechts)` — Blatt mit dem Satzspiegel als Rahmen (Seitenlayout ▸ Ränder); die Maße in mm, Blatt A4.
- `format_zeichner(quer)` — Hoch- oder Querformat: ein Blatt mit gestrichelter Mittellinie.
- `papier_zeichner()` — Blatt mit Eselsohr (Seitenlayout ▸ Größe).
- `textrichtung_zeichner(art)` — Kästchen mit „ABC“ in der jeweiligen Richtung: "waagerecht", "senkrecht_rl", "senkrecht_lr", "dreh90", "dreh270", "asiatisch270".

### `ui/baukasten/smartart_format_panel.py`

„Formatierung“ für SmartArt in der rechten Seitenleiste: Füllung und Linie, Effekte, Textoptionen — für den gewählten Knoten, ohne Auswahl für alle.

- **class `SmartArtFormatPanel`**(DiagrammFormatPanel)
  - `__init__(parent, werte)`
  - `_nur_format()`
  - `_teil_einrichten(werte)`

### `ui/baukasten/smartart_menues.py`

Menüs, Galerie und Miniaturen für SmartArt (Reiter „SmartArt-Design“, Schnellleiste am Knoten, Dialog „SmartArt-Grafik auswählen“).

- `_sa(b)`
- `_sym(name)`
- **class `_Auffrischend`**(MenueListe) — Ein Menü, das seine Zeilen bei jedem Öffnen neu bewertet (grau, Haken) — das Band baut ein Menü nur einmal.
  - `__init__(bau, parent)`
  - `_neu()`
- `form_menue(b)`
- `level_menue(b)`
- `hierarchie_menue(b, mit_rechts_links)` — Die Layoutvarianten des Organigramms; ``mit_rechts_links``: oben noch „Layout von rechts nach links“ (Schnellleiste am Knoten).
- `layout_menue(b)` — „Layout ändern“: die 15 Layouts des Katalogs mit ihren Anzeigenamen; das gewählte trägt einen Haken.
- `stil_bild(nr, groesse, blau)` — Zwei übereinanderstehende Kästen im Formenstil ``nr`` (``SA.STILE``: Flach, Einfach, Hell, Kräftig, 3D).
- `stile_menue(b)`
- `stile_galerie(b)`
- `_farben(grau)` — (Fläche, Rand, Strich für Text) — grau im Raster des Dialogs, blau in der großen Vorschau.
- `_kasten(p, r, fl, rand, strich, text, rund)`
- `_pfeil(p, a, b, col)`
- `_m_organigramm(p, W, H, c)`
- `_m_liste(p, W, H, c)`
- `_m_prozess(p, W, H, c)`
- `_m_zyklus(p, W, H, c)`
- `_m_pyramide(p, W, H, c)`
- `_m_spalten(p, W, H, c)`
- `_m_gruppen(p, W, H, c)`
- `_m_matrix(p, W, H, c)`
- `_m_chevron(p, W, H, c)`
- `_m_radial(p, W, H, c)`
- `_m_zielscheibe(p, W, H, c)`
- `_m_trichter(p, W, H, c)`
- `_m_zeitachse(p, W, H, c)`
- `_m_stufen(p, W, H, c)`
- `_zeile(p, x, y, w, col, punkt)` — Eine Aufzählungszeile: Punkt und Strich.
- `_m_punktliste(p, W, H, c)`
- `_m_balkenliste(p, W, H, c)`
- `_m_beschreibungsliste(p, W, H, c)`
- `_m_spaltenrahmen(p, W, H, c)`
- `_m_bildliste(p, W, H, c)`
- `_m_perspektive(p, W, H, c)`
- `_m_konvergenz(p, W, H, c)`
- `_m_kartenprozess(p, W, H, c)`
- `_m_kreisbeziehung(p, W, H, c)`
- `_m_segmentzyklus(p, W, H, c)`
- `zeichne_miniatur(p, r, schluessel, grau)` — Zeichnet die Miniatur des Layouts in ``r``.
- `miniatur(schluessel, grau, groesse)`

### `ui/baukasten/sortieren_dialog.py`

Das Fenster „Text sortieren“ als Baustein (Start ▸ Absatz ▸ Sortieren): ein Hauptschlüssel und bis zu zwei weitere („Anschließend nach“),

- `_feld(w, breite)` — Feldhöhe wie überall; ``breite`` nur für kleine Felder (ein Zeichen), sonst richtet sich das Feld nach dem Gitter.
- **class `SortierOptionenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, trenner, gross_klein, sprache, nur_spalte)`
  - `trenner()`
- **class `_Schluessel`** — Ein Schlüssel „nach … Typ … Aufsteigend/Absteigend“ im ``FormularGitter`` ``g``: Feld über die Breite, darunter Typ, dann die Richtung.
  - `__init__(g, eltern, mit_keine)`
  - `fuellen(felder)`
  - `_aktiv()`
  - `wert()`
- **class `SortierenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, texte)`
  - `_aktualisieren()` — Felder gibt es erst, wenn die Absätze durch den Trenner geteilt sind; ohne Felder sind die weiteren Schlüssel und die
  - `_optionen()`
  - `werte()`

### `ui/baukasten/speichern_fenster.py`

Das eine Speichern-Fenster: Orte links, Ordnerinhalt rechts, unten Dateiname und Dateityp.

- `_symbol(name, px)`
- **class `_DateiModell`**(QFileSystemModel) — Dateimodell mit deutschen Spaltenköpfen (Qt liefert sie sonst englisch).
  - `headerData(section, orientation, role)`
- **class `_Symbole`**(QFileIconProvider) — Ordner und Dateien in der Liste mit denselben Liniensymbolen wie der Rest des Fensters.
  - `__init__()`
  - `icon(info)`
- `_ordner(art)`
- **class `SpeichernFenster`**(QDialog) — ``typen``: Liste (Endung, Filtertext) wie („.docx“, „Word-Dokument (*.docx)“). ``ergebnis()`` → (Pfad, Endung).
  - `__init__(parent, titel, startpfad, typen, vorwahl, oeffnen, mehrere)`
  - `_ort(text, pfad, ic)`
  - `_knopf(ic, tipp, aktion, pruefbar)`
  - `endung()`
  - `gehe_zu(pfad, merken)`
  - `zurueck()`
  - `vor()`
  - `hoch()`
  - `_pfad_zeigen()`
  - `ansicht(nr)`
  - `neuer_ordner()`
  - `_filter_setzen()`
  - `_typ_gewechselt()`
  - `_angeklickt(idx)`
  - `_auswahl_geaendert(*_a)`
  - `_doppelklick(idx)`
  - `zielpfad()` — Pfad aus Ordner und Dateiname; die Endung des gewählten Dateityps gilt (eine andere bekannte wird ersetzt).
  - `speichern()`
  - `ergebnis()`
  - `dateien()`
- `speicherort_waehlen(parent, titel, startpfad, typen, vorwahl)` — Öffnet das Speichern-Fenster. → (Pfad mit Endung, Endung) oder None bei Abbruch.
- `ordner_waehlen(parent, titel, startordner)` — Dasselbe Fenster zum Wählen eines Ordners. → Ordner oder None bei Abbruch.
- `datei_waehlen(parent, titel, start, filter_text, mehrere)` — Dasselbe Fenster zum Öffnen. ``filter_text`` im Qt-Stil („Dokumente (*.docx *.odt);;Alle Dateien (*)“).
- `datei_speichern(parent, titel, startpfad, filter_text)` — Speichern mit einem Filter im Qt-Stil („JSON (*.json)“) — für Lunivos eigene Dateien (Sicherungen, Gelerntes …).
- **class `Dateifenster`** — Dieselben Aufrufe wie ``QFileDialog.get…`` (Rückgabe wie dort), aber mit Lunivos eigenem Fenster.
  - `getOpenFileName(parent, titel, start, filter_text, *_a, **_k)`
  - `getOpenFileNames(parent, titel, start, filter_text, *_a, **_k)`
  - `getSaveFileName(parent, titel, start, filter_text, *_a, **_k)`
  - `getExistingDirectory(parent, titel, start, *_a, **_k)`
- `_ordner_name_fragen(parent)` — Kleines Fenster „Neuer Ordner“ in der Größe der übrigen Felder (statt des winzigen Eingabefensters von Qt).

### `ui/baukasten/tabstopp_dialog.py`

Das Fenster „Tabstopps“ als Baustein: Position, Ausrichtung und Füllzeichen festlegen, löschen, alle löschen.

- `aus_block(bf)` — Die Tabstopps eines Absatzformats als Liste aus Millimetern, Ausrichtung und Füllzeichen.
- `zu_block(bf, stopps)` — Tabstopps (mm, Ausrichtung, Füllzeichen) in ein Absatzformat schreiben.
- `als_text(stopps)` — Tabstopps als Text für eine Formatvorlage: ``30.0:rechts:punkt;80.0:mitte:`` (leer = keine).
- `aus_text(text)`
- `_text(mm, art, fuell)`
- **class `TabstoppDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, stopps, standard_mm)` — ``standard_mm``: Standardabstand der Tabstopps des Dokuments (``None``: das Feld bleibt weg).
  - `_fuellen()`
  - `_knoepfe(*_)`
  - `_zeile(i)`
  - `festlegen()`
  - `loeschen()`
  - `alle()`
  - `stopps()`
  - `standard_abstand()` — Der Standardabstand in Millimetern (``None``, wenn das Fenster ohne dieses Feld aufgerufen wurde).

### `ui/baukasten/tasten_dialog.py`

Das Fenster „Tastenkombination“ als Baustein: eine Tastenkombination aufnehmen und zuweisen.

- **class `TastenDialog`**(QDialog)
  - `__init__(parent, aktuell, *, belegt)`
  - `taste()`
  - `_pruefen(*_)`

### `ui/baukasten/text_format.py`

Textformat-Bausteine: Schriftname, Größe, Fett, Kursiv, Ausrichtung, Zeilenabstand — so wie im Band (Start ▸ Schriftart, Absatz).

- `schrift_feld(combo, breite)` — Das Feld für den Schriftnamen (im Band mit Live-Vorschau, im Fenster ohne).
- `groesse_feld(combo, breite)` — Das Feld für die Schriftgröße: zum Tippen und mit der Liste der üblichen Größen.
- `text_knopf(symbol, tipp)` — F, K oder U als Knopf zum Ein-/Ausschalten, in dem Schnitt, den er bedeutet (wie im Band).
- `ausrichtung_knoepfe()` — Linksbündig, Zentriert, Rechtsbündig, Blocksatz — gleiche Symbole und Namen wie im Band; immer höchstens einer gewählt.
- `_zeilen_symbol(abstand)`
- `_abstand_symbol(mehr)`
- `_einzug_symbol(mehr)`
- **class `TextFormatLeiste`**(QWidget) — Zwei Zeilen wie im Band: Schrift, Größe, Fett, Kursiv · Ausrichtung (und mit ``absatz=True`` Zeilenabstand, Absatzabstand und
  - `__init__(parent, *, absatz)`
  - `_trenner()`
  - `_aktion(name, symbol, fn)`
  - `_ausrichtung(schl, an)`
  - `_zeilenabstand(f, an)`
  - `_zeige_zeilen()`
  - `_abstand(delta)`
  - `_einzug(delta)`
  - `werte()`
  - `setze(d)` — Alle Felder auf die Werte einer Vorlage stellen (ohne ``geaendert`` zu melden).
- `unter_format(art)` — Nur die Unterstreichung als Zeichenformat (zum Zusammenführen, ohne anderes anzufassen).
- `zu_format(w)` — Die Werte eines Zeichenfensters als Zeichenformat (zum Anwenden im Editor und für Vorschauen).
- `aus_format(cf, standard_schrift, standard_groesse)` — Die Werte eines Zeichenformats (zum Vorbelegen eines Zeichenfensters).
- `zeichne_absaetze(p, rect, absaetze, mittig)` — Absätze (Absatzformat, Zeichenformat, Text) in ein Rechteck zeichnen — die Vorschau der Formatierungsfenster.

### `ui/baukasten/texteffekt_dialog.py`

Das Fenster „Texteffekte formatieren“ als Baustein: Reiter „Textfüllung und -kontur“ und „Effekte“ (Schatten, Reflektion, Leuchten, 3D-Format).

- **class `_Pfeil`**(QToolButton) — Der Pfeil vor einer Abschnittsüberschrift: schaltet um wie ein Umschaltknopf (``setChecked``, ``toggled``), zeigt aber keinen Knopfrahmen.
  - `__init__()`
  - `isChecked()`
  - `setChecked(an)`
  - `toggle()`
- **class `Abschnitt`**(QWidget) — Aufklappbarer Abschnitt: Pfeil und Überschrift in Großbuchstaben links, optional ein Bedienelement rechts (z. B. die Voreinstellung).
  - `__init__(titel, rechts)`
  - `_umschalten(an)`
  - `zeile(text, widget)`
  - `breit(widget)`
- `_linien_icon(art, form, groesse)` — Kachel der Linienauswahl: eine Linie in Strichart und Form.
- **class `TexteffektPanel`**(QWidget)
  - `__init__(parent, werte)`
  - `_scroll(seite)`
  - `_tab_icon(t, unterstrichen)`
  - `_seite_fuellung(w)`
  - `_kopffarbe(c)` — Die Farbe im Kopf der Textfüllung: „Keine Füllung“ oder eine einfarbige Füllung.
  - `_kopf_verlauf(farbe)` — „Graduelle Füllung“ im Farbmenü: Farbverlauf von hell nach dunkel in dieser Farbe.
  - `_linien_auswahl()`
  - `_linie_gewaehlt(schluessel)`
  - `_voreinstellungs_knopf(text)`
  - `_seite_effekte(w)`
  - `_schritt_feld(lo, hi, suffix, schritt, nk)` — Zahlenfeld mit Minus und Plus an den Seiten (wie die Größenfelder im 3D-Format des WPS).
  - `_zweier(*teile)`
  - `_d3_zuruecksetzen()`
  - `_menue_zeigen(m, knopf)`
  - `_schatten_auswahl()`
  - `_refl_auswahl()`
  - `_leucht_auswahl()`
  - `_material_auswahl()`
  - `_licht_auswahl()`
  - `_setze_material(material, licht)`
  - `_setze_teil(name, wert, text)` — Eine Voreinstellung übernehmen: die Regler zeigen ihre Werte.
  - `_teil_in_regler(name)`
  - `setze(w)` — Werte ins Panel schreiben (ohne ``geaendert`` zu melden).
  - `_setze(w)`
  - `_setze_fuellung(w)`
  - `_setze_effekte(w)`
  - `werte()`
  - `_werte_fuellung()` — (Werte der Füllung und Kontur, zusätzliche Schlüssel dazu: Verlauf, Konturverlauf, Konturform).
  - `_werte_effekte()` — Schatten, Reflektion, Leuchten und 3D mit den Werten der Regler (gemeinsam für Text und Objekte).
  - `_einschalten(name)` — Ein Regler eines Effekts wurde bewegt: der Effekt ist damit an (mit den Werten, die die Regler zeigen).
  - `_sichtbar()` — Nur die Felder zeigen, die zur gewählten Füllung und Linie gehören (spart Höhe in der Seitenleiste). Das Objekt-Panel baut die Seite selbst und hat sie nicht.
  - `_neu(*_)`
  - `_melden()`
  - `_male(p, rect)`
- **class `TexteffektDialog`**(PanelFaehig, QDialog) — Das Fenster „Texteffekte formatieren“: das Panel mit „OK“ (wie in der Vorlage; das Schließen-Kreuz bricht ab). Felder des Panels sind hier erreichbar.
  - `__init__(parent, werte)`
  - `passe_an(breite, hoehe)` — Die Seite nimmt die ganze Höhe der Seitenleiste: die Abschnitte rollen sonst in einem winzigen Streifen.
  - `__getattr__(name)`

### `ui/baukasten/umbruch_symbole.py`

Die Bildchen für den Textumbruch um ein Bild (wie im WPS): Textzeilen in Grau, das Bild als blaues Feld.

- `umbruch_zeichner(art)`

### `ui/baukasten/umschlossen_dialog.py`

Das Fenster „Eingeschlossene Zeichen“ als Baustein: Vorlage (Ohne, Text reduzieren, Symbol erweitern), Text und Form (Kreis, Quadrat, Dreieck, Raute).

- `form_bild(form, px, gross, text)` — Die Form als kleines Bild (für die Liste) oder, mit ``text``, als Beispiel für die Vorlage.
- `_vorlagenbild(vorlage)`
- **class `UmschlosseneZeichenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, text, form, vorlage)`
  - `werte()`

### `ui/baukasten/voreinstellung_menue.py`

Auswahl von Voreinstellungen als Popup mit Bildchen in Abschnitten (Schatten: Kein, Außen, Innen, Perspektive; Leuchten; Spiegelung;

- **class `VoreinstellungMenue`**(QMenu)
  - `__init__(parent, *, keine, kachel)`
  - `_kopf(text)`
  - `_gitter(eintraege, spalten)`
  - `abschnitt(titel, eintraege, spalten)`
  - `_waehle(schluessel)`

### `ui/baukasten/vorlagen_galerie.py`

Die Seite „Neu“: leeres Dokument direkt starten oder Standard- und eigene Vorlagen getrennt durchsuchen.

- `_blatt_bild(doc, page)` — Erste Seite eines Dokuments, auf Kachelbreite verkleinert.
- `_geruest_bild(muster, benutzer)`
- `_datei_bild(pfad)`
- **class `_Kachel`**(QToolButton) — Ein Blatt mit Name darunter; eine Rubrik zeigt zusätzlich ein Ordnerzeichen mit der Zahl ihrer Vorlagen.
  - `__init__(name, art, wert, schluessel, anzahl)`
  - `_platzhalter(symbol)`
  - `bild_setzen(pm)`
  - `_mit_ordnerzeichen(pm)` — Eine Rubrik: das erste Blatt, dahinter angedeutet weitere, vorn ein Schild mit der Zahl.
- **class `VorlagenGalerie`**(QWidget)
  - `__init__(settings, kann_speichern, benutzer, parent)`
  - `_daten_lesen()`
  - `_ziel()` — Wohin „Dieses Dokument als Vorlage behalten“ ablegt: in die geöffnete Rubrik, sonst in den Vorlagenordner.
  - `_stempel(p)`
  - `_datei_kachel(p, gruppe)`
  - `_geruest_kachel(m)`
  - `_bauen()`
  - `_naechstes_bild()`
  - `_bild_fuer(k)`
  - `rubrik_oeffnen(name)`
  - `_reiter_setzen(schl)`
  - `_sichtbar()`
  - `_anordnen(*_a)`
  - `resizeEvent(e)`
  - `_rubrik_anlegen()`
  - `_ordner_waehlen()`
  - `_ordner_oeffnen()`
  - `neu_lesen()` — Der Ordner wird bei jedem Öffnen der Seite neu gelesen.

### `ui/baukasten/werkbank.py`

Werkbank: die Funktionen eines Reiters der Schreibhilfe als große, selbsterklärende Zeilen (Symbol, Name, Hinweis, Tastenkürzel, bei Schaltern „an/aus“).

- **class `FunktionsZeile`**(QFrame) — Eine große, anklickbare Zeile; mit Tastatur bedienbar (Tab, Leertaste oder Eingabe) und mit Fokusrahmen.
  - `__init__(f, fenster)`
  - `mouseReleaseEvent(e)`
  - `keyPressEvent(e)`
  - `_los()`
  - `aktualisieren()`
- **class `Werkbank`**(QScrollArea) — Die Zeilen eines Reiters; ``oben`` (optional) ist ein Widget über den Zeilen, etwa ein Hinweis.
  - `__init__(fenster, reiter, oben, nur)`
  - `aktualisieren()`

### `ui/baukasten/zellen_raster.py`

Zellenraster: wie bei WPS die Tabelle einfügen — mit der Maus über Zellen fahren, „3 × 4“ lesen, klicken.

- **class `_Gitter`**(QWidget)
  - `__init__(raster, zeilen, spalten, zelle)`
  - `_zelle_bei(pos)`
  - `setze(z, s)`
  - `mouseMoveEvent(e)`
  - `leaveEvent(e)`
  - `mouseReleaseEvent(e)`
  - `paintEvent(e)`
- **class `ZellenRaster`**(QMenu) — Meldet ``gewaehlt(zeilen, spalten)``. Darunter lassen sich mit ``fuss(...)`` weitere Einträge anhängen.
  - `__init__(parent, zeilen, spalten, *, leer_text)`
  - `_beschriften(z, s)`
  - `waehle(zeilen, spalten)`
  - `fuss(text, aktion)`

### `ui/baukasten/zusatz_panel.py`

Zusatzfenster in der Seitenleiste: ein Fenster (zum Beispiel „Nummerierung und Aufzählungszeichen“) öffnet sich nicht über dem Text, sondern als Seite

- **class `_Seite`**(QWidget) — Eine Seite des Panels: oben der Inhalt des Fensters (rollt bei Bedarf, nie seitlich, steht oben in seiner natürlichen Höhe),
  - `__init__(d)`
  - `_anheften(d)` — Die Knopfzeile des Fensters aus seinem Layout nehmen (sie bleibt mit dem Fenster verbunden).
  - `freigeben()` — Fenster wieder aus der Seite lösen (der Aufrufer liest danach noch Werte aus ihm).
- `zusatz_knopf(symbol, tipp, aktion, name)` — Ein Knopf der Titelzeile (Zurück, Schließen, Anheften): flach, mit Symbol aus ``icons``.
- `zusatz_kopf(*teile)` — Die Titelzeile der Seitenleistenfenster samt Linie darunter: ``teile`` von links nach rechts; das erste QLabel/der Titel nimmt den freien Platz.
- **class `ZusatzPanel`**(QWidget) — Die Seite in der Seitenleiste. Unterfenster (``zeige_unter``) legen sich als weitere Seite darüber, mit „← Zurück“.
  - `__init__()`
  - `oeffne(d, fertig)`
  - `_beendet(d, ergebnis)`
  - `unter_ausfuehren(d)` — Ein weiteres Fenster als Seite über die offene legen und warten (wie ``exec``): zum Beispiel „Farben“ aus „Rahmen und Schattierung“.
  - `_zurueck()`
  - `_schliessen()`
  - `_kopf_neu()`
  - `raeumen()`
- `ausfuehren_in(seite, d, vorher, nachher)` — ``d`` als unterste Seite von ``seite`` zeigen und warten (wie ``d.exec()``). ``vorher()`` zeigt die Seitenleiste, ``nachher()`` stellt sie zurück.
- `ausfuehren_im_stapel(stapel, d, breite, hoehe)` — ``d`` als Seite in einem anderen Stapel zeigen und warten (wie ``d.exec()``) — zum Beispiel in der linken Seitenleiste, damit ein
- `leiste_fuer(d)` — Die Seitenleiste, in der ``d`` sich zeigen soll — oder None (dann wie bisher als Fenster): Panels aus, kein Hauptfenster, oder ein anderes Fenster hält schon den Fokus.
- **class `PanelFaehig`** — Zusatzfenster (Einstellungen, die man selten braucht): ``exec()`` zeigt sie in der Seitenleiste statt über dem Text.
  - `exec()`

## `ui/contextual`

### `ui/contextual/__init__.py`

Kontextabhängige Reiter: Tabellen, Bilder/Formen, Kopf-/Fußzeile, Formulare.


### `ui/contextual/diagramm_tools.py`

Kontext-Reiter „Diagrammtools“ nach der WPS-Vorlage (erscheint bei markiertem Diagramm, Kontext ``diagramm``).


### `ui/contextual/header_footer_tools.py`

Kontext-Reiter „Kopf- und Fußzeile“ nach der WPS-Vorlage: Gruppen ohne Namen, Klappen für Kopfzeile, Fußzeile, Seitenzahl,


### `ui/contextual/image_tools.py`

Kontext-Reiter „Bildtools“ und „Zeichentools“ (für Formen im Text: ``form``; für freie Objekte inkl. WordArt/Textfeld: ``zeichen``).


### `ui/contextual/serien_tools.py`

Kontext-Reiter „Mailings“ (Seriendruck) nach der WPS-Vorlage: erscheint über Verweise ▸ Seriendruck und bleibt, bis


### `ui/contextual/table_tools.py`

Kontext-Reiter „Tabellentools“ (erscheint, wenn die Schreibmarke in einer Tabelle steht).


### `ui/contextual/text_tools.py`

Kontext-Reiter „Texttools“ nach der WPS-Vorlage (erscheint bei markiertem WordArt oder Textfeld, zusammen mit „Zeichentools“).


## `ui/dialogs`

### `ui/dialogs/__init__.py`

Dialoge und Optionen.


### `ui/dialogs/bildschirmfoto.py`

Bildschirmfoto: ganzer Bildschirm oder aufgezogener Bereich.

- **class `BereichWahl`**(QWidget) — Vollbild mit eingefrorenem Bildschirm; mit der Maus einen Bereich aufziehen (Esc bricht ab).
  - `__init__(bild)`
  - `paintEvent(ev)`
  - `_quelle(r)`
  - `mousePressEvent(e)`
  - `mouseMoveEvent(e)`
  - `mouseReleaseEvent(e)`
  - `keyPressEvent(e)`

### `ui/dialogs/diagramm_fenster.py`

„Diagramm einfügen“ nach der Vorlage (einfuegen/07 und Prüfkatalog): links die Diagrammarten mit eigenen Bildchen, oben die

- `art_symbol(sym, px)` — Diagrammart-Symbol aus dem zentralen Lucide-Katalog.
- **class `DiagrammDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, vorhanden)` — ``vorhanden``: Daten eines vorhandenen Diagramms (Diagrammart, Titel, Rubriken, Reihen, Kombination) — dann öffnet das Fenster damit.
  - `_kombi_tabelle()`
  - `_kombi_fuellen()` — Eine Zeile je Datenreihe; Werte aus ``self.kombi``.
  - `_kombi_geaendert(*_)`
  - `kompakt_machen()` — In der Seitenleiste: die Diagrammarten wie in WPS in einer Spalte über der Vorschau (alle sichtbar, ohne Rollbalken),
  - `passe_an(breite, _hoehe)` — Auf die echte Breite der Seitenleiste: zwei Spalten Diagrammarten, Vorschau so breit wie der Platz.
  - `_gruppe(zeile)`
  - `_waehle(untertyp)`
  - `_daten()`
  - `_ist_kombi()`
  - `bild(breite, hoehe)`
  - `daten()`
  - `aktualisieren(*_)`

### `ui/dialogs/dokument_dialoge.py`

Kleine Dialoge: Seite einrichten, Absatz, Kopf-/Fußzeile, Tabelle, Suchen/Ersetzen.

- **class `PageSetupDialog`**(PanelFaehig, QDialog)
  - `__init__(page, parent)`
  - `result_page()`
  - `accept()`
- **class `HeaderFooterDialog`**(PanelFaehig, QDialog)
  - `__init__(title, hf, parent)`
  - `value()`
- **class `TableDialog`**(PanelFaehig, QDialog) — „Tabelle einfügen“ wie in WPS: Tabellengröße, Einstellung für optimale Breite, Abmessungen für neue Tabellen speichern.
  - `__init__(parent, vorgabe)`
  - `spaltenbreite_px()` — Feste Breite jeder Spalte in Bildpunkten; None: automatisch (Seitenbreite).
- **class `BildGroesseDialog`**(PanelFaehig, QDialog)
  - `__init__(breite_px, hoehe_px, parent)`
  - `_b(v)`
  - `_h(v)`
  - `breite_px()`
  - `hoehe_px()`
- **class `ZoomDialog`**(PanelFaehig, QDialog) — Ansicht ▸ Zoom: feste Stufen, Seitenbreite, ganze Seite oder eigener Wert.
  - `__init__(parent, aktuell)`
  - `ergebnis()`
- **class `TabellenEigenschaftenDialog`**(PanelFaehig, QDialog) — „Tabelleneigenschaften“: Breite, Ausrichtung, Rahmenstärke, Zellenabstand, Kopfzeile. Ändert die Tabelle nicht selbst; der Aufrufer liest die Felder.
  - `__init__(parent, breite_prozent, ausrichtung, rand, abstand, kopfzeile)`
- **class `BildZuschneidenDialog`**(PanelFaehig, QDialog) — „Bild zuschneiden“: wie viele Bildpunkte links, oben, rechts und unten abgeschnitten werden.
  - `__init__(parent)`
  - `werte()` — (links, oben, rechts, unten) in Bildpunkten.

### `ui/dialogs/einfuegen_dialoge.py`

Dialoge zum Einfügen: Formen, WordArt, Diagramm, Piktogramm, Formel, Deckblatt, Datum, Textbausteine.

- `_ok(dlg)`
- **class `_Vorschau`**(QLabel) — Vorschaubild, das sich der Breite anpasst (in der Seitenleiste kleiner, nie breiter als 460 px).
  - `__init__()`
  - `setze(img)`
  - `_neu()`
  - `resizeEvent(ev)`
- **class `VorschauMixin`**
  - `_vorschau_bauen(layout)`
  - `_zeige(img)`
- **class `FormDialog`**(PanelFaehig, QDialog, VorschauMixin)
  - `__init__(parent, form)`
  - `bild()`
  - `daten()`
  - `aktualisieren(*_)`
- **class `_LayoutGalerie`**(QWidget) — Galerie der SmartArt-Layouts: Bildchen (selbst gezeichnet) in einem KachelFeld, die Spaltenzahl folgt der Breite.
  - `__init__(namen, zeichner, aktuell)`
  - `_bauen(spalten)`
  - `_klick(name)`
  - `setze(name)`
  - `aktuell()`
  - `resizeEvent(ev)`
- `_layout_bildchen(p, r, name)` — Graue Miniatur eines SmartArt-Layouts (selbst gezeichnet, ``ui/baukasten/smartart_menues.py``).
- **class `SmartArtDialog`**(PanelFaehig, QDialog, VorschauMixin) — SmartArt auswählen (wie WPS „Grafik auswählen“): Galerie der Layouts, darunter Name, Beschreibung und Vorschau, OK.
  - `__init__(parent, daten)`
  - `layout_()`
  - `_layout(name)`
  - `daten()`
  - `aktualisieren(*_)`
- **class `WordArtDialog`**(PanelFaehig, QDialog, VorschauMixin)
  - `__init__(parent, text, stil, farbe, vorlage)` — ``vorlage``: Nummer eines Galerie-Stils (``E.WORDART_VORLAGEN``); ohne sie gelten ``stil`` und ``farbe``.
  - `vorlage_nr()`
  - `bild()`
  - `aktualisieren(*_)`
- **class `DiagrammDatenDialog`**(PanelFaehig, QDialog) — Titel und Daten des Diagramms (Unterfenster von „Diagramm einfügen“): erste Spalte Rubriken, weitere Spalten Datenreihen.
  - `__init__(parent, titel, kategorien, reihen)`
  - `_reihe_dazu()`
  - `daten()`
- **class `PiktogrammDialog`**(PanelFaehig, QDialog)
  - `__init__(parent)`
  - `_fuellen(q)`
  - `ergebnis()`
- **class `FormelDialog`**(PanelFaehig, QDialog)
  - `__init__(parent)`
  - `_zeige(*_)`
- **class `DeckblattDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, autor)`
- **class `DatumDialog`**(PanelFaehig, QDialog) — Wie die Vorlage: links „Verfügbare Formate“, rechts „Sprache“, darunter „Automatisch aktualisieren“ (dann als Datumsfeld).
  - `__init__(parent, sprache)`
  - `_loc()`
  - `_fuellen(*_)`
  - `ergebnis()`
  - `feldanweisung()` — Bei „Automatisch aktualisieren“ die Feldanweisung (DATE/TIME), sonst None.
- **class `BausteinDialog`**(PanelFaehig, QDialog) — Textbausteine: links die Liste (mitgelieferte und eigene), rechts die Vorschau; Name und Kürzel oben. „Aus Markierung …“ merkt den markierten Text
  - `__init__(parent, ed)`
  - `_fuellen(wahl)`
  - `_aktuell()`
  - `_zeigen()`
  - `_neu()`
  - `_weg()`
  - `_einfuegen()`

### `ui/dialogs/einfuegen_fenster.py`

Kleine Fenster des Reiters Einfügen nach den WPS-Vorlagen: „Zahl“, „Felder“, „Text in Tabelle umwandeln“, „Tabelle in Text konvertieren“.

- `_titel(text, feld)`
- **class `ZahlDialog`**(PanelFaehig, QDialog) — Feld „Zahl“, darunter die Liste „Zahlentyp“ (wie die Vorlage „Zahl“).
  - `__init__(parent)`
  - `ergebnis()` — Die Zahl im gewählten Typ; ``ValueError`` bei falscher Eingabe.
  - `_pruefen()`
- **class `FelderDialog`**(PanelFaehig, QDialog) — „Felder“ wie in der Vorlage: links „Feld auswählen“ mit den Feldnamen, rechts „Feldeigenschaften“ mit Feldfunktionen,
  - `__init__(parent, kontext)`
  - `_kopf(text)`
  - `kompakt_machen()` — In der Seitenleiste: Feldnamen über den Eigenschaften.
  - `_zeile(schl, text, w, aktiv)`
  - `_box(eintraege, bearbeitbar, daten)`
  - `_zeigen(name)`
  - `_wert(schl)`
  - `_bauen(*_)` — Feldfunktion aus dem Assistenten (außer bei Formel, die man selbst schreibt).
  - `_formel_format(muster)`
  - `_formel_einsetzen(box)`
  - `_gueltig()`
  - `_pruefen(*_)`
  - `feld()` — (Feldanweisung, Ergebnis); mit „Formatierung beibehalten“ trägt die Anweisung ``\* MERGEFORMAT``.
- **class `AutoTextDialog`**(PanelFaehig, QDialog) — „AutoText erstellen“: Name für die Markierung (Vorschlag: ihre ersten Wörter).
  - `__init__(parent, markierung)`
  - `name()`
- **class `TrennerDialog`**(PanelFaehig, QDialog) — „Text in Tabelle umwandeln“ (mit Spaltenzahl) oder „Tabelle in Text konvertieren“: woran getrennt wird.
  - `__init__(parent, *, zu_tabelle, texte)`
  - `trenner()`
  - `spalten()`
  - `_zaehlen()`
- **class `SeitenzahlDialog`**(PanelFaehig, QDialog) — „Seitenzahl einfügen“ wie in der Vorlage: Format und Position, Kapitelnummer einbeziehen (Formatvorlage, Trennzeichen, Beispiele),
  - `__init__(parent, page)`
  - `_zustand(*_a)`
  - `werte()`
- **class `HyperlinkDialog`**(PanelFaehig, QDialog) — „Hyperlink“ wie in der Vorlage: links „Link zu“ (Datei oder Webseite, Aktuelles Dokument, E-Mail-Adresse), oben „Anzuzeigender Text“
  - `__init__(parent, *, text, ziele, ordner, adressen)`
  - `kompakt_machen()` — In der Seitenleiste: „Link zu“ oben (drei Ziele untereinander, Bild neben dem Text), die Felder darunter in voller Breite.
  - `_ordner_setzen(pfad)`
  - `_ordner_zeigen(pfad)`
  - `_doppelklick(i)`
  - `_quickinfo()`
  - `art_waehlen(i)`
  - `_pruefen()`
  - `adresse_zu_href(adresse)` — Eingabe → Linkziel: Dateipfad → file://…, „www.…“ → https://…, sonst unverändert.
  - `ergebnis()`
- **class `ObjektDialog`**(PanelFaehig, QDialog) — „Objekt einfügen“ wie in der Vorlage. „Neu“ (ein eingebettetes Office-Objekt anlegen) kann Lunivo nicht und bleibt grau;
  - `__init__(parent, *, als_symbol, ordner)`
  - `_suchen()`
  - `art()` — "symbol" \| "bild" \| "text" \| "" (keine Datei).
  - `_beschreiben()`

### `ui/dialogs/formular_dialog.py`

Dialog zum Anlegen eines Formularfelds (Textfeld, Auswahlliste, Datum, Kontrollkästchen, Schaltfläche).

- **class `FormFeldDialog`**(PanelFaehig, QDialog)
  - `__init__(fenster, art, bestehend)`
  - `_ok()`
  - `meta()`

### `ui/dialogs/hilfe_dialoge.py`

Hilfe: Handbuch, Tastenkürzel, Erweiterungen.

- `_browser(parent, titel, breite, hoehe)`
- **class `_Lesefeld`**(QTextBrowser) — Der Text des Handbuchs in einer ruhigen Spalte: nicht breiter als ~780 px, die Spalte steht in der Mitte.
  - `resizeEvent(e)`
- `_handbuch_gestalten(b)` — Gibt dem Markdown-Text die Gestalt der Vorlage: Antiqua mit Luft, Überschriften, Tabellen ohne Gitter, Merkkästen, Tastenchips.
- `handbuch(parent)` — Das Handbuch: links die Gliederung (Gruppen, Abschnitte), rechts der Text. Er liegt als Markdown in resources/handbuch.md.
- `_fuss(d, v)` — Wie in der Vorlage: „Abbrechen“ und „Schließen“ rechts unten, beide schließen das Fenster.
- `_titel(text)`
- `_dialog(parent, titel, breite)`
- `tastenkuerzel(parent)` — „Tastenkombinationen“: je Gruppe eine Überschrift, darunter zwei Kürzel mit Wirkung nebeneinander.
- `_erweiterungen_liste()`
- `erweiterungen(parent)` — „Erweiterungen“: jede Karte zeigt mit „DA“, ob der Teil schon geholt ist.
- `ueber(parent, version)`

### `ui/dialogs/ki_dialoge.py`

KI-Konfiguration: Aufgaben-Modellzuweisung, Liste der KI-Modelle, „Eigenen Anbieter hinzufügen“.

- `_tags_text(a)`
- **class `_Antwort`**(QObject)
- **class `AnbieterDialog`**(QDialog) — Neuer oder zu bearbeitender Anbieter: Name, Vorlage, URL, Schlüssel, Modell (Liste vom Anbieter), Fähigkeiten.
  - `__init__(fenster, konfig, bestehend)`
  - `_chips_legen(spalten)` — „Modell verwenden für“ als gleichmäßiges Raster (gleich breite Felder) statt einer Zeile, die irgendwo umbricht.
  - `kompakt_machen()` — In der Seitenleiste: der Titel steht schon im Kopf der Seite, und die Fähigkeiten stehen zu zweit nebeneinander.
  - `_vorlage_gewaehlt(i)`
  - `_holen(still)`
  - `_geholt(r)`
  - `_ok()`
- **class `ModellListe`**(QWidget) — Die Liste der verbundenen KI-Modelle: hinzufügen, bearbeiten, entfernen (im Fenster „KI-Einstellungen“ und als eigenes Fenster).
  - `__init__(fenster, konfig)`
  - `_fuellen()`
  - `_knoepfe(*_)`
  - `_aktuell()`
  - `_neu()`
  - `_bearbeiten()`
  - `_entfernen()`
- **class `ModellListeDialog`**(QDialog) — „Liste der KI-Modelle“ als eigenes Fenster (Optionen).
  - `__init__(fenster, konfig)`
- `modell_combo(konfig, aufgabe, gewaehlt)` — Die Auswahl „welches Modell für diese Aufgabe?“ — dieselbe in der Modellzuweisung und in den erweiterten Einstellungen des Chats.
- **class `ModellZuweisung`**(QWidget) — Je Aufgabe ein Modell: Chatbot, Zusammenfassen, Übersetzung, Textanalyse, Bildgenerierung.
  - `__init__(fenster)`
  - `aufbauen()`
  - `uebernehmen()`
- **class `KIKonfigurationDialog`**(QDialog) — Die Modellzuweisung als eigenes Fenster (nur noch für Altaufrufe; im Alltag öffnet „KI-Einstellungen“).
  - `__init__(fenster)`
  - `_ok()`
- **class `SprachListe`**(QListWidget) — Eine Sprachliste mit hohen Zeilen (wie das alte Fenster „Einstellungen der Übersetzung“); bedienbar wie eine Auswahl: ``currentData()``,
  - `__init__(eintraege)`
  - `currentData()`
  - `currentText()`
  - `findData(daten)`
  - `setCurrentIndex(i)`
  - `setCurrentText(text)`
- **class `SprachePanel`**(QWidget) — Die Sprachen der Schreibhilfe, nebeneinander: „Sprache für die Überprüfung“ (Sprache des Dokuments) und „Übersetzen nach“ (Ziel der KI-Übersetzung).
  - `__init__(fenster)`
  - `kompakt_machen()` — In der Seitenleiste: die zwei Listen untereinander statt nebeneinander, jede mit sechs sichtbaren Zeilen (der Rest rollt).
  - `uebernehmen()`
- **class `McpDialog`**(QDialog) — Ein MCP-Server: Name, Startbefehl, ein/aus; „Testen“ startet ihn kurz und zeigt seine Werkzeuge.
  - `__init__(fenster, e)`
  - `_testen()`
  - `_ok()`
  - `werte()`
- **class `McpListe`**(QWidget) — Die eingetragenen MCP-Server: hinzufügen, bearbeiten, entfernen.
  - `__init__(fenster, konfig)`
  - `fuellen()`
  - `_knoepfe(*_)`
  - `_aktuell()`
  - `_neu()`
  - `_bearbeiten()`
  - `_entfernen()`
- **class `WebsuchePanel`**(QWidget) — Websuche für den KI-Chat: Anbieter, Adresse oder Schlüssel, Zahl der Treffer. Ein: die Frage geht an den Suchanbieter.
  - `__init__(konfig)`
  - `werte()`
  - `_testen()`
  - `uebernehmen()`
- **class `KIEinstellungenDialog`**(PanelFaehig, QDialog) — Das eine Fenster für alles zur KI: verbundene Modelle, Modellzuweisung, MCP-Server und Websuche.
  - `__init__(fenster, start)`
  - `kompakt_machen()` — In der Seitenleiste: kurze Reiternamen (die langen stehen im Tipp), damit alle fünf nebeneinander passen.
  - `freischalten()` — Ohne verbundenes Modell ist nur der erste Reiter bedienbar; mit Modell (auch Ollama auf diesem Rechner) sind alle frei.
  - `neues_modell()`
  - `_ok()`
- **class `SchnelleAktionDialog`**(PanelFaehig, QDialog) — „Schnelle KI-Aktion erstellen“: eine einmalige KI-Aufgabe mit Name, Anweisung, Ergebnisart und Zugriff.
  - `__init__(fenster)`
  - `_umschalten()` — Erst die ersten sechs Vorlagen, mit „Alle anzeigen“ alle.
  - `_vorlage(name, prompt)`
  - `_ok()`
  - `werte()`
- **class `ErgebnisseDialog`**(PanelFaehig, QDialog) — „Alle Ergebnisse anzeigen“: die KI-Antworten dieser Sitzung; Kopieren oder an der Schreibmarke einfügen.
  - `__init__(fenster)`
  - `_zeigen(i)`
  - `_einfuegen()`

### `ui/dialogs/lesehilfe_dialog.py`

Lesehilfe: Papierton, Abstände, Zeilenfokus und Absatzfokus — wirkt nur auf die Anzeige, nicht auf das gespeicherte Dokument.

- **class `LesehilfeDialog`**(PanelFaehig, QDialog)
  - `__init__(fenster)`
  - `zeige(knopf)` — In der Seitenleiste öffnen (Standard); ohne Seitenleiste unter dem Knopf aufklappen.
  - `zeige_unter(knopf)` — Unter dem Knopf „Lesehilfe“ aufklappen (ohne ihn: wie ein gewöhnliches Fenster).
  - `anwenden()`
  - `reject()` — „Abbrechen“ stellt den Stand von vorher wieder her.

### `ui/dialogs/oberflaeche_dialoge.py`

Oberfläche anpassen: Register (Reiter) auswählen und ordnen, Schnellzugriff, Symbole austauschen, Oberfläche wählen.

- `lade_json(settings, key, standard)`
- `_satz(text, gedaempft)` — Erklärung über den Feldern: bricht um.
- **class `RegisterAnpassenDialog`**(PanelFaehig, QDialog) — Reiter ein-/ausblenden und umordnen — wie „Menüband anpassen“ in WPS.
  - `__init__(parent, settings, daten)`
  - `_schieben(d)`
  - `_speichern()`
- **class `SchnellzugriffDialog`**(PanelFaehig, QDialog) — Welche Knöpfe in der Schnellzugriffsleiste neben dem ☰-Menü stehen.
  - `__init__(parent, settings, alle, aktuell)`
  - `_speichern()`
- **class `EigeneZeichnungDialog`**(PanelFaehig, QDialog) — „Eigene Zeichnung …“: eine SVG-Datei oder nur Pfaddaten hineinkopieren; die Vorschau zeichnet beim Tippen mit.
  - `__init__(parent)`
  - `_schau()`
  - `_ok()`
- **class `SymbolTauschenDialog`**(PanelFaehig, QDialog) — Ein Symbol austauschen — wie in der ersten Fassung: Getauscht wird die Zeichnung, nicht der Knopf; sie ändert sich überall,
  - `__init__(parent, settings, name)`
  - `passe_an(breite, hoehe)` — In der Seitenleiste so viele Zeichnungen nebeneinander, wie in die Breite passen.
  - `_befehle()`
  - `_kopf_zeigen()`
  - `_gitter_zeigen()`
  - `_anwenden(meldung)`
  - `_waehle(katalogname)`
  - `_eigene()`
  - `_dieses_zurueck()`
  - `_alle_zurueck()`
  - `reject()` — Abbrechen (auch Esc und ✕) nimmt zurück, was in diesem Fenster getauscht wurde.
- **class `OberflaecheDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, settings)`
  - `wahl()`

### `ui/dialogs/optionen.py`

Optionen — das Fenster hinter „☰ Menü ▸ Optionen“ (F9): sechs Seiten in einer flachen Liste, oben eine Suche.

- **class `OptionenAnsicht`**(LesenSeiten, AnsichtSeiten, DateiSeiten, BefehleSeiten, LunivoSeiten, NameKiSeiten, QWidget) — Alle Optionen als Ansicht (Liste und Suche links, Seite rechts) — sie steht in der Datei-Ansicht („☰ Menü ▸ Erweiterte
  - `__init__(fenster, seite)`
  - `eventFilter(obj, ev)`
  - `_erklaere(name)`
  - `gehe_zu(key)` — Eine Seite zeigen; frühere Seitennamen führen auf die neue Seite und klappen dort den passenden Bereich auf.
  - `_index_bauen()`
  - `_suchen(q)`
  - `_springe(it)`
  - `_band_merken()` — Die Änderung steht in den Einstellungen; das Band wird beim Verlassen der Seite neu gebaut (nicht bei jedem Klick).
  - `_band_jetzt(*_a)`
  - `hideEvent(ev)`
- **class `OptionenDialog`**(QDialog) — Die Optionen als eigenes Fenster (für Aufrufe außerhalb der Datei-Ansicht); gleicher Inhalt wie `OptionenAnsicht`.
  - `__init__(fenster, seite)`

### `ui/dialogs/sendungen_dialoge.py`

Dialoge zu Sendungen: Umschlag, Etiketten, Seriendruck, Regeln, Vorschau.

- `_ok(dlg, text_ok)`
- **class `UmschlagDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, absender)`
- **class `EtikettenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent)`
- **class `SeriendruckDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, felder, gespeichert)`
  - `_laden()`
- **class `RegelDialog`**(PanelFaehig, QDialog)
  - `__init__(parent)`

### `ui/dialogs/serien_fenster.py`

Fenster des Reiters „Mailings“ (Seriendruck): Empfänger auswählen, Seriendruckfeld einfügen, übereinstimmende Felder festlegen.

- **class `EmpfaengerDialog`**(PanelFaehig, QDialog) — „Seriendruckempfänger“: alle Sätze der Datenquelle als Tabelle, je Zeile ein Haken; „Alle“ und „Keine“.
  - `__init__(parent, spalten, saetze, aktiv)`
  - `_alle(an)`
  - `ergebnis()`
- **class `FeldDialog`**(PanelFaehig, QDialog) — „Seriendruckfeld einfügen“: die Spalten der Datenquelle; ohne Datenquelle ein Name zum Eintippen. „Einfügen“ meldet
  - `__init__(parent, spalten)`
  - `_melden()`
- **class `ZuordnenDialog`**(PanelFaehig, QDialog) — „Übereinstimmende Felder festlegen“: zu jedem Feld im Text die Spalte der Datenquelle, aus der es seinen Wert bekommt.
  - `__init__(parent, felder, spalten, zuordnung)`
  - `ergebnis()`

### `ui/dialogs/silben_dialog.py`

Einstellungen für „Silben farbig“: alles, was jemand mit Legasthenie braucht, um es für sich passend zu machen.

- **class `SilbenDialog`**(PanelFaehig, QDialog)
  - `__init__(fenster)`
  - `_farbe_waehlen(i)`
  - `_knoepfe_faerben()`
  - `_zustand()`
  - `konfig()`
  - `anwenden()` — Wirkt sofort auf Vorschau und alle offenen Dokumente (Abbrechen stellt den alten Stand wieder her).
  - `_standard()`
  - `reject()`

### `ui/dialogs/sonderzeichen.py`

Das Fenster „Symbol“ (Einfügen › Symbol › Weitere Symbole …) in der Seitenleiste, nach der Vorlage mit drei Reitern:

- **class `SymbolDaten`** — Zuletzt verwendet, benutzerdefinierte Symbole (Zeichen, Haken) und Tastenkombinationen — in den Einstellungen (``get``/``set``).
  - `__init__(einstellungen, standard, anzahl)`
  - `_lesen(key, leer)`
  - `zuletzt()`
  - `merken(z)`
  - `benutzer()` — Die Liste „Benutzerdefinierte Symbole“ in ihrer Reihenfolge, je Zeichen mit Haken (``True``: in der Klappe zu sehen).
  - `setze_benutzer(liste)`
  - `sichtbar()`
  - `zuruecksetzen()`
  - `tasten()`
  - `setze_tasten(tasten)`
- **class `_Speicher`**
  - `__init__()`
  - `get(key, default)`
  - `set(key, wert)`
- **class `Zeichenraster`**(QWidget) — Zeichen in Zellen, die sich der Breite anpassen: Spaltenzahl = Breite / Zelle, Höhe folgt der Zahl der Zeilen (``heightForWidth``).
  - `__init__(parent)`
  - `setze(zeichen, schrift)`
  - `zeichen()`
  - `waehle(code)`
  - `spalten()`
  - `hasHeightForWidth()`
  - `heightForWidth(breite)`
  - `sizeHint()`
  - `minimumSizeHint()`
  - `zelle_von(i)`
  - `paintEvent(_ev)`
  - `_index_bei(pos)`
  - `mousePressEvent(ev)`
  - `mouseDoubleClickEvent(ev)`
  - `_setze_index(i)`
  - `keyPressEvent(ev)`
  - `focusInEvent(ev)`
  - `focusOutEvent(ev)`
- **class `_TastenFenster`**(PanelFaehig, TastenDialog) — „Tastenkombination“ als Seite über dem Fenster „Symbol“.
- **class `SonderzeichenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, einfuegen, daten, *, bei_tasten)`
  - `_symbole()`
  - `_schrift_neu(*_)`
  - `_gewaehlt(cp)`
  - `_code_zeigen()`
  - `_code_getippt(text)`
  - `_sonderzeichen()`
  - `_benutzer()`
  - `_breiten()`
  - `resizeEvent(ev)`
  - `showEvent(ev)`
  - `_benutzer_fuellen(wahl)`
  - `_liste_aus_widget()`
  - `_liste_knoepfe()`
  - `_haken(*_)`
  - `_verschieben(schritt)`
  - `_entfernen()`
  - `_zuruecksetzen()`
  - `_taste_festlegen()`
  - `_tasten_melden()`
  - `zeichen_jetzt()` — Das Zeichen, das „Einfügen“ gerade einfügt: je nach Reiter aus Raster, Sonderzeichen oder benutzerdefinierter Liste.
  - `_reiter(i)`
  - `_knoepfe()`
  - `_einfuegen()`
  - `_zu_benutzer()`

### `ui/dialogs/ueberpruefen_fenster.py`

Fenster des Reiters „Überprüfen“ nach den Vorlagen (ueberpruefen/02, 10).

- **class `WoerterDialog`**(PanelFaehig, QDialog) — „Wörter zählen“: die Statistiken untereinander, Werte rechtsbündig; der Haken nimmt Fuß- und Endnoten dazu.
  - `__init__(parent, ohne, mit)`
  - `_zeigen(*_)`
- **class `SchutzDialog`**(PanelFaehig, QDialog) — „Bearbeitung einschränken“ in der Seitenleiste: Dokumentschutz einstellen und „Schutz starten …“; steht ein Schutz,
  - `__init__(parent, art)`
  - `_zustand(*_)`
  - `ergebnis()` — Die gewählte Art des Schutzes; None: kein Schutz (auch nach „Schutz beenden“).

### `ui/dialogs/verweise_dialoge.py`

Dialoge zu Verweisen: Textmarken, Quellen. (Beschriftung und Querverweis: ``verweise_fenster.py``.)

- `_knoepfe(dlg)`
- **class `TextmarkeDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, ed)`
  - `_fuellen()`
  - `_add()`
  - `_del()`
  - `_gehe()`
- **class `QuelleDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, q)`
  - `ergebnis()`
- **class `QuellenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, ed)`
  - `_fuellen()`
  - `_akt()`
  - `_neu()`
  - `_bearb()`
  - `_weg()`
  - `_zitat()`

### `ui/dialogs/verweise_fenster.py`

Fenster des Reiters Verweise nach den WPS-Vorlagen: „Inhaltsverzeichnis“, „Indexeintrag festlegen“, „Beschriftung“ (mit

- `_titel(text, feld)`
- **class `InhaltsverzeichnisDialog`**(PanelFaehig, QDialog) — Links Füllzeichen, Ebenen anzeigen, Seitenzahlen anzeigen/rechtsbündig, Hyperlinks verwenden; rechts die Seitenansicht.
  - `__init__(parent, opt)`
  - `kompakt_machen()` — In der Seitenleiste: die Seitenansicht unter den Einstellungen.
  - `ergebnis()`
  - `_auffrischen(*_)`
  - `_male(p, r)`
- **class `IndexeintragDialog`**(PanelFaehig, QDialog) — Haupt- und Untereintrag mit Sortierung, Optionen (Querverweis „Siehe“, aktuelle Seite, Seitenbereich über eine Textmarke),
  - `__init__(parent, vorschlag, marken, auswahl)`
  - `eintrag()`
  - `_melden(alle)`
  - `_auffrischen()`
- **class `NummerierungDialog`**(PanelFaehig, QDialog) — „Beschriftungsnummerierung“: Schreibweise der Nummer. Kapitelnummern kennt Lunivo noch nicht (grau).
  - `__init__(parent, zahl)`
  - `zahl()`
- **class `BeschriftungDialog`**(PanelFaehig, QDialog) — „Beschriftung“ wie die Vorlage: Feld mit „Tabelle 1“ zum Weiterschreiben, Bezeichnung, Position (nur bei markiertem Objekt),
  - `__init__(parent, eigene, naechste, objekt, label)`
  - `_vorspann()` — Den Anfang „Tabelle 1“ im Feld erneuern, Geschriebenes dahinter behalten.
  - `_neu()`
  - `_loeschen()`
  - `_nummerierung()`
  - `ergebnis()`
- **class `QuerverweisDialog`**(PanelFaehig, QDialog) — „Querverweis“ wie die Vorlage: Verweistyp, Verweisen auf, „Als Hyperlink einfügen“, „Oben/unten einschließen“, die Liste
  - `__init__(parent, ziele)`
  - `_art_gewaehlt(art)`
  - `_auffrischen()`
  - `ergebnis()`
  - `_melden()`

### `ui/dialogs/vorlagen_dialog.py`

Neu aus Vorlage: die mitgelieferten Gerüste und die Dateien aus dem Vorlagenordner.

- **class `VorlagenDialog`**(QDialog)
  - `__init__(parent, settings, kann_speichern)`
  - `_fuellen()`
  - `_ordner_waehlen()`
  - `_ordner_oeffnen()`
  - `_als_vorlage()`
  - `_ok()`

### `ui/dialogs/wasserzeichen_fenster.py`

Fenster „Wasserzeichen“ nach der WPS-Vorlage: oben Bildwasserzeichen, darunter Textwasserzeichen, Transparenz, rechts die Vorschau

- `_titel(text, feld)`
- `_feld(w, breite)`
- **class `WasserzeichenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, aktuell, page, ordner)`
  - `_lage_felder(g, kuerzel)` — Format, Horizontal und Vertikal (je Liste und Abstand vom Rand).
  - `_vorbelegen(a)`
  - `_art(an, andere)`
  - `_bild_waehlen()`
  - `bild_laden(pfad)`
  - `_zustand(*_a)`
  - `_male(p, r)`
  - `ergebnis()` — Das eingestellte Wasserzeichen; None, wenn keine Art angekreuzt ist (oder kein Bild bzw. kein Text da ist).
  - `bereich()`

### `ui/dialogs/welche_hilfe.py`

„Welche Hilfe wann“: die Stufen der Schreibhilfe von der Wellenlinie bis zur KI, die Etiketten der Funde und ein Weg durch einen Brief.

- `_text(text)`
- **class `HilfeWannDialog`**(PanelFaehig, QDialog)
  - `__init__(fenster)`
  - `_zeile(stufe, titel, kuerzel, frage, rechts, aktion, trenner)`
  - `_nachziehen(name, an)`

## `ui/dialogs/optionen_seiten`

### `ui/dialogs/optionen_seiten/__init__.py`

Die Seiten des Optionen-Fensters, je Thema ein Baustein (``ui/dialogs/optionen.py`` setzt sie zusammen).


### `ui/dialogs/optionen_seiten/ansicht.py`

Optionen: Ansicht und Darstellung.

- **class `AnsichtSeiten`** — Optionen: Ansicht und Darstellung. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/ui/dialogs/optionen.py``).
  - `_ansicht(titel)`
  - `_aussehen(p)` — Hell, Dunkel oder wie das System: drei große Schaltflächen, genau eine ist gewählt (kein ausgegrauter Zusatzschalter).
  - `_oberflaeche_wahl(p, f)`
  - `_darstellung(p, f)` — Schrift größer/kleiner, Weicher Kontrast, Größe der Symbole, Schrift der Bedienung.

### `ui/dialogs/optionen_seiten/befehle.py`

Optionen: Menüband, Schnellzugriff, Sicherheit.

- **class `BefehleSeiten`** — Optionen: Menüband, Schnellzugriff, Sicherheit. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/ui/dialogs/optionen.py``).
  - `_zwei_listen(p, links_kopf, rechts_kopf, hinzu, weg, kategorie)` — Gerüst der Vorlage: links „Befehle auswählen“ (Auswahl, Suche, Liste), in der Mitte Hinzufügen/Entfernen, rechts die Liste
  - `_schieben(liste, d)`
  - `_menueband(titel)`
  - `_schnellzugriff(titel)`
  - `_sicherheit(titel)`
  - `_verfolgen(titel)`

### `ui/dialogs/optionen_seiten/datei.py`

Optionen: Schreiben, Speichern, Drucken und PDF.

- **class `DateiSeiten`** — Optionen: Schreiben, Speichern, Drucken und PDF. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/ui/dialogs/optionen.py``).
  - `_schreiben(titel)` — Schrift für neuen Text, Prüfung, AutoKorrektur; im Einzelnen eingeklappt (alle AutoKorrektur-Fälle bleiben erhalten).
  - `_speichern(titel)`
  - `_zwischenstaende_loeschen()`
  - `_sicherungskopien_oeffnen()`
  - `_daten_sichern()`
  - `_daten_zurueckholen()`
  - `_drucken(titel)` — Drucken und PDF auf einer Seite: das Häufige sichtbar, der Rest eingeklappt.

### `ui/dialogs/optionen_seiten/gemeinsam.py`

Gemeinsame Werte der Bausteine.

- `erklaerung(name)` — Der Satz zu einer Einstellung (aus resources/daten/optionen_erklaerungen.json); leer, wenn es keinen gibt.
- **class `_Seite`**(QWidget) — Eine Optionenseite: Gruppen mit Zeilen; Werte stehen sofort in den Einstellungen.
  - `__init__(fenster, titel, offen)`
  - `gruppe(name)`
  - `mehr(name)` — Eingeklappter Bereich am Ende einer Seite; ``unter`` legt Gruppen hinein.
  - `unter(e, name)`
  - `haken(f, key, text, std, wirkt)`
  - `_zeile(f, c, text)` — Haken in die Gruppe setzen; gibt es einen Erklärsatz, steht er immer sichtbar darunter (nicht nur als QuickInfo).
  - `auswahl(f, key, label, werte, std, wirkt)`
  - `wahl(f, key, label, eintraege, std, wirkt)` — Auswahl mit Anzeigetext und gespeichertem Wert (Text oder Ja/Nein).
  - `schalter(f, text, ist, umschalten)` — Haken, der den Zustand eines anderen Teils des Programms zeigt und schaltet (Navigationsbereich, Gitternetzlinien …).
  - `eingabe(key, platzhalter)`
  - `felder(f, eintraege, spalten)` — Eingabefelder im Raster, jedes mit seinem Platzhalter als Beschriftung.
  - `pfad(f, key, text, platzhalter, wirkt)` — Ordner-Zeile: Beschriftung, darunter Feld und „Wählen …“.
  - `stufen(f, key, label, eintraege, std, wirkt)` — Auswahl aus benannten Stufen („normal“, „weit“ …), die als Zahl gespeichert werden.
  - `zahl(f, key, label, lo, hi, std, einheit, dezimal, wirkt)`
  - `zeile(f, text)`
  - `hinweis(text)`
  - `aktion(text, knopf, aktion, name)` — Zeile mit Text und Knopf in der Gruppe, die zuletzt begonnen wurde.
  - `haken_aus(f, text, grund, an)` — Ein Haken, den es in der ersten Fassung gab und der hier noch nichts bewirkt: grau, mit Grund.
  - `abschluss()`
- **class `_Karte`**(QFormLayout) — Zeilen einer Gruppe. Haken stehen wie in der ersten Fassung zu zweit nebeneinander, mit Linie zwischen den Zeilen;
  - `__init__(eltern)`
  - `addRow(*args)`
  - `aktion(text, knopf, aktion, name)` — Zeile aus Text und darunter einem Knopf („Den Text hören“ / „Stimme und Tempo …“).
  - `ende()` — Unterste Linie der letzten Haken-Zeile weg (die Karte hat selbst einen Rand); halbe Zeile mit Platz auffüllen.

### `ui/dialogs/optionen_seiten/lesen.py`

Optionen: Leichter lesen, Sprache.

- **class `LesenSeiten`** — Optionen: Leichter lesen, Sprache. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/ui/dialogs/optionen.py``).
  - `_lesehilfe(titel)`
  - `_silbentrennung_haken(p, f)` — Haken „Silbentrennung“: gilt für das Dokument, das gerade offen ist (derselbe Schalter wie im Reiter Schreibhilfe).
  - `_lese_schriften(p, e)` — Die drei Schriften zum leichteren Lesen mit Probe; sagt, ob sie da sind.
  - `_uebersetzung_oeffnen()`

### `ui/dialogs/optionen_seiten/lunivo.py`

Optionen: KI, Gedächtnis, Erweitert.

- **class `LunivoSeiten`** — Optionen: KI, Gedächtnis, Erweitert. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/ui/dialogs/optionen.py``).
  - `_ki(titel)`
  - `_gedaechtnis(titel)`
  - `_erweitert(titel)`

### `ui/dialogs/optionen_seiten/name_ki.py`

Optionen: Name und KI, dazu die Werkzeug-Fenster (Menüband, Schnellzugriff, Kennwort, Änderungen verfolgen).

- **class `NameKiSeiten`** — Optionen: Name und KI. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/ui/dialogs/optionen.py``).
  - `_name_ki(titel)`
  - `_anpassen(key)` — Eines der Werkzeuge als Fenster zeigen; das Band wird danach neu gebaut, wenn es sich geändert hat.

## `ui/document`

### `ui/document/__init__.py`

Dokumentbereich: Editor, Seitenfläche, Dokumentreiter, Lineal, Navigation.


### `ui/document/base.py`

- `_ziel_fragment(html, standard)` — HTML einfügen, aber Schriftart, -größe, Farben und Hintergründe des Ziels behalten.

### `ui/document/blasen_flaeche.py`

Die Fläche neben der Seite, auf der die Sprechblasen des Editors stehen (Kommentare, verfolgte Änderungen).

- **class `BlasenFlaeche`**(QWidget)
  - `__init__(editor)`
  - `grundfarbe()` — Der Grund der Fläche ist derselbe wie rund um das Blatt (der Hintergrund des Dokumentfensters) — der Streifen ist also nicht zu sehen, nur die Blasen darauf.
  - `paintEvent(e)`
  - `_blase_bei(pos)`
  - `mousePressEvent(e)`
  - `_menue(bl, pos)`
  - `mouseDoubleClickEvent(e)`

### `ui/document/document_area.py`

Ein geöffnetes Dokument: Editor auf grauem Arbeitsgrund, Pfad, Meta, Wiederherstellungs-Kennung.

- **class `DocumentTab`**(QScrollArea)
  - `__init__(loaded, path, title)`
  - `set_layout(art)` — blatt (Drucklayout) \| web (Weblayout) \| doppelt (Zwei Seiten, nur Ansicht).
  - `resizeEvent(ev)`
  - `_rand(seite, mm)`
  - `zeige_lineale(waagerecht, senkrecht)`
  - `_lineale_anordnen()` — Lineale in den Rand des Viewports legen; nur im Drucklayout (Weblayout und Zwei Seiten haben keine Blattkanten).
  - `_lineale_neu_zeichnen(*_)`
  - `zoom_breite()` — Seitenbreite: die Seite füllt die Breite des Fensters.
  - `zoom_seite()` — Eine Seite: die ganze Seite ist sichtbar.
  - `page()`
  - `is_modified()`
  - `set_path(path)`

### `ui/document/document_editor.py`

Der Editor: QTextEdit mit Seitenbreite, Formatierungsbefehlen und Seitenzählung.

- `_ziel_fragment(html, standard)` — HTML einfügen, aber Schriftart, -größe, Farben und Hintergründe des Ziels behalten (Fett, Kursiv, Verweise bleiben).
- **class `DocumentEditor`**(AnzeigeBaustein, SpaltenBaustein, SeitenBaustein, FormatierungBaustein, BilderBaustein, SchreibhilfeBaustein, FreieBilderMixin, ZusatzMixin, QTextEdit)
  - `__init__(parent)`
  - `_verbinde_groesse()`
  - `_passe_hoehe_an(*_)`
  - `_blatt_anzahl()` — Anzahl der Blätter: so viele, wie der Textfluss des Editors Seiten braucht (plus Noten-Seiten, die nur der Druck anhängt).
  - `_aussen()`
  - `_scroll_outer()`
  - `set_document_and_page(doc, page)`
  - `apply_page(page)`
  - `focusInEvent(e)`
  - `mousePressEvent(e)`
  - `dragMoveEvent(e)`
  - `dropEvent(e)`
  - `mouseMoveEvent(e)`
  - `mouseDoubleClickEvent(e)`
  - `resizeEvent(e)`
  - `wheelEvent(e)`
  - `contextMenuEvent(e)`
  - `mouseReleaseEvent(e)`
  - `paintEvent(e)`
  - `keyPressEvent(e)`
  - `_teilen_vorher(e)` — Enter teilt einen Absatz: Absatznummer, wenn der Absatz einen Seiten-/Spaltenumbruch davor oder ein Abschnittsende trägt.
  - `_teilen_danach(nr)` — Qt kopiert das Absatzformat in den neuen Absatz. Der Umbruch davor gilt nur für den ersten Teil (sonst macht jedes Enter ein
  - `focusOutEvent(e)`
  - `insertFromMimeData(source)`
  - `_einfuegen_mit(source, modus, neu)` — Einfügen als EIN Rückgängig-Schritt; danach bietet die kleine Schaltfläche die anderen Formen an (Optionen ▸ Bearbeiten).
  - `_einfuegen_schaltflaeche(quelle, start, ende, modus)`
  - `_einfuegen_neu(quelle, start, modus)`
  - `_paste_btn_pruefen()`

### `ui/document/document_tabs.py`

Dokumentreiter ganz oben (mit „+“) und der Stapel der Dokumente darunter.

- **class `DocTabs`**(QObject) — Wie ein QTabWidget, nur dass Reiterleiste und Inhalt getrennt eingebaut werden.
  - `__init__()`
  - `_moved(von, nach)`
  - `_bar_changed(i)`
  - `addTab(w, title)`
  - `count()`
  - `widget(i)`
  - `currentIndex()`
  - `currentWidget()`
  - `setCurrentIndex(i)`
  - `setCurrentWidget(w)`
  - `setTabText(i, t)`
  - `setTabIcon(i, icon)`
  - `tabText(i)`
  - `setTabToolTip(i, t)`
  - `removeTab(i)`

### `ui/document/editor_anzeige.py`

Anzeige: Sprechblasen, ausgeblendeter Text, Lesehilfe.

- **class `AnzeigeBaustein`** — Anzeige: Sprechblasen, ausgeblendeter Text, Lesehilfe. Baustein von ``DocumentEditor`` (siehe ``lunivo_writer/ui/document/document_editor.py``).
  - `blasen_konfig()`
  - `blasen_rand()`
  - `blasen_linien()`
  - `_blasen_da()`
  - `_blasen_einrichten()` — Seitenrand für die Blasen: Fläche neben der Seite (setViewportMargins), nur wenn es Blasen gibt.
  - `_blasen_geometrie()`
  - `blasen_layout(breite)` — [(Blase, Rechteck in der Blasenfläche, y der Textzeile)] — gestapelt, ohne sich zu überlappen.
  - `kommentar_bearbeiten(kid)` — Doppelklick auf eine Blase: den Kommentar in der Karte links bearbeiten.
  - `set_versteckt_zeigen(an)`
  - `ist_versteckt()`
  - `_fragmente_in(von, bis)`
  - `set_versteckt(an)` — Markierung (oder Wort am Zeiger) als ausgeblendeten Text formatieren / zurücknehmen.
  - `set_zeilenfokus(an)`
  - `set_marken(an)`
  - `set_lesehilfe(papier, buchstaben, wort)`
  - `set_zeilenluft(faktor)` — Lesehilfe „Zeilenluft“: nur in dieser Anzeige; gespeichert und gedruckt wird ohne (editor/lese_zeilenluft.py).
  - `set_lesefokus(wachstum, blasse)` — wachstum: 1,0 / 1,05 / 1,10 für den Absatz, in dem die Schreibmarke steht; blasse: 1,0 / 0,62 / 0,38 für den übrigen Text.
  - `_lese_aktiv()`
  - `_lese_neu(*_, erzwingen)`
  - `_lese_blasse_auswahl()` — Zusatzauswahl, die den Text außerhalb des aktuellen Absatzes in die Farbe des Papiers mischt (nur der sichtbare Bereich).
  - `_lese_wachstum_zeichnen()` — Der Absatz an der Schreibmarke wird ein wenig größer gezeichnet (aus der Mitte, ohne den Umbruch zu ändern): sein
  - `_aenderungszeilen_gecacht()`
  - `_kapitel_je_blatt(pg)` — Kapitelnummer je Blatt für die Seitenzahl („2-1“), nur wenn die Einrichtung sie verlangt; gemerkt je Textstand.
  - `_extras_zeichnen(p, sp)` — Objektanker, Änderungsbalken, Kopf- und Fußzeile im Rand der Seite.

### `ui/document/editor_bilder.py`

Bilder im Text.

- **class `BilderBaustein`** — Bilder im Text. Baustein von ``DocumentEditor`` (siehe ``lunivo_writer/ui/document/document_editor.py``).
  - `_bild_cursor()`
  - `bild_format()`
  - `bild_setzen(width, height, alt)`
  - `_wortweise()` — Wortweise markieren: eine mit der Maus gezogene Auswahl wird an Wortgrenzen erweitert.
  - `_cursor_at(pos)`

### `ui/document/editor_formatierung.py`

Zeichen- und Absatzformat, Einfügen, Suchen.

- **class `FormatierungBaustein`** — Zeichen- und Absatzformat, Einfügen, Suchen. Baustein von ``DocumentEditor`` (siehe ``lunivo_writer/ui/document/document_editor.py``).
  - `_merge(fmt)`
  - `toggle_bold(on)`
  - `toggle_italic(on)`
  - `toggle_underline(on)`
  - `set_underline_style(stil)`
  - `set_outline(an)`
  - `set_letter_spacing(px)`
  - `set_capitalization(cap)`
  - `toggle_strike(on)`
  - `set_script(kind)`
  - `set_font_family(family)`
  - `set_font_size(pt)`
  - `grow_font(delta)`
  - `set_text_color(color)`
  - `set_highlight(color)`
  - `change_case(mode)`
  - `clear_formatting()`
  - `_block_merge(fn)`
  - `set_alignment(al)`
  - `change_indent(delta_mm)`
  - `set_page_break_before(an)`
  - `set_indents(left_mm, right_mm, first_mm)`
  - `standard_tab_mm()` — Standardtabstopps des Dokuments (Abstand in mm).
  - `set_standard_tab_mm(mm)`
  - `set_absatzopt(w)` — Absatzoptionen (Umbruchregeln, Zeilenumbruch, Zeichenabstand, Raster) der markierten Absätze setzen.
  - `set_tabstopps(stopps)` — Tabstopps als Liste aus (Millimeter, Ausrichtung, Füllzeichen) setzen.
  - `set_line_spacing(factor)`
  - `set_line_height(art, wert)` — Zeilenabstand: ``faktor`` (Vielfaches), ``mindestens`` oder ``genau`` (Punkt).
  - `set_paragraph_spacing(before_pt, after_pt)`
  - `toggle_list(kind, style)`
  - `list_remove(nur_qt)` — Aufzählung/Nummerierung vom Absatz an der Schreibmarke (bzw. der Auswahl) nehmen.
  - `list_level(delta)`
  - `apply_style(name)` — Formatvorlage auf alle Absätze der Markierung (oder den Absatz am Zeiger) anwenden.
  - `_stil_auf_block(blk, name)`
  - `_zeichen_der_vorlage(d)` — Das Zeichenformat einer Vorlage (alle Felder des Fensters „Schriftart“). Was die Vorlage nicht setzt, bleibt in der Auswahl, wie es ist.
  - `_ebene_der_vorlage(blk, name)` — „Verbinden mit Formatvorlage“ (Gliederung anpassen): ein Absatz mit dieser Vorlage gehört zur verbundenen Ebene der Gliederung.
  - `stil_tasten()` — Die Tastenkombinationen der Formatvorlagen (nur gültig, solange der Editor den Fokus hat).
  - `_liste_auf_block(blk, text)` — Absatz einer Formatvorlage mit Liste: aufeinanderfolgende Absätze mit derselben Liste zählen gemeinsam.
  - `liste_spec()` — Die Liste des Absatzes an der Schreibmarke (siehe ``editor.listen``) oder None.
  - `_mehrstufig_am_zeiger()` — (Ebene, Gliederung) des Absatzes an der Schreibmarke, wenn er zu einer mehrstufigen Liste gehört.
  - `set_mehrstufig(defn, ebene_nr)` — Die markierten Absätze in eine mehrstufige Liste setzen (``defn=None``: herausnehmen). Der Text rückt ein, die Nummer steht davor.
  - `set_liste(spec)` — Liste setzen: ändert die Liste des Absatzes (alle ihre Absätze) oder legt für die Auswahl eine neue an; None nimmt sie weg.
  - `_nummern_zeichen(lst, zeichen)` — Schrift der Nummern: Qt zeichnet sie mit dem Zeichenformat des Absatzes.
  - `stil_neu_anwenden(name)` — Nach „Formatvorlagen verwalten“: alle Absätze dieser Vorlage im Dokument neu formatieren.
  - `_stil_name(bf)`
  - `stil_aus_auswahl()` — Definition für eine neue Formatvorlage nach dem Absatz, in dem die Schreibmarke steht.
  - `_absatz_felder(bf)` — Die Felder des Fensters „Absatz“ (außer Ausrichtung, Einzug links, Abstände), als Felder einer Formatvorlage.
  - `_zeichen_felder(cf)` — Die Felder des Fensters „Schriftart“ (ohne Schrift, Größe, Schnitt, Farbe) eines Zeichenformats, als Felder einer Formatvorlage.
  - `_rahmen_felder()` — Rahmen und Schattierung des Absatzes an der Schreibmarke als Felder einer Formatvorlage.
  - `stil_entfernen(name)` — Eine gelöschte eigene Vorlage: die Absätze behalten ihr Aussehen, verlieren aber die Zuordnung.
  - `current_style()`
  - `insert_page_break()`
  - `insert_column_break()`
  - `insert_table(rows, cols, borders, spaltenbreite)` — Tabelle an der Schreibmarke; ``spaltenbreite`` (Bildpunkte): feste Spalten, sonst passt sie sich der Seitenbreite an.
  - `insert_image(path)`
  - `insert_link(url, text, tipp)` — Link an der Schreibmarke; mit Markierung wird sie zum Link. ``tipp``: QuickInfo beim Überfahren.
  - `find_text(text, backwards, case, whole)`
  - `replace_current(find, repl, case)`
  - `_format_am_anfang(cur)` — Das Zeichenformat des ersten Zeichens der Markierung (``charFormat()`` eines Cursors mit Markierung wäre das davor).
  - `replace_all(find, repl, case, whole)`

### `ui/document/editor_gemeinsam.py`

Gemeinsame Werte der Bausteine.


### `ui/document/editor_schreibhilfe.py`

Schreibhilfe im Text.

- **class `SchreibhilfeBaustein`** — Schreibhilfe im Text. Baustein von ``DocumentEditor`` (siehe ``lunivo_writer/ui/document/document_editor.py``).
  - `cut()`
  - `set_wellen(funde)`
  - `replace_range(von, bis, neu, erwartet)`
  - `select_range(von, bis)`
  - `_wort_vor_cursor()`
  - `_vorschlaege_zeigen()`
  - `_vorschlag_nehmen(wort)`
  - `_autokorr_anwenden()`
  - `_folge_vorher(e)` — Return am Ende eines Absatzes, dessen Vorlage einen „folgenden Absatz“ kennt → (Name der Folgevorlage, Absatznummer).
  - `_folge_danach(folge, nr)`
  - `_taste(e)`
  - `_rechts_leerzeichen_weg(c)` — AutoKorrektur: Leerzeichen am Ende einer rechtsbündigen Zeile würden den Text nach links schieben — sie werden entfernt.
  - `_kreiszahl()` — AutoKorrektur: „(1)“ … „(20)“ werden zu ① … ⑳ (Optionen ▸ Bearbeiten ▸ AutoKorrektur).
  - `_autoformat_liste()` — „1. “ / „1) “ am Absatzanfang → Nummerierung, „* “ / „- “ / „• “ → Aufzählung.
  - `_autokorr_extras()` — Netzadressen → Hyperlinks; Leerzeichen am Absatzanfang → Erstzeileneinzug.

### `ui/document/editor_seiten.py`

Abschnitte, Seitenzählung, Paginierung.

- **class `SeitenBaustein`** — Abschnitte, Seitenzählung, Paginierung. Baustein von ``DocumentEditor`` (siehe ``lunivo_writer/ui/document/document_editor.py``).
  - `seite_letzter_block()` — Der letzte Absatz, der auf dem Blatt der Schreibmarke beginnt (für „Leere Seite“: das neue Blatt kommt dahinter).
  - `abschnitt_nr()`
  - `abschnitt_seite(nr)` — Kopie der Einrichtung des Abschnitts `nr` (Vorgabe: des aktuellen).
  - `kopffuss()` — Der Bearbeiter für Kopf- und Fußzeile direkt auf der Seite (siehe ``kopffuss_bearbeiter``).
  - `abschnitt_einfuegen(typ)`
  - `abschnitt_entfernen()`
  - `abschnitt_gehe(nr)`
  - `_recount()` — Seitenzahl und Seitenwechsel neu bestimmen. Die Blätter selbst entstehen aus dem Textfluss des Editors; die
  - `_seitenwechsel(d)` — Zeichenstellen, an denen eine neue Seite beginnt (erste Zeile der Seiten 2, 3, …).
  - `seitenwechsel()`
  - `page_count()`
  - `current_page()` — Blatt, auf dem die Schreibmarke steht (so, wie es im Editor angezeigt wird).
  - `_cursor_moved()`
  - `set_silbenfarben(konfig)` — Silben farbig (reine Anzeige, ändert das Dokument nicht); konfig None oder an=False schaltet ab.
  - `word_count()`

### `ui/document/editor_spalten.py`

Spalten im Editor.

- **class `SpaltenBaustein`** — Spalten im Editor. Baustein von ``DocumentEditor`` (siehe ``lunivo_writer/ui/document/document_editor.py``).
  - `_blatt_aktiv()` — Blattmodus (Drucklayout): echte Blätter mit Rand und Zwischenraum; nur das Weblayout ist ein Endlosfluss.
  - `_mehrspaltig()`
  - `_sp_geo()` — Maße des Textflusses und (bei gleich großen Blättern) jedes Blattes. Bei verschieden großen Blättern (``_qplan``) sind
  - `blatt_oben(nr)` — y des oberen Randes von Blatt `nr` (0-basiert) im Editor — die Lineale richten sich danach.
  - `_blatt(k)` — Maße von Blatt `k` im Editor (mit Zoom): x (linker Blattrand), W, H, ml, mt, mb, cw (Textbreite), ch (Texthöhe), pg.
  - `_q_oben()` — Obere Blattränder bei verschieden großen Blättern (zwischengespeichert je Plan und Zoom).
  - `_quer_auffrischen()` — Plan der Blattgrößen neu bestimmen (nur einspaltig, nicht im Weblayout). → True, wenn sich Breite oder Fluss geändert haben.
  - `_blatt_bei_y(vy)`
  - `_sp_ursprung(lp)` — Ecke links oben der Textspalte, in der die logische Seite `lp` des Textflusses steht (Editorkoordinaten).
  - `_sp_einrichten()` — Dokument in Spaltenbreite und -höhe legen: feste Zeilenbreite, damit QTextEdit die Seitenhöhe nicht wieder auf „endlos“ setzt.
  - `_sp_view(dx, dy)` — Dokumentkoordinate (fortlaufender Fluss der Spaltenseiten) → Punkt auf dem Blatt.
  - `_sp_doc(vx, vy)` — Punkt auf dem Blatt → Dokumentkoordinate; Punkte in Rändern und Lücken landen in der nächsten Spalte.
  - `_sp_neu_zeichnen(*_)`
  - `_sp_blinken()`
  - `cursorRect(*args)`
  - `cursorForPosition(pos)`
  - `anchorAt(pos)`
  - `_maus_abgebildet(e)` — Mausereignis mit Dokumentkoordinaten (nur bei Spalten); QTextEdit selbst rechnet in Dokumentkoordinaten.
  - `_ziehen_abgebildet(e)` — Ziehen/Ablegen: QTextEdit rechnet in Dokumentkoordinaten, der Editor zeigt aber Blätter → Position abbilden.
  - `_kopffuss_zone(y)` — „kopf“ im oberen, „fuss“ im unteren Rand der Seite (nur Seitenansicht, nicht im Weblayout).
  - `_arbeitsflaeche()` — Grauer Arbeitsbereich zwischen und um die Blätter (gleich dem Grund hinter dem Editor).
  - `_blatt_zeichnen(e)` — Arbeitsfläche, Blätter mit Schatten, dann Text, Auswahl, Schreibmarke und Wellenlinien: jede Seite des Textflusses
  - `set_web(an)`
  - `set_web_breite(px)`
  - `set_gliederung(an)` — Gliederungsansicht: nur Überschriften sind sichtbar; der Text dazwischen ist ausgeblendet (nicht gelöscht).
  - `gliederung_ebene(delta)` — Überschrift hoch-/herabstufen (Gliederung): Ebene 1..6, darüber/darunter wird sie zu Text/Titel.
  - `set_zeilennummern(an)`
  - `_zeilennummern_zeichnen(p)`
  - `apply_design(fliess, kopf, farbe)` — Design: Schriftart für Text und Überschriften, Farbe der Überschriften — für das ganze Dokument.
  - `set_absatzrahmen(wert)`
  - `absatzrahmen()` — Der Rahmen des Absatzes an der Schreibmarke (bei Auswahl: des ersten Absatzes) als ``Linie``, sonst None.
  - `set_absatzschatten(fuell, muster)` — Füllung (und Muster darüber) der markierten Absätze; ``None`` und kein Muster nehmen sie weg.
  - `absatzschatten()` — (Füllfarbe oder None, (Musterschlüssel, Musterfarbe) oder None) des Absatzes an der Schreibmarke.
  - `toggle_rtl()`
  - `_fluss_planen()`
  - `_seitenfluss()` — Umbruchregeln (Zusammenhalten, nicht vom nächsten Absatz trennen, Absatzkontrolle) auf die Seiten anwenden.
  - `_hat_effekt()` — Gibt es Textstücke mit Effekten, die Lunivo selbst zeichnet (Verlauf, Schatten, Spiegelung, Leuchten, 3D)? Das Ergebnis gilt bis zur nächsten Änderung.
  - `_hat_tabfuell()`
  - `_hat_mehrstufig()`
  - `_hat_rahmen()`
  - `set_gitter(an)`
  - `seitenspannen()` — Senkrechte Bereiche (von, bis) jedes Blattes im Editor.
  - `_wasserzeichen_je_blatt()` — Wasserzeichen je Blatt, wenn ein Abschnitt ein eigenes hat („Übernehmen für: Aktueller Abschnitt“); sonst None.
  - `_deckblatt_grafik(p, k, blatt)` — Ganzseitiges Bild (Deckblatt, ``editor/deckblatt.py``) des Blattes ``k`` auf die Blattfläche, vor dem Text.
  - `_schmuck_zeichnen(p)`
  - `_gitter_zeichnen(p)`
  - `seitenfarbe_anwenden()`
  - `set_zoom(faktor)` — Ansicht vergrößern/verkleinern. Das Dokument selbst (Schriftgrößen, Maße) bleibt unverändert.
  - `page_settings_changed(page)` — Seiteneinrichtung ändern — für den Abschnitt, in dem die Schreibmarke steht (der erste Abschnitt ist das Dokument).

### `ui/document/freie_bilder_bedienung.py`

Frei positionierte Bilder im Editor: zeichnen, anklicken, verschieben, in der Größe ändern, löschen (siehe editor/freie_bilder.py).

- **class `FreieBilderMixin`**
  - `_frei_sel()`
  - `_frei_sel(wert)`
  - `_frei_init()`
  - `_frei_schluessel(a)`
  - `_frei_liste()` — Alle frei positionierten Bilder aller Blätter: (Schlüssel, Angabe, Bild, Rechteck im Editor, hinter, Blatt-Nr.). Unabhängig davon, was
  - `_frei_zeichnen(p, sicht, hinter)` — Bilder der sichtbaren Blätter, hinter (``hinter``) oder vor dem Text; die vorderen zeichnen auch die Auswahl.
  - `_frei_text_markieren(p, r, a, bild)` — WordArt wie in WPS: der Text im gewählten Objekt ist grau hinterlegt (nur der Text, kein Kasten über dem Objekt).
  - `_frei_rechteck(a, n)`
  - `_frei_leiste()` — Die Schaltflächen neben dem markierten Objekt: für Bilder und Diagramme eigene, sonst die der Formen und WordArt.
  - `_frei_knopf_rects(r)` — Die Schaltflächen rechts neben dem Bild: oben der Minus-Knopf (klappt sie ein), darunter Layoutoptionen, Formstile, Füllung, Kontur.
  - `_frei_auswahl_zeichnen(p, r, a)`
  - `_frei_angabe()` — Die Angabe des gewählten freien Objekts (oder None).
  - `_frei_abbilden(r, a, rr)` — Ein Rechteck in logischen Bildpunkten des Objekts (Breite ``b`` × Höhe ``h``) in Editor-Koordinaten (Zoom, Lage) umrechnen.
  - `_frei_sa_geo(a)` — Rechtecke der SmartArt-Knoten (logisch), zwischengemerkt, bis sich Knoten oder Größe ändern.
  - `_frei_knoten_rect(r)` — Der gewählte SmartArt-Knoten in Editor-Koordinaten (ohne Drehung) oder None.
  - `_frei_teile_zeichnen(p, r, a)` — Rahmen mit kleinen runden Griffen um den gewählten Diagrammteil bzw. SmartArt-Knoten (dünner als der Rahmen des Objekts).
  - `_frei_adj_lagen(r, a)` — Lage der Anpassungsgriffe (gelbe Raute) der gewählten Form in Editor-Koordinaten: {"adj0": Punkt, …}; leer bei anderen Objekten.
  - `_frei_dunkel(name)` — Das Symbol dunkel gefärbt: die Knöpfe am Bild sind immer weiß, auch im dunklen Design (dort wären die Symbole sonst hell auf weiß).
  - `_frei_griff_mitte(r, name)`
  - `_frei_griff_bei(pos)`
  - `_frei_text_bei(pos)` — Liegt an dieser Stelle Text? Dann gehört der Klick dem Text, nicht einem Bild dahinter.
  - `_frei_bild_bei(pos, auch_hinten)`
  - `_frei_maus(e, art)` — True, wenn das Ereignis ein Bild betrifft und der Editor es nicht weiter behandeln soll.
  - `_frei_ziehen(e)`
  - `_frei_adj_vorschau(a0, i, wert)` — Die Form beim Ziehen der gelben Raute laufend neu zeichnen (nur das Bild, kein Dokumentschritt).
  - `_frei_ablegen()`
  - `_frei_absatz_aendern(blk, idx, neu)` — Ändert (oder, mit ``neu=None``, entfernt) die Angabe ``idx`` am Absatz ``blk`` — als ein Schritt, den Rückgängig zurücknimmt.
  - `_frei_teil_klick(pos, a)` — Ein Klick in das markierte Diagramm wählt den Teil darunter, in das markierte SmartArt den Knoten darunter.
  - `_frei_teilwahl_aufheben()` — Vor dem Abwählen des Objekts: den gewählten Diagrammteil bzw. SmartArt-Knoten wieder abwählen.
  - `_frei_teil_tipp(e, pos, griff)` — Beim Überfahren des markierten Diagramms steht der Name des Teils unter der Maus im Tooltip.
  - `frei_knoten_edit_starten(text)` — Ein Eingabefeld über dem gewählten SmartArt-Knoten (Doppelklick, Enter oder Tippen). ``text``: bereits getippte Zeichen werden hinter den
  - `_frei_knoten_edit_ende(verwerfen)` — Das Eingabefeld schließen und den Text in den Knoten übernehmen (``verwerfen``: nicht übernehmen).
  - `_frei_knopf(name, pos)`
  - `_frei_befehl_knopf(name, pos)` — Bild: Vergrößern (Ansicht mit Zoom) und Zuschneiden; Diagramm: Elemente, Stile, Einstellungen (Datenfenster) — jeweils der Befehl des Bandes.
  - `_frei_anker_menue(pos)` — Menü des Absatz-Symbols links vom Rahmen: Absatzformat zurücksetzen, Symbol ausblenden.
  - `_frei_anker_ausblenden()`
  - `_frei_absatz_zuruecksetzen()` — Der Absatz, an dem das Objekt hängt, bekommt Ausrichtung, Einzüge und Abstände zurück (das Objekt bleibt).
  - `_frei_wirken(**teile)`
  - `_frei_formstile(pos)`
  - `frei_formstile_menue(parent, ed)`
  - `_frei_formatierung(reiter)` — Zahnrad der Schnellleiste und Rechtsklick „Formatieren“: die Seitenleiste „Formatierung“ für das gewählte Objekt (Diagramm, SmartArt, Form, Bild …).
  - `_frei_effekte()` — „Weitere Effekte …“: die Seitenleiste „Formatierung“ mit den Effekten.
  - `_frei_fuell(pos)`
  - `frei_fuell_menue(parent, ed)`
  - `_frei_fuell_fenster(art)` — „Fülleffekte“, „Weitere Farbverläufe/Texturen/Muster“: die Seitenleiste „Formatierung“ auf „Füllung und Linie“ mit dieser Füllungsart.
  - `_frei_kontur(pos)`
  - `frei_kontur_menue(parent, ed)`
  - `_frei_linien_fenster()` — „Weitere Linien …“: die Seitenleiste „Formatierung“ auf dem Reiter „Füllung und Linie“ (Farbe, Breite, Strichart).
  - `bild_layout_popup(global_pos)`
  - `_frei_layout_popup(global_pos)`
  - `bild_layout_dialog()` — Das Fenster „Layout“ für das markierte Bild (frei oder im Text).
  - `_frei_taste(e)`

### `ui/document/freiform_bedienung.py`

Punkte einer Form bearbeiten mit der Maus (Zeichentools ▸ Form bearbeiten ▸ Punkte bearbeiten); Rechnen in ``editor/freiform.py``.

- `aktiv(ed)`
- `starten(ed)` — Die gewählte Form in eine Freiform umwandeln (falls nötig; ein Schritt für Rückgängig) und den Modus einschalten.
- `beenden(ed)`
- `_eintrag(ed)`
- `_punkte(ed, a)`
- **class `_Abb`** — Anteil (0..1) im Zeichenrechteck der Form ↔ Bildschirm (Editorkoordinaten) für ein Objekt (Zoom, Lage, Drehung).
  - `__init__(a, r)`
  - `zu_schirm(x, y)`
  - `zu_anteil(pos)`
- `_punkt_bei(punkte, abb, pos)` — Index des Punkts (oder Steuerpunkts) unter der Maus; Punkte gehen vor Steuerpunkten.
- `zeichnen(ed, p, r, a)` — Punkte (Quadrate), Steuerpunkte (Kreise mit Haltelinie) und den gewählten Punkt (gefüllt) der Form.
- `_speichern(ed, punkte)`
- `_vorschau(ed, key, a, punkte)` — Das Bild der Form mit den vorläufigen Punkten neu zeichnen — ohne Dokumentschritt.
- `maus(ed, e, art)` — True, wenn das Ereignis zum Bearbeiten der Punkte gehört (art: press, move, release, doppel).
- `taste(ed, e)` — Esc beendet den Modus, Entf/Rücktaste löscht den gewählten Punkt (nie die ganze Form).

### `ui/document/kopffuss_bearbeiter.py`

Kopf- und Fußzeile direkt auf der Seite bearbeiten (Einfügen ▸ Kopf- und Fußzeile, Doppelklick in den Seitenrand).

- `_symbol(art)` — Aktionssymbol aus dem zentralen Lucide-Katalog.
- **class `_Linie`**(QWidget) — Gestrichelte graue Linie über die ganze Blattbreite, an der der Kopf-/Fußbereich endet.
  - `__init__(eltern)`
  - `paintEvent(e)`
- **class `_EinfuegenPanel`**(QMenu) — Aufklappfeld „Seitenzahl einfügen“: Format, Position (fünf Kacheln mit Seitenbildchen), Übernehmen für, OK.
  - `__init__(eltern)`
  - `ort_setzen(ort)`
  - `_ok()`
- **class `_Feld`**(QPlainTextEdit) — Das Textfeld über dem Kopf- bzw. Fußbereich: randlos, gestrichelter Rahmen, Esc beendet.
  - `__init__(eltern, zone)`
  - `_feld_format(art)`
  - `felder_setzen(text, zahlen)` — Den Text mit {PAGE}/{PAGES} ins Feld schreiben; die Felder erscheinen als ``zahlen["PAGE"]`` bzw. ``zahlen["PAGES"]``.
  - `text_lesen()` — Der Text, in dem jedes Feld wieder als {PAGE}/{PAGES} steht.
  - `_feld_bei(pos)` — (Anfang, Ende) des Feldes, das die Zeichen vor/hinter ``pos`` berührt, sonst None — getrennt nach 'davor' und 'dahinter'.
  - `focusInEvent(e)`
  - `keyPressEvent(e)`
  - `paintEvent(e)`
- **class `_Leiste`**(QWidget) — Die schwebende Leiste neben dem Etikett des aktiven Bereichs: mit Seitenzahl drei Knöpfe, ohne nur „Seitenzahl einfügen“.
  - `__init__(eltern)`
  - `zahl_zeigen(mit)` — Mit Seitenzahl: drei Knöpfe; ohne: nur „Seitenzahl einfügen“ (beides linksbündig, direkt neben dem Etikett).
  - `natuerliche_breite()`
- **class `KopfFussBearbeiter`**(QObject)
  - `__init__(editor)`
  - `feld()` — Das Feld des aktiven Bereichs (``zone``); None, solange noch nie gestartet.
  - `_teile()`
  - `starte(zone, blatt)`
  - `beende()`
  - `wechseln()` — Zwischen Kopf- und Fußzeile springen: Schreibmarke ins andere Feld, die Leiste zieht mit.
  - `abschnitt_springen(schritt)` — Zur Kopfzeile des vorigen/nächsten Abschnitts; → False, wenn es keinen gibt.
  - `_fokus(zone)` — Klick/Schreibmarke in den anderen Bereich: die Leiste und das Absatz-Symbol ziehen dorthin.
  - `_cursor_blatt()`
  - `_art(page)` — "first", "even" oder "": welche Kopf-/Fußzeile das Blatt trägt (siehe ``PageSettings.kopf_fuss_art``).
  - `_name(page, zone)`
  - `_etikett(page, zone)`
  - `hf(page, zone)`
  - `_laden()` — Beide Felder (Kopf und Fuß) des aktuellen Blatts füllen.
  - `_leiste_laden(page)`
  - `_ausrichten(zone, align)`
  - `_geaendert()`
  - `speichern()` — Den Text des Feldes in die Seiteneinrichtung des Abschnitts schreiben (sofort; sonst nach kurzer Pause beim Tippen).
  - `aendern(aendere, neu_laden)` — ``aendere(page)`` auf die Einrichtung des aktuellen Abschnitts anwenden und speichern; → danach das Feld neu füllen.
  - `ausrichtung_setzen(align)`
  - `tabstopp_einfuegen()`
  - `_rect(zone)`
  - `_platzieren()`
  - `eventFilter(o, e)`
  - `_menues()`
  - `_menue_neu(m)`
  - `seitenzahl_einfuegen(ausr, muster, zahl, bereich)` — Seitenzahl in die Zeile setzen, die gerade bearbeitet wird („Seitenzahl einfügen ▾“); ``bereich``: dokument \| seite \| abschnitt.
  - `_start_setzen(n)`
  - `_menue_format(m)`
  - `_menue_loeschen(m)`
  - `seitenzahl_loeschen(art)` — Seitenzahl entfernen: "dokument" (alle Abschnitte), "abschnitt", "aktuelle", "auf", "von" (siehe ``seitenzahl_loeschen_bereich``).
  - `_hinweis(text)`

### `ui/document/lineal.py`

Waagerechtes und senkrechtes Lineal am Rand des Dokumentfensters.

- **class `_Lineal`**(QWidget)
  - `__init__(tab)`
  - `_versatz()` — Wo der Editor (das Blatt) im Fenster steht — ändert sich beim Rollen.
  - `px(mm)`
  - `farben()`
  - `_schrift(p)`
- **class `LinealH`**(_Lineal)
  - `_einzuege()`
  - `_x0()` — x des linken Blattrandes im Lineal.
  - `_marken()` — Name → x-Position (Bildpunkte) der ziehbaren Marken.
  - `paintEvent(ev)`
  - `_treffer(x, y)`
  - `mouseMoveEvent(ev)`
  - `_mm(x, name)`
  - `mousePressEvent(ev)`
  - `mouseReleaseEvent(ev)`
- **class `LinealV`**(_Lineal)
  - `_blatt()` — Nummer des Blattes, in dem die Schreibmarke steht — das Lineal richtet sich nach diesem Blatt.
  - `_o()` — y des oberen Blattrandes des aktuellen Blattes im Lineal.
  - `paintEvent(ev)`
  - `_treffer(y)`
  - `mouseMoveEvent(ev)`
  - `mousePressEvent(ev)`
  - `mouseReleaseEvent(ev)`

### `ui/document/navigation.py`

Die linke Seitenleiste: Suchen und ersetzen, Kommentare, Überschriften, Änderungen, Noten und Vorlesen — jedes als Feld mit Titel, Menü und ✕.

- `_datum(iso)`
- **class `KommentarKarte`**(QFrame) — Ein Kommentar: Verfasser, Datum, Text und Zeigen / Bearbeiten / Gelöst / Löschen; beim Bearbeiten steht der Text in einem Eingabefeld.
  - `__init__(b, k, ed, aktualisieren, pt, bearbeiten, speichern, abbrechen, bearbeite_los)`
- **class `NavigationPanel`**(QWidget)
  - `__init__(get_editor, fenster)`
  - `zeige_tab(key)`
  - `aktuelle_seite()`
  - `showEvent(e)`
  - `hideEvent(e)`
  - `spaeter()`
  - `aktualisieren()`
  - `anzahl(key)` — Wie viele Einträge ein Feld gerade zeigt (für Tests und die Zähler).
  - `_bau_suche()`
  - `unterfenster(d)` — Ein Unterfenster (Schriftart, Absatz … für „Format“) als Seite hier in der linken Leiste zeigen — die rechte Seitenleiste bleibt zu.
  - `suche_zeigen(text, reiter, element)` — Das Feld öffnen, die Markierung (oder ``text``) einsetzen und in das Suchfeld springen; ``reiter``: Suchen, Ersetzen oder Gehe zu.
  - `_zaehlen()`
  - `_weiter(rueckwaerts)`
  - `_ersetzen_eins()`
  - `_ersetzen_alle()`
  - `_bau_kommentare()`
  - `_kommentar_schrift(key)` — Schriftgröße der Kommentare: in den Karten hier und in den Blasen am Seitenrand.
  - `kommentar_bearbeiten(kid)` — Den Kommentar in seiner Karte bearbeiten (Doppelklick auf die Blase oder „Bearbeiten“).
  - `_bearbeiten_speichern(kid, text)`
  - `_bearbeiten_abbrechen()`
  - `_sortieren(key)`
  - `_anzeigen(key)`
  - `_neu_zeigen()`
  - `_neu_schliessen()`
  - `_neu_speichern()`
  - `_kommentare()`
  - `_bau_ueberschriften()`
  - `_einstellung(key, std)`
  - `_merke(key, wert)`
  - `_schrift(key, speichern)`
  - `_umbrechen(an, speichern)`
  - `_ebene(n)` — Alles bis zur Ebene ``n`` aufklappen, tiefere Ebenen zuklappen.
  - `_ueberschriften()`
  - `_klick(item, _col)`
  - `_kartenfeld(r, leer_text)` — Ein Feld mit Karten in einer Rolle (ohne seitliches Rollen) und einem Hinweis für den leeren Zustand. → (Layout, Hinweis)
  - `_bau_aenderungen()`
  - `_befehl(name)`
  - `_verfolgen_zeigen()`
  - `_bau_noten()`
  - `_karte(titel, text, farbe, kopf_rechts)`
  - `_aenderungen_und_noten()`
  - `_aend_aktion(name, daten)`
  - `_bau_vorlesen()`

### `ui/document/noten_feld.py`

Notenfeld unten im Fenster: hier schreibt man den Text einer Fuß- oder Endnote, direkt nach dem Einfügen oder nach einem Klick auf das Zeichen im Text.

- **class `_Eingabe`**(QPlainTextEdit)
  - `keyPressEvent(e)`
- **class `NotenFeld`**(PanelRahmen) — ``get_editor``: liefert den aktuellen Editor. Zeigt sich mit `oeffnen(art, id)`, schließt mit ✕, Esc oder `zumachen()`.
  - `__init__(get_editor)`
  - `oeffnen(art, nid)`
  - `_getippt()`
  - `zumachen()`

### `ui/document/seiten_ansicht.py`

Zwei-Seiten-Ansicht: die Seiten des Dokuments nebeneinander, so wie sie gedruckt werden (nur zum Ansehen).

- **class `SeitenAnsicht`**(QWidget)
  - `__init__(editor, breite)`

### `ui/document/suchen_feld.py`

„Suchen und Ersetzen“ in der linken Seitenleiste — aufgebaut wie das Fenster der Vorlage, aber als Feld neben dem Text:

- `_gleich(a, b)`
- `_format_text(f)` — „Format: Fett, Schriftart: Arial, Hervorgehoben“ — was als Bedingung an einem Feld hängt.
- `_linie()`
- **class `FormatvorlageWahl`**(QDialog) — Eine Formatvorlage aus der Liste wählen (für „Format ▸ Formatvorlage …“ beim Suchen und Ersetzen).
  - `__init__(parent, aktuell)`
  - `name()`
- **class `SuchenFeld`**(QWidget) — Inhalt des Feldes „Suchen und ersetzen“. ``unterfenster(dialog) -> bool`` zeigt ein Unterfenster in der linken Leiste (wie ``exec``).
  - `__init__(get_editor, unterfenster)`
  - `_feld()`
  - `_knopf(text, menue)`
  - `_sprung(symbol, tipp)` — Pfeilknopf neben dem Suchfeld (vorheriger/nächster Treffer) — quadratisch, so hoch wie das Feld.
  - `_titel(text, feld)`
  - `_bau_suchen()` — Aufbau von oben nach unten: was man sucht (Feld, Pfeile, Trefferzahl), was man einsetzt (nur Reiter Ersetzen), dann zwei
  - `eventFilter(obj, e)`
  - `keyPressEvent(e)`
  - `_bau_gehe_zu()`
  - `_element_gewaehlt(t)`
  - `gehe(richtung)`
  - `zeige(reiter, element)` — Reiter „Suchen“, „Ersetzen“ oder „Gehe zu“ zeigen; bei „Gehe zu“ optional das Element (Seite, Abschnitt …) wählen.
  - `_reiter(i)`
  - `_optionen_neu()`
  - `auftrag()`
  - `_bedingungen(a, f)`
  - `_ersatz_formate()` — Zeichenformat und Absatz-Änderung für „Ersetzen durch“ (aus „Format“ am Ersetzen-Feld).
  - `_bereich()`
  - `zaehlen()`
  - `weitersuchen(vorherige)` — „Weitersuchen“ (in der eingestellten Richtung) oder „Vorherige suchen“ (entgegen). Abwärts und Aufwärts halten am Ende an,
  - `_waehle(ed, t)`
  - `_merken(combo)`
  - `ersetzen_eins()`
  - `ersetzen_alle()`
  - `_hervorheben(an)`
  - `_suchen_in_fuellen()`
  - `_suchen_in(auswahl)` — Wie in der Vorlage: alle Treffer im gewählten Teil finden und zeigen; „Aktuelle Auswahl“ begrenzt auch die weitere Suche.
  - `_format_menue_fuellen()`
  - `_spezial_menue_fuellen()`
  - `_spezial(code)`
  - `_geaendert()`
  - `_format_schrift()`
  - `_format_absatz()`
  - `_format_tabs()`
  - `_format_stil()`
  - `_format_hervor()` — Wie in der Vorlage: erster Klick „Hervorgehoben“, zweiter „Nicht hervorgehoben“, dritter ohne Bedingung.
  - `_format_loeschen()`
- `_absatz_format(w)` — Die geänderten Absatzwerte als Absatzformat (für „Ersetzen durch“): nur, was im Fenster geändert wurde.

### `ui/document/tabelle_stift.py`

„Tabelle zeichnen“ (Einfügen ▸ Tabelle): mit dem Stift ein Rechteck auf die Seite ziehen; gestrichelt erscheinen die Zellen und

- `groesse(breite, hoehe, zoom)` — (Zeilen, Spalten) für ein gezogenes Rechteck; mindestens 1 × 1.
- `_stift_cursor()` — Stift in Dunkel mit weißem Rand: auf weißem Blatt wie auf dunklem Grund gut zu sehen (Spitze oben links).
- **class `TabellenStift`**(QWidget)
  - `__init__(ed)`
  - `_im_dokument(global_pos)`
  - `eventFilter(obj, ev)`
  - `_einfuegen()`
  - `_rechteck()`
  - `zellen()`
  - `beenden()`
  - `paintEvent(_e)`

### `ui/document/vorschau_ansicht.py`

Vorschau im Dokumentfenster: statt des Dokuments steht ein schreibgeschützter Editor mit einer abgeleiteten Fassung da — der

- `aktiv(tab, art)`
- `zeigen(tab, doc, art)`
- `beenden(tab)`

### `ui/document/zusatz_editor.py`

Editor-Seite von Kommentaren, Fuß-/Endnoten und Änderungsverfolgung (Mixin für DocumentEditor).

- `autor_farbe(autor)`
- **class `ZusatzMixin`**
  - `_zusatz_init()`
  - `zusatz_binden(meta)` — Meta-Daten des Dokuments (Kommentartexte, Noten) mit dem Editor teilen.
  - `_fragmente()`
  - `_bereiche(prop, schluessel)` — Zusammenhängende Textstücke mit gleicher Eigenschaft: [{von, bis, wert, cf}].
  - `kommentar_bereiche()`
  - `aenderungen()`
  - `noten_stellen()`
  - `_bereich_format(von, bis, props)`
  - `_eigenschaft_weg(prop, pred, von, bis)`
  - `kommentar_neu(text)`
  - `set_suchtreffer(bereiche)` — Alle Treffer der Suche farbig hinterlegen (leere Liste nimmt die Markierung weg).
  - `kommentar_text_setzen(kid, text)` — Den Text eines Kommentars ändern; Blase und Karte zeigen ihn sofort neu.
  - `kommentar_geloest(kid, geloest)` — Einen Kommentar als gelöst markieren (oder wieder öffnen); er bleibt im Dokument.
  - `kommentar_loeschen(kid)`
  - `kommentare_alle_loeschen()`
  - `_springe(bereiche, delta)`
  - `kommentar_springen(delta)`
  - `kommentar_am_cursor()`
  - `note_neu(art, text)`
  - `noten_neu_nummerieren()`
  - `note_loeschen(art, nid)`
  - `note_an(pos)` — (Art, Id) der Note, deren Zeichen an Stelle `pos` liegt (oder direkt davor), sonst None.
  - `notentext_geaendert()` — Der Text einer Note wurde im Notenfeld geändert: Seitenansicht und Karten links ziehen nach (gebündelt, nicht bei jedem Zeichen).
  - `note_springen(delta, art)` — Zur nächsten (delta 1) oder vorigen (-1) Note springen; ``art`` "f" oder "e" nur Fuß- bzw. Endnoten.
  - `set_verfolgen(an)`
  - `_markiere_geloescht(von, bis)` — Statt zu löschen als gelöscht kennzeichnen — eigener, noch nicht angenommener Einfügetext verschwindet wirklich.
  - `_loesche_verfolgt(von, bis, ende)`
  - `_verfolgte_taste(e)`
  - `_jetzt()`
  - `_inhalt_geaendert(pos, entfernt, hinzu)`
  - `aenderung_annehmen(b, annehmen)`
  - `alle_aenderungen(annehmen)`
  - `aenderung_sichtbar(b)` — Ob eine Änderung zum gewählten Markup gehört (Bearbeiter, Tag).
  - `angezeigte_aenderungen(annehmen)` — Nur die Änderungen annehmen oder ablehnen, die das Markup gerade zeigt.
  - `markup_filter_setzen(**werte)`
  - `aenderung_springen(delta)`
  - `aenderung_am_cursor()`
  - `_zus_geaendert()`
  - `set_markup(an)`
  - `_overlays_neu()` — Wellenlinien der Schreibhilfe plus Markup (Kommentare, Änderungen) als Zusatzauswahl — nichts davon landet im Format.

## `ui/hauptfenster`

### `ui/hauptfenster/__init__.py`

Bausteine des Hauptfensters (``ui/main_window.py``), nach Aufgaben geteilt.


### `ui/hauptfenster/backstage_steuerung.py`

Datei-Ansicht (Backstage).

- **class `BackstageBaustein`** — Datei-Ansicht (Backstage). Baustein von ``MainWindow`` (siehe ``lunivo_writer/ui/main_window.py``).
  - `_backstage_verbinden()`
  - `_menue_geklickt()` — ☰ Menü: öffnet die Datei-Ansicht, ein zweiter Klick schließt sie wieder.
  - `_ist_datei(i)`
  - `_reiter_gewechselt(i)`
  - `_reiter_angeklickt(i)`
  - `backstage_oeffnen(seite, unter)`
  - `backstage_zu()`
  - `backstage_schliessen()`
  - `show_main_menu()`
  - `_leiste_links()` — Schmale Leiste links: Suchen, Kommentare, Überschriften, Änderungen, Noten, Vorlesen. Ein Klick öffnet das Feld, ein zweiter schließt es.
  - `_links_klick(key)`
  - `_links_sync()`
  - `_leiste_rechts()` — Schmale Leiste rechts: Die vier Reiter der Schreibhilfe (Prüfen, Lesen, Schreiben, KI) und der KI-Chat schalten die Seitenleiste um.
  - `_rechts_klick(name)` — Ein Knopf der Leiste: öffnet die Seitenleiste auf dem Reiter; ein zweiter Klick auf denselben Reiter schließt sie wieder.
  - `_rechts_sync()`
  - `_seitenleiste_oeffnen()` — Gemeinsam für alle Bereiche „Formatierung“: die Seitenleiste einblenden, falls sie zu ist.
  - `texteffekte_seitenleiste()` — Den Bereich „Texteffekte formatieren“ in der Seitenleiste öffnen; Änderungen gelten sofort für die Markierung.
  - `objektformat_seitenleiste(reiter, fuellung)` — Den Bereich „Formatierung“ für das markierte Bild in der Seitenleiste öffnen (Füllung und Linie, Effekte); Änderungen gelten sofort.
  - `formatierung_seitenleiste(reiter)` — Zahnrad der Schnellleiste und „Formatieren“ im Rechtsklick-Menü: die Seitenleiste „Formatierung“ passend zum gewählten Objekt.
  - `_smartart_werte(e)`
  - `smartartformat_seitenleiste()` — Zahnrad am SmartArt: die Seitenleiste „Formatierung“ für den gewählten Knoten (ohne Auswahl: alle Knoten); Änderungen gelten sofort.
  - `smartartformat_folgen()` — Wählt der Benutzer einen anderen Knoten, zeigt der offene Bereich dessen Format.
  - `_diagramm_werte(e)` — Die Werte für die Seitenleiste „Formatierung“ des gewählten Diagrammteils (None ohne markiertes Diagramm).
  - `diagrammformat_seitenleiste()` — „Formatieren“ in den Diagrammtools: die Seitenleiste „Formatierung“ für den gewählten Diagrammteil öffnen; Änderungen gelten sofort.
  - `_format_folgen(schluessel, lesen)` — Gemeinsam für alle Bereiche „Formatierung“: ist er offen, zeigt er die Werte des neu gewählten Objekts (``lesen(editor)`` -> Werte oder None).
  - `diagrammformat_folgen()` — Wählt der Benutzer einen anderen Diagrammteil, zeigt der offene Bereich dessen Format.
  - `_objekt_text_verbinden()` — Die Textoptionen der Seitenleiste wirken auf den Text im gewählten WordArt oder Textfeld (``editor/frei_objekt.py``).
  - `_zeichen_masse(e)` — Höhe und Breite im Reiter Zeichentools (``bild_…``) und Bildtools (``bt_…``) mit dem markierten Bild abgleichen.
  - `objektformat_folgen()` — Wählt der Benutzer ein anderes Bild, zeigt der offene Bereich dessen Werte.
  - `_effekt_sync()` — Folgt die Markierung einer anderen Formatierung, zeigt der offene Bereich „Texteffekte“ deren Werte.
  - `toggle_sidebar()`
  - `toggle_menubar()`
  - `rename_document()`
  - `toggle_sperre()` — Überprüfen ▸ Bearbeitung einschränken: Dokument schreibgeschützt (nur in dieser Sitzung).
  - `toggle_marks(on)`
  - `insert_table()`
  - `insert_image()`
  - `insert_link()`
  - `insert_date()`
  - `edit_header_footer(header)`
  - `kopffuss_starten(editor, header)` — Kopf- oder Fußzeile auf der Seite bearbeiten: Textfeld über dem Rand, Kontext-Reiter „Kopf- und Fußzeile“ eingeblendet und aktiv.
  - `_kopffuss_aus()`
  - `insert_page_number()`
  - `find_dialog_show(reiter, element)` — Strg+F, Strg+H, Strg+G: „Suchen und ersetzen“ als Feld in der linken Seitenleiste (Reiter Suchen, Ersetzen oder Gehe zu).

### `ui/hauptfenster/bearbeiten.py`

Bearbeiten, Einfügen, Seite.

- **class `BearbeitenBaustein`** — Bearbeiten, Einfügen, Seite. Baustein von ``MainWindow`` (siehe ``lunivo_writer/ui/main_window.py``).
  - `paste_plain()`
  - `choose_color()`
  - `choose_highlight()`
  - `paragraph_dialog()`
  - `tabstopp_dialog()`
  - `_lesehilfe_auf(e)`
  - `mini_zeigen(ed, pos, rechtsklick)`
  - `markup_neu()` — Markup- und Sprechblasen-Einstellungen haben sich geändert: Seitenrand für Blasen und Auszeichnung neu aufbauen.
  - `versteckt_anwenden(e)`
  - `silbenfarben_anwenden(e)`
  - `lineale_anwenden(tab)`
  - `formatzeichen_anwenden(e)` — Formatierungszeichen für Reiter: Absatzmarken und Leerzeichen/Tabstopps getrennt (Optionen ▸ Ansicht).
  - `marken_setzen(absatz, leer)` — Absatzmarken und/oder Leerzeichen und Tabstopps ein- oder ausschalten (None = unverändert).
  - `ansicht_optionen_anwenden()` — Statusleiste, QuickInfo, Bedienschrift, Symbolgröße — aus den Optionen.
  - `lesehilfe_anwenden()`
  - `set_marken(an)`
  - `chat_oeffnen(vorlage)`
  - `vorlesen(ab_hier)`
  - `stimme_waehlen()`
  - `_nav_aktion(name, b)`
  - `zeige_navigation(tab)`
  - `autor_angaben()`
  - `toggle_navigation()`
  - `toggle_lesemodus()`
  - `set_theme(wahl)`
  - `thema_ist_dunkel()`
  - `thema_wechseln()` — Schneller Zugang zu Hell und Dunkel (Strg+Umschalt+D, Statusleiste, Ansicht-Menü): wechselt zum jeweils anderen.
  - `thema_anzeigen()`
  - `_bereiche_bauen()`
  - `_chat_knopf_pruefen()` — Der schwebende KI-Chat-Knopf ist weg, solange der Chat in der Seitenleiste offen ist.
  - `ki_schnell_zeigen()` — Die Schnellen KI-Aktionen mit Zugriff „Schnellzugriff“ in der Schnellzugriffsleiste zeigen.
  - `_page_change(fn)`
  - `set_margins(top, bottom, left, right)`
  - `set_orientation(landscape)`
  - `set_paper(name)`
  - `page_setup()`

### `ui/hauptfenster/dateien.py`

Dateien, Vorlagen, Wiederherstellung.

- **class `DateienBaustein`** — Dateien, Vorlagen, Wiederherstellung. Baustein von ``MainWindow`` (siehe ``lunivo_writer/ui/main_window.py``).
  - `new_document()`
  - `_add_tab(tab)`
  - `open_dialog()`
  - `open_path(path)`
  - `_show_report(rep, title, when)`
  - `save()`
  - `_save_tab(tab)`
  - `save_as()`
  - `save_as_format(ext)` — Speichern unter mit vorgewähltem Dateiformat (Untermenü „Speichern unter ▸“) — dasselbe Fenster wie „Speichern unter“.
  - `_ask_path(tab, title, only)` — Das eine Speichern-Fenster: Dateiname und Dateityp. `only` wählt den Dateityp vor, alle anderen bleiben wählbar.
  - `_save_tab_as(tab, only)`
  - `_darf_ueberschreiben(tab, path)` — Fragt nach, bevor eine Datei überschrieben wird, die außerhalb von Lunivo geändert wurde oder offen ist.
  - `_write(tab, path, mark_saved)`
  - `save_copy()`
  - `export_as(ext, title)`
  - `pdf_wahl_start(t)` — Die Vorgaben für das PDF-Fenster und den PDF-Weg über „Speichern unter“ (Kennwörter werden nie gemerkt).
  - `export_pdf_dialog()` — Öffnet den PDF-Export als Seite in der zweiten Spalte des Datei-Menüs.
  - `pdf_export_widget()` — Baut die PDF-Exportseite des Datei-Menüs; alle Exportwahloptionen bleiben erhalten.
  - `bild_export_widget()` — Baut die Bildexportseite des Datei-Menüs; schreibt Bilder ohne ein separates Exportfenster.
  - `_pdf_schreiben(t, path, wahl)` — Schreibt die PDF. Ohne ``wahl`` (Weg über „Speichern unter“) gelten die gemerkten Exportoptionen, ganzes Dokument, ohne Kennwort.
  - `druck_start()` — Letzte Wahl im Druckfenster; Hintergrund, Grafik und Leerseiten teilen sich die Schalter mit den Optionen.
  - `druck_merken(e)`
  - `druck_vorschau(t)`
  - `_druck_args(t)`
  - `druck_ansicht(t, parent)` — Das Druckfenster ohne Knopfzeile (Menü ▸ Drucken, zweite Spalte).
  - `print_dialog()` — Drucken (Strg+P, Schnellzugriff, Druckvorschau): die Seite „Drucken“ im Menü, kein eigenes Fenster.
  - `druckfenster()` — Dasselbe als eigenes Fenster (für Aufrufer ohne Menü).
  - `druck_hilfe()`
  - `drucke_nach_wahl(t, e)` — Druckt das Blatt `t` nach der Wahl `e` (Druckfenster oder Menü ▸ Drucken).
  - `_drucker_eigenschaften(dlg, name)`
  - `print_preview()`
  - `ausgabe_ppi()` — Standard-Ausgabeziel: Auflösung für „Als Bild exportieren“.
  - `druckoptionen()`
  - `_blasen_fuer_druck()`
  - `_silben_fuer_druck()`
  - `_neuer_drucker()`
  - `_vor_dem_drucken(tab)` — „Felder vor dem Drucken aktualisieren“: Verzeichnisse neu rechnen.
  - `reiter_menue(index, pos)` — Kontextmenü am Dokumentreiter.
  - `_reiter_schliessen(behalten, nur_andere)`
  - `close_tab(index)`
  - `_zusatz_kuerzel()` — Kürzel ohne eigene Aktion (Tabelle in windows/kuerzel.py zeigt sie in der Hilfe).
  - `_tab_weiter(d)`
  - `benutzerdaten()`
  - `neu_aus_vorlage()` — Die Seite „Neu“ im Menü: alle Vorlagen als Blätter mit Vorschau.
  - `neu_aus_wahl(art, wert)` — Legt ein neues Dokument nach der Wahl auf der Seite „Neu“ an: leer, ein Gerüst oder eine Abschrift einer Vorlagendatei.
  - `als_vorlage_speichern(ordner)` — Legt das Blatt als Vorlage ab: im Vorlagenordner oder (``ordner``) in einer seiner Rubriken.
  - `autosave_now()`
  - `offer_recovery()`

### `ui/hauptfenster/gemeinsam.py`

Gemeinsame Werte der Bausteine.

- **class `_QuickInfo`**(QObject) — Schluckt die Hinweistexte (QuickInfo) an Knöpfen und Feldern, wenn sie ausgeschaltet sind (Optionen ▸ Ansicht).
  - `__init__()`
  - `eventFilter(obj, ev)`

### `ui/hauptfenster/oberflaeche.py`

Oberfläche: Register oder Symbolleisten.

- **class `OberflaecheBaustein`** — Oberfläche: Register oder Symbolleisten. Baustein von ``MainWindow`` (siehe ``lunivo_writer/ui/main_window.py``).
  - `_symbole_anwenden()`
  - `_band_erzeugen()`
  - `oberflaeche_aendern(art, menueleiste)`
  - `neu_bauen_band()`
  - `_band_neu_bauen()`

## `ui/ribbon`

### `ui/ribbon/__init__.py`

Menüband: Reiterleiste, Gruppen, Knöpfe, Symbol-/Menüleisten.


### `ui/ribbon/menubar.py`

Menüleiste, gebaut aus register.json („menues“).

- `_taste(t)`
- `baue_menueleiste(mb, menues, befehle)` — Füllt die Menüleiste. → Anzahl der Menüpunkte ohne nativen Befehl.
- `_fenster_menue(m, befehle)`

### `ui/ribbon/menue_tafel.py`

Das ☰ Menü: links die Datei-Befehle, rechts der Inhalt (zuletzt verwendete Dateien oder die Punkte eines Untermenüs).

- `_menue_symbol(name)`
- `_datum(pfad)` — Änderungsdatum der Datei für die Liste „Zuletzt verwendet“ (leer, wenn es sie nicht mehr gibt).
- **class `MenueTafel`**(QFrame)
  - `__init__(punkte, befehle, fenster)`
  - `eventFilter(obj, ev)`
  - `_leeren()`
  - `_zeige_zuletzt()`
  - `_zeige_unter(p)`
  - `_klick(p)`
  - `zeigen_unter(widget)`

### `ui/ribbon/plan.py`

Die Reiterleiste nach der Struktur „LUNIVO WRITER“: Datei, Start, Einfügen, Seitenlayout, Verweise, Überprüfen,

- `plan(register)` — Die Reiter in der Reihenfolge der Struktur; Kontext-Register stehen am Ende (zunächst verborgen).

### `ui/ribbon/ribbon_bar.py`

Das Band (Register): Reiter → Gruppen → Knöpfe, gebaut aus resources/register.json.

- `lade_register()`
- **class `_BandSeite`**(QScrollArea) — Eine Seite des Bandes. Ist sie breiter als das Fenster, erscheinen am Rand Pfeile zum Blättern (‹ und ›), wie in der Vorlage Writer;
  - `__init__()`
  - `blaettern(richtung)`
  - `_pfeile_zeigen(*_)`
  - `_pfeile_legen()`
  - `resizeEvent(ev)`
  - `wheelEvent(ev)`
- `_zweizeilig(text)`
- **class `_ReiterLeiste`**(QTabBar)
  - `mouseDoubleClickEvent(ev)`
  - `ist_kontext(i)`
  - `tabSizeHint(i)`
  - `paintEvent(ev)`
- **class `RegisterBand`**(QWidget) — Kopfzeile (☰, Schnellzugriff, Reiter) und darunter das Band des gewählten Reiters.
  - `__init__(befehle, daten, cfg, schnell)`
  - `_reiter_geklickt(_i)`
  - `einklappen_umschalten()`
  - `_trenner()`
  - `_plan_angepasst()` — Reiter in der Reihenfolge der Struktur — ausgeblendete weglassen, eigene Reihenfolge beachten (Register anpassen).
  - `_tausch_rechtsklick(k, sym)` — Rechtsklick auf einen Knopf: Fenster „Symbol austauschen“ mit der Zeichnung dieses Knopfes.
  - `_schnellzugriff()`
  - `ki_schnell(aktionen, ausfuehren)` — „Schnelle KI-Aktionen“ mit Zugriff „Schnellzugriff“: je ein Knopf hinter den übrigen der Schnellzugriffsleiste.
  - `_reiter(r)`
  - `_gruppe(g)`
  - `_knoepfe_geordnet(g, inhalt)` — Knöpfe in der Reihenfolge der Liste: große stehen allein, aufeinanderfolgende kleine bilden eine Spalte aus zwei Zeilen.
  - `_knoepfe_schrift(g, inhalt)` — Wie WPS: oben Schriftname und -größe, daneben die Größen-/Löschknöpfe; darunter die Zeichenformate.
  - `_knoepfe_tt_schrift(g, inhalt)` — Texttools: Schriftname und -größe oben (wirken auf das markierte WordArt/Textfeld), darunter die Zeichenformate — wie bei Start.
  - `_knoepfe_galerie(g, inhalt)` — Eine Galerie wie in WPS: drei Kacheln zum Anklicken und daneben ein Pfeil mit der ganzen Auswahl (Befehl ``galerie_<name>``).
  - `_knoepfe_raender(g, inhalt)` — Der Rand-Knopf und daneben wie bei WPS die vier Maßfelder Oben/Unten/Links/Rechts (in der gewählten Maßeinheit).
  - `_knoepfe_masse(g, inhalt)` — Höhe und Breite des markierten Bildes (Zeichentools); „Seitenverhältnis sperren“ hält das Verhältnis beim Ändern.
  - `_knoepfe(g, inhalt)`
  - `_stile()`
  - `_stile_popup(unter)` — Alle Formatvorlagen als Galerie (Pfeil rechts neben der Reihe): Probe in der Vorlage, Name darunter; Überfahren zeigt live.
  - `stile_aktualisieren()` — Die Galerie neu füllen — die eingebauten Vorlagen und die selbst angelegten (editor/stile.py).
  - `eventFilter(obj, ev)`
  - `_raender()`
  - `_knopf(e, gross)`
  - `_klappe(name)` — Das Menü einer Klappe: erst die Bausteine der Oberfläche (``KLAPPEN``), sonst ``menue_<name>`` des Befehlsbausteins.
  - `_menue_fuellen(menu, items)`
  - `kontext(name, sichtbar, aktivieren)` — Kontext-Register (Tabellentools, Bildtools …) ein- oder ausblenden; ``aktivieren``: gleich öffnen.
  - `_start_index()`
  - `gruppe_widget(g)` — Eine Gruppe als eigenständiges Widget (für die Seitenleiste).
  - `aktualisieren(hat_dokument)`

### `ui/ribbon/toolbars.py`

Oberfläche „Symbolleisten“: ☰ Menü + obere Leiste (Datei/Dokument) + untere Leiste (Text) + Zusammenhangsleiste.

- **class `Symbolleisten`**(QWidget)
  - `__init__(befehle)`
  - `_zeile(v)`
  - `_trenner(h)`
  - `_fuellen(h, liste)`
  - `_knopf(sym, tip, akt, haken)`
  - `_abstand(box)`
  - `kontext(name, sichtbar, aktivieren)`
  - `aktualisieren(hat_dokument)`

## `ui/ribbon/tabs`

### `ui/ribbon/tabs/__init__.py`

Die Reiter des Menübands (Datei, Start, Einfügen, Seitenlayout, Verweise, Überprüfen, Schreibhilfe, Ansicht).


### `ui/ribbon/tabs/ai_tab.py`

Reiter „Schreibhilfe“: Lesen, Prüfen, Beim Schreiben, Vorlesen, Sprache, Bausteine, KI und Anzeigen — jede Funktion einmal, jede mit eigenem Symbol.

- `_knoepfe(gruppe)` — Die Band-Knöpfe einer Gruppe: erst die kleinen, dann die großen.
- `_pruefen_menue(e)` — Das eine Prüfmenü: wann geprüft wird (F7), gründlich, mit KI (F8), Hilfen und die Sprache des Dokuments.
- `bauen(register)`

### `ui/ribbon/tabs/baustein.py`

Baustein für die Reiterbeschreibungen: ein Knopf als Wörterbuch.

- `k(symbol, name, tun, gross, **kw)`
- `anordnen_knopf(art, name, **kw)` — Ein Knopf der Gruppe „Anordnen“ (``art``: drehen, gruppieren, ausrichten, umbruch, vorn, hinten, auswahlbereich); ``name`` und ``gross``/``text`` je Reiter.
- `anordnen_gruppe(*knoepfe)` — Die Gruppe „Anordnen“ der Kontext-Reiter.
- `alle(tab)` — Alle Knöpfe eines Reiters aus register.json nach Namen.
- `uebrige(tab, benutzt)` — Knöpfe des Reiters, die in der neuen Anordnung noch nicht vorkommen (damit keine Funktion verloren geht).

### `ui/ribbon/tabs/file_tab.py`

Reiter „Datei“ (die Backstage-Ansicht ersetzt das Band; die Gruppen bleiben als Vorlage für Menüs und Symbolleisten).

- `bauen(register)`

### `ui/ribbon/tabs/home_tab.py`

Reiter „Start“ in der Anordnung von WPS Office.

- `bauen(start)` — Reiter Start in der Anordnung von WPS Office: Zwischenablage (Einfügen, Ausschneiden/Kopieren, Format übertragen), Schriftart mit

### `ui/ribbon/tabs/insert_tab.py`

Reiter „Einfügen“ in der Anordnung von WPS Office (Vorlagen im Ordner einfuegen/): Deckblatt, Leere Seite ▾, Umbrüche ▾, Tabelle ▾,

- `bauen(register)`

### `ui/ribbon/tabs/layout_tab.py`

Reiter „Seitenlayout“ in der Anordnung von WPS Office: Designs, Ränder mit den vier Maßfeldern, Seite einrichten

- `bauen(register)`

### `ui/ribbon/tabs/mailings_tab.py`

Reiter „Sendungen“ (nur nach „Register anpassen“ sichtbar): Serienbriefe und Formulare.

- `bauen(register)`

### `ui/ribbon/tabs/references_tab.py`

Reiter „Verweise“ (in register.json „Referenzen“) in der Anordnung von WPS Office: TOC einfügen, Inhaltsverzeichnis

- `bauen(register)`

### `ui/ribbon/tabs/review_tab.py`

Reiter „Überprüfen“ nach den Vorlagen (ueberpruefen/01–10): Rechtschreibprüfung, Wörter zählen, Kommentare, Änderungen

- `bauen(register)`

### `ui/ribbon/tabs/section_tab.py`

Reiter „Abschnitt“ in der Anordnung von WPS Office.

- `bauen(register)`

### `ui/ribbon/tabs/view_tab.py`

Reiter „Ansicht“ in der Anordnung von WPS Office: Dokumentansichten (Vollbild, Lesemodus, Drucklayout, Weblayout), Navigationsbereich

- `bauen(register)`

## `ui/sidebar`

### `ui/sidebar/__init__.py`

Rechte Seitenleiste: Schreibhilfe und KI-Chat.


### `ui/sidebar/sidebar.py`

Die Schreibhilfe-Seitenleiste: Prüfen, Wellen/Vorhersage/AutoKorr, Funde, „Für wen?“, KI-Knöpfe.

- **class `SchreibhilfePanel`**(QWidget)
  - `__init__(assistent, parent)`
  - `verbinde_ki(dienst, fenster)`
  - `_schalter_nachziehen(name, an)`
  - `_thema_nachziehen(name)`
  - `ki_aktualisieren(laeuft)` — Ohne Modell steht oben auf dem Reiter KI der Weg dorthin; die Zeilen selbst bleiben bedienbar (ein Klick führt in die KI-Einstellungen).
  - `_werk_bauen()` — Die Reiter Lesen, Schreiben und KI aus dem Katalog; der Reiter Prüfen sind die Funde plus die Wege dahin.
  - `werkbank_aktualisieren()`
  - `aktueller_reiter()`
  - `zeige_reiter(name)` — Einen Reiter der Werkbank öffnen (und die Seitenleiste auf die Schreibhilfe stellen).
  - `_ollama_pruefen()`
  - `_ollama_da(modelle)`
  - `zeige_vorschlaege(lst)`
  - `_funde_zeigen()` — Ergebnisse (Hinweise, Vorschläge, Übersetzung) erscheinen auf dem Reiter Prüfen — die Seitenleiste wird dafür geöffnet und umgestellt.
  - `zeige_hinweis(titel, text, cent)`
  - `_karten_leeren()`
  - `_leer(text)`
  - `_format_zustand()`
  - `format_panel(schluessel)`
  - `_formatierung_host(panel_klasse, menue_text, werte)` — Der gemeinsame Rahmen der Bereiche „Formatierung“: Kopf mit „Formatierung ▾“, Anheften und Schließen, darunter das Panel.
  - `zeige_format(schluessel, werte, **verbindungen)` — Den Bereich „Formatierung“ für ``schluessel`` zeigen. ``verbindungen``: Signalname des Panels -> Empfänger (``None`` wird übergangen).
  - `format_sichtbar(schluessel)`
  - `aktualisiere_format(schluessel, werte)` — Die Werte des Panels an die Markierung anpassen (wenn der Benutzer gerade nicht darin bedient).
  - `zeige_texteffekte(werte, anwenden)`
  - `texteffekte_sichtbar()`
  - `aktualisiere_texteffekte(werte)`
  - `zeige_objektformat(werte, anwenden, reiter, bild_wunsch)` — ``reiter``: 0 = Füllung und Linie, 1 = Effekte.
  - `objektformat_sichtbar()`
  - `aktualisiere_objektformat(werte)`
  - `zeige_diagrammformat(werte, anwenden, alt_anwenden, bild_wunsch, teil_wunsch)`
  - `diagrammformat_sichtbar()`
  - `aktualisiere_diagrammformat(werte)`
  - `zeige_smartartformat(werte, anwenden, bild_wunsch)`
  - `zusatz_ausfuehren(d)` — Ein Zusatzfenster als Seite hier in der Seitenleiste zeigen, solange man es bearbeitet (wie ``d.exec()``). Die Breite bleibt.
  - `zeige_bereich(i)` — 0 = Schreibhilfe, 1 = KI-Chat.
  - `setze_bereiche(band, ki_gruppen)` — Den KI-Bereich bauen: nur der Chat (Verlauf, Eingabe) — alles andere steht im Reiter Schreibhilfe und im Fenster „KI-Einstellungen“.
  - `zeige(funde)`
  - `_alle()`
  - `welche_hilfe()`

## `ui/sidebar/panels`

### `ui/sidebar/panels/__init__.py`

Bereiche der Seitenleiste.


### `ui/sidebar/panels/ai_panel.py`

KI-Chat in der Seitenleiste (Bereich „KI“): mehrere Runden, der Dokumenttext geht als Auskunft mit.

- **class `ChatEingabe`**(QPlainTextEdit) — Mehrzeiliges Eingabefeld für den Chat: Enter schickt ab, Umschalt+Enter macht eine neue Zeile. ``text()``/``setText()`` wie beim Einzeiler.
  - `__init__()`
  - `keyPressEvent(e)`
  - `text()`
  - `setText(t)`
- **class `ChatPanel`**(QWidget) — KI-Chat: Kopf („KI-Chat“, Einstellungen, Schließen), Verlauf, darunter Eingabe mit Senden; Bild und Neu als kleine Knöpfe.
  - `__init__(dienst, fenster)`
  - `_erweitert(ev)` — „Erweiterte Einstellungen anzeigen“: Modell (dieselbe Wahl wie in der Modellzuweisung), Länge, Temperatur, Top P, Stoppfolgen — in der KI-Konfiguration gespeichert.
  - `_modelle_neu()` — Nach einer Änderung in den KI-Einstellungen die Modellliste dieser Auswahl neu füllen.
  - `zustand()` — Verlauf und Eingabe gibt es erst mit einem verbundenen Modell.
  - `_einstellungen()`
  - `_blase(text, ki, cent)`
  - `_einfuegen(text)`
  - `_ersetzen(text)`
  - `senden()`
  - `_bild()`
  - `_aktion_ergebnis(name, text, cent)` — Das Ergebnis einer Schnellen KI-Aktion steht im Chat wie eine Antwort (und ist Teil des Gesprächs).
  - `_antwort(text, cent)`
  - `leeren()`

### `ui/sidebar/panels/writing_panel.py`

Bereich „Schreibhilfe“ der Seitenleiste: die Karten für Funde, Vorschläge und Hinweise.

- `kurz(text)` — Lange gleiche Zeichenfolgen (viele Leerzeichen hintereinander) kurz zeigen: „␣×34“ — sonst wird die Karte breiter als die Seitenleiste.
- `marke(art)`
- **class `FundKarte`**(QFrame)
  - `__init__(fund, assistent, parent, dienst)`
  - `_vorschlag_holen()`
  - `_vorschlag_da(v)`
  - `_annehmen()`
  - `_verwerfen()`
  - `_zeigen()`
  - `_hoeren()`
  - `mousePressEvent(e)`
- **class `VorschlagKarte`**(QFrame)
  - `__init__(v, dienst, panel)`
  - `_lassen()`
  - `_einsetzen()`
  - `_weg(abgelehnt)`
- **class `HinweisKarte`**(QFrame) — Antworten, die den Text nicht ersetzen sollen (Zusammenfassung, Analyse).
  - `__init__(titel, text, cent, fenster, panel)`
  - `_kopieren()`
  - `_ende()`
  - `_weg()`

## `ui/statusbar`

### `ui/statusbar/__init__.py`

Statusleiste.


### `ui/statusbar/status_bar.py`

Statusleiste: Meldung, Wörter/Zeichen, Seite, Zoom (− Regler + Anzeige).

- **class `StatusBar`**(QStatusBar)
  - `__init__(parent)`
  - `thema_zeigen(dunkel)`
  - `meldung(text)`
  - `zaehler(woerter, zeichen)`
  - `seite(aktuell, gesamt)`
  - `zoom_zeigen(faktor)`

## `ui/widgets`

### `ui/widgets/__init__.py`

Wiederverwendbare Widgets (Symbole, Fließlayout, Live-Vorschau, Minisymbolleiste).


### `ui/widgets/flow_layout.py`

Umbrechendes Layout für die Auswahlknöpfe (nach dem Qt-Beispiel „Flow Layout“).

- **class `FlowLayout`**(QLayout)
  - `__init__(parent, spacing)`
  - `addItem(item)`
  - `count()`
  - `itemAt(i)`
  - `takeAt(i)`
  - `expandingDirections()`
  - `hasHeightForWidth()`
  - `heightForWidth(w)`
  - `setGeometry(r)`
  - `sizeHint()`
  - `minimumSize()`
  - `_lay(rect, test)`

### `ui/widgets/icons.py`

Einheitliche Office-Symbole: 24×24-Strichzeichnungen aus Lucide, mit Qt gerendert.

- `pfade_original()` — Die mitgelieferten Symbole, ohne Austausch.
- `pfade()`
- `uebersteuern(tausch)` — Austausch {Symbolname: Katalogname} anwenden (Ansicht ▸ Symbol austauschen); leere Zuordnung stellt alles zurück.
- `katalog()` — Alle 1800 Lucide-Symbole (Name → 24×24-Pfad) — für Piktogramm einfügen und Symbol austauschen.
- `katalog_bild(name, px, farbe, strich)`
- `pfad_bild(pfad, px, farbe)` — Eine Zeichnung (Katalogpfad oder eigene) als Bild — für Vorschau und Auswahlfenster.
- `hat(name)`
- `_symbolpfad(name)` — Gibt zuerst das semantische Standardsymbol, sonst das Lucide-Katalogsymbol zurück.
- `eigene_zeichnung(text, gefuellt)` — SVG oder Pfaddaten → Zeichnung, auf 24 × 24 gebracht und mittig eingepasst (Zeichenkette für den Austausch).
- `_svg(pfad, farbe)`
- `svg_datei(name, farbe)` — Lucide-SVG als Datei für Qt-Stylesheets, die SVG-Daten nicht direkt annehmen.
- `_pixmap(name, farbe, px)`
- `icon(name, px)`
- `icon_aus_pfad(pfad, px)` — Ein Liniensymbol aus einem Pfad (24er-Raster, Strichstil wie die übrigen Symbole) in den Farben der Palette.
- `leeren()`
- `setze(knopf, name, px)` — Symbol auf einen Knopf setzen und den Namen merken: beim Wechsel zwischen hell und dunkel bekommt er sein Symbol in der neuen Farbe zurück.
- `alle_neu()` — Nach einem Farbwechsel: alle Knöpfe mit gemerktem Symbol neu beziehen (der Zwischenspeicher ist dann schon geleert).

### `ui/widgets/kontextmenue.py`

Das Rechtsklick-Menü des Textes, deutsch und in der Reihenfolge der Vorlage: Zwischenablage, Format übertragen, Schriftart, Absatz,

- `_symbole()`
- `menue_bauen(editor, fenster)` — Das Menü für den Editor ``editor`` des Fensters ``fenster``; der Aufrufer zeigt es und löscht es danach.

### `ui/widgets/live_vorschau.py`

Live-Vorschau: Beim Überfahren einer Formatvorlage, Schrift, Größe oder Farbe zeigt das Dokument das Ergebnis schon — ohne dass etwas

- **class `LiveVorschau`**
  - `__init__(fenster)`
  - `aktiv()`
  - `zeigen(anwenden)` — anwenden(editor) wendet das Format an; es wird beim nächsten `ende()` zurückgenommen.
  - `ende()`
- **class `Ueberfahren`**(QObject) — Event-Filter: Zeiger über dem Knopf → Vorschau, Zeiger weg oder Klick → Vorschau beenden.
  - `__init__(vorschau, anwenden)`
  - `eventFilter(o, e)`
- **class `VorschauCombo`**(QComboBox) — Auswahlfeld, dessen Einträge beim Überfahren (highlighted) als Vorschau gezeigt werden.
  - `__init__(vorschau_fn, ende_fn, parent)`
  - `hidePopup()`
- **class `VorschauFontCombo`**(QFontComboBox)
  - `__init__(vorschau_fn, ende_fn, parent)`
  - `hidePopup()`

### `ui/widgets/mini_leiste.py`

Minisymbolleiste: schwebende Leiste mit den häufigsten Formaten über der Auswahl oder am Rechtsklick.

- `_symbole()`
- **class `MiniLeiste`**(QFrame)
  - `__init__(fenster)`
  - `_ausrichtung_menue()`
  - `_menue_setzen(b, tun)` — Das Menü ist dasselbe wie im Band (Einfügen, Farbpaletten mit „Zuletzt benutzt“ und Vorschau, Zeilenabstand); es entsteht nach jeder Wahl neu.
  - `_nach_farbe(b, tun)`
  - `_schrift(name)`
  - `_groesse(text)`
  - `_tun(tun)`
  - `aktualisieren()`
  - `zeigen(editor, global_pos, rechtsklick)` — Über global_pos zeigen (am Rechtsklick darunter, neben dem Menü); verschwindet bei Tastendruck oder Auswahlende.
  - `_pruefen(editor)`
- **class `_Zu`**(QObject) — Schließt die Leiste bei Tastendruck, Mausrad und Fokusverlust des Editors.
  - `__init__(leiste, editor)`
  - `eventFilter(o, e)`

### `ui/widgets/schweb_knopf.py`

Ein runder Knopf, der unten rechts über dem Blatt schwebt (wie der KI-Chat-Knopf in ONLYOFFICE).

- **class `SchwebKnopf`**(QToolButton)
  - `__init__(editor, symbol, tipp, aktion)`
  - `platzieren()`
  - `eventFilter(obj, e)`

