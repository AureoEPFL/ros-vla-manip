# Simulation assets

- `worlds/` — Gazebo world files (`.world`)
- `robots/` — robot descriptions (URDF / xacro), e.g. Franka Panda, UR5
- `launch/` — Gazebo + MoveIt bring-up launch files

## Default robot

Franka Emika Panda (7-DOF + gripper), the most common arm in VLA research.
UR5 is a drop-in alternative.

## Bring-up (from `ros2_ws`)

```bash
ros2 launch ros_vla_manip bringup.launch.py
```

Starts Gazebo, spawns the arm, and launches MoveIt.
