# DOCX-Korpus: Roundtrip-Bericht

Jedes Dokument: einlesen → ohne Änderung speichern → erneut einlesen; verglichen werden Text, Zeichenformat-Läufe, Tabellenstruktur, Bilder, Kopf-/Fußzeile.
Alle Dokumente sind selbst erzeugt (python-docx und eigenes XML), keine aus Word, LibreOffice oder Google Docs — siehe Grenze in `werkzeug/pruefen/docx_korpus.py`.

| Dokument | Abweichungen nach Roundtrip | Hinweise beim Lesen |
|---|---|---|
| `tabelle_verbunden` | keine | – |
| `kopf_fuss_abschnitte` | keine | – |
| `schwebendes_bild` | keine | – |
| `kommentare` | keine | – |
| `fussnoten` | keine | – |
| `inhaltsverzeichnis_und_verweise` | keine | – |
| `stile_vererbung` | keine | – |
| `schriften_und_sprachen` | keine | – |
| `ungewoehnlich` | keine | Verschachtelte Tabellen werden nicht dargestellt. |
