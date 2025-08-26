# Astro Sorter

**Astro Sorter** est une application Python (PyQt6) permettant d’organiser, renommer et préparer vos photos d’astrophotographie (NEF/RAW) sous Windows 11.  
Le projet est conçu pour être **modulaire, maintenable et extensible**, avec une interface graphique claire et des modules indépendants.

---

## ✨ Fonctionnalités

- **Renommage par lots**  
- **Conversion RAW (NEF)** → JPEG & TIFF (uniquement si manquant)  
- **Organisation automatique en arborescence**  
  - `/NEF`, `/JPEG`, `/TIFF`  
  - `/lights`, `/darks`, `/bias`, `/flats`  
- **Liens symboliques** (réduction de la duplication de fichiers)  
- **Métadonnées de géolocalisation** (latitude/longitude persistantes + favoris)  
- **Génération de fichiers projets Sequator** (`.sep`)  
- **Intégration Siril**  
  - Génération de scripts  
  - Ou lancement direct de Siril  

---

## 🛠️ Technologies utilisées

- Python 3.11+  
- PyQt6 (interface graphique)  
- Pathlib (gestion des fichiers)  
- ExifTool / piexif (métadonnées)  
- xml.etree.ElementTree (projets Sequator)  
- subprocess (intégration Siril)  

---

## 📂 Organisation du projet

```text
astro_sorter_project/
├── astro_sorter/
│   ├── __init__.py
│   ├── persistence.py       # Persistance des réglages & favoris
│   ├── exif_utils.py        # Gestion EXIF et géolocalisation
│   ├── conversion.py        # Conversion NEF en JPEG/TIFF
│   ├── sequator.py          # Génération de projets Sequator (.sep)
│   ├── siril.py             # Intégration Siril (scripts & lancement)
│   └── ui_main.py           # Interface PyQt6
├── main.py                  # Point d’entrée
├── requirements.txt         # Dépendances
├── scaffold.ps1             # Script d’installation Windows
├── tests/                   # Tests unitaires
│   ├── test_persistence.py
│   ├── test_sequator.py
│   └── test_conversion_smoke.py
└── .github/
    └── workflows/
        └── python-ci.yml    # Intégration continue GitHub Actions