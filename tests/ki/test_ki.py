import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from lunivo_writer.ki import ki as K


def konfig(tmp_path, **kw):
    k = K.KIKonfig(str(tmp_path / "ki.json"))
    k.d["einwilligungen"] = [{"anbieter": "Anthropic (Claude)", "umfang": "dokument", "seit": "2026-11-04"}]       # die Tests prüfen die Anbindung, nicht die Rückfrage
    k.d.update(kw)
    return k


class Handler(BaseHTTPRequestHandler):
    antwort = {}
    gesehen = []
    status = 200

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        Handler.gesehen.append((self.path, {k.lower(): v for k, v in self.headers.items()}, json.loads(self.rfile.read(n))))
        if Handler.gesehen[-1][2].get("stream") and "teile" in Handler.antwort:
            body = b"".join(json.dumps(t).encode() + b"\n" for t in Handler.antwort["teile"])
        else:
            body = json.dumps(Handler.antwort).encode()
        self.send_response(Handler.status); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        body = json.dumps({"models": [{"name": "b:1"}, {"name": "a:2"}]}).encode()
        self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def log_message(self, *a): pass


@pytest.fixture
def server():
    srv = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    Handler.gesehen = []; Handler.status = 200
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def test_schluesseldatei_ist_privat(tmp_path):
    k = konfig(tmp_path); k.setze("apiKey", "geheim")
    assert oct(os.stat(k.pfad).st_mode & 0o777) == "0o600"
    assert K.KIKonfig(k.pfad)["apiKey"] == "geheim"


def test_anweisung_enthaelt_empfaenger_zettel_gedaechtnis(tmp_path):
    k = konfig(tmp_path, empfaenger="Amt", zettel="Es geht um eine Kürzung.")
    a = K.anweisung_korrektur(k, {"woerter": {"vieleicht": "vielleicht"}, "inRuhe": {"meyr": True}})
    assert "Behörde" in a and "Kürzung" in a and "vieleicht statt vielleicht" in a and "meyr" in a


def test_ollama_anfrage(tmp_path, server, monkeypatch):
    monkeypatch.setattr(K, "OLLAMA_URL", server)
    Handler.antwort = {"message": {"content": "<think>grübel</think>Hallo Welt"}}
    ki = K.KI(konfig(tmp_path, modell="ollama:qwen3:8b"))
    r = ki.korrigieren("hallo welt")
    assert r["text"] == "Hallo Welt"
    pfad, _kopf, body = Handler.gesehen[0]
    assert pfad == "/api/chat" and body["model"] == "qwen3:8b" and body["messages"][0]["role"] == "system"
    assert ki.schickt_nach_aussen() is None                      # lokal: nichts verlässt den Rechner


def test_ollama_tempo_optionen(tmp_path, server, monkeypatch):
    monkeypatch.setattr(K, "OLLAMA_URL", server)
    Handler.antwort = {"message": {"content": "Hallo"}}
    ki = K.KI(konfig(tmp_path, modell="ollama:qwen3:8b"))
    assert ki.korrigieren("kurz")["text"] == "Hallo"
    body = Handler.gesehen[0][2]
    assert body["keep_alive"] == "30m" and body["stream"] is False
    assert body["options"]["num_ctx"] == 8192 and 512 <= body["options"]["num_predict"] <= 2048
    assert "num_thread" not in body["options"]                    # Vorgabe: automatisch
    assert K.num_thread_begrenzen(0) == 0 and K.num_thread_begrenzen("x") == 0 and K.num_thread_begrenzen(999) == (os.cpu_count() or 999)
    ki.k.chat_setzen(numThread=2)
    ki.korrigieren("kurz")
    assert Handler.gesehen[1][2]["options"]["num_thread"] == min(2, os.cpu_count() or 2)
    assert K.num_ctx_fuer(4096, 30000, 1024) == 16384            # langer Verlauf wird nie abgeschnitten
    assert K.num_predict_fuer(0, True, False) == 1024 and K.num_predict_fuer(0, True, False, 300) == 300


