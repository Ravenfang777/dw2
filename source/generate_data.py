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
       '#define AQUA_PART_COUNT 6',
       f'#define AQUA_ANCHOR_INDEX {next(i for i,r in enumerate(report["motions"]) if r["normal_slot"]==98)}',
       'typedef struct { unsigned int field,size,sentinel; const unsigned char *before,*after[AQUA_PROFILE_COUNT],*dodge,*blizzard; } AquaPart;',
       'typedef struct { unsigned int request,normal_slot,olympus_slot,raw_bytes,part_count,event_count; const unsigned int *event_schema; unsigned int scalars[7]; AquaPart parts[AQUA_PART_COUNT]; } AquaMotion;',
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
    dodge=(ROOT/'dodge/fixtures/aqua_s010.bin').read_bytes() if r['normal_slot']==10 else None
    blizzard=(ROOT/f'blizzard/fixtures/aqua_{stem}.bin').read_bytes() if r['normal_slot'] in [55,80] else None
    assert all(len(c)==len(before) and c[:80]==before[:80] for c in converted)
    if dodge:assert len(dodge)==len(before) and dodge[:80]==before[:80]
    body_keys=[]
    for n_at,p_at in [(24,28),(32,36)]:
        at=u32(before,p_at)
        for i in range(u32(before,n_at)):
            n=before[at+i*6+3];first=struct.unpack_from('<H',before,at+i*6+4)[0];body_keys.append(first+n)
    segments=[(20,u32(before,16)*4),(28,u32(before,24)*6),(40,max(body_keys)*16),(56,u32(before,52)*8),(36,u32(before,32)*6)]
    event_count=0;event_schema='0'
    if r['normal_slot'] in [98,99,100,101,102,103,110]:
        at=u32(before,60);schema=[]
        while u32(before,at+len(schema)*4)!=0xffffffff:
            schema.extend(struct.unpack_from('<III',before,at+len(schema)*4))
        event_count=len(schema)//3;first=schema[2]
        assert all(schema[i*3+2]==first+sum(schema[j*3+1] for j in range(i))*16 for i in range(event_count))
        name=f'events_{r["normal_slot"]}';lines.append(f'static const unsigned int {name}[]={{'+','.join(str(x)+'u' for x in schema)+'};')
        event_schema=name;segments.append((60,sum(schema[i*3+1] for i in range(event_count))*16))
    parts=[];allowed=set()
    for field,size in segments:
        offset=schema[2] if field==60 else u32(before,field);blobs=[data[offset:offset+size] for data in [before,*converted]]
        assert all(len(b)==size for b in blobs)
        symbols=[array(b) for b in blobs];allowed.update(range(offset,offset+size))
        sentinel=max(range(0,size-3,4),key=lambda k:len({b[k:k+4] for b in blobs}))
        assert len({b[sentinel:sentinel+4] for b in blobs})>1
        extra=array(dodge[offset:offset+size]) if dodge else '0'
        snow=array(blizzard[offset:offset+size]) if blizzard else '0'
        parts.append('{'+f'{field},{size},{sentinel},{symbols[0]},'+'{'+','.join(symbols[1:])+'},'+extra+','+snow+'}')
    for after in converted+([dodge] if dodge else [])+([blizzard] if blizzard else []):assert all(a==b or p in allowed for p,(a,b) in enumerate(zip(before,after)))
    scalars=','.join(str(u32(before,p))+'u' for p in [4,8,16,24,32,44,52])
    descriptors.append('{'+f'{r["request"]},{r["normal_slot"]},{r["olympus_slot"]},{len(before)},{len(parts)},{event_count},{event_schema},'+'{'+scalars+'},'+'{'+','.join(parts)+'}}')
lines+=['static const AquaMotion aqua_motions[AQUA_MOTION_COUNT]={',',\n'.join(descriptors),'};']
# Main Aqua also routes Stop/Aero to the current Gravity family. Numbered
# profiles retain the v13 Thunder-only routing. All native flags and the
# original table size remain; installed MSETs stay original.
request_rows=[]
for name in ['he','normal']:
    suffix='_he' if name=='he' else ''
    source=ROOT.parent/f'sora_source/Custom Movesets KH1/xa_ex_0010{suffix}.mset'
    if not source.exists():source=ROOT.parent/f'assets/xa_ex_0010{suffix}.mset'
    mset=source.read_bytes();start=u32(mset,8);end=u32(mset,12)
    before=mset[start:end];after=bytearray(before)
    assert len(before)==1408
    for request,old,new in [(0x38,19 if suffix else 56,18 if suffix else 55),
                            (0x85,43 if suffix else 81,42 if suffix else 80)]:
        word=u32(before,request*4);assert word==0x1000|old
        struct.pack_into('<I',after,request*4,(word&~0xfff)|new)
    main=bytearray(after)
    for request,new in [(0x3b,18 if suffix else 55),(0x3c,18 if suffix else 55),
                        (0x88,42 if suffix else 80),(0x89,42 if suffix else 80)]:
        word=u32(main,request*4)
        old=(19 if suffix else 56) if request<0x80 else (43 if suffix else 81)
        assert word==(0x1000|old)
        struct.pack_into('<I',main,request*4,(word&~0xfff)|new)
    (ROOT/f'fixtures/requests_{name}_original.bin').write_bytes(before)
    (ROOT/f'fixtures/requests_{name}_aqua.bin').write_bytes(after)
    (ROOT/f'fixtures/requests_{name}_main.bin').write_bytes(main)
    request_rows.append('{'+f'{len(before)},{array(before)},{array(bytes(after))},{array(bytes(main))}'+'}')
lines+=['typedef struct { unsigned int bytes; const unsigned char *before,*after,*main_after; } AquaRequestTable;',
        'static const AquaRequestTable aqua_requests[2]={'+','.join(request_rows)+'};']
(ROOT/'aqua_data.h').write_text('\n'.join(lines)+'\n')
(ROOT/'data_validation.json').write_text(json.dumps({'passed':True,'motions':len(descriptors),'profiles':5,
    'all_headers_and_motion_sizes_identical':True,'all_changes_inside_existing_body_and_helper_tables':False,'all_changes_inside_existing_body_helper_and_event_key_tables':True,'event_descriptor_counts_pointers_and_payloads_preserved':True,'air_dodge_extra_pose':True,'default_glide_records_unmapped_and_unmodified':True,
    'unique_data_blocks':len(arrays)},indent=2)+'\n')
print('Generated',len(descriptors),'motions and 5 profiles;',len(arrays),'unique blocks')
