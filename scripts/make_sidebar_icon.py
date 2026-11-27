"""Generate custom_components/heads_up/frontend/heads-up-icons.js (no dependencies).

Home Assistant draws an icon as one path, filled with the nonzero rule. The brand mark is three
filled outlines in the black monochrome SVG of the brand kit, drawn there with the even-odd rule.
This moves them onto a 24x24 grid and turns every hole against its outline, so both rules give the
same picture. Run: `python scripts/make_sidebar_icon.py`.
"""

from __future__ import annotations

import re
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT / "docs/brand/Heads_up_Complete_Brand_Kit/02_Icons/Monochrome-Black/monochrome_black.svg"
)
OUT = ROOT / "custom_components/heads_up/frontend/heads-up-icons.js"
GRID = 24.0
CONTENT = 21.5  # the longer side of the mark on the grid
PARTS = ("house", "bell", "clapper")
SAMPLES = 16  # points per curve, for the size and direction of an outline

Point = tuple[float, float]
Segment = list[Point]  # one point: a line; three points: a cubic curve
Outline = tuple[Point, list[Segment]]  # start, segments; every outline is closed


def parse(d: str) -> list[Outline]:
    """Closed outlines of a path that uses the absolute commands M, L, C and Z."""
    tokens = re.findall(r"[A-Za-z]|-?\d*\.?\d+", d)
    outlines: list[Outline] = []
    start: Point | None = None
    segments: list[Segment] = []
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
                if start is None:
                    raise ValueError("Z without an outline")
                if segments[-1][-1] != start:
                    segments.append([start])
                outlines.append((start, segments))
                start, segments = None, []
                continue
        if command == "M" and start is None:
            start = take()
            command = "L"
        elif command == "L":
            segments.append([take()])
        elif command == "C":
            segments.append([take(), take(), take()])
        else:
            raise ValueError(f"unsupported path command {command!r}")
    if start is not None:
        raise ValueError("open outline")
    return outlines


def flatten(outline: Outline) -> list[Point]:
    start, segments = outline
    points = [start]
    for segment in segments:
        control = [points[-1], *segment]
        for step in range(1, SAMPLES + 1):
            row = control
            t = step / SAMPLES
            while len(row) > 1:
                row = [
                    (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for a, b in pairwise(row)
                ]
            points.append(row[0])
    return points


def area(points: list[Point]) -> float:
    """Signed area; the sign is the direction of the outline."""
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in pairwise(points)) / 2


def contains(points: list[Point], point: Point) -> bool:
    x, y = point
    inside = False
    for (ax, ay), (bx, by) in pairwise(points):
        if (ay > y) != (by > y) and x < ax + (y - ay) / (by - ay) * (bx - ax):
            inside = not inside
    return inside


def reverse(outline: Outline) -> Outline:
    start, segments = outline
    ends = [start, *(segment[-1] for segment in segments)]
    turned = [[*segment[-2::-1], ends[index]] for index, segment in enumerate(segments)]
    return ends[-1], turned[::-1]


def orient(outlines: list[Outline]) -> list[Outline]:
    """Outlines at an even depth run one way, the holes in them the other way."""
    flat = [flatten(outline) for outline in outlines]
    result = []
    for index, outline in enumerate(outlines):
        depth = sum(contains(other, outline[0]) for i, other in enumerate(flat) if i != index)
        wanted = 1 if depth % 2 == 0 else -1
        result.append(outline if area(flat[index]) * wanted > 0 else reverse(outline))
    return result


def num(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def build() -> str:
    svg = SOURCE.read_text(encoding="utf-8")
    paths = dict(re.findall(r'<path id="([a-z]+)" d="([^"]+)"', svg))
    missing = [part for part in PARTS if part not in paths]
    if missing:
        raise ValueError(f"no path {missing} in {SOURCE}")
    outlines = orient([outline for part in PARTS for outline in parse(paths[part])])

    points = [point for outline in outlines for point in flatten(outline)]
    left, top = min(x for x, _ in points), min(y for _, y in points)
    right, bottom = max(x for x, _ in points), max(y for _, y in points)
    scale = CONTENT / max(right - left, bottom - top)
    dx = (GRID - (right - left) * scale) / 2 - left * scale
    dy = (GRID - (bottom - top) * scale) / 2 - top * scale

    def xy(point: Point) -> str:
        return f"{num(point[0] * scale + dx)} {num(point[1] * scale + dy)}"

    path = "".join(
        "M"
        + xy(start)
        + "".join(("C" if len(s) == 3 else "L") + " ".join(xy(p) for p in s) for s in segments)
        + "Z"
        for start, segments in outlines
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