def test_ollama_streaming_und_abbruch(tmp_path, server, monkeypatch):
    monkeypatch.setattr(K, "OLLAMA_URL", server)
    Handler.antwort = {"teile": [{"message": {"content": "Hal"}}, {"message": {"content": "lo"}},
                                 {"message": {"content": ""}, "done": True, "done_reason": "length"}]}
    ki = K.KI(konfig(tmp_path, modell="ollama:qwen3:8b"))
    teile = []
    r = ki.chat([{"rolle": "mensch", "text": "hi"}], strom=teile.append)
    assert Handler.gesehen[0][2]["stream"] is True and teile and teile[-1] == "Hallo"
    assert r["text"] == "Hallo" and "gekürzt" in r["kuerzung"]      # der Hinweis liegt neben dem Antworttext, nicht darin
    ev = threading.Event(); ev.set()
    assert "Abgebrochen" in ki.chat([{"rolle": "mensch", "text": "hi"}], strom=teile.append, abbruch=ev)["fehler"]


def test_claude_anfrage_schluessel_im_kopf_und_kosten(tmp_path, server, monkeypatch):
    monkeypatch.setattr(K, "CLAUDE_URL", server + "/v1/messages")
    Handler.antwort = {"content": [{"type": "text", "text": "Fertig"}], "model": "claude-sonnet-5",
                       "usage": {"input_tokens": 1000000, "output_tokens": 0}}
    k = konfig(tmp_path, modell="claude-sonnet-5", apiKey="sk-test")
    ki = K.KI(k)
    r = ki.zusammenfassen("langer text")
    assert r["text"] == "Fertig" and abs(r["cent"] - 300) < 1e-6
    assert Handler.gesehen[0][1]["x-api-key"] == "sk-test" and k["kosten"] > 0
    assert ki.schickt_nach_aussen() == "Anthropic (Claude)"


def test_claude_fehler_werden_uebersetzt(tmp_path, server, monkeypatch):
    monkeypatch.setattr(K, "CLAUDE_URL", server + "/v1/messages")
    Handler.status = 401; Handler.antwort = {"error": {"message": "invalid"}}
    r = K.KI(konfig(tmp_path, modell="claude-opus-5", apiKey="x")).korrigieren("a")
    assert "Schlüssel wird abgelehnt" in r["fehler"]
    Handler.status = 400; Handler.antwort = {"error": {"message": "Your credit balance is too low"}}
    assert "Guthaben" in K.KI(konfig(tmp_path, modell="claude-opus-5", apiKey="x")).korrigieren("a")["fehler"]


def test_ohne_schluessel_kein_netzzugriff(tmp_path):
    ki = K.KI(konfig(tmp_path, modell="claude-opus-5", apiKey=""))
    assert not ki.verfuegbar() and "kein Schlüssel" in ki.korrigieren("a")["fehler"]


def test_eigener_anbieter(tmp_path, server):
    k = konfig(tmp_path)
    a = k.anbieter_hinzufuegen("Test", server, "tok", "m1"); k.d["modell"] = "eigen:" + a["id"]
    Handler.antwort = {"choices": [{"message": {"content": "ok"}}]}
    ki = K.KI(k)
    assert ki.zusammenfassen("x")["text"] == "ok"
    assert Handler.gesehen[0][0] == "/chat/completions" and Handler.gesehen[0][1]["authorization"] == "Bearer tok"
    assert ki.schickt_nach_aussen() is None                       # localhost zählt als lokal


def test_vorschlaege_nur_zeichengenaue(tmp_path, server, monkeypatch):
    monkeypatch.setattr(K, "OLLAMA_URL", server)
    text = "Das ist ein sehr umständlich formulierter Satz. Kurz."
    Handler.antwort = {"message": {"content": json.dumps({"vorschlaege": [
        {"alt": "Das ist ein sehr umständlich formulierter Satz.", "neu": "Der Satz ist umständlich.", "grund": "kürzer"},
        {"alt": "Gibt es nicht im Text.", "neu": "x", "grund": "y"}]})}}
    r = K.KI(konfig(tmp_path, modell="ollama:m")).vorschlaege(text)
    assert len(r["vorschlaege"]) == 1


