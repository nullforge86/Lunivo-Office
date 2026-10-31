"""Befehle: Kontext-Reiter „WPSArt-Design“ für das SmartArt als freies Objekt (``editor/frei_objekt.py``, Art ``smartart``).

Die Knoten stehen als Baum in den Daten (``editor/smartart.py``); die Befehle wirken auf den gewählten Knoten (``daten["auswahl"]``, gesetzt über
``smartartKnotenWaehlen`` oder die Mausbedienung). Zum Ausgrauen gibt es zu jedem Befehl mit Richtung einen eigenen Namen samt ``kann_…``.
Ein Baustein von ``Befehle`` (siehe ``core/commands.py``)."""
from __future__ import annotations


class SmartArtToolsBefehle:
    def _sa(self) -> dict | None:
        from lunivo_writer.editor import smartart as SA
        return SA.daten_der_auswahl(self.ed) if self.ed else None

    def _sa_hinweis(self) -> bool:
        self.w.lbl_msg.setText("Bitte zuerst ein SmartArt-Objekt auswählen.")
        return False

    def _sa_tun(self, f, *args) -> bool:
        from lunivo_writer.editor import smartart as SA
        if self._sa() is None:
            return self._sa_hinweis()
        ok = getattr(SA, f)(self.ed, *args)
        self.w.band.aktualisieren()
        return ok

    # ---- Knoten wählen und beschriften ------------------------------------------------------------------------------------------------
    def smartartKnotenWaehlen(self, k=None, ident=None):
        """Knoten wählen (``smartartKnotenWaehlen:["k2"]``; ohne Id: Auswahl aufheben). Zeichnet nicht neu."""
        from lunivo_writer.editor import smartart as SA
        return SA.knoten_waehlen(self.ed, ident) if self._sa() is not None else self._sa_hinweis()

    def smartartKnotenText(self, k=None, ident=None, text=""):
        """Den Text eines Knotens setzen (Eintippen im Knoten)."""
        return self._sa_tun("knoten_text_setzen", ident, text)

    # ---- WPSArt-Design -------------------------------------------------------------------------------------------------------------------
    def smartartFormEinfuegen(self, k=None, wie="nach"):
        """„Form einfügen“: ``nach`` | ``vor`` | ``unter`` | ``ueber`` | ``assistent`` relativ zum gewählten Knoten (ohne Auswahl: hinter den letzten);
        der neue Knoten wird gewählt."""
        return self._sa_tun("befehl_form", wie)

    def smartartLevel(self, k=None, richtung="erhoehen"):
        """„Level erhöhen“ (``erhoehen``) / „Level reduzieren“ (``reduzieren``): der gewählte Knoten samt Unterknoten."""
        return self._sa_tun("befehl_level", richtung)

    def smartartLevelErhoehen(self, k=None): return self.smartartLevel(k, "erhoehen")

    def smartartLevelReduzieren(self, k=None): return self.smartartLevel(k, "reduzieren")

    def smartartVerschieben(self, k=None, richtung="vor"):
        """„Vorwärts“ (``vor``) / „Rückwärts“ (``zurueck``): den Knoten unter seinen Geschwistern verschieben."""
        return self._sa_tun("befehl_verschieben", richtung)

    def smartartVorwaerts(self, k=None): return self.smartartVerschieben(k, "vor")

    def smartartRueckwaerts(self, k=None): return self.smartartVerschieben(k, "zurueck")

    def smartartAufzaehlung(self, k=None):
        """„Aufzählungszeichen einfügen“: ein Aufzählungspunkt „Text“ unter dem gewählten Knoten."""
        return self._sa_tun("befehl_aufzaehlung")

    def smartartRechtsLinks(self, k=None):
        """„Layout von rechts nach links“ umschalten (``rtl``); Zustand: ``an_smartartRechtsLinks``."""
        from lunivo_writer.editor import smartart as SA
        d = self._sa()
        if d is None:
            return self._sa_hinweis()
        ok = SA.aendern(self.ed, **({"rtl": None} if d.get("rtl") else {"rtl": True}))
        self.w.band.aktualisieren()
        return ok

    def an_smartartRechtsLinks(self) -> bool:
        return bool((self._sa() or {}).get("rtl"))

    def smartartHierarchie(self, k=None, art="standard"):
        """Organigramm-Variante: ``standard`` | ``beide`` | ``haengend_links`` | ``haengend_rechts`` (nur bei den Layouts Organigramm/Hierarchie)."""
        from lunivo_writer.editor import smartart as SA
        if self._sa() is None:
            return self._sa_hinweis()
        if not SA.kann(self.ed, "hierarchie") or art not in dict(SA.HIERARCHIEN):
            return False
        ok = SA.aendern(self.ed, hierarchie=None if art == "standard" else art)
        self.w.band.aktualisieren()
        return ok

    def smartartStil(self, k=None, nr=1):
        """Formenstil 0 bis 4 (``SA.STILE``: Flach, Einfach, Hell, Kräftig, 3D)."""
        from lunivo_writer.editor import smartart as SA
        if self._sa() is None:
            return self._sa_hinweis()
        ok = SA.aendern(self.ed, stil=max(0, min(int(nr), len(SA.STILE) - 1)))
        self.w.band.aktualisieren()
        return ok

    def smartartLayout(self, k=None, name=None):
        """Layout wechseln (Schlüssel aus ``SA.LAYOUTS``); Knoten und Farben bleiben."""
        from lunivo_writer.editor import smartart as SA
        if self._sa() is None:
            return self._sa_hinweis()
        if name not in SA.LAYOUTS:
            return False
        ok = SA.aendern(self.ed, layout=name)
        self.w.band.aktualisieren()
        return ok

    # ---- Zustände zum Ausgrauen -------------------------------------------------------------------------------------------------------------
    def _sa_kann(self, was, richtung="") -> bool:
        from lunivo_writer.editor import smartart as SA
        return bool(self.ed) and SA.kann(self.ed, was, richtung)

    def kann_smartartKnotenWaehlen(self) -> bool: return self._sa() is not None

    def kann_smartartFormEinfuegen(self) -> bool: return self._sa() is not None

    def kann_smartartAufzaehlung(self) -> bool: return self._sa_kann("knoten")

    def kann_smartartLevelErhoehen(self) -> bool: return self._sa_kann("level", "erhoehen")

    def kann_smartartLevelReduzieren(self) -> bool: return self._sa_kann("level", "reduzieren")

    def kann_smartartVorwaerts(self) -> bool: return self._sa_kann("verschieben", "vor")

    def kann_smartartRueckwaerts(self) -> bool: return self._sa_kann("verschieben", "zurueck")

    def kann_smartartHierarchie(self) -> bool: return self._sa_kann("hierarchie")

    def kann_smartartRechtsLinks(self) -> bool: return self._sa() is not None

    def kann_smartartStil(self) -> bool: return self._sa() is not None
