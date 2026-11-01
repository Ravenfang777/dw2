KH1FM AQUA MOTION TEST v2 - REVISED ISOLATION TEST
KH1 Final Mix PC / Steam, OpenKH Panacea

Use v2 in place of Aqua v1. This revision corrects a stale terminal boundary
left when v1 enlarged the MSET, and assigns Barrier to the Guard motion
observed in your log (request D4). v1 had incorrectly replaced Glide's
startup/hold/recovery motions. v2 restores those from your original inputs.

Your returned log also shows Nine Styles / Dual Wield v52 actively replacing
poses, with Master and Dark Riku selected. That prevents an isolated Aqua
motion test. The log contains no exception or fault address establishing
which component caused your crash. This revision is not game-tested here.

EXACT TEST SETUP
1. Fully exit Kingdom Hearts Final Mix.
2. In OpenKH's KH1 mod list, disable Aqua v1, Nine Styles / Dual Wield v52,
   and any other Sora model, moveset, or combat-animation replacements.
   Import this ZIP and enable only Aqua Motion Test v2 among those mods.
3. Choose Mod Loader > Build Only.
4. Extract this ZIP somewhere writable and run CHECK_AQUA_TEST.cmd.
   It uses the OpenKH folder from your log by default. If it cannot find that
   folder, drag your OpenKH folder onto CHECK_AQUA_TEST.cmd instead.
   It checks the compiled MSET hashes and looks for the old dual-wield DLL.
   It also collects up to three recent KH1 Windows Application Error events.
   It only reads your installation; it writes Aqua_Test_Check.txt beside itself.
5. Resolve any FAIL entries. Then launch through OpenKH with the same mod list.

TEST MOVEMENT FIRST
Load a normal-Sora save in Traverse Town. Stand still, walk, run, stop and
turn, then jump and land. These motion records retain your original Sora
bytes in v2. Stop here if movement is wrong or the game crashes.

If that passes, equip Guard and Dodge Roll, temporarily unequip extra combo
modifiers/finishers, and test one ground attack, the full ground combo, air
attacks, Guard, and Cartwheel. Check Olympus after ordinary Sora is stable.

RETURN
Aqua_Test_Check.txt plus whether the crash happens during basic movement or
only after a particular attack/Guard/Cartwheel. A short video will help judge
the idle and poses. Run the checker again after a crash to capture any new
Windows error event. An old kh1-dual-wield.log is not an Aqua-load confirmation:
this standalone asset test includes no DLL and does not create that log.

CONTENTS AND LIMITS
- Ground: donor clips 300 / 301 / 302 / 304; initial attack ordering.
- Air: donor clips 305 / 306 / 309.
- Guard: donor clip 400, fitted to the native Guard clip duration.
- Dodge Roll: donor clip 009 (Cartwheel).
Normal Sora and Olympus movesets are included. Native KH1 damage, timing,
actor travel and defensive rules remain. Barrier's bubble/360-degree BBS
behavior, a selectable style in v52, Halloween and Atlantica are not included.

TO REMOVE
Disable v2, fully exit, and rebuild. The checker does not change game files.

validation.json and validation_olympus.json describe offline checks; they
cannot establish runtime loader behavior or fix the cause of an unidentified
crash. source/ includes the converter, regression checks and credits.
