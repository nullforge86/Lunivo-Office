# Speichern, Dateiformate und Datensicherheit

Zentrale Übersicht über die Dateiformate, das Speichern und bekannte Grenzen.
Code: `src/lunivo_writer/services/file_service.py` (Formate), `sicher_schreiben.py` (sicherer Schreibweg),
`docx_writer.py` / `docx_reader.py` (DOCX), `odt_writer.py` / `odt_reader.py` (ODT, FODT),
`rtf_writer.py` / `rtf_reader.py` (RTF) sowie `src/lunivo_writer/ui/hauptfenster/dateien.py`
und `src/lunivo_writer/ui/baukasten/speichern_fenster.py` (Dateioberfläche).

**Lunivo liest und schreibt die unterstützten Formate selbst.** Es startet beim Öffnen und Speichern kein anderes Office-Programm
(geprüft mit `tests/test_odt_rtf.py::test_kein_fremdes_programm_beim_speichern_und_oeffnen`).

## Formate

Lunivo ist eine Textverarbeitung. **XLSX/XLS (Tabellenkalkulation) und PPTX/PPT (Präsentation) werden nicht unterstützt** — weder
Öffnen noch Speichern. Beim Öffnen entscheidet die Endung über den Leser, aber jeder Leser prüft den Inhalt selbst (ZIP-Paket bzw.
Dateikopf); eine falsche oder beschädigte Datei wird als Fehler gemeldet, nicht „irgendwie“ geöffnet.

| Format | Öffnen und Lesen | Bearbeiten | Speichern im selben Format (`Strg+S`) | Speichern unter | Export |
|---|---|---|---|---|---|
| DOCX (Office Open XML, ECMA-376) | ja, eigener Leser (python-docx); mit Kennwort über msoffcrypto | ja | ja | ja | – |
| DOTX, DOCM (Word-Vorlage, Word mit Makros) | ja, wie DOCX; Makros werden nicht ausgeführt und nicht übernommen | ja | nein, öffnet „Speichern unter“ | als DOCX/ODT/… | – |
| ODT (OpenDocument 1.3) | ja, eigener Leser | ja | ja | ja, eigener Schreiber | – |
| FODT (flaches ODT, eine XML-Datei) | ja, eigener Leser | ja | nein, öffnet „Speichern unter“ | als DOCX/ODT/… | – |
| RTF | ja, eigener Leser | ja | ja | ja, eigener Schreiber | – |
| TXT (UTF-8) | ja; UTF-8, sonst cp1252, sonst Latin-1 | ja | ja | ja | – |
| DOC, DOT (Word 97–2003), WPS (Works) | **nein**, klare Meldung mit dem Rat, im Ursprungsprogramm als DOCX zu speichern | – | – | – | – |
| PDF | **nein** | – | – | im selben Fenster wählbar, ist aber eine Ausgabe | ja (`QPdfWriter`) |
| PNG (Bild der Seite) | nein | – | – | – | ja, je Seite eine Datei |

DOC ist ein geschlossenes Binärformat; ohne fremdes Programm lässt es sich nicht verlässlich schreiben. Auf Wunsch des Eigentümers
(2026-10-27) ist es ganz entfernt statt halb unterstützt.

### Was ODT und RTF mitnehmen

| | ODT | RTF |
|---|---|---|
| Absätze: Ausrichtung, Einzüge, Abstände, Seitenumbruch davor | ja | ja |
| Überschriften (Ebene 1–9) | `text:h` mit Ebene | `\outlinelevel` und Vorlage „heading N“ |
| Zeichen: Schrift, Größe, fett, kursiv, unterstrichen, durchgestrichen, hoch/tief, Farbe, Hintergrund | ja | ja |
| Listen mit Punkten oder Nummern, mehrere Ebenen | ja | ja (`\pn` und angezeigter Listentext) |
| Tabellen, auch verbundene Zellen | ja | ja (verbundene Zellen beim Lesen getrennt) |
| Bilder im Text | PNG in `Pictures/` | PNG (`\pngblip`); beim Lesen auch JPEG und EMF mit Bitmap |
| Frei positionierte Bilder (im Text und in Kopf-/Fußzeile) | ja, Rahmen am Absatz (Lage, vor/hinter dem Text) | **nein**, mit Hinweis |
| Seitengröße, Ränder, Querformat | ja (`styles.xml`) | ja |
| Kopf- und Fußzeile mit Seitenzahl und Seitenanzahl, „Erste Seite anders“ | ja | ja |
| Titel, Autor | `meta.xml` | `\info` |
| Fuß- und Endnoten, Kommentare, Wasserzeichen, Seitenrahmen, Textspalten | **nein**, mit Hinweis | **nein**, mit Hinweis |

