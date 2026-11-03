"""Offline donor-to-Sora pose calibration; does not write game files."""
import math,warnings
import numpy as np
from scipy.spatial.transform import Rotation
from bbs_pose_tools import bind_components,worlds
from kh1_motion_source import matrix

TARGET_NAMES={}
def group(targets,source_name):
    for target in targets:TARGET_NAMES[target]=source_name
group(range(0,3),'center');group([3],'koshi')
group(range(68,72),'hara');group([76,77],'hara');group([78],'mune')
group(range(144,150),'kubi');group([150],'atama')
group(range(89,93),'R_kata');group([93],'R_ude1');group([94],'R_ude2');group(range(95,102),'R_te')
group(range(194,198),'L_kata');group([198],'L_ude1');group([199],'L_ude2');group(range(200,207),'L_te')
group([16,17],'R_momo');group([18],'R_sune');group(range(19,23),'R_ashi1');group([23,24],'R_ashi2')
group([42,43],'L_momo');group([44],'L_sune');group(range(45,49),'L_ashi1');group([49,50],'L_ashi2')


def rotation(m):
    result=m[:3,:3].copy()
    result/=np.linalg.norm(result,axis=0)
    if not np.isfinite(result).all() or np.linalg.det(result)<0.99:
        raise ValueError('Invalid retarget rotation basis')
    return result


class Retarget:
    def __init__(self,source,target,native_idle):
        self.source=source;self.target=target;self.source_components=bind_components(source)
        self.indices={b["name"]:b["index"] for b in source["bones"]}
        self.mapping={target:self.indices[name] for target,name in TARGET_NAMES.items()}
        assert source["bone_count"]==51 and len(self.mapping)==len(TARGET_NAMES)
        self.source_bind=[]
        for bone in source['bones']:
            m=np.array(bone['transform']).reshape(4,4).T
            parent=bone['parent']
            self.source_bind.append(m if parent is None else self.source_bind[parent]@m)
        self.source_bind=np.array(self.source_bind)
        self.source_rotation=np.array([rotation(m) for m in self.source_bind])
        self.target_rotation=np.array([rotation(m) for m in target.bind])
        self.source_hip=(self.source_bind[self.indices['L_momo'],:3,3]+self.source_bind[self.indices['R_momo'],:3,3])*0.5
        target_hip=(target.bind[17,:3,3]+target.bind[43,:3,3])*0.5
        self.ratio=target_hip[1]/self.source_hip[1]
        if not 40 < self.ratio < 150:raise ValueError('Unexpected donor/target unit ratio')
        self.rest=target.local.copy();accepted=0
        for i,parent in enumerate(target.parents):
            if i in self.mapping:continue
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
            if i in self.mapping:
                source_i=self.mapping[i]
                desired=(donor_rotations[source_i]@self.source_rotation[source_i].T
                         @self.target_rotation[i])
                mapped_angles.append(parent_r.T@desired);mapped_indices.append(i)
            else:
                desired=parent_r@self.rest_rotation[i]
            if i==0:
                local[i,6:9]=self.target.bind[0,:3,3]
                source_hip=(source_pose[self.indices['L_momo'],:3,3]+source_pose[self.indices['R_momo'],:3,3])*0.5
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
            for source_i,target_i in [(self.indices['R_ashi2'],22),(self.indices['L_ashi2'],48)]:
                height=donor[source_i,1,3]-self.source_bind[source_i,1,3]
                wanted=self.target.bind[target_i,1,3]+height*self.ratio
                candidates.append((height,wanted-result[target_i,1,3]))
            for source_i,target_i in [(self.indices['R_yubiB'],101),(self.indices['L_yubiB'],206)]:
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


