"""Inspect BBS PMO/PAM/ARC source files without modifying game assets.

Format references: OpenKH's BBS pmo.html, pam.html, and arc.html.
This is a source decoder, not a KH1 animation converter or runtime mod.
"""
from __future__ import annotations

import argparse
import bisect
import csv
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import struct


class FormatError(ValueError):
    pass


def unpack(fmt: str, data: bytes, offset: int):
    size = struct.calcsize(fmt)
    if offset < 0 or offset + size > len(data):
        raise FormatError(f"Truncated data at 0x{offset:X}, need {size} bytes")
    return struct.unpack_from(fmt, data, offset)


def name_string(raw: bytes) -> str:
    return raw.split(b"\0", 1)[0].decode("ascii", "replace")


@dataclass
class Channel:
    frames: list[int]
    values: list[float]

    def sample(self, frame: float) -> float:
        if len(self.frames) == 1 or frame <= self.frames[0]:
            return self.values[0]
        if frame >= self.frames[-1]:
            return self.values[-1]
        index = bisect.bisect_right(self.frames, frame) - 1
        fraction = (frame - self.frames[index]) / (self.frames[index + 1] - self.frames[index])
        return self.values[index] * (1.0 - fraction) + self.values[index + 1] * fraction


@dataclass
class Animation:
    slot: int
    name: str
    flag: int
    fps: int
    interpolation_frames: int
    loop_from: int
    loop_to: int
    frame_count: int
    bone_count: int
    channels: dict[tuple[int, int], Channel]
    data_end: int

    def sample_channels(self, frame: float) -> dict[tuple[int, int], float]:
        frame = min(max(frame, 0.0), float(self.frame_count - 1))
        return {key: channel.sample(frame) for key, channel in self.channels.items()}


def read_pam(data: bytes, expected_bones: int | None = None) -> list[Animation]:
    if data[:4] != b"PAM\0":
        raise FormatError("Not a PAM container")
    count, = unpack("<I", data, 4)
    if count > (len(data) - 16) // 16:
        raise FormatError("PAM entry table exceeds container")
    entries = [unpack("<I12s", data, 16 + index * 16) for index in range(count)]
    offsets = sorted(set(offset for offset, _ in entries if offset))
    animations = []
    for slot, (offset, raw_name) in enumerate(entries):
        if not offset:
            continue  # An empty entry is not an animation.
        if offset < 16 + count * 16:
            raise FormatError("PAM animation overlaps its table")
        bound = next((value for value in offsets if value > offset), len(data))
        flag, fps, interpolation, loop_from, bones, reserved, frames, loop_to = unpack(
            "<HBBHBBHH", data, offset
        )
        if not fps or not frames or not bones:
            raise FormatError(f"Invalid animation header in slot {slot}")
        if expected_bones is not None and bones != expected_bones:
            raise FormatError(f"Animation has {bones} bones; model has {expected_bones}")
        masks = unpack("<" + "H" * bones, data, offset + 12)
        position = offset + 12 + 2 * bones
        channels = {}
        for bone, mask in enumerate(masks):
            if mask & ~0x1FF:
                raise FormatError(f"Unknown channel mask 0x{mask:X}")
            for axis in range(9):
                if not mask & (1 << axis):
                    continue
                maximum, minimum = unpack("<ff", data, position)
                position += 8
                if not math.isfinite(maximum) or not math.isfinite(minimum):
                    raise FormatError("Non-finite channel range")
                integer_fmt = "<B" if frames <= 255 else "<H"
                integer_size = struct.calcsize(integer_fmt)
                key_count, = unpack(integer_fmt, data, position)
                position += integer_size
                if key_count < 1 or key_count > frames:
                    raise FormatError(f"Invalid key count {key_count} for {frames} frames")
                if key_count == 1:
                    channel = Channel([0], [maximum])
                else:
                    times, values = [], []
                    for key in range(key_count):
                        if key_count == frames:
                            time = key
                        else:
                            time, = unpack(integer_fmt, data, position)
                            position += integer_size
                        quantized, = unpack("<H", data, position)
                        position += 2
                        if time >= frames or (times and time <= times[-1]):
                            raise FormatError("Non-increasing or out-of-range keyframe")
                        times.append(time)
                        values.append(minimum + (maximum - minimum) * quantized / 65535.0)
                    channel = Channel(times, values)
                    # Retarget sampling policy: exporter tracks confined to
                    # [-pi,pi] cross a wrapped seam; interpolate their nearest
                    # equivalent angles. Tracks already outside that range
                    # retain explicit authored winding. Integer-frame rotation
                    # matrices and the original file bytes remain unchanged.
                    if 3 <= axis <= 5 and all(abs(value) <= math.pi + 1e-4 for value in values):
                        continuous = [values[0]]
                        offset = 0.0
                        for before, after in zip(values, values[1:]):
                            delta = after - before
                            if delta > math.pi:
                                offset -= 2 * math.pi
                            elif delta < -math.pi:
                                offset += 2 * math.pi
                            continuous.append(after + offset)
                        channel = Channel(times, continuous)
                channels[(bone, axis)] = channel
                if position > bound:
                    raise FormatError("Animation channels exceed entry boundary")
        animations.append(Animation(slot, name_string(raw_name), flag, fps,
                                    interpolation, loop_from, loop_to, frames,
                                    bones, channels, position))
    return animations


