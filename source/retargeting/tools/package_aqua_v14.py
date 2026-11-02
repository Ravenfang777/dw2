"""Package Aqua v14: main-only casting/second hits and the logged dodge fix."""
from pathlib import Path
import csv,hashlib,json,shutil,struct,sys,zipfile
from aqua_v14_plan import SETS,BANK,GLIDE_SLOTS
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'KH1FM_Aqua_Animation_Test_v14'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

README='''KH1FM AQUA ANIMATION TEST v14
Steam Global / OpenKH Panacea

MAIN AQUA CHANGES
Fire: ground391; air316
Cure: ground427; air318
Stop / Aero: ground317; air390 (current Gravity animations)
Ground combo:300,365,366
Air combo:351,371,393
Both native second-ground variants use365. Each combo is first, second, finisher.
Fire retains its split release/recovery structure using the swapped source clip.
Stop/Aero share Gravity's existing86-ground/78-air-frame casting records;
previously they shared Cure's68/68-frame records. Native spell behavior remains.

AERIAL DODGE504 REPAIR
Your v13 log recorded five airborne presses rejected only by mask0x100:
state2, request0xA, one allowed air motion queued, held/pressed6, input record
0x03000000. V13 misread bit24 as a busy command. The supplied executable skips
command dispatch when that bit is set; when it is clear, a nonzero low command
byte dispatches a native command. V14 follows that native branch condition.
The logged input now plays504 in the actual-DLL mock host for all five profiles
and both banks. Actual post-fix KH1 verification is still needed.

Release Circle after takeoff, then press it again airborne. Neutral and
directional stick input are supported. It is once per airtime; landing rearms.
The checked native queue always restarts the fall animation, including from
an existing fall. Pending native commits, timeouts and interruptions are handled.
It remains an animation test: no added invulnerability, height or BBS dash travel.

TEST4 NUMBERED PROFILES - ANIMATIONS RETAINED FROM v13
aqua   : ground300 365 366 ; air351 371 393 (new main profile)
aqua 1 : ground316 317 318 ; air391 390 427
aqua 2 : ground315 371 366 ; air365 218 332
aqua 3 : ground393 411 352 ; air616 407 351
aqua 4 : ground510 511 512 ; air504 514 399

The Fire/Cure swaps and Stop/Aero routing edits apply only to main aqua.
Numbered entries keep v13 Fire316/391, Cure318/427 and Stop/Aero318/427.
Thunder, Blizzard and Gravity use317/390 in every profile. LEFT-hand spell
origins/glow, item007/395, falling506, Guard, Cartwheel, reactions and movement
remain. All five entries share the corrected504 input handling.
Ability ids117..121 and0AP remain. Select one while idle; other Aqua entries
turn off. Saved selections are respected. Native abilities are never evicted.

INSTALL
1. Fully close KH1.
2. Disable Aqua v13 and all older Aqua packages, Sora Restore Check and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH and enable Aqua Animation Test v14.
4. Build and Run, then load your save and equip aqua while idle.

TEST
- With main aqua, test Fire and Cure on the ground and in the air.
- Check grounded Stop/Aero against grounded Gravity, then aerial Stop/Aero
  against aerial Gravity. They should use matching animation families.
- Test ground300/365/366 and air351/371/393. Unequip native combo replacements
  such as Slapshot, Vortex and Hurricane Blast for clean basic-combo testing.
- Jump, release Circle, then press again to test504; land between attempts.
- Check LEFT-hand effects, item use, Glide350, transitions/reloads and both saves.
- Numbered profiles retain their v13 animations. Turning Aqua off at idle
  restores the original bodies and original actor request-table pointer.

IF DODGE STILL FAILS
Return the new kh1-aqua.log from beside KINGDOM HEARTS FINAL MIX.exe after one
test. Its first line must identify v14. AIR DODGE READY and CONTROL OBSERVED
confirm hook admission and arrival. AIR INPUT records the accepted/rejected
press, current/first queued request, held/pressed input and command flags.
The file is replaced on each game launch; capture it before restarting.
CHECK_AQUA_V14.cmd checks installed asset hashes and writes
Aqua_Animation_Check_v14.txt. Drag your OpenKH folder onto it if needed.

RETAINED GLIDE350
The first40 native Glide frames play source0..20, then hold source frame20.
Steering carries that progress into the next native Glide pose. Native release
into fall6 plays closing source20..40 on the existing40-frame fall record,
then returns to506. Landing/busy actions/off interrupt the closing pose.
Normal Glide records75..78 match Olympus37..40. The original120/60/60/60-frame
record capacities remain. Native Glide/Superglide unlock, equipped ability,
held-input, state, velocity, descent and collision requirements remain.
The checked control hook provides phase handling; air_dodge=0 disables only
504, retaining native Circle/Glide input and the350 controller.

CAPACITY / BEHAVIOR
Both installed MSET files are original. All fitted records keep native headers,
lengths, counts, table allocation, eleven helpers and helper travel. Only known
normal Sora/Olympus motion data and request tables are admitted. No records,
helper slots, hitboxes or new BBS command logic are added. KH1 damage, spell
scripts, MP/targeting, native event tracks and defensive windows remain native.
Source changes alter poses; existing native record durations govern their speed.
Thunder retains its86/78-frame alternate casting duration. Main Stop/Aero now
use that same Gravity family timing. Final cast timing/FX needs an in-game check.

FILES
ABILITY_SETS.txt lists current sequences.
SPELL_MAPPING.csv lists all seven spells, ground/air, for all five profiles.
ANIMATION_MAP.csv lists51 usual records per profile (50 available in Olympus).
AIR_DODGE_MAPPING.csv and GLIDE_MAPPING.csv describe the transient actions.
TEST_CLIP_SOURCES.csv lists selected sources, ranges, frames, FPS and hashes.
source contains current code, fitted fixtures, test reports and rebuild inputs.
inventory retains the existing349-clip list; current assignments are the CSVs.
007/395 are aliases for the same item animation payload. Numeric source IDs
are not official command names.

OPTIONAL FALLBACKS / REMOVE
To disable Circle504, copy DISABLE_AIR_DODGE_kh1-aqua.ini beside the EXE as
kh1-aqua.ini and restart. To retain native weapon-tip casting attachments, use
DISABLE_HAND_MAGIC_kh1-aqua.ini. Combine air_dodge=0 and hand_magic=0 in a
single [aqua] INI if needed. Remove the INI and restart for defaults.
To remove all five Aqua entries, use REMOVE_AQUA_kh1-aqua.ini as kh1-aqua.ini,
leave v14 enabled, restart and load each save to clean. Check AQUA ABILITIES
REMOVED, then save in-game. Exit, remove the INI, disable v14 and rebuild.
Only ids117..121 are removed; native ability order stays intact.

VALIDATION
64 actual-PE Win64-ABI mock-host tests passed, including the logged Jump input,
native-command exclusion, delayed commits, all five profiles/both banks,
main-only spell lookup changes, idle switching/restoration and failure paths.
17 geometry/assignment checks passed across105 serialized profile/transient
assignments (86 distinct fitted records), including the new second hits,
main-only spell swaps, Fire continuity, native capacities/travel and hair/wrists.
All fits remain below the existing5-unit position-error limit. The checks do
not run Windows/KH1 or render Sora's mesh; post-fix gameplay needs confirmation.
'''

