#!/usr/bin/env python3
# coding: UTF-8

import rclpy
import tf2_ros

from std_msgs.msg import String
from geometry_msgs.msg import TransformStamped

from .CollaborationStateHeader import *
from .TransitionModule import Transition
from .CollaborationToolModule import CollaborationTool
from .CollaborationCommunicationModule import *
from .MovePlannerModule import MovePlanner

#定数の定義
DEFAULT_VELOCITY = 1.0
DEFAULT_DIRECTION = "side"
RETRY_COUNT_MAX = 3
PICK_1_OFFSET_X = 0.06
PICK_1_OFFSET_Y = -0.01
PICK_1_OFFSET_Z = 0.25
PICK_1_POSE = "marker_frame"
PICK_2_OFFSET_X = 0.0
PICK_2_OFFSET_Y = 0.0
PICK_2_OFFSET_Z = -0.18
PICK_2_VELOCITY = 1.0
PICK_2_DIRECTION = "side"
PICK_3_OFFSET_X = 0.0
PICK_3_OFFSET_Y = 0.0
PICK_3_OFFSET_Z = 0.20
PICK_3_VELOCITY = 1.0
PICK_3_DIRECTION = "side"
PLACE_1_OFFSET_X = 0.415
PLACE_1_OFFSET_Y = -0.320
PLACE_1_OFFSET_Z = 0.415
PLACE_2_OFFSET_X = 0.0
PLACE_2_OFFSET_Y = 0.0
PLACE_2_OFFSET_Z = -0.10
PLACE_2_VELOCITY = 1.0
PLACE_2_DIRECTION = "side"
PLACE_3_OFFSET_X = 0.0
PLACE_3_OFFSET_Y = 0.0
PLACE_3_OFFSET_Z = 0.05
PLACE_3_VELOCITY = 1.0
PLACE_3_DIRECTION = "side"
BEFORE_START_WAIT = 0.5
PREPAR_WAIT = 3
PAUSED_WAIT = 0.5
NON_OPERATING_WAIT = 1
CAMERA_NAME = 'camera'
MARKER_NAME = 'marker_frame'

###########################################
# ハンド制御クラス.                       #
###########################################
class GripperControlCommand:
    def __init__(self):
        self.node = CollaborationTool.get_node()

        # publisher
        self.control_pub = self.node.create_publisher(
            String,
            '/gripper_judge',
            100
        )

        # subscriber
        self.result_sub = self.node.create_subscription(
            String,
            '/hand_result',
            self.ResultCallback,
            10
        )

        self.send_judge = String()
        self.recieve_result = String()

        self.GRIPPER_RETRY_CNT = 100
        self.GRIPPER_MOVE_WAIT = 5.0

    def gripper_control(self, command="open"):
        wait_cnt = 0

        if command == "open":
            while True:
                self.send_judge.data = "open"
                self.control_pub.publish(self.send_judge)

                if self.recieve_result.data == "done":
                    self.send_judge.data = "done"
                    self.control_pub.publish(self.send_judge)
                    break

                elif wait_cnt > self.GRIPPER_RETRY_CNT:
                    CollaborationTool.loginfo(
                        "gripper retry..."
                    )
                    break

                CollaborationTool.wait_time(0.1)
                wait_cnt += 1

        if command == "close":
            while True:
                self.send_judge.data = "close"
                self.control_pub.publish(self.send_judge)

                if self.recieve_result.data == "done":
                    self.send_judge.data = "done"
                    self.control_pub.publish(self.send_judge)
                    break

                elif wait_cnt > self.GRIPPER_RETRY_CNT:
                    CollaborationTool.loginfo(
                        "gripper retry..."
                    )
                    break

                CollaborationTool.wait_time(0.1)
                wait_cnt += 1

        CollaborationTool.wait_time(
            self.GRIPPER_MOVE_WAIT
        )

        if wait_cnt > self.GRIPPER_RETRY_CNT:
            return False
        else:
            return True

    def ResultCallback(self, result_):
        self.recieve_result = result_

