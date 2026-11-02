KH1FM AQUA ANIMATION TEST v8
Steam Global / OpenKH Panacea

ABILITY: aqua (lowercase), 0 AP, id117

V8 CHANGES
- Restored Sora hair chains 155..193 to the model's bind rotations, removing
  five inherited idle-pose bends that were held through the Aqua animations.
- Added bounded wrist/elbow/knee clearance corrections. These preserve bone
  lengths and scales and reduce joint/capsule overlap in the offline samples.
  This is not full mesh self-collision; some contact may still need adjustment.
- Added experimental RIGHT-HAND magic attachment routing. During Aqua's native
  ground/air cast requests, weapon attachment 0x30 uses right-palm world matrix
  101. Both native attachment position and effect-matrix queries are handled,
  so spell origins and attached glow can follow the hand. The game still runs
  its own spell scripts, trajectories, targeting, effects, MP and damage.
- Included the complete current Aqua inventory: 349 unique animation payloads,
  739 source occurrences, source IDs, frames, FPS, timing, raw loop data,
  channel/key counts, source locators/hashes and identification status.

INSTALL
1. Fully close KH1.
2. Disable Aqua v7 and all older Aqua packages, Sora Restore Check v3, and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH, enable Aqua Animation Test v8, then Build and Run.
4. Load your usual save. Equip aqua while standing idle. Guard and Dodge Roll
   still require their native abilities. Unequip aqua while idle to compare.

FIRST TEST
Start with aqua OFF, then ON, then OFF while idle. With aqua ON:
- Check the hair from front, side and behind while idle and running.
- Check ground/air combos, Cartwheel and Guard for wrist/elbow/knee clipping.
- Cast Fire and Blizzard, then each other available spell on the ground and
  in the air. Check the RIGHT hand for the glow and launch point. Check that
  launched projectiles continue normally and companion casts still look normal.
- Unequip aqua while idle and repeat a spell to check native attachment behavior.
Repeat on the second save, and try a room transition and a save reload.

The new kh1-aqua.log beside the game EXE must start with ANIMATION TEST v8.
Successful body selection logs AQUA MOTIONS ENABLED and 0x2F normal / 0x2E
Olympus records. The magic installer logs AQUA HAND MAGIC READY; actual routed
queries log AQUA HAND MAGIC ORIGIN and/or AQUA HAND MAGIC MATRIX plus the
native request number. READY alone does not prove a spell used that route.
Return this NEW log and a short comparison video, including a cast where the
glow/origin remains incorrect if one does. The optional CHECK_AQUA_V8.cmd
checks installed hashes and writes Aqua_Animation_Check_v8.txt.

OPTIONAL HAND-MAGIC FALLBACK
To keep the v8 hair/limb changes with native spell attachments, copy
DISABLE_HAND_MAGIC_kh1-aqua.ini beside the game EXE and rename it kh1-aqua.ini.
Restart the game. Remove that INI and restart to test hand routing again.

MOVE INVENTORY
inventory/Aqua_Move_Inventory_v8.xlsx has filterable clip and KH1 assignment
tables. CSV and JSON copies are included. Source IDs retain leading zeroes.
The 349 entries are animation clips, including cinematic/event material;
they are not 349 identified gameplay commands. Names describe reviewed poses
or existing assignments. Provisional and unidentified clips are marked.
PAM numeric names alone do not establish official BBS command names.
Raw loop fields do not guarantee gameplay looping. Duration = frames / FPS;
the last sampled frame occurs at (frames - 1) / FPS.
The 47 current normal records use 32 unique source clips. Olympus has 46
copies; one ledge recovery exists only in the normal bank. ANIMATION_MAP.csv
lists assignments; REMAINING_NATIVE.csv lists unassigned native records.

SCOPE
V7's movement, jumping, ledges, casting poses, items, reactions, combos, Guard
and Cartwheel remain mapped. KH1 action timing, native travel, guard coverage,
dodge invincibility and combat rules remain in use. Barrier is still a Guard
pose. Per-spell BBS choreography has not been separated from the shared casts.
Hair and limb corrections apply only to mapped Aqua motions.

Both installed MSETs are your original files. The DLL validates all applicable
records and reuses their existing in-memory tables and key capacity. Headers,
lengths, counts, eleven helpers and native travel tracks retain their layout.
Two separately checked native attachment entry points supply hand magic.
Unknown function bytes leave native attachments active. Unequipping restores
the original motion tables and uses the native attachment behavior.

SAVE / REMOVE AQUA
You can compare without saving. Saving in-game may retain ability id117.
To remove it, copy REMOVE_AQUA_kh1-aqua.ini beside the game EXE, renamed
kh1-aqua.ini. Leave v8 enabled, restart and load each save to clean. Check for
AQUA ABILITY REMOVED, then save in-game to retain removal. Exit, remove the
INI, disable v8 and rebuild. Only id117 is removed.

VALIDATION
The included reports describe checks of serialized poses and execution of
the final PE DLL in a Win64 ABI mock host. They verify routing, scope, exact
on/off restoration, hair rest shape, bounded corrections, pose transitions,
original capacities and native travel. They do not run Windows/KH1 or render
Sora's mesh. V8 hand magic and appearance need the in-game test above.
