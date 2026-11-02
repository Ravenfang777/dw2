KH1FM AQUA ANIMATION TEST v14
Steam Global / OpenKH Panacea

MAIN AQUA CHANGES
Fire: ground391; air316
Cure: ground427; air318
Stop / Aero: ground317; air390 (current Gravity animations)
Ground combo:300,365,366
Air combo:351,371,393
Both native second-ground variants use365. Each combo is first, second, finisher.
Fire retains its split release/recovery structure using the swapped source clip.
Stop/Aero share Gravity's existing86-ground/78-air-frame casting records;
previously they shared Cure's68/68-frame records. Native spell behavior remains.

AERIAL DODGE504 REPAIR
Your v13 log recorded five airborne presses rejected only by mask0x100:
state2, request0xA, one allowed air motion queued, held/pressed6, input record
0x03000000. V13 misread bit24 as a busy command. The supplied executable skips
command dispatch when that bit is set; when it is clear, a nonzero low command
byte dispatches a native command. V14 follows that native branch condition.
The logged input now plays504 in the actual-DLL mock host for all five profiles
and both banks. Actual post-fix KH1 verification is still needed.

Release Circle after takeoff, then press it again airborne. Neutral and
directional stick input are supported. It is once per airtime; landing rearms.
The checked native queue always restarts the fall animation, including from
an existing fall. Pending native commits, timeouts and interruptions are handled.
It remains an animation test: no added invulnerability, height or BBS dash travel.

TEST4 NUMBERED PROFILES - ANIMATIONS RETAINED FROM v13
aqua   : ground300 365 366 ; air351 371 393 (new main profile)
aqua 1 : ground316 317 318 ; air391 390 427
aqua 2 : ground315 371 366 ; air365 218 332
aqua 3 : ground393 411 352 ; air616 407 351
aqua 4 : ground510 511 512 ; air504 514 399

The Fire/Cure swaps and Stop/Aero routing edits apply only to main aqua.
Numbered entries keep v13 Fire316/391, Cure318/427 and Stop/Aero318/427.
Thunder, Blizzard and Gravity use317/390 in every profile. LEFT-hand spell
origins/glow, item007/395, falling506, Guard, Cartwheel, reactions and movement
remain. All five entries share the corrected504 input handling.
Ability ids117..121 and0AP remain. Select one while idle; other Aqua entries
turn off. Saved selections are respected. Native abilities are never evicted.

INSTALL
1. Fully close KH1.
2. Disable Aqua v13 and all older Aqua packages, Sora Restore Check and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH and enable Aqua Animation Test v14.
4. Build and Run, then load your save and equip aqua while idle.

TEST
- With main aqua, test Fire and Cure on the ground and in the air.
- Check grounded Stop/Aero against grounded Gravity, then aerial Stop/Aero
  against aerial Gravity. They should use matching animation families.
- Test ground300/365/366 and air351/371/393. Unequip native combo replacements
  such as Slapshot, Vortex and Hurricane Blast for clean basic-combo testing.
- Jump, release Circle, then press again to test504; land between attempts.
- Check LEFT-hand effects, item use, Glide350, transitions/reloads and both saves.
- Numbered profiles retain their v13 animations. Turning Aqua off at idle
  restores the original bodies and original actor request-table pointer.

IF DODGE STILL FAILS
Return the new kh1-aqua.log from beside KINGDOM HEARTS FINAL MIX.exe after one
test. Its first line must identify v14. AIR DODGE READY and CONTROL OBSERVED
confirm hook admission and arrival. AIR INPUT records the accepted/rejected
press, current/first queued request, held/pressed input and command flags.
The file is replaced on each game launch; capture it before restarting.
CHECK_AQUA_V14.cmd checks installed asset hashes and writes
Aqua_Animation_Check_v14.txt. Drag your OpenKH folder onto it if needed.

RETAINED GLIDE350
The first40 native Glide frames play source0..20, then hold source frame20.
Steering carries that progress into the next native Glide pose. Native release
into fall6 plays closing source20..40 on the existing40-frame fall record,
then returns to506. Landing/busy actions/off interrupt the closing pose.
Normal Glide records75..78 match Olympus37..40. The original120/60/60/60-frame
record capacities remain. Native Glide/Superglide unlock, equipped ability,
held-input, state, velocity, descent and collision requirements remain.
The checked control hook provides phase handling; air_dodge=0 disables only
504, retaining native Circle/Glide input and the350 controller.

CAPACITY / BEHAVIOR
Both installed MSET files are original. All fitted records keep native headers,
lengths, counts, table allocation, eleven helpers and helper travel. Only known
normal Sora/Olympus motion data and request tables are admitted. No records,
helper slots, hitboxes or new BBS command logic are added. KH1 damage, spell
scripts, MP/targeting, native event tracks and defensive windows remain native.
Source changes alter poses; existing native record durations govern their speed.
Thunder retains its86/78-frame alternate casting duration. Main Stop/Aero now
use that same Gravity family timing. Final cast timing/FX needs an in-game check.

FILES
ABILITY_SETS.txt lists current sequences.
SPELL_MAPPING.csv lists all seven spells, ground/air, for all five profiles.
ANIMATION_MAP.csv lists51 usual records per profile (50 available in Olympus).
AIR_DODGE_MAPPING.csv and GLIDE_MAPPING.csv describe the transient actions.
TEST_CLIP_SOURCES.csv lists selected sources, ranges, frames, FPS and hashes.
source contains current code, fitted fixtures, test reports and rebuild inputs.
inventory retains the existing349-clip list; current assignments are the CSVs.
007/395 are aliases for the same item animation payload. Numeric source IDs
are not official command names.

OPTIONAL FALLBACKS / REMOVE
To disable Circle504, copy DISABLE_AIR_DODGE_kh1-aqua.ini beside the EXE as
kh1-aqua.ini and restart. To retain native weapon-tip casting attachments, use
DISABLE_HAND_MAGIC_kh1-aqua.ini. Combine air_dodge=0 and hand_magic=0 in a
single [aqua] INI if needed. Remove the INI and restart for defaults.
To remove all five Aqua entries, use REMOVE_AQUA_kh1-aqua.ini as kh1-aqua.ini,
leave v14 enabled, restart and load each save to clean. Check AQUA ABILITIES
REMOVED, then save in-game. Exit, remove the INI, disable v14 and rebuild.
Only ids117..121 are removed; native ability order stays intact.

VALIDATION
64 actual-PE Win64-ABI mock-host tests passed, including the logged Jump input,
native-command exclusion, delayed commits, all five profiles/both banks,
main-only spell lookup changes, idle switching/restoration and failure paths.
17 geometry/assignment checks passed across105 serialized profile/transient
assignments (86 distinct fitted records), including the new second hits,
main-only spell swaps, Fire continuity, native capacities/travel and hair/wrists.
All fits remain below the existing5-unit position-error limit. The checks do
not run Windows/KH1 or render Sora's mesh; post-fix gameplay needs confirmation.
