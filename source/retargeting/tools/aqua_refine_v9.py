"""Anatomical wrist pivots and bounded arm clearance for Aqua test profiles.

Sora's 95..99 / 200..204 are the distal forearm and roll helpers. The hand
bends at 100 / 205. Moving the bend to the hand pivot avoids treating the
distal forearm as a hand. All edits are rotations; bind lengths/scales remain.
"""
import numpy as np
from scipy.spatial.transform import Rotation
from kh1_motion_source import matrices
from aqua_retarget_v7 import turn_between
from aqua_refine_v8 import closest,world_of

def apply_world_rotations(model,local,desired):
    transforms=matrices(local);result=np.empty_like(transforms)
    for i,p in enumerate(model.parents):
        if i in desired:
            parent=np.eye(3) if p<0 else result[p,:3,:3]
            relative=parent.T@desired[i]
            local[i,3:6]=Rotation.from_matrix(relative).as_euler('xyz')
            transforms[i,:3,:3]=relative*local[i,:3]
        result[i]=transforms[i] if p<0 else result[p]@transforms[i]
    return result

def align_wrists(model,local,world):
    desired={}
    for elbow,first,pivot in [(94,95,100),(199,200,205)]:
        forearm_delta=world[elbow,:3,:3]@model.bind[elbow,:3,:3].T
        for i in range(first,pivot):desired[i]=forearm_delta@model.bind[i,:3,:3]
        # Preserve the authored hand orientation, at its anatomical pivot.
        desired[pivot]=world[pivot,:3,:3].copy()
    return apply_world_rotations(model,local,desired)

def solve(model,local,world,start,bend,end,goal,pole_goal,upper_helpers=(),lower_helpers=(),pole_limit=.45):
    a=world[start,:3,3].copy();b=world[bend,:3,3].copy();c=world[end,:3,3].copy()
    l1=float(np.linalg.norm(b-a));l2=float(np.linalg.norm(c-b));delta=goal-a;distance=float(np.linalg.norm(delta))
    if min(l1,l2,distance)<1e-6:return world
    d=float(np.clip(distance,abs(l1-l2)+.05,l1+l2-.05));direction=delta/distance;goal=a+direction*d
    old=b-a-direction*float((b-a)@direction);new=pole_goal-a-direction*float((pole_goal-a)@direction)
    if min(np.linalg.norm(old),np.linalg.norm(new))<1e-6:return world
    old/=np.linalg.norm(old);new/=np.linalg.norm(new)
    theta=float(np.arccos(np.clip(old@new,-1,1)))
    if theta>pole_limit:
        ortho=new-old*np.cos(theta)
        if np.linalg.norm(ortho)<1e-6:return world
        new=old*np.cos(pole_limit)+ortho/np.linalg.norm(ortho)*np.sin(pole_limit)
    along=(l1*l1+d*d-l2*l2)/(2*d)
    knee=a+direction*along+new*np.sqrt(max(0.,l1*l1-along*along))
    upper=turn_between(b-a,knee-a);lower=turn_between(c-b,goal-knee)
    desired={start:upper@world[start,:3,:3],bend:lower@world[bend,:3,:3],end:world[end,:3,:3].copy()}
    for i in upper_helpers:desired[i]=upper@world[i,:3,:3]
    for i in lower_helpers:desired[i]=lower@world[i,:3,:3]
    return apply_world_rotations(model,local,desired)

def torso_push(point,a,b,radius,fallback):
    near=closest(point,a,b);away=point-near;gap=float(np.linalg.norm(away))
    if gap>=radius:return np.zeros(3)
    direction=away/gap if gap>1e-5 else fallback
    return direction*(radius-gap)

def refine(model,local,world,grounded,plan=None):
    local=local.copy();local[155:194,3:6]=model.local[155:194,3:6]
    world=align_wrists(model,local,world_of(model,local))
    right=world[93,:3,3]-world[198,:3,3]
    if np.linalg.norm(right)<1e-6:return local,world
    right/=np.linalg.norm(right)
    # Only the original finisher needs the larger correction envelope. Other
    # authored clips keep a smaller adjustment, including the four test sets.
    strong=bool(plan and plan['normal_slot'] in [101,104] and plan['donor'] in ['304','309'])
    maximum=18. if strong else 5.
    hand_start={i:world[i,:3,3].copy() for i in [100,205]}
    for iteration in range(3 if strong else 1):
        for upper,elbow,wrist,side,other in [(93,94,100,1,199),(198,199,205,-1,94)]:
            a=world[3,:3,3];b=world[144,:3,3]
            hand=world[wrist,:3,3].copy();e=world[elbow,:3,3].copy();fallback=right*side
            radius=20. if strong else 18.
            push=torso_push(hand,a,b,radius,fallback) if grounded else np.zeros(3)
            pole=torso_push(e,a,b,19. if strong else 17.,fallback)
            if strong:
                shoulder=world[upper,:3,3]
                for t in [.35,.6,.85]:
                    interior=shoulder*(1-t)+e*t
                    pole+=torso_push(interior,a,b,18.,fallback)*t*.8
            # Inspect the forearm interior as well as its endpoints.
            for t in [.25,.5,.75]:
                interior=e*(1-t)+hand*t
                correction=torso_push(interior,a,b,radius,fallback)
                push+=correction*t*.45;pole+=correction*(1-t)*.6
            elbow_gap=float(np.linalg.norm(e-world[other,:3,3]))
            if elbow_gap<12.:pole+=fallback*(12.-elbow_gap)*.5
            if np.linalg.norm(pole)>maximum:pole*=maximum/np.linalg.norm(pole)
            goal=hand+push
            movement=goal-hand_start[wrist]
            if np.linalg.norm(movement)>maximum:goal=hand_start[wrist]+movement*maximum/np.linalg.norm(movement)
            if not grounded:goal=hand # preserve ledge and airborne hand goals
            if np.linalg.norm(pole)>1e-5 or np.linalg.norm(goal-hand)>1e-5:
                world=solve(model,local,world,upper,elbow,wrist,goal,e+pole,lower_helpers=range(elbow+1,wrist),pole_limit=1. if strong else .4)
    # Preserve the supported V7 foot spacing while separating close knees.
    gap=float((world[44,:3,3]-world[18,:3,3])@(-right));amount=float(np.clip((12.-gap)*.5,0.,4.))
    if amount>1e-5:
        for hip,knee,ankle,helper,side in [(17,18,19,16,1),(43,44,45,42,-1)]:
            e=world[knee,:3,3].copy()
            world=solve(model,local,world,hip,knee,ankle,world[ankle,:3,3].copy(),e+right*(side*amount),upper_helpers=(helper,))
    return local,world
