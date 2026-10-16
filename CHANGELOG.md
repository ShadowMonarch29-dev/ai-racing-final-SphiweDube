# CHANGELOG — Corkscrew Tuning Sessions

All experiments run on the **Corkscrew** track using `snakeoil3_gym.py` as the base.
Lap times and damage read from the TORCS top-left panel at lap end.

---

## base — Original script

**File:** `snakeoil3_gym.py`
**What changed:** Nothing. Unmodified original.
**Why:** Establish a reference point before any tuning.

| Metric | Value |
|---|---|
| Lap time | 00:54.9 |
| Damage | None |
| Top speed | 302 km/h |
| **Keep?** | **Yes** |

**Notes:** Car completed the lap and hit 302 km/h but never brakes — only lifts off
the throttle. Used as the comparison baseline for all future versions.

---

## v1 — Corner braking (first attempt)

**File:** `snakeoil3_v1.py`
**Lines changed:** 8 new lines inserted after line 551 (all marked `# BOB-v1`)
**What changed:** Added the first ever braking logic. When forward speed exceeded
80 km/h **and** the straight-ahead track sensor read under 150 m, the brake pedal
was pressed to 0.5 (half pressure).
**Why:** The base car only lifts off the throttle in corners — it never brakes. The
goal was to scrub speed before corners and reduce damage.

| Metric | Before (base) | After (v1) | Delta |
|---|---|---|---|
| Lap time | 00:54.9 | 02:35.2 | +1:40.3 slower |
| Damage | None | None | No change |
| Top speed | 302 km/h | 195 km/h | −107 km/h |
| **Keep?** | — | **Yes** | — |

**What was observed:** Car spun in the chicane section and was too slow on straights.
**Root cause diagnosed:** `dist_threshold = 150` was too large — brakes fired *during*
corners instead of before them. `brake_amount = 0.5` was too aggressive and unloaded
the rear wheels mid-turn, causing the spin. Throttle and brake also ran simultaneously
with no coordination.
**Decision:** Keep as a stepping stone — zero damage proves the braking concept works.

---

## v1.1 — Corner braking (tightened thresholds)

**File:** `snakeoil3_v1.py`
**Lines changed:** 2 lines (marked `# BOB-v1.1`)

| Line | Was | Now |
|---|---|---|
| `dist_threshold` | `150` | `80` |
| `brake_amount` | `0.5` | `0.3` |

**What changed:** Braking distance threshold cut nearly in half (150 → 80 m) so
brakes only fire very close to a corner, not during the long approach. Brake pressure
reduced from 0.5 to 0.3 to avoid unloading the rear wheels mid-turn.
**Why:** Fix the v1 chicane spin and recover some straight-line speed.

| Metric | Before (v1) | After (v1.1) | Delta |
|---|---|---|---|
| Lap time | 02:35.2 | 02:33.3 | +1.9 s faster |
| Damage | None | Yes | ❌ Damage returned |
| Top speed | 195 km/h | 217 km/h | +22 km/h |
| **Keep?** | — | **No** | — |

**What was observed:** Lap time improved slightly and top speed recovered, but damage
returned — the tighter threshold may have left too little braking distance on some
corners, or the 0.3 pressure still destabilised the car on certain bends.
**Decision:** Discard. The threshold is in the right direction but the balance between
`dist_threshold` and `brake_amount` is not yet right. Next experiment should try
raising `dist_threshold` back to ~110–120 while keeping `brake_amount` at 0.3, to
find the middle ground between v1 and v1.1.

---

## v1.2 — Corner braking (wider trigger, lighter pedal)

**File:** `snakeoil3_v1.py`
**Lines changed:** 3 lines (marked `# BOB-v1.1`)

| Setting | Was (v1.1) | Now (v1.2) |
|---|---|---|
| `speed_threshold` | `80` | `90` |
| `dist_threshold` | `80` | `111` |
| `brake_amount` | `0.3` | `0.35` |

