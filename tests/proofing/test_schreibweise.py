from lunivo_writer.editor.schreibweise import umwandeln, sortiert
def test_arten():
    assert umwandeln("hallo welt. wie geht's? gut", "satz") == "Hallo welt. Wie geht's? Gut"
    assert umwandeln("hallo WELT", "title") == "Hallo Welt"
    assert umwandeln("aB", "toggle") == "Ab"
    assert umwandeln("ab", "upper") == "AB" and umwandeln("AB", "lower") == "ab"
def test_sortiert():
    assert sortiert(["b", "A", "c"]) == ["A", "b", "c"]
    assert sortiert(["b", "A", "c"], absteigend=True) == ["c", "b", "A"]
    assert sortiert(["b", "A", "a"], gross_klein=True) == ["A", "a", "b"]
    assert sortiert(["10 x", "9 y", "100 z"], typ="zahl") == ["9 y", "10 x", "100 z"]
    assert sortiert(["2.1.2024", "1.5.2023"], typ="datum") == ["1.5.2023", "2.1.2024"]
