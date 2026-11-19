"""GameStore 히어로 슬라이드 배경 도트 그림 생성기 (pixelkit + covers.py의 그리기 도구).

320x160 도트로 그린 뒤 5배(1600x800)로 키워 img/hero-*.png 로 넣는다. 원본 크기는 sprites/ 에 남긴다.
슬라이드 글이 왼쪽에 겹치므로 보여 줄 대상(해, 헛간, 크리스탈, 달, 황금 나무)은 오른쪽에 둔다.
실행: python Tools/SpriteGen/heroes.py [farm cavern neon golden]
"""
import math
import random
import sys

from PIL import Image
from pixelkit import Part, scale2x

from covers import (BAYER, PAL, Canvas, OUT_RAW, OUT_SITE, disc, dither, noise, poly, render, sky, sprite,
                    stars)

HW, HH = 320, 160
SCALE = 5


def ridge(cv, base, amp, seed, ch, freqs=((0.04, 1.0), (0.11, .5)), x0=0, x1=HW):
    """noise 능선 아래를 ch로 채우고 높이 목록을 돌려준다."""
    hs = []
    for x in range(x0, x1):
        h = round(base + noise(x, seed, amp, freqs))
        hs.append(h)
        for y in range(h, HH):
            cv.set(x, y, ch)
    return hs


def scaled(rows):
    return ["".join(r) for r in scale2x([list(r) for r in rows])]


# ============================================================
# 1. 노을 지는 농장 (스타듀 밸리 슬라이드)
# ============================================================
FARM_PAL = {
    "f0": "#1c1240", "f1": "#3a1f5a", "f2": "#6a2f6e", "f3": "#b2486c", "f4": "#ec7258", "f5": "#ffad6a",
    "sun": "#fff4c8", "sun2": "#ffd47a", "cs": "#ff9a84", "cs2": "#c86478",
    "mf": "#6b3f70", "mm": "#4a3a5e", "hm": "#56743f", "hm2": "#44603a",
    "hn": "#2e4a2a", "hn2": "#22381f", "cr": "#5c8c38", "cr2": "#86b84a",
    "br": "#7a2632", "br2": "#9c3440", "brf": "#3d1522", "brf2": "#5a2032", "dr": "#e8c8a0", "win": "#ffd27a",
    "sl": "#4e3f58", "sl2": "#6a5878", "ts": "#1d3022", "ts2": "#2a4430", "fn": "#1a120f", "ff": "#fff4a8",
}


