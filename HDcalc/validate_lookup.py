#!/usr/bin/env python3
"""Quick validator for fullhd_lookup.json integrity and known control points.

Control points verified against FullHD etalon (FullHD - etalon/!Рассчеты_upd_v.5.xlsx)
on 2026-04-07. The authoritative source is the etalon Excel file.
"""

import json
import bisect
from pathlib import Path

LOOKUP_PATH = Path(__file__).with_name("fullhd_lookup.json")


def lookup_gate(table, lons, lon):
    lon = lon % 360.0
    idx = bisect.bisect_right(lons, lon) - 1
    if idx < 0:
        idx = len(table) - 1
    row = table[idx]
    return row[1], row[2], row[3], row[4]


def main():
    if not LOOKUP_PATH.exists():
        print(f"ERROR: missing {LOOKUP_PATH.name}")
        raise SystemExit(1)

    data = json.loads(LOOKUP_PATH.read_text(encoding="utf-8"))
    lons = [row[0] for row in data]

    print(f"rows={len(data)} first={lons[0]} last={lons[-1]}")

    # Control points validated against etalon (FullHD - etalon/!Рассчеты_upd_v.5.xlsx)
    # CORRECTED 2026-04-07: old values (24.4->44, 11.5->45) were wrong
    checks = [
        ("control-24.4", 24.4, 42),   # was 44 (wrong), etalon confirms 42
        ("control-11.5", 11.5, 21),   # was 45 (wrong), etalon confirms 21
        ("control-30.0", 30.0,  3),   # Gate 3 at start of Taurus
        ("control-60.0", 60.0,  8),   # Gate 8
        ("control-79.5", 79.5, 45),   # Gate 45 (used in 20.05.1974 test case)
        ("control-90.0", 90.0, 15),   # Gate 15
    ]

    failed = False
    for name, lon, expected_gate in checks:
        gate, line, color, tone = lookup_gate(data, lons, lon)
        ok = gate == expected_gate
        status = "PASS" if ok else "FAIL"
        print(f"{status}: {name}: lon={lon} -> gate={gate}.{line} c/t={color}/{tone}, expected_gate={expected_gate}")
        failed = failed or (not ok)

    # Structural check: all 64 gates present
    present_gates = set(row[1] for row in data)
    missing = set(range(1, 65)) - present_gates
    if missing:
        print(f"FAIL: missing gates: {sorted(missing)}")
        failed = True
    else:
        print(f"PASS: all 64 gates present, {len(data)} rows total")

    if failed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
