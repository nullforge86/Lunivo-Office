"""Chat-Bezug: reine Logik (chat_bezug, ChatModell) und Dienst mit echtem Editor (Ersetzen/Einfügen in einem Undo-Schritt)."""
from types import SimpleNamespace

import pytest

from lunivo_writer.ki import chat_bezug as CB
from lunivo_writer.ki.chat_modell import ChatModell


def _bezug(**kw):
    a = dict(von=2, bis=5, markiert=True, revision=7, alt="abc", dokument=1)
    a.update(kw)
    return CB.bezug_bauen(**a)


def test_bezug_bauen_ohne_markierung_hat_keinen_alttext():
    b = _bezug(markiert=False, von=4, bis=4)
    assert b["alt"] == "" and not b["markiert"] and b["von"] == b["bis"] == 4


def test_bezug_pruefen_streng():
    b = _bezug()
    assert CB.bezug_pruefen(b, 7, 1) == (True, "")
    assert CB.bezug_pruefen(b, 8, 1) == (False, CB.MELDUNG_GEAENDERT)
    assert CB.bezug_pruefen(b, 7, 2) == (False, CB.MELDUNG_EDITOR)
    assert CB.bezug_pruefen(b, None, None)[0] is False
    assert CB.bezug_pruefen(None, 7, 1) == (False, CB.MELDUNG_KEIN_BEZUG)


def test_bezug_pruefen_erkennt_editor_und_dokumentobjekt():
    editor = object()
    anderes_editor = object()
    erstes_dokument = object()
    anderes_dokument = object()
    b = CB.bezug_bauen(0, 3, True, 7, "alt", 123,
                       editor_obj=editor, dokument_obj=erstes_dokument)
    assert CB.bezug_pruefen(b, 7, 123, dokument_jetzt=erstes_dokument,
                            editor_obj_jetzt=editor) == (True, "")
    assert CB.bezug_pruefen(b, 7, 123, dokument_jetzt=anderes_dokument,
                            editor_obj_jetzt=editor) == (False, CB.MELDUNG_EDITOR)
    assert CB.bezug_pruefen(b, 7, 123, dokument_jetzt=erstes_dokument,
                            editor_obj_jetzt=anderes_editor) == (False, CB.MELDUNG_EDITOR)


def test_vorschau_stuecke_diff_und_rueckfall(monkeypatch):
    st = CB.vorschau_stuecke("Das ist gut.", "Das ist sehr gut.")
    assert "".join(t for a, t in st if a != "neu") == "Das ist gut."
    assert "".join(t for a, t in st if a != "entfernt") == "Das ist sehr gut."
    monkeypatch.setattr(CB.K, "aenderungen", lambda a, n: None)
    assert CB.vorschau_stuecke("alt", "neu") == [("entfernt", "alt"), ("neu", "neu")]
    assert CB.vorschau_einfuegen("x") == [("neu", "x")] and CB.vorschau_einfuegen("") == []


def test_modell_gibt_bezug_an_antwort_weiter():
    m = ChatModell()
    b = _bezug()
    k = m.anfrage("Frage", None, b)
    assert "bezug" not in m.nachrichten[0] and m.bezug_von(0) is None
    assert m.antwort(k, "Antwort", None)
    assert m.bezug_von(1) is b
    assert all("bezug" not in v for v in m.verlauf())          # geht nie an die KI
    m.wiederholen()
    assert m._bezug_offen is None
    k = m.anfrage("Neu", None, None)
    m.antwort(k, "A2")
    assert m.bezug_von(len(m.nachrichten) - 1) is None


@pytest.fixture
def dienst(app, tmp_path, monkeypatch):
    from PySide6.QtGui import QTextCursor
    from PySide6.QtWidgets import QPlainTextEdit
    from lunivo_writer.ki import ki_dienst as S
    from lunivo_writer.oberflaeche.dokument.bearbeitung.editor_schreibhilfe import SchreibhilfeBaustein

    class Ed(SchreibhilfeBaustein, QPlainTextEdit):
        pass

    monkeypatch.setattr(S, "data_dir", lambda: str(tmp_path))
    ed = Ed()
    ed.setPlainText("Das ist ein Text.")
    fenster = SimpleNamespace(ed=ed, current_editor=lambda: fenster.ed)
    assistent = SimpleNamespace(thema="", gelernt=SimpleNamespace(daten={}), pruefen=lambda: None)
    d = S.KIDienst(assistent, fenster)
    d.ed, d.cursor = ed, QTextCursor
    return d


def _frage(d, markieren=True):
    c = d.ed.textCursor()
    c.setPosition(4) if not markieren else (c.setPosition(4), c.setPosition(7, d.cursor.KeepAnchor))
    d.ed.setTextCursor(c)
    k = d.chat_modell.anfrage("Frage", None, d.chat_bezug())
    d.chat_modell.antwort(k, "war")
    return len(d.chat_modell.nachrichten) - 1


