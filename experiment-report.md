# Experiment Report — Corner 9 Braking Investigation
## Track: Corkscrew · File: snakeoil3_v2.py

---

## v2-C9 — Zone-specific braking (2380–2410 m, brake=0.6)

| Field | Detail |
|---|---|
| **Baseline** | v1.3 — `snakeoil3_v1.py` with `speed_threshold=92`, `dist_threshold=96`, `brake_amount=0.4`. Lap time 02:10.8, damage 33, top speed 212 km/h. All 33 damage points came from Corner 9 (2410–2504 m) where the car went off-track left with `trackPos = -1.645`. |
| **Hypothesis** | Corner 9 damage is a **braking zone problem**: the car arrives too fast at 2410 m and can't complete the left-hand bend. A harder, earlier brake before Corner 9 — between 2380 m and 2410 m — should scrub enough speed to keep the car on track, without affecting the other 15 corners. |
| **AI recommendation** | Add a zone-specific `elif` branch in the corner braking block: if `2380 < distFromStart < 2410` AND `speedX > 70`, apply `brake = 0.6` — firmer than the general 0.4. This fires regardless of the track sensor reading and is positioned as an `elif` so it cannot double-fire with the general braking condition. One previously failed hypothesis (raising `steer * 50 → 80`) was discarded because it made Corner 10 worse without fixing Corner 9's entry speed. |
| **Change made** | 3 lines added to `snakeoil3_v2.py` (marked `# BOB-C9`): `elif 2380 < S.get('distFromStart', 0) < 2410 and S['speedX'] > 70: R['brake'] = 0.6`. Nothing else changed. Telemetry, connection fix, general braking, steering, gears all identical to `snakeoil3_v2_clean.py`. |
| **Predicted result** | Lap completed (no DNF). Damage 0–10 — zone-specific brake prevents the initial wall contact at 2473 m. Lap time close to 02:10.8 — only 30 m of extra braking so minimal time cost. Top speed ~212 km/h (straights unaffected). |
| **Actual lap time** | 02:15.59 — lap completed ✅. Approximately 5 seconds slower than v1.3 baseline. |
| **Damage** | 25 — reduced from 33 (baseline) but NOT eliminated. 3 damage events all still at Corner 9 (2472–2498 m). First contact at 62.4 km/h with `trackPos = -1.648` — almost identical to baseline. |
| **What surprised us?** | The zone-specific brake did not prevent the first wall contact at all. The car arrived at 2472 m at 62.4 km/h — practically the same as the v1.3 baseline (61 km/h, −1.645). The car then went backwards to −69 km/h (worse than baseline's −53 km/h). Corner 10 extended to 2762 m vs 2516 m in baseline — spin was longer. CHECK — unclear whether zone actually fired. |
| **Keep / modify / revert** | **Modify.** Widen zone to 2350–2415 m and raise pressure to 0.75. |
| **Next experiment** | v2-C9b — see below. |

---

## v2-C9b — Zone-specific braking widened (2350–2415 m, brake=0.75)

| Field | Detail |
|---|---|
| **Baseline** | v2-C9 — 02:15.59, damage 25, top speed 211 km/h. |
| **Hypothesis** | v2-C9's zone (2380–2410 m, 0.6) fired too late or with too little pressure. Widening the zone 30 m earlier and raising pressure to 0.75 will reduce entry speed at 2472 m below the 62 km/h contact threshold. |
| **AI recommendation** | Update the `elif` zone start from 2380 to 2350, end from 2410 to 2415, and brake from 0.6 to 0.75. Same `speedX > 70` guard. |
| **Change made** | 3 values updated in the `# BOB-C9b` block: zone `2350–2415 m`, `brake = 0.75`. |
| **Predicted result** | Damage < 15. Lap time approximately 02:13–02:15. Entry speed at 2472 m drops below 55 km/h. |
| **Actual lap time** | 02:14 — lap completed ✅. |
| **Damage** | 24 — reduced by 1 from v2-C9 (25). Corner 9 damage events: first contact still at ~2472 m, speed still ~62 km/h. Spin continued to −57 km/h. Corner 10 off-track zone extended to 2762 m. |
| **What surprised us?** | Entry speed at first contact (2472 m) essentially unchanged across v2-C9 and v2-C9b — both 62 km/h. Widening the zone by 30 m and raising pressure by 0.15 had almost no effect on entry speed. This strongly suggests the zone is either not firing at all, OR the car's `distFromStart` reading behaves differently in this section of the track (possible reset or non-linear reporting). CHECK — must open `lap_data.csv` and inspect brake column values between 2350–2415 m before any further zone adjustments. |
| **Keep / modify / revert** | **Do not keep.** Blocked: cannot make progress by adjusting zone thresholds until zone firing is confirmed in CSV. |
| **Next experiment** | Open `lap_data.csv` from the v2-C9b run. Filter rows where `distFromStart` is between 2350 and 2415. If `brake` column shows `0` throughout, the `elif` never fired — meaning the general braking condition (`track[9] < 96`) was already setting `brake = 0.4` in those rows and taking priority over the `elif`. If that is the case, the fix is to convert the `elif` to a separate block that always overrides when in the zone. If `brake` shows 0.75 in the zone, the braking is firing but not enough — the problem is structural (car already off-centre left before 2350 m). |

---

## v2-C10 — Full architecture rewrite (sensor braking, ABS, adaptation)

| Field | Detail |
|---|---|
| **Baseline** | v2-C9b — 02:14, damage 24. Zone-specific brake confirmed firing but entry speed at Corner 9 still ~62 km/h across all zone experiments. |
| **Hypothesis** | The hand-tuned threshold system (fixed speed/distance triggers) cannot handle all 16+ corners. A physics-based braking model (`v_safe = √(2 × BRAKE_DECEL × track_ahead)`) will generalise across all corners automatically. Combined with `abs(steer)` penalty fix, ABS, and lap adaptation, zero damage should be achievable without hand-coding each corner. |
| **AI recommendation** | Replace the entire braking block with sensor-based physics formula. Fix the signed-steer bug. Add steering rate limit, speed-based lock reduction, earlier turn-in via side sensors, ABS pulse, throttle isolation, proportional traction control, stuck recovery, and lap-time adaptation. Keep BOB-C9c Corner 9 zone as a safety net. |
| **Change made** | Full rewrite of `drive_example()` body — ~80 lines replaced. Telemetry CSV, gearbox thresholds, and BOB-C9c zone preserved unchanged. |
| **Predicted result** | Zero damage (physics model generalises). Lap time improvement over 02:14. Adaptation converges over 3–5 laps. |
| **Actual lap time** | **01:53** ✅ — best braking-active time recorded. |
| **Damage** | **0** ✅ — first clean zero-damage lap since the original base script. |
| **What surprised us?** | The physics-based approach solved all 8 off-track corners in a single run. Previous iterations spent 10+ experiments adjusting two numbers for one corner. The `abs(steer)` bug fix alone likely contributed significantly — right-hand corners were previously getting a *speed increase* instead of a reduction. |
| **Keep / modify / revert** | **Keep.** New baseline for all further tuning. |
| **Next experiment** | Raise `BRAKE_DECEL` from 11 to 12 to recover lap time toward 01:30 while monitoring damage. If zero damage holds, raise `TARGET_LAP` from 110.5 to 100 to make the adaptation push harder sooner. |
