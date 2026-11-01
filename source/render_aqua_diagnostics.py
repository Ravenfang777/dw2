"""Render diagnostic bone poses from a decoded BBS source bank.

Uses PMO bind transforms for unanimated channels. No KH1 retargeting is implied.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial.transform import Rotation

from bbs_source_inspector import read_pmo_skeleton, read_pam, iter_pam_sources


CHAINS = [
    (["center", "hara", "mune", "kubi", "atama"], "#d6e0f0"),
    (["mune", "R_kata", "R_ude1", "R_ude2", "R_te"], "#ffb66c"),
    (["mune", "L_kata", "L_ude1", "L_ude2", "L_te"], "#7dc9ff"),
    (["center", "koshi", "R_momo", "R_sune", "R_ashi1", "R_ashi2"], "#ffb66c"),
    (["center", "koshi", "L_momo", "L_sune", "L_ashi1", "L_ashi2"], "#7dc9ff"),
]


def font(size):
    path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(str(path), size) if path.is_file() else ImageFont.load_default()


def bind_components(skeleton):
    result = []
    for bone in skeleton["bones"]:
        matrix = np.array(bone["transform"]).reshape(4, 4).T
        scale = np.linalg.norm(matrix[:3, :3], axis=0)
        rotation = Rotation.from_matrix(matrix[:3, :3] / scale).as_euler("xyz")
        result.append(np.concatenate([matrix[:3, 3], rotation, scale]))
    return np.array(result)


def worlds(skeleton, animation, frame, bind):
    components = bind.copy()
    for (bone, axis), value in animation.sample_channels(frame).items():
        components[bone, axis] = value
    result = []
    for index, bone in enumerate(skeleton["bones"]):
        values = components[index]
        matrix = np.eye(4)
        matrix[:3, :3] = Rotation.from_euler("xyz", values[3:6]).as_matrix() @ np.diag(values[6:9])
        matrix[:3, 3] = values[:3]
        parent = bone["parent"]
        result.append(matrix if parent is None else result[parent] @ matrix)
    return np.array(result)


def project(points):
    # Fixed three-quarter diagnostic view, vertical axis is source Y.
    return np.stack([points[..., 0] * 0.85 + points[..., 2] * 0.526,
                     -points[..., 1] + points[..., 2] * 0.19 - points[..., 0] * 0.12], axis=-1)


def draw_tile(skeleton, positions, size):
    image = Image.new("RGB", size, "#111926")
    draw = ImageDraw.Draw(image)
    indexes = {bone["name"]: bone["index"] for bone in skeleton["bones"]}
    used = sorted({indexes[name] for names, _ in CHAINS for name in names})
    points = project(positions[used])
    minimum, maximum = points.min(axis=0), points.max(axis=0)
    span = np.maximum(maximum-minimum, 0.05)
    scale = min((size[0]-20)/span[0], (size[1]-25)/span[1], 60.0)
    shift = np.array(size)/2 - (minimum+maximum)/2*scale
    pose(draw, positions, skeleton, shift, scale=scale)
    return image


def pose(draw, positions, skeleton, box, scale=65.0, center=None):
    name_index = {bone["name"]: bone.get("index", index) for index, bone in enumerate(skeleton["bones"])}
    if center is None:
        center = np.zeros(3)
    points = project(positions - center)
    ox, oy = box
    points = points * scale + np.array([ox, oy])
    for names, color in CHAINS:
        coords = [tuple(points[name_index[name]]) for name in names]
        draw.line(coords, fill=color, width=3)
        for xy in coords:
            draw.ellipse((xy[0]-2, xy[1]-2, xy[0]+2, xy[1]+2), fill=color)
    xy = points[name_index["atama"]]
    draw.ellipse((xy[0]-7, xy[1]-9, xy[0]+7, xy[1]+6), outline="#d6e0f0", width=2)


def render(root, out):
    out.mkdir(parents=True, exist_ok=True)
    skeleton = read_pmo_skeleton((root / "p02ex00.pmo").read_bytes())
    bind = bind_components(skeleton)
    packed = []
    for locator, kind, data in iter_pam_sources(root):
        if kind == "arc":
            for animation in read_pam(data, skeleton["bone_count"]):
                packed.append((locator, animation))
    # Keep duplicate command variants visible; their source identity matters.
    for page in range(math.ceil(len(packed) / 15)):
        batch = packed[page*15:(page+1)*15]
        image = Image.new("RGB", (1536, 160 + len(batch)*150), "#111926")
        draw = ImageDraw.Draw(image)
        draw.text((24, 18), "AQUA / SOURCE MOTION INSPECTION", font=font(27), fill="#e8effa")
        draw.text((24, 59), "Original BBS body poses. Orange: right limbs. Blue: left limbs. No weapon or KH1 conversion.", font=font(17), fill="#acb9ce")
        draw.text((24, 88), "Frames sampled across each full clip. Names are numeric source labels, not action assignments.", font=font(16), fill="#acb9ce")
        for row, (locator, animation) in enumerate(batch):
            top = 140 + row*150
            draw.line((20, top, 1516, top), fill="#354254")
            source = locator.split("::")[0]
            draw.text((24, top+9), Path(source).name, font=font(16), fill="#edf3ff")
            draw.text((24, top+34), f"motion {animation.name} / {animation.frame_count} frames", font=font(14), fill="#acb9ce")
            sample_frames = np.linspace(0, animation.frame_count-1, 7)
            for col, frame in enumerate(sample_frames):
                transforms = worlds(skeleton, animation, float(frame), bind)
                positions = transforms[:, :3, 3]
                tile = draw_tile(skeleton, positions, (168, 130))
                image.paste(tile, (282 + col*177, top+12))
        image.save(out / f"packed_motion_sheet_{page+1:02}.png")
    # The only ordinary-range gameplay clip supplied is examined separately.
    candidate = next(((source, anim) for source, anim in packed if anim.name == "045"), None)
    if candidate:
        source, animation = candidate
        frames = []
        for frame in np.linspace(0, animation.frame_count-1, min(animation.frame_count, 70)):
            image = Image.new("RGB", (720, 480), "#111926")
            draw = ImageDraw.Draw(image)
            draw.text((22, 18), "Aqua source clip 045", font=font(26), fill="#edf3ff")
            draw.text((22, 57), "Diagnostic pose playback — action not assigned", font=font(16), fill="#acb9ce")
            transforms = worlds(skeleton, animation, float(frame), bind)
            positions = transforms[:, :3, 3]
            center = positions[1].copy(); center[1] = 0
            draw.line((70, 423, 650, 423), fill="#354254")
            pose(draw, positions, skeleton, (360, 423), scale=140, center=center)
            draw.text((22, 447), f"{Path(source.split('::')[0]).name} / frame {frame:.0f}", font=font(15), fill="#acb9ce")
            frames.append(image)
        frames[0].save(out / "Aqua_Source_045.gif", save_all=True, append_images=frames[1:],
                       duration=round(1000/animation.fps), loop=0, disposal=2)
    return len(packed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print("Rendered source clips:", render(args.root, args.out))
