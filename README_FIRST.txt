KH1FM AQUA ANIMATION TEST v9
Steam Global / OpenKH Panacea

FIVE ABILITIES, ALL 0 AP
aqua   : original Aqua combo set, with corrected wrist pivots/arm clearance
aqua 1 : ground 045 217 218 ; air 332 357 361
aqua 2 : ground 362 363 350 ; air 365 366 370
aqua 3 : ground 370 371 372 ; air 373 506 315
aqua 4 : ground 316 317 318 ; air 391 390 427

These are alternatives. Each includes the common Aqua movement, jumps,
casting poses, items, reactions, Guard and Cartwheel. Selecting a new Aqua
entry unequips the other Aqua entries. Native abilities retain their states.
Unequipping the selected Aqua entry restores the original mapped Sora motions.
Change selections while idle; an active action finishes before the data switch.
The first slot is the first attack, the second is the second attack, and the
third is the finisher. KH1's alternate second ground attack uses that same
second source clip, so it stays within your selected three-animation set.

V9 CORRECTIONS
- Moved hand bending to Sora's anatomical hand pivots. Distal forearm helpers
  now follow the forearm rather than rotating with the hand; this targets the
  combat-idle wrist/cuff separation and applies across all five profiles.
- Strengthened arm clearance during the original ground and air finishers,
  including tests of the upper-arm and forearm interiors against the torso.
  Segment lengths, local attachment offsets and scales remain unchanged.
- Moved the working native spell-origin and glow/effect-matrix route to the
  LEFT palm (the other hand from v8). It applies to all five Aqua profiles.
- Kept the corrected hair rest rotations from v8.

INSTALL
1. Fully close KH1.
2. Disable Aqua v8 and all older Aqua packages, Sora Restore Check, and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH and enable Aqua Animation Test v9.
4. Build and Run. Load your save. Missing Aqua entries are added unequipped;
   a previously saved selection is respected. Existing native entries are not
   evicted. If the ability list lacks room, the log reports the missing space.
5. Select aqua or aqua 1..4 in Abilities while standing idle. You do not need
   to equip the original aqua entry along with one of the numbered entries.

TEST
- First use aqua to compare combat idle from front/side and the original
  ground finisher. Check forearm-to-hand alignment and arms crossing the body.
- Cast ground/air spells and confirm launch points and attached glow use the
  LEFT hand. Recheck a spell with all Aqua entries off for native behavior.
- Select aqua 1, then 2, 3 and 4 while idle. Test three-hit ground and air
  combos with each. For a clean test, unequip Slapshot, Sliding Dash, Vortex,
  Hurricane Blast and other native combo replacements. Their unassigned
  actions otherwise retain their native animations. Guard and Dodge Roll
  still need their native abilities equipped.
- Repeat on your other save, after a room transition and after a save reload.

RETURN
Return the NEW kh1-aqua.log beside the game EXE and a short comparison video.
Its first line must say ANIMATION TEST v9. The log records 0x2F normal / 0x2E
Olympus records and profile 0=native, 1=aqua, 2=aqua 1, 3=aqua 2, 4=aqua 3,
5=aqua 4. Hand queries log AQUA HAND MAGIC ORIGIN / MATRIX with the native
request number. CHECK_AQUA_V9.cmd optionally checks installation hashes and
writes Aqua_Animation_Check_v9.txt.

SCOPE AND TIMING
The selected source clips are resampled to the existing KH1 action durations.
This tests animations. Native KH1 hit events, damage, spell simulation, MP,
projectile trajectories, targeting, guard coverage, dodge invincibility and
actor travel remain in use. The native weapon-attachment position/matrix
queries are redirected to the left hand during eligible Aqua casts.
Source animations do not bring their BBS commands, projectiles or effects into
the combo. Guard is still the Barrier pose with KH1 Guard behavior.

Both installed MSET files are your original files. In-memory poses fit within
their existing tables; headers, lengths, counts and eleven helpers retain the
original layout. Current foreign/unknown records block body writes. Other
Sora costume/forms banks are not admitted by this test.

FILE GUIDE
ABILITY_SETS.txt lists the five abilities and exact numeric selections.
ANIMATION_MAP.csv lists all five profiles' effective motion assignments.
TEST_CLIP_SOURCES.csv gives source banks, frame counts, hashes and fitted slots.
REMAINING_NATIVE.csv lists unassigned native records.
The earlier 349-clip source inventory CSV/JSON is included under inventory;
use this package's ANIMATION_MAP.csv for the current ability assignments.
045 uses p02ex_004.arc; 370 uses p02ex_133.arc. Numbered source labels are not
assumed to be official BBS command names.

OPTIONAL NATIVE-MAGIC FALLBACK
To test the v9 poses with native spell attachments, copy
DISABLE_HAND_MAGIC_kh1-aqua.ini beside the game EXE as kh1-aqua.ini and restart.
Remove that INI and restart to restore left-hand routing.

SAVE / REMOVE ALL AQUA ENTRIES
Saving in-game may retain ids117..121. To remove all five, copy
REMOVE_AQUA_kh1-aqua.ini beside the game EXE as kh1-aqua.ini, leave v9 enabled,
restart and load each save to clean. Check AQUA ABILITIES REMOVED, then save
in-game. Exit, remove the INI, disable v9 and rebuild. Native ability order
is preserved; only these five test ids are removed.

VALIDATION
34 tests execute the compiled PE DLL in a Win64 ABI mock host. They include
all five selections in both banks, exclusivity, save/reload behavior, removal,
exact restoration and the distinct left-palm attachment route.
12 independent geometry tests cover all 75 generated records, including the
forearm helper angles, source capacities, hair rest shape, unit skin bases,
native travel and transitions. The original finisher's joint/capsule overlap
is substantially reduced. These checks do not render Sora's mesh or execute
Windows/KH1. The final idle/finisher appearance and left-hand FX need your
in-game comparison; some clipping may still need adjustment.
