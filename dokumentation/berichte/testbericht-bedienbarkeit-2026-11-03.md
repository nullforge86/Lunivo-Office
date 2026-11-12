# Testbericht: Bedienbarkeit, Navigation und Barrierefreiheit

Stand 2026-11-03. Quelltext wurde **nicht** verändert; dieser Bericht ist die einzige neue Datei.

## Methode und Grenzen (bitte zuerst lesen)

| Art | Bedeutung |
|---|---|
| **[B]** beobachtet | Am laufenden Hauptfenster gemessen (Qt `offscreen`, 1200×800, leere Einstellungen, ein Aufruf mit Bildschirmfoto und Zählung der Knöpfe) |
| **[Q]** Quelltext | In `register.json`, `kuerzel.py`, Doku oder Code nachgewiesen |
| **[V]** vermutet | Folgt aus dem Befund, nicht selbst bedient |
| **[T]** Vorschlag | Verbesserungsidee |

**Nicht möglich:** Tastatur- und Mausbedienung am echten Bildschirm, Screenreader, Fensterwechsel per Hand, Dialoge öffnen und schließen, Speichern/Öffnen/Drucken/PDF. Alles, was dazu gesagt wird, ist **nicht getestet**. Es lief kein Test der Projekt-Suite (laut Projektregel keine Volltests).

## Umgesetzt und neu bewertet (nach Freigabe, 2026-11-03)

| Nr. | Ergebnis |
|---|---|
| F1 / V1 | **Behoben:** Menü „Referenzen“ heißt „Verweise“ (`register.json`). |
| F2 / V2 | **Behoben:** „Rechtschreibprüfung“ überall (Knopf, Menü, Kurzbeschriftung in `band_leiste.py`, `dokumentation/benutzerhandbuch/pruefung-und-ki.md`). Prüfknöpfe bleiben: „Dokumentprüfung“ ist der Sammelname, „Barrierefreiheit prüfen“ ist eine andere Funktion. |
| F3 | **Kein Fehler:** Reiter „Abschnitt“ kommt aus `oberflaeche/band/reiter/abschnitt_reiter.py` (in Python gebaut, nicht in `register.json`). |
| F4 | **Kein Fehler:** Das Band blättert bei Platzmangel mit Pfeilen ‹ › (`_BandSeite`), so gewollt. |
| F5 / V4 | **Teilweise behoben:** Bandknöpfe mit Symbol sind mindestens 36 px breit (`MIN_KNOPF`). Die Höhe (24–25 px in der zweizeiligen Bandzeile) bleibt, sie zu ändern wäre ein Umbau des Bandes. Pfeilknöpfe und Hilfsknöpfe (Absatz-Layout, Zoom) sind weiter kleiner. |
| F6 / V8 | **Behoben:** `NamenFilter` (`oberflaeche/baukasten/geruest/zugaenglichkeit.py`) gibt jedem Knopf ohne Namen seinen Tooltip als Namen; danach hat kein sichtbarer Knopf im Hauptfenster mehr keinen Namen (gemessen). Test: `test_namenfilter_gibt_symbolknoepfen_einen_namen`. |
| F7 | **Bewusst so:** Blätterpfeile des Bandes und das Absatz-Layout-Symbol nehmen keinen Fokus, damit die Schreibmarke im Text bleibt; die Funktionen sind per Tastatur anders erreichbar [V]. |
| F8 / V3 | **Messfehler, kein Fehler:** Mein erster Testaufruf übersprang `start()`. Das Programm beginnt mit einem leeren Blatt (`kern/anwendung.py`), Band und Blatt sind dann aktiv (Bildschirmfoto geprüft). |
| V5 | **Umgesetzt:** Option *Anzeige ▸ Namen unter den Symbolen der Randleisten* (aus als Vorgabe). Beide Zustände am Bildschirmfoto geprüft. |
| V6 | **Umgesetzt:** 15 Menüpunkte zeigen jetzt ihr Kürzel (Strg+W/Q/H/K/L/E/R/J, Strg+Umschalt+L/N/8, Strg+Alt+F/D/T, Strg+Enter). Nur Kürzel, die im Code wirklich gebunden sind. Kein Kürzel doppelt belegt (gemessen: 55 Kürzel, 0 Konflikte). |
| V7 | **Entfällt:** Die Seitenleiste ist 300–420 px breit (`seitenleiste.py`). Der Eindruck „halbe Breite“ kam aus dem Testaufruf ohne Dokument. |
| V9 | **Umgesetzt:** Fünf Fehlermeldungen nennen jetzt, was nicht geschah, den Grund und den nächsten Schritt (Speichern, PDF-Export, Sichern, Einspielen, Zurückholen). Die übrigen Meldungstexte habe ich gelesen: sie sind kurz und verständlich. |
| neu | **Behoben:** Der Schließen-Knopf der Dokumentreiter hatte den englischen Tooltip „Close Tab“, jetzt „Dokument schließen“. |

