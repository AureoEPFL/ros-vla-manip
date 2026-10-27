"""Launch the VLA bridge node (SmolVLA inference -> arm actions).

Usage:
    ros2 launch ros_vla_manip vla_bridge.launch.py model_id:=<your-hf>/my-smolvla
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

    model_id = LaunchConfiguration("model_id")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "model_id",
                default_value="lerobot/smolvla_base",
                description="Hugging Face model id (base or fine-tuned LoRA).",
            ),
            Node(
                package="ros_vla_manip",
                executable="vla_bridge",
                name="vla_bridge",
                output="screen",
                parameters=[config_path, {"model_id": model_id}],
            ),
        ]
    )
