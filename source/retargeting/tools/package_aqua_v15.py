"""Package Aqua v15: native Glide middle/tip magic, guarded504 and late combo timing."""
from pathlib import Path
import csv,hashlib,json,shutil,struct,sys,zipfile
from aqua_v15_plan import SETS,BANK,GLIDE_SLOTS
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'KH1FM_Aqua_Animation_Test_v15'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

README='''KH1FM AQUA ANIMATION TEST v15
Steam Global / OpenKH Panacea

MAIN AQUA
Ground combo:300 ->365 ->366.
Air combo:351 ->352 ->393 (second air hit changed to352).
Blizzard/Blizzara/Blizzaga now use Fire's current animation:391 ground,316 air,
including Fire's recovery phase. The spell remains Blizzard: native MP,
element, projectiles, target and spell logic are retained.
Fire391/316, Cure427/318 and Stop/Aero317/390 retain v14's assignments.

MAGIC ORIGIN / EFFECTS
All Aqua profiles use native keyblade-tip spell origins and effect matrices.
No palm-redirection hooks are installed. Older hand_magic INI settings are
ignored in this build. Item007/395, falling506 and other spell logic remain.

GLIDE
Keep Aqua350 opening source0..20 during the first40 native frames. At frame40,
restore all four ORIGINAL Sora Glide motion bodies and resume their original
clock, steering and looping. Native release into fall6 retains Aqua350's
closing source20..40, then returns to506. Glide's normal ability, held-input,
state, movement, descent and collision requirements remain; it is not granted.

AERIAL DODGE504
The v14 log shows504 being accepted, followed immediately by native Glide71.
Native movement can enter Glide later using cached selection flags after the
input callback returns, beyond the scope of its temporary pad mask.
V15 adds a checked hook at the native regular-Glide constructor. While504 owns
the fall pose, that deferred Glide entry is suppressed for the verified Sora
actor. After504 ends, native Glide passes through normally. Both the control
and Glide entries verify before either is patched; failed admission retains
native controls. Tests exercise the deferred call after control returns.

Jump, release Circle, then press it again airborne. Neutral and directional
stick input are allowed. One504 per airtime; land to rearm. The native fall
queue restarts the40-frame animation and returns to506. No extra height,
invulnerability or BBS dash travel is added. Post-fix KH1 testing is still needed.

GROUND COMBO2 TIMING - MAIN AQUA ONLY
Both native variants keep source365 and their original lengths/counts.
C9/normal99 (Olympus61),48 native frames: first contact8 ->35; follow-up47.
CA/normal100 (Olympus62),64 native frames: first contact24 ->47; follow-up63.
All frame numbers are zero based at60fps. The follow-up window opens at the
final animation frame. Existing contact, trail/sound and state-event timestamps
are delayed together; the original event payloads, counts, descriptor pointers,
hitboxes and damage values remain. Native commands that use this same cancel
window also become available later. Check the hit/chain feel in-game.

NUMBERED TEST4 COMBO / SPELL POSES RETAINED
aqua 1 : ground316 317 318 ; air391 390 427
aqua 2 : ground315 371 366 ; air365 218 332
aqua 3 : ground393 411 352 ; air616 407 351
aqua 4 : ground510 511 512 ; air504 514 399
The352 air second, Fire-style Blizzard and365 event retiming apply to main aqua.
The native-tip magic, original Glide middle and504 guard apply to all five.
Numbered spell poses retain their previous assignments. Select one while idle;
zero-AP ids117..121 and saved selections remain. Native abilities are not evicted.

INSTALL
1. Fully close KH1.
2. Disable Aqua v14 and all older Aqua packages, Sora Restore Check and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH, enable Aqua Animation Test v15, Build and Run.
4. Load your save and equip aqua while idle.

TEST
- Check main ground300/365/366: late second contact, full second animation,
  then the next attack. Test locked/unlocked attacks to cover both variants.
- Check air351/352/393 and ground/air Blizzaga with Fire's animation.
- Check native weapon-tip spell effects, including Fire, Cure and Stop/Aero.
- Jump, release Circle, press again for504; land between attempts.
- Test Glide's Aqua opening, Sora middle while steering, then Aqua closing.
- Check both saves, room transitions/reloads and restoration with Aqua off.
For clean basic-combo testing, unequip Slapshot, Vortex, Hurricane Blast and
other native combo replacements; their separate actions keep their own timing.

IF DODGE STILL FAILS / INSTALL CHECK
Return the new kh1-aqua.log from beside KINGDOM HEARTS FINAL MIX.exe after one
test. The first line must identify v15. Look for AIR DODGE READY, accepted504,
then deferred native Glide constructor suppressed. Capture the log before
restarting, since each launch replaces it. CHECK_AQUA_V15.cmd checks installed
hashes and writes Aqua_Animation_Check_v15.txt. Drag your OpenKH folder onto it
if its default path does not match.

CAPACITY / RESTORATION
Both installed MSET files are original. All runtime motion headers, lengths,
table allocations, bone/helper counts, eleven helpers and native travel stay
original. The main second-ground edits change existing event time values only;
live encoded event descriptor pointers are retained. Unknown data blocks writes.
Body and request-table switching/restoration waits for idle. BBS command scripts,
MP logic or new invulnerability/hitboxes are not imported. Guard/Cartwheel motion
records retain native defensive windows. Spell timing uses the existing target
records, including Gravity's86/78 frames for main Stop/Aero.

FILES
ANIMATION_MAP.csv: usual motions for all five profiles.
SPELL_MAPPING.csv: every spell, ground/air, including current Blizzard routing.
COMBO_TIMING.csv: main second-ground contact and follow-up frames.
AIR_DODGE_MAPPING.csv / GLIDE_MAPPING.csv: movement phases and input rule.
TEST_CLIP_SOURCES.csv: exact source banks, cuts, frames, FPS and hashes.
source: current code, fixtures, tests, evidence reports and rebuild inputs.
inventory: existing349-clip inventory; current assignments are the root CSVs.
Numeric animation IDs are source identifiers, not official command names.

OPTIONAL DISABLE / REMOVE
To disable only airborne504, copy DISABLE_AIR_DODGE_kh1-aqua.ini beside the EXE
as kh1-aqua.ini and restart. Native Circle/Glide and the Glide pose phases remain.
To remove all five entries, use REMOVE_AQUA_kh1-aqua.ini as kh1-aqua.ini, leave
v15 enabled, restart and load each save to clean. Check AQUA ABILITIES REMOVED,
then save in-game. Exit, remove the INI, disable v15 and rebuild. Only117..121
are removed. Remove a temporary INI and restart to use default movement settings.

VALIDATION
65 actual-PE Win64-ABI runtime tests and18 geometry/assignment checks passed.
They cover deferred Glide after control, original constructor/trampoline calls,
native-tip casting, original Sora mid-flight bodies, Blizzard recovery queues,
main-only timing/restoration and unknown-data rejection across both banks.
Timing tests also execute the supplied executable's actual native event sampler.
All105 serialized pose assignments (86 distinct fitted records) keep the existing
capacity bounds. These checks do not run Windows/KH1 or render Sora's mesh.
The dodge fix, transition appearance and new contact/chain feel need in-game testing.
'''

