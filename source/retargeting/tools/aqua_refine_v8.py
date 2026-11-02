"""Bounded pose corrections for Sora's hair and wider limbs.

Hair chains 155..193 return to MDLS bind rotations. Anatomical edits use
two-link rotation solves; bone offsets and scales never change. Hand placement
is preserved in aerial and ledge poses. This is not mesh collision simulation.
"""
import numpy as np
from scipy.spatial.transform import Rotation
from kh1_motion_source import matrices
from aqua_retarget_v7 import turn_between

HAIR=range(155,194)

def world_of(model,local):
    transforms=matrices(local);world=np.empty_like(transforms)
    for i,p in enumerate(model.parents):world[i]=transforms[i] if p<0 else world[p]@transforms[i]
    return world

def closest(point,a,b):
    d=b-a;den=float(d@d)
    return a+d*np.clip(float((point-a)@d)/den if den>1e-8 else 0.,0.,1.)

def solve(model,local,world,start,bend,end,goal,pole_goal,extra_upper=()):
    a=world[start,:3,3].copy();b=world[bend,:3,3].copy();c=world[end,:3,3].copy()
    l1=float(np.linalg.norm(b-a));l2=float(np.linalg.norm(c-b));delta=goal-a;d=float(np.linalg.norm(delta))
    if min(l1,l2,d)<1e-6:return world
    d=float(np.clip(d,abs(l1-l2)+.05,l1+l2-.05));direction=delta/np.linalg.norm(delta);goal=a+direction*d
    old_pole=b-a-direction*float((b-a)@direction)
    new_pole=pole_goal-a-direction*float((pole_goal-a)@direction)
    if min(np.linalg.norm(old_pole),np.linalg.norm(new_pole))<1e-6:return world
    old_pole/=np.linalg.norm(old_pole);new_pole/=np.linalg.norm(new_pole)
    # Avoid abrupt pole flips at almost straight elbows/knees.
    theta=np.arccos(np.clip(float(old_pole@new_pole),-1,1))
    if theta>.35:new_pole=old_pole*np.cos(.35)+(new_pole-old_pole*np.cos(theta))/max(np.sin(theta),1e-6)*np.sin(.35)
    new_pole/=np.linalg.norm(new_pole)
    along=(l1*l1+d*d-l2*l2)/(2*d)
    knee=a+direction*along+new_pole*np.sqrt(max(0.,l1*l1-along*along))
    upper=turn_between(b-a,knee-a);lower=turn_between(c-b,goal-knee)
    desired={start:upper@world[start,:3,:3],bend:lower@world[bend,:3,:3],end:world[end,:3,:3].copy()}
    for i in extra_upper:desired[i]=upper@world[i,:3,:3]
    transforms=matrices(local);result=np.empty_like(world)
    for i,p in enumerate(model.parents):
        if i in desired:
            parent_r=np.eye(3) if p<0 else result[p,:3,:3]
            relative=parent_r.T@desired[i]
            local[i,3:6]=Rotation.from_matrix(relative).as_euler('xyz')
            transforms[i,:3,:3]=relative*local[i,:3]
        result[i]=transforms[i] if p<0 else result[p]@transforms[i]
    return result

def refine(model,local,world,grounded):
    local=local.copy()
    local[list(HAIR),3:6]=model.local[list(HAIR),3:6]
    world=world_of(model,local)
    # A chest-relative outward direction works through spins and Cartwheel.
    right=world[93,:3,3]-world[198,:3,3]
    if np.linalg.norm(right)<1e-6:return local,world
    right/=np.linalg.norm(right)
    for upper,elbow,wrist,side,other in [(93,94,95,1,199),(198,199,200,-1,94)]:
        a=world[3,:3,3];b=world[144,:3,3]
        hand=world[wrist,:3,3].copy();e=world[elbow,:3,3].copy()
        nearest=closest(hand,a,b);away=hand-nearest;gap=float(np.linalg.norm(away))
        goal=hand.copy()
        if grounded and gap<17.:
            direction=away/max(gap,1e-6)
            if gap<1e-4:direction=right*side
            goal+=direction*min(4.,17.-gap)
        nearest=closest(e,a,b);away=e-nearest;gap=float(np.linalg.norm(away))
        correction=np.zeros(3)
        if gap<16.:correction+=away/max(gap,1e-6)*min(5.,16.-gap)
        elbow_gap=float(np.linalg.norm(e-world[other,:3,3]))
        if elbow_gap<12.:correction+=right*side*min(4.,(12.-elbow_gap)*.5)
        if np.linalg.norm(correction)>5.:correction*=5./np.linalg.norm(correction)
        if np.linalg.norm(correction)>1e-5 or np.linalg.norm(goal-hand)>1e-5:
            world=solve(model,local,world,upper,elbow,wrist,goal,e+correction)
    # Keep each knee on its own side when the two knees get close. Foot
    # positions and rotations are retained from the supported V7 stance solve.
    knee_gap=float((world[44,:3,3]-world[18,:3,3])@(-right))
    amount=float(np.clip((12.-knee_gap)*.5,0.,4.))
    if amount>1e-5:
        for hip,knee,ankle,helper,side in [(17,18,19,16,1),(43,44,45,42,-1)]:
            e=world[knee,:3,3].copy()
            world=solve(model,local,world,hip,knee,ankle,world[ankle,:3,3].copy(),e+right*(side*amount),(helper,))
    return local,world
