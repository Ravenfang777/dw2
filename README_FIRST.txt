KH1FM AQUA BODY COMBO TEST v6
Steam Global / OpenKH Panacea

ABILITY: aqua (lowercase), 0 AP, ability id117
Newly learned aqua starts unequipped. An existing saved selection is respected.

WHAT V6 TESTS
Equipping aqua switches nine original animation records to retargeted Aqua
body poses: four ground attack records, three aerial attack records, the
Barrier pose on Guard, and the Cartwheel pose on Dodge Roll. Unequipping aqua
restores all nine original records. Normal Sora and Olympus are supported.

This is a body-animation test. KH1 still chooses the combo sequence and uses
its original hitboxes, attack/guard timing, defensive coverage, invincibility,
travel distance, effects and sounds. Barrier is not yet a 360-degree defense
or a new visual effect. Cartwheel uses the native Dodge Roll movement/window.

INSTALL AND TEST
1. Fully close the game.
2. Disable Aqua v1-v5, Sora Restore Check v3, and Nine Styles / Dual Wield v52.
   Keep other Sora model/moveset replacements disabled for this comparison.
3. Import this ZIP into OpenKH. Enable Aqua Body Combo Test v6. Build and Run.
4. Load the Olympus save. Leave Guard and Dodge Roll equipped. Turn off attack
   replacements such as Slapshot, Sliding Dash, Vortex, Stun Impact, Ripple
   Drive, Zantetsuken and Hurricane Blast for the ordinary-combo test.
5. With aqua OFF, try a ground combo, a jumping aerial combo, Guard and Dodge
   Roll. Equip aqua while idle and repeat. Unequip it and repeat once more.
   Allow each action to finish before opening the menu. Use Combo Master if
   needed to continue combos while striking empty air.
6. Repeat on the Traverse Town save. Test walking/running/jumping between
   actions, and loading the other save from a fresh launch.

RETURN
A short OFF / ON / OFF video and the NEW kh1-aqua.log from beside the game EXE.
The first log line must say AQUA BODY COMBO TEST v6. A successful application
logs AQUA MOTIONS ENABLED and the bank name. Turning aqua off logs AQUA MOTIONS
DISABLED. If the body change does not appear, return the log as it stands.

The log is created beside:
C:\Steam\steamapps\common\KINGDOM HEARTS -HD 1.5+2.5 ReMIX-\KINGDOM HEARTS FINAL MIX.exe

If needed, extract the ZIP and run CHECK_ABILITY.cmd after the OpenKH build.
It writes Aqua_Body_Combo_Check_v6.txt beside itself and checks file hashes.

HOW THIS DIFFERS FROM V1/V2
The files installed on disk remain your original Sora and Olympus MSETs.
The DLL changes data only after all nine live records pass verification.
The motion records keep their original sizes, headers, channel counts, bone
count and eleven helper slots. No expanded motion bank or helper hierarchy
is allocated. The compact FK body reuses existing key capacity; the original
travel helper and its ancestor tracks remain intact. Unknown/changed data
causes the controller to wait without writing body data.

The body poses are fitted to this fixed capacity, so they approximate the
donor motion. The offline preview is a skeleton check, not a game recording.
Idle, walk, run and other action records are not replaced. Other Sora forms
or costume animation banks have not been admitted by this test.

SAVE / REMOVE AQUA
You can compare without saving. Saving in-game may retain ability id117.
To remove aqua from a save later:
- Put REMOVE_AQUA_kh1-aqua.ini beside the game EXE, renamed kh1-aqua.ini.
- Leave v6 enabled, restart, load each save to clean and check for AQUA ABILITY
  REMOVED in the log. Save in-game to retain the removal.
- Exit, remove the INI, disable v6 and rebuild.
Only ability id117 is removed; the other abilities keep their order.

VALIDATION
Nine fitted motion records passed 1,853 quarter-frame pose checks. Motion
sizes and headers match their originals; native travel error was zero in
the offline evaluator. Sixteen checks executed the actual compiled PE DLL
in a mock Win64 host, including both banks, exact reversible data changes,
mid-action deferral, bank reloads, uninstall, and rejection of foreign data.
These checks do not execute Windows or KH1. V6 still needs your game test.

The v5 log you supplied confirms the aqua ability and its first-attack arm
gate worked in Olympus. It does not establish v6 body-animation compatibility.
