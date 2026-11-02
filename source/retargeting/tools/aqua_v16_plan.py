"""Aqua v16: native Blizzard, usable combo recovery, lifted run head."""
from copy import deepcopy
from aqua_v15_plan import get_plan as previous_plan,assign,SETS,BANK,SOURCES,GLIDE_SLOTS

def get_plan(profile):
    if profile==7:
        result=[p for p in deepcopy(previous_plan(0)) if p['normal_slot'] in [55,80]]
        for p in result:
            assign(p,'391' if p['normal_slot']==55 else '316')
            p['action']='Blizzard Fire visual, native spell events'
        return result
    result=deepcopy(previous_plan(profile))
    for p in result:
        p.pop('event_timing',None)
        if profile==0:
            if p['normal_slot']==98:p['event_timing']='first_contact'
            if p['normal_slot'] in [99,100]:
                p['event_timing']='second_contact_recovery'
                p['source_timing']='combo_finish_hold'
                p['native_hold_frame']=32 if p['normal_slot']==99 else 44
            if p['normal_slot'] in [5,6,7]:p['run_head_lift_degrees']=12.
    return result
