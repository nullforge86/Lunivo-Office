# KI-Handbuch für Lunivo Writer

Dieses Handbuch beschreibt die optionalen KI-Funktionen, ihre Bedienung und die dazugehörigen Einstellungen in Lunivo Writer. Es richtet sich an Anwenderinnen und Anwender und orientiert sich an der vorhandenen Anwendung und ihren Einstellungen.

> **Wichtig:** Die KI ist eine Ergänzung. Schreiben, Speichern und die eingebauten Prüf- und Lesehilfen funktionieren auch ohne einen KI-Dienst. Welche KI-Funktionen tatsächlich verfügbar sind, hängt vom eingerichteten Anbieter, dem gewählten Modell und dessen Fähigkeiten ab.

## Inhaltsverzeichnis

- [1. Überblick](#1-überblick)
- [2. Welche KI-Funktionen gibt es?](#2-welche-ki-funktionen-gibt-es)
- [3. KI-Anbieter und Betriebsarten](#3-ki-anbieter-und-betriebsarten)
- [4. KI einrichten](#4-ki-einrichten)
- [5. KI-Funktionen verwenden](#5-ki-funktionen-verwenden)
- [6. Modelle den Aufgaben zuweisen](#6-modelle-den-aufgaben-zuweisen)
- [7. Eigene Anbieter einrichten](#7-eigene-anbieter-einrichten)
- [8. Eigene Assistenten](#8-eigene-assistenten)
- [9. Datenschutz und Einwilligungen](#9-datenschutz-und-einwilligungen)
- [10. Websuche](#10-websuche)
- [11. Offline-Übersetzung](#11-offline-übersetzung)
- [12. Kosten und laufende Assistenten](#12-kosten-und-laufende-assistenten)
- [13. Fehlerbehebung](#13-fehlerbehebung)
- [14. Weiterführende Dokumentation](#14-weiterführende-dokumentation)

## 1. Überblick

Lunivo Writer ist eine lokale Desktop-Textverarbeitung. Die KI-Funktionen sind optional und werden erst nach eigener Einrichtung verwendet. Je nach Aufgabe kann Lunivo einen Online-Dienst oder ein lokales Modell auf dem eigenen Rechner ansprechen.

Die KI kann beim Überarbeiten und Verstehen von Text helfen. Sie ersetzt nicht die eigene Prüfung: Ergebnisse können unvollständig oder falsch sein. Lies Vorschläge deshalb durch, bevor du sie in ein Dokument übernimmst.

### Voraussetzungen

- Lunivo Writer ist installiert und startet.
- Für einen Online-Anbieter ist ein gültiger API-Schlüssel erforderlich.
- Für lokale KI muss Ollama installiert sein und ein passendes Modell lokal verfügbar sein.
- Das ausgewählte Modell muss die gewünschte Aufgabe unterstützen.
- Für Online-Funktionen wird eine Internetverbindung benötigt.

## 2. Welche KI-Funktionen gibt es?

Die KI-Einstellungen von Lunivo enthalten getrennte Aufgabenbereiche. Dadurch kann für verschiedene Aufgaben jeweils ein anderes Modell verwendet werden.

| Funktion | Zweck |
|---|---|
| Chatbot | Fragen stellen und mit einem KI-Assistenten über Inhalte sprechen |
| KI-Korrektur | Text sprachlich überarbeiten und Korrekturvorschläge erhalten |
| Zusammenfassen | Längere Inhalte auf die wesentlichen Aussagen reduzieren |
| Übersetzung | Text in eine andere Sprache übertragen |
| Textanalyse | Einen Text untersuchen und eine strukturierte Einschätzung anfordern |
| Bildgenerierung | Bilder mithilfe eines dafür geeigneten Anbieters bzw. Modells erzeugen |
| Websuche | Eine Websuche als Informationsquelle für KI-gestützte Aufgaben verwenden |
| Eigene Assistenten | Eigene, auf einen bestimmten Zweck ausgerichtete Assistenten definieren |

Nicht jedes Modell beherrscht jede Aufgabe. Insbesondere Bildgenerierung benötigt einen dafür geeigneten Dienst. Wenn eine Aufgabe nicht angeboten wird oder fehlschlägt, prüfe die Fähigkeiten des gewählten Modells und die Konfiguration des Anbieters.

### KI-Korrektur und normale Schreibhilfe

Die normale Schreibhilfe und die KI-Korrektur sind unterschiedliche Funktionen:

- Die eingebauten Prüfer und gegebenenfalls LanguageTool melden Fundstellen als Karten in der Seitenleiste.
- KI-Vorschläge können ebenfalls als Funde in der Seitenleiste erscheinen.
- Die KI-Korrektur (F8) bearbeitet den ausgewählten bzw. vorgesehenen Text direkt. Sie ist nicht dasselbe wie die Prüfung mit F7 und erzeugt keine Fundkarten.
- Vorschläge der Schreibhilfe werden grundsätzlich erst nach deiner Entscheidung übernommen.

Weitere Informationen zu den Prüfungsstufen stehen in [Prüfung, Vorhersage und KI](pruefung-und-ki.md).

## 3. KI-Anbieter und Betriebsarten

Lunivo unterstützt mehrere Wege, ein KI-Modell anzusprechen.

### Lokale KI mit Ollama

Ollama führt Modelle auf dem eigenen Rechner aus. Der Text muss dafür nicht an einen externen KI-Anbieter übertragen werden.

1. Installiere Ollama nach dessen eigener Installationsanleitung.
2. Lade ein Modell herunter, das die gewünschte Aufgabe unterstützt.
3. Stelle sicher, dass Ollama läuft.
4. Öffne in Lunivo **Optionen → Name und KI → Prüfung und KI**.
5. Wähle Ollama bzw. das lokale Modell für die gewünschte Aufgabe aus.
6. Prüfe mit einer kurzen, unverfänglichen Texteingabe, ob die Verbindung funktioniert.

Die Leistung hängt von Modellgröße und Rechnerausstattung ab. Ein lokales Modell kann langsamer sein oder weniger Fähigkeiten besitzen als ein leistungsfähiger Online-Dienst.

### Online-Anbieter

Lunivo kann Online-KI-Dienste über ihre API ansprechen. Dazu gehören die integrierten Anbieter und OpenAI-kompatible Schnittstellen. Je nach aktueller Konfiguration sind beispielsweise OpenAI, OpenRouter, Gemini, Mistral, Groq, DeepSeek oder Together AI nutzbar. Claude wird über Anthropic angebunden.

Für einen Online-Anbieter benötigst du in der Regel:

- einen API-Schlüssel des Anbieters,
- eine gültige Modellkennung,
- gegebenenfalls einen eingerichteten Zugang bzw. ein verfügbares Guthaben beim Anbieter.

API-Schlüssel werden vom jeweiligen Anbieter ausgestellt. Beachte dessen Nutzungsbedingungen, Datenschutzbestimmungen und mögliche Kosten. Ein ChatGPT- oder Webseitenkonto ist nicht automatisch mit einem API-Zugang gleichzusetzen.

### Argos Translate

Für Übersetzungen kann Lunivo zusätzlich Argos Translate lokal verwenden. Diese Übersetzung läuft offline und überträgt den Text nicht an einen KI-Anbieter. Einzelheiten stehen im Abschnitt [Offline-Übersetzung](#11-offline-übersetzung).

## 4. KI einrichten

Die KI-Konfiguration befindet sich in den Optionen.

1. Öffne **☰ Menü → Optionen** oder drücke **F9**.
2. Wähle links **Name und KI**.
3. Öffne unter **Weitere Einstellungen** den Bereich **Prüfung und KI**.
4. Richte zunächst einen Anbieter ein und hinterlege bei Bedarf den API-Schlüssel.
5. Wähle für die benötigten Aufgaben ein Modell aus.
6. Prüfe die Datenschutz-Einwilligungen, bevor du erstmals Text an einen Online-Dienst sendest.

Die Optionen werden direkt übernommen. Es ist kein zusätzlicher Speichern-Knopf für jede einzelne Änderung erforderlich.

### API-Schlüssel

Ein API-Schlüssel authentifiziert Lunivo gegenüber einem Online-Anbieter.

- Verwende den Schlüssel des tatsächlich ausgewählten Anbieters.
- Achte darauf, dass der Schlüssel zum Anbieter und gegebenenfalls zum gewählten API-Endpunkt gehört.
- Behandle den Schlüssel wie ein Passwort und gib ihn nicht weiter.
- Wenn ein Schlüssel ungültig oder widerrufen ist, erstelle beim Anbieter einen neuen und aktualisiere die Einstellung in Lunivo.

### Für wen ist der Text?

Die KI-Korrektur kann berücksichtigen, für wen ein Text bestimmt ist. Ein amtliches Schreiben benötigt beispielsweise einen anderen Ton als eine private Nachricht. Wähle die passende Zielgruppe bzw. den vorgesehenen Empfänger in den KI-Einstellungen, wenn diese Auswahl für die Korrektur angeboten wird.

## 5. KI-Funktionen verwenden

Die genaue Darstellung kann sich je nach Aufgabe und Programmversion unterscheiden. Die folgenden Hinweise beschreiben den Zweck der Funktionen und die sinnvolle Arbeitsweise.

### Chatbot

Der Chatbot dient dazu, Fragen zu stellen und Inhalte mit einem KI-Assistenten zu besprechen.

1. Öffne den KI-Chat in Lunivo.
2. Stelle eine konkrete Frage oder beschreibe die Aufgabe.
3. Gib bei Bedarf den relevanten Text als Kontext mit.
4. Lies die Antwort kritisch durch.
5. Übernimm nur Informationen oder Formulierungen, die du geprüft hast.

Formuliere Fragen möglichst eindeutig. Nenne beispielsweise gewünschte Länge, Zielgruppe oder Schreibstil.

### KI-Korrektur

Die KI-Korrektur ist für eine sprachliche Überarbeitung gedacht.

1. Öffne das Dokument und markiere den Text, den du bearbeiten möchtest, sofern die Funktion eine Auswahl verwendet.
2. Starte die KI-Korrektur mit **F8**.
3. Prüfe das Ergebnis im Dokument.
4. Kontrolliere insbesondere Namen, Zahlen, Fachbegriffe, Zitate und die beabsichtigte Aussage.

Die KI kann Formulierungen verändern. Vergleiche das Ergebnis mit dem Original, damit keine wichtige Bedeutung verloren geht.

### Korrekturvorschläge in der Schreibhilfe

KI-Vorschläge können neben den übrigen Prüfergebnissen als Karten in der Schreibhilfe erscheinen. Prüfe die Begründung und den Vorschlag, bevor du eine Änderung übernimmst. Die übrigen Prüfstufen bleiben davon getrennt.

### Zusammenfassen

Die Zusammenfassung verdichtet einen längeren Text auf seine Kernaussagen. Prüfe, ob wichtige Einschränkungen, Zahlen, Gegenargumente oder Schlussfolgerungen fehlen. Eine Zusammenfassung ist eine verkürzte Wiedergabe und ersetzt nicht das Original.

### Übersetzen

Für die Übersetzung kann ein KI-Modell, Argos Translate oder die automatische Auswahl verwendet werden. Welche Variante verwendet wurde, wird im Ergebnis kenntlich gemacht. Siehe [Offline-Übersetzung](#11-offline-übersetzung).

### Textanalyse

Die Textanalyse lässt einen Text anhand einer KI-Aufgabe untersuchen. Die Aussagekraft hängt vom Modell und der Aufgabenstellung ab. Betrachte das Ergebnis als Hilfestellung und nicht als verbindliche fachliche Bewertung.

### Bildgenerierung

Die Bildgenerierung benötigt einen Anbieter bzw. ein Modell, das Bilder erzeugen kann. Ein gewöhnliches Textmodell unterstützt diese Funktion nicht automatisch. Wenn die Bildgenerierung nicht verfügbar ist, prüfe die zugewiesene Aufgabe und die Fähigkeiten des ausgewählten Anbieters.

## 6. Modelle den Aufgaben zuweisen

In der Modellzuweisung kann für einzelne Aufgaben ein eigenes Modell ausgewählt werden. Das ist hilfreich, wenn ein Anbieter beispielsweise ein schnelles Textmodell und ein anderes Modell für anspruchsvollere Aufgaben bereitstellt.

Die Aufgabenbereiche umfassen unter anderem:

- Chatbot
- Zusammenfassen
- Übersetzung
- Textanalyse
- Bildgenerierung

Wähle für jede Aufgabe ein Modell, das die benötigte Funktion unterstützt. Eine Modellkennung muss exakt zum ausgewählten Anbieter passen. Die Auswahl **Automatisch** kann – soweit für die Aufgabe vorgesehen – eine verfügbare und erlaubte Variante wählen.

### Hinweise zur Auswahl

- Ein Textmodell ist nicht automatisch ein Bildmodell.
- Nicht jedes Modell unterstützt alle Eingabe- und Ausgabeformate.
- Größere Modelle benötigen häufig mehr Rechenleistung oder verursachen höhere API-Kosten.
- Ein lokal installiertes Modell muss auf dem Rechner tatsächlich vorhanden und über Ollama erreichbar sein.

## 7. Eigene Anbieter einrichten

Neben den integrierten Anbietern können eigene Anbieter bzw. kompatible API-Endpunkte eingetragen werden.

Je nach Anbieter-Konfiguration werden insbesondere folgende Angaben benötigt:

- **Name:** Bezeichnung, unter der der Anbieter in Lunivo erscheint.
- **URL:** API-Endpunkt des Dienstes.
- **API-Schlüssel:** Zugangsschlüssel, sofern der Dienst einen verlangt.
- **Modell:** Modellkennung, die der Endpunkt erwartet.
- **Fähigkeiten:** Aufgaben, die der Anbieter bzw. das Modell unterstützt.

Trage nur die offiziellen Angaben des jeweiligen Dienstes ein. Eine falsche URL, ein nicht passender Schlüssel oder eine unbekannte Modellkennung führen häufig zu Verbindungs- oder Antwortfehlern.

Wenn ein Anbieter mehrere Modelle bereitstellt, prüfe, ob die Modellkennung in der Modellzuweisung korrekt ausgewählt ist.

## 8. Eigene Assistenten

Mit eigenen Assistenten lassen sich wiederverwendbare Aufgabenbeschreibungen bzw. Prompts für bestimmte Arbeitsabläufe anlegen.

Ein Assistent sollte möglichst klar festlegen:

- welche Aufgabe er erfüllen soll,
- welchen Text oder Kontext er berücksichtigen soll,
- welche Zielgruppe oder welcher Stil gewünscht ist,
- in welcher Form das Ergebnis zurückgegeben werden soll.

Beispiel für eine Aufgabenbeschreibung:

> Überarbeite den bereitgestellten Text in verständlichem, sachlichem Deutsch. Behalte die Aussage, Namen, Zahlen und Fachbegriffe bei. Ergänze keine Informationen, die nicht im Ausgangstext stehen. Gib nur den überarbeiteten Text zurück.

Passe die Beschreibung an deinen Zweck an. Prüfe jedes Ergebnis, bevor du es in ein Dokument übernimmst.

## 9. Datenschutz und Einwilligungen

Lunivo unterscheidet zwischen lokaler Verarbeitung und der Übertragung von Text an externe Dienste.

### Lokale Verarbeitung

Bei lokalen Ollama-Modellen und lokalen Diensten, die über eine lokale Adresse angesprochen werden, ist keine Einwilligung zur Übertragung an einen externen Anbieter erforderlich. Die Verarbeitung findet auf dem eigenen Rechner bzw. im lokalen Dienst statt.

### Online-Verarbeitung

Wenn Text an einen Cloud-Anbieter gesendet werden soll, benötigt Lunivo vorher eine Einwilligung.

- Beim ersten entsprechenden Aufruf kann Lunivo vor dem Senden nachfragen.
- Wenn du die Übertragung ablehnst, wird der Text nicht an diesen Anbieter gesendet.
- Einwilligungen können einzeln oder vollständig widerrufen werden.
- Nach einem Widerruf wird für eine spätere Übertragung erneut eine Einwilligung benötigt.

Übertrage keine vertraulichen, persönlichen oder fremden Inhalte an einen Online-Dienst, wenn du dazu nicht berechtigt bist. Prüfe im Zweifel die Datenschutzregeln deiner Organisation und die Bedingungen des Anbieters.

### Was bedeutet die Einwilligung?

Die Einwilligung erlaubt die Übermittlung der jeweils benötigten Textinhalte an den gewählten Online-Dienst. Sie ist keine Garantie dafür, wie der Anbieter die Daten anschließend verarbeitet. Dafür gelten zusätzlich die Datenschutz- und Nutzungsbedingungen des Anbieters.

## 10. Websuche

Lunivo kann eine Websuche als zusätzliche Informationsquelle für KI-gestützte Aufgaben verwenden. In den Einstellungen sind Suchdienste wie SearXNG und Brave Search vorgesehen. Je nach Dienst können eine URL bzw. ein Zugangsschlüssel und die gewünschte Anzahl der Suchtreffer relevant sein.

### Einrichtung

1. Öffne **Optionen → Name und KI → Prüfung und KI**.
2. Suche die Einstellungen für Websuche.
3. Wähle bzw. konfiguriere den unterstützten Suchdienst.
4. Hinterlege die vom Dienst benötigten Zugangsdaten.
5. Stelle die gewünschte Trefferanzahl ein.

Die Websuche benötigt eine Internetverbindung. Suchergebnisse können veraltet, unvollständig oder falsch sein. Öffne wichtige Quellen selbst und prüfe Veröffentlichungsdatum, Urheber und Inhalt.

## 11. Offline-Übersetzung

Für die Übersetzung gibt es drei Betriebsarten in der Modellzuweisung:

| Auswahl | Verhalten |
|---|---|
| Bestimmtes KI-Modell | Verwendet das fest zugewiesene Modell |
| Lokal (offline) | Übersetzt mit Argos Translate; der Text verlässt den Rechner nicht |
| Automatisch | Verwendet eine erlaubte und erreichbare KI, sonst die lokale Übersetzung |

Wenn eine KI-Anfrage fehlschlägt oder die erforderliche Datenschutz-Einwilligung abgelehnt wird, kann die automatische Auswahl einmal auf die lokale Übersetzung zurückfallen. Im Ergebnis wird kenntlich gemacht, ob mit **KI** oder **Lokal** übersetzt wurde.

Deutsch und Englisch sind in der mitgelieferten Paketkonfiguration vorgesehen. Weitere Sprachpaare können über **Offline-Sprachen** in den Schreibhilfe-Einstellungen auf Wunsch ergänzt werden.

Die lokale Übersetzung benötigt die optionale Argos-Translate-Bibliothek und passende Sprachpakete. Fehlt die Bibliothek, bleibt Lunivo grundsätzlich startfähig; die lokale Übersetzung steht dann jedoch nicht zur Verfügung.

## 12. Kosten und laufende Assistenten

Online-Anbieter können die Nutzung nach Anfragen, verarbeiteten Textmengen oder anderen Tarifen berechnen. Lunivo legt die Preise des jeweiligen Anbieters nicht fest.

Beachte besonders:

- Große Textmengen können mehr Kosten verursachen als kurze Eingaben.
- Häufige Wiederholungen und umfangreiche Kontexte können zusätzliche Anfragen auslösen.
- Prüfe die Abrechnung und Nutzungsgrenzen direkt beim Anbieter.
- Nutze für Tests zunächst kurze, nicht vertrauliche Texte.

**Fortlaufende Assistenten** können bei Änderungen am Text erneut Anfragen auslösen. Das kann zu wiederholter Datenübertragung und zusätzlichen Kosten führen. Verwende diese Funktion bewusst und beobachte, wann sie aktiv ist.

## 13. Fehlerbehebung

| Problem | Mögliche Ursache und Prüfung |
|---|---|
| Keine KI-Antwort | Prüfe, ob ein Anbieter und ein Modell eingerichtet sind und der Dienst erreichbar ist. |
| API-Fehler oder Authentifizierungsfehler | API-Schlüssel kontrollieren; prüfen, ob er zum Anbieter gehört und noch gültig ist. |
| Modell nicht gefunden | Modellkennung mit der Angabe des Anbieters vergleichen. |
| Lokales Ollama-Modell antwortet nicht | Prüfen, ob Ollama läuft und das Modell lokal heruntergeladen wurde. |
| Aufgabe wird nicht unterstützt | Ein Modell auswählen, das die benötigte Fähigkeit besitzt. |
| Bildgenerierung funktioniert nicht | Prüfen, ob ein bildfähiger Anbieter bzw. ein passendes Bildmodell zugewiesen ist. |
| Online-Anfrage wird nicht gesendet | Datenschutzabfrage prüfen; bei Ablehnung wird nichts an den Cloud-Dienst übertragen. |
| Übersetzung funktioniert offline nicht | Argos-Translate-Bibliothek und passendes Sprachpaket prüfen. |
| Websuche liefert keine Treffer | Suchdienst, URL, Zugangsdaten und Internetverbindung kontrollieren. |
| Anfrage ist langsam | Modellgröße, Rechnerleistung, Netzverbindung und Auslastung des Anbieters berücksichtigen. |

Wenn ein Problem bestehen bleibt, notiere die verwendete Aufgabe, den Anbieter, die Modellkennung und die genaue Fehlermeldung. Veröffentliche dabei niemals deinen API-Schlüssel oder vertrauliche Dokumentinhalte.

## 14. Weiterführende Dokumentation

- [Prüfung, Vorhersage und KI](pruefung-und-ki.md) – Schreibhilfe, Prüfstufen und KI-Korrektur.
- [Einstellungen](einstellungen.md) – Überblick über das Optionen-Fenster.
- [Aufbau der Optionen](aufbau-optionen.md) – Seiten, Gruppen und Fundorte der Einstellungen.
- [Lesen und Schreiben](lesen-und-schreiben.md) – Schreibhilfe und weitere Schreibfunktionen.
- [Projekt-README](../README.md) – Installation, Voraussetzungen und Überblick über Lunivo Writer.

---

[Zurück zur README](../README.md)
