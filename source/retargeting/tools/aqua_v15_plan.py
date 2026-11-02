"""Main Aqua second-air352 and later second-ground contact/chain windows."""
from copy import deepcopy
from aqua_v14_plan import get_plan as previous_plan,assign,SETS,BANK,SOURCES,GLIDE_SLOTS

def get_plan(profile):
    result=deepcopy(previous_plan(profile))
    if profile==0:
        for p in result:
            if p['normal_slot']==103:assign(p,'352')
            if p['normal_slot'] in [99,100]:p['event_timing']='late_contact_finish_chain'
    return result
