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
---

## ⚙️ Installation

### Requirements
- Python 3.10+
- Windows 11 (tested)
- [Siril](https://siril.org/) installed and available in PATH (optional, for scripts)
- [Sequator](https://sites.google.com/view/sequator/) (optional, for generated project files)

### Install steps

1. Clone the repository:
```powershell
git clone https://github.com/yourusername/astro_sorter_project.git
cd astro_sorter_project
```
2. Create a virtual environment and activate it:
```python
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Install dependencies:
```python
pip install -r requirements.txt
```

4. Run the application:
```python
python main.py
```

### Quickstart

* Select a folder containing NEF raw images
* Enter or select a saved location (latitude/longitude)
* Use the batch rename tool
* Convert files to JPEG/TIFF (if missing)
* Organize into Lights / Darks / Flats / Biases
* Optionally export a Sequator project (.sep) or run a Siril workflow

### Quickstart CLI

```powershell
# Convert, create Sequator and DSS files, then run advanced Siril workflow:
python astro_sorter_cli.py `
  --input "D:\Astro\2025-08-12\Session1" `
  --output "D:\Astro\2025-08-12\Processed" `
  --convert --sequator --dss `
  --siril advanced `
  --project-name "PerseidSession"
```
 
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
```


---
## 🚀 Roadmap

- [ ] Extended Siril workflows  
- [ ] Support for DeepSkyStacker  
- [ ] Advanced EXIF/metadata handling  
- [ ] CLI (headless mode)  
