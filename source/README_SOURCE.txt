AQUA V13 REVISED TEST 4 SOURCE

Normal installation requires OpenKH/Panacea; these are development files.

DLL BUILD / EXECUTION CHECK (Linux x64)
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
GCC, GNU ld with i386pep support and Python are needed. Geometry checks need
NumPy/SciPy. Runtime tests execute the actual emitted PE exports and native
entry detours/trampolines against a Win64 ABI mock host, not Windows/KH1.

REBUILD POSES (optional; NumPy, SciPy, Pillow)
From this source directory:
  python3 retargeting/tools/build_aqua_complete_v13.py --profile 0 --output .
  python3 retargeting/tools/build_aqua_complete_v13.py --profile 1 --output sets/p1
  python3 retargeting/tools/build_aqua_complete_v13.py --profile 2 --output sets/p2
  python3 retargeting/tools/build_aqua_complete_v13.py --profile 3 --output sets/p3
  python3 retargeting/tools/build_aqua_complete_v13.py --profile 4 --output sets/p4
  python3 retargeting/tools/build_aqua_complete_v13.py --profile 5 --output dodge
  python3 retargeting/tools/build_aqua_complete_v13.py --profile 6 --output glide_stop
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
--slots followed by normal slot numbers rebuilds only those records. Required
source ARC files are in retargeting/core_source. Original MSETs are ../assets.
The builder supports an already exported source tree. Its package root,
source_arcs and sora_source paths resolve against this directory via the
inherited retargeting layout described below. Baseline caches can be rebuilt;
they are not distributed. Anatomical refinements run once per immutable baseline.

EXPORTED RETARGETING LAYOUT
retargeting/tools contains the v13 builder and its plan/dependencies. The
exported builder defaults to the bundled assets when run from this directory;
its source directory is found relative to its script. See the paths used by
build_aqua_complete_v13.py. No original game EXE is included.

FIVE PROFILE GATE / CAPACITIES
All51 normal or50 Olympus records verify against the exact original or known
Aqua variants before initial body writes. Header sizes, frame counts, allocation,
body/helper counts, the eleven helpers, hierarchy and native helper travel remain
original. Five immutable profiles share unchanged blocks; four numbered sets
replace seven physical combo records each (C8,C9/CA,CB,CC,CD,CE).
Source hashes distinguish variants; cache identities include source hash,
source range, loop/root policy and the Glide time mapping.
The builder pins a knot at native frame40 for Glide's static held pose.

Ability ids117..121 are zero AP. Newly enabled Aqua entries win and only other
Aqua entries turn off. Missing entries are granted only if all fit with a list
terminator in the original48-byte list. Native entries are never evicted.
Switching/restoration waits for idle. Unknown data blocks writes. Reloaded banks
are re-admitted; original body/request pointers restore when Aqua is off.

AIRBORNE CIRCLE504
AquaPart.dodge stores the fitted non-looped504 variant of fall slot10. The
native control0x2A6220 entry is admitted against17 exact bytes. Its trampoline
copies10 bytes, relocates the RIP-relative cookie load using original0x554A88,
then jumps to original+17. Native can-act0x297870 and queue0x29F980 signatures
verify before installation; these functions are called, not detoured.

The v12 already-falling route wrote actor+16C=0 without a queued motion restart.
V13 always calls native queue(actor,6,0). Pending actions wait up to16 controller
checks while the native request remains queued, even when current request is
already6 and its old fall clock is late. No sentinel physical-slot writes or
native state/velocity changes are used. A queue timeout, foreign data, landing,
interruption or ability-off restores the known506 body without stale writes.
The broad command-low-byte exclusion is narrowed to native committed bit
0x01000000. Fresh Jump bits6 at pad+8 are accepted after release even when pad+4
is already clear. Any finite valid stick direction is accepted. One504 use
per airtime; landing rearms. Logical Jump bits at pad+4,+8,+10,+14 are masked only
around original control, then those bits are restored without undoing native
changes to other buttons. Native gravity, collision and defense remain.

The log records first arrival at the Sora native control callback and the first
24 input decisions. AIR INPUT rejection mask bits:
  0x001 scope/actor/bank/profile/event/menu/script exclusion
  0x002 used this airtime or504 already active
  0x004 button release has not armed the action
  0x008 native state is not1/2
  0x010 invalid height or height<=1
  0x020 invalid direction/tilt
  0x040 busy motion, Glide or Glide closing pose
  0x080 shortcut or conflicting held button
  0x100 committed native command
  0x200 incompatible queued motion
  0x400 native can-act rejected
  0x800 fall-body admission or writable queue fields rejected
Zero means accepted. The queued native restart completion is logged too.
No current in-game log was supplied to confirm the original failure's cause.

GLIDE350
The actual native state21 Glide constructor0x2B2D30 requests0x71. Native direction
handling selects71/72/73/74 (aliases76/77/78/79 share the same physical records).
Normal slots75..78 match Olympus37..40 byte-for-byte. BC/BD/BE are not substituted.
Glide release at0x2B2CD1 requests native fall6; there are no separate start/stop
Glide records for this route. glide_validation.json records the executable evidence.

V13 fits source350[0,20] into the first40 native frames of each Glide record,
then holds source20 for the rest. During admitted Glide, the controller caps
the native pose clock at40 and carries progress into queued directional motion
start frames. This prevents takeoff from replaying when steering or looping.
The controller validates the exact affected Glide body before clock/queue writes.
Glide exit into native fall6 uses AquaPart.glide_stop, source350[20,40], on the
existing40-frame fall record. It queues a native fall restart, restores506 at
clock39, and ends on interruption/landing/off. This extra pose and dodge504 are
mutually exclusive. Other mapped motion bodies remain unchanged.
The existing control hook is also installed with air_dodge=0 so native350 phases
can run while Circle504 is disabled. Native Glide ability admission, held-input
rules, state, horizontal movement, descent, collision and defense are untouched.
Clock changes control pose timing only. No extra native MSET records are created.

CASTING / LEFT HAND
Actor+1D8 points to an immutable1408-byte copy while Aqua is active. Only Thunder
requests38/85 move to the alternate existing casting records normal55/80 or
Olympus18/42. Native ground36+spell and air83+spell dispatch remains unchanged.
All other request words and flags remain; the original table is never written.
Fire316/391, Thunder317/390 and Cure318/427 retain the previous source assignments.
Thunder durations remain86/78 rather than shared68/68; final timing needs KH1.
Two existing attachment entry hooks route cast attachment0x30 to LEFT palm206,
selector0x20CE. Native spell scripts, MP, targeting and events remain native.
Exact entry spans and source EXE hash are in native_attachment_validation.json
and cast_request_validation.json. Foreign actors/actions fall through unchanged.

ANATOMICAL REFINEMENTS / SOURCE VARIANTS
V9 wrist pivots100/205 retain authored hand orientation; distal helpers95..99
and200..204 keep bind angles. Rotation-only limb solves preserve local segment
offsets/scales; hair155..193 keeps bind rotations. The frozen V8 reference checks
bounded displacements only for unchanged source actions. Current changed item,
second-ground, finisher, air-combo, fall and casts are excluded from that historical
comparison. This is not rendered mesh collision checking.
007/395 use the identical29-frame shared payload from p02ex_200.arc; gameplay395
is chosen. Other source choices use exact recorded payload hashes. Numeric IDs
are not official command names. Current assignments are the root CSVs; the
unchanged349-clip inventory retains its earlier metadata.

Existing upstream licenses/notices remain in licenses.
Format reference: https://openkh.dev/bbs/file/type/pam.html