def test_vorschlaege_konfidenz_gespeichert_und_sortiert(tmp_path, server, monkeypatch):
    monkeypatch.setattr(K, "OLLAMA_URL", server)
    text = "Erster langer Satz hier. Zweiter langer Satz da. Dritter."
    Handler.antwort = {"message": {"content": json.dumps({"vorschlaege": [
        {"alt": "Erster langer Satz hier.", "neu": "Erster Satz.", "grund": "kürzer", "konfidenz": 0.3},
        {"alt": "Zweiter langer Satz da.", "neu": "Zweiter Satz.", "grund": "kürzer", "konfidenz": 0.9},
        {"alt": "Dritter.", "neu": "3.", "grund": "kürzer", "konfidenz": "viel"}]})}}
    r = K.KI(konfig(tmp_path, modell="ollama:m")).vorschlaege(text)["vorschlaege"]
    assert [v["konfidenz"] for v in r] == [0.9, 0.5, 0.3]            # sortiert; Unsinn wird 0,5
    assert all(v["quelle"] == "ki" for v in r)
    from lunivo_writer.dienste.gelernt import Gelernt
    g = Gelernt(str(tmp_path / "g.json"))
    g.ki_vermerken(r[0], True); g.ki_vermerken(r[0], False); g.ki_vermerken(r[0], True)
    assert abs(g.ki_trefferquote(9) - 2 / 3) < 1e-9 and g.ki_trefferquote(0) is None
    assert Gelernt(str(tmp_path / "g.json")).daten["ki"]["9"] == {"angenommen": 2, "abgelehnt": 1}   # überlebt Neustart


def test_diff_ersetzt_nur_geaendertes():
    alt = "Wir hat keine Zahlung.\nDanke"
    neu = "Wir haben keine Zahlung.\nDanke"
    ops, ganz, n = K.ersetze_ergebnis(alt, neu)
    assert not ganz and n == 1
    text = alt
    for von, bis, t in ops:                                       # von hinten nach vorn
        text = text[:von] + t + text[bis:]
    assert text == neu and len(ops) == 1 and ops[0][2] == "haben"


def test_diff_ungleiche_zeilen_tauscht_ganz():
    assert K.ersetze_ergebnis("a\nb", "a")[1] is True


def test_ollama_modelle(server, monkeypatch, tmp_path):
    monkeypatch.setattr(K, "OLLAMA_URL", server)
    assert K.KI(konfig(tmp_path)).ollama_modelle() == ["a:2", "b:1"]


def test_bildgenerierung_und_anbieter(tmp_path):
    """Anbieter mit „Bilder“, Aufgabe zuweisen, Bild von einem gefälschten OpenAI-Server holen."""
    import base64, json, threading
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from PySide6.QtGui import QImage, QColor
    from PySide6.QtCore import QBuffer, QIODevice
    img = QImage(8, 8, QImage.Format_RGB32); img.fill(QColor("red"))
    buf = QBuffer(); buf.open(QIODevice.WriteOnly); img.save(buf, "PNG")
    png = base64.b64encode(bytes(buf.data())).decode()
    gesehen = {}

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            gesehen["pfad"] = self.path
            gesehen["body"] = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            body = json.dumps({"data": [{"b64_json": png}]}).encode()
            self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        def do_GET(self):
            body = json.dumps({"data": [{"id": "bild-1"}, {"id": "text-1"}]}).encode()
            self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        def log_message(self, *a): pass
    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_port}/v1"
    k = K.KIKonfig(str(tmp_path / "ki.json"))
    ki = K.KI(k)
    assert "fehler" in ki.bild_erzeugen("ein Hund")                    # ohne Zuweisung
    assert K.anbieter_modelle(url) == ["bild-1", "text-1"]
    a = k.anbieter_hinzufuegen("Bilder", url, "tok", "bild-1", ["text", "bilder", "unsinn"])
    assert a["verwendungFuer"] == ["text", "bilder"]
    assert [m["id"] for m in k.alle_modelle() if "bilder" in m["verwendungFuer"]] == ["eigen:" + a["id"]]
    k.aufgabe_setzen("bildgenerierung", "eigen:" + a["id"])
    r = ki.bild_erzeugen("ein Hund")
    assert QImage.fromData(r["bild"]).width() == 8
    assert gesehen["pfad"] == "/v1/images/generations" and gesehen["body"]["prompt"] == "ein Hund"
    k.anbieter_entfernen(a["id"])
    assert "bildgenerierung" not in k["aufgaben"]