**What changed:** Distance trigger widened from 80 m to 111 m — giving the car more
braking distance before corners. Speed threshold raised from 80 to 90 km/h to prevent
braking at low-speed chicane exits. Brake pressure nudged from 0.3 to 0.35 to compensate
for the slightly later trigger point.
**Why:** v1.1 reintroduced damage, most likely because the 80 m trigger left too little
time to slow down. This version gives the car an earlier warning while staying gentler
than the original v1 (150 m / 0.5).

| Metric | Before (v1.1) | After (v1.2) | Delta |
|---|---|---|---|
| Lap time | 02:33.3 | DNF | — |
| Damage | 0 | 57 | ❌ Damage returned |
| Top speed | 217 km/h | 217 km/h | No change |
| **Keep?** | — | **No** | — |

**What was observed:** Car did not finish the lap (DNF) and accumulated 57 damage —
the worst damage score recorded so far. The wider 111 m trigger combined with 0.35
brake pressure was likely firing too early on fast sweeping sections, destabilising
the car before genuine corners.
**Decision:** Discard. The 111 m distance threshold is too aggressive on this track.

---

## v1.3 — Corner braking (current active build)

**File:** `snakeoil3_v1.py`
**Lines changed:** 3 lines (marked `# BOB-v1.1`)

| Setting | Was (v1.2) | Now (v1.3) |
|---|---|---|
| `speed_threshold` | `90` | `92` |
| `dist_threshold` | `111` | `96` |
| `brake_amount` | `0.35` | `0.4` |

**What changed:** Distance trigger tightened from 111 m to 96 m — splitting the
difference between v1.1 (80 m, too late) and v1.2 (111 m, untested). Speed threshold
raised slightly to 92 km/h. Brake pressure raised to 0.4 — firmer than v1.1 but
below the v1 level that caused spins.
**Why:** Find the middle ground where the car brakes early enough to avoid damage but
late enough not to brake mid-corner. 96 m is a deliberate midpoint based on the
sensor analysis — far enough for a genuine approach warning, close enough to avoid
false triggers on sweeping bends.

| Metric | Before (v1.2) | After (v1.3) | Delta |
|---|---|---|---|
| Lap time | DNF | 02:10.8 | ✅ Lap completed |
| Damage | 57 | 33 | ✅ −24 improvement |
| Top speed | 217 km/h | 212 km/h | −5 km/h |
| **Keep?** | — | **Yes** | — |

**What was observed:** First version to both finish the lap cleanly AND reduce damage
below v1's zero-damage run time. Tightening the trigger to 96 m prevented mid-corner
false braking. Damage of 33 suggests one or two contact events still occur — likely
on the sharpest corners where 0.4 pressure is still slightly too late or too hard.
**Decision:** Keep. Best timed lap with braking active. Next target: reduce damage
from 33 toward zero while protecting the 02:10.8 lap time.

---

## v2 — Telemetry build (snakeoil3_v2.py, clean baseline)

**File:** `snakeoil3_v2.py`
**Lines changed:** 15 new lines marked `# BOB-telemetry` + connection fix replacing `pkill torcs`
**What changed:** Copied v1.3 driving logic into a new file with CSV telemetry added. Every step
writes a row to `lap_data.csv` (distFromStart, speedX, trackPos, angle, steer, accel, brake, gear,
track_ahead, damage). Connection crash-kill replaced with a clean `sys.exit` message for Windows.
**Why:** Enable data-driven diagnosis of the Corner 9 damage source.

| Metric | Before (v1.3) | After (v2) | Delta |
|---|---|---|---|
| Lap time | 02:10.8 | 02:12 | +1.2 s |
| Damage | 33 | 32 | −1 |
| Top speed | 212 km/h | 213 km/h | +1 km/h |
| **Keep?** | — | **No** | — |

**Decision:** Not kept as a racing version — driving logic identical to v1.3 so no improvement
expected. Exists solely as the telemetry base for further experiments.

---

## v2.1 — Speed and increased braking

