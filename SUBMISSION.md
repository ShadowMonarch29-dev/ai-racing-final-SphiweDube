# Submission — AI Racing Controller

**Track:** Corkscrew  
**Controller file:** `snakeoil3_v2.py` (version v2-C10)  
**Simulator:** TORCS with SCR server plugin  

---

## Summary

A rule-based autonomous driving controller developed through 12 iterative experiments
on the Corkscrew track. The approach evolved from a fixed-threshold braking system to
a physics-based sensor model with ABS, traction control, and lap-time adaptation.
The final version completed the Corkscrew with zero damage.

---

## Lap Results

All times and damage values read from the TORCS top-left panel at lap end.
Top speed read from the same panel. Results marked "not recorded" were not captured.

| Version | What Changed | Lap Time | Damage | Top Speed | Kept |
|---|---|---|---|---|---|
| base | Nothing — original unmodified script | 00:54.9 | 0 | 302 km/h | Yes |
| v1 | First braking logic: `track[9] < 150`, `brake=0.5` | 02:35.2 | 0 | 195 km/h | Yes |
| v1.1 | Tightened: `dist=80`, `brake=0.3` | 02:33.3 | 0 | 217 km/h | No |
| v1.2 | Widened: `speed=90`, `dist=111`, `brake=0.35` | DNF | 57 | 217 km/h | No |
| v1.3 | Balanced: `speed=92`, `dist=96`, `brake=0.4` | 02:10.8 | 33 | 212 km/h | Yes |
| v2 | Telemetry build — driving logic identical to v1.3 | 02:12 | 32 | 213 km/h | No |
| v2.1 | Threshold adjustment | 02:13 | 29 | 216 km/h | No |
| v2-H | Hypothesis test: `steer*80` corner penalty | DNF | 31 | 213 km/h | No |
| v2-C9 | Zone-specific brake: `2380–2410 m`, `brake=0.6` | 02:15.59 | 25 | 211 km/h | No |
| v2-C9b | Widened zone: `2350–2415 m`, `brake=0.75` | 02:14 | 24 | 209 km/h | No |
| **v2-C10** | **Physics-based braking, ABS, lap adaptation** | **01:53** | **0** | **209 km/h** | **Yes** |

---

## Controller Design (v2-C10)

### Approach
Rule-based with physics-derived braking. No machine learning. No training data.
All decisions made in real time from the 19 track-edge sensors, speed, angle,
track position, and wheel spin velocity.

### Architecture

**Braking**  
Safe speed computed from the straight-ahead sensor distance:
```
v_safe = √(2 × BRAKE_DECEL × track_ahead)    [BRAKE_DECEL = 11.0 m/s²]
```
Brake pressure scaled proportionally to excess speed over `v_safe`.
A lateral penalty (`abs(steer) × 60`) reduces the target in corners equally for
left and right turns — fixing a signed-steer bug in the original base script.

**ABS**  
When front wheels approach lock-up (near-zero spin while rears roll), brake
pressure is halved for that tick to restore steering authority.

**Steering**  
Angle correction + centre pull + turn-in aim (steers toward the longer side sensor
group) + speed-based lock reduction above 100 km/h + rate limit of 0.06 per tick.

**Throttle**  
Zero while braking. Incrementally builds/bleeds (`±0.01` per tick) relative to
the effective target speed. Emergency boost below 10 km/h to prevent stalling.

**Traction control**  
Proportional throttle cut when rear wheel spin exceeds front by more than 5 rad/s.
Cut scaled as `slip / 50`, capped at 0.05–0.3.

**Lap-time adaptation**  
Target: 110.5 s (1:50.50). After each lap the push multiplier (`LAP_PUSH`)
increases by 0.01 if slower than target, decreases by 0.02 after any damage or
off-track event, and gently eases when on target. Range: 0.85–1.10.

**Stuck / spin recovery**  
After 30 consecutive ticks at speed < 5 km/h with `|trackPos| > 0.9`, the car
engages reverse gear, counter-steers, and applies 50% throttle to escape.

**Corner 9 safety zone**  
A hardcoded zone (`distFromStart 2350–2415 m`, `brake ≥ 0.75`) was retained from
earlier experiments as insurance for the Corkscrew's blind left-hander at ~2410 m.

### Parameters

| Parameter | Value | Notes |
|---|---|---|
| `BRAKE_DECEL` | 11.0 m/s² | Primary lap time lever — raise to brake later |
| `LAT_PENALTY` | 60.0 | Corner speed reduction per steer unit |
| `V_MIN_CORNER` | 40.0 km/h | Minimum speed; never brakes below this |
| `TARGET_LAP` | 110.5 s | Adaptation lap time target |
| `AIM_GAIN` | 0.004 | Turn-in strength toward longer side sensor |
| Steering rate limit | 0.06/tick | Prevents snap-steer overshoot |

---

## Development Method

All development used a hypothesis-test-measure loop:
1. Identify a problem from `lap_data.csv` (telemetry written every tick)
2. Form a hypothesis about the cause
3. Make the smallest code change that tests it
4. Run one lap, record results in `lap_log.xlsx`
5. Keep, modify, or revert based on results

Full experiment history in `experiment-report.md`.  
Full version history in `CHANGELOG.md`.  
Parameter reference in `tuning-card.md`.

---

## What Is Not Included

The following components are required to run the controller but are not present
in this submission folder:

| Component | Where to get it | Notes |
|---|---|---|
| TORCS simulator | [http://torcs.org](http://torcs.org) | Open source; Windows build available |
| SCR server plugin | [http://scr.geccocompetitions.com/](http://scr.geccocompetitions.com/) | Required for UDP port 3001 |
| Corkscrew track | Included in standard TORCS installation | Select in TORCS GUI |
| `autostart.sh` | `gym_torcs/gym_torcs/` in original project | Linux only; not needed on Windows |

---

## Files Not Included

The following files exist in the project but are not part of this submission:

| File | Reason not included |
|---|---|
| `snakeoil3_gym.py` | Original unmodified base — not the submitted controller |
| `snakeoil3_v1.py` | Intermediate development version |
| `snakeoil3_v2_clean.py` | Rollback snapshot — internal development only |
| `v1-brake-plan.md` | Internal planning document |
| `torcs/lap_data.csv` | Telemetry from most recent run — regenerated each session |
| `Recording 2026-10-16 223105.mp4` | Screen recording — not recorded |
| `car1-ow1.rgb` | TORCS car skin file — not part of the controller |

---

## Known Issues

- Lap time on Corkscrew: 01:53 (best recorded). The base script (no braking) ran 00:54.9.
  The gap of ~58 seconds is the cost of conservative braking. `BRAKE_DECEL` was not raised
  above 11.0 during recorded experiments — see `tuning-card.md` for the next step.
- The BOB-C9c safety zone is hardcoded to Corkscrew geometry. It will fire at the wrong
  point on other tracks.
- Performance on tracks other than Corkscrew: **not recorded**.
- Multi-lap adaptation behaviour beyond lap 1: **not recorded** (all logged laps are single
  laps from a standing start).
