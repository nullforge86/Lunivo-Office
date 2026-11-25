from __future__ import annotations
from core.objekte.anordnung.image_object import ImageObject
from core.objekte.anordnung.shape_object import ShapeObject


P_BILDANKER = "user:1048623"            # Absatzeigenschaft mit den frei positionierten Bildern (JSON-Liste); entspricht ``editor/dokument/zusatz.B_BILDANKER``


Objekt = ImageObject | ShapeObject
