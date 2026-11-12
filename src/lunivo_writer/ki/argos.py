"""Lokale Offline-Übersetzung mit argostranslate. Der Text verlässt den Rechner nie.

Argos ist optional: ohne die Bibliothek startet das Programm normal, die Übersetzung meldet dann verständlich, was fehlt.
Immer im Hintergrund aufrufen (nie im UI-Thread); die Funktionen blockieren.
"""
from __future__ import annotations

import glob
import os
import re

CODES = {"Englisch": "en", "Deutsch": "de", "Türkisch": "tr", "Russisch": "ru", "Ukrainisch": "uk", "Polnisch": "pl",
         "Rumänisch": "ro", "Arabisch": "ar", "Französisch": "fr", "Spanisch": "es", "Italienisch": "it",
         "Griechisch": "el", "Niederländisch": "nl", "Portugiesisch": "pt"}

_STOPP = {
    "de": "der die das und ist nicht ich ein eine mit von zu den auf für dem sich auch es wir sie sind wird haben",
    "en": "the and is of to in that it was for on are with as be this have not you at by from",
    "fr": "le la les des et est une un du que pour pas dans qui sur au avec ce il nous vous sont",
    "es": "el la los las de que y en un una es por con para no se su al lo como más pero",
    "it": "il lo la gli le di che e un una è per con non si su da come più ma sono",
    "nl": "de het een en van ik te dat die in is niet op met voor zijn er maar om ook",
    "pt": "o a os as de que e do da em um uma é para com não se por mais como mas foi",
    "pl": "i w nie na to się z że do jest jak ale po co tak za od czy już przez",
    "tr": "ve bir bu için ile de da ne ben sen o çok daha gibi var değil mi ama olarak",
    "ro": "și de în la cu nu un o este pe că se din pentru care mai sau dar ce sunt",
}
_WOERTER = {k: set(v.split()) for k, v in _STOPP.items()}
_installiert = False


def code_fuer(sprache: str) -> str | None:
    s = (sprache or "").strip()
    if s in CODES:
        return CODES[s]
    return s.lower() if s.lower() in CODES.values() else None


def erkenne_sprache(text: str) -> str:
    """Einfache Erkennung (Schrift, dann Stoppwörter). Bei Unklarheit Deutsch."""
    text = text or ""
    zaehl = {"cyr": 0, "ar": 0, "el": 0}
    for ch in text:
        o = ord(ch)
        if 0x400 <= o <= 0x4FF:
            zaehl["cyr"] += 1
        elif 0x600 <= o <= 0x6FF:
            zaehl["ar"] += 1
        elif 0x370 <= o <= 0x3FF:
            zaehl["el"] += 1
    if max(zaehl.values()) > 0 and max(zaehl.values()) >= len(re.findall(r"[^\W\d_]", text)) / 2:
        if zaehl["ar"] == max(zaehl.values()):
            return "ar"
        if zaehl["el"] == max(zaehl.values()):
            return "el"
        return "uk" if re.search("[іїєґІЇЄҐ]", text) else "ru"
    woerter = re.findall(r"[^\W\d_]+", text.lower())
    beste, punkte = "de", 0
    for code, menge in _WOERTER.items():
        n = sum(1 for w in woerter if w in menge)
        if n > punkte:
            beste, punkte = code, n
    return beste


def _fehler(text: str) -> dict:
    return {"fehler": text}


def _bibliothek():
    """(package, translate) oder None, wenn argostranslate fehlt. Speicherort der Pakete vorher auf einen beschreibbaren Ordner legen."""
    try:
        from lunivo_writer.plattform import pfade
        os.environ.setdefault("ARGOS_PACKAGES_DIR", pfade.argos_pakete_dir())
        import argostranslate.package as package
        import argostranslate.translate as translate
    except Exception:       # fehlende Bibliothek oder fehlerhafte Installation: kein Absturz, nur Meldung
        return None
    try:
        import argostranslate.settings as einst
        from pathlib import Path
        from lunivo_writer.plattform import pfade
        einst.package_data_dir = Path(pfade.argos_pakete_dir())
    except Exception:
        pass
    return package, translate


def _mitgelieferte_installieren(package) -> None:
    """Beim ersten Bedarf einmalig alle .argosmodel-Dateien aus den Suchorten installieren (bereits Installierte überspringt Argos nicht,
    darum nur einmal je Programmlauf und nur, wenn noch kein Sprachpaket da ist)."""
    global _installiert
    if _installiert:
        return
    _installiert = True
    try:
        if package.get_installed_packages():
            return
    except Exception:
        pass
    from lunivo_writer.plattform import pfade
    for ordner in pfade.argos_dirs():
        for datei in sorted(glob.glob(os.path.join(ordner, "*.argosmodel"))):
            try:
                package.install_from_path(datei)
            except Exception:
                continue


