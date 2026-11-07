"""Alte und neue Importpfade für den Diagrammbereich verweisen auf dieselben Module."""

from importlib import import_module

from lunivo_writer import editor


def test_diagramm_importpfade_teilen_modulzustand():
    for name in ("diagramm", "diagramm_format", "diagramm_geo", "diagramm_kreis", "diagramm_teile", "diagramm_zusatz"):
        alt = import_module(f"lunivo_writer.editor.{name}")
        neu = import_module(f"lunivo_writer.editor.diagramme.{name}")
        assert alt is neu
        assert getattr(editor, name) is neu

    alt = import_module("lunivo_writer.editor.diagramm_format")
    neu = import_module("lunivo_writer.editor.diagramme.diagramm_format")
    vorher = alt.OBJEKT_DREH
    alt.OBJEKT_DREH = 15.0
    try:
        assert neu.OBJEKT_DREH == 15.0
    finally:
        alt.OBJEKT_DREH = vorher
