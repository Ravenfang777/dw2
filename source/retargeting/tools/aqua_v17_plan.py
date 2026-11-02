"""Main Aqua300 second /305,407,351 air; native Glide; skinned head fix."""
from copy import deepcopy
from aqua_v16_plan import get_plan as previous_plan,assign,SETS,BANK,SOURCES
GLIDE_SLOTS={}

def base_assign(p,clip):
    for key in ['source_sha256','source_aliases']:p.pop(key,None)
    p.update(donor=clip,source_bank='base',source_range=None,loop=False)

def get_plan(profile):
    if profile==6:raise ValueError('Default Glide has no Aqua closing overlay')
    result=[p for p in deepcopy(previous_plan(profile)) if p['normal_slot'] not in [75,76,77,78]]
    if profile==0:
        for p in result:
            slot=p['normal_slot']
            if slot in [99,100]:
                base_assign(p,'300');p['event_timing']='second300_contact_recovery'
            if slot==102:base_assign(p,'305')
            if slot in [103,104]:assign(p,'407' if slot==103 else '351')
            if slot in [5,6,7]:
                p.pop('run_head_lift_degrees',None)
                p['run_head_mapping']='source_head5_to_skin150'
    return result