SOURCE='''AQUA V15 DEVELOPMENT SOURCE

BUILD / CHECK (Linux x64)
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
Requires Python/GCC/GNU ld i386pep; geometry needs NumPy/SciPy.
Runtime checks execute the actual emitted PE and Win64 ABI entry detours with
native-control mocks. The native event sampler fixture is real supplied EXE code.

REBUILD POSES (optional; NumPy/SciPy/Pillow)
From this source directory, run retargeting/tools/build_aqua_complete_v15.py
with --profile0 --output .; profiles1..4 use outputs sets/p1..p4,profile5 uses
dodge and profile6 uses glide_stop. Arguments have spaces: --profile 0.
Then regenerate data, build and run both checks. --slots limits rebuilt records.
Model/source inputs are under retargeting; original MSETs are ../assets.
The exported builder resolves its paths relative to this source layout.

NEW SECOND-AIR / SPELL POSES
Main103 uses352 from p02ex_352.arc. The v15 plan inherits v14's other sources.
Main Blizzard requests37/84 now use Fire release records54/79, retaining native
request flags. cast_followup detects a verified main Blizzard queue, calls the
checked native append0x29FA30 to add recovery3D/8A, then places it before the
unchanged original terminal record. The logical spell stays37/84; original
terminal payloads, spell scripts, MP, targeting and element are retained.
Numbered profile body overrides and request tables retain their previous casts.

EVENT RETIMING WITHOUT NATIVE ALLOCATION/PATH CHANGES
Main99/100 keep their exact existing48/64-frame headers and source365 poses.
aqua_event_timing_v15.py changes only the first float of existing16-byte event
records. It warps the earliest kind4 state0x16 contact from8->35 or24->47 and
keeps all other timed state/trail/sound records aligned. Kind5 opens at47/63
and closes at48/64. All descriptor words/counts/pointers and payload bytes stay.
The actual native sampler0x394770 reads these fixtures in the runtime tests.
Native kind5 sets model+14 bit0x400000 at0x3922AF, copied to actor+1CC by0x29F515;
0x29EFB0 reads that bit for native cancellation/chain decisions.

AquaMotion.part_count is5 normally and6 for the two second-ground records.
The sixth AquaPart uses header field60 as an event-descriptor indirection.
The generated schema verifies descriptor type/count, terminator and every live
key pointer against the known contiguous layout. Only the key stream is copied;
live encoded descriptor pointers are never overwritten. Original and main
retimed streams are known immutable variants; numbered profiles use original
event times. This changes DLL admission metadata, not native MSET counts.
Unknown event schema/payload blocks the whole body transaction. All motion
headers, sizes, eleven helpers and existing travel remain original.

DEFERRED GLIDE GUARD FOR504
V14's accepted504 was immediately replaced by Glide71 in kh1-aqua(4).log.
0x2AFD79 reads cached global0x2D5EC10 bit0x80;0x2AFD82 calls native regular Glide
at0x2B26C0 independently of the temporary input mask. V15 hooks that constructor
only for an admitted live Sora504 session. Otherwise its original code resumes.
The14-byte span40534883ec20488bd9e862060000 contains the nine-byte prologue and
a relative call. The trampoline copies9bytes, calls original0x2B2D30 via absolute
RAX, then jumps to0x2B26CE without destroying the returned EAX. The native subtype
AND at+1D is checked too. The existing control0x2A6220 span and both constructor
anchors are admitted before either patch; protection failure leaves both intact.
Tests exercise a deferred native constructor after the input callback returns,
and the relocated successful original constructor including its subtype clear.
No Superglide constructor is hooked. Native state/velocity/defense are retained.

GLIDE / MAGIC
Glide starts with the existing350 source0..20 opening, reaching frame40. Then
all four original Sora Glide body parts are restored and the native clock and
steering resume. The fast cache recognizes that known temporary original-body
state. Native Glide ending restores the opening fixtures for next use and plays
the existing350[20,40] fall overlay before506. The frame/header counts stay native.
Magic attachment detours are removed. Native point/matrix attachment0x30 is used
for every spell/profile; legacy hand_magic INI values are ignored.

OTHER RETAINED SYSTEMS
Zero-AP ids117..121, exclusive selection, saved states, native ability-list size,
original request pointer restoration, item007/395, falling506, wrist/hair
refinements and all unrelated motion data remain. Guard/Cartwheel records keep
native defensive windows. The main second-ground cancel window is later, so
other commands using it are also delayed. Only idle transactions change profiles.

Evidence and scope are in the validation JSON files; all current action/source
assignments are the root CSVs. The supplied full EXE and user log are not included.
Existing upstream licenses remain in licenses. Format reference:
https://openkh.dev/bbs/file/type/pam.html
'''

