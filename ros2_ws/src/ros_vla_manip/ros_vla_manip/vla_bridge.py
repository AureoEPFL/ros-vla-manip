"""SmolVLA inference bridge for ROS 2.

Subscribes to a camera image, the robot joint state, and a natural-language
instruction; runs a Vision-Language-Action policy (SmolVLA via LeRobot); and
publishes end-effector actions to drive a simulated arm (Gazebo + MoveIt).

This node mirrors the ROS2SmolVLA pattern. It is a working skeleton: wire the
observation builder to your exact camera topic and joint ordering, and route the
published action to your MoveIt / joint-trajectory controller.

Required (GPU machine or Colab-side inference):
    pip install lerobot torch
"""

from typing import Dict, Optional

import numpy as np
import rclpy
from rclpy.node import Node

from cv_bridge import CvBridge
from geometry_msgs.msg import Pose
from sensor_msgs.msg import Image, JointState
from std_msgs.msg import Float32, String

# LeRobot / SmolVLA are imported lazily so the node can start (and report a
# clear error) even when the training stack is not installed on the sim machine.
try:
    import torch
    from lerobot.policies.smolvla.configuration_smolvla import SmolVLAConfig
    from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy

    LEROBOT_AVAILABLE = True
except ImportError:  # pragma: no cover - environment-dependent
    torch = None
    SmolVLAConfig = SmolVLAPolicy = None
    LEROBOT_AVAILABLE = False


class VLABridge(Node):
    """ROS 2 node that wraps a LeRobot SmolVLA policy as an action publisher."""

    def __init__(self) -> None:
        super().__init__("vla_bridge")

        # ---- Parameters -----------------------------------------------------
        self.declare_parameter("model_id", "lerobot/smolvla_base")
        self.declare_parameter("camera_topic", "/camera/image_raw")
        self.declare_parameter("joint_state_topic", "/joint_states")
        self.declare_parameter("instruction_topic", "/vla/instruction")
        self.declare_parameter("ee_action_topic", "/vla/ee_action")
        self.declare_parameter("gripper_topic", "/vla/gripper")
        self.declare_parameter("control_hz", 20.0)
        self.declare_parameter("device", "cuda")
        self.declare_parameter("image_size", 256)  # resize shortest side

        self._model_id = self.get_parameter("model_id").value
        self._camera_topic = self.get_parameter("camera_topic").value
        self._joint_state_topic = self.get_parameter("joint_state_topic").value
        self._instruction_topic = self.get_parameter("instruction_topic").value
        self._ee_action_topic = self.get_parameter("ee_action_topic").value
        self._gripper_topic = self.get_parameter("gripper_topic").value
        self._control_hz = self.get_parameter("control_hz").value
        self._device = self.get_parameter("device").value
        self._image_size = self.get_parameter("image_size").value

        # ---- State ----------------------------------------------------------
        self._bridge = CvBridge()
        self._latest_image: Optional[np.ndarray] = None
        self._latest_joint_state: Optional[np.ndarray] = None
        self._instruction: str = ""

        # ---- Load the policy ------------------------------------------------
        self._policy = self._load_policy()

        # ---- ROS interface --------------------------------------------------
        self._image_sub = self.create_subscription(
            Image, self._camera_topic, self._on_image, 1
        )
        self._joint_sub = self.create_subscription(
            JointState, self._joint_state_topic, self._on_joint_state, 1
        )
        self._instr_sub = self.create_subscription(
            String, self._instruction_topic, self._on_instruction, 1
        )
        self._ee_pub = self.create_publisher(Pose, self._ee_action_topic, 1)
        self._gripper_pub = self.create_publisher(Float32, self._gripper_topic, 1)

        self._timer = self.create_timer(1.0 / self._control_hz, self._step)
        self.get_logger().info(f"VLA bridge ready (model={self._model_id})")

    # ------------------------------------------------------------------ setup
    def _load_policy(self):
        if not LEROBOT_AVAILABLE:
            self.get_logger().error(
                "LeRobot/SmolVLA not installed. Run: pip install lerobot torch"
            )
            raise RuntimeError("LeRobot is required to run the VLA bridge.")

        if self._device == "cuda" and not torch.cuda.is_available():
            self.get_logger().warn("CUDA requested but unavailable; using CPU.")
            self._device = "cpu"

        self.get_logger().info(f"Loading SmolVLA policy from '{self._model_id}'...")
        policy = SmolVLAPolicy.from_pretrained(self._model_id)
        policy.to(self._device)
        policy.eval()
        return policy

    # ------------------------------------------------------------ callbacks
    def _on_image(self, msg: Image) -> None:
        # ROS Image -> numpy HxWxC uint8 (RGB)
        self._latest_image = self._bridge.imgmsg_to_cv2(msg, desired_encoding="rgb8")

    def _on_joint_state(self, msg: JointState) -> None:
        self._latest_joint_state = np.array(msg.position, dtype=np.float32)

    def _on_instruction(self, msg: String) -> None:
        self._instruction = msg.data
        self.get_logger().info(f"New instruction: {msg.data}")

    # ------------------------------------------------------------- control
    def _step(self) -> None:
        if self._latest_image is None or self._latest_joint_state is None:
            return  # wait for first observation

        observation = self._build_observation()
        action = self._policy.select_action(observation)  # torch.Tensor
        action = action.detach().cpu().numpy().squeeze(0)

        # De-normalize if the policy stores dataset output statistics.
        if getattr(self._policy, "normalize_outputs", None):
            action = self._policy.unnormalize_outputs({"action": action})["action"]

        self._publish_action(action)

    def _build_observation(self) -> Dict[str, np.ndarray]:
        """Assemble a LeRobot-style observation dict.

        Adapt the exact keys/ordering to your robot. SmolVLA expects at least
        'observation.images.<cam>' (HxWxC uint8) and 'observation.state' (1D).
        """
        image = self._resize_image(self._latest_image, self._image_size)
        # LeRobot policies expect a batch + channel-last uint8 image.
        image = image.astype(np.uint8)
        state = self._latest_joint_state.astype(np.float32)

        return {
            "observation.images.cam": image[None, ...],  # (1, H, W, C)
            "observation.state": state[None, ...],       # (1, D)
            "task": np.array([self._instruction], dtype=object),
        }

    @staticmethod
    def _resize_image(image: np.ndarray, size: int) -> np.ndarray:
        h, w = image.shape[:2]
        scale = size / min(h, w)
        new_h, new_w = int(round(h * scale)), int(round(w * scale))
        from PIL import Image as PILImage  # LeRobot depends on Pillow

        return np.asarray(PILImage.fromarray(image).resize((new_w, new_h)))

    def _publish_action(self, action: np.ndarray) -> None:
        """Interpret the raw action and publish it.

        For SmolVLA the action is typically a 7-D vector:
        [dx, dy, dz, droll, dpitch, dyaw, gripper]. Adjust the slicing to your
        action space. Here we emit an end-effector pose (translation only) and a
        separate gripper command.
        """
        # End-effector delta translation (first 3 dims).
        pose = Pose()
        pose.position.x = float(action[0])
        pose.position.y = float(action[1])
        pose.position.z = float(action[2])
        # Orientation left unchanged (identity) unless your action space has RPY.
        pose.orientation.w = 1.0
        self._ee_pub.publish(pose)

        # Gripper: last dim if present, else 0.0.
        gripper = float(action[-1]) if action.shape[0] >= 4 else 0.0
        self._gripper_pub.publish(Float32(data=gripper))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = VLABridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
