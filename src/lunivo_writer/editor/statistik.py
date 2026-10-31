"""Wörter zählen wie das Fenster der Vorlage: Seiten, Wörter, Zeichen mit und ohne Leerzeichen, Absätze, nicht-asiatische Wörter,
asiatische Zeichen. Keine Oberfläche.

    zaehlen(texte, seiten, absaetze)  → dict mit den Werten
    texte_des_dokuments(doc)          → [Text je Absatz] (leere Absätze zählen nicht als Absatz)
"""
from __future__ import annotations

import re

# Asiatische Schriftzeichen (CJK, Kana, Hangul): jedes zählt für sich, wie in Word und WPS
ASIATISCH = re.compile(r"[⺀-⿿　-〿぀-ヿ㄀-ㇿ㐀-䶿一-鿿가-힯豈-﫿＀-￯]")


def texte_des_dokuments(doc) -> list[str]:
    out = []
    b = doc.firstBlock()
    while b.isValid():
        if b.isVisible():
            out.append(b.text().replace("￼", ""))      # Objektzeichen (Bilder) zählen nicht
        b = b.next()
    return out


def zaehlen(texte: list[str], seiten: int = 1) -> dict:
    """``texte``: ein Eintrag je Absatz (auch Noten und Textfelder, wenn sie mitzählen sollen)."""
    ganz = "\n".join(texte)
    asiatisch = len(ASIATISCH.findall(ganz))
    ohne_asien = ASIATISCH.sub(" ", ganz)
    nicht_asiatisch = len(ohne_asien.split())
    mit = sum(len(t) for t in texte)
    ohne = sum(len("".join(t.split())) for t in texte)
    return {"seiten": seiten, "woerter": nicht_asiatisch + asiatisch, "zeichen_ohne": ohne, "zeichen_mit": mit,
            "absaetze": sum(1 for t in texte if t.strip()), "nicht_asiatisch": nicht_asiatisch, "asiatisch": asiatisch}
