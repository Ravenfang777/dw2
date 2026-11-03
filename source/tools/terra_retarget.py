"""Bind-length calibration with consistent cloth attachments and hand grip.

V6 borrowed local offsets and cloth folds from one native idle frame. A fixed
fold can pull clothing away from a new limb pose. Keep checked face/finger/grip
turns while restoring the model's own cloth and attachment rest transforms.
"""
import numpy as np
from scipy.spatial.transform import Rotation
from terra_retarget_math import Retarget
from kh1_motion_source import matrices

def turn_between(a,b):
    a=a/np.linalg.norm(a);b=b/np.linalg.norm(b);v=np.cross(a,b);w=1+float(a@b)
    if w<1e-6:
        basis=np.array([0.,1.,0.]) if abs(a[1])<.9 else np.array([0.,0.,1.])
        axis=np.cross(a,basis);return Rotation.from_rotvec(axis/np.linalg.norm(axis)*np.pi).as_matrix()
    q=np.r_[v,w];return Rotation.from_quat(q/np.linalg.norm(q)).as_matrix()

class RetargetV7(Retarget):
    def __init__(self,source,target,native_idle):
        super().__init__(source,target,native_idle)
        previous=self.rest.copy()
        keep_turns=set(range(103,128))|set(range(152,194))|set(range(207,232))|set(range(280,293))
        for i in range(len(target.parents)):
            if i not in self.mapping and i not in keep_turns:self.rest[i,3:6]=target.local[i,3:6]
            # The equipped blade's authored grip is a placement adjustment.
            # Every anatomical/clothing attachment keeps its own bind offset.
            if i!=280:self.rest[i,6:9]=target.local[i,6:9]
            self.rest[i,:3]=target.local[i,:3]
        self.rest_rotation=Rotation.from_euler('xyz',self.rest[:,3:6]).as_matrix()
        self.corrected_rest_joints=int(np.sum(np.max(np.abs(self.rest-previous),axis=1)>1e-5))
        self.max_attachment_offset_correction=float(np.max(np.linalg.norm(self.rest[1:,6:9]-previous[1:,6:9],axis=1)))

    def sample(self,animation,frame,grounded=False):
        local,body=super().sample(animation,frame,grounded)
        if not grounded:return local,body
        # Terra's close stance can overlap Sora's substantially larger boots.
        # Widen only supported stances, through a two-link leg solve. Every
        # segment keeps its own length; no scaling or attachment edits occur.
        feet=body[[19,45],:3,3];hips=body[[17,43],:3,3]
        support=float(np.clip((12-abs(feet[0,1]-feet[1,1]))/6,0,1))
        support*=float(np.clip((30-float(np.max(feet[:,1])))/10,0,1))
        support*=float(np.clip((body[151,1,3]-body[3,1,3]-15)/15,0,1))
        lateral=hips[1]-hips[0];lateral[1]=0
        if np.linalg.norm(lateral)<1e-6 or support<1e-6:return local,body
        lateral/=np.linalg.norm(lateral)
        minimum=np.linalg.norm(self.target.bind[43,:3,3]-self.target.bind[17,:3,3])*1.35
        spread=float(np.clip((minimum-float((feet[1]-feet[0])@lateral))*.5,0,7))*support
        if spread<1e-6:return local,body
        orientations={}
        for hip,knee,ankle,first,last,sign in [(17,18,19,16,24,-1),(43,44,45,42,50,1)]:
            start=body[hip,:3,3];bend=body[knee,:3,3];end=body[ankle,:3,3]
            goal=end+lateral*(sign*spread)
            a=float(np.linalg.norm(bend-start));b=float(np.linalg.norm(end-bend))
            delta=goal-start;distance=float(np.linalg.norm(delta));maximum=a+b-.25
            if distance>maximum:delta*=maximum/distance;distance=maximum;goal=start+delta
            direction=delta/distance;pole=bend-start-direction*float((bend-start)@direction)
            if np.linalg.norm(pole)<1e-5:
                pole=np.cross(direction,lateral)
                if np.linalg.norm(pole)<1e-5:pole=np.cross(direction,[0,0,1])
            pole/=np.linalg.norm(pole)
            along=(a*a+distance*distance-b*b)/(2*distance)
            new_bend=start+direction*along+pole*np.sqrt(max(0.,a*a-along*along))
            upper=turn_between(bend-start,new_bend-start)
            lower=turn_between(end-bend,goal-new_bend)
            orientations[first]=upper@body[first,:3,:3]
            orientations[hip]=upper@body[hip,:3,:3]
            orientations[knee]=lower@body[knee,:3,:3]
            for i in range(ankle,last+1):orientations[i]=body[i,:3,:3]
        result=np.empty_like(body);transforms=matrices(local)
        for i,parent in enumerate(self.target.parents):
            if i in orientations:
                parent_r=np.eye(3) if parent<0 else result[parent,:3,:3]
                relative=parent_r.T@orientations[i]
                local[i,3:6]=Rotation.from_matrix(relative).as_euler('xyz')
                transforms[i,:3,:3]=relative*local[i,:3]
            result[i]=transforms[i] if parent<0 else result[parent]@transforms[i]
        return local,result
