KH1FM AQUA ANIMATION TEST v13 - REVISED TEST 4
Steam Global / OpenKH Panacea

MAIN AQUA
Ground combo: 300, 218, 366 (first, second, finisher).
Both native second-ground variants now use218.
Air combo: 351, 353, 393 (first, second, finisher).
Ground and aerial item use: 007 /395, using the shared395 payload.
Glide:350 opening frames0..20, held middle frame20 during flight, then
closing frames20..40 before returning to506 falling.

Aerial Dodge504 now always queues a native animation restart, including when
Sora is already falling. The old path only reset the fall clock. Uncommitted
command-menu selections no longer block the action; a committed native
command still takes priority. Fresh presses are accepted even if the held
input bit is already clear. Logs now identify rejected input and whether the
native control callback is being reached. These changes passed offline
checks; the cause of your in-game failure has not been confirmed from a log.

TEST 4 ABILITIES - ALL 0 AP
aqua   : ground300 218 366 ; air351 353 393
aqua 1 : ground316 317 318 ; air391 390 427
aqua 2 : ground315 371 366 ; air365 218 332
aqua 3 : ground393 411 352 ; air616 407 351
aqua 4 : ground510 511 512 ; air504 514 399

Each triplet means first attack, second attack, finisher. KH1's alternate
second ground attack uses the selected second clip too. Numbered entries
share the main movement, Glide, item use, falling, casting, reactions,
Guard, Cartwheel and airborne dodge; their combos are the differences.
Select one while idle; the other Aqua entries turn off. Existing ability
ids117..121, saved selections and all native ability entries are retained.

INSTALL
1. Fully close KH1.
2. Disable Aqua v12 and every older Aqua package, Sora Restore Check and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH and enable Aqua Animation Test v13.
4. Build and Run, then load your save.
5. Equip aqua or aqua1..4 while idle. Missing entries are granted off;
   saved selections are respected. Native entries are never evicted to fit.

TEST ORDER
- Equip aqua and test ground300/218/366, then air351/353/393.
- Jump, release Circle, then tap Circle again for504. Test a neutral stick
  and a directional stick. It is once per airtime; land to rearm.
- Test ordinary Glide with its native unlock, equipped ability and input
  requirements. It retains native movement and release rules. Check350's
  opening, held middle pose, steering, then closing pose when Glide ends.
  A successful504 press consumes Circle during that action. After it ends,
  native Glide can resume; holding the takeoff button also retains native
  Glide behavior. This build does not grant Glide or Superglide.
- Use an item on the ground and in the air; check007/395.
- Equip aqua1..4 while idle; test each ground and air triplet. For clean
  combo testing, unequip Slapshot, Sliding Dash, Vortex, Hurricane Blast and
  other native combo replacements; they retain their separate native poses.
- Recheck Fire, Thunder and Cure with LEFT-hand effects, both saves, room
  transitions and reloads; finally turn all Aqua entries off and check Sora.

IF504 STILL DOES NOT PLAY
Return kh1-aqua.log from beside KINGDOM HEARTS FINAL MIX.exe after one test.
Its first line must identify v13. It records AIR DODGE READY, CONTROL OBSERVED,
accepted/rejected AIR INPUT data, and queued-restart completion. Each run
replaces the log, so capture it before restarting. CHECK_AQUA_V13.cmd verifies
installed asset hashes and writes Aqua_Animation_Check_v13.txt; include that
report if installation is in doubt.

MOVEMENT / ANIMATION SCOPE
504 remains an animation test using the existing40-frame fall record. It
adds no invulnerability, double-jump height or new BBS dash movement. Native
state, gravity, velocity, collision and interruption rules remain in control.
350 uses the real four native Glide records, including the shared Superglide
poses. The first40 native frames play source0..20; later flight holds source20.
Steering carries the current pose progress into the next native Glide motion.
Native Glide release returns to fall6; a temporary40-frame closing350 pose
then restores506. Landing, attacks, casts and unequipping interrupt it.
The source has41 frames at30fps. Native motion headers and capacities stay
original; the opening/held records retain120/60/60/60 native-frame capacities.
Phase control requires the checked control hook. If admission fails, the log
says AIR ACTIONS UNAVAILABLE and other Aqua animations remain available.

LAYOUT / CASTING
Both installed MSET files are original. All fitted records keep original
headers, lengths, table allocations, bone counts, eleven helpers and travel.
Unknown motion data or request tables block writes. Only the supplied normal
Sora and Olympus banks are admitted. Body switching waits for idle.
KH1's damage, event tracks, spell scripts, MP, targeting, Guard coverage and
Dodge Roll windows remain native. BBS command scripts/effects/damage are not
imported with these animations. Existing hair and wrist corrections remain.
Fire316/391, Thunder317/390, Cure318/427 and LEFT-hand spell origins/glow remain.
Thunder keeps the alternate86 ground/78 air casting durations from v10;
Blizzard/Gravity share317/390 and Stop/Aero share318/427. Cast timing and final
mesh/FX appearance still require an in-game check.

FILE GUIDE
ABILITY_SETS.txt: current Test4 sequences.
ANIMATION_MAP.csv: the51 usual records per profile (50 available in Olympus).
AIR_DODGE_MAPPING.csv: temporary504 and its input rule.
GLIDE_MAPPING.csv: source350 phases, native slots, timing and hold behavior.
TEST_CLIP_SOURCES.csv: current changed actions/test sets with source frames,
exact bank/PAM member, aliases and animation payload hashes.
source/source_selections.json: inventory choices for this build.
inventory: unchanged349-clip inventory; current mappings are the root CSVs.
007/395 are aliases for identical source animation data;395 is selected here.
Numeric IDs are source identifiers, not official command names.

OPTIONAL FALLBACKS
To disable only airborne Circle504, copy DISABLE_AIR_DODGE_kh1-aqua.ini beside
the EXE as kh1-aqua.ini and restart. Native Circle/Glide input and the350 phase
controller remain available. To retain weapon-tip spell attachments, use
DISABLE_HAND_MAGIC_kh1-aqua.ini instead. Combine air_dodge=0 and hand_magic=0
in one [aqua] INI if needed. Remove the INI and restart for defaults.

REMOVE ALL AQUA ENTRIES
Copy REMOVE_AQUA_kh1-aqua.ini beside the EXE as kh1-aqua.ini. Leave v13 enabled,
restart and load each save to clean. Check AQUA ABILITIES REMOVED, then save
in-game. Exit, remove the INI, disable v13 and rebuild. Only ids117..121 are
removed; native ability order stays intact.

VALIDATION
59 tests execute the emitted PE DLL in a Win64 ABI mock host, including delayed
native restart, input diagnostics, all five profiles, both banks, Glide steering,
closing/interruptions, lookup/body restoration and hook failure paths.
15 geometry/assignment tests cover81 generated pose variants, the exact new
mappings, item alias hash, Glide hold/closing boundary, native capacities,
travel, bind lengths/scales, wrists, hair and existing jump/Fire transitions.
All fits remain below the existing5-unit position-error limit with no capacity
expansion. These checks do not run Windows/KH1 or render Sora's mesh.
The new504 route,350 behavior, new clips and final appearance need in-game testing.
