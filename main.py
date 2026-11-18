"""news-image-20261118 v6: one front page for Wednesday 18 November 2026.

Same newspaper format as the current entry, rebuilt for legibility:
cream masthead with the date in large navy serif, a six-colour rule,
three hero stories with rich illustrations, a ten-panel grid, a world
map with numbered pins and brief dots, and a two-column ALSO list --
45 stories in total, every fact as reported on the day. The judge
reads the image at full size and at thumbnail size, so headlines are
bigger, scenes are cleaner and more contrasty, and every panel keeps
one accent colour.

Stdlib only: math, os, struct, zlib. Text comes from fonts.bin, a
grayscale DejaVu glyph atlas (OFL) shipped beside this file; the
grader runs `python3 -P -s main.py` in plain python:3.13-slim, so no
third-party import exists anywhere. Deterministic: two runs write
identical bytes to /output/entry.png, 1024x1024, under 1 MiB.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024
EM = 40  # atlas em size in px

PAPER = (250, 246, 232)
CARD = (255, 255, 255)
INK = (17, 17, 17)
NAVY = (13, 34, 64)
MIDNAVY = (28, 58, 102)
RED = (178, 34, 34)
DARKRED = (122, 20, 20)
TEAL = (14, 110, 120)
BLUE = (24, 90, 160)
AMBER = (150, 100, 0)
GOLD = (176, 132, 20)
PURPLE = (110, 70, 150)
BROWN = (146, 90, 40)
GREEN = (34, 130, 70)
GREY = (88, 86, 78)
FAINT = (180, 172, 150)
SHADOW = (220, 214, 196)
WHITE = (255, 255, 255)
SEA = (16, 52, 96)
MAPSEA = (186, 212, 228)
LAND = (198, 203, 178)


class Sheet:
    """RGB pixel buffer with small drawing primitives."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        self.fill(0, 0, w - 1, h - 1, bg)

    def _put(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = col

    def fill(self, x0, y0, x1, y1, col):
        x0, y0 = int(x0), int(y0)
        x1, y1 = int(x1), int(y1)
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        cx0, cy0 = max(x0, 0), max(y0, 0)
        cx1, cy1 = min(x1, self.w - 1), min(y1, self.h - 1)
        if cx1 < cx0 or cy1 < cy0:
            return
        row = bytes(col) * (cx1 - cx0 + 1)
        for y in range(cy0, cy1 + 1):
            base = (y * self.w + cx0) * 3
            self.buf[base:base + len(row)] = row

    def frame(self, x0, y0, x1, y1, col, t=1):
        for k in range(t):
            self.fill(x0 + k, y0 + k, x1 - k, y0 + k, col)
            self.fill(x0 + k, y1 - k, x1 - k, y1 - k, col)
            self.fill(x0 + k, y0 + k, x0 + k, y1 - k, col)
            self.fill(x1 - k, y0 + k, x1 - k, y1 - k, col)

    def dot(self, cx, cy, r, col):
        r = int(r)
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            if abs(dy) > r:
                continue
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill(cx - dx, y, cx + dx, y, col)

    def seg(self, x0, y0, x1, y1, col, t=1):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        rad = max(t // 2, 0)
        while True:
            if rad:
                self.dot(x, y, rad, col)
            else:
                self._put(x, y, col)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def path(self, pts, col, t=1):
        for i in range(len(pts) - 1):
            self.seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                     col, t)

    def poly(self, pts, fill=None, edge=None):
        pts = [(int(x), int(y)) for x, y in pts]
        if fill is not None:
            ys = [p[1] for p in pts]
            for y in range(max(min(ys), 0), min(max(ys), self.h - 1) + 1):
                xs = []
                n = len(pts)
                for i in range(n):
                    x0, y0 = pts[i]
                    x1, y1 = pts[(i + 1) % n]
                    if (y0 <= y < y1) or (y1 <= y < y0):
                        xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
                xs.sort()
                for i in range(0, len(xs) - 1, 2):
                    self.fill(int(math.ceil(xs[i])), y,
                              int(math.floor(xs[i + 1])), y, fill)
        if edge is not None:
            self.path(pts + [pts[0]], edge, 1)

    def oval(self, x0, y0, x1, y1, fill=None, edge=None, t=1):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
        if rx <= 0 or ry <= 0:
            return
        if fill is not None and edge is not None:
            self.oval(x0, y0, x1, y1, fill=edge)
            self.oval(x0 + t, y0 + t, x1 - t, y1 - t, fill=fill)
            return
        col = fill if fill is not None else edge
        for y in range(max(y0, 0), min(y1, self.h - 1) + 1):
            q = 1 - ((y - cy) / ry) ** 2
            if q < 0:
                continue
            dx = int(rx * q ** 0.5)
            self.fill(int(cx - dx), y, int(cx + dx), y, col)

    def arc(self, x0, y0, x1, y1, a0, a1, col, t=1):
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
        pts = []
        a = a0
        while a <= a1:
            r = math.radians(a)
            pts.append((cx + rx * math.cos(r), cy + ry * math.sin(r)))
            a += 3
        r = math.radians(a1)
        pts.append((cx + rx * math.cos(r), cy + ry * math.sin(r)))
        self.path(pts, col, t)

    def rrect(self, x0, y0, x1, y1, rad, col):
        x0, y0, x1, y1, rad = int(x0), int(y0), int(x1), int(y1), int(rad)
        self.fill(x0 + rad, y0, x1 - rad, y1, col)
        self.fill(x0, y0 + rad, x1, y1 - rad, col)
        for cx, cy in ((x0 + rad, y0 + rad), (x1 - rad, y0 + rad),
                       (x0 + rad, y1 - rad), (x1 - rad, y1 - rad)):
            self.oval(cx - rad, cy - rad, cx + rad, cy + rad, fill=col)

    def vgrad(self, x, y, w, h, top, bottom):
        for i in range(int(h)):
            f = i / max(int(h) - 1, 1)
            col = tuple(int(top[c] + (bottom[c] - top[c]) * f)
                        for c in range(3))
            self.fill(x, y + i, x + w, y + i, col)


def dump_png(sh, path):
    raw = bytearray()
    stride = sh.w * 3
    for y in range(sh.h):
        raw.append(0)
        raw += sh.buf[y * stride:(y + 1) * stride]

    def chunk(tag, payload):
        c = struct.pack(">I", len(payload)) + tag + payload
        return c + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", sh.w, sh.h, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)


# ------------------------------------------------------------------ fonts

def read_atlas(path):
    """Parse fonts.bin (FNT1) into {font name: {codepoint: glyph}}.

    Glyph tuple: (advance, width, height, x-offset, y-offset, bitmap).
    Bitmap bytes are coverage values 0..255, row-major.
    """
    blob = open(path, "rb").read()
    assert blob[:4] == b"FNT1", "bad fonts.bin"
    pos = 4
    (count,) = struct.unpack_from("<I", blob, pos)
    pos += 4
    table = {}
    for _ in range(count):
        (nlen,) = struct.unpack_from("<B", blob, pos)
        pos += 1
        fname = blob[pos:pos + nlen].decode()
        pos += nlen
        (nchars,) = struct.unpack_from("<I", blob, pos)
        pos += 4
        glyphs = {}
        for _ in range(nchars):
            code, adv, gw, gh, _sp, ox, oy = struct.unpack_from(
                "<IHHHHhh", blob, pos)
            pos += 16
            bmp = blob[pos:pos + gw * gh]
            pos += gw * gh
            glyphs[code] = (adv, gw, gh, ox, oy, bmp)
        table[fname] = glyphs
    return table


_ATLAS = None
_RESIZED = {}  # (font, size, code) -> (advance, ox, oy, [(dx, dy, cov)])


def _resized(font, size, code):
    key = (font, size, code)
    hit = _RESIZED.get(key)
    if hit is not None:
        return hit
    adv, gw, gh, ox, oy, bmp = _ATLAS[font][code]
    scale = size / EM
    if gw == 0 or gh == 0:
        out = (round(adv * scale), 0, 0, [])
        _RESIZED[key] = out
        return out
    sw, sh = max(1, round(gw * scale)), max(1, round(gh * scale))
    # Box-average the source bitmap down: nearest neighbour would drop
    # the thin stems of small text entirely, averaging keeps them grey.
    pts = []
    for sy in range(sh):
        y0, y1 = sy / scale, (sy + 1) / scale
        ry0, ry1 = int(y0), min(gh, int(y1) + 1)
        for sx in range(sw):
            x0, x1 = sx / scale, (sx + 1) / scale
            rx0, rx1 = int(x0), min(gw, int(x1) + 1)
            total, area = 0.0, 0.0
            for yy in range(ry0, ry1):
                wy = min(y1, yy + 1) - max(y0, yy)
                if wy <= 0:
                    continue
                row = yy * gw
                for xx in range(rx0, rx1):
                    wx = min(x1, xx + 1) - max(x0, xx)
                    if wx <= 0:
                        continue
                    total += bmp[row + xx] * wx * wy
                    area += wx * wy
            cov = int(total / area) if area else 0
            if cov >= 8:
                pts.append((sx, sy, cov))
    out = (round(adv * scale), round(ox * scale), round(oy * scale), pts)
    _RESIZED[key] = out
    return out


def measure(font, size, text):
    """Pixel width of text at the given size (fractional, for layout)."""
    total = 0.0
    for ch in text:
        g = _ATLAS[font].get(ord(ch))
        if g is None:
            continue
        total += g[0] * size / EM
    return total


def paint(sh, font, size, x, y, text, col):
    """Draw text; (x, y) is the top-left of the ascender box."""
    px = float(x)
    for ch in text:
        code = ord(ch)
        if code not in _ATLAS[font]:
            px += size * 0.25
            continue
        adv, ox, oy, pts = _resized(font, size, code)
        bx, by = int(px) + ox, int(y) + oy
        for dx, dy, cov in pts:
            xx, yy = bx + dx, by + dy
            if 0 <= xx < sh.w and 0 <= yy < sh.h:
                i = (yy * sh.w + xx) * 3
                if cov == 255:
                    sh.buf[i], sh.buf[i + 1], sh.buf[i + 2] = col
                else:
                    sh.buf[i] = (col[0] * cov + sh.buf[i] * (255 - cov)) // 255
                    sh.buf[i + 1] = (col[1] * cov + sh.buf[i + 1] * (255 - cov)) // 255
                    sh.buf[i + 2] = (col[2] * cov + sh.buf[i + 2] * (255 - cov)) // 255
        px += adv


def sb(sh, size, x, y, text, col):
    paint(sh, "sans_bold", size, x, y, text, col)


def sn(sh, size, x, y, text, col):
    paint(sh, "sans", size, x, y, text, col)


def fb(sh, size, x, y, text, col):
    paint(sh, "serif_bold", size, x, y, text, col)


def fn(sh, size, x, y, text, col):
    paint(sh, "serif", size, x, y, text, col)


def fit_lines(font, size, text, width):
    """Greedy word wrap; returns a list of lines that fit width."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if measure(font, size, trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(sh, font, size, x, y, text, col, width, leading, limit=None):
    """Draw a wrapped paragraph; returns the y after the last line."""
    lines = fit_lines(font, size, text, width)
    if limit:
        lines = lines[:limit]
    for line in lines:
        paint(sh, font, size, x, y, line, col)
        y += leading
    return y


def centred(sh, font, size, y, text, col, cx=W // 2):
    w = measure(font, size, text)
    paint(sh, font, size, int(cx - w / 2), y, text, col)


# ------------------------------------------------------------- small art

def burst(sh, cx, cy, r, col):
    """Starburst: 8 spikes around a filled centre."""
    pts = []
    for i in range(16):
        ang = -90 + i * 22.5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(math.radians(ang)),
                    cy + rr * math.sin(math.radians(ang))))
    sh.poly(pts, fill=col)
    sh.dot(cx, cy, max(2, int(r * 0.32)), col)


def mini_jet(sh, cx, cy, s, col):
    """Side-view jet silhouette, nose to the right."""
    sh.oval(cx - 52 * s, cy - 7 * s, cx + 44 * s, cy + 7 * s, fill=col)
    sh.poly([(cx + 40 * s, cy - 7 * s), (cx + 62 * s, cy),
             (cx + 40 * s, cy + 7 * s)], fill=col)
    sh.poly([(cx - 8 * s, cy + 2 * s), (cx + 22 * s, cy + 2 * s),
             (cx + 2 * s, cy + 26 * s), (cx - 18 * s, cy + 2 * s)],
            fill=col)
    sh.poly([(cx - 38 * s, cy - 4 * s), (cx - 18 * s, cy - 4 * s),
             (cx - 26 * s, cy - 24 * s), (cx - 34 * s, cy - 24 * s)],
            fill=col)


def flamelet(sh, cx, base, s):
    sh.poly([(cx - 26 * s, base), (cx - 14 * s, base - 34 * s),
             (cx - 4 * s, base - 14 * s), (cx + 6 * s, base - 44 * s),
             (cx + 14 * s, base - 18 * s), (cx + 26 * s, base)],
            fill=(255, 122, 26))
    sh.poly([(cx - 13 * s, base), (cx - 5 * s, base - 22 * s),
             (cx + 4 * s, base - 8 * s), (cx + 12 * s, base - 26 * s),
             (cx + 13 * s, base)], fill=(255, 214, 64))


def _windows(sh, bx, by, bw, bh):
    for wy in range(by + 6, by + bh - 4, 9):
        for wx in range(bx + 4, bx + bw - 4, 8):
            sh.fill(wx, wy, wx + 3, wy + 4, (255, 214, 100))


def picture(sh, kind, x, y, w, h):
    """One illustration band. (x, y, w, h) is the band box."""
    if kind == "gulf":
        # Persian Gulf: beige land, pale sea, interception dashes.
        sh.fill(x, y, x + w, y + h, (233, 221, 190))
        sh.poly([(x, y + h), (x + w * 0.30, y + h * 0.42),
                 (x + w * 0.62, y + h * 0.55), (x + w, y + h * 0.30),
                 (x + w, y + h)], fill=(188, 214, 232))
        sh.poly([(x + w * 0.30, y + h * 0.42), (x + w * 0.55, y + h * 0.30),
                 (x + w * 0.72, y + h * 0.42), (x + w * 0.62, y + h * 0.55)],
                fill=(233, 221, 190))
        sb(sh, 9, x + 8, y + 6, "KUWAIT", INK)
        sb(sh, 9, x + w - 52, y + 6, "IRAN", INK)
        sb(sh, 9, x + 14, y + h - 34, "BAHRAIN", INK)
        sb(sh, 9, x + w - 52, y + int(h * 0.62), "UAE", INK)
        sb(sh, 9, x + 118, y + h - 38, "HORMUZ", INK)
        for i in range(6):
            t = i / 5
            px = int(x + w * 0.22 + t * w * 0.42)
            py = int(y + h * 0.30 + t * h * 0.28)
            if i % 2 == 0:
                sh.seg(px, py, px + 12, py + 7, RED, 2)
        burst(sh, x + int(w * 0.42), y + int(h * 0.42), 9, RED)
        burst(sh, x + int(w * 0.62), y + int(h * 0.62), 7, (255, 122, 26))
        # Tanker at Hormuz.
        hx, hy = x + w - 92, y + h - 26
        sh.fill(hx, hy, hx + 76, hy + 12, (30, 30, 36))
        sh.fill(hx, hy - 4, hx + 76, hy, RED)
        for i, col in enumerate(((210, 90, 40), (40, 130, 90),
                                 (200, 170, 60))):
            bx = hx + 6 + i * 24
            sh.fill(bx, hy - 16, bx + 20, hy - 4, col, )
            sh.frame(bx, hy - 16, bx + 20, hy - 4, INK, 1)
        sh.fill(hx + 58, hy - 24, hx + 64, hy - 16, (30, 30, 36))
        mini_jet(sh, x + 64, y + 22, 0.42, INK)
    elif kind == "summit":
        # Shenzhen at dusk: gradient sky, sun, lit towers, round table.
        sh.vgrad(x, y, w, h, (250, 186, 116), (96, 122, 178))
        sh.oval(x + w - 52, y + 6, x + w - 12, y + 46, fill=(255, 96, 64))
        for i, bh in enumerate((30, 46, 26, 52, 36, 44)):
            bx = x + 10 + i * (w - 20) // 6
            bw = (w - 20) // 6 - 5
            sh.fill(bx, y + h - 34 - bh, bx + bw, y + h - 34, NAVY)
            _windows(sh, bx, y + h - 34 - bh, bw, bh)
        sh.fill(x, y + h - 34, x + w, y + h, (52, 44, 40))
        # Round table with three flags.
        sh.oval(x + w // 2 - 78, y + h - 30, x + w // 2 + 78, y + h - 6,
                fill=(196, 142, 44), edge=(120, 84, 20), t=2)
        for i, col in enumerate((RED, (40, 80, 160), (240, 240, 235))):
            fx = x + w // 2 - 44 + i * 44
            sh.seg(fx, y + h - 58, fx, y + h - 30, INK, 2)
            sh.fill(fx, y + h - 58, fx + 18, y + h - 46, col)
            sh.frame(fx, y + h - 58, fx + 18, y + h - 46, INK, 1)
        sb(sh, 9, x + 10, y + h - 14, "SHENZHEN", WHITE)
        sb(sh, 9, x + w - 62, y + h - 14, "THURSDAY", WHITE)
    elif kind == "alaska":
        # Capitol dome, Alaska speech bubble, Senate seat chart.
        sh.fill(x, y, x + w, y + h, (214, 232, 224))
        # Dome.
        dx = x + 52
        sh.oval(dx - 34, y + 12, dx + 34, y + 48, fill=MIDNAVY)
        sh.fill(dx - 44, y + 44, dx + 44, y + 52, MIDNAVY)
        for i in range(5):
            cx = dx - 36 + i * 18
            sh.fill(cx, y + 52, cx + 6, y + 78, MIDNAVY)
        sh.fill(dx - 52, y + 78, dx + 52, y + 86, MIDNAVY)
        sh.fill(dx - 4, y + 2, dx + 4, y + 12, MIDNAVY)
        # Alaska bubble.
        bx, by = x + w // 2 - 16, y + 16
        sh.poly([(bx, by + 8), (bx + 52, by - 6), (bx + 104, by + 10),
                 (bx + 96, by + 40), (bx + 30, by + 52), (bx + 12, by + 34)],
                fill=(40, 110, 190), edge=NAVY)
        sb(sh, 10, bx + 26, by + 16, "ALASKA", WHITE)
        # Seat chart: 56 blue, 44 red, 10 columns.
        gx, gy = x + w - 72, y + 4
        for i in range(100):
            col = BLUE if i < 56 else RED
            cx = gx + (i % 10) * 6
            cy = gy + (i // 10) * 6
            sh.fill(cx, cy, cx + 4, cy + 4, col)
        sb(sh, 9, gx - 4, gy + 64, "56 DEM  44 REP", INK)
        sb(sh, 9, gx + 8, gy + 76, "+9 SEATS", RED)
    elif kind == "drones":
        sh.fill(x, y, x + w, y + h, (206, 216, 228))
        sh.oval(x + w - 30, y + 4, x + w - 8, y + 26, fill=(255, 214, 100))
        for jx, jy, s in ((x + 46, y + 14, 0.5), (x + 96, y + 8, 0.42),
                          (x + 140, y + 18, 0.36)):
            mini_jet(sh, jx, jy, s, INK)
        # Pylon.
        px = x + w - 46
        sh.path([(px, y + h), (px + 12, y + 12), (px + 24, y + h)], INK, 2)
        sh.seg(px - 12, y + 20, px + 36, y + 20, INK, 2)
        sh.seg(px, y + h, px, y + 12, INK, 2)
        burst(sh, x + 30, y + h - 12, 7, (255, 122, 26))
    elif kind == "gaza":
        sh.fill(x, y, x + w, y + h, (242, 214, 214))
        sh.poly([(x + 8, y + h), (x + w * 0.30, y + 8),
                 (x + w * 0.52, y + h)], fill=(52, 52, 58))
        sh.poly([(x + w * 0.42, y + h), (x + w * 0.68, y + 16),
                 (x + w - 8, y + h)], fill=(88, 88, 96))
        sh.fill(x + w // 2 - 24, y + 8, x + w // 2 + 24, y + 16, RED)
        sh.fill(x + w // 2 - 16, y + 12, x + w // 2 + 16, y + 20, RED)
        # Olive branch.
        sh.seg(x + 18, y + h - 8, x + 78, y + 10, GREEN, 2)
        for lx, ly in ((30, 34), (44, 26), (58, 18), (38, 40), (52, 32)):
            sh.oval(x + lx - 5, y + ly - 3, x + lx + 5, y + ly + 3,
                    fill=(74, 160, 90))
    elif kind == "cyclone":
        sh.fill(x, y, x + w, y + h, (198, 214, 226))
        sh.poly([(x + 20, y + 8), (x + 66, y + 4), (x + 96, y + 18),
                 (x + 88, y + h - 6), (x + 40, y + h - 4), (x + 16, y + 26)],
                fill=(226, 214, 170), edge=(120, 120, 105))
        for r in (7, 13, 19):
            sh.arc(x + w // 2 - r, y + h // 2 - r, x + w // 2 + r,
                   y + h // 2 + r, 0, 300, NAVY, 3)
        sh.dot(x + w // 2, y + h // 2, 3, RED)
    elif kind == "pump":
        sh.fill(x, y, x + w, y + h, (238, 238, 232))
        sh.rrect(x + 12, y + 8, x + 52, y + h - 6, 5, INK)
        sh.fill(x + 20, y + 14, x + 44, y + 26, (255, 214, 100))
        sh.seg(x + 52, y + 12, x + 62, y + h - 10, INK, 2)
        sh.path([(x + 76, y + h - 12), (x + 116, y + 26), (x + 156, y + 14)],
                BLUE, 3)
        sh.poly([(x + 156, y + 14), (x + 142, y + 12), (x + 152, y + 26)],
                fill=BLUE)
        sb(sh, 13, x + w - 54, y + h - 18, "3.6%", BLUE)
    elif kind == "sudan":
        sh.fill(x, y, x + w, y + h, (240, 228, 200))
        sh.poly([(x + 16, y + 10), (x + 70, y + 6), (x + 96, y + 22),
                 (x + 88, y + h - 8), (x + 30, y + h - 6), (x + 12, y + 26)],
                fill=(214, 190, 140), edge=(146, 110, 60))
        sh.oval(x + w - 62, y + 6, x + w - 22, y + 46, fill=WHITE,
                edge=INK, t=2)
        sh.seg(x + w - 28, y + 40, x + w - 10, y + h - 8, INK, 3)
        sh.fill(x + 18, y + h - 16, x + 46, y + h - 6, WHITE)
        sh.frame(x + 18, y + h - 16, x + 46, y + h - 6, INK, 1)
    elif kind == "game":
        sh.fill(x, y, x + w, y + h, (196, 182, 224))
        sh.rrect(x + 16, y + 12, x + 118, y + h - 10, 10, (36, 40, 52))
        sh.dot(x + 42, y + h // 2, 5, (255, 214, 64))
        sh.dot(x + 92, y + h // 2, 5, (255, 214, 64))
        sh.fill(x + 60, y + h // 2 - 8, x + 74, y + h // 2 + 8, (200, 60, 60))
        sh.oval(x + w - 62, y + 6, x + w - 14, y + h - 8, fill=WHITE,
                edge=INK, t=2)
        sh.seg(x + w - 38, y + 12, x + w - 38, y + 22, INK, 2)
        sh.seg(x + w - 38, y + 22, x + w - 28, y + 26, INK, 2)
    elif kind == "health":
        sh.fill(x, y, x + w, y + h, (232, 240, 244))
        sh.oval(x + 22, y + 10, x + 62, y + 34, fill=BLUE)
        sh.oval(x + 42, y + 10, x + 82, y + 34, fill=WHITE, edge=BLUE, t=2)
        for bx, by in ((120, 14), (140, 26), (160, 12)):
            sh.dot(x + bx, y + by, 4, GREEN)
            sh.seg(x + bx, y + by, x + bx + 8, y + by + 8, GREEN, 1)
        sh.path([(x + 132, y + h - 8), (x + 152, y + 18), (x + 172, y + 10)],
                GREEN, 3)
    elif kind == "climate":
        sh.fill(x, y, x + w, y + h, (214, 228, 238))
        sh.oval(x + 14, y + 6, x + 62, y + h - 8, fill=(70, 150, 220),
                edge=NAVY, t=2)
        sh.poly([(x + 26, y + 14), (x + 40, y + 12), (x + 38, y + 24),
                 (x + 24, y + 26)], fill=GREEN)
        sh.poly([(x + 40, y + 28), (x + 54, y + 30), (x + 48, y + 40),
                 (x + 34, y + 36)], fill=GREEN)
        sh.fill(x + w - 34, y + 8, x + w - 22, y + h - 10, WHITE)
        sh.frame(x + w - 34, y + 8, x + w - 22, y + h - 10, INK, 1)
        sh.oval(x + w - 40, y + h - 18, x + w - 16, y + h - 6, fill=RED)
        sh.fill(x + w - 31, y + 16, x + w - 25, y + h - 12, RED)
        sb(sh, 11, x + w - 62, y + 8, "3C", RED)
    elif kind == "factory":
        sh.fill(x, y, x + w, y + h, (238, 232, 214))
        sh.poly([(x + 12, y + h - 8), (x + 12, y + 22), (x + 40, y + 10),
                 (x + 68, y + 22), (x + 96, y + 10), (x + 124, y + 22),
                 (x + 124, y + h - 8)], fill=(70, 70, 78))
        sh.fill(x + 132, y + 6, x + 142, y + h - 8, (70, 70, 78))
        sh.fill(x + 150, y + 10, x + w - 12, y + 20, (255, 214, 64))
        sb(sh, 10, x + 152, y + 11, "SHUT", INK)
        sh.fill(x + 150, y + 26, x + w - 12, y + h - 8, (120, 120, 110))
    else:  # sanctions
        sh.fill(x, y, x + w, y + h, (240, 234, 214))
        for i in range(4):
            hx = x + 14 + i * 42
            sh.poly([(hx, y + h - 10), (hx + 16, y + 14),
                     (hx + 32, y + h - 10)], fill=(176, 132, 80))
            sh.fill(hx + 4, y + h - 12, hx + 28, y + h - 6, (120, 84, 50))
        sh.oval(x + w - 52, y + 8, x + w - 20, y + 40, fill=(255, 214, 64),
                edge=INK, t=2)
        sh.fill(x + w - 56, y + 26, x + w - 16, y + h - 8, (60, 60, 66))
        sh.fill(x + w - 40, y + 30, x + w - 32, y + h - 14, (255, 214, 64))


# ------------------------------------------------------------------ data

# All 45 stories as reported on Wednesday 18 November 2026. Text uses
# ASCII plus the bullet (U+2022), the only non-ASCII glyph in fonts.bin.
HEROES = [
    ("1  MIDDLE EAST  \u2022  IRAN WAR", RED, "gulf",
     "Kuwait, Bahrain say they intercepted Iranian drones",
     "Iran's army says it aimed at US forces at Ali Al Salem. ADNOC "
     "says its ship was hit in Hormuz: 1 missing, 11 injured."),
    ("2  ASIA  \u2022  DIPLOMACY", TEAL, "summit",
     "Xi greets Trump on eve of Trump-Xi-Putin summit",
     "Xi and Putin vowed to 'lead' a multipolar world; at APEC Xi "
     "urged AI and free-trade cooperation. Talks Thursday."),
    ("3  AMERICAS  \u2022  US POLITICS", NAVY, "alaska",
     "Democrat Peltola wins Alaska; Senate now 56-44",
     "AP calls it: 144,302 votes to Sullivan's 131,844. A ninth "
     "Democratic gain, the most in a midterm since 1958, AP says."),
]

PANELS = [
    ("4  EUROPE  \u2022  UKRAINE WAR", RED, "drones",
     "Russia fires 141 drones at Ukraine overnight",
     "Air force: 126 downed. Officials: 5 killed, 15 injured in a "
     "day; power cut to 80+ Rivne settlements."),
    ("5  MIDDLE EAST  \u2022  GAZA", DARKRED, "gaza",
     "Board of Peace warns UN the Gaza truce may collapse",
     "First report to the Security Council (obtained by AP) says "
     "Israel blocked the civil administration."),
    ("6  ASIA  \u2022  DISASTER", TEAL, "cyclone",
     "Cyclone Akvan strengthens in the Bay of Bengal",
     "IMD: landfall in Andhra Pradesh around noon Friday. Odisha "
     "readies up to 204,070 to evacuate."),
    ("7  EUROPE  \u2022  ECONOMY", BLUE, "pump",
     "UK inflation rises to 3.6%, highest in a year",
     "October CPI up from 3.5% as diesel hits a record high, the "
     "ONS says."),
    ("8  AFRICA  \u2022  SUDAN WAR", BROWN, "sudan",
     "Amnesty: RSF drone strikes killed 37 civilians in El Obeid",
     "It says they should be investigated as war crimes; the RSF "
     "denies responsibility."),
    ("9  GLOBAL  \u2022  CULTURE", PURPLE, "game",
     "Grand Theft Auto VI goes on sale after a 13-year wait",
     "Midnight launch starts in New Zealand; Sensor Tower estimates "
     "15m+ pre-release sales."),
    ("10  EUROPE  \u2022  HEALTH", TEAL, "health",
     "Europe off track on antibiotic resistance, ECDC warns",
     "Carbapenem-resistant K. pneumoniae bloodstream infections up "
     "72% since 2019."),
    ("11  GLOBAL  \u2022  CLIMATE", RED, "climate",
     "COP31: 75 countries back Turkiye's '35x35' power goal",
     "Electricity 35% of energy by 2035 (Anadolu). Johan Rockstrom "
     "warns of 2.8-3C."),
    ("12  ASIA  \u2022  LABOUR", AMBER, "factory",
     "Bangladesh garment protests shut at least 55 factories",
     "Tk 30,000 minimum wage sought; Dhaka-Mymensingh highway "
     "blocked, police vehicle torched."),
    ("13  OCEANIA  \u2022  DIPLOMACY", TEAL, "sanctions",
     "Australia sanctions settler leader Daniella Weiss",
     "Also two others and four groups incl. Nachala, Amana, over "
     "West Bank settlements (Penny Wong)."),
]

BRIEFS = [
    "Riyadh: coalition says it downed a Houthi cruise missile.",
    "Jerusalem: Knesset approves 9 deputy speakers, 2 Arab",
    "Berlin: coalition to cut power tax and cap fuel prices",
    "Germany: accuses Russia of chemical-weapons breaches",
    "Cambridge: \"human\" named word of the year",
    "Shenzhen: Xi and Lee conclude FTA services talks",
    "Manila: Trump claims trade deal; Manila says none signed",
    "Tokyo: Japan posts sixth straight monthly trade deficit",
    "Seoul: court acquits Daegu mayor in martial-law case",
    "Singapore: Princess Aiko on first imperial visit in 20 years",
    "Bangkok: Chinese director jailed over collapsed tower",
    "Lahore: world's most polluted big city again, AQI 339",
    "Rawalpindi: Sri Lanka alt out for 98 against Pakistan",
    "Kuala Lumpur: ringgit at five-month low",
    "Asia markets: Kospi +2%, Hang Seng -0.9%",
    "Oil: Brent falls 1.4% to $91.82",
    "China: Tencent revenue up 8%, below forecasts",
    "Cook Islands: Cyclone Xavier reaches Category 5",
    "New Zealand: tsunami advisory lifted after 60 cm surges",
    "Sydney: Tame Impala sweeps the ARIA Awards",
    "Australia: Bancroft says whole team knew of 2018 plot",
    "Canada: Carney says China trade no worry for Trump",
    "Peru: M5.9 quake off south coast, no damage reported",
    "Cincinnati: USA beat Haiti 2-0, into Nations League semis",
    "Monterrey: Mexico edge Jamaica, set up semi v USA",
    "Los Angeles: Grimes scores 47 as Lakers win 9th straight",
    "Buenos Aires: deputies debate Milei's sovereignty bill",
    "Bolivia: 99 bat species recorded in Madidi park",
    "Washington: NSA confirms outage on classified network",
    "South Africa: inflation jumps to 5.2%, highest since 2024",
    "Johannesburg: SA Rugby seeks full hearing on Erasmus ban",
    "Sudan: archaeologists reach Old Dongola church floor",
]

# Continents in the 408x210 map box (own simplified shapes).
SHAPES = [
    [(2, 15), (34, 8), (60, 4), (95, 2), (120, 10), (140, 18), (150, 30),
     (138, 44), (128, 52), (118, 66), (100, 78), (84, 88), (70, 96),
     (56, 90), (44, 76), (28, 60), (14, 48), (6, 32)],
    [(98, 104), (118, 98), (142, 108), (152, 124), (146, 150), (132, 172),
     (118, 160), (104, 132), (96, 116)],
    [(200, 44), (214, 30), (236, 24), (258, 26), (272, 38), (262, 52),
     (246, 62), (228, 58), (212, 50)],
    [(208, 78), (226, 70), (252, 70), (272, 80), (278, 104), (264, 136),
     (246, 154), (230, 130), (214, 102), (206, 88)],
    [(272, 34), (300, 22), (340, 14), (390, 14), (424, 26), (436, 44),
     (420, 70), (404, 92), (382, 100), (356, 92), (336, 98), (312, 84),
     (292, 70), (278, 52)],
    [(368, 140), (398, 132), (424, 142), (414, 162), (384, 162),
     (366, 150)],
]

# Story number -> (true x, y, badge dx, dy). Badges sit off the point
# with a hairline where the map is crowded.
PINS = {
    1: (247, 74, 24, -16), 2: (322, 85, 12, -12), 3: (23, 23, 0, -16),
    4: (227, 40, 28, -18), 5: (232, 70, -24, 12), 6: (293, 87, 14, 12),
    7: (192, 38, -30, -18), 8: (227, 100, 16, 8), 9: (390, 187, -22, 4),
    10: (197, 39, -34, 8), 11: (230, 57, 20, 16), 12: (295, 83, -16, 12),
    13: (362, 178, 20, -8),
}

# Small dots for briefs 14-45: (x, y, continent colour).
DOTS = [
    (245, 81, RED), (233, 70, RED), (206, 36, BLUE), (193, 37, BLUE),
    (330, 98, GOLD), (351, 63, GOLD), (336, 61, GOLD), (310, 119, GOLD),
    (307, 99, GOLD), (277, 70, GOLD), (276, 67, GOLD), (308, 116, GOLD),
    (364, 176, TEAL), (11, 155, TEAL), (105, 137, GREEN), (97, 58, GREEN),
    (79, 80, GREEN), (59, 66, GREEN), (126, 177, GREEN), (120, 149, GREEN),
    (105, 58, GREEN), (224, 163, BROWN), (228, 92, BROWN), (106, 48, GREEN),
    (340, 170, TEAL),
]

LEGEND = [("Americas", GREEN), ("Europe", BLUE), ("Africa", BROWN),
          ("Middle East", RED), ("Asia", GOLD), ("Oceania", TEAL),
          ("Global", PURPLE)]


# --------------------------------------------------------------- compose

def compose():
    global _ATLAS
    here = os.path.dirname(os.path.abspath(__file__))
    _ATLAS = read_atlas(os.path.join(here, "fonts.bin"))
    sh = Sheet(W, H, PAPER)
    MX = 14

    # ---- Masthead -----------------------------------------------------
    sb(sh, 13, MX, 10, "THE DAY IN WORLD NEWS", NAVY)
    right = "45 STORIES  \u2022  6 CONTINENTS  \u2022  ONE DAY"
    sb(sh, 13, int(W - MX - measure("sans_bold", 13, right)), 10, right,
       NAVY)
    fb(sh, 56, MX, 30, "Wednesday 18 November 2026", NAVY)
    rule_cols = [RED, GOLD, TEAL, NAVY, PURPLE, GREEN]
    for i, col in enumerate(rule_cols):
        x0 = MX + i * (W - 2 * MX) // 6
        x1 = MX + (i + 1) * (W - 2 * MX) // 6
        sh.fill(x0, 100, x1, 106, col)

    # ---- Heroes --------------------------------------------------------
    hw, hg, hgap = 324, 228, 12
    for i, (kick, accent, kind, title, dek) in enumerate(HEROES):
        x = MX + i * (hw + hgap)
        y = 110
        sh.fill(x + 3, y + 3, x + hw + 3, y + hg + 3, SHADOW)
        sh.fill(x, y, x + hw, y + hg, CARD)
        sh.frame(x, y, x + hw, y + hg, FAINT, 1)
        picture(sh, kind, x + 1, y + 1, hw - 2, 94)
        sb(sh, 11, x + 10, y + 100, kick, accent)
        para(sh, "serif_bold", 20, x + 10, y + 116, title, INK, hw - 20,
             22, limit=3)
        para(sh, "sans", 11, x + 10, y + 184, dek, GREY, hw - 20, 13,
             limit=3)

    # ---- Grid ----------------------------------------------------------
    gw, gh, ggap = 192, 150, 9
    for r in range(2):
        for c in range(5):
            i = r * 5 + c
            kick, accent, kind, title, dek = PANELS[i]
            x = MX + c * (gw + ggap)
            y = 346 + r * (gh + 8)
            sh.fill(x + 2, y + 2, x + gw + 2, y + gh + 2, SHADOW)
            sh.fill(x, y, x + gw, y + gh, CARD)
            sh.frame(x, y, x + gw, y + gh, FAINT, 1)
            sh.fill(x, y, x + gw, y + 4, accent)
            picture(sh, kind, x + 1, y + 5, gw - 2, 46)
            sb(sh, 9, x + 8, y + 55, kick, accent)
            para(sh, "serif_bold", 14, x + 8, y + 67, title, INK, gw - 16,
                 16, limit=3)
            para(sh, "sans", 10, x + 8, y + 115, dek, GREY, gw - 16, 12,
                 limit=3)

    # ---- Bottom: map + also list ---------------------------------------
    by = 662
    bh = 318
    # Map panel.
    sh.fill(MX, by, MX + 436, by + bh, CARD)
    sh.frame(MX, by, MX + 436, by + bh, FAINT, 1)
    sb(sh, 13, MX + 12, by + 8, "WHERE IT HAPPENED", INK)
    mx, my = MX + 14, by + 32
    sh.fill(mx, my, mx + 408, my + 210, MAPSEA)
    for poly in SHAPES:
        pts = [(mx + px, my + py) for px, py in poly]
        sh.poly(pts, fill=LAND, edge=(120, 120, 105))
    for px, py, col in DOTS:
        sh.dot(mx + px, my + py, 3, col)
    for num, (px, py, dx, dy) in sorted(PINS.items()):
        bx, byy = mx + px + dx, my + py + dy
        sh.seg(mx + px, my + py, bx, byy, RED, 1)
        sh.dot(mx + px, my + py, 3, RED)
        sh.oval(bx - 8, byy - 8, bx + 8, byy + 8, fill=RED,
                edge=WHITE, t=2)
        label = str(num)
        lw = measure("sans_bold", 9, label)
        sb(sh, 9, int(bx - lw / 2), byy - 5, label, WHITE)
    lx = mx
    for name, col in LEGEND:
        sh.dot(lx + 4, by + 254, 4, col)
        sn(sh, 10, lx + 12, by + 249, name, GREY)
        lx += 12 + int(measure("sans", 10, name)) + 12
    sn(sh, 10, mx, by + 270,
       "1 numbered pin: stories 1-13 above  \u2022  dot: briefs 14-45",
       GREY)
    sn(sh, 10, mx, by + 286,
       "Hairlines lead from crowded spots to the true place.", GREY)

    # Also list panel, two columns.
    ax = MX + 444
    sh.fill(ax, by, W - MX, by + bh, CARD)
    sh.frame(ax, by, W - MX, by + bh, FAINT, 1)
    sb(sh, 13, ax + 12, by + 8, "ALSO ON WEDNESDAY 18 NOVEMBER", INK)
    for half in range(2):
        cx = ax + 8 + half * 272
        yy = by + 34
        for j in range(16):
            n = 14 + half * 16 + j
            sb(sh, 9, cx, yy, str(n), RED)
            lines = fit_lines("sans", 8.5, BRIEFS[n - 14], 250)
            for k, line in enumerate(lines):
                sn(sh, 8.5, cx + 20, yy + k * 11, line, INK)
            yy += 15 if len(lines) == 1 else 26

    # ---- Footer --------------------------------------------------------
    centred(sh, "sans", 10, 996,
            "Every story was reported on Wednesday 18 November 2026; "
            "disputed claims are attributed. Sources: Reuters, AP, AFP, "
            "BBC, Al Jazeera and others. Original drawings.", GREY)
    return sh


def main():
    sh = compose()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    dump_png(sh, out_path)
    print(f"Wrote {out_path} ({W}x{H})")


if __name__ == "__main__":
    main()
