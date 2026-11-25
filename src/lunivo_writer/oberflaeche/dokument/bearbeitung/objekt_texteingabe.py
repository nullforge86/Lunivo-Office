"""Schreiben direkt im gewählten Objekt (WordArt oder Textfeld): ein Qt-Eingabefeld (``QTextEdit``) über dem Objekt.

Das Feld ist nur ein Eingabeelement der Oberfläche: Der Text und seine Auszeichnungen (Läufe) kommen als Wörterbücher ins Objekt
(``frei_objekt.aendern``), gesetzt und gezeichnet wird er vom Kern. Das Feld führt keinen eigenen Dokumentzustand."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPen, QTextCursor

from lunivo_writer.editor.objekte.frei.frei_objekt import TEXT_ARTEN, ZEICHEN_SCHLUESSEL, _aendern_innen, laeufe_zusammen, ziel
from lunivo_writer.oberflaeche.bauteile.textfeld_fragmente import absatz_fragmente


def _fmt_unter(cf, k, v) -> None:
    cf.setFontUnderline(bool(v))                       # die Art der Linie steht im Objekt; das Eingabefeld zeigt nur „unterstrichen“


def _fmt_hoch_tief(cf, k, v) -> None:
    from PySide6.QtGui import QTextCharFormat
    cf.setVerticalAlignment(QTextCharFormat.AlignSuperScript if k == "hoch" and v else QTextCharFormat.AlignSubScript if k == "tief" and v
                            else QTextCharFormat.AlignNormal)


def _fmt_schrift(cf, k, v) -> None:
    if v:
        cf.setFontFamilies([v])


def _fmt_pt(cf, k, v) -> None:
    if v:
        cf.setFontPointSize(float(v))


# Schlüssel der Texttools -> Setzer auf dem Zeichenformat (cf, Schlüssel, Wert)
_FORMAT_SETZER = {
    "fett": lambda cf, k, v: cf.setFontWeight(QFont.Bold if v else QFont.Normal),
    "kursiv": lambda cf, k, v: cf.setFontItalic(bool(v)),
    "unter": _fmt_unter,
    "unterfarbe": lambda cf, k, v: cf.setUnderlineColor(QColor(v) if v else QColor()),
    "durch": lambda cf, k, v: cf.setFontStrikeOut(bool(v)),
    "hoch": _fmt_hoch_tief,
    "tief": _fmt_hoch_tief,
    "hervor": lambda cf, k, v: cf.setBackground(QColor(v) if v else QColor(0, 0, 0, 0)),
    "fuell": lambda cf, k, v: cf.setForeground(QColor(v) if v else QColor(0, 0, 0, 0)),
    "kontur": lambda cf, k, v: cf.setTextOutline(QPen(QColor(v), 1.0) if v else QPen(Qt.NoPen)),
    "schrift": _fmt_schrift,
    "pt": _fmt_pt,
}


def _format_aus_kw(kw: dict):
    """Zeichenformat für das Eingabefeld aus Schlüsseln der Texttools (nur die genannten)."""
    from PySide6.QtGui import QTextCharFormat
    cf = QTextCharFormat()
    for k, v in kw.items():
        setzer = _FORMAT_SETZER.get(k)
        if setzer:
            setzer(cf, k, v)
    return cf


def _lauf_schnitt(cf, setze) -> None:
    """Fett, kursiv, unterstrichen, durchgestrichen, hoch- und tiefgestellt."""
    from PySide6.QtGui import QTextCharFormat, QTextFormat
    if cf.hasProperty(QTextFormat.FontWeight):
        setze("fett", cf.fontWeight() >= QFont.DemiBold)
    if cf.hasProperty(QTextFormat.FontItalic):
        setze("kursiv", cf.fontItalic())
    if cf.hasProperty(QTextFormat.TextUnderlineStyle) or cf.hasProperty(QTextFormat.FontUnderline):
        setze("unter", cf.fontUnderline())
    if cf.hasProperty(QTextFormat.FontStrikeOut):
        setze("durch", cf.fontStrikeOut())
    if cf.hasProperty(QTextFormat.TextVerticalAlignment):
        va = cf.verticalAlignment()
        setze("hoch", va == QTextCharFormat.AlignSuperScript); setze("tief", va == QTextCharFormat.AlignSubScript)


def _lauf_farben(cf, setze) -> None:
    """Hervorhebung, Textfarbe (mit Deckkraft) und Kontur; leer = ausdrücklich keine."""
    from PySide6.QtGui import QTextFormat
    if cf.hasProperty(QTextFormat.BackgroundBrush):
        c = cf.background().color(); setze("hervor", c.name() if c.alpha() else "")
    if cf.hasProperty(QTextFormat.ForegroundBrush):
        c = cf.foreground().color(); setze("fuell", (c.name(QColor.HexArgb) if c.alpha() < 255 else c.name()) if c.alpha() else "")
    if cf.hasProperty(QTextFormat.TextOutline):
        pen = cf.textOutline(); setze("kontur", pen.color().name() if pen.style() != Qt.NoPen else "")


def _lauf_schrift(cf, setze) -> None:
    from PySide6.QtGui import QTextFormat
    if cf.hasProperty(QTextFormat.FontFamilies) and cf.fontFamilies():
        setze("schrift", cf.fontFamilies()[0])
    if cf.hasProperty(QTextFormat.FontPointSize):
        setze("pt", cf.fontPointSize())


def _lauf_aus_format(cf, basis: dict) -> dict:
    """Die Zeichenschlüssel, die ein Format ausdrücklich setzt und die vom Objekt abweichen."""
    lauf: dict = {}

    def setze(k, wert):
        if wert != basis.get(k):
            lauf[k] = wert
    _lauf_schnitt(cf, setze); _lauf_farben(cf, setze); _lauf_schrift(cf, setze)
    return {k: v for k, v in lauf.items() if not (v in (False, "", None) and basis.get(k) in (None, False, ""))}


def _basis(d: dict, art: str) -> dict:
    return {k: d.get(k, True if (k == "fett" and art == "wordart") else None) for k in ZEICHEN_SCHLUESSEL}


def _widget_laeufe(w, d: dict, art: str) -> list[dict] | None:
    """Die Läufe aus dem Eingabefeld; ``None``, wenn der ganze Text ohne eigene Formate ist."""
    basis = _basis(d, art)
    laeufe: list[dict] = []
    blk = w.document().firstBlock(); erste = True
    while blk.isValid():
        if not erste:
            laeufe.append({"t": "\n"})
        erste = False
        for fr in absatz_fragmente(blk):
            if fr.text():
                laeufe.append({"t": fr.text(), **_lauf_aus_format(fr.charFormat(), basis)})
        blk = blk.next()
    laeufe = laeufe_zusammen(laeufe)
    if all(len(r) == 1 for r in laeufe):
        return None
    return laeufe


def _edit_laden(ed) -> None:
    """Das Eingabefeld mit den Läufen des Objekts füllen (Auswahl bleibt erhalten)."""
    w = getattr(ed, "_frei_edit", None)
    z = ziel(ed)
    if w is None or z is None:
        return
    art, d, _k, _a, _b = z
    c0 = w.textCursor(); pos, anker = c0.position(), c0.anchor()
    w.blockSignals(True)
    w.clear()
    c = w.textCursor()
    from PySide6.QtGui import QTextCharFormat
    for r in (d.get("laeufe") or [{"t": d.get("text", "")}]):
        c.insertText(r["t"], _format_aus_kw({k: v for k, v in r.items() if k in ZEICHEN_SCHLUESSEL}))
    w.blockSignals(False)
    c = w.textCursor(); n = len(w.toPlainText())
    c.setPosition(min(anker, n)); c.setPosition(min(pos, n), QTextCursor.KeepAnchor); w.setTextCursor(c)


def _edit_stil(ed) -> None:
    """Schrift, Farbe und Ausrichtung des Eingabefeldes folgen den Parametern des Objekts (auch nach einem Knopf der Texttools)."""
    w = getattr(ed, "_frei_edit", None)
    z = ziel(ed)
    if w is None or z is None:
        return
    art, d, _key, a, _bild = z
    z_ = ed.zoom
    f = QFont(d.get("schrift", "Liberation Sans")); f.setPixelSize(max(6, round(float(d.get("pt", 36 if art == "wordart" else 11)) * 96 / 72 * z_)))
    f.setBold(bool(d.get("fett", art == "wordart"))); f.setItalic(bool(d.get("kursiv"))); f.setUnderline(bool(d.get("unter"))); f.setStrikeOut(bool(d.get("durch")))
    w.setFont(f); w.document().setDefaultFont(f)
    farbe = d.get("fuell") or d.get("farbe") or ("#2f78bd" if art == "wordart" else "#1f1f1f")
    grund = "transparent"
    fu = a.get("fuell")
    if art == "textfeld" and fu and fu.get("art") == "farbe":
        grund = fu["farbe"]
    w.setStyleSheet(f"QTextEdit {{ background: {grund}; color: {farbe}; border: none; selection-background-color: #8a9ab0; }}")


def edit_platzieren(ed) -> None:
    """Das Eingabefeld deckt das Objekt (folgt dem Blatt beim Scrollen und Zoomen)."""
    w = getattr(ed, "_frei_edit", None)
    if w is None:
        return
    a = ed.ansicht
    treffer = a.ergebnis().objekte.get(ed._frei_edit_key)
    if treffer is None:
        return
    seite, r = treffer
    blatt, z = a.blatt(seite), a.zoom
    rand = int((8 if ed._frei_edit_art == "textfeld" else 20) * z)
    w.setGeometry(QRectF(blatt.left() + r.x * z, blatt.top() + r.y * z, r.width * z, r.height * z).toRect().adjusted(rand, rand, -rand, -rand))


def bearbeiten_starten(ed) -> bool:
    """Schreibt direkt im gewählten Objekt (WordArt oder Textfeld): ein Eingabefeld über dem Text. Eingabe, Markieren, Rückschritt und Enter
    (neue Zeile) wirken wie im Text; Esc oder ein Klick außerhalb beendet und übernimmt. Die Knöpfe der Texttools wirken auf die Markierung,
    ohne Markierung auf das ganze Objekt (``aendern``)."""
    from PySide6.QtWidgets import QTextEdit
    z = ziel(ed)
    if z is None or z[0] not in TEXT_ARTEN:
        return False
    bearbeiten_beenden(ed)
    art, d, key, _a, _b = z
    if d.get("von"):                                                 # Folgefeld einer Verknüpfung: der Text gehört dem ersten Feld
        return False

    class Feld(QTextEdit):
        def keyPressEvent(self, e):
            if e.key() == Qt.Key_Escape:
                bearbeiten_beenden(ed); return
            super().keyPressEvent(e)

        def focusOutEvent(self, e):
            super().focusOutEvent(e)
            if getattr(ed, "_frei_edit", None) is self and e.reason() not in (Qt.PopupFocusReason, Qt.ActiveWindowFocusReason):
                bearbeiten_beenden(ed)

        def insertFromMimeData(self, quelle):                        # Einfügen: nur Text
            self.insertPlainText(quelle.text())

    w = Feld(ed.viewport())
    w.setFrameShape(Feld.NoFrame); w.setAcceptRichText(False)
    w.setLineWrapMode(Feld.WidgetWidth if art == "textfeld" else Feld.NoWrap)
    w.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff); w.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    ed._frei_edit, ed._frei_edit_key, ed._frei_edit_art = w, key, art
    _edit_laden(ed)
    ed._frei_edit_text, ed._frei_edit_laeufe = w.toPlainText(), _widget_laeufe(w, d, art)
    _edit_stil(ed)
    ed._frei_liste(); edit_platzieren(ed)
    w.show(); w.setFocus()
    c = w.textCursor(); c.select(QTextCursor.Document) if art == "wordart" else c.movePosition(QTextCursor.End); w.setTextCursor(c)
    ed.viewport().update()
    return True


def auswahl_daten(ed) -> dict | None:
    """Die Zeichenformate der Markierung (oder der Schreibmarke) im Eingabefeld — wirksame Werte, auch die des Objekts. Für den Zustand der
    Knöpfe der Texttools; ``None``, wenn nicht im Objekt geschrieben wird."""
    w = getattr(ed, "_frei_edit", None)
    z = ziel(ed)
    if w is None or z is None:
        return None
    art, d, _k, _a, _b = z
    basis = _basis(d, art)
    c = w.textCursor()
    if c.hasSelection():
        c = QTextCursor(w.document()); c.setPosition(w.textCursor().selectionStart() + 1)
    return {**basis, **_lauf_aus_format(c.charFormat(), basis)}


def edit_uebernehmen(ed) -> None:
    """Der eingegebene Text mit seinen Formaten kommt ins Objekt (ohne das Feld zu schließen)."""
    w = getattr(ed, "_frei_edit", None)
    z = ziel(ed)
    if w is None or z is None:
        return
    art, d, _k, _a, _b = z
    text, laeufe = w.toPlainText(), _widget_laeufe(w, d, art)
    if text != ed._frei_edit_text or laeufe != ed._frei_edit_laeufe:
        ed._frei_edit_text, ed._frei_edit_laeufe = text, laeufe
        kw = {"text": text if art == "textfeld" else (text or " "), "laeufe": laeufe}
        _aendern_innen(ed, art, **kw)


def bearbeiten_beenden(ed) -> None:
    w = getattr(ed, "_frei_edit", None)
    if w is None:
        return
    edit_uebernehmen(ed)
    ed._frei_edit = None
    w.hide(); w.deleteLater()
    ed.viewport().update(); ed.setFocus()
