AQUA V7 SOURCE

Normal installation requires OpenKH/Panacea only. These development scripts
are not required to play the test.

BUILD THE WINDOWS DLL ON A LINUX X64 DEVELOPMENT HOST
From this source directory:
    python3 generate_data.py
    python3 build.py
    python3 test_runtime.py
Requires Python 3.12 standard library, GCC and GNU ld with i386pep support.
The builder converts GCC ELF relocations to AMD64 COFF, creates Kernel32
imports and links a PE32+ DLL. The runtime test maps that actual PE image,
relocates it and executes its exports with mocked MS x64 ABI host functions.
It does not run Windows or Kingdom Hearts.

REGENERATE THE RETARGETED MOTION FIXTURES (OPTIONAL)
Requires NumPy, SciPy and Pillow. The supplied original Sora model and Aqua
PMO/PAM/ARC inputs are under retargeting. Original MSET inputs are ../assets.
From this source directory:
    python3 retargeting/tools/build_aqua_complete_v7.py .
    python3 test_visuals.py
    python3 generate_data.py
    python3 build.py
    python3 test_runtime.py
An optional list of normal slots after the output directory rebuilds only
those slots and merges their results into the existing curve_validation.json.
Sampling caches are reproducible and are not included in this package.

V7 DEFORMATION AND TRANSITION CHANGES
aqua_retarget_v7.py restores bind translations for anatomical/cloth joints,
retains checked native face/finger/grip turns and resets inherited cloth folds.
Supported stances receive a bounded two-link leg correction for Sora's boots;
the solve does not change lengths or scales. The mapper uses Aqua's source
poses throughout each action instead of blending toward Sora inside the clip.
Loop closure removes native travel before matching body endpoints. The normal
and high-jump takeoff/rise records use contiguous source ranges. Ledge poses
anchor Aqua's left palm to the native right-palm grip point; the last climb
phase gradually returns to the native root trajectory.

CAPACITY AND REVERSIBILITY
All motion headers, file/record lengths, bone counts, channel counts, constant
counts and helper counts retain their original values. The body uses FK inside
those allocations. Unused helper channels are neutralized to reuse their key
space; the native travel helper and every ancestor retain their tracks and keys.
The generated header contains before/after versions of five existing tables:
body flags, body channels, keys, constants and helper channels. Original header
pointers may be relative or native handles; their runtime storage is retained.

The controller identifies the bank with C8 because both banks have identical
idle/walk prefixes. It validates every applicable record before any body writes.
The normal-only ledge recovery is skipped in Olympus. Selection changes wait
for idle. Cached frame checks validate shared readable ranges, native header
handles/scalars, table pointers and changed-word sentinels. Fragmented tables
retain a checked fallback. Unknown data blocks publication/restoration writes.

VALIDATION AND LIMITS
test_visuals.py checks serialized geometry, skin bases, supported stance width,
loop closure, jump handoff, left-hand ledge contact and native travel. The fit
report measures all quarter frames. test_runtime.py executes the actual DLL and
checks exact reversibility, bank changes, fragmented tables, ability handling,
uninstall, query overhead and rejection of foreign data. Neither validates the
rendered game mesh. V7 needs a live user test.

ANIMATION_MAP.csv and REMAINING_NATIVE.csv in the package root define the scope.
Casting poses are shared visual assignments; native combat/effect rules remain.
The user's v52 reference and Lua controllers supplied the runtime address and
ability-interface evidence. Original source licenses/notices are in licenses.
The old kh1-dual-wield.dll is not included or required.

FORMAT REFERENCE
https://openkh.dev/bbs/file/type/pam.html documents the source frame, channel
and loop fields used by the decoder. Native KH1 constraint semantics follow
the user-provided native_mset.rs reference retained in the project history.
