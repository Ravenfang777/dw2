"""Tilt the skinned skull right about character forward; retain aerial cast yaw."""
import numpy as np
from scipy.spatial.transform import Rotation
from aqua_refine_v19 import refine as previous_refine
from aqua_refine_v9 import apply_world_rotations
from aqua_retarget_math import rotation

def refine(model,local,world,grounded,plan=None):
    local,world=previous_refine(model,local,world,grounded,plan)
    if plan and plan.get('head_roll_character_degrees'):
        # +X is Sora's left; Rz(+20) tilts skull up(+Y) toward his right(-X).
        roll=Rotation.from_euler('z',plan['head_roll_character_degrees'],degrees=True).as_matrix()
        root=rotation(world[0]);wanted=root@roll@root.T@rotation(world[150])
        world=apply_world_rotations(model,local,{150:wanted})
    return local,world
