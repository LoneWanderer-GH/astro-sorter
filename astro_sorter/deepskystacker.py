from pathlib import Path
from typing import Iterable


HEADER = "DeepSkyStacker file list"


def _norm_list(files: Iterable[Path] | None) -> list[str]:
    if not files:
        return []
    return [str(Path(f)) for f in files]


def create_dss_file(
    output_path: Path,
    lights: Iterable[Path],
    darks: Iterable[Path] | None = None,
    flats: Iterable[Path] | None = None,
    biases: Iterable[Path] | None = None,
) -> Path:
    """
    Generate a DSS-compatible text file listing LIGHTS/DARKS/FLATS/BIAS.
    Each path is written on its own line, grouped by section.

    DeepSkyStacker can open this .txt directly (File list).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lights = _norm_list(lights)
    darks = _norm_list(darks)
    flats = _norm_list(flats)
    biases = _norm_list(biases)

    with output_path.open("w", encoding="utf-8") as f:
        f.write(f"{HEADER}\n\n")

        def section(title: str, items: list[str]):
            if not items:
                return
            f.write(f"# {title}\n")
            for it in items:
                f.write(f"{it}\n")
            f.write("\n")

        section("LIGHTS", lights)
        section("DARKS", darks)
        section("FLATS", flats)
        section("BIAS/Offset", biases)

    return output_path
