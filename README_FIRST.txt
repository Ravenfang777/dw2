KH1FM AQUA ANIMATION TEST v11 - TEST 3
Steam Global / OpenKH Panacea

NEW MAIN AQUA ACTIONS
- Ground combo finisher: 411 (first/second ground attacks stay 300/301/302).
- Neutral aerial dodge: 504. In free air, release Jump/Circle after takeoff,
  leave the left stick neutral, then press Circle again. One use per airtime;
  land to rearm. The numbered Aqua entries inherit this movement action.
- Normal falling remains 506. Fire316/391, Thunder317/390, Cure318/427 and
  LEFT-hand spell origins/glow remain from v10.

TEST 3 ABILITIES - ALL 0 AP
aqua   : main ground finisher411, neutral aerial dodge504; original main air combo
aqua 1 : ground 516 518 519 ; air 607 608 609
aqua 2 : ground 610 611 612 ; air 616 618 619
aqua 3 : ground 613 602 603 ; air 604 605 606
aqua 4 : ground 617 405 406 ; air 407 452 621

The first clip is attack one, second clip attack two, third clip the finisher.
KH1's alternate second ground attack uses the same selected second clip.
Numbered entries share the main movement/casting/reaction/Guard/Cartwheel poses;
only their combo assignments differ. Select one Aqua entry while idle. The
other Aqua entries turn off automatically; native ability states stay intact.
Ids117..121 and saved selections remain compatible with v10.

AERIAL DODGE TEST BEHAVIOR
This adds an animation action on logical Jump/Circle with a neutral left stick.
A fresh press after releasing the takeoff button is required. Directional
Circle, holding the initial jump, ground actions, attacks/casts/reactions,
ledge transitions, scenes and shortcut inputs do not start it.
504 is fitted to the existing 40-frame fall record. The native motion clock
starts at zero; the pose plays once, then the normal 506 body is restored.
Landing, attack/cast interruption, unequipping and actor/bank changes end it.
The native control step runs with only its Jump bits temporarily consumed
during the dodge; those input bits are restored immediately afterward.
Normal directional movement, gravity, velocity and collisions remain native.
This test does NOT add BBS dodge travel, a vertical boost or invincibility.
If you hold Circle after the pose ends, KH1 may then enter its normal Glide.

INSTALL
1. Fully close KH1.
2. Disable Aqua v10 and all older Aqua packages, Sora Restore Check and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH and enable Aqua Animation Test v11.
4. Build and Run, then load your save.
5. Equip aqua or one of aqua 1..4 while idle. Missing entries are granted off;
   saved selections are respected. Native entries are never evicted to fit.

TEST ORDER
- Equip aqua. Test its three-hit ground combo and the new 411 finisher.
- Jump, release Circle, leave the left stick neutral, then tap Circle again.
  Look for 504 once, followed by 506. Land and repeat. Also test directional
  Circle and a held takeoff press; these should retain their native behavior.
- Test interruption by attacking/casting and landing. Check normal Glide too.
- Equip aqua 1, 2, 3 and 4 while idle; test each three-hit ground/air combo.
  Unequip Slapshot, Sliding Dash, Vortex, Hurricane Blast and other native
  combo replacements for a clean test. Guard and Dodge Roll still need their
  native abilities; the new aerial pose needs no additional native ability.
- Recheck Fire/Thunder/Cure and LEFT-hand effects. Turn all Aqua entries off
  and check Sora's native poses/controls. Repeat on both saves, after room
  transitions and after save reloads.

RETURN
Return the NEW kh1-aqua.log beside the game EXE and a short video. Its first
line must say ANIMATION TEST v11 Test 3. AIR DODGE READY confirms control-hook
admission; AIR DODGE 504 confirms the input trigger. AIR DODGE UNAVAILABLE
leaves other Aqua poses available and retains native air input.
Profile log values: 0 native, 1 aqua, 2 aqua 1, 3 aqua 2, 4 aqua 3, 5 aqua 4.
CHECK_AQUA_V11.cmd optionally checks installation hashes and writes
Aqua_Animation_Check_v11.txt.

SCOPE / RETAINED FEATURES
Both installed MSETs are original. Runtime body poses fit their existing
headers, table sizes, bone counts and eleven helpers. The aerial pose is a
second body variant for the existing fall record, not an added native record.
Unknown/foreign motion tables block writes. Hair rest rotations and anatomical
wrist/forearm alignment corrections are retained. Only the supplied normal
Sora and Olympus banks are admitted. Native damage, hit events, spell scripts,
MP, targeting, Guard coverage, Dodge Roll invincibility and actor travel remain.
BBS command logic, effects, damage and hitboxes are not imported with a clip.

SHARED CASTING FROM V10
Thunder and Cure normally share a native physical cast record. The existing
actor-local request copy routes Thunder to a separate casting family. Blizzard
and Gravity inherit317/390; Stop and Aero inherit318/427. Thunder uses 86 ground
and 78 air frames instead of 68/68. This inherited timing still needs in-game
verification. Fire's release/recovery follows continuous portions of316/391.
Unequipping Aqua restores the exact original request lookup and mapped poses.

FILE GUIDE
ABILITY_SETS.txt gives the exact Test 3 sequences.
ANIMATION_MAP.csv lists all five profiles' usual motion assignments.
AIR_DODGE_MAPPING.csv describes the temporary 504 overlay for each profile.
TEST_CLIP_SOURCES.csv gives new source banks, frame counts and payload hashes.
411 uses the dedicated p02ex_313.arc variant; 504 uses p02ex_157.arc. Numeric
labels are not assumed to be official BBS command names.
The unchanged 349-clip source inventory remains under inventory. Use this
package's mapping CSVs for current ability assignments.

OPTIONAL FALLBACKS
To disable only the new airborne input action, copy
DISABLE_AIR_DODGE_kh1-aqua.ini beside the EXE as kh1-aqua.ini and restart.
The411 finisher, Test 3 combos, normal506 fall and left-hand magic remain.
To retain native weapon-tip spell attachments, use
DISABLE_HAND_MAGIC_kh1-aqua.ini instead. You can combine air_dodge=0 and
hand_magic=0 in one [aqua] INI. Remove the INI and restart to restore defaults.

REMOVE ALL AQUA ENTRIES
Copy REMOVE_AQUA_kh1-aqua.ini beside the game EXE as kh1-aqua.ini. Leave v11
installed, restart and load each save to clean. Check AQUA ABILITIES REMOVED,
then save in-game. Exit, remove the INI, disable v11 and rebuild. Only ids117..121
are removed; native ability order is preserved.

VALIDATION
49 tests execute the emitted PE DLL in a Win64 ABI mock host, including the
real control-entry detour and relocated-cookie trampoline, neutral/held/
directional inputs, one use per airtime, native queueing, interruptions,
lookup/body/input restoration, all five profiles/both banks, foreign-data and
allocation/admission failures. 13 geometry/assignment checks cover all76 pose
variants, exact Test 3 IDs, original capacities, bind lengths/scales, hair,
wrist helpers, native travel and retained jump/Fire transitions.
Clip616 fills the first air attack's available key pool; its fitted maximum
position error remains below the existing5-unit limit. No capacity expansion
or relaxed fit limit is used.
These checks do not run Windows/KH1 or render Sora's mesh. The new control
hook and aerial pose timing need an in-game test; clipping or pose transitions
may still need adjustment.
