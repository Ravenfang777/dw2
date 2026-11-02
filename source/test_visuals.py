"""Independent checks of serialized V13 base, Glide phases, aerial dodge and revised Test 4 profiles."""
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
all_converted={(0,s):m for s,m in converted.items()}
for profile in range(1,5):
    data=json.loads((ROOT/f'sets/p{profile}/curve_validation.json').read_text())
    for row in data['motions']:
        all_converted[(profile,row['normal_slot'])]=parse_motion((ROOT/f"sets/p{profile}/fixtures/aqua_{row['fixture_stem']}.bin").read_bytes())

dodge_report=json.loads((ROOT/'dodge/curve_validation.json').read_text())
assert len(dodge_report['motions'])==1 and dodge_report['motions'][0]['donor']=='504'
all_converted[(5,10)]=parse_motion((ROOT/'dodge/fixtures/aqua_s010.bin').read_bytes())
glide_stop_report=json.loads((ROOT/'glide_stop/curve_validation.json').read_text())
all_converted[(6,10)]=parse_motion((ROOT/'glide_stop/fixtures/aqua_s010.bin').read_bytes())

@lru_cache(maxsize=1)
def clearance_samples():
    data=np.load(ROOT/'fixtures/v8_arm_reference.npz');actual=[]
    for slot in data['slots']:
        m=converted[int(slot)]
        actual.append(np.array([pose(model,m,float(f))[data['joints'],:3,3] for f in np.linspace(0,m.frames-1,41)]))
    return data['positions'],np.array(actual)

def capsule_overlap(points,pair,radius):
    a=points[:,:,0,:];d=points[:,:,1,:]-a;total=0.
    for i in pair:
        p=points[:,:,i,:];t=np.clip(np.sum((p-a)*d,axis=2)/np.sum(d*d,axis=2),0,1)
        gap=np.linalg.norm(p-(a+d*t[:,:,None]),axis=2);total+=float(np.maximum(0,radius-gap).sum())
    return total

