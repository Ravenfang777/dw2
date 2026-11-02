"""Package Aqua v13: revised Test4, actual native Glide phases and dodge restart."""
from pathlib import Path
import csv,hashlib,json,shutil,struct,sys,zipfile
from aqua_v13_plan import SETS,BANK,GLIDE_SLOTS
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'KH1FM_Aqua_Animation_Test_v13'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

README='''KH1FM AQUA ANIMATION TEST v13 - REVISED TEST 4
Steam Global / OpenKH Panacea

MAIN AQUA
Ground combo: 300, 218, 366 (first, second, finisher).
Both native second-ground variants now use218.
Air combo: 351, 353, 393 (first, second, finisher).
Ground and aerial item use: 007 /395, using the shared395 payload.
Glide:350 opening frames0..20, held middle frame20 during flight, then
closing frames20..40 before returning to506 falling.

Aerial Dodge504 now always queues a native animation restart, including when
Sora is already falling. The old path only reset the fall clock. Uncommitted
command-menu selections no longer block the action; a committed native
command still takes priority. Fresh presses are accepted even if the held
input bit is already clear. Logs now identify rejected input and whether the
native control callback is being reached. These changes passed offline
checks; the cause of your in-game failure has not been confirmed from a log.

TEST 4 ABILITIES - ALL 0 AP
aqua   : ground300 218 366 ; air351 353 393
aqua 1 : ground316 317 318 ; air391 390 427
aqua 2 : ground315 371 366 ; air365 218 332
aqua 3 : ground393 411 352 ; air616 407 351
aqua 4 : ground510 511 512 ; air504 514 399

Each triplet means first attack, second attack, finisher. KH1's alternate
second ground attack uses the selected second clip too. Numbered entries
share the main movement, Glide, item use, falling, casting, reactions,
Guard, Cartwheel and airborne dodge; their combos are the differences.
Select one while idle; the other Aqua entries turn off. Existing ability
ids117..121, saved selections and all native ability entries are retained.

INSTALL
1. Fully close KH1.
2. Disable Aqua v12 and every older Aqua package, Sora Restore Check and
   Nine Styles / Dual Wield. Keep other Sora model/moveset replacements off.
3. Import this ZIP into OpenKH and enable Aqua Animation Test v13.
4. Build and Run, then load your save.
5. Equip aqua or aqua1..4 while idle. Missing entries are granted off;
   saved selections are respected. Native entries are never evicted to fit.

TEST ORDER
- Equip aqua and test ground300/218/366, then air351/353/393.
- Jump, release Circle, then tap Circle again for504. Test a neutral stick
  and a directional stick. It is once per airtime; land to rearm.
- Test ordinary Glide with its native unlock, equipped ability and input
  requirements. It retains native movement and release rules. Check350's
  opening, held middle pose, steering, then closing pose when Glide ends.
  A successful504 press consumes Circle during that action. After it ends,
  native Glide can resume; holding the takeoff button also retains native
  Glide behavior. This build does not grant Glide or Superglide.
- Use an item on the ground and in the air; check007/395.
- Equip aqua1..4 while idle; test each ground and air triplet. For clean
  combo testing, unequip Slapshot, Sliding Dash, Vortex, Hurricane Blast and
  other native combo replacements; they retain their separate native poses.
- Recheck Fire, Thunder and Cure with LEFT-hand effects, both saves, room
  transitions and reloads; finally turn all Aqua entries off and check Sora.

IF504 STILL DOES NOT PLAY
Return kh1-aqua.log from beside KINGDOM HEARTS FINAL MIX.exe after one test.
Its first line must identify v13. It records AIR DODGE READY, CONTROL OBSERVED,
accepted/rejected AIR INPUT data, and queued-restart completion. Each run
replaces the log, so capture it before restarting. CHECK_AQUA_V13.cmd verifies
installed asset hashes and writes Aqua_Animation_Check_v13.txt; include that
report if installation is in doubt.

MOVEMENT / ANIMATION SCOPE
504 remains an animation test using the existing40-frame fall record. It
adds no invulnerability, double-jump height or new BBS dash movement. Native
state, gravity, velocity, collision and interruption rules remain in control.
350 uses the real four native Glide records, including the shared Superglide
poses. The first40 native frames play source0..20; later flight holds source20.
Steering carries the current pose progress into the next native Glide motion.
Native Glide release returns to fall6; a temporary40-frame closing350 pose
then restores506. Landing, attacks, casts and unequipping interrupt it.
The source has41 frames at30fps. Native motion headers and capacities stay
original; the opening/held records retain120/60/60/60 native-frame capacities.
Phase control requires the checked control hook. If admission fails, the log
says AIR ACTIONS UNAVAILABLE and other Aqua animations remain available.

LAYOUT / CASTING
Both installed MSET files are original. All fitted records keep original
headers, lengths, table allocations, bone counts, eleven helpers and travel.
Unknown motion data or request tables block writes. Only the supplied normal
Sora and Olympus banks are admitted. Body switching waits for idle.
KH1's damage, event tracks, spell scripts, MP, targeting, Guard coverage and
Dodge Roll windows remain native. BBS command scripts/effects/damage are not
imported with these animations. Existing hair and wrist corrections remain.
Fire316/391, Thunder317/390, Cure318/427 and LEFT-hand spell origins/glow remain.
Thunder keeps the alternate86 ground/78 air casting durations from v10;
Blizzard/Gravity share317/390 and Stop/Aero share318/427. Cast timing and final
mesh/FX appearance still require an in-game check.

FILE GUIDE
ABILITY_SETS.txt: current Test4 sequences.
ANIMATION_MAP.csv: the51 usual records per profile (50 available in Olympus).
AIR_DODGE_MAPPING.csv: temporary504 and its input rule.
GLIDE_MAPPING.csv: source350 phases, native slots, timing and hold behavior.
TEST_CLIP_SOURCES.csv: current changed actions/test sets with source frames,
exact bank/PAM member, aliases and animation payload hashes.
source/source_selections.json: inventory choices for this build.
inventory: unchanged349-clip inventory; current mappings are the root CSVs.
007/395 are aliases for identical source animation data;395 is selected here.
Numeric IDs are source identifiers, not official command names.

OPTIONAL FALLBACKS
To disable only airborne Circle504, copy DISABLE_AIR_DODGE_kh1-aqua.ini beside
the EXE as kh1-aqua.ini and restart. Native Circle/Glide input and the350 phase
controller remain available. To retain weapon-tip spell attachments, use
DISABLE_HAND_MAGIC_kh1-aqua.ini instead. Combine air_dodge=0 and hand_magic=0
in one [aqua] INI if needed. Remove the INI and restart for defaults.

REMOVE ALL AQUA ENTRIES
Copy REMOVE_AQUA_kh1-aqua.ini beside the EXE as kh1-aqua.ini. Leave v13 enabled,
restart and load each save to clean. Check AQUA ABILITIES REMOVED, then save
in-game. Exit, remove the INI, disable v13 and rebuild. Only ids117..121 are
removed; native ability order stays intact.

VALIDATION
59 tests execute the emitted PE DLL in a Win64 ABI mock host, including delayed
native restart, input diagnostics, all five profiles, both banks, Glide steering,
closing/interruptions, lookup/body restoration and hook failure paths.
15 geometry/assignment tests cover81 generated pose variants, the exact new
mappings, item alias hash, Glide hold/closing boundary, native capacities,
travel, bind lengths/scales, wrists, hair and existing jump/Fire transitions.
All fits remain below the existing5-unit position-error limit with no capacity
expansion. These checks do not run Windows/KH1 or render Sora's mesh.
The new504 route,350 behavior, new clips and final appearance need in-game testing.
'''

