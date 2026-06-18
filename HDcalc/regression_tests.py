#!/usr/bin/env python3
"""
Regression tests for Human Design Calculator gate lookup.
Tests validate that gate assignments match expected values from etalon data.

Run:  python3 regression_tests.py
Exit 0 = all PASS, Exit 1 = failures found
"""

import json
import bisect
import sys
import swisseph as swe
from pathlib import Path

# ── Setup ──────────────────────────────────────────────────────────────────────
swe.set_ephe_path("")  # use built-in Moshier ephemeris

LOOKUP_PATH = Path(__file__).with_name("fullhd_lookup.json")
GL = json.loads(LOOKUP_PATH.read_text(encoding="utf-8"))
GL_LONS = [e[0] for e in GL]
iflag = swe.FLG_MOSEPH | swe.FLG_SPEED

def lookup(lon):
    lon = lon % 360.0
    idx = bisect.bisect_right(GL_LONS, lon) - 1
    if idx < 0:
        idx = len(GL) - 1
    e = GL[idx]
    return e[1], e[2], e[3], e[4]

def design_jd(birth_jd):
    res, _ = swe.calc_ut(birth_jd, swe.SUN, iflag)
    target = (res[0] - 88.0) % 360.0
    jd = birth_jd - 88.0
    for _ in range(50):
        res, _ = swe.calc_ut(jd, swe.SUN, iflag)
        diff = (target - res[0] + 180) % 360 - 180
        if abs(diff) < 1e-8:
            break
        spd = res[3] if res[3] > 0.01 else 0.9856
        jd += diff / spd
    return jd

PLANETS = [
    (swe.SUN,       'Sun'),
    (swe.MOON,      'Moon'),
    (swe.MERCURY,   'Mercury'),
    (swe.VENUS,     'Venus'),
    (swe.MARS,      'Mars'),
    (swe.JUPITER,   'Jupiter'),
    (swe.SATURN,    'Saturn'),
    (swe.URANUS,    'Uranus'),
    (swe.NEPTUNE,   'Neptune'),
    (swe.PLUTO,     'Pluto'),
    (swe.TRUE_NODE, 'N.Node'),
    (swe.CHIRON,    'Chiron'),
]

def calc_gates(year, month, day, hour, minute, tz_offset):
    """Return (personality_gates, design_gates, all_gates, planet_table)."""
    ut_h = hour + minute / 60.0 - tz_offset
    bjd = swe.julday(year, month, day, ut_h)
    djd = design_jd(bjd)

    p_gates, d_gates = set(), set()
    table = []
    sun_lp = sun_ld = nn_lp = nn_ld = None

    for pid, name in PLANETS:
        try:
            rp, _ = swe.calc_ut(bjd, pid, iflag)
            rd, _ = swe.calc_ut(djd, pid, iflag)
            lp, ld = rp[0], rd[0]
            gp, lnp, _, _ = lookup(lp)
            gd, lnd, _, _ = lookup(ld)
            p_gates.add(gp)
            d_gates.add(gd)
            table.append((name, round(lp, 3), gp, lnp, round(ld, 3), gd, lnd))
            if name == 'Sun':    sun_lp = lp; sun_ld = ld
            if name == 'N.Node': nn_lp  = lp; nn_ld  = ld
        except Exception:
            pass  # Chiron may fail without SE files; continue

    # Earth = Sun + 180
    if sun_lp is not None:
        elp = (sun_lp + 180) % 360
        eld = (sun_ld + 180) % 360
        eg_p, el_p, _, _ = lookup(elp)
        eg_d, el_d, _, _ = lookup(eld)
        p_gates.add(eg_p); d_gates.add(eg_d)
        table.insert(1, ('Earth', round(elp, 3), eg_p, el_p, round(eld, 3), eg_d, el_d))

    # South Node = N.Node + 180
    if nn_lp is not None:
        slp = (nn_lp + 180) % 360
        sld = (nn_ld + 180) % 360
        sg_p, sl_p, _, _ = lookup(slp)
        sg_d, sl_d, _, _ = lookup(sld)
        p_gates.add(sg_p); d_gates.add(sg_d)
        table.append(('S.Node', round(slp, 3), sg_p, sl_p, round(sld, 3), sg_d, sl_d))

    return p_gates, d_gates, p_gates | d_gates, table


