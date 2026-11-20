"""Vedic + Western birth-chart calculator (Swiss Ephemeris).

Usage:
  python astro/chart.py --date 1999-12-20 --time 17:30 --tz 5.5 \
      --lat 12.5462 --lon 77.4198 [--now 2026-11-20]

Requires: pip install pyswisseph
"""
import argparse
from datetime import datetime, timedelta, timezone

import swisseph as swe

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
RASHI = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula",
         "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"]
SIGN_LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus",
             "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
              "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
              "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
              "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
              "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
              "Uttara Bhadrapada", "Revati"]
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter",
               "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
               "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
PLANETS = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
           ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
           ("Saturn", swe.SATURN), ("Rahu", swe.MEAN_NODE)]
WESTERN_EXTRA = [("Uranus", swe.URANUS), ("Neptune", swe.NEPTUNE),
                 ("Pluto", swe.PLUTO)]
EXALT = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3,
         "Venus": 11, "Saturn": 6}
OWN = {"Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
       "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10]}
YEAR = 365.2425


def dms(x):
    d = int(x)
    m = int(round((x - d) * 60))
    if m == 60:
        d, m = d + 1, 0
    return f"{d:2d}°{m:02d}'"


def fmt(lon, names=SIGNS):
    return f"{names[int(lon // 30)]:<11} {dms(lon % 30)}"


def jd_of(dt_utc):
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)


def positions(jd, sidereal):
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    if sidereal:
        flags |= swe.FLG_SIDEREAL
    out = {}
    for name, pid in PLANETS + ([] if sidereal else WESTERN_EXTRA):
        xx, _ = swe.calc_ut(jd, pid, flags)
        out[name] = (xx[0] % 360, xx[3] < 0)
    out["Ketu"] = ((out["Rahu"][0] + 180) % 360, True)
    return out


def dignity(planet, sign):
    if planet in EXALT:
        if sign == EXALT[planet]:
            return "exalted"
        if sign == (EXALT[planet] + 6) % 12:
            return "debilitated"
        if sign in OWN[planet]:
            return "own sign"
    return ""


