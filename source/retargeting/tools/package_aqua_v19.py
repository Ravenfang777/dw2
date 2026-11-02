"""Ship verified v19 sources, mappings and a standalone Panacea test ZIP."""
from pathlib import Path
import csv,hashlib,json,shutil,struct,zipfile
from aqua_v19_plan import SETS,BANK
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'KH1FM_Aqua_Animation_Test_v19'
D=ROOT/'ability_v19'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write_json(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
def csv_file(name,rows):
    with (DEST/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

README="KH1FM AQUA ANIMATION TEST v19\nSteam Global / OpenKH Panacea\n\nCHANGES APPLY TO THE MAIN aqua ABILITY\nGround: 300 -> 301 -> 366, with the first12 source frames removed from366.\nAir: 305 -> 353 -> 407.\nCombat idle: skinned skull turns20 degrees left.\nAerial Fire AND Blizzard: skinned skull turns20 degrees right. Fire recovery\nuses the same adjustment so the head does not snap between cast portions.\nNormal run now uses013; combat run now uses004. Both remain proper loops.\n\nGUARD\nAqua400 plays fully forward once, then fully backward once, at its source30fps\nspeed. Nominal total duration is2.6 seconds. The native guard window spans the\nwhole sequence. Native Guard selection must succeed; Guard still needs to be\nequipped. The main ability does not grant Guard automatically.\n\nThe controller observes native Guard action row0x3D, then changes only the\nnative actor-motion delta for that action. It bypasses the facing-cone check\nfor Sora's own live native Guard objects during that witnessed action.\nNative contact, priorities, projectile deflection, feedback and attacks that\ncannot normally be guarded still use the game's handling. This is all-angle\nGuard, not permanent invulnerability. Interruption, unload or ability changes\nend its extra controller behavior. Other actions do not gain all-angle defense.\n\nThe animation headers,54-frame record, bone/helper counts, allocations and\noriginal MSET files remain unchanged. The native motion clock advances more\nslowly for Guard. The finisher's native motion clock advances faster after the\nsource trim so removing its beginning actually shortens the action.\n\nTAP DODGE REPLACES HELD GLIDE\nIn the air, release Circle after takeoff and then tap Circle. Main aqua starts\n504 once and suppresses normal held-Glide activation. It captures the character\nmovement direction at that tap, then travels for the full animation with small\nupward lift. Releasing Circle or the stick does not shorten it or stop travel.\nWhen the animation finishes,506 falling resumes. Release then tap again after\ncompletion to perform another burst. Holding Circle never repeats the burst\nand never returns to held Glide while main aqua remains active.\n\nDirection uses the native movement vector. With neutral input it uses existing\nhorizontal momentum, then character facing if stationary. Main travel uses a\nnormalized direction at speed14 per native time unit, with lift0.75 over39 units\n(the existing40-frame visual). A full unobstructed burst requests546 horizontal\nunits and29.25 lift. Native walls, ceilings, landing and interruptions still\napply. Actor positions are never written directly. The air_dodge=0 diagnostic\noption restores native air input/Glide.\n\nNUMBERED TEST ABILITIES RETAIN v18\n aqua1 ground371 365 366 / air218 332 393\n aqua2 ground352 353 407 / air351 304 303\n aqua3 ground300 301 302 / air616 407 351\n aqua4 ground510 511 512 / air504 514 399\nTheir combos, casts, idle, runs, Guard animation/timing, steered dodge and normal\nGlide retain v18 behavior. Main changes are isolated with explicit older common\npose payloads. All five ability IDs117..121 and0AP are retained.\n\nOTHER RETAINED BEHAVIOR\nMain ground300/301, keyblade-tip magic, native Blizzard events with Fire poses,\noriginal KH1 Sora damage/knockback, idle hair bind correction and remaining\nAqua animations. Default KH2 Sora reactions are still pending P_EX100 source\nassets; no KH2 reaction replacement is claimed here.\n\nINSTALL / TEST\n1. Fully close KH1. Disable the previous Aqua test and any NineStyles/Dual Wield\n   or KH2 Combat build. Install this v19 ZIP in OpenKH, then Build and Run.\n2. Equip MAIN aqua while idle. The log banner must sayv19.\n3. Test Guard entry, reverse exit and attacks approaching from front/side/rear.\n4. Test ground300/301/trimmed366 and air305/353/407.\n5. Tap Circle airborne with a direction, release both inputs and watch the full\n   burst. Hold Circle afterward: it must not begin normal Glide. Test a new tap.\n6. Check combat idle, aerial Fire/Blizzard head direction and both run variants.\n7. Switch to a numbered test while idle to check its unchanged v18 behavior.\n\nVALIDATION\nOffline checks execute the actual PE DLL in a Win64 ABI mock and sample the\nserialized poses. New hook anchors and control paths are checked against the\nsupplied Steam executable. No live Windows/KH1 game rendering or playtest is\nclaimed. Please return kh1-aqua.log and a short video if timing, directional\nblocking, movement or head orientation needs adjustment.\n"
SOURCE="AQUA v19 SOURCE\nBuild with Python3.12, GCC and GNU binutils:\n  python3 generate_data.py\n  python3 build.py\n  python3 test_runtime.py\n  python3 test_visuals.py\nNo Windows SDK is needed. Tests use a Linux Win64 ABI mock, not KH1.\n\nNew main-only controller: aqua_guard.h. It observes native row0x3D at2A3980,\nscales the actor-motion delta at29F0A0 and scopes the facing-angle check at\n2B4640 to Sora's own live Guard objects. No HP/hurt interceptor or direct\nanimation-clock/position writes. The three hooks admit all original prefixes\nand protect all destinations before publishing; failures restore permissions\nwithout a partial patch. Guard delta53/156 yields source30fps forward/reverse;\nfinisher delta47/35 preserves the remaining source's prior speed after trim.\n\nRetarget tools are under retargeting/tools. Regenerate with:\n  python3 retargeting/tools/build_aqua_complete_v19.py --profile 0\nProfiles1..4 are numbered,5 is dodge,7 is main Blizzard. Selective --slots works.\nNative motion headers, sizes and pointer/descriptor counts remain unchanged.\nEvent time edits use existing keys and preserve their payloads. Numbered poses\nthat would otherwise inherit new main changes explicitly retain v18 payloads.\n\nMain head turns use real SKIN skull150. The run swap preserves native travel,\nclosed loops, authored source head mapping and original segment lengths.\nTap dodge uses504 in the existing fall record and native collision callbacks.\nNumbered profiles retain v18 behavior. Default KH2 reactions remain pending.\n"

def build():
    runtime=load(D/'runtime_validation.json');geometry=load(D/'visual_validation.json')
    reports=[load(D/'curve_validation.json')]+[load(D/f'sets/p{i}/curve_validation.json') for i in range(1,5)]
    extra=[(name,load(D/name/'curve_validation.json')) for name in ['dodge','blizzard']]
    assert runtime['passed'] and geometry['passed'] and runtime['tests']==81 and geometry['tests']==26
    assert all(r['passed'] for r in reports+[r for _,r in extra]) and len(reports[0]['motions'])==37
    if DEST.exists():shutil.rmtree(DEST)
    shutil.copytree(ROOT/'KH1FM_Aqua_Animation_Test_v18',DEST,ignore=shutil.ignore_patterns('__pycache__','*.so','*.o','*.obj','sampling_cache','kh1-aqua.dll'))
    for p in DEST.glob('*v18*'):p.unlink()
    if (DEST/'source/glide_stop').exists():shutil.rmtree(DEST/'source/glide_stop')
    for name in ['fixtures','sets','dodge','blizzard']:
        target=DEST/'source'/name
        if target.exists():shutil.rmtree(target)
        shutil.copytree(D/name,target,ignore=shutil.ignore_patterns('__pycache__'))
    names=['aqua.c','aqua_guard.h','aqua_magic.h','aqua_cast_requests.h','aqua_air_dodge.h','aqua_blizzard.h','aqua_data.h','build.py','generate_data.py','test_runtime.py','test_bridge.c','test_visuals.py']
    names+=sorted(p.name for p in D.glob('*validation.json'))
    names+=['source_selections.json','Collect_KH2_Sora_Source.ps1']
    for name in names:shutil.copy2(D/name,DEST/'source'/name)
    shutil.copy2(D/'kh1-aqua.dll',DEST/'dll/kh1-aqua.dll')
    tools=DEST/'source/retargeting/tools'
    for name in ['aqua_v16_plan.py','aqua_v17_plan.py','aqua_v19_plan.py','aqua_event_timing_v17.py','aqua_refine_v17.py','aqua_event_timing_v19.py','aqua_refine_v19.py','build_aqua_complete_v19.py','package_aqua_v19.py','validate_aqua_v19.py']:
        shutil.copy2(ROOT/'tools'/name,tools/name)
    for name in sorted(set(BANK.values())):shutil.copy2(D/'source_arcs'/name,DEST/'source/retargeting/core_source'/name)
    shutil.copy2(D/'Collect_KH2_Sora_Source.ps1',DEST/'Collect_KH2_Sora_Source.ps1')
    (DEST/'COLLECT_KH2_SORA_SOURCE.cmd').write_bytes(b'@echo off\r\nsetlocal\r\npowershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File \"%~dp0Collect_KH2_Sora_Source.ps1\" %*\r\npause\r\n')
    (DEST/'README_FIRST.txt').write_text(README);(DEST/'source/README_SOURCE.txt').write_text(SOURCE)
    mod=(DEST/'mod.yml').read_text();a=mod.index('description:');b=mod.index('assets:')
    mod=mod[:a]+'''description: >-
  Aqua v19 main: normal-speed full-duration all-angle Guard, air305/353/407,366 trimmed12 source frames, tap504 replaces Glide, head yaw and swapped run loops. Numbered tests retain v18. Original MSETs and native reactions. Steam Global/Panacea.
'''+mod[b:]
    (DEST/'mod.yml').write_text(mod.replace('Test v18','Test v19'))
    checker=(ROOT/'KH1FM_Aqua_Animation_Test_v18/Check_Aqua_Animations_v18.ps1').read_text().replace('v18','v19').replace('V18','V19')
    (DEST/'Check_Aqua_Animations_v19.ps1').write_text(checker)
    (DEST/'CHECK_AQUA_V18.cmd').unlink(missing_ok=True)
    (DEST/'Check_Aqua_Animations_v18.ps1').unlink(missing_ok=True)
    (DEST/'CHECK_AQUA_V19.cmd').write_bytes(b'@echo off\r\nsetlocal\r\npowershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check_Aqua_Animations_v19.ps1" %*\r\npause\r\n')
    for name,remove,air in [('REMOVE_AQUA',1,0),('DISABLE_AIR_DODGE',0,0)]:
        (DEST/f'{name}_kh1-aqua.ini').write_text(f'[aqua]\nremove_aqua={remove}\nhand_magic=0\nair_dodge={air}\n')
    labels=['aqua']+[f'aqua {i}' for i in range(1,5)]
    (DEST/'ABILITY_SETS.txt').write_text('\n'.join([f'{label} / id{117+i} /0AP / ground '+('300 301 366 / air305 353 407' if i==0 else ' '.join(SETS[i-1][0])+' / air'+' '.join(SETS[i-1][1])) for i,label in enumerate(labels)])+'\n\nv19: select one while idle. See README_FIRST.txt for current changes and test order.\n')
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
                'Run head mapping':r.get('run_head_mapping',''),'Head yaw degrees':r.get('head_yaw_character_degrees',0),'Runtime rate':r.get('runtime_playback_rate',1),'Root policy':r['root']})
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
        airmaps.append({'Ability':label,'Ability id':117+profile,'Aqua clip':'504',
            'Trigger':'fresh airborne tap, replaces held Glide' if profile==0 else 'v18 fresh Circle once per airtime',
            'Direction':'captured movement, then momentum/facing fallback' if profile==0 else 'live stick steering',
            'Release stops travel':False if profile==0 else 'neutral brakes horizontal',
            'Native frames':40,'Speed':14,'Lift per native unit':.75,'Requested duration':39,'Fall clip':'506'})
        glides.append({'Ability':label,'Visual':'504 tap replacement' if profile==0 else 'original Sora native Glide',
            'Native motion slots':'75,76,77,78','Native motion bytes changed':False,
            'Held Glide activation':'suppressed' if profile==0 else 'v18 native',
            'Native clocks unmodified':True,'Fall after exit':'506'})
        for slot in [5,6,7]:runs.append({'Ability':label,'Normal slot':slot,'Aqua clip':active[slot]['donor'],'Corrected SKIN joint':150,'Authored head source bone':5,'Hair helper151 local':'native bind','Torso and neck retained':True,'Bind lengths and scale retained':True})
    for name,rows in [('ANIMATION_MAP.csv',maps),('SPELL_MAPPING.csv',spells),('AIR_DODGE_MAPPING.csv',airmaps),('GLIDE_MAPPING.csv',glides),('RUN_POSE.csv',runs)]:csv_file(name,rows)
    guard=[];reactions=[]
    native=load(D/'fixtures/native_reactions.json')
    for label in labels:
        guard.append({'Ability':label,'Aqua clip':'400','Normal slot':110,'Olympus slot':72,
            'Forward timeline':'0..26.5' if label=='aqua' else 'v18 0..10',
            'Reverse timeline':'26.5..53' if label=='aqua' else 'v18 36..52',
            'Native motion delta factor':53./156. if label=='aqua' else 1.,
            'Defense window':'0..54' if label=='aqua' else 'v18 native',
            'Facing restriction':'all angles for witnessed native Guard' if label=='aqua' else 'v18 native'})
        for row in native:
            reactions.append({'Ability':label,'Request':f'0x{row["request"]:02X}','Normal slot':row['normal_slot'],
                'Olympus slot':row['olympus_slot'],'Native frames':row['frames'],'Current animation':'original KH1 Sora',
                'Aqua override':False,'Requested replacement':'default KH2 Sora','Status':'pending source P_EX100.mdlx and P_EX100.mset'})
    csv_file('GUARD_MAPPING.csv',guard);csv_file('DAMAGE_REACTIONS.csv',reactions)
    from kh1_motion_source import read_mset
    raw=(ROOT/'sora_source/Custom Movesets KH1/xa_ex_0010.mset').read_bytes()
    bank=read_mset(raw);table=raw[struct.unpack_from('<I',raw,8)[0]:struct.unpack_from('<I',raw,12)[0]]
    untouched=[]
    for slot,motion in enumerate(bank['motions']):
        if motion is None or slot in base:continue
        requests=[f'0x{request:02X}' for request in range(len(table)//4) if (struct.unpack_from('<I',table,request*4)[0]&0xfff)==slot]
        status='Original native action; no Aqua replacement'
        if 61<=slot<=70:status='Original KH1 Sora damage; default KH2 replacement pending source'
        elif 75<=slot<=78:status='Original native Glide'
        untouched.append({'Normal slot':slot,'Native request descriptors':' / '.join(requests),'Frames':motion.frames,'Status':status})
    csv_file('REMAINING_NATIVE.csv',untouched)
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
    expected={'version':19,'assets':[]}
    for name,local in [('dll/kh1-aqua.dll','dll/kh1-aqua.dll'),('xa_ex_0010.mset','assets/xa_ex_0010.mset'),('xa_ex_0010_he.mset','assets/xa_ex_0010_he.mset')]:
        p=DEST/local;expected['assets'].append({'name':name,'sha256':sha(p),'bytes':p.stat().st_size})
    write_json(DEST/'expected_assets.json',expected)
    distinct={};assignments=0
    folders=[(D,reports[0])]+[(D/f'sets/p{i}',reports[i]) for i in range(1,5)]+[(D/name,r) for name,r in extra]
    for folder,rpt in folders:
        assignments+=len(rpt['motions'])
        for r in rpt['motions']:distinct.setdefault((r['normal_slot'],sha(folder/f"fixtures/aqua_{r['fixture_stem']}.bin")),r)
    values=list(distinct.values())
    validation={'version':19,'test_round':'main Aqua controller and pose revisions','offline_checks_passed':True,'game_runtime_tested':False,
        'abilities':labels,'ability_ids':list(range(117,122)),'main_ground_combo':['300','301','366'],'main_air_combo':['305','353','407'],
        'main_blizzard_ground_air':['391','316'],'blizzard_native_lookup_and_events_restored':True,'blizzard_added_queue_entries':0,
        'ground_contact_frames':[12,6.4,8.8],'second_source_finish_and_chain_open_frames':[32,44],'second_chain_window_widths':[16,20],
        'glide':'main replaced by tap504; numbered native Glide','air_dodge':'main504 captured movement direction, tap replaces held Glide; speed14 lift0.75 duration39','run_head_skin_joint':150,'run_head_direction':'authored source head5; hair helper151 at bind',
        'keyblade_tip_magic':True,'numbered_cast_poses_retained':True,'numbered_profiles_preserved_from_v18':True,'aqua3_air_and_aqua4_retained':True,'test_sets':SETS,'native_motion_headers_counts_and_sizes_preserved':True,
        'normal_motion_records':37,'olympus_motion_records':36,'helper_slots':11,'original_installed_msets':True,'kh2_damage_replacement_completed':False,'damage_reactions_current':'native KH1 Sora; KH2 source pending','idle_front_hair_joints_at_bind':[151,152,153,154],'guard_source':'main400 normal source30fps forward/reverse, full guard window and all-angle native contacts',
        'serialized_profile_and_transient_assignments':assignments,'distinct_fitted_records':len(values),
        'runtime_pe_tests':runtime['tests'],'geometry_tests':geometry['tests'],
        'pose_samples':sum(r['validated_pose_samples'] for r in values),'max_pose_position_fit_error':max(r['max_pose_position_error'] for r in values),
        'max_pose_basis_fit_error':max(r['max_pose_basis_error'] for r in values),
        'max_native_travel_error':max(r['root_helper_error'] for r in values),
        'max_scale_error':max(r['max_scale_error'] for r in values),'dll_sha256':sha(DEST/'dll/kh1-aqua.dll'),
        'limitations':['No Windows/KH1 or rendered-mesh test performed','Default KH2 Sora reaction source missing; original KH1 Sora reactions used pending capture','Spell release, collision, contact feel, Glide transitions and run appearance require in-game testing']}
    write_json(DEST/'validation.json',validation)
    assert len(maps)==185 and len(spells)==70 and len(source_rows)==assignments and assignments==112
    for suffix in ['', '_he']:assert (DEST/f'assets/xa_ex_0010{suffix}.mset').read_bytes()==(ROOT/f'sora_source/Custom Movesets KH1/xa_ex_0010{suffix}.mset').read_bytes()
    with zipfile.ZipFile(DEST.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.so','.o','.obj']:z.write(p,p.relative_to(DEST))
    with zipfile.ZipFile(DEST.with_suffix('.zip')) as z:assert z.testzip() is None
    print(json.dumps({'zip':str(DEST.with_suffix('.zip')),'bytes':DEST.with_suffix('.zip').stat().st_size,'sha256':sha(DEST.with_suffix('.zip')),'validation':validation},indent=2))
if __name__=='__main__':build()
