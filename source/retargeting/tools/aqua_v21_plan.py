"""Main-only faster recovery and swapped air follow-ups; preserve numbered tests."""
from copy import deepcopy
from aqua_v20_plan import get_plan as previous_plan,choose,SETS,BANK,SOURCES

def get_plan(profile):
    result=deepcopy(previous_plan(profile))
    if profile==0:
        for p in result:
            slot=p['normal_slot']
            if slot in [99,100]:
                p.update(source_range=[0,30],native_hold_frame=24. if slot==99 else 33.6,
                    runtime_playback_rate=1. if slot==99 else 1.4,
                    recovery_tail_rate_multiplier=2.,event_timing='shorter_second_recovery')
            if slot==101:
                p.update(source_range=[15,47],runtime_playback_rate=47./32.,event_timing='trim_finisher_source15')
            if slot in [103,104]:
                choose(p,'407' if slot==103 else '353')
                p['event_timing']='swapped_air_contacts'
    return result