###########################################
# TFブロードキャストクラス.               #
###########################################

# 協働ブロードキャストクラスの抽象クラス.
class HumanCollaborationBroadcast(CollaborationCommunication):
    """
    Base class that HumanCollaboration communication for request
    Define machine-dependent packages
    """

    def __init__(self):
        self.node = CollaborationTool.get_node()

        self.broadcaster = tf2_ros.StaticTransformBroadcaster(
            self.node
        )

    def execute(self, object):
        pass


# TFブロードキャストクラス.
class TfBroadcast(HumanCollaborationBroadcast):
    def __init__(self, workdetection: WorkDetectionClient):
        super().__init__()
        self.workdetection = workdetection

    def execute(self, object):
        static_transformStamped = TransformStamped()

        static_transformStamped.header.stamp = (
            self.node.get_clock().now().to_msg()
        )

        static_transformStamped.header.frame_id = CAMERA_NAME
        static_transformStamped.child_frame_id = MARKER_NAME

        static_transformStamped.transform.translation.x = (
            self.workdetection
            .work_detect_result
            .work_detection_results[0]
            .pose.position.x
        )

        static_transformStamped.transform.translation.y = (
            self.workdetection
            .work_detect_result
            .work_detection_results[0]
            .pose.position.y
        )

        static_transformStamped.transform.translation.z = (
            self.workdetection
            .work_detect_result
            .work_detection_results[0]
            .pose.position.z
        )

        static_transformStamped.transform.rotation.x = (
            self.workdetection
            .work_detect_result
            .work_detection_results[0]
            .pose.orientation.x
        )

        static_transformStamped.transform.rotation.y = (
            self.workdetection
            .work_detect_result
            .work_detection_results[0]
            .pose.orientation.y
        )

        static_transformStamped.transform.rotation.z = (
            self.workdetection
            .work_detect_result
            .work_detection_results[0]
            .pose.orientation.z
        )

        static_transformStamped.transform.rotation.w = (
            self.workdetection
            .work_detect_result
            .work_detection_results[0]
            .pose.orientation.w
        )

        self.broadcaster.sendTransform(
            static_transformStamped
        )

        return True

###########################################
#MovePlanner共有クラス.                   #
###########################################
class ShareMovePlanner:
    move_plannner = None

    @classmethod
    def get_move_planner(cls):
        if cls.move_plannner is None:
            cls.move_plannner = MovePlanner()

        return cls.move_plannner
    
###########################################
#初期処理クラス.                          #
###########################################
class INITIALISE(CollaborationState):
    def __init__(self,
                 label,
                 taskfin:TaskFinishServer,
                 tran:Transition,
                 outcomes):
        super().__init__(label, tran, outcomes)
        self.planner = ShareMovePlanner.get_move_planner()
        self.taskfin = taskfin
        self.counter = 0

    def execute(self, userdata):
        CollaborationCurrentData.SetCurrentState(self)
        
        if self.tran.get_event().is_workend():
            task_command_list = CollaborationCurrentData.GetCurrentCommandList()
            task_command = task_command_list.get(0)
            self.taskfin.execute(task_command)

        if self.tran.is_tran() :
            nextstate = self.tran.transition()
            self.tran.reset_event()
            return nextstate
        
        if self.preempt('INIITIALISE is being preempted!!!'):
            return 'preempted'
        
        #初期処理を行う.
        return self.initialise()

    def initialise(self):
        ###ロボットごとの初期動作.
        #ここから.

        while not CollaborationTool.is_shutdown():
          #初期位置移動.
          ret = self.init_pose()
          if 'succeeded' == ret:
                break
          elif 'retry' == ret:
            continue
          else:
            return ret

        #ここまで.
        return 'succeeded'

    #初期位置移動.
    def init_pose(self):
        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            self.counter += 1
            CollaborationTool.loginfo('Initialise')
            rc = self.planner.initial_pose()
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'

