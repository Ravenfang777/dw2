"""Main Aqua casting swaps and second hits; numbered Test4 profiles retain v13."""
from copy import deepcopy
from aqua_v13_plan import get_plan as previous_plan,assign,SETS,BANK,SOURCES,GLIDE_SLOTS
MAIN_CAST_SLOTS={54,56,57,79,81,82}
MAIN_CHANGES={54:('391',[0,31]),57:('391',[31,48]),
              79:('316',[0,20]),82:('316',[20,30]),
              56:('427',None),81:('318',None),
              99:('365',None),100:('365',None),103:('371',None)}

def get_plan(profile):
    if profile in [5,6]:return deepcopy(previous_plan(profile))
    if profile:
        # These six immutable v13 poses are shared by all numbered profiles.
        common=[p for p in deepcopy(previous_plan(0)) if p['normal_slot'] in MAIN_CAST_SLOTS]
        return sorted(common+deepcopy(previous_plan(profile)),key=lambda p:p['normal_slot'])
    result=deepcopy(previous_plan(0))
    for p in result:
        slot=p['normal_slot']
        if slot in MAIN_CHANGES:
            clip,source_range=MAIN_CHANGES[slot]
            assign(p,clip);p['source_range']=source_range
    return result
