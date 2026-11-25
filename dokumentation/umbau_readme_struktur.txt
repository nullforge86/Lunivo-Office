LUNIVO OFFICE – UMBAU AUF DIE STRUKTUR DES URSPRUENGLICHEN PROMPTS
Stand: 25.11.2026 (Arbeitsbranch: umbau/readme-struktur, noch nicht committet)
====================================================================


1. AUSGANGSLAGE
---------------
Der Stand vor dem Absturz (Migration der README-Struktur, Schritt 9) ist nicht
mehr vollstaendig vorhanden. Gefundene Sicherungen:

  Ort                                                        Inhalt
  ---------------------------------------------------------  ---------------------------------------------
  ~/Wiederherstellung/projekt/                               nur framework/ (232 Dateien), 4x vcl, 2x writer,
                                                             1x system, Bericht migration/abschluss.md
  ~/Wiederherstellung/src-vor-phase7-1244.tgz                kompletter Code VOR der Verschiebung (alte Ordner)
  ~/.claude/sicherung/src-vor-phase7-1244.tgz                Kopie davon
  ~/Videos/Lunivo-Office-aufgeraeumt/Lunivo-Office-aufgeraeumt   Git-Stand vom 24.11. (letzter Commit ab7c5b1)
  ~/Lunivo-Office-main, ~/Vorlagen/.../src.zip               aeltere Staende
  GitHub nullforge86/Lunivo-Office                           Branch refactor/grundlegende-neustrukturierung
  Timeshift                                                  sichert /home nicht -> keine Hilfe

Entscheidung des Eigentuemers: NICHT von vorne anfangen, sondern den heutigen
Stand (oberflaeche / farmwork / core / infrastruktur) auf die Struktur der
README umbauen.


2. ZIELSTRUKTUR (laut README)
-----------------------------
  src/core        Dokumentmodell, Fachlogik, Qt-frei
  src/framework   Anwendungsschicht, einziges Zugangstor zum Kern, Qt-frei
  src/vcl         Darstellung; vcl/qt = einzige Stelle mit Qt
  src/writer      Steuerung der Oberflaeche, Qt-frei
  src/filter      Dateiformate (docx, odt, pdf, rtf, txt)
  src/system      Dateisystem, Einstellungen, Pfade, Ressourcen
  (kein Ordner src/lunivo_writer mehr)

Richtung:   vcl/qt -> writer -> framework -> core / filter / system


3. ZUORDNUNG ALT -> NEU (so ausgefuehrt)
----------------------------------------
  core                          -> core
  farmwork                      -> framework
  infrastruktur                 -> system
  ressourcen (im Paket)         -> system/ressourcen
  editor                        -> core/editor            (Uebergang)
  korrektur                     -> core/korrektur         (Uebergang)
  ki                            -> framework/ki           (Uebergang)
  dienste/docx|odt|pdf|rtf|txt  -> filter/<format>        (Uebergang)
  dienste/ausgabe, dateizugriff,
          dokumentpflege, integrationen
                                -> framework/dokumentverwaltung/<name>  (Uebergang)
  app.py                        -> vcl/qt/fenster/app.py
  oberflaeche/ (395 Python-Dateien), je Datei nach Qt-Abhaengigkeit:
     mit Qt (279 Dateien)       -> vcl/qt/...
     ohne Qt (116 Dateien)      -> writer/...  bzw. vcl/rendering (Zeichnen)

  Bereich der Oberflaeche      Qt-Seite (vcl/qt/...)         Qt-freie Seite
  ---------------------------  ----------------------------  -------------------
  band                         widgets/ribbon                writer/werkzeugleisten
  baukasten                    widgets/bausteine             writer/baukasten
  bauteile                     widgets/bausteine/bauteile    writer/baukasten/bauteile
  dialoge                      widgets/dialoge               writer/dialoge
  dokument                     widgets/dokumentansicht       writer/dokumentansicht
  funktionen                   widgets/funktionen            writer/funktionen
  hauptfenster                 fenster                       writer/hauptfenster
  kontext                      widgets/kontextmenues         writer/kontextmenues
  seitenleiste                 widgets/seitenleisten         writer/seitenleisten
  statusleiste                 widgets/statusleiste          writer/statusleiste
  zeichnen                     rendering/zeichnen            vcl/rendering/zeichnen

