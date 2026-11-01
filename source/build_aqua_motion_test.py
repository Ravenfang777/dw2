"""Build an isolated KH1 native-MSET body-motion test from user-owned assets.

No BBS actor logic, events, collisions, particles, or sounds are transplanted.
The original KH1 motion prefixes, helper keys, timings and action maps survive.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,math,struct,warnings
import numpy as np
from scipy.spatial.transform import Rotation

from bbs_source_inspector import read_pmo_skeleton,read_pam
from render_aqua_diagnostics import bind_components,worlds
from kh1_motion_source import read_model,read_mset,parse_motion,pose,helper_pose,matrix,u32


ROOT=Path(__file__).resolve().parents[1]

# Anatomical roles, measured against both received skeletons. Sora's duplicate
# frame/corrective joints share the donor role; his lengths and widths stay his.
MAPPING={}
def group(targets,source):
    for target in targets:MAPPING[target]=source
group(range(0,3),1);group([3],33)
group(range(68,72),2);group([76,77],2);group([78],3)
group(range(144,151),4);group([151],5)
group(range(89,93),14);group([93],15);group([94],16);group(range(95,102),17)
group(range(194,198),24);group([198],25);group([199],26);group(range(200,207),27)
group([16,17],47);group([18],48);group(range(19,23),49);group([23,24],50)
group([42,43],41);group([44],42);group(range(45,49),43);group([49,50],44)

# Native request values resolve through the MSET's actual second-section map.
# Attack-group order is provisional pending the user's first gameplay feedback.
PLAN=[
    {'action':'ground first','request':0xC8,'donor':'300'},
    {'action':'ground second','request':0xC9,'donor':'301'},
    {'action':'ground alternate','request':0xCA,'donor':'302'},
    {'action':'ground finisher','request':0xCB,'donor':'304'},
    {'action':'air first','request':0xCC,'donor':'305'},
    {'action':'air second','request':0xCD,'donor':'306'},
    {'action':'air finisher','request':0xCE,'donor':'309'},
    {'action':'Guard startup','request':0xBC,'donor':'400','source_range':[0.,20.]},
    {'action':'Guard hold','request':0xBD,'donor':'400','source_range':[20.,20.]},
    {'action':'Guard recovery','request':0xBE,'donor':'400','source_range':[20.,0.]},
    {'action':'Dodge Roll / Cartwheel','request':0xDC,'donor':'009'},
]


def rotation(m):
    result=m[:3,:3].copy()
    result/=np.linalg.norm(result,axis=0)
    if not np.isfinite(result).all() or np.linalg.det(result)<0.99:
        raise ValueError('Invalid retarget rotation basis')
    return result


class Retarget:
    def __init__(self,source,target,native_idle):
        self.source=source;self.target=target;self.source_components=bind_components(source)
        self.source_bind=[]
        for bone in source['bones']:
            m=np.array(bone['transform']).reshape(4,4).T
            parent=bone['parent']
            self.source_bind.append(m if parent is None else self.source_bind[parent]@m)
        self.source_bind=np.array(self.source_bind)
        self.source_rotation=np.array([rotation(m) for m in self.source_bind])
        self.target_rotation=np.array([rotation(m) for m in target.bind])
        self.source_hip=(self.source_bind[41,:3,3]+self.source_bind[47,:3,3])*0.5
        target_hip=(target.bind[17,:3,3]+target.bind[43,:3,3])*0.5
        self.ratio=target_hip[1]/self.source_hip[1]
        if not 40 < self.ratio < 150:raise ValueError('Unexpected donor/target unit ratio')
        self.rest=target.local.copy();accepted=0
        for i,parent in enumerate(target.parents):
            if i in MAPPING:continue
            reference=matrix(target.local[i])
            local=native_idle[i] if parent<0 else np.linalg.inv(native_idle[parent])@native_idle[i]
            axes=np.linalg.norm(local[:3,:3],axis=0)
            if not np.isfinite(local).all() or np.min(axes)<1e-6:continue
            if np.max(np.abs(local[3]-[0,0,0,1]))>1e-5:continue
            if np.linalg.norm(local[:3,3]-reference[:3,3])>32:continue
            if np.any(axes/target.local[i,:3]<0.5) or np.any(axes/target.local[i,:3]>2):continue
            try:
                basis=rotation(local)
            except ValueError:
                continue
            if np.max(np.abs(basis.T@basis-np.eye(3)))>0.02:continue
            with warnings.catch_warnings():
                warnings.simplefilter('ignore',UserWarning)
                self.rest[i,3:6]=Rotation.from_matrix(basis).as_euler('xyz')
            self.rest[i,6:9]=local[:3,3];accepted+=1
        self.accepted_secondary=accepted
        self.rest_rotation=Rotation.from_euler('xyz',self.rest[:,3:6]).as_matrix()
        self.accum_scale=self.rest[:,:3].copy()
        for i,parent in enumerate(target.parents):
            if parent>=0:self.accum_scale[i]*=self.accum_scale[parent]

    def from_world(self,source_pose):
        local=self.rest.copy();result=np.repeat(np.eye(4)[None],len(self.target.parents),axis=0)
        rotations=np.empty((len(self.target.parents),3,3))
        donor_rotations=source_pose[:,:3,:3]/np.linalg.norm(source_pose[:,:3,:3],axis=1)[:,None,:]
        mapped_angles=[];mapped_indices=[]
        for i,parent in enumerate(self.target.parents):
            parent_r=np.eye(3) if parent<0 else rotations[parent]
            if i in MAPPING:
                source_i=MAPPING[i]
                desired=(donor_rotations[source_i]@self.source_rotation[source_i].T
                         @self.target_rotation[i])
                mapped_angles.append(parent_r.T@desired);mapped_indices.append(i)
            else:
                desired=parent_r@self.rest_rotation[i]
            if i==0:
                local[i,6:9]=self.target.bind[0,:3,3]
                source_hip=(source_pose[41,:3,3]+source_pose[47,:3,3])*0.5
                local[i,7]+=(source_hip[1]-self.source_hip[1])*self.ratio
            # All mapped local translations remain Sora's own authored lengths.
            result[i,:3,:3]=desired*self.accum_scale[i]
            result[i,:3,3]=local[i,6:9] if parent<0 else (result[parent,:3,:3]@local[i,6:9]+result[parent,:3,3])
            rotations[i]=desired
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',UserWarning)
            local[mapped_indices,3:6]=Rotation.from_matrix(np.array(mapped_angles)).as_euler('xyz')
        return local,result

    def sample(self,animation,frame,grounded=False):
        donor=worlds(self.source,animation,frame,self.source_components)
        local,result=self.from_world(donor)
        if grounded:
            # Match the authored source support height while retaining Sora's
            # own segment lengths. Hands participate during Cartwheel; in a
            # standing pose their weight is negligible. This is a body-height
            # calibration, not an actor mover or a new collision/IK hook.
            candidates=[]
            for source_i,target_i in [(50,22),(44,48)]:
                height=donor[source_i,1,3]-self.source_bind[source_i,1,3]
                wanted=self.target.bind[target_i,1,3]+height*self.ratio
                candidates.append((height,wanted-result[target_i,1,3]))
            for source_i,target_i in [(18,101),(28,206)]:
                height=donor[source_i,1,3]
                candidates.append((height,height*self.ratio-result[target_i,1,3]))
            heights=np.array([v[0] for v in candidates]);corrections=np.array([v[1] for v in candidates])
            weights=np.exp(-(heights-heights.min())/0.025)
            correction=float(weights@corrections/weights.sum())
            if not math.isfinite(correction) or abs(correction)>100:
                raise ValueError('Unbounded anatomical support correction')
            local[0,7]+=correction
            result[:,1,3]+=correction
        return local,result


def align(data,alignment=16):
    data.extend(bytes((-len(data))%alignment))


def sample_times(frames,lo,hi):
    times=list(np.arange(0.,frames-1+1e-6,.5))
    if lo!=hi:
        for source_time in range(math.ceil(min(lo,hi)),math.floor(max(lo,hi))+1):
            times.append((source_time-lo)/(hi-lo)*(frames-1))
    ticks=sorted({round(t*256) for t in times if 0<=t<=frames-1})
    return np.array(ticks,dtype=float)/256


def bake_height(calibration,animation,lo,hi,frames,grounded):
    cache={}
    def sample(tick):
        if tick not in cache:
            t=tick/256/max(1,frames-1)
            cache[tick]=calibration.sample(animation,lo+(hi-lo)*t,grounded)
        return cache[tick]
    ticks=[round(t*256) for t in sample_times(frames,lo,hi)]
    for _ in range(16):
        additions=[];worst=0.
        for a,b in zip(ticks,ticks[1:]):
            av=sample(a)[0][0,7];bv=sample(b)[0][0,7]
            errors=[]
            for fraction in [.25,.5,.75]:
                tick=round(a+(b-a)*fraction)
                if tick in [a,b]:continue
                predicted=av+(bv-av)*(tick-a)/(b-a)
                error=abs(float(sample(tick)[0][0,7]-predicted))
                worst=max(worst,error);errors.append((error,tick))
            if errors:
                error,tick=max(errors)
                if error>.12:additions.append(tick)
        if not additions:break
        ticks=sorted(set(ticks+additions))
        if len(ticks)>255:raise ValueError('Adaptive body-height curve exceeds native 255-key channel')
    else:raise ValueError('Adaptive body-height sampling did not converge')
    local=np.array([sample(t)[0] for t in ticks]);world=np.array([sample(t)[1] for t in ticks])
    return np.array(ticks)/256,local,world,worst


def compile_helper_motion(original,calibration,animation,lo,hi,times,body_samples):
    """Transfer donor FK curves to native helpers, then copy world rotations.

    Constant calibration children perform the bind-basis conversion without
    rebaking animated donor rotations into Sora's different Euler bases.
    A duplicate of the old final helper preserves native actor root movement.
    """
    data=bytearray(original.raw);n=len(original.flags)
    old_key_count=max((c.first+len(c.keys) for c in original.channels+original.helper_channels),default=0)
    old_key_pointer=u32(original.raw,40)
    keys=bytearray(original.raw[old_key_pointer:old_key_pointer+old_key_count*16])
    old_helpers=len(original.helper_local)
    helper_records=bytearray(original.raw[u32(original.raw,48):u32(original.raw,48)+old_helpers*40])
    helper_channels=bytearray(original.raw[u32(original.raw,36):u32(original.raw,36)+len(original.helper_channels)*6])
    body_channels=bytearray();constants=bytearray();flags=np.zeros(n,dtype=np.uint32)

    def add_channel(table,bone,kind,key_times,values):
        if len(values)>255:raise ValueError('Native channel exceeds 255 keys')
        if np.ptp(values)<1e-7:return False
        first=len(keys)//16
        if first+len(values)>65535:raise ValueError('Native key-index limit')
        table.extend(struct.pack('<HBBH',bone,kind,len(values),first))
        last_tick=-1
        for frame,value in zip(key_times,values):
            tick=round(float(frame)*256)
            if tick<=last_tick:raise ValueError('Duplicate or unordered helper key tick')
            last_tick=tick
            keys.extend(struct.pack('<ifff',(tick<<8)|1,float(value),0.,0.))
        return True

    used=set(MAPPING.values())
    for source_i in list(used):
        parent=calibration.source['bones'][source_i]['parent']
        while parent is not None:
            used.add(parent);parent=calibration.source['bones'][parent]['parent']
    source_to_helper={};source_components=calibration.source_components.copy()
    for (bone,axis),value in animation.sample_channels(lo).items():source_components[bone,axis]=value
    for source_i in sorted(used):
        index=len(helper_records)//40;source_to_helper[source_i]=index
        source_parent=calibration.source['bones'][source_i]['parent']
        parent=0 if source_parent is None else source_to_helper[source_parent]
        v=source_components[source_i]
        helper_records.extend(struct.pack('<3fi3f3f',*v[6:9],parent,*v[3:6],*v[:3]))
        if lo==hi:continue
        for axis in range(9):
            channel=animation.channels.get((source_i,axis))
            if channel is None:continue
            interior=[float(t) for t in channel.frames if min(lo,hi)<t<max(lo,hi)]
            source_times=[lo]+sorted(interior,reverse=hi<lo)+[hi]
            values=[channel.sample(t) for t in source_times]
            native_times=[(t-lo)/(hi-lo)*(original.frames-1) for t in source_times]
            # Source T/R/S axes map to KH1 S/R/T channel kinds.
            kind=axis+7 if axis<3 else axis+1 if axis<6 else axis-5
            add_channel(helper_channels,index,kind,native_times,values)

    calibration_helpers={}
    for target_i,source_i in MAPPING.items():
        basis=calibration.source_rotation[source_i].T@calibration.target_rotation[target_i]
        identity=(source_i,tuple(np.round(basis,7).ravel()))
        index=calibration_helpers.get(identity)
        if index is None:
            index=len(helper_records)//40
            with warnings.catch_warnings():
                warnings.simplefilter('ignore',UserWarning)
                angles=Rotation.from_matrix(basis).as_euler('xyz')
            helper_records.extend(struct.pack('<3fi3f3f',1.,1.,1.,source_to_helper[source_i],*angles,0.,0.,0.))
            calibration_helpers[identity]=index
        flags[target_i]=2|((index+1)<<2)

    # The game's root-movement output comes from the final helper. Keep the old
    # hierarchy and append an exact copy of that final record and its tracks.
    root_copy_index=len(helper_records)//40
    helper_records.extend(original.raw[u32(original.raw,48)+(old_helpers-1)*40:u32(original.raw,48)+old_helpers*40])
    for channel in original.helper_channels:
        if channel.bone==old_helpers-1:
            packed=channel.kind|(channel.before<<4)|(channel.after<<6)
            helper_channels.extend(struct.pack('<HBBH',root_copy_index,packed,len(channel.keys),channel.first))
    helper_count=len(helper_records)//40
    if helper_count>128:raise ValueError('This test limits the native helper hierarchy to 128 records')

    base=calibration.rest.copy();base[0,6:9]=body_samples[0,0,6:9]
    for bone in range(n):
        for component in range(9):constants.extend(struct.pack('<HHf',bone,component+1,float(base[bone,component])))
    add_channel(body_channels,0,8,times,body_samples[:,0,7])
    align(data);flags_at=len(data);data.extend(flags.astype('<u4').tobytes())
    align(data);constants_at=len(data);data.extend(constants)
    align(data);body_channels_at=len(data);data.extend(body_channels)
    align(data);helper_at=len(data);data.extend(helper_records)
    align(data);helper_channels_at=len(data);data.extend(helper_channels)
    align(data);keys_at=len(data);data.extend(keys);align(data)
    patches={20:flags_at,24:len(body_channels)//6,28:body_channels_at,
             32:len(helper_channels)//6,36:helper_channels_at,40:keys_at,
             44:helper_count,48:helper_at,52:len(constants)//8,56:constants_at}
    for offset,value in patches.items():struct.pack_into('<I',data,offset,value)
    parsed=parse_motion(bytes(data))
    allowed={j for at in patches for j in range(at,at+4)}
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original.raw,data)))
    assert np.array_equal(parsed.helper_local[:old_helpers],original.helper_local)
    assert np.array_equal(parsed.helper_local[-1],original.helper_local[-1])
    assert parsed.helper_parents[-1]==original.helper_parents[-1]
    for before,after in zip(original.helper_channels,parsed.helper_channels):
        assert (before.bone,before.kind,before.before,before.after,before.first)==(after.bone,after.kind,after.before,after.after,after.first)
        assert np.array_equal(before.keys,after.keys)
    return bytes(data),{'dynamic_body_tracks':len(body_channels)//6,'helper_tracks':len(helper_channels)//6,
                       'native_helper_records':old_helpers,'retarget_helper_records':helper_count,
                       'source_helper_joints':len(used),'calibration_helpers':len(calibration_helpers),
                       'constants':len(constants)//8,'shared_keys':len(keys)//16,
                       'original_bytes':len(original.raw),'retargeted_bytes':len(data)}


def build(source_name='xa_ex_0010.mset', report_name='validation.json'):
    source=read_pmo_skeleton((ROOT/'core_source/p02ex00.pmo').read_bytes())
    donor={a.name:a for a in read_pam((ROOT/'core_source/p02ex_001.pam').read_bytes(),54)}
    model_data=(ROOT/'sora_source/Custom Movesets KH1/xa_ex_0010.mdls').read_bytes()
    source_mset=(ROOT/'sora_source/Custom Movesets KH1'/source_name).read_bytes()
    model=read_model(model_data);bank=read_mset(source_mset)
    if len(model.parents)!=293:raise ValueError('This calibration requires normal Sora, 293 joints')
    calibration=Retarget(source,model,pose(model,bank['motions'][1],0))
    _,rest=calibration.from_world(calibration.source_bind)
    rest_error=max(float(np.max(np.abs(rest[i]-model.bind[i]))) for i in MAPPING)
    if rest_error>1e-3:raise AssertionError(('Mapped bind pose drift',rest_error))
    new_bank=bytearray(bank['bank']);records=[];frames_for_preview={}
    remap_at=bank['sections'][1]
    desired_by_slot={}
    for plan in PLAN:
        request=plan['request'];entry=u32(source_mset,remap_at+request*4);slot=entry&4095
        if slot>=len(bank['motions']) or bank['motions'][slot] is None:raise ValueError('Unresolved native request')
        original=bank['motions'][slot];animation=donor[plan['donor']]
        lo,hi=plan.get('source_range',[0.,float(animation.frame_count-1)])
        times,locals_,poses,height_error=bake_height(calibration,animation,lo,hi,original.frames,
                                                    not plan['action'].startswith('air '))
        body,metrics=compile_helper_motion(original,calibration,animation,lo,hi,times,locals_)
        align(new_bank);at=len(new_bank);new_bank.extend(body)
        struct.pack_into('<I',new_bank,64+slot*4,at-64)
        integer_indices=np.searchsorted(times,np.arange(original.frames,dtype=float))
        desired_by_slot[slot]=poses[integer_indices]
        frames_for_preview[slot]=poses[integer_indices]
        records.append({**plan,'request_hex':f'0x{request:02X}','native_slot':slot,
                        'native_frames':original.frames,'native_fps':original.fps,
                        'source_frames':animation.frame_count,'source_fps':animation.fps,
                        'body_height_samples':len(times),'max_checked_height_interpolation_error':height_error,
                        'anatomical_support_height':not plan['action'].startswith('air '),
                        'sample_source_range':[lo,hi],**metrics})
    struct.pack_into('<I',new_bank,4,len(new_bank)-8)
    delta=len(new_bank)-len(bank['bank'])
    if delta%16:raise AssertionError('Section relocation must preserve 16-byte alignment')
    result=bytearray(source_mset[:bank['start']]+new_bank+source_mset[bank['end']:])
    for i,offset in enumerate(bank['sections']):
        if offset>=bank['end']:struct.pack_into('<I',result,4+i*4,offset+delta)
    verified=read_mset(bytes(result))
    targets=set(desired_by_slot)
    preserved=0
    for slot,(before,after) in enumerate(zip(bank['motions'],verified['motions'])):
        assert (before is None)==(after is None)
        if before is None:continue
        assert before.frames==after.frames and before.fps==after.fps
        if slot not in targets:
            assert after.raw.startswith(before.raw)
            preserved+=1
    for i in range(1,len(bank['sections'])):
        old_start=bank['sections'][i];old_end=bank['sections'][i+1] if i+1<len(bank['sections']) else len(source_mset)
        new_start=verified['sections'][i]
        assert source_mset[old_start:old_end]==result[new_start:new_start+old_end-old_start]
    worst_position=0.;worst_basis=0.;worst_length=0.;samples=0
    worst_between_position=0.;worst_between_basis=0.;worst_root=0.;between_samples=0
    for slot,expected in desired_by_slot.items():
        motion=verified['motions'][slot]
        for frame in range(motion.frames):
            actual=pose(model,motion,float(frame))
            worst_position=max(worst_position,float(np.max(np.abs(actual[:,:3,3]-expected[frame,:,:3,3]))))
            worst_basis=max(worst_basis,float(np.max(np.abs(actual[:,:3,:3]-expected[frame,:,:3,:3]))))
            for i,parent in enumerate(model.parents):
                if i not in MAPPING or parent<0:continue
                distance=np.linalg.norm(actual[i,:3,3]-actual[parent,:3,3])
                reference=np.linalg.norm(model.local[i,6:9])
                worst_length=max(worst_length,abs(float(distance-reference)))
            samples+=1
    for record in records:
        slot=record['native_slot'];motion=verified['motions'][slot]
        original=bank['motions'][slot];animation=donor[record['donor']]
        lo,hi=record['sample_source_range']
        # Half frames catch Euler discontinuities; quarter frames check the
        # interpolation of the densely sampled anatomical height correction.
        for frame in np.arange(.25,motion.frames-1,.25):
            if float(frame).is_integer():continue
            source_frame=lo+(hi-lo)*float(frame)/(motion.frames-1)
            _,expected=calibration.sample(animation,source_frame,record['anatomical_support_height'])
            actual=pose(model,motion,float(frame))
            worst_between_position=max(worst_between_position,float(np.max(np.abs(actual[:,:3,3]-expected[:,:3,3]))))
            worst_between_basis=max(worst_between_basis,float(np.max(np.abs(actual[:,:3,:3]-expected[:,:3,:3]))))
            between_samples+=1
        for frame in np.arange(0.,motion.frames,.5):
            before=helper_pose(original,float(frame))[-1]
            after=helper_pose(motion,float(frame))[-1]
            worst_root=max(worst_root,float(np.max(np.abs(before-after))))
    if worst_position>1.0 or worst_basis>0.01 or worst_length>0.005:
        raise AssertionError(('Serialized pose does not match retarget',worst_position,worst_basis,worst_length))
    if worst_between_position>2.0 or worst_between_basis>0.01 or worst_root>1e-7:
        raise AssertionError(('Subframe pose or native root movement changed',worst_between_position,worst_between_basis,worst_root))
    out=ROOT/'KH1FM_Aqua_Motion_Test_v1';(out/'assets').mkdir(parents=True,exist_ok=True)
    (out/'assets'/source_name).write_bytes(result)
    validation={'passed':True,'asset_name':source_name,'source_core_bank':'data/bbs/arc/pc/p02base.arc::p02ex_001.pam',
                'source_model_bones':54,'target_model_bones':293,'mapped_target_joints':len(MAPPING),
                'secondary_rest_joints':calibration.accepted_secondary,'unit_ratio':calibration.ratio,
                'mapped_bind_matrix_error':rest_error,'replaced_motions':len(records),
                'preserved_other_motions':preserved,'verified_integer_frame_poses':samples,
                'max_position_roundtrip_error':worst_position,'max_basis_roundtrip_error':worst_basis,
                'max_mapped_segment_length_error':worst_length,'action_maps_byte_identical':True,
                'verified_between_frame_poses':between_samples,
                'max_between_frame_position_error':worst_between_position,
                'max_between_frame_basis_error':worst_between_basis,
                'max_native_root_helper_matrix_error':worst_root,
                'native_helper_keys_and_prefixes_preserved':True,'game_runtime_tested':False,
                'rotation_transfer':'Native donor helper hierarchy and constant per-bone bind calibration; world-rotation-copy flags',
                'source_sha256':{'sora_model':hashlib.sha256(model_data).hexdigest(),
                                 'sora_mset':hashlib.sha256(source_mset).hexdigest(),
                                 'aqua_pam':hashlib.sha256((ROOT/'core_source/p02ex_001.pam').read_bytes()).hexdigest()},
                'output_sha256':hashlib.sha256(result).hexdigest(),'motions':records}
    (out/report_name).write_text(json.dumps(validation,indent=2)+'\n')
    np.savez_compressed(ROOT/(source_name+'_preview.npz'),**{str(k):v for k,v in frames_for_preview.items()})
    print(json.dumps({k:v for k,v in validation.items() if k not in ['motions','source_sha256']},indent=2))
    return validation


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace',type=Path,default=ROOT)
    parser.add_argument('--source-name',default='xa_ex_0010.mset',choices=['xa_ex_0010.mset','xa_ex_0010_he.mset'])
    parser.add_argument('--report-name',default='validation.json')
    args=parser.parse_args()
    ROOT=args.workspace.resolve()
    build(args.source_name,args.report_name)
