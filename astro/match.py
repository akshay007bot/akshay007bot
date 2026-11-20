"""Ashtakoota (36-guna) kundali matching + Manglik check.

Usage:
  python astro/match.py --boy 1999-12-20,17:30 --girl 2001-10-08,18:15 \
      --lat 12.5462 --lon 77.4198 [--tz 5.5]
(Use --boy-lat/--girl-lat etc. if birthplaces differ.)
"""
import argparse
from datetime import datetime, timedelta

import swisseph as swe

from chart import NAKSHATRAS, RASHI, jd_of, positions

SPAN = 360 / 27
# Varna by Moon sign: 3 Brahmin, 2 Kshatriya, 1 Vaishya, 0 Shudra
VARNA = [2, 1, 0, 3, 2, 1, 0, 3, 2, 1, 0, 3]
VARNA_N = ["Shudra", "Vaishya", "Kshatriya", "Brahmin"]
# Vashya groups: C=Chatushpada, M=Manava, J=Jalachara, V=Vanachara, K=Keeta
VASHYA_T = {"C": {"C": 2, "M": 1, "J": 1, "V": .5, "K": 1},
            "M": {"C": 1, "M": 2, "J": .5, "V": 0, "K": 1},
            "J": {"C": 1, "M": .5, "J": 2, "V": 1, "K": 1},
            "V": {"C": .5, "M": 0, "J": 1, "V": 2, "K": 0},
            "K": {"C": 1, "M": 1, "J": 1, "V": 0, "K": 2}}
YONI_OF = ["Horse", "Elephant", "Sheep", "Serpent", "Serpent", "Dog", "Cat",
           "Sheep", "Cat", "Rat", "Rat", "Cow", "Buffalo", "Tiger", "Buffalo",
           "Tiger", "Deer", "Deer", "Dog", "Monkey", "Mongoose", "Monkey",
           "Lion", "Horse", "Lion", "Cow", "Elephant"]
YONI_ORDER = ["Horse", "Elephant", "Sheep", "Serpent", "Dog", "Cat", "Rat",
              "Cow", "Buffalo", "Tiger", "Deer", "Monkey", "Mongoose", "Lion"]
YONI_M = [[4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 3, 3, 2, 1],
          [2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0],
          [2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1],
          [3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2],
          [2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1],
          [2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1],
          [2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2],
          [1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1],
          [0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1],
          [1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1],
          [3, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1],
          [3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2],
          [2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2],
          [1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4]]
LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars",
        "Jupiter", "Saturn", "Saturn", "Jupiter"]
FRIENDS = {"Sun": ({"Moon", "Mars", "Jupiter"}, {"Mercury"}),
           "Moon": ({"Sun", "Mercury"}, {"Mars", "Jupiter", "Venus", "Saturn"}),
           "Mars": ({"Sun", "Moon", "Jupiter"}, {"Venus", "Saturn"}),
           "Mercury": ({"Sun", "Venus"}, {"Mars", "Jupiter", "Saturn"}),
           "Jupiter": ({"Sun", "Moon", "Mars"}, {"Saturn"}),
           "Venus": ({"Mercury", "Saturn"}, {"Mars", "Jupiter"}),
           "Saturn": ({"Mercury", "Venus"}, {"Mars", "Jupiter"})}
GANA = "DMRMDMDDRRMMDRDRDRRMMDRRMMD"  # per nakshatra
GANA_N = {"D": "Deva", "M": "Manushya", "R": "Rakshasa"}
GANA_T = {("D", "D"): 6, ("D", "M"): 6, ("D", "R"): 1,
          ("M", "D"): 5, ("M", "M"): 6, ("M", "R"): 0,
          ("R", "D"): 0, ("R", "M"): 0, ("R", "R"): 6}  # (boy, girl)
NADI = [0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1,
        0, 0, 1, 2]
NADI_N = ["Adi", "Madhya", "Antya"]