# ---- Chat-Zustand (ohne Oberfläche)
def test_chat_phasen_und_wiederholen():
    from lunivo_writer.ki.chat_modell import ChatModell
    m = ChatModell()
    assert m.phase == "leer"
    k = m.anfrage("Hallo Welt")
    assert m.phase == "laufend" and m.titel == "Hallo Welt"
    assert m.fehler(k, "Es hat nicht geklappt: x") and m.phase == "fehler"
    assert m.nachrichten[-1]["fehler"]["text"].startswith("Es hat") and m.verlauf() == [{"rolle": "mensch", "text": "Hallo Welt"}]
    assert m.wiederholen() == "Hallo Welt" and m.nachrichten == []
    k = m.anfrage("Hallo Welt")
    assert m.antwort(k, "Hi", 3) and m.phase == "bereit"


def test_chat_neues_gespraech_verwirft_alte_antwort():
    from lunivo_writer.ki.chat_modell import ChatModell
    m = ChatModell()
    k = m.anfrage("Frage")
    m.neues_gespraech()
    assert not m.antwort(k, "zu spät") and m.phase == "leer" and m.nachrichten == []
    assert m.gespraeche[0]["titel"] == "Frage"
    m.aktion("Kürzen", "kurz")
    assert [n["rolle"] for n in m.verlauf()] == ["mensch", "ki"]


def test_chat_vorschlaege_je_zustand():
    from lunivo_writer.ki.chat_vorschlaege import chat_vorschlaege
    titel = ["Dokument zusammenfassen", "Text umschreiben", "Text vereinfachen", "Inhalt erweitern", "Dokument Korrektur lesen",
             "Zusammenfassung erstellen", "Text übersetzen", "Inhaltsverzeichnis erstellen", "Titel vorschlagen", "Kernpunkte hervorheben"]
    for a, l in ((True, False), (False, False), (False, True)):          # Markierung, Dokument, leeres Dokument: immer dieselben zehn in dieser Reihenfolge
        v = chat_vorschlaege(a, l)
        assert [e["titel"] for e in v] == titel and all(e["anweisung"] and e["hinweis"] for e in v)
        assert all(e["aktiv"] is (not l) for e in v)                      # leer: gesperrt statt versteckt


# ---- Denktiefe, Bildanhang, Bildprüfung
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20


def _bild(tmp_path, name="a.png", inhalt=PNG):
    p = tmp_path / name
    p.write_bytes(inhalt)
    return str(p)


def test_bild_pruefen_nach_inhalt_und_groesse(tmp_path):
    from lunivo_writer.ki import modellfaehigkeit as MF
    assert MF.bild_pruefen(_bild(tmp_path))["typ"] == "image/png"
    assert MF.bild_pruefen(_bild(tmp_path, "x.png", b"\xff\xd8\xff" + b"0" * 20))["typ"] == "image/jpeg"     # Endung lügt
    assert "nicht unterstützt" in MF.bild_pruefen(_bild(tmp_path, "t.png", b"GIF89a" + b"0" * 20))["fehler"]
    assert "gibt es nicht" in MF.bild_pruefen(str(tmp_path / "nix.png"))["fehler"]
    assert "zu groß" in MF.bild_pruefen(_bild(tmp_path, "g.png", PNG + b"0" * MF.BILD_MAX_BYTES))["fehler"]


