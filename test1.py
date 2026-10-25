#!/usr/bin/env python3
"""
Generuje spirálovou cívku ve formátu KiCad PCB.

Příklad:
    & "C:/Users/ks1207/AppData/Local/Python/bin/python.exe" test1.py --outer-radius 20 --track-width 0.6 --turns 6 --center-x 60 --center-y 60

Výstup: spiral_antenna.kicad_pcb
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import List, Tuple


def point_on_spiral(
    radius_mm: float,
    angle_deg: float,
    center_x_mm: float,
    center_y_mm: float,
) -> Tuple[float, float]:
    angle_rad = math.radians(angle_deg)
    x = center_x_mm + radius_mm * math.cos(angle_rad)
    y = center_y_mm + radius_mm * math.sin(angle_rad)
    return x, y


def build_kicad_pcb(
    outer_radius_mm: float,
    track_width_mm: float,
    turns: float,
    center_x_mm: float = 60.0,
    center_y_mm: float = 60.0,
    pad_size_mm: float = 2.5,
) -> str:
    if outer_radius_mm <= 0:
        raise ValueError("Vnější poloměr musí být větší než 0.")
    if track_width_mm <= 0:
        raise ValueError("Tloušťka cesty musí být větší než 0.")
    if turns <= 0:
        raise ValueError("Počet závitů musí být větší než 0.")

    board_margin_mm = 15.0
    board_half_size = max(40.0, outer_radius_mm + board_margin_mm + pad_size_mm)

    lines: List[str] = [
        '(kicad_pcb (version 20211014) (generator "python-spiral-coil")',
        '  (general',
        '    (thickness 1.6)',
        '    (drawings 0)',
        '    (tracks 0)',
        '    (zones 0)',
        '    (modules 0)',
        '    (nets 0)',
        '  )',
        '  (layers',
        '    (0 "F.Cu" signal)',
        '    (31 "B.Cu" signal)',
        '  )',
        '  (setup',
        '    (pad_to_mask_clearance 0.0)',
        '    (solder_mask_min_width 0.0)',
        '  )',
        f'  (gr_line (start {center_x_mm - board_half_size:.4f} {center_y_mm - board_half_size:.4f}) (end {center_x_mm + board_half_size:.4f} {center_y_mm - board_half_size:.4f}) (layer "F.Cu") (width 0.1000))',
        f'  (gr_line (start {center_x_mm + board_half_size:.4f} {center_y_mm - board_half_size:.4f}) (end {center_x_mm + board_half_size:.4f} {center_y_mm + board_half_size:.4f}) (layer "F.Cu") (width 0.1000))',
        f'  (gr_line (start {center_x_mm + board_half_size:.4f} {center_y_mm + board_half_size:.4f}) (end {center_x_mm - board_half_size:.4f} {center_y_mm + board_half_size:.4f}) (layer "F.Cu") (width 0.1000))',
        f'  (gr_line (start {center_x_mm - board_half_size:.4f} {center_y_mm + board_half_size:.4f}) (end {center_x_mm - board_half_size:.4f} {center_y_mm - board_half_size:.4f}) (layer "F.Cu") (width 0.1000))',
    ]

    total_turns = turns * 2.0 * math.pi
    start_radius = 0.5 * max(track_width_mm, 0.2)
    end_radius = outer_radius_mm
    angle_step_deg = 2.0

    previous_point = None
    for i in range(int(total_turns / math.radians(angle_step_deg)) + 1):
        angle_deg = i * angle_step_deg
        if angle_deg > 360.0 * turns:
            angle_deg = 360.0 * turns
        radius = start_radius + (end_radius - start_radius) * (angle_deg / (360.0 * turns))
        x, y = point_on_spiral(radius, angle_deg, center_x_mm, center_y_mm)

        if previous_point is not None:
            x0, y0 = previous_point
            lines.append(
                f'  (gr_line (start {x0:.4f} {y0:.4f}) (end {x:.4f} {y:.4f}) (layer "F.Cu") (width {track_width_mm:.4f}))'
            )
        previous_point = (x, y)

    # Start pad and end pad for coil connection as valid KiCad modules
    start_pad_x = center_x_mm + (start_radius * 0.5) * math.cos(math.radians(0.0))
    start_pad_y = center_y_mm + (start_radius * 0.5) * math.sin(math.radians(0.0))
    end_x, end_y = point_on_spiral(end_radius, 360.0 * turns, center_x_mm, center_y_mm)

    lines.append(f'  (module "spiral_start" (layer "F.Cu") (tedit 0) (at {start_pad_x:.4f} {start_pad_y:.4f})')
    lines.append('    (descr "Start pad")')
    lines.append(f'    (pad 1 smd rect (at 0 0) (size {pad_size_mm:.4f} {pad_size_mm:.4f}) (layers "F.Cu" "F.Mask"))')
    lines.append('  )')

    lines.append(f'  (module "spiral_end" (layer "F.Cu") (tedit 0) (at {end_x:.4f} {end_y:.4f})')
    lines.append('    (descr "End pad")')
    lines.append(f'    (pad 2 smd rect (at 0 0) (size {pad_size_mm:.4f} {pad_size_mm:.4f}) (layers "F.Cu" "F.Mask"))')
    lines.append('  )')

    lines.append(')')
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Vygeneruje spirálovou cívku ve formátu KiCad PCB."
    )
    parser.add_argument("--outer-radius", type=float, required=True, help="Vnější poloměr spirály v mm.")
    parser.add_argument("--track-width", type=float, required=True, help="Tloušťka cesty v mm.")
    parser.add_argument("--turns", type=float, default=6.0, help="Počet závitů spirály.")
    parser.add_argument("--center-x", type=float, default=60.0, help="Střed X v mm.")
    parser.add_argument("--center-y", type=float, default=60.0, help="Střed Y v mm.")
    parser.add_argument("--pad-size", type=float, default=2.5, help="Velikost padů pro přívod v mm.")
    parser.add_argument("--output", type=str, default="spiral_antenna.kicad_pcb", help="Výstupní soubor KiCad PCB.")

    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.write_text(
        build_kicad_pcb(
            outer_radius_mm=args.outer_radius,
            track_width_mm=args.track_width,
            turns=args.turns,
            center_x_mm=args.center_x,
            center_y_mm=args.center_y,
            pad_size_mm=args.pad_size,
        ),
        encoding="utf-8",
    )

    print(f"Soubor vytvořen: {output_path.resolve()}")
    print("Otevři ho v KiCad -> PCB Editor a spirála se zobrazí.")


if __name__ == "__main__":
    main()
