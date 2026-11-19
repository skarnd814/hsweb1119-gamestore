"""GameStore 게임 표지 도트 그림 생성기 (pixelkit).

120x160 도트로 그린 뒤 5배(600x800)로 키워 사이트 img/ 폴더에 넣는다.
원본 크기 그림은 sprites/ 에 남긴다. 실행: python Tools/SpriteGen/covers.py
"""
import math
import random
from pathlib import Path

from PIL import Image
from pixelkit import Part, hex_rgba, palette_rgba

W, H = 120, 160
SCALE = 5
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT_RAW = HERE / "sprites"
OUT_SITE = ROOT / "img"

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

PAL = {
    # 하늘 (위 → 지평선)
    "s0": "#0c0a26", "s1": "#1b1546", "s2": "#372164", "s3": "#682e72", "s4": "#ad486c", "s5": "#e4725a", "s6": "#ffb067",
    "st": "#ffffff", "st2": "#b9b4ff",
    "sun": "#fff0b8", "sun2": "#ffc870", "halo": "#ffd08a",
    "m0": "#4b2c5f", "m1": "#2d1d45",
    # 땅
    "G2": "#a6ec5a", "G1": "#58bb3c", "G0": "#2f7a2c",
    "D2": "#a8703f", "D1": "#8a5530", "D0": "#62391f",
    "T2": "#8d92a8", "T1": "#646a80", "T0": "#454a5e", "T9": "#30333f",
    "C0": "#100d18", "C1": "#1a1626", "C2": "#241f33",
    # 광석
    "cu": "#d8702e", "cu2": "#ffb47a", "au": "#f0c030", "au2": "#fff3a8",
    "gm": "#38d8e6", "gm2": "#d0ffff", "am": "#9c48e0", "am2": "#e4b8ff",
    # 용암
    "L0": "#9c1a0c", "L1": "#e8471a", "L2": "#ff9a1e", "L3": "#fff07a",
    # 나무·집
    "w0": "#5a3418", "w1": "#8b5a2b", "w2": "#c08040",
    "r0": "#7a2a26", "r1": "#b0413e", "r2": "#d8665a",
    "win": "#ffe27a", "win2": "#fff6c8",
    # 광부
    "Y": "#f2c230", "y": "#b8860b", "lamp": "#fffbe0",
    "S": "#f1c29a", "s": "#c98f68",
    "B": "#3a6fd8", "b": "#24489a", "P": "#5a4632", "p": "#382a1c", "O": "#2a2030",
    "ax": "#c8d0de", "ax2": "#6b7488",
    # 불빛
    "f0": "#ff7a1a", "f1": "#ffd23f", "f2": "#fff5c0",
    "mu": "#2fd6c8", "mu2": "#bafff6",
    # 글자
    "t0": "#fff6c8", "t1": "#ffd23f", "t2": "#f59a1e", "t3": "#d8641a", "tk": "#2a1406", "tsh": "#140a04",
    "K": "#0b0910",
}

# 제목용 5x7 도트 글꼴 (2배로 찍어 10x14)
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "'": ["#", "#", "#", ".", ".", ".", "."],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    " ": ["..", "..", "..", "..", "..", "..", ".."],
}

TITLE_COLS = ("t0", "t1", "t2", "t3")


def noise(x, seed, amp=1.0, freqs=((0.11, 1.0), (0.29, 0.6), (0.53, 0.25))):
    rnd = random.Random(seed)
    return amp * sum(a * math.sin(x * f + rnd.uniform(0, 6.28)) for f, a in freqs)


