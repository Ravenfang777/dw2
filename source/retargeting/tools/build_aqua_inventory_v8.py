"""Inventory only the Aqua sources supplied by the user; deduplicate clip bytes.

Numeric PAM labels are source identifiers, not inferred command names. Every
source occurrence is retained, including duplicate loose files and ARC members.
"""
from pathlib import Path
import csv, hashlib, json, struct
from collections import Counter
from bbs_source_inspector import read_pam, read_arc
from aqua_v7_plan import PLAN

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'inventory_v8'
LABELS={
'001':('Idle','Observed pose','Movement'),
'002':('Combat idle','Observed pose','Movement'),
'003':('Walk','Observed pose','Movement'),
'004':('Run','Observed pose','Movement'),
'005':('Jump','Observed pose','Movement'),
'006':('Fall','Observed pose','Movement'),
'007':('Landing','Observed pose','Movement'),
'008':('Ledge grab candidate','Provisional','Movement'),
'009':('Cartwheel','Observed pose','Defense'),
'010':('Stance transition candidate','Provisional','Movement'),
'011':('Stance transition candidate','Provisional','Movement'),
'012':('Combat walk','Observed pose','Movement'),
'013':('Combat run','Observed pose','Movement'),
'014':('High jump / Doubleflight candidate','Provisional','Movement'),
'015':('Air movement candidate','Provisional','Movement'),
'016':('Air recovery candidate','Provisional','Movement'),
'017':('Air movement candidate','Provisional','Movement'),
'020':('Ledge hang','Observed pose','Movement'),
'021':('Ledge climb','Observed pose','Movement'),
'024':('Horizontal body pose','Provisional','Unidentified action'),
'043':('Sliding / recovery candidate','Provisional','Movement'),
'200':('Front flinch','Observed pose','Reaction'),
'202':('Back flinch','Observed pose','Reaction'),
'204':('Heavy front reaction','Observed pose','Reaction'),
'205':('Recovery candidate','Provisional','Reaction'),
'206':('Heavy back reaction','Observed pose','Reaction'),
'207':('Recovery candidate','Provisional','Reaction'),
'208':('Unidentified reaction','Provisional','Reaction'),
'209':('Unidentified reaction','Provisional','Reaction'),
'212':('Knockdown / reaction candidate','Provisional','Reaction'),
'213':('Recovery candidate','Provisional','Reaction'),
'214':('Air front reaction','Observed pose','Reaction'),
'215':('Air back reaction','Observed pose','Reaction'),
'216':('Unidentified reaction','Provisional','Reaction'),
'300':('Ground combo 1','Observed pose','Attack'),
'301':('Ground combo 2','Observed pose','Attack'),
'302':('Ground alternate combo','Observed pose','Attack'),
'303':('Ground alternate / finisher candidate','Provisional','Attack'),
'304':('Ground finisher with flip','Observed pose','Attack'),
'305':('Air combo 1','Observed pose','Attack'),
'306':('Air combo 2','Observed pose','Attack'),
'307':('Air alternate combo','Observed pose','Attack'),
'308':('Air alternate combo','Observed pose','Attack'),
'309':('Air finisher','Observed pose','Attack'),
'320':('Overhead / jumping action; assigned to overhead cast','Provisional','Casting assignment'),
'354':('Ground casting pose assignment','Provisional','Casting assignment'),
'355':('Air casting pose assignment','Provisional','Casting assignment'),
'400':('Barrier pose','Observed pose','Defense'),
'408':('Barrier release / reaction candidate','Provisional','Defense'),
'600':('Ground item use','Observed pose','Item'),
}

def sources():
    for folder in ['core_source','round2_regular','round3_regular','input']:
        for path in sorted((ROOT/folder).rglob('*')):
            if path.is_file() and path.suffix.lower() in ['.pam','.arc']:
                yield path
    pc=ROOT/'capture_20261101/Sources/data/bbs/arc/pc'
    for path in sorted(pc.glob('p02*.arc')):yield path

