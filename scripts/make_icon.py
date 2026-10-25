"""Generate custom_components/heads_up/brand/icon.png (256x256, no dependencies).

A banner with an exclamation mark on a rounded square. Run: `python scripts/make_icon.py`.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

SIZE = 256
SUPER = 4  # samples per pixel side
BLUE = (3, 102, 214)
WHITE = (255, 255, 255)
AMBER = (245, 166, 35)
OUT = Path(__file__).resolve().parent.parent / "custom_components/heads_up/brand/icon.png"


def in_round_rect(x: float, y: float, x0: float, y0: float, x1: float, y1: float, r: float) -> bool:
    if not (x0 <= x <= x1 and y0 <= y <= y1):
        return False
    cx = min(max(x, x0 + r), x1 - r)
    cy = min(max(y, y0 + r), y1 - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def sample(x: float, y: float) -> tuple[int, int, int, int]:
    if not in_round_rect(x, y, 0, 0, SIZE, SIZE, 52):
        return (0, 0, 0, 0)
    colour = BLUE
    if in_round_rect(x, y, 32, 80, 224, 176, 22):  # the banner
        colour = WHITE
        if in_round_rect(x, y, 56, 98, 70, 140, 7) or (x - 63) ** 2 + (y - 156) ** 2 <= 9**2:
            colour = AMBER  # exclamation mark
        elif in_round_rect(x, y, 92, 100, 200, 116, 8) or in_round_rect(x, y, 92, 138, 170, 154, 8):
            colour = BLUE  # two lines of text
    return (*colour, 255)


def pixel(px: int, py: int) -> bytes:
    acc = [0, 0, 0, 0]
    for sy in range(SUPER):
        for sx in range(SUPER):
            r, g, b, a = sample(px + (sx + 0.5) / SUPER, py + (sy + 0.5) / SUPER)
            acc[0] += r * a
            acc[1] += g * a
            acc[2] += b * a
            acc[3] += a
    n = SUPER * SUPER
    alpha = acc[3] // n
    if acc[3] == 0:
        return bytes(4)
    return bytes([acc[0] // acc[3], acc[1] // acc[3], acc[2] // acc[3], alpha])


def chunk(kind: bytes, data: bytes) -> bytes:
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))


def main() -> None:
    rows = b"".join(b"\x00" + b"".join(pixel(px, py) for px in range(SIZE)) for py in range(SIZE))
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows, 9))
        + chunk(b"IEND", b"")
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(png)
    print(f"wrote {OUT} ({len(png)} bytes)")


main()