def _suche(translate, von: str, nach: str):
    """Übersetzer von→nach, direkt oder über Englisch; sonst None."""
    sprachen = {s.code: s for s in translate.get_installed_languages()}
    if von not in sprachen or nach not in sprachen:
        return None

    def paar(a, b):
        return sprachen[a].get_translation(sprachen[b])
    direkt = paar(von, nach)
    if direkt is not None:
        return direkt.translate
    if "en" in sprachen and von != "en" and nach != "en":
        a, b = paar(von, "en"), paar("en", nach)
        if a is not None and b is not None:
            return lambda t: b.translate(a.translate(t))
    return None


def uebersetze(text: str, sprache: str, quelle: str | None = None) -> dict:
    """{"text": …, "methode": "Lokal"} oder {"fehler": …}. ``sprache`` ist der deutsche Name (oder ISO-Code) der Zielsprache."""
    nach = code_fuer(sprache)
    if nach is None:
        return _fehler(f"Die Sprache „{sprache}“ kann die lokale Übersetzung nicht.")
    bib = _bibliothek()
    if bib is None:
        return _fehler("Die lokale Übersetzung (Argos) ist auf diesem Rechner nicht eingerichtet: Das Programmteil „argostranslate“ fehlt.")
    package, translate = bib
    von = (code_fuer(quelle) if quelle else None) or erkenne_sprache(text)
    if von == nach:
        return {"text": text, "methode": "Lokal"}
    try:
        _mitgelieferte_installieren(package)
        werkzeug = _suche(translate, von, nach)
        if werkzeug is None:
            return _fehler(f"Für {von} → {nach} ist kein lokales Sprachpaket installiert. "
                           "Laden Sie die Sprache in den Schreibhilfe-Einstellungen unter „Offline-Sprachen“ herunter.")
        zeilen = [werkzeug(z) if z.strip() else z for z in text.split("\n")]
    except Exception as e:
        return _fehler(f"Die lokale Übersetzung ist fehlgeschlagen: {e}")
    return {"text": "\n".join(zeilen), "methode": "Lokal"}


# ---------------------------------------------------------------- optionale Sprachpakete
def _name(code: str) -> str:
    return next((n for n, c in CODES.items() if c == code), code)


def installierte_richtungen() -> list[dict]:
    """Bereits installierte Richtungen: [{"von", "nach", "name"}]. Leer, wenn Argos fehlt. Kein Netz."""
    bib = _bibliothek()
    if bib is None:
        return []
    package, _ = bib
    try:
        _mitgelieferte_installieren(package)
        pakete = package.get_installed_packages()
    except Exception:
        return []
    return [{"von": p.from_code, "nach": p.to_code, "name": f"{_name(p.from_code)} → {_name(p.to_code)}"} for p in pakete]


def verfuegbare_richtungen() -> dict:
    """Noch nicht installierte Richtungen aus dem Argos-Paketindex: {"richtungen": [{"von","nach","name","groesse_mb"}]} oder {"fehler"}.
    Holt den Index aus dem Netz — nur auf ausdrücklichen Aufruf, im Hintergrund."""
    bib = _bibliothek()
    if bib is None:
        return _fehler("Die lokale Übersetzung (Argos) ist auf diesem Rechner nicht eingerichtet: Das Programmteil „argostranslate“ fehlt.")
    package, _ = bib
    try:
        package.update_package_index()
        da = {(r["von"], r["nach"]) for r in installierte_richtungen()}
        liste = []
        for p in package.get_available_packages():
            if (p.from_code, p.to_code) in da:
                continue
            gr = getattr(p, "package_size", None)
            liste.append({"von": p.from_code, "nach": p.to_code, "name": f"{_name(p.from_code)} → {_name(p.to_code)}",
                          "groesse_mb": round(gr / 1e6) if isinstance(gr, (int, float)) and gr else None})
    except Exception as e:
        return _fehler(_netzfehler(e))
    return {"richtungen": liste}


def richtung_installieren(von: str, nach: str) -> dict:
    """Lädt das Paket von→nach herunter und installiert es. Nur auf ausdrücklichen Wunsch, im Hintergrund; nie automatisch.
    Der einzige Ort, an dem Argos das Netz nutzt (neben der Indexabfrage oben)."""
    bib = _bibliothek()
    if bib is None:
        return _fehler("Die lokale Übersetzung (Argos) ist auf diesem Rechner nicht eingerichtet: Das Programmteil „argostranslate“ fehlt.")
    package, _ = bib
    try:
        package.update_package_index()
        p = next((x for x in package.get_available_packages() if x.from_code == von and x.to_code == nach), None)
        if p is None:
            return _fehler(f"Für {_name(von)} → {_name(nach)} gibt es kein Sprachpaket im Argos-Verzeichnis.")
        package.install_from_path(p.download())
    except Exception as e:
        return _fehler(_netzfehler(e))
    return {"ok": True, "name": f"{_name(von)} → {_name(nach)}"}


def _netzfehler(e: Exception) -> str:
    import urllib.error
    if isinstance(e, (urllib.error.URLError, OSError, TimeoutError)) or type(e).__module__.startswith(("requests", "urllib3")):
        return f"Das Sprachpaket konnte nicht geladen werden — keine Verbindung zum Argos-Verzeichnis ({e}). Prüfen Sie die Internetverbindung."
    return f"Das Sprachpaket konnte nicht installiert werden: {e}"
