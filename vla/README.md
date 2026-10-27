# VLA: training & evaluation

Everything for the Vision-Language-Action model lives here.

| File | Purpose |
|---|---|
| [`finetune_smolvla.ipynb`](finetune_smolvla.ipynb) | Fine-tune `lerobot/smolvla_base` on the SO-100 pick-place dataset (branch 1 — real-robot deployment) |
| [`metaworld_train_eval.ipynb`](metaworld_train_eval.ipynb) | Fine-tune SmolVLA on Meta-World MT50 + evaluation in the MuJoCo simulator with video recording (branch 2 — sim benchmark) |
| [`libero_train_eval.ipynb`](libero_train_eval.ipynb) | Same idea for LIBERO — requires Linux + EGL (blocked on Kaggle, kept for reference) |
| `collect_sim.py` (TODO) | Record Gazebo teleop/scripted episodes into LeRobot format |
| `eval_sim.py` (TODO) | Roll out a policy in Gazebo and report success rate |

## Model choice: SmolVLA

- Model card: <https://huggingface.co/lerobot/smolvla_base>
- ~450M params; fine-tunes the action expert while freezing the vision encoder (efficient on a free Colab T4).

## Dataset format

Data is stored on the Hugging Face Hub in **LeRobot format** (episodes of
`(state, action, image, language)` frames). See
<https://huggingface.co/docs/lerobot/index>.
