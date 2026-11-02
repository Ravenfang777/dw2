"""Aqua assignments for identified normal-Sora motions and their Olympus copies.

Unrelated field actions, summons, Sora-only limits, swimming and glide remain
native. Numeric source identities are retained for review of provisional poses.
"""
PLAN=[]
def add(slot,request,action,donor,*,source_range=None,loop=False,grounded=True,root='travel',bank='base'):
    PLAN.append(dict(normal_slot=slot,request=request,action=action,donor=donor,
                     source_range=source_range,loop=loop,grounded=grounded,root=root,source_bank=bank))

add(0,0,'idle','001',loop=True)
add(1,0,'combat idle','002',loop=True)
for slot in [2,3]:add(slot,1,'walk','003',loop=True)
add(4,1,'combat walk','012',loop=True)
for slot in [5,6]:add(slot,2,'run','004',loop=True)
add(7,2,'combat run','013',loop=True)
add(8,4,'jump takeoff','005',source_range=[0,9],grounded=False)
add(9,5,'jump rise','005',source_range=[9,12],grounded=False)
add(10,6,'fall','006',source_range=[7,15],loop=True,grounded=False)
add(11,7,'landing','007')
add(12,9,'high jump takeoff','014',source_range=[0,16],grounded=False)
add(13,10,'high jump rise','014',source_range=[16,31],grounded=False)
add(14,13,'ledge hang','020',source_range=[55,94],loop=True,grounded=False,root='hand_anchor')
PLAN[-1]['anchor_hand']=206
add(15,14,'ledge climb start','021',source_range=[0,4],grounded=False,root='hand_anchor')
PLAN[-1]['anchor_hand']=206
add(16,15,'ledge climb finish','021',source_range=[4,13],grounded=False,root='climb')
PLAN[-1]['anchor_hand']=206
add(17,16,'ledge landing recovery','007',root='native')
PLAN[-1]['normal_only']=True

# Ground casting shares three native body records among the seven spells;
# Fire has a separate recovery. Matching Aqua ground/air casting poses are
# visual assignments; the original KH1 release events remain authoritative.
add(54,0x36,'ground cast release','354',source_range=[0,23])
add(55,0x37,'ground overhead cast','320')
add(56,0x38,'ground support cast','354')
add(57,0x3d,'ground cast recovery','354',source_range=[23,35])
add(58,0x3e,'ground item use','600')
add(59,0x3f,'air item use','601',grounded=False,bank='p02ex_628.arc')

for slot,request,name,clip in [(61,0x48,'front high flinch','200'),(62,0x49,'front low flinch','200'),
 (63,0x4a,'back high flinch','202'),(64,0x4b,'back low flinch','202'),
 (65,0x4c,'heavy front reaction','204'),(66,0x4d,'heavy back reaction','206'),
 (67,0x4e,'air front reaction','214'),(68,0x4f,'air back reaction','215'),
 (69,0x50,'air front recovery','214'),(70,0x51,'air back recovery','215')]:
    add(slot,request,name,clip,grounded=slot<65,root='native')
add(79,0x83,'air cast release','355',source_range=[0,21],grounded=False)
add(80,0x84,'air overhead cast','320',grounded=False)
add(81,0x85,'air support cast','355',grounded=False)
add(82,0x8a,'air cast recovery','355',source_range=[21,33],grounded=False)

for slot,request,name,clip in [(98,0xc8,'ground first','300'),(99,0xc9,'ground second','301'),
 (100,0xca,'ground alternate','302'),(101,0xcb,'ground finisher','304'),
 (102,0xcc,'air first','305'),(103,0xcd,'air second','306'),(104,0xce,'air finisher','309'),
 (110,0xd4,'Guard / Barrier pose','400'),(117,0xdc,'Dodge Roll / Cartwheel pose','009')]:
    add(slot,request,name,clip,grounded=not 102<=slot<=104)
PLAN.sort(key=lambda p:p['normal_slot'])
