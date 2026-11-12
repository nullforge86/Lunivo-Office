from PySide6.QtCore import QSettings, QStandardPaths

from lunivo_writer.dienste import wiederherstellung
from lunivo_writer.dienste.einstellungen_dienst import Settings


def test_settings_persist_and_recent(app, tmp_path):
    ini = str(tmp_path / "s.ini")
    s = Settings(QSettings(ini, QSettings.IniFormat))
    s.set("theme", "dark"); s.set("n", 7)
    for i in range(20):
        s.add_recent(f"/x/{i}.docx")
    s.add_recent("/x/5.docx")
    s2 = Settings(QSettings(ini, QSettings.IniFormat))
    assert s2.get("theme") == "dark" and s2.get_int("n", 0) == 7
    r = s2.recent()
    assert r[0] == "/x/5.docx" and len(r) == 12 and len(set(r)) == 12
    s2.remove_recent("/x/5.docx")
    assert "/x/5.docx" not in s2.recent()


def test_recovery_cycle(app, tmp_path, monkeypatch):
    monkeypatch.setattr(wiederherstellung, "recovery_dir", lambda: str(tmp_path))
    t = wiederherstellung.new_token()
    d, m = wiederherstellung.paths(t)
    open(d, "wb").write(b"x")
    wiederherstellung.write_meta(t, "/a/b.docx", "b")
    e = wiederherstellung.pending()
    assert len(e) == 1 and e[0].original == "/a/b.docx"
    assert wiederherstellung.pending(exclude={t}) == []
    wiederherstellung.discard(t)
    assert wiederherstellung.pending() == []


def test_gedaechtnis_zaehlt_nur_beim_ausdruecklichen_pruefen(tmp_path):
    from lunivo_writer.dienste.gelernt import LERN_SCHWELLE, Gelernt
    g = Gelernt(str(tmp_path / "g.json"))
    from lunivo_writer.modelle.korrektur import ProofingIssue
    fund = ProofingIssue(von=0, bis=4, alt="Meyr", neu="Mehr", wort_ebene=True, art="fehler", grund="x")
    for _ in range(LERN_SCHWELLE - 1):
        g.merke_gezeigt([fund])
    assert not g.daten["inRuhe"]
    g.merke_gezeigt([fund])
    assert g.daten["inRuhe"] == {"meyr": True} and "meyr" not in g.daten["gezeigt"]
    g2 = Gelernt(str(tmp_path / "g.json"))                       # bleibt gespeichert
    assert g2.daten["inRuhe"] == {"meyr": True}
    g2.gewaehlt(ProofingIssue(von=0, bis=9, alt="Vieleicht", neu="Vielleicht", wort_ebene=True))
    assert g2.daten["woerter"]["vieleicht"] == "Vielleicht"