def vimshottari(moon_lon, birth):
    span = 360 / 27
    nak = int(moon_lon // span)
    frac_left = 1 - (moon_lon % span) / span
    lord_i = nak % 9
    periods = []
    start = birth
    for k in range(9 * 2):
        lord = DASHA_ORDER[(lord_i + k) % 9]
        yrs = DASHA_YEARS[lord] * (frac_left if k == 0 else 1)
        # Back-date the first dasha's start so sub-periods line up.
        full_start = start - timedelta(days=DASHA_YEARS[lord] * (1 - frac_left) * YEAR) if k == 0 else start
        end = start + timedelta(days=yrs * YEAR)
        periods.append((lord, full_start, start, end))
        start = end
    return periods


def antardashas(maha, full_start):
    i = DASHA_ORDER.index(maha)
    t = full_start
    out = []
    for k in range(9):
        sub = DASHA_ORDER[(i + k) % 9]
        d = DASHA_YEARS[maha] * DASHA_YEARS[sub] / 120
        e = t + timedelta(days=d * YEAR)
        out.append((sub, t, e))
        t = e
    return out


def aspects(pos):
    names = list(pos)
    kinds = [(0, "conjunct", 8), (60, "sextile", 5), (90, "square", 7),
             (120, "trine", 7), (180, "opposite", 8)]
    res = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if {a, b} == {"Rahu", "Ketu"}:
                continue
            d = abs(pos[a][0] - pos[b][0]) % 360
            d = min(d, 360 - d)
            for ang, nm, orb in kinds:
                if abs(d - ang) <= orb:
                    res.append(f"{a} {nm} {b} (orb {abs(d - ang):.1f}°)")
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--date", required=True)
    p.add_argument("--time", required=True)
    p.add_argument("--tz", type=float, default=5.5)
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--now", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    a = p.parse_args()

    local = datetime.strptime(f"{a.date} {a.time}", "%Y-%m-%d %H:%M")
    utc = local - timedelta(hours=a.tz)
    jd = jd_of(utc)
    now = datetime.strptime(a.now, "%Y-%m-%d")
    jd_now = jd_of(now)

    print(f"Birth: {local} local (UTC {utc}), lat {a.lat}, lon {a.lon}\n")

    # ---------------- WESTERN ----------------
    cusps, ascmc = swe.houses(jd, a.lat, a.lon, b"P")
    wpos = positions(jd, sidereal=False)

    def whouse(lon):
        for i in range(12):
            s, e = cusps[i], cusps[(i + 1) % 12]
            if (lon - s) % 360 < (e - s) % 360:
                return i + 1
        return 12

    print("=" * 60)
    print("WESTERN (tropical zodiac, Placidus houses)")
    print("=" * 60)
    print(f"Ascendant  {fmt(ascmc[0])}")
    print(f"Midheaven  {fmt(ascmc[1])}")
    for n, (lon, r) in wpos.items():
        print(f"{n:<9}  {fmt(lon)}  house {whouse(lon):>2}{'  (R)' if r and n not in ('Rahu','Ketu') else ''}")
    print("\nMajor aspects:")
    for s in aspects({k: v for k, v in wpos.items() if k not in ("Rahu", "Ketu")}):
        print("  " + s)

    # ---------------- VEDIC ----------------
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayan = swe.get_ayanamsa_ut(jd)
    vpos = positions(jd, sidereal=True)
    asc_sid = (ascmc[0] - ayan) % 360
    lagna = int(asc_sid // 30)

    print("\n" + "=" * 60)
    print(f"VEDIC (sidereal, Lahiri ayanamsa {dms(ayan)}, whole-sign houses)")
    print("=" * 60)
    print(f"Lagna      {fmt(asc_sid, RASHI)}  (lord {SIGN_LORD[lagna]})")
    span = 360 / 27
    for n, (lon, r) in vpos.items():
        sign = int(lon // 30)
        h = (sign - lagna) % 12 + 1
        nak = int(lon // span)
        pada = int((lon % span) // (span / 4)) + 1
        dg = dignity(n, sign)
        print(f"{n:<9}  {fmt(lon, RASHI)}  house {h:>2}  {NAKSHATRAS[nak]:<17} pada {pada}"
              f"{'  (R)' if r and n not in ('Rahu','Ketu') else ''}{'  ' + dg if dg else ''}")

    moon = vpos["Moon"][0]
    print(f"\nMoon sign (Rashi): {RASHI[int(moon // 30)]}   "
          f"Janma nakshatra: {NAKSHATRAS[int(moon // span)]}")

    # Navamsa (D9)
    print("\nNavamsa (D9):")
    for n, (lon, _) in [("Lagna", (asc_sid, 0))] + list(vpos.items()):
        sign = int(lon // 30)
        part = int((lon % 30) // (30 / 9))
        start = {0: 0, 1: 9, 2: 6, 3: 3}[sign % 4]
        print(f"  {n:<8} {RASHI[(start + part) % 12]}")

    # Dashas
    print("\nVimshottari Mahadashas:")
    periods = vimshottari(moon, local)
    for lord, fs, s, e in periods:
        if e.year > 2070:
            break
        mark = "  <-- NOW" if s <= now < e else ""
        print(f"  {lord:<8} {s:%Y-%m-%d} -> {e:%Y-%m-%d}{mark}")
    for lord, fs, s, e in periods:
        if s <= now < e or (now < s and s.year <= now.year + 12):
            print(f"\n  Antardashas in {lord} Mahadasha:")
            for sub, ss, ee in antardashas(lord, fs):
                if ee < local:
                    continue
                mark = "  <-- NOW" if ss <= now < ee else ""
                print(f"    {lord}-{sub:<8} {max(ss, local):%Y-%m-%d} -> {ee:%Y-%m-%d}{mark}")

    # Transits now
    print("\n" + "=" * 60)
    print(f"TRANSITS on {now:%Y-%m-%d}")
    print("=" * 60)
    tpos = positions(jd_now, sidereal=True)
    msign = int(moon // 30)
    for n, (lon, r) in tpos.items():
        sign = int(lon // 30)
        print(f"{n:<9}  {fmt(lon, RASHI)}  house-from-Lagna {(sign - lagna) % 12 + 1:>2}"
              f"  house-from-Moon {(sign - msign) % 12 + 1:>2}{'  (R)' if r and n not in ('Rahu','Ketu') else ''}")
    s_from_moon = (int(tpos['Saturn'][0] // 30) - msign) % 12 + 1
    if s_from_moon in (12, 1, 2):
        print(f"\nSade Sati ACTIVE (Saturn in house {s_from_moon} from Moon)")
    elif s_from_moon in (4, 8):
        print(f"\nSaturn Dhaiya active (Saturn in house {s_from_moon} from Moon)")
    else:
        print(f"\nNo Sade Sati (Saturn in house {s_from_moon} from Moon)")


if __name__ == "__main__":
    main()
