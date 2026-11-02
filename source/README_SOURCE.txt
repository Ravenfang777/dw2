AQUA V12 TEST 4 SOURCE

Normal installation requires OpenKH/Panacea; these are development files.

DLL BUILD / EXECUTION CHECK (Linux x64)
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
GCC, GNU ld with i386pep support and Python are needed. Geometry checks also
need NumPy/SciPy. Runtime tests map the final PE and execute its real exports
and attachment detours against Win64 ABI mocks, not Windows or KH1.

REBUILD POSES (optional; NumPy, SciPy, Pillow)
From this source directory:
  python3 retargeting/tools/build_aqua_complete_v12.py --profile 0 --output .
  python3 retargeting/tools/build_aqua_complete_v12.py --profile 1 --output sets/p1
  python3 retargeting/tools/build_aqua_complete_v12.py --profile 2 --output sets/p2
  python3 retargeting/tools/build_aqua_complete_v12.py --profile 3 --output sets/p3
  python3 retargeting/tools/build_aqua_complete_v12.py --profile 4 --output sets/p4
  python3 retargeting/tools/build_aqua_complete_v12.py --profile 5 --output dodge
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
--slots followed by normal slot numbers rebuilds only those records in a
profile. Required source ARC files are in retargeting/core_source. Original
MSET files are ../assets. Immutable baseline sampling caches are reproducible
and are not distributed. V9 anatomical refinements are retained and applied once to each baseline.

ANATOMICAL WRIST PIVOTS
aqua_refine_v9.py keeps Sora's distal forearm helper angles at bind and applies
the hand's authored orientation at pivots100/205. Arm solves rotate the whole
distal forearm together and preserve the hand's orientation at that pivot.
Arm clearance includes interior arm samples. The new main ground finisher411
uses the normal correction envelope; the old304 finisher is no longer selected. All local anatomical
offsets/scales retain their bind values. The V8 reference contains 41 samples
of ten joints per original converted motion; it supports an independent
bounded-displacement checks for unchanged source actions only. New casts,
falling, finisher411 and the407/352/353 main air combo are excluded from that historical comparison. It is not mesh
collision detection. Hair155..193 retains the v8 bind-rest correction.

FIVE PROFILE GATE
The generated header stores original tables and five immutable after sets.
Unchanged profile blocks are shared. All 47/46 records are admitted against
the known original/base/test sets before any writes. Selection changes wait
for idle. Ability ids117..121 are 0 AP. Newly enabled Aqua entries win and
only other Aqua entries are turned off. Missing entries are granted only if
all fit with a terminator in the original 48-byte list. Native entries are
not evicted. Uninstall removes only ids117..121.

AIRBORNE AERIAL DODGE
The main plan remains47 normal /46 Olympus records. Profile5 of the retargeting
builder is a single non-looped504 variant of the existing fall record10.
generate_data.py stores this as AquaPart.dodge; admission accepts it and the
fast cache recognizes it only while the transient action is active.
aqua_air_dodge.h hooks Steam control0x2A6220 after exact17-byte admission. Its
trampoline copies the first10 bytes and rewrites the RIP-relative security-
cookie load as mov rax, imm64; mov rax,[rax], targeting original0x554A88.
The original control, can-act0x297870 and queued-motion0x29F980 bytes are
verified before installation. The last two functions are called, not hooked.
Fresh merged logical Jump/Circle bits6, any valid stick direction, free air1/2,
height>1, an admitted body bank and no busy/native queued action authorize504.
One use per airtime, armed after button release. Beginning from fall6 resets
only actor+16C to zero; beginning from rise queues native fall6. Native state,
velocity/gravity, collision and defense flags stay untouched. The control
call temporarily masks only Jump bits at pad+4/+8/+10/+14, then restores those
bits without undoing native changes to other buttons. Clock39, looping,
landing or interruption restores the normal506 pose. Unknown/unloaded records
are never restored by writing stale pointers. The action adds no invulnerability.
The native clock remains authoritative; waiting for a queued fall is bounded.
air_dodge_validation.json records original executable evidence. The test host
executes the real detour/trampoline and native can-act bytes; native queue and
control bodies are mocked. Actual Windows/KH1 testing remains outstanding.

ACTION CAST LOOKUP
Native Steam command handlers dispatch ground magic with 0x36+spell and air
magic with 0x83+spell. Thunder is index2, Cure index3. The supplied MSETs share
their physical record. aqua_cast_requests.h changes actor+1D8 to an immutable
1408-byte request copy while a verified Aqua profile is active. Only Thunder
moves to the alternate casting family (normal55/80, Olympus18/42); all other
request words and native flags remain. The original table is never written.
Native resolver0x2A01E0 reads that field (+8 from actor+1D0). All body and
request destinations must pass admission before writes; idle-only switching,
per-bank original pointers, foreign-pointer rejection and exact restoration
are tested. cast_request_validation.json records native instruction evidence
from the supplied executable. No new entry-point detour is used here.
Thunder therefore uses 86 ground / 78 air frames, instead of the shared
68/68 frames. Native per-record event tracks stay intact. Final spell timing
has not been tested in KH1. Blizzard/Gravity inherit317/390; Stop/Aero318/427.

LEFT-HAND MAGIC
The two native entry points and admitted instruction spans are unchanged from
v8. Their direct matrix selector is now0x20CE, the LEFT palm206, in all five
profiles. Native cast requests, current actor/bank, event/script exclusions
and native fallthrough are retained. No spell-resource or projectile script
is replaced. The supplied executable is not included; its original hash and
the entry spans are in native_attachment_validation.json.

CAPACITY / SOURCE IDS
No motion/header/table expansion is used. The cast lookup copy has the original
352 request words; only Thunder entries0x38/0x85 change their physical slot. The original eleven helpers and
native travel remain. Four sets change seven physical combo records each:
C8 first, C9/CA second, CB finisher, CC first air, CD second air, CE finisher.
The donor selection is in aqua_v12_plan.py. Numeric IDs retain their exact
source bank/hash in TEST_CLIP_SOURCES.csv; no command names are inferred.
The source inventory files under ../inventory retain v8's source metadata.
Current ability mappings are ../ANIMATION_MAP.csv.

Existing upstream licenses and notices are retained in licenses.
Format reference: https://openkh.dev/bbs/file/type/pam.html

TEST4 SOURCE VARIANTS
New requests carry source_sha256 and validate the exact selected PAM payload
before fitting. The sampling-cache name includes this identity. Aliases395,
051 and505 use the shared007/395,008/051 and060/505 inventory rows. Plain060
uses the separate40-frame p02ex_711.arc payload;052 uses the20-frame gameplay
clip. Prefer dedicated gameplay variants for045,353,399 and411. Required ARC
files, including xaa*.arc banks, are in retargeting/core_source. Exact choices
are source_selections.json; current assignments are the root mapping CSVs.
