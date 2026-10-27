# ROS 2 Humble + Gazebo Classic (CPU) development image

FROM ros:humble

ENV DEBIAN_FRONTEND=noninteractive

# Base ROS + Gazebo + MoveIt
RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-humble-gazebo-ros-pkgs \
      ros-humble-moveit \
      ros-humble-moveit-visual-tools \
      ros-humble-ros2-control \
      ros-humble-ros2-controllers \
      ros-humble-gripper-controllers \
      ros-humble-joint-state-publisher \
      ros-humble-joint-trajectory-controller \
      ros-humble-xacro \
      ros-humble-rviz2 \
      python3-pip \
      python3-colcon-common-extensions \
      git \
      nano \
      && rm -rf /var/lib/apt/lists/*

# Convenience: bashrc auto-sources ROS
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc

WORKDIR /ros2_ws

# Entry: build the workspace on start (override with `command:` as needed)
CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && colcon build --symlink-install && source install/setup.bash && exec bash"]
