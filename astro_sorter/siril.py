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


# Map friendly workflow names to script paths relative to this module.
WORKFLOWS = {
        "basic"     : "workflows/siril_basic.ssf",
        "advanced"  : "workflows/siril_advanced.ssf",
        "photometry": "workflows/siril_photometry.ssf",
}


def run_workflow(work_dir: Path, mode: str, siril_exe: str | None = None) -> None:
    """
    Run a Siril workflow (.ssf) in CLI mode.

    Args:
        work_dir: directory used as working dir by Siril
        mode: one of WORKFLOWS keys
        siril_exe: optional override for Siril executable name/path
                   Defaults to 'siril-cli' then fallback to 'siril'.
    """
    work_dir = Path(work_dir)
    if not work_dir.exists():
        raise FileNotFoundError(f"Working directory not found: {work_dir}")
    
    script_rel = WORKFLOWS.get(mode)
    if not script_rel:
        raise ValueError(f"Unknown Siril workflow '{mode}'. Options: {', '.join(WORKFLOWS)}")
    
    script_path = Path(__file__).parent / script_rel
    if not script_path.exists():
        raise FileNotFoundError(f"Siril script not found: {script_path}")
    
    # On Windows, Siril CLI might be 'siril-cli.exe' or 'siril.exe'
    exe = siril_exe or "siril-cli"
    cmd = [exe, "-d", str(work_dir), "-s", str(script_path)]
    
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        # Fallback if siril-cli is not found
        alt = "siril"
        if exe != alt:
            cmd[0] = alt
            subprocess.run(cmd, check=True)
        else:
            raise
