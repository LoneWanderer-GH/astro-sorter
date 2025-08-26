import argparse
import sys
from pathlib import Path

# Local imports
from astro_sorter import deepskystacker, sequator, siril

# Optional: conversion & renaming modules
# Make these optional so CLI remains usable even if not implemented yet.
try:
    from astro_sorter import conversion
except Exception:  # pragma: no cover
    conversion = None  # type: ignore


def _find_nef(folder: Path) -> list[Path]:
    return sorted(list(folder.glob("*.NEF")) + list(folder.glob("*.nef")))


def cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Astro Sorter CLI")
    p.add_argument("--input", type=Path, required=True, help="Input folder containing raw images")
    p.add_argument("--output", type=Path, required=True, help="Output folder (organized)")
    p.add_argument("--rename", action="store_true", help="Batch rename RAW files (module-dependent)")
    p.add_argument("--convert", action="store_true", help="Convert NEF -> JPEG/TIFF (if missing)")
    p.add_argument("--sequator", action="store_true", help="Generate Sequator .sep project (stack & trail)")
    p.add_argument("--dss", action="store_true", help="Generate DeepSkyStacker file list (.txt)")
    p.add_argument("--siril", choices=["basic", "advanced", "photometry"], help="Run a Siril workflow")
    p.add_argument("--siril-exe", type=str, default=None, help="Path or name for Siril executable (optional)")
    p.add_argument("--project-name", type=str, default="project", help="Base name for outputs")
    args = p.parse_args(argv)

    in_dir: Path = args.input
    out_dir: Path = args.output
    out_dir.mkdir(parents=True, exist_ok=True)

    lights = _find_nef(in_dir)
    if not lights:
        print("No NEF files found in input directory.", file=sys.stderr)
        return 2

    # 1) Rename (if your renaming logic exists in another module)
    if args.rename:
        if hasattr(conversion, "batch_rename"):  # type: ignore[attr-defined]
            print("Renaming NEF files...")
            conversion.batch_rename(lights)  # type: ignore[attr-defined]
        else:
            print("Rename requested but no renaming function found. Skipping.", file=sys.stderr)

    # 2) Convert
    if args.convert:
        if conversion and hasattr(conversion, "convert_all_nef"):
            print("Converting NEF files...")
            conversion.convert_all_nef(in_dir, out_dir)  # type: ignore[attr-defined]
        else:
            print("Convert requested but convert_all_nef not found. Skipping.", file=sys.stderr)

    # 3) Sequator .sep
    if args.sequator:
        print("Generating Sequator project (.sep)...")
        # Reuse your existing create_sequator_files signature
        sequator.create_sequator_files(
            _sequator_path=out_dir,
            _project_name=args.project_name,
            _dark_files=[],
            _flat_file=None,
            _raw_lights_files=lights,
        )

    # 4) DSS file list
    if args.dss:
        print("Generating DeepSkyStacker file list (project_dss.txt)...")
        deepskystacker.create_dss_file(out_dir / f"{args.project_name}_dss.txt", lights)

    # 5) Siril workflow
    if args.siril:
        print(f"Running Siril workflow: {args.siril}")
        siril.run_workflow(out_dir, args.siril, siril_exe=args.siril_exe)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
