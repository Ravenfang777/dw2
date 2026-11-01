KH1FM SORA RESTORE CHECK v3

This package restores your two previously supplied Sora MSET files unchanged.
It contains no Aqua animations, new helpers, retargeted curves, or new DLL.
It does not read or modify save files. The assets were checked byte for byte
against the original inputs used for the Aqua conversion.

PURPOSE
Your video shows visible animation/position problems in Aqua v2. You also
reported that your usual save would not load, while a backup loaded.
The video does not establish why the usual save failed, or that it is damaged.
This check establishes whether both saves and normal movement work again
with the original Sora movesets restored.

USE THIS PACKAGE FOR THE NEXT TEST
1. Fully exit Kingdom Hearts Final Mix.
2. In OpenKH's Kingdom Hearts 1 list, disable Aqua Motion Test v1, Aqua Motion
   Test v2, Nine Styles / Dual Wield v52, and other Sora moveset/model replacements.
3. Import this ZIP, enable Sora Restore Check v3, and choose Build Only.
4. Extract this ZIP somewhere writable. Double-click CHECK_RESTORE.cmd.
   It checks the compiled files against the original hashes and looks for the
   old dual-wield DLL. It collects available recent KH1 Windows crash events.
   It saves Sora_Restore_Check.txt beside itself, including a fallback console
   report if PowerShell cannot complete. Run the CMD file after extraction.
   If your OpenKH folder moved, drag the OpenKH folder onto CHECK_RESTORE.cmd.
5. If the installation checks pass, launch through OpenKH with that mod list.
   Try loading your usual save, then the backup. Test standing still, walking,
   running, jumping, and a basic attack. You can do these checks without saving.

RETURN
Sora_Restore_Check.txt and these two results:
- Usual save: loads normally / crashes / stays loading / other behavior.
- Backup save: normal Sora movement and attacks / describe remaining problems.

Aqua's asset-only tests do not create kh1-dual-wield.log. That file belongs to
the separate DLL mod. The checker creates its own report locally when run.

NEXT STEP
After the baseline works, the next Aqua probe should change one attack only.
Do not re-enable Aqua v1 or v2 for the baseline check.

The checker only reads the installation. OpenKH applies the two original
MSET replacements through the normal mod build. The packet includes no
Windows runtime execution results; it was assembled and verified offline.
