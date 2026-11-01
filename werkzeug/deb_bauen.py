#!/usr/bin/env python3
"""Baut genau eine .deb:  python3 werkzeug/deb_bauen.py [--ausgabe VERZEICHNIS]

Anwendung unter /opt/stevie-empire/lunivo-office/, Starter /usr/share/applications/stevie-lunivo-office.desktop,
Symlink /usr/bin/lunivo-office. Pakete kommen aus requirements.txt (pip --target), Benutzerdaten liegen nur in XDG-Verzeichnissen.
Braucht beim Bauen: python3, pip, dpkg-deb und Netz (oder einen pip-Cache)."""
import argparse
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
ZIEL = "/opt/stevie-empire/lunivo-office"
ICON_QUELLE = WURZEL / "assets/symbole/varianten/Abstrakt/icon-256.png"

STARTER = f"""#!/bin/sh
# Lunivo Office — startet die mitgelieferte Anwendung ohne Systempakete außer Python 3.
export PYTHONPATH="{ZIEL}/lib:{ZIEL}/app${{PYTHONPATH:+:$PYTHONPATH}}"
exec python3 -m lunivo_writer "$@"
"""

DESKTOP = f"""[Desktop Entry]
Type=Application
Name=Lunivo Office
Comment=Textverarbeitung
Exec=/usr/bin/lunivo-office %F
Icon={ZIEL}/lunivo-office.png
Terminal=false
StartupWMClass=Lunivo Writer
Categories=Office;WordProcessor;
MimeType=application/vnd.openxmlformats-officedocument.wordprocessingml.document;text/plain;
"""


def bauen(ausgabe: Path) -> Path:
    version = tomllib.loads((WURZEL / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    ausgabe.mkdir(parents=True, exist_ok=True)
    wurzel = ausgabe / "deb-staging"
    shutil.rmtree(wurzel, ignore_errors=True)
    app = wurzel / ZIEL.lstrip("/")
    app.mkdir(parents=True)

    shutil.copytree(WURZEL / "src/lunivo_writer", app / "app/lunivo_writer",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "--no-compile", "--target", str(app / "lib"),
                    "-r", str(WURZEL / "requirements.txt")], check=True)
    if ICON_QUELLE.exists():
        shutil.copy2(ICON_QUELLE, app / "lunivo-office.png")

    (wurzel / "usr/bin").mkdir(parents=True)
    starter = app / "lunivo-office"
    starter.write_text(STARTER, encoding="utf-8")
    starter.chmod(0o755)
    (wurzel / "usr/bin/lunivo-office").symlink_to(f"{ZIEL}/lunivo-office")

    (wurzel / "usr/share/applications").mkdir(parents=True)
    (wurzel / "usr/share/applications/stevie-lunivo-office.desktop").write_text(DESKTOP, encoding="utf-8")

    (wurzel / "DEBIAN").mkdir()
    (wurzel / "DEBIAN/control").write_text(
        f"Package: stevie-lunivo-office\nVersion: {version}\nSection: editors\nPriority: optional\nArchitecture: amd64\n"
        "Depends: python3 (>= 3.10), libgl1, libxkbcommon-x11-0, libxcb-cursor0\n"
        "Maintainer: Kay Siebke <kaysiebke@gmail.com>\n"
        "Description: Lunivo Office - native Textverarbeitung\n Python 3 mit PySide6 (Qt Widgets), eigenstaendig, ohne Webtechnik.\n",
        encoding="utf-8")
    ziel = ausgabe / f"stevie-lunivo-office_{version}_amd64.deb"
    subprocess.run(["dpkg-deb", "--root-owner-group", "--build", str(wurzel), str(ziel)], check=True)
    shutil.rmtree(wurzel)
    return ziel


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ausgabe", default=str(WURZEL / "dist"))
    print(bauen(Path(p.parse_args().ausgabe)))
