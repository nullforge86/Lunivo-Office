# Farmbau: verbindliche Kompositionsgrenze

**Alle regulären Startwege führen über `lunivo_writer.farmbau.start.main`.**
Qt-Komposition findet unter `farmbau/qt/` statt.
Der fachliche Dokumentenkern `core/` kennt weder Qt noch Farmbau oder Oberfläche.

```text
main.py / python -m lunivo_writer / console-script / starten-qt.sh
                        |
                        v
               farmbau/start.py
                        |
                        v
               farmbau/qt/anwendung.py
                  |             |
                  v             v
             oberflaeche/   adapter/qt/
                  |             |
                  +-----> core/ <+
```

## Regeln

1. Kein direkter Start von `kern/anwendung.py`; kein eigener Qt-Start in `app.py`.
2. Kein automatisches Zurückfallen auf alten Qt-Texteditor oder alternatives Modell.
3. Keine Qt-Importe im `core/`; fachliche Logik bleibt unabhängig.
4. Farmbau verdrahtet Komponenten; er enthält keine Dokumentbearbeitung.
5. Fehlende Implementierungen melden Fehler statt stillschweigend zu wechseln.

## Migrationsstand

Die erste Stufe erzwingt Farmbau für den **Anwendungsstart**. Der bestehende
Ordner `kern/` enthält Qt-gebundene Befehlsadapter und ist nicht mit
dem Qt-freien `core/` gleichzusetzen. `editor/` und Teile von
`dienste/` besitzen weiterhin historische Qt-Abhängigkeiten.
Ihre vollständige Vermittlung durch Farmbau erfordert weitere
gezielte Änderungen und Tests; sie wird hier nicht als erledigt behauptet.

Architekturtests: `tests/architektur/test_farmbau_grenze.py`.
