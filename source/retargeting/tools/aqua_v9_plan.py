"""Exact user-selected numbered clips for the four mutually exclusive tests."""
from copy import deepcopy
from aqua_v7_plan import PLAN as BASE

SETS=[
    (['045','217','218'],['332','357','361']),
    (['362','363','350'],['365','366','370']),
    (['370','371','372'],['373','506','315']),
    (['316','317','318'],['391','390','427']),
]
BANK={
'045':'004','217':'009','218':'009','332':'101','357':'102','361':'111',
'362':'111','363':'111','350':'116','365':'123','366':'128','370':'133',
'371':'133','372':'137','373':'137','506':'150','315':'151','316':'151',
'317':'152','318':'152','391':'153','390':'154','427':'154',
}

def get_plan(profile):
    if profile==0:return deepcopy(BASE)
    ground,air=SETS[profile-1];result=[]
    for p in deepcopy(BASE):
        slot=p['normal_slot']
        if not 98<=slot<=104:continue
        index={98:0,99:1,100:1,101:2,102:0,103:1,104:2}[slot]
        p['donor']=(ground if slot<=101 else air)[index]
        p['source_bank']='p02ex_'+BANK[p['donor']]+'.arc'
        p['source_range']=None;p['loop']=False
        result.append(p)
    return result
