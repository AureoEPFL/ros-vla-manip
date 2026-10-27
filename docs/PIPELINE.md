# The full pipeline, explained

This project fine-tunes a **Vision-Language-Action (VLA)** model and evaluates it
**in simulation** — no robot, no local GPU. Here is exactly what each stage does.

## Overview

```
① Data          ② Train          ③ Save            ④ Evaluate        ⑤ Demo videos
────────────────────────────────────────────────────────────────────────────────────
LeRobot         SmolVLA learns    checkpoint →      the model drives   we record the
dataset         to predict        Hugging Face      the simulated      screen →
(recorded       actions from      (oreocookiedough/ arm (Meta-World)   eval_episode_*.mp4
demos)          images+state      metaworld-smolvla)
```

## ① Data

We use **LeRobot-format datasets** hosted on Hugging Face. They contain episodes:
sequences of `(camera image, robot state, action, instruction)` recorded while a
human teleoperated a robot.

- SO-100 branch: [`lerobot/svla_so100_pickplace`](https://huggingface.co/datasets/lerobot/svla_so100_pickplace) (50 episodes)
- Meta-World branch: [`lerobot/metaworld_mt50`](https://huggingface.co/datasets/lerobot/metaworld_mt50) (2500 episodes, 50 tasks)

## ② Train (fine-tuning)

SmolVLA (450M params) already knows how to control arms from its pretraining.
We **fine-tune** it: show it the dataset, let it predict the next action, measure
the error (**loss**), and update the weights. The loss going down = it learns.

We freeze the vision encoder and only train the ~100M "action expert" parameters,
so it fits on a free Kaggle T4 GPU.

## ③ Save

The tuned weights are saved as a **checkpoint** and pushed to the Hub:
[oreocookiedough/metaworld-smolvla](https://huggingface.co/oreocookiedough/metaworld-smolvla).

## ④ Evaluate

We load the checkpoint and put it in the **Meta-World simulator** (MuJoCo,
Sawyer arm). The loop is:

```
image + state + task  →  model predicts an action  →  arm moves  →  new image  →  …
```

up to 400 steps. Each step gives a **reward** (0 = far, ~1 = almost done). If the
task is completed before the end, it's a **success**.

We run **N independent attempts** (episodes). The **success rate** = successes / N.

## ⑤ Demo videos

Each attempt is recorded as an `.mp4`:
- `eval_episode_0.mp4` = attempt #1
- `eval_episode_1.mp4` = attempt #2
- `eval_episode_2.mp4` = attempt #3

They are **not** "levels" — they are independent rolls of the same task.

## The tasks

| Task | Description | Difficulty |
|---|---|---|
| `reach-v2` | reach a target point | easy |
| `pick-place-v2` | grasp an object and place it | medium |
| `door-open-v2` | open a door | medium |
| `dial-turn-v3` | turn a dial | medium |
| `assembly-v3` | insert a peg into a hole | very hard |

## Current results

- **SO-100** (500 steps): loss 0.440 → 0.140.
- **Meta-World** (2000 steps, MT50): loss 1.885 → 0.281.
- **Eval `assembly-v3`**: 0/3 success (expected — 2000 steps is far below the
  ~100k steps used in the SmolVLA paper, and assembly is a hard precision task).

## Why 0% on the first eval (and how to fix it)

Too few steps + a hard task + multi-task dilution. Levers:
1. **Focus on one task** (specialize).
2. **Pick an easier task** (`reach-v2`, `pick-place-v2`).
3. **More steps** (10k+).
4. **More eval episodes** (20+) for a reliable number.
