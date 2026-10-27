# Fine-tuning a Vision-Language-Action model for robotic manipulation

**Can you fine-tune a small open-source VLA (Vision-Language-Action) model to do real manipulation tasks — on a free GPU, entirely in simulation, with no robot?**

This repository documents a complete, reproducible experiment: fine-tuning **[SmolVLA](https://huggingface.co/lerobot/smolvla_base)** (a 450M-parameter VLA) on **[LeRobot](https://github.com/huggingface/lerobot)** datasets and evaluating it in the **[Meta-World](https://meta-world.github.io/)** simulator. The goal is not just to "make it work", but to answer a concrete research question about *how* to fine-tune a VLA with limited compute.

---

## The research question

> **Does fine-tuning a small VLA on a broad multi-task benchmark help more than specializing it on a few tasks — and does specialization cause "catastrophic forgetting" on the tasks you didn't train on?**

To answer this, we compare **three models + one reference**, all evaluated on the **same 12 tasks**:

| Model | Starting point | Training data | Steps |
|-------|----------------|---------------|-------|
| **M0** | `lerobot/smolvla_base` (off-the-shelf) | — | 0 |
| **M1** | fresh SmolVLA | MT50 (50 tasks, 2 500 demos) | 10 000 |
| **M2** | fresh SmolVLA | 4 tasks only (basketball, bin-picking, pick-place, push) | 6 000 |
| **Expert** | — | scripted `Sawyer*V3Policy` | — (≈100% ceiling) |

The 12 evaluation tasks are stratified by difficulty (from Meta-World's official ranking):

| Difficulty | Tasks |
|-----------|-------|
| easy (3) | door-close, button-press-topdown, reach |
| medium (4) | basketball, bin-picking, coffee-push, sweep |
| hard (3) | pick-place, push, assembly |
| very-hard (2) | shelf-place, disassemble |

---

## Results (preliminary)

![Success rate by task](results/success_rate.svg)

| Task | Difficulty | M0 (base) | M1 (MT50) |
|------|-----------|-----------|-----------|
| door-close-v3 | easy | **100%** | 100% |
| button-press-topdown-v3 | easy | **80%** | 80% |
| reach-v3 | easy | 30% | 30% |
| basketball-v3 | medium | 20% | 20% |
| bin-picking-v3 | medium | 20% | 20% |
| sweep-v3 | medium | 10% | 10% |
| coffee-push-v3 | medium | 0% | 0% |
| pick-place-v3 | hard | 20% | 20% |
| push-v3 | hard | 20% | 20% |
| assembly-v3 | hard | 0% | 0% |
| shelf-place-v3 | very-hard | 10% | 10% |
| disassemble-v3 | very-hard | 10% | 10% |
| **Mean** | — | **≈ 27%** | **≈ 27%** |

*(10 episodes/task, 95% Wilson CI reported in the raw `eval_info.json`.)*

### 🔑 Key finding #1 — the base model is already competent

`lerobot/smolvla_base` is **not** an untrained model: it's a generalist VLA pre-trained on community manipulation data. Off-the-shelf, it already achieves **100% on door-close** and **80% on button-press**.

### 🔑 Key finding #2 — a short multi-task fine-tune changes nothing

M1 (10 000 steps on 50 tasks) is **statistically identical** to M0. Why? 10k steps × batch 32 ≈ **0.25 epoch** over the MT50 dataset — far too little to move a 450M-parameter model. The loss *did* decrease (0.44 → 0.14), but the observable behavior didn't budge.

This is the honest, documented result: **with limited compute, a broad multi-task fine-tune gives no measurable gain.**

---

## What's coming (in progress)

**M2 — the specialization experiment.** The insight behind it: training on *fewer* tasks concentrates the same compute into many more epochs per task.

| | M1 (multi-task) | M2 (specialized) |
|---|---|---|
| Tasks | 50 | 4 |
| Epochs per task (6-10k steps) | ~1.5 | **~12-20** |

So M2 should actually *move* the model this time. The open questions:

- **Specialization helps?** Does M2 beat M0/M1 on the 4 tasks it trained on?
- **Catastrophic forgetting?** Does M2 get *worse* on the 8 tasks it didn't train on?

Once M2 is trained and evaluated, the final comparison will be:

| Task | M0 (base) | M1 (MT50) | M2 (specialized) | Expert (ceiling) |
|------|-----------|-----------|------------------|------------------|
| … 12 tasks … | | | | |

→ Stay tuned — this is the main deliverable.

---

## How it works (the pipeline)

```
┌──────────────┐    ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  LeRobot      │──▶ │  Fine-tune      │──▶ │  Evaluate in      │──▶ │  Report          │
│  dataset      │    │  SmolVLA (VLA)  │    │  Meta-World (sim) │    │  success rate    │
│  (HF Hub)     │    │  on Kaggle T4   │    │  MuJoCo + Sawyer  │    │  + demo videos   │
└──────────────┘    └─────────────────┘    └──────────────────┘    └─────────────────┘
```

1. **Fine-tune** `lerobot/smolvla_base` on a LeRobot dataset (`lerobot/metaworld_mt50`) using the LeRobot CLI — on a **free Kaggle T4 GPU** (no local GPU needed).
2. **Evaluate** the policy in the **Meta-World** simulator (a MuJoCo-based Sawyer arm benchmark), measuring the per-task success rate.
3. **Record** rollout videos — successes *and* failures — for visual inspection.

### Demo videos (success & failure)

Rollout videos are in [`results/eval_pickplace/.../videos/pick-place-v3_0/`](results/eval_pickplace/output/eval/2026-10-25/14-13-20_metaworld_smolvla/videos/pick-place-v3_0/):

- ✅ **Success** — [episode 7](results/eval_pickplace/output/eval/2026-10-25/14-13-20_metaworld_smolvla/videos/pick-place-v3_0/eval_episode_7.mp4) and [episode 9](results/eval_pickplace/output/eval/2026-10-25/14-13-20_metaworld_smolvla/videos/pick-place-v3_0/eval_episode_9.mp4): clean grasp → lift → place at the goal.
- ❌ **Failure** — [episode 0](results/eval_pickplace/output/eval/2026-10-25/14-13-20_metaworld_smolvla/videos/pick-place-v3_0/eval_episode_0.mp4) and [episode 4](results/eval_pickplace/output/eval/2026-10-25/14-13-20_metaworld_smolvla/videos/pick-place-v3_0/eval_episode_4.mp4): misses the grasp / places the puck short.

*(Animated GIFs are coming — they'll be generated on Kaggle once the M2 run frees the GPU.)*

---

## Technical details

- **Model**: [SmolVLA](https://arxiv.org/abs/2506.01844) — 450M params, SmolVLM2-500M vision-language backbone + a ~100M-param action expert (vision encoder frozen, action expert trained).
- **Framework**: LeRobot (pinned to commit `d3793b7e` for reproducibility).
- **Compute**: free Kaggle notebooks (Tesla T4 ×2, ~12h/session). Long runs are **resumed across sessions** via `--resume=true --config_path=<checkpoint>`.
- **Environment**: Meta-World `pick-place`/`push`/… tasks (Sawyer arm, 4-dim action), `metaworld==3.1.1` + `mujoco==3.3.0`.
- **Metric**: success rate (task-completion flag from the simulator), with 95% Wilson confidence intervals.

### Reproducibility notes (gotchas we hit)

- LeRobot's Meta-World tasks use **`-v3` names** (`pick-place-v3`), not `-v2`.
- `metaworld==3.0.0` breaks with MuJoCo 3 → pin `metaworld==3.1.1` + `mujoco==3.3.0`.
- Fine-tuning from `--policy.path=lerobot/smolvla_base` fails on Meta-World (feature mismatch: the base was trained on a 3-camera/6-dim robot). Use `--policy.type=smolvla --policy.load_vlm_weights=true` instead.
- Kaggle's 12h timeout kills ~10k-step runs → save checkpoints every 2000 steps and resume.

---

## Repository layout

```
ros-vla-manip/
├─ README.md
├─ docs/                  ← STATE_OF_THE_ART, SETUP, ARCHITECTURE, TRAINING, EXPERIMENT_PLAN
├─ vla/                   ← fine-tuning & evaluation notebooks
├─ results/               ← metrics (loss, success rate) + eval videos/gifs
├─ sim/                   ← Gazebo/ROS worlds & robot config (optional deployment)
├─ ros2_ws/               ← ROS 2 workspace (optional deployment)
├─ docker/                ← reproducible container
└─ eval/                  ← evaluation utilities
```

## Roadmap

- [x] Fine-tune SmolVLA on MT50 (M1) + evaluate → documented "no measurable gain" finding
- [x] Baseline M0 (off-the-shelf SmolVLA) evaluation
- [ ] **M2** specialized fine-tune + evaluation (in progress)
- [ ] Final multi-task vs. specialized comparison + report
- [ ] (Stretch) ROS 2 + Gazebo deployment of the fine-tuned policy

## License

[MIT](LICENSE)
