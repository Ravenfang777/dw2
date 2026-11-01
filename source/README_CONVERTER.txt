OFFLINE CONVERTER / REBUILD

Requirements: Python 3.10+, numpy, scipy, Pillow.
Install the dependencies in your Python environment with:
    python -m pip install numpy scipy Pillow

Use your own extracted inputs in this workspace layout:
    AquaWork/core_source/p02ex00.pmo
    AquaWork/core_source/p02ex_001.pam
    AquaWork/sora_source/Custom Movesets KH1/xa_ex_0010.mdls
    AquaWork/sora_source/Custom Movesets KH1/xa_ex_0010.mset
    AquaWork/sora_source/Custom Movesets KH1/xa_ex_0010_he.mset

The donor PMO and PAM come from data/bbs/arc/pc/p02base.arc. The inspector's
read_arc function can extract this container. Original donor files and original
KH1 inputs are not duplicated in this package. Input SHA-256 hashes are recorded
in the validation reports; keep original inputs separate from modified outputs.

From the directory containing these Python scripts:
    python -m unittest discover -s . -p "test_*.py" -v
    python build_aqua_motion_test.py --workspace "D:/AquaWork"
    python build_aqua_motion_test.py --workspace "D:/AquaWork" --source-name xa_ex_0010_he.mset --report-name validation_olympus.json
    python render_aqua_test_preview.py --workspace "D:/AquaWork"

The builder writes assets and validation into AquaWork/KH1FM_Aqua_Motion_Test_v1.
The renderer requires the completed normal validation report.

IMPLEMENTATION
- 54-joint Aqua PMO local bind matrices calibrate 63 roles on Sora's 293-joint
  MDLS. Sora retains his own segment lengths and the checked native secondary
  rest pose. The mapping is explicit in build_aqua_motion_test.py.
- Donor local animation curves become native helper FK curves. Constant helper
  children apply bind-basis calibration. Native body copy-rotation constraints
  use these helpers, avoiding animated Euler conversion across rigs.
- A support-height correction transfers crouches and Cartwheel hand support;
  it is adaptively sampled into Sora's root-Y body channel. It does not add a
  new collision, movement, or IK runtime system.
- The original helper hierarchy, original key references, motion durations,
  control/event bytes, and later MSET sections remain. A duplicate of the old
  final helper supplies the original native root-movement output.
- Logical requests resolve through each MSET's real second-section remap,
  preserving all remap flags. The normal and Olympus maps are resolved separately.
- New motion records are appended to MMTN and the relevant offsets updated.
  Later MSET sections are relocated with their contents unchanged.
- Source rotation tracks bounded by +/-pi unwrap across seams before fractional
  sampling. Explicit source winding outside that range is retained.

VALIDATION
The builder checks mapped bind calibration, segment lengths, unchanged action
maps and unrelated motion prefixes, native root-helper output, and decoded
integer/fractional poses against independent donor-to-Sora matrix evaluation.
The two JSON reports describe the exact generated assets and source hashes.
These checks do not emulate the game's asset loader or prove gameplay behavior.

CREDITS / LICENSES
The native KH1 motion evaluator is adapted from the user's v52 source file
crates/kh1-data/src/native_mset.rs, from their local derivative of
JamesPMx / PM2CRAZY, KH2-Combat-in-KH1:
https://github.com/PM2CRAZY/KH2-Combat-in-KH1
Upstream base commit: 4adb946b642f6b9bd84f83d12ec16944e0638b8b
User-provided v52 derivative commit: 54d18b73d6b4359476e97a887332fefcc44a5cdd
The converter and Python adaptation were added by OpenAI Codex for this test.
The original MIT OR Apache-2.0 licenses and upstream notice are in licenses/.
NOTICE.upstream.txt describes the earlier upstream project, not the contents
or tested features of this standalone package.

BBS format references: OpenKH Team and contributors:
https://openkh.dev/bbs/file/type/arc.html
https://openkh.dev/bbs/file/type/pam.html
https://openkh.dev/bbs/file/type/pmo.html
OpenKH mod manifest reference:
https://openkh.dev/tool/GUI.ModsManager/creatingMods.html

The source-code licenses do not grant rights to Kingdom Hearts game assets.
This private prototype contains modified assets derived from the user's
provided files. Kingdom Hearts belongs to Disney / Square Enix.