###########################################
#スタート前処理クラス.                    #
###########################################
class BEFORE_START(CollaborationState):
    def __init__(self, label, taskfin:TaskFinishServer, tran:Transition, outcomes):
        super().__init__(label, tran, outcomes)
        self.taskfin = taskfin

    def execute(self, userdata):
        CollaborationCurrentData.SetCurrentState(self)
        if self.tran.get_event().is_pause():
            CollaborationState.set_history_label(self.label)
            self.tran.set_history_state(self.tran.get_state())

        if self.tran.is_tran() :
            nextstate = self.tran.transition()
            self.tran.reset_event()
            return nextstate
        
        CollaborationTool.loginfo('Before Start ...')
        if self.preempt('State BEFORE_START is being preempted!!!'):
            return 'preempted'
      
        return self.before_start()

    def before_start(self):
        ###ロボットごとのスタート前動作.
        #ここから.

        CollaborationTool.wait_time(BEFORE_START_WAIT)

        #ここまで.
        return 'succeeded'

###########################################
#準備中処理クラス.                        #
###########################################
class PREPAR_WORK(CollaborationState):
    def __init__(self, label, taskfin:TaskFinishServer, tran:Transition, area, disc, workd, outcomes):
        super().__init__(label, tran, outcomes)
        self.taskfin = taskfin
        self.area = area
        self.disc = disc
        self.workd = workd
        self.broadcast = TfBroadcast(self.workd)

    def execute(self, userdata):
        CollaborationCurrentData.SetCurrentState(self)

        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event
      
        CollaborationTool.loginfo('Preparing ...')
        if self.preempt('State Prepar is being preempted!!!'):
            return 'preempted'
        
        #準備処理.
        return self.prepar()

    def prepar(self):
        ###ロボットごとの準備動作.
        #ここから.

        CollaborationTool.wait_time(PREPAR_WAIT)
        self.counter = 0

        #周辺環境範囲設定.
        while not CollaborationTool.is_shutdown():
          ret = self.PeripheralEnvironmentAreaSet()
          if 'succeeded' == ret:
                break
          elif 'retry' == ret:
            continue
          else:
            return ret
          
        #ワーク検知.
        while not CollaborationTool.is_shutdown():
          ret = self.WorkDetect()
          if 'succeeded' == ret:
                break
          elif 'retry' == ret:
            continue
          else:
            return ret

        #ワーク位置計算.
        while not CollaborationTool.is_shutdown():
          ret = self.TFBroadCast()
          if 'succeeded' == ret:
                break
          elif 'retry' == ret:
            continue
          else:
            return ret
          
        #排出位置検出.
        while not CollaborationTool.is_shutdown():
          ret = self.DischargeDetect()
          if 'succeeded' == ret:
                break
          elif 'retry' == ret:
            continue
          else:
            return ret
        
        #ここまで.
        return 'succeeded'
    
    #周辺環境範囲を設定する.
    def PeripheralEnvironmentAreaSet(self):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event
        return 'succeeded'

    #排出位置を検出する.
    def DischargeDetect(self):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event

        CollaborationTool.loginfo("waiting place_position")
        self.disc.wait_for_service()
        CollaborationTool.loginfo("place_position comes up")

        event = self.check_event()
        if(None != event ):
            return event
        if self.counter < RETRY_COUNT_MAX:
            if self.preempt('State DischargeDetect is being preempted!!!'):
                return 'preempted'
            self.counter += 1
            #排出位置を探索.
            self.set_place_area()
            rc = self.disc.execute(None)
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc) 
        else:
            return 'aborted'

    #ワークを検知する.
    def WorkDetect(self):
        CollaborationTool.loginfo("waiting work_det_service")
        self.workd.wait_for_service()
        CollaborationTool.loginfo("work_det_service comes up")

        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event

        if self.counter < RETRY_COUNT_MAX:
            if self.preempt('State Work Detect is being preempted!!!'):
                return 'preempted'
            self.counter += 1
            #ワーク検知範囲の設定.
            self.set_presence_area()
            rc = self.workd.execute(None)
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc) 
        else:
            return 'aborted'
    
    #ワーク位置を計算する.
    def TFBroadCast(self):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event
        
        if self.counter < RETRY_COUNT_MAX:
            if self.preempt('State TFBroadCast is being preempted!!!'):
                return 'preempted'
            self.counter += 1
            rc = self.broadcast.execute(None)

            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'

    #排出位置を設定する.
    def set_place_area(self):
        #現在のコマンドリストを取得.
        command_list = CollaborationCurrentData.GetCurrentCommandList()
        task_command = command_list.get(0)
        place_area_list = task_command.get_PlaceLocationAreaList()
        print(place_area_list)
        place_area = place_area_list[0]
        print(place_area)
        self.disc.set_place_area(place_area.start_point.x,
                                     place_area.start_point.y,
                                     place_area.start_point.z,
                                     place_area.end_point.x,
                                     place_area.end_point.y,
                                     place_area.end_point.z,)

    #ワーク検知範囲を設定する.
    def set_presence_area(self):
        #現在のコマンドリストを取得.
        command_list = CollaborationCurrentData.GetCurrentCommandList()
        task_command = command_list.get(0)
        presence_area = task_command.work_presence_area
        self.workd.set_presence_area(task_command.task_command_id,
                                     task_command.work_type_id,
                                     presence_area.start_point.x,
                                     presence_area.start_point.y,
                                     presence_area.start_point.z,
                                     presence_area.end_point.x,
                                     presence_area.end_point.y,
                                     presence_area.end_point.z,)
    
    #作業途中で状態遷移するイベントの確認.
    def check_event(self):
        if self.tran.get_event().is_pause():
            CollaborationState.set_history_label(self.label)
            self.tran.set_history_state(self.tran.get_state())

        if self.tran.is_tran() :
            nextstate = self.tran.transition()
            self.tran.reset_event()
            return nextstate
        return None
        