def read_arc(data: bytes) -> tuple[list[tuple[str, bytes]], list[dict]]:
    if data[:4] != b"ARC\0":
        raise FormatError("Not an ARC container")
    version, count = unpack("<HH", data, 4)
    if version != 1:
        raise FormatError(f"Unsupported ARC version {version}")
    table_end = 16 + count * 32
    if table_end > len(data):
        raise FormatError("ARC entry table exceeds container")
    files, dependencies = [], []
    for index in range(count):
        directory_hash, offset, length, reserved, raw_name = unpack("<IIII16s", data, 16 + index * 32)
        name = name_string(raw_name)
        if directory_hash:
            dependencies.append({"name": name, "directory_hash": directory_hash,
                                 "length": length})
            continue
        if not length:
            continue
        if offset < table_end or offset + length > len(data):
            raise FormatError(f"ARC member {name!r} is out of bounds")
        files.append((name, data[offset:offset + length]))
    return files, dependencies


def read_pmo_skeleton(data: bytes) -> dict:
    if data[:4] != b"PMO\0":
        raise FormatError("Not a PMO model")
    offset, = unpack("<I", data, 12)
    model_scale, = unpack("<f", data, 24)
    if not offset or data[offset:offset + 4] != b"BON\0":
        raise FormatError("PMO skeleton is absent or unsupported")
    count, reserved, skinned_count, first_skinned = unpack("<HHHH", data, offset + 8)
    bones = []
    for ordinal in range(count):
        start = offset + 16 + ordinal * 160
        index, _, parent, _, skin_index = unpack("<HHHHH", data, start)
        raw_name, = unpack("<16s", data, start + 16)
        transform = unpack("<16f", data, start + 32)
        inverse = unpack("<16f", data, start + 96)
        if index != ordinal or (parent != 0xFFFF and parent >= count):
            raise FormatError("Unexpected bone numbering or parent")
        if any(not math.isfinite(v) for v in (*transform, *inverse)):
            raise FormatError("Non-finite skeleton transform")
        bones.append({"index": index, "parent": None if parent == 0xFFFF else parent,
                      "skin_index": None if skin_index == 0xFFFF else skin_index,
                      "name": name_string(raw_name), "transform": list(transform),
                      "inverse_transform": list(inverse)})
    for bone in bones:
        visited, current = set(), bone["index"]
        while current is not None:
            if current in visited:
                raise FormatError("Cyclic bone hierarchy")
            visited.add(current)
            current = bones[current]["parent"]
    return {"bone_count": count, "model_scale": model_scale,
            "skinned_bone_count": skinned_count, "first_skinned_bone": first_skinned,
            "bones": bones}


def iter_pam_sources(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() == ".pam":
            yield str(path.relative_to(root)), "loose", path.read_bytes()
        elif path.suffix.lower() == ".arc":
            members, _ = read_arc(path.read_bytes())
            for name, data in members:
                if data.startswith(b"PAM\0"):
                    yield f"{path.relative_to(root)}::{name}", "arc", data


def inspect(root: Path, out: Path) -> dict:
    model_path = root / "p02ex00.pmo"
    if not model_path.is_file():
        candidates = sorted(root.rglob("p02ex00.pmo"))
        if not candidates:
            raise FormatError("Aqua p02ex00.pmo model not found")
        model_path = candidates[0]
    model_data = model_path.read_bytes()
    skeleton = read_pmo_skeleton(model_data)
    records, failures, seen, sources = [], [], {}, []
    animation_hashes = set()
    for locator, kind, data in iter_pam_sources(root):
        digest = hashlib.sha256(data).hexdigest()
        sources.append({"locator": locator, "kind": kind, "sha256": digest,
                        "size_bytes": len(data)})
        if digest in seen:
            seen[digest]["duplicate_locators"].append(locator)
            continue
        source = {"source": locator, "kind": kind, "sha256": digest,
                  "duplicate_locators": []}
        seen[digest] = source
        try:
            animations = read_pam(data, skeleton["bone_count"])
            source["animation_count"] = len(animations)
            for animation in animations:
                start, = unpack("<I", data, 16 + 16 * animation.slot)
                animation_digest = hashlib.sha256(data[start:animation.data_end]).hexdigest()
                animation_hashes.add(animation_digest)
                record = {"source": locator, "source_kind": kind,
                          "slot": animation.slot, "name": animation.name,
                          "animation_sha256": animation_digest,
                          "frames": animation.frame_count, "fps": animation.fps,
                          "duration_seconds": round(animation.frame_count / animation.fps, 6),
                          "bones": animation.bone_count, "flag": animation.flag,
                          "interpolation_frames": animation.interpolation_frames,
                          "loop_from": animation.loop_from, "loop_to": animation.loop_to,
                          "channels": len(animation.channels),
                          "keyframes": sum(len(c.frames) for c in animation.channels.values()),
                          "semantic_action": "unassigned"}
                records.append(record)
        except (FormatError, struct.error) as error:
            failures.append({"source": locator, "error": str(error)})
    out.mkdir(parents=True, exist_ok=True)
    (out / "aqua_skeleton.json").write_text(json.dumps(skeleton, indent=2) + "\n")
    if records:
        with (out / "aqua_animation_inventory.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    report = {"model": str(model_path.relative_to(root)),
              "model_sha256": hashlib.sha256(model_data).hexdigest(),
              "bone_count": skeleton["bone_count"],
              "pam_sources_including_duplicates": len(sources),
              "unique_pam_payloads": len(seen),
              "decoded_animations": len(records),
              "unique_animation_payloads": len(animation_hashes),
              "loose_animations": sum(r["source_kind"] == "loose" for r in records),
              "arc_animations": sum(r["source_kind"] == "arc" for r in records),
              "failures": failures,
              "containers": list(seen.values()),
              "status": "source inspection only; action mapping not yet established",
              "kh1_runtime_mod_created": False}
    (out / "source_inspection.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = inspect(args.root, args.out)
    for key in ["bone_count", "pam_sources_including_duplicates", "unique_pam_payloads",
                "decoded_animations", "loose_animations", "arc_animations", "failures"]:
        print(f"{key}: {report[key]}")
    if report["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
