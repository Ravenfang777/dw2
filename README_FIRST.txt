KH1FM AQUA ANIMATION TEST v21
Steam Global / OpenKH Panacea

INSTALL
Fully close KH1. Disable v20/older Aqua tests and conflicting Nine Styles /
Dual Wield or combat builds. Install this ZIP in OpenKH, enable it, then Build
and Run. Equip MAIN aqua while idle. The log banner must say v21.
CHECK_AQUA_V21.cmd checks the compiled installation hashes if needed.

MAIN AQUA CHANGES
AERIAL DODGE
Tap Circle airborne after releasing it following takeoff.504 and its movement
run at1.5x the previous rate:26 native ticks instead of39 (two-thirds the time).
The complete unobstructed burst still requests546 horizontal units and29.25
units of lift. Direction stays locked to the tap's movement direction, with
the prior neutral momentum/facing fallback. Collision, ceilings, landing and
native interruptions still apply. Native fall handoff speed matches v20 to
avoid adding extra drift after the faster burst.

ONE DODGE PER AIRTIME. Completing504, releasing/repressing Circle, changing
Aqua abilities, recovering animation bindings or using Superglide do not grant
another dodge. Land to rearm. A new actor identity starts a new budget.

SUPERGLIDE
Native Superglide is usable again with its own normal button/ability checks.
Only ordinary Glide is replaced by tap504. A successful native Superglide can
interrupt504; a rejected Superglide does not cancel the dodge. It does not
reset the dodge's spent use. Native Glide/Superglide animation records remain
original. air_dodge=0 restores native air controls; the jump boost remains.
The1.5x dodge rate requires the verified actor-motion hook. If that hook cannot
be admitted, the controller logs and keeps the old matched movement/visual
rate rather than accelerating movement alone.

JUMP HEIGHT
Normal and High Jump receive25 percent more native launch height in MAIN.
The native launch runs first. Only its private arc height and ascent duration
are scaled (1.25 and sqrt1.25), leaving launch origin, global gravity, stats,
actor positions, native collision and ceiling handling untouched.

COMBOS
Ground remains300 ->301 ->366.
-301 retains source0..30, trimming7 more end frames compared with v20.
- Both second-attack variants enable the finisher at24 real native ticks
  instead of30. Their completed-pose recovery advances twice as fast.
-366 retains source15..47, removing3 more opening frames compared with v20.
  Its native hit/effect timing and playback duration follow that trim.
- First ground attack and its contact timing remain unchanged.
Air is now305 ->407 ->353. Native contact windows follow the swapped poses.
The first/second follow-up windows run18..40 and22..42 native clock units.
Native event counts, payloads, pointers, headers and allocation sizes remain.

RETAINED
Main Guard400 full forward/reverse at source30fps, wider native body capsule
and12-tick grace; combat-idle skull tilt right20 degrees; aerial Fire/Blizzard
right-facing head adjustment; swapped run loops; keyblade-tip magic; native
Blizzard spell logic; original KH1 Sora damage reactions. KH2 reaction source
assets are still pending. Installed Sora/Olympus MSETs stay original.

NUMBERED TEST ABILITIES RETAIN v20/v18
 aqua1 ground371365366 / air218332393
 aqua2 ground352353407 / air351304303
 aqua3 ground300301302 / air616407351
 aqua4 ground510511512 / air504514399
All148 active numbered records match v20 byte-for-byte. Numbered jump heights,
dodge rate/controls, casts and Guard behavior remain as before. All five
abilities retain0AP and IDs117..121. Switch profiles while idle.

IN-GAME TEST
1. Compare jump and High Jump height with main equipped/unequipped.
2. Tap airborne Circle and check faster504 with the same travel distance.
3. After504, release and tap again: no second dodge until landing. Land and
   repeat. Check that attacks, ability toggles and Superglide do not rearm it.
4. Use native Superglide with its ability equipped, including after504.
5. Check ground300/301/366 flow and air305/407/353 during combat.
Return kh1-aqua.log and a short clip if a visual, timing or movement issue
remains. The wider Guard and previous poses are unchanged in this test.

VALIDATION
110 actual-PE runtime tests and29 serialized-pose tests pass offline. Jump
checks execute the supplied game's actual launch and arc code in the mock
host. Faster-dodge distance is checked with both callback orders and several
timesteps. Native hook anchors match the supplied Steam executable. No live
Windows/KH1 playtest or rendered-mesh check was performed. Native collision,
allocation and input calls are mocked; in-game feel still needs testing.
Source, fixtures, reports and REBUILD_V21.txt are included in source/.

ROLLBACK / REMOVE
Close KH1, disable v21, enable the previous package and rebuild to roll back.
For complete ability removal, use REMOVE_AQUA_kh1-aqua.ini as kh1-aqua.ini next
to the game EXE, load a save and save again, then remove the config/mod.
