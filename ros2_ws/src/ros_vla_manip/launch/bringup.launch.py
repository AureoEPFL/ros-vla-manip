"""Bring-up: Gazebo + MoveIt + VLA bridge.

NOTE: the Gazebo/MoveIt includes below reference packages you must install and
point at your robot description (see sim/). They are commented so the file is a
valid launch file today; uncomment and adjust once the arm spawns in Gazebo.

Usage:
    ros2 launch ros_vla_manip bringup.launch.py robot:=panda
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("ros_vla_manip")
    config_path = os.path.join(pkg_share, "config", "vla_bridge.yaml")

    robot = LaunchConfiguration("robot")

    # TODO(you): once the robot is installed, uncomment the real bring-up:
    #   gazebo = IncludeLaunchDescription(...)   # ros2 launch gazebo_ros gazebo.launch.py
    #   spawn  = Node(package="gazebo_ros", executable="spawn_entity.py", ...)
    #   moveit = IncludeLaunchDescription(...)   # panda_moveit_config demo.launch.py

    vla_bridge = Node(
        package="ros_vla_manip",
        executable="vla_bridge",
        name="vla_bridge",
        output="screen",
        parameters=[config_path],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "robot", default_value="panda", description="Robot name (panda/ur5)."
            ),
            vla_bridge,
        ]
    )
