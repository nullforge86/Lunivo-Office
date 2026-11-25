"""Die PDF-Ausgabe läuft ohne Qt über ``dienste.pdf_ausgabe`` (Kern-Renderer und ``core.rendering.pdfziel``); dieser Name bleibt nur für ältere Aufrufer."""
from lunivo_writer.dienste.pdf.pdf_ausgabe import dokument_als_pdf  # noqa: F401
