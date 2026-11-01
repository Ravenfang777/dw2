KH1FM AQUA ARM PROBE v4
One ground attack; original native file layout

The restore check confirmed your original movesets load and that the old
dual-wield DLL was absent from the compiled mod folder. Aqua v2 still failed.
Do not use v1 or v2 for this test.

V4 changes the existing wrist-goal curves of the FIRST ordinary ground attack
using Aqua clip 300. The native arm/shoulder solver follows those goals.
The torso, legs, root movement, clip durations, event tables, animation offsets,
helper count and file length remain original. This does not attempt the full
Aqua combo, Guard or Cartwheel. Expect an altered first swing on native Sora.

EXACT SETUP
1. Fully close the game.
2. Disable Aqua v1, Aqua v2, Sora Restore Check v3, Nine Styles / Dual Wield v52,
   and other Sora moveset/model/combat-animation replacements.
3. Import this ZIP, enable Aqua Arm Probe v4, and choose Build Only.
4. Extract this ZIP somewhere writable and run CHECK_PROBE.cmd. It checks
   the compiled file hashes and creates Aqua_Arm_Probe_Check.txt beside itself.
5. Launch through OpenKH with that same mod list. Load the save that failed
   under v2. In Traverse Town, stand still, walk, stop and jump.
6. If loading and movement are normal, unequip attack replacements such as
   Slapshot/Sliding Dash/Vortex for the test, then tap Attack ONCE in empty
   space and let it finish. Repeat a few single taps. A full combo is not needed.

RETURN
Aqua_Arm_Probe_Check.txt plus:
- Did the usual save load, including a second fresh launch?
- Were idle/walking/jumping normal?
- Did one ground attack complete normally? A short video of that attack helps.
If loading or movement fails, return that result before testing attacks.

SCOPE
Only normal-world Sora's first-ground-attack arm curves are changed. The
Olympus MSET is an exact copy of your original file, to remove any stale v2
Olympus replacement. No new ability, selectable style, DLL, or save change.
The checker also collects available Windows Application Error events; it does
not read or modify save files. No Windows runtime testing was done here.

validation.json at the ZIP root contains the
actual byte-change bounds and offline pose checks. source/ contains the builder,
calibration math and format references. Passing these checks does not prove
runtime stability; this small probe is the next in-game compatibility check.
