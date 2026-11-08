import os

import pytest
from PySide6.QtGui import QTextBlockFormat, QTextCursor, QTextDocument

from lunivo_writer.ai import dokumentensuche as DS
from lunivo_writer.ai import dokument_abschnitte as DA


def test_abschnitte_nach_ueberschriften_und_laenge():
    a = DS.abschnitte_bilden([(1, "Kündigung"), (0, "Die Kündigung muss schriftlich erfolgen und drei Monate vorher eingehen."),
                              (1, "Miete"), (0, "Die Miete beträgt 800 Euro monatlich, zahlbar im Voraus bis zum dritten Werktag."),
                              (0, "x " * 2000)])
    assert [t for t, _x in a][:2] == ["Kündigung", "Miete"]
    assert len(a) >= 4 and all(len(x) <= DS.MAX_ABSCHNITT + 50 for _t, x in a)


def test_frage_zu_fts():
    q = DS.frage_zu_fts("Was steht im Vertrag zur Kündigung?")
    assert '"vertrag"*' in q and '"kündigung"*' in q and "steht" not in q and " OR " in q
    assert DS.frage_zu_fts("Was ist das?") == "" and DS.frage_zu_fts('"; drop') == '"drop"*'


def _ordner(tmp_path):
    frei = tmp_path / "frei"; frei.mkdir()
    (frei / "vertrag.txt").write_text("Mietvertrag\n\nDie Kündigung muss schriftlich erfolgen.\n\nDie Miete beträgt 800 Euro.", encoding="utf-8")
    (frei / "andere.txt").write_text("Rezept für Apfelkuchen mit Zimt und Zucker, Backzeit 45 Minuten.", encoding="utf-8")
    (frei / ".versteckt").mkdir(); (frei / ".versteckt" / "geheim.txt").write_text("Kündigung geheim", encoding="utf-8")
    (frei / "bild.png").write_bytes(b"x")
    geheim = tmp_path / "privat"; geheim.mkdir()
    (geheim / "pass.txt").write_text("Die Kündigung des Kontos privat", encoding="utf-8")
    os.symlink(geheim / "pass.txt", frei / "link.txt")
    return str(frei), str(geheim)


def test_index_suche_aktualisierung_und_freigabe(tmp_path):
    frei, geheim = _ordner(tmp_path)
    idx = DS.Index(str(tmp_path / "i.sqlite"))
    b = idx.aktualisieren([frei])
    assert b["neu"] == 2 and b["fehler"] == 0                         # versteckt, Bild und Link zählen nicht
    t = idx.suchen("Wie läuft die Kündigung im Vertrag?", [frei])
    assert t and t[0]["datei"] == "vertrag.txt" and "schriftlich" in t[0]["text"] and t[0]["ort"].startswith("Abschnitt")
    assert not idx.suchen("Kündigung", [geheim])                      # nicht freigegeben: nie ein Treffer
    assert idx.aktualisieren([frei]) == {"neu": 0, "geaendert": 0, "entfernt": 0, "fehler": 0, "offen": 0}
    p = os.path.join(frei, "vertrag.txt")
    open(p, "a", encoding="utf-8").write("\n\nNeu: Haustiere sind erlaubt.")
    os.utime(p, (1, 2_000_000_000))
    assert idx.aktualisieren([frei])["geaendert"] == 1 and idx.suchen("Haustiere", [frei])
    os.remove(p)
    assert idx.aktualisieren([frei])["entfernt"] == 1 and not idx.suchen("Haustiere", [frei])
    assert idx.aktualisieren([]) ["entfernt"] == 1 and idx.anzahl() == (0, 0)     # Freigabe zurückgenommen: Index vergisst


def test_zeitgrenze_und_fehlerhafte_datei(tmp_path):
    frei, _g = _ordner(tmp_path)
    idx = DS.Index(str(tmp_path / "i.sqlite"))
    def lesen(p):
        if p.endswith("andere.txt"):
            raise ValueError("kaputt")
        return [("Abschnitt 1", "t", "Inhalt zum Suchen")]
    assert idx.aktualisieren([frei], lesen)["fehler"] == 1
    assert idx.aktualisieren([frei], lesen, zeitgrenze=0.0000001)["offen"] >= 0


def test_docx_ueberschriften_werden_abschnitte(tmp_path, qapp=None):
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])
    from lunivo_writer.models.page import PageSettings
    from lunivo_writer.services.docx_writer import write_docx
    d = QTextDocument(); c = QTextCursor(d)
    h = QTextBlockFormat(); h.setHeadingLevel(1)
    c.setBlockFormat(h); c.insertText("Garantie")
    c.insertBlock(QTextBlockFormat()); c.insertText("Die Garantie gilt zwei Jahre ab Kaufdatum des Geräts.")
    p = str(tmp_path / "a.docx"); write_docx(p, d, PageSettings(), sicherung=False)
    st = DA.lesen(p)
    assert st and "Garantie" in st[0][1] and "zwei Jahre" in st[0][2]


def test_chat_nutzt_freigegebene_dokumente_mit_fundstellen(tmp_path):
    from lunivo_writer.ai import ki as K
    frei, geheim = _ordner(tmp_path)
    k = K.KIKonfig(str(tmp_path / "ki.json")); k.setze("modell", "ollama:x")
    k.dokumentsuche_setzen(an=True, ordner=[frei])
    ki = K.KI(k)
    gesehen = {}
    def falsch(anweisung, text, bauplan=None, modell=None, optionen=None):
        gesehen["system"] = anweisung
        return {"ergebnis": "Schriftlich."}
    ki.anfrage = falsch
    r = ki.chat([{"rolle": "mensch", "text": "Wie muss die Kündigung erfolgen?"}])
    assert "schriftlich erfolgen" in gesehen["system"] and "Fundstellen:" in r["text"] and "vertrag.txt" in r["text"]
    assert "Kontos privat" not in gesehen["system"]
    k.dokumentsuche_setzen(an=False)
    gesehen.clear(); ki.chat([{"rolle": "mensch", "text": "Wie muss die Kündigung erfolgen?"}])
    assert "Auszüge aus Dokumenten" not in gesehen["system"]
    k.dokumentsuche_setzen(an=True)
    k.setze("modell", "claude-sonnet-5"); k.setze("claude_erlaubt", True)
    gesehen.clear(); r = ki.chat([{"rolle": "mensch", "text": "Wie muss die Kündigung erfolgen?"}])
    assert "system" not in gesehen and "Zustimmung" in r["fehler"]                  # ohne Einwilligung für den Anbieter geht nichts hinaus
    k.einwilligung_geben("Anthropic (Claude)", "auszug")
    r = ki.chat([{"rolle": "mensch", "text": "Wie muss die Kündigung erfolgen?"}])
    assert "Auszüge aus Dokumenten" in gesehen["system"]                          # mit Einwilligung für Auszüge dürfen die Treffer mit
