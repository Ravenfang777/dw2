KH1FM TERRA ANIMATION TEST v4 -- STANDALONE
KH1FM Steam Global / OpenKH Panacea

INSTALL
1. Close KH1. Disable earlier Terra versions, standalone Aqua, Dual Wield/
   Nine Styles, other moveset DLLs and the full KH2 Combat overhaul.
2. Import this ZIP into OpenKH Mods Manager, then Build and Run.
3. Load your save, stand idle and equip terra. All Terra entries cost 0 AP.
4. Confirm TERRA ANIMATION TEST v4 in kh1-terra.log beside the game EXE.
   DLL changes require a full restart; F1 cannot reload a DLL.

HEAD POSE
Idle001 and combat idle002 tilt the whole head UP15 degrees. The correction
uses actual skinned skull150, so the face and hair follow together. Hair's
local bind shape, neck/limb lengths and scales are retained. These two shared
idle-pose changes apply to all Terra profiles; other actions are not tilted.

MAIN TERRA ANIMATIONS
Ground combo300 ->411 ->332; air305 ->306 ->353 (unchanged from v3).
Guard354: the former grounded Cure animation, fitted into the Guard slot.
Cure/Thunder/Aero/Stop: ground317, air318, with matching recovery tails.
Fire/Blizzard/Gravity retain ground315, air316 and their recovery tails.
Item use399 on both ground and air.
Native Guard and Dodge Roll abilities are still required for ground actions.
Guard's native defense rules/timing, spell effects/MP costs, item logic,
native combo/hit timing and keyblade-tip origins are preserved.

SQUARE AIR DASH FIX
With main terra active, tap Square in the air while free to act. The move
uses the same source009 as Terra's ground Slide/Dodge Roll replacement.
It locks the left-stick direction at the tap, or uses character facing if
the stick is neutral. Release does not shorten it; holding cannot extend
or repeat it. A fresh press after completion can start a new eligible dash.
No shared Superglide ability is needed. Native Superglide's old height50
threshold and legacy cooldown do not restrict this main-Terra move. Sora
must be airborne and clear of the floor. Attacks, casts, scripted actions
and incompatible queued actions retain priority. Native collision handles
walls/floors; no invulnerability, hitbox or direct actor-position write is added.
The v3 log showed the held-input mask0x00140000 check rejecting legitimate
Square presses as bit0x40. v4 removes that false modifier check and keeps
native command/queue checks. Rejected airborne attempts now log input and
action details. Successful starts log TERRA AIR DASH009.
Ordinary Glide remains usable. Held native Superglide stays replaced in main.

NUMBERED TESTS
terra 1..10 keep their v3 combos, Guard400, casts354/355/320, items600/601
and native Superglide. They receive only the shared idle head correction.
TERRA_ANIMATION_MAP.txt lists all assignments. TERRA_MOVE_INVENTORY.csv lists
137 original source variants, frame counts, FPS, banks and hashes.
Unequip Slapshot/Vortex and similar attack abilities to isolate basic combos.
Finish the current action and stand idle when switching/unequipping profiles.
Damage/knockback reactions and native jump height remain original.

ABILITY STORAGE
Main-first setup/adaptive pages are retained. Only custom IDs116..126 are
compacted/replaced. Native/foreign copies, equipped flags and AP are retained,
and one zero tail byte remains for native list readers. Missing custom entries
start OFF. No native learned ability is evicted to create space.

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
Check idle/combat idle head position, new Guard, all four changed spell
families on ground/air and both item poses. Jump, hold the stick and tap
Square. Also test release/holding, neutral stick, ordinary Glide, landing,
walls, damage interruption, switching and room changes in normal/Olympus.
Send the new kh1-terra.log and a short video if a pose or input still fails.

VALIDATION
59 checks execute the actual v4 PE DLL under a Linux Win64 ABI/API mock.
They include the reported high-bit Square rejection, direct main-ability
dash, no shared Superglide prerequisite, finite directional travel, native
spell/attack priority, restoration, ability pages and both motion banks.
14 geometry checks pass over121 fits, including a direct 15-degree skull
comparison and unchanged hair binds, lengths, scales and event payloads.
A clean exported-source rebuild must reproduce the delivered DLL exactly.
Live Windows/gameplay testing is still required for v4.

UNINSTALL / RETURN TO OTHER MODS
Set remove_terra=1 in kh1-terra.ini beside the game EXE. Launch/load, stand
idle and save, then close KH1, disable Terra and Build again. Only custom
IDs116..126 are removed. Remove mode overrides page/profile selection.
