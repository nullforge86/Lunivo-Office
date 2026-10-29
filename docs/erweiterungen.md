# Optionale Erweiterungen

Lunivo startet und funktioniert auch ohne zusätzliche Stimmen, Schriften, LanguageTool oder KI-Anbieter. Externe Erweiterungen werden getrennt installiert und liegen außerhalb des Projektordners.

| Erweiterung | Zweck | Einrichtung |
|---|---|---|
| **LanguageTool** | Zusätzliche Grammatikprüfung über „Gründlich prüfen“ | LanguageTool mit Java unter `~/.local/share/Lunivo/Lunivo Writer/languagetool/` ablegen |
| **Piper-Stimmen** | Aufgenommene Stimmen zum Vorlesen | `./stimme-holen.sh`; Stimmen arbeiten offline |
| **Leseschriften** | OpenDyslexic, Lexend und Atkinson Hyperlegible | `./schrift-holen.sh`; installiert benutzerspezifisch |
| **Ollama** | KI-Aufgaben mit einem lokalen Modell | Ollama und ein Modell selbst installieren, dann in Lunivo auswählen |
| **Online-KI** | Korrektur, Vorschläge und Übersetzung über einen Anbieter | Anbieter und persönlichen API-Schlüssel in den KI-Einstellungen einrichten |

LanguageTool wird als eigener Prozess auf dem Rechner gestartet und sendet den Text nicht an einen externen Dienst. Bei Online-KI wird der Text an den ausgewählten Anbieter übertragen.

Die Stimmen und Schriften lassen sich über die Skripte im Projekt ergänzen. Vor dem Download zeigen diese Skripte Ziel und Auswahl an; zum Entfernen bieten sie jeweils `--weg`.

---

[Zurück zur README](../README.md)
