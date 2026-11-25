"""Die PDF-Ausgabe läuft ohne Qt über ``dienste.pdf_ausgabe`` (Kern-Renderer und ``core.layout.drucklayout.ausgabe.pdfziel``); dieser Name bleibt nur für ältere Aufrufer."""
from filter.pdf.pdf_ausgabe import dokument_als_pdf  # noqa: F401
