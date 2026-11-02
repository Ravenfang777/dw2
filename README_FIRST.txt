KH1FM AQUA ANIMATION TEST v15
Steam Global / OpenKH Panacea

MAIN AQUA
Ground combo:300 ->365 ->366.
Air combo:351 ->352 ->393 (second air hit changed to352).
Blizzard/Blizzara/Blizzaga now use Fire's current animation:391 ground,316 air,
including Fire's recovery phase. The spell remains Blizzard: native MP,
element, projectiles, target and spell logic are retained.
Fire391/316, Cure427/318 and Stop/Aero317/390 retain v14's assignments.

MAGIC ORIGIN / EFFECTS
All Aqua profiles use native keyblade-tip spell origins and effect matrices.
No palm-redirection hooks are installed. Older hand_magic INI settings are
ignored in this build. Item007/395, falling506 and other spell logic remain.

GLIDE
Keep Aqua350 opening source0..20 during the first40 native frames. At frame40,
restore all four ORIGINAL Sora Glide motion bodies and resume their original
clock, steering and looping. Native release into fall6 retains Aqua350's
closing source20..40, then returns to506. Glide's normal ability, held-input,
state, movement, descent and collision requirements remain; it is not granted.

AERIAL DODGE504
The v14 log shows504 being accepted, followed immediately by native Glide71.
Native movement can enter Glide later using cached selection flags after the
input callback returns, beyond the scope of its temporary pad mask.
V15 adds a checked hook at the native regular-Glide constructor. While504 owns
the fall pose, that deferred Glide entry is suppressed for the verified Sora
actor. After504 ends, native Glide passes through normally. Both the control
and Glide entries verify before either is patched; failed admission retains
native controls. Tests exercise the deferred call after control returns.

Jump, release Circle, then press it again airborne. Neutral and directional
stick input are allowed. One504 per airtime; land to rearm. The native fall
queue restarts the40-frame animation and returns to506. No extra height,
invulnerability or BBS dash travel is added. Post-fix KH1 testing is still needed.

GROUND COMBO2 TIMING - MAIN AQUA ONLY
Both native variants keep source365 and their original lengths/counts.
C9/normal99 (Olympus61),48 native frames: first contact8 ->35; follow-up47.
CA/normal100 (Olympus62),64 native frames: first contact24 ->47; follow-up63.
All frame numbers are zero based at60fps. The follow-up window opens at the
final animation frame. Existing contact, trail/sound and state-event timestamps
are delayed together; the original event payloads, counts, descriptor pointers,
hitboxes and damage values remain. Native commands that use this same cancel
window also become available later. Check the hit/chain feel in-game.

NUMBERED TEST4 COMBO / SPELL POSES RETAINED
aqua 1 : ground316 317 318 ; air391 390 427
aqua 2 : ground315 371 366 ; air365 218 332
aqua 3 : ground393 411 352 ; air616 407 351
aqua 4 : ground510 511 512 ; air504 514 399
The352 air second, Fire-style Blizzard and365 event retiming apply to main aqua.
The native-tip magic, original Glide middle and504 guard apply to all five.
Numbered spell poses retain their previous assignments. Select one while idle;
zero-AP ids117..121 and saved selections remain. Native abilities are not evicted.

INSTALL
1. Fully close KH1.
2. Disable Aqua v14 and all older Aqua packages, Sora Restore Check and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH, enable Aqua Animation Test v15, Build and Run.
4. Load your save and equip aqua while idle.

TEST
- Check main ground300/365/366: late second contact, full second animation,
  then the next attack. Test locked/unlocked attacks to cover both variants.
- Check air351/352/393 and ground/air Blizzaga with Fire's animation.
- Check native weapon-tip spell effects, including Fire, Cure and Stop/Aero.
- Jump, release Circle, press again for504; land between attempts.
- Test Glide's Aqua opening, Sora middle while steering, then Aqua closing.
- Check both saves, room transitions/reloads and restoration with Aqua off.
For clean basic-combo testing, unequip Slapshot, Vortex, Hurricane Blast and
other native combo replacements; their separate actions keep their own timing.

IF DODGE STILL FAILS / INSTALL CHECK
Return the new kh1-aqua.log from beside KINGDOM HEARTS FINAL MIX.exe after one
test. The first line must identify v15. Look for AIR DODGE READY, accepted504,
then deferred native Glide constructor suppressed. Capture the log before
restarting, since each launch replaces it. CHECK_AQUA_V15.cmd checks installed
hashes and writes Aqua_Animation_Check_v15.txt. Drag your OpenKH folder onto it
if its default path does not match.

CAPACITY / RESTORATION
Both installed MSET files are original. All runtime motion headers, lengths,
table allocations, bone/helper counts, eleven helpers and native travel stay
original. The main second-ground edits change existing event time values only;
live encoded event descriptor pointers are retained. Unknown data blocks writes.
Body and request-table switching/restoration waits for idle. BBS command scripts,
MP logic or new invulnerability/hitboxes are not imported. Guard/Cartwheel motion
records retain native defensive windows. Spell timing uses the existing target
records, including Gravity's86/78 frames for main Stop/Aero.

FILES
ANIMATION_MAP.csv: usual motions for all five profiles.
SPELL_MAPPING.csv: every spell, ground/air, including current Blizzard routing.
COMBO_TIMING.csv: main second-ground contact and follow-up frames.
AIR_DODGE_MAPPING.csv / GLIDE_MAPPING.csv: movement phases and input rule.
TEST_CLIP_SOURCES.csv: exact source banks, cuts, frames, FPS and hashes.
source: current code, fixtures, tests, evidence reports and rebuild inputs.
inventory: existing349-clip inventory; current assignments are the root CSVs.
Numeric animation IDs are source identifiers, not official command names.

OPTIONAL DISABLE / REMOVE
To disable only airborne504, copy DISABLE_AIR_DODGE_kh1-aqua.ini beside the EXE
as kh1-aqua.ini and restart. Native Circle/Glide and the Glide pose phases remain.
To remove all five entries, use REMOVE_AQUA_kh1-aqua.ini as kh1-aqua.ini, leave
v15 enabled, restart and load each save to clean. Check AQUA ABILITIES REMOVED,
then save in-game. Exit, remove the INI, disable v15 and rebuild. Only117..121
are removed. Remove a temporary INI and restart to use default movement settings.

VALIDATION
65 actual-PE Win64-ABI runtime tests and18 geometry/assignment checks passed.
They cover deferred Glide after control, original constructor/trampoline calls,
native-tip casting, original Sora mid-flight bodies, Blizzard recovery queues,
main-only timing/restoration and unknown-data rejection across both banks.
Timing tests also execute the supplied executable's actual native event sampler.
All105 serialized pose assignments (86 distinct fitted records) keep the existing
capacity bounds. These checks do not run Windows/KH1 or render Sora's mesh.
The dodge fix, transition appearance and new contact/chain feel need in-game testing.
