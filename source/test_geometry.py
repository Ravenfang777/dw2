"""Verify serialized Terra-to-Sora anatomy and unchanged native motion structure."""
from pathlib import Path
import sys,json,hashlib,unittest,warnings
import numpy as np
from scipy.spatial.transform import Rotation
from functools import lru_cache
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'tools'))
from bbs_source_inspector import read_pmo_skeleton,read_arc
from kh1_motion_source import read_model,parse_motion,pose,helper_pose,apply,u32
from terra_retarget import RetargetV7
model=read_model((ROOT/'xa_ex_0010.mdls').read_bytes());source=read_pmo_skeleton((ROOT/'terra_source/p03ex00.pmo').read_bytes())
reports=[json.loads((ROOT/('curve_validation.json' if p==0 else f'sets/p{p}/curve_validation.json')).read_text()) for p in range(11)];records=[]
for profile,report in enumerate(reports):
 for row in report['motions']:
  folder=ROOT if profile==0 else ROOT/f'sets/p{profile}'
  before=parse_motion((folder/f"fixtures/original_{row['fixture_stem']}.bin").read_bytes());after=parse_motion((folder/f"fixtures/terra_{row['fixture_stem']}.bin").read_bytes())
  records.append((profile,row,before,after))
@lru_cache(maxsize=1)
def samples():
 data=[]
 for profile,row,before,after in records:
  for frame in np.linspace(0,after.frames-1,7):
   local=model.local.copy()
   for bone,kind,value in after.constants:local[bone,kind-1]=value
   apply(after.channels,local,float(frame));data.append((profile,row,before,after,float(frame),local,pose(model,after,float(frame))))
 return data
class GeometryTests(unittest.TestCase):
 def test_terra_original_named_anatomy_maps_to_sora(self):
  self.assertEqual(source['bone_count'],51)
  with warnings.catch_warnings():warnings.simplefilter('ignore');rig=RetargetV7(source,model,pose(model,records[0][2],0))
  self.assertEqual(rig.mapping[150],28);self.assertNotIn(151,rig.mapping)
  self.assertEqual(rig.mapping[17],3);self.assertEqual(rig.mapping[43],13)
  self.assertEqual(rig.mapping[100],38);self.assertEqual(rig.mapping[205],45);self.assertEqual(len(model.parents),293)
 def test_skull150_is_skinned_and_hair151_is_helper(self):
  raw=(ROOT/'xa_ex_0010.mdls').read_bytes();mobj=u32(raw,4);header=mobj+u32(raw,mobj+32);table=header+u32(raw,header+4)
  self.assertEqual((u32(raw,table+150*48+44)>>30)&3,1);self.assertEqual((u32(raw,table+151*48+44)>>30)&3,0)
 def test_embedded_models_match_the_original_terra_skeleton(self):
  checked=0
  for name,raw in read_arc((ROOT/'terra_source/p03base.arc').read_bytes())[0]:
   if raw.startswith(b'PMO\0'):
    embedded=read_pmo_skeleton(raw);self.assertEqual(embedded['bone_count'],51)
    for a,b in zip(embedded['bones'],source['bones']):
     self.assertEqual((a['index'],a['parent'],a['name']),(b['index'],b['parent'],b['name']))
     np.testing.assert_allclose(a['transform'],b['transform'],atol=1e-6,rtol=1e-6)
     np.testing.assert_allclose(a['inverse_transform'],b['inverse_transform'],atol=1e-6,rtol=1e-6)
    checked+=1
  self.assertEqual(checked,2)
 def test_all48_original_source_hashes_match(self):
  rows=json.loads((ROOT/'terra_source/Source_Manifest.json').read_text(encoding='utf-8-sig'));self.assertEqual(len(rows),48)
  for row in rows:
   p=ROOT/'terra_source'/Path(row['Path'].replace('\\','/')).name
   self.assertEqual(p.stat().st_size,row['Bytes']);self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest().upper(),row['SHA256'])
 def test_main_and_ten_profiles_have_exact_record_counts(self):
  self.assertEqual([len(r['motions']) for r in reports],[37]+[7]*10);self.assertEqual(len(records),107);self.assertTrue(all(r['passed'] for r in reports))
 def test_native_headers_allocations_and_helpers_unchanged(self):
  for profile,row,before,after in records:
   self.assertEqual(len(before.raw),len(after.raw));self.assertEqual(before.raw[:80],after.raw[:80]);self.assertEqual(before.helper_parents,after.helper_parents)
   np.testing.assert_array_equal(before.helper_local,after.helper_local);self.assertTrue(np.all(after.flags==0))
 def test_bone_offsets_lengths_and_scales_never_stretch(self):
  indexes=[i for i in range(1,293) if i!=280]
  for _,_,_,_,_,local,_ in samples():
   np.testing.assert_allclose(local[:,:3],model.local[:,:3],atol=1e-6,rtol=0);np.testing.assert_allclose(local[indexes,6:9],model.local[indexes,6:9],atol=1e-6,rtol=0)
 def test_hair_shape_uses_native_bind_rotations(self):
  wanted=Rotation.from_euler('xyz',model.local[151:194,3:6]).as_matrix()
  for _,_,_,_,_,local,_ in samples():np.testing.assert_allclose(Rotation.from_euler('xyz',local[151:194,3:6]).as_matrix(),wanted,atol=1e-6,rtol=0)
 def test_fractional_poses_are_finite_and_bounded(self):
  for _,_,_,_,_,_,world in samples():self.assertTrue(np.isfinite(world).all());self.assertLess(float(np.max(np.abs(world[:,:3,3]))),2000.)
 def test_native_travel_helpers_stay_exact(self):
  for profile,row,before,after in records:
   for frame in np.linspace(0,after.frames-1,9):np.testing.assert_array_equal(helper_pose(after,float(frame))[-1],helper_pose(before,float(frame))[-1])
 def test_native_event_descriptors_keys_and_payloads_unchanged(self):
  for profile,row,before,after in records:
   at=u32(before.raw,60);self.assertEqual(before.raw[at:],after.raw[at:])
 def test_looping_body_poses_close_without_resetting_travel(self):
  checked=0
  for profile,row,before,after in records:
   if row['loop']:
    first=pose(model,after,0);last=pose(model,after,float(after.frames-1));first[:,:3,3]-=helper_pose(after,0)[-1,:3,3];last[:,:3,3]-=helper_pose(after,float(after.frames-1))[-1,:3,3]
    np.testing.assert_allclose(first,last,atol=.005,rtol=0);checked+=1
  self.assertGreaterEqual(checked,8)
 def test_fit_errors_obey_original_quality_limits(self):
  for _,r,_,_ in records:
   self.assertLessEqual(r['max_pose_position_error'],5.);self.assertLessEqual(r['max_pose_basis_error'],.12);self.assertLessEqual(r['max_segment_length_error'],.01);self.assertEqual(r['root_helper_error'],0.)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(GeometryTests))
 (ROOT/'geometry_validation.json').write_text(json.dumps({'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'serialized_terra_records':len(records),'actual_game_tested':False},indent=2)+'\n')
 raise SystemExit(0 if result.wasSuccessful() else 1)
