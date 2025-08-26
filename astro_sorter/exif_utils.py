from __future__ import annotations
from pathlib import Path
import json, subprocess
from typing import Tuple, Optional, Dict

try:
    import piexif
    from PIL import Image
except Exception:
    piexif = None
    Image = None

def call_exe(exe: str | Path, *args):
    try:
        proc = subprocess.run([str(exe), *map(str, args)], capture_output=True, text=True, check=False)
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:
        return 127, "", f"Executable not found: {exe}"

def exiftool_available() -> bool:
    code, *_ = call_exe("exiftool", "-ver")
    return code == 0

def _deg_to_dms_rational(deg: float):
    d = int(abs(deg))
    m_float = (abs(deg) - d) * 60
    m = int(m_float)
    s = int(round((m_float - m) * 60 * 100))
    return ((d,1),(m,1),(s,100))

def write_gps_exiftool(path: Path, lat: float, lon: float) -> bool:
    code, out, err = call_exe("exiftool", f"-GPSLatitude={lat}", f"-GPSLongitude={lon}", "-overwrite_original", str(path))
    return code == 0

def write_gps_jpeg_piexif(jpg: Path, lat: float, lon: float) -> bool:
    if piexif and Image:
        try:
            img = Image.open(jpg)
            exif_dict = piexif.load(img.info.get("exif", b""))
            gps_ifd = exif_dict.get("GPS", {})
            gps_ifd[piexif.GPSIFD.GPSLatitudeRef] = b"N" if lat >= 0 else b"S"
            gps_ifd[piexif.GPSIFD.GPSLongitudeRef] = b"E" if lon >= 0 else b"W"
            gps_ifd[piexif.GPSIFD.GPSLatitude] = _deg_to_dms_rational(lat)
            gps_ifd[piexif.GPSIFD.GPSLongitude] = _deg_to_dms_rational(lon)
            exif_dict["GPS"] = gps_ifd
            exif_bytes = piexif.dump(exif_dict)
            img.save(jpg, exif=exif_bytes)
            return True
        except Exception:
            return False
    return False

def write_gps_generic(path: Path, lat: float, lon: float) -> bool:
    if exiftool_available():
        return write_gps_exiftool(path, lat, lon)
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        return write_gps_jpeg_piexif(path, lat, lon)
    # fallback XMP sidecar
    try:
        xmp = path.with_suffix(path.suffix + ".xmp")
        xmp.write_text(f"<x:xmpmeta><rdf:RDF><rdf:Description><exif:GPSLatitude>{lat}</exif:GPSLatitude><exif:GPSLongitude>{lon}</exif:GPSLongitude></rdf:Description></rdf:RDF></x:xmpmeta>")
        return True
    except Exception:
        return False

def read_exif_with_exiftool(path: Path) -> Dict[str, str]:
    code, out, err = call_exe("exiftool", "-json", str(path))
    if code == 0 and out:
        try:
            return json.loads(out)[0]
        except Exception:
            return {}
    return {}
