![Lunivo Office](bilder/lunivo-office.png)

# Lunivo Writer

Eine native Textverarbeitung für Linux, entwickelt mit Python 3 und PySide6/Qt Widgets. Die Schreibhilfe sitzt neben dem Dokument und zeigt Fundstellen mit Erklärungen und Vorschlägen. Änderungen übernimmt Lunivo nur auf deine Auswahl.

Lunivo braucht kein Konto und keine Internetverbindung für Schreiben, Prüfen und Speichern. Optionale Online-KI und externe Schreibhilfen werden erst nach eigener Einrichtung verwendet.

## Installation und Start

Voraussetzung ist Python 3.9 oder neuer. Beim ersten Start richtet das Skript eine eigene `.venv` ein und installiert die Projektabhängigkeiten:

```bash
./starten-qt.sh
```

Eine Datei lässt sich direkt öffnen:

```bash
./starten-qt.sh brief.docx
```

Mit `./starten-qt.sh --eintrag` wird ein Menüeintrag angelegt. `./starten-qt.sh --weg` entfernt diesen Eintrag; Programmumgebung und Dokumente bleiben erhalten.

## Was Lunivo kann

- Acht Register: Start, Einfügen, Seitenlayout, Referenzen, Überprüfen, Schreibhilfe, Sendungen und Ansicht.
- Eine Schreibhilfe für häufige Verwechslungen, Rechtschreibung, Grammatik, Wortvorhersage, Silbentrennung und Vorlesen.
- Dokumente in DOCX, ODT, FODT, RTF und TXT öffnen oder speichern. PDF und PNG lassen sich exportieren; PDF kann Lunivo nicht öffnen.
- Tabellen, Bilder, Formen, Diagramme, Formeln, Formatvorlagen, Kopf- und Fußzeilen sowie Seriendruck.
- Eine native Qt-Oberfläche mit Seitenleiste, Dokumentreitern und wahlweise Registerband oder Symbolleisten.

XLSX, XLS, PPTX, PPT sowie die alten DOC/DOT-Formate werden nicht unterstützt. Die bekannte Formatunterstützung und ihre Grenzen stehen in [Speichern und Dateiformate](docs/SPEICHERN.md).

## Datenschutz

Dokumente bleiben an dem Speicherort, den du auswählst. Einstellungen und Anwendungsdaten liegen in den XDG-Verzeichnissen des Benutzers. Optionale KI-Anbieter und Online-Dienste brauchen eine eigene Einrichtung; lokale Funktionen laufen ohne sie weiter.

## Dokumentation

- [Installation](docs/INSTALLATION.md)
- [Lesen und Schreiben](docs/lesen-und-schreiben.md)
- [Prüfung, Vorhersage und KI](docs/pruefung-und-ki.md)
- [Schreiben und Dokumente](docs/schreiben-und-dokumente.md)
- [Einstellungen](docs/einstellungen.md)
- [Speichern, Formate und Datensicherheit](docs/SPEICHERN.md)
- [Oberfläche](docs/oberflaeche.md)
- [Projektaufbau](docs/README.md)
- [UI-Technologie](docs/ui-technologie.md)
- [Interne Funktionen (Inventar)](docs/interne-funktionen.md)
- [Erweiterungen](docs/erweiterungen.md)
- [Entstehung](docs/ENTSTEHUNG.md)
- [Wohin Lunivo gehen soll](docs/RICHTUNG.md)

Weitere Hilfe gibt es im Programm unter **☰ Menü → Hilfe → Handbuch**.

## Mitmachen

Erfahrungen, Fragen und Verbesserungsvorschläge sind willkommen. Nutze dafür die [GitHub Discussions](../../discussions) oder melde einen [Fehler](../../issues/new?template=fehler.yml) beziehungsweise einen [Funktionswunsch](../../issues/new?template=wunsch.yml). Rechtschreibung muss dabei keine Rolle spielen.

## Lizenz

Lunivo steht unter der [MIT-Lizenz](LICENSE). Die mitgelieferten Lucide-Zeichnungen stehen unter ISC; der Lizenztext liegt in [docs/LIZENZ-LUCIDE.txt](docs/LIZENZ-LUCIDE.txt).
