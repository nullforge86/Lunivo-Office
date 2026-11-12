"""Was dem Chat vor dem Senden mitgegeben wird: Systemtext mit Dokument, Websuche, Dokumentensuche, Bildanhänge; und die Nachbearbeitung der Antwort.
``ki`` ist die ``KI``-Instanz (Konfiguration, Zustimmung, Fähigkeiten). Die Suchen laufen nur mit Zustimmung und dürfen den Chat nie verhindern."""
from __future__ import annotations

from lunivo_writer.ki import chat_antwort as CA
from lunivo_writer.ki import ki_transport as T
from lunivo_writer.ki.ki_konfiguration import EMPFAENGER

DOKUMENT_GRENZE = 12000
KUERZUNG_HINWEIS = "\n\n[Antwort wegen der Längengrenze gekürzt — in den Chat-Einstellungen „Maximale Länge“ erhöhen.]"


def system_text(ki, dokumenttext: str) -> str:
    system = ("Du bist ein Schreibassistent in einem Textverarbeitungsprogramm und antwortest kurz und klar auf Deutsch. "
              "Erfinde nichts dazu. " + EMPFAENGER.get(ki.k["empfaenger"], EMPFAENGER["egal"]))
    if dokumenttext.strip():
        system += "\n\nDer Mensch arbeitet gerade an diesem Text:\n" + dokumenttext[:DOKUMENT_GRENZE] + "\n\n" + CA.FORMAT_ZEILE
    return system


def sperre(ki, modell: str, verlauf: list[dict], dokumenttext: str, markiert: bool):
    """Fehlende Zustimmung (Text, dann Bildinhalt) als Wörterbuch, sonst None. ``markiert``: nur die Markierung geht raus."""
    umfang = "dokument" if dokumenttext.strip() and not markiert else "auszug"
    if (s := ki.zustimmung_fehlt(modell, umfang)) is not None:
        return s
    if verlauf and verlauf[-1].get("bilder"):
        return ki.zustimmung_fehlt(modell, "bild")           # der Bildinhalt geht an den Anbieter: eigene Einwilligung
    return None


def bilder(ki, modell: str, verlauf: list[dict]):
    """(Verlauf mit gelesenen Bildern, Fehler oder None). Lesen und Base64 erst hier, im Arbeitsfaden."""
    if not (verlauf and verlauf[-1].get("bilder")):
        return verlauf, None
    if not ki.faehigkeit(modell)[1]:
        return verlauf, {"fehler": "Das gewählte Modell kann keine Bilder verarbeiten. Bitte ein anderes Modell wählen."}
    verlauf, fehler = T.bilder_lesen(verlauf)
    return verlauf, ({"fehler": fehler} if fehler else None)


def websuche(ki, verlauf: list[dict]) -> tuple[str, str]:
    """(Zusatz für den Systemtext, Notiz für den Benutzer)."""
    ws = ki.k.websuche_optionen()
    if not (ws["an"] and verlauf):
        return "", ""
    ziel = ki.websuche_ziel()
    if ziel and not ki.k.hat_einwilligung(ziel, "auszug"):
        return "", f"(Die Websuche wurde nicht ausgeführt: keine Zustimmung, die Frage an „{ziel}“ zu senden.)\n\n"
    from lunivo_writer.ki import websuche as W
    try:
        treffer = W.suche(ws, verlauf[-1]["text"])
    except (OSError, ValueError) as e:
        return "", f"(Die Websuche hat nicht geklappt: {getattr(e, 'reason', e)})\n\n"
    if not treffer:
        return "", ""
    return "\n\nErgebnisse einer Websuche zur Frage (nenne die Nummer der Quelle, wenn du sie benutzt):\n" + W.als_text(treffer), ""


def dokumentensuche(ki, verlauf: list[dict], modell: str) -> tuple[str, str, list]:
    """(Zusatz für den Systemtext, Notiz, Fundstellen)."""
    dso = ki.k.dokumentsuche_optionen()
    if not (dso["an"] and dso["ordner"] and verlauf):
        return "", "", []
    aussen = ki.schickt_nach_aussen(modell)
    if aussen and not ki.k.hat_einwilligung(aussen, "auszug"):
        return "", f"(Die Dokumentensuche wurde nicht ausgeführt: keine Zustimmung, Auszüge an „{aussen}“ zu senden.)\n\n", []
    from lunivo_writer.ki import dokumentensuche as DS
    try:
        idx = DS.Index(ki.k.dokumentindex_pfad())
        idx.aktualisieren(dso["ordner"], zeitgrenze=4.0)       # nur Neues und Geändertes, mit Zeitgrenze
        quellen = idx.suchen(verlauf[-1]["text"], dso["ordner"], dso["anzahl"])
    except Exception as e:                                     # die Suche darf den Chat nie verhindern
        return "", f"(Die Dokumentensuche hat nicht geklappt: {e})\n\n", []
    if not quellen:
        return "", "", []
    return ("\n\nAuszüge aus Dokumenten des Benutzers (nenne die Nummer der Quelle, wenn du sie benutzt; antworte nur mit dem, "
            "was dort steht):\n" + DS.als_text(quellen)), "", quellen


def abschliessen(r: dict, quellen: list, notiz: str) -> dict:
    """Kürzungshinweis, Fundstellen und Notiz als eigene Felder (``kuerzung``, ``fundstellen``, ``notiz``) neben ``text`` legen."""
    if "text" not in r:
        return r
    if r.pop("abgeschnitten", False):
        r["kuerzung"] = KUERZUNG_HINWEIS.strip()
    if quellen:
        from lunivo_writer.ki import dokumentensuche as DS
        r["fundstellen"] = "Fundstellen:\n" + DS.fundstellen_zeilen(quellen)
    if notiz:
        r["notiz"] = notiz.strip()
    return r
