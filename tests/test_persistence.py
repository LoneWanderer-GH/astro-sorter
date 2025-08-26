from astro_sorter.persistence import Persistence, Position
import tempfile, shutil
from pathlib import Path

def test_positions_add_and_load(tmp_path):
    # simulate appdata folder
    pdir = tmp_path / "appdata"
    pdir.mkdir()
    pers = Persistence()
    # override file location for test
    pers.positions_file = pdir / "positions.json"
    pers._init_positions_file()
    pos = Position("spot", 48.8566, 2.3522)
    added = pers.add_position_if_new(pos, "favorites")
    assert added
    loaded = pers.load_positions("favorites")
    assert any(p.lat == 48.8566 for p in loaded)