def hero_farm():
    cv = Canvas(HW, HH)
    rnd = random.Random(21)
    pal = {**PAL, **FARM_PAL}
    sky(cv, ["f0", "f1", "f2", "f3", "f4", "f5"], 0, HH, 112)
    stars(cv, rnd, 26, 40, skip=(-1, -1))

    # 해와 빛 무리
    sx, sy = 226, 94
    for y in range(sy - 30, sy + 30):
        for x in range(sx - 30, sx + 30):
            d = math.hypot(x + .5 - sx, y + .5 - sy)
            if d <= 14:
                cv.set(x, y, "sun")
            elif d <= 17:
                cv.set(x, y, "sun2")
            elif d <= 27 and BAYER[y % 4][x % 4] < (27 - d) * 1.3:
                cv.set(x, y, "f5")
    # 구름 띠
    for cy, x0, x1 in ((58, 150, 250), (64, 230, 310), (72, 120, 200), (80, 250, 320), (50, 40, 130)):
        for x in range(x0, x1):
            edge = min(x - x0, x1 - x) / 10
            if edge > .4 or BAYER[cy % 4][x % 4] < edge * 16:
                cv.set(x, cy, "cs")
                if x0 + 6 < x < x1 - 6:
                    cv.set(x, cy + 1, "cs2")
    # 새
    for bx, by in ((200, 70), (210, 64), (192, 62)):
        for p in ((bx, by), (bx + 1, by - 1), (bx + 2, by), (bx + 3, by - 1), (bx + 4, by)):
            cv.set(*p, "K")

    ridge(cv, 94, 7, 101, "mf")
    ridge(cv, 103, 4, 102, "mm", ((0.03, 1.0), (0.09, .4)))
    hills = ridge(cv, 113, 3, 103, "hm", ((0.02, 1.0), (0.05, .5)))
    for x in range(HW):
        cv.set(x, hills[x], "hm2" if x % 3 else "hm")

    # 헛간과 사일로
    gy = min(hills[250:295])
    barn = sprite(scaled([
        "......RRRR......",
        "....RRRRRRRR....",
        "..RRRRRRRRRRRR..",
        "rrrrrrrrrrrrrrrr",
        ".BBBBBBBBBBBBBB.",
        ".BwBBBBBBBBBBwB.",
        ".BBBBBDDDDBBBBB.",
        ".BBBBBDXXDBBBBB.",
        ".BBBBBDXXDBBBBB.",
        ".BBBBBDDDDBBBBB.",
    ]), 250, gy - 19, {"R": "brf2", "r": "brf", "B": "br", "w": "win", "D": "dr", "X": "brf"},
        light={"br": "br2"})
    silo = sprite(scaled([
        "..SSSS..",
        ".SSSSSS.",
        "SSSSSSSS",
        "SSSSSSSS",
        "SSSSSSSS",
        "SSSSSSSS",
        "SSSSSSSS",
        "SSSSSSSS",
        "SSSSSSSS",
        "SSSSSSSS",
        "SSSSSSSS",
        "SSSSSSSS",
    ]), 284, gy - 23, {"S": "sl"}, light={"sl": "sl2"})
    cv.part(silo); cv.part(barn)

    def tree(x, base, r, h):
        t = Part().capsule((x, base), (x, base - h), 1.3, "ts")
        for dx, dy, rr in ((0, 0, r), (-r * .7, r * .5, r * .7), (r * .7, r * .5, r * .7), (0, -r * .6, r * .7)):
            t.capsule((x + dx, base - h - r * .4 + dy), (x + dx, base - h - r * .4 + dy), rr, "ts")
        t.light({"ts": "ts2"})
        cv.part(t)

    tree(196, hills[196] + 1, 7, 8)
    tree(184, hills[184] + 1, 4.5, 5)
    tree(312, hills[312] + 1, 8, 9)
    tree(26, 130, 13, 14)

    # 앞쪽 밭 (구부러진 고랑)
    def fy(x, off=0):
        return 128 + off + round(-6 * math.sin(x / HW * math.pi * .9 + .3))

    for x in range(HW):
        for y in range(fy(x), HH):
            cv.set(x, y, "hn")
        for k, off in enumerate(range(4, 40, 5)):
            y = fy(x, off)
            cv.set(x, y, "cr" if k % 2 else "cr2")
            if (x + k * 3) % 7 == 0:
                cv.set(x, y - 1, "cr2")
    for y in range(150, HH):
        for x in range(HW):
            if (x + y) % 2 == 0:
                cv.set(x, y, "hn2")
    # 울타리
    posts = list(range(150, HW + 8, 14))
    for x in posts:
        top = fy(x) - 12
        for y in range(top, top + 16):
            cv.set(x, y, "fn"); cv.set(x + 1, y, "fn")
    for off in (3, 9):
        for x in range(150, HW):
            cv.set(x, fy(x) - 12 + off, "fn")
    # 반딧불
    for _ in range(18):
        x, y = rnd.randrange(150, HW), rnd.randrange(128, 156)
        cv.set(x, y, "ff")
    lights = [((sx, sy), 70, (255, 190, 110))] + [((x, y), 4, (255, 240, 160))
                                                   for x, y in ((180, 140), (250, 146), (290, 136))]
    return render(cv, pal, lights, add=True)


# ============================================================
# 2. 지하 동굴 (할로우 나이트 슬라이드)
# ============================================================
CAVERN_PAL = {
    "v0": "#02050d", "v1": "#061224", "v2": "#0a1d36", "v3": "#0e2b4a",
    "bm": "#1d4a70", "ru": "#0f2a4a", "ru2": "#0b2140", "stc": "#02050c",
    "cy0": "#1550a2", "cy1": "#45d4f2", "cy2": "#d6fdff", "gr": "#050d1a", "gr2": "#02060e",
    "cw": "#0a111f", "cw2": "#16233a", "ey": "#ffe2a8", "ln": "#ffcf6a", "ln2": "#fff4c4", "mt": "#9ef2ff",
    "lg": "#6a4a2a", "lg0": "#3a2e2a",
}


