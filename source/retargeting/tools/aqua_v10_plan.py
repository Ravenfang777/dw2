"""User Test 2 combos and action-specific shared casting families."""
from copy import deepcopy
from aqua_v7_plan import PLAN as ORIGINAL

SETS=[
    (['392','393','428'],['429','504','514']),
    (['515','517','550'],['650','557','411']),
    (['399','352','353'],['500','501','503']),
    (['510','511','512'],['513','507','508']),
]
BANK={
    '316':'151','317':'152','318':'152','391':'153','390':'154','427':'154','506':'150',
    '392':'155','393':'155','428':'156','429':'156','504':'157','514':'157',
    '515':'204','517':'204','550':'204','650':'205','557':'206','411':'313',
    '399':'346','352':'352','353':'352','500':'501','501':'501','503':'501',
    '510':'501','511':'501','512':'501','513':'501','507':'509','508':'509',
}
# Retain the working release/recovery structure, with a shared source frame
# at each Fire boundary. Other spells use their full assigned source clip.
ACTION={
    10:('506',None,'fall'),
    54:('316',[0,20],'Fire cast release'),
    57:('316',[20,30],'Fire cast recovery'),
    55:('317',None,'Thunder casting family'),
    56:('318',None,'Cure casting family'),
    79:('391',[0,31],'air Fire cast release'),
    82:('391',[31,48],'air Fire cast recovery'),
    80:('390',None,'air Thunder casting family'),
    81:('427',None,'air Cure casting family'),
}

def get_plan(profile):
    base=deepcopy(ORIGINAL)
    for p in base:
        if p['normal_slot'] in ACTION:
            clip,frame_range,action=ACTION[p['normal_slot']]
            p.update(donor=clip,source_range=frame_range,action=action,source_bank='p02ex_'+BANK[clip]+'.arc')
            if p['normal_slot'] in {55:0x38,56:0x39,80:0x85,81:0x86}:
                p['request']={55:0x38,56:0x39,80:0x85,81:0x86}[p['normal_slot']]
    if not profile:return base
    ground,air=SETS[profile-1];result=[]
    for p in base:
        slot=p['normal_slot']
        if not 98<=slot<=104:continue
        index={98:0,99:1,100:1,101:2,102:0,103:1,104:2}[slot]
        clip=(ground if slot<=101 else air)[index]
        p.update(donor=clip,source_bank='p02ex_'+BANK[clip]+'.arc',source_range=None,loop=False)
        result.append(p)
    return result
