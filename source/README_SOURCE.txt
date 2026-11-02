AQUA V14 DEVELOPMENT SOURCE

BUILD / CHECK (Linux x64)
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
Requires Python, GCC and GNU ld with i386pep support. Geometry checks also
require NumPy/SciPy. The runtime host maps and executes the actual emitted PE
exports and checked detour/trampoline code; native game control/queue bodies
are mocked. It is not a Windows/KH1 run.

REBUILD FITTED POSES (optional; NumPy/SciPy/Pillow)
From this source directory:
  python3 retargeting/tools/build_aqua_complete_v14.py --profile 0 --output .
  python3 retargeting/tools/build_aqua_complete_v14.py --profile 1 --output sets/p1
  python3 retargeting/tools/build_aqua_complete_v14.py --profile 2 --output sets/p2
  python3 retargeting/tools/build_aqua_complete_v14.py --profile 3 --output sets/p3
  python3 retargeting/tools/build_aqua_complete_v14.py --profile 4 --output sets/p4
  python3 retargeting/tools/build_aqua_complete_v14.py --profile 5 --output dodge
  python3 retargeting/tools/build_aqua_complete_v14.py --profile 6 --output glide_stop
Then regenerate data, build and run the two checks above.
--slots followed by normal slot numbers rebuilds only those records.
The package builder resolves exported source paths separately from the working
project. Original MSET files are ../assets; the model is under
retargeting/sora_source. PAM/PMO/ARC inputs are under retargeting/core_source.
Baseline sampling caches can be regenerated and are not distributed.

MAIN-ONLY BODY VARIANTS
Main physical54/57 use391[0,31]/[31,48],79/82 use316[0,20]/[20,30],56 uses427,
and81 uses318. Main99/100 use365 and103 uses371. The v14 plan inherits the
remaining v13 actions and exact Test4 source choices. Each numbered profile
retains six extra v13 spell records as immutable overrides alongside its seven
combo records. Payloads are deduplicated in aqua_data.h. There are51 usual
normal records or50 Olympus records per profile; the original11 helpers,
header scalars, table lengths, allocations and native helper travel remain.
Existing wrist/hair/rotation-only limb refinements remain.

MAIN-ONLY REQUEST LOOKUP
Each bank has original, numbered and main request-table variants, all1408bytes.
Numbered profiles retain only Thunder38/85 rerouting. Main additionally maps
Stop/Aero3B/3C from normal56 to55 (Olympus19 to18), and88/89 from normal81 to80
(Olympus43 to42). Native flags and other request words are preserved. Original
tables are never written. cast_admit recognizes either owned copy only for
the tracked actor/bank, retaining its exact original pointer. All body/lookup
switches wait for idle and restore exactly. Foreign data blocks writes.
Stop/Aero now use Gravity's existing86/78 native-frame records, previously68/68.
No spell logic, MP, targeting or event-track data is replaced.

DODGE504: USER LOG AND NATIVE BRANCH EVIDENCE
kh1-aqua(3).log recorded24 decisions:18ground exclusions, five airborne
mask0x100 exclusions, and one airborne mask0x140 including a busy closing pose.
The five clean attempts had state2,request0xA,count1,held6,pressed6 and
command0x03000000. None accepted504. V13 rejected that exact replay too.
The native function0x2A6220 at0x2A629A tests byte[command+3]&1. A SET bit skips
command dispatch. Otherwise0x2A62F8 checks the low byte for nonzero and calls
0x2A7510 at0x2A6307. V13 had this exclusion backward. V14 rejects exactly:
  (command &0xFF)!=0 && (command &0x01000000)==0
The logged0x03000000 now permits504. Tests cover all profiles/banks, a native
Glide fallback when Jump is not consumed, and delayed native fall commits.
Busy actions, incompatible queued motions, menus/scripts, unsafe memory and
native can-act exclusions remain. Current code uses the same checked control
hook0x2A6220, can-act0x297870 and queue0x29F980. No new hooks are added.
The17-byte control span includes one RIP-relative cookie load, relocated via
0x554A88. Exact spans and the supplied executable hash are in the JSON evidence.
The game executable and uploaded user log are not distributed.

Air input rejection bits retain their v13 meaning except0x100 now denotes
an actual native command-dispatch candidate (the predicate above). Other bits:
0x001scope,0x002used,0x004not armed,0x008state,0x010height,0x020stick,0x040busy
motion/Glide,0x080shortcut,0x200queued motion,0x400native can-act,0x800admission.
504 temporarily supplies the known fall body; always queues native fall6 at0;
waits up to16 controller checks for commit; ends at39, loop, landing or interrupt.
The callback masks only logical Jump bits6 around original control and restores
only those bits, keeping unrelated native input changes. Native state, velocity,
gravity, collision and defense remain. No BBS travel or invulnerability is added.

RETAINED FEATURES
Glide350 uses source0..20 over the first40 native frames, holds source20 while
Glide continues and carries pose progress through native direction changes.
The controller validates the affected Glide body before pose-clock/queued-frame
writes. Native fall6 after Glide temporarily uses350[20,40], then506. Source
and native branch details are in glide_validation.json. The existing input
hook remains active with air_dodge=0 to support these phases.
LEFT-palm206 casting selector0x20CE, item007/395, movement, Guard/Cartwheel,
reactions, falling506, zero-AP ids117..121, exclusive selection and exact
idle-only body/lookup restoration are retained. The normal48-byte ability list
is not expanded and no native entry is evicted. Existing licenses remain.
Source choices and ranges are in aqua_v14_plan.py and the root CSV files.
The frozen V8 comparison covers unchanged source actions only; geometry checks
do not render the mesh or prove collision clearance in gameplay.

Existing upstream notices are retained in licenses.
Format reference: https://openkh.dev/bbs/file/type/pam.html
