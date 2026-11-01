"""Asset-free regression checks for the helper-based native serializer."""
import struct
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
from scipy.spatial.transform import Rotation

import build_aqua_motion_test as builder
from bbs_source_inspector import Animation,Channel
from kh1_motion_source import Model,parse_motion,pose,helper_pose


def fixture():
    data=bytearray(208)
    for at,value in {4:2,16:1,20:80,32:1,36:164,40:176,44:2,48:84}.items():
        struct.pack_into('<I',data,at,value)
    struct.pack_into('<f',data,8,60.)
    for i in range(2):
        struct.pack_into('<3fi3f3f',data,84+i*40,1.,1.,1.,-1 if i==0 else 0,0.,0.,0.,0.,0.,0.)
    struct.pack_into('<HBBH',data,164,1,9,2,0)
    for i in range(2):
        struct.pack_into('<ifff',data,176+i*16,(i*256<<8)|1,float(i)*8.,0.,0.)
    return parse_motion(bytes(data))


def convert(lo=0.,hi=1.):
    original=fixture()
    source_local=np.zeros((2,9));source_local[:,6:9]=1.
    source_local[1,3:6]=[.1,.3,-.2]
    source_rotation=np.stack([np.eye(3),Rotation.from_euler('xyz',source_local[1,3:6]).as_matrix()])
    target_rotation=Rotation.from_euler('xyz',[.2,-.4,.1]).as_matrix()[None]
    rest=np.array([[1.,1.,1.,.2,-.4,.1,0.,2.,0.]])
    calibration=SimpleNamespace(
        source={'bones':[{'parent':None},{'parent':0}]},source_components=source_local,
        source_rotation=source_rotation,target_rotation=target_rotation,rest=rest)
    channels={(1,3):Channel([0,1],[.1,.7]),(1,4):Channel([0,1],[.3,1.0]),
              (1,5):Channel([0,1],[-.2,.5])}
    animation=Animation(0,'test',0,30,0,0,1,2,2,channels,0)
    body=np.repeat(rest[None],3,axis=0);times=np.array([0.,.5,1.])
    with patch.dict(builder.MAPPING,{0:1},clear=True):
        data,metrics=builder.compile_helper_motion(original,calibration,animation,lo,hi,times,body)
    model=Model([-1],rest,np.eye(4)[None])
    return original,parse_motion(data),model,calibration,animation,metrics


class HelperSerializationTests(unittest.TestCase):
    def test_rotations_match_independent_donor_basis_at_fractional_frames(self):
        _,motion,model,cal,animation,_=convert()
        for frame in [.125,.25,.5,.75,.875]:
            angles=[animation.channels[(1,i)].sample(frame) for i in [3,4,5]]
            reference=(Rotation.from_euler('xyz',angles).as_matrix()
                       @cal.source_rotation[1].T@cal.target_rotation[0])
            actual=pose(model,motion,frame)[0,:3,:3]
            self.assertLess(float(np.max(np.abs(actual-reference))),1e-6)

    def test_native_root_helper_output_and_keys_survive(self):
        before,after,_,_,_,metrics=convert()
        self.assertEqual(metrics['native_helper_records'],2)
        for frame in np.arange(0.,1.01,.125):
            self.assertTrue(np.array_equal(helper_pose(before,frame)[-1],helper_pose(after,frame)[-1]))
        self.assertTrue(np.array_equal(before.helper_channels[0].keys,after.helper_channels[0].keys))

    def test_reverse_range_plays_donor_backwards(self):
        _,motion,model,cal,animation,_=convert(1.,0.)
        frame=.25
        angles=[animation.channels[(1,i)].sample(1.-frame) for i in [3,4,5]]
        reference=Rotation.from_euler('xyz',angles).as_matrix()@cal.source_rotation[1].T@cal.target_rotation[0]
        self.assertLess(float(np.max(np.abs(pose(model,motion,frame)[0,:3,:3]-reference))),1e-6)

    def test_hold_range_has_no_donor_animation_channels(self):
        _,motion,model,cal,animation,_=convert(.5,.5)
        self.assertTrue(np.array_equal(pose(model,motion,0),pose(model,motion,1)))
        self.assertEqual(len(motion.helper_channels),2)  # original and its root-output duplicate


if __name__=='__main__':unittest.main()
