#!/usr/bin/env python3
# coding: UTF-8

#####################################################################################################################
# このノードは，排出位置検出サブモジュールを実装するために作成したコードです．
# ==================================================================================================================#
# バージョン管理
# ==================================================================================================================#
# ver. 0.1: 基本実装（Linux版） 2023/08/28
# ==================================================================================================================#
# 依存ノード
# ==================================================================================================================#
# このノードはLinuxでのみ利用可能です．
# ==================================================================================================================#

import rclpy
from rclpy.node import Node

from place_position_detection_subsystem.srv import DetectPlacePosition


class PlacePositionDetectionNode(Node):

    def __init__(self):
        super().__init__('place_position_detect_node')

        self.service = self.create_service(
            DetectPlacePosition,
            'place_position_detect_service',
            self.response_data
        )

        self.get_logger().info("Initialization done")

    def response_data(self, request, response):
        self.get_logger().info("Request Data:")
        self.get_logger().info(str(request))

        # リストを受信する.

        # 排出位置候補から排出場所を決める.

        response.place_position_detection_result.task_command_id = 1

        self.get_logger().info("Response Data:")
        self.get_logger().info(str(response))

        return response


def main(args=None):
    rclpy.init(args=args)

    node = PlacePositionDetectionNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()