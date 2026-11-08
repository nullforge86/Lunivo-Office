"""Grenzen für fremde Dokumente: werden geprüft, bevor ein Leser (DOCX, ODT, RTF) das Dokument verarbeitet.

Geprüft wird das ZIP-Paket (DOCX, DOTX, DOCM, ODT) durch tatsächliches Entpacken in Stücken — nicht nach den Größenangaben im
Kopf der Datei, denn die kann ein präpariertes Paket falsch angeben. Dabei wird nichts gespeichert, nur gezählt.

    pruefe_paket(pfad, "DOCX")           # wirft DocumentIOError mit verständlicher Meldung
    pruefe_dateigroesse(pfad, "RTF")     # für Formate ohne Paket (RTF, FODT, TXT)
    sicheres_xml(daten)                  # xml.etree-Wurzel; ohne DTD/Entitäten, mit Tiefengrenze
    lxml_parser()                        # lxml-Parser ohne Entitätenauflösung und ohne Netzzugriff

Die Zahlen stehen in ``GRENZEN`` (eine Stelle); Tests setzen sie herunter, statt riesige Dateien zu bauen.
"""
from __future__ import annotations

import io
import logging
import os
import zipfile
from dataclasses import dataclass
from xml.etree import ElementTree as ET

from lunivo_writer.models.report import DocumentIOError

_log = logging.getLogger("lunivo.dateien")
MB = 1024 * 1024


@dataclass
class Grenzen:
    paket_bytes: int = 256 * MB              # Größe der Datei selbst (ZIP-Formate)
    text_bytes: int = 512 * MB               # RTF, FODT, TXT
    eintraege: int = 5000                    # Dateien im Paket
    entpackt_gesamt: int = 512 * MB          # alle Einträge zusammen, tatsächlich entpackt
    xml_eintrag: int = 64 * MB               # eine XML-Datei im Paket
    bild_eintrag: int = 64 * MB              # ein Bild oder sonstiger Eintrag
    verhaeltnis: int = 100                   # entpackt : gepackt; gilt erst ab ``verhaeltnis_ab``
    verhaeltnis_ab: int = 10 * MB
    xml_tiefe: int = 200                     # Schachtelungstiefe der Elemente
    kopf_pruefung: int = 16384               # so viele Anfangsbytes einer XML-Datei werden auf DTD/Entitäten durchsucht


GRENZEN = Grenzen()
_XML_ENDUNGEN = (".xml", ".rels", ".fodt")
_VERBOTEN = (b"<!ENTITY", b"<!DOCTYPE")      # Word und OpenDocument brauchen keine DTD; Entitäten wären ein Angriffsweg


def _mb(n: int) -> str:
    return f"{n // MB} MB"


def pruefe_dateigroesse(pfad: str, art: str, grenze: int | None = None) -> int:
    """Größe der Datei gegen die Grenze prüfen. → Größe in Byte."""
    try:
        groesse = os.path.getsize(pfad)
    except OSError as e:
        raise DocumentIOError(f"Datei nicht lesbar: {e.strerror or e}") from e
    grenze = grenze or GRENZEN.text_bytes
    if groesse > grenze:
        raise DocumentIOError(f"Die {art}-Datei ist mit {_mb(groesse)} größer als die zulässigen {_mb(grenze)} und wird aus "
                              "Sicherheitsgründen nicht geöffnet.")
    return groesse


def _zu_gross(art: str, was: str) -> DocumentIOError:
    return DocumentIOError(f"Die {art}-Datei ist {was} und wird aus Sicherheitsgründen nicht geöffnet.")