###########################################
#自律動作処理クラス.                      #
###########################################
class OPERATING_WORK(CollaborationState):
    def __init__(self,
                 label,
                 taskfin:TaskFinishServer,
                 tran:Transition,
                 outcomes):
        super().__init__(label, tran, outcomes)
        self.planner = ShareMovePlanner.get_move_planner()
        self.taskfin = taskfin
        self.counter = 0
        self.work_label = None
        self.gripper = GripperControlCommand()

    def execute(self, userdata):
        CollaborationCurrentData.SetCurrentState(self)
        #現在のコマンドリストを取得.
        command_list = CollaborationCurrentData.GetCurrentCommandList()
        CollaborationTool.loginfo(command_list.get(0).task_command_id)
        
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event
        
        #自律動作.
        return self.operating_work()

    #自律動作処理.
    def operating_work(self):
        ###ロボットごとの自律動作.
        #ここから.

        #ハンド開ける.
        if (None == self.work_label) or ('HandOpen1' == self.work_label):
          while not CollaborationTool.is_shutdown():
            self.work_label = 'HandOpen1'
            ret = self.hand_open()
            if 'succeeded' == ret:
                self.work_label = None
                break
            elif 'retry' == ret:
                continue
            else:
                return ret
        
        #ピック動作1.
        if (None == self.work_label) or ('TfManip' == self.work_label):
          while not CollaborationTool.is_shutdown():
            self.work_label = 'TfManip'
            ret = self.tf_manip(PICK_1_OFFSET_X, PICK_1_OFFSET_Y, PICK_1_OFFSET_Z, DEFAULT_VELOCITY, PICK_1_POSE)
            if 'succeeded' == ret:
                self.work_label = None
                break
            elif 'retry' == ret:
                continue
            else:
                return ret
        
        #ピック動作2.
        if (None == self.work_label) or ('CurrentManip1' == self.work_label):
          while not CollaborationTool.is_shutdown():
            self.work_label = 'CurrentManip1'
            ret = self.current_manip(PICK_2_OFFSET_X, PICK_2_OFFSET_Y, PICK_2_OFFSET_Z, PICK_2_VELOCITY)
            if 'succeeded' == ret:
                self.work_label = None
                break
            elif 'retry' == ret:
                continue
            else:
                return ret
        
        #ハンド閉じる.
        if (None == self.work_label) or ('HandClose1' == self.work_label):
          while not CollaborationTool.is_shutdown():
            self.work_label = 'HandClose1'
            ret = self.hand_close()
            if 'succeeded' == ret:
                self.work_label = None
                break
            elif 'retry' == ret:
                continue
            else:
                return ret

        #ピック動作3.
        if (None == self.work_label) or ('CurrentManip2' == self.work_label):
          while not CollaborationTool.is_shutdown():
            self.work_label = 'CurrentManip2'
            ret = self.current_manip(PICK_3_OFFSET_X, PICK_3_OFFSET_Y, PICK_3_OFFSET_Z, PICK_3_VELOCITY)
            if 'succeeded' == ret:
                self.work_label = None
                break
            elif 'retry' == ret:
                continue
            else:
                return ret
        
        #初期位置に戻る.
        if (None == self.work_label) or ('InitPose1' == self.work_label):
          while not CollaborationTool.is_shutdown():
            self.work_label = 'InitPose1'
            ret = self.init_pose()
            if 'succeeded' == ret:
                self.work_label = None
                break
            elif 'retry' == ret:
                continue
            else:
                return ret

        #プレース動作1.
        if (None == self.work_label) or ('NormalManip1' == self.work_label):
          while not CollaborationTool.is_shutdown():
            self.work_label = 'NormalManip1'
            ret = self.normal_manip(PLACE_1_OFFSET_X, PLACE_1_OFFSET_Y, PLACE_1_OFFSET_Z, DEFAULT_VELOCITY)
            if 'succeeded' == ret:
                self.work_label = None
                break
            elif 'retry' == ret:
                continue
            else:
                return ret
        
        #プレース動作2.
        if (None == self.work_label) or ('CurrentManip3' == self.work_label):
          while not CollaborationTool.is_shutdown():
            self.work_label = 'CurrentManip3'
            ret = self.current_manip(PLACE_2_OFFSET_X, PLACE_2_OFFSET_Y, PLACE_2_OFFSET_Z, PLACE_2_VELOCITY)
            if 'succeeded' == ret:
                self.work_label = None
                break
            elif 'retry' == ret:
                continue
            else:
                return ret
        
        #ハンド開ける.
        if (None == self.work_label) or ('HandOpen2' == self.work_label):
          while not CollaborationTool.is_shutdown():
            self.work_label = 'HandOpen2'
            ret = self.hand_open()
            if 'succeeded' == ret:
                self.work_label = None
                break
            elif 'retry' == ret:
                continue
            else:
                return ret
        
        #プレース動作3.
        if (None == self.work_label) or ('CurrentManip4' == self.work_label):
          while not CollaborationTool.is_shutdown():
            self.work_label = 'CurrentManip4'
            ret = self.current_manip(PLACE_3_OFFSET_X, PLACE_3_OFFSET_Y, PLACE_3_OFFSET_Z, PLACE_3_VELOCITY)
            if 'succeeded' == ret:
                self.work_label = None
                break
            elif 'retry' == ret:
                continue
            else:
                return ret
        
        #初期位置に戻る.
        if (None == self.work_label) or ('InitPose2' == self.work_label):
          while not CollaborationTool.is_shutdown():
            self.work_label = 'InitPose2'
            ret = self.init_pose()
            if 'succeeded' == ret:
                self.work_label = None
                break
            elif 'retry' == ret:
                continue
            else:
                return ret
        
        #ここまで.
        self.work_label = None
        return 'succeeded'
    
    #ハンド開ける.
    def hand_open(self):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event):
            return event
        
        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            if self.preempt('State HAND_OPEN is being preempted!!!'):
                return 'preempted'
            self.counter += 1
            CollaborationTool.loginfo('HandOpen')
            rc = self.gripper.gripper_control('open')
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'
    
    #ハンド閉める.
    def hand_close(self):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event):
            return event
        
        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            if self.preempt('State HAND_CLOSE is being preempted!!!'):
                return 'preempted'
            
            self.counter += 1
            CollaborationTool.loginfo('HandClose')
            rc = self.gripper.gripper_control('close')
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'
        
    def tf_manip(self,offset_x, offset_y, offset_z, vel, tf_pose):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event):
            return event
        
        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            if self.preempt('State TF_MANIP is being preempted!!!'):
                return 'preempted'
            self.counter += 1   
            CollaborationTool.loginfo('Manipulate at ({},{},{}) in scale velocity {}'.format(offset_x, offset_y, offset_z, vel, tf_pose))
            rc = self.planner.tf_position(offset_x, offset_y, offset_z, vel, tf_pose)
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'

    def current_manip(self, offset_x, offset_y, offset_z, vel):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event):
            return event
        
        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            if self.preempt('State CURRENT_MANIP is being preempted!!!'):
                return 'preempted'
            self.counter += 1
            CollaborationTool.loginfo('Manipulate at ({},{},{}) in scale velocity {}'.format(offset_x, offset_y, offset_z, vel))
            rc = self.planner.current_position(offset_x, offset_y, offset_z, vel)
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'

    #初期位置移動.
    def init_pose(self):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event):
            return event
        
        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            self.counter += 1
            CollaborationTool.loginfo('InitPose')
            rc = self.planner.initial_pose()
           #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'
        
    def normal_manip(self, offset_x, offset_y, offset_z, vel):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event):
            return event
        
        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            if self.preempt('State NORMAL_MANIP is being preempted!!!'):
                return 'preempted'
            self.counter += 1
            CollaborationTool.loginfo('Manipulate at ({},{},{}) in scale velocity {}'.format(offset_x, offset_y, offset_z, vel))
            rc = self.planner.grasp_position(offset_x, offset_y, offset_z, vel)
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'

    #作業途中で状態遷移するイベントの確認.
    def check_event(self):
        if self.tran.get_event().is_pause():
            CollaborationState.set_history_label(self.label)
            self.tran.set_history_state(self.tran.get_state())

        elif self.tran.get_event().is_workend():
            command_list = CollaborationCurrentData.GetCurrentCommandList()
            task_command = command_list.get(0)
            self.taskfin.execute(task_command)

        if self.tran.is_tran() :
            nextstate = self.tran.transition()
            self.tran.reset_event()
            return nextstate
        return None

