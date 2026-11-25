"""RTF-Formen schreiben (Gegenstück zu ``rtf/formen``): ``{\\shp{\\*\\shpinst … {\\sp{\\sn Name}{\\sv Wert}} {\\shptxt …}}}``, Qt-frei.

Formen, Textfelder, WordArt-Text und Bildrahmen werden als eigenständige Formen am Absatz geschrieben; eine Gruppe wird in ihre Teile zerlegt (RTF kennt Gruppen nur mit
eigener Gruppenstruktur, die Word nicht verlangt). Was RTF nicht ausdrückt, steht im Bericht: Mustervorlagen werden zum Raster, Bildfüllungen entfallen."""
from __future__ import annotations

from lunivo_writer.dienste.rtf.formen import _FORM
from lunivo_writer.dienste.rtf_basis import _text

_TYP = {v: k for k, v in _FORM.items()}
_UMBRUCH = {"oben_unten": 1, "quadrat": 2, "vor": 3, "hinter": 3, "eng": 4}
_STRICH = {"gestrichelt": 1, "gepunktet": 2, "strichpunkt": 4, "strichpunktpunkt": 5, "fein_gestrichelt": 6}


def _bgr(farbe) -> int:
    if isinstance(farbe, str) and len(farbe) == 7 and farbe.startswith("#"):
        try:
            return int(farbe[5:7] + farbe[3:5] + farbe[1:3], 16)
        except ValueError:
            pass
    return 0


def _sp(name: str, wert) -> str:
    return f"{{\\sp{{\\sn {name}}}{{\\sv {wert}}}}}"


def _text_gruppe(text: str, innen: dict) -> str:
    fmt = f"\\fs{int(round(float(innen.get('pt') or 12) * 2))}" + ("\\b" if innen.get("fett") else "") + ("\\i" if innen.get("kursiv") else "")
    absaetze = "\\par ".join(_text(z) for z in text.split("\n"))
    return f"{{\\shptxt \\pard\\plain{fmt} {absaetze}\\par}}"


