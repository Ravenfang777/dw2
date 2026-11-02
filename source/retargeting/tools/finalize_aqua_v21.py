"""Package verified v21 sources and unchanged native MSETs; optional v20 preservation check."""
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
    assert checks['runtime_validation.json']['tests']>=110 and checks['visual_validation.json']['tests']>=29
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
        write(SRC/'numbered_preservation_validation.json',{'version':21,'passed':True,'baseline':'delivered v20, numbered v18 behavior','compared_active_records':len(kept),'records':kept})
    preserve=json.loads((SRC/'numbered_preservation_validation.json').read_text());assert preserve['passed'] and preserve.get('compared_active_records')==148
    shutil.copyfile(SRC/'kh1-aqua.dll',ROOT/'dll/kh1-aqua.dll')
    assets=[{'name':name,'sha256':sha(path),'bytes':path.stat().st_size} for name,path in [('dll/kh1-aqua.dll',ROOT/'dll/kh1-aqua.dll'),('xa_ex_0010.mset',ROOT/'assets/xa_ex_0010.mset'),('xa_ex_0010_he.mset',ROOT/'assets/xa_ex_0010_he.mset')]]
    write(ROOT/'expected_assets.json',{'version':21,'assets':assets})
    for a in assets[1:]:assert a['sha256']=={'xa_ex_0010.mset':'60d43ee9b2e2744fd4c2c62cdf98b1e412aa28e48f2e6c0201bcb04a932dbb7b','xa_ex_0010_he.mset':'9be6c17dfe6d87cd6da910aaabc359f58af121ee8462e4c8a63076e4d6a37797'}[a['name']]
    rootreport={'version':21,'offline_checks_passed':True,'game_runtime_tested':False,
        'abilities':['aqua','aqua 1','aqua 2','aqua 3','aqua 4'],'ability_ids':[117,118,119,120,121],
        'main_ground_combo':['300','301','366'],'main_air_combo':['305','407','353'],
        'main_idle_skull_roll_right_degrees':20.,'jump_height_multiplier':1.25,'dodge_animation_and_travel_rate':1.5,'dodge_duration_native_ticks':26.,'dodge_distance':546.,'dodge_lift':29.25,'dodge_uses_per_airtime':1,'dodge_rearm':'landing','second_pose_hold_rate_multiplier':2.,'main_second_source_range':[0,30],'main_finisher_source_range':[15,47],
        'main_second_real_contact_ticks':6.4,'main_second_real_chain_open_ticks':24.,
        'main_air_chain_windows':{'102':[18,40],'103':[22,42]},
        'guard':'400 forward/reverse source30fps; wider body-centered native capsule radius50;12-tick parry/release grace',
        'glide':'ordinary Glide replaced by one504 per airtime; native Superglide retained',
        'binding':'already-applied bank readmits without body writes while moving; failed admission retried every8 frames',
        'numbered_profiles_preserved_from_v20':True,'numbered_active_records_compared':148,
        'native_installed_msets_unchanged':True,'native_headers_counts_sizes_and_travel_preserved':True,
        'normal_motion_records':37,'olympus_motion_records':36,'runtime_pe_tests':checks['runtime_validation.json']['tests'],
        'geometry_tests':checks['visual_validation.json']['tests'],'dll_sha256':assets[0]['sha256'],
        'keyblade_tip_magic':True,'reaction_animations':'native KH1 Sora; KH2 source still pending',
        'limitations':['No live Windows/KH1 playtest or rendered-mesh test.','Native allocation, clash and movement callbacks are mocked in the PE host; anchor bytes verified against supplied Steam executable.','Offline memory-query reductions are not game-FPS measurements.']}
    write(ROOT/'validation.json',rootreport);write(SRC/'package_validation.json',rootreport)
    for name in ['Check_Aqua_Animations_v20.ps1','CHECK_AQUA_V20.cmd']:
        old=ROOT/name
        if old.exists():
            new=ROOT/name.replace('v20','v21').replace('V20','V21')
            new.write_text(old.read_text().replace('v20','v21').replace('V20','V21'));old.unlink()
    (ROOT/'mod.yml').write_text('''title: KH1FM Aqua Animation Test v21
game: kh1
originalAuthor: Raven Fang concept; motion test by OpenAI Codex
description: >-
  Main Aqua v21: tap504 at1.5x speed with the same distance, once per airtime;
  native Superglide retained; jump height+25 percent; air305/407/353;
  shorter301 recovery and366 opening. Numbered tests retained. Original MSETs.
  Steam Global/Panacea.
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
    (ROOT/'README_FIRST.txt').write_text('''KH1FM AQUA ANIMATION TEST v21
Steam Global / OpenKH Panacea

INSTALL
Fully close KH1. Disable v20/older Aqua tests and conflicting Nine Styles /
Dual Wield or combat builds. Install this ZIP in OpenKH, enable it, then Build
and Run. Equip MAIN aqua while idle. The log banner must say v21.
CHECK_AQUA_V21.cmd checks the compiled installation hashes if needed.

MAIN AQUA CHANGES
AERIAL DODGE
Tap Circle airborne after releasing it following takeoff.504 and its movement
run at1.5x the previous rate:26 native ticks instead of39 (two-thirds the time).
The complete unobstructed burst still requests546 horizontal units and29.25
units of lift. Direction stays locked to the tap's movement direction, with
the prior neutral momentum/facing fallback. Collision, ceilings, landing and
native interruptions still apply. Native fall handoff speed matches v20 to
avoid adding extra drift after the faster burst.

ONE DODGE PER AIRTIME. Completing504, releasing/repressing Circle, changing
Aqua abilities, recovering animation bindings or using Superglide do not grant
another dodge. Land to rearm. A new actor identity starts a new budget.

SUPERGLIDE
Native Superglide is usable again with its own normal button/ability checks.
Only ordinary Glide is replaced by tap504. A successful native Superglide can
interrupt504; a rejected Superglide does not cancel the dodge. It does not
reset the dodge's spent use. Native Glide/Superglide animation records remain
original. air_dodge=0 restores native air controls; the jump boost remains.
The1.5x dodge rate requires the verified actor-motion hook. If that hook cannot
be admitted, the controller logs and keeps the old matched movement/visual
rate rather than accelerating movement alone.

JUMP HEIGHT
Normal and High Jump receive25 percent more native launch height in MAIN.
The native launch runs first. Only its private arc height and ascent duration
are scaled (1.25 and sqrt1.25), leaving launch origin, global gravity, stats,
actor positions, native collision and ceiling handling untouched.

COMBOS
Ground remains300 ->301 ->366.
-301 retains source0..30, trimming7 more end frames compared with v20.
- Both second-attack variants enable the finisher at24 real native ticks
  instead of30. Their completed-pose recovery advances twice as fast.
-366 retains source15..47, removing3 more opening frames compared with v20.
  Its native hit/effect timing and playback duration follow that trim.
- First ground attack and its contact timing remain unchanged.
Air is now305 ->407 ->353. Native contact windows follow the swapped poses.
The first/second follow-up windows run18..40 and22..42 native clock units.
Native event counts, payloads, pointers, headers and allocation sizes remain.

RETAINED
Main Guard400 full forward/reverse at source30fps, wider native body capsule
and12-tick grace; combat-idle skull tilt right20 degrees; aerial Fire/Blizzard
right-facing head adjustment; swapped run loops; keyblade-tip magic; native
Blizzard spell logic; original KH1 Sora damage reactions. KH2 reaction source
assets are still pending. Installed Sora/Olympus MSETs stay original.

NUMBERED TEST ABILITIES RETAIN v20/v18
 aqua1 ground371365366 / air218332393
 aqua2 ground352353407 / air351304303
 aqua3 ground300301302 / air616407351
 aqua4 ground510511512 / air504514399
All148 active numbered records match v20 byte-for-byte. Numbered jump heights,
dodge rate/controls, casts and Guard behavior remain as before. All five
abilities retain0AP and IDs117..121. Switch profiles while idle.

IN-GAME TEST
1. Compare jump and High Jump height with main equipped/unequipped.
2. Tap airborne Circle and check faster504 with the same travel distance.
3. After504, release and tap again: no second dodge until landing. Land and
   repeat. Check that attacks, ability toggles and Superglide do not rearm it.
4. Use native Superglide with its ability equipped, including after504.
5. Check ground300/301/366 flow and air305/407/353 during combat.
Return kh1-aqua.log and a short clip if a visual, timing or movement issue
remains. The wider Guard and previous poses are unchanged in this test.

VALIDATION
110 actual-PE runtime tests and29 serialized-pose tests pass offline. Jump
checks execute the supplied game's actual launch and arc code in the mock
host. Faster-dodge distance is checked with both callback orders and several
timesteps. Native hook anchors match the supplied Steam executable. No live
Windows/KH1 playtest or rendered-mesh check was performed. Native collision,
allocation and input calls are mocked; in-game feel still needs testing.
Source, fixtures, reports and REBUILD_V21.txt are included in source/.

ROLLBACK / REMOVE
Close KH1, disable v21, enable the previous package and rebuild to roll back.
For complete ability removal, use REMOVE_AQUA_kh1-aqua.ini as kh1-aqua.ini next
to the game EXE, load a save and save again, then remove the config/mod.
''')
    old_rebuild=SRC/'REBUILD_V20.txt'
    if old_rebuild.exists():old_rebuild.unlink()
    (SRC/'REBUILD_V21.txt').write_text('''Aqua v21 source rebuild (Python3, NumPy/SciPy, gcc and GNU ld)
Run from this source directory:
  python generate_data.py
  python build.py
  python test_runtime.py
  python test_visuals.py

To refit the changed main motions from included BBS source banks:
  python retargeting/tools/build_aqua_complete_v21.py --slots 99 100 101 103 104
  python retargeting/tools/analyze_aqua_recovery_v21.py
  python generate_data.py
  python build.py
The v21 fitter samples fractional source-hold times exactly. Earlier plan and
refinement modules are dependencies for retained poses and numbered profiles.
For native anchor verification, use your own supplied Steam EXE:
  python retargeting/tools/validate_aqua_v21.py PATH_TO_EXE
For packaging and byte-for-byte numbered preservation against v20:
  python retargeting/tools/finalize_aqua_v21.py --baseline PATH_TO_V20_FOLDER
Jump fixtures are small original function/constant excerpts from the supplied
EXE. The full native executable is not included. Math and native service calls
are stubbed in the PE host; game rendering/collision are not exercised here.
''')
    historical=SRC/'performance_validation.json'
    if historical.exists():
        folder=SRC/'history';folder.mkdir(exist_ok=True)
        shutil.move(historical,folder/'v20_performance_validation.json')
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
                'Native hold frame':r.get('native_hold_frame',''),'Source timing':r.get('source_timing') or 'linear','Recovery tail rate':r.get('recovery_tail_rate_multiplier',1.)})
    csvfile('ANIMATION_MAP.csv',list(maps[0]),maps)
    rows=[]
    for slot,contact,open_,close_,rate in [(98,12.,22.,40.,1.),(99,6.4,24.,48.,1.),(100,8.96,33.6,64.,1.4),(102,6.,18.,40.,1.),(103,7.,22.,42.,1.)]:
        r=by_slot[slot];rows.append({'Ability':'aqua','Normal slot':slot,'Olympus slot':r['olympus_slot'],'Aqua clip':r['donor'],
            'Native frames':r['native_frames'],'Contact frame':contact,'Chain opens':open_,'Chain closes':close_,
            'Runtime rate':rate,'Real contact native ticks':contact/rate,'Real chain opens native ticks':open_/rate})
    csvfile('COMBO_TIMING.csv',list(rows[0]),rows)
    guards=[{'Ability':'aqua','Clip':'400','Forward native clock':'0..26.5','Reverse native clock':'26.5..53','Motion delta factor':53./156.,
        'Native defense window':'0..54','Body capsule radius':50,'Release grace native ticks':12,'Parry grace native ticks':12,'Coverage':'all angles, native body shield'}]
    for i in range(1,5):guards.append({'Ability':f'aqua {i}','Clip':'400','Forward native clock':'v18','Reverse native clock':'v18','Motion delta factor':1.,'Native defense window':'v18','Body capsule radius':'native','Release grace native ticks':0,'Parry grace native ticks':0,'Coverage':'native'})
    csvfile('GUARD_MAPPING.csv',list(guards[0]),guards)
    dodge=[{'Ability':'aqua','Clip':'504','Speed':21.,'Lift per tick':1.125,'Duration ticks':26.,'Animation rate':1.5,'Distance':546.,'Lift':29.25,'Uses per airtime':1,'Rearm':'landing','Superglide':'native retained'}]
    for profile in range(1,5):dodge.append({'Ability':f'aqua {profile}','Clip':'504','Speed':14.,'Lift per tick':.75,'Duration ticks':39.,'Animation rate':1.,'Distance':546.,'Lift':29.25,'Uses per airtime':1,'Rearm':'prior v18 controls','Superglide':'native retained'})
    csvfile('AIR_DODGE_MAPPING.csv',list(dodge[0]),dodge)
    glide=[{'Ability':'aqua','Regular Glide':'replaced by one tap504 per airtime','Superglide':'native ability and activation retained','Native motion slots':'75,76,77,78','Native motion bytes':'unchanged'}]
    for profile in range(1,5):glide.append({'Ability':f'aqua {profile}','Regular Glide':'native v20/v18 behavior','Superglide':'native v20/v18 behavior','Native motion slots':'75,76,77,78','Native motion bytes':'unchanged'})
    csvfile('GLIDE_MAPPING.csv',list(glide[0]),glide)
    (ROOT/'ABILITY_SETS.txt').write_text('MAIN aqua (117,0AP): Ground300/301/366; Air305/407/353; Dodge504 once per airtime at1.5x rate; native Superglide; jump height1.25\nAqua1 (118): Ground371/365/366 Air218/332/393\nAqua2 (119): Ground352/353/407 Air351/304/303\nAqua3 (120): Ground300/301/302 Air616/407/351\nAqua4 (121): Ground510/511/512 Air504/514/399\nNumbered tests retain v20/v18.\n')
    zip_path=ROOT.parent/'KH1FM_Aqua_Animation_Test_v21.zip'
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
        assert 'CHECK_AQUA_V21.cmd' in z.namelist() and 'CHECK_AQUA_V20.cmd' not in z.namelist()
    result={'version':21,'passed':True,'archive':str(zip_path),'archive_bytes':zip_path.stat().st_size,'archive_sha256':sha(zip_path),
        'dll_sha256':assets[0]['sha256'],'zip_crc_checked':True,'runtime_tests':110,'geometry_tests':29,'numbered_records_preserved':148,'game_runtime_tested':False}
    print(json.dumps(result,indent=2));return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path);args=ap.parse_args();finalize(args.baseline)
