KH1FM TERRA ANIMATION TEST v3 -- STANDALONE
KH1FM Steam Global / OpenKH Panacea

INSTALL
1. Close KH1. Disable Terra v1/v2, standalone Aqua, Dual Wield/Nine Styles,
   other moveset DLLs and the full KH2 Combat overhaul.
2. Import this ZIP into OpenKH Mods Manager, then Build and Run.
3. Load your save, stand idle, then equip terra. All Terra entries cost 0 AP.
4. Confirm TERRA ANIMATION TEST v3 in kh1-terra.log beside the game EXE.
   Restart for DLL updates; F1 cannot reload a DLL.

MAIN TERRA CHANGES
Ground combo: 300 -> 411 -> 332 (both native second-hit variants use 411).
Air combo: 305 -> 306 -> 353.
Ground Fire, Blizzard and Gravity: 315.
Air Fire, Blizzard and Gravity: 316.
The requested casts use matching recovery tails from the same source clip.
Thunder, Cure, Aero and Stop retain their v2 cast poses. Native spell release
events, projectiles, MP costs, hit logic and keyblade-tip effects are retained.

SINGLE-TAP SUPERGLIDE REPLACEMENT
With main terra active and native Superglide enabled, tap your normal
Superglide button (Square by default) in the air. Terra's current ground
Slide/Dodge Roll source animation 009 plays as a finite aerial slide.
Holding the button does not extend it; release does not shorten it.
The move takes the stick direction at the tap, or character facing with a
neutral stick. It travels horizontally for the animation, then returns to
normal falling. Native Superglide's height threshold is retained (above 50
native units); attack, spell, scripted-action and shortcut conflicts reject it.
Native collision handles walls/floors. No damage protection or extra hitbox
is granted. A new tap after completion can start another slide when eligible.
Ordinary Glide remains usable. This replaces main Superglide only.

TEN NUMBERED TESTS AND SHARED ACTIONS
terra 1..10 retain their v2 combos, casts and native Superglide controls.
All profiles retain the existing idle/walk/run/jump/fall/ledge animations,
Guard400, ground Roll/Slide009 and items600/601. Damage reactions stay native.
TERRA_ANIMATION_MAP.txt gives all eleven profiles. TERRA_MOVE_INVENTORY.csv
lists 137 source variants with original frame counts, FPS, banks and hashes.
Native attack abilities keep their priority. Unequip Slapshot/Vortex and
similar abilities to isolate basic combos. KH1 combo/hit timing is retained.
Finish the action and stand idle before switching or unequipping profiles.

ABILITY STORAGE
v2's main-first setup and adaptive pages are retained. Only custom IDs
116..126 are compacted/replaced; native/foreign ability copies, equipped flags
and AP are preserved. One zero tail byte remains for native list readers.
Missing/reused custom entries initially start OFF. No native entry is evicted.

NUMBERED TEST PAGES
If there is room, terra and terra 1..10 all appear together.
Otherwise, terra appears on every page and the ten tests span several pages.
The log reports the current page, page count and first/last visible test in
ordinary decimal numbers. For example, with 37 other learned entries:
  Page 1: terra plus terra 1..9
  Page 2: terra plus terra 10
To change pages, copy kh1-terra.ini.example beside KINGDOM HEARTS FINAL MIX.exe,
rename it kh1-terra.ini, set test_page=2 (or the page listed in the log), and
restart KH1. Return to test_page=1 for the first page. Paging only affects
which custom test entries appear; all eleven animation profiles are included.
The number of tests per page depends on the save, not on the animation bank.

IF EVEN THE MAIN ABILITY HAS NO ROOM
No learned native entry is removed. To test without needing another slot,
use the same INI beside the game EXE and choose profile_override:
  0 = normal ability-menu selection (default)
  1 = main terra
  2 = terra 1, 3 = terra 2, ... 11 = terra 10
Restart after changing it. While nonzero, this setting controls the profile
instead of the equipped Terra ability. Set it back to 0 to use abilities.
If only terra fits, the override also makes the numbered tests accessible.

TEST AND REPORT
Check the new main ground/air combos and all six requested ground/air casts.
Test a Superglide tap, release, holding, neutral/directional stick, landing,
walls, damage interruption and ordinary Glide. Then switch to a numbered
ability and unequip to verify restoration. Try normal/Olympus saves and a
room change. Send kh1-terra.log and a short video for visual/timing issues.

VALIDATION
57 tests execute the actual v3 PE DLL under a Win64 ABI/API mock. They cover
all profiles/banks, native ability preservation/pages, spell recovery,
tap/hold/release, finite travel, input conflicts, interruptions, zero-time
pause, model unloads, native-event preservation and failed-hook rollback.
13 geometry checks pass over 114 serialized fits. The exported source
rebuild reproduces the delivered DLL exactly. Live Windows/gameplay testing
is still required. All poses come from the original Terra source capture.

UNINSTALL / RETURN TO OTHER MODS
Set remove_terra=1 in kh1-terra.ini beside the game EXE. Launch/load, stand
idle and save, then close KH1, disable Terra and Build again. Only custom
IDs116..126 are removed. Remove mode overrides page/profile selection.