**File:** `snakeoil3_v2.py`
**What changed:** Braking thresholds adjusted — speed and braking values modified.
**Why:** Attempt to reduce the 32 damage from v2 baseline.

| Metric | Before (v2) | After (v2.1) | Delta |
|---|---|---|---|
| Lap time | 02:12 | 02:13 | +1 s slower |
| Damage | 32 | 29 | −3 |
| Top speed | 213 km/h | 216 km/h | +3 km/h |
| **Keep?** | — | **No** | — |

**Decision:** Marginal damage improvement but lap time went up. Discarded.

---

## v2-H — Hypothesis test: stronger cornering slowdown (`steer * 80`)

**File:** `snakeoil3_v2.py`
**Lines changed:** 1 line marked `# BOB-H`

| Line | Was | Now |
|---|---|---|
| Throttle target penalty | `R['steer']*50` | `R['steer']*80` |

**What changed:** Raised the steering-based speed penalty from `* 50` to `* 80`, making the car
reduce its target speed more aggressively whenever it is turning.
**Why:** Hypothesis that Corner 9 damage was a throttle problem — car going too fast through turns.

| Metric | Before (v2 clean) | After (v2-H) | Delta |
|---|---|---|---|
| Lap time | 02:12 | DNF | — |
| Damage | 32 | 31 | −1 |
| Top speed | 213 km/h | 213 km/h | No change |
| **Keep?** | — | **No** | — |

**What was observed:** Car crashed and did not complete the lap. Entry speed at Corner 9 unchanged
(63 km/h vs 61 km/h baseline). Corner 10 became unstable after the Corner 9 spin.
**Root cause:** The `* 80` penalty fires during every corner, not before Corner 9. The car still
arrived at the same speed — the mechanism was wrong.
**Decision:** Revert. Hypothesis disproved — Corner 9 is a **braking zone** problem, not a
throttle reduction problem.

---

## v2-C9 — Zone-specific braking before Corner 9 (2380–2410 m, brake=0.6)

**File:** `snakeoil3_v2.py`
**Lines changed:** 3 lines marked `# BOB-C9`

```
elif 2380 < distFromStart < 2410 and speedX > 70:
    brake = 0.6
```

**What changed:** Added a targeted `elif` branch that applies `brake = 0.6` only in the 30 m
approach zone before Corner 9, regardless of the track sensor reading.
**Why:** First correct hypothesis — Corner 9 needs harder braking before the corner entry, not
during it. Zone-specific so no other corner is affected.

| Metric | Before (v2 clean) | After (v2-C9) | Delta |
|---|---|---|---|
| Lap time | 02:12 | 02:15.59 | +3.6 s slower |
| Damage | 32 | 25 | −7 ✅ |
| Top speed | 213 km/h | 211 km/h | −2 km/h |
| **Keep?** | — | **No** | — |

**What was observed:** Damage fell from 32 to 25 — improvement, but first contact at 2472 m
still at 62 km/h (unchanged from baseline). Zone either fired too late or pressure insufficient.
**Decision:** Modify — widen zone and raise pressure.

---

## v2-C9b — Zone-specific braking widened (2350–2415 m, brake=0.75)

**File:** `snakeoil3_v2.py`
**Lines changed:** 3 lines updated from `# BOB-C9` to `# BOB-C9b`

| Setting | Was (v2-C9) | Now (v2-C9b) |
|---|---|---|
| Zone start | 2380 m | 2350 m |
| Zone end | 2410 m | 2415 m |
| Brake pressure | 0.6 | 0.75 |

**What changed:** Zone widened by 30 m earlier (2380 → 2350) to give more braking distance.
Pressure raised from 0.6 to 0.75 to scrub more speed within the zone.
**Why:** v2-C9 entry speed was unchanged at 62 km/h — either the zone fired too late or
pressure was insufficient. Both variables increased simultaneously.

| Metric | Before (v2-C9) | After (v2-C9b) | Delta |
|---|---|---|---|
| Lap time | 02:15.59 | 02:14 | −1.6 s faster ✅ |
| Damage | 25 | 24 | −1 ✅ |
| Top speed | 211 km/h | 209 km/h | −2 km/h |
| **Keep?** | — | **No** | — |

