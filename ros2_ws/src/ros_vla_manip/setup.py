import os
from glob import glob

from setuptools import find_packages, setup

package_name = "ros_vla_manip"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Laissy Aurélien",
    maintainer_email="you@example.com",
    description="ROS 2 + Gazebo VLA manipulation: bring-up and SmolVLA inference bridge.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "vla_bridge = ros_vla_manip.vla_bridge:main",
        ],
    },
)