def test_ersetzen_ist_ein_undo_schritt(dienst):
    d = dienst
    i = _frage(d)
    assert d.chat_modell.bezug_von(i)["alt"] == "ist"
    assert d.bezug_gueltig(i, True) == (True, "")
    assert d.antwort_vorschau(i, True)
    assert d.antwort_ersetzen(i)[0]
    assert d.ed.toPlainText() == "Das war ein Text."
    d.ed.undo()
    assert d.ed.toPlainText() == "Das ist ein Text."


def test_ablehnung_bei_aenderung_und_editorwechsel(dienst):
    d = dienst
    i = _frage(d)
    d.ed.textCursor().insertText("X")
    ok, grund = d.antwort_ersetzen(i)
    assert not ok and grund == CB.MELDUNG_GEAENDERT
    assert d.antwort_einfuegen(i) == (False, CB.MELDUNG_GEAENDERT)
    d.ed.undo()
    j = _frage(d)
    d.w.current_editor = lambda: None
    assert d.antwort_einfuegen(j) == (False, CB.MELDUNG_EDITOR)


def test_einfuegen_ohne_markierung_ja_ersetzen_nein(dienst):
    d = dienst
    i = _frage(d, markieren=False)
    ok, grund = d.antwort_ersetzen(i)
    assert not ok and grund == CB.MELDUNG_OHNE_MARKIERUNG
    assert d.antwort_einfuegen(i)[0]
    assert d.ed.toPlainText() == "Das warist ein Text."
    assert d.antwort_einfuegen(i)[0] is False          # zweites Einfügen: Revision hat gewechselt
    d.ed.undo()
    assert d.ed.toPlainText() == "Das ist ein Text."


def test_aktion_hinweis_hat_bezug_ersetzen_hat_keinen(dienst):
    d = dienst
    c = d.ed.textCursor()
    c.setPosition(4); c.setPosition(7, d.cursor.KeepAnchor)
    d.ed.setTextCursor(c)
    eing = d._eingabe()
    d.aktionErgebnis.emit("Hinweis", "war", None, d._aktion_bezug(eing))
    d.aktionErgebnis.emit("Ersetzt", "war", None, CB.bezug_angewendet())
    i_hinweis, i_ersetzt = len(d.chat_modell.nachrichten) - 3, len(d.chat_modell.nachrichten) - 1
    assert d.bezug_gueltig(i_hinweis, True) == (True, "")
    assert d.bezug_gueltig(i_ersetzt) == (False, CB.MELDUNG_ANGEWENDET)
    assert d.antwort_ersetzen(i_ersetzt) == (False, CB.MELDUNG_ANGEWENDET)
    assert d.antwort_ersetzen(i_hinweis)[0] and d.ed.toPlainText() == "Das war ein Text."


def test_vorschau_ohne_markierung_nur_bei_ueberarbeitung():
    ganz = "Sehr geehrte Damen und Herren,\n\nhiermit bewerbe ich mich um die Stelle.\n\nMit freundlichen Grüßen"
    b = _bezug(markiert=False, alt="", ganz=ganz)
    assert b["ganz"] == ganz and _bezug()["ganz"] == ""
    n = {"text": "x", "kern": ganz.replace("hiermit bewerbe ich mich", "ich bewerbe mich")}
    st = CB.vorschau_der_nachricht(n, b)
    assert st and "".join(t for a, t in st if a != "neu") == ganz
    assert CB.vorschau_der_nachricht({"text": "x", "kern": "Es geht um eine Bewerbung als Pfleger."}, b) is None
    assert CB.vorschau_der_nachricht({"text": CB.__dict__ and "=== TEXT ===\nKurz\n=== ENDE ===", "kern": "Kurz"}, b)


def test_antwort_lage_und_kennung(dienst):
    d = dienst
    i = _frage(d)                                       # mit Markierung "ist"
    lage = d.antwort_lage(i)
    assert lage["gueltig"] and lage["vorher"] == "ist" and lage["nachher"] == "war" and lage["stuecke"]
    assert lage["einfuegen"] == (True, "") and lage["ersetzen"] == (True, "")
    assert d.antwort_index(lage["nr"]) == i
    j = _frage(d, markieren=False)                      # ohne Markierung, keine Überarbeitung: kein Vorher
    assert d.antwort_lage(j)["vorher"] == "" and d.antwort_lage(j)["stuecke"] is None
    assert d.antwort_lage(j)["ersetzen"][1] == CB.MELDUNG_OHNE_MARKIERUNG
    for schlecht in (-1, 99, 0):                        # 0 = Nutzerfrage
        assert d.antwort_lage(schlecht)["gueltig"] is False
    d.chat_modell.neues_gespraech()
    assert d.antwort_index(lage["nr"]) is None and d.antwort_index(None) is None


def test_antwort_lage_ueberarbeitung_ohne_markierung(dienst):
    d = dienst
    c = d.ed.textCursor(); c.setPosition(0); d.ed.setTextCursor(c)
    k = d.chat_modell.anfrage("Frage", None, d.chat_bezug())
    d.chat_modell.antwort(k, "=== TEXT ===\nDas ist kein Text.\n=== ENDE ===")
    lage = d.antwort_lage(len(d.chat_modell.nachrichten) - 1)
    assert lage["vorher"] == "Das ist ein Text." and lage["nachher"] == "Das ist kein Text."


