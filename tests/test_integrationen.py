import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from lunivo_writer.services.integrations import languagetool
from lunivo_writer.services import vorlesen


class _LT(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0)); self.rfile.read(n)
        body = json.dumps({"matches": [{"offset": 4, "length": 3, "message": "Falsch",
                                        "replacements": [{"value": "bin"}]}]}).encode()
        self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def log_message(self, *a): pass


def test_languagetool_antwort_wird_umgesetzt(monkeypatch):
    srv = HTTPServer(("127.0.0.1", 0), _LT)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    languagetool.fremd_erlauben(port)                               # ein fremder lokaler Dienst wird nur mit ausdrücklicher Erlaubnis benutzt
    try:
        funde = languagetool.pruefe("Ich bim da")       # Fake-Server — echtes LanguageTool ist hier nicht getestet
    finally:
        languagetool.fremd_erlauben(None)
        srv.shutdown()
    assert funde[0]["alt"] == "bim" and funde[0]["neu"] == "bin" and "LanguageTool" in funde[0]["grund"]


def test_languagetool_fehlt_ist_ein_klarer_fehler(monkeypatch, tmp_path):
    monkeypatch.setattr(languagetool, "ordner", lambda: str(tmp_path))
    monkeypatch.setattr(languagetool, "laeuft", lambda port=8081: False)
    with pytest.raises(languagetool.LanguageToolFehler):
        languagetool.starten()


def test_languagetool_fremder_dienst_wird_nicht_benutzt(monkeypatch, tmp_path):
    """Ein Dienst, der zufällig auf dem Port lauscht, bekommt keinen Text, solange der Benutzer ihn nicht erlaubt hat."""
    srv = HTTPServer(("127.0.0.1", 0), _LT)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    monkeypatch.setattr(languagetool, "PORT", srv.server_address[1])
    monkeypatch.setattr(languagetool, "ordner", lambda: str(tmp_path))          # kein eigenes Jar
    try:
        assert not languagetool.verfuegbar() and languagetool.status()["art"] == "keiner"
        with pytest.raises(languagetool.LanguageToolFehler):
            languagetool.pruefe("Ich bim da")
        languagetool.fremd_erlauben(srv.server_address[1])
        assert languagetool.verfuegbar() and languagetool.status()["art"] == "fremd"
    finally:
        languagetool.fremd_erlauben(None)
        srv.shutdown()


def test_languagetool_eigener_prozess_auf_freiem_port(monkeypatch, tmp_path):
    """Der eigene Prozess bekommt einen vom System gewählten Port, wird verwaltet und beim Beenden entsorgt."""
    import sys
    skript = tmp_path / "lt.py"
    skript.write_text("import sys\nfrom http.server import BaseHTTPRequestHandler, HTTPServer\n"
                      "class H(BaseHTTPRequestHandler):\n"
                      "    def do_POST(s):\n"
                      "        s.rfile.read(int(s.headers.get('Content-Length', 0))); b = b'{\"matches\": []}'\n"
                      "        s.send_response(200); s.send_header('Content-Length', str(len(b))); s.end_headers(); s.wfile.write(b)\n"
                      "    def log_message(s, *a): pass\n"
                      "HTTPServer(('127.0.0.1', int(sys.argv[-1])), H).serve_forever()\n", encoding="utf-8")
    (tmp_path / "languagetool-server.jar").write_bytes(b"x")
    monkeypatch.setattr(languagetool, "ordner", lambda: str(tmp_path))
    monkeypatch.setattr(languagetool.shutil, "which", lambda n: "/usr/bin/java")
    echt = languagetool.prozess.starten
    monkeypatch.setattr(languagetool.prozess, "starten", lambda args, **kw: echt([sys.executable, str(skript), args[-1]], **kw))
    try:
        assert languagetool.pruefe("Hallo") == []
        st = languagetool.status()
        assert st["art"] == "eigen" and st["port"] != 8081 and st["pid"]
        proc = languagetool._lauf["proc"]
        assert languagetool.starten() == st["port"]                  # kein zweiter Prozess
    finally:
        languagetool.beenden()
    assert proc.poll() is not None and languagetool.status()["art"] == "keiner"


def test_vorlesen_ohne_dienst_meldet_klar(monkeypatch):
    monkeypatch.setattr(vorlesen, "verfuegbar", lambda: False)
    with pytest.raises(vorlesen.VorlesenFehler):
        vorlesen.lies_vor("Hallo")


def test_vorlesen_spd_befehl(monkeypatch):
    gesehen = {}
    monkeypatch.setattr(vorlesen, "verfuegbar", lambda: True)
    monkeypatch.setattr(vorlesen, "piper_da", lambda: False)
    monkeypatch.setattr(vorlesen, "beenden", lambda: None)

    class P:
        def poll(self): return 0
    monkeypatch.setattr(vorlesen.subprocess, "Popen", lambda cmd, **k: gesehen.setdefault("cmd", cmd) and P())
    assert vorlesen.lies_vor("Hallo Welt", "", 20)
    assert gesehen["cmd"][:2] == ["spd-say", "-l"] and "20" in gesehen["cmd"] and gesehen["cmd"][-1] == "Hallo Welt"
    assert vorlesen.lies_vor("   ") is False


def test_integrationsverzeichnis_sagt_wohin_daten_gehen(tmp_path, monkeypatch):
    from lunivo_writer.ai import ki as K
    from lunivo_writer.services.integrations import verzeichnis
    monkeypatch.setattr(languagetool, "ordner", lambda: str(tmp_path))
    ki = K.KI(K.KIKonfig(str(tmp_path / "k.json")))
    ki.k.setze("apiKey", "sk-test")
    u = {e["schluessel"]: e for e in verzeichnis.uebersicht({"ki": ki})}
    assert set(u) == {"languagetool", "ki", "mcp"}
    assert u["languagetool"]["zustand"] == "nicht eingerichtet"
    assert u["ki"]["zustand"] == "ohne Zustimmung gesperrt" and "Internet" in u["ki"]["wohin"]
    ki.k.einwilligung_geben("Anthropic (Claude)", "auszug")
    assert verzeichnis.uebersicht({"ki": ki})[1]["zustand"] == "Zustimmung liegt vor"
    assert verzeichnis.uebersicht({})[1]["zustand"] == "nicht verbunden"


def test_languagetool_nicht_erreichbar_ist_ein_klarer_fehler(monkeypatch):
    """Ein erlaubter lokaler Dienst, der nicht antwortet, führt zu LanguageToolFehler statt zu einem Absturz oder Hängen."""
    import socket
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]               # Port reserviert, aber niemand hört zu
    monkeypatch.setattr(languagetool, "laeuft", lambda p=None: True)         # der Dienst „läuft“ laut Prüfung, antwortet aber nicht
    languagetool.fremd_erlauben(port)
    try:
        with pytest.raises(languagetool.LanguageToolFehler, match="antwortet nicht"):
            languagetool.pruefe("Text")
    finally:
        languagetool.fremd_erlauben(None)
