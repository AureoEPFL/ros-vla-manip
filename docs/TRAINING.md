# Training cookbook

Exact commands that worked (or failed, and why) during this project. LeRobot **v0.6.2**, Python ≥ 3.12.

## 1. SO-100 pick-place fine-tune (done)

```bash
pip install -e ".[smolvla,training]"
pip install -U torchao   # fix torchao/diffusers conflict on Colab/Kaggle

lerobot-train \
  --policy.path=lerobot/smolvla_base \
  --dataset.repo_id=lerobot/svla_so100_pickplace \
  --policy.repo_id=oreocookiedough/my-smolvla \
  --policy.push_to_hub=true \
  --policy.empty_cameras=1 \
  --rename_map='{"observation.images.top": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}' \
  --batch_size=16 \
  --steps=500 \
  --save_freq=100 \
  --log_freq=20 \
  --output_dir=outputs/train/my_smolvla \
  --policy.device=cuda \
  --wandb.enable=true
```

Result: loss 0.440 → 0.140 (500 steps), model on
[oreocookiedough/my-smolvla](https://huggingface.co/oreocookiedough/my-smolvla).

### Lessons learned

- The pretrained base is `lerobot/smolvla_base` (the `HuggingFaceTB/SmolVLA-Base`
  repo is **gated**).
- The dataset's cameras are `top`/`wrist` but SmolVLA expects `camera1/2/3` →
  `--rename_map` + `--policy.empty_cameras=1` (see the official
  [rename map doc](https://huggingface.co/docs/lerobot/v0.6.1/rename_map)).
- `--policy.push_to_hub` defaults to `true`; without `--policy.repo_id` the run
  crashes at startup with `ValueError: 'repo_id' argument missing`.
- `log_freq=200` by default → loss appears on W&B only after 200 steps.

## 2. Meta-World fine-tune + sim eval (in progress)

```bash
pip install -e ".[smolvla,training,metaworld]"

lerobot-train \
  --policy.type=smolvla \
  --policy.load_vlm_weights=true \
  --policy.push_to_hub=false \
  --dataset.repo_id=lerobot/metaworld_mt50 \
  --env.type=metaworld \
  --env.task=assembly-v3,dial-turn-v3,handle-press-side-v3 \
  --output_dir=./outputs/metaworld_smolvla \
  --steps=2000 \
  --batch_size=16 \
  --save_freq=500 \
  --log_freq=50 \
  --wandb.enable=true

lerobot-eval \
  --policy.path=outputs/metaworld_smolvla/checkpoints/last/pretrained_model \
  --env.type=metaworld \
  --env.task=assembly-v3 \
  --eval.batch_size=1 \
  --eval.n_episodes=3 \
  --eval.recording=true \
  --eval.recording_repo_id=oreocookiedough/eval_metaworld
```

## 3. LIBERO (attempted, blocked on Kaggle)

```bash
apt-get install -y libegl1-mesa-dev libgles2-mesa-dev libgl1-mesa-dev libosmesa6-dev patchelf
pip install -e ".[smolvla,training,libero]"
```

Fails on Kaggle (Python 3.13): `egl_probe` / `hf-egl-probe` only ship sdists and
their CMake build dies silently (`pip -q` hides the real error). Works on a Linux
machine with EGL properly set up; see [`vla/libero_train_eval.ipynb`](../vla/libero_train_eval.ipynb).

## Kaggle automation (CLI, no browser)

```bash
pip install kaggle
export KAGGLE_API_TOKEN=KGAT_...   # token from kaggle.com/settings/api

kaggle kernels push -p kaggle-run        # push + run (kernel-metadata.json sets GPU T4 x2, internet, private)
kaggle kernels status oreocookiedough/ros-vla-manip-metaworld
kaggle kernels logs   oreocookiedough/ros-vla-manip-metaworld   # only after the run completes
kaggle kernels output oreocookiedough/ros-vla-manip-metaworld -p kaggle-metaworld-output
```

### Kaggle gotchas

- GPU requires **phone verification** on the account.
- Logs via the API are **empty while the kernel runs** — only readable once done.
- `kernel-metadata.json`: `"enable_gpu": true, "machine_shape": "NvidiaTeslaT4"`.
- Redirect logs to a file in UTF-8 on Windows:
  `[Console]::OutputEncoding=[Text.Encoding]::UTF8; ... | Out-File -Encoding utf8`.
