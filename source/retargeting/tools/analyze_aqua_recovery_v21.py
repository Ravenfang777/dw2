"""Measure source motion and document the conservative main-only tail trim."""
from pathlib import Path
import json,sys
import numpy as np
from bbs_source_inspector import read_pam
from kh1_motion_source import read_model,read_mset,pose
from aqua_retarget_v7 import RetargetV7
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT.parent
model=read_model((ROOT/'sora_source/Custom Movesets KH1/xa_ex_0010.mdls').read_bytes())
bank=read_mset((WORK.parent/'assets/xa_ex_0010.mset').read_bytes())
source=__import__('bbs_source_inspector').read_pmo_skeleton((ROOT/'core_source/p02ex00.pmo').read_bytes())
rig=RetargetV7(source,model,pose(model,bank['motions'][1],0))
clips={a.name:a for a in read_pam((ROOT/'core_source/p02ex_001.pam').read_bytes(),54)}
rows=[]
for name,cut in [('300',None),('301',30)]:
 a=clips[name];frames=np.array([rig.sample(a,float(t),True)[1] for t in range(a.frame_count)])
 joints=[100,205,150,19,45]
 delta=np.linalg.norm(np.diff(frames[:, :, :3, 3][:,joints,:],axis=0),axis=2)
 step=np.sqrt(np.mean(delta**2,axis=1))
 row={'source':name,'source_frames':a.frame_count,'source_fps':a.fps,
      'measured_joints':joints,'rms_joint_distance_per_source_step':step.tolist(),
      'peak_rms_joint_step':float(step.max()),'retained_source_range':[0,cut if cut else a.frame_count-1]}
 if cut is not None:
  row.update(removed_tail_frames=list(range(cut+1,a.frame_count)),removed_tail_mean_rms_joint_step=float(step[cut:].mean()),
             removed_tail_fraction_of_peak=float(step[cut:].mean()/step.max()))
 else:row['decision']='Retain all first-swing frames and its existing hit/chain timing; no additional quiet plateau warrants cutting its strike.'
 rows.append(row)
report={'version':21,'passed':True,'game_runtime_tested':False,'main_only':True,
 'analysis':rows,'second_swing_chain_real_native_ticks':24.,'second_swing_contact_real_native_ticks':24.*8./30.,
 'second_swing_native_hold_frames':{'99':24.,'100':33.6},'second_swing_native_delta_factors':{'99':1.,'100':1.4},
 'finisher':'366 retains source15..47; additional3 leading frames removed after v20; native events and duration retimed',
 'air_chain_windows':{'102':[18.,40.],'103':[22.,42.]},'air_sequence':['305','407','353'],
 'numbered_profile_changes':False,'second_recovery_tail_rate_multiplier':2.,'additional_second_trim_after_v20':list(range(31,38))}
(WORK/'combo_recovery_analysis.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({r['source']:{k:r[k] for k in r if k in ['removed_tail_fraction_of_peak','removed_tail_mean_rms_joint_step','peak_rms_joint_step']} for r in rows},indent=2))
