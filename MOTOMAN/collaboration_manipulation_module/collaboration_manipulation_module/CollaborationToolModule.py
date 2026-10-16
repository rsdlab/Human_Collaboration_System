#!/usr/bin/env python3
# coding: UTF-8

import threading
import time

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.time import Time
from rclpy.executors import SingleThreadedExecutor


class CollaborationTool:
    _node = None
    _executor = None
    _executor_thread = None

    # ノードを初期化する.
    @classmethod
    def init_node(cls, name):
        if not rclpy.ok():
            rclpy.init()

        if cls._node is None:
            cls._node = Node(name)

        return cls._node

    # 生成済みNodeを取得する.
    @classmethod
    def get_node(cls):
        if cls._node is None:
            raise RuntimeError(
                "CollaborationTool.init_node() must be called before get_node()."
            )
        return cls._node

    # Executorを開始する.
    @classmethod
    def start_executor(cls):
        node = cls.get_node()

        # すでにExecutorが動作している場合は何もしない.
        if (
            cls._executor_thread is not None
            and cls._executor_thread.is_alive()
        ):
            return

        cls._executor = SingleThreadedExecutor()
        cls._executor.add_node(node)

        def spin_executor():
            try:
                cls._executor.spin()
            except Exception as e:
                print('Executor thread exception:', repr(e), flush=True)

        cls._executor_thread = threading.Thread(
            target=spin_executor,
            daemon=True
        )
        cls._executor_thread.start()

    # Executorを停止する.
    @classmethod
    def stop_executor(cls):
        if cls._executor is not None:
            cls._executor.shutdown()
            cls._executor = None

        if cls._executor_thread is not None:
            cls._executor_thread.join()
            cls._executor_thread = None

    # Futureの完了を待つ.
    # callback自体は専用Executorスレッドで処理する.
    @classmethod
    def wait_for_future(cls, future, timeout_sec=None):
        start_time = time.monotonic()

        while rclpy.ok() and not future.done():
            if (
                timeout_sec is not None
                and time.monotonic() - start_time >= timeout_sec
            ):
                return False

            time.sleep(0.01)

        return future.done()

    # ROS2を終了する.
    @classmethod
    def signal_shutdown(cls, reason):
        if cls._node is not None:
            cls._node.get_logger().info(
                'Shutdown: {}'.format(reason)
            )

        cls.stop_executor()

        if cls._node is not None:
            cls._node.destroy_node()
            cls._node = None

        if rclpy.ok():
            rclpy.shutdown()

    # サービス待機.
    # ROS2ではClientオブジェクトが必要になるため、
    # CollaborationCommunicationModule側で処理する.
    @classmethod
    def wait_for_service(cls, servicename):
        raise NotImplementedError(
            "wait_for_service() will be migrated with CollaborationClient."
        )

    # INFOログ.
    @classmethod
    def loginfo(cls, message, *args, **kwargs):
        node = cls.get_node()

        if args:
            try:
                message = message % args
            except TypeError:
                pass

        node.get_logger().info(str(message))

    # WARNログ.
    @classmethod
    def logwarn(cls, message, *args, **kwargs):
        node = cls.get_node()

        if args:
            try:
                message = message % args
            except TypeError:
                pass

        node.get_logger().warning(str(message))

    # 指定時間待機する.
    @classmethod
    def wait_time(cls, seconds):
        time.sleep(seconds)

    # ROS2 Timeを生成する.
    @classmethod
    def create_time(cls, seconds=0.0):
        return Time(seconds=seconds)

    # ROS2 Durationを生成する.
    @classmethod
    def create_duration(cls, seconds):
        return Duration(seconds=seconds)

    # ROS2が終了しているか確認する.
    @classmethod
    def is_shutdown(cls):
        return not rclpy.ok()