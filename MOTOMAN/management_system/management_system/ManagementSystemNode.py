#!/usr/bin/env python3
# coding: UTF-8

#####################################################################################################################
#このノードは，上位アプリを実装するために作成したコードです．　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 
#===================================================================================================================#
#バージョン管理
#===================================================================================================================#
#ver. 0.1:  基本実装（Linux版）　　　2023/06/28
#10/05 test_server.pyと単体検証を行うために，クラス部分をコメントアウト→統合試験でも成功
#===================================================================================================================#
#依存ノード
#===================================================================================================================#
#このノードはLinuxでのみ利用可能です．
#===================================================================================================================#

from abc import ABCMeta
from abc import abstractmethod
import rclpy
from rclpy.node import Node
from collaboration_manipulation_message.msg import TargetArea, TaskCommandList, TaskCommand, PlaceAreaCandidatesList
from collaboration_manipulation_message.srv import SendTaskCommand, NotifyTaskStatus, NotifyTaskResult, NotifyTaskCompletion, TerminateSystem
from collaboration_manipulation_message.srv import TerminateSystem

# from management_system.srv import *
from std_msgs.msg import Empty
import sys
import os


# インポート
from collaboration_manipulation_module.EnumerateModule import EnumCommandReceiveState

class SystemManagementBase(metaclass=ABCMeta):
    """
    Base class that SystemManagement communication
    Define machine-dependent packages
    """
    @abstractmethod
    def execute(self, data):
        pass


class SystemManagementPublisher(SystemManagementBase):
    def __init__(self, node, topic_name, class_type):
        self.node = node
        self.pub = self.node.create_publisher(
            class_type,
            topic_name,
            10
        )

    def execute(self, data):
        self.pub.publish(data)


class SystemManagementClient(SystemManagementBase):
    def __init__(self, node, service_name, service_class):
        self.node = node
        self.service_name = service_name
        self.service_class = service_class

        self.client = self.node.create_client(
            service_class,
            service_name
        )

    def wait_for_service(self, timeout_sec=1.0):
        while not self.client.wait_for_service(
            timeout_sec=timeout_sec
        ):
            if not rclpy.ok():
                return False

            self.node.get_logger().info(
                'Waiting for service: {}'.format(
                    self.service_name
                )
            )

        return True

    def execute(self, request):
        try:
            if not self.wait_for_service():
                self.node.get_logger().warning(
                    '{} service is not available'.format(
                        self.service_name
                    )
                )
                return False

            future = self.client.call_async(request)

            rclpy.spin_until_future_complete(
                self.node,
                future
            )

            response = future.result()

            if response is None:
                self.node.get_logger().warning(
                    '{} returned no response'.format(
                        self.service_name
                    )
                )
                return False

            self.node.get_logger().info(
                str(response)
            )

            return response

        except Exception as e:
            self.node.get_logger().warning(
                'Service call failed: {}'.format(e)
            )
            return False


class SystemManagementServer(SystemManagementBase):
    def __init__(
        self,
        node,
        service_name,
        service_class,
        callback_impl
    ):
        self.node = node
        self.service_name = service_name

        self.server = self.node.create_service(
            service_class,
            service_name,
            callback_impl
        )

    def service_delete(self, msg=''):
        if msg:
            self.node.get_logger().info(msg)

        self.node.destroy_service(self.server)

    def execute(self, object):
        pass

# 作業結果コマンド受信クラス.
class TaskResultServer(SystemManagementServer):
    def __init__(self, node):
        super().__init__(
            node,
            'notify_task_result',
            NotifyTaskResult,
            self.recv_task_result
        )
        self.task_failed = 0

    def service_delete(self):
        super().service_delete(
            'notify_task_result deleted'
        )

    # 作業結果コマンド受信.
    def recv_task_result(self, request, response):
        self.node.get_logger().info(
            'TaskResult: {}'.format(
                request.task_result.task_result
            )
        )

        if request.task_result.task_result is False:
            self.task_failed = 1

        response.return_code = 1

        return response

    def get_task_failed(self):
        return self.task_failed

    def reset_task_result(self):
        self.task_failed = 0

