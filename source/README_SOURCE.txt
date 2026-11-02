AQUA V16 SOURCE / REPRODUCIBILITY

The supplied original EXE is Steam Global timestamp1721645006, SHA256
 d790746245d26159f3ee0e1060e33b2fa2de06941850a4ac724f598722884bac.
Its full bytes and the user's log are not redistributed. Native anchors and
Master-reference provenance are recorded in native_movement_validation.json.

Build DLL on Linux with Python3, GCC and GNU ld PE support:
 python3 generate_data.py
 python3 build.py
 python3 test_runtime.py
 python3 test_visuals.py
NumPy/SciPy are required for pose fitting/geometry; Python3/GCC for runtime mocks.
The runtime checks map the actual emitted PE with Win64 ABI/import mocks.
They are not Windows/KH1 execution or a rendered-mesh test.

Optional source pose rebuild from this directory:
 python3 retargeting/tools/build_aqua_complete_v16.py --profile 0 --output .
 python3 retargeting/tools/build_aqua_complete_v16.py --profile 1 --output sets/p1
Profiles2..4 use sets/p2..p4;5 uses dodge;6 uses glide_stop;7 uses blizzard.
The builder finds model/PAM/ARC inputs below retargeting and original MSETs in
../assets. --slots limits rebuilt native records. The sampling cache is rebuilt
from immutable baseline data; refinements are applied once. Regenerate data,
rebuild the DLL and run checks after modifying any serialized fixture.

Blizzard selector: aqua_blizzard.h recognizes current/newly queued logical37/84
including native request flags, verifies the admitted55/80 motion parts, then
copies only full391/316 body curves into those original records. Their native
spell events and request lookup remain. Restore the shared317/390 body before
the next spell, interruption, ability-off or idle profile switch. No recovery
append, terminal reordering, MP call or projectile hook exists in v16.

Main timing: aqua_event_timing_v16 changes existing hit/chain frame floats for
98/99/100 only. It preserves every descriptor, key payload, sound and effect key.
Second365 reaches its last source frame at native32/44, then holds. Kind5 opens
32/44 through48/64, giving16/20 native frames to chain after the full swing.
The sixth runtime AquaPart admits the known event-key stream through header60,
checking all encoded descriptor/key handles. All native allocation sizes/counts
remain original. Other profiles use original event times, and off restores them.

Aerial dodge: aqua_air_dodge.h verifies and installs control0x2A6220, regular
Glide constructor0x2B26C0 and native state2 displacement0x2AF6A0 hooks. It admits
all anchors and obtains all code-page protections before patching any entry.
The control trampoline relocates the RIP cookie load; the Glide trampoline
relocates its common constructor call. The16-byte movement span is entirely
position independent and preserves its TEST flags before resuming native code.
Outside admitted504, all three original functions pass through.

On a fresh free-air Circle, native state setter0x2B1960 selects fall callbacks,
then native queue0x29F980 restarts fall10 with504 body. The native input command
predicate remains the checked low-byte/bit24 test. A held takeoff cannot retrigger;
landing rearms once per airtime. Deferred cached Glide selection is blocked only
for that live session. Native controller commands and busy actions interrupt it.

Movement borrows the supplied Master begin_aerial_dodge structure: neutral up,
normalized stick travel, held arc, finite action, native fall handoff. Exact KH2
growth values are absent from the supplied extract. The separately documented
96/6/.75 values are KH1 test tuning, without the v52 style's2x distance multiplier.
The callback returns requested displacement before KH1's collision pass. It never
writes actor+10 position. Native wall/ceiling/floor/collision callbacks remain.
A release caps upward speed; the native ceiling bit clips lift. At normal handoff,
arc values are reset to the actual actor Y, and fall506 resumes. No defense or
hitbox import is added. This is not a full source-identical Master port.

Glide retains Aqua350 throughout start/held middle/closing. Native current and
queued visual clocks cap40 after the opening, including direction changes. No
native Sora body is republished during flight. Native Glide physics/unlocks are
untouched. 350 stop uses the fall overlay, then506 returns on end/interruption.

Run refinement: aqua_refine_v16 lifts head151 by12 degrees only on slots5/6/7
relative to the character's root-right axis. It preserves torso and local bind
hair, joint translations, scale, helper travel and all unrelated motions.
Previous run fixtures are frozen solely for independent geometry comparison.

IDs117..121, exclusivity, idle transactions, original request pointers, keyblade
tip attachment0x30, wrist and limb refinements and native defensive windows stay.
Current mappings are the root CSVs; source event timing is in validation JSON.
Previous plan/refiner modules are retained as explicit build dependencies.
Existing upstream license files remain in licenses.