def shape_rtf(art: str, breite: float, hoehe: float, daten: dict, lage: dict, melden, ebene: int = 0, bild_pict: str = "", roh_pict: str = "") -> str:
    """Die Form als RTF-Gruppe. ``lage``: ``bezug_h``, ``bezug_v``, ``x``, ``y``, ``umbruch`` (Bildpunkte); ``bild_pict``: fertige ``\\pict``-Gruppe für Bildrahmen."""
    innen = daten.get("daten") if isinstance(daten.get("daten"), dict) else {}
    x, y = float(lage.get("x") or 0.0), float(lage.get("y") or 0.0)
    geom = (f"\\shpleft{round(x * 15)}\\shptop{round(y * 15)}\\shpright{round((x + breite) * 15)}\\shpbottom{round((y + hoehe) * 15)}\\shpfhdr0"
            f"\\shpbx{ {'seite': 'page', 'rand': 'margin'}.get(lage.get('bezug_h'), 'column') }\\shpby{ {'seite': 'page', 'rand': 'margin'}.get(lage.get('bezug_v'), 'para') }"
            f"\\shpwr{_UMBRUCH.get(lage.get('umbruch'), 2)}\\shpfblwtxt{1 if lage.get('umbruch') == 'hinter' else 0}\\shpz{ebene}")
    eig = []
    if art == "bild":
        eig += [_sp("shapeType", 75), f"{{\\sp{{\\sn pib}}{{\\sv {bild_pict}}}}}"]
        text = ""
    elif art == "wordart":
        eig += [_sp("shapeType", 136), _sp("gtextUNICODE", _text(str(innen.get("text") or ""))), _sp("gtextFont", _text(str(innen.get("schrift") or "Liberation Sans")))]
        voll = innen.get("fuell") if isinstance(innen.get("fuell"), dict) else {}
        eig += [_sp("fillColor", _bgr(voll.get("farbe") or "#000000"))]
        text = ""
        melden("WordArt wird in RTF als Fontwork-Text mit Farbe geschrieben; Verlauf, Schatten und Verformung gehen dabei verloren.")
    else:
        kind = str(innen.get("form") or "rechteck").casefold() if art == "form" else "rechteck"
        typ = 202 if art == "textfeld" else _TYP.get(kind)
        if typ is None:
            melden(f"Die Form „{kind}“ hat in RTF keinen Namen und wurde als Rechteck geschrieben.")
            typ = 1
        eig.append(_sp("shapeType", typ))
        voll = daten.get("fuell") if "fuell" in daten else ({"art": "farbe", "farbe": innen["fuell"]} if innen.get("fuell") else {})
        if voll == {} or not isinstance(voll, dict) or kind == "linie":
            eig.append(_sp("fFilled", 0))
        else:
            fart, farbe = voll.get("art", "farbe"), voll.get("farbe") or "#ffffff"
            if fart == "graduell":
                stops = voll.get("stops") or []
                if len(stops) > 2:
                    melden("Ein Farbverlauf mit mehr als zwei Farben wurde in der RTF-Datei auf Anfangs- und Endfarbe verkürzt.")
                eig += [_sp("fillType", 7), _sp("fillColor", _bgr(stops[0][1] if stops else voll.get("hell", farbe))), _sp("fillBackColor", _bgr(stops[-1][1] if stops else voll.get("dunkel", "#ffffff"))),
                        _sp("fillAngle", int(((90.0 - float(voll.get("winkel", 90.0))) % 360.0) * 65536))]
            elif fart == "muster":
                if voll.get("key") not in ("rein", None):
                    melden("Ein Füllmuster wurde in der RTF-Datei als Raster aus Muster- und Grundfarbe geschrieben (RTF-Formen kennen keine Mustertabelle).")
                eig += [_sp("fillType", 1 if voll.get("key") not in ("rein", None) else 0), _sp("fillColor", _bgr(farbe)), _sp("fillBackColor", _bgr(voll.get("grund") or "#ffffff"))]
            elif fart == "bild":
                melden("Eine Bildfüllung wird in der RTF-Datei nicht gespeichert; die Form bleibt ohne Füllung.")
                eig.append(_sp("fFilled", 0))
            else:
                eig.append(_sp("fillColor", _bgr(farbe)))
        if roh_pict:                                                  # aufbewahrtes Füllbild in unbekanntem Format: unverändert zurück
            eig += [_sp("fillType", 3), f"{{\\sp{{\\sn fillBlip}}{{\\sv {roh_pict}}}}}"]
        rand = daten.get("rand") if isinstance(daten.get("rand"), dict) else None
        linie = (rand or {}).get("farbe") or str(innen.get("linie") or "")
        if linie:
            b = float((rand or {}).get("b") or innen.get("strich") or 1.0)
            eig += [_sp("lineColor", _bgr(linie)), _sp("lineWidth", int(b * 9525))]
            if (rand or {}).get("art") in _STRICH:
                eig.append(_sp("lineDashing", _STRICH[rand["art"]]))
        else:
            eig.append(_sp("fLine", 0))
        text = str(innen.get("text") or "")
        if art == "textfeld":
            ins = innen.get("innen") if isinstance(innen.get("innen"), (list, tuple)) and len(innen["innen"]) == 4 else None
            if ins:
                eig += [_sp(k, int(float(v) * 9525)) for k, v in zip(("dxTextLeft", "dyTextTop", "dxTextRight", "dyTextBottom"), ins)]
    dreh = float(daten.get("dreh", 0) or 0)
    if dreh:
        eig.append(_sp("rotation", int((dreh % 360) * 65536)))
    for k, n in (("flipH", "fFlipH"), ("flipV", "fFlipV")):
        if daten.get(k):
            eig.append(_sp(n, 1))
    txt = _text_gruppe(text, innen) if text.strip() else ""
    return f"{{\\shp{{\\*\\shpinst{geom}{''.join(eig)}{txt}}}}}"
