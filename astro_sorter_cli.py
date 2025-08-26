import argparse
from pathlib import Path
from astro_sorter import conversion, sequator, siril, deepskystacker

def main():
    parser = argparse.ArgumentParser(description="Astro Sorter CLI")
    parser.add_argument("--input", type=Path, required=True, help="Input folder containing NEF files")
    parser.add_argument("--rename", action="store_true", help="Batch rename NEF files")
    parser.add_argument("--convert", action="store_true", help="Convert NEF to JPEG/TIFF if missing")
    parser.add_argument("--sequator", action="store_true", help="Generate Sequator project files")
    parser.add_argument("--dss", action="store_true", help="Generate DeepSkyStacker file list")
    parser.add_argument("--siril", choices=["basic", "advanced", "photometry"], help="Run Siril workflow")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")

    args = parser.parse_args()

    # Example pipeline
    if args.rename:
        print("Renaming NEF files...")
        # TODO: call renaming logic

    if args.convert:
        print("Converting NEF files...")
        conversion.convert_all_nef(args.input, args.output)

    if args.sequator:
        print("Generating Sequator project...")
        sequator.create_sequator_files(args.output, "project", [], None, list(args.input.glob("*.NEF")))

    if args.dss:
        print("Generating DSS project file...")
        deepskystacker.create_dss_file(args.output / "project_dss.txt", list(args.input.glob("*.NEF")))

    if args.siril:
        print(f"Running Siril workflow: {args.siril}")
        siril.run_workflow(args.output, args.siril)

if __name__ == "__main__":
    main()
