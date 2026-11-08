from lunivo_writer.ai.ki_anfragen import KIAnfragenMixin


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
