#!/usr/bin/env python3
"""The Tuesday Globe -- Tuesday 24 November 2026 in one image.

Draws a newspaper front page, pixel by pixel, with the Python 3
standard library only. No network, no photographs, no stock imagery.
Deterministic: running it twice writes byte-identical PNG bytes.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

W, H = 1024, 768
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
PATH = os.path.join(OUT, "entry.png")

PAPER = (250, 246, 235)
INK = (22, 22, 22)
RED = (178, 34, 34)
BLUE = (28, 68, 128)
GREY = (110, 108, 100)
GREEN = (46, 190, 110)
DARKGREEN = (18, 54, 46)
GRID = (36, 84, 68)
GOLD = (200, 170, 60)

# ---------------------------------------------------------------- canvas
buf = bytearray(W * H * 3)
for i in range(W * H):
    buf[i * 3:i * 3 + 3] = bytes(PAPER)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i:i + 3] = bytes(c)


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_px(xx, yy, c)


def hline(x, y, w, c):
    rect(x, y, w, 1, c)


def vline(x, y, h, c):
    rect(x, y, 1, h, c)


def line(x0, y0, x1, y1, c):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        set_px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def thick_line(x0, y0, x1, y1, c, t=3):
    for dx in range(-(t // 2), t // 2 + 1):
        for dy in range(-(t // 2), t // 2 + 1):
            line(x0 + dx, y0 + dy, x1 + dx, y1 + dy, c)


def tri(x0, y0, x1, y1, x2, y2, c):
    # filled triangle via horizontal scanlines
    pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = pts
    for yy in range(ay, cy + 1):
        if yy < by:
            t1 = (yy - ay) / max(1, by - ay)
            xa = ax + (bx - ax) * t1
        else:
            t1 = (yy - by) / max(1, cy - by)
            xa = bx + (cx - bx) * t1
        t2 = (yy - ay) / max(1, cy - ay)
        xb = ax + (cx - ax) * t2
        x_lo, x_hi = int(min(xa, xb)), int(max(xa, xb))
        hline(x_lo, yy, x_hi - x_lo + 1, c)


# ---------------------------------------------------------------- 5x7 font
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}
CHAR_W = 6  # 5 px glyph + 1 px gap


def text_w(s, scale):
    return len(s) * CHAR_W * scale - scale


def draw_text(x, y, s, scale, c):
    s = s.upper()
    for ci, ch in enumerate(s):
        g = FONT.get(ch, FONT["?"])
        ox = x + ci * CHAR_W * scale
        for r in range(7):
            for cc in range(5):
                if g[r][cc] == "1":
                    rect(ox + cc * scale, y + r * scale, scale, scale, c)
    return x + text_w(s, scale)


def draw_centered(y, s, scale, c):
    draw_text((W - text_w(s, scale)) // 2, y, s, scale, c)


def wrap(s, width_px, scale):
    words = s.split(" ")
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if text_w(t, scale) <= width_px:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, width_px, scale, c, lh=None):
    lh = lh or (9 * scale)
    for ln in wrap(s, width_px, scale):
        draw_text(x, y, ln, scale, c)
        y += lh
    return y


# ---------------------------------------------------------------- masthead
hline(24, 14, W - 48, INK)
hline(24, 17, W - 48, INK)
draw_centered(28, "THE TUESDAY GLOBE", 6, INK)
hline(24, 78, W - 48, INK)
draw_text(24, 86, "NO. 328", 2, GREY)
draw_centered(86, "TUESDAY 24 NOVEMBER 2026", 2, RED)
draw_text(W - 24 - text_w("PRICE: ONE DAY'S NEWS", 2), 86,
          "PRICE: ONE DAY'S NEWS", 2, GREY)
hline(24, 104, W - 48, INK)
rect(24, 107, W - 48, 3, INK)

# ---------------------------------------------------------------- headline
draw_centered(122, "HUANG IS BACK", 6, INK)
draw_centered(172, "NVIDIA REINSTATES ITS CEO", 4, INK)
draw_centered(210, "AFTER PRESIDENT TRUMP INTERVENED, THE CHIPMAKER REVERSED THE SACKING -", 2, INK)
draw_centered(228, "MARKETS SURGED: S AND P 500 +4.73%, NASDAQ +6.51%, SEOUL +6%, NIKKEI +3.91%", 2, INK)

# ------------------------------------------------------- illustration panel
IX, IY, IW, IH = 24, 246, 976, 190
rect(IX, IY, IW, IH, DARKGREEN)
# horizontal grid lines
for gy in range(IY + 28, IY + IH - 34, 28):
    hline(IX, gy, IW, GRID)
# rising bars, two red dips on the way up
BAR_BASE = IY + 156
BAR_H = [36, 48, 42, 62, 55, 75, 68, 88, 80, 102, 95, 115, 108, 128, 120, 140]
BAR_RED = {2, 8}
for bi, bh in enumerate(BAR_H):
    bx = IX + 52 + bi * 56
    bc = (214, 84, 70) if bi in BAR_RED else GREEN
    rect(bx, BAR_BASE - bh, 40, bh, bc)
    rect(bx, BAR_BASE - bh, 40, 4, (220, 235, 220))
# small NVDA chip glyph, top left
CX, CY2 = IX + 16, IY + 12
rect(CX, CY2, 44, 44, GOLD)
rect(CX + 6, CY2 + 6, 32, 32, (30, 30, 30))
for px in range(CX + 8, CX + 40, 8):
    vline(px, CY2 - 6, 6, GOLD)
    vline(px, CY2 + 44, 6, GOLD)
for py in range(CY2 + 8, CY2 + 40, 8):
    hline(CX - 6, py, 6, GOLD)
    hline(CX + 44, py, 6, GOLD)
draw_text(CX + 10, CY2 + 18, "NVDA", 1, (240, 240, 240))
# thick white arrow climbing from the panel origin to the top right,
# now starting at the bottom-left corner so it reads as one trend line
thick_line(IX + 36, BAR_BASE + 4, IX + IW - 60, IY + 18, (250, 246, 235), 5)
tri(IX + IW - 60, IY + 18, IX + IW - 96, IY + 8, IX + IW - 92, IY + 38,
    (250, 246, 235))
# light strip at the bottom of the panel with the index moves
rect(IX, IY + IH - 32, IW, 32, (238, 232, 218))
draw_text(IX + 12, IY + IH - 24,
          "S AND P 500 +4.73%    NASDAQ +6.51%    KOSPI +6%    NIKKEI +3.91%",
          2, INK)
# caption bar under the picture
rect(IX, IY + IH - 2, IW, 2, INK)
draw_text(IX + 4, IY + IH + 8, "THE MARKET REACTION: WALL STREET SURGED AS NVIDIA REVERSED THE SACKING OF JENSEN HUANG.", 1, GREY)

# ---------------------------------------------------------------- columns
CY = 462
# left column: lead story
LX, LW = 24, 520
draw_text(LX, CY, "SANTA CLARA -", 2, RED)
y = para(LX, CY + 22,
          "Nvidia has reinstated Jensen Huang as chief executive less "
          "than two weeks after he was forced out, after President Trump "
          "intervened in the boardroom row.", LW, 2, INK)
y = para(LX, y + 8,
          "Markets surged on the news. The S and P 500 rose 4.73%, the "
          "Nasdaq jumped 6.51%, Seoul gained 6% and Tokyo's Nikkei "
          "climbed 3.91%.", LW, 2, INK)
# markets at a glance
hline(LX, y + 10, LW, GREY)
draw_text(LX, y + 18, "MARKETS AT A GLANCE", 2, RED)
draw_text(LX, y + 40, "S AND P 500 +4.73%    NASDAQ +6.51%", 1, INK)
draw_text(LX, y + 54, "KOSPI +6%    NIKKEI +3.91%", 1, INK)

# right column: three side stories
RX, RW = 580, 420
vline(560, CY, 232, GREY)
ry = CY
for kicker, head, body in [
    ("IRAN", "BLOCKADE STANDOFF AT WHITE HOUSE",
     "Vice President JD Vance and Secretary of State Marco Rubio met "
     "Qatar's prime minister at the White House. Iran vowed to use all "
     "tools to confront the blockade, and Netanyahu urged Trump to "
     "resume strikes."),
    ("GAZA", "STRIKE KILLS HAMAS SECURITY CHIEF",
     "An Israeli airstrike killed Hamas internal security chief Naeem "
     "Abu Nahel and six others in Gaza City on Tuesday, officials said."),
    ("UKRAINE", "DRONES HIT RUSSIAN SHIPS OFF LIBYA",
     "Ukraine confirmed its naval drones struck Russian ships off "
     "Libya, including the corvette Merkury. The UN mission in Libya "
     "called for an independent probe."),
]:
    draw_text(RX, ry, kicker, 2, RED)
    ry = para(RX, ry + 20, head, RW, 2, INK)
    ry = para(RX, ry + 4, body, RW, 1, INK, lh=10)
    ry += 6

# ---------------------------------------------------------------- ticker
TY = 706
rect(24, TY, W - 48, 44, INK)
draw_text(36, TY + 7, "COP31 ENDS WITHOUT A DEAL AFTER TWO DAYS OF OVERTIME", 2, (250, 246, 235))
draw_text(36, TY + 25, "NATO VOWS TO DEFEND SPACE AFTER REPORTS OF RUSSIAN NUCLEAR SATELLITE - 5.6 QUAKE HITS NEPAL - UK HEAT DEATHS HIT RECORD 5,258", 1, (200, 196, 182))
hline(24, TY + 50, W - 48, INK)
draw_centered(758, "THE TUESDAY GLOBE - TUESDAY 24 NOVEMBER 2026", 1, GREY)

# ---------------------------------------------------------------- write PNG
os.makedirs(OUT, exist_ok=True)


def chunk(kind, data):
    c = struct.pack(">I", len(data)) + kind + data
    return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


raw = b"".join(b"\x00" + bytes(buf[y * W * 3:(y + 1) * W * 3]) for y in range(H))
png = (b"\x89PNG\r\n\x1a\n"
       + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
       + chunk(b"IDAT", zlib.compress(raw, 9))
       + chunk(b"IEND", b""))
with open(PATH, "wb") as f:
    f.write(png)
print("wrote", PATH, len(png), "bytes")
