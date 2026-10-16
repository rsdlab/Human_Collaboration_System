#!/usr/bin/env python3
# coding: UTF-8

import rclpy
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.time import Time

import tf2_ros
from tf_transformations import quaternion_from_euler

from geometry_msgs.msg import PoseStamped
from shape_msgs.msg import SolidPrimitive

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    Constraints,
    JointConstraint,
    PositionConstraint,
    OrientationConstraint,
)

from .CollaborationToolModule import CollaborationTool


# === MoveIt2 settings ===
MOVE_GROUP_COMMAND_NAME = 'motoman_gp8'
MOVE_FRAME_NAME = 'base_link'

# ROS2 MoveIt config の SRDF で確認した planning group の tip link.
# ROS1 では grasp_point を使用していたため、
# 実際の TCP との対応については今後確認が必要.
MOVE_LINK_NAME = 'link_6_t'

MOVE_PLANNING_PIPELINE = 'ompl'
MOVE_PLANNER_ID = 'RRTConnect'

# 現在は controller 設定が未確認のため、
# MoveIt2 には planning のみ要求する.
MOVE_PLAN_ONLY = True


class MovePlanner:

    def __init__(self):
        self.node = CollaborationTool.get_node()

        # MoveIt2 MoveGroup Action Client
        self.move_group_client = ActionClient(
            self.node,
            MoveGroup,
            '/move_action'
        )

        # TF2
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(
            self.tf_buffer,
            self.node
        )

        CollaborationTool.loginfo(
            'MovePlanner initialized for MoveIt2'
        )

    # =========================================================
    # Public API
    # =========================================================

    def grasp_position(self, x, y, z, velocity):
        pose = self.target_pose(x, y, z)

        goal_msg = self.create_pose_goal(
            pose,
            velocity
        )

        return self.send_goal(goal_msg)

    def get_transform(self, target_frame, source_frame, timeout_sec=4.0):
        """
        TFを取得する。
        TransformListener作成直後でもTFを受信できるように、
        can_transform()を確認しながらNodeをspinする。
        """

        end_time = self.node.get_clock().now() + Duration(
            seconds=timeout_sec
        )

        while rclpy.ok():
            if self.tf_buffer.can_transform(
                target_frame,
                source_frame,
                Time()
            ):
                try:
                    return self.tf_buffer.lookup_transform(
                        target_frame,
                        source_frame,
                        Time()
                    )

                except Exception as e:
                    CollaborationTool.logwarn(
                        'Failed to lookup transform: {}'.format(e)
                    )
                    return None

            if self.node.get_clock().now() >= end_time:
                CollaborationTool.logwarn(
                    'Timeout waiting for transform: {} -> {}'.format(
                        target_frame,
                        source_frame
                    )
                )
                return None



    def current_position(
        self,
        offset_x,
        offset_y,
        offset_z,
        velocity
    ):
        transform = self.get_transform(
            MOVE_FRAME_NAME,
            MOVE_LINK_NAME
        )

        if transform is None:
            CollaborationTool.logwarn(
                'Failed to get current pose.'
            )
            return False

        x = transform.transform.translation.x + offset_x
        y = transform.transform.translation.y + offset_y
        z = transform.transform.translation.z + offset_z

        pose = self.target_pose(x, y, z)

        goal_msg = self.create_pose_goal(
            pose,
            velocity
        )

        return self.send_goal(goal_msg)

    def tf_position(
        self,
        offset_x,
        offset_y,
        offset_z,
        velocity,
        tf_pose
    ):
        transform = self.get_transform(
            MOVE_FRAME_NAME,
            tf_pose
        )

        if transform is None:
            CollaborationTool.loginfo(
                'Not found frame: {}'.format(tf_pose)
            )
            return False

        x = transform.transform.translation.x + offset_x
        y = transform.transform.translation.y + offset_y

        # ROS1版の動作を維持し、
        # z はTFの値ではなくoffset_zをそのまま使用する.
        z = offset_z

        pose = self.target_pose(x, y, z)

        goal_msg = self.create_pose_goal(
            pose,
            velocity
        )

        return self.send_goal(goal_msg)

    def joint_value(
        self,
        joint_1_s,
        joint_2_l,
        joint_3_u,
        joint_4_r,
        joint_5_b,
        joint_6_t,
        vel
    ):
        joint_values = [
            joint_1_s,
            joint_2_l,
            joint_3_u,
            joint_4_r,
            joint_5_b,
            joint_6_t
        ]

        goal_msg = self.create_joint_goal(
            joint_values,
            vel
        )

        return self.send_goal(goal_msg)

    def initial_pose(self):
        # ROS1版 initial_pose() と同じ目標値.
        joint_values = [
            0.0,
            0.0,
            0.0,
            0.0,
            -1.57,
            0.0
        ]

        goal_msg = self.create_joint_goal(
            joint_values,
            1.0
        )

        return self.send_goal(goal_msg)

    # =========================================================
    # Pose / Goal creation
    # =========================================================

    def target_pose(self, x, y, z):
        quat = quaternion_from_euler(
            0.0,
            -3.14,
            -1.57
        )

        pose = PoseStamped()
        pose.header.frame_id = MOVE_FRAME_NAME
        pose.header.stamp = self.node.get_clock().now().to_msg()

        pose.pose.orientation.x = quat[0]
        pose.pose.orientation.y = quat[1]
        pose.pose.orientation.z = quat[2]
        pose.pose.orientation.w = quat[3]

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z

        return pose

    def create_pose_goal(self, pose, velocity):
        goal_msg = self.create_base_goal(velocity)

        constraints = Constraints()

        # === Position constraint ===
        position_constraint = PositionConstraint()
        position_constraint.header.frame_id = MOVE_FRAME_NAME
        position_constraint.link_name = MOVE_LINK_NAME

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.SPHERE
        primitive.dimensions = [0.001]

        position_constraint.constraint_region.primitives.append(
            primitive
        )

        position_constraint.constraint_region.primitive_poses.append(
            pose.pose
        )

        position_constraint.weight = 1.0

        # === Orientation constraint ===
        orientation_constraint = OrientationConstraint()
        orientation_constraint.header.frame_id = MOVE_FRAME_NAME
        orientation_constraint.link_name = MOVE_LINK_NAME
        orientation_constraint.orientation = pose.pose.orientation

        orientation_constraint.absolute_x_axis_tolerance = 0.01
        orientation_constraint.absolute_y_axis_tolerance = 0.01
        orientation_constraint.absolute_z_axis_tolerance = 0.01
        orientation_constraint.weight = 1.0

        constraints.position_constraints.append(
            position_constraint
        )

        constraints.orientation_constraints.append(
            orientation_constraint
        )

        goal_msg.request.goal_constraints.append(
            constraints
        )

        return goal_msg

    def create_joint_goal(self, joint_values, velocity):
        goal_msg = self.create_base_goal(velocity)

        joint_names = [
            'joint_1_s',
            'joint_2_l',
            'joint_3_u',
            'joint_4_r',
            'joint_5_b',
            'joint_6_t'
        ]

        constraints = Constraints()

        for joint_name, joint_value in zip(
            joint_names,
            joint_values
        ):
            joint_constraint = JointConstraint()

            joint_constraint.joint_name = joint_name
            joint_constraint.position = float(joint_value)

            joint_constraint.tolerance_above = 0.001
            joint_constraint.tolerance_below = 0.001
            joint_constraint.weight = 1.0

            constraints.joint_constraints.append(
                joint_constraint
            )

        goal_msg.request.goal_constraints.append(
            constraints
        )

        return goal_msg

    def create_base_goal(self, velocity):
        goal_msg = MoveGroup.Goal()

        goal_msg.request.group_name = MOVE_GROUP_COMMAND_NAME
        goal_msg.request.pipeline_id = MOVE_PLANNING_PIPELINE
        goal_msg.request.planner_id = MOVE_PLANNER_ID

        goal_msg.request.num_planning_attempts = 1
        goal_msg.request.allowed_planning_time = 5.0

        goal_msg.request.max_velocity_scaling_factor = float(
            velocity
        )

        goal_msg.request.max_acceleration_scaling_factor = float(
            velocity
        )

        goal_msg.planning_options.plan_only = MOVE_PLAN_ONLY
        goal_msg.planning_options.look_around = False
        goal_msg.planning_options.replan = True
        goal_msg.planning_options.replan_attempts = 1

        return goal_msg

    # =========================================================
    # MoveGroup Action
    # =========================================================

    def send_goal(self, goal_msg):
        if not self.move_group_client.wait_for_server(
            timeout_sec=5.0
        ):
            CollaborationTool.logwarn(
                'MoveGroup action server is not available.'
            )
            return False

        future = self.move_group_client.send_goal_async(
            goal_msg
        )

        if not CollaborationTool.wait_for_future(
            future,
            timeout_sec=10.0
        ):
            CollaborationTool.logwarn(
                'Timed out waiting for MoveGroup goal response.'
            )
            return False

        goal_handle = future.result()

        if goal_handle is None:
            CollaborationTool.logwarn(
                'Failed to send MoveGroup goal.'
            )
            return False

        if not goal_handle.accepted:
            CollaborationTool.logwarn(
                'MoveGroup goal was rejected.'
            )
            return False

        result_future = goal_handle.get_result_async()

        if not CollaborationTool.wait_for_future(
            result_future,
            timeout_sec=30.0
        ):
            CollaborationTool.logwarn(
                'Timed out waiting for MoveGroup result.'
            )
            return False

        result = result_future.result()

        if result is None:
            CollaborationTool.logwarn(
                'Failed to receive MoveGroup result.'
            )
            return False

        error_code = result.result.error_code.val

        if error_code != 1:
            CollaborationTool.logwarn(
                'MoveIt planning failed. error_code={}'.format(
                    error_code
                )
            )
            return False

        CollaborationTool.loginfo(
            'MoveIt planning succeeded.'
        )

        return True