def write_csv(path,rows):
    if not rows:return
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def build():
    OUT.mkdir(exist_ok=True)
    clips={};occurrences=[];failures=[];pam_count=0;container_hashes=set()
    base_hashes={};air_item_hash=None
    for path in sources():
        # Input capture also contains other characters; require Aqua's prefix.
        if path.name.startswith('p') and not path.name.startswith('p02'):continue
        raw=path.read_bytes()
        try:
            members=read_arc(raw)[0] if path.suffix.lower()=='.arc' else [(path.name,raw)]
        except (ValueError,struct.error) as e:
            failures.append({'source':str(path.relative_to(ROOT)),'error':str(e)});continue
        for member,data in members:
            if data[:4]!=b'PAM\0':continue
            if member.startswith('p') and not member.startswith('p02'):continue
            pam_count+=1;container_hashes.add(hashlib.sha256(data).hexdigest())
            locator=str(path.relative_to(ROOT))+(f'::{member}' if path.suffix.lower()=='.arc' else '')
            try:animations=read_pam(data)
            except (ValueError,struct.error) as e:
                failures.append({'source':locator,'error':str(e)});continue
            separate='p02bd' in locator
            cinematic=path.suffix.lower()=='.pam' and path.name!='p02ex_001.pam'
            for a in animations:
                if a.bone_count!=54:
                    failures.append({'source':locator,'clip':a.name,'error':f'Non-base bone count {a.bone_count}; not included'});continue
                start=struct.unpack_from('<I',data,16+16*a.slot)[0]
                digest=hashlib.sha256(data[start:a.data_end]).hexdigest()
                c=clips.setdefault(digest,{'clip_id':'AQ-'+digest[:12], 'animation_sha256':digest,
                    'names':set(),'sources':set(),'groups':set(),'frames':a.frame_count,'fps':a.fps,
                    'duration_seconds':a.frame_count/a.fps,'last_frame_seconds':(a.frame_count-1)/a.fps,
                    'bones':a.bone_count,'flag':a.flag,'loop_from':a.loop_from,'loop_to':a.loop_to,
                    'interpolation_frames':a.interpolation_frames,'channels':len(a.channels),
                    'keys':sum(len(ch.frames) for ch in a.channels.values()),'payload_bytes':a.data_end-start})
                group='Separate p02bd bank' if separate else ('Cinematic / event source' if cinematic else 'Gameplay source')
                c['groups'].add(group);c['names'].add(a.name);c['sources'].add(locator)
                occurrences.append({'clip_id':c['clip_id'],'source':locator,'pam_slot':a.slot,'source_name':a.name,
                                    'animation_sha256':digest,'pam_sha256':hashlib.sha256(data).hexdigest()})
                if path==ROOT/'core_source/p02ex_001.pam':base_hashes[a.name]=digest
                if path.name=='p02ex_628.arc' and a.name=='601':air_item_hash=digest
    uses={};mappings=[]
    report=json.loads((ROOT/'ability_v7/curve_validation.json').read_text())
    native={r['normal_slot']:r for r in report['motions']}
    for p in PLAN:
        digest=base_hashes[p['donor']] if p['source_bank']=='base' else air_item_hash
        assert digest in clips,p
        uses.setdefault(digest,[]).append(f"{p['action']} (slot {p['normal_slot']}, req 0x{p['request']:02X})")
        n=native[p['normal_slot']]
        mappings.append({'normal_slot':p['normal_slot'],'olympus_slot':n['olympus_slot'] if n['olympus_slot']!=0xffffffff else 'Not present',
            'request_hex':f"0x{p['request']:02X}",'kh1_action':p['action'],'clip_id':clips[digest]['clip_id'],
            'aqua_name':p['donor'],'aqua_bank':p['source_bank'],'source_start_frame':(p['source_range'] or [0,clips[digest]['frames']-1])[0],
            'source_end_frame':(p['source_range'] or [0,clips[digest]['frames']-1])[1],
            'kh1_frames':n['native_frames'],'kh1_fps':60,'pose_loop':p['loop'],'root_policy':p['root']})
    lookup={d:name for name,d in base_hashes.items()}
    rows=[]
    for digest,c in clips.items():
        base_name=lookup.get(digest)
        label,confidence,category=LABELS.get(base_name,('Unidentified clip','Unidentified','Unidentified action'))
        if digest==air_item_hash:label,confidence,category='Air item use assignment','Provisional','Item'
        group=' / '.join(sorted(c['groups']))
        if 'Separate p02bd bank' in c['groups'] and 'Gameplay source' not in c['groups']:
            category='Separate rig/bank';confidence='Compatibility unverified'
        if all(g=='Cinematic / event source' for g in c['groups']):category='Cinematic / event';label='Unidentified cinematic / event clip'
        locators=sorted(c['sources'],key=lambda s:(s!='core_source/p02ex_001.pam',not s.startswith('core_source/'),not s.startswith('capture_'),s))
        rows.append({'clip_id':c['clip_id'],'source_names':' / '.join(sorted(c['names'])),'source_group':group,
            'identification':label,'confidence':confidence,'category':category,'frames':c['frames'],'fps':c['fps'],
            'duration_seconds':c['duration_seconds'],'last_frame_seconds':c['last_frame_seconds'],
            'loop_from':c['loop_from'],'loop_to':c['loop_to'],'raw_flag_hex':f"0x{c['flag']:04X}",
            'interpolation_frames':c['interpolation_frames'],'bones':c['bones'],'channels':c['channels'],'keys':c['keys'],
            'payload_bytes':c['payload_bytes'],'kh1_assignments':'; '.join(uses.get(digest,[])) or 'Not assigned',
            'source_copy_count':sum(o['animation_sha256']==digest for o in occurrences),
            'primary_source':locators[0],'all_sources':'\n'.join(locators),'animation_sha256':digest})
    base_order={clips[d]['clip_id']:name for name,d in base_hashes.items()}
    rows.sort(key=lambda r:(0,base_order[r['clip_id']]) if r['clip_id'] in base_order else
              (1,'Cinematic' in r['source_group'],'Separate' in r['source_group'],r['primary_source'],r['source_names'],r['clip_id']))
    assert len({r['clip_id'] for r in rows})==len(rows)
    write_csv(OUT/'Aqua_All_Clips.csv',rows);write_csv(OUT/'Aqua_Source_Copies.csv',occurrences);write_csv(OUT/'Aqua_KH1_Assignments.csv',mappings)
    result={'unique_clips':len(rows),'decoded_occurrences':len(occurrences),'pam_occurrences':pam_count,'unique_pam_payloads':len(container_hashes),
        'group_counts':dict(Counter(r['source_group'] for r in rows)),'confidence_counts':dict(Counter(r['confidence'] for r in rows)),
        'kh1_assignments':len(mappings),'assigned_unique_clips':len(uses),'failures':failures,
        'duration_definition':'Frames / FPS; last sample is at (Frames - 1) / FPS.',
        'identification_note':'Observed pose describes reviewed movement, not an official BBS command name. Numeric names alone do not establish command identity.',
        'loop_note':'Loop from/to and flags are raw PAM metadata. They are not a guarantee that a command loops in gameplay.',
        'rows':rows,'mappings':mappings}
    (OUT/'Aqua_Inventory.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['rows','mappings']},indent=2))
    return result

if __name__=='__main__':build()
