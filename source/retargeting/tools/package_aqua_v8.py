"""Build the reviewable OpenKH v8 test ZIP from validated local outputs."""
from pathlib import Path
import csv,hashlib,json,shutil,struct,zipfile

ROOT=Path(__file__).resolve().parents[1]
WORKSPACE=ROOT.parent
DEST=ROOT/'KH1FM_Aqua_Animation_Test_v8'

README='''KH1FM AQUA ANIMATION TEST v8
Steam Global / OpenKH Panacea

ABILITY: aqua (lowercase), 0 AP, id117

V8 CHANGES
- Restored Sora hair chains 155..193 to the model's bind rotations, removing
  five inherited idle-pose bends that were held through the Aqua animations.
- Added bounded wrist/elbow/knee clearance corrections. These preserve bone
  lengths and scales and reduce joint/capsule overlap in the offline samples.
  This is not full mesh self-collision; some contact may still need adjustment.
- Added experimental RIGHT-HAND magic attachment routing. During Aqua's native
  ground/air cast requests, weapon attachment 0x30 uses right-palm world matrix
  101. Both native attachment position and effect-matrix queries are handled,
  so spell origins and attached glow can follow the hand. The game still runs
  its own spell scripts, trajectories, targeting, effects, MP and damage.
- Included the complete current Aqua inventory: 349 unique animation payloads,
  739 source occurrences, source IDs, frames, FPS, timing, raw loop data,
  channel/key counts, source locators/hashes and identification status.

INSTALL
1. Fully close KH1.
2. Disable Aqua v7 and all older Aqua packages, Sora Restore Check v3, and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH, enable Aqua Animation Test v8, then Build and Run.
4. Load your usual save. Equip aqua while standing idle. Guard and Dodge Roll
   still require their native abilities. Unequip aqua while idle to compare.

FIRST TEST
Start with aqua OFF, then ON, then OFF while idle. With aqua ON:
- Check the hair from front, side and behind while idle and running.
- Check ground/air combos, Cartwheel and Guard for wrist/elbow/knee clipping.
- Cast Fire and Blizzard, then each other available spell on the ground and
  in the air. Check the RIGHT hand for the glow and launch point. Check that
  launched projectiles continue normally and companion casts still look normal.
- Unequip aqua while idle and repeat a spell to check native attachment behavior.
Repeat on the second save, and try a room transition and a save reload.

The new kh1-aqua.log beside the game EXE must start with ANIMATION TEST v8.
Successful body selection logs AQUA MOTIONS ENABLED and 0x2F normal / 0x2E
Olympus records. The magic installer logs AQUA HAND MAGIC READY; actual routed
queries log AQUA HAND MAGIC ORIGIN and/or AQUA HAND MAGIC MATRIX plus the
native request number. READY alone does not prove a spell used that route.
Return this NEW log and a short comparison video, including a cast where the
glow/origin remains incorrect if one does. The optional CHECK_AQUA_V8.cmd
checks installed hashes and writes Aqua_Animation_Check_v8.txt.

OPTIONAL HAND-MAGIC FALLBACK
To keep the v8 hair/limb changes with native spell attachments, copy
DISABLE_HAND_MAGIC_kh1-aqua.ini beside the game EXE and rename it kh1-aqua.ini.
Restart the game. Remove that INI and restart to test hand routing again.

MOVE INVENTORY
inventory/Aqua_Move_Inventory_v8.xlsx has filterable clip and KH1 assignment
tables. CSV and JSON copies are included. Source IDs retain leading zeroes.
The 349 entries are animation clips, including cinematic/event material;
they are not 349 identified gameplay commands. Names describe reviewed poses
or existing assignments. Provisional and unidentified clips are marked.
PAM numeric names alone do not establish official BBS command names.
Raw loop fields do not guarantee gameplay looping. Duration = frames / FPS;
the last sampled frame occurs at (frames - 1) / FPS.
The 47 current normal records use 32 unique source clips. Olympus has 46
copies; one ledge recovery exists only in the normal bank. ANIMATION_MAP.csv
lists assignments; REMAINING_NATIVE.csv lists unassigned native records.

SCOPE
V7's movement, jumping, ledges, casting poses, items, reactions, combos, Guard
and Cartwheel remain mapped. KH1 action timing, native travel, guard coverage,
dodge invincibility and combat rules remain in use. Barrier is still a Guard
pose. Per-spell BBS choreography has not been separated from the shared casts.
Hair and limb corrections apply only to mapped Aqua motions.

Both installed MSETs are your original files. The DLL validates all applicable
records and reuses their existing in-memory tables and key capacity. Headers,
lengths, counts, eleven helpers and native travel tracks retain their layout.
Two separately checked native attachment entry points supply hand magic.
Unknown function bytes leave native attachments active. Unequipping restores
the original motion tables and uses the native attachment behavior.

SAVE / REMOVE AQUA
You can compare without saving. Saving in-game may retain ability id117.
To remove it, copy REMOVE_AQUA_kh1-aqua.ini beside the game EXE, renamed
kh1-aqua.ini. Leave v8 enabled, restart and load each save to clean. Check for
AQUA ABILITY REMOVED, then save in-game to retain removal. Exit, remove the
INI, disable v8 and rebuild. Only id117 is removed.

VALIDATION
The included reports describe checks of serialized poses and execution of
the final PE DLL in a Win64 ABI mock host. They verify routing, scope, exact
on/off restoration, hair rest shape, bounded corrections, pose transitions,
original capacities and native travel. They do not run Windows/KH1 or render
Sora's mesh. V8 hand magic and appearance need the in-game test above.
'''