# 作業完了コマンド受信クラス.
class TaskCompleteServer(SystemManagementServer):
    def __init__(self, node):
        super().__init__(
            node,
            'notify_task_completion',
            NotifyTaskCompletion,
            self.recv_task_complete
        )
        self.task_complete = 0

    def service_delete(self):
        super().service_delete(
            'notify_task_completion deleted'
        )

    # 作業完了コマンド受信.
    def recv_task_complete(self, request, response):
        self.node.get_logger().info(
            'TaskComplete: task_command_list_id={}'.format(
                request.task_command_list_id
            )
        )

        self.task_complete = 1
        response.return_code = 1

        return response

    def get_task_complete(self):
        return self.task_complete

    def reset_task_complete(self):
        self.task_complete = 0

# システム終了指令.
class TerminateSystemClient(SystemManagementClient):
    def __init__(self, node):
        super().__init__(
            node,
            'terminate_system',
            TerminateSystem
        )

    def execute(self):
        request = TerminateSystem.Request()
        request.empty = Empty()

        return super().execute(request)

# 作業開始指令.
class SendTaskCommandClient(SystemManagementClient):
    def __init__(self, node):
        super().__init__(
            node,
            'sned_command_service',
            SendTaskCommand
        )

    def execute(self):
        self.node.get_logger().info(
            '{} start'.format(self.__class__.__name__)
        )

        # 作業コマンド作成 ここから.

        # 作業コマンドリスト作成.
        set_task_command_list = TaskCommandList()

        set_task_command = TaskCommand()
        set_task_command.task_command_id = 1
        set_task_command.work_type_id = 1
        set_task_command.picking_count = 1

        # ワーク検知エリア設定.
        set_task_command.work_presence_area = TargetArea()

        set_task_command.work_presence_area.start_point.x = -2.0
        set_task_command.work_presence_area.start_point.y = -2.0
        set_task_command.work_presence_area.start_point.z = 0.0

        set_task_command.work_presence_area.end_point.x = 2.0
        set_task_command.work_presence_area.end_point.y = 2.0
        set_task_command.work_presence_area.end_point.z = 2.0

        # 廃棄候補エリアリスト作成.
        set_task_command.place_area_candidates = PlaceAreaCandidatesList()

        # 廃棄候補エリア作成.
        dis_area = TargetArea()

        dis_area.start_point.x = -2.0
        dis_area.start_point.y = -2.0
        dis_area.start_point.z = 0.0

        dis_area.end_point.x = 2.0
        dis_area.end_point.y = 2.0
        dis_area.end_point.z = 2.0

        set_task_command.place_area_candidates.place_area_candidates.append(
            dis_area
        )

        self.node.get_logger().info(
            str(set_task_command)
        )

        set_task_command_list.task_commands.append(
            set_task_command
        )

        # ここまで.

        request = SendTaskCommand.Request()
        request.task_commands = set_task_command_list

        ret = super().execute(request)

        self.node.get_logger().info(
            'result {}'.format(ret)
        )

        return ret

def wait(node, result: TaskResultServer, comp: TaskCompleteServer):
    while (
        not result.get_task_failed()
        and not comp.get_task_complete()
        and rclpy.ok()
    ):
        rclpy.spin_once(
            node,
            timeout_sec=0.05
        )


def main(cmd_type=None, args=None):
    rclpy.init(args=args)

    node = Node('management_system_node')

    result = TaskResultServer(node)
    complete = TaskCompleteServer(node)

    try:
        if cmd_type is None:
            node.get_logger().error(
                'error ! not selected'
            )
            return

        if cmd_type == 'command':
            cmd = SendTaskCommandClient(node)

            # 作業結果を初期化.
            result.reset_task_result()
            complete.reset_task_complete()

            # 送信完了まで繰り返す.
            while rclpy.ok():
                ret = cmd.execute()

                if ret is not False:
                    if ret.response == EnumCommandReceiveState.e_received():
                        break

                node.get_logger().info(
                    'command_retry'
                )

                rclpy.spin_once(
                    node,
                    timeout_sec=1.0
                )

            # 動作完了まで待つ.
            wait(
                node,
                result,
                complete
            )

            if result.get_task_failed() is True:
                return Empty()

        elif cmd_type == 'halt':
            cmd = TerminateSystemClient(node)
            cmd.execute()

        else:
            node.get_logger().error(
                'error ! unknown command: {}'.format(
                    cmd_type
                )
            )

    finally:
        result.service_delete()
        complete.service_delete()

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    args = sys.argv

    if len(args) == 1:
        print("error command xxxx [yyyy]")

    elif len(args) == 2:
        main(args[1])