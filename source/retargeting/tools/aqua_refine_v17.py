"""Put Aqua's authored head orientation on Sora's skinned skull150.

151 is an unskinned hair root. The prior mapping put Aqua head5 there while
skull150 inherited Aqua neck4. Correct runs at skull150, then leave hair151
at its native local bind rotation so the face and hair follow one head.
"""
import numpy as np
from scipy.spatial.transform import Rotation
from aqua_refine_v9 import refine as previous_refine,apply_world_rotations
from aqua_retarget_math import rotation
HEAD_SKIN_JOINT=150
HEAD_HAIR_HELPER=151

def refine(model,local,world,grounded,plan=None):
    local,world=previous_refine(model,local,world,grounded,plan)
    if plan and plan.get('run_head_mapping')=='source_head5_to_skin150':
        authored_head=rotation(world[HEAD_HAIR_HELPER])@rotation(model.bind[HEAD_HAIR_HELPER]).T
        local[HEAD_HAIR_HELPER,3:6]=model.local[HEAD_HAIR_HELPER,3:6]
        world=apply_world_rotations(model,local,{HEAD_SKIN_JOINT:authored_head@rotation(model.bind[HEAD_SKIN_JOINT])})
    return local,world
