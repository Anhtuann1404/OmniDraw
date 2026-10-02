"""Render a checked DEV schedule without post-solve geometry changes.

This diagnostic SVG is explicitly unvalidated by TV3; it is not a print/export
authorization or a product renderer. No HAL imports or physical actions.
"""

import json
import xml.etree.ElementTree as ET

from .geometry import check_selected_geometry
from .schedule_checker import check_schedule_cost
from .schemas import canonical_hash


def render_dev_svg(case, schedule, theta):
    check_selected_geometry(case, schedule)
    replay = check_schedule_cost(case, schedule, theta)
    variants = {(c.owner_index, v.candidate_id): v for c in case.candidates for v in c.variants}
    paths = []
    all_points = [case.boundary.p0_mm, case.boundary.p_end_mm]
    for action in schedule.actions:
        key = action.stroke.key()
        stroke = next(s for s in variants[key[:2]].strokes if s.stroke_id == key[2])
        points = list(reversed(stroke.polyline_mm)) if action.orientation == "reverse" else stroke.polyline_mm
        paths.append((action, points))
        all_points.extend(points)
    x0, y0 = min(p[0] for p in all_points) - 1, min(p[1] for p in all_points) - 1
    width, height = max(p[0] for p in all_points) + 1 - x0, max(p[1] for p in all_points) + 1 - y0
    root = ET.Element("svg", xmlns="http://www.w3.org/2000/svg",
                      viewBox=f"{x0} {y0} {width} {height}", width=f"{width}mm", height=f"{height}mm")
    ET.SubElement(root, "title").text = "OmniDraw DEV diagnostic — independent validation NOT_RUN"
    ET.SubElement(root, "metadata").text = json.dumps({
        "usage": "DEV_ONLY", "candidate_set_sha256": case.candidate_set_sha256,
        "schedule_sha256": canonical_hash(schedule.model_dump(mode="json")),
        "independent_validation": "NOT_RUN", "quality_gate": "PENDING",
        "J_mm": replay.J_mm, "N_cycle": replay.N_cycle, "cost_policy_id": replay.cost_policy_id}, allow_nan=False)
    group = ET.SubElement(root, "g", fill="none", stroke="black", **{"stroke-width": "0.1"})
    for order, (action, points) in enumerate(paths):
        commands = [f"{'M' if j == 0 else 'L'} {x} {y}" for j, (x, y) in enumerate(points)]
        ET.SubElement(group, "path", d=" ".join(commands), **{
            "data-order": str(order), "data-owner": str(action.stroke.owner_index),
            "data-candidate": action.stroke.candidate_id, "data-stroke": action.stroke.stroke_id,
            "data-orientation": action.orientation, "data-transition": action.transition})
    return ET.tostring(root, encoding="unicode") + "\n"
