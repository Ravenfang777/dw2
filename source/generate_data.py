"""Generate the controller's reversible body data from the packaged fixtures."""
from pathlib import Path
import struct,json,hashlib
ROOT=Path(__file__).resolve().parent
report=json.loads((ROOT/'curve_validation.json').read_text())
def u32(d,p):return struct.unpack_from('<I',d,p)[0]
lines=['/* Generated from original and compact-FK motion fixtures. */',
       f'#define AQUA_MOTION_COUNT {len(report["motions"])}',
       '#define AQUA_PART_COUNT 5',
       f'#define AQUA_ANCHOR_INDEX {next(i for i,r in enumerate(report["motions"]) if r["normal_slot"]==98)}',
       'typedef struct { unsigned int field,size,sentinel; const unsigned char *before,*after; } AquaPart;',
       'typedef struct { unsigned int request,normal_slot,olympus_slot,raw_bytes; unsigned int scalars[7]; AquaPart parts[AQUA_PART_COUNT]; } AquaMotion;',
       'static const unsigned int aqua_scalar_fields[7]={4,8,16,24,32,44,52};']
def array(name,data):
    lines.append(f'static const unsigned char {name}[{len(data)}] = {{')
    for i in range(0,len(data),24):lines.append(','.join(str(v) for v in data[i:i+24])+',')
    lines.append('};')
descriptors=[]
for index,r in enumerate(report['motions']):
    request=r['request'];stem=r['fixture_stem'];before=(ROOT/f'fixtures/original_{stem}.bin').read_bytes();after=(ROOT/f'fixtures/aqua_{stem}.bin').read_bytes()
    assert len(before)==len(after) and before[:80]==after[:80]
    channel_at=u32(before,28);body_keys=[]
    for i in range(u32(before,24)):
        n=before[channel_at+i*6+3];first=struct.unpack_from('<H',before,channel_at+i*6+4)[0];body_keys.append(first+n)
    helper_at=u32(before,36)
    for i in range(u32(before,32)):
        n=before[helper_at+i*6+3];first=struct.unpack_from('<H',before,helper_at+i*6+4)[0];body_keys.append(first+n)
    segments=[(20,u32(before,16)*4),(28,u32(before,24)*6),(40,max(body_keys)*16),(56,u32(before,52)*8),(36,u32(before,32)*6)]
    parts=[];allowed=set()
    for j,(field,size) in enumerate(segments):
        offset=u32(before,field);a=before[offset:offset+size];b=after[offset:offset+size];assert len(a)==size and len(b)==size
        array(f'b{index}_{j}',a);array(f'a{index}_{j}',b);allowed.update(range(offset,offset+size))
        sentinel=next(k for k in range(0,size-3,4) if a[k:k+4]!=b[k:k+4])
        parts.append('{'+f'{field},{size},{sentinel},b{index}_{j},a{index}_{j}'+'}')
    assert all(a==b or p in allowed for p,(a,b) in enumerate(zip(before,after)))
    scalars=','.join(str(u32(before,p))+'u' for p in [4,8,16,24,32,44,52])
    descriptors.append('{'+f'{request},{r["normal_slot"]},{r["olympus_slot"]},{len(before)},'+'{'+scalars+'},'+'{'+','.join(parts)+'}}')
lines+=['static const AquaMotion aqua_motions[AQUA_MOTION_COUNT]={',',\n'.join(descriptors),'};']
(ROOT/'aqua_data.h').write_text('\n'.join(lines)+'\n')
(ROOT/'data_validation.json').write_text(json.dumps({'passed':True,'motions':len(descriptors),'source':'Packaged full-byte original and Aqua fixtures','all_headers_and_motion_sizes_identical':True,'all_changes_inside_existing_body_and_helper_tables':True},indent=2)+'\n')
print('Generated',len(descriptors),'motion descriptors')