SOURCE='''AQUA V8 SOURCE

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
'''

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    runtime=json.loads((ROOT/'ability_v8/runtime_validation.json').read_text())
    geometry=json.loads((ROOT/'ability_v8/visual_validation.json').read_text())
    curves=json.loads((ROOT/'ability_v8/curve_validation.json').read_text())
    assert runtime['passed'] and geometry['passed'] and curves['passed']
    shutil.copytree(ROOT/'KH1FM_Aqua_Animation_Test_v7',DEST,dirs_exist_ok=True)
    shutil.rmtree(DEST/'preview',ignore_errors=True)
    for path in [DEST/'CHECK_AQUA_V7.cmd',DEST/'Check_Aqua_Animations_v7.ps1']:path.unlink(missing_ok=True)
    for n in ['aqua.c','aqua_magic.h','aqua_data.h','build.py','generate_data.py','test_runtime.py','test_bridge.c','test_visuals.py',
              'curve_validation.json','data_validation.json','runtime_validation.json','visual_validation.json','clearance_validation.json']:
        shutil.copy2(ROOT/'ability_v8'/n,DEST/'source'/n)
    shutil.copytree(ROOT/'ability_v8/fixtures',DEST/'source/fixtures',dirs_exist_ok=True)
    shutil.copy2(ROOT/'ability_v8/kh1-aqua.dll',DEST/'dll/kh1-aqua.dll')
    for name in ['build_aqua_complete_v8.py','aqua_refine_v8.py','build_aqua_inventory_v8.py','build_aqua_inventory_v8.mjs','package_aqua_v8.py']:
        shutil.copy2(ROOT/'tools'/name,DEST/'source/retargeting/tools'/name)
    (DEST/'source/README_SOURCE.txt').write_text(SOURCE)
    (DEST/'README_FIRST.txt').write_text(README)
    (DEST/'mod.yml').write_text('''title: KH1FM Aqua Animation Test v8
game: kh1
originalAuthor: Raven Fang concept; motion test by OpenAI Codex
description: >-
  The 0 AP ability aqua selects Aqua motions with restored hair rest shape,
  bounded limb clearance and experimental right-hand native spell attachments.
  Includes the 349-clip Aqua inventory. Steam Global / Panacea; disable older
  Aqua packages and Nine Styles / Dual Wield.
assets:
- name: dll/kh1-aqua.dll
  method: copy
  source:
  - name: dll/kh1-aqua.dll
- name: xa_ex_0010.mset
  method: copy
  source:
  - name: assets/xa_ex_0010.mset
- name: xa_ex_0010_he.mset
  method: copy
  source:
  - name: assets/xa_ex_0010_he.mset
''')
    (DEST/'DISABLE_HAND_MAGIC_kh1-aqua.ini').write_text('[aqua]\nhand_magic=0\nremove_aqua=0\n')
    (DEST/'REMOVE_AQUA_kh1-aqua.ini').write_text('[aqua]\nremove_aqua=1\nhand_magic=0\n')
    checker=(ROOT/'KH1FM_Aqua_Animation_Test_v7/Check_Aqua_Animations_v7.ps1').read_text().replace('v7','v8').replace('CHECK_ABILITY.cmd','CHECK_AQUA_V8.cmd')
    (DEST/'Check_Aqua_Animations_v8.ps1').write_text(checker)
    (DEST/'CHECK_AQUA_V8.cmd').write_bytes(b'@echo off\r\nsetlocal\r\npowershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check_Aqua_Animations_v8.ps1" %*\r\npause\r\n')
    inv=DEST/'inventory';inv.mkdir(exist_ok=True)
    for path in (ROOT/'inventory_v8').glob('*'):
        if path.suffix in ['.csv','.json']:shutil.copy2(path,inv/path.name)
    shutil.copy2(WORKSPACE/'outputs/aqua_v8/Aqua_Move_Inventory_v8.xlsx',inv/'Aqua_Move_Inventory_v8.xlsx')
    shutil.copy2(WORKSPACE/'outputs/aqua_v8/spreadsheet_validation.json',DEST/'source/spreadsheet_validation.json')
    expected={'version':8,'assets':[]}
    for logical,actual in [('dll/kh1-aqua.dll',DEST/'dll/kh1-aqua.dll'),('xa_ex_0010.mset',DEST/'assets/xa_ex_0010.mset'),('xa_ex_0010_he.mset',DEST/'assets/xa_ex_0010_he.mset')]:
        expected['assets'].append({'name':logical,'sha256':sha(actual),'bytes':actual.stat().st_size})
    (DEST/'expected_assets.json').write_text(json.dumps(expected,indent=2)+'\n')
    exe=ROOT/'native_reference/Custom Movesets KH1/KINGDOM HEARTS FINAL MIX.exe'
    evidence={'user_supplied_executable_sha256':sha(exe),'executable_bytes':exe.stat().st_size,'timestamp':1721645006,
              'matrix_rva':'0x29EA00','matrix_stolen_bytes':'48895c24084889742410574883ec20',
              'position_rva':'0x29EB20','position_stolen_bytes':'405355574881ec800000000f29742460',
              'stolen_instructions_complete_and_without_rip_relative_operands':True,
              'logical_weapon_attachment':'0x30','direct_right_palm_matrix_selector':'0x2065','right_palm_index':101,
              'event_rva':'0x298C9A0','cast_requests':['0x36..0x3D','0x83..0x8A'],
              'runtime_mock_routes_both_attachments':True,'windows_or_game_executed':False}
    (DEST/'source/native_attachment_validation.json').write_text(json.dumps(evidence,indent=2)+'\n')
    inventory=json.loads((ROOT/'inventory_v8/Aqua_Inventory.json').read_text())
    validation={'version':8,'offline_checks_passed':True,'game_runtime_tested':False,'normal_motion_records':47,'olympus_motion_records':46,
                'hair_bind_rotation_joints':39,'inherited_hair_bends_reset':5,
                'pose_samples':sum(x['validated_pose_samples'] for x in curves['motions']),
                'max_pose_position_fit_error':max(x['max_pose_position_error'] for x in curves['motions']),
                'max_non_root_attachment_translation_error':max(x['max_non_root_attachment_translation_error'] for x in curves['motions']),
                'max_scale_error':max(x['max_scale_error'] for x in curves['motions']),
                'native_travel_error':max(x['root_helper_error'] for x in curves['motions']),
                'original_motion_lengths_headers_and_counts_preserved':True,'helper_slots':11,'original_msets_on_disk':True,
                'actual_pe_mock_tests':runtime['tests'],'geometry_transition_tests':geometry['tests'],
                'native_attachment_hooks':2,'hand_magic_game_rendering_verified':False,
                'unique_inventory_clips':inventory['unique_clips'],'source_occurrences':inventory['decoded_occurrences'],
                'dll_sha256':sha(DEST/'dll/kh1-aqua.dll'),
                'limitations':['Windows/KH1 rendering of v8 pending','Clearance uses joint/capsule proxies, not full mesh collision',
                'Hand routing handles attachment 0x30 in eligible native casts; per-spell use requires live confirmation',
                'Shared casting poses; per-spell BBS choreography not separated','Unassigned records remain native']}
    (DEST/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    with zipfile.ZipFile(DEST.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path in sorted(DEST.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:z.write(path,path.relative_to(DEST))
    print(json.dumps({'zip':str(DEST.with_suffix('.zip')),'bytes':DEST.with_suffix('.zip').stat().st_size,'sha256':sha(DEST.with_suffix('.zip')),'validation':validation},indent=2))

if __name__=='__main__':build()
