"""Lunivo Hybrid — weitere Symbole (Text, Seite, Tabelle, Objekte, Diagramme, Datei, Navigation).

Wird von lunivo_hybrid_erzeugen.py eingebunden. ``weitere(s, G)`` liefert {Symbolname: SVG-Körper};
``ZUORDNUNG_WEITERE`` ordnet ihnen die Symbolnamen der Oberfläche zu.
"""
from __future__ import annotations


def weitere(s, G):
    pf, rc, kr, seite, linien, tabelle, sprechblase, lupe, pfeil = G.pf, G.rc, G.kr, G.seite, G.linien, G.tabelle, G.sprechblase, G.lupe, G.pfeil
    I = {}

    # ---------- Text ----------
    A = "M4.5 24L11 8l6.5 16M6.8 19h8.4"
    I["gross_a"] = pf(s, A, sw=2.4) + pf(s, "M24 15V5M20.3 8.7L24 5l3.7 3.7", stroke="blue", sw=2.4)
    I["klein_a"] = pf(s, A, sw=2.4) + pf(s, "M24 5v10M20.3 11.3L24 15l3.7-3.7", stroke="blue", sw=2.4)
    I["eimer"] = pf(s, "M4.5 15L15 4.5 25.5 15l-8.700 8.700a2.500 2.500 0 0 1-3.500 0z", "blue") + pf(s, "M15 4.5l-2.500-2.500M4.500 15h21", sw=1.6) \
        + pf(s, "M27.500 20c1.800 2.200 2.300 3.200 2.300 4.300a2.300 2.300 0 0 1-4.600 0c0-1.100.5-2.100 2.300-4.300z", "purple", "purple", 1)
    I["palette"] = pf(s, "M16 3.500C9 3.500 3.500 9 3.500 16S9 28.500 15 28.500c2.200 0 2.700-1.300 2.100-2.700-.6-1.600.3-3 2.100-3H23A5.500 5.500 0 0 0 28.500 17.500C28.500 9.500 23 3.500 16 3.500z", "paper") \
        + kr(s, 9.500, 15, 1.800, "red", "red", 1) + kr(s, 13, 9.500, 1.800, "yellow", "yellow", 1) + kr(s, 20, 9.500, 1.800, "green", "green", 1) + kr(s, 24, 15, 1.800, "blue", "blue", 1)
    I["pinsel"] = pf(s, "M27 5L15 17", sw=3) + pf(s, "M15 17c-3.200-1-6 1-6 4.200 0 1.800-1.400 3.200-4 3.800 6.500 2.600 13-.6 13-5.500z", "purple")
    I["pipette"] = pf(s, "M20.500 5.500l6 6-3.200 3.200-6-6z", "blue") + pf(s, "M17.300 11.300l4.500 4.500L11 26.500l-5.500 1 1-5.500z", "paper") + pf(s, "M10 22l4 4", sw=1.4)
    I["radierer"] = pf(s, "M13 26L5.500 18.500a2.500 2.500 0 0 1 0-3.500L15.500 5a2.500 2.500 0 0 1 3.500 0l7.500 7.500a2.500 2.500 0 0 1 0 3.500L17 26z", "paper") \
        + pf(s, "M10.500 10l11.500 11.500L17 26l-11.500-11.500z", "red", "ink", 1.6) + pf(s, "M13 26h14", sw=2)
    I["einzug_mehr"] = linien(s, [7, 25], 5, 27) + linien(s, [13.500, 18.500], 15, 27, "ink", 1.9) + pf(s, "M5 12.500l5.500 3.500L5 19.500z", "blue", "blue", 1.4)
    I["einzug_weniger"] = linien(s, [7, 25], 5, 27) + linien(s, [13.500, 18.500], 15, 27, "ink", 1.9) + pf(s, "M10.500 12.500L5 16l5.500 3.500z", "blue", "blue", 1.4)
    I["abstand"] = linien(s, [5, 27], 5, 27, "ink", 2.2) + pf(s, "M16 9.500v13M12.500 13L16 9.500 19.500 13M12.500 19l3.500 3.500 3.500-3.500", stroke="purple", sw=2.2)
    I["ausrichten"] = pf(s, "M5 4v24", stroke="purple", sw=2.4) + rc(s, 9, 7, 17, 6, 1.500, "blue") + rc(s, 9, 19, 10, 6, 1.500, "blue")
    I["zeilenumbruch"] = pf(s, "M26 6v10H9", sw=2.400) + pf(s, "M14 10.500L8.500 16 14 21.500", stroke="blue", sw=2.600)
    I["spaltenumbruch"] = rc(s, 4, 5, 10, 22, 2, "paper") + rc(s, 18, 5, 10, 22, 2, "paper") + pf(s, "M16 10v12", stroke="purple", sw=2.200) + linien(s, [11, 16], 7, 11, "ink", 1.500) + linien(s, [11, 16], 21, 25, "ink", 1.500)
    I["tabstopp"] = pf(s, "M4.500 16h16M16 11l5 5-5 5", sw=2.200) + pf(s, "M27 7v18", stroke="purple", sw=3)
    I["textrichtung"] = pf(s, "M4.500 24L10 11l5.500 13M6.500 20h7", sw=2.200) + pf(s, "M20 8h7v7M27 8l-8 8", stroke="blue", sw=2.400)
    I["ebenen"] = pf(s, "M16 4.500l12 6.500-12 6.500L4 11z", "blue") + pf(s, "M4 17l12 6.500L28 17M4 22.500l12 6.500 12-6.500", sw=1.900)
    I["ebene_hoch"] = rc(s, 5, 14, 15, 13, 2.500, "paper") + rc(s, 10, 8, 15, 13, 2.500, "blue") + pf(s, "M26 12V4M22.500 7.500L26 4l3.500 3.500", stroke="purple", sw=2.200)
    I["ebene_tief"] = rc(s, 10, 8, 15, 13, 2.500, "paper") + rc(s, 5, 14, 15, 13, 2.500, "blue") + pf(s, "M27 21v8M23.500 25.500L27 29l3.500-3.500", stroke="purple", sw=2.200)
    I["umriss"] = pf(s, "M16 5.500c-5.500 0-9 4-9 10.500S10.500 26.500 16 26.500 25 22.500 25 16 21.500 5.500 16 5.500z", "none", "blue", 2.400) + pf(s, "M12 21l4-10 4 10M13.300 18h5.400", sw=2)
    I["texteffekt"] = pf(s, "M4.500 25L11 9l6.500 16M6.800 20h8.400", sw=2.600) + pf(s, "M24 5l1.600 4.400L30 11l-4.400 1.600L24 17l-1.600-4.400L18 11l4.400-1.600z", "purple", "purple", 1.200)
    I["hochgestellt"] = pf(s, "M5 26l11-14M16 26L5 12", sw=2.600) + pf(s, "M20 9a3 3 0 0 1 6 .2c0 2-6 3.800-6 6.300h6.200", stroke="purple", sw=2)
    I["tiefgestellt"] = pf(s, "M5 20l11-14M16 20L5 6", sw=2.600) + pf(s, "M20 22a3 3 0 0 1 6 .2c0 2-6 3.800-6 6.300h6.200", stroke="purple", sw=2)
    I["ohne_format"] = pf(s, "M5 25L11 9l6 16M7 20h8", sw=2.400) + pf(s, "M20 12l8 12M28 12l-8 12", stroke="red", sw=2.600)
    I["absatzmarke"] = pf(s, "M20 5v22M14.500 5v22M20 5h-6.500a5.800 5.800 0 0 0 0 11.600", stroke="blue", sw=2.800)
    # Stile (Formatvorlagen): Schrift mit abgestuften Ebenen – die Überschrift als farbiger Balken, darunter zwei kürzere Zeilen
    I["stile"] = (pf(s, "M3.500 25L10 6.500l6.500 18.500M6 18.500h8", sw=2.400) + rc(s, 20, 6, 9.500, 4.200, 2.100, "blue", "blue", 1)
                  + pf(s, "M20.500 17H27", stroke="purple", sw=2.400) + pf(s, "M20.500 24.500H24.500", sw=1.900))
    I["schreibweise"] = pf(s, "M3.500 24L9 10l5.500 14M5.500 20h7", sw=2.400) + pf(s, "M25 17.500a4 4 0 1 0 0 5.500M25 16.500v8", stroke="purple", sw=2.400)
    I["silben"] = pf(s, "M4 16h5M13 16h6M23 16h5", sw=2.400) + kr(s, 11, 16, 1.200, "blue", "blue", 1) + kr(s, 21, 16, 1.200, "blue", "blue", 1) + pf(s, "M6 9h4M14 9h8M6 23h8M18 23h8", stroke="purple", sw=2)
    I["sprache"] = kr(s, 16, 16, 12, "paper") + pf(s, "M4 16h24M16 4c-4 4-4 20 0 24M16 4c4 4 4 20 0 24", stroke="blue", sw=1.900)
    I["uebersetzen"] = rc(s, 3.500, 4.500, 14, 14, 2.500, "blue") + pf(s, "M7 14l3.500-7 3.500 7M8.300 11.500h4.400", stroke="white", sw=1.800) \
        + rc(s, 14.500, 13.500, 14, 14, 2.500, "paper") + pf(s, "M18.500 18.500h6M21.500 17v1.500c0 2.500-1.500 4-3 5M19.500 21c.8 1.600 2 2.600 4 3.200", stroke="purple", sw=1.800)
    I["buch"] = pf(s, "M6 4.500h17a3 3 0 0 1 3 3v19H8.500A2.500 2.500 0 0 1 6 24z", "blue") + pf(s, "M6 24a2.500 2.500 0 0 1 2.500-2.500H26", sw=1.800) + pf(s, "M11 10h10", stroke="white", sw=1.800)
    I["prozent"] = pf(s, "M25 6L7 26", sw=2.600) + kr(s, 9, 9, 3.500, "blue") + kr(s, 23, 23, 3.500, "purple")
    I["zahl"] = pf(s, "M12 5L9 27M23 5l-3 22M5.500 12h21M4.500 20h21", stroke="blue", sw=2.400)
    I["woerter"] = linien(s, [7, 13, 19], 4, 20, "ink", 1.900, {1: 16}) + rc(s, 17, 17, 11.500, 10, 2.500, "blue", "blue", 1) + pf(s, "M20 22h5.500M22.800 20v4", stroke="white", sw=1.800)
    I["vorhersage"] = pf(s, "M4.500 20L8.500 10l4 10M5.800 17h5.400", sw=2.100) + pf(s, "M16.500 10.500h8M16.500 15h5", stroke="ink", sw=1.800) + pf(s, "M23 22h5", stroke="blue", sw=2.400) \
        + rc(s, 4, 22, 17, 6, 2, "soft", "purple", 1.600)
    I["autokorr"] = pf(s, "M4.500 20L10 6l5.500 14M6.600 15.500h6.800", sw=2.200) + pf(s, "M15 24.500l4 4 9-10", stroke="green", sw=3)
    I["barrierefrei"] = kr(s, 16, 16, 12.500, "paper") + kr(s, 16, 9, 1.900, "blue", "blue", 1) + pf(s, "M8.500 13l7.500 1.500 7.500-1.500M16 14.500v5M16 19.500l-3.500 6M16 19.500l3.500 6", stroke="blue", sw=2)
    I["gruendlich"] = lupe(s, pf(s, "M9.500 13.700l2.800 2.800 5-5.500", stroke="green", sw=2.400))
    I["halt"] = pf(s, "M11 3.500h10L28.500 11v10L21 28.500H11L3.500 21V11z", "red") + pf(s, "M10.500 16h11", stroke="white", sw=3.200)
    I["verboten"] = kr(s, 16, 16, 12.500, "paper", "red", 2.800) + pf(s, "M7.500 24.500l17-17", stroke="red", sw=2.800)
    I["stopp"] = kr(s, 16, 16, 12.500, "red", "red", 1) + rc(s, 11, 11, 10, 10, 2, "white", "white", 1)
    I["gluehbirne"] = pf(s, "M16 3.500a9 9 0 0 0-5.500 16.100c.9.800 1.500 1.700 1.500 2.900V24h8v-1.500c0-1.200.6-2.100 1.500-2.900A9 9 0 0 0 16 3.500z", "yellow") + pf(s, "M12.500 28h7M13.500 24h5", sw=2)
    I["mikro"] = rc(s, 11.500, 3.500, 9, 16, 4.500, "purple") + pf(s, "M7 15a9 9 0 0 0 18 0M16 24v4M12 28h8", sw=2.100)
    I["schild_haken"] = pf(s, "M16 3.500l10 3.500v7.500c0 6-4.200 10.500-10 13.500C10.200 25 6 20.500 6 14.500V7z", "blue") + pf(s, "M11 15l3.500 3.500 7-7.500", stroke="white", sw=2.800)

    # ---------- Seite ----------
    I["abschnitt"] = seite(s) + pf(s, "M9 17h2.500M14.800 17h2.500M20.500 17H23", stroke="purple", sw=2.400) + linien(s, [12, 22], 9, 21, "ink", 1.600)
    I["leere_seite"] = seite(s) + pf(s, "M16 15.500v7M12.500 19h7", stroke="blue", sw=2.400)
    I["deckblatt"] = seite(s) + rc(s, 9.500, 12, 12, 5, 1.200, "blue", "blue", 1) + linien(s, [21, 24.500], 9.500, 21.500, "ink", 1.600, {1: 17})
    I["seitenrahmen"] = seite(s) + rc(s, 9, 12.500, 13, 13, 0.800, "none", "purple", 2.200)
    I["kopfzeile"] = seite(s) + rc(s, 6, 3.500, 19, 8, 0, "blue", "ink", 1.800) + linien(s, [17, 22], 10, 22, "ink", 1.500, {1: 17})
    I["fusszeile"] = seite(s) + rc(s, 6, 20, 19, 8.500, 0, "blue", "ink", 1.800) + linien(s, [12, 16], 10, 22, "ink", 1.500, {1: 17})
    I["kopf_fuss"] = seite(s) + rc(s, 6, 3.500, 19, 6.500, 0, "blue", "ink", 1.800) + rc(s, 6, 22, 19, 6.500, 0, "purple", "ink", 1.800) + linien(s, [15.500], 10, 22, "ink", 1.500)
    for n, d in (("oben", "M7 7h18"), ("unten", "M7 25h18"), ("links", "M7 7v18"), ("rechts", "M25 7v18")):
        I[f"kante_{n}"] = rc(s, 7, 7, 18, 18, 0, "none", "ink", 1.200, 'stroke-dasharray="2 2.400" opacity=".55"') + pf(s, d, stroke="blue", sw=3.400)
    I["kante_keine"] = rc(s, 7, 7, 18, 18, 0, "none", "ink", 1.600, 'stroke-dasharray="2.200 2.600"')
    I["wasserzeichen"] = seite(s) + pf(s, "M9 23l12-8", stroke="purple", sw=3.600, ) + linien(s, [13], 9, 14, "ink", 1.400)
    I["rahmen"] = rc(s, 4.500, 4.500, 23, 23, 3, "none", "blue", 2.800) + rc(s, 9.500, 9.500, 13, 13, 1.500, "paper")
    I["textrahmen"] = rc(s, 4, 6, 24, 20, 3, "paper") + linien(s, [12, 16.500, 21], 8.500, 23.500, "ink", 1.700, {2: 17}) + pf(s, "M4 6h4v-0", sw=1)
    I["kacheln"] = rc(s, 4, 4, 10.500, 10.500, 2.500, "blue") + rc(s, 17.500, 4, 10.500, 10.500, 2.500, "purple") + rc(s, 4, 17.500, 10.500, 10.500, 2.500, "paper") + rc(s, 17.500, 17.500, 10.500, 10.500, 2.500, "blue")
    I["textmarke"] = pf(s, "M8 4.500h16a1.500 1.500 0 0 1 1.500 1.500v22L16 21.500 6.500 28V6A1.500 1.500 0 0 1 8 4.500z", "purple")
    I["zitat"] = pf(s, "M12 9.500H7.500a2 2 0 0 0-2 2V17a2 2 0 0 0 2 2h4v1.500a3.500 3.500 0 0 1-3.500 3.500M26 9.500h-4.500a2 2 0 0 0-2 2V17a2 2 0 0 0 2 2h4v1.500a3.500 3.500 0 0 1-3.500 3.500", "blue", "ink", 2)
    I["datei"] = seite(s) + linien(s, [14, 19, 24], 10, 22, "ink", 1.600, {2: 17})
    I["datei_pfeil"] = seite(s) + pf(s, "M16 13v9M12 18.500l4 4 4-4", stroke="blue", sw=2.600)
    I["archiv"] = rc(s, 3.500, 5.500, 25, 7, 2, "purple") + pf(s, "M5.500 12.500v12a2 2 0 0 0 2 2h17a2 2 0 0 0 2-2v-12", "paper") + pf(s, "M12.500 18h7", sw=2.200)
    I["ordner_plus"] = pf(s, "M3.500 9a2 2 0 0 1 2-2h6l3 3h11a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2h-20a2 2 0 0 1-2-2z", "blue") + pf(s, "M16 14.500v8M12 18.500h8", stroke="white", sw=2.400)
    I["festplatte"] = rc(s, 3.500, 15, 25, 11, 3, "blue") + rc(s, 5.500, 5, 21, 10, 2.500, "paper") + kr(s, 8.500, 20.500, 1.200, "white", "white", 1) + pf(s, "M13 20.500h11", stroke="white", sw=1.800)
    I["herunterladen"] = pf(s, "M16 4.500v15M10.500 14.500l5.500 5.500 5.500-5.500", stroke="blue", sw=2.800) + pf(s, "M5 21.500v3a2 2 0 0 0 2 2h18a2 2 0 0 0 2-2v-3", sw=2.200)
    I["senden"] = pf(s, "M28 4L14 18M28 4l-8.500 24-5.500-10-10-5.500z", "blue")
    I["teilen"] = kr(s, 22.500, 7.500, 3.800, "blue") + kr(s, 8, 16, 3.800, "purple") + kr(s, 22.500, 24.500, 3.800, "blue") + pf(s, "M11.500 14.300l7.500-5M11.500 17.700l7.500 5", sw=2)
    I["abmelden"] = pf(s, "M13 5H7a2 2 0 0 0-2 2v18a2 2 0 0 0 2 2h6", sw=2.200) + pf(s, "M12 16h15M21.500 10.500L27 16l-5.500 5.500", stroke="red", sw=2.600)
    I["wolke"] = pf(s, "M9 24a6 6 0 0 1-.5-12A8 8 0 0 1 24 10.500 6.500 6.500 0 0 1 23.500 24z", "blue")
    I["code"] = pf(s, "M11 9l-7 7 7 7M21 9l7 7-7 7M18 6l-4 20", stroke="purple", sw=2.600)
    I["terminal"] = rc(s, 3.500, 5.500, 25, 21, 3, "ink", "ink", 1.600) + pf(s, "M9 12.500l4.500 3.500L9 19.500M16.500 21h6", stroke="green", sw=2.200)
    I["monitor"] = rc(s, 3.500, 5, 25, 16.500, 2.500, "blue") + pf(s, "M12 27h8M16 21.500V27", sw=2.200)
    I["praesentation"] = rc(s, 4, 5.500, 24, 16, 2.500, "paper") + pf(s, "M16 5.500V3M12 28l4-6.500 4 6.500", sw=2) + pf(s, "M9.500 17l4-4 3.500 3 5-5.500", stroke="purple", sw=2.200)
    I["video"] = rc(s, 3.500, 7.500, 18, 17, 3, "purple") + pf(s, "M21.500 14l7-4.500v13l-7-4.500z", "paper")
    I["haus"] = pf(s, "M4 15L16 4.500 28 15M7.500 13v13.500h17V13", "paper") + rc(s, 13, 18, 6, 8.500, 1, "blue", "ink", 1.800)
    I["uhr"] = kr(s, 16, 16, 12, "paper") + pf(s, "M16 9v7l4 3", stroke="blue", sw=2.600)
    I["briefumschlag"] = rc(s, 3.500, 7, 25, 18, 2.800, "paper") + pf(s, "M4.500 9.500L16 18l11.500-8.500", stroke="blue", sw=2.200)
    I["datenquelle"] = pf(s, "M5.500 7.500c0-2.200 4.700-4 10.500-4s10.500 1.800 10.500 4v17c0 2.200-4.700 4-10.500 4s-10.500-1.800-10.500-4z", "blue") + pf(s, "M5.500 7.500c0 2.200 4.700 4 10.500 4s10.500-1.800 10.500-4M5.500 16c0 2.200 4.700 4 10.500 4s10.500-1.800 10.500-4", sw=1.800)
    I["einzeldokumente"] = pf(s, "M11 4.500h9l5 5v14H11z", "paper") + pf(s, "M7 8.500v18h13", "none") + pf(s, "M20 4.500v5h5", sw=1.600) + linien(s, [15, 19], 14, 21, "blue", 1.600)

    # ---------- Tabelle ----------
    def tb(mark):
        return tabelle(s, 4, 5, 24, 22, "soft", 2, 2) + mark

    I["tabelle_zeichnen"] = tabelle(s, 3, 7, 21, 19, "soft", 2, 2) + pf(s, "M26 4.500l3.500 3.500-9.500 9.500-4 .5.500-4z", "purple") + pf(s, "M23.500 7l3.500 3.500", stroke="white", sw=1.400)
    I["tabelle_waehlen"] = tabelle(s, 4, 7, 21, 19, "soft", 2, 2) + pf(s, "M22 17l7 3-3 1.500L24.500 25z", "purple", "ink", 1.600)
    I["tabelle_teilen"] = tabelle(s, 4, 5, 24, 22, "soft", 1, 1) + rc(s, 4, 16, 24, 11, 0, "none", "purple", 2.400) + pf(s, "M16 18v7", stroke="purple", sw=2.400)
    I["tabelle_anpassen"] = tabelle(s, 4, 5, 24, 18, "soft", 2, 1) + pf(s, "M5 27h22M8.500 24.500L5.500 27l3 2.500M23.500 24.500l3 2.500-3 2.500", stroke="purple", sw=1.800)
    I["tabelle_eigenschaften"] = tabelle(s, 3, 5, 21, 19, "soft", 2, 2) + kr(s, 24, 24, 5.800, "paper", "ink", 1.800) + kr(s, 24, 24, 2, "blue", "blue", 1)
    I["tabelle_beschriftung"] = tabelle(s, 4, 4, 24, 17, "soft", 2, 1) + linien(s, [26], 8, 24, "purple", 2.400)
    I["zelle_oben"] = rc(s, 4, 4, 24, 24, 3, "paper") + linien(s, [9, 13], 8, 24, "blue", 2.400)
    I["zelle_mitte"] = rc(s, 4, 4, 24, 24, 3, "paper") + linien(s, [13.500, 18], 8, 24, "blue", 2.400)
    I["zelle_unten"] = rc(s, 4, 4, 24, 24, 3, "paper") + linien(s, [19, 23], 8, 24, "blue", 2.400)
    I["zeile_loeschen"] = tb(rc(s, 4, 16, 24, 5.500, 0, "red", None) + pf(s, "M13 18.800h6", stroke="white", sw=2) + rc(s, 4, 5, 24, 22, 3, "none"))
    I["spalte_loeschen"] = tb(rc(s, 12, 5.500, 8, 21.500, 0, "red", None) + pf(s, "M14.500 16h3", stroke="white", sw=2) + rc(s, 4, 5, 24, 22, 3, "none"))
    I["zellen_loeschen"] = tb(rc(s, 12, 16, 8, 5.500, 0, "red", None) + pf(s, "M14.500 18.800h3", stroke="white", sw=1.800) + rc(s, 4, 5, 24, 22, 3, "none"))

    # ---------- Bild & Objekte ----------
    I["bild_plus"] = rc(s, 3.500, 5.500, 22, 19, 3, "blue") + pf(s, "M3.500 21l6-6 4.500 4.500 3.500-3.500 8 8", "green") + kr(s, 18.500, 11.500, 2.200, "yellow", "ink", 1.300) \
        + kr(s, 24.500, 24.500, 5.500, "purple", "purple", 1) + pf(s, "M24.500 21.500v6M21.500 24.500h6", stroke="white", sw=2)
    I["bild_herunter"] = rc(s, 3.500, 5.500, 25, 21, 3, "blue") + pf(s, "M16 11v10M11.500 17l4.500 4.500 4.500-4.500", stroke="white", sw=2.600)
    I["bilder"] = rc(s, 8, 4.500, 20, 16, 2.500, "paper") + rc(s, 3.500, 10, 20, 17.500, 2.500, "blue") + pf(s, "M3.500 23.500l6-6 4 4 3-3 7 7", "green") + kr(s, 17, 15.500, 1.900, "yellow", "ink", 1.200)
    I["auswahl"] = rc(s, 4.500, 4.500, 18, 18, 1.500, "none", "blue", 2.200, 'stroke-dasharray="3 3"') + pf(s, "M16 14l12 5-5 2.500-2.500 5z", "purple", "ink", 1.800)
    I["zeiger"] = pf(s, "M8 4.500l17 9-7.500 2-2.500 8z", "purple")
    I["piktogramm"] = kr(s, 16, 16, 12.500, "yellow") + kr(s, 11.500, 13, 1.300, "ink", "ink", 1) + kr(s, 20.500, 13, 1.300, "ink", "ink", 1) + pf(s, "M10.500 19.500a6.500 6.500 0 0 0 11 0", sw=2)
    I["smartart"] = rc(s, 11, 3.500, 10, 7.500, 2, "blue") + rc(s, 3.500, 20.500, 10, 7.500, 2, "purple") + rc(s, 18.500, 20.500, 10, 7.500, 2, "green") + pf(s, "M16 11v4.500M8.500 20.500v-5h15v5", sw=2)
    I["gruppieren"] = rc(s, 3.500, 3.500, 25, 25, 3, "none", "ink", 1.600, 'stroke-dasharray="3 2.400"') + rc(s, 8, 8, 9, 9, 1.500, "blue") + rc(s, 15, 15, 9, 9, 1.500, "purple")
    I["drehen"] = pf(s, "M26 16a10 10 0 1 1-3-7.200M26 5v5.500h-5.500", stroke="purple", sw=2.800) + rc(s, 11.500, 11.500, 9, 9, 1.500, "blue")
    I["tauschen"] = pf(s, "M5 11h20M20 6l5 5-5 5M27 21H7M12 16l-5 5 5 5", stroke="purple", sw=2.600)
    I["schloss"] = rc(s, 6.500, 14, 19, 14, 3, "yellow") + pf(s, "M10.500 14V10.500a5.500 5.500 0 0 1 11 0V14", sw=2.400) + pf(s, "M16 19v4", sw=2.400)
    I["schluessel"] = kr(s, 10.500, 21.500, 6, "yellow") + pf(s, "M15 17l12-12M23 9.500l3.500 3.500M19.500 13l2.500 2.500", sw=2.200)
    I["anpassen"] = pf(s, "M4.500 12V4.500H12M20 4.500h7.500V12M27.500 20v7.500H20M12 27.500H4.500V20", stroke="blue", sw=2.800) + rc(s, 11, 11, 10, 10, 1.500, "paper")
    I["verschieben"] = pf(s, "M16 3.500v25M3.500 16h25M12 7.500l4-4 4 4M12 24.500l4 4 4-4M7.500 12l-4 4 4 4M24.500 12l4 4-4 4", stroke="purple", sw=2.400)
    I["zuschneiden"] = pf(s, "M9 3.500v18.500h18.500M3.500 9H22v18.500", stroke="blue", sw=2.800)
    I["umfliessen"] = rc(s, 4, 6, 11, 11, 2, "blue") + linien(s, [8, 12.500, 17], 18, 28, "ink", 1.800) + linien(s, [22, 26.500], 4, 28, "ink", 1.800) + pf(s, "M4 21.500h2", sw=1)
    I["linie"] = kr(s, 6.500, 25.500, 3, "blue") + kr(s, 25.500, 6.500, 3, "purple") + pf(s, "M8.600 23.400l14.800-14.800", sw=2.400)
    I["freihand"] = pf(s, "M3.500 22c4-12 7-12 9-6s5 6 8-2 5-7 8.500-3", stroke="purple", sw=2.800)
    I["welle"] = pf(s, "M3 16c3-8 5-8 8 0s5 8 8 0 5-8 8 0", stroke="blue", sw=2.800)
    I["kreis_form"] = kr(s, 16, 16, 11.500, "blue")
    I["quadrat_form"] = rc(s, 5, 5, 22, 22, 3, "blue")
    I["dreieck_form"] = pf(s, "M16 4.500l12 21H4z", "purple")
    I["raute_form"] = pf(s, "M16 3.500l12.500 12.500L16 28.500 3.500 16z", "blue")
    I["fuenfeck_form"] = pf(s, "M16 3.500l12 8.700-4.600 14.300H8.600L4 12.200z", "purple")
    I["sechseck_form"] = pf(s, "M9.500 5.500h13L29 16l-6.500 10.500h-13L3 16z", "blue")
    I["stern"] = pf(s, "M16 3.500l3.900 8 8.800 1.200-6.400 6.200 1.500 8.800L16 23.500l-7.800 4.200 1.500-8.800-6.400-6.200 8.800-1.200z", "yellow")
    I["herz"] = pf(s, "M16 27C6 20 4 14 4 10.500A6.500 6.500 0 0 1 16 7a6.500 6.500 0 0 1 12 3.500C28 14 26 20 16 27z", "red")
    I["sonne"] = kr(s, 16, 16, 5.500, "yellow") + pf(s, "M16 3.500v3M16 25.500v3M3.500 16h3M25.500 16h3M7.200 7.200l2.100 2.100M22.700 22.700l2.100 2.100M7.200 24.800l2.100-2.100M22.700 9.300l2.100-2.100", stroke="yellow", sw=2.400)
    I["mond"] = pf(s, "M25.500 19.500A11 11 0 0 1 12.500 6.500a11 11 0 1 0 13 13z", "purple")
    I["ziel"] = kr(s, 16, 16, 12, "paper") + kr(s, 16, 16, 7, "none", "blue", 2.200) + kr(s, 16, 16, 2.200, "red", "red", 1)
    I["stempel"] = pf(s, "M4 6h24M4 26h24", sw=1)  # Platzhalter (nicht zugeordnet)
    del I["stempel"]

    # ---------- Diagramme ----------
    I["balken_quer"] = rc(s, 5, 5, 11, 5.500, 1.500, "blue") + rc(s, 5, 13.300, 19, 5.500, 1.500, "purple") + rc(s, 5, 21.500, 15, 5.500, 1.500, "blue") + pf(s, "M3 3v26", sw=2)
    I["torte"] = kr(s, 16, 16, 11.500, "blue") + pf(s, "M16 16V4.500A11.500 11.500 0 0 1 27.500 16z", "purple") + pf(s, "M16 16L8 24.200", sw=1.600)
    I["ring"] = kr(s, 16, 16, 11.500, "blue") + pf(s, "M16 4.500A11.500 11.500 0 0 1 27.500 16H21A5 5 0 0 0 16 11z", "purple") + kr(s, 16, 16, 5, "paper")
    I["streu"] = pf(s, "M4 4v24h24", sw=2.200) + kr(s, 10, 20, 2.200, "blue", "blue", 1) + kr(s, 14, 12, 2.200, "purple", "purple", 1) + kr(s, 20, 17, 2.200, "blue", "blue", 1) + kr(s, 24, 8.500, 2.200, "purple", "purple", 1)
    I["netz"] = pf(s, "M16 4l11 8-4.200 13H9.200L5 12z", "none", "ink", 1.500) + pf(s, "M16 10l5.800 4.200-2.200 6.800h-7.200l-2.200-6.800z", "blue") + pf(s, "M16 4v6M27 12l-5.200 2.200M22.800 25l-3.200-4M9.200 25l3.200-4M5 12l5.200 2.200", sw=1.500)
    I["kombination"] = rc(s, 5, 15, 5.500, 12, 1.500, "blue") + rc(s, 13.200, 10, 5.500, 17, 1.500, "blue") + rc(s, 21.500, 18, 5.500, 9, 1.500, "blue") + pf(s, "M4 12l8-5 8 3.500 8-6", stroke="purple", sw=2.400) + pf(s, "M3 29h26", sw=2)
    I["kerzen"] = pf(s, "M8 4v24M16 7v19M24 3.500v20", sw=1.800) + rc(s, 5, 9.500, 6, 11, 1, "green") + rc(s, 13, 11.500, 6, 9, 1, "red") + rc(s, 21, 8, 6, 10, 1, "green")
    I["flaeche_chart"] = pf(s, "M3.500 25.500l7-9 6 4.500 6.500-11 5.500 6V25.500z", "blue") + pf(s, "M3 28.500h26", sw=2)
    I["linien_chart"] = pf(s, "M4 4v24h24", sw=2.200) + pf(s, "M7.500 21l6-7 5 4 8-10", stroke="purple", sw=2.600) + kr(s, 13.500, 14, 1.900, "paper", "purple", 1.800) + kr(s, 26.500, 8, 1.900, "paper", "purple", 1.800)
    I["trichter"] = pf(s, "M4 5.500h24l-9 11.500v8l-6 3v-11z", "blue")
    I["sigma"] = pf(s, "M24 6H8l8 10-8 10h16", stroke="purple", sw=2.800)
    I["omega"] = pf(s, "M6 26h6a8 8 0 1 1 8 0h6", stroke="purple", sw=2.800)
    I["phi"] = pf(s, "M16 4v24", stroke="purple", sw=2.800) + pf(s, "M16 8c-7 0-10 3-10 8s3 8 10 8 10-3 10-8-3-8-10-8z", "none", "purple", 2.800)
    I["beschriftung"] = pf(s, "M4 16l10-10h12a2 2 0 0 1 2 2v12L18 30 4 16z".replace("L18 30 4 16", "l-10 10z"), "yellow") + kr(s, 22.500, 9.500, 1.800, "paper", "ink", 1.600)

    # ---------- Navigation ----------
    I["pfeil_runter"] = pf(s, "M16 5v21M8.500 18.500L16 26l7.500-7.500", stroke="blue", sw=3)
    I["pfeil_hoch"] = pf(s, "M16 27V6M8.500 13.500L16 6l7.500 7.500", stroke="blue", sw=3)
    I["pfeil_rechts"] = pf(s, "M5 16h21M18.500 8.500L26 16l-7.500 7.500", stroke="blue", sw=3)
    I["pfeil_links_rechts"] = pf(s, "M4 12h24M22 6l6 6-6 6M28 22H4M10 16l-6 6 6 6", stroke="purple", sw=2.600)
    I["nach_unten"] = pf(s, "M7 12l9 9 9-9", stroke="blue", sw=3)
    I["nach_oben"] = pf(s, "M7 20l9-9 9 9", stroke="blue", sw=3)
    I["erster"] = pf(s, "M24 6L14 16l10 10M7 6v20", stroke="blue", sw=3)
    I["letzter"] = pf(s, "M8 6l10 10L8 26M25 6v20", stroke="blue", sw=3)
    I["haken_einfach"] = pf(s, "M6 17l7 7L26 9", stroke="green", sw=3.400)
    I["kreis_leer"] = kr(s, 16, 16, 11.500, "paper")
    I["punkt"] = kr(s, 16, 16, 4.500, "blue", "blue", 1)
    I["mehr_punkte"] = kr(s, 7, 16, 2.400, "blue", "blue", 1) + kr(s, 16, 16, 2.400, "blue", "blue", 1) + kr(s, 25, 16, 2.400, "blue", "blue", 1)
    I["menue"] = pf(s, "M5 9h22M5 16h22M5 23h22", sw=3)
    I["regler"] = pf(s, "M4 10h24M4 22h24", sw=1.900) + kr(s, 11, 10, 3.600, "blue") + kr(s, 21, 22, 3.600, "purple")
    I["stift_zeile"] = pf(s, "M24 5l4 4-14.500 14.500-5.500 1.500 1.500-5.500z", "purple") + pf(s, "M4 28.500h24", stroke="blue", sw=2.400)
    I["listen_start"] = pf(s, "M5 9h2M12 9h15M5 16h2M12 16h15M5 23h2M12 23h15", sw=2.200) + pf(s, "M4.500 4.500l3 2.500-3 2.500", stroke="blue", sw=0)
    I["gliederung_baum"] = rc(s, 4, 4, 9, 6.500, 1.500, "blue") + rc(s, 17.500, 12.500, 9, 6, 1.500, "paper") + rc(s, 17.500, 22, 9, 6, 1.500, "paper") + pf(s, "M8.500 10.500V25H17.500M8.500 15.500H17.500", sw=1.900)
    I["liste_minus"] = linien(s, [8, 16, 24], 4, 20, "ink", 2) + pf(s, "M22.500 24h6", stroke="red", sw=2.600)
    I["raster_layout"] = rc(s, 4, 4, 24, 24, 3, "paper") + pf(s, "M4 16h24M16 4v24", sw=1.800) + rc(s, 4.800, 4.800, 10.400, 10.400, 2, "blue", None)
    I["vorlage_layout"] = rc(s, 4, 4, 24, 24, 3, "paper") + rc(s, 4, 4, 24, 7, 3, "blue") + rc(s, 4, 15, 9, 13, 0, "soft", "ink", 1.600) + pf(s, "M17 17h7M17 22h7", sw=1.800)
    I["ersetzen_ab"] = pf(s, "M5 10h18M18 5l5 5-5 5", stroke="purple", sw=2.600) + pf(s, "M27 22H9M14 17l-5 5 5 5", stroke="blue", sw=2.600)
    I["papierkorb"] = pf(s, "M7.500 9.500l1.500 17a2 2 0 0 0 2 1.800h10a2 2 0 0 0 2-1.800l1.500-17z", "red") + pf(s, "M4.500 9.500h23M12 9.500V6a1.500 1.500 0 0 1 1.500-1.500h5A1.500 1.500 0 0 1 20 6v3.500", sw=2.200) + pf(s, "M13 14.500v9M19 14.500v9", stroke="white", sw=1.800)
    return I