# ── Test cases ─────────────────────────────────────────────────────────────────
# Format: (description, year, month, day, hour, minute, tz, must_have_gates, must_not_have_gates)
TESTS = [
    (
        "20.05.1974 15:25 Киев (UTC+3) — основной кейс",
        1974, 5, 20, 15, 25, 3,
        [45],   # Gate 45 обязан присутствовать (S.Node Personality ≈ 79.5°)
        [],
    ),
    (
        "Lookup: Gate 42 при lon=24.4° (контрольная точка эталона)",
        None, None, None, None, None, None,  # специальный lookup-тест
        [],
        [],
        {"lon_check": (24.4, 42)},
    ),
    (
        "Lookup: Gate 21 при lon=11.5° (контрольная точка эталона)",
        None, None, None, None, None, None,
        [], [],
        {"lon_check": (11.5, 21)},
    ),
    (
        "Lookup: Gate 45 при lon=79.5° (диапазон S.Node кейса)",
        None, None, None, None, None, None,
        [], [],
        {"lon_check": (79.5, 45)},
    ),
    (
        "Lookup: Gate 3 при lon=30.0°",
        None, None, None, None, None, None,
        [], [],
        {"lon_check": (30.0, 3)},
    ),
    (
        "Lookup: Gate 8 при lon=60.0°",
        None, None, None, None, None, None,
        [], [],
        {"lon_check": (60.0, 8)},
    ),
    (
        "Lookup: Gate 15 при lon=90.0°",
        None, None, None, None, None, None,
        [], [],
        {"lon_check": (90.0, 15)},
    ),
    (
        "Lookup: Gate 46 при lon=180.0°",
        None, None, None, None, None, None,
        [], [],
        {"lon_check": (180.0, 46)},
    ),
    (
        "Структура: все 64 ворота присутствуют в таблице",
        None, None, None, None, None, None,
        [], [],
        {"structure_check": True},
    ),
]


def run_tests():
    passed = 0
    failed = 0

    print("=" * 70)
    print("  REGRESSION TESTS — Human Design Gate Lookup")
    print("=" * 70)

    for i, test in enumerate(TESTS):
        desc = test[0]
        year, month, day, hour, minute, tz = test[1:7]
        must_have = test[7]
        must_not  = test[8]
        extra     = test[9] if len(test) > 9 else {}

        # Lookup-only test
        if "lon_check" in extra:
            lon, expected = extra["lon_check"]
            got, line, _, _ = lookup(lon)
            ok = got == expected
            status = "PASS" if ok else "FAIL"
            print(f"  [{status}] {desc}")
            if not ok:
                print(f"         lon={lon}° → got Gate {got}, expected Gate {expected}")
                failed += 1
            else:
                passed += 1
            continue

        # Structure test
        if "structure_check" in extra:
            present = set(e[1] for e in GL)
            missing = set(range(1, 65)) - present
            ok = len(missing) == 0
            status = "PASS" if ok else "FAIL"
            print(f"  [{status}] {desc}")
            if not ok:
                print(f"         Missing gates: {sorted(missing)}")
                failed += 1
            else:
                passed += 1
            continue

        # Full calculation test
        try:
            p_gates, d_gates, all_gates, table = calc_gates(
                year, month, day, hour, minute, tz
            )
            ok = True
            errors = []

            for g in must_have:
                if g not in all_gates:
                    ok = False
                    # Find which planet provides this gate
                    source = next(
                        (f"P:{r[0]}({r[2]})" for r in table if r[2] == g), None
                    ) or next(
                        (f"D:{r[0]}({r[5]})" for r in table if r[5] == g), None
                    ) or "NOT FOUND"
                    errors.append(f"Gate {g} ОТСУТСТВУЕТ (source={source})")

            for g in must_not:
                if g in all_gates:
                    ok = False
                    errors.append(f"Gate {g} ПРИСУТСТВУЕТ (не должен)")

            status = "PASS" if ok else "FAIL"
            print(f"  [{status}] {desc}")

            if ok and must_have:
                # Show which planet/source gave each required gate
                for g in must_have:
                    src = next((f"{r[0]} P(lon={r[1]}°)" for r in table if r[2] == g), None) \
                       or next((f"{r[0]} D(lon={r[4]}°)" for r in table if r[5] == g), None)
                    print(f"         Gate {g} ← {src}")

            for err in errors:
                print(f"         ERROR: {err}")

            if ok:
                passed += 1
            else:
                failed += 1

        except Exception as e:
            print(f"  [FAIL] {desc}")
            print(f"         EXCEPTION: {e}")
            failed += 1

    print()
    print("=" * 70)
    print(f"  ИТОГО: {passed} PASS, {failed} FAIL из {passed+failed} тестов")
    print("=" * 70)
    return failed


if __name__ == "__main__":
    fail_count = run_tests()
    sys.exit(1 if fail_count else 0)
