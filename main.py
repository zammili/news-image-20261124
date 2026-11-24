#!/usr/bin/env python3
"""THE WORLD LEDGER - front page for Tuesday 24 November 2026.

Draws a one-image newspaper front page summarising the day's world news.
Python 3 standard library only. The PNG encoder and the bitmap font below
are written by hand for this entry: no Pillow, no external images, no
network access at run time. Output is deterministic - run it twice and the
bytes are identical.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 768

WHITE = 255
LIGHT = 225
MID = 160
DARK = 80
BLACK = 0

# ---------------------------------------------------------------------------
# Canvas: a flat grayscale buffer, one byte per pixel.
# ---------------------------------------------------------------------------


class Canvas:
    def __init__(self, width, height, fill=WHITE):
        self.width = width
        self.height = height
        self.pixels = bytearray([fill]) * (width * height)

    def set(self, x, y, value):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y * self.width + x] = value

    def fill_rect(self, x, y, w, h, value):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        for yy in range(y0, y1):
            row = yy * self.width
            for xx in range(x0, x1):
                self.pixels[row + xx] = value

    def hline(self, x, y, w, value=BLACK, thick=1):
        self.fill_rect(x, y, w, thick, value)

    def vline(self, x, y, h, value=BLACK, thick=1):
        self.fill_rect(x, y, thick, h, value)

    def rect(self, x, y, w, h, value=BLACK, thick=1):
        self.hline(x, y, w, value, thick)
        self.hline(x, y + h - thick, w, value, thick)
        self.vline(x, y, h, value, thick)
        self.vline(x + w - thick, y, h, value, thick)

    def line(self, x0, y0, x1, y1, value=BLACK):
        """Bresenham line, for the chart's rising trend."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, value)
            self.set(x + 1, y, value)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy


# ---------------------------------------------------------------------------
# Bitmap font: hand-drawn 5x7 glyphs. '#' is ink, '.' is blank.
# ---------------------------------------------------------------------------

GLYPHS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "|": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
}

CHAR_W = 6  # 5 glyph columns + 1 blank column
CHAR_H = 7


def text_width(text, scale):
    return len(text) * CHAR_W * scale


def draw_glyph(canvas, x, y, glyph, scale, value=BLACK):
    for row, bits in enumerate(glyph):
        for col, ch in enumerate(bits):
            if ch == "#":
                canvas.fill_rect(
                    x + col * scale, y + row * scale, scale, scale, value
                )


def draw_text(canvas, x, y, text, scale, value=BLACK):
    cx = x
    for ch in text:
        glyph = GLYPHS.get(ch.upper(), GLYPHS["?"])
        draw_glyph(canvas, cx, y, glyph, scale, value)
        cx += CHAR_W * scale
    return cx - x


