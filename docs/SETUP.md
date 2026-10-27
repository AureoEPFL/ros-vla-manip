# Setup Guide

Two independent environments, connected only through the Hugging Face Hub:

1. **Simulation** — ROS 2 + Gazebo on Linux (this machine, CPU is fine).
2. **Training** — Google Colab (free T4 GPU).

You do **not** need a local GPU.

---

## A. Simulation environment

ROS 2 requires Linux. On Windows, use **WSL2** or **Docker**.

### Option 1 — Docker (recommended, most reproducible)

```bash
cd docker
docker compose up -d
docker compose exec ros bash
```

Inside the container, build and source the workspace:

```bash
cd /ros2_ws
colcon build --symlink-install
source install/setup.bash
```

> Requires Docker Desktop with WSL2 backend. See [`docker/Dockerfile`](../docker/Dockerfile).

### Option 2 — WSL2 (Ubuntu 22.04) native

```bash
# install ROS 2 Humble (see official docs for full steps)
sudo apt update && sudo apt install -y ros-humble-desktop

# Gazebo Classic + MoveIt 2
sudo apt install -y ros-humble-gazebo-ros-pkgs ros-humble-moveit

# source
source /opt/ros/humble/setup.bash
```

Official guides:
- [ROS 2 Humble install](https://docs.ros.org/en/humble/Installation.html)
- [MoveIt 2 install](https://moveit.picknik.ai/main/doc/tutorials/getting_started/getting_started.html)

### Bring up the arm

```bash
# (from ros2_ws)
ros2 launch panda_moveit_config demo.launch.py        # MoveIt demo (no physics)
ros2 launch ros_vla_manip bringup.launch.py           # Gazebo + MoveIt bring-up
```

First milestone: teleoperate the arm (MoveIt RViz) and confirm you can command
end-effector poses before touching the VLA.

---

## B. Training environment (Google Colab)

1. Open [`vla/finetune_smolvla.ipynb`](../vla/finetune_smolvla.ipynb).
2. In Colab: **File → Upload notebook** (or open from GitHub).
3. Run it. It will:
   - install LeRobot,
   - log you in to the Hugging Face Hub (with a write token),
   - download a LeRobot dataset,
   - fine-tune `lerobot/smolvla_base`,
   - push the adapter to the Hub.

Free Colab (T4, 16 GB) is enough for a small LoRA run on SmolVLA. Use a small
dataset (~1k episodes) and few epochs for the first smoke test.

> Get a HF token at <https://huggingface.co/settings/tokens> (needs *write* scope).

---

## C. Deployment (sim + policy)

1. Start the simulation (section A).
2. Launch the VLA bridge node, pointing it at your fine-tuned model:

```bash
ros2 run ros_vla_manip vla_bridge \
  --ros-args -p model_id:=<your-hf-username>/<your-smolvla-lora>
```

3. Publish a language instruction:

```bash
ros2 topic pub /vla/instruction std_msgs/msg/String "data: 'pick up the red cube'"
```

The arm should move accordingly.

---

## Verification checklist

- [ ] Gazebo opens and renders the arm (CPU).
- [ ] MoveIt can plan/move the arm in RViz.
- [ ] Colab fine-tune completes and pushes a LoRA to the Hub.
- [ ] The bridge node loads the checkpoint and produces actions.
- [ ] Language instruction → arm motion in simulation.