**Geprüft:** `test_verweise_vorlagen`, `test_ueberpruefen_vorlagen`, `test_layout_tab`, Teile von `test_start_reiter`, `test_main_window`, `test_optionen`, `test_baukasten` (bestanden). **Bekannt, nicht von diesen Änderungen:** `test_baukasten.py::test_fenster_stapel_unterfenster_als_seiten` meldet einen Fehler im Aufräumen (`_MintFilter` in `thema.py`), wenn `test_optionen.py` davor läuft; er tritt auch ohne meine Änderungen auf (mit `git stash` bestätigt).

## 1. Zusammenfassung

Der Funktionsumfang ist groß (191 Band-Knöpfe, 9 Menüs mit rund 300 Punkten, 8 Reiter) und überwiegend sauber gruppiert. Die Barrierefreiheit ist ernsthaft angelegt (Lesehilfe, Schriftgröße, Tooltips, Suche in Optionen, Beschriftung der Seitenliste). Die Hauptprobleme sind **uneinheitliche Begriffe**, **dieselbe Funktion an mehreren Stellen mit verschiedenem Namen**, **zu kleine Bedienflächen im Band** und **wenige Tastenkürzel im Menü**. Kein kritisches Problem nachgewiesen.

## 2. Getestete Bereiche

| Bereich | Status |
|---|---|
| Struktur von Reitern, Gruppen, Knöpfen, Menüs | aus Quelltext vollständig ausgewertet [Q] |
| Hauptfenster beim Start (Aussehen, Größen, Fokus) | beobachtet [B] |
| Kürzeltabelle (`oberflaeche/kuerzel.py`) | gelesen [Q] |
| Optionen (6 Seiten, Suche) | nur Doku/Code gelesen [Q] |
| Dialoge, Fensterwechsel, Dokumentbearbeitung, Speichern, Öffnen, Drucken, PDF, Schreibhilfe-Funktion | **nicht getestet** |

## 3. Fehler und Auffälligkeiten

| Nr. | Befund | Art | Schwere |
|---|---|---|---|
| F1 | **Reiter heißt „Verweise“, Menü und Definition heißen „Referenzen“.** `oberflaeche/band/reiter/verweise_reiter.py:11` benennt den Reiter um; `register.json` und die Menüleiste sagen „Referenzen“. Schritte: Menüleiste einschalten (Ansicht ▸ Oberfläche ▸ Menüleiste), Reiter und Menü vergleichen. | Q + B (Reiter im Foto) | mittel |
| F2 | **Gleiche Funktion, verschiedene Namen:** `rechtschreibung` heißt „Rechtschreibung“ (Überprüfen) und „Rechtschreibprüfung“ (Schreibhilfe). Zusätzlich: „Prüfen“, „Gründlich prüfen“, „Dokumentprüfung“, „Barrierefreiheit prüfen“ nebeneinander; „Dokumentprüfung“ ist Gruppe *und* Knopf. | Q | mittel |
| F3 | **Reiter „Abschnitt“** steht im Band [B], aber nicht in `register.json` (8 Reiter dort, davon „Sendungen“ ausgeblendet). Herkunft nicht geklärt. | B | klein (Doku/Auffindbarkeit) |
| F4 | **Band wird bei 1200 px abgeschnitten:** Gruppe „Bearbeiten“ zeigt „Auswähle…“, rechts ein Pfeil „›“ zum Weiterblättern. | B | mittel |
| F5 | **Kleine Bedienflächen:** 58 von 85 sichtbaren Knöpfen sind schmaler oder niedriger als 36 px (Projektvorgabe: nicht unter ~36 px). Ein Teil davon (Pfeile ⭨, Auswahlpfeile) ist erwartbar klein. | B | mittel |
| F6 | **34 von 85 sichtbaren Knöpfen ohne `accessibleName`**; sie haben aber Text oder Tooltip (keiner ohne beides). Für Screenreader ist der Name dann Text/Tooltip. | B | klein, [V] für Screenreader |
| F7 | **Ein sichtbarer Knopf ohne Tastaturfokus** (`NoFocus`), nicht identifiziert. | B | klein |
| F8 | **Beim Start kein Dokument:** grauer leerer Bereich ohne Hinweis, was zu tun ist (Neu/Öffnen); Band ist ausgegraut. | B | mittel (siehe B1) |

