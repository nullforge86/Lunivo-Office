"""Zahlen in anderer Schreibweise (Einfügen ▸ Zahl): 1,2,3 · A,B,C · I,II,III · eingekreist · Zahlwort. Keine Oberfläche.

    zahl_text(14, "roemisch")      # "XIV"
"""
from __future__ import annotations

from lunivo_writer.editor.zusatz import roemisch

# Schlüssel → Beschriftung in der Liste „Zahlentyp“, in dieser Reihenfolge
TYPEN = [("arabisch", "1, 2, 3, …"), ("gross", "A, B, C, …"), ("klein", "a, b, c, …"), ("roemisch", "I, II, III, …"),
         ("roemisch_klein", "i, ii, iii, …"), ("kreis", "①, ②, ③, …"), ("null", "01, 02, 03, …"), ("wort", "eins, zwei, drei, …")]

_EINER = ["", "ein", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf", "dreizehn", "vierzehn",
          "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn"]
_ZEHNER = ["", "", "zwanzig", "dreißig", "vierzig", "fünfzig", "sechzig", "siebzig", "achtzig", "neunzig"]


def _buchstaben(n: int) -> str:
    """1 → A, 26 → Z, 27 → AA (wie Listen in Word)."""
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _unter_tausend(n: int) -> str:
    h, r = divmod(n, 100)
    s = (_EINER[h] + "hundert") if h else ""
    if r < 20:
        s += _EINER[r]
    else:
        z, e = divmod(r, 10)
        s += (_EINER[e] + "und" if e else "") + _ZEHNER[z]
    return s


def zahlwort(n: int) -> str:
    """Deutsches Zahlwort bis 999 999 („einundzwanzig“, „eintausend“)."""
    if n == 0:
        return "null"
    t, r = divmod(n, 1000)
    s = (_unter_tausend(t) + "tausend") if t else ""
    s += _unter_tausend(r)
    return s + "s" if s.endswith("ein") else s


def grenzen(typ: str) -> tuple[int, int]:
    """Kleinste und größte Zahl, die der Typ darstellen kann."""
    return {"roemisch": (1, 3999), "roemisch_klein": (1, 3999), "kreis": (1, 50), "wort": (0, 999_999),
            "gross": (1, 18_278), "klein": (1, 18_278)}.get(typ, (0, 10 ** 15))


def zahl_text(n: int, typ: str) -> str:
    """Die Zahl im gewählten Typ; liegt sie außerhalb der Grenzen, ``ValueError``."""
    von, bis = grenzen(typ)
    if not von <= n <= bis:
        raise ValueError(f"Für diesen Zahlentyp sind nur Zahlen von {von} bis {bis} möglich.")
    if typ == "gross":
        return _buchstaben(n)
    if typ == "klein":
        return _buchstaben(n).lower()
    if typ == "roemisch":
        return roemisch(n).upper()
    if typ == "roemisch_klein":
        return roemisch(n)
    if typ == "kreis":
        if n <= 20:
            return chr(0x2460 + n - 1)
        if n <= 35:
            return chr(0x3251 + n - 21)
        return chr(0x32B1 + n - 36)
    if typ == "null":
        return f"{n:02d}"
    if typ == "wort":
        return zahlwort(n)
    return str(n)
