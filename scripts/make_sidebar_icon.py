"""Generate custom_components/heads_up/frontend/heads-up-icons.js (no dependencies).

Home Assistant draws an icon as one filled path. The brand mark is drawn with round strokes, so
this turns the strokes of the black monochrome SVG from the brand package into outlines on a
24x24 grid. Run: `python scripts/make_sidebar_icon.py`.
"""

from __future__ import annotations

import math
import re
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT / "docs/brand/heads_up_brand_package/icons/transparent"
    "/monochrome_black/monochrome_black.svg"
)
OUT = ROOT / "custom_components/heads_up/frontend/heads-up-icons.js"
GRID = 24.0
CONTENT = 21.5  # the longer side of the mark on the grid
PIECE = 1.0  # longest straight piece of a curve, in source units
SMOOTH = math.radians(20)  # a smaller turn needs no round join

Point = tuple[float, float]
Line = tuple[list[Point], bool]  # points, closed


def flatten(d: str) -> list[Line]:
    """Polylines of a path that uses the absolute commands M, L, C, Q and Z."""
    tokens = re.findall(r"[A-Za-z]|-?\d*\.?\d+", d)
    lines: list[Line] = []
    points: list[Point] = []
    command = ""
    index = 0

    def take() -> Point:
        nonlocal index
        point = (float(tokens[index]), float(tokens[index + 1]))
        index += 2
        return point

    while index < len(tokens):
        if tokens[index].isalpha():
            command = tokens[index]
            index += 1
            if command == "Z":
                lines.append((points, True))
                points = []
                continue
        if command == "M":
            if points:
                lines.append((points, False))
            points = [take()]
            command = "L"
        elif command == "L":
            points.append(take())
        elif command in ("C", "Q"):
            control = [points[-1], *(take() for _ in range(3 if command == "C" else 2))]
            steps = math.ceil(sum(math.dist(a, b) for a, b in pairwise(control)) / PIECE)
            for step in range(1, steps + 1):
                row = control
                t = step / steps
                while len(row) > 1:
                    row = [
                        (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                        for a, b in pairwise(row)
                    ]
                points.append(row[0])
        else:
            raise ValueError(f"unsupported path command {command!r}")
    if points:
        lines.append((points, False))
    return lines


def num(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def xy(point: Point) -> str:
    return f"{num(point[0])} {num(point[1])}"


def arc(radius: float, end: Point) -> str:
    return f"A{num(radius)} {num(radius)} 0 0 0 {xy(end)}"


def side(points: list[Point], radius: float, closed: bool) -> list[str]:
    """Path commands along one side of a polyline, starting with the first offset point."""
    pairs = list(pairwise([*points, *points[:1]] if closed else points))
    normals: list[Point] = []
    for a, b in pairs:
        length = math.dist(a, b)
        normals.append((-(b[1] - a[1]) / length, (b[0] - a[0]) / length))

    def shift(point: Point, normal: Point) -> Point:
        return (point[0] + normal[0] * radius, point[1] + normal[1] * radius)

    out = ["M" + xy(shift(pairs[0][0], normals[0]))]
    for index, ((_, end), normal) in enumerate(zip(pairs, normals, strict=True)):
        out.append("L" + xy(shift(end, normal)))
        if index == len(pairs) - 1 and not closed:
            break
        after = normals[(index + 1) % len(pairs)]
        cross = normal[0] * after[1] - normal[1] * after[0]
        turn = math.atan2(cross, normal[0] * after[0] + normal[1] * after[1])
        if abs(turn) < SMOOTH:
            out.append("L" + xy(shift(end, after)))
        elif turn < 0:  # outer side: round join
            out.append(arc(radius, shift(end, after)))
        else:  # inner side: through the corner, covered by the nonzero fill rule
            out.append("L" + xy(end))
            out.append("L" + xy(shift(end, after)))
    return out


def outline(points: list[Point], radius: float, closed: bool) -> str:
    if closed:  # two rings with opposite direction leave the inside empty
        return "".join([*side(points, radius, True), "Z", *side(points[::-1], radius, True), "Z"])
    forward = side(points, radius, False)
    back = side(points[::-1], radius, False)
    start = back[0][1:]
    end_cap = f"A{num(radius)} {num(radius)} 0 0 0 {start}"
    first = forward[0][1:]
    start_cap = f"A{num(radius)} {num(radius)} 0 0 0 {first}"
    return "".join([*forward, end_cap, *back[1:], start_cap, "Z"])


def clean(points: list[Point], closed: bool) -> list[Point]:
    kept = [points[0]]
    for point in points[1:]:
        if math.dist(point, kept[-1]) > 1e-3:
            kept.append(point)
    if closed and math.dist(kept[0], kept[-1]) <= 1e-3:
        kept.pop()
    return kept


def build() -> str:
    svg = SOURCE.read_text(encoding="utf-8")
    strokes = [
        (flatten(d), float(width))
        for d, width in re.findall(r'<path d="([^"]+)"[^>]*?stroke-width="([\d.]+)"', svg)
    ]
    if not strokes:
        raise ValueError(f"no stroked paths in {SOURCE}")
    edges = [
        (x - width / 2, y - width / 2, x + width / 2, y + width / 2)
        for lines, width in strokes
        for points, _ in lines
        for x, y in points
    ]
    left, top = min(e[0] for e in edges), min(e[1] for e in edges)
    right, bottom = max(e[2] for e in edges), max(e[3] for e in edges)
    scale = CONTENT / max(right - left, bottom - top)
    dx = (GRID - (right - left) * scale) / 2 - left * scale
    dy = (GRID - (bottom - top) * scale) / 2 - top * scale

    path = "".join(
        outline(
            clean([(x * scale + dx, y * scale + dy) for x, y in points], closed),
            width * scale / 2,
            closed,
        )
        for lines, width in strokes
        for points, closed in lines
    )
    return f"""// Heads Up sidebar icon `heads_up:logo`, the one-color brand mark.
// Generated by scripts/make_sidebar_icon.py. Do not edit.
const PATH =
  "{path}";
window.customIcons = window.customIcons || {{}};
window.customIcons.heads_up = {{
  getIcon: async () => ({{ path: PATH }}),
  getIconList: async () => [{{ name: "logo" }}],
}};
"""


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT}")
