KH1FM TERRA ANIMATION TEST v1 -- STANDALONE
Steam Global / OpenKH Panacea

INSTALL
1. Close KH1. Disable Dual Wield/Nine Styles, standalone Aqua, older moveset
   DLLs and the full KH2 Combat overhaul. Enable this separate Terra test.
2. Import this ZIP into OpenKH Mods Manager, then Build and Run.
3. Load a save, stand idle and equip terra. Missing entries start unequipped.
   Ten numbered test entries are terra 1 through terra 10; all cost0 AP.
4. Confirm TERRA ANIMATION TEST v1 in kh1-terra.log beside the game EXE.
   Restart for DLL changes; F1 cannot reload a DLL.

MAIN PROFILE
Ground300 ->301 ->303; air305 ->306 ->307.
Both native second-ground variants use301.
Includes Terra idle/combat idle, walk/run, jump/fall/landing, ledges,
Guard400, Dodge Roll/Slide009, items600/601 and casting354/355/320.
Terra's original51-bone skeleton is mapped by original bone names to Sora's
293-bone model. Limb lengths/scales, skinned skull150 and hair shape retain
native Sora anatomy. Sora's outfit, stats and equipped keyblade remain.

TEN TESTS
Each numbered ability selects three ground and three air source animations.
TERRA_ANIMATION_MAP.txt lists all11 profiles. TERRA_MOVE_INVENTORY.csv lists
137 source variants with frame counts, FPS, banks and hashes. Numeric labels
are original BBS source IDs; official command names remain unverified.
Clip519 has two original variants; terra8 uses p03ex_511.arc.

CONTROLS AND TIMING
KH1 retains input, native combo progression/hit/chain timing, collision,
Guard defense, magic/item logic and keyblade-tip effects. Equip native Guard
and Dodge Roll to use those actions. Native attack abilities such as
Slapshot/Vortex retain priority; unequip them to isolate the basic combos.
Combo Plus can extend the native chain. Test poses do not add their BBS
commands, extra hit events, projectiles or invulnerability.
Glide, Superglide, jump height and damage/knockback reactions remain original.
Aqua's custom aerial dodge, jump boost and all-angle Barrier are not imported.
Finish the current action and stand idle before switching/unequipping.

ABILITY STORAGE
Testing IDs116..126 reuse the private prototype range, including older
Aqua/Style entries. First setup leaves reused custom tests unequipped.
The65 native ability records, AP and native equipped flags are untouched.
No native ability is evicted if the48-byte list lacks room. If the log says
TERRA ABILITY SLOTS FULL, remove obsolete test entries using their original
mod's uninstall mode before retrying. Do not edit saves manually.

FIRST PLAYTEST
Check idle/run, jump/fall, ground/air combos, Guard and Dodge Roll. Try
numbered entries, then unequip to verify original Sora restoration. Repeat
with normal/Olympus saves and a room change. Send kh1-terra.log and a short
video for visual or timing issues. Some test clips are spells or movement.

VALIDATION
107 fitted records pass existing quality limits over23,127 fractional-frame
samples.27 actual-PE runtime checks plus13 geometry checks pass, including
all11 profiles/both banks, unchanged native headers/events/travel, restoration,
full ability lists, stale-pointer rejection and conflicting DLL admission.
These are offline checks; actual Windows loading and gameplay are untested.
Original Terra sources were used; no Aqua pose is substituted.

UNINSTALL / RETURN TO OTHER MODS
Create kh1-terra.ini beside the game EXE with:
[terra]
remove_terra=1
Launch/load, stand idle and save, then close the game, disable Terra and Build
again. Only custom IDs116..126 are removed; native abilities are retained.
