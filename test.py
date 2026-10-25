#!/usr/bin/env python3
"""
Generuje kruhovou anténu s mezerou pro přívod ve formátu KiCad PCB.

Příklad:
    python test.py --min-diameter 20 --trace-width 0.3 --gap 0.2 --rings 6 --feed-gap-deg 30 --feed-angle-deg 90

Výstup: ring_antenna.kicad_pcb
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Tuple


def point_on_circle(
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
    min_diameter_mm: float,
    trace_width_mm: float,
    gap_mm: float,
    rings_count: int,
    feed_gap_deg: float = 30.0,
    feed_angle_deg: float = 90.0,
    center_x_mm: float = 0.0,
    center_y_mm: float = 0.0,
) -> str:
    if min_diameter_mm <= 0:
        raise ValueError("Minimální průměr musí být větší než 0.")
    if trace_width_mm <= 0:
        raise ValueError("Tloušťka cesty musí být větší než 0.")
    if gap_mm < 0:
        raise ValueError("Odstup cesty nesmí být záporný.")
    if rings_count <= 0:
        raise ValueError("Počet kruhů musí být větší než 0.")
    if feed_gap_deg <= 0 or feed_gap_deg >= 360:
        raise ValueError("Úhel mezery pro přívod musí být v rozmezí 0 až 360 stupňů.")

    board_margin_mm = 15.0
    board_size_x_mm = max(40.0, (rings_count * (trace_width_mm + gap_mm) + min_diameter_mm) + board_margin_mm * 2.0)
    board_size_y_mm = board_size_x_mm

    lines = [
        "(kicad_pcb (version 20211014) (generator \"python-ring-antenna\")",
        "  (general",
        "    (thickness 1.6)",
        "    (drawings 0)",
        "    (tracks 0)",
        "    (zones 0)",
        "    (modules 0)",
        "    (nets 0)",
        "  )",
        "  (layers",
        "    (0 \"F.Cu\" signal)",
        "    (31 \"B.Cu\" signal)",
        "  )",
        "  (setup",
        "    (pad_to_mask_clearance 0.0)",
        "    (solder_mask_min_width 0.0)",
        "  )",
        f"  (gr_line (start {center_x_mm - board_size_x_mm / 2.0:.4f} {center_y_mm - board_size_y_mm / 2.0:.4f}) (end {center_x_mm + board_size_x_mm / 2.0:.4f} {center_y_mm - board_size_y_mm / 2.0:.4f}) (layer \"F.Cu\") (width 0.1000))",
        f"  (gr_line (start {center_x_mm + board_size_x_mm / 2.0:.4f} {center_y_mm - board_size_y_mm / 2.0:.4f}) (end {center_x_mm + board_size_x_mm / 2.0:.4f} {center_y_mm + board_size_y_mm / 2.0:.4f}) (layer \"F.Cu\") (width 0.1000))",
        f"  (gr_line (start {center_x_mm - board_size_x_mm / 2.0:.4f} {center_y_mm + board_size_y_mm / 2.0:.4f}) (end {center_x_mm + board_size_x_mm / 2.0:.4f} {center_y_mm + board_size_y_mm / 2.0:.4f}) (layer \"F.Cu\") (width 0.1000))",
        f"  (gr_line (start {center_x_mm - board_size_x_mm / 2.0:.4f} {center_y_mm - board_size_y_mm / 2.0:.4f}) (end {center_x_mm - board_size_x_mm / 2.0:.4f} {center_y_mm + board_size_y_mm / 2.0:.4f}) (layer \"F.Cu\") (width 0.1000))",
    ]

    initial_radius = min_diameter_mm / 2.0
    step_deg = 2.0

    for ring_index in range(rings_count):
        radius = initial_radius + ring_index * (trace_width_mm + gap_mm)
        start_angle = feed_angle_deg + feed_gap_deg / 2.0
        end_angle = feed_angle_deg + 360.0 - feed_gap_deg / 2.0

        previous_point = None
        for angle in [start_angle + i * step_deg for i in range(int((end_angle - start_angle) / step_deg) + 1)]:
            if angle > 360:
                angle -= 360
            x, y = point_on_circle(radius, angle, center_x_mm, center_y_mm)
            if previous_point is not None:
                x0, y0 = previous_point
                lines.append(
                    f"  (gr_line (start {x0:.4f} {y0:.4f}) (end {x:.4f} {y:.4f}) (layer \"F.Cu\") (width {trace_width_mm:.4f}))"
                )
            previous_point = (x, y)

    # Krátký přívodový vývod ve směru mezery
    feed_angle_rad = math.radians(feed_angle_deg)
    feed_x_outer = center_x_mm + (initial_radius + 0.5 * trace_width_mm) * math.cos(feed_angle_rad)
    feed_y_outer = center_y_mm + (initial_radius + 0.5 * trace_width_mm) * math.sin(feed_angle_rad)
    feed_x_inner = center_x_mm + 0.5 * trace_width_mm * math.cos(feed_angle_rad)
    feed_y_inner = center_y_mm + 0.5 * trace_width_mm * math.sin(feed_angle_rad)
    lines.append(
        f"  (gr_line (start {feed_x_inner:.4f} {feed_y_inner:.4f}) (end {feed_x_outer:.4f} {feed_y_outer:.4f}) (layer \"F.Cu\") (width {trace_width_mm:.4f}))"
    )

    lines.append(")")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Vygeneruje kruhovou anténu s mezerou pro přívod ve formátu KiCad PCB."
    )
    parser.add_argument("--min-diameter", type=float, required=True, help="Minimální průměr antény v mm.")
    parser.add_argument("--trace-width", type=float, required=True, help="Tloušťka cesty v mm.")
    parser.add_argument("--gap", type=float, required=True, help="Vzdálenost mezi kruhy v mm.")
    parser.add_argument("--rings", type=int, required=True, help="Počet kruhů.")
    parser.add_argument("--feed-gap-deg", type=float, default=30.0, help="Šířka mezery pro přívod v stupních.")
    parser.add_argument("--feed-angle-deg", type=float, default=90.0, help="Směr mezery pro přívod v stupních.")
    parser.add_argument(
        "--output",
        type=str,
        default="ring_antenna.kicad_pcb",
        help="Výstupní soubor KiCad PCB.",
    )
    parser.add_argument("--center-x", type=float, default=60.0, help="Střed X v mm.")
    parser.add_argument("--center-y", type=float, default=60.0, help="Střed Y v mm.")

    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.write_text(
        build_kicad_pcb(
            min_diameter_mm=args.min_diameter,
            trace_width_mm=args.trace_width,
            gap_mm=args.gap,
            rings_count=args.rings,
            feed_gap_deg=args.feed_gap_deg,
            feed_angle_deg=args.feed_angle_deg,
            center_x_mm=args.center_x,
            center_y_mm=args.center_y,
        ),
        encoding="utf-8",
    )

    print(f"Soubor vytvořen: {output_path.resolve()}")
    print("Otevři ho v KiCad -> PCB Editor a rozložení se zobrazí.")


if __name__ == "__main__":
    main()
