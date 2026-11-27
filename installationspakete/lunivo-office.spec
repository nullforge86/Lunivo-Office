# PyInstaller-Spezifikation für Lunivo Office (gemeinsam für Linux, Windows, macOS).
# Aufruf aus dem Projektwurzelordner:  pyinstaller installationspakete/lunivo-office.spec --noconfirm
# Einstieg ist main.py (wie beim Start aus dem Quellcode); Ressourcenpfade siehe src/system/pfade/ressourcen_pfade.py
# (gepackt: WURZEL = sys._MEIPASS, ASSETS = WURZEL/ressourcen, Paketdaten = WURZEL/system/ressourcen,
#  PROGRAMMORDNER = Ordner über WURZEL; dort liegen mitgelieferte Zusatzpakete wie argos/).
import os
import re
import sys

from PyInstaller.utils.hooks import collect_all, collect_submodules

WURZEL = os.path.abspath(os.getcwd())
SCHICHTEN = ("core", "framework", "vcl", "writer", "filter", "system")     # die Pakete unter src/
sys.path.insert(0, os.path.join(WURZEL, "src"))                            # damit collect_submodules die Schichten findet
EIGENE_MODULE = [m for schicht in SCHICHTEN for m in collect_submodules(schicht)]   # auch träge (per Namen) geladene Module
with open(os.path.join(WURZEL, "pyproject.toml"), encoding="utf-8") as f:
    VERSION = re.search(r'^version\s*=\s*"([^"]+)"', f.read(), re.M).group(1)

ICON_DIR = os.path.join(WURZEL, "erstellung", "icons")           # von installationspakete/icons_erzeugen.py angelegt
if sys.platform == "win32":
    ICON = os.path.join(ICON_DIR, "lunivo-office.ico")
elif sys.platform == "darwin":
    ICON = os.path.join(ICON_DIR, "lunivo-office.icns")
else:
    ICON = None

# Offline-Übersetzung (Argos): optional, wird eingebaut, wenn argostranslate in der Bauumgebung installiert ist.
ARGOS_DATEN, ARGOS_BIN, ARGOS_HIDDEN = [], [], []
for _paket in ("argostranslate", "ctranslate2", "sentencepiece", "stanza", "minisbd", "spacy"):
    try:
        _d, _b, _h = collect_all(_paket)
    except Exception:
        continue
    ARGOS_DATEN += _d; ARGOS_BIN += _b; ARGOS_HIDDEN += _h

a = Analysis(
    [os.path.join(WURZEL, "main.py")],
    binaries=ARGOS_BIN,
    pathex=[os.path.join(WURZEL, "src")],
    datas=[
        (os.path.join(WURZEL, "ressourcen"), "ressourcen"),
        (os.path.join(WURZEL, "src", "system", "ressourcen"), os.path.join("system", "ressourcen")),
    ] + ARGOS_DATEN,
    hiddenimports=EIGENE_MODULE + ["lxml.etree"] + ARGOS_HIDDEN,
    excludes=["tkinter", "pytest", "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.Qt3DCore",
              "PySide6.QtQuick", "PySide6.QtQml", "PySide6.QtMultimedia"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="lunivo-office", console=False, icon=ICON)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="lunivo-office")

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Lunivo Office.app",
        icon=ICON,
        bundle_identifier="de.lunivo.office",
        version=VERSION,
        info_plist={
            "CFBundleName": "Lunivo Office",
            "CFBundleDisplayName": "Lunivo Office",
            "CFBundleShortVersionString": VERSION,
            "CFBundleVersion": VERSION,
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "11.0",
            "CFBundleDocumentTypes": [{
                "CFBundleTypeName": "Word-Dokument", "CFBundleTypeRole": "Editor",
                "LSItemContentTypes": ["org.openxmlformats.wordprocessingml.document"],
            }],
        },
    )
