from __future__ import annotations
from pathlib import Path
from typing import List, Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget,
    QComboBox, QGroupBox, QFormLayout, QProgressBar, QTextEdit, QFileDialog, QMessageBox,
    QCheckBox, QSpinBox, QDialog, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from .persistence import Persistence, Position
from .conversion import convert_nef_to_jpeg_tiff
from .exif_utils import write_gps_generic, exiftool_available, read_exif_with_exiftool
from .sequator import create_sequator_files
from .siril import generate_siril_script, run_siril
import os

FRAME_KINDS = ["lights", "darks", "biases", "flats"]

class PreviewDialog(QDialog):
    def __init__(self, mapping: List[Tuple[Path, Path]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prévisualisation renommage")
        self.resize(900, 450)
        table = QTableWidget(len(mapping), 2)
        table.setHorizontalHeaderLabels(["Ancien nom", "Nouveau nom"])
        for i, (src, dst) in enumerate(mapping):
            table.setItem(i, 0, QTableWidgetItem(src.name))
            table.setItem(i, 1, QTableWidgetItem(dst.name))
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        ok = QPushButton("Appliquer"); cancel = QPushButton("Annuler")
        ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject)
        btns = QHBoxLayout(); btns.addStretch(1); btns.addWidget(ok); btns.addWidget(cancel)
        lay = QVBoxLayout(self); lay.addWidget(table); lay.addLayout(btns)

class UiAstroSorter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.persistence = Persistence()
        self.recent_positions = self.persistence.load_positions("recents")
        self.favorites = self.persistence.load_positions("favorites")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Paths
        paths = QHBoxLayout()
        self.src = QLineEdit(self.persistence.get_value("last_source", ""))
        b1 = QPushButton("Parcourir"); b1.clicked.connect(self.choose_src)
        self.dst = QLineEdit(self.persistence.get_value("last_target", ""))
        b2 = QPushButton("Parcourir"); b2.clicked.connect(self.choose_dst)
        paths.addWidget(QLabel("Src:")); paths.addWidget(self.src); paths.addWidget(b1)
        paths.addWidget(QLabel("Dst:")); paths.addWidget(self.dst); paths.addWidget(b2)
        layout.addLayout(paths)

        # Session / Siril options
        ss = QHBoxLayout()
        self.session = QLineEdit(self.persistence.get_value("session_name", "session"))
        self.siril_path = QLineEdit(self.persistence.get_value("siril_path", "siril"))
        self.siril_mode = QComboBox(); self.siril_mode.addItems(["Générer seulement", "Générer et lancer"])
        ss.addWidget(QLabel("Session:")); ss.addWidget(self.session)
        ss.addWidget(QLabel("Siril exe:")); ss.addWidget(self.siril_path); ss.addWidget(self.siril_mode)
        layout.addLayout(ss)

        # GPS group
        gps_box = QGroupBox("Position GPS (degrés décimaux)")
        gps_form = QFormLayout(gps_box)
        self.lat = QLineEdit(""); self.lon = QLineEdit(""); self.pos_name = QLineEdit("")
        gps_form.addRow("Latitude:", self.lat); gps_form.addRow("Longitude:", self.lon); gps_form.addRow("Nom:", self.pos_name)
        recent_row = QHBoxLayout()
        self.recent_combo = QComboBox(); self.fav_combo = QComboBox(); self.refresh_pos_combos()
        use_recent = QPushButton("Utiliser récent"); use_recent.clicked.connect(lambda: self.apply_pos_from_combo(self.recent_combo))
        use_fav = QPushButton("Utiliser favori"); use_fav.clicked.connect(lambda: self.apply_pos_from_combo(self.fav_combo))
        add_fav = QPushButton("Ajouter aux favoris"); add_fav.clicked.connect(self.add_favorite)
        recent_row.addWidget(QLabel("Récents:")); recent_row.addWidget(self.recent_combo); recent_row.addWidget(use_recent)
        recent_row.addWidget(QLabel("Favoris:")); recent_row.addWidget(self.fav_combo); recent_row.addWidget(use_fav); recent_row.addWidget(add_fav)
        gps_form.addRow(recent_row)
        layout.addWidget(gps_box)

        # Files & actions
        files = QHBoxLayout()
        self.list = QListWidget()
        files.addWidget(self.list)
        act = QVBoxLayout()
        bscan = QPushButton("Scanner NEF"); bscan.clicked.connect(self.scan_nef)
        brename = QPushButton("Renommer (prévisualiser)"); brename.clicked.connect(self.batch_rename_preview)
        bclass = QPushButton("Organiser (auto)"); bclass.clicked.connect(self.organize_tree_auto)
        bconvert = QPushButton("Convertir & écrire GPS"); bconvert.clicked.connect(self.batch_convert_and_write_gps)
        bseq = QPushButton("Créer projets Sequator"); bseq.clicked.connect(self.create_sequator_projects)
        bsiril = QPushButton("Générer &/ou lancer Siril"); bsiril.clicked.connect(self.siril_workflow)
        for b in (bscan, brename, bclass, bconvert, bseq, bsiril):
            act.addWidget(b)
        act.addStretch(1)
        files.addLayout(act)
        layout.addLayout(files)

        self.progress = QProgressBar(); layout.addWidget(self.progress)
        self.log = QTextEdit(); self.log.setReadOnly(True); layout.addWidget(self.log)

        # restore last paths
        if self.persistence.get_value("last_source"): self.src.setText(self.persistence.get_value("last_source"))
        if self.persistence.get_value("last_target"): self.dst.setText(self.persistence.get_value("last_target"))

    # pos helpers
    def refresh_pos_combos(self):
        self.recent_combo.clear(); self.fav_combo.clear()
        for p in self.recent_positions[-10:][::-1]:
            self.recent_combo.addItem(f"{p.name} ({p.lat:.5f},{p.lon:.5f})", p)
        for p in self.favorites:
            self.fav_combo.addItem(f"{p.name} ({p.lat:.5f},{p.lon:.5f})", p)

    def apply_pos_from_combo(self, combo):
        idx = combo.currentIndex()
        p = combo.itemData(idx)
        if p:
            self.pos_name.setText(p.name); self.lat.setText(str(p.lat)); self.lon.setText(str(p.lon))

    def add_favorite(self):
        try:
            lat = float(self.lat.text().strip()); lon = float(self.lon.text().strip())
        except Exception:
            QMessageBox.critical(self, "Erreur", "Lat/Lon invalides"); return
        name = self.pos_name.text().strip() or "spot"
        pos = Position(name, lat, lon)
        ok = self.persistence.add_position_if_new(pos, "favorites")
        if not ok:
            QMessageBox.information(self, "Info", "Position déjà présente dans les favoris.")
            return
        self.favorites = self.persistence.load_positions("favorites")
        self.refresh_pos_combos()
        QMessageBox.information(self, "OK", "Position ajoutée aux favoris.")

    # file ops
    def choose_src(self):
        d = QFileDialog.getExistingDirectory(self, "Choisir dossier source")
        if d: self.src.setText(d); self.persistence.set_value("last_source", d)

    def choose_dst(self):
        d = QFileDialog.getExistingDirectory(self, "Choisir dossier target")
        if d: self.dst.setText(d); self.persistence.set_value("last_target", d)

    def scan_nef(self):
        p = Path(self.src.text())
        if not p.is_dir():
            QMessageBox.critical(self, "Erreur", "Dossier source invalide"); return
        self.list.clear()
        for f in sorted(p.rglob("*.NEF")):
            self.list.addItem(str(f))
        self.log.append(f"Found {self.list.count()} NEF files")

    def batch_rename_preview(self):
        items = [Path(self.list.item(i).text()) for i in range(self.list.count())]
        if not items: QMessageBox.information(self, "Info", "Aucun fichier"); return
        mapping = []
        idx = 1
        session = self.session.text().strip() or "session"
        for p in items:
            # naive: use session + index; could extend to EXIF date
            new = p.with_name(f"{session}_{idx:03d}{p.suffix}")
            mapping.append((p, new)); idx += 1
        dlg = PreviewDialog(mapping, self)
        if dlg.exec() == QDialog.Accepted:
            for src, dst in mapping:
                try:
                    src.rename(dst)
                    self.log.append(f"Renamed: {src.name} -> {dst.name}")
                except Exception as e:
                    self.log.append(f"Rename failed: {src} : {e}")
            self.scan_nef()

    def organize_tree_auto(self):
        dst = Path(self.dst.text())
        if not dst:
            QMessageBox.critical(self, "Erreur", "Destination requise"); return
        # create tree
        for kind in FRAME_KINDS:
            for fmt in ("NEF", "JPEG", "TIFF"):
                (dst / kind / fmt).mkdir(parents=True, exist_ok=True)
        # simple link all NEF into lights/NEF (or we could use heuristics)
        for i in range(self.list.count()):
            p = Path(self.list.item(i).text())
            dest = dst / "lights" / "NEF" / p.name
            if not dest.exists():
                try:
                    os.link(str(p), str(dest))
                except Exception:
                    try:
                        os.symlink(str(p), str(dest))
                    except Exception:
                        shutil.copy2(str(p), str(dest))
        self.log.append("Organized into target tree (lights -> NEF)")

    def batch_convert_and_write_gps(self):
        dst = Path(self.dst.text())
        if not dst: QMessageBox.critical(self, "Erreur", "Destination requis"); return
        (dst / "lights" / "NEF").mkdir(parents=True, exist_ok=True)
        (dst / "lights" / "JPEG").mkdir(parents=True, exist_ok=True)
        (dst / "lights" / "TIFF").mkdir(parents=True, exist_ok=True)
        items = [Path(self.list.item(i).text()) for i in range(self.list.count())]
        total = len(items); self.progress.setMaximum(max(1,total))
        done = 0
        # do conversion and write GPS using current pos (if set)
        cur_pos = None
        try:
            if self.lat.text() and self.lon.text():
                cur_pos = (float(self.lat.text()), float(self.lon.text()))
        except Exception:
            cur_pos = None
        for src in items:
            jpg = dst / "lights" / "JPEG" / f"{src.stem}.jpg"
            tif = dst / "lights" / "TIFF" / f"{src.stem}.tif"
            jc, tc = convert_nef_to_jpeg_tiff(src, jpg, tif)
            self.log.append(f"{src.name}: JPG {'ok' if jc else 'skip'} TIFF {'ok' if tc else 'skip'}")
            # write gps metadata if available (applies to created files)
            if cur_pos:
                lat, lon = cur_pos
                for out in (jpg, tif, src):
                    try:
                        write_gps_generic(out, lat, lon)
                    except Exception:
                        pass
            done += 1; self.progress.setValue(done)
        QMessageBox.information(self, "OK", "Conversion terminée.")

    def create_sequator_projects(self):
        dst = Path(self.dst.text())
        if not dst: QMessageBox.critical(self, "Erreur", "Destination requis"); return
        lights = list((dst / "lights" / "TIFF").glob("*.tif"))
        if not lights:
            lights = list((dst / "lights" / "JPEG").glob("*.jpg"))
        darks = list((dst / "darks" / "TIFF").glob("*.tif"))
        flat = next((dst / "flats" / "TIFF").glob("*.tif"), None)
        create_sequator_files(dst / "lights", f"{self.session.text().strip() or 'session'}_lights", darks, flat, lights)
        QMessageBox.information(self, "OK", "Projets Sequator créés.")

    def siril_workflow(self):
        dst = Path(self.dst.text()); if not dst: QMessageBox.critical(self, "Erreur", "Destination requis"); return
        lights_dir = dst / "lights" / "TIFF"
        darks_dir = dst / "darks" / "TIFF"
        flats_dir = dst / "flats" / "TIFF"
        biases_dir = dst / "biases" / "TIFF"
        script_path = dst / "siril_script.ssf"
        generate_siril_script(script_path, lights_dir, darks_dir if darks_dir.exists() else None, flats_dir if flats_dir.exists() else None, biases_dir if biases_dir.exists() else None, result_name=f"{self.session.text().strip() or 'session'}_stack")
        mode = self.siril_mode.currentText()
        QMessageBox.information(self, "Siril", f"Siril script généré: {script_path}")
        if mode == "Générer et lancer":
            siril_exec = self.siril_path.text().strip() or "siril"
            code = run_siril(siril_exec, script_path)
            QMessageBox.information(self, "Siril", f"Siril exit code: {code}")
