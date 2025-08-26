from astro_sorter.sequator import create_sequator_files
from pathlib import Path
import tempfile

def test_create_sequator(tmp_path):
    seqdir = tmp_path / "seq"
    seqdir.mkdir()
    lights = [tmp_path / f"img{i}.tif" for i in range(5)]
    for f in lights: f.write_text("x")
    create_sequator_files(seqdir, "prj", [], None, lights)
    assert (seqdir / "prj-Stack.sep").exists()
    assert (seqdir / "prj-Trail.sep").exists()