def hero_cavern():
    cv = Canvas(HW, HH)
    rnd = random.Random(23)
    pal = {**PAL, **CAVERN_PAL}
    sky(cv, ["v0", "v1", "v2", "v3"], 0, HH)

    # 천장 틈의 빛줄기
    for top0, top1, spread, a in ((200, 214, 60, .26), (236, 244, 36, .2), (150, 156, 22, .14)):
        for y in range(0, 140):
            t = y / 140
            l, r = top0 + spread * .3 * t, top1 + spread * t
            for x in range(int(l), int(r) + 1):
                if BAYER[y % 4][x % 4] < 16 * a * (1 - t * .8):
                    cv.set(x, y, "bm")

    # 먼 폐허
    def arch(x0, w, top, ch):
        for y in range(top, 134):
            for x in range(x0, x0 + w):
                d = math.hypot(x + .5 - (x0 + w / 2), y + .5 - (top + w / 2))
                inner = abs(x + .5 - (x0 + w / 2)) < w / 2 - 4 and (y > top + w / 2 or d < w / 2 - 4)
                outer = y > top + w / 2 or d < w / 2
                if outer and not inner:
                    cv.set(x, y, ch)

    arch(112, 34, 72, "ru"); arch(262, 40, 62, "ru"); arch(188, 26, 92, "ru2")
    for x0, w, top in ((150, 9, 60), (304, 10, 50), (92, 12, 88), (236, 8, 84)):
        for y in range(top, 134):
            for x in range(x0, x0 + w):
                cv.set(x, y, "ru")
        poly(cv, [(x0, top), (x0 + w / 2, top - 12), (x0 + w, top)], "ru")

    # 종유석
    for x in range(HW):
        ln = 6 + round(abs(noise(x, 201, 10, ((0.13, 1.0), (0.37, .6), (0.71, .3)))))
        for y in range(ln):
            cv.set(x, y, "stc")

    # 땅
    ground = [132 + round(noise(x, 203, 2.2, ((0.03, 1.0), (0.08, .5)))) for x in range(HW)]
    for x in range(HW):
        for y in range(ground[x], HH):
            cv.set(x, y, "gr" if y < 146 else "gr2")

    # 크리스탈
    def crystal(cx, base, shards):
        for dx, h, w, ch in shards:
            poly(cv, [(cx + dx - w, base), (cx + dx, base - h), (cx + dx + w, base)], ch)
            poly(cv, [(cx + dx, base - h), (cx + dx + w, base), (cx + dx + w * .3, base)], "cy0")

    crystal(276, ground[276] + 2, ((-22, 18, 5, "cy0"), (-10, 40, 7, "cy1"), (4, 30, 6, "cy1"),
                                   (16, 20, 5, "cy0"), (26, 12, 4, "cy0")))
    crystal(124, ground[124] + 2, ((-6, 16, 4, "cy1"), (4, 10, 3, "cy0")))
    for x, y in ((266, 100), (270, 108), (280, 112)):
        cv.set(x, y, "cy2")

    # 랜턴을 든 방랑자
    rows = [
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
    gx = 200
    wander = sprite(scaled(rows), gx, ground[gx + 10] - 28, {"H": "cw2", "F": "cw", "e": "ey", "C": "cw", "a": "cw2"},
                    light={"cw2": "bm"})
    by = ground[gx + 10] - 28
    pole = Part().capsule((gx + 19, by + 16), (gx + 30, by + 6), .7, "cw2")
    pole.capsule((gx + 30, by + 6), (gx + 30, by + 10), .4, "cw2")
    pole.outline("K")
    cv.part(pole); cv.part(wander)
    lx, ly = gx + 30, by + 12
    # 랜턴 둘레의 따뜻한 빛 (배경 위에만 디더링)
    for y in range(ly - 16, ly + 18):
        for x in range(lx - 18, lx + 18):
            d = math.hypot(x + .5 - lx, y + .5 - ly)
            cur = cv.get(x, y) or ""
            if d < 16 and BAYER[y % 4][x % 4] < (16 - d) * 1.1:
                if cur[:1] in ("v", "b", "r"):
                    cv.set(x, y, "lg" if d < 9 else "lg0")
                elif cur in ("cw", "cw2", "gr"):
                    cv.set(x, y, "lg0")
    for p, ch in (((lx - 1, ly), "ln"), ((lx, ly), "ln2"), ((lx + 1, ly), "ln"), ((lx - 1, ly + 1), "ln"),
                  ((lx, ly + 1), "ln2"), ((lx + 1, ly + 1), "ln"), ((lx, ly + 2), "ln")):
        cv.set(*p, ch)

    # 떠다니는 빛
    for _ in range(46):
        x, y = rnd.randrange(110, HW), rnd.randrange(20, 130)
        if (cv.get(x, y) or "")[:1] in ("v", "b"):
            cv.set(x, y, "mt")
    lights = [((268, 116), 56, (80, 220, 255)), ((124, 128), 26, (80, 220, 255))]
    return render(cv, pal, lights, add=True)


# ============================================================
# 3. 네온 도시 (사이버펑크 2077 슬라이드)
# ============================================================
NEON_PAL = {
    "n0": "#06021a", "n1": "#12073a", "n2": "#2a0b4a", "n3": "#4b1460", "n4": "#6a1a66",
    "mn": "#ffe6fa", "mn2": "#ff9be6", "mn3": "#c050d0", "hz": "#8a2a7a",
    "bf": "#1d0f3e", "bm": "#110726", "bn": "#07030f",
    "wc": "#2a8cb0", "wp": "#a03a9a", "wy": "#c8a040",
    "np": "#ff2bd6", "np2": "#ffb0f2", "nc": "#2ee6ff", "nc2": "#c8fbff", "ny": "#fcee0a", "ny2": "#fffbb0",
    "st0": "#150630", "st1": "#07020f", "tr": "#ff3b6b", "tw": "#fff7d6", "rn": "#5a5a94", "red": "#ff2a3a",
}


def hero_neon():
    cv = Canvas(HW, HH)
    rnd = random.Random(25)
    pal = {**PAL, **NEON_PAL}
    sky(cv, ["n0", "n1", "n2", "n3", "n4"], 0, 140)
    stars(cv, rnd, 20, 50, skip=(-1, -1))

    # 달
    mx, my = 240, 52
    for y in range(my - 44, my + 44):
        for x in range(mx - 44, mx + 44):
            d = math.hypot(x + .5 - mx, y + .5 - my)
            if d <= 30:
                t = (y - (my - 30)) / 60
                ch = dither(t, ["mn", "mn2", "mn3"], x, y)
                if y > my and (y - my) % 7 < 1 + (y - my) // 10:
                    ch = "n3"
                cv.set(x, y, ch)
            elif d <= 42 and BAYER[y % 4][x % 4] < (42 - d) * .9:
                cv.set(x, y, "hz")

    def tower(x0, w, top, ch, win, dens):
        for y in range(top, 140):
            for x in range(x0, x0 + w):
                cv.set(x, y, ch)
                if win and (x - x0) % 3 == 1 and (y - top) % 4 == 2 and rnd.random() < dens:
                    cv.set(x, y, win)

    x = 0
    while x < HW:
        w = rnd.randrange(8, 16)
        tower(x, w, rnd.randrange(66, 104), "bf", "wy" if rnd.random() < .3 else None, .3)
        x += w
    x = 0
    while x < HW:
        w = rnd.randrange(10, 20)
        tower(x, w, rnd.randrange(86, 118), "bm", rnd.choice(("wc", "wp")), .45)
        x += w + rnd.randrange(0, 6)
    # 오른쪽 앞 빌딩과 간판
    for x0, w, top in ((190, 26, 70), (226, 18, 96), (262, 30, 62), (300, 20, 88)):
        tower(x0, w, top, "bn", rnd.choice(("wc", "wp", "wy")), .35)
    for y in range(78, 124):
        for x in range(266, 276):
            edge = x in (266, 275) or y in (78, 123)
            cv.set(x, y, "np" if edge else ("np2" if (y - 80) % 8 < 4 and 268 <= x <= 273 else "bn"))
    for y in range(100, 109):
        for x in range(194, 228):
            edge = x in (194, 227) or y in (100, 108)
            cv.set(x, y, "nc" if edge else ("nc2" if y == 104 and (x - 197) % 5 < 3 else "bn"))
    for y in range(116, 123):
        for x in range(232, 250):
            edge = x in (232, 249) or y in (116, 122)
            cv.set(x, y, "ny" if edge else ("ny2" if y in (118, 120) and x % 3 else "bn"))
    for y in range(92, 120, 3):
        for x in range(304, 316):
            if (x + y) % 2:
                cv.set(x, y, "nc")
    cv.set(275, 60, "red"); cv.set(203, 68, "red")
    # 하늘을 나는 차
    for cx, cy in ((150, 62), (300, 40)):
        for dx in range(-3, 4):
            cv.set(cx + dx, cy, "bf")
        for dx in range(-2, 3):
            cv.set(cx + dx, cy - 1, "bf")
        cv.set(cx + 4, cy, "ny2"); cv.set(cx - 4, cy, "red")

    # 거리
    for y in range(140, HH):
        for x in range(HW):
            cv.set(x, y, dither((y - 140) / 20, ["st0", "st1"], x, y))
    for x0, w, ch in ((266, 10, "np"), (194, 34, "nc"), (232, 18, "ny")):
        for i, y in enumerate(range(142, 158, 2)):
            for x in range(x0 + i, x0 + w - i):
                if (x + i) % 3 == 0:
                    cv.set(x, y, ch)
    for y, ch, x0 in ((146, "tr", 120), (150, "tw", 60), (153, "tr", 160)):
        for x in range(x0, HW):
            if BAYER[y % 4][x % 4] < (x - x0) / (HW - x0) * 16:
                cv.set(x, y, ch)
    # 비
    for _ in range(320):
        x, y = rnd.randrange(HW), rnd.randrange(0, HH)
        for i in range(3):
            cv.set(x + i // 2, y + i, "rn")
    lights = [((270, 100), 26, (255, 60, 220)), ((211, 104), 24, (60, 230, 255)), ((241, 119), 16, (255, 240, 40))]
    return render(cv, pal, lights, lambda x, y: y < 140, steps=(0.0, 0.1, 0.2), add=True)


# ============================================================
# 4. 황금 나무 (엘든 링 슬라이드)
# ============================================================
GOLD_PAL = {
    "g0": "#0e0a22", "g1": "#2c2050", "g2": "#6b4466", "g3": "#cf9558", "g4": "#f2c983",
    "gl0": "#a8681a", "gl1": "#e2a838", "gl2": "#ffd97a", "gl3": "#fff6d0", "tr0": "#6e4212", "tr1": "#c48a2e",
    "m0": "#4c3462", "m1": "#2b1f3d", "cs": "#1b1328", "cw": "#ffb35a",
    "k1": "#0d0816", "k2": "#241a30", "ar0": "#2a2a36", "ar1": "#4e5064", "ar2": "#7a7e94", "cp": "#4a1e22",
    "cp2": "#2c1014",
}


def hero_golden():
    cv = Canvas(HW, HH)
    rnd = random.Random(27)
    pal = {**PAL, **GOLD_PAL}
    sky(cv, ["g0", "g1", "g2", "g3", "g4"], 0, HH, 116)
    stars(cv, rnd, 30, 50, skip=(-1, -1))

    ridge(cv, 92, 8, 301, "m0")
    mid = ridge(cv, 112, 5, 302, "m1", ((0.03, 1.0), (0.09, .5)))

    # 성 (가운데 능선 위)
    cx0 = 136
    base = min(mid[cx0:cx0 + 40]) + 2
    castle = sprite(scaled([
        "..#.......#.........",
        ".###..#..###....#...",
        ".###.###.###...###..",
        ".###.###.###...###..",
        "####################",
        "###w###w#####w######",
        "####################",
    ]), cx0, base - 14, {"#": "cs", "w": "cw"}, ink=None)
    cv.part(castle)

    # 황금 나무
    tx, ground = 240, 118
    tree = Part()
    tree.capsule((tx, ground), (tx, ground - 24), 5.0, "tr1")
    tree.capsule((tx, ground - 24), (tx, ground - 46), 3.4, "tr1")
    for a, b, r in (((tx, ground - 36), (tx - 30, ground - 56), 2.0), ((tx, ground - 36), (tx + 30, ground - 56), 2.0),
                    ((tx, ground - 44), (tx - 16, ground - 66), 1.6), ((tx, ground - 44), (tx + 16, ground - 66), 1.6),
                    ((tx, ground - 46), (tx, ground - 72), 1.5),
                    ((tx - 3, ground - 2), (tx - 16, ground + 3), 2.0), ((tx + 3, ground - 2), (tx + 16, ground + 3), 2.0)):
        tree.capsule(a, b, r, "tr1")
    tree.shade({"tr1": "tr0"}).light({"tr1": "gl1"})
    cv.part(tree)
    # 수관: 겹친 잎 덩어리로 우산 모양, 덩어리 아래쪽만 어둡게
    clumps = ((tx, 50, 17), (tx - 20, 56, 15), (tx + 20, 56, 15), (tx - 38, 66, 12), (tx + 38, 66, 12),
              (tx - 10, 38, 13), (tx + 10, 38, 13), (tx, 28, 10), (tx - 54, 74, 8), (tx + 54, 74, 8),
              (tx - 28, 46, 10), (tx + 28, 46, 10))
    crown = Part()
    for x, y, r in clumps:
        crown.capsule((x, y), (x, y), r, "gl1")
    order = sorted(clumps, key=lambda c: c[1])
    for (x, y) in list(crown.px):
        # 가장 아래(앞)에 있는 덩어리를 기준으로 음영
        owner = None
        for c in order:
            if math.hypot(x + .5 - c[0], y + .5 - c[1]) <= c[2]:
                owner = c
        rel = (y + .5 - owner[1]) / owner[2]
        if rel > .62:
            crown.px[x, y] = "gl0"
        elif rel < -.5 and x < owner[0]:
            crown.px[x, y] = "gl2"
        elif rnd.random() < .06:
            crown.px[x, y] = "gl0"
    crown.light({"gl1": "gl2"})
    for _ in range(40):
        p = rnd.choice(list(crown.px))
        if crown.px[p] != "gl0":
            crown.px[p] = "gl3"
    cv.part(crown)
    for x, y in ((tx - 14, 70), (tx + 14, 70), (tx - 34, 80), (tx + 34, 80), (tx, 62)):
        cv.set(x, y, "tr0")

    # 떨어지는 잎
    for _ in range(60):
        x, y = rnd.randrange(130, HW), rnd.randrange(60, 150)
        if (cv.get(x, y) or "")[:1] in ("g", "m"):
            cv.set(x, y, "gl2" if rnd.random() < .5 else "gl1")

    # 앞 절벽과 기사
    poly(cv, [(0, 128), (120, 126), (176, 130), (196, 134), (204, 160), (0, 160)], "k1")
    poly(cv, [(204, 160), (214, 148), (320, 142), (320, 160)], "k1")
    for x in range(0, 204):
        for y in range(120, 150):
            if cv.get(x, y) == "k1":
                cv.set(x, y, "k2")
                break
    knight_rows = [
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
    ]
    kx, ky = 170, 130 - 30
    sword = Part().capsule((kx + 3, ky + 2), (kx + 22, ky + 26), 1.0, "ar2")
    sword.capsule((kx + 3, ky + 7), (kx + 9, ky + 3), .8, "ar0")
    sword.outline("K")
    knight = sprite(scaled(knight_rows), kx, ky, {"H": "ar1", "A": "ar1", "C": "cp", "L": "ar0", "B": "K"},
                    shade={"ar1": "ar0", "cp": "cp2"}, light={"ar1": "ar2"})
    cv.part(sword); cv.part(knight)

    lights = [((tx, 56), 90, (255, 200, 110))]
    return render(cv, pal, lights, add=True)


HEROES = {"farm": hero_farm, "cavern": hero_cavern, "neon": hero_neon, "golden": hero_golden}


def main():
    OUT_RAW.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or list(HEROES):
        img = HEROES[name]()
        img.save(OUT_RAW / f"hero_{name}.png")
        img.resize((HW * SCALE, HH * SCALE), Image.NEAREST).save(OUT_SITE / f"hero-{name}.png")
        print("saved", f"hero-{name}.png")


if __name__ == "__main__":
    main()