ZUORDNUNG_WEITERE = {
    # Text
    "groesserA": "gross_a", "a-arrow-up": "gross_a", "kleinerA": "klein_a", "a-arrow-down": "klein_a",
    "paint-bucket": "eimer", "absatztoenung": "eimer", "toenung": "eimer", "flaeche": "eimer",
    "palette": "palette", "farbe": "palette", "pinsel": "pinsel", "pinselchen": "pinsel", "pipette": "pipette",
    "radierer": "radierer", "tabelleRadierer": "radierer",
    "list-indent-increase": "einzug_mehr", "einzug": "einzug_mehr", "weEinzug": "einzug_mehr", "list-indent-decrease": "einzug_weniger", "weEinzugLeer": "einzug_weniger",
    "abstand": "abstand", "absatzlayout": "abstand", "ausrichten": "ausrichten", "verteilt": "ausrichten", "anordnen": "ausrichten",
    "zeilenumbruch": "zeilenumbruch", "weReturn": "zeilenumbruch", "weZeilenWeg": "zeilenumbruch", "spaltenumbruch": "spaltenumbruch",
    "tabstopp": "tabstopp", "schnelltab": "tabstopp", "weFuehrend": "tabstopp", "textrichtung": "textrichtung", "tabelleTextrichtung": "textrichtung",
    "ebenen": "ebenen", "ebeneHoch": "ebene_hoch", "ebeneTief": "ebene_tief", "umriss": "umriss", "texteffekt": "texteffekt", "wordart": "texteffekt",
    "superscript": "hochgestellt", "hoch": "hochgestellt", "subscript": "tiefgestellt", "tief": "tiefgestellt",
    "remove-formatting": "ohne_format", "ohneformat": "ohne_format", "steuerzeichen": "absatzmarke", "pilcrow": "absatzmarke", "pilcrow-left": "absatzmarke", "markupzeigen": "absatzmarke",
    "schreibweise": "schreibweise", "Stil": "schreibweise", "stile": "stile", "silben": "silben", "phonetisch": "silben", "trennung": "silben",
    "sprache": "sprache", "globe": "sprache", "uebersetzen": "uebersetzen", "woerterbuch": "buch", "thesaurus": "buch", "buch": "buch",
    "handbuch": "buch", "indexbuch": "buch", "Duden": "buch", "Prozent": "prozent", "zahl": "zahl", "woerter": "woerter", "wortextras": "woerter",
    "Vorhersage": "vorhersage", "autokorr": "autokorr", "barrierefrei": "barrierefrei", "gruendlich": "gruendlich",
    "halt": "halt", "octagon": "halt", "ban": "verboten", "circle-stop": "stopp", "vorschlag": "gluehbirne", "stimme": "mikro", "aufnahme": "mikro",
    "shield-check": "schild_haken", "lesen": "brille", "hoeren": "vorlesen",
    # Seite
    "abschnitt": "abschnitt", "abschnittgerade": "abschnitt", "abschnittlaufend": "abschnitt", "abschnittungerade": "abschnitt",
    "leereseite": "leere_seite", "deckblatt": "deckblatt", "seitenrahmen": "seitenrahmen", "kopfz": "kopfzeile", "fussz": "fusszeile", "kopffuss": "kopf_fuss",
    "kanteOben": "kante_oben", "kanteUnten": "kante_unten", "kanteLinks": "kante_links", "kanteRechts": "kante_rechts", "kanteKeine": "kante_keine", "kanteAlle": "seitenrahmen",
    "kaestchen": "gitter", "wasserzeichen": "wasserzeichen", "rahmen": "rahmen", "frame": "rahmen", "square": "quadrat_form",
    "textrahmen": "textrahmen", "square-text": "textrahmen", "text-cursor-input": "textrahmen", "form": "textrahmen", "formfeld": "textrahmen",
    "kacheln": "kacheln", "layout-grid": "kacheln", "panels-top-left": "vorlage_layout", "layout-template": "vorlage_layout", "vorlage": "vorlage_layout", "baustein": "vorlage_layout",
    "textmarke": "textmarke", "tag": "beschriftung", "beschriftung": "beschriftung", "zitat": "zitat", "quote": "zitat",
    "file": "datei", "file-text": "datei", "inhalt": "datei", "files": "kopieren", "ausdatei": "datei_pfeil", "file-pen": "aenderungen_nachverfolgen",
    "file-lock": "schloss", "archive": "archiv", "folder": "oeffnen", "folder-plus": "ordner_plus", "hard-drive": "festplatte", "download": "herunterladen",
    "send": "senden", "share": "teilen", "log-out": "abmelden", "beenden": "abmelden", "cloud": "wolke", "code": "code", "terminal": "terminal",
    "monitor": "monitor", "presentation": "praesentation", "video": "video", "house": "haus", "clock": "uhr", "clock-arrow-up": "zuletzt", "pruefzeit": "uhr",
    "mail": "briefumschlag", "briefumschlag": "briefumschlag", "datenquelle": "datenquelle", "einzeldokumente": "einzeldokumente",
    "link": "link", "verknuepft": "link", "eintrag": "datei", "endnote": "fussnote", "notentrenner": "fussnote",
    # Tabelle
    "table": "tabelle_einfuegen", "tabelleZeichnen": "tabelle_zeichnen", "tabelleWahl": "tabelle_waehlen", "tabelleTeilen": "tabelle_teilen", "tabelleTabelleTeilen": "tabelle_teilen",
    "tabelleAutoAnpassen": "tabelle_anpassen", "tabelleEigenschaften": "tabelle_eigenschaften", "tabelleBeschriftung": "tabelle_beschriftung",
    "tabelleZellAusrichtung": "zelle_mitte", "zelleMitte": "zelle_mitte", "zelleOben": "zelle_oben", "zelleUnten": "zelle_unten",
    "tabelleZeileLoeschen": "zeile_loeschen", "tabelleSpalteLoeschen": "spalte_loeschen", "tabelleZellenLoeschen": "zellen_loeschen",
    # Bild & Objekte
    "bildfoto": "bild", "image-plus": "bild_plus", "image-down": "bild_herunter", "images": "bilder", "auswahlbereich": "auswahl", "allesmark": "auswahl",
    "mouse-pointer": "zeiger", "piktogramm": "piktogramm", "smartart": "smartart", "workflow": "smartart", "network": "smartart", "zuordnen": "smartart",
    "zusammenfassen": "smartart", "zusammenfuehren": "smartart", "list-tree": "gliederung_baum", "gruppieren": "gruppieren", "objekte": "formen", "shapes": "formen",
    "objektdrehen": "drehen", "rotate-cw": "drehen", "rotate-ccw": "drehen", "refresh-cw": "drehen", "aktualisieren": "drehen", "arrow-left-right": "tauschen", "wechseln": "tauschen",
    "sperren": "schloss", "lock": "schloss", "key": "schluessel", "anpassen": "anpassen", "scaling": "anpassen", "maximize": "anpassen", "vollbild": "anpassen",
    "einpassen": "anpassen", "move": "verschieben", "crop": "zuschneiden", "textflussumbruch": "umfliessen", "umschlossen": "umfliessen", "eingeschlossen": "umfliessen",
    "linie": "linie", "freihand": "freihand", "wellen": "welle", "kreis": "torte", "circle": "kreis_leer", "ellipse": "kreis_form", "diamond": "raute_form",
    "triangle": "dreieck_form", "pentagon": "fuenfeck_form", "hexagon": "sechseck_form", "star": "stern", "heart": "herz", "sparkles": "assistent",
    "brain": "assistent", "sun": "sonne", "sun-dim": "sonne", "hell": "sonne", "dunkel": "mond", "target": "ziel", "box": "archiv", "dot": "punkt",
    "pen-line": "stift", "pencil": "stift", "square-pen": "stift", "type": "schreibweise", "baseline": "schreibweise",
    # Diagramme
    "chart-column": "diagramm", "saeule": "diagramm", "chart-bar": "balken_quer", "balkenquer": "balken_quer", "chart-pie": "torte", "donut": "ring",
    "chart-scatter": "streu", "punktwolke": "streu", "radar": "netz", "netz": "netz", "kombination": "kombination", "chart-no-axes-combined": "kombination",
    "chart-candlestick": "kerzen", "kurs": "kerzen", "chart-area": "flaeche_chart", "chart-line": "linien_chart", "filter": "trichter", "diagrammteil": "diagramm",
    "sigma": "sigma", "omega": "omega", "phi": "phi", "pi": "formel",
    # Navigation
    "arrow-down": "pfeil_runter", "arrow-up": "pfeil_hoch", "arrow-right": "pfeil_rechts", "chevron-down": "nach_unten", "chevron-up": "nach_oben",
    "chevron-first": "erster", "chevron-last": "letzter", "ersterSatz": "erster", "letzterSatz": "letzter", "check": "haken_einfach", "x": "schliessen", "cross": "schliessen",
    "ellipsis": "mehr_punkte", "menu": "menue", "sliders-horizontal": "regler", "settings-2": "regler", "optionen": "regler", "search": "suchen",
    "info": "info", "zurueck": "nach_links", "vor": "nach_rechts", "weniger": "minus", "equal": "tauschen", "list-start": "aufzaehlung", "list-minus": "liste_minus",
    "weNeu": "plus", "weLoeschen": "ablehnen", "weLeerWeg": "minus", "weSmart": "autokorr", "weLeerEin": "gitter", "weLeerModus": "gitter", "weLeerz": "gitter",
    "naechstesfeld": "nach_rechts", "seriefeld": "felder", "serienschliessen": "serienbrief_starten", "replace": "ersetzen",
    "send-right": "senden", "monitor-x": "monitor", "unter": "zelle_unten", "ecken": "rahmen", "unterart": "stift_zeile", "klappe": "nach_unten",
    "bereich": "auswahl", "automatisch": "assistent", "sortieren": "tauschen", "radius": "kreis_form", "space": "abstand", "sortiere": "tauschen",
    "log": "datei", "logs": "datei", "heart-handshake": "herz", "stern": "stern", "kleinerLupe": "zoom_minus", "grid": "gitter",
    "kurs2": "kerzen", "markierung": "markieren", "verteilen": "ausrichten", "pin": "textmarke", "markup2": "absatzmarke", "umschlag": "briefumschlag",
    "ersetzen_alt": "ersetzen_ab", "stempel": "stern", "paint": "eimer", "dokument": "datei", "doc": "datei", "tafel": "praesentation",
    "tasten": "terminal", "aehnlich": "vergleichen", "betonung": "fett", "clipboard-paste": "einfuegen", "copy": "kopieren", "delete": "papierkorb",
    "trash-2": "papierkorb", "disc": "speichern", "einschraenken": "schloss", "fortlaufend": "nummerierung", "list-chevrons-up-down": "tauschen",
    "view": "vorschau", "zeile": "links", "unterart2": "stift_zeile", "anchor": "textmarke", "cat": "herz", "can": "archiv", "send2": "senden",
}
