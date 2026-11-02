AQUA V8 SOURCE

Normal installation needs OpenKH/Panacea; these scripts are development files.

BUILD AND TEST THE WINDOWS DLL ON A LINUX X64 HOST
From this source directory:
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
The DLL builder uses Python, GCC and GNU ld with i386pep support. Visual tests
also need NumPy and SciPy. Runtime tests map and execute the actual PE with
Win64 ABI mocks. No Windows/game execution is claimed.

REGENERATE MOTION FIXTURES
  python3 retargeting/tools/build_aqua_complete_v8.py .
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
Requires NumPy, SciPy and Pillow. The supplied model/animation inputs are under
retargeting; original MSET inputs are ../assets. Optional numeric normal slots
after the output directory rebuild only those slots. Sampling caches are not
distributed. V8 first builds an immutable V7 baseline and then applies
aqua_refine_v8.py once before fitting. Rebuilding never compounds corrections.

HAIR AND CLEARANCE
Hair joints 155..193 use model bind rotations. The jaw and grip are preserved.
Bounded two-link arm/leg solves adjust goals/poles while preserving segment
lengths and local scales/offsets. Airborne hand goals are retained for ledges.
The frozen V7 clearance reference stores 21 samples per motion for eight
joints; per-motion SHA-256 values identify the original V7 fixtures. Independent
tests compare the serialized V8 joints against that reference. Capsule overlap
is a geometric proxy, not a guarantee of mesh separation in the game.

HAND MAGIC
aqua_magic.h admits the exact 15/16-byte instruction spans at Steam RVAs
0x29EA00 and 0x29EB20 from the user-supplied executable. These spans contain
complete instructions with no relative branches/calls or RIP-relative data.
Two native trampolines redirect logical weapon attachment 0x30 only when the
current loaded Sora and motion bank match an enabled Aqua bank, the request is
0x36..0x3D or 0x83..0x8A, and event/script scope is clear. Other actors, other
attachments, other actions and unequipped Aqua fall through to the original.
Native direct-matrix selector 0x2065 reads right-palm world matrix 101. Position
queries use that matrix's translation; effect-matrix queries use the matrix.
The native projectile/effect VM remains responsible for simulation and drawing.
The executable is not included. native_attachment_validation.json records its
hash, build timestamp, entry spans and reviewed selector semantics.

INVENTORY
retargeting/tools/build_aqua_inventory_v8.py reads the originally supplied
core_source, input, round2_regular, round3_regular and captured PC p02 banks.
Unused gameplay and cinematic assets are not required to run this mod and are
not copied into it. To rebuild the complete inventory, provide those source
folders again. The complete generated inventory and all source occurrences are
in ../inventory. The optional workbook builder requires @oai/artifact-tool.

CAPACITY AND LICENSING
All native motion headers, lengths and counts are unchanged. Body flags,
constants, channels and reusable key storage implement the poses; helper
hierarchy and native travel remain. The gate admits every applicable record
before writes and defers ability switches until idle. Existing source
licenses/notices are preserved in licenses. Nine Styles / Dual Wield is not
included or required. Format reference:
https://openkh.dev/bbs/file/type/pam.html
