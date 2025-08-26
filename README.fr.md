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

## ⚙️ Installation

### Prérequis
- Python 3.10+
- Windows 11 (testé)
- [Siril](https://siril.org/) installé et accessible dans le PATH (optionnel, pour lancer des scripts)
- [Sequator](https://sites.google.com/view/sequator/) (optionnel, pour exploiter les fichiers projet générés)

### Étapes d’installation

1. Cloner le dépôt :
```powershell
git clone https://github.com/yourusername/astro_sorter_project.git
cd astro_sorter_project
```

2. Créer et activer un environnement virtuel :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Installer les dépendances :

```powershell
pip install -r requirements.txt
```

4. Lancer l’application :

```powershell
python main.py
```

### Démarrage rapide
* Sélectionner un dossier contenant des images NEF
* Entrer ou choisir une position sauvegardée (latitude/longitude)
* Utiliser l’outil de renommage par lot
* Convertir les fichiers en JPEG/TIFF (si manquants)
* Organiser dans les répertoires Lights / Darks / Flats / Biases
* Exporter un projet Sequator (.sep) ou exécuter un workflow Siril

### Démarrage rapide en ligne de commande

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
```

## 🚀 Roadmap

- [ ] Workflows Siril avancés  
- [ ] Support de DeepSkyStacker  
- [ ] Gestion avancée des métadonnées EXIF  
- [ ] Mode CLI (sans interface graphique)  
