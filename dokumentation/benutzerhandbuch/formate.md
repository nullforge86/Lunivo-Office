# Dateiformate

Quelle: `src/lunivo_writer/dienste/formate.py` (Verzeichnis); neues Format = Eintrag dort + Leser/Schreiber.

| Format | Öffnen | Speichern | Unterstützt | Nicht unterstützt |
|---|---|---|---|---|
| DOCX-Dokument (`.docx`) | ja | ja | Formatvorlagen mit Vererbung; Zeichen- und Absatzformat; Listen; Tabellen mit verbundenen Zellen; Bilder im Text und schwebend; Kopf- und Fußzeilen; Abschnitte; Kommentare; Fuß- und Endnoten; Felder; Lesezeichen und Verweise | Verschachtelte Tabellen; Formeln (OMML); Zeichnungen und SmartArt außer den eigenen Formen; Makros |
| DOCX-Vorlage (`.dotx`) | ja | nein | wie DOCX | Speichern als Vorlage |
| DOCX-Dokument mit Makros (`.docm`) | ja | nein | wie DOCX | Makros |
| OpenDocument-Text (`.odt`) | ja | ja | Absätze, Zeichenformat, Listen, Tabellen, Bilder, Seitenformat | Änderungsverfolgung; Formeln; Formulare |
| Flaches OpenDocument (`.fodt`) | ja | nein | wie ODT | Speichern |
| Rich Text (`.rtf`) | ja | ja | Absätze, Zeichenformat, Listen, Tabellen, Bilder, Kopf- und Fußzeile | Fußnoten; Kommentare; Zeichnungen |
| Textdatei (`.txt`) | ja | ja | Reiner Text (UTF-8, Windows-1252 beim Lesen) | Formatierung; Tabellen; Bilder; Kopf- und Fußzeilen |
| PDF (`.pdf`) | nein | ja | Ausgabe mit Seitenlayout, Lesezeichen, Verweisen | Öffnen; Bearbeiten nach dem Export |
