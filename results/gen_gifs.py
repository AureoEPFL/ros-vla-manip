import os
import numpy as np
from PIL import Image
import imageio.v2 as imageio

SRC = os.path.join(
    "ros-vla-manip", "results", "eval_pickplace", "output", "eval",
    "2026-10-25", "14-13-20_metaworld_smolvla", "videos", "pick-place-v3_0",
)
DST = os.path.join("ros-vla-manip", "results", "gifs")
os.makedirs(DST, exist_ok=True)

# (output name, source video, max width)
jobs = [
    ("pickplace_success.gif", "eval_episode_7.mp4", 240),
    ("pickplace_success_9.gif", "eval_episode_9.mp4", 240),
    ("pickplace_failure.gif", "eval_episode_0.mp4", 240),
    ("pickplace_failure_4.gif", "eval_episode_4.mp4", 240),
]

for out, vid, width in jobs:
    src = os.path.join(SRC, vid)
    reader = imageio.get_reader(src)
    meta = reader.get_meta_data()
    fps = meta.get("fps", 30)
    frames = []
    for i, frame in enumerate(reader):
        if i % 2 == 0:  # skip every other frame to keep the gif small
            img = Image.fromarray(frame)
            h = int(img.height * width / img.width)
            img = img.resize((width, h))
            frames.append(np.array(img))
    imageio.mimsave(os.path.join(DST, out), frames, fps=15, loop=0)
    print(f"wrote {out}: {len(frames)} frames (src {fps:.0f} fps)")
