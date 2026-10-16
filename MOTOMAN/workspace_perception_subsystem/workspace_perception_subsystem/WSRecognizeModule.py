#!/usr/bin/env python
# coding: UTF-8

#####################################################################################################################
#このノードは．WS内環境認識サブシステムを作成したモジュールです．　　　　　　　　　　　　　　　 #
#===================================================================================================================#
#バージョン管理
#===================================================================================================================#
#ver. 0.1:  基本実装（Linux版）　　　2023/09/28
#===================================================================================================================#
#依存ノード
#===================================================================================================================#
#このノードはLinuxでのみ利用可能です．
#===================================================================================================================#

#python,TFのライブラリを使用
import rclpy
from rclpy.node import Node
import time
# from rospy.topics import Publisher, Subscriber

from std_msgs.msg import *
from geometry_msgs.msg import *

class WorkSpaceRecogniseNode(Node):
    def __init__(self):
        super().__init__('ws_recognise')
        self.pub = self.create_publisher(Float32, 'recg_data', 10)

    def send_ws_recognise(self):
        rate_hz = 10.0
        period = 1.0 / rate_hz
        while rclpy.ok():
            sensor = Float32()
            sensor.data = 1.0
            self.pub.publish(sensor)
            time.sleep(period)


def main():
    try:
        rclpy.init()
        node = WorkSpaceRecogniseNode()
        node.send_ws_recognise()
    except Exception as e:
        pass


if __name__ == '__main__':
    main()