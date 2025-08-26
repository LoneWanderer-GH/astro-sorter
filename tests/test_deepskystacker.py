from pathlib import Path
from astro_sorter.deepskystacker import create_dss_file, HEADER


def test_create_dss_file_writes_sections(tmp_path: Path):
    lights = [tmp_path / "L1.NEF", tmp_path / "L2.NEF"]
    darks = [tmp_path / "D1.NEF"]
    flats = []
    biases = [tmp_path / "B1.NEF"]

    # Touch files (not strictly required by function but realistic)
    for p in lights + darks + biases:
        p.write_bytes(b"")

    out = tmp_path / "project_dss.txt"
    create_dss_file(out, lights, darks, flats, biases)

    txt = out.read_text(encoding="utf-8")
    assert HEADER in txt
    assert "# LIGHTS" in txt
    assert str(lights[0]) in txt
    assert "# DARKS" in txt
    assert str(darks[0]) in txt
    assert "# FLATS" not in txt  # no flats section since list empty
    assert "# BIAS/Offset" in txt
