# ai-racing-final-SphiweDube
Project and Problem Statement

The unmodified base script (snakeoil3_gym.py) drives the Corkscrew in 00:54.9 with no damage and a 302 km/h top speed, but it has no braking logic at all — it only lifts off the throttle in corners. That is fast on a single lap, but it is not a controlled way to drive.
The problem: add braking so the car slows for corners deliberately, without crashing. The hard part turned out to be Corner 9 (~2410–2504 m), a left-hander where the first braking versions left the track (trackPos ≈ -1.645) and took 33 damage.
Goals:Finish the Corkscrew lap with zero damage.
Beat the first working braking lap (v1: 02:35.2).
Do it with a rule-based controller — no machine learning, no training data.
v2-C10 finished in 01:53 with zero damage — 42 s faster than v1, and the only braking version to complete a clean lap.

Setup and Run Command
Requirements
Python 3, standard library only. No pip install needed.
TORCS with the SCR server plugin (not part of the standard TORCS installer — see http://scr.geccocompetitions.com/).
Controller talks to TORCS over UDP port 3001. No other network setup.
TORCS setup (GUI)
Open TORCS.
Race → Quick Race → Configure Race → Drivers.
Move scr_server 1 from "Not Selected" to "Selected".
Select the Corkscrew track, click Accept, then start the race.
The car waits on the grid for a client — run the script now.
Order matters: start TORCS and reach the grid first, then run the script
Chosen script: snakeoil3_v2.py (v2-C10) — the only file needed to drive.
Self-contained. No local imports; it does not import any other file in this project.
Imports (all Python standard library): socket, sys, getopt, os, time, csv.
No third-party packages. No numpy, TensorFlow or gym.
Contains the UDP client (Client), server-state parsing, and the driving logic in drive_example() (lines 522–656).

Results
Times and damage read from the TORCS top-left panel at lap end. All laps are single laps from a standing start.


Enhancements over the base script

Line numbers refer to snakeoil3_v2.py.

Enhancement	Lines
1	CSV telemetry	61, 526–539, 661–673	Logs every tick to lap_data.csv for data-driven diagnosis
2	Clean connection exit	172–177	Countdown + clear message instead of the Linux pkill torcs crash-kill
3	Sensor-based braking	588–607	v_safe = √(2 × BRAKE_DECEL × track_ahead); brake scales with excess speed
4	abs(steer) penalty	598–601	Fixes signed-steer bug — left and right corners both cut target speed
5	Earlier turn-in	572–579	Steers toward the longer outer-sensor group (AIM_GAIN = 0.004)
6	Speed-based steering reduction	580–582	Less lock above 100 km/h to cut oversteer
7	Steering rate limit	583–586	Max 0.06 change per tick; prevents snap-steer
8	ABS	613–617	Halves brake when front wheels lock while rears roll
9	Throttle/brake isolation	619–627	Zero throttle while braking; ±0.01 per tick throttle build; stall boost under 10 km/h
10	Proportional traction control	629–632	Throttle cut scaled to wheel slip (slip / 50, 0.05–0.3)
11	Stuck / spin recovery	553–565	After 30 ticks beached, reverses and re-aligns
12	Lap-time adaptation	540–543, 634–647	LAP_PUSH multiplier (0.85–1.10) toward TARGET_LAP = 110.5 s (see limitation 5)
13	Corner 9 safety zone	609–611	Floor of 0.75 brake in 2350–2415 m when speed > 70 km/h


Bob is the AI coding assistant used throughout. In rough order of the work:
Explanation — walked through how the base script, sensors and SCR protocol work.
Planning — set up the hypothesis → smallest change → one lap → keep/modify/revert loop.
Diagnosis — read lap_data.csv to locate the failures: Corner 9 at ~2410–2504 m (trackPos ≈ -1.645), and 8 corners at 43–48 km/h minimum speed with the edge sensor at -1.00. This also exposed the signed-steer bug.
Code — wrote the changes in every version. In snakeoil3_v2.py the telemetry and Corner 9 lines carry # BOB-telemetry / # BOB-C9c tags; the v2-C10 rewrite of drive_example() (lines 540–656) was written by Bob and is not tagged line by line.
Tooling — wrote find_corners.py and the telemetry logging.
Documentation — drafted CHANGELOG.md, experiment-report.md, tuning-card.md, README.md and this file.
Student's contribution: set up TORCS and the SCR plugin, ran every lap, recorded each result in lap_log.xlsx, and decided which versions to keep or discard.

Video Link:https://youtu.be/60TsXwR2MVw
