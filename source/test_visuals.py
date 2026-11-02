"""Independent checks of serialized V14 main casting and combo edits, retained Test4 profiles, Glide and dodge."""
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

blizzard_report=json.loads((ROOT/'blizzard/curve_validation.json').read_text())
for row in blizzard_report['motions']:
    all_converted[(7,row['normal_slot'])]=parse_motion((ROOT/f"blizzard/fixtures/aqua_{row['fixture_stem']}.bin").read_bytes())

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
    def test_second_swing_reaches_the_end_before_a_useful_chain_window(self):
        for slot,finish in [(99,32),(100,44)]:
            m=converted[slot];last=pose(model,m,float(m.frames-1));last[:,:3,3]-=helper_pose(m,m.frames-1)[-1,:3,3]
            for f in [float(finish),float(finish+4),float(m.frames-1)]:
                at=pose(model,m,f);at[:,:3,3]-=helper_pose(m,f)[-1,:3,3]
                np.testing.assert_allclose(at,last,atol=.005,rtol=0)
            earlier=pose(model,m,float(finish-12))
            self.assertGreater(float(np.linalg.norm(earlier[100,:3,3]-pose(model,m,finish)[100,:3,3])),2.)
    def test_running_head_is_lifted_while_the_torso_and_bind_hair_are_preserved(self):
        from aqua_retarget_math import rotation
        for slot in [5,6,7]:
            # The reference was the shipped v15 run. Freeze those source curves
            # for a comparison which does not repeat the correction formula.
            old=parse_motion((ROOT/f'fixtures/v15_run_s{slot:03}.bin').read_bytes())
            for f in np.linspace(0,converted[slot].frames-1,9):
                a=pose(model,old,float(f));b=pose(model,converted[slot],float(f))
                fa=rotation(a[151])@rotation(model.bind[151]).T@np.array([0.,0.,1.])
                fb=rotation(b[151])@rotation(model.bind[151]).T@np.array([0.,0.,1.])
                self.assertGreater(fb[1]-fa[1],.17)
                np.testing.assert_allclose(a[:144],b[:144],atol=.004,rtol=0)
    def test_blizzard_variants_preserve_every_native_spell_event_and_allocation(self):
        for row in blizzard_report['motions']:
            slot=row['normal_slot'];m=all_converted[(7,slot)];native=original[slot]
            import struct
            at=struct.unpack_from('<I',native.raw,60)[0]
            self.assertEqual(m.raw[at:],native.raw[at:])
            self.assertEqual(m.raw[:80],native.raw[:80]);self.assertEqual(len(m.raw),len(native.raw))
            self.assertEqual(row['donor'],'391' if slot==55 else '316')
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
        for profile in range(5):
          for release,recovery in [(54,57),(79,82)]:
            a=all_converted[(profile,release)];b=all_converted[(profile,recovery)]
            pa=pose(model,a,float(a.frames-1));pb=pose(model,b,0)
            pa[:,:3,3]-=helper_pose(a,float(a.frames-1))[-1,:3,3]
            pb[:,:3,3]-=helper_pose(b,0)[-1,:3,3]
            np.testing.assert_allclose(pa,pb,atol=.003,rtol=0,err_msg=(release,recovery))
    def test_requested_action_clips_and_test_4_combos_match_serialized_reports(self):
        actions={99:'365',100:'365',101:'366',102:'351',103:'352',104:'393',58:'395',59:'395',10:'506',54:'391',57:'391',55:'317',56:'427',79:'316',82:'316',80:'390',81:'318'}
        for slot,clip in actions.items():self.assertEqual(by_slot[slot]['donor'],clip)
        self.assertEqual(by_slot[54]['source_range'][1],by_slot[57]['source_range'][0])
        self.assertEqual(by_slot[79]['source_range'][1],by_slot[82]['source_range'][0])
        wanted=[(['316','317','318'],['391','390','427']),
                (['315','371','366'],['365','218','332']),
                (['393','411','352'],['616','407','351']),
                (['510','511','512'],['504','514','399'])]
        for profile,(ground,air) in enumerate(wanted,1):
            rows=json.loads((ROOT/f'sets/p{profile}/curve_validation.json').read_text())['motions']
            actual={r['normal_slot']:r['donor'] for r in rows if 98<=r['normal_slot']<=104}
            self.assertEqual(actual,dict(zip(range(98,105),[ground[0],ground[1],ground[1],ground[2],*air])))
    def test_second_ground_event_edits_change_only_existing_time_values(self):
        import struct
        from aqua_event_timing_v16 import tracks
        for slot,contact,finish in [(98,12.,22.),(99,24.,32.),(100,36.,44.)]:
            before=original[slot].raw;after=converted[slot].raw
            self.assertEqual(tracks(before),tracks(after))
            allowed=set();active=[]
            for track,kind,count,keys in tracks(before):
                times=[]
                for i in range(count):
                    at=keys+i*16;times.append(struct.unpack_from('<f',after,at)[0]);allowed.update(range(at,at+4))
                    self.assertEqual(before[at+4:at+16],after[at+4:at+16])
                    if kind==4 and struct.unpack_from('<H',after,at+6)[0]==0x16:active.append(times[-1])
                self.assertEqual(times,sorted(times))
                if kind==5:self.assertEqual(times,[finish,40. if slot==98 else float(original[slot].frames)])
                if kind in [6,7]:self.assertEqual(before[keys:keys+count*16],after[keys:keys+count*16])
            self.assertEqual(min(active),contact)
            start=struct.unpack_from('<I',before,60)[0]
            self.assertTrue(all(before[i]==after[i] or i in allowed for i in range(start,len(before))))
    def test_numbered_profiles_retain_v13_fire_and_cure_poses(self):
        expected={54:('316',[0,20]),57:('316',[20,30]),56:('318',None),
                  79:('391',[0,31]),82:('391',[31,48]),81:('427',None)}
        for profile in range(1,5):
            data=json.loads((ROOT/f'sets/p{profile}/curve_validation.json').read_text())
            rows={r['normal_slot']:r for r in data['motions']}
            for slot,(clip,cut) in expected.items():
                self.assertEqual((rows[slot]['donor'],rows[slot]['source_range']),(clip,cut))
    def test_both_main_second_ground_variants_and_air_second_use_the_new_requested_clips(self):
        for slot,clip in [(99,'365'),(100,'365'),(103,'352')]:
            self.assertEqual(by_slot[slot]['donor'],clip);self.assertIsNone(by_slot[slot]['source_range'])
        self.assertEqual(by_slot[99]['source_sha256'],by_slot[100]['source_sha256'])
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
