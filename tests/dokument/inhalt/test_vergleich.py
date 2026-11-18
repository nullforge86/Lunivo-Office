"""Dokumente vergleichen und zusammenführen: Das Ergebnis sind verfolgte Änderungen im Dokumentenmodell (Schlüssel ``aenderung``, ``autor`` am Zeichenformat)."""
from lunivo_writer.core.document.dokument import Lauf
from lunivo_writer.editor.dokument import vergleich as V
from tests.hilfen_dokument import dokument


def _spuren(d):
    """[(art, autor, text)] zusammenhängender verfolgter Stücke in Dokumentreihenfolge."""
    return [(x.format["aenderung"], x.format.get("autor", ""), x.text) for a in d.absaetze() for x in a.inhalte if isinstance(x, Lauf) and x.format.get("aenderung")]


def _angenommen(d):
    """Der Text, wenn alle Änderungen angenommen werden (Gelöschtes fällt weg)."""
    return "\n".join("".join(x.text for x in a.inhalte if isinstance(x, Lauf) and x.format.get("aenderung") != "del") for a in d.absaetze())


def test_vergleich_markiert_einfuegung_und_loeschung():
    basis, andere = dokument("Das ist ein alter Text"), dokument("Das ist ein neuer schöner Text")
    ergebnis, _info = V.vergleichen(basis, andere, "Ann")
    arten = {a for a, _autor, _t in _spuren(ergebnis)}
    assert arten == {"ins", "del"} and all(autor == "Ann" for _a, autor, _t in _spuren(ergebnis))
    assert _angenommen(ergebnis) == "Das ist ein neuer schöner Text"
    assert next(iter(basis.absaetze())).text() == "Das ist ein alter Text"           # das Ausgangsdokument bleibt unberührt


def test_gleiche_dokumente_ergeben_keine_aenderung():
    ergebnis, _info = V.vergleichen(dokument("Gleich\nZwei"), dokument("Gleich\nZwei"), "Ann")
    assert _spuren(ergebnis) == []


def test_zusammenfuehren_mehrerer_fassungen():
    basis = dokument("Erster Absatz\nZweiter Absatz")
    ann, bob = dokument("Erster geänderter Absatz\nZweiter Absatz"), dokument("Erster Absatz\nZweiter bearbeiteter Absatz")
    ergebnis, _info, konflikte = V.zusammenfuehren(basis, [("Ann", ann), ("Bob", bob)])
    assert not konflikte
    autoren = {autor for _a, autor, _t in _spuren(ergebnis)}
    assert autoren == {"Ann", "Bob"}
