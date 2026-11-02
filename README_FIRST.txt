KH1FM AQUA ANIMATION TEST v7
Steam Global / OpenKH Panacea

ABILITY: aqua (lowercase), 0 AP, id117
Equip aqua while standing idle to select the Aqua animations. Unequip it while
idle to restore the original animations. A saved aqua selection is respected.

CHANGES FROM V6
- Corrected 62 inherited rest transforms, including cloth/attachment offsets.
  Anatomical and clothing offsets use Sora's own bind positions. The checked
  native weapon grip and face/finger turns are retained.
- Widened supported foot stances to allow room for Sora's larger boots, using
  a leg solve that preserves segment lengths and scales.
- Removed the return toward Sora's stance inside each Aqua attack. Aqua idle,
  movement and combat now share the same retarget calibration.
- Closed pose loops and split takeoff/rise so the airborne animation continues
  instead of restarting the jump. Falling uses Aqua's airborne loop.
- Anchored Aqua's raised LEFT ledge hand at Sora's native grip point.
- Reduced repeated memory queries by checking shared loaded ranges together.

ANIMATIONS INCLUDED
47 motion records on normal Sora; 46 on Olympus. One ledge recovery exists only
in the normal bank. This adds 38 records beyond the nine tested in v6:
  Regular/combat idle, walking and running variants
  Jump, high jump, rise, falling and landing
  Ledge hang, climb and recovery
  Shared ground/air casting poses and cast recoveries
  Ground/air item use and front/back/heavy/air damage reactions
  Corrected ground/air combos, Barrier pose and Cartwheel from v6

ANIMATION_MAP.csv gives every native slot, Aqua clip and source range. Casting
uses shared visual assignments; separate BBS choreography for each individual
spell has not been implemented. REMAINING_NATIVE.csv lists every unassigned
native record, including Sora-specific attack abilities, special actions and
field/mobility actions without a reviewed Aqua assignment.

INSTALL
1. Fully close KH1.
2. Disable all earlier Aqua packages v1-v6, Sora Restore Check v3, and Nine
   Styles / Dual Wield v52. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH and enable Aqua Animation Test v7.
4. Build and Run. Load the Olympus or Traverse Town save.
5. Open Abilities and select aqua. Change its selection while standing idle.
   Guard and Dodge Roll still need their own native abilities equipped.

TEST
First compare aqua OFF / ON / OFF while idle, walking, running, jumping,
landing, using basic ground/air combos, Guard and Dodge Roll. For ordinary
combo testing, unequip Slapshot, Sliding Dash, Vortex, Hurricane Blast and
other attack replacements; their unassigned native actions remain original.
Use Combo Master if needed for combos while striking empty air.

Then try ledge hanging/climbing, ground/air spells, item use and receiving a
normal hit. Repeat on the other save. Switch aqua while idle and allow the
current action to finish. Compare visible arm/leg/waist deformation, boot
spacing, transition pops and ledge contact.

RETURN
A short comparison video and the NEW kh1-aqua.log beside the game EXE. Its
first line must say AQUA ANIMATION TEST v7. Successful selection logs AQUA
MOTIONS ENABLED, the bank and verified motion count (0x2F normal / 0x2E Olympus).
Turning aqua off logs AQUA MOTIONS DISABLED. If a change is missing, return
the log unchanged. CHECK_AQUA_V7.cmd is an optional read-only file check after
extracting the ZIP and building; it writes Aqua_Animation_Check_v7.txt.

WHAT THIS TEST CHANGES
This is a body-animation replacement. KH1 retains action selection, durations,
actor travel, hitboxes, hit timing, damage, spell/item effects, guard coverage,
dodge invincibility and sounds. Barrier remains a pose with native Guard
behavior; Cartwheel uses the native Dodge Roll movement/window.

Both installed MSETs are your original files. After validating the complete
active bank, the DLL reuses existing in-memory tables and key capacity. File
sizes, motion headers/counts and eleven helper slots are preserved; the native
travel helper and ancestor tracks stay intact. Unknown or changed records
block body writes. Other Sora forms/costume banks are not admitted by this test.

SAVE / REMOVE AQUA
You can compare without saving. Saving in-game may retain ability id117.
To remove it later, place REMOVE_AQUA_kh1-aqua.ini beside the game EXE, renamed
kh1-aqua.ini. Leave v7 enabled, restart, load each save to clean and check for
AQUA ABILITY REMOVED. Save in-game to retain removal. Exit, remove the INI,
disable v7 and rebuild. Only id117 is removed; other ability order is retained.

VALIDATION
10,427 quarter-frame pose checks passed across the 47 motion records, with
zero non-root anatomical/clothing offset or scale error in the offline data.
Eight independent geometry/transition checks passed, including loop closure,
jump phase continuity, boot spacing, ledge-hand alignment and native travel.
Twenty-two checks executed the compiled PE DLL in a mock Win64 host, covering
both banks, exact ON/OFF restoration, bank reloads, fragmented table pointers,
uninstall, unknown data and the reduced query count.

These checks do not execute Windows or KH1 or render Sora's mesh. The changes
target the stretching and visual issues; their in-game appearance needs your
comparison. Your v6 result established that the previous body approach works.
