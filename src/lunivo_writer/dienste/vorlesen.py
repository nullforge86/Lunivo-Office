"""Vorlesen: Piper (offline, gute Stimme) wenn eingerichtet, sonst der Sprachdienst des Systems (``plattform/sprachausgabe.py``).

Es wird nichts heruntergeladen — Piper kommt über ./skripte/stimme-holen.sh, auf ausdrücklichen Wunsch.
"""
from __future__ import annotations

import os
import subprocess
import threading

from lunivo_writer.plattform.pfade import pfade
from lunivo_writer.plattform.prozess import prozess
from lunivo_writer.plattform.sprachausgabe import sprachausgabe

PIPER_NAMEN = {
    "de_DE-thorsten-medium": "Thorsten (männlich)", "de_DE-thorsten-high": "Thorsten, feiner (männlich)",
    "de_DE-thorsten-low": "Thorsten, gröber (männlich)", "de_DE-karlsson-low": "Karlsson (männlich)",
    "de_DE-pavoque-low": "Pavoque (männlich)", "de_DE-kerstin-low": "Kerstin (weiblich)",
    "de_DE-ramona-low": "Ramona (weiblich)", "de_DE-eva_k-x_low": "Eva (weiblich)",
    "de_DE-mls-medium": "Gemischt (mehrere Sprecher)",
    "de_DE-thorsten_emotional-medium": "Thorsten mit Gefühl (männlich)",
}
MAX_ZEICHEN = 20000
_lauf: dict = {"ton": None, "rechner": None}


class VorlesenFehler(Exception):
    pass


def piper_programm():
    for ort in pfade.piper_dirs():
        p = os.path.join(ort, "piper", sprachausgabe.programmname("piper"))
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p, ort
    return None, None


def piper_stimmen() -> list[dict]:
    programm, ort = piper_programm()
    if not programm:
        return []
    stufe = {"high": 0, "medium": 1, "low": 2, "x_low": 3}
    out = []
    for d in sorted(os.listdir(ort)):
        if d.endswith(".onnx"):
            k = d[:-5]
            out.append((stufe.get(k.rsplit("-", 1)[-1], 9), k, PIPER_NAMEN.get(k, k.replace("de_DE-", ""))))
    out.sort(key=lambda e: (e[0], e[2]))
    return [{"kennung": k, "name": n} for _r, k, n in out]


def _abspieler():
    return sprachausgabe.abspieler()


def piper_da() -> bool:
    return bool(piper_programm()[0] and piper_stimmen() and _abspieler())


def spd_da() -> bool:
    return sprachausgabe.system_da()


def verfuegbar() -> bool:
    return piper_da() or spd_da()


EINSTELLUNG_STIMME = "vorlesen/stimme"      # Schlüssel in den Einstellungen (eine Quelle für Fenster und Vorlesen)
EINSTELLUNG_TEMPO = "vorlesen/tempo"
TEMPO_MIN, TEMPO_MAX, TEMPO_SCHRITT = -100, 100, 10      # Tempo in Prozent: 0 = normal, negativ langsamer, positiv schneller


def tempo_begrenzen(tempo: int) -> int:
    return max(TEMPO_MIN, min(TEMPO_MAX, int(tempo or 0)))


def tempo_piper(tempo: int) -> float:
    t = tempo_begrenzen(tempo)
    return 1.0 - t * ((0.4 if t > 0 else 0.5) / TEMPO_MAX)


def stimmen() -> list[dict]:
    """Alle wählbaren Stimmen: zuerst Piper, dann die deutschen des Sprachdienstes."""
    liste = [{"kennung": "piper:" + s["kennung"], "name": s["name"]} for s in piper_stimmen()]
    liste += sprachausgabe.system_stimmen()
    return liste[:60]


def beenden() -> None:
    for k in ("ton", "rechner"):
        p = _lauf.get(k)
        _lauf[k] = None
        if p and p.poll() is None:
            try:
                p.terminate()
                p.wait(timeout=2)
            except (OSError, subprocess.SubprocessError):
                pass
    sprachausgabe.system_stoppen()


def vorlesetext(dok, von: int = 0, bis: int | None = None) -> str:
    """Der Text des Dokuments (``Dokument``) von ``von`` bis ``bis`` (Stellen im Rohtext) zum Vorlesen. Bilder mit Beschreibung werden angesagt
    („Bild: …“), dekorative Bilder und Bilder ohne Beschreibung übersprungen. Frei positionierte Bilder stehen vor dem Absatz, an dem sie verankert sind."""
    from lunivo_writer.core.document.dokument import InlineObjekt

    def ansage(o) -> str:
        alt = str(o.alt_text or "").strip()
        return f"Bild: {alt}. " if alt and not o.daten.get("dekor") else ""

    frei: dict[int, list] = {}
    for o in dok.objekte.values():
        frei.setdefault(o.anker, []).append(o)
    ende = sum(a.laenge + 1 for a in dok.absaetze()) if bis is None else bis
    zeilen: list[str] = []
    n = 0
    for a in dok.absaetze():
        anfang = n
        n += a.laenge + 1
        if n <= von or anfang >= ende:
            continue
        zeile = "".join(ansage(o) for o in frei.get(a.id, ())) if anfang >= von else ""
        versatz = 0
        for x in a.inhalte:
            laenge = len(x.text) if hasattr(x, "text") else 1
            if anfang + versatz + laenge > von and anfang + versatz < ende:
                if isinstance(x, InlineObjekt):
                    zeile += ansage(x)
                else:
                    zeile += x.text[max(0, von - anfang - versatz):max(0, ende - anfang - versatz)]
            versatz += laenge
        zeilen.append(zeile.strip())
    return "\n".join(zeilen)


def lies_vor(text: str, stimme: str = "", tempo: int = 0) -> bool:
    beenden()
    text = text.strip()[:MAX_ZEICHEN]
    if not text:
        return False
    if not verfuegbar():
        raise VorlesenFehler(sprachausgabe.hinweis_fehlt())
    if stimme.startswith("piper:") or (piper_da() and not stimme):
        programm, ort = piper_programm()
        kennung = stimme[6:] if stimme.startswith("piper:") else piper_stimmen()[0]["kennung"]
        modell = os.path.join(ort, kennung + ".onnx")
        if not os.path.isfile(modell):
            modell = os.path.join(ort, piper_stimmen()[0]["kennung"] + ".onnx")
        sprechen = prozess.starten([programm, "--model", modell, "--output_raw", "--length_scale",
                                     "%.2f" % tempo_piper(tempo)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL, env=dict(os.environ))
        ton = prozess.starten(_abspieler(), stdin=sprechen.stdout, stderr=subprocess.DEVNULL, env=dict(os.environ))
        sprechen.stdout.close()

        def fuettern():
            try:
                sprechen.stdin.write(text.encode("utf-8"))
                sprechen.stdin.close()
            except (OSError, ValueError):
                pass
        threading.Thread(target=fuettern, daemon=True).start()
        _lauf["ton"], _lauf["rechner"] = ton, sprechen
        return True
    _lauf["ton"] = sprachausgabe.system_sprechen(text, stimme, tempo_begrenzen(tempo))
    return True
