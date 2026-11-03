"""MCP-Server als Vertrauensgrenze: Größen, Nachrichtenzahl, Laufzeit, Abbruch, Umgebung, Aufräumen, Einstufung."""
import os
import sys
import textwrap

import pytest

from lunivo_writer.ai import mcp as M

KOPF = textwrap.dedent('''
    import json, sys, os, time
    def senden(i, r): print(json.dumps({"jsonrpc": "2.0", "id": i, "result": r}), flush=True)
    for zeile in sys.stdin:
        m = json.loads(zeile)
        if "id" not in m: continue
        if m["method"] == "initialize": senden(m["id"], {}); continue
''')


def server(tmp_path, koerper):
    p = tmp_path / "s.py"
    p.write_text(KOPF + textwrap.indent(textwrap.dedent(koerper), "    "), encoding="utf-8")
    return f"{sys.executable} {p}"


def test_normale_antwort_und_kuerzung(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "MAX_ERGEBNIS", 100)
    c = M.McpClient(server(tmp_path, 'senden(m["id"], {"content": [{"type": "text", "text": "x" * 1000}]})'))
    try:
        t = c.aufrufen("a", {})
    finally:
        c.schliessen()
    assert t.startswith("x" * 100) and "gekürzt" in t and len(t) < 200


def test_zu_grosse_nachricht_beendet_den_server(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "MAX_ZEILE", 1000)
    c = M.McpClient(server(tmp_path, 'senden(m["id"], {"content": [{"type": "text", "text": "x" * 5000}]})'))
    try:
        with pytest.raises(M.McpFehler, match="zu große"):
            c.aufrufen("a", {})
        assert c.p.wait(timeout=5) is not None
    finally:
        c.schliessen()


def test_nachrichtenflut_wird_begrenzt(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "MAX_NACHRICHTEN", 20)
    c = M.McpClient(server(tmp_path, 'for i in range(5000): senden(999, {})\nsenden(m["id"], {})'))
    try:
        with pytest.raises(M.McpFehler, match="zu viele"):
            c.aufrufen("a", {})
    finally:
        c.schliessen()


def test_server_stirbt_mitten_im_aufruf(tmp_path):
    c = M.McpClient(server(tmp_path, "sys.exit(0)"))
    try:
        with pytest.raises(M.McpFehler, match="beendet"):
            c.aufrufen("a", {})
    finally:
        c.schliessen()


def test_haengender_server_laufzeit(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "ZEIT", 0.5)
    c = M.McpClient(server(tmp_path, "time.sleep(60)"))
    try:
        with pytest.raises(M.McpFehler, match="zu lange"):
            c.aufrufen("a", {})
    finally:
        c.schliessen()
    assert c.p.poll() is not None                         # nach dem Schließen ist der Prozess weg


def test_lebensdauer_begrenzt(tmp_path, monkeypatch):
    c = M.McpClient(server(tmp_path, 'senden(m["id"], {})'))
    try:
        c.ende = 0
        with pytest.raises(M.McpFehler, match="zu lange"):
            c.aufrufen("a", {})
    finally:
        c.schliessen()


def test_zugangsdaten_gelangen_nicht_in_den_server(tmp_path, monkeypatch):
    monkeypatch.setenv("MEIN_API_KEY", "geheim123")
    monkeypatch.setenv("HARMLOS", "ok")
    c = M.McpClient(server(tmp_path, 'senden(m["id"], {"content": [{"type": "text", "text": os.environ.get("MEIN_API_KEY", "-") + "|" + os.environ.get("HARMLOS", "-")}]})'))
    try:
        assert c.aufrufen("a", {}) == "-|ok"
    finally:
        c.schliessen()


def test_schliessen_beendet_auch_kindprozesse(tmp_path):
    pidd = tmp_path / "kind.pid"
    code = f'import subprocess\nk = subprocess.Popen(["sleep", "60"]); open({str(pidd)!r}, "w").write(str(k.pid))\nsenden(m["id"], {{}})'
    c = M.McpClient(server(tmp_path, code))
    try:
        c.werkzeuge()
    finally:
        c.schliessen()
    pid = int(pidd.read_text())
    import time
    for _ in range(40):
        try:
            os.kill(pid, 0)
        except OSError:
            break
        time.sleep(0.1)
    else:
        pytest.fail("Kindprozess läuft noch")


def test_unbekannter_befehl_und_leerer_befehl():
    with pytest.raises(M.McpFehler):
        M.McpClient("gibt-es-nicht-xyz")
    with pytest.raises(M.McpFehler):
        M.McpClient("   ")


def test_art_des_werkzeugs():
    f = M.art_des_werkzeugs
    assert f({"name": "delete_file"}) == "löschen" and f({"name": "x", "annotations": {"destructiveHint": True}}) == "löschen"
    assert f({"name": "fetch_page"}) == "netzwerk" and f({"name": "x", "annotations": {"openWorldHint": True}}) == "netzwerk"
    assert f({"name": "write_file"}) == "schreiben" and f({"name": "x", "annotations": {"readOnlyHint": False}}) == "schreiben"
    assert f({"name": "list_dir"}) == "lesen" and f({"name": "x", "annotations": {"readOnlyHint": True}}) == "lesen"
    assert f({"name": "frobnicate"}) == "unbekannt"
