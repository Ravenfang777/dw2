KH1FM AQUA ANIMATION TEST v10 - TEST 2
Steam Global / OpenKH Panacea

MAIN AQUA ACTIONS
Action                   Ground source   Air source
Fire                     316             391
Thunder                  317             390
Cure                     318             427
Falling                  506

Fire uses one continuous source clip through KH1's release/recovery records:
316 frames 0..20 then 20..30; 391 frames 0..31 then 31..48.
506 replaces falling only. Jump takeoff/rise and landing keep their V9 poses.
The original aqua ground/air combos remain the same as V9.

FIVE ABILITIES, ALL 0 AP
aqua   : main Aqua moveset, with the action assignments above
aqua 1 : Test 2 ground 392 393 428 ; air 429 504 514
aqua 2 : Test 2 ground 515 517 550 ; air 650 557 411
aqua 3 : Test 2 ground 399 352 353 ; air 500 501 503
aqua 4 : Test 2 ground 510 511 512 ; air 513 507 508

The numbered entries inherit the main movement, falling, casting, items,
reactions, Guard and Cartwheel. Only their ground/air combo sets differ.
The first clip is attack one, the second attack two, the third the finisher.
KH1's alternate second ground attack also uses the selected second clip.
Selecting a new Aqua entry turns the other Aqua entries off. Native ability
states are retained. Select while idle; active actions finish before switching.
Ability ids117..121 and saved selections remain compatible with V9.

SHARED KH1 CAST RECORDS
Native KH1 dispatch is ground request 0x36 + spell index, air 0x83 + index.
Fire=0, Blizzard=1, Thunder=2, Cure=3, Gravity=4, Stop=5, Aero=6.
Thunder and Cure normally share a physical animation record. While any Aqua
entry is active, an actor-local copy of the existing request table routes only
Thunder requests 0x38/0x85 to the alternate casting record. Cure keeps 0x39/0x86.
All other request words/flags, table sizes, record counts and original tables
stay intact. Unequipping Aqua restores the exact original lookup pointer.
No new native-code hook is used for this cast separation.

Blizzard/Gravity share 317 on the ground and 390 in the air. Stop/Aero share
318 on the ground and 427 in the air. These inherited poses are intentional
for this test; the spells still run their native KH1 effects and game logic.
Thunder now uses that alternate record's native duration: 86 ground frames
and 78 air frames, instead of 68/68. Its cast/recovery timing needs an in-game
check. Other record durations stay as V9. This is an animation test; the BBS
clips' original durations are resampled to the selected KH1 records.

RETAINED CORRECTIONS
- Anatomical hand pivots100/205 and forearm-helper alignment from V9.
- Original main-combo finisher arm-clearance adjustment from V9.
- Hair rest rotations from V8; no animated anatomical stretch or scale.
- Working native spell-origin and glow/effect-matrix route to the LEFT palm206
  in all five profiles. The prior right-hand route has not been reinstated.

INSTALL
1. Fully close KH1.
2. Disable Aqua v9 and all older Aqua packages, Sora Restore Check, and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH and enable Aqua Animation Test v10.
4. Build and Run, then load your save. Missing Aqua entries are added off;
   a saved selection is respected. Native entries are never evicted to fit.
5. Equip aqua or one of aqua 1..4 while standing idle. The main aqua entry
   does not need to be equipped along with a numbered entry.

TEST
- With aqua equipped, check Fire, Thunder and Cure on the ground and in the
  air. Check spell release, recovery and the LEFT-hand launch/glow alignment.
- Step off a ledge and check 506 during falling. Check jumps/landing as well.
- Switch through aqua 1..4 while idle and test three-hit ground/air combos.
  Unequip Slapshot, Sliding Dash, Vortex, Hurricane Blast and other native
  combo replacements for a clean test; their separate actions stay native.
  Guard and Dodge Roll still need their native abilities equipped.
- Turn every Aqua entry off and recheck native casting. Repeat after room
  changes and after save reloads on both saves.

RETURN
Return the NEW kh1-aqua.log beside the game EXE and a short comparison video.
Its first line must say ANIMATION TEST v10 Test 2. Profile numbers in the log:
0=native, 1=aqua, 2=aqua 1, 3=aqua 2, 4=aqua 3, 5=aqua 4.
AQUA CAST REQUESTS reports enabling/restoring the separated Thunder lookup.
CHECK_AQUA_V10.cmd optionally checks installation hashes and writes
Aqua_Animation_Check_v10.txt.

SCOPE
KH1 damage, targeting, projectile scripts, spell simulation, MP, guard coverage,
dodge invincibility and actor travel remain native. Native attachment queries
use the left hand during eligible Aqua casts. BBS commands, damage and effects
are not imported. Guard uses the Barrier pose with KH1 Guard behavior.
Both installed MSET files are original. Motion poses use only existing table
allocations; all motion headers, counts, lengths and eleven helpers remain
original. Unknown/foreign body records or request tables block writes.
Only the supplied normal Sora and Olympus banks are admitted.

FILE GUIDE
ABILITY_SETS.txt gives exact Test 2 combos.
ANIMATION_MAP.csv lists all five profiles' effective action assignments.
TEST_CLIP_SOURCES.csv gives the new casts/falling and Test 2 source banks,
frame counts, payload hashes and fitted slots. 399 uses p02ex_346.arc,
353 uses p02ex_352.arc, and 411 uses p02ex_313.arc (dedicated source banks).
These numbered labels are not assumed to be official BBS command names.
REMAINING_NATIVE.csv lists unassigned native records.
The earlier 349-clip CSV/JSON inventory is included under inventory. Its
source metadata is unchanged; ANIMATION_MAP.csv has current assignments.

OPTIONAL NATIVE-MAGIC ATTACHMENTS
Copy DISABLE_HAND_MAGIC_kh1-aqua.ini beside the game EXE as kh1-aqua.ini and
restart to retain native weapon-tip attachments with these animation poses.
Remove that INI and restart to restore left-hand attachment routing. This
option does not disable the separated Thunder animation lookup.

SAVE / REMOVE ALL AQUA ENTRIES
Saving in-game may retain ids117..121. To remove them, copy
REMOVE_AQUA_kh1-aqua.ini beside the game EXE as kh1-aqua.ini, leave v10 enabled,
restart and load each save to clean. Check AQUA ABILITIES REMOVED, then save
in-game. Exit, remove the INI, disable v10 and rebuild. Native ability order
is preserved; only these five ids are removed.

VALIDATION
38 tests execute the compiled PE DLL in a Win64 ABI mock host. They include
all five profiles in both banks, exact action lookup mappings, only two changed
request words, original lookup/body restoration, reloads, exclusivity, removal,
foreign-data rejection and the distinct left-palm attachment route.
14 geometry/assignment tests cover all 75 generated records, native capacities,
hair, wrist helpers, bind lengths/scales, Fire phase continuity, looping fall,
jump transitions and the retained main-finisher clearance adjustment.
These checks do not render Sora's mesh or execute Windows/KH1. The new cast
routing and timing, source-clip appearance and final FX alignment need your
in-game check. Some mesh clipping may still need adjustment.
