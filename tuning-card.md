# Tuning Card — `drive_example()` in `snakeoil3_v2.py` (v2-C10)

> **Active file:** `snakeoil3_v2.py` — the architecture changed completely in v2-C10.
> The old fixed-threshold braking is gone. All knobs below are in `drive_example()`.
> Change one value at a time and log each run in `lap_log.xlsx` before changing another.
> **Current best:** 01:53, zero damage.

---

## Primary Knobs (highest impact)

| Setting | Location in code | Current Value | What It Controls | Raise it → | Lower it → | Crash Risk |
|---|---|---|---|---|---|---|
| `TARGET_LAP` | `target_speed` block | `110.5` s | Lap time target for adaptation. Car pushes harder each lap it finishes slower than this. | Car pushes harder sooner — more speed but higher damage risk. | Car backs off earlier — safer but slower. | **Medium** — controls aggression multiplier over many laps. |
| `BRAKE_DECEL` | braking block | `11.0` m/s² | How hard the physics model assumes the car can brake. Higher = car trusts it can stop sooner = brakes later = faster. | Brakes later, higher corner entry speed, faster laps — first thing to raise when chasing time. | Brakes earlier, more cautious — useful if corners are still catching the car. | **High** — most direct lever for lap time vs damage trade-off. |
| `V_MIN_CORNER` | braking block | `40.0` km/h | Floor speed — car never brakes below this. Prevents the car from braking to a crawl on hairpins. | Car doesn't slow as much for tight corners — can overshoot hairpins. | Car slows too much for every corner — sluggish through chicanes. | **Low** — only affects the tightest corners. |
| `LAT_PENALTY` | braking block | `60.0` | How much the target speed drops per unit of steering lock. `abs(steer)` is used so left and right corners are treated equally. | More speed reduction in all corners — safer, slower. | Less speed reduction — faster but corner exits get loose. | **Medium** — raise first if off-track in corners, lower if car feels too slow through bends. |

---

## Steering Knobs

| Setting | Location in code | Current Value | What It Controls | Raise it → | Lower it → | Crash Risk |
|---|---|---|---|---|---|---|
| Angle correction `* 15` | steering block | `15` | How hard the car corrects its nose angle vs the road. | Faster snap-back — can overshoot and wobble. | Slower correction — car points wrong way in corners. | **Medium** |
| Centre pull `* 0.10` | steering block | `0.10` | How hard the car pulls back to the track centre. | More forceful — can fight with angle correction. | Car drifts to edges. | **Low** |
| `AIM_GAIN` | steering block | `0.004` | How much the car steers toward the longer side sensor group — gives earlier turn-in. | Earlier turn-in, tighter apex — can clip the inside kerb. | Later turn-in, wider line — more conservative. | **Low** — gentle effect. |
| Speed steering reduction `0.003` | steering block | `0.003` | How much steering lock is reduced per km/h above 100 km/h. | Less lock at speed — more stable, less responsive. | More lock at speed — responsive but oversteer risk. | **Medium** — reduces high-speed crashes. |
| Steering rate limit `0.06` | steering block | `0.06` | Max steering change allowed per tick (~50/sec). Prevents snap-steer. | Faster steering response — more agile, more oversteer. | Very slow steering — misses tight corners. | **Medium** |

---

## Recovery & Safety Knobs

| Setting | Location in code | Current Value | What It Controls | Raise it → | Lower it → | Crash Risk |
|---|---|---|---|---|---|---|
| Stuck threshold `> 30` ticks | stuck recovery block | `30` | How long the car must be stopped/beached before reversing to escape. | Waits longer before reversing — better if car is just slow. | Triggers reverse too quickly — may engage mid-corner. | **Low** |
| ABS pulse `* 0.5` | ABS block | `0.5` | How much brake pressure is cut when front wheels lock. 0.5 = halved. | Gentler ABS intervention. | More aggressive pulse — may feel jerky. | **Low** |
| Traction cut divisor `/ 50` | traction control | `50` | Denominator controlling how aggressively throttle is cut per unit of wheel slip. | Less aggressive cut — more wheelspin allowed. | More aggressive cut — smoother exits. | **Medium** |

---

## Lap Adaptation Knobs

| Setting | Location in code | Current Value | What It Controls | Raise it → | Lower it → |
|---|---|---|---|---|---|
| `LAP_PUSH` ceiling `1.10` | adaptation block | `1.10` | Maximum speed multiplier the adaptation can reach. | Car can push harder over many laps. | Limits maximum aggression. |
| `LAP_PUSH` floor `0.85` | adaptation block | `0.85` | Minimum speed multiplier after damage/off-track. | Car doesn't back off as much after incidents. | Car backs off more conservatively after any incident. |
| Push increment `0.01` | adaptation block | `0.01` | How much push increases each slow lap. | Adapts faster — can overshoot into damage. | Adapts slowly — more conservative. |
| Back-off step `0.02` | adaptation block | `0.02` | How much push decreases after an off-track or damage event. | Backs off harder after incidents. | Barely backs off — stays aggressive after incidents. |

---

## Corner 9 Safety Zone (BOB-C9c)

| Setting | Location | Current Value | What It Controls |
|---|---|---|---|
| Zone start | BOB-C9c block | `2350` m | Where the Corner 9 override braking begins. Move earlier if car still arrives too fast. |
| Zone end | BOB-C9c block | `2415` m | Where it ends. Should match Corner 9 entry in your lap data (~2410 m). |
| Zone pressure | BOB-C9c block | `0.75` | Minimum brake pressure in this zone. Uses `max(general, 0.75)` so general braking can exceed it. |

---

## Quick Reference — What to Change First

| Goal | Setting | Direction |
|---|---|---|
| **Faster laps, same damage** | `BRAKE_DECEL` | Raise: 11 → 12 |
| **Eliminate remaining corner exits** | `LAT_PENALTY` | Raise: 60 → 70 |
| **Adapt to target lap faster** | `TARGET_LAP` | Lower: 110.5 → 100 |
| **Stop wobbling on straights** | Steering rate limit | Lower: 0.06 → 0.04 |
| **Earlier turn-in on long corners** | `AIM_GAIN` | Raise: 0.004 → 0.006 |
| **Car too slow through chicanes** | `V_MIN_CORNER` | Raise: 40 → 50 |
| **Damage returns after push** | `LAP_PUSH` ceiling | Lower: 1.10 → 1.05 |
