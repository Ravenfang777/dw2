"""Package validated Aqua v9 and its four exact numbered animation sets."""
from pathlib import Path
import csv,hashlib,json,shutil,sys,zipfile
from aqua_v9_plan import SETS,BANK
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'KH1FM_Aqua_Animation_Test_v9'

README='''KH1FM AQUA ANIMATION TEST v9
Steam Global / OpenKH Panacea

FIVE ABILITIES, ALL 0 AP
aqua   : original Aqua combo set, with corrected wrist pivots/arm clearance
aqua 1 : ground 045 217 218 ; air 332 357 361
aqua 2 : ground 362 363 350 ; air 365 366 370
aqua 3 : ground 370 371 372 ; air 373 506 315
aqua 4 : ground 316 317 318 ; air 391 390 427

These are alternatives. Each includes the common Aqua movement, jumps,
casting poses, items, reactions, Guard and Cartwheel. Selecting a new Aqua
entry unequips the other Aqua entries. Native abilities retain their states.
Unequipping the selected Aqua entry restores the original mapped Sora motions.
Change selections while idle; an active action finishes before the data switch.
The first slot is the first attack, the second is the second attack, and the
third is the finisher. KH1's alternate second ground attack uses that same
second source clip, so it stays within your selected three-animation set.

V9 CORRECTIONS
- Moved hand bending to Sora's anatomical hand pivots. Distal forearm helpers
  now follow the forearm rather than rotating with the hand; this targets the
  combat-idle wrist/cuff separation and applies across all five profiles.
- Strengthened arm clearance during the original ground and air finishers,
  including tests of the upper-arm and forearm interiors against the torso.
  Segment lengths, local attachment offsets and scales remain unchanged.
- Moved the working native spell-origin and glow/effect-matrix route to the
  LEFT palm (the other hand from v8). It applies to all five Aqua profiles.
- Kept the corrected hair rest rotations from v8.

INSTALL
1. Fully close KH1.
2. Disable Aqua v8 and all older Aqua packages, Sora Restore Check, and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH and enable Aqua Animation Test v9.
4. Build and Run. Load your save. Missing Aqua entries are added unequipped;
   a previously saved selection is respected. Existing native entries are not
   evicted. If the ability list lacks room, the log reports the missing space.
5. Select aqua or aqua 1..4 in Abilities while standing idle. You do not need
   to equip the original aqua entry along with one of the numbered entries.

TEST
- First use aqua to compare combat idle from front/side and the original
  ground finisher. Check forearm-to-hand alignment and arms crossing the body.
- Cast ground/air spells and confirm launch points and attached glow use the
  LEFT hand. Recheck a spell with all Aqua entries off for native behavior.
- Select aqua 1, then 2, 3 and 4 while idle. Test three-hit ground and air
  combos with each. For a clean test, unequip Slapshot, Sliding Dash, Vortex,
  Hurricane Blast and other native combo replacements. Their unassigned
  actions otherwise retain their native animations. Guard and Dodge Roll
  still need their native abilities equipped.
- Repeat on your other save, after a room transition and after a save reload.

RETURN
Return the NEW kh1-aqua.log beside the game EXE and a short comparison video.
Its first line must say ANIMATION TEST v9. The log records 0x2F normal / 0x2E
Olympus records and profile 0=native, 1=aqua, 2=aqua 1, 3=aqua 2, 4=aqua 3,
5=aqua 4. Hand queries log AQUA HAND MAGIC ORIGIN / MATRIX with the native
request number. CHECK_AQUA_V9.cmd optionally checks installation hashes and
writes Aqua_Animation_Check_v9.txt.

SCOPE AND TIMING
The selected source clips are resampled to the existing KH1 action durations.
This tests animations. Native KH1 hit events, damage, spell simulation, MP,
projectile trajectories, targeting, guard coverage, dodge invincibility and
actor travel remain in use. The native weapon-attachment position/matrix
queries are redirected to the left hand during eligible Aqua casts.
Source animations do not bring their BBS commands, projectiles or effects into
the combo. Guard is still the Barrier pose with KH1 Guard behavior.

Both installed MSET files are your original files. In-memory poses fit within
their existing tables; headers, lengths, counts and eleven helpers retain the
original layout. Current foreign/unknown records block body writes. Other
Sora costume/forms banks are not admitted by this test.

FILE GUIDE
ABILITY_SETS.txt lists the five abilities and exact numeric selections.
ANIMATION_MAP.csv lists all five profiles' effective motion assignments.
TEST_CLIP_SOURCES.csv gives source banks, frame counts, hashes and fitted slots.
REMAINING_NATIVE.csv lists unassigned native records.
The earlier 349-clip source inventory CSV/JSON is included under inventory;
use this package's ANIMATION_MAP.csv for the current ability assignments.
045 uses p02ex_004.arc; 370 uses p02ex_133.arc. Numbered source labels are not
assumed to be official BBS command names.

OPTIONAL NATIVE-MAGIC FALLBACK
To test the v9 poses with native spell attachments, copy
DISABLE_HAND_MAGIC_kh1-aqua.ini beside the game EXE as kh1-aqua.ini and restart.
Remove that INI and restart to restore left-hand routing.

SAVE / REMOVE ALL AQUA ENTRIES
Saving in-game may retain ids117..121. To remove all five, copy
REMOVE_AQUA_kh1-aqua.ini beside the game EXE as kh1-aqua.ini, leave v9 enabled,
restart and load each save to clean. Check AQUA ABILITIES REMOVED, then save
in-game. Exit, remove the INI, disable v9 and rebuild. Native ability order
is preserved; only these five test ids are removed.

VALIDATION
34 tests execute the compiled PE DLL in a Win64 ABI mock host. They include
all five selections in both banks, exclusivity, save/reload behavior, removal,
exact restoration and the distinct left-palm attachment route.
12 independent geometry tests cover all 75 generated records, including the
forearm helper angles, source capacities, hair rest shape, unit skin bases,
native travel and transitions. The original finisher's joint/capsule overlap
is substantially reduced. These checks do not render Sora's mesh or execute
Windows/KH1. The final idle/finisher appearance and left-hand FX need your
in-game comparison; some clipping may still need adjustment.
'''

