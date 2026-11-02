"""Main-only timing, head turns and animation choices; numbered tests retained."""
from copy import deepcopy
from aqua_v18_plan import get_plan as previous_plan,choose,SETS,BANK,SOURCES
MAIN_CHANGED_COMMON=[1,5,6,7,110]

def get_plan(profile):
    result=deepcopy(previous_plan(profile))
    if profile in [1,2,3,4]:
        present={p['normal_slot'] for p in result}
        result += [deepcopy(p) for p in previous_plan(0) if p['normal_slot'] in MAIN_CHANGED_COMMON and p['normal_slot'] not in present]
    if profile==0:
        for p in result:
            slot=p['normal_slot']
            if slot==103:choose(p,'353')
            if slot==104:choose(p,'407')
            if slot==101:
                p.update(source_range=[12,47],runtime_playback_rate=47./35.,event_timing='trim_finisher_source12')
            if slot in [5,6,7]:
                choose(p,'004' if slot==7 else '013');p.update(loop=True,run_head_mapping='source_head5_to_skin150')
            if slot==1:p['head_yaw_character_degrees']=20.
            if slot in [79,82]:p['head_yaw_character_degrees']=-20.
            if slot==110:
                p.update(source_timing='guard_forward_hold_reverse',guard_forward_end=26.5,
                    guard_reverse_start=26.5,guard_reverse_end=53.,runtime_playback_rate=53./156.,
                    event_timing='full_animation_guard')
    if profile==7:
        for p in result:
            if p['normal_slot']==80:p['head_yaw_character_degrees']=-20.
    return sorted(result,key=lambda p:p['normal_slot'])