SOURCE='''AQUA V14 DEVELOPMENT SOURCE

BUILD / CHECK (Linux x64)
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
Requires Python, GCC and GNU ld with i386pep support. Geometry checks also
require NumPy/SciPy. The runtime host maps and executes the actual emitted PE
exports and checked detour/trampoline code; native game control/queue bodies
are mocked. It is not a Windows/KH1 run.

REBUILD FITTED POSES (optional; NumPy/SciPy/Pillow)
From this source directory:
  python3 retargeting/tools/build_aqua_complete_v14.py --profile 0 --output .
  python3 retargeting/tools/build_aqua_complete_v14.py --profile 1 --output sets/p1
  python3 retargeting/tools/build_aqua_complete_v14.py --profile 2 --output sets/p2
  python3 retargeting/tools/build_aqua_complete_v14.py --profile 3 --output sets/p3
  python3 retargeting/tools/build_aqua_complete_v14.py --profile 4 --output sets/p4
  python3 retargeting/tools/build_aqua_complete_v14.py --profile 5 --output dodge
  python3 retargeting/tools/build_aqua_complete_v14.py --profile 6 --output glide_stop
Then regenerate data, build and run the two checks above.
--slots followed by normal slot numbers rebuilds only those records.
The package builder resolves exported source paths separately from the working
project. Original MSET files are ../assets; the model is under
retargeting/sora_source. PAM/PMO/ARC inputs are under retargeting/core_source.
Baseline sampling caches can be regenerated and are not distributed.

MAIN-ONLY BODY VARIANTS
Main physical54/57 use391[0,31]/[31,48],79/82 use316[0,20]/[20,30],56 uses427,
and81 uses318. Main99/100 use365 and103 uses371. The v14 plan inherits the
remaining v13 actions and exact Test4 source choices. Each numbered profile
retains six extra v13 spell records as immutable overrides alongside its seven
combo records. Payloads are deduplicated in aqua_data.h. There are51 usual
normal records or50 Olympus records per profile; the original11 helpers,
header scalars, table lengths, allocations and native helper travel remain.
Existing wrist/hair/rotation-only limb refinements remain.

MAIN-ONLY REQUEST LOOKUP
Each bank has original, numbered and main request-table variants, all1408bytes.
Numbered profiles retain only Thunder38/85 rerouting. Main additionally maps
Stop/Aero3B/3C from normal56 to55 (Olympus19 to18), and88/89 from normal81 to80
(Olympus43 to42). Native flags and other request words are preserved. Original
tables are never written. cast_admit recognizes either owned copy only for
the tracked actor/bank, retaining its exact original pointer. All body/lookup
switches wait for idle and restore exactly. Foreign data blocks writes.
Stop/Aero now use Gravity's existing86/78 native-frame records, previously68/68.
No spell logic, MP, targeting or event-track data is replaced.

DODGE504: USER LOG AND NATIVE BRANCH EVIDENCE
kh1-aqua(3).log recorded24 decisions:18ground exclusions, five airborne
mask0x100 exclusions, and one airborne mask0x140 including a busy closing pose.
The five clean attempts had state2,request0xA,count1,held6,pressed6 and
command0x03000000. None accepted504. V13 rejected that exact replay too.
The native function0x2A6220 at0x2A629A tests byte[command+3]&1. A SET bit skips
command dispatch. Otherwise0x2A62F8 checks the low byte for nonzero and calls
0x2A7510 at0x2A6307. V13 had this exclusion backward. V14 rejects exactly:
  (command &0xFF)!=0 && (command &0x01000000)==0
The logged0x03000000 now permits504. Tests cover all profiles/banks, a native
Glide fallback when Jump is not consumed, and delayed native fall commits.
Busy actions, incompatible queued motions, menus/scripts, unsafe memory and
native can-act exclusions remain. Current code uses the same checked control
hook0x2A6220, can-act0x297870 and queue0x29F980. No new hooks are added.
The17-byte control span includes one RIP-relative cookie load, relocated via
0x554A88. Exact spans and the supplied executable hash are in the JSON evidence.
The game executable and uploaded user log are not distributed.

Air input rejection bits retain their v13 meaning except0x100 now denotes
an actual native command-dispatch candidate (the predicate above). Other bits:
0x001scope,0x002used,0x004not armed,0x008state,0x010height,0x020stick,0x040busy
motion/Glide,0x080shortcut,0x200queued motion,0x400native can-act,0x800admission.
504 temporarily supplies the known fall body; always queues native fall6 at0;
waits up to16 controller checks for commit; ends at39, loop, landing or interrupt.
The callback masks only logical Jump bits6 around original control and restores
only those bits, keeping unrelated native input changes. Native state, velocity,
gravity, collision and defense remain. No BBS travel or invulnerability is added.

RETAINED FEATURES
Glide350 uses source0..20 over the first40 native frames, holds source20 while
Glide continues and carries pose progress through native direction changes.
The controller validates the affected Glide body before pose-clock/queued-frame
writes. Native fall6 after Glide temporarily uses350[20,40], then506. Source
and native branch details are in glide_validation.json. The existing input
hook remains active with air_dodge=0 to support these phases.
LEFT-palm206 casting selector0x20CE, item007/395, movement, Guard/Cartwheel,
reactions, falling506, zero-AP ids117..121, exclusive selection and exact
idle-only body/lookup restoration are retained. The normal48-byte ability list
is not expanded and no native entry is evicted. Existing licenses remain.
Source choices and ranges are in aqua_v14_plan.py and the root CSV files.
The frozen V8 comparison covers unchanged source actions only; geometry checks
do not render the mesh or prove collision clearance in gameplay.

Existing upstream notices are retained in licenses.
Format reference: https://openkh.dev/bbs/file/type/pam.html
'''

