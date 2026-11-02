"""Generate reversible original/base/four-test payloads in existing capacity."""
from pathlib import Path
import hashlib,json,struct
ROOT=Path(__file__).resolve().parent
report=json.loads((ROOT/'curve_validation.json').read_text())
sets=[json.loads((ROOT/f'sets/p{i}/curve_validation.json').read_text()) for i in range(1,5)]
assert report['passed'] and all(x['passed'] for x in sets)
lookup=[{r['normal_slot']:r for r in s['motions']} for s in sets]
def u32(d,p):return struct.unpack_from('<I',d,p)[0]
lines=['/* Generated immutable original and five Aqua profile payloads. */',
       '#define AQUA_PROFILE_COUNT 5',f'#define AQUA_MOTION_COUNT {len(report["motions"])}',
       '#define AQUA_PART_COUNT 5',
       f'#define AQUA_ANCHOR_INDEX {next(i for i,r in enumerate(report["motions"]) if r["normal_slot"]==98)}',
       'typedef struct { unsigned int field,size,sentinel; const unsigned char *before,*after[AQUA_PROFILE_COUNT]; } AquaPart;',
       'typedef struct { unsigned int request,normal_slot,olympus_slot,raw_bytes; unsigned int scalars[7]; AquaPart parts[AQUA_PART_COUNT]; } AquaMotion;',
       'static const unsigned int aqua_scalar_fields[7]={4,8,16,24,32,44,52};']
arrays={}
def array(data):
    digest=hashlib.sha256(data).hexdigest()
    if digest in arrays:return arrays[digest]
    name=f'payload_{len(arrays)}';arrays[digest]=name
    lines.append(f'static const unsigned char {name}[{len(data)}] = {{')
    for i in range(0,len(data),24):lines.append(','.join(str(v) for v in data[i:i+24])+',')
    lines.append('};');return name

descriptors=[]
for r in report['motions']:
    stem=r['fixture_stem'];before=(ROOT/f'fixtures/original_{stem}.bin').read_bytes()
    converted=[(ROOT/f'fixtures/aqua_{stem}.bin').read_bytes()]
    for i,by_slot in enumerate(lookup,1):
        if r['normal_slot'] in by_slot:
            sr=by_slot[r['normal_slot']];p=ROOT/f'sets/p{i}/fixtures'
            assert (p/f'original_{sr["fixture_stem"]}.bin').read_bytes()==before
            converted.append((p/f'aqua_{sr["fixture_stem"]}.bin').read_bytes())
        else:converted.append(converted[0])
    assert all(len(c)==len(before) and c[:80]==before[:80] for c in converted)
    body_keys=[]
    for n_at,p_at in [(24,28),(32,36)]:
        at=u32(before,p_at)
        for i in range(u32(before,n_at)):
            n=before[at+i*6+3];first=struct.unpack_from('<H',before,at+i*6+4)[0];body_keys.append(first+n)
    segments=[(20,u32(before,16)*4),(28,u32(before,24)*6),(40,max(body_keys)*16),(56,u32(before,52)*8),(36,u32(before,32)*6)]
    parts=[];allowed=set()
    for field,size in segments:
        offset=u32(before,field);blobs=[data[offset:offset+size] for data in [before,*converted]]
        assert all(len(b)==size for b in blobs)
        symbols=[array(b) for b in blobs];allowed.update(range(offset,offset+size))
        sentinel=max(range(0,size-3,4),key=lambda k:len({b[k:k+4] for b in blobs}))
        assert len({b[sentinel:sentinel+4] for b in blobs})>1
        parts.append('{'+f'{field},{size},{sentinel},{symbols[0]},'+'{'+','.join(symbols[1:])+'}}')
    for after in converted:assert all(a==b or p in allowed for p,(a,b) in enumerate(zip(before,after)))
    scalars=','.join(str(u32(before,p))+'u' for p in [4,8,16,24,32,44,52])
    descriptors.append('{'+f'{r["request"]},{r["normal_slot"]},{r["olympus_slot"]},{len(before)},'+'{'+scalars+'},'+'{'+','.join(parts)+'}}')
lines+=['static const AquaMotion aqua_motions[AQUA_MOTION_COUNT]={',',\n'.join(descriptors),'};']
(ROOT/'aqua_data.h').write_text('\n'.join(lines)+'\n')
(ROOT/'data_validation.json').write_text(json.dumps({'passed':True,'motions':len(descriptors),'profiles':5,
    'all_headers_and_motion_sizes_identical':True,'all_changes_inside_existing_body_and_helper_tables':True,
    'unique_data_blocks':len(arrays)},indent=2)+'\n')
print('Generated',len(descriptors),'motions and 5 profiles;',len(arrays),'unique blocks')