def test_denk_stufen_je_anbieter(tmp_path, server, monkeypatch):
    monkeypatch.setattr(K, "CLAUDE_URL", server + "/v1/messages")
    monkeypatch.setattr(K, "OLLAMA_URL", server)
    Handler.antwort = {"content": [{"type": "text", "text": "ok"}]}
    ki = K.KI(konfig(tmp_path, modell="claude-sonnet-5", apiKey="sk"))
    ki.anfrage("s", "t", optionen={"denktiefe": "hoch"})
    ki.anfrage("s", "t", optionen={"denktiefe": "aus"})
    ki.anfrage("s", "t")
    hoch, aus, auto = (g[2] for g in Handler.gesehen)
    assert hoch["output_config"]["effort"] == "high" and hoch["thinking"] == {"type": "adaptive"}
    assert "thinking" not in aus and "output_config" not in aus
    assert auto["output_config"]["effort"] == "low"
    Handler.gesehen = []
    ki.anfrage("s", "t", modell="claude-haiku-4-5", optionen={"denktiefe": "hoch"})
    assert "thinking" not in Handler.gesehen[0][2]
    Handler.gesehen = []
    Handler.antwort = {"message": {"content": "ok"}}
    ki.anfrage("s", "t", modell="ollama:q", optionen={"denktiefe": "mittel"})
    ki.anfrage("s", "t", modell="ollama:q")
    assert Handler.gesehen[0][2]["think"] == "medium" and Handler.gesehen[1][2]["think"] is False
    Handler.gesehen = []
    Handler.antwort = {"choices": [{"message": {"content": "ok"}}]}
    a = ki.k.anbieter_hinzufuegen("X", server, "", "m")
    ki.anfrage("s", "t", modell="eigen:" + a["id"], optionen={"denktiefe": "niedrig"})
    ki.anfrage("s", "t", modell="eigen:" + a["id"])
    assert Handler.gesehen[0][2]["reasoning_effort"] == "low" and "reasoning_effort" not in Handler.gesehen[1][2]


def test_denk_eigen_rueckfall_bei_400(tmp_path, server):
    Handler.antwort = {"choices": [{"message": {"content": "ok"}}]}
    ki = K.KI(konfig(tmp_path))
    a = ki.k.anbieter_hinzufuegen("X", server, "", "m")
    Handler.status = 400
    r = ki.anfrage("s", "t", modell="eigen:" + a["id"], optionen={"denktiefe": "hoch"})
    assert "400" in r["fehler"] and len(Handler.gesehen) == 2 and "reasoning_effort" not in Handler.gesehen[1][2]


def test_bild_format_je_anbieter(tmp_path, server, monkeypatch):
    monkeypatch.setattr(K, "CLAUDE_URL", server + "/v1/messages")
    monkeypatch.setattr(K, "OLLAMA_URL", server)
    pfad = _bild(tmp_path)
    verlauf = [{"rolle": "mensch", "text": "alt", "bilder": [{"pfad": pfad}]}, {"rolle": "ki", "text": "ja"},
               {"rolle": "mensch", "text": "neu", "bilder": [{"pfad": pfad}]}]
    # Claude: nur das letzte Bild, vor dem Text; frühere mit Platzhalter
    Handler.antwort = {"content": [{"type": "text", "text": "ok"}]}
    ki = K.KI(konfig(tmp_path, modell="claude-sonnet-5", apiKey="sk"))
    ki.k.einwilligung_geben("Anthropic (Claude)", "bild")
    assert ki.chat(verlauf)["text"] == "ok"
    m = Handler.gesehen[0][2]["messages"]
    assert m[0]["content"] == "alt\n[Bild]"
    assert m[2]["content"][0]["type"] == "image" and m[2]["content"][0]["source"]["media_type"] == "image/png"
    assert m[2]["content"][1] == {"type": "text", "text": "neu"}
    # Ollama
    Handler.gesehen = []
    Handler.antwort = {"message": {"content": "ok"}}
    ki.k.d["modell"] = "ollama:v"
    K.KI._faehig["v"] = (0, {"vision"})
    assert ki.chat(verlauf)["text"] == "ok"
    m = Handler.gesehen[0][2]["messages"]
    assert len(m[3]["images"][0]) > 10 and "images" not in m[1]
    # eigener Anbieter: nur mit Etikett „visuell“
    Handler.gesehen = []
    Handler.antwort = {"choices": [{"message": {"content": "ok"}}]}
    a = ki.k.anbieter_hinzufuegen("X", server, "", "m", ["text"])
    ki.k.aufgabe_setzen("chatbot", "eigen:" + a["id"])
    assert "keine Bilder" in ki.chat(verlauf)["fehler"] and not Handler.gesehen
    ki.k.anbieter_aktualisieren(a["id"], "X", server, "", "m", ["text", "visuell"])
    assert ki.chat(verlauf)["text"] == "ok"
    teil = Handler.gesehen[0][2]["messages"][3]["content"]
    assert teil[-1]["image_url"]["url"].startswith("data:image/png;base64,")