def write_csv(name,rows):
    with (DEST/name).open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def build():
    d=ROOT/'ability_v14';runtime=json.loads((d/'runtime_validation.json').read_text());geometry=json.loads((d/'visual_validation.json').read_text())
    reports=[json.loads((d/'curve_validation.json').read_text())]+[json.loads((d/f'sets/p{i}/curve_validation.json').read_text()) for i in range(1,5)]
    dodge=json.loads((d/'dodge/curve_validation.json').read_text());stop=json.loads((d/'glide_stop/curve_validation.json').read_text())
    assert runtime['passed'] and geometry['passed'] and all(x['passed'] for x in reports+[dodge,stop])
    assert runtime['tests']==64 and geometry['tests']==17 and len(reports[0]['motions'])==51
    shutil.copytree(ROOT/'KH1FM_Aqua_Animation_Test_v13',DEST,dirs_exist_ok=True)
    for name in ['CHECK_AQUA_V13.cmd','Check_Aqua_Animations_v13.ps1']:(DEST/name).unlink(missing_ok=True)
    for name in ['aqua.c','aqua_magic.h','aqua_cast_requests.h','aqua_air_dodge.h','aqua_data.h','build.py','generate_data.py','test_runtime.py','test_bridge.c','test_visuals.py',
                 'curve_validation.json','data_validation.json','runtime_validation.json','visual_validation.json','cast_request_validation.json','air_dodge_validation.json','glide_validation.json','source_selections.json']:
        shutil.copy2(d/name,DEST/'source'/name)
    for name in ['fixtures','sets','dodge','glide_stop']:shutil.copytree(d/name,DEST/'source'/name,dirs_exist_ok=True)
    shutil.copy2(d/'kh1-aqua.dll',DEST/'dll/kh1-aqua.dll')
    tools=DEST/'source/retargeting/tools'
    for name in ['build_aqua_complete_v14.py','aqua_v14_plan.py','package_aqua_v14.py']:shutil.copy2(ROOT/'tools'/name,tools/name)
    for name in sorted(set(BANK.values())):shutil.copy2(d/'source_arcs'/name,DEST/'source/retargeting/core_source'/name)
    # Export path resolution, matching previous bundles, without changing the fitted payloads.
    script=tools/'build_aqua_complete_v14.py';s=script.read_text()
    s=s.replace("ROOT=Path(__file__).resolve().parents[1]","ROOT=Path(__file__).resolve().parents[1]\nEXPORTED=ROOT.parent.name=='source'\nWORK=ROOT.parent if EXPORTED else ROOT/'ability_v14'")
    s=s.replace("ROOT/'ability_v14/sampling_cache'","WORK/'sampling_cache'").replace("ROOT/'ability_v14/source_arcs'","WORK/'source_arcs'")
    s=s.replace("if not arc.exists():arc=ROOT/'core_source'/plan['source_bank']","if not arc.exists():arc=ROOT/'core_source'/plan['source_bank']")
    s=s.replace("output=ROOT/'ability_v14' if not args.profile else ROOT/('ability_v14/glide_stop' if args.profile==6 else f'ability_v14/sets/p{args.profile}')",
                "output=WORK if not args.profile else WORK/('glide_stop' if args.profile==6 else f'sets/p{args.profile}')")
    script.write_text(s)
    (DEST/'README_FIRST.txt').write_text(README);(DEST/'source/README_SOURCE.txt').write_text(SOURCE)
    manifest=(ROOT/'KH1FM_Aqua_Animation_Test_v13/mod.yml').read_text();a=manifest.index('description:');b=manifest.index('assets:')
    desc='Revised Test4: main ground300/365/366, air351/371/393; Fire391/316, Cure427/318, Stop/Aero317/390. Fixes logged Jump-flag dodge504 rejection. Numbered Test4 animations preserved; LEFT-hand magic, Glide350 and falling506 retained. Steam Global/Panacea; disable older Aqua and Nine Styles.'
    manifest=manifest[:a]+'description: >-\n  '+desc+'\n'+manifest[b:]
    (DEST/'mod.yml').write_text(manifest.replace('Animation Test v13','Animation Test v14'))
    checker=(ROOT/'KH1FM_Aqua_Animation_Test_v13/Check_Aqua_Animations_v13.ps1').read_text().replace('v13','v14').replace('CHECK_AQUA_V13','CHECK_AQUA_V14')
    (DEST/'Check_Aqua_Animations_v14.ps1').write_text(checker)
    (DEST/'CHECK_AQUA_V14.cmd').write_bytes(b'@echo off\r\nsetlocal\r\npowershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check_Aqua_Animations_v14.ps1" %*\r\npause\r\n')
    for name,remove,magic,air in [('REMOVE_AQUA',1,0,0),('DISABLE_HAND_MAGIC',0,0,1),('DISABLE_AIR_DODGE',0,1,0)]:
        (DEST/f'{name}_kh1-aqua.ini').write_text(f'[aqua]\nremove_aqua={remove}\nhand_magic={magic}\nair_dodge={air}\n')
    labels=['aqua']+[f'aqua {i}' for i in range(1,5)]
    (DEST/'ABILITY_SETS.txt').write_text('\n'.join([f'Ability {label} / id{117+i} / 0 AP'+
        (' / ground300 365 366 / air351 371 393' if not i else f' / ground {" ".join(SETS[i-1][0])} / air {" ".join(SETS[i-1][1])}') for i,label in enumerate(labels)])+
        '\n\nRevised Test4 / v14. Select one while idle. Main-only casting edits; numbered casts retained. Common: corrected dodge504, glide350, item007/395, fall506 and LEFT-hand magic.\n')
    maps=[];sources=[];airmaps=[];glidemaps=[];spellmaps=[]
    from bbs_source_inspector import read_arc,read_pam
    for profile in range(5):
        active={r['normal_slot']:r for r in reports[0]['motions']}
        if profile:active.update({r['normal_slot']:r for r in reports[profile]['motions']})
        for r in sorted(active.values(),key=lambda r:r['normal_slot']):
            maps.append({'Ability':labels[profile],'Ability id':117+profile,'Action':r['action'],'Native request':f'0x{r["request"]:02X}',
                'Normal slot':r['normal_slot'],'Olympus slot':r['olympus_slot'] if r['olympus_slot']!=0xffffffff else 'not present',
                'Aqua clip':r['donor'],'Source aliases':r.get('source_aliases',''),'Source bank':r['source_bank'],'Source frame range':str(r['source_range']) if r['source_range'] else 'full',
                'Pose loop':r['loop'],'Native frames':r['native_frames'],'Source timing':r.get('source_timing','linear'),
                'Native hold frame':r.get('native_hold_frame',''),'Root policy':r['root']})
        airmaps.append({'Ability':labels[profile],'Ability id':117+profile,'Action':'Aerial dodge','Aqua clip':'504',
            'Trigger':'Fresh airborne Jump/Circle after release; neutral or directional stick; once per airtime','Normal slot':10,'Olympus slot':10,
            'Native frames':40,'Always queued native restart':True,'Logged Jump flags0x03000000 allowed':True,'Native command dispatch candidate excluded':True,'Normal falling clip':'506','Input restored after control':True,'Native gravity and velocity':True})
        for phase,source,native,nslots,hslots,trigger in [
            ('start','0..20','0..40','75,76,77,78','37,38,39,40','Native Glide state21 requests71..74 or76..79'),
            ('held flight','20','40 held','75,76,77,78','37,38,39,40','Continue native Glide; preserve phase through steering'),
            ('stop','20..40','0..39','10','10','Native Glide ends into fall request6; interrupt on landing/busy action')]:
            glidemaps.append({'Ability':labels[profile],'Ability id':117+profile,'Phase':phase,'Aqua clip':'350','Source frames':source,
                'Native frame timing':native,'Normal slots':nslots,'Olympus slots':hslots,'Trigger':trigger,'Restored falling clip':'506'})
    for profile,label in enumerate(labels):
        for aerial in [False,True]:
            poses=['316','317','317','318','317','318','318'] if not aerial else ['391','390','390','427','390','427','427']
            if profile==0:
                poses[0]='391' if not aerial else '316'
                poses[3]='427' if not aerial else '318'
                poses[5]=poses[6]='317' if not aerial else '390'
            bank='normal';variant='main' if profile==0 else 'aqua'
            table=(d/f'fixtures/requests_{bank}_{variant}.bin').read_bytes()
            he=(d/f'fixtures/requests_he_{variant}.bin').read_bytes()
            for index,(spell,clip) in enumerate(zip(['Fire','Blizzard','Thunder','Cure','Gravity','Stop','Aero'],poses)):
                request=(0x83 if aerial else 0x36)+index
                target=struct.unpack_from('<I',table,request*4)[0]&0xfff
                row=next(r for r in reports[0]['motions'] if r['normal_slot']==target)
                spellmaps.append({'Ability':label,'Ability id':117+profile,'Spell':spell,'Mode':'air' if aerial else 'ground','Aqua clip':clip,
                    'Native request':f'0x{request:02X}','Normal slot':target,'Olympus slot':struct.unpack_from('<I',he,request*4)[0]&0xfff,
                    'Native frames':row['native_frames'],'Fire recovery normal slot':(82 if aerial else 57) if spell=='Fire' else ''})
    write_csv('SPELL_MAPPING.csv',spellmaps)
    for profile,report in enumerate(reports+[dodge,stop]):
        for r in report['motions']:
            if not profile and r['normal_slot'] not in [54,55,56,57,58,59,75,76,77,78,79,80,81,82,99,100,101,102,103,104]:continue
            arc=d/'source_arcs'/r['source_bank']
            if not arc.exists():arc=ROOT/'capture_20261101/Sources/data/bbs/arc/pc'/r['source_bank']
            members,_=read_arc(arc.read_bytes());found=[]
            for member,data in members:
                if not data.startswith(b'PAM\0'):continue
                for animation in read_pam(data,54):
                    if animation.name!=r['donor']:continue
                    start=struct.unpack_from('<I',data,16+16*animation.slot)[0];digest=hashlib.sha256(data[start:animation.data_end]).hexdigest()
                    if r.get('source_sha256'):assert digest==r['source_sha256']
                    found.append({'Ability':labels[profile] if profile<5 else 'all Aqua entries','Action':r['action'],'Normal slot':r['normal_slot'],
                        'Source name':animation.name,'Source aliases':r.get('source_aliases',''),'Source bank':r['source_bank'],'PAM member':member,
                        'Source frames':animation.frame_count,'Source FPS':animation.fps,'Source frame range':str(r['source_range']) if r['source_range'] else 'full',
                        'Animation SHA256':digest,'Native frames':r['native_frames'],'Native FPS':60,'Source timing':r.get('source_timing','linear')})
            assert len(found)==1,(r['donor'],r['source_bank'],len(found));sources+=found
    for name,rows in [('ANIMATION_MAP.csv',maps),('AIR_DODGE_MAPPING.csv',airmaps),('GLIDE_MAPPING.csv',glidemaps),('TEST_CLIP_SOURCES.csv',sources)]:write_csv(name,rows)
    expected={'version':14,'assets':[]}
    for name,p in [('dll/kh1-aqua.dll',DEST/'dll/kh1-aqua.dll'),('xa_ex_0010.mset',DEST/'assets/xa_ex_0010.mset'),('xa_ex_0010_he.mset',DEST/'assets/xa_ex_0010_he.mset')]:
        expected['assets'].append({'name':name,'sha256':sha(p),'bytes':p.stat().st_size})
    (DEST/'expected_assets.json').write_text(json.dumps(expected,indent=2)+'\n')
    assignments=sum(len(r['motions']) for r in reports+[dodge,stop])
    distinct={}
    for folder,report in [(d,reports[0])]+[(d/f'sets/p{i}',reports[i]) for i in range(1,5)]+[(d/'dodge',dodge),(d/'glide_stop',stop)]:
        for r in report['motions']:
            key=(r['normal_slot'],sha(folder/f"fixtures/aqua_{r['fixture_stem']}.bin"))
            distinct.setdefault(key,r)
    records=list(distinct.values())
    validation={'version':14,'test_round':4,'test_round_label':'revised Test4','offline_checks_passed':True,'game_runtime_tested':False,
        'abilities':labels,'ability_ids':list(range(117,122)),'main_ground_combo':['300','365','366'],'main_air_combo':['351','371','393'],'main_fire_ground_air':['391','316'],'main_cure_ground_air':['427','318'],'main_stop_aero_ground_air':['317','390'],'numbered_profile_animations_preserved_from_v13':True,
        'item_use':'395','item_source_aliases':'007 / 395','glide':'350','glide_opening_source_range':[0,20],'glide_held_source_frame':20,'glide_closing_source_range':[20,40],
        'air_dodge':'504','normal_falling':'506','test_4_combos':SETS,'normal_motion_records_per_profile':51,'olympus_motion_records_per_profile':50,
        'unique_generated_pose_variants':len(records),'serialized_profile_transient_assignments':assignments,'actual_pe_mock_tests':runtime['tests'],'geometry_assignment_tests':geometry['tests'],
        'pose_samples':sum(r['validated_pose_samples'] for r in records),'max_pose_position_fit_error':max(r['max_pose_position_error'] for r in records),
        'max_non_root_attachment_translation_error':max(r['max_non_root_attachment_translation_error'] for r in records),
        'max_scale_error':max(r['max_scale_error'] for r in records),'native_travel_error':max(r['root_helper_error'] for r in records),
        'original_motion_lengths_headers_counts_and_msets_preserved':True,'helper_slots':11,'left_palm_magic':206,
        'air_dodge_always_native_queued_restart':True,'air_dodge_one_per_airtime':True,'air_dodge_directional_input_allowed':True,
        'air_dodge_input_diagnostics':True,'glide_native_unlock_required':True,'glide_direction_changes_keep_pose_progress':True,'dll_sha256':sha(DEST/'dll/kh1-aqua.dll'),
        'limitations':['Windows/KH1 execution and rendered appearance pending','Logged Jump-flag rejection reproduced and corrected offline; post-fix KH1 verification pending',
            'Native Glide unlock/input/physics remain;350 phase transitions need in-game testing','504 retains native fall gravity and40-frame timing with no extra invulnerability',
            'Main Stop/Aero now share Gravity86/78 timing instead of Cure68/68; Thunder86/78 retained']}
    (DEST/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    assert len(maps)==255 and len(glidemaps)==15 and len(records)==86 and assignments==105
    for suffix in ['', '_he']:
        assert (DEST/f'assets/xa_ex_0010{suffix}.mset').read_bytes()==(ROOT/f'sora_source/Custom Movesets KH1/xa_ex_0010{suffix}.mset').read_bytes()
    with zipfile.ZipFile(DEST.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.so','.o','.obj']:z.write(p,p.relative_to(DEST))
    with zipfile.ZipFile(DEST.with_suffix('.zip')) as z:assert z.testzip() is None
    print(json.dumps({'zip':str(DEST.with_suffix('.zip')),'bytes':DEST.with_suffix('.zip').stat().st_size,'sha256':sha(DEST.with_suffix('.zip')),'validation':validation},indent=2))
if __name__=='__main__':build()
