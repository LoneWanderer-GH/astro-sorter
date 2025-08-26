from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional


def generate_siril_script(
        output_path: Path, lights_dir: Path, darks_dir: Optional[Path] = None, flats_dir: Optional[Path] = None,
        biases_dir: Optional[Path] = None, result_name: str = "result_stacked", method: str = "rej",
        rej_params: str = "3 3"
        ) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["requires 1.2", f"cd {lights_dir}", "setext .tif"]
    # preprocess if calibration frames exist
    preprocess_parts = []
    if darks_dir and any(darks_dir.glob("*.tif")):
        preprocess_parts.append(f"-dark={darks_dir}\\")
    if flats_dir and any(flats_dir.glob("*.tif")):
        preprocess_parts.append(f"-flat={flats_dir}\\")
    if biases_dir and any(biases_dir.glob("*.tif")):
        preprocess_parts.append(f"-bias={biases_dir}\\")
    if preprocess_parts:
        lines.append("preprocess light " + " ".join(preprocess_parts))
    # register and stack
    lines.append("register light")
    lines.append(f"stack light {method} {rej_params} -norm=addscale -out=../result/{result_name}")
    output_path.write_text("\n".join(lines))
    return output_path


def run_siril(siril_exe: Path | str, script_path: Path) -> int:
    try:
        proc = subprocess.run([str(siril_exe), "-s", str(script_path)], capture_output=True, text=True)
        return proc.returncode
    except FileNotFoundError:
        return 127


WORKFLOWS = {
        "basic"     : "workflows/siril_basic.ssf",
        "advanced"  : "workflows/siril_advanced.ssf",
        "photometry": "workflows/siril_photometry.ssf",
}


def run_workflow(work_dir: Path, mode: str):
    script_path = Path(__file__).parent / WORKFLOWS[mode]
    if not script_path.exists():
        raise FileNotFoundError(f"Siril script not found: {script_path}")
    
    cmd = ["siril-cli", "-d", str(work_dir), "-s", str(script_path)]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