def pruefe_paket(pfad: str, art: str) -> None:
    """Prüft ein ZIP-Paket, bevor irgendetwas daraus gelesen wird. Wirft DocumentIOError, sonst Rückkehr ohne Wert."""
    g = GRENZEN
    pruefe_dateigroesse(pfad, art, g.paket_bytes)
    try:
        z = zipfile.ZipFile(pfad)
    except (zipfile.BadZipFile, OSError) as e:
        raise DocumentIOError(f"Die Datei ist kein gültiges {art}-Dokument oder beschädigt.") from e
    with z:
        infos = z.infolist()
        if len(infos) > g.eintraege:
            raise _zu_gross(art, f"ungewöhnlich umfangreich ({len(infos)} Teile, erlaubt sind {g.eintraege})")
        namen = [i.filename for i in infos]
        if len(set(namen)) != len(namen):
            raise _zu_gross(art, "fehlerhaft aufgebaut (doppelte Teile)")
        gesamt = 0
        for i in infos:
            if i.is_dir():
                continue
            if i.flag_bits & 0x1:
                raise _zu_gross(art, "mit Paketverschlüsselung geschützt, die nicht unterstützt wird")
            grenze = g.xml_eintrag if i.filename.lower().endswith(_XML_ENDUNGEN) else g.bild_eintrag
            if i.file_size > grenze:           # schnelle Absage nach der Angabe im Kopf; die echte Prüfung folgt unten
                raise _zu_gross(art, f"in einem Teil („{i.filename}“) zu groß ({_mb(i.file_size)})")
            echt = _entpacken_zaehlen(z, i, art, grenze, g.entpackt_gesamt - gesamt)
            gesamt += echt
    _log.debug("%s-Paket geprüft: %d Teile, %s entpackt", art, len(infos), _mb(gesamt))


def _entpacken_zaehlen(z: zipfile.ZipFile, info: zipfile.ZipInfo, art: str, grenze: int, rest: int) -> int:
    """Entpackt einen Eintrag nur zum Zählen. Prüft Größe, Gesamtgröße, Verhältnis und (bei XML) DTD/Entitäten."""
    g = GRENZEN
    ist_xml = info.filename.lower().endswith(_XML_ENDUNGEN)
    n, kopf = 0, b""
    try:
        with z.open(info) as f:
            while True:
                stueck = f.read(MB)
                if not stueck:
                    break
                n += len(stueck)
                if ist_xml and len(kopf) < g.kopf_pruefung:
                    kopf += stueck[:g.kopf_pruefung - len(kopf)]
                    if any(v in kopf for v in _VERBOTEN):
                        raise _zu_gross(art, f"unzulässig aufgebaut („{info.filename}“ enthält eine DTD oder Entitäten)")
                if n > grenze:
                    raise _zu_gross(art, f"in einem Teil („{info.filename}“) entpackt zu groß (über {_mb(grenze)})")
                if n > rest:
                    raise _zu_gross(art, f"entpackt größer als die zulässigen {_mb(g.entpackt_gesamt)}")
                if n >= g.verhaeltnis_ab and info.compress_size and n / info.compress_size > g.verhaeltnis:
                    raise _zu_gross(art, f"verdächtig stark komprimiert („{info.filename}“)")
    except DocumentIOError:
        raise
    except (zipfile.BadZipFile, OSError, EOFError, NotImplementedError, RuntimeError, ValueError) as e:
        _log.warning("%s-Paket nicht entpackbar (%s): %s", art, info.filename, type(e).__name__)
        raise DocumentIOError(f"Die Datei ist kein gültiges {art}-Dokument oder beschädigt.") from e
    except Exception as e:                      # zlib.error u. a. bei abgeschnittenen Daten
        _log.warning("%s-Paket nicht entpackbar (%s): %s", art, info.filename, type(e).__name__)
        raise DocumentIOError(f"Die Datei ist kein gültiges {art}-Dokument oder beschädigt.") from e
    return n


def _tiefe_pruefen(daten: bytes) -> ET.Element:
    it = ET.iterparse(io.BytesIO(daten), events=("start", "end"))
    tiefe = 0
    for ereignis, _el in it:
        if ereignis == "start":
            tiefe += 1
            if tiefe > GRENZEN.xml_tiefe:
                raise DocumentIOError("Das Dokument ist zu tief verschachtelt, um es sicher zu öffnen.")
        else:
            tiefe -= 1
    return it.root


def sicheres_xml(daten: bytes) -> ET.Element:
    """XML lesen wie ``ET.fromstring``, aber ohne DTD und Entitäten und mit Tiefengrenze. Wirft DocumentIOError."""
    kopf = daten[:GRENZEN.kopf_pruefung]
    if any(v in kopf for v in _VERBOTEN):
        raise DocumentIOError("Das Dokument enthält eine nicht zulässige XML-Deklaration (DTD oder Entitäten) und wird nicht geöffnet.")
    try:
        return _tiefe_pruefen(daten)
    except ET.ParseError as e:
        raise DocumentIOError("Die Datei ist beschädigt (fehlerhaftes XML).") from e


def lxml_parser():
    """lxml-Parser für selbst gelesene Teile: keine Entitäten, kein Netz, keine DTD, keine Riesenknoten."""
    from lxml import etree
    return etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False, huge_tree=False, dtd_validation=False)
