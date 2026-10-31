"""requirements*.txt (für ./starten-qt.sh und pip) und pyproject.toml führen dieselben Pakete; Qt wird ohne das Web-Sammelpaket installiert."""
import os
import re
import tomllib

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _zeilen(name):
    with open(os.path.join(WURZEL, name), encoding="utf-8") as fh:
        return [z.strip() for z in fh if z.strip() and not z.startswith(("#", "-r"))]


def _pyproject():
    with open(os.path.join(WURZEL, "pyproject.toml"), "rb") as fh:
        return tomllib.load(fh)["project"]


def _norm(spec):
    return re.sub(r"\s+", "", spec).lower().replace("_", "-")


def test_laufzeitpakete_gleich_in_pyproject_und_requirements():
    assert sorted(map(_norm, _zeilen("requirements.txt"))) == sorted(map(_norm, _pyproject()["dependencies"]))


def test_entwicklungspakete_gleich():
    assert sorted(map(_norm, _zeilen("requirements-dev.txt"))) == sorted(map(_norm, _pyproject()["optional-dependencies"]["dev"]))


def test_kein_web_sammelpaket_und_keine_webmodule():
    namen = {_norm(re.split(r"[<>=!~ ]", s)[0]) for s in _pyproject()["dependencies"]}
    assert "pyside6" not in namen and "pyside6-webengine" not in namen
