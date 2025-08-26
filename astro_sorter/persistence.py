from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
from typing import List, Optional
from PyQt6.QtCore import QSettings

APP_NAME = "AstroSorter"
ORG = "AstroTools"

@dataclass
class Position:
    name: str
    lat: float
    lon: float

class Persistence:
    def __init__(self):
        # QSettings uses native storage (registry on Windows).
        self.qsettings = QSettings(ORG, APP_NAME)
        # positions file path in user appdata
        appdata = Path(self.qsettings.value("positions_dir", "")) if self.qsettings.value("positions_dir", "") else Path.home() / f".{APP_NAME.lower()}"
        appdata.mkdir(parents=True, exist_ok=True)
        self.positions_file = appdata / "positions.json"
        if not self.positions_file.exists():
            self.positions_file.write_text(json.dumps({"recents": [], "favorites": []}, indent=2))

    # QSettings wrappers
    def set_value(self, key: str, value):
        self.qsettings.setValue(key, value)

    def get_value(self, key: str, default=None):
        val = self.qsettings.value(key, default)
        return val if val is not None else default

    # positions JSON
    def load_positions(self, key: str = "recents") -> List[Position]:
        raw = json.loads(self.positions_file.read_text())
        return [Position(**p) for p in raw.get(key, [])]

    def save_positions(self, positions: List[Position], key: str = "recents"):
        raw = json.loads(self.positions_file.read_text())
        raw[key] = [asdict(p) for p in positions]
        self.positions_file.write_text(json.dumps(raw, indent=2))

    def add_position_if_new(self, pos: Position, key: str = "favorites") -> bool:
        raw = json.loads(self.positions_file.read_text())
        items = raw.get(key, [])
        for p in items:
            if float(p.get("lat")) == float(pos.lat) and float(p.get("lon")) == float(pos.lon):
                return False
        items.append(asdict(pos))
        raw[key] = items
        self.positions_file.write_text(json.dumps(raw, indent=2))
        return True
