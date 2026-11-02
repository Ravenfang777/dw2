"""Ship verified v17 sources, mappings and a standalone Panacea test ZIP."""
from pathlib import Path
import csv,hashlib,json,shutil,struct,zipfile
from aqua_v17_plan import SETS,BANK
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'KH1FM_Aqua_Animation_Test_v17'
D=ROOT/'ability_v17'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write_json(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
def csv_file(name,rows):
    with (DEST/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

README="KH1FM AQUA ANIMATION TEST v17\nSteam Global / OpenKH Panacea\n\nREQUESTED MAIN AQUA MOVES\nGround:300 ->300 ->366. Both native second-ground variants now use300.\nAir:305 ->407 ->351.\nThe first ground hit retains v16's earlier contact. The second swing still\ncompletes before a16/20-native-frame recovery window allows the finisher.\nIts hit keys now match300's strike phase. Native damage and event payloads,\nsounds, effects and all four numbered test sets are retained.\n\nDEFAULT GLIDE\nAll Glide animation bodies, opening/flight/ending behavior, native clocks,\nqueued start frames, steering and movement are original Sora/KH1 again.\nThere is no Aqua350 opening, held pose, closing overlay or clock clamp.\nGlide records75..78 (Olympus37..40) are absent from Aqua's runtime patch table.\nNormal Glide unlock and held-button requirements remain native. The regular\nGlide constructor passes through except while the active504 dodge owns the air\naction. Native Glide ending returns to the selected profile's normal fall506;\nthere is no added350 ending or fall restart. Superglide is unchanged.\n\nDUAL D2X AERIAL DODGE / AQUA504\nUses the recorded Dual D/Master baseline: height145, horizontal speed18.\nAs in Dual D's2x setting, every requested upward/directional displacement is\nmultiplied by2. The full held rise is290 units and moving speed36 units per\nnative clock unit. This does not multiply animation duration or arc time.\nAqua504 remains in the existing40-frame native fall record, then506 resumes.\nNeutral stick rises vertically; tilted stick adds normalized directional travel.\nRelease Circle after takeoff, then press again airborne. One dodge per airtime;\nland to rearm. Holding/releasing Circle retains the existing full/short arc rule.\n\nThe recorded Dual D145/18 values and2x policy are matched. The KH1 controller's\nexisting gravity/release adapter remains: baseline gravity0.75, upward release\ncap4 and falling cap20, before2x displacement scaling. This is not a claim that\nthose adapter coefficients were extracted from KH2. Exact KH2 gravity/clip202\nlength was not present in the supplied source extract. Native collision, landing\nand interruption callbacks remain; the mod never writes actor position directly.\nNo new invulnerability, guard window, hitbox or growth ability is granted.\n\nWHOLE HEAD DURING RUNNING\nV16 targeted joint151, an unskinned hair helper. The face/skull is skinned joint\n150. V17 puts Aqua's authored head-bone5 direction on skull150, then keeps\nhair helper151 at its local bind rotation. The face and attached hair now follow\none head instead of adding a separate tilt to the bangs. This is a head mapping\ncorrection rather than another fixed hair-angle adjustment. Ordinary/combat run\nslots5/6/7 are corrected. Torso, neck, bind lengths, scales and native travel stay.\nAppearance needs a live game check; the offline tests verify the actual skin flag\nand the serialized skull/head orientation, not just a helper's position.\n\nRETAINED ABILITIES / CASTING\nMain aqua / id117 /0AP: ground300 300 366; air305 407 351.\naqua 1 / id118 /0AP: ground316 317 318; air391 390 427.\naqua 2 / id119 /0AP: ground315 371 366; air365 218 332.\naqua 3 / id120 /0AP: ground393 411 352; air616 407 351.\naqua 4 / id121 /0AP: ground510 511 512; air504 514 399.\nNumbered tests are unchanged. Default Glide,2x dodge and common run correction\napply to all five. Select one while idle; native ability entries are not evicted.\nMain Fire391/316, Blizzard Fire visuals on original Blizzard events, Cure427/318,\nStop/Aero317/390, item007/395, falling506 and keyblade-tip magic remain from v16.\n\nINSTALL\n1. Fully close KH1.\n2. Disable Aqua v16 and all older Aqua packages, Sora Restore Check and\n   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.\n3. Import this ZIP in OpenKH, enable Aqua Animation Test v17, Build and Run.\n4. Load your save and equip main aqua while standing idle.\n\nTEST ORDER\n- Check ground300 ->300 ->366, both locked and unlocked.\n- Check air305 ->407 ->351 through the finisher.\n- Run sideways to the camera and inspect the FACE/head angle and hair together.\n- Jump, release Circle and press again: neutral lift, then directional travel\n  on another jump. Hold/release to compare height. Land between attempts.\n- Check native Glide start, straight flight, turns and release. No Aqua350 pose\n  should play, and a long flight/turn must not hold or clamp the native clock.\n- Check both saves/room changes, numbered sets and restoration with aqua off.\nFor clean basic-combo tests, unequip Slapshot, Vortex, Hurricane Blast and other\nnative attack replacements; those separate actions retain their own timing.\n\nLOG / INSTALL CHECK\nCapture the new kh1-aqua.log before restarting, since each launch replaces it.\nIt should begin v17. Dodge should log DUAL D2X MOVEMENT,504 accepted, queued\nrestart committed and DODGE MOVEMENT ACTIVE. No GLIDE350 marker should appear.\nCHECK_AQUA_V17.cmd checks installed asset hashes and writes\nAqua_Animation_Check_v17.txt; drag the OpenKH folder onto it if needed.\nA short side-view recording will help verify the visible head correction.\n\nVALIDATION\n71 actual-PE runtime checks and22 geometry/assignment checks passed offline.\nTests cover both banks, new combo assignments and strike phase, all five\nprofiles, untouched native Glide bodies/clocks/queues,2x lift/direction with\nunchanged504 timing, native handoff, original Blizzard events and restoration.\nRun checks verify skull150's native skin flag, authored head orientation and\nneutral hair helper151. All original motion headers, sizes, frame/bone/helper\ncounts and travel remain. Both installed MSETs are original. There are47 mapped\nnormal records and46 Olympus records; native Glide is deliberately not mapped.\nWindows/KH1 and the rendered mesh were not executed here. In-game visual quality,\ncontroller feel and collision still need verification.\n\nFILES\nANIMATION_MAP.csv / SPELL_MAPPING.csv: current five-profile assignments/casts.\nCOMBO_TIMING.csv: first/second contacts and full-swing recovery windows.\nAIR_DODGE_MAPPING.csv: Dual D baseline,2x travel and timing.\nGLIDE_MAPPING.csv: original native Glide scope. RUN_POSE.csv: skin/head mapping.\nTEST_CLIP_SOURCES.csv: source banks, frames, rates, cuts and hashes.\nsource: rebuild code, original/fitted fixtures, checks and evidence reports.\ninventory: existing349-clip source inventory. Numeric IDs are source labels;\nofficial BBS move names remain unverified where the inventory says so.\n\nOPTIONAL DISABLE / REMOVE\nCopy DISABLE_AIR_DODGE_kh1-aqua.ini beside the EXE as kh1-aqua.ini and restart\nto disable only504 input/movement. Glide remains fully native. Remove the INI\nand restart to reenable. To remove all five abilities, use REMOVE_AQUA_kh1-aqua.ini\nas kh1-aqua.ini, leave v17 enabled, restart/load each save, check ABILITIES REMOVED,\nsave in-game, exit, remove the INI, disable v17 and rebuild. Only IDs117..121 are\nremoved. Profile/body switching/restoration waits until idle.\n"
SOURCE="AQUA V17 SOURCE / REPRODUCIBILITY\n\nBuild DLL on Linux with Python3, GCC and GNU ld PE support:\n python3 generate_data.py\n python3 build.py\n python3 test_runtime.py\n python3 test_visuals.py\nNumPy/SciPy are needed for pose fitting/geometry. Runtime tests map the actual\nemitted PE with Win64 ABI/import mocks; they are not Windows/KH1 execution.\n\nOptional source pose rebuild from this source directory:\n python3 retargeting/tools/build_aqua_complete_v17.py --profile 0 --output .\n python3 retargeting/tools/build_aqua_complete_v17.py --profile 1 --output sets/p1\nProfiles2..4 use sets/p2..p4;5 uses dodge;7 uses blizzard. No profile6 Glide\nclosing overlay exists in v17. The builder resolves its model/PAM/ARC inputs\nbelow retargeting, with original MSETs in ../assets. --slots limits records.\nThe immutable sampling baseline is refined once. Regenerate data, rebuild and\nrun checks after changing fixtures. Previous plan/refiner modules are explicit\ndependencies, not the current behavior. The v17 CSVs and plan are authoritative.\n\nMain ground300/300/366; air305/407/351. Both99/100 use300 and complete it at\nnative32/44 before kind5 chain windows32..48/44..64. Contact times are selected\nfrom the first300 pose's12/47 phase:384/47 and528/47 native frames. First98\nretains contact12 and chain22..40. Existing event payloads, descriptors, counts,\nencoded handles and sound/effect keys stay original. Only existing hit/chain\nframe floats change for main98/99/100; numbered tests use native event timing.\nThe actual native event sampler0x394770 is exercised by the runtime tests.\n\nDefault Glide:75..78 are absent from the47-record Aqua patch table. There are\nno Glide body writes, clocks, queued-frame edits, opening/holding/closing state,\n350 fall overlays or extra endings. The only remaining Glide hook is the\nexisting constructor guard for active504; every other call resumes native code.\nTests populate independent original Glide records in both mock banks and verify\nall bytes, clocks and queued start frames through all five profiles and turns.\n\nDual D2x: the earlier v52 log recorded growth height145 and speed18. The supplied\nNineStyles_v52.patch aerial_dodge_step multiplies displacement by2 while leaving\ntiming unchanged. V17 stores unscaled145/18 baseline motion and applies2 to all\nrequested XYZ displacement and handoff velocity values. The existing40-frame504\nvisual and once-per-airtime/free-air input policy remain. The KH1 gravity/release\nadapter (.75 /4 /20 baseline) remains explicit: exact KH2 coefficients and motion\n202's length are absent, so this does not claim a complete KH2 controller import.\nNative collision resolves the displacement. No actor+10 position writes occur.\n\nRun head fix: native MDLS link word bit30..31 identifies skinned bones. Joint150\nhas skin flag1; helper151 has flag0. V16 incorrectly added lift at151, moving\nhair without the skull. V17 refines only run5/6/7: transfer the authored source\nhead5 orientation (formerly mapped to151) to150 and restore151's bind rotation.\nSkull150 and the attached subtree then follow the same head. No torso/neck,\nattachment translation, bind length, scale or travel change is introduced.\nThe geometry test compares the REAL skinned skull150 to independent frozen\npre-v16 authored-head fixtures, and checks the raw native skin flags/hair local.\n\nBlizzard remains the v16 selector: logical37/84 and original native event tracks\nstay; main casts temporarily receive full391/316 bodies in55/80. No native spell\nqueue append, terminal reordering, projectile/MP hook or element change exists.\nRestore the shared317/390 pose on the next action, off or profile transition.\nKeyblade-tip attachment0x30, original native defensive windows and all numbered\ncombo/cast fixtures remain. Five saved zero-AP IDs117..121 remain exclusive.\n\nNative hook anchors and source/log evidence are in the validation JSON files.\nThe original Steam Global EXE timestamp1721645006 has SHA256\n d790746245d26159f3ee0e1060e33b2fa2de06941850a4ac724f598722884bac.\nIts full bytes and the user's video/log are not redistributed. Existing upstream\nlicenses remain in licenses. Test limits are stated in README_FIRST.txt.\n"

def build():
    runtime=load(D/'runtime_validation.json');geometry=load(D/'visual_validation.json')
    reports=[load(D/'curve_validation.json')]+[load(D/f'sets/p{i}/curve_validation.json') for i in range(1,5)]
    extra=[(name,load(D/name/'curve_validation.json')) for name in ['dodge','blizzard']]
    assert runtime['passed'] and geometry['passed'] and runtime['tests']==71 and geometry['tests']==22
    assert all(r['passed'] for r in reports+[r for _,r in extra]) and len(reports[0]['motions'])==47
    if DEST.exists():shutil.rmtree(DEST)
    shutil.copytree(ROOT/'KH1FM_Aqua_Animation_Test_v16',DEST,ignore=shutil.ignore_patterns('__pycache__','*.so','*.o','*.obj','sampling_cache','kh1-aqua.dll'))
    for p in DEST.glob('*v16*'):p.unlink()
    if (DEST/'source/glide_stop').exists():shutil.rmtree(DEST/'source/glide_stop')
    for name in ['fixtures','sets','dodge','blizzard']:
        target=DEST/'source'/name
        if target.exists():shutil.rmtree(target)
        shutil.copytree(D/name,target,ignore=shutil.ignore_patterns('__pycache__'))
    names=['aqua.c','aqua_magic.h','aqua_cast_requests.h','aqua_air_dodge.h','aqua_blizzard.h','aqua_data.h','build.py','generate_data.py','test_runtime.py','test_bridge.c','test_visuals.py']
    names+=sorted(p.name for p in D.glob('*validation.json'))
    names+=['source_selections.json']
    for name in names:shutil.copy2(D/name,DEST/'source'/name)
    shutil.copy2(D/'kh1-aqua.dll',DEST/'dll/kh1-aqua.dll')
    tools=DEST/'source/retargeting/tools'
    for name in ['aqua_v16_plan.py','aqua_v17_plan.py','aqua_event_timing_v17.py','aqua_refine_v17.py','build_aqua_complete_v17.py','package_aqua_v17.py','validate_aqua_v17.py']:
        shutil.copy2(ROOT/'tools'/name,tools/name)
    for name in sorted(set(BANK.values())):shutil.copy2(D/'source_arcs'/name,DEST/'source/retargeting/core_source'/name)
    (DEST/'README_FIRST.txt').write_text(README);(DEST/'source/README_SOURCE.txt').write_text(SOURCE)
    mod=(DEST/'mod.yml').read_text();a=mod.index('description:');b=mod.index('assets:')
    mod=mod[:a]+'''description: >-
  Aqua v17: ground300/300/366 and air305/407/351, retained native Blizzard events with Fire visuals and full second-swing recovery, native default Glide, Dual D145/18 baseline at2x504 travel and corrected skinned-head running direction. Five0-AP abilities; original MSETs. Steam Global/Panacea.
'''+mod[b:]
    (DEST/'mod.yml').write_text(mod.replace('Test v16','Test v17'))
    checker=(ROOT/'KH1FM_Aqua_Animation_Test_v16/Check_Aqua_Animations_v16.ps1').read_text().replace('v16','v17').replace('V16','V17')
    (DEST/'Check_Aqua_Animations_v17.ps1').write_text(checker)
    (DEST/'CHECK_AQUA_V16.cmd').unlink(missing_ok=True)
    (DEST/'CHECK_AQUA_V17.cmd').write_bytes(b'@echo off\r\nsetlocal\r\npowershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check_Aqua_Animations_v17.ps1" %*\r\npause\r\n')
    for name,remove,air in [('REMOVE_AQUA',1,0),('DISABLE_AIR_DODGE',0,0)]:
        (DEST/f'{name}_kh1-aqua.ini').write_text(f'[aqua]\nremove_aqua={remove}\nhand_magic=0\nair_dodge={air}\n')
    labels=['aqua']+[f'aqua {i}' for i in range(1,5)]
    (DEST/'ABILITY_SETS.txt').write_text('\n'.join([f'{label} / id{117+i} /0AP / ground '+('300 300 366 / air305 407 351' if i==0 else ' '.join(SETS[i-1][0])+' / air'+' '.join(SETS[i-1][1])) for i,label in enumerate(labels)])+'\n\nv17: select one while idle. See README_FIRST.txt for current changes and test order.\n')
    maps=[];spells=[];airmaps=[];glides=[];runs=[]
    base={r['normal_slot']:r for r in reports[0]['motions']}
    for profile,label in enumerate(labels):
        active=dict(base)
        if profile:active.update({r['normal_slot']:r for r in reports[profile]['motions']})
        for r in sorted(active.values(),key=lambda r:r['normal_slot']):
            maps.append({'Ability':label,'Ability id':117+profile,'Action':r['action'],'Native request':f'0x{r["request"]:02X}',
                'Normal slot':r['normal_slot'],'Olympus slot':r['olympus_slot'] if r['olympus_slot']!=0xffffffff else 'not present',
                'Aqua clip':r['donor'],'Source aliases':r.get('source_aliases',''),'Source bank':r['source_bank'],'Source frame range':str(r['source_range']) if r['source_range'] else 'full',
                'Pose loop':r['loop'],'Native frames':r['native_frames'],'Source timing':r.get('source_timing','linear'),'Native hold frame':r.get('native_hold_frame',''),
                'Run head mapping':r.get('run_head_mapping',''),'Root policy':r['root']})
        for aerial in [False,True]:
            table=(D/f"fixtures/requests_normal_{'main' if profile==0 else 'aqua'}.bin").read_bytes()
            he=(D/f"fixtures/requests_he_{'main' if profile==0 else 'aqua'}.bin").read_bytes()
            for index,spell in enumerate(['Fire','Blizzard','Thunder','Cure','Gravity','Stop','Aero']):
                request=(0x83 if aerial else 0x36)+index;slot=struct.unpack_from('<I',table,request*4)[0]&0xfff
                row=active[slot];clip=('316' if aerial else '391') if spell=='Blizzard' and profile==0 else row['donor']
                spells.append({'Ability':label,'Ability id':117+profile,'Spell':spell,'Mode':'air' if aerial else 'ground',
                    'Aqua clip':clip,'Native request':f'0x{request:02X}','Normal slot':slot,'Olympus slot':struct.unpack_from('<I',he,request*4)[0]&0xfff,
                    'Native frames':row['native_frames'],'Transient body selector':spell=='Blizzard' and profile==0,
                    'Original native spell event tracks':True,'Native recovery normal slot':(82 if aerial else 57) if spell=='Fire' else ''})
        airmaps.append({'Ability':label,'Ability id':117+profile,'Aqua clip':'504','Trigger':'Fresh airborne Circle after release; once per airtime',
            'Neutral stick':'vertical lift','Tilted stick':'vertical lift plus normalized stick direction','Dual D base height':145,'Dual D base speed':18,'Travel multiplier':2,'Effective full held rise':290,'Effective horizontal speed':36,
            'Native frames':40,'Fall clip':'506','Collision':'native displacement callback before collision','Extra defense or damage':False})
        glides.append({'Ability':label,'Visual':'original Sora native Glide','Normal slots':'75,76,77,78','Olympus slots':'37,38,39,40','Aqua overrides':0,'Clock and queued frame changes':0,'Opening flight ending':'native','Normal fall after native exit':'506'})
        for slot in [5,6,7]:runs.append({'Ability':label,'Normal slot':slot,'Aqua clip':active[slot]['donor'],'Corrected SKIN joint':150,'Authored head source bone':5,'Hair helper151 local':'native bind','Torso and neck retained':True,'Bind lengths and scale retained':True})
    for name,rows in [('ANIMATION_MAP.csv',maps),('SPELL_MAPPING.csv',spells),('AIR_DODGE_MAPPING.csv',airmaps),('GLIDE_MAPPING.csv',glides),('RUN_POSE.csv',runs)]:csv_file(name,rows)
    timing=load(D/'combo_timing_validation.json');combo=[]
    for slot in [98,99,100]:
        r=base[slot];t=timing['variants'][str(slot)]
        combo.append({'Ability':'aqua','Normal slot':slot,'Olympus slot':r['olympus_slot'],'Aqua clip':r['donor'],'Native frames':r['native_frames'],
            'Contact frame':t['contact_after'],'Full source finishes frame':r.get('native_hold_frame',r['native_frames']-1),
            'Next hit enabled frame':t['chain_opens'],'Chain window closes frame':t['chain_closes'],'Chain window native frames':t['chain_closes']-t['chain_opens'],
            'Sound effect keys and all event payloads original':True})
    csv_file('COMBO_TIMING.csv',combo)
    from bbs_source_inspector import read_arc,read_pam
    source_rows=[]
    for profile,report in enumerate(reports+[r for _,r in extra]):
        for r in report['motions']:
            if r['source_bank']=='base':
                payload=(ROOT/'core_source/p02ex_001.pam').read_bytes();members=[('p02ex_001.pam',payload)]
            else:
                arc=D/'source_arcs'/r['source_bank']
                if not arc.exists():arc=DEST/'source/retargeting/core_source'/r['source_bank']
                members,_=read_arc(arc.read_bytes())
            found=[]
            for member,data in members:
                if not data.startswith(b'PAM\0'):continue
                for animation in read_pam(data,54):
                    if animation.name!=r['donor']:continue
                    start=struct.unpack_from('<I',data,16+16*animation.slot)[0];digest=hashlib.sha256(data[start:animation.data_end]).hexdigest()
                    if r.get('source_sha256'):assert digest==r['source_sha256']
                    found.append({'Ability':labels[profile] if profile<5 else ['all Aqua entries: dodge','main Aqua: Blizzard'][profile-5],
                        'Action':r['action'],'Normal slot':r['normal_slot'],'Source name':animation.name,'Source aliases':r.get('source_aliases',''),
                        'Source bank':r['source_bank'],'PAM member':member,'Source frames':animation.frame_count,'Source FPS':animation.fps,
                        'Source frame range':str(r['source_range']) if r['source_range'] else 'full','Animation SHA256':digest,'Native frames':r['native_frames'],'Source timing':r.get('source_timing','linear')})
            assert len(found)==1,(r['donor'],r['source_bank'],len(found));source_rows+=found
    csv_file('TEST_CLIP_SOURCES.csv',source_rows)
    expected={'version':17,'assets':[]}
    for name,local in [('dll/kh1-aqua.dll','dll/kh1-aqua.dll'),('xa_ex_0010.mset','assets/xa_ex_0010.mset'),('xa_ex_0010_he.mset','assets/xa_ex_0010_he.mset')]:
        p=DEST/local;expected['assets'].append({'name':name,'sha256':sha(p),'bytes':p.stat().st_size})
    write_json(DEST/'expected_assets.json',expected)
    distinct={};assignments=0
    folders=[(D,reports[0])]+[(D/f'sets/p{i}',reports[i]) for i in range(1,5)]+[(D/name,r) for name,r in extra]
    for folder,rpt in folders:
        assignments+=len(rpt['motions'])
        for r in rpt['motions']:distinct.setdefault((r['normal_slot'],sha(folder/f"fixtures/aqua_{r['fixture_stem']}.bin")),r)
    values=list(distinct.values())
    validation={'version':17,'test_round':'revised Test4','offline_checks_passed':True,'game_runtime_tested':False,
        'abilities':labels,'ability_ids':list(range(117,122)),'main_ground_combo':['300','300','366'],'main_air_combo':['305','407','351'],
        'main_blizzard_ground_air':['391','316'],'blizzard_native_lookup_and_events_restored':True,'blizzard_added_queue_entries':0,
        'ground_contact_frames':[12,384/47,528/47],'second_source_finish_and_chain_open_frames':[32,44],'second_chain_window_widths':[16,20],
        'glide':'original native default; no Aqua overrides','air_dodge':'504 Dual D145/18 baseline at2x displacement, unchanged duration','run_head_skin_joint':150,'run_head_direction':'authored source head5; hair helper151 at bind',
        'keyblade_tip_magic':True,'numbered_combo_and_cast_poses_retained':True,'test_sets':SETS,'native_motion_headers_counts_and_sizes_preserved':True,
        'normal_motion_records':47,'olympus_motion_records':46,'helper_slots':11,'original_installed_msets':True,
        'serialized_profile_and_transient_assignments':assignments,'distinct_fitted_records':len(values),
        'runtime_pe_tests':runtime['tests'],'geometry_tests':geometry['tests'],
        'pose_samples':sum(r['validated_pose_samples'] for r in values),'max_pose_position_fit_error':max(r['max_pose_position_error'] for r in values),
        'max_pose_basis_fit_error':max(r['max_pose_basis_error'] for r in values),
        'max_native_travel_error':max(r['root_helper_error'] for r in values),
        'max_scale_error':max(r['max_scale_error'] for r in values),'dll_sha256':sha(DEST/'dll/kh1-aqua.dll'),
        'limitations':['No Windows/KH1 or rendered-mesh test performed','Dual D growth145/18 and2x policy matched; existing KH1 gravity/release adapter retained','Spell release, collision, contact feel, Glide transitions and run appearance require in-game testing']}
    write_json(DEST/'validation.json',validation)
    assert len(maps)==235 and len(spells)==70 and len(source_rows)==assignments and assignments==102
    assert len(values)==81,(len(values),assignments)
    for suffix in ['', '_he']:assert (DEST/f'assets/xa_ex_0010{suffix}.mset').read_bytes()==(ROOT/f'sora_source/Custom Movesets KH1/xa_ex_0010{suffix}.mset').read_bytes()
    with zipfile.ZipFile(DEST.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.so','.o','.obj']:z.write(p,p.relative_to(DEST))
    with zipfile.ZipFile(DEST.with_suffix('.zip')) as z:assert z.testzip() is None
    print(json.dumps({'zip':str(DEST.with_suffix('.zip')),'bytes':DEST.with_suffix('.zip').stat().st_size,'sha256':sha(DEST.with_suffix('.zip')),'validation':validation},indent=2))
if __name__=='__main__':build()