def test_ersetzen_einer_ueberarbeitung_behaelt_die_formatierung(dienst):
    from PySide6.QtGui import QFont, QTextCharFormat
    d = dienst
    c = d.ed.textCursor()
    c.setPosition(8); c.setPosition(11, d.cursor.KeepAnchor)                 # „ein“ fett
    fett = QTextCharFormat(); fett.setFontWeight(QFont.Bold); c.mergeCharFormat(fett)
    c.setPosition(0); c.setPosition(17, d.cursor.KeepAnchor); d.ed.setTextCursor(c)
    k = d.chat_modell.anfrage("Frage", None, d.chat_bezug())
    d.chat_modell.antwort(k, "Das war ein Text.")
    i = len(d.chat_modell.nachrichten) - 1
    assert CB.ersetz_schritte("Das ist ein Text.", "Das war ein Text.") == [(4, 7, "war")]
    assert CB.ersetz_schritte("ist", "Etwas ganz anderes") is None           # keine Überarbeitung: als Ganzes ersetzen
    assert d.antwort_ersetzen(i)[0] and d.ed.toPlainText() == "Das war ein Text."
    c = d.ed.textCursor(); c.setPosition(10)
    assert c.charFormat().fontWeight() == QFont.Bold                          # unveränderte Stelle behält ihr Format
    c.setPosition(6); assert c.charFormat().fontWeight() != QFont.Bold
    d.ed.undo()
    assert d.ed.toPlainText() == "Das ist ein Text."                         # ein Schritt für Rückgängig


def test_ersetzen_ohne_markierung_bei_ueberarbeitung_des_ganzen_dokuments(dienst):
    from PySide6.QtGui import QFont, QTextCharFormat
    d = dienst
    c = d.ed.textCursor()
    c.setPosition(8); c.setPosition(11, d.cursor.KeepAnchor)                 # „ein“ fett
    fett = QTextCharFormat(); fett.setFontWeight(QFont.Bold); c.mergeCharFormat(fett)
    c.setPosition(4); d.ed.setTextCursor(c)                                  # nichts markiert
    k = d.chat_modell.anfrage("Frage", None, d.chat_bezug())
    d.chat_modell.antwort(k, "Hier ist der Text:\n\nDas war ein Text.\n\nIch habe ein Wort geändert.")
    i = len(d.chat_modell.nachrichten) - 1
    assert d.bezug_gueltig(i, True) == (True, "")
    assert d.antwort_ersetzen(i)[0] and d.ed.toPlainText() == "Das war ein Text."
    c = d.ed.textCursor(); c.setPosition(10)
    assert c.charFormat().fontWeight() == QFont.Bold
    d.ed.undo()
    assert d.ed.toPlainText() == "Das ist ein Text."


def test_antwort_rezension_traegt_aenderungen_ein(dienst):
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor(); ed.setPlainText("Das ist ein Text."); ed.zusatz_binden({})
    dienst.ed = dienst.w.ed = ed
    c = ed.textCursor(); c.setPosition(0); c.setPosition(17, dienst.cursor.KeepAnchor); ed.setTextCursor(c)
    k = dienst.chat_modell.anfrage("Frage", None, dienst.chat_bezug())
    dienst.chat_modell.antwort(k, "Das war ein Text.")
    i = len(dienst.chat_modell.nachrichten) - 1
    assert dienst.antwort_lage(i)["rezension"] == (True, "")
    ok, meldung = dienst.antwort_rezension(i)
    assert ok and meldung == CB.MELDUNG_REZENSION
    assert [b["wert"] for b in ed.aenderungen()] == ["del", "ins"] and not ed.verfolgen
    ed.undo()
    assert ed.toPlainText() == "Das ist ein Text." and not ed.aenderungen()


def test_antwort_rezension_abgelehnt_ohne_ueberarbeitung_oder_verfolgung(dienst):
    d = dienst
    c = d.ed.textCursor(); c.setPosition(0); c.setPosition(17, d.cursor.KeepAnchor); d.ed.setTextCursor(c)
    k = d.chat_modell.anfrage("Frage", None, d.chat_bezug())
    d.chat_modell.antwort(k, "Das war ein Text.")
    i = len(d.chat_modell.nachrichten) - 1                         # Überarbeitung, aber Test-Editor ohne Verfolgung
    assert d.antwort_rezension(i) == (False, CB.MELDUNG_OHNE_VERFOLGUNG)
    k = d.chat_modell.anfrage("Frage", None, d.chat_bezug())
    d.chat_modell.antwort(k, "etwas ganz anderes")
    j = len(d.chat_modell.nachrichten) - 1
    assert d.antwort_rezension(j) == (False, CB.MELDUNG_KEINE_REZENSION)
    assert d.ed.toPlainText() == "Das ist ein Text."
