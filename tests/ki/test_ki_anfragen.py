from lunivo_writer.ki.ki_anfragen import KIAnfragenMixin
from lunivo_writer.ki.ki_aktionen import KIAktionenMixin


class _Signal:
    def __init__(self):
        self.werte = []

    def emit(self, *werte):
        self.werte.append(werte)


class _Dokument:
    def revision(self):
        return 4


class _Editor:
    def __init__(self, dokument):
        self._dokument = dokument

    def document(self):
        return self._dokument

    def replace_range(self, *args, **kwargs):
        self.ersatz = (args, kwargs)
        return True


class _Dienst(KIAnfragenMixin):
    def __init__(self):
        self._arbeit_laeuft = True
        self.laeuft = _Signal()
        self.status = _Signal()
        self.ergebnisse = []

    def merke_ergebnis(self, *args):
        self.ergebnisse.append(args)


def test_ki_antwort_fuer_anders_dokument_wird_verworfen():
    erstes = _Dokument()
    zweites = _Dokument()
    assert erstes.revision() == zweites.revision()

    dienst = _Dienst()
    angewendet = []
    eingabe = {
        "ed": _Editor(zweites),
        "dokument": erstes,
        "rev": erstes.revision(),
        "text": "Ursprünglicher Text",
    }

    dienst._fertig((lambda r, e: angewendet.append((r, e)), eingabe), {"text": "KI-Antwort"})

    assert angewendet == []
    assert dienst.ergebnisse == []
    assert dienst.status.werte
    assert dienst.laeuft.werte == [(False,)]



def test_bildantwort_fuer_gewechseltes_dokument_wird_verworfen():
    erstes = _Dokument()
    zweites = _Dokument()
    dienst = _Dienst()
    eingefuegt = []
    dienst._bild_fertig = lambda r, e: eingefuegt.append((r, e))
    eingabe = {
        "ed": _Editor(zweites),
        "dokument": erstes,
        "rev": erstes.revision(),
        "cursor": (0, 0),
    }

    dienst._fertig(("bild", eingabe), {"bild": b"bilddaten"})

    assert eingefuegt == []
    assert dienst.status.werte == [
        ("Das Dokument wurde gewechselt oder geändert, während das Bild erzeugt wurde. Das Bild wurde verworfen.",)
    ]
    assert dienst.laeuft.werte == [(False,)]



class _Fenster:
    def __init__(self, editor):
        self._editor = editor

    def current_editor(self):
        return self._editor


class _DienstMitAktionen(_Dienst, KIAktionenMixin):
    pass


def test_ki_vorschlag_nach_dokumentwechsel_nicht_einsetzen():
    erstes = _Dokument()
    zweites = _Dokument()
    editor = _Editor(zweites)
    dienst = _DienstMitAktionen()
    dienst.w = _Fenster(editor)

    vorschlag = {
        "alt": "Ursprünglicher Satz",
        "neu": "Verbesserter Satz",
        "_ed": editor,
        "_dokument": erstes,
        "_rev": erstes.revision(),
    }

    assert dienst.vorschlag_aktuell(vorschlag) is False
    assert dienst.vorschlag_einsetzen(vorschlag) is False
    assert not hasattr(editor, "ersatz")
    assert dienst.status.werte == [
        ("Das Dokument wurde gewechselt oder geändert — der KI-Vorschlag ist veraltet.",)
    ]
