"""Prüfung des Dokumentaufbaus. Ohne Qt.

``pruefe_dokument`` findet Verstöße gegen die Regeln des Modells — die Bearbeitungssitzung hält sie ein; Dateileser prüfen damit,
was sie gebaut haben.
"""
from __future__ import annotations

from core.dokument.dokument import ABSCHNITT_BEGINN, OBJEKT_ARTEN, UMBRUCH_ARTEN, Absatz, Dokument, InlineObjekt, Lauf, Rahmen, Tabelle
from core.dokument.formate import FormatFehler, pruefe


def pruefe_dokument(d: Dokument) -> list:
    """Gibt die Fehler als Texte zurück; eine leere Liste heißt: Der Aufbau stimmt."""
    fehler: list = []
    ids: set = set()

    def neue_id(i, was):
        if not isinstance(i, int) or i < 1:
            fehler.append(f"{was}: ungültige Id {i!r}")
        elif i in ids:
            fehler.append(f"{was}: Id {i} ist doppelt vergeben")
        elif i >= d.naechste_id:
            fehler.append(f"{was}: Id {i} liegt über dem Zähler des Dokuments")
        ids.add(i)

    def fmt(art, werte, was):
        try:
            pruefe(art, werte)
        except FormatFehler as e:
            fehler.append(f"{was}: {e}")

    def bloecke(liste, wo, anfang_ok=False):
        if not liste:
            fehler.append(f"{wo}: enthält keinen Absatz")
            return
        if not isinstance(liste[-1], Absatz):
            fehler.append(f"{wo}: endet nicht mit einem Absatz")
        for i, b in enumerate(liste):
            if isinstance(b, Absatz):
                absatz(b)
            elif isinstance(b, (Tabelle, Rahmen)):
                if (i == 0 and not anfang_ok) or (i > 0 and not isinstance(liste[i - 1], Absatz)):
                    fehler.append(f"{wo}: {type(b).__name__} {b.id} hat keinen Absatz davor")
                if isinstance(b, Tabelle):
                    tabelle(b)
                else:
                    neue_id(b.id, f"Rahmen {b.id}")
                    fmt("rahmen", b.format, f"Rahmen {b.id}")
                    bloecke(b.bloecke, f"Rahmen {b.id}")
            else:
                fehler.append(f"{wo}: unbekannter Block {type(b).__name__}")

    def absatz(a):
        was = f"Absatz {a.id}"
        neue_id(a.id, was)
        fmt("absatz", a.format, was)
        fmt("zeichen", a.zeichenformat, was)
        if a.format.get("vorlage") and a.format["vorlage"] not in d.vorlagen:
            fehler.append(f"{was}: Formatvorlage „{a.format['vorlage']}“ fehlt")
        if a.liste_id is not None:
            if a.liste_id not in d.listen:
                fehler.append(f"{was}: Liste {a.liste_id} fehlt")
            elif not 0 <= a.ebene < len(d.listen[a.liste_id].ebenen):
                fehler.append(f"{was}: Listenebene {a.ebene} gibt es nicht")
        vorher = None
        for x in a.inhalte:
            if isinstance(x, Lauf):
                if not x.text:
                    fehler.append(f"{was}: leeres Textstück")
                if "\n" in x.text:
                    fehler.append(f"{was}: Zeilenwechsel im Textstück")
                if isinstance(vorher, Lauf) and vorher.format == x.format and "feld" not in x.format:
                    fehler.append(f"{was}: benachbarte Textstücke mit gleichem Format")
            elif isinstance(x, InlineObjekt):
                neue_id(x.id, f"Objekt in {was}")
                objekt(x, f"Objekt {x.id}")
            else:
                fehler.append(f"{was}: unbekannter Inhalt {type(x).__name__}")
                continue
            fmt("zeichen", x.format, was)
            k = x.format.get("kommentar")
            if k is not None and k not in d.kommentare:
                fehler.append(f"{was}: Kommentar {k} fehlt")
            n = x.format.get("note")
            if n is not None:
                art, _, nid = n.partition(":")
                if art not in d.noten or not nid.isdigit() or int(nid) not in d.noten[art]:
                    fehler.append(f"{was}: Note {n} fehlt")
            vorher = x

    def objekt(o, was):
        if o.art not in OBJEKT_ARTEN:
            fehler.append(f"{was}: unbekannte Art {o.art}")
        if o.breite < 0 or o.hoehe < 0:
            fehler.append(f"{was}: negative Größe")
        if o.ressource and o.ressource not in d.ressourcen:
            fehler.append(f"{was}: Bilddaten „{o.ressource}“ fehlen")

    def tabelle(t):
        was = f"Tabelle {t.id}"
        neue_id(t.id, was)
        fmt("tabelle", t.format, was)
        if not t.zellen or not t.zellen[0]:
            fehler.append(f"{was}: hat keine Zellen")
            return
        zeilen, spalten = t.zeilen, t.spalten
        if any(len(z) != spalten for z in t.zellen):
            fehler.append(f"{was}: Zeilen sind verschieden lang")
            return
        if len(t.spaltenbreiten) != spalten:
            fehler.append(f"{was}: {len(t.spaltenbreiten)} Spaltenbreiten für {spalten} Spalten")
        if len(t.zeilenhoehen) != zeilen:
            fehler.append(f"{was}: {len(t.zeilenhoehen)} Zeilenhöhen für {zeilen} Zeilen")
        belegt: dict = {}
        for z in range(zeilen):
            for s in range(spalten):
                c = t.zellen[z][s]
                if c.verdeckt_von is not None:
                    continue
                fmt("zelle", c.format, f"{was}, Zelle {z}/{s}")
                if c.zeilenspanne < 1 or c.spaltenspanne < 1 or z + c.zeilenspanne > zeilen or s + c.spaltenspanne > spalten:
                    fehler.append(f"{was}, Zelle {z}/{s}: Spanne reicht über die Tabelle hinaus")
                    continue
                for dz in range(c.zeilenspanne):
                    for ds in range(c.spaltenspanne):
                        if (z + dz, s + ds) in belegt:
                            fehler.append(f"{was}: Zellen {belegt[(z + dz, s + ds)]} und {(z, s)} überdecken sich")
                        belegt[(z + dz, s + ds)] = (z, s)
                bloecke(c.bloecke, f"{was}, Zelle {z}/{s}")
        for z in range(zeilen):
            for s in range(spalten):
                c = t.zellen[z][s]
                if c.verdeckt_von is None:
                    continue
                if c.bloecke:
                    fehler.append(f"{was}, Zelle {z}/{s}: verdeckte Zelle hat Inhalt")
                if belegt.get((z, s)) != tuple(c.verdeckt_von) or tuple(c.verdeckt_von) == (z, s):
                    fehler.append(f"{was}, Zelle {z}/{s}: Verweis auf die verbundene Zelle stimmt nicht")

    if not d.abschnitte:
        fehler.append("Das Dokument hat keinen Abschnitt")
    for n, abschnitt in enumerate(d.abschnitte):
        neue_id(abschnitt.id, f"Abschnitt {n}")
        if abschnitt.beginn not in ABSCHNITT_BEGINN:
            fehler.append(f"Abschnitt {n}: unbekannter Beginn {abschnitt.beginn}")
        seite = abschnitt.seite
        if seite.width_mm <= 0 or seite.height_mm <= 0:
            fehler.append(f"Abschnitt {n}: Papier ohne Größe")
        elif seite.margin_left_mm + seite.margin_right_mm >= seite.width_mm or seite.margin_top_mm + seite.margin_bottom_mm >= seite.height_mm:
            fehler.append(f"Abschnitt {n}: Ränder lassen keinen Platz für Text")
        bloecke(abschnitt.bloecke, f"Abschnitt {n}", anfang_ok=n > 0)

    absaetze = {a.id for a in d.absaetze()}
    for oid, o in d.objekte.items():
        was = f"Freies Objekt {oid}"
        if o.id != oid:
            fehler.append(f"{was}: Schlüssel und Id stimmen nicht überein")
        neue_id(o.id, was)
        objekt(o, was)
        if o.anker not in absaetze:
            fehler.append(f"{was}: Ankerabsatz {o.anker} fehlt")
        if o.umbruch not in UMBRUCH_ARTEN:
            fehler.append(f"{was}: unbekannter Textumbruch {o.umbruch}")
    for lid, liste in d.listen.items():
        neue_id(liste.id, f"Liste {lid}")
        if liste.id != lid or not 1 <= len(liste.ebenen) <= 9:
            fehler.append(f"Liste {lid}: Id oder Zahl der Ebenen stimmt nicht")
    for name, v in d.vorlagen.items():
        if v.name != name:
            fehler.append(f"Formatvorlage „{name}“: Schlüssel und Name stimmen nicht überein")
        fmt("zeichen", v.zeichen, f"Formatvorlage „{name}“")
        fmt("absatz", v.absatz, f"Formatvorlage „{name}“")
        gesehen, basis = {name}, v.basis
        while basis:
            if basis in gesehen:
                fehler.append(f"Formatvorlage „{name}“: Basisvorlagen bilden einen Kreis")
                break
            gesehen.add(basis)
            basis = d.vorlagen[basis].basis if basis in d.vorlagen else ""
    for kid, k in d.kommentare.items():
        if k.id != kid:
            fehler.append(f"Kommentar {kid}: Schlüssel und Id stimmen nicht überein")
        if k.antwort_auf is not None and k.antwort_auf not in d.kommentare:
            fehler.append(f"Kommentar {kid}: beantworteter Kommentar {k.antwort_auf} fehlt")
    for art in d.noten:
        if art not in ("f", "e"):
            fehler.append(f"Unbekannte Notenart {art}")
    return fehler
