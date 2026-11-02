KH1FM AQUA ANIMATION TEST v20
Steam Global / OpenKH Panacea

INSTALL
Fully close KH1. Disable v19/older Aqua tests and Nine Styles/Dual Wield or
other conflicting combat builds. Import this ZIP into OpenKH, enable it, then
Build and Run. Equip MAIN aqua while idle. The log banner must say v20.
Use CHECK_AQUA_V20.cmd to check compiled file hashes if needed.

MAIN AQUA CHANGES
- Combat idle tilts Sora's actual skinned skull20 degrees RIGHT. This replaces
  v19's left-facing yaw. Hair bind corrections remain. Aerial Fire/Blizzard
  retain the prior right-facing yaw; run animations retain the prior swap.
- Ground combo remains300 ->301 ->366. Trim301's quiet final3 source frames
  (retain0..37). Both native variants now reach the contact and follow-up
  phases at matching real times: hit about6.49 ticks, follow-up30 ticks.
  The first swing's contact timing remains unchanged.366 retains its existing
  source12..47 trim and playback rate; no additional leading frames were cut.
- Air combo remains305 ->353 ->407. First follow-up window18..40, second
 24..42 native clock units. These reach each non-finisher's end to make the
  follow-up less easy to miss. Native event payloads/counts/pointers remain.
- Guard400 still plays fully forward then reverse at source30fps (2.6s).
  A wider body-centered capsule (radius50, centers35/85 units above the actor)
  supplies native guard contacts around Sora, including behind him. It uses
  the native constructor, contact mask, collision/deflection and retirement.
  Native Guard must be equipped and selected. This is a timed defense:
  release adds up to12 native ticks (~0.2s); parry6E/6F retains up to12 ticks.
  New attacks, magic, movement, damage, scripts, menus or ability changes cancel
  the extra shield. Recycled pool slots are not retired by this controller.
- Airborne Circle tap starts504 with captured movement direction and slight
  lift for39 units. Release Circle after takeoff, then tap. Releasing input
  does not shorten travel. Native collision/landing/interruptions still apply.
  Normal AND Superglide share the blocked constructor while MAIN is selected,
  including during binding recovery. air_dodge=0 restores native air behavior.
- A temporary residency/save-readiness interruption no longer forces an
  already-correct Aqua bank to wait for idle. It can be fully revalidated
  without body writes while moving. Failed full admissions retry every8
  frames. Reset/suspension messages identify the path in kh1-aqua.log.
  Guard angle checks skip unrelated clash pairs before querying Sora.

NUMBERED TEST ABILITIES RETAINED
 aqua1 ground371365366 / air218332393
 aqua2 ground352353407 / air351304303
 aqua3 ground300301302 / air616407351
 aqua4 ground510511512 / air504514399
All148 active numbered records compare byte-for-byte with delivered v19.
Their legacy v18 poses, timing and controls remain. All five ability IDs
117..121 retain0AP and exclusive selection. Switch profiles while idle.

RETAINED
Original on-disk Sora/Olympus MSETs; native headers/counts/allocations/travel;
keyblade-tip magic; native Blizzard spell logic with Fire visuals; native KH1
Sora reactions. Default KH2 Sora reaction assets are still pending.

TEST IN GAME
1. Check combat-idle right tilt and ground300/301/366 flow in both banks.
2. Repeat air305/353/407 during combat, including rapid and late follow-ups.
3. Tap Circle with each direction, release input, then hold Circle after504.
   Check that Glide does not return after combat, damage or a map transition.
4. Guard attacks from behind and either side, then repeat after a parry.
5. Check performance around the earlier Glide fallback situation. Return the
   resulting kh1-aqua.log and, if a visual/timing issue remains, a short clip.

VALIDATION AND LIMITS
98 actual-PE runtime tests and29 serialized-pose tests pass offline. Native
hook anchors match the supplied Steam executable. No live Windows/KH1 playtest
or rendered-mesh check was performed. Native callbacks are mocked in the PE
host; full combat behavior and visual feel need the in-game tests above.
In the offline lost-binding scenario, memory queries over120 moving frames
fell from33960 (v19) to1241 (v20). This is not a game-FPS measurement or proof
of the original slowdown's complete cause. Reports and rebuild sources are
included in source/. See source/REBUILD_V20.txt.

ROLLBACK / REMOVE
To roll back, close KH1, disable v20, enable the previous package and rebuild.
For complete ability removal, use REMOVE_AQUA_kh1-aqua.ini as kh1-aqua.ini next
to the game EXE, load a save and save again, then remove the config/mod.
