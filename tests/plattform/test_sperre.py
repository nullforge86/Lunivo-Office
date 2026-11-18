import pytest

from lunivo_writer.plattform import sperre


def test_zweite_sperre_auf_dieselbe_datei_ist_belegt_und_nach_freigabe_wieder_frei(tmp_path):
    datei = str(tmp_path / "a.lock")
    fd = sperre.sperre_oeffnen(datei)
    with pytest.raises(sperre.SperreBelegt):
        sperre.sperre_oeffnen(datei)
    sperre.sperre_freigeben(fd)
    sperre.sperre_freigeben(sperre.sperre_oeffnen(datei))
