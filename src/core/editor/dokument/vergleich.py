"""Dokumente vergleichen und zusammenführen — das Ergebnis sind verfolgte Änderungen (einfügen/löschen, mit Autor und Datum). Ohne Qt.

Vergleichen: Das Ausgangsdokument bleibt als Text und Formatierung erhalten; was das andere Dokument anders hat, steht als verfolgte
Änderung darin. Es wird nach Absätzen ausgerichtet und in ähnlichen Absätzen wortweise verglichen.
Zusammenführen: mehrere überarbeitete Fassungen desselben Ausgangsdokuments mit je eigenem Autor in einem Dokument; überschneiden sich
zwei Löschungen/Ersetzungen verschiedener Autoren, gilt die erste, die andere wird als Konflikt gemeldet.

Grenzen: Es werden Text und Absätze verglichen, keine Formatänderungen und keine Tabellenstruktur (Zellentext wie Absätze); ein
zusammengeführter Absatz erscheint als gelöscht + neu. Bereits verfolgte Änderungen im Ausgangsdokument bleiben unberührt."""
from __future__ import annotations

import copy
import difflib
import re

from core.dokument.dokument import Auswahl, Dokument, Lauf, Position
from core.bearbeitung import Bearbeitungssitzung

TOKEN = re.compile(r"\s+|\w+|[^\w\s]", re.UNICODE)
AEHNLICH = 0.4


def ops_bestimmen(basis: Dokument, andere: Dokument, autor: str) -> list[dict]:
    """Änderungen von ``basis`` nach ``andere`` als Operationen auf den Absätzen von ``basis`` (Nummer des Absatzes in Dokumentreihenfolge)."""
    ta, tb = [a.text() for a in basis.absaetze()], [a.text() for a in andere.absaetze()]
    ops: list[dict] = []

    def loeschen(i):
        if ta[i]:
            ops.append({"art": "del", "absatz": i, "von": 0, "bis": len(ta[i]), "autor": autor})
        else:
            ops.append({"art": "delleer", "absatz": i, "von": 0, "bis": 0, "autor": autor})

    def einfuegen_vor(i, j):
        ops.append({"art": "insblock", "absatz": i, "von": -1, "bis": -1, "autor": autor, "text": tb[j]})

    def wortweise(i, j):
        wa, wb = TOKEN.findall(ta[i]), TOKEN.findall(tb[j])
        pos = [0]
        for w in wa:
            pos.append(pos[-1] + len(w))
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, wa, wb, autojunk=False).get_opcodes():
            if tag == "equal":
                continue
            g = (autor, i, i1) if tag == "replace" else None              # eine Ersetzung gilt ganz oder gar nicht
            if tag in ("delete", "replace"):
                ops.append({"art": "del", "absatz": i, "von": pos[i1], "bis": pos[i2], "autor": autor, "gruppe": g})
            if tag in ("insert", "replace"):
                ops.append({"art": "ins", "absatz": i, "von": pos[i2], "bis": pos[i2], "text": "".join(wb[j1:j2]), "autor": autor, "gruppe": g})

    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        if tag == "delete":
            for i in range(i1, i2):
                loeschen(i)
        elif tag == "insert":
            for j in range(j1, j2):
                einfuegen_vor(i1, j)
        else:                                                            # replace: Absätze paarweise wortweise, Reste ganz
            n = min(i2 - i1, j2 - j1)
            for k in range(n):
                i, j = i1 + k, j1 + k
                if difflib.SequenceMatcher(None, ta[i], tb[j], autojunk=False).ratio() >= AEHNLICH:
                    wortweise(i, j)
                else:
                    loeschen(i)
                    einfuegen_vor(i + 1, j)
            for i in range(i1 + n, i2):
                loeschen(i)
            for j in range(j1 + n, j2):
                einfuegen_vor(i2, j)
    return ops


def _bereich(op: dict) -> tuple[int, int]:
    return (0, 10 ** 9) if op["art"] in ("delleer",) else (op["von"], op["bis"])