class Canvas:
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.c = [[None] * w for _ in range(h)]

    def set(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.c[y][x] = ch

    def get(self, x, y):
        return self.c[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def part(self, part):
        for (x, y), ch in part.px.items():
            self.set(x, y, ch)


def dither(t, bands, x, y):
    """0~1 위치 t를 색 띠 bands 사이에서 4x4 디더링으로 고른다."""
    f = max(0.0, min(0.9999, t)) * (len(bands) - 1)
    i = int(f)
    return bands[i + 1] if (f - i) * 16 > BAYER[y % 4][x % 4] + 0.5 else bands[i]


def title(cv, lines, y0, cols=TITLE_COLS, ink="tk", shadow_ch="tsh", gap=4):
    """도트 글꼴 제목. lines의 각 줄은 글자열 또는 (글자열, 색 4개). 그림자·외곽선을 두르고 마지막 줄 아래 y를 돌려준다."""
    letters = Part()
    y = y0
    for line in lines:
        text, lc = (line, cols) if isinstance(line, str) else line
        widths = [len(FONT[c][0]) * 2 for c in text]
        x = (cv.w - (sum(widths) + 2 * (len(text) - 1))) // 2
        for c, w in zip(text, widths):
            for gy, row in enumerate(FONT[c]):
                for gx, ch in enumerate(row):
                    if ch == "#":
                        for ax in range(2):
                            for ay in range(2):
                                yy = gy * 2 + ay
                                col = lc[0] if yy < 2 else lc[1] if yy < 7 else lc[2] if yy < 11 else lc[3]
                                letters.px[x + gx * 2 + ax, y + yy] = col
            x += w + 2
        y += 14 + gap
    shadow = letters.moved(1, 2)
    shadow.px = {p: shadow_ch for p in shadow.px}
    shadow.outline(shadow_ch)
    letters.outline(ink)
    cv.part(shadow); cv.part(letters)
    return y - gap + 3


def render(cv, pal_hex, lights=(), lit=lambda x, y: True, steps=(0.0, 0.14, 0.26, 0.38), add=False):
    """문자 캔버스 → 그림. lights: ((x, y), 반지름, (r, g, b)) 목록. 빛은 몇 단계로 끊어 디더링해 섞는다.
    add=True면 빛 색을 더해서(어두운 곳이 회색으로 뜨지 않고 빛 색으로 물듦) 칠한다."""
    pal = palette_rgba(pal_hex)
    img = Image.new("RGBA", (cv.w, cv.h))
    for y in range(cv.h):
        for x in range(cv.w):
            r, g, b, a = pal[cv.c[y][x]]
            if lights and lit(x, y):
                best, col = 0.0, None
                for (lx, ly), rad, lc in lights:
                    k = max(0.0, 1 - math.hypot(x + .5 - lx, y + .5 - ly) / rad)
                    if k > best:
                        best, col = k, lc
                step = steps[min(len(steps) - 1, int(best * len(steps) + (BAYER[y % 4][x % 4] / 16 - .5) * .5))]
                if col and step:
                    if add:
                        r, g, b = (min(255, round(v + c * step * .55)) for v, c in zip((r, g, b), col))
                    else:
                        r, g, b = (round(v + (c - v) * step) for v, c in zip((r, g, b), col))
            img.putpixel((x, y), (r, g, b, a))
    return img


def sky(cv, bands, y0, y1, span=None):
    """y0~y1 줄을 bands 색 띠로 디더링해 칠한다 (span: 그라데이션 길이)."""
    span = span or (y1 - y0)
    for y in range(y0, y1):
        for x in range(cv.w):
            cv.set(x, y, dither((y - y0) / span, bands, x, y))


def stars(cv, rnd, n, y1, cols=("st", "st2"), skip=(6, 40)):
    for _ in range(n):
        x, y = rnd.randrange(cv.w), rnd.randrange(0, y1)
        if not (skip[0] <= y <= skip[1]):
            cv.set(x, y, cols[0] if rnd.random() < .4 else cols[1])


def disc(cv, cx, cy, r, ch, keep=None):
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if math.hypot(x + .5 - cx, y + .5 - cy) <= r and (keep is None or cv.get(x, y) in keep):
                cv.set(x, y, ch)


def poly(cv, pts, ch, keep=None):
    """다각형 채우기 (픽셀 가운데가 안에 있으면 칠함)."""
    ys = [p[1] for p in pts]
    for y in range(int(min(ys)), int(max(ys)) + 1):
        cy = y + .5
        xs = []
        for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
            if (y1 <= cy < y2) or (y2 <= cy < y1):
                xs.append(x1 + (cy - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            for x in range(math.ceil(a - .5), math.floor(b - .5) + 1):
                if keep is None or cv.get(x, y) in keep:
                    cv.set(x, y, ch)


def sprite(rows, x, y, keys, shade=None, light=None, ink="K"):
    """문자 격자 캐릭터: keys로 팔레트 이름을 바꾸고 빛·그림자·외곽선을 두른 Part."""
    p = Part().grid(rows, x, y)
    p.px = {q: keys.get(c, c) for q, c in p.px.items()}
    if shade:
        p.shade(shade)
    if light:
        p.light(light)
    if ink:
        p.outline(ink)
    return p


def draw_cover_terraria():
    cv = Canvas()
    rnd = random.Random(7)

    # ---- 하늘
    sky = ["s0", "s1", "s2", "s3", "s4", "s5", "s6"]
    for y in range(80):
        for x in range(W):
            cv.set(x, y, dither(y / 76, sky, x, y))
    for _ in range(40):
        x, y = rnd.randrange(W), rnd.randrange(0, 44)
        if not (6 <= y <= 25):
            cv.set(x, y, "st" if rnd.random() < .4 else "st2")
    for x, y in ((14, 34), (101, 30), (60, 38)):
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            cv.set(x + dx, y + dy, "st2")
        cv.set(x, y, "st")

    # ---- 해 (지는 해)
    sx, sy = 92, 57
    for y in range(sy - 16, sy + 16):
        for x in range(sx - 16, sx + 16):
            d = math.hypot(x + .5 - sx, y + .5 - sy)
            if d <= 9:
                cv.set(x, y, "sun" if d <= 7 else "sun2")
            elif d <= 13 and (x + y) % 2 == 0:
                cv.set(x, y, "halo" if d <= 11 else "s6")
    for y in (60, 63):   # 해를 가로지르는 구름 띠
        for x in range(sx - 12, sx + 13):
            if cv.get(x, y) in ("sun", "sun2"):
                cv.set(x, y, "s5")

    # ---- 먼 산
    for x in range(W):
        h0 = round(56 + noise(x, 11, 4, ((0.07, 1.0), (0.19, .5))))
        h1 = round(66 + noise(x, 12, 3.5, ((0.09, 1.0), (0.27, .4))))
        for y in range(h0, 80):
            cv.set(x, y, "m0")
        for y in range(h1, 80):
            cv.set(x, y, "m1")

    # ---- 지면 높이
    surf = []
    for x in range(W):
        s = 78 + round(noise(x, 21, 1.6))
        if 54 <= x <= 90:
            s = 78
        surf.append(s)
    stone_top = [101 + round(noise(x, 31, 2.2)) for x in range(W)]

    # ---- 흙과 돌
    for x in range(W):
        for y in range(surf[x], H):
            if y < surf[x] + 2:
                ch = "G2" if y == surf[x] else "G1"
            elif y < surf[x] + 3:
                ch = "G0" if (x % 3) else "D1"
            elif y < stone_top[x]:
                r = rnd.random()
                ch = "D0" if r < .12 else ("D2" if r < .2 else "D1")
                if y == stone_top[x] - 1 and rnd.random() < .5:
                    ch = "T1"
            else:
                deep = (y - stone_top[x]) / 60
                r = rnd.random()
                base = "T1" if deep < .45 else "T0"
                ch = "T9" if r < .1 else ("T2" if r < .16 and deep < .45 else base)
            cv.set(x, y, ch)
    # 잔디 아래로 늘어진 풀
    for x in range(W):
        if rnd.random() < .35:
            cv.set(x, surf[x] + 3, "G0")

    # ---- 동굴 파기
    cave = set()
    top = {}
    for x in range(4, 116):
        u = (x - 60) / 57
        t = round(124 - 15 * math.sqrt(max(0.0, 1 - u * u)) + noise(x, 41, 1.6))
        b = round(139 + noise(x, 42, 1.0))
        if x >= 70:
            b = 147 + round(noise(x, 43, .8))
        top[x] = t
        for y in range(t, b):
            cave.add((x, y))
    # 갱도 (집 옆에서 동굴까지)
    shaft_x = (53, 58)
    for x in range(shaft_x[0], shaft_x[1] + 1):
        for y in range(surf[x], top.get(x, 120) + 1):
            cave.add((x, y))
    for (x, y) in cave:
        v = math.sin(x * .37 + y * .21) + math.sin(y * .53 - x * .17) + rnd.uniform(-.4, .4)
        cv.set(x, y, "C2" if v > .9 else ("C0" if v < -1.3 else "C1"))
    # 동굴 테두리를 어둡게
    for (x, y) in list(cave):
        for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if q not in cave and cv.get(*q) in ("T1", "T0", "T2", "T9", "D1", "D0", "D2"):
                cv.set(*q, "T0" if q[1] > y or q[1] == y else "T9")
    # 종유석
    for x in range(14, 106, 9):
        if x in top and not (shaft_x[0] - 2 <= x <= shaft_x[1] + 2):
            ln = 2 + rnd.randrange(3)
            for i in range(ln):
                cv.set(x, top[x] + i, "T0")
                if i < ln - 1:
                    cv.set(x + 1, top[x] + i, "T9")

    # ---- 광석
    def ore(cx, cy, a, b, n=5):
        """광석 덩어리: 작은 알갱이 2~3개를 붙이고, 알갱이마다 왼쪽 위에 반짝이는 점."""
        gems = [(cx, cy)] + [(cx + rnd.choice((-3, -2, 2, 3)), cy + rnd.choice((-2, -1, 1, 2))) for _ in range(1 + n // 5)]
        for gx, gy in gems:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    p = (gx + dx, gy + dy)
                    if abs(dx) + abs(dy) == 2 and rnd.random() < .6:
                        continue
                    if p not in cave and (cv.get(*p) or "")[:1] in ("T", "D"):
                        cv.set(*p, a)
            if (gx - 1, gy - 1) not in cave and cv.get(gx - 1, gy - 1) == a:
                cv.set(gx - 1, gy - 1, b)
            elif (gx, gy - 1) not in cave and cv.get(gx, gy - 1) == a:
                cv.set(gx, gy - 1, b)

    for cx, cy in ((12, 88), (40, 94), (78, 90), (112, 96), (26, 98), (96, 86)):
        ore(cx, cy, "cu", "cu2", 9)
    for cx, cy in ((8, 112), (110, 110), (46, 151), (20, 153), (84, 154)):
        ore(cx, cy, "au", "au2", 10)
    for cx, cy in ((90, 108), (5, 140), (64, 156), (32, 156)):
        ore(cx, cy, "gm", "gm2", 7)
    for cx, cy in ((30, 107), (113, 132), (104, 156)):
        ore(cx, cy, "am", "am2", 7)

    # ---- 용암
    cave_bottom = {}
    for (x, y) in cave:
        cave_bottom[x] = max(cave_bottom.get(x, 0), y)
    for (x, y) in cave:
        if x >= 70 and y >= 141:
            if y == 141:
                ch = "L3" if (x + 1) % 5 else "L2"
            elif y == 142:
                ch = "L2"
            else:
                ch = "L1" if (x * 3 + y) % 7 else "L2"
            cv.set(x, y, ch)
    for x in range(70, 116):
        if (x, 147) in cave or (x, 146) in cave:
            pass
    for bx, by in ((78, 139), (96, 138), (108, 140)):
        cv.set(bx, by, "L2"); cv.set(bx, by + 1, "L3")
    cv.set(87, 137, "L2")

    # ---- 사다리 (갱도)
    for y in range(surf[shaft_x[0]], cave_bottom[shaft_x[0] + 1] + 1):
        cv.set(shaft_x[0] + 1, y, "w1")
        cv.set(shaft_x[1] - 1, y, "w0")
        if y % 3 == 0:
            for x in range(shaft_x[0] + 1, shaft_x[1]):
                cv.set(x, y, "w2")

    # ---- 나무
    def tree(x, base, hgt, r):
        t = Part()
        t.capsule((x + .5, base), (x + .5, base - hgt), 1.2, "w1")
        t.shade({"w1": "w0"})
        c = Part()
        cy = base - hgt - r + 2
        c.capsule((x + .5, cy), (x + .5, cy), r, "G1")
        c.capsule((x - r * .6, cy + r * .5), (x - r * .6, cy + r * .5), r * .7, "G1")
        c.capsule((x + 1 + r * .6, cy + r * .5), (x + 1 + r * .6, cy + r * .5), r * .7, "G1")
        c.shade({"G1": "G0"}).light({"G1": "G2"})
        t.outline("K"); c.outline("K")
        cv.part(t); cv.part(c)

    tree(14, surf[14], 9, 6)
    tree(34, surf[34], 6, 4.5)
    tree(114, surf[114], 7, 5)

    # ---- 집
    house = Part().grid([
        "........RR........",
        "......RRRRRR......",
        "....RRRRRRRRRR....",
        "..RRRRRRRRRRRRRR..",
        "rrrrrrrrrrrrrrrrrr",
        ".WWWWWWWWWWWWWWWW.",
        ".WwwwwwwwwwwwwwwW.",
        ".WwNNNwwwwwDDDDwW.",
        ".WwNnNwwwwwDDDDwW.",
        ".WwNNNwwwwwDDkDwW.",
        ".WwwwwwwwwwDDDDwW.",
        ".WwwwwwwwwwDDDDwW.",
        ".WWWWWWWWWWWWWWWW.",
    ], 0, 0)
    remap = {"R": "r1", "r": "r0", "W": "w0", "w": "w1", "N": "win", "n": "win2", "D": "w0", "k": "au"}
    house.px = {p: remap[c] for p, c in house.px.items()}
    house.light({"r1": "r2"})
    house = house.moved(62, 78 - 13)
    house.outline("K")
    cv.part(house)
    # 굴뚝 연기
    for i, (dx, dy) in enumerate(((72, 61), (73, 58), (75, 55), (77, 52))):
        cv.set(dx, dy, "st2"); cv.set(dx + 1, dy, "st2")
        if i > 1:
            cv.set(dx, dy - 1, "st2")

    # ---- 횃불과 버섯
    tx, ty = 20, 126
    torch = Part().grid([
        "..f..",
        ".fhf.",
        "fhHhf",
        "fhHhf",
        ".fhf.",
        "..w..",
        "..w..",
        "..d..",
        ".ddd.",
    ], tx - 2, ty - 5)
    torch.px = {p: {"f": "f0", "h": "f1", "H": "f2", "w": "w1", "d": "w0"}[c] for p, c in torch.px.items()}
    cv.part(torch)
    for mx, mh in ((10, 3), (13, 2), (64, 2), (67, 3)):
        fy = 138 + round(noise(mx, 42, 1.0)) - 1
        for i in range(mh):
            cv.set(mx, fy - i, "mu2")
        for dx in (-1, 0, 1):
            cv.set(mx + dx, fy - mh, "mu")
        cv.set(mx, fy - mh - 1, "mu")

    # ---- 광부
    miner = Part().grid([
        "....YYYY....",
        "...YYYYYYL..",
        "..yyyyyyyy..",
        "...SSSSS....",
        "...SSSKS....",
        "...sSSSS....",
        "...BBBBB....",
        "..BBBBBBB...",
        "..BBBBBBBS..",
        "..SBBBBB....",
        "...PPPPP....",
        "...PP.PP....",
        "...PP.PP....",
        "..OOO.OOO...",
    ], 0, 0)
    miner.px = {p: ("lamp" if c == "L" else c) for p, c in miner.px.items()}
    miner.shade({"B": "b", "P": "p", "Y": "y"})
    pick = Part()
    pick.capsule((9.5, 8.5), (13.5, 1.5), .6, "w1")
    pick.capsule((10.5, -.5), (13.5, .5), .7, "ax")
    pick.capsule((13.5, .5), (16, 3.5), .7, "ax")
    pick.shade({"ax": "ax2"})
    floor = 138 + round(noise(40, 42, 1.0)) - 1
    ox, oy = 36, floor - 13
    pick = pick.moved(ox, oy)
    miner = miner.moved(ox, oy)
    pick.outline("K"); miner.outline("K")
    cv.part(pick); cv.part(miner)

    # ---- 제목
    title(cv, ["TERRARIA"], 8)

    # ---- 색 입히기 + 빛(횃불, 용암)
    lights = [((tx + .5, ty - 2.5), 20, (255, 150, 50)), ((94, 143), 30, (255, 90, 20))]
    lit = set(cave)
    for (x, y) in cave:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                lit.add((x + dx, y + dy))
    return render(cv, PAL, lights, lambda x, y: (x, y) in lit and y > 100)


# ============================================================
# 하데스: 지하 세계에서 빛나는 출구로 오르는 계단
# ============================================================
HADES_PAL = {
    "h0": "#0e0306", "h1": "#22060b", "h2": "#3e0b10", "h3": "#651714", "h4": "#962c18",
    "c0": "#2a1d24", "c1": "#4c3a40", "c2": "#76616a", "c3": "#9c8790",
    "g0": "#a87420", "g1": "#e8b44a",
    "dw1": "#ffb04a", "dw2": "#ffe08a", "dw3": "#fff8e0", "ray": "#b8461e",
    "R": "#c42a2a", "r": "#7c1414", "Hh": "#3a1410", "Gl": "#f2c94a",
    "t0": "#fff6dc", "t1": "#ffd56a", "t2": "#e8862a", "t3": "#b0381a",
}


def column(cv, x0, w, top, bottom, broken=False, rnd=None):
    for y in range(top, bottom):
        for x in range(x0, x0 + w):
            k = (x - x0) % 3
            cv.set(x, y, "c2" if k == 0 else ("c0" if k == 2 else "c1"))
        cv.set(x0, y, "c3"); cv.set(x0 + w - 1, y, "c0")
    if broken:
        for x in range(x0, x0 + w):
            for y in range(top - 1, top + rnd.randrange(0, 4)):
                cv.set(x, y, None if y < top else "c0")
    else:
        for x in range(x0 - 2, x0 + w + 2):
            cv.set(x, top - 3, "g1"); cv.set(x, top - 2, "c2"); cv.set(x, top - 1, "g0")
    for x in range(x0 - 1, x0 + w + 1):
        cv.set(x, bottom - 2, "c2"); cv.set(x, bottom - 1, "c0")


def draw_cover_hades():
    cv = Canvas()
    rnd = random.Random(3)
    pal = {**PAL, **HADES_PAL}
    sky(cv, ["h0", "h1", "h2", "h3", "h4"], 0, H, 150)

    # 출구 아치와 빛줄기
    cx = 60
    for y in range(64, 132):
        half = (y - 64) * .55 + 7
        for x in range(W):
            if abs(x + .5 - cx) < half and (x + y) % 2 == 0 and abs(x + .5 - cx) % 9 < 3:
                cv.set(x, y, "ray")
    for y in range(26, 66):
        for x in range(44, 77):
            d = math.hypot(x + .5 - cx, y + .5 - 42)
            inside = (y >= 42 and 49 <= x <= 70) or (y < 42 and d <= 11)
            frame = (y >= 42 and 46 <= x <= 73) or (y < 42 and d <= 14)
            if inside:
                dd = math.hypot(x + .5 - cx, (y + .5 - 50) * .7)
                cv.set(x, y, "dw3" if dd < 6 else "dw2" if dd < 10 else "dw1")
            elif frame:
                cv.set(x, y, "g1" if (y < 42 and d <= 12) or x in (48, 71) else "c1")

    # 기둥 (뒤 → 앞)
    column(cv, 24, 6, 58, 128, broken=True, rnd=rnd)
    column(cv, 90, 6, 62, 128)
    column(cv, 4, 9, 44, 130)
    column(cv, 107, 9, 44, 130, broken=True, rnd=rnd)
    for x in range(W):
        for y in range(H):
            if cv.get(x, y) is None:
                cv.set(x, y, dither(y / 150, ["h0", "h1", "h2", "h3", "h4"], x, y))

    # 계단
    for i in range(16):
        y = 64 + i * 4
        hw = 8 + i * 1.9
        for x in range(round(cx - hw), round(cx + hw)):
            cv.set(x, y, "c3"); cv.set(x, y + 1, "c2")
            cv.set(x, y + 2, "c1"); cv.set(x, y + 3, "c0" if (x + i) % 7 else "c1")
        cv.set(round(cx - hw) - 1, y + 1, "c0"); cv.set(round(cx + hw), y + 1, "c0")
    for y in range(128, 134):
        for x in range(8, 112):
            cv.set(x, y, "c2" if y == 128 else ("c0" if y == 133 else "c1"))

    # 불의 강
    for x in range(W):
        wave = 135 + round(math.sin(x * .31) * 1.2)
        for y in range(134, H):
            if y < wave:
                continue
            if y == wave:
                ch = "L3"
            elif y == wave + 1:
                ch = "L2"
            else:
                n = math.sin(x * .25 + y * .6) + math.sin(x * .11 - y * .3)
                ch = "L0" if n < -1.1 else ("L2" if n > 1.2 else "L1")
            cv.set(x, y, ch)
    # 불티
    for _ in range(60):
        x, y = rnd.randrange(W), rnd.randrange(36, 134)
        if (cv.get(x, y) or "")[:1] in ("h", "r"):
            cv.set(x, y, "L3" if rnd.random() < .3 else "L2")

    # 계단을 오르는 전사 (뒷모습)
    hero = sprite([
        "..G.G.G....",
        "..GHHHG....",
        "..HHHHH....",
        "..HHHHH....",
        "...SSS.....",
        ".RRRRRRR...",
        "SRRRRRRRS..",
        "SRRRRRRRS..",
        "sRRRRRRRs..",
        ".RRRRRRR...",
        ".RRRRRRRR..",
        ".RRRRRRRR..",
        "..ss.ss....",
        "..ss.ss....",
        "..OO.OO....",
    ], 54, 82, {"G": "Gl", "H": "Hh", "R": "R"}, shade={"R": "r"})
    blade = Part().capsule((62.5, 90.5), (66.5, 98.5), .5, "dw2")
    blade.outline("K")
    cv.part(blade); cv.part(hero)

    y_t = title(cv, ["HADES"], 8)
    lights = [((60, 46), 54, (255, 214, 150)), ((24, 150), 36, (255, 90, 30)), ((96, 150), 36, (255, 90, 30))]
    return render(cv, pal, lights, lambda x, y: y > y_t, add=True)


# ============================================================
# 엘든 링: 빛의 고리를 두른 황금 나무와 절벽 위 기사
# ============================================================
ELDEN_PAL = {
    "e0": "#0c0a1e", "e1": "#1f183a", "e2": "#3a2a52", "e3": "#64425e", "e4": "#a26c58", "e5": "#d8a462",
    "gl0": "#a8681a", "gl1": "#e2a838", "gl2": "#ffd97a", "gl3": "#fff6d0",
    "tr0": "#6e4212", "tr1": "#c48a2e",
    "m0": "#3c2a50", "m1": "#241a36", "m2": "#150f22",
    "k1": "#0c0814", "k2": "#2a2034",
    "ar0": "#2a2a36", "ar1": "#4e5064", "ar2": "#7a7e94", "cp": "#4a1e22", "cp2": "#2c1014",
    "t0": "#fff6d8", "t1": "#f2d48a", "t2": "#d9a845", "t3": "#a8742a",
}


def draw_cover_elden():
    cv = Canvas()
    rnd = random.Random(5)
    pal = {**PAL, **ELDEN_PAL}
    sky(cv, ["e0", "e1", "e2", "e3", "e4", "e5"], 0, 112)
    stars(cv, rnd, 30, 50, skip=(4, 40))

    # 빛의 고리
    cx, cy, rr = 60, 70, 25
    for y in range(cy - rr - 4, cy + rr + 4):
        for x in range(cx - rr - 4, cx + rr + 4):
            d = math.hypot(x + .5 - cx, y + .5 - cy)
            if abs(d - rr) < .8:
                cv.set(x, y, "gl2")
            elif abs(d - rr) < 2.2 and BAYER[y % 4][x % 4] < 5:
                cv.set(x, y, "gl1")

    # 산과 성
    for x in range(W):
        h0 = round(86 + noise(x, 51, 4, ((0.08, 1.0), (0.21, .5))))
        h1 = round(98 + noise(x, 52, 3, ((0.06, 1.0), (0.25, .4))))
        for y in range(h0, H):
            cv.set(x, y, "m0")
        for y in range(h1, H):
            cv.set(x, y, "m1")
    castle = sprite([
        "..#.......#....",
        ".###..#..###...",
        ".###.###.###...",
        ".###.###.###.#.",
        "#############.#",
        "###############",
        "###w###w####w##",
        "###############",
    ], 92, 84, {"#": "m2", "w": "dw2"}, ink=None)
    pal.setdefault("dw2", "#ffd08a")
    cv.part(castle)

    # 황금 나무
    tree = Part()
    tree.capsule((60, 101), (60, 86), 3.2, "tr1")
    tree.capsule((60, 86), (60, 72), 2.2, "tr1")
    for a, b, r in (((60, 80), (44, 70), 1.3), ((60, 80), (76, 70), 1.3), ((60, 74), (51, 62), 1.1),
                    ((60, 74), (69, 62), 1.1), ((60, 72), (60, 58), 1.0),
                    ((58, 99), (49, 103), 1.2), ((62, 99), (71, 103), 1.2)):
        tree.capsule(a, b, r, "tr1")
    tree.shade({"tr1": "tr0"}).light({"tr1": "gl1"})
    cv.part(tree)
    crown = Part()
    clumps = ((60, 58, 9), (47, 63, 7), (73, 63, 7), (37, 69, 5), (83, 69, 5), (52, 52, 7),
              (68, 52, 7), (60, 46, 6), (42, 70, 4), (78, 70, 4))
    for x, y, r in clumps:
        crown.capsule((x, y), (x, y), r, "gl1")
    # 잎 덩어리 결: 덩어리마다 아래쪽은 어둡게, 위쪽은 밝게
    for (x, y) in list(crown.px):
        cx_, cy_, r_ = min(clumps, key=lambda c: math.hypot(x + .5 - c[0], y + .5 - c[1]) - c[2])
        rel = (y + .5 - cy_) / r_
        n = math.sin(x * .9 + y * .4) + math.sin(y * 1.1 - x * .3)
        if rel > .45 or n < -1.3:
            crown.px[x, y] = "gl0"
        elif rel < -.45 and (x - cx_) < r_ * .3:
            crown.px[x, y] = "gl2"
    crown.light({"gl1": "gl2"})
    for _ in range(22):
        p = rnd.choice(list(crown.px))
        crown.px[p] = "gl3"
    cv.part(crown)
    # 가지 사이로 보이는 틈
    for x, y in ((55, 66), (65, 66), (44, 74), (76, 74)):
        cv.set(x, y, "tr0")
    # 떨어지는 잎
    for _ in range(26):
        x, y = rnd.randrange(10, 110), rnd.randrange(62, 130)
        if (cv.get(x, y) or "")[:1] in ("e", "m"):
            cv.set(x, y, "gl2" if rnd.random() < .5 else "gl1")
    # 앞 절벽
    poly(cv, [(0, 120), (34, 121), (52, 126), (64, 133), (70, 160), (0, 160)], "k1")
    poly(cv, [(70, 160), (78, 146), (120, 141), (120, 160)], "k1")
    for x in range(0, 66):
        for y in range(118, 140):
            if cv.get(x, y) == "k1" and cv.get(x, y - 1) not in ("k1", "k2"):
                cv.set(x, y, "k2")
                break

    # 기사 (뒷모습, 나무를 바라봄)
    sword = Part().capsule((25.5, 103.5), (36.5, 118.5), .6, "ar2")
    sword.capsule((25, 106), (28, 104), .5, "ar0")
    sword.outline("K")
    knight = sprite([
        "....HHH......",
        "...HHHHH.....",
        "...HHHHH.....",
        "....HHH......",
        "..AAAAAAA....",
        ".AAAAAAAAA...",
        ".ACCCCCCCA...",
        "..CCCCCCC....",
        "..CCCCCCCC...",
        "..CCCCCCCCC..",
        "..CCCCCCCCCC.",
        "...CCCCCCCCCC",
        "...LL..LL.C.C",
        "...LL..LL....",
        "..BBB..BBB...",
    ], 24, 106, {"H": "ar1", "A": "ar1", "C": "cp", "L": "ar0", "B": "K"}, shade={"ar1": "ar0", "cp": "cp2"},
        light={"ar1": "ar2"})
    cv.part(sword); cv.part(knight)

    y_t = title(cv, ["ELDEN", "RING"], 6)
    lights = [((60, 62), 44, (255, 200, 110))]
    return render(cv, pal, lights, lambda x, y: y > y_t, add=True)


# ============================================================
# 발더스 게이트 3: 달 앞을 나는 용, 성문 앞의 세 모험가
# ============================================================
BG3_PAL = {
    "b0": "#060918", "b1": "#10183a", "b2": "#232658", "b3": "#45285c", "b4": "#86283a", "b5": "#d0502a",
    "mo": "#ece6d2", "mo2": "#bfb8a4",
    "dk": "#07040c", "dk2": "#1e1226", "ey": "#ff3a2a",
    "sw0": "#2e3246", "sw1": "#4a4f68", "sw2": "#6e7490", "sw3": "#9aa0b8",
    "rf0": "#3a1a2a", "rf1": "#6a2a3a", "bn": "#a8202a", "bn2": "#d8463e",
    "gt": "#160c10", "cb0": "#22202c", "cb1": "#3c3a4c", "cb2": "#5a586c",
    "f0": "#ff7a1a", "f1": "#ffd23f", "f2": "#fff5c0",
    "ft": "#7a7e94", "ft2": "#b8bcd0", "sh": "#7a3a1a", "mg": "#5a2a8a", "mg2": "#8a4ac0",
    "rg": "#2a5a3a", "rg2": "#3e7a50", "orb": "#7ff4ff", "orb2": "#e8ffff", "ar0": "#2a2a36",
    "t0": "#fff1d0", "t1": "#f0c060", "t2": "#c8782a", "t3": "#8a3a1a",
}


def brick(cv, x0, y0, x1, y1, base, mortar, hi=None):
    for y in range(y0, y1):
        for x in range(x0, x1):
            row = (y - y0) // 4
            if (y - y0) % 4 == 3 or (x + (row % 2) * 4) % 8 == 0:
                cv.set(x, y, mortar)
            else:
                cv.set(x, y, hi if hi and (y - y0) % 4 == 0 else base)


def draw_cover_bg3():
    cv = Canvas()
    rnd = random.Random(9)
    pal = {**PAL, **BG3_PAL}
    sky(cv, ["b0", "b1", "b2", "b3", "b4", "b5"], 0, 104)
    stars(cv, rnd, 40, 60, skip=(4, 42))
    disc(cv, 40, 58, 13, "mo")
    for x, y, r in ((36, 54, 3), (45, 62, 2), (40, 66, 1.5), (44, 51, 1.5)):
        disc(cv, x, y, r, "mo2")

    # 용 (달 앞을 지나감)
    for wing in ([(64, 57), (59, 30), (64, 34), (68, 25), (73, 32), (78, 21), (80, 34), (82, 58)],
                 [(80, 59), (89, 31), (94, 36), (100, 29), (103, 37), (108, 33), (106, 50), (90, 63)]):
        poly(cv, wing, "dk2")
    dragon = Part()
    for a, b, r in (((64, 56), (86, 61), 3.4), ((64, 56), (54, 48), 2.2), ((54, 48), (47, 49), 2.3),
                    ((47, 50), (43, 52), 1.2), ((86, 61), (98, 67), 2.2), ((98, 67), (108, 65), 1.4),
                    ((108, 65), (114, 60), .9), ((72, 54), (60, 30), .8), ((72, 54), (68, 26), .7),
                    ((72, 54), (78, 22), .8), ((84, 58), (90, 32), .8), ((84, 58), (100, 30), .7),
                    ((84, 58), (108, 34), .8), ((70, 62), (68, 68), 1), ((82, 64), (82, 70), 1)):
        dragon.capsule(a, b, r, "dk")
    cv.part(dragon)
    cv.set(48, 47, "ey"); cv.set(49, 47, "ey")

    # 뒤쪽 도시와 불타는 지평선
    for x in range(0, W, 7):
        h = 78 + rnd.randrange(0, 18)
        w = rnd.randrange(5, 9)
        for y in range(h, 100):
            for xx in range(x, x + w):
                cv.set(xx, y, "rf0")
        poly(cv, [(x - 1, h), (x + w / 2, h - 7), (x + w + 1, h)], "rf0")
        if rnd.random() < .7:
            cv.set(x + 2, h + 4, "f1")

    # 성벽과 성문
    brick(cv, 0, 98, W, 142, "sw1", "sw0", "sw2")
    for x in range(0, W, 8):
        for y in range(93, 98):
            for xx in range(x, x + 4):
                cv.set(xx, y, "sw1" if y > 93 else "sw2")
    for tx in (24, 76):
        brick(cv, tx, 74, tx + 20, 142, "sw2", "sw0", "sw3")
        for x in range(tx - 1, tx + 21, 5):
            for y in range(69, 74):
                for xx in range(x, x + 3):
                    cv.set(xx, y, "sw2")
        poly(cv, [(tx - 2, 70), (tx + 10, 50), (tx + 22, 70)], "rf1")
        poly(cv, [(tx + 10, 50), (tx + 22, 70), (tx + 10, 70)], "rf0")
        for y in range(78, 98):
            for x in range(tx + 6, tx + 14):
                if not (y > 94 and x in (tx + 9, tx + 10)):
                    cv.set(x, y, "bn2" if x == tx + 6 else "bn")
        cv.set(tx + 9, 85, "f1"); cv.set(tx + 10, 85, "f1"); cv.set(tx + 9, 86, "f1"); cv.set(tx + 10, 86, "f1")
    # 아치 문
    gx = 60
    for y in range(96, 142):
        for x in range(44, 77):
            d = math.hypot(x + .5 - gx, y + .5 - 112)
            inside = (y >= 112 and 47 <= x <= 72) or (y < 112 and d <= 13)
            ring = (y >= 112 and 45 <= x <= 74) or (y < 112 and d <= 15.5)
            if inside:
                glow = (y - 100) / 42
                cv.set(x, y, "b5" if glow > .6 and (x + y) % 2 else ("b4" if glow > .3 else "gt"))
                if (x - 47) % 5 == 0 or (y - 100) % 6 == 0:
                    cv.set(x, y, "dk")
            elif ring:
                cv.set(x, y, "sw3" if y < 112 and (round(math.atan2(y - 112, x - gx) * 6)) % 2 else "sw2")
    # 횃불
    for tx in (42, 78):
        for p, ch in (((tx, 110), "w0"), ((tx, 109), "w1"), ((tx, 108), "f0"), ((tx, 107), "f1"),
                      ((tx, 106), "f2"), ((tx - 1, 107), "f0"), ((tx + 1, 107), "f0"), ((tx, 105), "f1")):
            cv.set(*p, ch)

    # 길
    for y in range(142, H):
        for x in range(W):
            row = (y - 142) // 3
            mortar = (y - 142) % 3 == 2 or (x + row * 3) % (6 + row) == 0
            cv.set(x, y, "cb0" if mortar else ("cb2" if (y - 142) % 3 == 0 else "cb1"))

    # 세 모험가 (뒷모습)
    fighter = sprite([
        "...hhh....",
        "..hhhhh...",
        "..hhhhh...",
        ".AAAAAAA..",
        "AsSSSSsAA.",
        "AsSOSSsAA.",
        "AsSSSSsA..",
        ".sSSSSs...",
        ".AAAAAA...",
        ".LL..LL...",
        ".LL..LL...",
        "BBB..BBB..",
    ], 34, 144, {"h": "ft", "A": "ft", "S": "sh", "s": "w0", "O": "f1", "L": "ar0", "B": "K"},
        light={"ft": "ft2"})
    mage = sprite([
        "....H.....",
        "...HH.....",
        "...HHH....",
        "..HHHHH...",
        "HHHHHHHHH.",
        "..MMMMM...",
        ".MMMMMMM..",
        ".MMMMMMM..",
        "MMMMMMMMM.",
        "MMMMMMMMM.",
        "MMMMMMMMM.",
        "..B...B...",
    ], 55, 144, {"H": "mg", "M": "mg"}, light={"mg": "mg2"})
    staff = Part().capsule((65.5, 140), (65.5, 156), .5, "w1")
    staff.capsule((65.5, 139), (65.5, 139), 1.4, "orb")
    staff.px[65, 139] = "orb2"
    staff.outline("K")
    rogue = sprite([
        "...RRR....",
        "..RRRRR...",
        "..RRRRR...",
        ".RRRRRRR..",
        "RRRRRRRRR.",
        "RRRRRRRRR.",
        ".RRRRRRR..",
        ".rRRRRRr..",
        "..PPPPP...",
        "..PP.PP...",
        "..PP.PP...",
        ".BBB.BBB..",
    ], 76, 144, {"R": "rg", "r": "ax", "P": "ar0", "B": "K"}, light={"rg": "rg2"})
    for p in (fighter, staff, mage, rogue):
        cv.part(p)

    y_t = title(cv, ["BALDUR'S", "GATE 3"], 6)
    lights = [((42, 106), 13, (255, 150, 50)), ((78, 106), 13, (255, 150, 50)), ((60, 134), 22, (255, 90, 30)),
              ((65.5, 139), 10, (110, 230, 255))]
    return render(cv, pal, lights, lambda x, y: y > 60, add=True)


# ============================================================
# 사이버펑크 2077: 비 내리는 네온 도시를 내려다보는 옥상
# ============================================================
CYBER_PAL = {
    "c0": "#05030f", "c1": "#110a28", "c2": "#2a0e45", "c3": "#4e1258", "c4": "#82206a",
    "k0": "#07050d", "k1": "#110c1f", "k2": "#1d1636", "k3": "#2c2350",
    "np": "#ff2bd6", "np2": "#ffb0f2", "nc": "#2ee6ff", "nc2": "#c8fbff", "ny": "#fcee0a", "ny2": "#fffbb0",
    "wc": "#2a8cb0", "wp": "#a03a9a", "wy": "#c8a040", "rn": "#5a5a94", "red": "#ff2a3a",
    "jk": "#16141c", "jk2": "#2c2a36", "hr": "#2a1830", "S": "#e8b090", "s": "#b07a5a",
    "pn": "#2a2a44", "pn2": "#3c3c5c",
    "t0": "#fffde0", "t1": "#fcee0a", "t2": "#e0c400", "t3": "#a88a00", "tk": "#14001c", "tsh": "#ff2bd6",
}


def draw_cover_cyber():
    cv = Canvas()
    rnd = random.Random(11)
    pal = {**PAL, **CYBER_PAL}
    sky(cv, ["c0", "c1", "c2", "c3", "c4"], 0, 120)

    def tower(x0, w, top, base, ch, win, density):
        for y in range(top, base):
            for x in range(x0, x0 + w):
                cv.set(x, y, ch)
                if (x - x0) % 3 == 1 and (y - top) % 4 == 2 and rnd.random() < density:
                    cv.set(x, y, win)

    # 먼 빌딩 → 가까운 빌딩
    x = 0
    while x < W:
        w = rnd.randrange(6, 12)
        tower(x, w, rnd.randrange(52, 86), 132, "k2", rnd.choice(("wc", "wp")), .35)
        x += w
    tower(48, 18, 30, 132, "k1", "wc", .5)
    for y in range(22, 30):
        cv.set(56, y, "k1")
    cv.set(56, 21, "red")
    for y in range(34, 130, 2):
        cv.set(49, y, "nc"); cv.set(64, y, "np")
    for x0, w, top in ((0, 14, 70), (14, 12, 84), (30, 14, 92), (70, 16, 78), (88, 12, 96), (102, 18, 74)):
        tower(x0, w, top, 132, "k1", rnd.choice(("wc", "wp", "wy")), .55)

    # 네온 간판
    for y in range(78, 112):
        for x in range(4, 11):
            edge = x in (4, 10) or y in (78, 111)
            cv.set(x, y, "np" if edge else ("np2" if (y - 80) % 6 < 3 and 6 <= x <= 8 else "k0"))
    for y in range(86, 93):
        for x in range(72, 98):
            edge = x in (72, 97) or y in (86, 92)
            cv.set(x, y, "nc" if edge else ("nc2" if y == 89 and (x - 74) % 4 < 2 else "k0"))
    for y in range(100, 106):
        for x in range(32, 46):
            edge = x in (32, 45) or y in (100, 105)
            cv.set(x, y, "ny" if edge else ("ny2" if y in (102, 103) and x % 3 else "k0"))
    # 하늘을 나는 차
    for p, ch in (((88, 50), "k3"), ((89, 50), "k3"), ((90, 50), "k3"), ((91, 50), "k3"), ((92, 50), "k3"),
                  ((89, 49), "k3"), ((90, 49), "k3"), ((91, 49), "k3"), ((93, 50), "ny2"), ((87, 50), "red")):
        cv.set(*p, ch)
    # 옥상
    for y in range(132, H):
        for x in range(W):
            seam = (y - 132) in (7, 17) or (x + (y > 139) * 9) % 18 == 0
            cv.set(x, y, "k1" if seam else "k0")
    for x in range(W):
        cv.set(x, 128, "pn2"); cv.set(x, 132, "pn")
    for x in range(0, W, 8):
        for y in range(128, 133):
            cv.set(x, y, "pn2")
    # 젖은 바닥에 비친 네온 (가로 줄무늬)
    for x0, w, ch in ((2, 12, "np"), (30, 16, "ny"), (68, 26, "nc")):
        for i, y in enumerate(range(136, 158, 3)):
            off = (i * 3) % 5
            for x in range(x0 + off, x0 + w - off):
                if (x + i) % 3:
                    cv.set(x, y, ch)

    # 주인공 (뒷모습, 도시를 내려다봄) — Scale2x로 2배
    from pixelkit import scale2x
    rows = [

        "....hhhh......",
        "...hhhhhh.....",
        "...hhhhhh.....",
        "...hhhhhh.....",
        "....SSSS......",
        "..YJJJJJJY....",
        ".YJJJJJJJJY...",
        "JJJJJJJJJJJc..",
        "JJJJJJJJJJJc..",
        "JJJYYYYJJJJc..",
        "JJ.JJJJJJ.Jc..",
        "JJ.JJJJJJ.cc..",
        "SS.JJJJJJ.cc..",
        "...JJJJJJ.....",
        "...PPPPPP.....",
        "...PPP.PPP....",
        "...PPP.PPP....",
        "...PPP.PPP....",
        "...PP...PP....",
        "..BBB...BBB...",
    ]
    big = ["".join(r) for r in scale2x([list(r) for r in rows])]
    hero = sprite(big, 78, 117, {"h": "hr", "J": "jk", "Y": "ny", "c": "nc", "P": "pn2", "B": "K"},
                  light={"jk": "jk2"})
    cv.part(hero)

    # 비
    for _ in range(140):
        x, y = rnd.randrange(W), rnd.randrange(44, H)
        for i in range(3):
            if cv.get(x + i // 2, y + i) not in (None,):
                cv.set(x + i // 2, y + i, "rn")

    y_t = title(cv, ["CYBERPUNK", ("2077", ("nc2", "nc", "#0aa8c8", "#06708a"))], 6)
    pal.update({"#0aa8c8": "#0aa8c8", "#06708a": "#06708a"})
    return render(cv, pal)


# ============================================================
# 리썰 컴퍼니: 버려진 행성, 착륙선, 손전등을 든 직원과 어둠 속 눈
# ============================================================
LETHAL_PAL = {
    "l0": "#04070a", "l1": "#0a1216", "l2": "#121f26", "l3": "#1e3036", "l4": "#2c4248",
    "cn0": "#22282c", "cn1": "#3a4248", "cn2": "#566068", "hz": "#e8b020",
    "d0": "#160f0c", "d1": "#2e1e16", "d2": "#4a3020", "d3": "#6a4628",
    "sh0": "#2e3338", "sh1": "#5a6068", "sh2": "#8e969e", "wm": "#ffd890", "wm2": "#fff2cc",
    "o0": "#963c0c", "o1": "#e06a18", "o2": "#ff9c4a", "vs": "#18262c", "vs2": "#7ad8e8",
    "bm": "#f6eab0", "ey": "#ff2a2a", "mn": "#0a0a0c", "mo": "#d8e2dc",
    "red": "#ff3020", "grn": "#3aff6a", "dk": "#ffd23a",
    "t0": "#ffe8e0", "t1": "#ff6a50", "t2": "#d8281a", "t3": "#8a1010", "tk": "#14040a",
}


def draw_cover_lethal():
    cv = Canvas()
    rnd = random.Random(13)
    pal = {**PAL, **LETHAL_PAL}
    sky(cv, ["l0", "l1", "l2", "l3", "l4"], 0, H, 112)
    stars(cv, rnd, 26, 70, skip=(4, 42))
    disc(cv, 100, 52, 8, "mo")
    disc(cv, 103, 50, 7.5, "l1", keep=("mo",))

    # 시설
    for y in range(60, 114):
        for x in range(58, 120):
            cv.set(x, y, "cn2" if y == 60 else ("cn0" if (x - 58) % 12 == 0 or (y - 60) % 14 == 0 else "cn1"))
    for x in range(52, 58):
        for y in range(70, 114):
            cv.set(x, y, "cn0" if x in (52, 57) else "sh1")
    for y in range(76, 80):
        for x in range(76, 102):
            cv.set(x, y, "hz" if ((x + y) // 3) % 2 else "K")
    for y in range(80, 114):
        for x in range(78, 100):
            cv.set(x, y, "K")
    monster = Part()
    monster.capsule((89, 88), (89, 113), 2.4, "mn")
    monster.capsule((89, 86), (89, 86), 3, "mn")
    monster.capsule((86, 94), (82, 110), .8, "mn")
    monster.capsule((92, 94), (96, 110), .8, "mn")
    cv.part(monster)
    cv.set(87, 86, "ey"); cv.set(91, 86, "ey")
    for p in ((88, 56), (89, 56), (88, 57), (89, 57)):
        cv.set(*p, "red")
    for y in (58, 59):
        cv.set(88, y, "cn0"); cv.set(89, y, "cn0")

    # 땅
    ground = [112 + round(noise(x, 61, 1.5)) for x in range(W)]
    for x in range(W):
        for y in range(ground[x], H):
            r = rnd.random()
            cv.set(x, y, "d2" if y == ground[x] else ("d0" if r < .14 else ("d3" if r < .2 else "d1")))
    for _ in range(14):
        rx, ry = rnd.randrange(W), rnd.randrange(120, H)
        disc(cv, rx, ry, rnd.uniform(1, 2.4), "d2")
        cv.set(rx - 1, ry - 1, "d3")
    # 착륙선
    ship = Part()
    ship.grid([
        "....SSSSSSSSSSSSSSSSSSSSSSSSS.....",
        "..SSSSSSSSSSSSSSSSSSSSSSSSSSSSS...",
        ".SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS..",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS.",
        "SSmSSmSSmSSmSSmSSmSSmSSmSSSSSSSSS.",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSWWWWWS.",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSWWWWWS.",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSWWWWWS.",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSWWWWWS.",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSWWWWWS.",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSWWWWWS.",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSWWWWWS.",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSWWWWWS.",
        "sssssssssssssssssssssssssssWWWWWs.",
        ".ss........ss........ss.....s.ss..",
        ".ss........ss........ss.......ss..",
    ], 2, 92)
    ship.px = {p: {"S": "sh1", "s": "sh0", "m": "sh2", "W": "wm"}[c] for p, c in ship.px.items()}
    ship.light({"sh1": "sh2"})
    ship.outline("K")
    cv.part(ship)
    cv.set(4, 95, "red"); cv.set(32, 95, "grn")
    poly(cv, [(29, 106), (34, 106), (44, 115), (36, 115)], "sh0")
    for y in range(98, 106):
        cv.set(31, y, "wm2")

    # 손전등 빛
    poly(cv, [(56, 132), (104, 116), (108, 146)], "bm", keep=("d0", "d1", "d2", "d3", "l4"))
    for y in range(110, 150):
        for x in range(56, 110):
            if cv.get(x, y) == "bm" and BAYER[y % 4][x % 4] > 9 - (x - 56) * .12:
                cv.set(x, y, "d2")
    # 주운 고철 (고무 오리, 깡통)
    for p, ch in (((76, 136), "dk"), ((77, 136), "dk"), ((77, 135), "dk"), ((78, 135), "o1"), ((75, 136), "dk"),
                  ((76, 137), "dk"), ((77, 137), "dk"), ((90, 140), "red"), ((90, 139), "red"), ((90, 141), "cn2")):
        cv.set(*p, ch)

    # 직원 (주황 우주복)
    worker = sprite([
        "...HHHHH....",
        "..HHHHHHH...",
        "..HVVVVHH...",
        "..HVvVVHH...",
        "..HHHHHHH...",
        ".OOOOOOOOO..",
        "POOOOOOOOOO.",
        "POOOOOOOOOGG",
        "POOOOOOOOOG.",
        "POOOOOOOO...",
        ".OOOOOOOO...",
        ".OOO..OOO...",
        ".OOO..OOO...",
        ".OOO..OOO...",
        ".BBB..BBB...",
        "BBBB..BBBB..",
    ], 44, 120, {"H": "o1", "O": "o1", "V": "vs", "v": "vs2", "P": "sh0", "G": "sh2", "B": "sh0"},
        shade={"o1": "o0"}, light={"o1": "o2"})
    cv.part(worker)

    y_t = title(cv, ["LETHAL", "COMPANY"], 6)
    lights = [((33, 106), 22, (255, 190, 110)), ((88, 56), 12, (255, 50, 30)), ((89, 86), 7, (255, 40, 40))]
    return render(cv, pal, lights, lambda x, y: y > y_t, add=True)


# ============================================================
# 스타듀 밸리: 맑은 아침의 농장과 밭
# ============================================================
STARDEW_PAL = {
    "sd0": "#4aa6e8", "sd1": "#74bdf0", "sd2": "#a6daf5", "sd3": "#d4eef6", "sd4": "#fde6b4",
    "cl": "#ffffff", "cl2": "#d6e8f4", "mt": "#9db7dc", "mt2": "#7f9cc8",
    "hl1": "#a6e070", "hl2": "#7cc456", "hl3": "#5aa83f",
    "so0": "#7a4a26", "so1": "#9c6638", "so2": "#b47a44",
    "pk": "#f2862e", "pk2": "#ffb060", "pk0": "#c45a18", "sp": "#5ab83c", "sp2": "#8ad85a",
    "ap": "#e2423a", "wh": "#ffffff", "bk": "#f2a33a", "sm": "#eef4f8",
    "t0": "#fff8e0", "t1": "#ffe7a8", "t2": "#f2c060", "t3": "#d89038", "tk": "#5a2e12", "tsh": "#3a1d0c",
}


def draw_cover_stardew():
    cv = Canvas()
    rnd = random.Random(17)
    pal = {**PAL, **STARDEW_PAL}
    sky(cv, ["sd0", "sd1", "sd2", "sd3", "sd4"], 0, 104, 96)

    # 해와 구름
    for y in range(30, 72):
        for x in range(76, 118):
            d = math.hypot(x + .5 - 98, y + .5 - 52)
            if d <= 7:
                cv.set(x, y, "sun")
            elif d <= 9:
                cv.set(x, y, "sun2")
            elif d <= 13 and (x + y) % 2 == 0:
                cv.set(x, y, "sd4")
    for cx, cy, s in ((22, 60, 1.0), (66, 68, .8), (110, 76, .6)):
        cloud = Part()
        for dx, dy, r in ((0, 0, 6), (-7, 2, 4.5), (7, 2, 4.5), (-3, -4, 4), (4, -3, 4.5), (-12, 4, 3), (12, 4, 3)):
            cloud.capsule((cx + dx * s, cy + dy * s), (cx + dx * s, cy + dy * s), r * s, "cl")
        bottom = max(y for _, y in cloud.px)
        cloud.px = {(x, y): ("cl2" if y >= bottom - 1 else c) for (x, y), c in cloud.px.items()}
        cv.part(cloud)

    # 먼 산과 언덕
    for x in range(W):
        h = round(80 + noise(x, 71, 5, ((0.09, 1.0), (0.23, .5))))
        for y in range(h, H):
            cv.set(x, y, "mt2" if (x + y) % 9 == 0 else "mt")
        if h < 76:
            for y in range(h, h + 2):
                cv.set(x, y, "cl")
    for x in range(W):
        h1 = round(90 + noise(x, 72, 2.2, ((0.06, 1.0), (0.17, .4))))
        h2 = round(97 + noise(x, 73, 1.6, ((0.05, 1.0), (0.19, .4))))
        for y in range(h1, H):
            cv.set(x, y, "hl1")
        for y in range(h2, H):
            cv.set(x, y, "hl2" if y > h2 else "hl1")

    # 농가
    for x, y, r in ((25, 69, 1.6), (27, 65, 2), (30, 60, 2.4), (34, 55, 2.6)):
        disc(cv, x, y, r, "sm")
    house_rows = [
        ".........cc..........",
        "....RRRRRccRRRR......",
        "...RRRRRRccRRRRR.....",
        "..RRRRRRRRRRRRRRR....",
        ".RRRRRRRRRRRRRRRRR...",
        "rrrrrrrrrrrrrrrrrrr..",
        ".WWWWWWWWWWWWWWWWW...",
        ".WNNNWWWWDDDWWNNNW...",
        ".WNnNWWWWDDDWWNnNW...",
        ".WNNNWWWWDDDWWNNNW...",
        ".WWWWWWWWDDkWWWWWW...",
        ".wwwwwwwwDDDwwwwww...",
        ".WWWWWWWWDDDWWWWWW...",
    ]
    from pixelkit import scale2x
    big = ["".join(r) for r in scale2x([list(r) for r in house_rows])]
    house = sprite(big, 4, 73, {"R": "r1", "r": "r0", "c": "w0", "W": "w2", "w": "w1", "N": "win", "n": "win2",
                                "D": "w0", "k": "au"}, light={"r1": "r2"})
    cv.part(house)

    # 사과나무
    tree = Part()
    tree.capsule((100.5, 104), (100.5, 88), 1.6, "w1")
    tree.shade({"w1": "w0"})
    crown = Part()
    for dx, dy, r in ((0, 0, 9), (-8, 4, 6), (8, 4, 6), (-3, -6, 6), (4, -6, 6)):
        crown.capsule((100 + dx, 82 + dy), (100 + dx, 82 + dy), r, "G1")
    crown.shade({"G1": "G0"}).light({"G1": "G2"})
    for p in ((95, 80), (104, 78), (108, 86), (98, 88), (91, 86), (102, 84)):
        crown.px[p] = "ap"
    tree.outline("K"); crown.outline("K")
    cv.part(tree); cv.part(crown)

    # 닭
    chick = sprite([
        "....cc.",
        "...WWWb",
        "W.WWWW.",
        "WWWWWW.",
        ".WWWW..",
        "..y.y..",
    ], 46, 98, {"W": "wh", "c": "ap", "b": "bk", "y": "bk"})
    cv.part(chick)

    # 밭 (원근: 소실점으로 모이는 고랑)
    vx, vy, top, bot = 60, 92, 106, H
    edges = list(range(-260, 400, 40))
    for i, (b0, b1) in enumerate(zip(edges, edges[1:])):
        t0x = vx + (b0 - vx) * (top - vy) / (bot - vy)
        t1x = vx + (b1 - vx) * (top - vy) / (bot - vy)
        poly(cv, [(t0x, top), (t1x, top), (b1, bot), (b0, bot)], "so1" if i % 2 else "so2")
    for y in range(top, top + 2):
        for x in range(W):
            if cv.get(x, y) in ("so1", "so2"):
                cv.set(x, y, "so0")
    # 작물: 밝은 고랑 가운데 줄을 따라
    for i, (b0, b1) in enumerate(zip(edges, edges[1:])):
        if i % 2:
            continue
        bc = (b0 + b1) / 2
        tc = vx + (bc - vx) * (top - vy) / (bot - vy)
        for k, y in enumerate((112, 119, 128, 140, 156)):
            x = round(tc + (bc - tc) * (y - top) / (bot - top))
            s = (y - top) / (bot - top)
            if not (2 <= x < W - 2):
                continue
            r = 1.3 + s * 3.2
            if (i // 2 + k) % 3 == 0:
                pk = Part().capsule((x - r * .5, y - r), (x + r * .5, y - r), r, "pk")
                pk.shade({"pk": "pk0"}).light({"pk": "pk2"})
                pk.px[x, round(y - 2 * r - .5)] = "sp"
                pk.outline("K")
                cv.part(pk)
            else:
                # 잎채소 포기: 동그란 잎 덩어리 셋
                leaf = Part()
                for dx in (-r * .7, 0, r * .7):
                    leaf.capsule((x + dx, y - r * .8), (x + dx, y - r * .8), r * .62, "sp")
                leaf.shade({"sp": "G0"}).light({"sp": "sp2"})
                leaf.outline("K")
                cv.part(leaf)

    # 울타리 (앞 왼쪽)
    for x in range(0, 30, 7):
        for y in range(98, 110):
            cv.set(x, y, "w1"); cv.set(x + 1, y, "w0")
    for y in (101, 105):
        for x in range(0, 30):
            if cv.get(x, y) not in ("w1", "w0"):
                cv.set(x, y, "w2")

    title(cv, ["STARDEW", "VALLEY"], 6)
    return render(cv, pal)


# ============================================================
# 할로우 나이트: 어두운 지하 성당의 큰 창과 등불을 든 방랑자
# ============================================================
HOLLOW_PAL = {
    "hb0": "#2c5a80", "hb1": "#1b3c5a", "hb2": "#11283e", "hb3": "#0a1828", "hb4": "#050b14",
    "fr": "#07101c", "fr2": "#0d1b2c", "gs0": "#1e4466", "gs1": "#2e6890", "gs2": "#4c8cb8", "gs3": "#8cc4e8",
    "ry": "#3a6e96", "pl0": "#060d18", "pl1": "#0f1c2e", "pl2": "#1c3048",
    "cl0": "#04080f", "cl1": "#0a1424", "eye": "#e6fbff", "lm": "#e6fbff", "lm2": "#7fdcff",
    "sp": "#cfeaff", "mo": "#9ee8ff", "gd": "#03060c",
    "t0": "#ffffff", "t1": "#e6f2ff", "t2": "#b8d4f0", "t3": "#8ab0d8", "tk": "#03060c", "tsh": "#000000",
}


def draw_cover_hollow():
    cv = Canvas()
    rnd = random.Random(19)
    pal = {**PAL, **HOLLOW_PAL}
    bands = ["hb0", "hb1", "hb2", "hb3", "hb4"]
    for y in range(H):
        for x in range(W):
            cv.set(x, y, dither(math.hypot((x + .5 - 60) * .8, y + .5) / 150, bands, x, y))

    # 큰 아치 창
    cx = 60
    for y in range(24, 118):
        for x in range(26, 95):
            d = math.hypot(x + .5 - cx, y + .5 - 58)
            outer = (y >= 58 and 28 <= x <= 91) or (y < 58 and d <= 32)
            inner = (y >= 58 and 33 <= x <= 86) or (y < 58 and d <= 27)
            if inner:
                t = (y - 30) / 90
                cv.set(x, y, dither(t, ["gs3", "gs2", "gs1", "gs0"], x, y))
            elif outer:
                cv.set(x, y, "fr2" if x < cx else "fr")
    # 창살 무늬
    for y in range(30, 118):
        for x in range(33, 87):
            if cv.get(x, y) and cv.get(x, y)[:2] == "gs":
                d = math.hypot(x + .5 - cx, y + .5 - 52)
                ang = math.degrees(math.atan2(y + .5 - 52, x + .5 - cx)) % 45
                if (abs(d - 14) < .8 or abs(d - 6) < .7 or (d < 14 and ang < 3)
                        or x in (46, 60, 74) and y > 66 or y == 84 or (y == 66 and d > 13)):
                    cv.set(x, y, "fr")
    # 빛줄기
    for y in range(66, 150):
        half = 14 + (y - 66) * .35
        for x in range(W):
            if abs(x + .5 - cx) < half and (x * 2 + y) % 6 == 0 and (cv.get(x, y) or "")[:2] == "hb":
                cv.set(x, y, "ry")

    # 기둥
    for x0, x1 in ((2, 18), (102, 118)):
        for y in range(18, 140):
            for x in range(x0, x1):
                cv.set(x, y, "pl2" if x == x0 + 2 else ("pl0" if (x - x0) % 5 == 4 else "pl1"))
        for y in range(14, 20):
            for x in range(x0 - 2, x1 + 2):
                cv.set(x, y, "pl2" if y == 14 else "pl1")
    # 늘어진 뿌리
    for rx in (30, 40, 82, 92):
        ln = rnd.randrange(16, 30)
        for y in range(0, ln):
            x = rx + round(math.sin(y * .3 + rx) * 1.5)
            cv.set(x, y, "cl0"); cv.set(x + 1, y, "cl0")

    # 바닥
    ground = [116 + round(noise(x, 81, 1.2)) for x in range(W)]
    for x in range(W):
        for y in range(ground[x], H):
            cv.set(x, y, "gd")
        if rnd.random() < .3:
            h = rnd.randrange(2, 5)
            for j in range(h):
                cv.set(x, ground[x] - 1 - j, "gd")
    for x in (20, 26, 88, 96, 108):
        cv.set(x, ground[x] - 4, "sp"); cv.set(x, ground[x] - 3, "gd")
    poly(cv, [(12, 117), (12, 104), (16, 101), (19, 106), (22, 100), (24, 117)], "pl0")

    # 등불을 든 방랑자 (Scale2x로 2배, 밝은 창 앞에 실루엣)
    from pixelkit import scale2x
    w_rows = [
        "....HHH.....",
        "...HHHHH....",
        "..HHFFFHH...",
        "..HFeFeFH...",
        "..HHFFFHH...",
        "...CCCCC....",
        "..CCCCCCC...",
        "..CCCCCCCa..",
        ".CCCCCCCC...",
        ".CCCCCCCCC..",
        ".CCCCCCCCC..",
        "CCCCCCCCCCC.",
        "CCCCCCCCCCC.",
        ".C.C.CC.C.C.",
    ]
    big = ["".join(r) for r in scale2x([list(r) for r in w_rows])]
    wanderer = sprite(big, 46, 88, {"H": "cl1", "F": "cl0", "e": "eye", "C": "cl0", "a": "cl1"},
                      light={"cl1": "pl2"})
    staff = Part().capsule((65, 104), (74, 82), .8, "pl2")
    staff.capsule((75, 80), (75, 80), 2.2, "lm2")
    staff.px[75, 80] = "lm"; staff.px[74, 80] = "lm"; staff.px[75, 79] = "lm"
    staff.outline("K")
    cv.part(staff); cv.part(wanderer)

    # 포자와 빛 나비
    for _ in range(36):
        x, y = rnd.randrange(W), rnd.randrange(30, 116)
        if (cv.get(x, y) or "")[:2] in ("hb", "gs", "ry"):
            cv.set(x, y, "sp")
    for mx, my in ((80, 92), (38, 80), (90, 60)):
        for p in ((mx - 1, my), (mx + 1, my), (mx, my + 1), (mx - 2, my - 1), (mx + 2, my - 1)):
            cv.set(*p, "mo")

    title(cv, ["HOLLOW", "KNIGHT"], 124)
    lights = [((75, 80), 24, (140, 220, 255)), ((60, 50), 40, (120, 180, 230))]
    return render(cv, pal, lights, lambda x, y: y < 122, add=True)


COVERS = {
    "stardew": draw_cover_stardew,
    "hollow": draw_cover_hollow,
    "terraria": draw_cover_terraria,
    "hades": draw_cover_hades,
    "eldenring": draw_cover_elden,
    "bg3": draw_cover_bg3,
    "cyberpunk": draw_cover_cyber,
    "lethal": draw_cover_lethal,
}


def main():
    import sys
    OUT_RAW.mkdir(parents=True, exist_ok=True)
    names = sys.argv[1:] or list(COVERS)
    for name in names:
        img = COVERS[name]()
        img.save(OUT_RAW / f"cover_{name}.png")
        img.resize((W * SCALE, H * SCALE), Image.NEAREST).save(OUT_SITE / f"cover-{name}.png")
        print("saved", f"cover-{name}.png")


if __name__ == "__main__":
    main()
