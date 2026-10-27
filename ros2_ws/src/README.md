# ros2_ws — ROS 2 workspace

Custom ROS 2 packages for this project.

Planned packages:

- `ros_vla_manip` — Gazebo/MoveIt bring-up launch files + the VLA inference bridge node.
- `vla_bridge` (inside `ros_vla_manip`) — subscribes to camera + state, runs SmolVLA, publishes actions.

## Build

```bash
colcon build --symlink-install
source install/setup.bash
```

## Bring-up

```bash
ros2 launch ros_vla_manip bringup.launch.py
```

## VLA bridge topics

| Topic | Type | Direction |
|---|---|---|
| `/camera/image_raw` | `sensor_msgs/Image` | in |
| `/joint_states` | `sensor_msgs/JointState` | in |
| `/vla/instruction` | `std_msgs/String` | in (language goal) |
| `/vla/ee_action` | `geometry_msgs/Pose` | out |
| `/vla/gripper` | `std_msgs/Float32` | out |
