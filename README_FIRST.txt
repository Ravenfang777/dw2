KH1FM AQUA ANIMATION TEST v18
Steam Global / OpenKH Panacea

MAIN AQUA
Ground: 300 -> 301 -> 366. Air: 305 -> 407 -> 351.
301 is fitted into both native second-ground variants. Its full source plays
before a 16/20-native-frame recovery window allows the finisher. Existing
native hit payloads remain; contact timing follows 301's source-frame8 strike.

NEXT TEST ABILITIES
Ability       Ground            Air
 aqua 1       371 365 366       218 332 393
 aqua 2       352 353 407       351 304 303
 aqua 3       300 301 302       616 407 351
 aqua 4       510 511 512       504 514 399
Aqua3 air and Aqua4 were not specified for replacement and retain v17 mappings.
The main entry and four tests use the same ability IDs117..121 and0AP.
Select one while idle. Existing native ability entries are never evicted.

AERIAL DODGE504
Release Circle after takeoff, then press Circle once while airborne. Land to
rearm. Direction is read from the held left stick on every native control
update, so turning the stick steers throughout the animation. Releasing Circle
does not shorten the dodge. Neutral stick stops horizontal motion while the
slight lift continues. Stick pressure scales horizontal speed, with a deadzone
and normalized diagonals. This replaces v17's high Dual D ballistic arc.

Tuning: full-stick speed14 units/native clock unit, upward speed0.75, duration39
clock units over the existing40-frame fall record. An unobstructed complete
path requests546 horizontal units and29.25 units of lift. These are requested
movements before native collision, not a guaranteed in-game distance. Ceilings
clip upward travel; landing, damage, scripted actions and other interruptions
return to native handling. The mod never writes actor position directly and
adds no invulnerability, hitbox or defense. Fall506 resumes after504.

GUARD400 FORWARD AND REVERSE
The full source animation plays forward once during native frames0..10,
holds its last pose during10..36, then plays once in reverse during36..52.
Forward speed is3.9x and reverse speed2.4375x the source's30fps timing: both
exceed the requested minimum1.25x. This fits the existing54-frame native record
and aligns the reverse with native recovery. No hold-to-guard mechanic is added.
Original Guard events and defensive timing remain. Native cancels, attacks,
damage and scene changes can interrupt recovery. Guard must be equipped normally.
The common Guard record is shared by all Aqua profiles.

IDLE FRONT HAIR
Idle/combat-idle now retain native local bind rotations for the connected front
hair root and chain151..154. Side/back hair155..193 remains at bind as before.
The idle skull direction, joint lengths, scales and native travel are retained.
The v17 run correction on skinned skull150 remains. A live visual check is
still needed; the offline checks verify connected joint transforms and skin
bases rather than claim an in-game mesh rendering.

DAMAGE / KNOCKBACK: KH2 SOURCE STILL NEEDED
The requested default KH2 Sora replacement is NOT included yet. The provided
KH2 combat DLL loads Sora data from the installed game and contains no source
motions. P_EX100_BTLF is Valor and is not a default Sora substitute.
All Aqua damage/knockback replacements have been removed. This build currently
uses original KH1 Sora reactions for requests48..51 (normal61..70/Olympus24..33).
Other native reaction/parry records also remain original. This fallback is KH1,
not KH2. No recovery logic, damage calculation or defensive window is altered.

To finish KH2 reactions, supply extracted obj/P_EX100.mdlx and obj/P_EX100.mset.
COLLECT_KH2_SORA_SOURCE.cmd opens a folder selector, copies only those default
Sora BAR files, and writes a separate KH2_Sora_Source_*.zip. Choose extracted
KH2 data or its obj folder; the helper does not extract large PKG containers.
Upload the resulting ZIP. The helper never changes the selected source files.

RETAINED
Original KH1 Glide, native Blizzard events with main Fire visuals, keyblade-tip
magic, all numbered casting assignments and the remaining main Aqua actions.
No additional ability IDs are added. Native motion headers, counts, lengths,
293-bone skeleton, eleven helper slots and allocations remain unchanged. The
installed normal/Olympus MSETs are original; the ability gate applies body curves
and scoped event time edits only at runtime.

INSTALL / TEST
1. Close KH1. Disable older Aqua and KH2 Combat/NineStyles/Dual Wield builds.
2. Install this ZIP in OpenKH Mods Manager, then Build and Run.
3. Equip main aqua while idle. Check idle hair,300/301/366, air305/407/351,
   Guard entry/recovery, then a Circle dodge with forward/side/back stick input.
4. During dodge, turn the stick and return it to neutral; lift should remain
   small throughout504 and normal falling should resume afterward.
5. Test aqua1..3 combos and verify Blizzard, standard Glide and damage reactions.
6. Repeat in normal and Olympus environments. Share kh1-aqua.log plus a short
   video for trajectory, hair or Guard adjustments. The log banner must sayv18.

VALIDATION
Offline tests execute the built PE DLL with a controlled Win64 host and sample
serialized geometry, original event data and native executable anchors. This
is not a Windows/KH1 playtest. See validation.json for exact current results.
The KH2 damage replacement remains explicitly pending source assets.
