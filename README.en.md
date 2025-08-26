# Astro Sorter

**Astro Sorter** is a Python (PyQt6) application designed to organize, rename, and prepare your astrophotography photos (NEF/RAW) on Windows 11.  
The project is built to be **modular, maintainable, and extensible**, with a clean graphical interface and independent modules.

---

## ✨ Features

- **Batch Renaming**  
- **RAW (NEF) Conversion** → JPEG & TIFF (only if missing)  
- **Automatic Directory Structure**  
  - `/NEF`, `/JPEG`, `/TIFF`  
  - `/lights`, `/darks`, `/bias`, `/flats`  
- **Symbolic Links** (minimizing file duplication)  
- **Geolocation Metadata** (latitude/longitude with persistence & favorites)  
- **Sequator Project File Generation** (`.sep`)  
- **Siril Integration**  
  - Generate scripts  
  - Or directly launch Siril  

---

## 🛠️ Tech Stack

- Python 3.11+  
- PyQt6 (GUI)  
- Pathlib (file management)  
- ExifTool / piexif (metadata)  
- xml.etree.ElementTree (Sequator)  
- subprocess (Siril integration)  

---

## 📂 Project Structure

```text
astro_sorter_project/
├── astro_sorter/
│   ├── __init__.py
│   ├── persistence.py       # Persistence of settings & favorites
│   ├── exif_utils.py        # EXIF geotagging helpers
│   ├── conversion.py        # NEF to JPEG/TIFF
│   ├── sequator.py          # Sequator project (.sep) generator
│   ├── siril.py             # Siril integration (scripts & launch)
│   └── ui_main.py           # PyQt6 GUI
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── scaffold.ps1             # Windows setup script
├── tests/                   # Unit tests
│   ├── test_persistence.py
│   ├── test_sequator.py
│   └── test_conversion_smoke.py
└── .github/
    └── workflows/
        └── python-ci.yml    # GitHub Actions CI