SOURCE='''AQUA V13 REVISED TEST 4 SOURCE

Normal installation requires OpenKH/Panacea; these are development files.

DLL BUILD / EXECUTION CHECK (Linux x64)
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
GCC, GNU ld with i386pep support and Python are needed. Geometry checks need
NumPy/SciPy. Runtime tests execute the actual emitted PE exports and native
entry detours/trampolines against a Win64 ABI mock host, not Windows/KH1.

REBUILD POSES (optional; NumPy, SciPy, Pillow)
From this source directory:
  python3 retargeting/tools/build_aqua_complete_v13.py --profile 0 --output .
  python3 retargeting/tools/build_aqua_complete_v13.py --profile 1 --output sets/p1
  python3 retargeting/tools/build_aqua_complete_v13.py --profile 2 --output sets/p2
  python3 retargeting/tools/build_aqua_complete_v13.py --profile 3 --output sets/p3
  python3 retargeting/tools/build_aqua_complete_v13.py --profile 4 --output sets/p4
  python3 retargeting/tools/build_aqua_complete_v13.py --profile 5 --output dodge
  python3 retargeting/tools/build_aqua_complete_v13.py --profile 6 --output glide_stop
  python3 generate_data.py
  python3 build.py
  python3 test_runtime.py
  python3 test_visuals.py
--slots followed by normal slot numbers rebuilds only those records. Required
source ARC files are in retargeting/core_source. Original MSETs are ../assets.
The builder supports an already exported source tree. Its package root,
source_arcs and sora_source paths resolve against this directory via the
inherited retargeting layout described below. Baseline caches can be rebuilt;
they are not distributed. Anatomical refinements run once per immutable baseline.

EXPORTED RETARGETING LAYOUT
retargeting/tools contains the v13 builder and its plan/dependencies. The
exported builder defaults to the bundled assets when run from this directory;
its source directory is found relative to its script. See the paths used by
build_aqua_complete_v13.py. No original game EXE is included.

FIVE PROFILE GATE / CAPACITIES
All51 normal or50 Olympus records verify against the exact original or known
Aqua variants before initial body writes. Header sizes, frame counts, allocation,
body/helper counts, the eleven helpers, hierarchy and native helper travel remain
original. Five immutable profiles share unchanged blocks; four numbered sets
replace seven physical combo records each (C8,C9/CA,CB,CC,CD,CE).
Source hashes distinguish variants; cache identities include source hash,
source range, loop/root policy and the Glide time mapping.
The builder pins a knot at native frame40 for Glide's static held pose.

Ability ids117..121 are zero AP. Newly enabled Aqua entries win and only other
Aqua entries turn off. Missing entries are granted only if all fit with a list
terminator in the original48-byte list. Native entries are never evicted.
Switching/restoration waits for idle. Unknown data blocks writes. Reloaded banks
are re-admitted; original body/request pointers restore when Aqua is off.

AIRBORNE CIRCLE504
AquaPart.dodge stores the fitted non-looped504 variant of fall slot10. The
native control0x2A6220 entry is admitted against17 exact bytes. Its trampoline
copies10 bytes, relocates the RIP-relative cookie load using original0x554A88,
then jumps to original+17. Native can-act0x297870 and queue0x29F980 signatures
verify before installation; these functions are called, not detoured.

The v12 already-falling route wrote actor+16C=0 without a queued motion restart.
V13 always calls native queue(actor,6,0). Pending actions wait up to16 controller
checks while the native request remains queued, even when current request is
already6 and its old fall clock is late. No sentinel physical-slot writes or
native state/velocity changes are used. A queue timeout, foreign data, landing,
interruption or ability-off restores the known506 body without stale writes.
The broad command-low-byte exclusion is narrowed to native committed bit
0x01000000. Fresh Jump bits6 at pad+8 are accepted after release even when pad+4
is already clear. Any finite valid stick direction is accepted. One504 use
per airtime; landing rearms. Logical Jump bits at pad+4,+8,+10,+14 are masked only
around original control, then those bits are restored without undoing native
changes to other buttons. Native gravity, collision and defense remain.

The log records first arrival at the Sora native control callback and the first
24 input decisions. AIR INPUT rejection mask bits:
  0x001 scope/actor/bank/profile/event/menu/script exclusion
  0x002 used this airtime or504 already active
  0x004 button release has not armed the action
  0x008 native state is not1/2
  0x010 invalid height or height<=1
  0x020 invalid direction/tilt
  0x040 busy motion, Glide or Glide closing pose
  0x080 shortcut or conflicting held button
  0x100 committed native command
  0x200 incompatible queued motion
  0x400 native can-act rejected
  0x800 fall-body admission or writable queue fields rejected
Zero means accepted. The queued native restart completion is logged too.
No current in-game log was supplied to confirm the original failure's cause.

GLIDE350
The actual native state21 Glide constructor0x2B2D30 requests0x71. Native direction
handling selects71/72/73/74 (aliases76/77/78/79 share the same physical records).
Normal slots75..78 match Olympus37..40 byte-for-byte. BC/BD/BE are not substituted.
Glide release at0x2B2CD1 requests native fall6; there are no separate start/stop
Glide records for this route. glide_validation.json records the executable evidence.

V13 fits source350[0,20] into the first40 native frames of each Glide record,
then holds source20 for the rest. During admitted Glide, the controller caps
the native pose clock at40 and carries progress into queued directional motion
start frames. This prevents takeoff from replaying when steering or looping.
The controller validates the exact affected Glide body before clock/queue writes.
Glide exit into native fall6 uses AquaPart.glide_stop, source350[20,40], on the
existing40-frame fall record. It queues a native fall restart, restores506 at
clock39, and ends on interruption/landing/off. This extra pose and dodge504 are
mutually exclusive. Other mapped motion bodies remain unchanged.
The existing control hook is also installed with air_dodge=0 so native350 phases
can run while Circle504 is disabled. Native Glide ability admission, held-input
rules, state, horizontal movement, descent, collision and defense are untouched.
Clock changes control pose timing only. No extra native MSET records are created.

CASTING / LEFT HAND
Actor+1D8 points to an immutable1408-byte copy while Aqua is active. Only Thunder
requests38/85 move to the alternate existing casting records normal55/80 or
Olympus18/42. Native ground36+spell and air83+spell dispatch remains unchanged.
All other request words and flags remain; the original table is never written.
Fire316/391, Thunder317/390 and Cure318/427 retain the previous source assignments.
Thunder durations remain86/78 rather than shared68/68; final timing needs KH1.
Two existing attachment entry hooks route cast attachment0x30 to LEFT palm206,
selector0x20CE. Native spell scripts, MP, targeting and events remain native.
Exact entry spans and source EXE hash are in native_attachment_validation.json
and cast_request_validation.json. Foreign actors/actions fall through unchanged.

ANATOMICAL REFINEMENTS / SOURCE VARIANTS
V9 wrist pivots100/205 retain authored hand orientation; distal helpers95..99
and200..204 keep bind angles. Rotation-only limb solves preserve local segment
offsets/scales; hair155..193 keeps bind rotations. The frozen V8 reference checks
bounded displacements only for unchanged source actions. Current changed item,
second-ground, finisher, air-combo, fall and casts are excluded from that historical
comparison. This is not rendered mesh collision checking.
007/395 use the identical29-frame shared payload from p02ex_200.arc; gameplay395
is chosen. Other source choices use exact recorded payload hashes. Numeric IDs
are not official command names. Current assignments are the root CSVs; the
unchanged349-clip inventory retains its earlier metadata.

Existing upstream licenses/notices remain in licenses.
Format reference: https://openkh.dev/bbs/file/type/pam.html
'''

