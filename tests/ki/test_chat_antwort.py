from lunivo_writer.ki import chat_antwort as CA
from lunivo_writer.ki import chat_bezug as CB
from lunivo_writer.ki import ki_chat_kontext as CK


def test_marker():
    t = f"Gern.\n{CA.MARKE_ANFANG}\nSehr geehrte Frau X,\n\nbitte.\n{CA.MARKE_ENDE}\nIch habe gekürzt."
    assert CA.teilen(t) == ("Gern.", "Sehr geehrte Frau X,\n\nbitte.", "Ich habe gekürzt.")
    assert CA.strom_text("Hallo " + CA.MARKE_ANFANG[:4]) == "Hallo "


def test_heuristik_einleitung_brief_erklaerung():
    t = "Hier ist der überarbeitete Text:\n\nSehr geehrte Frau X,\n\nbitte antworten Sie.\n\nIch habe einige Änderungen vorgenommen:\n* kürzer\n* höflicher"
    e, k, x = CA.teilen(t)
    assert e == "Hier ist der überarbeitete Text:"
    assert k == "Sehr geehrte Frau X,\n\nbitte antworten Sie."
    assert x.startswith("Ich habe") and "* höflicher" in x


def test_kein_treffer_bleibt():
    assert CA.teilen("Ein ganz normaler Satz.") == ("", "Ein ganz normaler Satz.", "")
    assert CA.teilen("Ich habe Hunger.") == ("", "Ich habe Hunger.", "")


def test_abschliessen_und_diff():
    r = CK.abschliessen({"text": "a", "abgeschnitten": True}, [], "(Notiz)\n\n")
    assert r["text"] == "a" and r["notiz"] == "(Notiz)" and r["kuerzung"] and "abgeschnitten" not in r
    st = CB.vorschau_stuecke("Liebe Frau X,\n\nbitte kommen.", "Liebe Frau X,\n\n**bitte** kommen Sie.")
    assert any(a == "gleich" for a, _ in st)
    n = {"text": "x", "kern": "Das ist sehr gut."}
    assert CB.vorschau_der_nachricht(n, {"markiert": True, "alt": "Das ist gut."})
    assert CB.vorschau_der_nachricht(n, {"markiert": False, "alt": ""}) is None
