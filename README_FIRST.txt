KH1FM AQUA ANIMATION TEST v16
Steam Global / OpenKH Panacea

CHANGES FOR THIS TEST
Blizzard: restored its ORIGINAL native request records and spell-event tracks.
Main Aqua borrows full Fire visuals391 ground /316 air in Blizzard's own slots.
The added recovery queue and Fire lookup remap from v15 are removed. Native
Blizzard scripts, projectile release, MP, element, target and effects remain.
This applies to Blizzard, Blizzara and Blizzaga. Test on the ground and in air.

Main ground combo remains300 ->365 ->366; air remains351 ->352 ->393.
The first ground hit's contact is earlier (12 instead of18 native frames).
Both second-hit variants reach the END of365 before a usable follow-up window:
- normal99 / Olympus61: swing finishes32; chain window32..48; contact24.
- normal100 / Olympus62: swing finishes44; chain window44..64; contact36.
The second motion holds its final pose during that recovery window. This
replaces v15's single-frame chain window. Existing damage/event payloads and
sound/effect keys stay original. All numbers above use the native motion clock.
The main first-hit follow-up window remains22..40. Numbered tests keep their
original native event timing. Test locked and unlocked attacks for both variants.

Glide: Aqua350 opens with source frames0..20, holds source frame20 during
flight, then closes with20..40 before falling506. Turning does not replay the
opening. The Sora middle-body handoff has been removed. KH1 still controls
Glide's movement, collision, steering, normal unlock and held-button release.

Aerial dodge: uses a Master-style movement controller with the assigned Aqua504
visual. Neutral stick gives vertical lift; a tilted stick adds directional
travel. Release Circle after takeoff, then press it again while airborne.
One dodge per airtime; landing rearms it. Holding Circle allows the fuller arc;
releasing early shortens the upward part. Native Glide entry is suppressed only
while504 is active. Afterward KH1 resumes fall506 at the actual collided height.
The controller supplies displacement BEFORE native collision. It never writes
actor position directly. Walls, ceilings, landing and interruptions stay native.
This is a KH1 adaptation of Master's movement structure, not an exact KH2 port.
Current test tuning: held rise96 native units, horizontal speed6 units per
native frame, up speed12, gravity0.75, release up-speed cap4, max fall speed20.
No extra invulnerability, guard window or damage is added. Superglide remains.

Run: the head is lifted12 degrees in ordinary and combat running. Torso motion,
body proportions and bind hair rotations are retained. Check the angle in-game.

NUMBERED TEST4 SETS
Main aqua / id117: ground300 365 366; air351 352 393.
aqua 1 / id118: ground316 317 318; air391 390 427.
aqua 2 / id119: ground315 371 366; air365 218 332.
aqua 3 / id120: ground393 411 352; air616 407 351.
aqua 4 / id121: ground510 511 512; air504 514 399.
Only main aqua gets the Blizzard visual selector and ground event edits.
Common movement/run changes and keyblade-tip magic apply to all five abilities.
Main Fire391/316, Cure427/318, Stop/Aero317/390 and item007/395 are retained.
Numbered cast poses are unchanged. Select one Aqua ability while standing idle;
all five cost0 AP, use the existing saved IDs, and are mutually exclusive.

INSTALL
1. Fully close KH1.
2. Disable Aqua v15 and every older Aqua package, Sora Restore Check and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH, enable Aqua Animation Test v16, Build and Run.
4. Load a save and equip main aqua while standing idle.

TEST ORDER
1. Grounded Blizzard, Blizzara/Blizzaga if available, then aerial Blizzard.
2. Ground basic combo300 ->365 ->366, locked and unlocked. Confirm the first
   hit feels earlier and a follow-up during the second hit's recovery chains.
3. Jump, release Circle, press again: neutral lift, then directional lift on
   another jump. Hold/release to compare height; land between attempts.
4. Glide straight, turn both ways, hold a longer flight, then release. Check
   Aqua's beginning, held pose and ending.
5. Run facing sideways to inspect head pitch; check both saves and room reloads.
6. Unequip aqua, stand idle, and check Sora restoration. Check numbered sets too.
For clean basic-combo tests, unequip Slapshot, Vortex, Hurricane Blast and other
native attack replacements. Those separate native actions keep their own timing.

LOG / INSTALL CHECK
Return the new kh1-aqua.log after testing, with a short recording if appearance
or collision still fails. Capture it before restarting; each launch replaces it.
The first line should say v16. Aerial dodge should log AIR DODGE READY, accepted
504, queued restart committed and DODGE MOVEMENT ACTIVE. If the last marker is
missing, the animation ran without reaching the movement callback.
CHECK_AQUA_V16.cmd checks installed asset hashes and writes
Aqua_Animation_Check_v16.txt. Drag the OpenKH folder onto it if needed.

VALIDATION / LIMITS
72 actual-PE runtime checks and21 geometry/assignment checks passed offline.
The tests cover both motion banks, original Blizzard queue/event bytes, all
profiles, input/deferred Glide handling, movement direction and held/released
arcs, native fall handoff, unknown-data rejection, restoration and run/head fit.
The chain checks execute the supplied executable's actual native event sampler.
All motion headers, frame counts, allocations, eleven helpers and native travel
tracks retain their original capacity. Installed Sora/Olympus MSETs are original.
Neither Windows/KH1 nor Sora's rendered mesh was executed here. In-game spell
release, collision behavior, movement feel and appearance still need checking.

FILES
ANIMATION_MAP.csv: usual motion/source assignments for all five abilities.
SPELL_MAPPING.csv: all spells on the ground/in air, including transient Blizzard.
COMBO_TIMING.csv: main first/second contacts, source finish and chain windows.
AIR_DODGE_MAPPING.csv / GLIDE_MAPPING.csv: inputs, movement and visual phases.
TEST_CLIP_SOURCES.csv: exact source banks, frames, rates, cuts and hashes.
RUN_POSE.csv: running head correction. source: rebuild code, fixtures and checks.
inventory: prior349-clip inventory. Numeric IDs are source identifiers; official
BBS command names remain unverified where the inventory says so.

OPTIONAL DISABLE / REMOVE
Copy DISABLE_AIR_DODGE_kh1-aqua.ini beside the EXE as kh1-aqua.ini and restart
to disable only504 input/movement. Native Circle/Glide input remains available;
Aqua's Glide poses still apply. Remove the temporary INI and restart to reenable.
To remove all five abilities, use REMOVE_AQUA_kh1-aqua.ini as kh1-aqua.ini,
leave v16 enabled, restart and load each save to clean. Check ABILITIES REMOVED,
save in-game, exit, remove the INI, disable v16 and rebuild. Only IDs117..121 are
removed. Native ability entries are never evicted. Profile/body restoration
waits for idle; the native ability-list allocation remains unchanged.
