# AI Racing Controller — TORCS Corkscrew
## `snakeoil3_v2.py` · version v2-C10

A rule-based autonomous driving controller for TORCS, developed and tuned through
iterative data-driven experimentation on the **Corkscrew** track.

---

## Repository Contents

| File | Purpose |
|---|---|
| `snakeoil3_v2.py` | **The controller.** Contains all driving logic plus CSV telemetry. |
| `find_corners.py` | Post-run analysis tool. Reads `lap_data.csv` and prints corner zones, straight zones, and damage events. |
| `CHANGELOG.md` | Full record of every experiment run, what changed, and why. |
| `tuning-card.md` | Reference card for all tunable parameters with plain-English descriptions. |
| `experiment-report.md` | Hypothesis-driven experiment log for the Corner 9 investigation. |
| `lap_log.xlsx` | Raw lap results spreadsheet (version, time, damage, top speed, keep decision). |

---

## Requirements

### Python
- **Python 3** (tested on Python 3.x — no version constraint beyond Python 3)
- **Standard library only** — no pip installs required.

The imports in `snakeoil3_v2.py` are:
```python
import socket    # built-in
import sys       # built-in
import getopt    # built-in
import os        # built-in
import time      # built-in
import csv       # built-in
```

There are **no third-party dependencies**. No numpy, no TensorFlow, no gym.

### TORCS Simulator
- **TORCS** with the **SCR (Simulated Car Racing) server plugin** installed.
- The SCR plugin is *not* included in the standard TORCS installer — it must be applied
  as a separate patch. See [http://scr.geccocompetitions.com/](http://scr.geccocompetitions.com/)
  for the original SCR competition materials.
- **Windows:** A Windows build of TORCS with SCR support is available. See
  `torcs/TORCS_Python_Windows_Troubleshooting_Guide.docx` in the original project for
  Windows-specific setup instructions.
- The controller communicates with TORCS over **UDP on port 3001**. No other network
  configuration is required.

### SCR Plugin Setup (TORCS GUI)
Before running the controller, TORCS must be configured with the SCR server driver:

1. Open TORCS
2. **Race → Quick Race → Configure Race → Drivers**
3. Move **`scr_server 1`** from "Not Selected" to "Selected"
4. Click **Accept**, then start the race
5. The car will sit on the grid waiting for a client — run the script at this point

---

## How to Run

### Mandatory startup order
**Start TORCS first, get to the race grid, then run the script.**
If the script is run before TORCS is ready, it will print a countdown and exit cleanly
without disturbing the simulator.

### Launch command
```powershell
cd path\to\submission\folder
python snakeoil3_v2.py
```

### Optional command-line arguments
The controller inherits the full snakeoil argument parser:

```
--host, -H <host>    TORCS server host  [localhost]
--port, -p <port>    TORCS port         [3001]
--id,   -i <id>      Client ID          [SCR]
--steps,-m <#>       Max steps          [100000]  (~50 steps/sec)
--track,-t <track>   Track name         [unknown]
--stage,-s <#>       0=warmup 1=qual 2=race 3=unknown  [3]
--debug,-d           Print full telemetry to stderr
--help, -h           Show help
```

Example with explicit port:
```powershell
python snakeoil3_v2.py --port 3001
```

### Telemetry output
Every step writes one row to **`lap_data.csv`** in the same directory as the script.
The file is created fresh each run. Columns:

```
distFromStart, speedX, trackPos, angle, steer, accel, brake, gear, track_ahead, damage
```

The file is flushed after every row — safe to open in Excel while the race is running,
and data is preserved if the script is stopped mid-lap with Ctrl+C.

### Lap time output
Each completed lap prints to the terminal:
```
Lap time: 113.20 s  (push=1.010)
```

### Analysis after a run
```powershell
python find_corners.py
```
Reads `lap_data.csv` from the current directory. Prints corner zones (track_ahead < 40 m),
straight zones (track_ahead > 150 m), and every tick where damage increased.

---

## Sensor Configuration

The controller uses 19 track-edge distance sensors, configured at these angles (degrees):
```
-45 -19 -12 -7 -4 -2.5 -1.7 -1 -0.5 0 0.5 1 1.7 2.5 4 7 12 19 45
```
The sensor at index 9 (0°, dead ahead) is the primary braking input.
Side sensor groups (indices 0–3 left, 15–18 right) are used for turn-in aim.

---

## Known Limitations

- **Linux auto-restart code removed.** The original `pkill torcs` / shell relaunch sequence
  from the base `snakeoil3_gym.py` has been replaced with a clean exit message for
  Windows compatibility. On Linux the simulator will not auto-relaunch on connection failure.
- **Single track tuned.** All parameters were tuned on Corkscrew. Performance on other
  tracks is untested.
- **BOB-C9c safety zone** is hardcoded to `distFromStart 2350–2415 m` — this is specific
  to the Corkscrew track geometry and will fire incorrectly on other tracks.
- **No vision input.** The controller uses only the 19 track sensors, speed, angle,
  trackPos, and wheel spin velocity. No camera or pixel input.
