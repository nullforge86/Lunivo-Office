"""Referenzseiten aus einem zuvor im Ursprungsprogramm erzeugten PDF (QtPdf) oder aus bereitgestellten Seitenbildern. Es wird nur dargestellt, nichts interpretiert."""
from __future__ import annotations

import os


class ReferenzFehler(Exception):
    pass


def pdf_info(pfad: str) -> dict:
    """Seitenzahl und Seitengrößen (mm) eines PDFs. Wirft ``ReferenzFehler`` (z. B. defekt oder verschlüsselt)."""
    from PySide6.QtPdf import QPdfDocument
    doc = QPdfDocument(None)
    fehler = doc.load(pfad)
    if fehler != QPdfDocument.Error.None_:
        raise ReferenzFehler(f"PDF nicht lesbar ({fehler.name})")
    try:
        n = doc.pageCount()
        groessen = [(doc.pagePointSize(i).width() * 25.4 / 72.0, doc.pagePointSize(i).height() * 25.4 / 72.0) for i in range(min(n, 400))]
        return {"seiten": n, "groessen_mm": groessen}
    finally:
        doc.close()


def pdf_seiten(pfad: str, ordner: str, praefix: str, max_seiten: int, faktor: float = 1.0) -> dict:
    """Rendert die PDF-Seiten mit 96 dpi · ``faktor`` nach PNG. → ``{"seiten": gesamt, "pfade": [...], "groessen_mm": [...]}``."""
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QColor, QImage, QPainter
    from PySide6.QtPdf import QPdfDocument
    doc = QPdfDocument(None)
    fehler = doc.load(pfad)
    if fehler != QPdfDocument.Error.None_:
        raise ReferenzFehler(f"PDF nicht lesbar ({fehler.name})")
    try:
        os.makedirs(ordner, exist_ok=True)
        n = doc.pageCount()
        pfade, groessen = [], []
        for i in range(min(n, max_seiten)):
            pt = doc.pagePointSize(i)
            w, h = max(1, round(pt.width() * 96 / 72 * faktor)), max(1, round(pt.height() * 96 / 72 * faktor))
            bild = doc.render(i, QSize(w, h))
            if bild.isNull():
                raise ReferenzFehler(f"PDF-Seite {i + 1} lässt sich nicht darstellen")
            weiss = QImage(bild.size(), QImage.Format_RGB32)             # PDF-Seiten sind transparent: auf Weiß setzen
            weiss.fill(QColor("white"))
            p = QPainter(weiss)
            p.drawImage(0, 0, bild)
            p.end()
            ziel = os.path.join(ordner, f"{praefix}_{i + 1:04d}.png")
            weiss.save(ziel, "PNG")
            pfade.append(ziel)
            groessen.append((pt.width() * 25.4 / 72.0, pt.height() * 25.4 / 72.0))
        return {"seiten": n, "pfade": pfade, "groessen_mm": groessen}
    finally:
        doc.close()


def bilder_seiten(ordner: str, max_seiten: int) -> dict:
    """Seitenbilder aus einem Ordner (natürlich sortiert; je Datei eine Seite). Die Bilder werden nicht kopiert."""
    from kompatibilitaetspruefer.verwaltung.dateisuche import bilddateien
    dateien = bilddateien(ordner)
    if not dateien:
        raise ReferenzFehler("Der Bilderordner enthält keine Seitenbilder")
    return {"seiten": len(dateien), "pfade": dateien[:max_seiten], "groessen_mm": []}


def referenzseiten(ref: dict, ordner: str, max_seiten: int, faktor: float = 1.0) -> dict | None:
    """Referenzseiten laut Zuordnung (PDF bevorzugt); ``None``, wenn nichts Visuelles zugeordnet ist."""
    if ref.get("pdf"):
        if not os.path.isfile(ref["pdf"]):
            raise ReferenzFehler("Die zugeordnete Referenz-PDF existiert nicht mehr")
        return {"quelle": "pdf", **pdf_seiten(ref["pdf"], ordner, "ref", max_seiten, faktor)}
    if ref.get("bilder"):
        if not os.path.isdir(ref["bilder"]):
            raise ReferenzFehler("Der zugeordnete Bilderordner existiert nicht mehr")
        return {"quelle": "bilder", **bilder_seiten(ref["bilder"], max_seiten)}
    return None
