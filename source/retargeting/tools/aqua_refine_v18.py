"""Keep the entire front hair chain in the model's own local rest pose."""
from aqua_refine_v17 import refine as previous_refine
from aqua_refine_v8 import world_of

def refine(model,local,world,grounded,plan=None):
    local,world=previous_refine(model,local,world,grounded,plan)
    if plan and plan.get('idle_front_hair')=='bind151_154':
        # 151 is the unskinned hair root, 152..154 its front chain. Retarget's
        # native-idle rest correction must not bend these relative to the head.
        # Reset the connected chain together; retain skull150 and all offsets.
        local[151:155,3:6]=model.local[151:155,3:6]
        world=world_of(model,local)
    return local,world
