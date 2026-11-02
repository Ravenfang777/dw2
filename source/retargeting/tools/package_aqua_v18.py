"""Ship verified v18 sources, mappings and a standalone Panacea test ZIP."""
from pathlib import Path
import csv,hashlib,json,shutil,struct,zipfile
from aqua_v18_plan import SETS,BANK
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'KH1FM_Aqua_Animation_Test_v18'
D=ROOT/'ability_v18'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write_json(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
def csv_file(name,rows):
    with (DEST/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

README="KH1FM AQUA ANIMATION TEST v18\nSteam Global / OpenKH Panacea\n\nMAIN AQUA\nGround: 300 -> 301 -> 366. Air: 305 -> 407 -> 351.\n301 is fitted into both native second-ground variants. Its full source plays\nbefore a 16/20-native-frame recovery window allows the finisher. Existing\nnative hit payloads remain; contact timing follows 301's source-frame8 strike.\n\nNEXT TEST ABILITIES\nAbility       Ground            Air\n aqua 1       371 365 366       218 332 393\n aqua 2       352 353 407       351 304 303\n aqua 3       300 301 302       616 407 351\n aqua 4       510 511 512       504 514 399\nAqua3 air and Aqua4 were not specified for replacement and retain v17 mappings.\nThe main entry and four tests use the same ability IDs117..121 and0AP.\nSelect one while idle. Existing native ability entries are never evicted.\n\nAERIAL DODGE504\nRelease Circle after takeoff, then press Circle once while airborne. Land to\nrearm. Direction is read from the held left stick on every native control\nupdate, so turning the stick steers throughout the animation. Releasing Circle\ndoes not shorten the dodge. Neutral stick stops horizontal motion while the\nslight lift continues. Stick pressure scales horizontal speed, with a deadzone\nand normalized diagonals. This replaces v17's high Dual D ballistic arc.\n\nTuning: full-stick speed14 units/native clock unit, upward speed0.75, duration39\nclock units over the existing40-frame fall record. An unobstructed complete\npath requests546 horizontal units and29.25 units of lift. These are requested\nmovements before native collision, not a guaranteed in-game distance. Ceilings\nclip upward travel; landing, damage, scripted actions and other interruptions\nreturn to native handling. The mod never writes actor position directly and\nadds no invulnerability, hitbox or defense. Fall506 resumes after504.\n\nGUARD400 FORWARD AND REVERSE\nThe full source animation plays forward once during native frames0..10,\nholds its last pose during10..36, then plays once in reverse during36..52.\nForward speed is3.9x and reverse speed2.4375x the source's30fps timing: both\nexceed the requested minimum1.25x. This fits the existing54-frame native record\nand aligns the reverse with native recovery. No hold-to-guard mechanic is added.\nOriginal Guard events and defensive timing remain. Native cancels, attacks,\ndamage and scene changes can interrupt recovery. Guard must be equipped normally.\nThe common Guard record is shared by all Aqua profiles.\n\nIDLE FRONT HAIR\nIdle/combat-idle now retain native local bind rotations for the connected front\nhair root and chain151..154. Side/back hair155..193 remains at bind as before.\nThe idle skull direction, joint lengths, scales and native travel are retained.\nThe v17 run correction on skinned skull150 remains. A live visual check is\nstill needed; the offline checks verify connected joint transforms and skin\nbases rather than claim an in-game mesh rendering.\n\nDAMAGE / KNOCKBACK: KH2 SOURCE STILL NEEDED\nThe requested default KH2 Sora replacement is NOT included yet. The provided\nKH2 combat DLL loads Sora data from the installed game and contains no source\nmotions. P_EX100_BTLF is Valor and is not a default Sora substitute.\nAll Aqua damage/knockback replacements have been removed. This build currently\nuses original KH1 Sora reactions for requests48..51 (normal61..70/Olympus24..33).\nOther native reaction/parry records also remain original. This fallback is KH1,\nnot KH2. No recovery logic, damage calculation or defensive window is altered.\n\nTo finish KH2 reactions, supply extracted obj/P_EX100.mdlx and obj/P_EX100.mset.\nCOLLECT_KH2_SORA_SOURCE.cmd opens a folder selector, copies only those default\nSora BAR files, and writes a separate KH2_Sora_Source_*.zip. Choose extracted\nKH2 data or its obj folder; the helper does not extract large PKG containers.\nUpload the resulting ZIP. The helper never changes the selected source files.\n\nRETAINED\nOriginal KH1 Glide, native Blizzard events with main Fire visuals, keyblade-tip\nmagic, all numbered casting assignments and the remaining main Aqua actions.\nNo additional ability IDs are added. Native motion headers, counts, lengths,\n293-bone skeleton, eleven helper slots and allocations remain unchanged. The\ninstalled normal/Olympus MSETs are original; the ability gate applies body curves\nand scoped event time edits only at runtime.\n\nINSTALL / TEST\n1. Close KH1. Disable older Aqua and KH2 Combat/NineStyles/Dual Wield builds.\n2. Install this ZIP in OpenKH Mods Manager, then Build and Run.\n3. Equip main aqua while idle. Check idle hair,300/301/366, air305/407/351,\n   Guard entry/recovery, then a Circle dodge with forward/side/back stick input.\n4. During dodge, turn the stick and return it to neutral; lift should remain\n   small throughout504 and normal falling should resume afterward.\n5. Test aqua1..3 combos and verify Blizzard, standard Glide and damage reactions.\n6. Repeat in normal and Olympus environments. Share kh1-aqua.log plus a short\n   video for trajectory, hair or Guard adjustments. The log banner must sayv18.\n\nVALIDATION\nOffline tests execute the built PE DLL with a controlled Win64 host and sample\nserialized geometry, original event data and native executable anchors. This\nis not a Windows/KH1 playtest. See validation.json for exact current results.\nThe KH2 damage replacement remains explicitly pending source assets.\n"
SOURCE='AQUA v18 SOURCE\nRuntime: aqua.c plus aqua_data.h, aqua_air_dodge.h, aqua_blizzard.h,\naqua_cast_requests.h and aqua_magic.h. Immutable before/after payloads fit the\noriginal KH1 record capacities. Native Guard events and all damage reactions\npass through. Ground event changes are limited to existing time values.\n\nRebuild: Python3.12, GCC and GNU binutils; no Windows SDK required.\n  python3 generate_data.py\n  python3 build.py\n  python3 test_runtime.py\n  python3 test_visuals.py\nThese tests use a Linux Win64 ABI mock; they do not run KH1.\n\nRetarget source and supplied BBS/native KH1 fixtures are included under\nretargeting. To regenerate a profile (0main,1..4numbered,5dodge,7Blizzard):\n  python3 retargeting/tools/build_aqua_complete_v18.py --profile 0\nUse profiles0..5 or7. Selective --slots is supported.\nNo sampling cache is required; source clipping/timing fingerprints prevent\nreuse across different guards or combo timelines. Guard uses a forward/hold/\nreverse source timeline without changing any native headers or action clocks.\n\nThe desired KH2 Sora reaction mapping is recorded in damage_reaction_validation.\njson, but no KH2 source game assets are bundled or replacement claimed.\nCollect_KH2_Sora_Source.ps1 is a Windows PowerShell5.1 helper for loose extracted\nP_EX100.mdlx and P_EX100.mset. It never substitutes Valor or other characters.\n\nFor transparency, every runtime/visual/native validation marks game execution\nas false. In-game testing remains necessary for feel, collision and hair mesh.\n'

def build():
    runtime=load(D/'runtime_validation.json');geometry=load(D/'visual_validation.json')
    reports=[load(D/'curve_validation.json')]+[load(D/f'sets/p{i}/curve_validation.json') for i in range(1,5)]
    extra=[(name,load(D/name/'curve_validation.json')) for name in ['dodge','blizzard']]
    assert runtime['passed'] and geometry['passed'] and runtime['tests']==74 and geometry['tests']==24
    assert all(r['passed'] for r in reports+[r for _,r in extra]) and len(reports[0]['motions'])==37
    if DEST.exists():shutil.rmtree(DEST)
    shutil.copytree(ROOT/'KH1FM_Aqua_Animation_Test_v17',DEST,ignore=shutil.ignore_patterns('__pycache__','*.so','*.o','*.obj','sampling_cache','kh1-aqua.dll'))
    for p in DEST.glob('*v17*'):p.unlink()
    if (DEST/'source/glide_stop').exists():shutil.rmtree(DEST/'source/glide_stop')
    for name in ['fixtures','sets','dodge','blizzard']:
        target=DEST/'source'/name
        if target.exists():shutil.rmtree(target)
        shutil.copytree(D/name,target,ignore=shutil.ignore_patterns('__pycache__'))
    names=['aqua.c','aqua_magic.h','aqua_cast_requests.h','aqua_air_dodge.h','aqua_blizzard.h','aqua_data.h','build.py','generate_data.py','test_runtime.py','test_bridge.c','test_visuals.py']
    names+=sorted(p.name for p in D.glob('*validation.json'))
    names+=['source_selections.json','Collect_KH2_Sora_Source.ps1']
    for name in names:shutil.copy2(D/name,DEST/'source'/name)
    shutil.copy2(D/'kh1-aqua.dll',DEST/'dll/kh1-aqua.dll')
    tools=DEST/'source/retargeting/tools'
    for name in ['aqua_v16_plan.py','aqua_v17_plan.py','aqua_v18_plan.py','aqua_event_timing_v17.py','aqua_refine_v17.py','aqua_event_timing_v18.py','aqua_refine_v18.py','build_aqua_complete_v18.py','package_aqua_v18.py','validate_aqua_v18.py']:
        shutil.copy2(ROOT/'tools'/name,tools/name)
    for name in sorted(set(BANK.values())):shutil.copy2(D/'source_arcs'/name,DEST/'source/retargeting/core_source'/name)
    shutil.copy2(D/'Collect_KH2_Sora_Source.ps1',DEST/'Collect_KH2_Sora_Source.ps1')
    (DEST/'COLLECT_KH2_SORA_SOURCE.cmd').write_bytes(b'@echo off\r\nsetlocal\r\npowershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File \"%~dp0Collect_KH2_Sora_Source.ps1\" %*\r\npause\r\n')
    (DEST/'README_FIRST.txt').write_text(README);(DEST/'source/README_SOURCE.txt').write_text(SOURCE)
    mod=(DEST/'mod.yml').read_text();a=mod.index('description:');b=mod.index('assets:')
    mod=mod[:a]+'''description: >-
  Aqua v18: ground300/301/366, next tests1-3, front hair bind repair, steerable504 dodge with slight sustained lift and forward/reverse400 Guard. Default Glide and original KH1 Sora reactions; KH2 reaction source pending. Five0-AP abilities; original MSETs. Steam Global/Panacea.
'''+mod[b:]
    (DEST/'mod.yml').write_text(mod.replace('Test v17','Test v18'))
    checker=(ROOT/'KH1FM_Aqua_Animation_Test_v17/Check_Aqua_Animations_v17.ps1').read_text().replace('v17','v18').replace('V17','V18')
    (DEST/'Check_Aqua_Animations_v18.ps1').write_text(checker)
    (DEST/'CHECK_AQUA_V17.cmd').unlink(missing_ok=True)
    (DEST/'Check_Aqua_Animations_v17.ps1').unlink(missing_ok=True)
    (DEST/'CHECK_AQUA_V18.cmd').write_bytes(b'@echo off\r\nsetlocal\r\npowershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check_Aqua_Animations_v18.ps1" %*\r\npause\r\n')
    for name,remove,air in [('REMOVE_AQUA',1,0),('DISABLE_AIR_DODGE',0,0)]:
        (DEST/f'{name}_kh1-aqua.ini').write_text(f'[aqua]\nremove_aqua={remove}\nhand_magic=0\nair_dodge={air}\n')
    labels=['aqua']+[f'aqua {i}' for i in range(1,5)]
    (DEST/'ABILITY_SETS.txt').write_text('\n'.join([f'{label} / id{117+i} /0AP / ground '+('300 301 366 / air305 407 351' if i==0 else ' '.join(SETS[i-1][0])+' / air'+' '.join(SETS[i-1][1])) for i,label in enumerate(labels)])+'\n\nv18: select one while idle. See README_FIRST.txt for current changes and test order.\n')
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
            'Neutral stick':'stop horizontal; continue slight lift','Tilted stick':'resampled stick direction and pressure throughout504','Total requested lift':29.25,'Full stick horizontal speed':14,'Full requested travel':546,'Circle release cuts lift':False,
            'Native frames':40,'Fall clip':'506','Collision':'native displacement callback before collision','Extra defense or damage':False})
        glides.append({'Ability':label,'Visual':'original Sora native Glide','Normal slots':'75,76,77,78','Olympus slots':'37,38,39,40','Aqua overrides':0,'Clock and queued frame changes':0,'Opening flight ending':'native','Normal fall after native exit':'506'})
        for slot in [5,6,7]:runs.append({'Ability':label,'Normal slot':slot,'Aqua clip':active[slot]['donor'],'Corrected SKIN joint':150,'Authored head source bone':5,'Hair helper151 local':'native bind','Torso and neck retained':True,'Bind lengths and scale retained':True})
    for name,rows in [('ANIMATION_MAP.csv',maps),('SPELL_MAPPING.csv',spells),('AIR_DODGE_MAPPING.csv',airmaps),('GLIDE_MAPPING.csv',glides),('RUN_POSE.csv',runs)]:csv_file(name,rows)
    guard=[];reactions=[]
    native=load(D/'fixtures/native_reactions.json')
    for label in labels:
        guard.append({'Ability':label,'Aqua clip':'400','Native normal slot':110,'Olympus slot':72,
            'Forward native frames':'0..10','Hold native frames':'10..36','Reverse native frames':'36..52',
            'Forward source speed':3.9,'Reverse source speed':2.4375,'Native events and defense original':True})
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
    expected={'version':18,'assets':[]}
    for name,local in [('dll/kh1-aqua.dll','dll/kh1-aqua.dll'),('xa_ex_0010.mset','assets/xa_ex_0010.mset'),('xa_ex_0010_he.mset','assets/xa_ex_0010_he.mset')]:
        p=DEST/local;expected['assets'].append({'name':name,'sha256':sha(p),'bytes':p.stat().st_size})
    write_json(DEST/'expected_assets.json',expected)
    distinct={};assignments=0
    folders=[(D,reports[0])]+[(D/f'sets/p{i}',reports[i]) for i in range(1,5)]+[(D/name,r) for name,r in extra]
    for folder,rpt in folders:
        assignments+=len(rpt['motions'])
        for r in rpt['motions']:distinct.setdefault((r['normal_slot'],sha(folder/f"fixtures/aqua_{r['fixture_stem']}.bin")),r)
    values=list(distinct.values())
    validation={'version':18,'test_round':'next test; abilities1..3 updated','offline_checks_passed':True,'game_runtime_tested':False,
        'abilities':labels,'ability_ids':list(range(117,122)),'main_ground_combo':['300','301','366'],'main_air_combo':['305','407','351'],
        'main_blizzard_ground_air':['391','316'],'blizzard_native_lookup_and_events_restored':True,'blizzard_added_queue_entries':0,
        'ground_contact_frames':[12,6.4,8.8],'second_source_finish_and_chain_open_frames':[32,44],'second_chain_window_widths':[16,20],
        'glide':'original native default; no Aqua overrides','air_dodge':'504 live stick speed14 with sustained lift0.75, duration39 native units','run_head_skin_joint':150,'run_head_direction':'authored source head5; hair helper151 at bind',
        'keyblade_tip_magic':True,'numbered_cast_poses_retained':True,'numbered_combos_1_3_updated':True,'aqua3_air_and_aqua4_retained':True,'test_sets':SETS,'native_motion_headers_counts_and_sizes_preserved':True,
        'normal_motion_records':37,'olympus_motion_records':36,'helper_slots':11,'original_installed_msets':True,'kh2_damage_replacement_completed':False,'damage_reactions_current':'native KH1 Sora; KH2 source pending','idle_front_hair_joints_at_bind':[151,152,153,154],'guard_source':'400 forward/hold/reverse',
        'serialized_profile_and_transient_assignments':assignments,'distinct_fitted_records':len(values),
        'runtime_pe_tests':runtime['tests'],'geometry_tests':geometry['tests'],
        'pose_samples':sum(r['validated_pose_samples'] for r in values),'max_pose_position_fit_error':max(r['max_pose_position_error'] for r in values),
        'max_pose_basis_fit_error':max(r['max_pose_basis_error'] for r in values),
        'max_native_travel_error':max(r['root_helper_error'] for r in values),
        'max_scale_error':max(r['max_scale_error'] for r in values),'dll_sha256':sha(DEST/'dll/kh1-aqua.dll'),
        'limitations':['No Windows/KH1 or rendered-mesh test performed','Default KH2 Sora reaction source missing; original KH1 Sora reactions used pending capture','Spell release, collision, contact feel, Glide transitions and run appearance require in-game testing']}
    write_json(DEST/'validation.json',validation)
    assert len(maps)==185 and len(spells)==70 and len(source_rows)==assignments and assignments==92
    for suffix in ['', '_he']:assert (DEST/f'assets/xa_ex_0010{suffix}.mset').read_bytes()==(ROOT/f'sora_source/Custom Movesets KH1/xa_ex_0010{suffix}.mset').read_bytes()
    with zipfile.ZipFile(DEST.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.so','.o','.obj']:z.write(p,p.relative_to(DEST))
    with zipfile.ZipFile(DEST.with_suffix('.zip')) as z:assert z.testzip() is None
    print(json.dumps({'zip':str(DEST.with_suffix('.zip')),'bytes':DEST.with_suffix('.zip').stat().st_size,'sha256':sha(DEST.with_suffix('.zip')),'validation':validation},indent=2))
if __name__=='__main__':build()