###########################################
#非自律動作処理クラス.                    #
###########################################
class NON_OPERATING_WORK(CollaborationState):
    def __init__(self, label, taskfin:TaskFinishServer, tran:Transition, outcomes):
        super().__init__(label, tran, outcomes)
        self.taskfin = taskfin
        self.planner = ShareMovePlanner.get_move_planner()

    def execute(self, userdata):
        CollaborationCurrentData.SetCurrentState(self)
        #現在のコマンドリストを取得.
        command_list = CollaborationCurrentData.GetCurrentCommandList()
        CollaborationTool.loginfo(command_list.get(0).task_command_id)
        
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event
        
        #非自律動作処理.
        return self.non_operating_work()
    
    #非自律動作処理.
    def non_operating_work(self):
        ###ロボットごとの非自律動作.
        #ここから.

        CollaborationTool.wait_time(NON_OPERATING_WAIT)

        #初期位置に戻る.
        if (None == self.work_label) or ('InitPose1' == self.work_label):
          while not CollaborationTool.is_shutdown():
            self.work_label = 'InitPose1'
            ret = self.init_pose()
            if 'succeeded' == ret:
                self.work_label = None
                break
            elif 'retry' == ret:
                continue
            else:
                return ret
        
        #ここまで.
        self.work_label = None
        return 'succeeded'
    
    #初期位置移動.
    def init_pose(self):
        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event):
            return event
        
        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            self.counter += 1
            CollaborationTool.loginfo('InitPose')
            rc = self.planner.initial_pose()
           #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'

    #作業途中で状態遷移するイベントの確認.
    def check_event(self):
        if self.tran.get_event().is_pause():
            CollaborationState.set_history_label(self.label)
            self.tran.set_history_state(self.tran.get_state())

        elif self.tran.get_event().is_workend():
            command_list = CollaborationCurrentData.GetCurrentCommandList()
            task_command = command_list.get(0)
            self.taskfin.execute(task_command)

        if self.tran.is_tran() :
            nextstate = self.tran.transition()
            self.tran.reset_event()
            return nextstate
        return None

