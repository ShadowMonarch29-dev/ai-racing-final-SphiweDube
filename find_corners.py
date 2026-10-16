"""
find_corners.py
Reads lap_data.csv produced by snakeoil3_v2.py and prints:
  1. Corner zones  – stretches where track_ahead < 40 m
  2. Straight zones – stretches where track_ahead > 150 m
  3. Damage events – every row where damage increased vs the previous row
Rows before the standing-start reset (distFromStart first drops near zero
after an initial non-zero stretch) are discarded automatically.
Uses only Python built-in libraries.
"""

import csv
import sys
import os

# ── Config ────────────────────────────────────────────────────────────────────
CSV_FILE        = 'lap_data.csv'
CORNER_THRESH   = 40.0    # track_ahead < this  → inside a corner zone
STRAIGHT_THRESH = 150.0   # track_ahead > this  → inside a straight zone
LAP_START_DIST  = 5.0     # distFromStart below this value counts as "near zero"
# ──────────────────────────────────────────────────────────────────────────────


def load_rows(path):
    """Read CSV and return list of dicts with float values where possible."""
    if not os.path.exists(path):
        print(f"ERROR: '{path}' not found.")
        print("Run snakeoil3_v2.py first to generate the file.")
        sys.exit(1)

    rows = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = {}
            for k, v in raw.items():
                try:
                    row[k] = float(v)
                except (ValueError, TypeError):
                    row[k] = v
            rows.append(row)
    return rows


def find_lap_start(rows):
    """
    Skip rows before the standing-start reset.
    Strategy: find the first row where distFromStart is near zero AFTER
    at least one row where distFromStart was clearly non-zero (> LAP_START_DIST).
    Everything from that near-zero row onward is the real lap.
    """
    seen_nonzero = False
    for i, row in enumerate(rows):
        d = row.get('distFromStart', 0)
        if not isinstance(d, float):
            continue
        if d > LAP_START_DIST:
            seen_nonzero = True
        if seen_nonzero and d <= LAP_START_DIST:
            return i  # first reset point found
    # No reset detected — assume all rows are valid lap data
    return 0


def find_zones(rows, key, below=None, above=None):
    """
    Return a list of zones: stretches where rows[key] is consistently
    below `below` or above `above` (only one should be set).
    Each zone is a dict with: start_dist, end_dist, and a list of rows.
    """
    zones = []
    current = None

    for row in rows:
        val = row.get(key)
        if not isinstance(val, float):
            if current:
                zones.append(current)
                current = None
            continue

        in_zone = (below is not None and val < below) or \
                  (above is not None and val > above)

        if in_zone:
            if current is None:
                current = {
                    'start_dist': row.get('distFromStart', '?'),
                    'end_dist':   row.get('distFromStart', '?'),
                    'rows': [row],
                }
            else:
                current['end_dist'] = row.get('distFromStart', '?')
                current['rows'].append(row)
        else:
            if current is not None:
                zones.append(current)
                current = None

    if current is not None:
        zones.append(current)

    return zones


def find_damage_events(rows):
    """Return rows where damage value increased compared to the previous row."""
    events = []
    prev_damage = None
    for row in rows:
        dmg = row.get('damage')
        if not isinstance(dmg, float):
            continue
        if prev_damage is not None and dmg > prev_damage:
            events.append({
                'distFromStart': row.get('distFromStart', '?'),
                'speedX':        row.get('speedX', '?'),
                'trackPos':      row.get('trackPos', '?'),
                'damage_before': prev_damage,
                'damage_after':  dmg,
                'damage_delta':  dmg - prev_damage,
            })
        prev_damage = dmg
    return events


def fmt(v, decimals=1):
    """Format a float or return the raw value if not a float."""
    return f'{v:.{decimals}f}' if isinstance(v, float) else str(v)


def print_corner_zones(zones):
    print('=' * 65)
    print(f'CORNER ZONES  (track_ahead < {CORNER_THRESH} m)')
    print('=' * 65)
    if not zones:
        print('  None found.')
        return
    for i, z in enumerate(zones, 1):
        rows      = z['rows']
        speeds    = [r['speedX']      for r in rows if isinstance(r.get('speedX'), float)]
        edges     = [r['track_ahead'] for r in rows if isinstance(r.get('track_ahead'), float)]
        min_speed = min(speeds) if speeds else '?'
        min_edge  = min(edges)  if edges  else '?'
        print(
            f"  Corner {i:>3}:  "
            f"{fmt(z['start_dist'])} m → {fmt(z['end_dist'])} m  |  "
            f"min speed {fmt(min_speed)} km/h  |  "
            f"closest edge {fmt(min_edge, 2)} m"
        )
    print()


def print_straight_zones(zones):
    print('=' * 65)
    print(f'STRAIGHT ZONES  (track_ahead > {STRAIGHT_THRESH} m)')
    print('=' * 65)
    if not zones:
        print('  None found.')
        return
    for i, z in enumerate(zones, 1):
        rows      = z['rows']
        speeds    = [r['speedX'] for r in rows if isinstance(r.get('speedX'), float)]
        max_speed = max(speeds) if speeds else '?'
        print(
            f"  Straight {i:>3}:  "
            f"{fmt(z['start_dist'])} m → {fmt(z['end_dist'])} m  |  "
            f"max speed {fmt(max_speed)} km/h"
        )
    print()


def print_damage_events(events):
    print('=' * 65)
    print('DAMAGE EVENTS  (damage increased)')
    print('=' * 65)
    if not events:
        print('  No damage recorded.')
        return
    for e in events:
        print(
            f"  dist {fmt(e['distFromStart'])} m  |  "
            f"speed {fmt(e['speedX'])} km/h  |  "
            f"trackPos {fmt(e['trackPos'], 3)}  |  "
            f"damage +{fmt(e['damage_delta'], 0)}  "
            f"({fmt(e['damage_before'], 0)} → {fmt(e['damage_after'], 0)})"
        )
    print()


def main():
    print(f"\nReading {CSV_FILE} …")
    rows = load_rows(CSV_FILE)
    print(f"  {len(rows)} rows loaded.")

    lap_start = find_lap_start(rows)
    if lap_start > 0:
        print(f"  Discarding {lap_start} pre-start rows (standing start detected at row {lap_start}).")
    rows = rows[lap_start:]
    print(f"  {len(rows)} rows used for analysis.\n")

    corner_zones   = find_zones(rows, 'track_ahead', below=CORNER_THRESH)
    straight_zones = find_zones(rows, 'track_ahead', above=STRAIGHT_THRESH)
    damage_events  = find_damage_events(rows)

    print_corner_zones(corner_zones)
    print_straight_zones(straight_zones)
    print_damage_events(damage_events)

    print('─' * 65)
    print(f"Summary: {len(corner_zones)} corner zone(s), "
          f"{len(straight_zones)} straight zone(s), "
          f"{len(damage_events)} damage event(s).")
    print()


if __name__ == '__main__':
    main()
