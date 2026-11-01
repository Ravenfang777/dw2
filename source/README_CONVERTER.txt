AQUA ARM PROBE v4 - OFFLINE BUILDER

Requirements: Python 3.10+, numpy, scipy, Pillow.
    python -m pip install numpy scipy Pillow

Input layout (original files, not v1/v2 modified outputs):
    AquaWork/core_source/p02ex00.pmo
    AquaWork/core_source/p02ex_001.pam
    AquaWork/sora_source/Custom Movesets KH1/xa_ex_0010.mdls
    AquaWork/sora_source/Custom Movesets KH1/xa_ex_0010.mset
    AquaWork/sora_source/Custom Movesets KH1/xa_ex_0010_he.mset
The PMO/PAM are from data/bbs/arc/pc/p02base.arc, supplied in the source capture.

Run from the folder containing these scripts:
    python build_aqua_arm_probe.py --workspace "D:/AquaWork"
Output: AquaWork/KH1FM_Aqua_Arm_Probe_v4, assets plus validation/expected hashes.

WHY THIS PROBE DIFFERS
The user's restore test loaded the original Sora movesets; Aqua v2 still
failed on loading and displayed bad positions on a backup save. V2's offline
solver checks did not establish compatibility with the native asset loader.
The exact native failure has not been identified.

V4 edits only FLOAT DATA within six existing helper translation curves of
physical slot98 (request C8). Native wrist goals4/7 use Aqua300 arm vectors,
calibrated through each shoulder's frame, blended with the native trajectory
with a sin(pi*phase)^2 envelope. The original arm/clavicle solver stays active.
Reach is limited to the original arm length with a small margin. Existing key
times, interpolation modes, indices, counts and all file headers remain intact.
Both tangent fields receive the central derivative per 1/256-frame tick.
Endpoint key records are kept exactly. Shared curve keys reject the build.

No motion or helper is appended; no pointer, section boundary, flag, event,
constant, duration or table entry is rewritten. The Olympus file is copied
from the original input. Original actor root movement stays byte-identical.

VALIDATION
The script proves every changed byte lies in eligible existing wrist value/
tangent fields. All117 other motion records and the full later MSET sections
match the original bytes. A quarter-frame pose comparison checks that only
arm/clavicle descendants change and that root movement and the other body
matrices agree exactly. Arm reach and numeric bounds are checked.
These are offline checks. Native-game behavior still requires the user's test.

CODE AND FORMAT CREDITS
The native KH1 reader/evaluator follows the user's v52 native_mset.rs, from
JamesPMx / PM2CRAZY, KH2-Combat-in-KH1 (MIT OR Apache-2.0):
https://github.com/PM2CRAZY/KH2-Combat-in-KH1
Upstream base commit: 4adb946b642f6b9bd84f83d12ec16944e0638b8b
User v52 derivative: 54d18b73d6b4359476e97a887332fefcc44a5cdd
Python adaptation and this probe were added by OpenAI Codex.
The licenses and original upstream notice are in licenses/. The upstream
notice describes that separate project's scope, not this package's contents.

BBS format documentation by the OpenKH team and contributors:
https://openkh.dev/bbs/file/type/arc.html
https://openkh.dev/bbs/file/type/pam.html
https://openkh.dev/bbs/file/type/pmo.html

Game assets are from the user's supplied files. Kingdom Hearts belongs to
Disney / Square Enix. Source-code licenses do not license the game assets.