SOURCE='''AQUA V9 SOURCE

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
  python3 retargeting/tools/build_aqua_complete_v9.py --profile 0 --output .
  python3 retargeting/tools/build_aqua_complete_v9.py --profile 1 --output sets/p1
  python3 retargeting/tools/build_aqua_complete_v9.py --profile 2 --output sets/p2
  python3 retargeting/tools/build_aqua_complete_v9.py --profile 3 --output sets/p3
  python3 retargeting/tools/build_aqua_complete_v9.py --profile 4 --output sets/p4
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
--slots followed by normal slot numbers rebuilds only those records in a
profile. Required source ARC files are in retargeting/core_source. Original
MSET files are ../assets. Immutable baseline sampling caches are reproducible
and are not distributed. V9 refinements are applied once to each baseline.

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

LEFT-HAND MAGIC
The two native entry points and admitted instruction spans are unchanged from
v8. Their direct matrix selector is now0x20CE, the LEFT palm206, in all five
profiles. Native cast requests, current actor/bank, event/script exclusions
and native fallthrough are retained. No spell-resource or projectile script
is replaced. The supplied executable is not included; its original hash and
the entry spans are in native_attachment_validation.json.

CAPACITY / SOURCE IDS
No motion/header/table expansion is used. The original eleven helpers and
native travel remain. Four sets change seven physical combo records each:
C8 first, C9/CA second, CB finisher, CC first air, CD second air, CE finisher.
The donor selection is in aqua_v9_plan.py. Numeric IDs retain their exact
source bank/hash in TEST_CLIP_SOURCES.csv; no command names are inferred.
The source inventory files under ../inventory retain v8's source metadata.
Current ability mappings are ../ANIMATION_MAP.csv.

Existing upstream licenses and notices are retained in licenses.
Format reference: https://openkh.dev/bbs/file/type/pam.html
'''

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def build():
    d=ROOT/'ability_v9';runtime=json.loads((d/'runtime_validation.json').read_text());geometry=json.loads((d/'visual_validation.json').read_text())
    reports=[json.loads((d/'curve_validation.json').read_text())]+[json.loads((d/f'sets/p{i}/curve_validation.json').read_text()) for i in range(1,5)]
    assert runtime['passed'] and geometry['passed'] and all(r['passed'] for r in reports)
    shutil.copytree(ROOT/'KH1FM_Aqua_Animation_Test_v8',DEST,dirs_exist_ok=True)
    for p in [DEST/'CHECK_AQUA_V8.cmd',DEST/'Check_Aqua_Animations_v8.ps1',DEST/'inventory/Aqua_Move_Inventory_v8.xlsx']:
        p.unlink(missing_ok=True)
    for n in ['aqua.c','aqua_magic.h','aqua_data.h','build.py','generate_data.py','test_runtime.py','test_bridge.c','test_visuals.py',
              'curve_validation.json','data_validation.json','runtime_validation.json','visual_validation.json','arm_alignment_validation.json']:
        shutil.copy2(d/n,DEST/'source'/n)
    (DEST/'source/clearance_validation.json').unlink(missing_ok=True)
    (DEST/'source/spreadsheet_validation.json').unlink(missing_ok=True)
    shutil.copytree(d/'fixtures',DEST/'source/fixtures',dirs_exist_ok=True)
    shutil.copytree(d/'sets',DEST/'source/sets',dirs_exist_ok=True)
    shutil.copy2(d/'kh1-aqua.dll',DEST/'dll/kh1-aqua.dll')
    tools=DEST/'source/retargeting/tools'
    for name in ['build_aqua_complete_v9.py','aqua_refine_v9.py','aqua_v9_plan.py','aqua_refine_v8.py','package_aqua_v9.py']:
        shutil.copy2(ROOT/'tools'/name,tools/name)
    for number in sorted(set(BANK.values())):
        name=f'p02ex_{number}.arc';shutil.copy2(ROOT/'capture_20261101/Sources/data/bbs/arc/pc'/name,DEST/'source/retargeting/core_source'/name)
    (DEST/'README_FIRST.txt').write_text(README);(DEST/'source/README_SOURCE.txt').write_text(SOURCE)
    desc='The 0 AP abilities aqua and aqua 1..4 select Aqua moves with anatomical wrist correction, finisher arm clearance, LEFT-hand native magic and four exact numbered combo test sets. Steam Global / Panacea; disable earlier Aqua packages and Nine Styles / Dual Wield.'
    manifest=(ROOT/'KH1FM_Aqua_Animation_Test_v8/mod.yml').read_text();start=manifest.index('description:');end=manifest.index('assets:')
    manifest=manifest[:start]+'description: >-\n  '+desc+'\n'+manifest[end:]
    (DEST/'mod.yml').write_text(manifest.replace('Animation Test v8','Animation Test v9'))
    checker=(ROOT/'KH1FM_Aqua_Animation_Test_v8/Check_Aqua_Animations_v8.ps1').read_text().replace('v8','v9').replace('CHECK_AQUA_V8','CHECK_AQUA_V9')
    (DEST/'Check_Aqua_Animations_v9.ps1').write_text(checker)
    (DEST/'CHECK_AQUA_V9.cmd').write_bytes(b'@echo off\r\nsetlocal\r\npowershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check_Aqua_Animations_v9.ps1" %*\r\npause\r\n')
    (DEST/'REMOVE_AQUA_kh1-aqua.ini').write_text('[aqua]\nremove_aqua=1\nhand_magic=0\n')
    (DEST/'DISABLE_HAND_MAGIC_kh1-aqua.ini').write_text('[aqua]\nremove_aqua=0\nhand_magic=0\n')
    labels=['aqua']+[f'aqua {i}' for i in range(1,5)]
    (DEST/'ABILITY_SETS.txt').write_text('\n'.join([f'Ability {label} / id{117+i} / 0 AP' + (' / original Aqua set' if not i else f' / ground {" ".join(SETS[i-1][0])} / air {" ".join(SETS[i-1][1])}') for i,label in enumerate(labels)])+'\n\nSelect one while idle. Other Aqua entries turn off automatically.\n')
    maps=[];sources=[]
    sys.path.insert(0,str(ROOT/'tools'));from bbs_source_inspector import read_arc,read_pam
    import struct
    for profile in range(5):
        active={r['normal_slot']:r for r in reports[0]['motions']}
        if profile:active.update({r['normal_slot']:r for r in reports[profile]['motions']})
        for r in sorted(active.values(),key=lambda x:x['normal_slot']):
            maps.append({'Ability':labels[profile],'Ability id':117+profile,'Action':r['action'],'Native request':f'0x{r["request"]:02X}',
                'Normal slot':r['normal_slot'],'Olympus slot':r['olympus_slot'] if r['olympus_slot']!=0xffffffff else 'not present',
                'Aqua clip':r['donor'],'Source bank':r['source_bank'],'Source frame range':str(r['source_range']) if r['source_range'] else 'full',
                'Pose loop':r['loop'],'Native frames':r['native_frames'],'Root policy':r['root']})
        if not profile:continue
        for r in reports[profile]['motions']:
            arc=ROOT/'capture_20261101/Sources/data/bbs/arc/pc'/r['source_bank'];members,_=read_arc(arc.read_bytes())
            for member,data in members:
                if not data.startswith(b'PAM\0'):continue
                for a in read_pam(data,54):
                    if a.name!=r['donor']:continue
                    start=struct.unpack_from('<I',data,16+16*a.slot)[0]
                    sources.append({'Ability':labels[profile],'Action':r['action'],'Normal slot':r['normal_slot'],'Source name':a.name,
                        'Source bank':r['source_bank'],'PAM member':member,'Source frames':a.frame_count,'Source FPS':a.fps,
                        'Animation SHA256':hashlib.sha256(data[start:a.data_end]).hexdigest(),'Native frames':r['native_frames'],'Native FPS':60})
    for name,rows in [('ANIMATION_MAP.csv',maps),('TEST_CLIP_SOURCES.csv',sources)]:
        with (DEST/name).open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    # Keep the old source inventory, but remove its outdated assignment view.
    (DEST/'inventory/Aqua_KH1_Assignments.csv').unlink(missing_ok=True)
    expected={'version':9,'assets':[]}
    for logical,actual in [('dll/kh1-aqua.dll',DEST/'dll/kh1-aqua.dll'),('xa_ex_0010.mset',DEST/'assets/xa_ex_0010.mset'),('xa_ex_0010_he.mset',DEST/'assets/xa_ex_0010_he.mset')]:
        expected['assets'].append({'name':logical,'sha256':sha(actual),'bytes':actual.stat().st_size})
    (DEST/'expected_assets.json').write_text(json.dumps(expected,indent=2)+'\n')
    native=json.loads((DEST/'source/native_attachment_validation.json').read_text());native.pop('direct_right_palm_matrix_selector',None);native.pop('right_palm_index',None)
    native.update({'direct_left_palm_matrix_selector':'0x20CE','left_palm_index':206,'runtime_mock_profiles_tested':5,'windows_or_game_executed':False})
    (DEST/'source/native_attachment_validation.json').write_text(json.dumps(native,indent=2)+'\n')
    all_records=[r for report in reports for r in report['motions']]
    validation={'version':9,'offline_checks_passed':True,'game_runtime_tested':False,'abilities':labels,'ability_ids':list(range(117,122)),
        'normal_motion_records_per_profile':47,'olympus_motion_records_per_profile':46,'unique_generated_records':len(all_records),
        'actual_pe_mock_tests':runtime['tests'],'geometry_transition_tests':geometry['tests'],'pose_samples':sum(r['validated_pose_samples'] for r in all_records),
        'max_pose_position_fit_error':max(r['max_pose_position_error'] for r in all_records),
        'max_non_root_attachment_translation_error':max(r['max_non_root_attachment_translation_error'] for r in all_records),
        'max_scale_error':max(r['max_scale_error'] for r in all_records),'native_travel_error':max(r['root_helper_error'] for r in all_records),
        'original_motion_lengths_headers_and_counts_preserved':True,'helper_slots':11,'original_msets_on_disk':True,
        'left_palm_magic':206,'dll_sha256':sha(DEST/'dll/kh1-aqua.dll'),
        'limitations':['Windows/KH1 rendering of v9 pending','Arm separation uses joint/capsule checks; some mesh clipping may remain',
                       'Numbered clips use native KH1 durations and hit events; BBS commands/effects are not imported']}
    (DEST/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    with zipfile.ZipFile(DEST.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:z.write(p,p.relative_to(DEST))
    print(json.dumps({'zip':str(DEST.with_suffix('.zip')),'bytes':DEST.with_suffix('.zip').stat().st_size,'sha256':sha(DEST.with_suffix('.zip')),'validation':validation},indent=2))

if __name__=='__main__':build()
