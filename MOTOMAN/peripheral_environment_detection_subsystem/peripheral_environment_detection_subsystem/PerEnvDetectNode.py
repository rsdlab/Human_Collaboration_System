#!/usr/bin/env python3
# coding: UTF-8

#####################################################################################################################
# このノードは，周辺環境計測モジュールを実装するために作成したコードです．
# ==================================================================================================================#
# バージョン管理
# ==================================================================================================================#
# ver. 0.1: 基本実装（Linux版） 2023/06/28
# ==================================================================================================================#
# 依存ノード
# ==================================================================================================================#
# このノードはLinuxでのみ利用可能です．
# ==================================================================================================================#

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32, Int32

from peripheral_environment_detection_subsystem.srv import SetMonitoringArea
from collaboration_manipulation_message.msg import MonitoringAreaList


class AreaIntrusionDetect(Node):

    def __init__(self):
        super().__init__('peripheral_environment_detection_node')

        self.result_pub = self.create_publisher(
            Int32,
            '/intrusion_result',
            10
        )

        self.length_sub = self.create_subscription(
            Float32,
            '/len_topic',
            self.UrgCallback,
            10
        )

        self.setup_req = self.create_service(
            SetMonitoringArea,
            'per_env_det_service',
            self.setup_request
        )

        self.setup_data = MonitoringAreaList()
        self.result_data = 0
        self.urg_data = 0.0
        self.basis_length = 0.3  # [m]

        self.timer = self.create_timer(
            0.1,
            self.mainloop
        )

        self.get_logger().info("Initialization done")

    def setup_request(self, request, response):
        self.setup_data.monitoring_areas = request.monitoring_areas.monitoring_areas

        if self.setup_data.monitoring_areas:
            self.get_logger().info("Setup succeeded")

            response.response = 1

            self.get_logger().info("Setup Data")
            self.get_logger().info(str(self.setup_data))
            self.get_logger().info("AreaIntrusionDetection start!")

        else:
            self.get_logger().info("Setup fail")
            response.response = 0

        return response

    def UrgCallback(self, urg_):
        self.urg_data = urg_.data

    def mainloop(self):
        if self.setup_data.monitoring_areas:
            msg = Int32()
            msg.data = self.result_data

            self.result_pub.publish(msg)

            self.setup_data = MonitoringAreaList()

            # TODO サブスクライバー作成.


def main(args=None):
    rclpy.init(args=args)

    aid = AreaIntrusionDetect()

    try:
        rclpy.spin(aid)

    except KeyboardInterrupt:
        pass

    finally:
        aid.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()