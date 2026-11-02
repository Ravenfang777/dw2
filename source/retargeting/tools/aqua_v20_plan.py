"""Main recovery trims, right skull roll, and wider air follow-up windows."""
from copy import deepcopy
from aqua_v19_plan import get_plan as previous_plan,choose,SETS,BANK,SOURCES

def get_plan(profile):
    result=deepcopy(previous_plan(profile))
    if profile==0:
        for p in result:
            s=p['normal_slot']
            if s==1:
                p.pop('head_yaw_character_degrees',None)
                p['head_roll_character_degrees']=20.
            if s in [99,100]:
                p.update(source_range=[0,37],native_hold_frame=30. if s==99 else 42.,
                    runtime_playback_rate=1. if s==99 else 1.4,event_timing='trim_second_recovery')
            if s in [102,103]:p['event_timing']='air_followup_window'
    return result
