KH1FM AQUA ANIMATION TEST v12 - TEST 4
Steam Global / OpenKH Panacea

MAIN AQUA
- Air combo: 407, 352, 353 (first, second, finisher).
- Aerial dodge: 504 on a fresh Circle press while jumping/falling, with either
  neutral or directional left-stick input. The previous neutral-stick gate
  is removed. Release the takeoff button, then press Circle again in the air.
  It remains once per airtime; landing rearms it. Numbered entries inherit it.
- Ground finisher411, normal falling506, Fire316/391, Thunder317/390,
  Cure318/427, LEFT-hand spell origins/glow and wrist/hair corrections remain.

TEST 4 ABILITIES - ALL 0 AP
aqua   : main ground combo300/301/302/411; air407/352/353; airborne504
aqua 1 : ground622 623 045 ; air220 221 351
aqua 2 : ground353 399 411 ; air413 710 711
aqua 3 : ground060 022 023 ; air025 026 052
aqua 4 : ground701 700 708 ; air007 / 395, 008 / 051, 060 / 505

The slash pairs are aliases for identical animation data, not alternate picks.
The shared versions are selected as395 (29 source frames),051 (16 frames),
and505 (30 frames). These are distinct from the ordinary007/008 base clips.
Plain60 in aqua3 uses the separate40-frame060 from p02ex_711.arc. The4th air
finisher060 /505 uses the30-frame shared payload. Source hashes and exact
banks are recorded in TEST_CLIP_SOURCES.csv and source/source_selections.json.

Each triplet is attack one, attack two, finisher. KH1's alternate second ground
attack uses the selected second clip too. Numbered entries share the main
movement/casting/reaction/Guard/Cartwheel poses; only their combos differ.
Select one Aqua entry while idle; the other Aqua entries turn off. Native
ability states and ids117..121 are retained, including saved selections.

INSTALL
1. Fully close KH1.
2. Disable Aqua v11 and all older Aqua packages, Sora Restore Check and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH and enable Aqua Animation Test v12.
4. Build and Run, then load your save.
5. Equip aqua or one of aqua1..4 while idle. Missing entries are granted off;
   saved selections are respected. Native entries are never evicted to fit.

TEST ORDER
- Equip aqua and test the407/352/353 air combo. Its ground finisher stays411.
- Jump, release Circle, then tap Circle again. Check504 with no stick input,
  while moving forward/back/left/right and while moving diagonally. Land to
  rearm between tests. The native direction vector is passed through unchanged.
- Check return to506 falling, landing and interruption by attacking/casting.
- Equip aqua1..4 while idle; test their ground and air triplets. For a clean
  test, unequip Slapshot, Sliding Dash, Vortex, Hurricane Blast and other
  native combo replacements. Their separate actions keep their native poses.
- Recheck spells and LEFT-hand effects, both saves, room transitions/reloads,
  then turn every Aqua entry off and check native Sora controls and poses.

AERIAL DODGE SCOPE
This remains an animation test using the existing40-frame fall record.
504 plays once, then restores506. It keeps native air steering, gravity,
velocity and collisions; no BBS dash/boost, hitbox or invulnerability is added.
A held takeoff button does not retrigger it. Attacks/casts/reactions, ledges,
scene/menu/shortcut input and other busy actions do not start it. Guard and
Dodge Roll still need their native abilities;504 needs no extra native ability.
A fresh moving-air Circle now takes the504 route too. If you keep Circle held
past the pose, KH1 may then enter its native Glide. Glide's poses stay native.

RETURN
Return the NEW kh1-aqua.log beside the game EXE and a short video. Its first
line must say ANIMATION TEST v12 Test 4. AIR DODGE READY confirms hook admission;
AIR DODGE504 confirms a trigger with neutral or directional input. If it says
AIR DODGE UNAVAILABLE, other Aqua poses remain available with native air input.
Profile values:0 native,1 aqua,2 aqua1,3 aqua2,4 aqua3,5 aqua4.
CHECK_AQUA_V12.cmd optionally checks installation hashes and writes
Aqua_Animation_Check_v12.txt.

LAYOUT / CASTING
Both installed MSETs are original. All generated poses keep native headers,
lengths, table allocations, bone counts, eleven helpers and native travel.
Unknown/foreign motion data or request tables block writes. Only the supplied
normal Sora and Olympus banks are admitted. KH1 damage, native hit events,
spell scripts/MP/targeting, Guard coverage and Dodge Roll windows remain.
BBS command logic/effects/damage are not imported with these source clips.
Thunder retains v10's separated casting lookup and86 ground/78 air frames
rather than68/68. Blizzard/Gravity share317/390; Stop/Aero318/427. That inherited
cast timing still needs an in-game check. Unequipping restores native lookup
pointers and mapped body records when the current action finishes at idle.

FILE GUIDE
ABILITY_SETS.txt lists Test4 sequences.
ANIMATION_MAP.csv lists the usual motions for all five profiles.
AIR_DODGE_MAPPING.csv lists the temporary504 action and input rule.
TEST_CLIP_SOURCES.csv lists main combo/dodge and Test4 sources, frame counts,
aliases and payload hashes; source/source_selections.json records inventory choices.
The unchanged349-clip inventory is under inventory. Current assignments are
in this package's mapping files. Numeric IDs are not official command names.

OPTIONAL FALLBACKS
To disable only the airborne Circle action, copy
DISABLE_AIR_DODGE_kh1-aqua.ini beside the EXE as kh1-aqua.ini and restart.
The main air combo, ground finisher, Test4 sets, fall506 and magic remain.
To retain native weapon-tip spell attachments, use
DISABLE_HAND_MAGIC_kh1-aqua.ini instead. Combine air_dodge=0 and hand_magic=0
in one [aqua] INI if needed. Remove the INI and restart to restore defaults.

REMOVE ALL AQUA ENTRIES
Copy REMOVE_AQUA_kh1-aqua.ini beside the EXE as kh1-aqua.ini. Leave v12 enabled,
restart and load each save to clean. Check AQUA ABILITIES REMOVED, then save
in-game. Exit, remove the INI, disable v12 and rebuild. Only ids117..121 are
removed; native ability order stays intact.

VALIDATION
50 tests execute the emitted PE DLL in a Win64 ABI mock host. They cover
neutral/directional Circle, unchanged direction/input data, one use per airtime,
held-button and busy-action exclusions, interruptions, body/lookup restoration,
all five profiles/both banks, native detours/trampolines and failure paths.
14 geometry/assignment tests cover all76 pose variants, exact Test4 triplets,
slash-alias hashes and distinct plain060, native capacities/travel, bind lengths
and scales, hair, wrists and retained jump/Fire transitions. All fits remain
below the existing5-unit position-error limit; no capacity expansion is used.
These checks do not run Windows/KH1 or render Sora's mesh. The directional
Circle route, new clips and final pose/FX appearance need in-game testing.
