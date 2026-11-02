"""Ship verified v16 sources, mappings and a standalone Panacea test ZIP."""
from pathlib import Path
import csv,hashlib,json,shutil,struct,zipfile
from aqua_v16_plan import SETS,BANK
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'KH1FM_Aqua_Animation_Test_v16'
D=ROOT/'ability_v16'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write_json(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
def csv_file(name,rows):
    with (DEST/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

README='''KH1FM AQUA ANIMATION TEST v16
Steam Global / OpenKH Panacea

CHANGES FOR THIS TEST
Blizzard: restored its ORIGINAL native request records and spell-event tracks.
Main Aqua borrows full Fire visuals391 ground /316 air in Blizzard's own slots.
The added recovery queue and Fire lookup remap from v15 are removed. Native
Blizzard scripts, projectile release, MP, element, target and effects remain.
This applies to Blizzard, Blizzara and Blizzaga. Test on the ground and in air.

Main ground combo remains300 ->365 ->366; air remains351 ->352 ->393.
The first ground hit's contact is earlier (12 instead of18 native frames).
Both second-hit variants reach the END of365 before a usable follow-up window:
- normal99 / Olympus61: swing finishes32; chain window32..48; contact24.
- normal100 / Olympus62: swing finishes44; chain window44..64; contact36.
The second motion holds its final pose during that recovery window. This
replaces v15's single-frame chain window. Existing damage/event payloads and
sound/effect keys stay original. All numbers above use the native motion clock.
The main first-hit follow-up window remains22..40. Numbered tests keep their
original native event timing. Test locked and unlocked attacks for both variants.

Glide: Aqua350 opens with source frames0..20, holds source frame20 during
flight, then closes with20..40 before falling506. Turning does not replay the
opening. The Sora middle-body handoff has been removed. KH1 still controls
Glide's movement, collision, steering, normal unlock and held-button release.

Aerial dodge: uses a Master-style movement controller with the assigned Aqua504
visual. Neutral stick gives vertical lift; a tilted stick adds directional
travel. Release Circle after takeoff, then press it again while airborne.
One dodge per airtime; landing rearms it. Holding Circle allows the fuller arc;
releasing early shortens the upward part. Native Glide entry is suppressed only
while504 is active. Afterward KH1 resumes fall506 at the actual collided height.
The controller supplies displacement BEFORE native collision. It never writes
actor position directly. Walls, ceilings, landing and interruptions stay native.
This is a KH1 adaptation of Master's movement structure, not an exact KH2 port.
Current test tuning: held rise96 native units, horizontal speed6 units per
native frame, up speed12, gravity0.75, release up-speed cap4, max fall speed20.
No extra invulnerability, guard window or damage is added. Superglide remains.

Run: the head is lifted12 degrees in ordinary and combat running. Torso motion,
body proportions and bind hair rotations are retained. Check the angle in-game.

NUMBERED TEST4 SETS
Main aqua / id117: ground300 365 366; air351 352 393.
aqua 1 / id118: ground316 317 318; air391 390 427.
aqua 2 / id119: ground315 371 366; air365 218 332.
aqua 3 / id120: ground393 411 352; air616 407 351.
aqua 4 / id121: ground510 511 512; air504 514 399.
Only main aqua gets the Blizzard visual selector and ground event edits.
Common movement/run changes and keyblade-tip magic apply to all five abilities.
Main Fire391/316, Cure427/318, Stop/Aero317/390 and item007/395 are retained.
Numbered cast poses are unchanged. Select one Aqua ability while standing idle;
all five cost0 AP, use the existing saved IDs, and are mutually exclusive.

INSTALL
1. Fully close KH1.
2. Disable Aqua v15 and every older Aqua package, Sora Restore Check and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH, enable Aqua Animation Test v16, Build and Run.
4. Load a save and equip main aqua while standing idle.

TEST ORDER
1. Grounded Blizzard, Blizzara/Blizzaga if available, then aerial Blizzard.
2. Ground basic combo300 ->365 ->366, locked and unlocked. Confirm the first
   hit feels earlier and a follow-up during the second hit's recovery chains.
3. Jump, release Circle, press again: neutral lift, then directional lift on
   another jump. Hold/release to compare height; land between attempts.
4. Glide straight, turn both ways, hold a longer flight, then release. Check
   Aqua's beginning, held pose and ending.
5. Run facing sideways to inspect head pitch; check both saves and room reloads.
6. Unequip aqua, stand idle, and check Sora restoration. Check numbered sets too.
For clean basic-combo tests, unequip Slapshot, Vortex, Hurricane Blast and other
native attack replacements. Those separate native actions keep their own timing.

LOG / INSTALL CHECK
Return the new kh1-aqua.log after testing, with a short recording if appearance
or collision still fails. Capture it before restarting; each launch replaces it.
The first line should say v16. Aerial dodge should log AIR DODGE READY, accepted
504, queued restart committed and DODGE MOVEMENT ACTIVE. If the last marker is
missing, the animation ran without reaching the movement callback.
CHECK_AQUA_V16.cmd checks installed asset hashes and writes
Aqua_Animation_Check_v16.txt. Drag the OpenKH folder onto it if needed.

VALIDATION / LIMITS
72 actual-PE runtime checks and21 geometry/assignment checks passed offline.
The tests cover both motion banks, original Blizzard queue/event bytes, all
profiles, input/deferred Glide handling, movement direction and held/released
arcs, native fall handoff, unknown-data rejection, restoration and run/head fit.
The chain checks execute the supplied executable's actual native event sampler.
All motion headers, frame counts, allocations, eleven helpers and native travel
tracks retain their original capacity. Installed Sora/Olympus MSETs are original.
Neither Windows/KH1 nor Sora's rendered mesh was executed here. In-game spell
release, collision behavior, movement feel and appearance still need checking.

FILES
ANIMATION_MAP.csv: usual motion/source assignments for all five abilities.
SPELL_MAPPING.csv: all spells on the ground/in air, including transient Blizzard.
COMBO_TIMING.csv: main first/second contacts, source finish and chain windows.
AIR_DODGE_MAPPING.csv / GLIDE_MAPPING.csv: inputs, movement and visual phases.
TEST_CLIP_SOURCES.csv: exact source banks, frames, rates, cuts and hashes.
RUN_POSE.csv: running head correction. source: rebuild code, fixtures and checks.
inventory: prior349-clip inventory. Numeric IDs are source identifiers; official
BBS command names remain unverified where the inventory says so.

OPTIONAL DISABLE / REMOVE
Copy DISABLE_AIR_DODGE_kh1-aqua.ini beside the EXE as kh1-aqua.ini and restart
to disable only504 input/movement. Native Circle/Glide input remains available;
Aqua's Glide poses still apply. Remove the temporary INI and restart to reenable.
To remove all five abilities, use REMOVE_AQUA_kh1-aqua.ini as kh1-aqua.ini,
leave v16 enabled, restart and load each save to clean. Check ABILITIES REMOVED,
save in-game, exit, remove the INI, disable v16 and rebuild. Only IDs117..121 are
removed. Native ability entries are never evicted. Profile/body restoration
waits for idle; the native ability-list allocation remains unchanged.
'''
SOURCE='''AQUA V16 SOURCE / REPRODUCIBILITY

The supplied original EXE is Steam Global timestamp1721645006, SHA256
 d790746245d26159f3ee0e1060e33b2fa2de06941850a4ac724f598722884bac.
Its full bytes and the user's log are not redistributed. Native anchors and
Master-reference provenance are recorded in native_movement_validation.json.

Build DLL on Linux with Python3, GCC and GNU ld PE support:
 python3 generate_data.py
 python3 build.py
 python3 test_runtime.py
 python3 test_visuals.py
NumPy/SciPy are required for pose fitting/geometry; Python3/GCC for runtime mocks.
The runtime checks map the actual emitted PE with Win64 ABI/import mocks.
They are not Windows/KH1 execution or a rendered-mesh test.

Optional source pose rebuild from this directory:
 python3 retargeting/tools/build_aqua_complete_v16.py --profile 0 --output .
 python3 retargeting/tools/build_aqua_complete_v16.py --profile 1 --output sets/p1
Profiles2..4 use sets/p2..p4;5 uses dodge;6 uses glide_stop;7 uses blizzard.
The builder finds model/PAM/ARC inputs below retargeting and original MSETs in
../assets. --slots limits rebuilt native records. The sampling cache is rebuilt
from immutable baseline data; refinements are applied once. Regenerate data,
rebuild the DLL and run checks after modifying any serialized fixture.

Blizzard selector: aqua_blizzard.h recognizes current/newly queued logical37/84
including native request flags, verifies the admitted55/80 motion parts, then
copies only full391/316 body curves into those original records. Their native
spell events and request lookup remain. Restore the shared317/390 body before
the next spell, interruption, ability-off or idle profile switch. No recovery
append, terminal reordering, MP call or projectile hook exists in v16.

Main timing: aqua_event_timing_v16 changes existing hit/chain frame floats for
98/99/100 only. It preserves every descriptor, key payload, sound and effect key.
Second365 reaches its last source frame at native32/44, then holds. Kind5 opens
32/44 through48/64, giving16/20 native frames to chain after the full swing.
The sixth runtime AquaPart admits the known event-key stream through header60,
checking all encoded descriptor/key handles. All native allocation sizes/counts
remain original. Other profiles use original event times, and off restores them.

Aerial dodge: aqua_air_dodge.h verifies and installs control0x2A6220, regular
Glide constructor0x2B26C0 and native state2 displacement0x2AF6A0 hooks. It admits
all anchors and obtains all code-page protections before patching any entry.
The control trampoline relocates the RIP cookie load; the Glide trampoline
relocates its common constructor call. The16-byte movement span is entirely
position independent and preserves its TEST flags before resuming native code.
Outside admitted504, all three original functions pass through.

On a fresh free-air Circle, native state setter0x2B1960 selects fall callbacks,
then native queue0x29F980 restarts fall10 with504 body. The native input command
predicate remains the checked low-byte/bit24 test. A held takeoff cannot retrigger;
landing rearms once per airtime. Deferred cached Glide selection is blocked only
for that live session. Native controller commands and busy actions interrupt it.

Movement borrows the supplied Master begin_aerial_dodge structure: neutral up,
normalized stick travel, held arc, finite action, native fall handoff. Exact KH2
growth values are absent from the supplied extract. The separately documented
96/6/.75 values are KH1 test tuning, without the v52 style's2x distance multiplier.
The callback returns requested displacement before KH1's collision pass. It never
writes actor+10 position. Native wall/ceiling/floor/collision callbacks remain.
A release caps upward speed; the native ceiling bit clips lift. At normal handoff,
arc values are reset to the actual actor Y, and fall506 resumes. No defense or
hitbox import is added. This is not a full source-identical Master port.

Glide retains Aqua350 throughout start/held middle/closing. Native current and
queued visual clocks cap40 after the opening, including direction changes. No
native Sora body is republished during flight. Native Glide physics/unlocks are
untouched. 350 stop uses the fall overlay, then506 returns on end/interruption.

Run refinement: aqua_refine_v16 lifts head151 by12 degrees only on slots5/6/7
relative to the character's root-right axis. It preserves torso and local bind
hair, joint translations, scale, helper travel and all unrelated motions.
Previous run fixtures are frozen solely for independent geometry comparison.

IDs117..121, exclusivity, idle transactions, original request pointers, keyblade
tip attachment0x30, wrist and limb refinements and native defensive windows stay.
Current mappings are the root CSVs; source event timing is in validation JSON.
Previous plan/refiner modules are retained as explicit build dependencies.
Existing upstream license files remain in licenses.
'''

def build():
    runtime=load(D/'runtime_validation.json');geometry=load(D/'visual_validation.json')
    reports=[load(D/'curve_validation.json')]+[load(D/f'sets/p{i}/curve_validation.json') for i in range(1,5)]
    extra=[(name,load(D/name/'curve_validation.json')) for name in ['dodge','glide_stop','blizzard']]
    assert runtime['passed'] and geometry['passed'] and runtime['tests']==72 and geometry['tests']==21
    assert all(r['passed'] for r in reports+[r for _,r in extra]) and len(reports[0]['motions'])==51
    if DEST.exists():shutil.rmtree(DEST)
    shutil.copytree(ROOT/'KH1FM_Aqua_Animation_Test_v15',DEST,ignore=shutil.ignore_patterns('__pycache__','*.so','*.o','*.obj'))
    for p in DEST.glob('*v15*'):p.unlink()
    for name in ['fixtures','sets','dodge','glide_stop','blizzard']:
        target=DEST/'source'/name
        if target.exists():shutil.rmtree(target)
        shutil.copytree(D/name,target,ignore=shutil.ignore_patterns('__pycache__'))
    names=['aqua.c','aqua_magic.h','aqua_cast_requests.h','aqua_air_dodge.h','aqua_blizzard.h','aqua_data.h','build.py','generate_data.py','test_runtime.py','test_bridge.c','test_visuals.py']
    names+=sorted(p.name for p in D.glob('*validation.json'))
    names+=['source_selections.json']
    for name in names:shutil.copy2(D/name,DEST/'source'/name)
    shutil.copy2(D/'kh1-aqua.dll',DEST/'dll/kh1-aqua.dll')
    tools=DEST/'source/retargeting/tools'
    for name in ['aqua_v15_plan.py','aqua_v16_plan.py','aqua_event_timing_v16.py','aqua_refine_v16.py','build_aqua_complete_v16.py','package_aqua_v16.py','validate_aqua_v16.py']:
        shutil.copy2(ROOT/'tools'/name,tools/name)
    for name in sorted(set(BANK.values())):shutil.copy2(D/'source_arcs'/name,DEST/'source/retargeting/core_source'/name)
    script=tools/'build_aqua_complete_v16.py';s=script.read_text()
    s=s.replace("ROOT=Path(__file__).resolve().parents[1]","ROOT=Path(__file__).resolve().parents[1]\nEXPORTED=ROOT.parent.name=='source'\nWORK=ROOT.parent if EXPORTED else ROOT/'ability_v16'")
    s=s.replace("ROOT/'ability_v16/sampling_cache'","WORK/'sampling_cache'").replace("ROOT/'ability_v16/source_arcs'","WORK/'source_arcs'")
    old="output=ROOT/'ability_v16' if not args.profile else ROOT/('ability_v16/blizzard' if args.profile==7 else 'ability_v16/glide_stop' if args.profile==6 else f'ability_v16/sets/p{args.profile}')"
    new="output=WORK if not args.profile else WORK/({5:'dodge',6:'glide_stop',7:'blizzard'}.get(args.profile,f'sets/p{args.profile}'))"
    assert old in s;s=s.replace(old,new);script.write_text(s)
    (DEST/'README_FIRST.txt').write_text(README);(DEST/'source/README_SOURCE.txt').write_text(SOURCE)
    mod=(DEST/'mod.yml').read_text();a=mod.index('description:');b=mod.index('assets:')
    mod=mod[:a]+'''description: >-
  Aqua v16: native Blizzard events with Fire visuals, earlier first ground hit and completed second swing with usable recovery, Aqua350 held Glide, Master-style504 lift/directional movement and lifted running head. Five0-AP abilities; original MSETs. Steam Global/Panacea.
'''+mod[b:]
    (DEST/'mod.yml').write_text(mod.replace('Test v15','Test v16'))
    checker=(ROOT/'KH1FM_Aqua_Animation_Test_v15/Check_Aqua_Animations_v15.ps1').read_text().replace('v15','v16').replace('V15','V16')
    (DEST/'Check_Aqua_Animations_v16.ps1').write_text(checker)
    (DEST/'CHECK_AQUA_V15.cmd').unlink(missing_ok=True)
    (DEST/'CHECK_AQUA_V16.cmd').write_bytes(b'@echo off\r\nsetlocal\r\npowershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check_Aqua_Animations_v16.ps1" %*\r\npause\r\n')
    for name,remove,air in [('REMOVE_AQUA',1,0),('DISABLE_AIR_DODGE',0,0)]:
        (DEST/f'{name}_kh1-aqua.ini').write_text(f'[aqua]\nremove_aqua={remove}\nhand_magic=0\nair_dodge={air}\n')
    labels=['aqua']+[f'aqua {i}' for i in range(1,5)]
    (DEST/'ABILITY_SETS.txt').write_text('\n'.join([f'{label} / id{117+i} /0AP / ground '+('300 365 366 / air351 352 393' if i==0 else ' '.join(SETS[i-1][0])+' / air'+' '.join(SETS[i-1][1])) for i,label in enumerate(labels)])+'\n\nv16: select one while idle. See README_FIRST.txt for current changes and test order.\n')
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
                'Run head lift degrees':r.get('run_head_lift_degrees',0),'Root policy':r['root']})
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
            'Neutral stick':'vertical lift','Tilted stick':'vertical lift plus normalized stick direction','Held rise test units':96,'Horizontal test speed':6,
            'Native frames':40,'Fall clip':'506','Collision':'native displacement callback before collision','Extra defense or damage':False})
        for phase,frames,timing,slots,he_slots in [('opening','0..20','0..40','75,76,77,78','37,38,39,40'),('held middle','20','clock held40 while native Glide runs','75,76,77,78','37,38,39,40'),('closing','20..40','0..39','10','10')]:
            glides.append({'Ability':label,'Phase':phase,'Aqua clip':'350','Source frames':frames,'Native timing':timing,'Normal slots':slots,'Olympus slots':he_slots,'Fall clip':'506'})
        for slot in [5,6,7]:runs.append({'Ability':label,'Normal slot':slot,'Aqua clip':active[slot]['donor'],'Head lift degrees':12,'Corrected joint':151,'Torso retained':True,'Bind hair retained':True})
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
                    found.append({'Ability':labels[profile] if profile<5 else ['all Aqua entries: dodge','all Aqua entries: Glide closing','main Aqua: Blizzard'][profile-5],
                        'Action':r['action'],'Normal slot':r['normal_slot'],'Source name':animation.name,'Source aliases':r.get('source_aliases',''),
                        'Source bank':r['source_bank'],'PAM member':member,'Source frames':animation.frame_count,'Source FPS':animation.fps,
                        'Source frame range':str(r['source_range']) if r['source_range'] else 'full','Animation SHA256':digest,'Native frames':r['native_frames'],'Source timing':r.get('source_timing','linear')})
            assert len(found)==1,(r['donor'],r['source_bank'],len(found));source_rows+=found
    csv_file('TEST_CLIP_SOURCES.csv',source_rows)
    expected={'version':16,'assets':[]}
    for name,local in [('dll/kh1-aqua.dll','dll/kh1-aqua.dll'),('xa_ex_0010.mset','assets/xa_ex_0010.mset'),('xa_ex_0010_he.mset','assets/xa_ex_0010_he.mset')]:
        p=DEST/local;expected['assets'].append({'name':name,'sha256':sha(p),'bytes':p.stat().st_size})
    write_json(DEST/'expected_assets.json',expected)
    distinct={};assignments=0
    folders=[(D,reports[0])]+[(D/f'sets/p{i}',reports[i]) for i in range(1,5)]+[(D/name,r) for name,r in extra]
    for folder,rpt in folders:
        assignments+=len(rpt['motions'])
        for r in rpt['motions']:distinct.setdefault((r['normal_slot'],sha(folder/f"fixtures/aqua_{r['fixture_stem']}.bin")),r)
    values=list(distinct.values())
    validation={'version':16,'test_round':'revised Test4','offline_checks_passed':True,'game_runtime_tested':False,
        'abilities':labels,'ability_ids':list(range(117,122)),'main_ground_combo':['300','365','366'],'main_air_combo':['351','352','393'],
        'main_blizzard_ground_air':['391','316'],'blizzard_native_lookup_and_events_restored':True,'blizzard_added_queue_entries':0,
        'ground_contact_frames':[12,24,36],'second_source_finish_and_chain_open_frames':[32,44],'second_chain_window_widths':[16,20],
        'glide':'350 opening0..20 / held20 / closing20..40','air_dodge':'504 Master-style KH1 movement adaptation','run_head_lift_degrees':12,
        'keyblade_tip_magic':True,'numbered_combo_and_cast_poses_retained':True,'test_sets':SETS,'native_motion_headers_counts_and_sizes_preserved':True,
        'normal_motion_records':51,'olympus_motion_records':50,'helper_slots':11,'original_installed_msets':True,
        'serialized_profile_and_transient_assignments':assignments,'distinct_fitted_records':len(values),
        'runtime_pe_tests':runtime['tests'],'geometry_tests':geometry['tests'],
        'pose_samples':sum(r['validated_pose_samples'] for r in values),'max_pose_position_fit_error':max(r['max_pose_position_error'] for r in values),
        'max_pose_basis_fit_error':max(r['max_pose_basis_error'] for r in values),
        'max_native_travel_error':max(r['root_helper_error'] for r in values),
        'max_scale_error':max(r['max_scale_error'] for r in values),'dll_sha256':sha(DEST/'dll/kh1-aqua.dll'),
        'limitations':['No Windows/KH1 or rendered-mesh test performed','Master-style movement uses documented KH1 test tuning; exact KH2 growth parameters not imported','Spell release, collision, contact feel, Glide transitions and run appearance require in-game testing']}
    write_json(DEST/'validation.json',validation)
    assert len(maps)==255 and len(spells)==70 and len(source_rows)==assignments and assignments==107
    assert len(values)==88,(len(values),assignments)
    for suffix in ['', '_he']:assert (DEST/f'assets/xa_ex_0010{suffix}.mset').read_bytes()==(ROOT/f'sora_source/Custom Movesets KH1/xa_ex_0010{suffix}.mset').read_bytes()
    with zipfile.ZipFile(DEST.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.so','.o','.obj']:z.write(p,p.relative_to(DEST))
    with zipfile.ZipFile(DEST.with_suffix('.zip')) as z:assert z.testzip() is None
    print(json.dumps({'zip':str(DEST.with_suffix('.zip')),'bytes':DEST.with_suffix('.zip').stat().st_size,'sha256':sha(DEST.with_suffix('.zip')),'validation':validation},indent=2))
if __name__=='__main__':build()
