AQUA V17 SOURCE / REPRODUCIBILITY

Build DLL on Linux with Python3, GCC and GNU ld PE support:
 python3 generate_data.py
 python3 build.py
 python3 test_runtime.py
 python3 test_visuals.py
NumPy/SciPy are needed for pose fitting/geometry. Runtime tests map the actual
emitted PE with Win64 ABI/import mocks; they are not Windows/KH1 execution.

Optional source pose rebuild from this source directory:
 python3 retargeting/tools/build_aqua_complete_v17.py --profile 0 --output .
 python3 retargeting/tools/build_aqua_complete_v17.py --profile 1 --output sets/p1
Profiles2..4 use sets/p2..p4;5 uses dodge;7 uses blizzard. No profile6 Glide
closing overlay exists in v17. The builder resolves its model/PAM/ARC inputs
below retargeting, with original MSETs in ../assets. --slots limits records.
The immutable sampling baseline is refined once. Regenerate data, rebuild and
run checks after changing fixtures. Previous plan/refiner modules are explicit
dependencies, not the current behavior. The v17 CSVs and plan are authoritative.

Main ground300/300/366; air305/407/351. Both99/100 use300 and complete it at
native32/44 before kind5 chain windows32..48/44..64. Contact times are selected
from the first300 pose's12/47 phase:384/47 and528/47 native frames. First98
retains contact12 and chain22..40. Existing event payloads, descriptors, counts,
encoded handles and sound/effect keys stay original. Only existing hit/chain
frame floats change for main98/99/100; numbered tests use native event timing.
The actual native event sampler0x394770 is exercised by the runtime tests.

Default Glide:75..78 are absent from the47-record Aqua patch table. There are
no Glide body writes, clocks, queued-frame edits, opening/holding/closing state,
350 fall overlays or extra endings. The only remaining Glide hook is the
existing constructor guard for active504; every other call resumes native code.
Tests populate independent original Glide records in both mock banks and verify
all bytes, clocks and queued start frames through all five profiles and turns.

Dual D2x: the earlier v52 log recorded growth height145 and speed18. The supplied
NineStyles_v52.patch aerial_dodge_step multiplies displacement by2 while leaving
timing unchanged. V17 stores unscaled145/18 baseline motion and applies2 to all
requested XYZ displacement and handoff velocity values. The existing40-frame504
visual and once-per-airtime/free-air input policy remain. The KH1 gravity/release
adapter (.75 /4 /20 baseline) remains explicit: exact KH2 coefficients and motion
202's length are absent, so this does not claim a complete KH2 controller import.
Native collision resolves the displacement. No actor+10 position writes occur.

Run head fix: native MDLS link word bit30..31 identifies skinned bones. Joint150
has skin flag1; helper151 has flag0. V16 incorrectly added lift at151, moving
hair without the skull. V17 refines only run5/6/7: transfer the authored source
head5 orientation (formerly mapped to151) to150 and restore151's bind rotation.
Skull150 and the attached subtree then follow the same head. No torso/neck,
attachment translation, bind length, scale or travel change is introduced.
The geometry test compares the REAL skinned skull150 to independent frozen
pre-v16 authored-head fixtures, and checks the raw native skin flags/hair local.

Blizzard remains the v16 selector: logical37/84 and original native event tracks
stay; main casts temporarily receive full391/316 bodies in55/80. No native spell
queue append, terminal reordering, projectile/MP hook or element change exists.
Restore the shared317/390 pose on the next action, off or profile transition.
Keyblade-tip attachment0x30, original native defensive windows and all numbered
combo/cast fixtures remain. Five saved zero-AP IDs117..121 remain exclusive.

Native hook anchors and source/log evidence are in the validation JSON files.
The original Steam Global EXE timestamp1721645006 has SHA256
 d790746245d26159f3ee0e1060e33b2fa2de06941850a4ac724f598722884bac.
Its full bytes and the user's video/log are not redistributed. Existing upstream
licenses remain in licenses. Test limits are stated in README_FIRST.txt.
