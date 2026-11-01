"""Build an in-place, one-attack Aqua arm-path probe without MSET growth.

This is a diagnostic. It is not the complete Aqua attack/body conversion.
Only existing wrist-goal curve values/tangents in C8 are eligible to change.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,math,struct
import numpy as np

from bbs_source_inspector import read_pam,read_pmo_skeleton
from aqua_retarget_math import Retarget,rotation
from kh1_motion_source import read_model,read_mset,pose,helper_pose,u32

ROOT=Path(__file__).resolve().parents[1]
PACKAGE='KH1FM_Aqua_Arm_Probe_v4'
ARMS=[{'name':'right','helper':4,'start':93,'elbow':94,'end':95,'parent':92},
      {'name':'left','helper':7,'start':198,'elbow':199,'end':200,'parent':197}]


def build(root=ROOT):
    inputs=root/'sora_source/Custom Movesets KH1'
    original=(inputs/'xa_ex_0010.mset').read_bytes()
    model=read_model((inputs/'xa_ex_0010.mdls').read_bytes());bank=read_mset(original)
    slot=u32(original,bank['sections'][1]+0xC8*4)&4095
    native=bank['motions'][slot]
    assert slot==98 and native.frames==48 and len(native.helper_local)==11
    assert all(native.helper_parents[a['helper']]==3 for a in ARMS)
    source=read_pmo_skeleton((root/'core_source/p02ex00.pmo').read_bytes())
    animation=next(a for a in read_pam((root/'core_source/p02ex_001.pam').read_bytes(),54) if a.name=='300')
    calibration=Retarget(source,model,pose(model,bank['motions'][1],0.))
    cache={}
    max_reach={a['name']:abs(float(model.local[a['elbow'],6]))+abs(float(model.local[a['end'],6])) for a in ARMS}
    assert all(20<v<100 for v in max_reach.values())

    def goals(frame):
        frame=float(frame)
        if frame in cache:return cache[frame]
        native_body=pose(model,native,frame);helpers=helper_pose(native,frame)
        t=min(1.,max(0.,frame/(native.frames-1)))
        _,aqua_body=calibration.sample(animation,t*(animation.frame_count-1),False)
        weight=math.sin(math.pi*t)**2
        result={}
        for arm in ARMS:
            h=arm['helper'];parent=native.helper_parents[h]
            inverse=np.linalg.inv(helpers[parent])
            current=(inverse@helpers[h])[:3,3]
            # Transfer the donor arm vector through the shoulder attachment's
            # calibrated local basis. Native torso, legs and root stay native.
            vector=aqua_body[arm['end'],:3,3]-aqua_body[arm['start'],:3,3]
            arm_local=rotation(aqua_body[arm['parent']]).T@vector
            desired_vector=rotation(native_body[arm['parent']])@arm_local
            shoulder=native_body[arm['start'],:3,3]
            desired_world=shoulder+desired_vector
            desired_local=(inverse@np.r_[desired_world,1.])[:3]
            value=current+(desired_local-current)*weight
            # Leave a small margin so interpolation cannot demand a locked,
            # fully extended native two-link IK arm.
            shoulder_local=(inverse@np.r_[shoulder,1.])[:3]
            direction=value-shoulder_local;distance=np.linalg.norm(direction)
            maximum=max_reach[arm['name']]-.75
            if distance>maximum:value=shoulder_local+direction*(maximum/distance)
            result[h]=value
        cache[frame]=result
        return result

    selected=[c for c in native.helper_channels if c.bone in [4,7] and c.kind in [7,8,9]]
    assert len(selected)==6
    all_channels=native.channels+native.helper_channels
    owners={}
    for channel in all_channels:
        for k in range(channel.first,channel.first+len(channel.keys)):
            owners.setdefault(k,[]).append(channel)
    result=bytearray(original);allowed=set();records=[];written=0
    at=bank['start']+bank['offsets'][slot];key_at=u32(native.raw,40)
    for channel in selected:
        changed=0
        for local_index,key in enumerate(channel.keys):
            frame=float(key[0])/256
            # Preserve authored endpoint values/tangents exactly; admission,
            # start and handoff poses keep their original endpoint records.
            if not 0<frame<native.frames-1:continue
            k=channel.first+local_index
            if len(owners[k])!=1:raise ValueError('A selected wrist key is shared by another curve')
            axis=channel.kind-7
            value=float(goals(frame)[channel.bone][axis])
            epsilon=1/32
            derivative=float((goals(frame+epsilon)[channel.bone][axis]-goals(frame-epsilon)[channel.bone][axis])/(2*epsilon*256))
            derivative=float(np.clip(derivative,-.05,.05))
            if not math.isfinite(value) or abs(value)>150:raise ValueError('Unbounded wrist control value')
            p=at+key_at+k*16+4
            struct.pack_into('<3f',result,p,value,derivative,derivative)
            allowed.update(range(p,p+12));changed+=1;written+=1
        records.append({'helper':channel.bone,'kind':channel.kind,'key_count':len(channel.keys),
                        'changed_key_records':changed,'original_key_indices_and_times_preserved':True})
    assert len(result)==len(original)
    changes=[i for i,(a,b) in enumerate(zip(original,result)) if a!=b]
    assert changes and set(changes)<=allowed
    verified=read_mset(bytes(result));converted=verified['motions'][slot]
    assert original[:128]==result[:128]
    assert original[bank['sections'][1]:]==result[bank['sections'][1]:]
    assert converted.raw[:80]==native.raw[:80]
    assert np.array_equal(converted.flags,native.flags)
    assert np.array_equal(converted.helper_local,native.helper_local)
    assert native.constants==converted.constants
    for index,(before,after) in enumerate(zip(bank['motions'],verified['motions'])):
        if index!=slot:assert before.raw==after.raw
    selected_ids={id(c) for c in selected}
    for before,after in zip(native.channels+native.helper_channels,converted.channels+converted.helper_channels):
        assert (before.bone,before.kind,before.first,before.before,before.after)==(after.bone,after.kind,after.first,after.before,after.after)
        assert np.array_equal(before.keys[:,[0,4]],after.keys[:,[0,4]])
        if id(before) not in selected_ids:
            assert np.array_equal(before.keys,after.keys)

    affected=set()
    for i,parent in enumerate(model.parents):
        # The authored clavicle aim joints also follow the wrist goals.
        if i in [92,197] or parent in affected:affected.add(i)
    unaffected=[i for i in range(len(model.parents)) if i not in affected]
    worst_body=0.;worst_root=0.;max_hand_change=0.;samples=0;unexpected={}
    max_arm_stretch=0.
    for frame in np.arange(0.,native.frames-.001,.25):
        before=pose(model,native,float(frame));after=pose(model,converted,float(frame))
        worst_body=max(worst_body,float(np.max(np.abs(before[unaffected]-after[unaffected]))))
        for i in unaffected:
            error=float(np.max(np.abs(before[i]-after[i])))
            if error>1e-6:unexpected[i]=max(unexpected.get(i,0.),error)
        worst_root=max(worst_root,float(np.max(np.abs(helper_pose(native,float(frame))[-1]-helper_pose(converted,float(frame))[-1]))))
        for arm in ARMS:
            distance=np.linalg.norm(after[arm['end'],:3,3]-after[arm['start'],:3,3])
            max_arm_stretch=max(max_arm_stretch,float(distance-max_reach[arm['name']]))
            max_hand_change=max(max_hand_change,float(np.linalg.norm(after[arm['end'],:3,3]-before[arm['end'],:3,3])))
        samples+=1
    if worst_body>1e-6 or worst_root>1e-7 or max_arm_stretch>3:
        raise AssertionError(('Non-arm pose, actor travel or arm reach changed',worst_body,worst_root,max_arm_stretch,unexpected))
    out=root/PACKAGE;(out/'assets').mkdir(parents=True,exist_ok=True)
    (out/'assets/xa_ex_0010.mset').write_bytes(result)
    he=(inputs/'xa_ex_0010_he.mset').read_bytes();(out/'assets/xa_ex_0010_he.mset').write_bytes(he)
    report={'offline_checks_passed':True,'game_runtime_tested':False,'scope':'Aqua 300 arm paths blended into original first ground attack only',
            'request':'0xC8','native_slot':slot,'source_clip':'300','source_animation_frames':animation.frame_count,
            'native_frames':native.frames,'file_size_before':len(original),'file_size_after':len(result),
            'changed_bytes':len(changes),'patched_existing_key_records':written,'eligible_float_bytes':len(allowed),
            'all_changes_inside_existing_wrist_curves':True,'motion_headers_flags_tables_and_counts_identical':True,
            'existing_helper_count':len(native.helper_local),'helper_count_after':len(converted.helper_local),
            'other_motions_byte_identical':len(bank['motions'])-1,'olympus_file_byte_identical':True,
            'validated_pose_samples':samples,'non_arm_matrix_error':worst_body,'native_root_motion_error':worst_root,
            'max_wrist_displacement_from_native':max_hand_change,'max_arm_reach_excess':max_arm_stretch,
            'source_sha256':hashlib.sha256(original).hexdigest(),'output_sha256':hashlib.sha256(result).hexdigest(),
            'curves':records}
    (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'expected_assets.json').write_text(json.dumps({'version':4,'assets':[{'name':'xa_ex_0010.mset','sha256':report['output_sha256']},{'name':'xa_ex_0010_he.mset','sha256':hashlib.sha256(he).hexdigest()}]},indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='curves'},indent=2))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workspace',type=Path,default=ROOT)
    build(parser.parse_args().workspace.resolve())
