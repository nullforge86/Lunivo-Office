"""Stilformat: fachlich abgegrenzte Editor-Funktionen."""
from __future__ import annotations

from __future__ import annotations  # noqa: F401
from PySide6.QtCore import QTimer, Qt, QUrl  # noqa: F401
from PySide6.QtGui import QBrush, QColor, QFont, QImage, QPen, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument, QTextFormat, QTextFrameFormat, QTextImageFormat, QTextListFormat, QTextTableFormat, QTextLength  # noqa: F401
from lunivo_writer.services.docx_reader import LH_PROPORTIONAL, STYLE_PROP  # noqa: F401
from lunivo_writer.editor.zusatz import P_VERSTECKT  # noqa: F401
from lunivo_writer.models.page import mm_to_px, px_to_mm  # noqa: F401
from lunivo_writer.editor import stile  # noqa: F401
from lunivo_writer.editor.zusatz import abstand_davor_px  # noqa: F401
from lunivo_writer.core.farben import Farbe  # noqa: F401


class StilformatMixin:
    """Teilbereich der Formatierungs- und Bearbeitungsfunktionen."""

    def apply_style(self, name: str) -> None:
        kf = self._kf()
        if kf is not None:                                      # Formatvorlagen gehören zu Absätzen des Dokuments, nicht zur Kopf-/Fußzeile
            kf._hinweis("Formatvorlagen gelten nur im Dokumenttext.")
            return
        """Formatvorlage auf alle Absätze der Markierung (oder den Absatz am Zeiger) anwenden."""
        cur = self.textCursor()
        cur.beginEditBlock()
        von, bis = sorted((cur.anchor(), cur.position()))
        c = QTextCursor(self.document()); c.setPosition(von)
        blk = c.block()
        while blk.isValid() and blk.position() <= bis:
            self._stil_auf_block(blk, name)
            blk = blk.next()
        cur.endEditBlock()
        self.setFocus()

    def _stil_auf_block(self, blk, name: str) -> None:
        d = stile.definition(name)
        cc = QTextCursor(blk)
        bf = cc.blockFormat()
        level = d["ebene"]
        bf.setHeadingLevel(level)
        key = d.get("key")
        if key:
            bf.setProperty(STYLE_PROP, key)
        else:
            bf.clearProperty(STYLE_PROP)
        bf.setTopMargin(d["vor"] / 0.75); bf.setBottomMargin(d["nach"] / 0.75)
        if d.get("zeilen_art") in ("genau", "mindestens"):
            bf.setLineHeight(d.get("zeilen_pt", 12.0) / 0.75, 2 if d["zeilen_art"] == "genau" else 3)
        elif d.get("zeilen"):
            bf.setLineHeight(d["zeilen"] * 100, LH_PROPORTIONAL)
        if d.get("rechts"):
            from lunivo_writer.editor.querblatt import rechts_setzen
            rechts_setzen(bf, mm_to_px(d["rechts"]))
        if d.get("erste"):
            bf.setTextIndent(mm_to_px(d["erste"]))
        if d.get("rtl"):
            bf.setLayoutDirection(Qt.RightToLeft)
        if d.get("umbruch"):
            bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore)
        if d.get("gliederung") and d.get("key"):                    # Gliederungsebene einer eigenen Vorlage: Überschriftsebene (Qt kennt 1 bis 6)
            bf.setHeadingLevel(min(6, int(d["gliederung"])))
        if d.get("opt"):
            from lunivo_writer.editor import absatzopt
            absatzopt.setzen(bf, absatzopt.aus_text(d["opt"]))
        if d.get("einzug"):
            bf.setLeftMargin(mm_to_px(d["einzug"]))
        if d["ausr"]:
            bf.setAlignment({"links": Qt.AlignLeft, "mitte": Qt.AlignHCenter, "rechts": Qt.AlignRight, "block": Qt.AlignJustify}[d["ausr"]])
        if d.get("rahmen"):
            from lunivo_writer.editor.zusatz import B_RAHMEN
            bf.setProperty(B_RAHMEN, d["rahmen"])
        if d.get("muster") or d.get("fuell"):
            from lunivo_writer.editor import muster as M
            from lunivo_writer.editor.zusatz import B_MUSTER
            fuell = d.get("fuell") or None
            if d.get("muster"):
                bf.setBackground(M.pinsel(d["muster"], d.get("musterfarbe") or Farbe.SCHWARZ, fuell))
                bf.setProperty(B_MUSTER, M.als_text(d["muster"], d.get("musterfarbe") or Farbe.SCHWARZ, fuell))
            else:
                bf.setBackground(QBrush(QColor(fuell)))
        cc.setBlockFormat(bf)
        if d.get("tabs"):
            from lunivo_writer.ui.baukasten.tabstopp_dialog import aus_text as tabs_aus, zu_block
            bf = QTextCursor(blk).blockFormat(); zu_block(bf, tabs_aus(d["tabs"]))
            QTextCursor(blk).setBlockFormat(bf)
        if d.get("liste"):
            self._liste_auf_block(blk, d["liste"])
        sel = QTextCursor(blk)
        sel.movePosition(QTextCursor.StartOfBlock)
        sel.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        f = self._zeichen_der_vorlage(d)
        sel.mergeCharFormat(f)
        if d.get("versteckt"):
            f2 = QTextCharFormat(); f2.setProperty(P_VERSTECKT, 1); sel.mergeCharFormat(f2)
        if d.get("effekt"):
            from lunivo_writer.editor import texteffekt
            e = texteffekt.aus_text(d["effekt"], d.get("farbe", ""))
            if e:
                sel.mergeCharFormat(texteffekt.zu_format(e))
        self._ebene_der_vorlage(blk, name)

    def _zeichen_der_vorlage(self, d: dict) -> QTextCharFormat:
        """Das Zeichenformat einer Vorlage (alle Felder des Fensters „Schriftart“). Was die Vorlage nicht setzt, bleibt in der Auswahl, wie es ist."""
        from lunivo_writer.editor.zusatz import P_BETONUNG, P_DOPPELT, P_FONT_ASIEN, P_FONT_KOMPLEX, P_RASTER
        from lunivo_writer.ui.baukasten.text_format import ZEICHEN, zu_format
        zw = {k: d.get(k, v) for k, v in ZEICHEN.items()}
        f = zu_format(zw)
        if not zw["groesse"]:
            f.setFontPointSize(self.document().defaultFont().pointSizeF() or 11)
        Q = QTextFormat
        for schluessel, props in ((("unter",), (Q.TextUnderlineStyle,)), (("unterfarbe",), (Q.TextUnderlineColor,)),
                                  (("durch", "doppelt"), (Q.FontStrikeOut,)), (("hoch", "tief"), (Q.TextVerticalAlignment,)),
                                  (("kapital", "gross"), (Q.FontCapitalization,)), (("abstand",), (Q.FontLetterSpacingType, Q.FontLetterSpacing)),
                                  (("kerning", "kern_ab"), (Q.FontKerning,)), (("skala",), (Q.FontStretch,)), (("position",), (Q.TextBaselineOffset,)),
                                  (("raster",), (P_RASTER,)), (("doppelt",), (P_DOPPELT,)), (("betonung",), (P_BETONUNG,)),
                                  (("schrift_asien",), (P_FONT_ASIEN,)), (("schrift_komplex",), (P_FONT_KOMPLEX,))):
            if all(zw[k] == ZEICHEN[k] for k in schluessel):
                for pr in props:
                    f.clearProperty(pr)
        if not (zw["schrift"] or zw["schrift_asien"] or zw["schrift_komplex"]):
            f.clearProperty(Q.FontFamilies)
        return f

    def _ebene_der_vorlage(self, blk, name: str) -> None:
        """„Verbinden mit Formatvorlage“ (Gliederung anpassen): ein Absatz mit dieser Vorlage gehört zur verbundenen Ebene der Gliederung."""
        from lunivo_writer.editor import mehrstufig
        from lunivo_writer.editor.zusatz import B_MEHRSTUFIG
        b = blk.previous()
        defn = None
        while b.isValid():                                       # die nächste Gliederung davor, sonst die erste im Dokument
            if b.blockFormat().hasProperty(B_MEHRSTUFIG):
                w = mehrstufig.aus_block(b.blockFormat().stringProperty(B_MEHRSTUFIG))
                defn = w[1] if w else None
                break
            b = b.previous()
        if defn is None:
            return
        for i, e in enumerate(defn["ebenen"]):
            if e.get("vorlage") == name:
                c = QTextCursor(blk); bf = c.blockFormat()
                bf.setProperty(B_MEHRSTUFIG, mehrstufig.block_wert(i + 1, defn)); c.setBlockFormat(bf)
                mehrstufig.einrichten_alle(self.document())
                return

    def stil_tasten(self) -> None:
        """Die Tastenkombinationen der Formatvorlagen (nur gültig, solange der Editor den Fokus hat)."""
        from PySide6.QtGui import QKeySequence, QShortcut
        for s in getattr(self, "_stil_kurz", []):
            s.setEnabled(False); s.deleteLater()
        self._stil_kurz = []
        for n in stile.namen():
            t = stile.definition(n).get("taste", "")
            if t:
                sc = QShortcut(QKeySequence(t), self); sc.setContext(Qt.WidgetShortcut)
                sc.activated.connect(lambda n=n: self.apply_style(n))
                self._stil_kurz.append(sc)

    def _liste_auf_block(self, blk, text: str) -> None:
        """Absatz einer Formatvorlage mit Liste: aufeinanderfolgende Absätze mit derselben Liste zählen gemeinsam."""
        from lunivo_writer.editor import listen
        spec = listen.aus_text(text)
        if spec is None:
            return
        if "ebenen" in spec:
            from lunivo_writer.editor.mehrstufig import block_wert
            from lunivo_writer.editor.zusatz import B_MEHRSTUFIG
            c = QTextCursor(blk); bf = c.blockFormat()
            bf.setProperty(B_MEHRSTUFIG, block_wert(1, spec))
            c.setBlockFormat(bf)
            from lunivo_writer.editor import mehrstufig
            mehrstufig.einrichten_alle(self.document())
            return
        fmt = listen.zu_format(spec)
        vor = blk.previous().textList() if blk.previous().isValid() else None
        if vor is not None and listen.aus_format(vor.format()) == {k: v for k, v in spec.items() if k != "zeichen"}:
            vor.add(blk)
            self._nummern_zeichen(vor, spec.get("zeichen"))
        else:
            self._nummern_zeichen(QTextCursor(blk).createList(fmt), spec.get("zeichen"))

    def liste_spec(self):
        """Die Liste des Absatzes an der Schreibmarke (siehe ``editor.listen``) oder None."""
        from lunivo_writer.editor import listen, mehrstufig
        m = self._mehrstufig_am_zeiger()
        if m:
            return m[1]
        l = self.textCursor().currentList()
        return listen.aus_format(l.format()) if l else None

    def _mehrstufig_am_zeiger(self):
        """(Ebene, Gliederung) des Absatzes an der Schreibmarke, wenn er zu einer mehrstufigen Liste gehört."""
        from lunivo_writer.editor import mehrstufig
        from lunivo_writer.editor.zusatz import B_MEHRSTUFIG
        bf = self.textCursor().blockFormat()
        return mehrstufig.aus_block(bf.stringProperty(B_MEHRSTUFIG)) if bf.hasProperty(B_MEHRSTUFIG) else None

    def stil_neu_anwenden(self, name: str) -> int:
        """Nach „Formatvorlagen verwalten“: alle Absätze dieser Vorlage im Dokument neu formatieren."""
        n = 0
        cur = QTextCursor(self.document())
        cur.beginEditBlock()
        blk = self.document().firstBlock()
        while blk.isValid():
            if self._stil_name(blk.blockFormat()) == name:
                self._stil_auf_block(blk, name); n += 1
            blk = blk.next()
        cur.endEditBlock()
        return n

    @staticmethod
    def _stil_name(bf) -> str:
        key = bf.property(STYLE_PROP) if bf.hasProperty(STYLE_PROP) else None
        if key and str(key).startswith(stile.PRAEFIX):                # eine eigene Vorlage geht vor der Überschriftsebene, die sie setzen kann
            return stile.key_zu_name(str(key)) or "Standard"
        lvl = bf.headingLevel()
        if lvl in (1, 2, 3):
            return f"Überschrift {lvl}"
        for pfad in ("Title", "Subtitle", "Quote", "No Spacing"):
            if key == pfad:
                return stile.key_zu_name(pfad)
        if key and str(key).startswith(stile.PRAEFIX):
            return stile.key_zu_name(str(key)) or "Standard"
        return "Standard"

    def stil_aus_auswahl(self) -> dict:
        """Definition für eine neue Formatvorlage nach dem Absatz, in dem die Schreibmarke steht."""
        from lunivo_writer.editor import texteffekt
        from lunivo_writer.editor.listen import als_text
        from lunivo_writer.ui.baukasten.tabstopp_dialog import als_text as tabs_text, aus_block
        c = self.textCursor()
        bf, cf = c.blockFormat(), c.charFormat()
        ausr = {Qt.AlignHCenter: "mitte", Qt.AlignRight: "rechts", Qt.AlignJustify: "block"}
        a = next((v for k, v in ausr.items() if bf.alignment() & k), "")
        fam = cf.fontFamilies()
        return {"groesse": round(cf.fontPointSize(), 1) if cf.fontPointSize() > 0 else 0, "fett": cf.fontWeight() >= 600,
                "kursiv": cf.fontItalic(), "farbe": cf.foreground().color().name() if cf.foreground().style() != Qt.NoBrush and cf.hasProperty(QTextFormat.ForegroundBrush) else "",
                "schrift": fam[0] if fam else "", "vor": round(abstand_davor_px(bf) * 0.75, 1), "nach": round(bf.bottomMargin() * 0.75, 1), "ausr": a,
                **self._rahmen_felder(), "liste": als_text(self.liste_spec()),
                "effekt": texteffekt.als_text(texteffekt.aus_format(cf)),
                "tabs": tabs_text(aus_block(bf)), **self._zeichen_felder(cf), **self._absatz_felder(bf)}

    @staticmethod
    def _absatz_felder(bf) -> dict:
        """Die Felder des Fensters „Absatz“ (außer Ausrichtung, Einzug links, Abstände), als Felder einer Formatvorlage."""
        from lunivo_writer.editor import absatzopt, seitenfluss
        lart = {2: "genau", 3: "mindestens"}.get(int(bf.lineHeightType()), "faktor")
        from lunivo_writer.editor.querblatt import rechts_px
        return {"rechts": round(px_to_mm(rechts_px(bf)), 1), "erste": round(px_to_mm(bf.textIndent()), 1), "rtl": bf.layoutDirection() == Qt.RightToLeft,
                "umbruch": seitenfluss.ist_manuell(bf), "zeilen_art": lart, "zeilen_pt": round(bf.lineHeight() * 0.75, 1) if lart != "faktor" else 12.0,
                "gliederung": 0, "opt": absatzopt.als_text(absatzopt.lesen(bf))}

    def _zeichen_felder(self, cf) -> dict:
        """Die Felder des Fensters „Schriftart“ (ohne Schrift, Größe, Schnitt, Farbe) eines Zeichenformats, als Felder einer Formatvorlage."""
        from lunivo_writer.ui.baukasten.text_format import aus_format
        w = aus_format(cf)
        keys = ("unter", "unterfarbe", "durch", "doppelt", "hoch", "tief", "kapital", "gross", "abstand", "kerning", "betonung", "schrift_asien", "schnitt_asien",
                "groesse_asien", "schrift_komplex", "schnitt_komplex", "groesse_komplex", "skala", "position", "kern_ab", "raster")
        return {**{k: w[k] for k in keys}, "versteckt": cf.hasProperty(P_VERSTECKT)}

    def _rahmen_felder(self) -> dict:
        """Rahmen und Schattierung des Absatzes an der Schreibmarke als Felder einer Formatvorlage."""
        l = self.absatzrahmen()
        fuell, muster = self.absatzschatten()
        return {"rahmen": l.text() if l else "", "fuell": fuell or "", "muster": muster[0] if muster else "",
                "musterfarbe": muster[1] if muster else ""}

    def stil_entfernen(self, name: str) -> int:
        """Eine gelöschte eigene Vorlage: die Absätze behalten ihr Aussehen, verlieren aber die Zuordnung."""
        n = 0
        cur = QTextCursor(self.document())
        cur.beginEditBlock()
        blk = self.document().firstBlock()
        while blk.isValid():
            if blk.blockFormat().hasProperty(STYLE_PROP) and blk.blockFormat().property(STYLE_PROP) == stile.PRAEFIX + name:
                c = QTextCursor(blk); bf = c.blockFormat(); bf.clearProperty(STYLE_PROP); c.setBlockFormat(bf); n += 1
            blk = blk.next()
        cur.endEditBlock()
        return n

    def current_style(self) -> str:
        return self._stil_name(self.textCursor().blockFormat())


    # ---- Einfügen ----------------------------------------------------------------
