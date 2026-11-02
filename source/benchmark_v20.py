"""Offline log-shaped binding recovery comparison; measurements are not game FPS."""
import gc,json,time
from pathlib import Path
import test_runtime as t
here=Path(__file__).resolve().parent
reports={}
for version in [19,20]:
 t.ROOT=here if version==20 else here.parent.parent/'KH1FM_Aqua_Animation_Test_v19/source'
 h=t.Host(air=True);h.arm_air();t.w32(h.actor+0x164,2);t.w32(h.actor+0x70,0)
 t.w32(h.actor+0x374,0);h.frame();t.w32(h.actor+0x374,1)
 before=h.snapshot();q=t.bridge.bridge_queries();start=time.perf_counter()
 for _ in range(120):h.frame()
 elapsed=time.perf_counter()-start
 reports[str(version)]={'moving_frames':120,'memory_queries':t.bridge.bridge_queries()-q,
    'mock_elapsed_seconds':elapsed,'payloads_unchanged':h.snapshot()==before,
    'switch_pending': 'SWITCH PENDING' in t.bridge.bridge_log().decode(),
    'read_only_binding_recovery':'BINDING RECOVERED' in t.bridge.bridge_log().decode()}
 del h;gc.collect()
assert reports['20']['payloads_unchanged'] and not reports['20']['switch_pending']
assert reports['20']['memory_queries']<reports['19']['memory_queries']*.2
out={'version':20,'passed':True,'game_runtime_tested':False,'scenario':'temporary actor residency loss, then 120 walking frames, selected main Aqua',
 'versions':reports,'note':'Actual PE DLLs executed in Linux Win64 ABI host; timings include mocked memory calls, and do not measure game FPS or prove the original slowdown cause.'}
(here/'performance_validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
