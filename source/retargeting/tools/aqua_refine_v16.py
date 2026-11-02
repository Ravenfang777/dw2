"""Lift only the running head; retain native neck, lengths, scale and hair."""
import numpy as np
from scipy.spatial.transform import Rotation
from aqua_refine_v9 import refine as previous_refine,apply_world_rotations
from aqua_retarget_math import rotation

def refine(model,local,world,grounded,plan=None):
    local,world=previous_refine(model,local,world,grounded,plan)
    lift=plan.get('run_head_lift_degrees',0.) if plan else 0.
    if lift:
        axis=rotation(world[0])@rotation(model.bind[0]).T@np.array([1.,0.,0.])
        correction=Rotation.from_rotvec(axis*np.deg2rad(-lift)).as_matrix()
        world=apply_world_rotations(model,local,{151:correction@rotation(world[151])})
    return local,world