Regel fuer "ohne Qt": Eine Datei kommt nur dann nach writer, wenn sie weder
selbst Qt importiert noch (auch indirekt) eine Qt-Datei der Oberflaeche.


4. WAS BEREITS ERLEDIGT IST
---------------------------
  [x] 847 Dateien mit "git mv" verschoben (Verlauf bleibt erhalten)
  [x] 688 Dateien umgeschrieben: alle Importe, Pfadangaben in Tests,
      Werkzeugen, Skripten, Dokumentation
  [x] 52 fehlende __init__.py angelegt
  [x] Alle 881 Module lassen sich importieren, bis auf die unter 5 genannten
  [x] Schichtenregeln neu geschrieben: src/framework/pruefung/architektur.py
  [x] Importwaechter angepasst: src/framework/pruefung/importe.py
  [x] Uebergangsliste neu abgebildet: src/framework/pruefung/uebergang.py
      -> Pruefung ergab exakt dieselben 176 Verletzer wie vorher
         (keine neuen, keine ueberholten Eintraege)
  [x] Darstellungswaechter auf vcl + writer umgestellt
      (src/writer/baukasten/pruefung/darstellung_waechter.py)


5. NOCH OFFEN (naechste Schritte, in dieser Reihenfolge)
--------------------------------------------------------
  [x] Pfade ressourcen_pfade.py und pfade.py an die neue Ebenentiefe angepasst
  [x] __version__ jetzt in src/framework/schnittstellen/version.py
  [x] main.py haengt den Importwaechter vor dem Start ein
  [x] Waechtertests auf die neuen Ordner angepasst (Edit erledigt)
  [x] pyproject.toml, skripte/starten-qt.sh, werkzeuge/erstellung/deb-bauen.sh
  [x] CLAUDE.md: Schichtentabelle und Pfade (Git-Haken/CI rufen dieselben
      Testdateien auf, Aenderung nicht noetig)
  [x] Importpruefung ueber alle Module: 882 Module, 0 Fehler
  [ ] Die vier Waechtertests ausfuehren (Freigabe des Eigentuemers noetig)
  [ ] AGENTS.md: Schichtnamen angleichen
  [ ] Programmstart per Hand pruefen (python3 main.py), Aussehen vergleichen
  [ ] Commit auf umbau/readme-struktur (Git-Haken fuehrt die Waechter aus)


6. BEKANNTE ABWEICHUNGEN VON DER README
---------------------------------------
  - writer/ ist nur so weit Qt-frei, wie die Dateien vorher schon Qt-frei
    waren; fachliche Steuerung aus Qt-Dateien herauszuloesen ist ein
    eigener, spaeterer Schritt.
  - Uebergangsordner (core/editor, core/korrektur, framework/ki, filter,
    framework/dokumentverwaltung/...) sind noch nicht in die fachlichen
    Unterordner der README einsortiert.
  - Icons liegen weiter in <Projekt>/ressourcen/ (README: system/ressourcen/icons).
  - Unterordner heissen teils doppelt (vcl/qt/fenster/fenster/...).
  - Historische Berichte unter dokumentation/berichte/ nennen noch alte Pfade.


7. RUECKWEG
-----------
  Der Umbau liegt auf dem Branch umbau/readme-struktur. Der vorherige Stand
  ist unveraendert auf dem Branch refactor/grundlegende-neustrukturierung
  (lokal und auf GitHub).
  Zurueck:  git checkout -f refactor/grundlegende-neustrukturierung