###########################################
#一時停止中処理クラス                     #
###########################################
class PAUSED_WORK(CollaborationState):
    def __init__(self, label, taskfin:TaskFinishServer, tran:Transition, outcomes):
        super().__init__(label, tran, outcomes)
        self.taskfin = taskfin
        self.counter = 0
        self.planner = ShareMovePlanner.get_move_planner()

    def execute(self, userdata):
        CollaborationCurrentData.SetCurrentState(self)

        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event

        CollaborationTool.loginfo('Preparing ...')
        if self.preempt('State Prepar is being preempted!!!'):
            return 'preempted'
        
        #待機処理.
        return self.paused()

    def paused(self):
        ###ロボットごとの待機動作.
        #ここから.

        CollaborationTool.wait_time(PAUSED_WAIT)

        #作業途中で状態遷移するイベントの確認.
        event = self.check_event()
        if(None != event ):
            return event
        
        #初期位置移動.
        while not CollaborationTool.is_shutdown():
          ret = self.init_pose()
          if 'succeeded' == ret:
                break
          elif 'retry' == ret:
            continue
          else:
            return ret

        #ここまで.
        return 'succeeded'

    #初期位置移動.
    def init_pose(self):
        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            self.counter += 1
            CollaborationTool.loginfo('init_pose')
            rc = self.planner.initial_pose()
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'

    #作業途中で状態遷移するイベントの確認.
    def check_event(self):
        if self.tran.get_event().is_workend():
            command_list = CollaborationCurrentData.GetCurrentCommandList()
            task_command = command_list.get(0)
            self.taskfin.execute(task_command)

        if self.tran.is_tran() :
            nextstate = self.tran.transition()
            self.tran.reset_event()
            return nextstate
        return None

