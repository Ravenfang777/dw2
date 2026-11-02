"""Next Aqua tests, idle bangs, reversible Guard, native reactions pending KH2."""
from copy import deepcopy
from aqua_v17_plan import get_plan as previous_plan,base_assign,assign,BANK,SOURCES
SETS=[
    (['371','365','366'],['218','332','393']),
    (['352','353','407'],['351','304','303']),
    (['300','301','302'],['616','407','351']),
    (['510','511','512'],['504','514','399']),
]

def choose(p,clip):
    if clip in SOURCES:assign(p,clip)
    else:base_assign(p,clip)
    return p

def get_plan(profile):
    # Omit every Aqua damage/recovery replacement. All native KH1 reaction
    # records remain untouched until the actual default KH2 source is supplied.
    result=[p for p in deepcopy(previous_plan(profile)) if not 61<=p['normal_slot']<=70]
    for p in result:
        slot=p['normal_slot']
        if profile==0:
            if slot in [99,100]:
                base_assign(p,'301');p['event_timing']='second301_contact_recovery'
            if slot in [0,1]:p['idle_front_hair']='bind151_154'
            if slot==110:
                p.update(source_timing='guard_forward_hold_reverse',guard_forward_end=10.,
                         guard_reverse_start=36.,guard_reverse_end=52.)
        if profile in [1,2,3,4] and 98<=slot<=104:
            ground,air=SETS[profile-1]
            choose(p,(ground if slot<=101 else air)[{98:0,99:1,100:1,101:2,102:0,103:1,104:2}[slot]])
    return result
