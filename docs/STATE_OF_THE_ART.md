# State of the Art (late 2026)

A concise, opinionated survey of the landscape this project sits in. Each section
names the key players, what's actually usable today, and how it maps to this repo.

---

## 1. Vision-Language-Action (VLA) models

VLA models are the current frontier of robot "foundation models": a single model
that takes images + a natural-language instruction and outputs robot actions
(end-effector poses, joint targets, gripper commands).

### Model families, roughly by size

| Model | Size | Notes | Status |
|---|---|---|---|
| **SmolVLA** | ~440M | Distilled, fast, cheap to fine-tune; our choice | ✅ actively developed (Hugging Face) |
| **RT-2** (Google) | 55B | Early VLA, text+image → actions | research |
| **OpenVLA** | 7B | Open, Prismatic-VLM backbone; very widely used | ✅ mature |
| **π0 / π0-FAST** (Physical Intelligence) | 3B | Flow-matching actions; strong real-world results | frontier, partly closed |
| **GR00T N1** (NVIDIA) | 2B | Dual-system (fast/slow) VLA | frontier |
| **Octo** | ~93M | Lightweight transformer policy | ✅ mature |

**Takeaway for this project:** SmolVLA is the sweet spot — small enough to
LoRA-fine-tune on a free Colab T4 (16 GB), yet a genuine VLA you can point at
real manipulation tasks.

### Key references

- [SmolVLA base model](https://huggingface.co/lerobot/smolvla_base)
- [SmolVLA technical report](https://huggingface.co/blog/smolvla) (Hugging Face blog)
- OpenVLA: [paper](https://arxiv.org/abs/2406.09246) · [repo](https://github.com/openvla/openvla)
- π0: [blog](https://www.physicalintelligence.company/blog/pi0)

---

## 2. Training & deployment frameworks

**LeRobot** (Hugging Face) is now the de-facto standard: dataset format, training
scripts, and a real-robot/sim evaluation loop in one place.

- [LeRobot GitHub](https://github.com/huggingface/lerobot)
- [LeRobot docs](https://huggingface.co/docs/lerobot/index)
- Datasets are plain Hugging Face Hub datasets in the **LeRobot format**
  (episodes of `(state, action, image, language)` frames), which makes sharing
  and fine-tuning trivial.

### ROS integration

- **ROS2SmolVLA** — bridges SmolVLA into ROS 2 for industrial/lightweight robots.
  [paper](https://arxiv.org/html/2608.23320v1). Directly relevant to our
  deployment layer.
- **RoboBridge** — modular framework to bridge policies to real-world agents.
  [paper](https://dev.alphaxiv.org/abs/2607.27881).
- LeRobot ships a ROS 2 bridge for SO-100 arms; the same pattern generalizes to
  any ROS robot (we replicate it for the Panda/UR5 in Gazebo).

---

## 3. SLAM & navigation (our stretch goal)

The classic, well-supported stack is **ROS 2 + Nav2 + a SLAM backend**:

| Backend | Type | Notes |
|---|---|---|
| **slam_toolbox** | 2D lidar | Easiest, ROS-native, good docs |
| **RTAB-Map** | RGB-D / 3D | Visual + lidar, loop closure, great for RGB-D |
| **Cartographer** | 2D/3D | Google; mature but maintenance slowed |
| **NICE-SLAM / NeRF-SLAM** | Neural / 3D | Research frontier, dense reconstruction |

Mobile-manipulator projects combine a VLA (for the arm) with Nav2/SLAM (for the
base). That is a natural phase-2 extension of this repo.

- [ROS 2 survey](https://dl.acm.org/doi/full/10.1145/3815113)
- [Sim-to-real RL transfer: Isaac Sim → Gazebo → real ROS 2 robots](https://export.arxiv.org/abs/2501.02902)

---

## 4. Simulation

| Simulator | GPU needed? | ROS 2 | Best for |
|---|---|---|---|
| **Gazebo Classic** | No (CPU ok) | excellent (Humble) | **our choice** — zero GPU friction |
| **Gazebo Sim (Ignition)** | No | good (Jazzy) | modern alternative |
| **NVIDIA Isaac Sim / Lab** | **Yes** (NVIDIA) | good | high-fidelity, RL, sim-to-real |
| **MuJoCo / PyBullet** | No | via bridges | fast physics, RL |

Since this project targets **no NVIDIA GPU**, Gazebo Classic + ROS 2 Humble is
the pragmatic choice; the design is simulator-agnostic so Isaac Sim can be
swapped in later.

---

## 5. Datasets (Hugging Face)

Pre-collected manipulation data you can fine-tune on immediately (all on the HF
Hub in LeRobot format):

- **ALOHA / ACT** datasets — bimanual tabletop manipulation
- **DROID** — 76k trajectories, diverse real-world tasks
- **Open X-Embodiment (OXE)** — the big cross-embodiment collection
- **SO-100 / SO-101** — cheap open-source arm data
- **AgiBot / AgiBot-World** — large-scale Chinese robot data

For a coherent first fine-tune, use a **single-robot, single-task** LeRobot
dataset (e.g. an ALOHA or SO-100 subset), then mix in your own Gazebo-collected
trajectories.

---

## 6. Where this project sits

There is a clear, well-trodden path from "no robot, no GPU" to "language-driven
arm in simulation":

1. **Collect** trajectories by teleoperating the arm in Gazebo (or use HF data).
2. **Fine-tune** SmolVLA with LoRA on Colab.
3. **Evaluate** the policy back in Gazebo via a ROS 2 action bridge.

The two genuinely novel/active areas to watch for your "state of the art" write-up
are (a) small-VLA distillation (SmolVLA-class) and (b) sim-to-real transfer of
VLA policies — both have strong 2025–2026 literature.
