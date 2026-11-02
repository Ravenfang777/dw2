"""Aqua Test 3 combo sets, main ground finisher411, aerial dodge504."""
from copy import deepcopy
from aqua_v10_plan import get_plan as previous_plan
SETS=[
 (['516','518','519'],['607','608','609']),
 (['610','611','612'],['616','618','619']),
 (['613','602','603'],['604','605','606']),
 (['617','405','406'],['407','452','621']),
]
BANK={'504':'157','411':'313','516':'511','518':'511','519':'511',
      '607':'601','608':'601','609':'602','610':'602','611':'603','612':'603',
      '616':'605','618':'609','619':'609','613':'620',
      '602':'621','603':'621','604':'621','605':'621','606':'621',
      '617':'622','405':'624','406':'624','407':'624','452':'626','621':'629'}
def get_plan(profile):
    base=deepcopy(previous_plan(0))
    for p in base:
        if p['normal_slot']==101:p.update(donor='411',source_range=None,source_bank='p02ex_313.arc')
    if not profile:return base
    if profile==5:
        p=next(p for p in base if p['normal_slot']==10)
        p.update(donor='504',source_range=None,source_bank='p02ex_157.arc',loop=False,action='neutral aerial dodge overlay')
        return [p]
    ground,air=SETS[profile-1];result=[]
    for p in base:
        slot=p['normal_slot']
        if not 98<=slot<=104:continue
        index={98:0,99:1,100:1,101:2,102:0,103:1,104:2}[slot]
        clip=(ground if slot<=101 else air)[index]
        p.update(donor=clip,source_bank='p02ex_'+BANK[clip]+'.arc',source_range=None,loop=False)
        result.append(p)
    return result