### Bekannte Einschränkungen

- **ODT/RTF:** siehe Tabelle; was fehlt, meldet der Bericht „Hinweise zum Speichern“ bzw. beim Öffnen. Formvorlagen werden als direkte
  Formatierung geschrieben (das Aussehen bleibt, die Vorlagennamen nicht).
- **TXT:** nur Text; Formatierung, Listen, Tabellen, Bilder, Kopf-/Fußzeile gehen verloren (Hinweis beim Speichern).
- **PDF:** Export ist eine Einbahnstraße. Ein PDF lässt sich in Lunivo nicht wieder öffnen oder bearbeiten.
- Was DOCX selbst nicht abdeckt (Textfelder, Formeln, Formen, Wasserzeichen u. a.), steht im Bericht über nicht Übernommenes.
- Schutz beim Öffnen: ZIP-Pakete über 512 MB entpackt und RTF-Dateien über 512 MB werden abgelehnt; wiederholte Tabellenzeilen und
  -spalten sind auf 1000 begrenzt.

### Strukturprüfung nach dem Schreiben

| Format | Geprüft |
|---|---|
| DOCX | ZIP-Paket, alle Prüfsummen, `[Content_Types].xml` und `word/document.xml` vorhanden und wohlgeformtes XML; verschlüsselt: OLE-Kopf |
| ODT | ZIP-Paket, Prüfsummen, erster Eintrag `mimetype` unkomprimiert = `application/vnd.oasis.opendocument.text`, `content.xml` und `META-INF/manifest.xml` wohlgeformt |
| RTF | Kopf `{\rtf`, Klammern ausgeglichen |
| PDF | Kopf `%PDF-`, Abschluss `%%EOF` |
| TXT | gültiges UTF-8 |

Das ist **keine vollständige Schemaprüfung** nach ECMA-376 oder ODF. Für eine Schemaprüfung von ODT eignet sich der ODF-Validator
(odf.openpreservation.org); die Referenzseiten von Microsoft, ECMA und OpenOffice waren bei der Erstellung aus der Arbeitsumgebung
nicht erreichbar und sind nicht ausgewertet.

## Sicherer Schreibweg

Jeder Speichervorgang — DOCX, TXT, ODT, RTF, PDF, auch Vorlagen — läuft über `sicher_schreiben.schreiben`:

1. **Sperre:** Dieselbe Datei kann nicht gleichzeitig zweimal gespeichert werden — im Programm (Sperre je Pfad) und zwischen
   Lunivo-Fenstern (`flock` auf eine Sperrdatei in `$XDG_RUNTIME_DIR/lunivo-sperren`). Der zweite Versuch bekommt eine klare Meldung.
2. **Temp-Datei im Zielordner** (`.<name>.lunivo-XXXX.tmp`, versteckt) — gleiches Dateisystem, damit das Ersetzen atomar ist.
3. **`fsync`** der Temp-Datei, dann **Strukturprüfung** (siehe oben). Ist die neue Fassung kaputt, wird nichts ersetzt.
4. **Sicherungskopie** der bisherigen Fassung nach `<Datenordner>/sicherungen/<Kennung>/` (Datenordner:
   `~/.local/share/<Organisation>/<Programm>/`). Je Dokument die letzten **5** Fassungen, höchstens **30 Tage**; ältere werden beim
   nächsten Speichern entfernt. `pfad.txt` im Ordner nennt die Originaldatei. Öffnen: `Optionen → Speichern → Sicherungskopien öffnen …`.
5. **Rechte übernehmen** (eine `0644`-Datei bleibt `0644`; neue Dateien folgen der `umask`), **`os.replace`**, `fsync` des Ordners.
   Symbolische Verknüpfungen werden aufgelöst: die Verknüpfung bleibt, ihr Ziel wird ersetzt.
