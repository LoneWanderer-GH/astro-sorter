from __future__ import annotations
from pathlib import Path
from typing import List, Optional
import xml.etree.ElementTree as ET

SEQ_COMPOSITION_MODE_STACK = "0"
SEQ_COMPOSITION_MODE_TRAIL = "1"
SEQ_DISTORTION_CORRECTION_COMPLEX = "2"
XML_FALSE = "false"
XML_TRUE = "true"
SEQ_REDUCE_POLLUTION_MODE_UNEVEN = "1"
SEQ_INTEGRATION_MODE_ACCUMULATION = "0"

def _add_path_nodes(parent: ET.Element, tag: str, seq_root: Path, file_path: Path):
    node = ET.SubElement(parent, tag)
    try:
        if file_path.is_relative_to(seq_root):
            ET.SubElement(node, "RelativePath").text = str(file_path.relative_to(seq_root))
    except Exception:
        pass
    ET.SubElement(node, "AbsolutePath").text = str(file_path)
    return node

def create_sequator_files(sequator_path: Path, project_name: str, dark_files: List[Path], flat_file: Optional[Path], raw_lights_files: List[Path]):
    stack_root = ET.Element("SequatorProject", version="1.0")
    trail_root = ET.Element("SequatorProject", version="1.0")

    for f in raw_lights_files:
        for r in (stack_root, trail_root):
            _add_path_nodes(r, "StarImage", sequator_path, f)

    base_image_index = len(raw_lights_files) // 2 if raw_lights_files else 0
    base_image_file = raw_lights_files[base_image_index] if raw_lights_files else None

    for r, label, composition_mode in (
        (stack_root, "Stack", SEQ_COMPOSITION_MODE_STACK),
        (trail_root, "Trail", SEQ_COMPOSITION_MODE_TRAIL),
    ):
        if base_image_file:
            _add_path_nodes(r, "BaseImage", sequator_path, base_image_file)
        for d in dark_files:
            _add_path_nodes(r, "NoiseImage", sequator_path, d)
        ET.SubElement(r, "HomogenizeVignetting").text = XML_FALSE
        if flat_file and flat_file.exists():
            _add_path_nodes(r, "VignettingImage", sequator_path, flat_file)
            ET.SubElement(r, "HomogenizeVignetting").text = XML_TRUE

        output_path = sequator_path / f"{project_name}-{label}.tif"
        output = ET.SubElement(r, "Output")
        ET.SubElement(output, "RelativePath").text = str(output_path.name)

        ET.SubElement(r, "UnifyExposure").text = XML_FALSE
        ET.SubElement(r, "CompositionMode", max="1").text = composition_mode
        ET.SubElement(r, "IntegrationMode", max="3").text = SEQ_INTEGRATION_MODE_ACCUMULATION
        ET.SubElement(r, "SigmaIndex", max="4").text = "2"
        ET.SubElement(r, "FreezeGroundSelective").text = XML_TRUE
        ET.SubElement(r, "DumpAsLinear").text = XML_TRUE
        ET.SubElement(r, "TrailsMotionEffect").text = XML_FALSE
        ET.SubElement(r, "AutoBrightness").text = XML_TRUE
        ET.SubElement(r, "HDR").text = XML_TRUE
        ET.SubElement(r, "RemoveHotPixels").text = XML_TRUE
        ET.SubElement(r, "MergePixels").text = XML_FALSE
        ET.SubElement(r, "DistortionCorrection", max="2").text = SEQ_DISTORTION_CORRECTION_COMPLEX
        ET.SubElement(r, "ReducePollution").text = XML_TRUE
        ET.SubElement(r, "ReducePollutionMode", max="1").text = SEQ_REDUCE_POLLUTION_MODE_UNEVEN
        ET.SubElement(r, "ReducePollutionStrength", max="4").text = "2"
        ET.SubElement(r, "AggressiveSuppression").text = XML_FALSE
        ET.SubElement(r, "EnhanceStars").text = XML_TRUE
        ET.SubElement(r, "EnhanceStarsStrength", max="4").text = "3"
        star_bound = ET.SubElement(r, "StarBound")
        for t in ("X1","Y1","X2","Y2","X1","Y1","X2","Y2","Height"):
            ET.SubElement(star_bound, t).text = "0.000000"
        ET.SubElement(r, "SkyRegionMode", max="3").text = "0"
        ET.SubElement(r, "TimeLapse").text = XML_FALSE
        ET.SubElement(r, "TimeLapseFrames", max="30").text = "5"
        ET.SubElement(r, "ColorSpace", max="2").text = "0"

    for r, label in ((stack_root, "Stack"), (trail_root, "Trail")):
        tree = ET.ElementTree(r)
        try:
            ET.indent(tree)
        except Exception:
            pass
        tree.write(sequator_path / f"{project_name}-{label}.sep", encoding="utf-8", xml_declaration=True)
