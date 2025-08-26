import pytest
from astro_sorter.conversion import convert_nef_to_jpeg_tiff
from pathlib import Path
import tempfile

def test_conversion_no_raw(tmp_path):
    # just ensure function doesn't crash on missing tools (returns False,False)
    src = tmp_path / "dummy.NEF"
    src.write_text("not a raw")
    jpg = tmp_path / "out.jpg"
    tif = tmp_path / "out.tif"
    j, t = convert_nef_to_jpeg_tiff(src, jpg, tif)
    assert isinstance(j, bool) and isinstance(t, bool)