###########################################
#終了処理クラス.                          #
###########################################        
class FINALISE(CollaborationState):
    def __init__(self,
                 label,
                 taskfin:TaskFinishServer,
                 tran:Transition,
                 outcomes):
        super().__init__(label, tran, outcomes)
        self.planner = ShareMovePlanner.get_move_planner()
        self.taskfin = taskfin
        self.counter = 0

    def execute(self, userdata):
        CollaborationCurrentData.SetCurrentState(self)

        if self.tran.get_event().is_workend():
            task_command_list = CollaborationCurrentData.GetCurrentCommandList()
            task_command = task_command_list.get(0)
            self.taskfin.execute(task_command)

        if self.tran.is_tran() :
            nextstate = self.tran.transition()
            self.tran.reset_event()
            return nextstate
        
        if self.preempt('INIITIALISE_POSE is being preempted!!!'):
            return 'preempted'
        
        #終了処理を行う.
        return self.finalise()

    #終了処理.
    def finalise(self):
        ###ロボットごとの終了動作.
        #ここから.

        #初期位置移動.
        while not CollaborationTool.is_shutdown():
          ret = self.init_pose()
          if 'succeeded' == ret:
                break
          elif 'retry' == ret:
            continue
          else:
            return ret

        #終了する.
        CollaborationTool.signal_shutdown("sys_manage_halt")

        #ここまで.
        return 'succeeded'
    
    def init_pose(self):
        #3回以上連続で失敗したら異常終了する.
        if self.counter < RETRY_COUNT_MAX:
            self.counter += 1
            CollaborationTool.loginfo('finalise')
            rc = self.planner.initial_pose()
            #正常完了の場合はエラーカウンターをリセット.
            if True == rc:
                self.counter = 0
            return self.return_btos(rc)
        else:
            return 'aborted'