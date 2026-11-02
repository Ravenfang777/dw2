KH1FM AQUA ANIMATION TEST v17
Steam Global / OpenKH Panacea

REQUESTED MAIN AQUA MOVES
Ground:300 ->300 ->366. Both native second-ground variants now use300.
Air:305 ->407 ->351.
The first ground hit retains v16's earlier contact. The second swing still
completes before a16/20-native-frame recovery window allows the finisher.
Its hit keys now match300's strike phase. Native damage and event payloads,
sounds, effects and all four numbered test sets are retained.

DEFAULT GLIDE
All Glide animation bodies, opening/flight/ending behavior, native clocks,
queued start frames, steering and movement are original Sora/KH1 again.
There is no Aqua350 opening, held pose, closing overlay or clock clamp.
Glide records75..78 (Olympus37..40) are absent from Aqua's runtime patch table.
Normal Glide unlock and held-button requirements remain native. The regular
Glide constructor passes through except while the active504 dodge owns the air
action. Native Glide ending returns to the selected profile's normal fall506;
there is no added350 ending or fall restart. Superglide is unchanged.

DUAL D2X AERIAL DODGE / AQUA504
Uses the recorded Dual D/Master baseline: height145, horizontal speed18.
As in Dual D's2x setting, every requested upward/directional displacement is
multiplied by2. The full held rise is290 units and moving speed36 units per
native clock unit. This does not multiply animation duration or arc time.
Aqua504 remains in the existing40-frame native fall record, then506 resumes.
Neutral stick rises vertically; tilted stick adds normalized directional travel.
Release Circle after takeoff, then press again airborne. One dodge per airtime;
land to rearm. Holding/releasing Circle retains the existing full/short arc rule.

The recorded Dual D145/18 values and2x policy are matched. The KH1 controller's
existing gravity/release adapter remains: baseline gravity0.75, upward release
cap4 and falling cap20, before2x displacement scaling. This is not a claim that
those adapter coefficients were extracted from KH2. Exact KH2 gravity/clip202
length was not present in the supplied source extract. Native collision, landing
and interruption callbacks remain; the mod never writes actor position directly.
No new invulnerability, guard window, hitbox or growth ability is granted.

WHOLE HEAD DURING RUNNING
V16 targeted joint151, an unskinned hair helper. The face/skull is skinned joint
150. V17 puts Aqua's authored head-bone5 direction on skull150, then keeps
hair helper151 at its local bind rotation. The face and attached hair now follow
one head instead of adding a separate tilt to the bangs. This is a head mapping
correction rather than another fixed hair-angle adjustment. Ordinary/combat run
slots5/6/7 are corrected. Torso, neck, bind lengths, scales and native travel stay.
Appearance needs a live game check; the offline tests verify the actual skin flag
and the serialized skull/head orientation, not just a helper's position.

RETAINED ABILITIES / CASTING
Main aqua / id117 /0AP: ground300 300 366; air305 407 351.
aqua 1 / id118 /0AP: ground316 317 318; air391 390 427.
aqua 2 / id119 /0AP: ground315 371 366; air365 218 332.
aqua 3 / id120 /0AP: ground393 411 352; air616 407 351.
aqua 4 / id121 /0AP: ground510 511 512; air504 514 399.
Numbered tests are unchanged. Default Glide,2x dodge and common run correction
apply to all five. Select one while idle; native ability entries are not evicted.
Main Fire391/316, Blizzard Fire visuals on original Blizzard events, Cure427/318,
Stop/Aero317/390, item007/395, falling506 and keyblade-tip magic remain from v16.

INSTALL
1. Fully close KH1.
2. Disable Aqua v16 and all older Aqua packages, Sora Restore Check and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP in OpenKH, enable Aqua Animation Test v17, Build and Run.
4. Load your save and equip main aqua while standing idle.

TEST ORDER
- Check ground300 ->300 ->366, both locked and unlocked.
- Check air305 ->407 ->351 through the finisher.
- Run sideways to the camera and inspect the FACE/head angle and hair together.
- Jump, release Circle and press again: neutral lift, then directional travel
  on another jump. Hold/release to compare height. Land between attempts.
- Check native Glide start, straight flight, turns and release. No Aqua350 pose
  should play, and a long flight/turn must not hold or clamp the native clock.
- Check both saves/room changes, numbered sets and restoration with aqua off.
For clean basic-combo tests, unequip Slapshot, Vortex, Hurricane Blast and other
native attack replacements; those separate actions retain their own timing.

LOG / INSTALL CHECK
Capture the new kh1-aqua.log before restarting, since each launch replaces it.
It should begin v17. Dodge should log DUAL D2X MOVEMENT,504 accepted, queued
restart committed and DODGE MOVEMENT ACTIVE. No GLIDE350 marker should appear.
CHECK_AQUA_V17.cmd checks installed asset hashes and writes
Aqua_Animation_Check_v17.txt; drag the OpenKH folder onto it if needed.
A short side-view recording will help verify the visible head correction.

VALIDATION
71 actual-PE runtime checks and22 geometry/assignment checks passed offline.
Tests cover both banks, new combo assignments and strike phase, all five
profiles, untouched native Glide bodies/clocks/queues,2x lift/direction with
unchanged504 timing, native handoff, original Blizzard events and restoration.
Run checks verify skull150's native skin flag, authored head orientation and
neutral hair helper151. All original motion headers, sizes, frame/bone/helper
counts and travel remain. Both installed MSETs are original. There are47 mapped
normal records and46 Olympus records; native Glide is deliberately not mapped.
Windows/KH1 and the rendered mesh were not executed here. In-game visual quality,
controller feel and collision still need verification.

FILES
ANIMATION_MAP.csv / SPELL_MAPPING.csv: current five-profile assignments/casts.
COMBO_TIMING.csv: first/second contacts and full-swing recovery windows.
AIR_DODGE_MAPPING.csv: Dual D baseline,2x travel and timing.
GLIDE_MAPPING.csv: original native Glide scope. RUN_POSE.csv: skin/head mapping.
TEST_CLIP_SOURCES.csv: source banks, frames, rates, cuts and hashes.
source: rebuild code, original/fitted fixtures, checks and evidence reports.
inventory: existing349-clip source inventory. Numeric IDs are source labels;
official BBS move names remain unverified where the inventory says so.

OPTIONAL DISABLE / REMOVE
Copy DISABLE_AIR_DODGE_kh1-aqua.ini beside the EXE as kh1-aqua.ini and restart
to disable only504 input/movement. Glide remains fully native. Remove the INI
and restart to reenable. To remove all five abilities, use REMOVE_AQUA_kh1-aqua.ini
as kh1-aqua.ini, leave v17 enabled, restart/load each save, check ABILITIES REMOVED,
save in-game, exit, remove the INI, disable v17 and rebuild. Only IDs117..121 are
removed. Profile/body switching/restoration waits until idle.