class VisualTests(unittest.TestCase):
    def test_limb_clearance_keeps_wrist_and_ankle_displacements_bounded(self):
        before,after=clearance_samples()
        # The frozen V8 positions only compare the same source actions; V10's
        # newly assigned casts, fall, finisher and air combo have different poses.
        slots=np.load(ROOT/'fixtures/v8_arm_reference.npz')['slots']
        same_source=~np.isin(slots,[10,54,55,56,57,58,59,79,80,81,82,99,100,101,102,103,104])
        before=before[same_source];after=after[same_source]
        self.assertLess(float(np.max(np.linalg.norm(after[:,:,[4,7],:]-before[:,:,[4,7],:],axis=3))),23.)
        self.assertLess(float(np.max(np.linalg.norm(after[:,:,[8,9],:]-before[:,:,[8,9],:],axis=3))),2.)
    def test_distal_forearm_helpers_keep_bind_angles_instead_of_bending_with_the_hand(self):
        ids=list(range(95,100))+list(range(200,205));wanted=Rotation.from_euler('xyz',model.local[ids,3:6]).as_matrix()
        for key,m in all_converted.items():
            for f in np.linspace(0,m.frames-1,7):
                local=model.local.copy()
                for b,k,v in m.constants:local[b,k-1]=v
                apply(m.channels,local,float(f))
                actual=Rotation.from_euler('xyz',local[ids,3:6]).as_matrix()
                np.testing.assert_allclose(actual,wanted,atol=1e-6,rtol=0,err_msg=(key,f))
    def test_hair_chains_keep_model_bind_rotations_through_all_actions(self):
        expected=Rotation.from_euler('xyz',model.local[155:194,3:6]).as_matrix()
        for slot,m in all_converted.items():
            for f in np.linspace(0,m.frames-1,7):
                local=model.local.copy()
                for b,k,v in m.constants:local[b,k-1]=v
                apply(m.channels,local,float(f))
                actual=Rotation.from_euler('xyz',local[155:194,3:6]).as_matrix()
                np.testing.assert_allclose(actual,expected,atol=1e-6,rtol=0,err_msg=(slot,f))
    def test_every_motion_keeps_original_header_length_and_helper_hierarchy(self):
        for (profile,slot),m in all_converted.items():
            o=original[slot];self.assertEqual(len(m.raw),len(o.raw));self.assertEqual(m.raw[:80],o.raw[:80]);self.assertEqual(m.helper_parents,o.helper_parents)
            np.testing.assert_array_equal(m.helper_local,o.helper_local)
    def test_serialized_poses_keep_bind_lengths_and_scale_without_anatomical_translation_warps(self):
        indices=[i for i in range(1,293) if i!=280]
        for slot,m in all_converted.items():
            for f in np.linspace(0,m.frames-1,9):
                local=model.local.copy()
                for b,k,v in m.constants:local[b,k-1]=v
                apply(m.channels,local,float(f))
                np.testing.assert_allclose(local[indices,6:9],model.local[indices,6:9],atol=1e-6,rtol=0)
                np.testing.assert_allclose(local[:,:3],model.local[:,:3],atol=1e-6,rtol=0)
    def test_skin_bases_have_no_extra_scale_or_shear(self):
        worst=0.
        for slot,m in all_converted.items():
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
    def test_fire_casts_continue_across_release_and_recovery(self):
        for release,recovery in [(54,57),(79,82)]:
            a=converted[release];b=converted[recovery]
            pa=pose(model,a,float(a.frames-1));pb=pose(model,b,0)
            pa[:,:3,3]-=helper_pose(a,float(a.frames-1))[-1,:3,3]
            pb[:,:3,3]-=helper_pose(b,0)[-1,:3,3]
            np.testing.assert_allclose(pa,pb,atol=.003,rtol=0,err_msg=(release,recovery))
    def test_requested_action_clips_and_test_4_combos_match_serialized_reports(self):
        actions={99:'218',100:'218',101:'366',102:'351',103:'353',104:'393',58:'395',59:'395',10:'506',54:'316',57:'316',55:'317',56:'318',79:'391',82:'391',80:'390',81:'427'}
        for slot,clip in actions.items():self.assertEqual(by_slot[slot]['donor'],clip)
        self.assertEqual(by_slot[54]['source_range'][1],by_slot[57]['source_range'][0])
        self.assertEqual(by_slot[79]['source_range'][1],by_slot[82]['source_range'][0])
        wanted=[(['316','317','318'],['391','390','427']),
                (['315','371','366'],['365','218','332']),
                (['393','411','352'],['616','407','351']),
                (['510','511','512'],['504','514','399'])]
        for profile,(ground,air) in enumerate(wanted,1):
            rows=json.loads((ROOT/f'sets/p{profile}/curve_validation.json').read_text())['motions']
            actual={r['normal_slot']:r['donor'] for r in rows}
            self.assertEqual(actual,dict(zip(range(98,105),[ground[0],ground[1],ground[1],ground[2],*air])))
    def test_item_007_395_uses_the_requested_shared_payload_in_both_native_item_actions(self):
        for slot in [58,59]:
            row=by_slot[slot]
            self.assertEqual(row['donor'],'395');self.assertEqual(row['source_aliases'],'007 / 395')
            self.assertEqual(row['source_sha256'],'bb421875fd62baf56d5e0b0f19fadecca5037593ad2d257db8f66cac92ee4b96')
    def test_glide_opening_reaches_a_static_middle_pose_and_matches_the_closing_boundary(self):
        stop=all_converted[(6,10)];end=pose(model,stop,0)
        end[:,:3,3]-=helper_pose(stop,0)[-1,:3,3]
        for slot in range(75,79):
            row=by_slot[slot];m=converted[slot]
            self.assertEqual(row['donor'],'350');self.assertEqual(row['source_range'],[0,20])
            self.assertEqual(row['native_hold_frame'],40)
            for f in [40.,45.,float(m.frames-1)]:
                actual=pose(model,m,f);actual[:,:3,3]-=helper_pose(m,f)[-1,:3,3]
                np.testing.assert_allclose(actual,end,atol=.004,rtol=0,err_msg=(slot,f))
        self.assertEqual(glide_stop_report['motions'][0]['source_range'],[20,40])
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
        for (profile,slot),m in all_converted.items():
            for f in np.linspace(0,m.frames-1,11):
                np.testing.assert_allclose(helper_pose(m,float(f))[-1],helper_pose(original[slot],float(f))[-1],atol=1e-7,rtol=0)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(VisualTests))
    (ROOT/'visual_validation.json').write_text(json.dumps({'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'mesh_or_game_rendered':False},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
