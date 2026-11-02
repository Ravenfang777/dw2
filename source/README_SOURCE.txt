AQUA V10 TEST 2 SOURCE

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
  python3 retargeting/tools/build_aqua_complete_v10.py --profile 0 --output .
  python3 retargeting/tools/build_aqua_complete_v10.py --profile 1 --output sets/p1
  python3 retargeting/tools/build_aqua_complete_v10.py --profile 2 --output sets/p2
  python3 retargeting/tools/build_aqua_complete_v10.py --profile 3 --output sets/p3
  python3 retargeting/tools/build_aqua_complete_v10.py --profile 4 --output sets/p4
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
Finisher clearance checks include interior arm samples. All local anatomical
offsets/scales retain their bind values. The V8 reference contains 41 samples
of ten joints per original converted motion; it supports an independent
before/after comparison of serialized forearm clearance. It is not mesh
collision detection. Hair155..193 retains the v8 bind-rest correction.

FIVE PROFILE GATE
The generated header stores original tables and five immutable after sets.
Unchanged profile blocks are shared. All 47/46 records are admitted against
the known original/base/test sets before any writes. Selection changes wait
for idle. Ability ids117..121 are 0 AP. Newly enabled Aqua entries win and
only other Aqua entries are turned off. Missing entries are granted only if
all fit with a terminator in the original 48-byte list. Native entries are
not evicted. Uninstall removes only ids117..121.

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
The donor selection is in aqua_v10_plan.py. Numeric IDs retain their exact
source bank/hash in TEST_CLIP_SOURCES.csv; no command names are inferred.
The source inventory files under ../inventory retain v8's source metadata.
Current ability mappings are ../ANIMATION_MAP.csv.

Existing upstream licenses and notices are retained in licenses.
Format reference: https://openkh.dev/bbs/file/type/pam.html
