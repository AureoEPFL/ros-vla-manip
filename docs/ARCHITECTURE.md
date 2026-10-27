# Architecture

System design and data flow for the `ros-vla-manip` pipeline.

## High-level view

```
                        Hugging Face Hub
                              │
        ┌─────────────────────┼─────────────────────┐
        │ upload dataset      │ download checkpoint │
        ▼                     │                     ▼
┌───────────────┐     ┌───────────────┐     ┌──────────────────┐
│  Data          │     │  Training      │     │  Simulation       │
│  collection    │     │  (Colab, T4)   │     │  (local, CPU)     │
│  (Gazebo)      │     │  LeRobot+LoRA  │     │  Gazebo + ROS 2   │
└───────┬───────┘     └───────────────┘     └────────▲─────────┘
        │   LeRobot-format episodes                   │
        └──────────────────┐                         │
                           │                         │
                 ┌─────────▼─────────────────────────┴──┐
                 │   VLA inference node (ROS 2)          │
                 │   images → policy → joint/EE action   │
                 └──────────────────────────────────────┘
```

## Components

### 1. Simulation (`sim/`, `ros2_ws/`)
- **Gazebo Classic** provides the physics and rendering (CPU-rendered).
- **ROS 2 Humble** is the middleware: every actuator/sensor is a topic.
- **MoveIt 2** handles IK/motion planning for teleop and scripted policies.
- The **robot** (Franka Panda by default) is spawned from a URDF/xacro.

### 2. Data collection (`vla/`)
Two sources of LeRobot-format data:
- **Downstream:** Hugging Face datasets (ALOHA, SO-100, DROID, …).
- **Upstream:** our own episodes recorded by teleoperating (or scripting) the arm
  in Gazebo. Each episode is a sequence of `(image, state, action, language)`
  frames — LeRobot's `push_dataset_to_hub` stores them.

### 3. Training (`vla/finetune_smolvla.ipynb`)
- Runs on **Google Colab (free T4)** — no local GPU.
- `lerobot/smolvla_base` (450M) — fine-tunes the action expert while freezing the vision encoder.
- Outputs a compact LoRA checkpoint pushed to the Hub.

### 4. Deployment / inference (`ros2_ws/src/vla_bridge/`)
A ROS 2 node that:
1. Subscribes to the camera topic (RGB) and the robot state.
2. Feeds the image + a language instruction to the fine-tuned SmolVLA.
3. Publishes the predicted end-effector action to MoveIt / the arm controller.
4. Loops at the policy's control frequency.

This mirrors the [ROS2SmolVLA](https://arxiv.org/html/2608.23320v1) pattern.

## Data contract (LeRobot format)

| Field | Type | Meaning |
|---|---|---|
| `observation.state` | float[] | robot proprioception (joints/EE) |
| `observation.images.cam` | uint8 (H,W,C) | camera frame |
| `action` | float[] | commanded action (EE delta pose + gripper) |
| `language_instruction` | str | the task sentence |

## Control loop

```
loop:
    img   = camera.subscribe()
    state = robot.get_state()
    action = vla.predict(img, instruction, state)   # e.g. 20 Hz
    robot.apply(action)                              # MoveIt / joint controller
```

## Extension: SLAM (phase 2)

Swap the fixed-base arm for a mobile manipulator and add Nav2 + slam_toolbox/RTAB-Map.
The VLA bridge is unchanged; the base becomes an additional controllable DOF.
