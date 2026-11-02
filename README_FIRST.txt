KH1FM AQUA ANIMATION TEST v19
Steam Global / OpenKH Panacea

CHANGES APPLY TO THE MAIN aqua ABILITY
Ground: 300 -> 301 -> 366, with the first12 source frames removed from366.
Air: 305 -> 353 -> 407.
Combat idle: skinned skull turns20 degrees left.
Aerial Fire AND Blizzard: skinned skull turns20 degrees right. Fire recovery
uses the same adjustment so the head does not snap between cast portions.
Normal run now uses013; combat run now uses004. Both remain proper loops.

GUARD
Aqua400 plays fully forward once, then fully backward once, at its source30fps
speed. Nominal total duration is2.6 seconds. The native guard window spans the
whole sequence. Native Guard selection must succeed; Guard still needs to be
equipped. The main ability does not grant Guard automatically.

The controller observes native Guard action row0x3D, then changes only the
native actor-motion delta for that action. It bypasses the facing-cone check
for Sora's own live native Guard objects during that witnessed action.
Native contact, priorities, projectile deflection, feedback and attacks that
cannot normally be guarded still use the game's handling. This is all-angle
Guard, not permanent invulnerability. Interruption, unload or ability changes
end its extra controller behavior. Other actions do not gain all-angle defense.

The animation headers,54-frame record, bone/helper counts, allocations and
original MSET files remain unchanged. The native motion clock advances more
slowly for Guard. The finisher's native motion clock advances faster after the
source trim so removing its beginning actually shortens the action.

TAP DODGE REPLACES HELD GLIDE
In the air, release Circle after takeoff and then tap Circle. Main aqua starts
504 once and suppresses normal held-Glide activation. It captures the character
movement direction at that tap, then travels for the full animation with small
upward lift. Releasing Circle or the stick does not shorten it or stop travel.
When the animation finishes,506 falling resumes. Release then tap again after
completion to perform another burst. Holding Circle never repeats the burst
and never returns to held Glide while main aqua remains active.

Direction uses the native movement vector. With neutral input it uses existing
horizontal momentum, then character facing if stationary. Main travel uses a
normalized direction at speed14 per native time unit, with lift0.75 over39 units
(the existing40-frame visual). A full unobstructed burst requests546 horizontal
units and29.25 lift. Native walls, ceilings, landing and interruptions still
apply. Actor positions are never written directly. The air_dodge=0 diagnostic
option restores native air input/Glide.

NUMBERED TEST ABILITIES RETAIN v18
 aqua1 ground371 365 366 / air218 332 393
 aqua2 ground352 353 407 / air351 304 303
 aqua3 ground300 301 302 / air616 407 351
 aqua4 ground510 511 512 / air504 514 399
Their combos, casts, idle, runs, Guard animation/timing, steered dodge and normal
Glide retain v18 behavior. Main changes are isolated with explicit older common
pose payloads. All five ability IDs117..121 and0AP are retained.

OTHER RETAINED BEHAVIOR
Main ground300/301, keyblade-tip magic, native Blizzard events with Fire poses,
original KH1 Sora damage/knockback, idle hair bind correction and remaining
Aqua animations. Default KH2 Sora reactions are still pending P_EX100 source
assets; no KH2 reaction replacement is claimed here.

INSTALL / TEST
1. Fully close KH1. Disable the previous Aqua test and any NineStyles/Dual Wield
   or KH2 Combat build. Install this v19 ZIP in OpenKH, then Build and Run.
2. Equip MAIN aqua while idle. The log banner must sayv19.
3. Test Guard entry, reverse exit and attacks approaching from front/side/rear.
4. Test ground300/301/trimmed366 and air305/353/407.
5. Tap Circle airborne with a direction, release both inputs and watch the full
   burst. Hold Circle afterward: it must not begin normal Glide. Test a new tap.
6. Check combat idle, aerial Fire/Blizzard head direction and both run variants.
7. Switch to a numbered test while idle to check its unchanged v18 behavior.

VALIDATION
Offline checks execute the actual PE DLL in a Win64 ABI mock and sample the
serialized poses. New hook anchors and control paths are checked against the
supplied Steam executable. No live Windows/KH1 game rendering or playtest is
claimed. Please return kh1-aqua.log and a short video if timing, directional
blocking, movement or head orientation needs adjustment.
