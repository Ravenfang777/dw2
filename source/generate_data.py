"""Generate reversible Terra body tables for main and ten animation test profiles."""
from pathlib import Path
import hashlib,json,struct
ROOT=Path(__file__).resolve().parent
report=json.loads((ROOT/'curve_validation.json').read_text());assert report['passed'] and len(report['motions'])==37
sets=[json.loads((ROOT/f'sets/p{i}/curve_validation.json').read_text()) for i in range(1,11)]
assert all(x['passed'] and len(x['motions'])==7 for x in sets)
lookup=[{r['normal_slot']:r for r in s['motions']} for s in sets]
shared={r['normal_slot']:r for r in json.loads((ROOT/'sets/shared_v2/curve_validation.json').read_text())['motions']}
overlays=json.loads((ROOT/'overlays/curve_validation.json').read_text());assert overlays['passed'] and len(overlays['motions'])==3
overlay_lookup={r['normal_slot']:r for r in overlays['motions']}
u32=lambda d,p:struct.unpack_from('<I',d,p)[0]
lines=['/* Generated original / eleven Terra profile body payloads. Native event bytes are never included as write destinations. */',
 '#define TERRA_PROFILE_COUNT 11',f'#define TERRA_MOTION_COUNT {len(report["motions"])}','#define TERRA_PART_COUNT 5',
 f'#define TERRA_ANCHOR_INDEX {next(i for i,r in enumerate(report["motions"]) if r["normal_slot"]==98)}',
 'typedef struct { unsigned int field,size,sentinel; const unsigned char *before,*after[TERRA_PROFILE_COUNT],*variant; } TerraPart;',
 'typedef struct { unsigned int request,normal_slot,olympus_slot,raw_bytes,part_count,event_count; const unsigned int *event_schema; unsigned int scalars[7]; TerraPart parts[TERRA_PART_COUNT]; } TerraMotion;',
 'static const unsigned int terra_scalar_fields[7]={4,8,16,24,32,44,52};']
arrays={}
def array(data):
 h=hashlib.sha256(data).hexdigest()
 if h in arrays:return arrays[h]
 name=f'payload_{len(arrays)}';arrays[h]=name;lines.append(f'static const unsigned char {name}[{len(data)}] = {{')
 for i in range(0,len(data),24):lines.append(','.join(str(v) for v in data[i:i+24])+',')
 lines.append('};');return name
records=[]
for r in report['motions']:
 stem=r['fixture_stem'];before=(ROOT/f'fixtures/original_{stem}.bin').read_bytes();converted=[(ROOT/f'fixtures/terra_{stem}.bin').read_bytes()]
 for i,table in enumerate(lookup,1):
  if r['normal_slot'] in table:
   sr=table[r['normal_slot']];folder=ROOT/f'sets/p{i}/fixtures';assert (folder/f'original_{sr["fixture_stem"]}.bin').read_bytes()==before
   converted.append((folder/f'terra_{sr["fixture_stem"]}.bin').read_bytes())
  elif r['normal_slot'] in shared:
   sr=shared[r['normal_slot']];folder=ROOT/'sets/shared_v2/fixtures';assert (folder/f'original_{sr["fixture_stem"]}.bin').read_bytes()==before
   converted.append((folder/f'terra_{sr["fixture_stem"]}.bin').read_bytes())
  else:converted.append(converted[0])
 assert len(converted)==11 and all(len(c)==len(before) and c[:80]==before[:80] for c in converted)
 variant=(ROOT/f'overlays/fixtures/terra_{stem}.bin').read_bytes() if r['normal_slot'] in overlay_lookup else None
 if variant:assert len(variant)==len(before) and variant[:80]==before[:80]
 ends=[]
 for n_at,p_at in [(24,28),(32,36)]:
  at=u32(before,p_at)
  for j in range(u32(before,n_at)):ends.append(struct.unpack_from('<H',before,at+j*6+4)[0]+before[at+j*6+3])
 segments=[(20,u32(before,16)*4),(28,u32(before,24)*6),(40,max(ends)*16),(56,u32(before,52)*8),(36,u32(before,32)*6)]
 parts=[];allowed=set()
 for field,size in segments:
  offset=u32(before,field);blobs=[b[offset:offset+size] for b in [before,*converted]+([variant] if variant else [])];assert all(len(b)==size for b in blobs)
  symbols=[array(b) for b in blobs]
  sentinel=max(range(0,size-3,4),key=lambda k:len({b[k:k+4] for b in blobs}))
  # Some native helper descriptors can already match the mapped output; shape
  # and every byte are still admitted, with this checked pointer sentinel.
  parts.append('{'+f'{field},{size},{sentinel},{symbols[0]},'+'{'+','.join(symbols[1:12])+'},'+(symbols[12] if variant else '0')+'}');allowed.update(range(offset,offset+size))
 for after in converted+([variant] if variant else []):assert all(a==b or p in allowed for p,(a,b) in enumerate(zip(before,after)))
 scalars=','.join(str(u32(before,p))+'u' for p in [4,8,16,24,32,44,52])
 records.append('{'+f'{r["request"]},{r["normal_slot"]},{r["olympus_slot"]},{len(before)},{len(parts)},0,0,'+'{'+scalars+'},'+'{'+','.join(parts)+'}}')
lines+=['static const TerraMotion terra_motions[TERRA_MOTION_COUNT]={',',\n'.join(records),'};']
(ROOT/'terra_data.h').write_text('\n'.join(lines)+'\n')
(ROOT/'data_validation.json').write_text(json.dumps({'passed':True,'motions':len(records),'profiles':11,'main_only_body_variants':3,'numbered_common_payloads_retained_from_v3':len(shared),'headers_counts_and_capacities_unchanged':True,'native_event_and_request_bytes_unchanged':True,'all_changes_inside_existing_body_helper_tables':True,'unique_data_blocks':len(arrays)},indent=2)+'\n')
print('Generated',len(records),'mapped motions and11 profiles;',len(arrays),'unique blocks')
