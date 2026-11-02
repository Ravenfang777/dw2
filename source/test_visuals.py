"""Independent checks of serialized V8 geometry constraints and transitions."""
from pathlib import Path
import json,sys,unittest
import numpy as np
from scipy.spatial.transform import Rotation
from functools import lru_cache
ROOT=Path(__file__).resolve().parent
TOOLS=ROOT/'retargeting/tools'
if not TOOLS.exists():TOOLS=ROOT.parent/'tools'
sys.path.insert(0,str(TOOLS))
from kh1_motion_source import read_model,parse_motion,pose,helper_pose,apply
MODEL=ROOT/'retargeting/sora_source/Custom Movesets KH1/xa_ex_0010.mdls'
if not MODEL.exists():MODEL=ROOT.parent/'sora_source/Custom Movesets KH1/xa_ex_0010.mdls'
model=read_model(MODEL.read_bytes());inverse_bind=np.linalg.inv(model.bind)
report=json.loads((ROOT/'curve_validation.json').read_text())
records=report['motions'];by_slot={r['normal_slot']:r for r in records}
original={r['normal_slot']:parse_motion((ROOT/f"fixtures/original_{r['fixture_stem']}.bin").read_bytes()) for r in records}
converted={r['normal_slot']:parse_motion((ROOT/f"fixtures/aqua_{r['fixture_stem']}.bin").read_bytes()) for r in records}

@lru_cache(maxsize=1)
def clearance_samples():
    data=np.load(ROOT/'fixtures/v7_clearance_reference.npz');actual=[]
    for slot in data['slots']:
        m=converted[int(slot)]
        actual.append(np.array([pose(model,m,float(f))[data['joints'],:3,3] for f in np.linspace(0,m.frames-1,21)]))
    return data['positions'],np.array(actual)

def capsule_overlap(points,pair,radius):
    a=points[:,:,0,:];d=points[:,:,1,:]-a;total=0.
    for i in pair:
        p=points[:,:,i,:];t=np.clip(np.sum((p-a)*d,axis=2)/np.sum(d*d,axis=2),0,1)
        gap=np.linalg.norm(p-(a+d*t[:,:,None]),axis=2);total+=float(np.maximum(0,radius-gap).sum())
    return total

class VisualTests(unittest.TestCase):
    def test_joint_capsule_overlap_reduces_against_frozen_v7_reference(self):
        before,after=clearance_samples()
        for pair,radius in [([2,3],17.),([4,5],16.)]:
            self.assertLess(capsule_overlap(after,pair,radius),capsule_overlap(before,pair,radius))
    def test_limb_clearance_keeps_wrist_and_ankle_displacements_bounded(self):
        before,after=clearance_samples()
        self.assertLess(float(np.max(np.linalg.norm(after[:,:,[2,3],:]-before[:,:,[2,3],:],axis=3))),5.)
        self.assertLess(float(np.max(np.linalg.norm(after[:,:,[6,7],:]-before[:,:,[6,7],:],axis=3))),2.)
    def test_hair_chains_keep_model_bind_rotations_through_all_actions(self):
        expected=Rotation.from_euler('xyz',model.local[155:194,3:6]).as_matrix()
        for slot,m in converted.items():
            for f in np.linspace(0,m.frames-1,7):
                local=model.local.copy()
                for b,k,v in m.constants:local[b,k-1]=v
                apply(m.channels,local,float(f))
                actual=Rotation.from_euler('xyz',local[155:194,3:6]).as_matrix()
                np.testing.assert_allclose(actual,expected,atol=1e-6,rtol=0,err_msg=(slot,f))
    def test_every_motion_keeps_original_header_length_and_helper_hierarchy(self):
        for slot,m in converted.items():
            o=original[slot];self.assertEqual(len(m.raw),len(o.raw));self.assertEqual(m.raw[:80],o.raw[:80]);self.assertEqual(m.helper_parents,o.helper_parents)
            np.testing.assert_array_equal(m.helper_local,o.helper_local)
    def test_serialized_poses_keep_bind_lengths_and_scale_without_anatomical_translation_warps(self):
        indices=[i for i in range(1,293) if i!=280]
        for slot,m in converted.items():
            for f in np.linspace(0,m.frames-1,9):
                local=model.local.copy()
                for b,k,v in m.constants:local[b,k-1]=v
                apply(m.channels,local,float(f))
                np.testing.assert_allclose(local[indices,6:9],model.local[indices,6:9],atol=1e-6,rtol=0)
                np.testing.assert_allclose(local[:,:3],model.local[:,:3],atol=1e-6,rtol=0)
    def test_skin_bases_have_no_extra_scale_or_shear(self):
        worst=0.
        for slot,m in converted.items():
            for f in np.linspace(0,m.frames-1,9):
                skin=pose(model,m,float(f))@inverse_bind
                singular=np.linalg.svd(skin[:,:3,:3],compute_uv=False)
                worst=max(worst,float(np.max(np.abs(singular-1))))
        self.assertLess(worst,2e-5)
    def test_all_looped_body_poses_close_after_removing_native_actor_travel(self):
        for r in records:
            if not r['loop']:continue
            m=converted[r['normal_slot']];a=pose(model,m,0);b=pose(model,m,float(m.frames-1))
            a[:,:3,3]-=helper_pose(m,0)[-1,:3,3];b[:,:3,3]-=helper_pose(m,float(m.frames-1))[-1,:3,3]
            np.testing.assert_allclose(a,b,atol=.003,rtol=0,err_msg=r['action'])
    def test_jump_and_high_jump_continue_across_the_native_rise_boundaries(self):
        for takeoff,rise in [(8,9),(12,13)]:
            a=converted[takeoff];b=converted[rise]
            pa=pose(model,a,float(a.frames-1));pb=pose(model,b,0)
            pa[:,:3,3]-=helper_pose(a,float(a.frames-1))[-1,:3,3];pb[:,:3,3]-=helper_pose(b,0)[-1,:3,3]
            np.testing.assert_allclose(pa,pb,atol=.003,rtol=0)
    def test_supported_idle_stances_allow_room_for_soras_boots(self):
        minimum=float(np.linalg.norm(model.bind[43,:3,3]-model.bind[17,:3,3])*1.35)
        for slot in [0,1]:
            p=pose(model,converted[slot],0);lateral=p[43,:3,3]-p[17,:3,3];lateral[1]=0;lateral/=np.linalg.norm(lateral)
            gap=float((p[45,:3,3]-p[19,:3,3])@lateral)
            self.assertGreaterEqual(gap,minimum-1,slot)
    def test_ledge_uses_aquas_raised_left_hand_at_the_native_grip_point(self):
        for slot in [14,15]:
            m=converted[slot]
            for f in np.linspace(0,m.frames-1,11):
                actual=pose(model,m,float(f));native=pose(model,original[slot],float(f))
                error=float(np.linalg.norm(actual[206,:3,3]-native[101,:3,3]))
                self.assertLess(error,3.,(slot,float(f),error))
    def test_travel_helper_is_unchanged_through_every_fitted_motion(self):
        for slot,m in converted.items():
            for f in np.linspace(0,m.frames-1,11):
                np.testing.assert_allclose(helper_pose(m,float(f))[-1],helper_pose(original[slot],float(f))[-1],atol=1e-7,rtol=0)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(VisualTests))
    (ROOT/'visual_validation.json').write_text(json.dumps({'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'mesh_or_game_rendered':False},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