def vashya(lon):
    s, d = int(lon // 30), lon % 30
    if s in (0, 1) or (s == 8 and d >= 15) or (s == 9 and d < 15):
        return "C"
    if s in (3, 11) or (s == 9 and d >= 15):
        return "J"
    if s == 4:
        return "V"
    if s == 7:
        return "K"
    return "M"


def rel(a, b):
    if a == b:
        return "F"
    f, e = FRIENDS[a]
    return "F" if b in f else "E" if b in e else "N"


def maitri(a, b):
    r = {rel(a, b), rel(b, a)}
    if r == {"F"}:
        return 5
    if r == {"F", "N"}:
        return 4
    if r == {"N"}:
        return 3
    if r == {"F", "E"}:
        return 1
    if r == {"N", "E"}:
        return .5
    return 0


def tara(from_n, to_n):
    return ((to_n - from_n) % 27 + 1) % 9 not in (3, 5, 7)


def info(date, time, tz, lat, lon):
    local = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    jd = jd_of(local - timedelta(hours=tz))
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    pos = positions(jd, sidereal=True)
    _, ascmc = swe.houses(jd, lat, lon, b"P")
    asc = (ascmc[0] - swe.get_ayanamsa_ut(jd)) % 360
    return pos, asc


def manglik(pos, asc):
    mars = int(pos["Mars"][0] // 30)
    out = {}
    for ref, lon in (("Lagna", asc), ("Moon", pos["Moon"][0]),
                     ("Venus", pos["Venus"][0])):
        h = (mars - int(lon // 30)) % 12 + 1
        out[ref] = (h, h in (1, 2, 4, 7, 8, 12))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--boy", required=True)
    p.add_argument("--girl", required=True)
    p.add_argument("--tz", type=float, default=5.5)
    p.add_argument("--lat", type=float)
    p.add_argument("--lon", type=float)
    for w in ("boy", "girl"):
        p.add_argument(f"--{w}-lat", type=float)
        p.add_argument(f"--{w}-lon", type=float)
    a = p.parse_args()

    data = {}
    for w in ("boy", "girl"):
        d, t = getattr(a, w).split(",")
        lat = getattr(a, f"{w}_lat") or a.lat
        lon = getattr(a, f"{w}_lon") or a.lon
        data[w] = info(d, t, a.tz, lat, lon)

    (bp, ba), (gp, ga) = data["boy"], data["girl"]
    bm, gm = bp["Moon"][0], gp["Moon"][0]
    bs, gs = int(bm // 30), int(gm // 30)
    bn, gn = int(bm // SPAN), int(gm // SPAN)

    for w, m, n in (("Boy", bm, bn), ("Girl", gm, gn)):
        print(f"{w:<5} Moon: {RASHI[int(m // 30)]}, {NAKSHATRAS[n]} "
              f"(Gana {GANA_N[GANA[n]]}, Nadi {NADI_N[NADI[n]]}, "
              f"Yoni {YONI_OF[n]}, Varna {VARNA_N[VARNA[int(m // 30)]]})")
    print()

    rows = []
    rows.append(("Varna", 1, 1 if VARNA[bs] >= VARNA[gs] else 0,
                 "work/ego compatibility"))
    rows.append(("Vashya", 2, VASHYA_T[vashya(bm)][vashya(gm)],
                 "mutual attraction/influence"))
    rows.append(("Tara", 3, 1.5 * tara(gn, bn) + 1.5 * tara(bn, gn),
                 "health & fortune together"))
    yb, yg = YONI_ORDER.index(YONI_OF[bn]), YONI_ORDER.index(YONI_OF[gn])
    rows.append(("Yoni", 4, YONI_M[yb][yg], "physical/intimate compatibility"))
    gm_score = maitri(LORD[bs], LORD[gs])
    rows.append(("Graha Maitri", 5, gm_score, "mental friendship"))
    rows.append(("Gana", 6, GANA_T[(GANA[bn], GANA[gn])], "temperament"))
    dist = (gs - bs) % 12 + 1
    bhak_bad = dist in (2, 12, 5, 9, 6, 8)
    rows.append(("Bhakoot", 7, 0 if bhak_bad else 7,
                 f"family/finance/emotional bond (signs {dist}/{(bs - gs) % 12 + 1} apart)"))
    rows.append(("Nadi", 8, 0 if NADI[bn] == NADI[gn] else 8,
                 "health/progeny"))

    total = 0
    for name, mx, sc, note in rows:
        total += sc
        print(f"{name:<13} {sc:>4} / {mx}   {note}")
    print(f"{'TOTAL':<13} {total:>4} / 36")
    verdict = ("excellent" if total >= 32 else "very good" if total >= 28 else
               "good" if total >= 24 else "acceptable" if total >= 18 else
               "not recommended traditionally")
    print(f"Traditional verdict: {verdict} (18+ is the usual minimum)\n")

    print("Dosha cancellations (classical rules):")
    if bhak_bad:
        lb, lg = LORD[bs], LORD[gs]
        ok = lb == lg or (rel(lb, lg) == "F" and rel(lg, lb) == "F")
        print(f"  Bhakoot dosha: Moon-sign lords {lb} & {lg} "
              f"{'are mutual friends -> CANCELLED' if ok else 'not mutual friends -> stands'}")
    if GANA_T[(GANA[bn], GANA[gn])] == 0:
        print(f"  Gana dosha: {'Graha Maitri is strong -> commonly treated as CANCELLED' if gm_score >= 4 else 'stands'}")
    if NADI[bn] == NADI[gn]:
        print("  Nadi dosha present (most serious koota)")
    else:
        print("  No Nadi dosha")

    print("\nManglik check (Mars in 1/2/4/7/8/12):")
    for w, (pos, asc) in (("Boy", data["boy"]), ("Girl", data["girl"])):
        m = manglik(pos, asc)
        s = ", ".join(f"from {k}: house {h}{' MANGLIK' if f else ''}"
                      for k, (h, f) in m.items())
        print(f"  {w:<5} Mars in {RASHI[int(pos['Mars'][0] // 30)]} — {s}")


if __name__ == "__main__":
    main()