6. Bei jedem Fehler wird die Temp-Datei entfernt. Reste nach einem Absturz werden beim nächsten Speichern derselben Datei weggeräumt
   (wenn älter als 10 Minuten).

**Vor dem Überschreiben** fragt die Oberfläche, wenn

- die Datei seit dem Öffnen oder letzten Speichern **außerhalb von Lunivo geändert** wurde (Änderungszeit oder Größe weichen ab) —
  etwa durch ein anderes Programm oder die Synchronisierung eines Cloud-Ordners. Abbrechen lässt die Datei unberührt; Überschreiben
  legt die fremde Fassung in die Sicherungskopien.
- ein anderes Office-Programm die Datei offen hat (Sperrdatei `.~lock.<name>#`, wie sie LibreOffice und andere anlegen).

**Erfolg** meldet die Statusleiste erst nach dem Ersetzen. Bei einem Fehler erscheint eine verständliche Meldung (z. B. „Auf dem
Datenträger ist nicht genug Platz. Die bisherige Datei ist unverändert.“), das Dokument bleibt geöffnet, bearbeitbar und als geändert markiert.

Die **automatische Sicherung** (Wiederherstellung nach Absturz, `<Datenordner>/recovery/`) nutzt denselben Schreibweg ohne Sicherungskopien.

### Was die Plattform garantiert

- **Lokale Linux-Dateisysteme (ext4, btrfs, xfs):** `rename` ist atomar. Nach einem Prozessabbruch liegt entweder die alte oder die neue
  Fassung vollständig vor (getestet: `test_prozessabbruch_waehrend_des_schreibens`). Bei Stromausfall gilt das, soweit Datenträger und
  Treiber `fsync` ehrlich umsetzen (Schreibcache der Platte). Getestet werden kann ein Stromausfall nicht.
- **Netz- und FUSE-Laufwerke** (SMB/CIFS, NFS, sshfs, rclone- oder andere Cloud-Mounts): Atomarität und `fsync` sind nicht zugesichert;
  `fsync` auf Ordnern kann fehlen. Lunivo versucht es und macht weiter.
- **Cloud-Ordner** (Nextcloud, Dropbox, Google Drive über Synchronisierungsprogramm): Lunivo schreibt nur lokal; die Synchronisierung
  macht ein fremdes Programm. Lunivo erkennt, wenn es die Datei inzwischen geändert hat, und fragt. Konflikte *innerhalb* des
  Synchronisierungsprogramms (z. B. Konfliktkopien) löst Lunivo nicht.
- Dateisperren unter Linux sind beratend: Andere Programme als Lunivo und LibreOffice (über seine Sperrdatei) werden nicht erkannt.

## Prüfen

Automatisch:

```bash
.venv/bin/python -m pytest tests/test_speichern_sicher.py tests/test_formats.py tests/test_odt_rtf.py
.venv/bin/python werkzeug/speicherpruefung.py          # alle Formate speichern, prüfen, öffnen; Protokoll in SQLite
```

Das Prüfprotokoll (`~/.cache/lunivo-writer/speicherpruefung.sqlite3`) enthält Test-ID, Zeit, Format, Testfall, Ergebnisse,
Größe, SHA-256 und Fehlerkategorie — keine Dokumentinhalte. Abfrage z. B. `sqlite3 <datei> "select format, testfall, fehlerkategorie from pruefung"`.

Von Hand (in einem eigenen Testordner, nicht mit echten Dokumenten):

1. Neues Dokument mit Umlauten schreiben, `Speichern unter` → Dateityp nacheinander DOCX, ODT, RTF, TXT, PDF. Jede Datei wieder öffnen
   (PDF in einem PDF-Betrachter) und den Text vergleichen.
2. Eine DOCX öffnen, ändern, `Strg+S` dreimal. `Optionen → Speichern → Sicherungskopien öffnen …` zeigt die Vorfassungen.
3. Datei öffnen, in einem anderen Programm (oder mit `touch`) ändern, in Lunivo `Strg+S` → Rückfrage erscheint; „Abbrechen“ lässt die Datei unverändert.
4. Ordner schreibschützen (`chmod a-w ordner`) und speichern → Meldung „Keine Schreibrechte …“, Dokument bleibt offen. Danach `chmod u+w ordner`.
5. Nach dem Test: `ls -la ordner` zeigt keine `.lunivo-*.tmp`-Reste.