def write_csv(name,rows):
    with (DEST/name).open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def build():
    d=ROOT/'ability_v15';runtime=json.loads((d/'runtime_validation.json').read_text());geometry=json.loads((d/'visual_validation.json').read_text())
    reports=[json.loads((d/'curve_validation.json').read_text())]+[json.loads((d/f'sets/p{i}/curve_validation.json').read_text()) for i in range(1,5)]
    dodge=json.loads((d/'dodge/curve_validation.json').read_text());stop=json.loads((d/'glide_stop/curve_validation.json').read_text())
    assert runtime['passed'] and geometry['passed'] and all(x['passed'] for x in reports+[dodge,stop])
    assert runtime['tests']==65 and geometry['tests']==18 and len(reports[0]['motions'])==51
    shutil.copytree(ROOT/'KH1FM_Aqua_Animation_Test_v14',DEST,dirs_exist_ok=True)
    for name in ['CHECK_AQUA_V14.cmd','Check_Aqua_Animations_v14.ps1','DISABLE_HAND_MAGIC_kh1-aqua.ini']:(DEST/name).unlink(missing_ok=True)
    for name in ['aqua.c','aqua_magic.h','aqua_cast_requests.h','aqua_air_dodge.h','aqua_data.h','build.py','generate_data.py','test_runtime.py','test_bridge.c','test_visuals.py',
                 'curve_validation.json','data_validation.json','runtime_validation.json','visual_validation.json','cast_request_validation.json','air_dodge_validation.json','glide_validation.json','source_selections.json','native_attachment_validation.json','combo_timing_validation.json']:
        shutil.copy2(d/name,DEST/'source'/name)
    for name in ['fixtures','sets','dodge','glide_stop']:shutil.copytree(d/name,DEST/'source'/name,dirs_exist_ok=True)
    shutil.copy2(d/'kh1-aqua.dll',DEST/'dll/kh1-aqua.dll')
    tools=DEST/'source/retargeting/tools'
    for name in ['build_aqua_complete_v15.py','aqua_v15_plan.py','package_aqua_v15.py','aqua_event_timing_v15.py']:shutil.copy2(ROOT/'tools'/name,tools/name)
    for name in sorted(set(BANK.values())):shutil.copy2(d/'source_arcs'/name,DEST/'source/retargeting/core_source'/name)
    # Export path resolution, matching previous bundles, without changing the fitted payloads.
    script=tools/'build_aqua_complete_v15.py';s=script.read_text()
    s=s.replace("ROOT=Path(__file__).resolve().parents[1]","ROOT=Path(__file__).resolve().parents[1]\nEXPORTED=ROOT.parent.name=='source'\nWORK=ROOT.parent if EXPORTED else ROOT/'ability_v15'")
    s=s.replace("ROOT/'ability_v15/sampling_cache'","WORK/'sampling_cache'").replace("ROOT/'ability_v15/source_arcs'","WORK/'source_arcs'")
    s=s.replace("if not arc.exists():arc=ROOT/'core_source'/plan['source_bank']","if not arc.exists():arc=ROOT/'core_source'/plan['source_bank']")
    s=s.replace("output=ROOT/'ability_v15' if not args.profile else ROOT/('ability_v15/glide_stop' if args.profile==6 else f'ability_v15/sets/p{args.profile}')",
                "output=WORK if not args.profile else WORK/('glide_stop' if args.profile==6 else f'sets/p{args.profile}')")
    script.write_text(s)
    (DEST/'README_FIRST.txt').write_text(README);(DEST/'source/README_SOURCE.txt').write_text(SOURCE)
    manifest=(ROOT/'KH1FM_Aqua_Animation_Test_v14/mod.yml').read_text();a=manifest.index('description:');b=manifest.index('assets:')
    desc='Main air second352; Blizzard uses Fire release/recovery; native keyblade-tip magic; original Sora Glide middle with Aqua350 opening/end. Adds deferred Glide guard for504 and retimes365 ground-second contact/chain to the end. Numbered combo/spell poses retained. Steam Global/Panacea.'
    manifest=manifest[:a]+'description: >-\n  '+desc+'\n'+manifest[b:]
    (DEST/'mod.yml').write_text(manifest.replace('Animation Test v14','Animation Test v15'))
    checker=(ROOT/'KH1FM_Aqua_Animation_Test_v14/Check_Aqua_Animations_v14.ps1').read_text().replace('v14','v15').replace('CHECK_AQUA_V14','CHECK_AQUA_V15')
    (DEST/'Check_Aqua_Animations_v15.ps1').write_text(checker)
    (DEST/'CHECK_AQUA_V15.cmd').write_bytes(b'@echo off\r\nsetlocal\r\npowershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check_Aqua_Animations_v15.ps1" %*\r\npause\r\n')
    for name,remove,magic,air in [('REMOVE_AQUA',1,0,0),('DISABLE_AIR_DODGE',0,0,0)]:
        (DEST/f'{name}_kh1-aqua.ini').write_text(f'[aqua]\nremove_aqua={remove}\nhand_magic={magic}\nair_dodge={air}\n')
    labels=['aqua']+[f'aqua {i}' for i in range(1,5)]
    (DEST/'ABILITY_SETS.txt').write_text('\n'.join([f'Ability {label} / id{117+i} / 0 AP'+
        (' / ground300 365 366 / air351 352 393' if not i else f' / ground {" ".join(SETS[i-1][0])} / air {" ".join(SETS[i-1][1])}') for i,label in enumerate(labels)])+
        '\n\nRevised Test4 / v15. Select one while idle. Main changes: air second352, Fire-style Blizzard and late ground-second timing. Common: guarded dodge504, Aqua350 opening/end with native Sora Glide middle, keyblade-tip magic.\n')
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
            ('native flight','original Sora','original native clock','75,76,77,78','37,38,39,40','After frame40 restore all original Sora Glide body parts; native steering and looping'),
            ('stop','20..40','0..39','10','10','Native Glide ends into fall request6; interrupt on landing/busy action')]:
            glidemaps.append({'Ability':labels[profile],'Ability id':117+profile,'Phase':phase,'Aqua clip':'native Sora' if phase=='native flight' else '350','Source frames':source,
                'Native frame timing':native,'Normal slots':nslots,'Olympus slots':hslots,'Trigger':trigger,'Restored falling clip':'506'})
    for profile,label in enumerate(labels):
        for aerial in [False,True]:
            poses=['316','317','317','318','317','318','318'] if not aerial else ['391','390','390','427','390','427','427']
            if profile==0:
                poses[0]=poses[1]='391' if not aerial else '316'
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
                    'Native frames':row['native_frames'],'Fire recovery normal slot':(82 if aerial else 57) if spell=='Fire' or (profile==0 and spell=='Blizzard') else ''})
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
    timing=json.loads((d/'combo_timing_validation.json').read_text())
    write_csv('COMBO_TIMING.csv',[{'Ability':'aqua','Normal slot':slot,'Olympus slot':61 if slot==99 else 62,'Aqua clip':'365',
        'Old first contact frame':timing['variants'][str(slot)]['contact_before'],
        'New first contact frame':timing['variants'][str(slot)]['contact_after'],
        'Next hit enabled frame':timing['variants'][str(slot)]['chain_opens'],
        'Window closes frame':timing['variants'][str(slot)]['chain_closes'],'Native FPS':60} for slot in [99,100]])
    expected={'version':15,'assets':[]}
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
    validation={'version':15,'test_round':4,'test_round_label':'revised Test4','offline_checks_passed':True,'game_runtime_tested':False,
        'abilities':labels,'ability_ids':list(range(117,122)),'main_ground_combo':['300','365','366'],'main_air_combo':['351','352','393'],'main_fire_ground_air':['391','316'],'main_cure_ground_air':['427','318'],'main_stop_aero_ground_air':['317','390'],'numbered_combo_and_spell_poses_preserved_from_v14':True,'main_blizzard_ground_air':['391','316'],'keyblade_tip_magic':True,'deferred_native_glide_guard':True,
        'item_use':'395','item_source_aliases':'007 / 395','glide':'350','glide_opening_source_range':[0,20],'glide_held_source_frame':None,'glide_middle':'original Sora bodies and clock','glide_closing_source_range':[20,40],
        'air_dodge':'504','normal_falling':'506','test_4_combos':SETS,'normal_motion_records_per_profile':51,'olympus_motion_records_per_profile':50,
        'unique_generated_pose_variants':len(records),'serialized_profile_transient_assignments':assignments,'actual_pe_mock_tests':runtime['tests'],'geometry_assignment_tests':geometry['tests'],
        'pose_samples':sum(r['validated_pose_samples'] for r in records),'max_pose_position_fit_error':max(r['max_pose_position_error'] for r in records),
        'max_non_root_attachment_translation_error':max(r['max_non_root_attachment_translation_error'] for r in records),
        'max_scale_error':max(r['max_scale_error'] for r in records),'native_travel_error':max(r['root_helper_error'] for r in records),
        'original_motion_lengths_headers_counts_and_msets_preserved':True,'helper_slots':11,'native_magic_attachment':'0x30','palm_attachment_hooks':0,'ground_second_contact_frames':[35,47],'ground_second_chain_frames':[47,63],
        'air_dodge_always_native_queued_restart':True,'air_dodge_one_per_airtime':True,'air_dodge_directional_input_allowed':True,
        'air_dodge_input_diagnostics':True,'glide_native_unlock_required':True,'glide_direction_changes_keep_pose_progress':True,'dll_sha256':sha(DEST/'dll/kh1-aqua.dll'),
        'limitations':['Windows/KH1 execution and rendered appearance pending','Deferred native Glide takeover reproduced after control and guarded offline; post-fix KH1 verification pending',
            'Aqua opening/end handoffs to native Sora middle need in-game visual testing','504 retains native fall gravity and40-frame timing with no extra invulnerability',
            'Main ground-second cancel/follow-up timing now waits for the final frame; check feel in-game']}
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
