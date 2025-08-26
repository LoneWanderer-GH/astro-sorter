import sys
from pathlib import Path
import types
import builtins
import pytest

import astro_sorter_cli


class DummyCompleted:
    def __init__(self, returncode=0):
        self.returncode = returncode


def test_cli_end_to_end_minimal(tmp_path: Path, monkeypatch):
    # Arrange: create fake NEF inputs
    in_dir = tmp_path / "input"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    (in_dir / "A.NEF").write_bytes(b"")
    (in_dir / "B.nef").write_bytes(b"")

    # Monkeypatch conversion module presence and functions
    fake_conversion = types.SimpleNamespace(
        convert_all_nef=lambda a, b: None
    )
    sys.modules["astro_sorter.conversion"] = fake_conversion  # type: ignore

    # Monkeypatch subprocess.run used in siril.run_workflow
    def fake_run(cmd, check):
        # pretend Siril succeeded
        return DummyCompleted(0)

    import subprocess
    monkeypatch.setattr(subprocess, "run", fake_run)

    # Act: run CLI with convert + sequator + dss (no siril)
    argv = [
        "--input", str(in_dir),
        "--output", str(out_dir),
        "--convert",
        "--sequator",
        "--dss",
        "--project-name", "tproj",
    ]
    code = astro_sorter_cli.cli(argv)

    # Assert
    assert code == 0
    assert (out_dir / "tproj_dss.txt").exists()
    # Sequator file(s) are created by your existing module; we only check directory exists
    assert out_dir.exists()


def test_cli_siril_invocation(tmp_path: Path, monkeypatch):
    # Prepare dirs & a dummy light
    in_dir = tmp_path / "input"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    (in_dir / "C.NEF").write_bytes(b"")

    # conversion optional
    sys.modules["astro_sorter.conversion"] = types.SimpleNamespace()  # type: ignore

    # Catch the exact command used for Siril
    captured = {}
    def fake_run(cmd, check):
        captured["cmd"] = cmd
        return DummyCompleted(0)

    import subprocess
    monkeypatch.setattr(subprocess, "run", fake_run)

    code = astro_sorter_cli.cli([
        "--input", str(in_dir),
        "--output", str(out_dir),
        "--siril", "basic",
    ])
    assert code == 0
    assert "siril" in captured["cmd"][0]  # 'siril-cli' or fallback 'siril'
