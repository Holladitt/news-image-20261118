"""news-image-20261118 v3: sum up Wednesday 18 November 2026 in one image.

Dense front-page format, after the Feed winners for this bounty:
a masthead with the date, 3 hero stories, a 10-panel grid, a world
map with numbered story dots, and an "ALSO ON" list, for 31 stories
in total. Deterministic, network-free Pillow drawing to
/output/entry.png, 1024x1024, under 1 MiB. Two runs write identical
bytes.

Stories, all reported on 18 Nov 2026 (cross-checked across sources):
  Heroes: 1 Bahrain and Kuwait intercept Iranian drones after the
  US strike on Qeshm; an ADNOC ship is hit in Hormuz, 1 missing,
  11 injured; 2 Xi greets Trump on the Shenzhen tarmac on the eve
  of the first Trump-Xi-Putin summit; 3 Peltola wins Alaska, giving
  Democrats a 56-44 Senate.
  Grid: 4 Russia fires 141 drones at Ukraine, 126 downed; 5 Board
  of Peace warns the Gaza truce may collapse; 6 Cyclone Akvan
  strengthens toward Andhra Pradesh; 7 UK inflation 3.6%, highest
  in a year; 8 Amnesty: RSF drone strikes killed 37 in El Obeid;
  9 Voyager 1 reaches one light-day from Earth; 10 GTA VI reviews
  land as the worldwide release begins; 11 Europe off track on
  antibiotic resistance; 12 Bangladesh garment protests shut 55
  factories; 13 Australia sanctions settler leader Daniella Weiss.
  Also: Houthi missile downed over Riyadh, EU EUR45bn Ukraine
  loan, gold slide, Gaza floods, Cyclone Xavier Cat 5, NZ tsunami
  advisory lifted, Germany on chemical weapons, Berlin tax cuts,
  Cambridge word of the year, Tokyo trade deficit, Seoul acquittal,
  Princess Aiko in Singapore, Lahore AQI 339, Asia markets and
  Brent, Tencent, Rubio on outages, Peru quake, Colombia GDP.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = Path("/output/entry.png")

PAPER = (250, 246, 232)
INK = (17, 17, 17)
NAVY = (13, 34, 64)
RED = (178, 34, 34)
DARKRED = (122, 20, 20)
TEAL = (14, 110, 120)
AMBER = (150, 100, 0)
WHITE = (255, 255, 255)
GREY = (88, 86, 78)
SEA = (16, 52, 96)
SKY = (178, 214, 235)
LAND = (198, 203, 178)
MAPSEA = (186, 212, 228)


def font(name, size):
    for path in (
        f"/usr/share/fonts/truetype/dejavu/DejaVu{name}.ttf",
        f"/usr/share/fonts/truetype/liberation/Liberation{name}.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


SERIF_B = lambda s: font("Serif-Bold", s)  # noqa: E731
SERIF = lambda s: font("Serif", s)  # noqa: E731
SANS_B = lambda s: font("Sans-Bold", s)  # noqa: E731
SANS = lambda s: font("Sans", s)  # noqa: E731


def wrap(draw, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, fill, width, leading, max_lines=None):
    lines = wrap(draw, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def jet(draw, cx, cy, scale, fill):
    s = scale
    draw.ellipse([cx - 52 * s, cy - 7 * s, cx + 44 * s, cy + 7 * s], fill=fill)
    draw.polygon([(cx + 40 * s, cy - 7 * s), (cx + 62 * s, cy),
                  (cx + 40 * s, cy + 7 * s)], fill=fill)
    draw.polygon([(cx - 8 * s, cy + 2 * s), (cx + 22 * s, cy + 2 * s),
                  (cx + 2 * s, cy + 26 * s), (cx - 18 * s, cy + 2 * s)],
                 fill=fill)
    draw.polygon([(cx - 38 * s, cy - 4 * s), (cx - 18 * s, cy - 4 * s),
                  (cx - 26 * s, cy - 24 * s), (cx - 34 * s, cy - 24 * s)],
                 fill=fill)


def flame(draw, cx, base, s):
    draw.polygon(
        [(cx - 26 * s, base), (cx - 14 * s, base - 34 * s),
         (cx - 4 * s, base - 14 * s), (cx + 6 * s, base - 44 * s),
         (cx + 14 * s, base - 18 * s), (cx + 26 * s, base)],
        fill=(255, 122, 26),
    )
    draw.polygon(
        [(cx - 13 * s, base), (cx - 5 * s, base - 22 * s),
         (cx + 4 * s, base - 8 * s), (cx + 12 * s, base - 26 * s),
         (cx + 13 * s, base)],
        fill=(255, 214, 64),
    )


def gradient(draw, x, y, w, h, top, bottom):
    """Vertical colour gradient, drawn as one line per row."""
    for i in range(h):
        t = i / max(h - 1, 1)
        col = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        draw.line([(x, y + i), (x + w, y + i)], fill=col)


def star(draw, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -90 + i * 36
        rr = r if i % 2 == 0 else r * 0.45
        import math
        pts.append((cx + rr * math.cos(math.radians(ang)),
                    cy + rr * math.sin(math.radians(ang))))
    draw.polygon(pts, fill=fill)


def scene(draw, kind, x, y, w, h):
    """A small illustration band for one story kind."""
    if kind == "sea":
        gradient(draw, x, y, w, h, (255, 140, 60), (255, 90, 40))
        draw.ellipse([x + w - 56, y + 4, x + w - 14, y + 46],
                     fill=(255, 224, 130))
        gradient(draw, x, y + h // 2, w, h - h // 2, (24, 80, 140), SEA)
        for wy in (h // 2 + 8, h // 2 + 20, h - 6):
            draw.arc([x - 30, y + wy - 8, x + 120, y + wy + 8], 200, 340,
                     fill=(140, 190, 230), width=2)
            draw.arc([x + w - 120, y + wy - 8, x + w + 30, y + wy + 8],
                     200, 340, fill=(140, 190, 230), width=2)
        # Tanker with containers, flames and smoke.
        draw.rectangle([x + 16, y + h - 24, x + w - 16, y + h - 10],
                       fill=(30, 30, 36))
        draw.rectangle([x + 16, y + h - 28, x + w - 16, y + h - 24],
                       fill=RED)
        for i, col in enumerate(((210, 90, 40), (40, 130, 90),
                                 (200, 170, 60))):
            bx = x + 28 + i * 52
            draw.rectangle([bx, y + h - 46, bx + 44, y + h - 28], fill=col,
                           outline=INK, width=1)
        flame(draw, x + w // 2 - 34, y + h - 44, 0.42)
        flame(draw, x + w // 2 + 28, y + h - 44, 0.36)
        for cx, cy, r in ((x + w // 2 - 34, y + 8, 11),
                          (x + w // 2 - 12, y + 2, 13),
                          (x + w // 2 + 28, y + 10, 10)):
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 60, 66))
        jet(draw, x + 52, y + 14, 0.5, INK)
        draw.line([x + 8, y + 14, x + 28, y + 14], fill=WHITE, width=2)
    elif kind == "skyline":
        gradient(draw, x, y, w, h, (250, 180, 110), (90, 120, 180))
        draw.ellipse([x + w - 48, y + 4, x + w - 10, y + 42], fill=(255, 80, 60))
        for i, bh in enumerate((34, 48, 28, 52, 38)):
            bx = x + 12 + i * (w - 24) // 5
            bw = (w - 24) // 5 - 6
            draw.rectangle([bx, y + h - 12 - bh, bx + bw, y + h - 12],
                           fill=NAVY)
            for wy in range(y + h - 12 - bh + 6, y + h - 16, 10):
                for wx in range(bx + 4, bx + bw - 4, 9):
                    draw.rectangle([wx, wy, wx + 4, wy + 4],
                                   fill=(255, 214, 100))
        draw.line([x + 18, y + 8, x + 18, y + 26], fill=WHITE, width=2)
        draw.polygon([(x + 18, y + 8), (x + 34, y + 12), (x + 18, y + 16)],
                     fill=RED)
    elif kind == "vote":
        for i in range(7):
            col = RED if i % 2 == 0 else WHITE
            draw.rectangle([x, y + i * h // 7, x + w, y + (i + 1) * h // 7],
                           fill=col)
        draw.rectangle([x, y, x + w // 3, y + h // 2], fill=NAVY)
        for sx in (x + 10, x + 30, x + 50, x + 70):
            for sy in (y + 8, y + 20):
                star(draw, sx, sy, 4, WHITE)
        draw.rectangle([x + w // 2 - 32, y + 14, x + w // 2 + 32, y + h - 8],
                       fill=(240, 240, 235), outline=INK, width=2)
        draw.rectangle([x + w // 2 - 40, y + 8, x + w // 2 + 40, y + 16],
                       fill=NAVY, outline=INK, width=1)
        draw.line([x + w // 2 - 20, y + h // 2 + 2, x + w // 2 - 4,
                   y + h - 14], fill=RED, width=4)
        draw.line([x + w // 2 - 4, y + h - 14, x + w // 2 + 22, y + 12],
                  fill=RED, width=4)
    elif kind == "bridge":
        draw.rectangle([x, y, x + w, y + h], fill=SKY)
        draw.rectangle([x + 8, y + h - 24, x + w // 2 - 12, y + h - 14],
                       fill=(60, 60, 66))
        draw.rectangle([x + w // 2 + 12, y + h - 24, x + w - 8, y + h - 14],
                       fill=(60, 60, 66))
        draw.polygon([(x + w // 2 - 12, y + h - 24), (x + w // 2, y + h - 8),
                      (x + w // 2 + 12, y + h - 24)], fill=(60, 60, 66))
        flame(draw, x + w // 2, y + h - 22, 0.3)
        draw.rectangle([x, y + h - 10, x + w, y + h], fill=(70, 130, 180))
    elif kind == "jet":
        draw.rectangle([x, y, x + w, y + h], fill=(214, 232, 244))
        draw.ellipse([x + w - 46, y + 4, x + w - 8, y + 42], fill=RED)
        jet(draw, x + w // 2 - 10, y + h // 2 + 4, 0.55, NAVY)
    elif kind == "aid":
        draw.rectangle([x, y, x + w, y + h], fill=(238, 232, 214))
        draw.polygon([(x + 20, y + h - 10), (x + w // 2, y + 8),
                      (x + w - 20, y + h - 10)], fill=(120, 130, 140))
        draw.rectangle([x + w // 2 - 6, y + 14, x + w // 2 + 6, y + 34],
                       fill=RED)
        draw.rectangle([x + w // 2 - 14, y + 20, x + w // 2 + 14, y + 28],
                       fill=RED)
    elif kind == "outage":
        draw.rectangle([x, y, x + w, y + h], fill=(24, 28, 36))
        draw.polygon([(x + w // 2 + 8, y + 6), (x + w // 2 - 12, y + h // 2 + 4),
                      (x + w // 2 + 2, y + h // 2 + 4),
                      (x + w // 2 - 8, y + h - 6),
                      (x + w // 2 + 14, y + h // 2 - 2),
                      (x + w // 2, y + h // 2 - 2)], fill=(255, 214, 64))
    elif kind == "health":
        draw.rectangle([x, y, x + w, y + h], fill=(232, 240, 244))
        draw.ellipse([x + w // 2 - 18, y + 6, x + w // 2 + 18, y + 42],
                     fill=RED)
        draw.rectangle([x + w // 2 - 4, y + 12, x + w // 2 + 4, y + 36],
                       fill=WHITE)
        draw.rectangle([x + w // 2 - 12, y + 20, x + w // 2 + 12, y + 28],
                       fill=WHITE)
    elif kind == "market":
        draw.rectangle([x, y, x + w, y + h], fill=(238, 238, 232))
        draw.line([(x + 12, y + 12), (x + w // 3, y + 20),
                   (x + 2 * w // 3, y + 16), (x + w - 12, y + h - 10)],
                  fill=RED, width=4)
        draw.polygon([(x + w - 24, y + h - 16), (x + w - 8, y + h - 16),
                      (x + w - 16, y + h - 4)], fill=RED)
    elif kind == "storm":
        draw.rectangle([x, y, x + w, y + h], fill=(200, 214, 226))
        for r in (8, 16, 24):
            draw.arc([x + w // 2 - r, y + h // 2 - r, x + w // 2 + r,
                      y + h // 2 + r], 0, 270, fill=NAVY, width=3)
        for lx in (x + 16, x + 40, x + w - 40, x + w - 16):
            draw.line([lx, y + h - 14, lx - 4, y + h - 4], fill=NAVY, width=2)
    elif kind == "space":
        gradient(draw, x, y, w, h, (8, 12, 34), (30, 50, 110))
        for sx, sy, r in ((x + 16, y + 10, 2), (x + 48, y + 22, 2),
                          (x + w - 30, y + 8, 2), (x + w - 60, y + 26, 2),
                          (x + 90, y + 8, 2), (x + 130, y + 30, 1),
                          (x + w - 90, y + 12, 1)):
            draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)
        draw.ellipse([x + 6, y + h - 22, x + 30, y + h - 2],
                     fill=(60, 140, 220), outline=(140, 200, 255), width=2)
        draw.ellipse([x + w // 2 - 8, y + h // 2 - 8, x + w // 2 + 8,
                      y + h // 2 + 8], fill=(255, 214, 64))
        draw.line([x + w // 2 - 26, y + h // 2, x + w // 2 + 26,
                   y + h // 2], fill=(180, 190, 220), width=2)
        draw.line([x + w // 2, y + h // 2 - 12, x + w // 2 + 14,
                   y + h // 2 - 20], fill=(180, 190, 220), width=2)
    elif kind == "court":
        draw.rectangle([x, y, x + w, y + h], fill=(238, 232, 214))
        for i in range(3):
            cx = x + 24 + i * (w - 48) // 2
            draw.rectangle([cx - 5, y + 10, cx + 5, y + h - 12], fill=NAVY)
        draw.rectangle([x + 12, y + 8, x + w - 12, y + 14], fill=NAVY)
    elif kind == "sanction":
        draw.rectangle([x, y, x + w, y + h], fill=(238, 238, 232))
        draw.rectangle([x + w // 2 - 18, y + 6, x + w // 2 + 18, y + h - 6],
                       fill=WHITE, outline=INK, width=2)
        draw.line([x + w // 2 - 10, y + 10, x + w // 2 + 10, y + h - 10],
                  fill=RED, width=4)
        draw.line([x + w // 2 + 10, y + 10, x + w // 2 - 10, y + h - 10],
                  fill=RED, width=4)
    elif kind == "yemen":
        draw.rectangle([x, y, x + w, y + h], fill=(232, 214, 170))
        draw.polygon([(x, y + h - 8), (x + w // 3, y + 14),
                      (x + 2 * w // 3, y + h - 8)], fill=(200, 170, 110))
        draw.polygon([(x + w // 3, y + h - 8), (x + 2 * w // 3, y + 10),
                      (x + w, y + h - 8)], fill=(180, 145, 90))
    else:  # game
        draw.rectangle([x, y, x + w, y + h], fill=(24, 28, 36))
        draw.rounded_rectangle([x + 18, y + 10, x + w - 18, y + h - 10],
                               radius=10, fill=(60, 70, 90))
        for cx, cy in ((x + w // 2 - 14, y + h // 2 - 4),
                       (x + w // 2 + 14, y + h // 2 - 4)):
            draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 214, 64))


CONTINENTS = [
    # North America: Alaska, Canada, USA, Mexico, Central America.
    [(18, 38), (55, 22), (110, 20), (150, 32), (138, 52), (128, 62),
     (118, 78), (96, 84), (78, 98), (62, 92), (48, 76), (28, 62),
     (16, 48)],
    # South America.
    [(98, 102), (128, 98), (152, 116), (146, 142), (128, 172),
     (112, 158), (98, 128)],
    # Europe.
    [(208, 38), (232, 24), (262, 28), (272, 44), (258, 58), (240, 66),
     (222, 58), (210, 48)],
    # Africa.
    [(212, 74), (244, 68), (272, 78), (278, 106), (262, 140),
     (244, 156), (226, 128), (212, 100)],
    # Asia.
    [(276, 32), (320, 18), (380, 16), (430, 30), (444, 52), (420, 78),
     (402, 96), (368, 102), (344, 88), (318, 96), (296, 78), (282, 54)],
    # Australia.
    [(382, 138), (418, 132), (442, 146), (428, 164), (392, 164),
     (378, 152)],
]

DOTS = {  # story number -> (map x, map y) in the 460x190 map box
    1: (330, 85), 2: (400, 75), 3: (55, 45), 4: (265, 50), 5: (295, 90),
    6: (360, 95), 7: (215, 45), 8: (250, 110), 9: (70, 82),
    10: (445, 165), 11: (232, 58), 12: (375, 90), 13: (410, 150),
}

HERO = [
    ("1  MIDDLE EAST  •  IRAN WAR", RED, "sea",
     "Bahrain and Kuwait intercept Iran's drones",
     "Iran says it hit a U.S. base at Ali Al Salem. An ADNOC ship "
     "is hit in Hormuz: 1 missing, 11 injured."),
    ("2  ASIA  •  SUMMIT", TEAL, "skyline",
     "Xi greets Trump on eve of three-way summit",
     "A hug on the Shenzhen tarmac. Trump, Xi and Putin meet on "
     "Thursday, the first such summit."),
    ("3  AMERICAS  •  U.S. POLITICS", NAVY, "vote",
     "Peltola wins Alaska; Senate now 56-44",
     "AP calls it 144,302 to 131,844. A ninth Democratic gain, the "
     "most in a midterm since 1958."),
]

GRID = [
    ("4  EUROPE  •  UKRAINE WAR", "jet",
     "Russia fires 141 drones at Ukraine",
     "Air force says 126 downed. Five killed, 15 injured; power cut "
     "to 80+ settlements."),
    ("5  MIDDLE EAST  •  GAZA", "aid",
     "Board of Peace warns Gaza truce may collapse",
     "Its first report to the U.N. Security Council says Israel "
     "blocked the civil administration."),
    ("6  ASIA  •  WEATHER", "storm",
     "Cyclone Akvan strengthens",
     "Landfall due in Andhra Pradesh around noon Friday; Odisha "
     "readies 204,070 to evacuate."),
    ("7  EUROPE  •  ECONOMY", "market",
     "UK inflation rises to 3.6%",
     "Highest in a year. October CPI up from 3.5% as diesel hits a "
     "record high, the ONS says."),
    ("8  AFRICA  •  SUDAN WAR", "yemen",
     "RSF drone strikes killed 37 in El Obeid",
     "Amnesty says they should be investigated as war crimes; the "
     "RSF denies responsibility."),
    ("9  SPACE  •  SCIENCE", "space",
     "Voyager 1, one light-day from Earth",
     "The first human-made object at 25.9bn km. A radio signal now "
     "takes a full day to reach it."),
    ("10  GLOBAL  •  GAMES", "game",
     "GTA VI reviews land as release begins",
     "First reviews call it a masterpiece, 99 on Metacritic. The "
     "launch rolls west from New Zealand."),
    ("11  EUROPE  •  HEALTH", "health",
     "Europe off track on antibiotic resistance",
     "Drug-resistant bloodstream infections up 72% since 2019, the "
     "ECDC warns."),
    ("12  ASIA  •  LABOUR", "skyline",
     "Bangladesh garment protests shut 55 factories",
     "Workers seek a Tk 30,000 minimum wage; the Dhaka-Mymensingh "
     "highway is blocked."),
    ("13  OCEANIA  •  DIPLOMACY", "sanction",
     "Australia sanctions settler leader Weiss",
     "Also two others and four groups over West Bank settlements, "
     "Foreign Minister Wong says."),
]

ALSO = [
    "Riyadh: coalition says it downed a Houthi cruise missile.",
    "EU proposes a EUR45bn loan to fund Ukraine in 2027.",
    "Gold slides to its lowest in more than a year.",
    "Floods swamp Gaza's tents; WHO asks for open aid routes.",
    "Cyclone Xavier reaches Category 5 near the Cook Islands.",
    "New Zealand tsunami advisory lifted after 60cm surges.",
    "Germany accuses Russia of chemical-weapons breaches.",
    "Berlin coalition to cut tax and cap fuel prices.",
    "Cambridge names \"human\" its word of the year.",
    "Tokyo posts a sixth straight monthly trade deficit.",
    "Seoul court acquits Daegu mayor in martial-law case.",
    "Singapore: Princess Aiko on first imperial visit in 20 years.",
    "Lahore is the world's most polluted big city again, AQI 339.",
    "Asia markets: Kospi +2%, Hang Seng -0.9%; Brent falls to $91.82.",
    "Tencent revenue up 8%, below forecasts.",
    "Rubio: no sign of cyberattack behind the outages.",
    "Peru: M5.9 quake off the south coast; no damage reported.",
    "Colombia's economy shrinks 0.8% in Q3.",
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 20  # side margin

    # ---- Masthead -------------------------------------------------------
    d.rectangle([0, 0, W, 118], fill=NAVY)
    d.text((MX, 10), "THE DAY IN WORLD NEWS", font=SANS_B(14),
           fill=(255, 214, 100))
    d.text((640, 10), "31 STORIES  •  6 CONTINENTS  •  ONE DAY",
           font=SANS_B(14), fill=(255, 214, 100))
    d.text((MX, 30), "Wednesday 18 November 2026", font=SERIF_B(46),
           fill=WHITE)
    d.text((MX, 88),
           "Everything on this page happened, or was first reported, "
           "on Wednesday 18 November 2026.",
           font=SERIF(16), fill=(200, 210, 225))
    d.rectangle([0, 118, W, 122], fill=RED)

    # ---- Heroes ----------------------------------------------------------
    hw, hg, gap = 322, 182, 8
    for i, (cat, col, kind, title, dek) in enumerate(HERO):
        x = MX + i * (hw + gap)
        y = 126
        d.rectangle([x + 3, y + 3, x + hw + 3, y + hg + 3],
                    fill=(220, 214, 196))
        d.rectangle([x, y, x + hw, y + hg], fill=WHITE,
                    outline=(180, 172, 150), width=2)
        d.rectangle([x, y, x + hw, y + 6], fill=col)
        scene(d, kind, x + 2, y + 8, hw - 4, 52)
        d.text((x + 10, y + 64), cat, font=SANS_B(11), fill=col)
        text_block(d, x + 10, y + 82, title, SERIF_B(19), INK, hw - 20, 22,
                   max_lines=2)
        text_block(d, x + 10, y + 128, dek, SANS(12), GREY, hw - 20, 15,
                   max_lines=3)

    # ---- Grid ------------------------------------------------------------
    gw, gh = 190, 156
    for r in range(2):
        for c in range(5):
            i = r * 5 + c
            cat, kind, title, dek = GRID[i]
            x = MX + c * (gw + gap)
            y = 318 + r * (gh + gap)
            d.rectangle([x + 2, y + 2, x + gw + 2, y + gh + 2],
                        fill=(220, 214, 196))
            d.rectangle([x, y, x + gw, y + gh], fill=WHITE,
                        outline=(180, 172, 150), width=2)
            d.rectangle([x, y, x + gw, y + 5], fill=RED)
            scene(d, kind, x + 2, y + 7, gw - 4, 38)
            d.text((x + 8, y + 48), cat, font=SANS_B(9), fill=RED)
            text_block(d, x + 8, y + 62, title, SERIF_B(14), INK, gw - 16,
                       16, max_lines=2)
            text_block(d, x + 8, y + 96, dek, SANS(11), GREY, gw - 16, 13,
                       max_lines=4)

    # ---- Bottom: map + also list -----------------------------------------
    by = 642
    # Map panel.
    d.rectangle([MX, by, MX + 500, by + 288], fill=WHITE,
                outline=(180, 172, 150), width=2)
    d.text((MX + 12, by + 8), "WHERE IT HAPPENED", font=SANS_B(14), fill=INK)
    d.text((MX + 12, by + 28),
           "Numbered pins: stories 1-13 above",
           font=SANS(12), fill=GREY)
    mx, my = MX + 20, by + 52
    d.rectangle([mx, my, mx + 460, my + 190], fill=MAPSEA)
    for poly in CONTINENTS:
        pts = [(mx + px, my + py) for px, py in poly]
        d.polygon(pts, fill=LAND, outline=(120, 120, 105))
    for num, (px, py) in DOTS.items():
        cx, cy = mx + px, my + py
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED,
                  outline=WHITE, width=2)
        d.text((cx - 3, cy - 6), str(num), font=SANS_B(10), fill=WHITE)
    d.text((mx, my + 198),
           "Americas  •  Europe  •  Africa  •  Middle East  •  Asia  •  "
           "Oceania  •  Global",
           font=SANS(12), fill=GREY)
    d.text((mx, my + 216),
           "Hairlines lead from crowded spots to the true place.",
           font=SANS(11), fill=GREY)

    # Also list panel.
    ax = MX + 508
    d.rectangle([ax, by, W - MX, by + 288], fill=WHITE,
                outline=(180, 172, 150), width=2)
    d.text((ax + 12, by + 8), "ALSO ON WEDNESDAY 18 NOVEMBER",
           font=SANS_B(14), fill=INK)
    yy = by + 34
    for i, item in enumerate(ALSO, start=14):
        d.text((ax + 12, yy), f"{i}", font=SANS_B(12), fill=RED)
        text_block(d, ax + 44, yy, item, SANS(12), INK, 400, 15,
                   max_lines=1)
        yy += 14

    # ---- Footer ----------------------------------------------------------
    d.rectangle([0, 942, W, H], fill=INK)
    text_block(d, MX, 952,
               "Every story was reported on Wednesday 18 November 2026; "
               "disputed claims are attributed. Sources: Reuters, AP, "
               "AFP, BBC, Al Jazeera and others. Original drawings.",
               SANS(13), WHITE, W - 2 * MX, 17, max_lines=2)
    d.text((MX, 992), "THE WORLD IN ONE DAY  •  18 NOVEMBER 2026",
           font=SANS_B(12), fill=(180, 180, 170))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, format="PNG")
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
