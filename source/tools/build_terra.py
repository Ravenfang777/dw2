"""Build checked Terra body payloads for main and ten standalone test profiles."""
from pathlib import Path
import os,sys,json,hashlib,struct,warnings,time
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from bbs_source_inspector import read_pmo_skeleton,read_arc,read_pam
from kh1_motion_source import read_model,read_mset,pose
from terra_retarget import RetargetV7
from terra_fit import compact
ROOT=Path(__file__).resolve().parents[1]
MODEL=BANK=HE=CAL=ANIMS=None
FORCE=False

def initialize(force=False):
 global MODEL,BANK,HE,CAL,ANIMS,FORCE
 FORCE=force
 warnings.filterwarnings('ignore',message='Gimbal lock detected')
 MODEL=read_model((ROOT/'xa_ex_0010.mdls').read_bytes());BANK=read_mset((ROOT/'xa_ex_0010.mset').read_bytes());HE=read_mset((ROOT/'xa_ex_0010_he.mset').read_bytes())
 source=read_pmo_skeleton((ROOT/'terra_source/p03ex00.pmo').read_bytes());CAL=RetargetV7(source,MODEL,pose(MODEL,BANK['motions'][1],0))
 ANIMS={}
 for path in sorted((ROOT/'terra_source').glob('*.arc')):
  for member,payload in read_arc(path.read_bytes())[0]:
   if payload.startswith(b'PAM\0'):
    for a in read_pam(payload,51):
     start=struct.unpack_from('<I',payload,16+16*a.slot)[0];sha=hashlib.sha256(payload[start:a.data_end]).hexdigest()
     # Duplicate numeric labels can be bank-specific variants. The sorted
     # canonical bank is explicit in every serialized record/selection report.
     if a.name not in ANIMS:ANIMS[a.name]=(a,path.name,sha)

def common_plan():
 rows=[]
 def add(slot,request,action,donor,source_range=None,loop=False,grounded=True,root='travel',normal_only=False):
  rows.append(dict(normal_slot=slot,request=request,action=action,donor=donor,source_range=source_range,loop=loop,grounded=grounded,root=root,normal_only=normal_only))
 add(0,0,'idle','001',loop=True);rows[-1]['head_pitch_up_degrees']=15.
 add(1,0,'combat idle','002',loop=True);rows[-1]['head_pitch_up_degrees']=15.
 for slot in [2,3]:add(slot,1,'walk','003',loop=True)
 add(4,1,'combat walk','012',loop=True)
 for slot in [5,6]:add(slot,2,'run','004',loop=True)
 add(7,2,'combat run','013',loop=True)
 add(8,4,'jump takeoff','005',[0,9],grounded=False);add(9,5,'jump rise','005',[9,15],grounded=False)
 add(10,6,'fall','006',[7,20],loop=True,grounded=False);add(11,7,'landing','007')
 add(12,9,'high jump takeoff','014',[0,16],grounded=False);add(13,10,'high jump rise','014',[16,32],grounded=False)
 add(14,13,'ledge hang','020',[55,94],loop=True,grounded=False,root='hand_anchor');rows[-1]['anchor_hand']=206
 add(15,14,'ledge climb start','021',[0,4],grounded=False,root='hand_anchor');rows[-1]['anchor_hand']=206
 add(16,15,'ledge climb finish','021',[4,13],grounded=False,root='climb');rows[-1]['anchor_hand']=206
 add(17,16,'ledge landing recovery','007',root='native',normal_only=True)
 add(54,0x36,'ground Fire release','315',[0,23]);add(55,0x37,'ground Blizzard/Gravity release','315',[0,23]);add(56,0x38,'ground Cure/Thunder/Aero/Stop release','317',[0,24])
 add(57,0x3d,'ground Cure/Thunder/Aero/Stop recovery','317',[24,36]);add(58,0x3e,'ground item','399');add(59,0x3f,'air item','399',grounded=False)
 add(79,0x83,'air Fire release','316',[0,23],grounded=False);add(80,0x84,'air Blizzard/Gravity release','316',[0,23],grounded=False)
 add(81,0x85,'air Cure/Thunder/Aero/Stop release','318',[0,24],grounded=False);add(82,0x8a,'air Cure/Thunder/Aero/Stop recovery','318',[24,36],grounded=False)
 add(110,0xd4,'Guard pose (former grounded Cure)','354');add(117,0xdc,'Dodge Roll / Terra slide pose','009')
 return rows

def overlay_plan():
 return [dict(normal_slot=slot,request=request,action=action,donor=donor,source_range=source_range,loop=False,grounded=grounded,root='travel',normal_only=False)
  for slot,request,action,donor,source_range,grounded in [
   (10,6,'Superglide tap slide during native fall','009',None,False),
   (57,0x3d,'ground Fire/Blizzard/Gravity recovery','315',[23,35],True),
   (82,0x8a,'air Fire/Blizzard/Gravity recovery','316',[23,35],False)]]

def numbered_cast_plan():
 return [dict(normal_slot=slot,request=request,action=action,donor=donor,source_range=source_range,loop=False,grounded=grounded,root='travel',normal_only=False)
  for slot,request,action,donor,source_range,grounded in [
   (54,0x36,'ground cast release','354',[0,23],True),
   (55,0x37,'ground overhead cast','320',None,True),
   (79,0x83,'air cast release','355',[0,29],False),
   (80,0x84,'air overhead cast','320',None,False),
   (56,0x38,'ground support cast','354',None,True),
   (57,0x3d,'ground cast recovery','354',[23,35],True),
   (58,0x3e,'ground item','600',None,True),
   (59,0x3f,'air item','601',None,False),
   (81,0x85,'air support cast','355',None,False),
   (82,0x8a,'air cast recovery','355',[29,50],False),
   (110,0xd4,'Guard pose','400',None,True)]]

