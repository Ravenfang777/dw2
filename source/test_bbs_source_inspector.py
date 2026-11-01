"""Boundary and interpolation checks independent of the uploaded source data."""
import struct
import unittest
import math

from bbs_source_inspector import FormatError, read_arc, read_pam


def pam_with_channel(frames, keys, minimum=-2.0, maximum=2.0, dense=False):
    # One bone, translation X; one valid animation following the 16-byte entry.
    header = b"PAM\0" + struct.pack("<I6sH", 1, b"\0"*6, 1)
    entry = struct.pack("<I12s", 32, b"test")
    animation = struct.pack("<HBBHBBHHH", 0, 30, 0, 0, 1, 0, frames, 0, 1)
    count_format = "<B" if frames <= 255 else "<H"
    animation += struct.pack("<ff", maximum, minimum)
    animation += struct.pack(count_format, len(keys))
    if len(keys) > 1:
        for frame, value in keys:
            if not dense:
                animation += struct.pack(count_format, frame)
            animation += struct.pack("<H", value)
    return header + entry + animation


class PamTests(unittest.TestCase):
    def test_wrapped_rotation_crosses_pi_without_a_full_reverse_turn(self):
        data=bytearray(pam_with_channel(2,[(0,0),(1,65535)],minimum=math.radians(179),maximum=math.radians(-179),dense=True))
        struct.pack_into('<H',data,44,1<<3)
        animation,=read_pam(bytes(data))
        self.assertAlmostEqual(animation.channels[(0,3)].sample(.5),math.pi,places=6)

    def test_explicit_sparse_rotation_winding_is_preserved(self):
        data=bytearray(pam_with_channel(31,[(0,0),(30,65535)],minimum=0.,maximum=2*math.pi))
        struct.pack_into('<H',data,44,1<<3)
        animation,=read_pam(bytes(data))
        self.assertAlmostEqual(animation.channels[(0,3)].sample(15),math.pi,places=6)

    def test_sparse_quantized_interpolation(self):
        data = pam_with_channel(11, [(0, 0), (10, 65535)])
        animation, = read_pam(data, 1)
        channel = animation.channels[(0, 0)]
        self.assertEqual(channel.sample(0), -2.0)
        self.assertEqual(channel.sample(5), 0.0)
        self.assertEqual(channel.sample(10), 2.0)
        self.assertEqual(channel.sample(-1), -2.0)
        self.assertEqual(channel.sample(20), 2.0)

    def test_dense_implicit_frame_numbers(self):
        data = pam_with_channel(3, [(0, 0), (1, 32768), (2, 65535)], dense=True)
        animation, = read_pam(data)
        self.assertEqual(animation.channels[(0, 0)].frames, [0, 1, 2])
        self.assertAlmostEqual(animation.channels[(0, 0)].sample(1), 2.0/65535, places=7)

    def test_constant_channel_has_no_key_bytes(self):
        data = pam_with_channel(20, [(0, 0)], minimum=7.0, maximum=7.0)
        animation, = read_pam(data)
        self.assertEqual(animation.channels[(0, 0)].sample(10), 7.0)
        self.assertEqual(animation.data_end, len(data))

    def test_long_sparse_track_uses_16_bit_frame_ids(self):
        data = pam_with_channel(300, [(0, 0), (299, 65535)])
        animation, = read_pam(data)
        self.assertEqual(animation.channels[(0, 0)].frames, [0, 299])
        self.assertAlmostEqual(animation.channels[(0, 0)].sample(149.5), 0.0)

    def test_rejects_bone_mismatch(self):
        with self.assertRaises(FormatError):
            read_pam(pam_with_channel(2, [(0, 0)]), expected_bones=54)

    def test_rejects_truncated_track(self):
        data = pam_with_channel(11, [(0, 0), (10, 65535)])
        with self.assertRaises(FormatError):
            read_pam(data[:-1])

    def test_rejects_non_increasing_frames(self):
        data = pam_with_channel(11, [(3, 0), (3, 65535)])
        with self.assertRaises(FormatError):
            read_pam(data)

    def test_empty_slot_is_not_an_animation(self):
        data = b"PAM\0" + struct.pack("<I6sH", 1, b"\0"*6, 1) + bytes(16)
        self.assertEqual(read_pam(data), [])


class ArcTests(unittest.TestCase):
    def test_dependency_is_not_extracted_as_payload(self):
        data = b"ARC\0" + struct.pack("<HHII", 1, 1, 0, 0)
        data += struct.pack("<IIII16s", 17232, 0, 0, 0, b"shared")
        files, dependencies = read_arc(data)
        self.assertEqual(files, [])
        self.assertEqual(dependencies[0]["name"], "shared")

    def test_rejects_payload_outside_container(self):
        data = b"ARC\0" + struct.pack("<HHII", 1, 1, 0, 0)
        data += struct.pack("<IIII16s", 0, 48, 999, 0, b"missing.pam")
        with self.assertRaises(FormatError):
            read_arc(data)


if __name__ == "__main__":
    unittest.main()
