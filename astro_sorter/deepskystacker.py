from pathlib import Path

def create_dss_file(output_path: Path, lights, darks=None, flats=None, biases=None):
    """
    Generate a DSS-compatible .txt file listing calibration frames.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("DeepSkyStacker file list\n")
        f.write("\n")

        def _write_section(title, files):
            if not files:
                return
            f.write(f"# {title}\n")
            for img in files:
                f.write(f"{img}\n")
            f.write("\n")

        _write_section("LIGHTS", lights)
        _write_section("DARKS", darks)
        _write_section("FLATS", flats)
        _write_section("BIAS/Offset", biases)

    return output_path
