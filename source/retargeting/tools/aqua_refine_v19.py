"""Yaw the actual skinned skull, retaining hair shape and face proportions."""
import numpy as np
from scipy.spatial.transform import Rotation
from aqua_refine_v18 import refine as previous_refine
from aqua_refine_v9 import apply_world_rotations
from aqua_retarget_math import rotation

def refine(model,local,world,grounded,plan=None):
    local,world=previous_refine(model,local,world,grounded,plan)
    if plan and plan.get('head_yaw_character_degrees'):
        # Sora left hand205 is +X in native bind; +Y yaw turns +Z toward +X.
        # Rotate skull150 in character coordinates; the hair is its descendant.
        yaw=Rotation.from_rotvec(np.array([0.,np.deg2rad(plan['head_yaw_character_degrees']),0.])).as_matrix()
        wanted=rotation(world[0])@yaw@rotation(world[0]).T@rotation(world[150])
        world=apply_world_rotations(model,local,{150:wanted})
    return local,world
