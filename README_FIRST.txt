KH1FM AQUA ABILITY TEST v5
Steam Global / OpenKH Panacea

NEW ABILITY: aqua
AP cost: 0. Initially unequipped. Ability id 117 (reserved for this test).

Equip aqua to enable the tested v4 arm motion on the FIRST ordinary ground
attack. Unequip it to restore the original Sora curves. The current test still
changes only that attack's arm paths; it is not yet the full Aqua moveset.

BOTH SAVE LOCATIONS
The Olympus clip uses the same original attack data as the normal Sora clip.
V4 deliberately left the Olympus file untouched, explaining the world-specific
result. V5 recognizes both physical slots: 98 normal Sora and 60 Olympus.
Your town recording is Traverse Town. Both locations are supported by this probe.

INSTALL
1. Fully close the game.
2. Disable Aqua v1, v2, Sora Restore Check v3, Aqua Arm Probe v4, and Nine Styles /
   Dual Wield v52. Keep other moveset/model/combat-animation replacements off.
3. Import this ZIP and enable Aqua Ability Test v5. Use Build and Run.
4. Load a save. Open Sora's Abilities menu and find aqua. It starts UNEQUIPPED.
5. Test a normal first ground attack with aqua OFF, then ON, then OFF again.
   Unequip attack replacements such as Slapshot/Sliding Dash/Vortex for this
   comparison. Equip/unequip while standing idle, and let each single swing end.
6. Repeat the comparison in the Coliseum save and the Traverse Town save.

RETURN
A short OFF/ON/OFF video and kh1-aqua.log. The DLL creates that log beside:
    C:\Steam\steamapps\common\KINGDOM HEARTS -HD 1.5+2.5 ReMIX-\KINGDOM HEARTS FINAL MIX.exe
The log records ability registration/selection, admitted bank slots, and native
attack requests. If aqua is missing, return the log before changing other mods.
CHECK_ABILITY.cmd can confirm the built files if needed; run it after extracting
this ZIP and after an OpenKH build. It writes Aqua_Ability_Check.txt beside itself.

WHAT THIS BUILD PRESERVES
The original Sora MSET files are copied on disk. The DLL checks the live attack
record before changing the same 60 existing wrist key records as v4. It restores
the original data when aqua is off. All native headers, helper counts, timings,
root movement, events and other animations stay original. No HP/MP/damage,
input, actor position, or extra weapon is written. Full ground/air combos,
Barrier and Cartwheel will follow after the named ability and gate are verified.

SAVE / REMOVE THE TEST ABILITY
The ability is inserted into the loaded ability list. Saving in-game can retain
that custom ability byte. For a temporary test, you can compare without saving.
If you saved with aqua and want to remove this module:
- Put the supplied REMOVE_AQUA_kh1-aqua.ini beside the game EXE, renamed exactly
  kh1-aqua.ini. Leave this v5 mod enabled for that removal run.
- Restart, load each save you want cleaned, and check the log for AQUA ABILITY
  REMOVED. Save in-game to retain removal. Only ability id117 is removed.
- Exit, remove the INI, disable v5 in OpenKH and rebuild.

VALIDATION
The actual compiled DLL was executed in an offline Win64 ABI mock host. The
checks cover registration, both banks, reversible curve writes, rejection of
unknown/changed data, full ability-list handling and removal. This was not a
Windows or game execution. The in-game menu and live gate still need your test.
The module accepts only the verified Steam executable timestamp; it logs and
leaves gameplay unchanged on a different build or if v52 is loaded.