def test_bild_ollama_unbekannt_ist_nicht_faehig(tmp_path, monkeypatch):
    monkeypatch.setattr(K, "OLLAMA_URL", "http://127.0.0.1:9")
    K.KI._faehig.pop("nix", None)
    ki = K.KI(konfig(tmp_path))
    assert ki.faehigkeit("ollama:nix") == (False, False)
    assert ki.kann_bild("ollama:nix") is False


def test_chat_modell_bilder_und_neues_gespraech():
    from lunivo_writer.ki.chat_modell import ChatModell
    c = ChatModell()
    c.anfrage("x", [{"pfad": "/a.png", "typ": "image/png", "bytes": 1}])
    assert c.verlauf()[0]["bilder"][0]["pfad"] == "/a.png"
    c.abbrechen(); c.wiederholen()
    assert c.wiederhol_bilder
    c.neues_gespraech()
    assert not c.wiederhol_bilder and c.nachrichten == []


def test_werkzeug_automatisch_nur_nicht_gespeichert(tmp_path):
    k = K.KIKonfig(str(tmp_path / "k.json"))
    k.chat_setzen(werkzeuge="automatisch", denktiefe="hoch")
    assert json.load(open(tmp_path / "k.json"))["chat"] == {"werkzeuge": "fragen", "denktiefe": "hoch"}
    assert K.KIKonfig(str(tmp_path / "k.json")).chat_optionen()["werkzeuge"] == "fragen"


def test_assistent_migration_filter_und_aendern(tmp_path):
    k = K.KIKonfig(str(tmp_path / "ki.json"))
    k.d["assistenten"].append({"id": "alt1", "name": "Alt", "prompt": "p", "modus": "ersetzen", "zugriff": "schnell"})      # Bestand ohne Art
    n = k.assistent_hinzufuegen("Dauer", "q", "kommentar", art="fortlaufend", ausloeser="absatz", verzoegerung=1, kommentar=True, an=True)
    assert [a["name"] for a in k.assistenten("aktion")] == ["Alt"] and [a["name"] for a in k.assistenten("fortlaufend")] == ["Dauer"]
    assert n["verzoegerung"] == 2 and n["umfang"] == "absatz" and n["an"] is True and n["kommentar"] is True
    z = k.assistent_hinzufuegen("Akt", "r", "kommentar", art="aktion", an=True, umfang="dokument")
    assert z["modus"] == "hinweis" and z["an"] is False and z["umfang"] == "absatz"       # Aktion: nur alte Modi, nie „an“
    assert k.assistent_aendern(n["id"], an=False)["an"] is False and k.assistent_aendern("nix", an=True) is None
    assert len(K.VORLAGEN_ASSISTENT) == 6 and all(v[2] in K.FORTLAUFEND_MODI for v in K.VORLAGEN_ASSISTENT)
