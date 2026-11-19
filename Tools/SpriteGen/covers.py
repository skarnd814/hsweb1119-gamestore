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

FONT = {
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
}


def noise(x, seed, amp=1.0, freqs=((0.11, 1.0), (0.29, 0.6), (0.53, 0.25))):
    rnd = random.Random(seed)
    return amp * sum(a * math.sin(x * f + rnd.uniform(0, 6.28)) for f, a in freqs)


class Canvas:
    def __init__(self):
        self.c = [[None] * W for _ in range(H)]

    def set(self, x, y, ch):
        if 0 <= x < W and 0 <= y < H:
            self.c[y][x] = ch

    def get(self, x, y):
        return self.c[y][x] if 0 <= x < W and 0 <= y < H else None

    def part(self, part):
        for (x, y), ch in part.px.items():
            self.set(x, y, ch)


def dither(t, bands, x, y):
    """0~1 위치 t를 색 띠 bands 사이에서 4x4 디더링으로 고른다."""
    f = max(0.0, min(0.9999, t)) * (len(bands) - 1)
    i = int(f)
    return bands[i + 1] if (f - i) * 16 > BAYER[y % 4][x % 4] + 0.5 else bands[i]


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
    title = "TERRARIA"
    widths = [len(FONT[c][0]) * 2 for c in title]
    total = sum(widths) + 2 * (len(title) - 1)
    x0, y0 = (W - total) // 2, 8
    letters = Part()
    x = x0
    for c, w in zip(title, widths):
        for gy, row in enumerate(FONT[c]):
            for gx, ch in enumerate(row):
                if ch == "#":
                    for ax in range(2):
                        for ay in range(2):
                            yy = gy * 2 + ay
                            col = "t0" if yy < 2 else "t1" if yy < 7 else "t2" if yy < 11 else "t3"
                            letters.px[x + gx * 2 + ax, y0 + yy] = col
        x += w + 2
    shadow = letters.moved(1, 2)
    shadow.px = {p: "tsh" for p in shadow.px}
    shadow.outline("tsh")
    letters.outline("tk")
    cv.part(shadow); cv.part(letters)

    # ---- 색 입히기 + 빛(횃불, 용암, 헬멧 등)
    pal = palette_rgba(PAL)
    img = Image.new("RGBA", (W, H))
    lights = [((tx + .5, ty - 2.5), 20, (255, 150, 50)), ((94, 143), 30, (255, 90, 20))]
    lit = set(cave)
    for (x, y) in cave:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                lit.add((x + dx, y + dy))
    for y in range(H):
        for x in range(W):
            r, g, b, a = pal[cv.c[y][x]]
            if (x, y) in lit and y > 100:
                best, col = 0.0, None
                for (lx, ly), rad, lc in lights:
                    d = math.hypot(x + .5 - lx, y + .5 - ly)
                    k = max(0.0, 1 - d / rad)
                    if k > best:
                        best, col = k, lc
                step = (0.0, 0.14, 0.26, 0.38)[min(3, int(best * 4 + (BAYER[y % 4][x % 4] / 16 - .5) * .5))]
                if col and step:
                    r, g, b = (round(v + (c - v) * step) for v, c in zip((r, g, b), col))
            img.putpixel((x, y), (r, g, b, a))
    return img


def main():
    OUT_RAW.mkdir(parents=True, exist_ok=True)
    img = draw_cover_terraria()
    img.save(OUT_RAW / "cover_terraria.png")
    big = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
    big.save(OUT_SITE / "cover-terraria.png")
    print("saved", OUT_RAW / "cover_terraria.png", OUT_SITE / "cover-terraria.png")


if __name__ == "__main__":
    main()