def zusammenlegen(listen: list[list[dict]]) -> tuple[list[dict], list[str]]:
    """Operationen mehrerer Autoren vereinen; überschneidende Löschungen verschiedener Autoren → die erste gilt, die andere ist Konflikt."""
    ops: list[dict] = []
    konflikte: list[str] = []
    verworfen: set = set()
    for liste in listen:
        for op in liste:
            if op.get("gruppe") is not None and op["gruppe"] in verworfen:
                continue
            if op["art"] in ("del", "delleer"):
                v, b = _bereich(op)
                clash = next((o for o in ops if o["art"] in ("del", "delleer") and o["absatz"] == op["absatz"] and o["autor"] != op["autor"]
                              and v < max(_bereich(o)[1], _bereich(o)[0] + 1) and _bereich(o)[0] < max(b, v + 1)), None)
                if clash:
                    konflikte.append(f"Absatz {op['absatz'] + 1}: Änderung von {op['autor']} überschneidet sich mit der von {clash['autor']} — es gilt {clash['autor']}.")
                    if op.get("gruppe") is not None:
                        verworfen.add(op["gruppe"])
                    continue
            ops.append(op)
    return ops, konflikte


def _jetzt() -> str:
    from core.editor.dokument.vergleich_datum_kern import _jetzt as kernfunktion
    return kernfunktion()


def _freie_strecken(a, von: int, bis: int) -> list[tuple[int, int]]:
    """Die Strecken von ``von`` bis ``bis`` im Absatz ohne Änderungsmarke (bereits verfolgte Zeichen bleiben, wie sie sind)."""
    aus, versatz = [], 0
    for x in a.inhalte:
        n = len(x.text) if isinstance(x, Lauf) else 1
        v, b = max(von, versatz), min(bis, versatz + n)
        if v < b and "aenderung" not in x.format:
            if aus and aus[-1][1] == v:
                aus[-1] = (aus[-1][0], b)
            else:
                aus.append((v, b))
        versatz += n
    return aus


def anwenden(s: Bearbeitungssitzung, ops: list[dict], datum: str | None = None) -> dict:
    """Operationen als verfolgte Änderungen in die Sitzung schreiben (von hinten nach vorn, damit die Stellen stimmen)."""
    s.nachverfolgen = True
    s.datum = datum or _jetzt()
    stat = {"eingefuegt": 0, "geloescht": 0}
    ids = [a.id for a in s.dokument.absaetze()]

    def schluessel(op):
        return (op["absatz"], op["von"], 1 if op["art"] in ("ins", "insblock") else 0)

    for op in sorted(ops, key=schluessel, reverse=True):
        s.autor = op["autor"]
        art = op["art"]
        if art == "del" and op["absatz"] < len(ids):
            a = s._absatz(ids[op["absatz"]])
            for v, b in reversed(_freie_strecken(a, op["von"], op["bis"])):
                s.loeschen(Auswahl(Position(a.id, v), Position(a.id, b)))
                stat["geloescht"] += b - v
        elif art == "ins" and op["absatz"] < len(ids):
            s.text_einfuegen(op["text"], Position(ids[op["absatz"]], op["von"]))
            stat["eingefuegt"] += len(op["text"])
        elif art == "insblock":
            if op["absatz"] < len(ids):
                s.text_einfuegen(op["text"] + "\n", Position(ids[op["absatz"]], 0))
            else:                                                        # hinter dem letzten Absatz
                letzter = s._absatz(ids[-1])
                s.text_einfuegen("\n" + op["text"], Position(letzter.id, letzter.laenge))
            stat["eingefuegt"] += len(op["text"])
    s.nachverfolgen = False
    return stat


def vergleichen(basis: Dokument, andere: Dokument, autor: str = "Vergleich") -> tuple[Dokument, dict]:
    ziel = copy.deepcopy(basis)
    s = Bearbeitungssitzung(ziel)
    ops = ops_bestimmen(ziel, andere, autor)
    stat = anwenden(s, ops)
    stat["operationen"] = len(ops)
    return ziel, stat


def zusammenfuehren(basis: Dokument, fassungen: list[tuple[str, Dokument]]) -> tuple[Dokument, dict, list[str]]:
    ziel = copy.deepcopy(basis)
    s = Bearbeitungssitzung(ziel)
    listen = [ops_bestimmen(ziel, doc, autor) for autor, doc in fassungen]
    ops, konflikte = zusammenlegen(listen)
    stat = anwenden(s, ops)
    stat["operationen"] = len(ops)
    return ziel, stat, konflikte