## 4. Barrierefreiheit (Legasthenie-Blick)

- **Begriffe** (F1, F2): gleiche Sache unter zwei Namen erhöht die Merklast.
- **Doppelte Funktionen im Band** [Q]: Silbentrennung, Thesaurus, Rechtschreibung, Lesemodus (Schreibhilfe und Überprüfen/Ansicht), Querverweis (Einfügen und Referenzen), Textfeld (Einfügen und Sendungen/Formular); Textrichtung und Umbrüche (Start und Seitenlayout). Das hilft Wiederfinden, aber die Namen müssen dann **gleich** sein. „Seitenränder“ steht als Gruppe, als Katalog und als Knopf im Reiter Seitenlayout (Gruppen „Ränder“ und „Seitenränder“) — verwirrend.
- **Menü:** 27 von rund 297 Menüpunkten tragen ein Kürzel; im Menü „Start“ 62 Punkte mit 9 Untermenüs. Viele Untermenüs sind mühsam für Menschen mit Orientierungsschwierigkeiten [V].
- **Rechtsklick:** ausgegraut statt versteckt — gut und beibehalten (Doku `oberflaeche.md`).
- **Symbole:** linke und rechte Seitenleiste zeigen nur Symbole ohne Text [B]; Bedeutung nur per Tooltip. Rechts „?“ (Hilfe) neben Prüfen-Symbol.
- **Schreibhilfe-Seitenleiste** nimmt beim Start etwa die Hälfte der Breite ein [B] und verkleinert die Schreibfläche.
- **Meldungen:** 48 Aufrufe von `QMessageBox` (18 Warnung, 26 Information, 13 Frage, 2 kritisch). Wortlaut und Rückmeldungen **nicht geprüft**.

## 5. Verbesserungsvorschläge [T] mit Auswirkung

| Nr. | Vorschlag | Auswirkung auf Bestehendes |
|---|---|---|
| V1 | Reiter und Menü einheitlich benennen (empfohlen „Verweise“ wie im Band, Menü „Referenzen“ umbenennen; oder umgekehrt) | nur Beschriftung; `register.json`, `verweise_reiter.py`, Tests/Handbuch mit dem Namen prüfen |
| V2 | Gleiche Aktion = gleicher Name (Rechtschreibung/-prüfung) und Prüfknöpfe vereinheitlichen | Beschriftung; Tastenkürzel unberührt |
| V3 | Leerer Startzustand: Hinweis „Neu (Strg+N) oder Öffnen (Strg+O)“ in der Schreibfläche | rein anzeigend |
| V4 | Band: Gruppen früher in Auswahlmenü falten statt abzuschneiden; Mindestgröße 36 px für alle Knöpfe (Pfeil ⭨ mit größerer Trefferfläche) | Layoutänderung im Band; mit `werkzeuge/pruefungen/funktionspruefung.py` gezielt prüfen |
| V5 | Seitenleisten-Symbole optional mit Text (Einstellung „Beschriftung anzeigen“) | optional, nichts entfällt |
| V6 | Mehr Kürzel in Menüs anzeigen, Kürzelliste (`kuerzel.py`) mit F1-Hilfe verknüpfen | Konflikte vorher gegen `setShortcut` prüfen |
| V7 | Schreibhilfe-Seitenleiste beim Start schmaler oder zugeklappt, Breite merken | Zustand der Seitenleiste |
| V8 | `accessibleName` für alle Symbolknöpfe setzen (Name = Text) | reine Zusatzinformation |
| V9 | Fehlermeldungen systematisch lesen: Satz 1 sagt was geschah, Satz 2 was zu tun ist | Textänderung |

