"""Package verified v20 sources and unchanged native MSETs; optional v19 preservation check."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[3];SRC=ROOT/'source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):p.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def csvfile(name,fields,rows):
    with (ROOT/name).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
def finalize(baseline=None):
    checks={name:json.loads((SRC/name).read_text()) for name in ['runtime_validation.json','visual_validation.json','native_controller_validation.json','data_validation.json','combo_recovery_analysis.json']}
    assert all(r['passed'] for r in checks.values()),checks
    assert checks['runtime_validation.json']['tests']>=98 and checks['visual_validation.json']['tests']>=29
    report=json.loads((SRC/'curve_validation.json').read_text());motions=report['motions'];by_slot={r['normal_slot']:r for r in motions}
    kept=[]
    if baseline:
        before=baseline/'source'
        for profile in range(1,5):
            for row in motions:
                name=f"aqua_{row['fixture_stem']}.bin";a=before/f'sets/p{profile}/fixtures'/name;b=SRC/f'sets/p{profile}/fixtures'/name
                if not a.exists():a=before/'fixtures'/name
                if not b.exists():b=SRC/'fixtures'/name
                assert a.read_bytes()==b.read_bytes(),(profile,name)
                kept.append({'profile':profile,'normal_slot':row['normal_slot'],'sha256':sha(b)})
        for f in ['xa_ex_0010.mset','xa_ex_0010_he.mset']:assert (baseline/'assets'/f).read_bytes()==(ROOT/'assets'/f).read_bytes()
        write(SRC/'numbered_preservation_validation.json',{'version':20,'passed':True,'baseline':'delivered v19, numbered v18 behavior','compared_active_records':len(kept),'records':kept})
    preserve=json.loads((SRC/'numbered_preservation_validation.json').read_text());assert preserve['passed'] and preserve.get('compared_active_records')==148
    shutil.copyfile(SRC/'kh1-aqua.dll',ROOT/'dll/kh1-aqua.dll')
    assets=[{'name':name,'sha256':sha(path),'bytes':path.stat().st_size} for name,path in [('dll/kh1-aqua.dll',ROOT/'dll/kh1-aqua.dll'),('xa_ex_0010.mset',ROOT/'assets/xa_ex_0010.mset'),('xa_ex_0010_he.mset',ROOT/'assets/xa_ex_0010_he.mset')]]
    write(ROOT/'expected_assets.json',{'version':20,'assets':assets})
    for a in assets[1:]:assert a['sha256']=={'xa_ex_0010.mset':'60d43ee9b2e2744fd4c2c62cdf98b1e412aa28e48f2e6c0201bcb04a932dbb7b','xa_ex_0010_he.mset':'9be6c17dfe6d87cd6da910aaabc359f58af121ee8462e4c8a63076e4d6a37797'}[a['name']]
    rootreport={'version':20,'offline_checks_passed':True,'game_runtime_tested':False,
        'abilities':['aqua','aqua 1','aqua 2','aqua 3','aqua 4'],'ability_ids':[117,118,119,120,121],
        'main_ground_combo':['300','301','366'],'main_air_combo':['305','353','407'],
        'main_idle_skull_roll_right_degrees':20.,'main_second_source_range':[0,37],'main_finisher_source_range':[12,47],
        'main_second_real_contact_ticks':30.*8./37.,'main_second_real_chain_open_ticks':30.,
        'main_air_chain_windows':{'102':[18,40],'103':[24,42]},
        'guard':'400 forward/reverse source30fps; wider body-centered native capsule radius50;12-tick parry/release grace',
        'glide':'normal and Superglide replaced by finite504; selection-based suppression survives binding recovery',
        'binding':'already-applied bank readmits without body writes while moving; failed admission retried every8 frames',
        'numbered_profiles_preserved_from_v19':True,'numbered_active_records_compared':148,
        'native_installed_msets_unchanged':True,'native_headers_counts_sizes_and_travel_preserved':True,
        'normal_motion_records':37,'olympus_motion_records':36,'runtime_pe_tests':checks['runtime_validation.json']['tests'],
        'geometry_tests':checks['visual_validation.json']['tests'],'dll_sha256':assets[0]['sha256'],
        'keyblade_tip_magic':True,'reaction_animations':'native KH1 Sora; KH2 source still pending',
        'limitations':['No live Windows/KH1 playtest or rendered-mesh test.','Native allocation, clash and movement callbacks are mocked in the PE host; anchor bytes verified against supplied Steam executable.','Offline memory-query reductions are not game-FPS measurements.']}
    write(ROOT/'validation.json',rootreport);write(SRC/'package_validation.json',rootreport)
    for name in ['Check_Aqua_Animations_v19.ps1','CHECK_AQUA_V19.cmd']:
        old=ROOT/name
        if old.exists():
            new=ROOT/name.replace('v19','v20').replace('V19','V20')
            new.write_text(old.read_text().replace('v19','v20').replace('V19','V20'));old.unlink()
    (ROOT/'mod.yml').write_text('''title: KH1FM Aqua Animation Test v20
game: kh1
originalAuthor: Raven Fang concept; motion test by OpenAI Codex
description: >-
  Main Aqua v20: right20 skull tilt,301 recovery trim, wider air followups,
  wider native all-angle body Guard and12-tick grace, tap504 replaces both
  Glides through bounded binding recovery. Numbered tests retain v19/v18.
  Original MSETs. Steam Global/Panacea.
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
    (ROOT/'README_FIRST.txt').write_text('''KH1FM AQUA ANIMATION TEST v20
Steam Global / OpenKH Panacea

INSTALL
Fully close KH1. Disable v19/older Aqua tests and Nine Styles/Dual Wield or
other conflicting combat builds. Import this ZIP into OpenKH, enable it, then
Build and Run. Equip MAIN aqua while idle. The log banner must say v20.
Use CHECK_AQUA_V20.cmd to check compiled file hashes if needed.

MAIN AQUA CHANGES
- Combat idle tilts Sora's actual skinned skull20 degrees RIGHT. This replaces
  v19's left-facing yaw. Hair bind corrections remain. Aerial Fire/Blizzard
  retain the prior right-facing yaw; run animations retain the prior swap.
- Ground combo remains300 ->301 ->366. Trim301's quiet final3 source frames
  (retain0..37). Both native variants now reach the contact and follow-up
  phases at matching real times: hit about6.49 ticks, follow-up30 ticks.
  The first swing's contact timing remains unchanged.366 retains its existing
  source12..47 trim and playback rate; no additional leading frames were cut.
- Air combo remains305 ->353 ->407. First follow-up window18..40, second
 24..42 native clock units. These reach each non-finisher's end to make the
  follow-up less easy to miss. Native event payloads/counts/pointers remain.
- Guard400 still plays fully forward then reverse at source30fps (2.6s).
  A wider body-centered capsule (radius50, centers35/85 units above the actor)
  supplies native guard contacts around Sora, including behind him. It uses
  the native constructor, contact mask, collision/deflection and retirement.
  Native Guard must be equipped and selected. This is a timed defense:
  release adds up to12 native ticks (~0.2s); parry6E/6F retains up to12 ticks.
  New attacks, magic, movement, damage, scripts, menus or ability changes cancel
  the extra shield. Recycled pool slots are not retired by this controller.
- Airborne Circle tap starts504 with captured movement direction and slight
  lift for39 units. Release Circle after takeoff, then tap. Releasing input
  does not shorten travel. Native collision/landing/interruptions still apply.
  Normal AND Superglide share the blocked constructor while MAIN is selected,
  including during binding recovery. air_dodge=0 restores native air behavior.
- A temporary residency/save-readiness interruption no longer forces an
  already-correct Aqua bank to wait for idle. It can be fully revalidated
  without body writes while moving. Failed full admissions retry every8
  frames. Reset/suspension messages identify the path in kh1-aqua.log.
  Guard angle checks skip unrelated clash pairs before querying Sora.

NUMBERED TEST ABILITIES RETAINED
 aqua1 ground371365366 / air218332393
 aqua2 ground352353407 / air351304303
 aqua3 ground300301302 / air616407351
 aqua4 ground510511512 / air504514399
All148 active numbered records compare byte-for-byte with delivered v19.
Their legacy v18 poses, timing and controls remain. All five ability IDs
117..121 retain0AP and exclusive selection. Switch profiles while idle.

RETAINED
Original on-disk Sora/Olympus MSETs; native headers/counts/allocations/travel;
keyblade-tip magic; native Blizzard spell logic with Fire visuals; native KH1
Sora reactions. Default KH2 Sora reaction assets are still pending.

TEST IN GAME
1. Check combat-idle right tilt and ground300/301/366 flow in both banks.
2. Repeat air305/353/407 during combat, including rapid and late follow-ups.
3. Tap Circle with each direction, release input, then hold Circle after504.
   Check that Glide does not return after combat, damage or a map transition.
4. Guard attacks from behind and either side, then repeat after a parry.
5. Check performance around the earlier Glide fallback situation. Return the
   resulting kh1-aqua.log and, if a visual/timing issue remains, a short clip.

VALIDATION AND LIMITS
98 actual-PE runtime tests and29 serialized-pose tests pass offline. Native
hook anchors match the supplied Steam executable. No live Windows/KH1 playtest
or rendered-mesh check was performed. Native callbacks are mocked in the PE
host; full combat behavior and visual feel need the in-game tests above.
In the offline lost-binding scenario, memory queries over120 moving frames
fell from33960 (v19) to1241 (v20). This is not a game-FPS measurement or proof
of the original slowdown's complete cause. Reports and rebuild sources are
included in source/. See source/REBUILD_V20.txt.

ROLLBACK / REMOVE
To roll back, close KH1, disable v20, enable the previous package and rebuild.
For complete ability removal, use REMOVE_AQUA_kh1-aqua.ini as kh1-aqua.ini next
to the game EXE, load a save and save again, then remove the config/mod.
''')
    (SRC/'REBUILD_V20.txt').write_text('''Aqua v20 source rebuild (Python3, NumPy/SciPy, gcc and GNU ld required)
Run from this source directory:
  python generate_data.py
  python build.py
  python test_runtime.py
  python test_visuals.py

The packaged fixtures are the verified serialized inputs to the DLL build.
To refit the changed main motions from the included original source banks:
  python retargeting/tools/build_aqua_complete_v20.py --slots1 99 100 102 103
  python retargeting/tools/analyze_aqua_recovery_v20.py
  python generate_data.py
  python build.py
Only the five listed records changed their serialized body/events in v20.
For complete main/profile regeneration, use build_aqua_complete_v20.py with
--profile0,1,2,3,4,5 or7 as needed (separate --profile and its number).
The older plan/refine modules are dependencies for the retained poses.
Native anchor verification requires your supplied Steam EXE:
  python retargeting/tools/validate_aqua_v20.py PATH_TO_EXE
benchmark_v20.py optionally compares a sibling v19 source/dll package.
finalize_aqua_v20.py --baseline PATH_TO_V19 rechecks all numbered active
records before packaging. Native game binaries are not included here.
'''.replace('--slots1','--slots 1').replace('--profile0,1,2,3,4,5 or7','--profile 0,1,2,3,4,5 or7'))
    maps=[]
    for profile in range(5):
        by={r['normal_slot']:r for r in json.loads((SRC/f'sets/p{profile}/curve_validation.json').read_text())['motions']} if profile else {}
        for original in motions:
            r=by.get(original['normal_slot'],original)
            maps.append({'Ability':'aqua'+(f' {profile}' if profile else ''),'Ability id':117+profile,'Action':r['action'],
                'Native request':hex(r['request']),'Normal slot':r['normal_slot'],'Olympus slot':r['olympus_slot'],
                'Aqua clip':r['donor'],'Source bank':r['source_bank'],'Source frame range':r['source_range'] or 'full',
                'Native frames':r['native_frames'],'Pose loop':r['loop'],'Head yaw degrees':r.get('head_yaw_character_degrees',0),
                'Head roll right degrees':r.get('head_roll_character_degrees',0),'Runtime rate':r.get('runtime_playback_rate',1),
                'Native hold frame':r.get('native_hold_frame',''),'Source timing':r.get('source_timing') or 'linear'})
    csvfile('ANIMATION_MAP.csv',list(maps[0]),maps)
    rows=[]
    for slot,contact,open_,close_,rate in [(98,12.,22.,40.,1.),(99,30.*8/37.,30.,48.,1.),(100,42.*8/37.,42.,64.,1.4),(102,6.,18.,40.,1.),(103,12.,24.,42.,1.)]:
        r=by_slot[slot];rows.append({'Ability':'aqua','Normal slot':slot,'Olympus slot':r['olympus_slot'],'Aqua clip':r['donor'],
            'Native frames':r['native_frames'],'Contact frame':contact,'Chain opens':open_,'Chain closes':close_,
            'Runtime rate':rate,'Real contact native ticks':contact/rate,'Real chain opens native ticks':open_/rate})
    csvfile('COMBO_TIMING.csv',list(rows[0]),rows)
    guards=[{'Ability':'aqua','Clip':'400','Forward native clock':'0..26.5','Reverse native clock':'26.5..53','Motion delta factor':53./156.,
        'Native defense window':'0..54','Body capsule radius':50,'Release grace native ticks':12,'Parry grace native ticks':12,'Coverage':'all angles, native body shield'}]
    for i in range(1,5):guards.append({'Ability':f'aqua {i}','Clip':'400','Forward native clock':'v18','Reverse native clock':'v18','Motion delta factor':1.,'Native defense window':'v18','Body capsule radius':'native','Release grace native ticks':0,'Parry grace native ticks':0,'Coverage':'native'})
    csvfile('GUARD_MAPPING.csv',list(guards[0]),guards)
    for name in ['AIR_DODGE_MAPPING.csv','GLIDE_MAPPING.csv']:
        text=(ROOT/name).read_text(encoding='utf-8-sig').replace('replaces held Glide','replaces normal and Superglide through binding recovery')
        (ROOT/name).write_text(text,encoding='utf-8-sig')
    zip_path=ROOT.parent/'KH1FM_Aqua_Animation_Test_v20.zip'
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path in sorted(ROOT.rglob('*')):
            if not path.is_file():continue
            rel=path.relative_to(ROOT)
            if any(p in ['__pycache__','sampling_cache'] for p in rel.parts) or path.suffix in ['.so','.o','.obj','.pyc','.log']:continue
            if rel==Path('source/kh1-aqua.dll'):continue
            z.write(path,str(rel))
    with zipfile.ZipFile(zip_path) as z:
        assert z.testzip() is None
        assert z.read('dll/kh1-aqua.dll')==(SRC/'kh1-aqua.dll').read_bytes()
        assert 'CHECK_AQUA_V20.cmd' in z.namelist() and 'CHECK_AQUA_V19.cmd' not in z.namelist()
    result={'version':20,'passed':True,'archive':str(zip_path),'archive_bytes':zip_path.stat().st_size,'archive_sha256':sha(zip_path),
        'dll_sha256':assets[0]['sha256'],'zip_crc_checked':True,'runtime_tests':98,'geometry_tests':29,'numbered_records_preserved':148,'game_runtime_tested':False}
    print(json.dumps(result,indent=2));return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path);args=ap.parse_args();finalize(args.baseline)