def draw_text_centered(canvas, cx, y, text, scale, value=BLACK):
    w = text_width(text, scale)
    draw_text(canvas, cx - w // 2, y, text, scale, value)
    return w


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width px."""
    unit = CHAR_W * scale
    max_chars = max(1, max_width // unit)
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            trial = word if not current else current + " " + word
            if len(trial) <= max_chars:
                current = trial
            else:
                if current:
                    lines.append(current)
                # A single over-long word is hard-split.
                while len(word) > max_chars:
                    lines.append(word[:max_chars])
                    word = word[max_chars:]
                current = word
        if current:
            lines.append(current)
    return lines


def draw_paragraph(canvas, x, y, text, max_width, scale, line_gap=4, value=BLACK):
    lines = wrap_text(text, max_width, scale)
    line_height = CHAR_H * scale + line_gap
    for i, line in enumerate(lines):
        draw_text(canvas, x, y + i * line_height, line, scale, value)
    return len(lines)


# ---------------------------------------------------------------------------
# Minimal PNG writer: grayscale, 8-bit, no filtering.
# ---------------------------------------------------------------------------


def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(canvas, path):
    raw = bytearray()
    for y in range(canvas.height):
        raw.append(0)  # filter type 0 (none)
        start = y * canvas.width
        raw += canvas.pixels[start:start + canvas.width]
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 0, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += _chunk(b"IHDR", ihdr)
    data += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)


# ---------------------------------------------------------------------------
# The front page. Vertical budget (768 px tall):
#   masthead 22-78, rules + date 88-128, lead headline 140-189,
#   subhead 200-236, lead row 248-374, markets strip 386-438,
#   rule 450, side stories 464-666, rule 678, ticker 690-748.
# ---------------------------------------------------------------------------

MARKETS = [
    ("S&P 500", "+4.73%"),
    ("NASDAQ", "+6.51%"),
    ("KOSPI", "+6.00%"),
    ("NIKKEI", "+3.91%"),
]


def draw_chart(canvas, x, y, w, h):
    """Bar chart of the day's index jumps, drawn with plain rectangles."""
    canvas.rect(x, y, w, h, BLACK, 2)
    draw_text(canvas, x + 12, y + 8, "MARKETS SURGE ON THE NEWS", 1)
    base = y + h - 34
    top = y + 34
    canvas.hline(x + 10, base, w - 20, BLACK, 2)
    canvas.vline(x + 10, top, base - top, BLACK, 2)
    values = [4.73, 6.51, 6.00, 3.91]
    labels = ["S&P 500", "NASDAQ", "KOSPI", "NIKKEI"]
    max_v = 7.0
    slot = (w - 40) // 4
    bar_w = 44
    tops = []
    for i, (value, label) in enumerate(zip(values, labels)):
        bar_h = int((base - top - 8) * value / max_v)
        bx = x + 24 + i * slot
        by = base - bar_h
        tops.append((bx + bar_w // 2, by))
        canvas.fill_rect(bx, by, bar_w, bar_h, DARK)
        canvas.rect(bx, by, bar_w, bar_h, BLACK, 1)
        draw_text_centered(canvas, bx + bar_w // 2, by - 14,
                           "+%.2f%%" % value, 1)
        draw_text_centered(canvas, bx + bar_w // 2, base + 6, label, 1)
    # Rising trend line across the bar tops.
    for i in range(1, len(tops)):
        canvas.line(tops[i - 1][0], tops[i - 1][1], tops[i][0], tops[i][1])
    draw_text(canvas, x + 12, y + h - 14,
              "ONE-DAY MOVE, TUESDAY 24 NOVEMBER 2026", 1, DARK)


def draw_markets_strip(canvas, x, y, w, h):
    canvas.rect(x, y, w, h, BLACK, 2)
    title = "MARKETS AT A GLANCE"
    draw_text(canvas, x + 12, y + h // 2 - 7, title, 2)
    rest_x = x + 12 + text_width(title, 2) + 24
    rest_w = x + w - 12 - rest_x
    slot = rest_w // len(MARKETS)
    for i, (name, change) in enumerate(MARKETS):
        entry = "%s %s" % (name, change)
        ex = rest_x + i * slot
        draw_text(canvas, ex, y + h // 2 - 7, entry, 2)
        if i:
            canvas.vline(ex - 10, y + 10, h - 20, LIGHT, 1)


def draw_story_row(canvas, x, y, w, kicker, headline, body):
    """One full-width story row: kicker + headline, then wrapped body."""
    draw_text(canvas, x, y, kicker + " -", 1, DARK)
    draw_text(canvas, x + text_width(kicker + " - ", 1), y, headline, 2)
    draw_paragraph(canvas, x, y + 20, body, w, 2, line_gap=2)


def build():
    c = Canvas(WIDTH, HEIGHT)
    c.rect(6, 6, WIDTH - 12, HEIGHT - 12, BLACK, 3)

    # --- Masthead -------------------------------------------------------
    draw_text_centered(c, WIDTH // 2, 22, "THE WORLD LEDGER", 8)
    c.hline(24, 88, WIDTH - 48, BLACK, 3)
    draw_text(c, 26, 98, "NO. 328", 2)
    draw_text_centered(c, WIDTH // 2, 96, "TUESDAY 24 NOVEMBER 2026", 3)
    price = "PRICE: FREE"
    draw_text(c, WIDTH - 26 - text_width(price, 2), 98, price, 2)
    c.hline(24, 128, WIDTH - 48, BLACK, 2)

    # --- Lead story -----------------------------------------------------
    draw_text(c, 24, 140, "LEAD STORY", 1, DARK)
    draw_text(c, 24, 152, "HUANG IS BACK", 7)
    draw_paragraph(
        c, 24, 212,
        "NVIDIA REINSTATES ITS FOUNDER-CHIEF AFTER PRESIDENT TRUMP "
        "INTERVENES IN THE BOARDROOM COUP.",
        WIDTH - 48, 2, line_gap=3,
    )

    lead_body = (
        "Nvidia reinstated Jensen Huang as chief executive less than two "
        "weeks after he was forced out, after President Donald Trump "
        "intervened. Markets surged on the news: the S&P 500 jumped "
        "4.73%, the Nasdaq soared 6.51%, Seoul rose 6% and the Nikkei "
        "climbed 3.91%."
    )
    draw_paragraph(c, 24, 248, lead_body, 520, 2, line_gap=4)

    # Chart sits right of the lead body.
    draw_chart(c, 580, 248, 420, 126)

    # Markets strip under the lead row.
    draw_markets_strip(c, 24, 386, WIDTH - 48, 52)

    c.hline(24, 450, WIDTH - 48, BLACK, 2)

    # --- Three side stories, full-width rows -----------------------------
    draw_story_row(
        c, 24, 464, WIDTH - 48, "MIDDLE EAST",
        "IRAN STANDOFF DEEPENS",
        "JD Vance and Secretary of State Marco Rubio met Qatar's prime "
        "minister at the White House as Iran vowed to use all tools to "
        "confront the US naval blockade. Netanyahu pressed President "
        "Trump to resume strikes on Iran.",
    )
    draw_story_row(
        c, 24, 532, WIDTH - 48, "GAZA",
        "GAZA STRIKE KILLS HAMAS SECURITY CHIEF",
        "An Israeli airstrike killed Hamas internal security chief Naeem "
        "Abu Nahel and six others in Gaza City on Tuesday, officials "
        "said, as the fragile ceasefire came under fresh strain.",
    )
    draw_story_row(
        c, 24, 600, WIDTH - 48, "UKRAINE / LIBYA",
        "UKRAINE DRONES HIT RUSSIAN SHIPS OFF LIBYA",
        "Ukraine confirmed its naval drones struck Russian ships off "
        "Libya, hitting the corvette Merkury. The UN mission in Libya "
        "called for an independent investigation into the attack.",
    )

    # --- Ticker ----------------------------------------------------------
    c.hline(24, 678, WIDTH - 48, BLACK, 2)
    ticker = (
        "COP31 CLIMATE TALKS IN ANTALYA END WITHOUT A DEAL | NATO CHIEF "
        "MARK RUTTE VOWS TO DEFEND SPACE AFTER REPORTS RUSSIA WAS "
        "PREPARING A NUCLEAR-ARMED SATELLITE | 5.6-MAGNITUDE QUAKE "
        "STRIKES NEPAL NEAR THE CHINA BORDER | UK RECORDS HIGHEST ANNUAL "
        "HEAT DEATHS: 5,258 IN SUMMER 2026"
    )
    draw_text(c, 24, 690, "THE WIRE", 1, DARK)
    draw_paragraph(c, 24, 704, ticker, WIDTH - 48, 1, line_gap=3, value=DARK)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    canvas = build()
    write_png(canvas, path)
    print("wrote %s (%dx%d)" % (path, WIDTH, HEIGHT))


if __name__ == "__main__":
    main()