## 6. Priorisierung

1. **Hoch:** F1, F2 (Begriffe), F5/F4 (Bedienflächen und Abschneiden), F8.
2. **Mittel:** V5, V6, V7.
3. **Niedrig:** F3, F6, F7, V8.

## 7. Navigation vereinfachen

- Eine Benennung je Funktion, egal wo sie steht (Tabelle „Doppelte Funktionen“ als Prüfliste).
- Reiter „Schreibhilfe“ als zentrale Stelle behalten, Dubletten in anderen Reitern verweisen auf dieselben Namen.
- Menü „Start“ (62 Punkte) in Gruppen mit Zwischentiteln statt Untermenüs gliedern [T].

## 8. Regressionseinschätzung

V1–V3, V5, V8, V9 sind Beschriftungen oder reine Zusatzanzeigen, geringes Risiko für Kürzel, Menüs, Speichern, Drucken, PDF. V4 und V7 betreffen Layout/Zustand und brauchen gezielte Prüfung am Band. Zum Zusammenspiel mit Speichern, Öffnen, Drucken, PDF und Schreibhilfe: **nicht geprüft**.

## 8a. Schritt 2: Abläufe am laufenden Programm (beobachtet, Qt offscreen, simulierte Tasten)

| Ablauf | Beobachtung |
|---|---|
| Strg+B zweimal, dann Fett über den Befehl des Bandknopfs | Fett an, aus, an: Kürzel und Band wirken gleich |
| F9 öffnet Optionen, Haken ändern, Escape | Optionen öffnen, Haken wechselt; **Fund:** danach stand der Fokus auf einem Knopf, nicht im Text → **behoben**, Fokus ist wieder im Dokument |
| Strg+N, Text tippen, Strg+Tab hin und zurück | Zweites Dokument entsteht; Text beider Dokumente bleibt erhalten; Fenstertitel stimmt |
| Strg+H, Strg+F, Strg+D, F5 | Alle öffnen in der Seitenleiste (kein loses Fenster), Fokus im Feld; **Fund:** nach Schließen von Strg+D stand der Fokus auf einem Knopf → **behoben** (Fokus zurück in den Text), ebenso beim Schließen der Seitenleiste mit F5 |
| Tab im Text | Bleibt im Text (Einzug/nächste Lücke). **Fund:** Per Tastatur kam man aus dem Text nicht ins Band → **behoben:** F10 springt zu den Reitern, Tab geht durch Schnellzugriff und Band, F10 zurück in den Text; in `kuerzel.py` (Hilfe) eingetragen |
| Strg+Umschalt+N, Strg+Umschalt+L | Navigationsbereich schaltet um, Lesemodus löst aus |
| Strg+W (Dokument ungeändert) | Schließt, Fokus im verbleibenden Dokument |
| Beenden des Testprogramms | **Fund (mein neuer Namensfilter):** verschachtelte Aufrufe beim Abbau → mit Wiedereintritts-Schutz und Abmelden beim Beenden **behoben** |

**Regression (gezielt, bestanden):** `test_fenster_seitenleiste`, `test_schreibhilfe`, `test_pdf_export`, `test_speichern_sicher` (152), `test_backstage`, `test_main_window`, `test_docx_roundtrip` (52), Druck/Vorschau-Teile von `test_baukasten` (7).

## 9. Weiterhin nicht getestet

- Screenreader (Orca/NVDA) und echte Hardware-Tastatur: nur simulierte Tasten.
- Rückfrage beim Schließen eines **geänderten** Dokuments (Fenster wartet auf Eingabe).
- Aussehen der Menüleiste (standardmäßig ausgeblendet), Dunkelmodus, andere Bildschirmgrößen und Skalierungen.
- Tatsächlicher Ausdruck auf einem Drucker; Windows und macOS.
- Hilfe-Dialog und Kontext-Reiter im Ablauf.

## 10. Empfohlener nächster Schritt

Auf dem echten Bildschirm eine kurze Sitzung (30 min) mit den Abläufen aus dem Auftrag, danach V1 und V2 (Begriffe) als erste, risikoarme Änderung — erst nach deiner Freigabe.
