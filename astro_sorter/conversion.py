from __future__ import annotations
from pathlib import Path
from typing import Tuple
import shutil
from .exif_utils import call_exe

try:
    import rawpy
    import imageio.v2 as imageio
    import numpy as np
except Exception:
    rawpy = None
    imageio = None
    np = None

def convert_nef_to_jpeg_tiff(src_nef: Path, jpg_out: Path, tif_out: Path) -> Tuple[bool, bool]:
    jpg_created = False
    tif_created = False
    if jpg_out.exists() and tif_out.exists():
        return jpg_created, tif_created
    if rawpy and imageio:
        try:
            with rawpy.imread(str(src_nef)) as raw:
                rgb16 = raw.postprocess(output_bps=16, no_auto_bright=True, gamma=(1,1))
            if not tif_out.exists():
                imageio.imwrite(str(tif_out), rgb16)
                tif_created = True
            if not jpg_out.exists():
                if np is None:
                    raise RuntimeError("numpy requis pour JPEG via rawpy")
                rgb8 = (rgb16 / 256).astype('uint8')
                imageio.imwrite(str(jpg_out), rgb8, quality=95)
                jpg_created = True
            return jpg_created, tif_created
        except Exception:
            pass
    # fallback: dcraw
    code, out, err = call_exe("dcraw", "-T", "-6", "-W", str(src_nef))
    if code == 0:
        tiff_generated = src_nef.with_suffix(".tiff")
        if tiff_generated.exists():
            shutil.move(str(tiff_generated), str(tif_out))
            tif_created = True
            # optionally create JPG via PIL
            try:
                from PIL import Image
                img = Image.open(tif_out)
                img = img.convert('RGB')
                img.save(jpg_out, quality=95)
                jpg_created = True
            except Exception:
                pass
    return jpg_created, tif_created
