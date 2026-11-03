KH1FM TERRA ANIMATION TEST v2 -- STANDALONE
KH1FM Steam Global / OpenKH Panacea

INSTALL
1. Close KH1. Disable Terra v1, standalone Aqua, Dual Wield/Nine Styles,
   other moveset DLLs and the full KH2 Combat overhaul.
2. Import this ZIP into OpenKH Mods Manager, then Build and Run.
3. Load a save and stand idle. Equip terra in the abilities menu.
4. Check for TERRA ANIMATION TEST v2 in kh1-terra.log beside the game EXE.
   DLL updates require a restart; F1 does not reload a DLL.

WHAT v2 FIXES
The supplied v1 log stopped at TERRA ABILITY SLOTS FULL. v1 required room for
all eleven entries before adding the main ability. v2 prioritizes terra and
shows as many numbered tests as fit, using pages when necessary.

Only custom IDs 116..126 are compacted or replaced. Existing learned native
abilities, their copies, equipped flags and AP are preserved. Unknown custom
entries outside that range are preserved too. A zero tail byte is retained
because native ability readers scan to a terminator. The list is not enlarged.
Saved Aqua/Style entries in this private range are reused and initially OFF.
All visible Terra entries cost 0 AP; equipping one disables the other Terra
entries. Page installation waits for idle. Stand idle to finish a switch.

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

MAIN PROFILE AND TEN TESTS
Main ground: 300 -> 301 -> 303. Main air: 305 -> 306 -> 307.
Includes Terra idle/combat idle, walk/run, jump/fall/landing, ledges,
Guard 400, Dodge Roll/Slide 009, items 600/601 and casting 354/355/320.
TERRA_ANIMATION_MAP.txt lists all eleven profiles and common mappings.
TERRA_MOVE_INVENTORY.csv lists 137 source variants, frame counts, FPS,
source banks and hashes. Numeric labels are original BBS IDs; official
command names have not been verified. Test 8 uses clip 519 from p03ex_511.arc.

COMBAT AND VISUAL SCOPE
Animation poses and fitting are unchanged from Terra v1. KH1 retains input,
combo progression, hit/chain timing, collision, Guard defense, spell/item
logic and keyblade-tip effects. Equip native Guard and Dodge Roll to use them.
Unequip Slapshot/Vortex and similar attack abilities to isolate basic combos.
Test poses do not import their BBS commands, hit events or projectiles.
Glide, Superglide, jump height and damage/knockback reactions remain native.
The mod retains Sora's model, native limb lengths, hair, outfit, stats and
equipped keyblade. No Aqua poses or Dual Wield controller are imported.

TEST AND REPORT
Test main ground/air combos, movement, Guard, Roll, numbered entries and
unequipping. Check normal/Olympus saves and room changes. For issues, send
the new kh1-terra.log and a short video showing the selected ability/action.
The new log identifies slot occupancy as well as profile and motion admission.

VALIDATION
39 checks execute the actual v2 PE DLL under a Win64 ABI/API mock. They cover
near-full saves, legacy styles, all pages, duplicate native abilities, native
zero-terminated counting, config overrides, idle setup, restoration, both
banks and all eleven profiles. No actual Windows/game run is claimed for v2.
All v1 fitted motion inputs and the generated motion header are byte-identical:
107 records retain the existing 13 geometry checks and fitting validation.
A clean exported-source rebuild must reproduce the delivered DLL exactly.

UNINSTALL / RETURN TO OTHER MODS
Set remove_terra=1 in kh1-terra.ini beside the game EXE. Launch/load, stand
idle and save, then close KH1, disable Terra and Build again. This removes
only custom IDs 116..126; native learned abilities and AP remain intact.
Remove mode takes priority over page and profile override settings.
