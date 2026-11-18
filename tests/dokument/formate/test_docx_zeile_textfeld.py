"""Aus einer Formular-DOCX (PDF-Umwandlung): „mindestens“-Zeilenabstand, Textfeld-Innenabstand, Gruppe in der Zeile."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import zipfile


def test_zeilenabstand_mindestens_hin_und_zurueck(app, tmp_path):
    from tests.hilfen_dokument import docx_rundlauf, sitzung
    s = sitzung("Zeile")
    s.absatzformat_anwenden({"zeilenabstand_art": "mindestens", "zeilenabstand": 20.0})
    gelesen, _schreib, _lese, pfad = docx_rundlauf(s.dokument, tmp_path)
    assert 'w:lineRule="atLeast"' in zipfile.ZipFile(pfad).read("word/document.xml").decode()
    a = next(iter(gelesen.absaetze()))
    assert a.format.get("zeilenabstand_art") == "mindestens" and a.format.get("zeilenabstand") == 20.0


def test_textfeld_innenabstand_null_setzt_text_an_den_rand(app):
    from lunivo_writer.editor.objekte import frei_objekt_text as T
    d = {"text": "XXXX", "schrift": "Liberation Sans", "pt": 11, "farbe": "#000000"}
    mit = T.textfeld_zeichnen(d, 120, 30)                                  # Standard: 8 px Innenabstand
    ohne = T.textfeld_zeichnen({**d, "innen": [0, 0, 0, 0]}, 120, 30)

    def erste_spalte(img):
        for x in range(img.width()):
            if any(img.pixelColor(x, y).alpha() > 0 for y in range(img.height())):
                return x / T._SS
    assert erste_spalte(ohne) < 3 <= 8 - 1 < erste_spalte(mit) + 1