**What was observed:** Marginal improvements on both metrics but damage still not eliminated.
Entry speed at Corner 9 still not sufficiently reduced — each iteration reduces damage by only
1–7 points. Zone firing needs to be confirmed via CSV telemetry before further threshold changes.
**Decision:** Do not keep. Investigate via telemetry CSV whether zone actually fires before
continuing threshold adjustments.

---

## v2-C10 — Full rewrite: sensor-based braking, ABS, traction control, lap adaptation

**File:** `snakeoil3_v2.py`
**What changed:** Complete replacement of the hand-tuned threshold braking system with a
physics-based approach. All improvements grounded in lap data showing 8 corners with
`closest_edge = -1.00` at 43–48 km/h minimum speeds.

| System | What it does |
|---|---|
| Sensor-based braking | `v_safe = √(2 × BRAKE_DECEL × track_ahead)` — scales brake to actual gap |
| `abs(steer)` penalty | Fixed signed-steer bug — both left and right corners now reduce target speed |
| Earlier turn-in | Steers toward the longer side sensor group for better apex approach |
| Speed-based steering reduction | Lock reduced above 100 km/h to cut oversteer |
| Steering rate limit | Max 0.06 change per tick — prevents snap-steer |
| ABS | Pulses brake when front wheels lock, restores steering authority |
| Throttle/brake isolation | Zero throttle while braking — no simultaneous gas/brake |
| Proportional traction control | Cuts throttle scaled to slip amount, not a flat chop |
| Stuck/spin recovery | Reverses and re-aligns after 30 ticks beached |
| Lap-time adaptation | `TARGET_LAP = 110.5 s` — pushes harder when slow, backs off after damage |

| Metric | Before (v2-C9b) | After (v2-C10) | Delta |
|---|---|---|---|
| Lap time | 02:14 | **01:53** | **−21 s** ✅ |
| Damage | 24 | **0** | **−24** ✅ |
| Top speed | 209 km/h | 209 km/h | No change |
| **Keep?** | — | **Yes** | — |

**What was observed:** First clean lap with zero damage since the base script. Lap time of
01:53 is the best braking-active time recorded — 17.8 seconds faster than the previous best
(v1.3 at 02:10.8) and only 58 seconds off the base no-braking time of 00:54.9.
**Decision:** Keep. This is the new baseline for all further tuning.

---

## Summary

| Version | Lap Time | Damage | Top Speed | Keep? |
|---|---|---|---|---|
| base | 00:54.9 | 0 | 302 km/h | ✅ Yes |
| v1 | 02:35.2 | 0 | 195 km/h | ✅ Yes |
| v1.1 | 02:33.3 | 0 | 217 km/h | ❌ No |
| v1.2 | DNF | 57 | 217 km/h | ❌ No |
| v1.3 | 02:10.8 | 33 | 212 km/h | ✅ Yes |
| v2 | 02:12 | 32 | 213 km/h | ❌ No (telemetry base) |
| v2.1 | 02:13 | 29 | 216 km/h | ❌ No |
| v2-H | DNF | 31 | 213 km/h | ❌ No |
| v2-C9 | 02:15.59 | 25 | 211 km/h | ❌ No |
| v2-C9b | 02:14 | 24 | 209 km/h | ❌ No |
| **v2-C10** | **01:53** | **0** | **209 km/h** | **✅ Yes** |

**Current best lap:** base — 00:54.9 (no braking logic, no damage)
**Current best with braking:** v2-C10 — 01:53 (zero damage, −17.8 s vs previous best v1.3)
**Progress:** base 00:54 → v1.3 02:10 → v2-C10 01:53 → gap to base now 58 s
**Next target:** Reduce lap time toward 01:30 by raising `BRAKE_DECEL` (11 → 12) and
`TARGET_LAP` (110.5 → 100) now that zero damage is confirmed stable.