def write_csv(name,rows):
    with (DEST/name).open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def build():
    d=ROOT/'ability_v13';runtime=json.loads((d/'runtime_validation.json').read_text());geometry=json.loads((d/'visual_validation.json').read_text())
    reports=[json.loads((d/'curve_validation.json').read_text())]+[json.loads((d/f'sets/p{i}/curve_validation.json').read_text()) for i in range(1,5)]
    dodge=json.loads((d/'dodge/curve_validation.json').read_text());stop=json.loads((d/'glide_stop/curve_validation.json').read_text())
    assert runtime['passed'] and geometry['passed'] and all(x['passed'] for x in reports+[dodge,stop])
    assert runtime['tests']==59 and geometry['tests']==15 and len(reports[0]['motions'])==51
    shutil.copytree(ROOT/'KH1FM_Aqua_Animation_Test_v12',DEST,dirs_exist_ok=True)
    for name in ['CHECK_AQUA_V12.cmd','Check_Aqua_Animations_v12.ps1']:(DEST/name).unlink(missing_ok=True)
    for name in ['aqua.c','aqua_magic.h','aqua_cast_requests.h','aqua_air_dodge.h','aqua_data.h','build.py','generate_data.py','test_runtime.py','test_bridge.c','test_visuals.py',
                 'curve_validation.json','data_validation.json','runtime_validation.json','visual_validation.json','cast_request_validation.json','air_dodge_validation.json','glide_validation.json','source_selections.json']:
        shutil.copy2(d/name,DEST/'source'/name)
    for name in ['fixtures','sets','dodge','glide_stop']:shutil.copytree(d/name,DEST/'source'/name,dirs_exist_ok=True)
    shutil.copy2(d/'kh1-aqua.dll',DEST/'dll/kh1-aqua.dll')
    tools=DEST/'source/retargeting/tools'
    for name in ['build_aqua_complete_v13.py','aqua_v13_plan.py','package_aqua_v13.py']:shutil.copy2(ROOT/'tools'/name,tools/name)
    for name in sorted(set(BANK.values())):shutil.copy2(d/'source_arcs'/name,DEST/'source/retargeting/core_source'/name)
    # Export path resolution, matching previous bundles, without changing the fitted payloads.
    script=tools/'build_aqua_complete_v13.py';s=script.read_text()
    s=s.replace("ROOT=Path(__file__).resolve().parents[1]","ROOT=Path(__file__).resolve().parents[1]\nEXPORTED=ROOT.parent.name=='source'\nWORK=ROOT.parent if EXPORTED else ROOT/'ability_v13'")
    s=s.replace("ROOT/'ability_v13/sampling_cache'","WORK/'sampling_cache'").replace("ROOT/'ability_v13/source_arcs'","WORK/'source_arcs'")
    s=s.replace("if not arc.exists():arc=ROOT/'core_source'/plan['source_bank']","if not arc.exists():arc=ROOT/'core_source'/plan['source_bank']")
    s=s.replace("output=ROOT/'ability_v13' if not args.profile else ROOT/('ability_v13/glide_stop' if args.profile==6 else f'ability_v13/sets/p{args.profile}')",
                "output=WORK if not args.profile else WORK/('glide_stop' if args.profile==6 else f'sets/p{args.profile}')")
    script.write_text(s)
    (DEST/'README_FIRST.txt').write_text(README);(DEST/'source/README_SOURCE.txt').write_text(SOURCE)
    manifest=(ROOT/'KH1FM_Aqua_Animation_Test_v12/mod.yml').read_text();a=manifest.index('description:');b=manifest.index('assets:')
    desc='Revised Test4: main ground300/218/366, air351/353/393, item007/395 and actual native Glide350 opening/held-middle/closing. Circle504 queues a native restart with input diagnostics. Four new combo sets; retains LEFT-hand magic, casts and falling506. Steam Global/Panacea; disable older Aqua and Nine Styles.'
    manifest=manifest[:a]+'description: >-\n  '+desc+'\n'+manifest[b:]
    (DEST/'mod.yml').write_text(manifest.replace('Animation Test v12','Animation Test v13'))
    checker=(ROOT/'KH1FM_Aqua_Animation_Test_v12/Check_Aqua_Animations_v12.ps1').read_text().replace('v12','v13').replace('CHECK_AQUA_V12','CHECK_AQUA_V13')
    (DEST/'Check_Aqua_Animations_v13.ps1').write_text(checker)
    (DEST/'CHECK_AQUA_V13.cmd').write_bytes(b'@echo off\r\nsetlocal\r\npowershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check_Aqua_Animations_v13.ps1" %*\r\npause\r\n')
    for name,remove,magic,air in [('REMOVE_AQUA',1,0,0),('DISABLE_HAND_MAGIC',0,0,1),('DISABLE_AIR_DODGE',0,1,0)]:
        (DEST/f'{name}_kh1-aqua.ini').write_text(f'[aqua]\nremove_aqua={remove}\nhand_magic={magic}\nair_dodge={air}\n')
    labels=['aqua']+[f'aqua {i}' for i in range(1,5)]
    (DEST/'ABILITY_SETS.txt').write_text('\n'.join([f'Ability {label} / id{117+i} / 0 AP'+
        (' / ground300 218 366 / air351 353 393' if not i else f' / ground {" ".join(SETS[i-1][0])} / air {" ".join(SETS[i-1][1])}') for i,label in enumerate(labels)])+
        '\n\nRevised Test4 / v13. Select one while idle. Common actions: dodge504, glide350, item007/395, fall506 and LEFT-hand magic.\n')
    maps=[];sources=[];airmaps=[];glidemaps=[]
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
            'Native frames':40,'Always queued native restart':True,'Uncommitted menu item allowed':True,'Normal falling clip':'506','Input restored after control':True,'Native gravity and velocity':True})
        for phase,source,native,nslots,hslots,trigger in [
            ('start','0..20','0..40','75,76,77,78','37,38,39,40','Native Glide state21 requests71..74 or76..79'),
            ('held flight','20','40 held','75,76,77,78','37,38,39,40','Continue native Glide; preserve phase through steering'),
            ('stop','20..40','0..39','10','10','Native Glide ends into fall request6; interrupt on landing/busy action')]:
            glidemaps.append({'Ability':labels[profile],'Ability id':117+profile,'Phase':phase,'Aqua clip':'350','Source frames':source,
                'Native frame timing':native,'Normal slots':nslots,'Olympus slots':hslots,'Trigger':trigger,'Restored falling clip':'506'})
    for profile,report in enumerate(reports+[dodge,stop]):
        for r in report['motions']:
            if not profile and r['normal_slot'] not in [58,59,75,76,77,78,99,100,101,102,103,104]:continue
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
    expected={'version':13,'assets':[]}
    for name,p in [('dll/kh1-aqua.dll',DEST/'dll/kh1-aqua.dll'),('xa_ex_0010.mset',DEST/'assets/xa_ex_0010.mset'),('xa_ex_0010_he.mset',DEST/'assets/xa_ex_0010_he.mset')]:
        expected['assets'].append({'name':name,'sha256':sha(p),'bytes':p.stat().st_size})
    (DEST/'expected_assets.json').write_text(json.dumps(expected,indent=2)+'\n')
    records=[r for report in reports+[dodge,stop] for r in report['motions']]
    validation={'version':13,'test_round':4,'test_round_label':'revised Test4','offline_checks_passed':True,'game_runtime_tested':False,
        'abilities':labels,'ability_ids':list(range(117,122)),'main_ground_combo':['300','218','366'],'main_air_combo':['351','353','393'],
        'item_use':'395','item_source_aliases':'007 / 395','glide':'350','glide_opening_source_range':[0,20],'glide_held_source_frame':20,'glide_closing_source_range':[20,40],
        'air_dodge':'504','normal_falling':'506','test_4_combos':SETS,'normal_motion_records_per_profile':51,'olympus_motion_records_per_profile':50,
        'unique_generated_pose_variants':len(records),'actual_pe_mock_tests':runtime['tests'],'geometry_assignment_tests':geometry['tests'],
        'pose_samples':sum(r['validated_pose_samples'] for r in records),'max_pose_position_fit_error':max(r['max_pose_position_error'] for r in records),
        'max_non_root_attachment_translation_error':max(r['max_non_root_attachment_translation_error'] for r in records),
        'max_scale_error':max(r['max_scale_error'] for r in records),'native_travel_error':max(r['root_helper_error'] for r in records),
        'original_motion_lengths_headers_counts_and_msets_preserved':True,'helper_slots':11,'left_palm_magic':206,
        'air_dodge_always_native_queued_restart':True,'air_dodge_one_per_airtime':True,'air_dodge_directional_input_allowed':True,
        'air_dodge_input_diagnostics':True,'glide_native_unlock_required':True,'glide_direction_changes_keep_pose_progress':True,'dll_sha256':sha(DEST/'dll/kh1-aqua.dll'),
        'limitations':['Windows/KH1 execution and rendered appearance pending','The cause of504 failure has not been confirmed by an in-game log',
            'Native Glide unlock/input/physics remain;350 phase transitions need in-game testing','504 retains native fall gravity and40-frame timing with no extra invulnerability',
            'Thunder retains v10 alternate casting durations86/78']}
    (DEST/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    assert len(maps)==255 and len(glidemaps)==15 and len(records)==81
    for suffix in ['', '_he']:
        assert (DEST/f'assets/xa_ex_0010{suffix}.mset').read_bytes()==(ROOT/f'sora_source/Custom Movesets KH1/xa_ex_0010{suffix}.mset').read_bytes()
    with zipfile.ZipFile(DEST.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.so','.o','.obj']:z.write(p,p.relative_to(DEST))
    with zipfile.ZipFile(DEST.with_suffix('.zip')) as z:assert z.testzip() is None
    print(json.dumps({'zip':str(DEST.with_suffix('.zip')),'bytes':DEST.with_suffix('.zip').stat().st_size,'sha256':sha(DEST.with_suffix('.zip')),'validation':validation},indent=2))
if __name__=='__main__':build()
