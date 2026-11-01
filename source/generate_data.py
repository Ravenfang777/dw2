from pathlib import Path
import struct,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from kh1_motion_source import read_mset,u32
p=ROOT/'sora_source/Custom Movesets KH1'
orig=(p/'xa_ex_0010.mset').read_bytes();probe=(ROOT/'KH1FM_Aqua_Arm_Probe_v4/assets/xa_ex_0010.mset').read_bytes()
bank=read_mset(orig);m=bank['motions'][98];changed=read_mset(probe)['motions'][98]
he=(p/'xa_ex_0010_he.mset').read_bytes();heb=read_mset(he);heslot=u32(he,heb['sections'][1]+0xc8*4)&4095
assert heb['motions'][heslot].raw==m.raw
key_at=u32(m.raw,40);count=max(c.first+len(c.keys) for c in m.channels+m.helper_channels)
patches=[]
for k in range(count):
    before=m.raw[key_at+k*16:key_at+k*16+16];after=changed.raw[key_at+k*16:key_at+k*16+16]
    if before!=after:
        assert before[:4]==after[:4]
        patches.append((k,*struct.unpack('<4I',before),*struct.unpack('<3I',after[4:])))
assert len(patches)==60
selected=[c for c in m.helper_channels if c.bone in [4,7] and c.kind in [7,8,9]]
guards=sorted(set([c.first for c in selected]+[c.first+len(c.keys)-1 for c in selected]))
scalar=[(at,u32(m.raw,at)) for at in [4,8,16,24,32,44,52]]
channel_at=u32(m.raw,36);channels=m.raw[channel_at:channel_at+len(m.helper_channels)*6]
lines=['/* Generated only from user-provided original Sora and the tested v4 probe. */',
       '#define AQUA_PATCH_COUNT '+str(len(patches)),
       'typedef struct { unsigned int key; unsigned int head; unsigned int before[3]; unsigned int after[3]; } AquaPatch;',
       'static const AquaPatch aqua_patches[AQUA_PATCH_COUNT] = {']
for k,head,*vals in patches:lines.append('    {'+str(k)+','+hex(head)+', {'+','.join(hex(v)+'u' for v in vals[:3])+'}, {'+','.join(hex(v)+'u' for v in vals[3:])+'}},')
lines+=['};','typedef struct { unsigned int key; unsigned int words[4]; } AquaGuard;',f'#define AQUA_GUARD_COUNT {len(guards)}','static const AquaGuard aqua_guards[AQUA_GUARD_COUNT] = {']
for k in guards:lines.append('    {'+str(k)+', {'+','.join(hex(v)+'u' for v in struct.unpack_from('<4I',m.raw,key_at+k*16))+'}},')
lines+=['};','typedef struct { unsigned int offset,value; } AquaScalar;',f'#define AQUA_SCALAR_COUNT {len(scalar)}','static const AquaScalar aqua_scalars[AQUA_SCALAR_COUNT] = {']
for at,v in scalar:lines.append(f'    {{{at},{hex(v)}u}},')
lines+=['};',f'#define AQUA_CHANNEL_BYTES {len(channels)}','static const unsigned char aqua_helper_channels[AQUA_CHANNEL_BYTES] = {'+','.join(hex(v) for v in channels)+'};',f'#define AQUA_KEY_BYTES {count*16}',f'#define AQUA_RAW_MOTION_BYTES {len(m.raw)}']
(Path(__file__).parent/'aqua_data.h').write_text('\n'.join(lines)+'\n')
report={'source_sha256':hashlib.sha256(orig).hexdigest(),'v4_sha256':hashlib.sha256(probe).hexdigest(),'patches':len(patches),'normal_slot':98,'olympus_slot':heslot,'normal_and_olympus_first_attack_identical':True,'unchanged_anchor_keys':guards,'scalar_fingerprint':scalar,'key_bytes':count*16,'motion_bytes':len(m.raw)}
(Path(__file__).parent/'data_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
