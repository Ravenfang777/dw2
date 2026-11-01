AQUA V6 SOURCE AND OFFLINE VALIDATION

Normal installation needs only OpenKH/Panacea and the files selected by mod.yml.
No Python/compiler is needed to play the test.

CONTROLLER BUILD (Linux x64 development host)
From this source directory:
    python3 generate_data.py
    python3 build.py
    python3 test_runtime.py
Requires GCC, GNU ld with i386pep, and Python 3.12 standard library.
The build converts GCC ELF relocations to AMD64 COFF, creates Kernel32 imports
and links a Windows PE32+ DLL. The test maps that actual PE, relocates it and
executes its exports with MS x64 ABI host stubs. This is not a Windows test.
Copy the built kh1-aqua.dll into the package's dll folder only after checks pass.

The fixtures are complete original and converted native motion records. The
header generator verifies that their lengths and 80-byte headers match, then
emits exact before/after versions of five existing tables: flags, body channel
descriptors, key records, body constants, and helper channel descriptors.
The DLL admits all nine motions before writing any of them. Runtime header
pointers may be relative or native encoded handles; their storage is retained.

BODY RETARGET GENERATION (optional)
Requires NumPy, SciPy and Pillow in addition to Python. The user-provided PMO,
PAM and original Sora model are included under retargeting. The generator uses
the original MSETs in ../assets as input, so it can rebuild from this package:
    python3 retargeting/tools/build_aqua_compact_fk.py .
Then rerun generate_data.py, build.py and test_runtime.py above.
The retarget generator's pose sampling cache is reproducible and not packaged.

The fit preserves all native counts and allocation sizes. Unused helper channels
are neutralized and their existing key capacity is reused for FK body curves.
The travel helper and every ancestor keep their original channels and keys.
No helper hierarchy is expanded. Existing body channels/constants become the
compact FK animation; unused body channels are harmless repeated unit-scale
curves. Every original byte is available for restoration when aqua is off.

MAPPING AND LIMITS
C8/C9/CA/CB -> Aqua 300/301/302/304 ground records.
CC/CD/CE -> Aqua 305/306/309 aerial records.
D4 -> Aqua 400 Barrier pose; DC -> Aqua 009 Cartwheel pose.
These are visual action assignments using the native KH1 action map. KH1 still
selects chain steps/finishers and supplies timing, hits, guard coverage, dodge
travel/invincibility, sounds and effects. No BBS gameplay engine is included.
The sparse fixed-capacity fit approximates donor rotations; curve_validation.json
records measured errors. Neither the preview nor the mock host tests is a game
execution. Live Windows/KH1 compatibility remains to be tested by the user.

The runtime addresses and ability interface were derived from the user's v52
reference and Lua controllers. Existing source/notice licenses are retained in
licenses. The old kh1-dual-wield.dll is not included or required by this build.