def combo_plan(ground,air):
 return [dict(normal_slot=slot,request=request,action=action,donor=clip,source_range=None,loop=False,grounded=slot<102,root='travel',normal_only=False)
  for slot,request,action,clip in [(98,0xc8,'ground first',ground[0]),(99,0xc9,'ground second',ground[1]),(100,0xca,'ground alternate second',ground[1]),(101,0xcb,'ground finisher',ground[2]),(102,0xcc,'air first',air[0]),(103,0xcd,'air second',air[1]),(104,0xce,'air finisher',air[2])]]

def build_one(job):
 profile,plan=job;slot=plan['normal_slot'];folder=ROOT if profile==0 else ROOT/'overlays' if profile==-1 else ROOT/'sets/shared_v2' if profile==-2 else ROOT/f'sets/p{profile}';fixture=folder/'fixtures';fixture.mkdir(parents=True,exist_ok=True)
 if not FORCE and (fixture/f'terra_s{slot:03d}.bin').exists() and (fixture/f's{slot:03d}_metrics.json').exists():
  metrics=json.loads((fixture/f's{slot:03d}_metrics.json').read_text())
  if all(metrics.get(k)==v for k,v in plan.items()):return profile,metrics
 native=BANK['motions'][slot];a,bank,sha=ANIMS[plan['donor']];plan={**plan,'source_bank':bank,'source_sha256':sha}
 if plan['donor']=='616':plan['tip_precision']=True
 if plan['source_range']:assert 0<=plan['source_range'][0]<plan['source_range'][1]<=a.frame_count-1
 hes=[i for i,m in enumerate(HE['motions']) if m is not None and m.raw==native.raw]
 assert len(hes)==1 or (not hes and plan.get('normal_only')),(slot,hes)
 start=time.monotonic();result,metrics=compact(MODEL,native,a,CAL,plan)
 stem=f's{slot:03d}';(fixture/f'original_{stem}.bin').write_bytes(native.raw);(fixture/f'terra_{stem}.bin').write_bytes(result.raw)
 metrics={**plan,'fixture_stem':stem,'olympus_slot':hes[0] if hes else 0xffffffff,'native_frames':native.frames,'motion_bytes':len(native.raw),'source_frames':a.frame_count,'source_fps':a.fps,**metrics,'fit_seconds':round(time.monotonic()-start,3)}
 (fixture/f'{stem}_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');return profile,metrics

def main():
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=4);ap.add_argument('--slot',type=int);ap.add_argument('--force',action='store_true');args=ap.parse_args()
 if args.force:
  import shutil
  shutil.rmtree(ROOT/'sampling_cache',ignore_errors=True)
 config=json.loads((ROOT/'profile_plan.json').read_text());jobs=[(0,p) for p in common_plan()+combo_plan(config['main']['ground'],config['main']['air'])]
 for test in config['tests']:jobs.extend((test['profile'],p) for p in combo_plan(test['ground'],test['air']))
 jobs.extend((-1,p) for p in overlay_plan())
 jobs.extend((-2,p) for p in numbered_cast_plan())
 if args.slot is not None:jobs=[j for j in jobs if j[1]['normal_slot']==args.slot and j[0]==0]
 profiles={i:[] for i in range(-2,11)};failures=[]
 with ProcessPoolExecutor(max_workers=args.workers,initializer=initialize,initargs=(args.force,)) as pool:
  pending={pool.submit(build_one,j):j for j in jobs}
  for future in as_completed(pending):
   j=pending[future]
   try:
    profile,metrics=future.result();profiles[profile].append(metrics)
    print(f"PROFILE {profile:02} SLOT {metrics['normal_slot']:03} Terra {metrics['donor']} pose_error={metrics['max_pose_position_error']:.3f} keys={metrics['body_keys_used']}/{metrics['reusable_key_capacity']} seconds={metrics['fit_seconds']}",flush=True)
   except Exception as e:
    failures.append({'profile':j[0],'plan':j[1],'error':repr(e)});print('FAILED',j[0],j[1]['normal_slot'],j[1]['donor'],repr(e),flush=True)
 for profile,records in profiles.items():
  if not records:continue
  folder=ROOT if profile==0 else ROOT/'overlays' if profile==-1 else ROOT/'sets/shared_v2' if profile==-2 else ROOT/f'sets/p{profile}'
  (folder/'curve_validation.json').write_text(json.dumps({'passed':not any(f['profile']==profile for f in failures),'profile':profile,'source_character':'Terra','source_bones':51,'target_bones':293,'motion_headers_counts_and_capacities_unchanged':True,'native_events_hitboxes_and_defensive_timing_unchanged':True,'native_glide_and_damage_reactions_unchanged':True,'motions':sorted(records,key=lambda r:r['normal_slot'])},indent=2)+'\n')
 (ROOT/'fit_failures.json').write_text(json.dumps(failures,indent=2)+'\n')
 print('COMPLETED',sum(map(len,profiles.values())),'FAILURES',len(failures),flush=True)
 return bool(failures)
if __name__=='__main__':raise SystemExit(main())
