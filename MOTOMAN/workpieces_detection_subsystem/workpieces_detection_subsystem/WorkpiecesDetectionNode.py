#!/usr/bin/env python3
# coding: UTF-8
#####################################################################################################################
# このノードは，ワーク検出モジュールを実装するために作成したコードです．
# ==================================================================================================================#
# バージョン管理
# ==================================================================================================================#
# ver. 0.1: 基本実装（Linux版） 2023/06/28
# ==================================================================================================================#
# 依存ノード
# ==================================================================================================================#
# このノードはLinuxでのみ利用可能です．
# ==================================================================================================================#

import os
import yaml

import rclpy
from rclpy.node import Node

from ament_index_python.packages import get_package_share_directory

from aruco_msgs.msg import MarkerArray

from collaboration_manipulation_message.msg import WorkDetectionResult
from collaboration_manipulation_message.srv import DetectWorkpieces


class WorkDetect(Node):

    def __init__(self):
        super().__init__('work_detection_node')

        self.length_sub = self.create_subscription(
            MarkerArray,
            '/aruco_marker_publisher/markers',
            self.ArucoCallback,
            10
        )

        self.setup_req = self.create_service(
            DetectWorkpieces,
            'detect_workpieces_service',
            self.pose_request
        )

        self.aruco_data = []

        self.get_logger().info("Initialization done")

    def ArucoCallback(self, aruco_):
        self.aruco_data = aruco_.markers

    def pose_request(self, request, response):
        # ワーク検知処理.

        # リクエストの確認
        self.get_logger().info("Request Data:")
        self.get_logger().info(str(request))

        self.get_logger().info("Aruco Data:")
        self.get_logger().info(str(self.aruco_data))

        set_data = WorkDetectionResult()

        if request.task_command_id == 1:

            config = None

            if request.work_type_id == 1:
                package_path = get_package_share_directory(
                    'workpieces_detection_subsystem'
                )

                config_path = os.path.join(
                    package_path,
                    'config',
                    'sandwich_id.yaml'
                )

                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)

            elif request.work_type_id == 2:
                package_path = get_package_share_directory(
                    'workpieces_detection_subsystem'
                )

                config_path = os.path.join(
                    package_path,
                    'config',
                    'drink_id.yaml'
                )

                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)

            # 該当データ検索.
            if config is not None:
                self.SerchData(
                    config,
                    request,
                    set_data
                )

            self.get_logger().info(str(set_data.pose))

            set_data.work_type_id = request.work_type_id

            response.work_detection_results.work_detection_results.append(
                set_data
            )

            self.get_logger().info(
                str(
                    response.work_detection_results.work_detection_results
                )
            )

        elif request.task_command_id == 2:
            # 未実装
            set_data.work_type_id = request.work_type_id

            response.work_detection_results.work_detection_results.append(
                set_data
            )

        else:
            # 定義されていない作業指令IDの場合
            set_data.work_type_id = request.work_type_id

            response.work_detection_results.work_detection_results.append(
                set_data
            )

        return response

    # 範囲内のワーク検索.
    def SerchData(self, config, request, set_data):
        if config and self.aruco_data:
            for i in range(len(self.aruco_data)):

                if self.aruco_data[i].id == config[i]:

                    if (
                        request.target_area.start_point.x
                        < self.aruco_data[i].pose.pose.position.x
                        < request.target_area.end_point.x
                        and
                        request.target_area.start_point.y
                        < self.aruco_data[i].pose.pose.position.y
                        < request.target_area.end_point.y
                        and
                        request.target_area.start_point.z
                        < self.aruco_data[i].pose.pose.position.z
                        < request.target_area.end_point.z
                    ):
                        set_data.pose.position.x = (
                            self.aruco_data[i].pose.pose.position.x
                        )
                        set_data.pose.position.y = (
                            self.aruco_data[i].pose.pose.position.y
                        )
                        set_data.pose.position.z = (
                            self.aruco_data[i].pose.pose.position.z
                        )

                        set_data.pose.orientation.x = (
                            self.aruco_data[i].pose.pose.orientation.x
                        )
                        set_data.pose.orientation.y = (
                            self.aruco_data[i].pose.pose.orientation.y
                        )
                        set_data.pose.orientation.z = (
                            self.aruco_data[i].pose.pose.orientation.z
                        )
                        set_data.pose.orientation.w = (
                            self.aruco_data[i].pose.pose.orientation.w
                        )

                        self.get_logger().info(str(set_data.pose))

                        return None


def main(args=None):
    rclpy.init(args=args)

    wd = WorkDetect()

    try:
        rclpy.spin(wd)

    except KeyboardInterrupt:
        pass

    finally:
        wd.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()