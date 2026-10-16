#!/usr/bin/env python3
# coding: UTF-8
from abc import ABCMeta
from abc import abstractmethod
from .EnumerateModule import EnumEvent
from collaboration_manipulation_message.msg import TargetArea, PlaceAreaCandidatesList, TaskCommand, TaskCommandList
from collaboration_manipulation_message.srv import * 
import queue
import threading

#状態遷移のオブザーバ抽象クラス.
class CollaborationEventSubscriver(metaclass=ABCMeta):
    @abstractmethod
    def update(self, event:EnumEvent):
        pass

#状態遷移のサブジェクト(通知者)クラス.
class CollaborationEventPublisher:
    subscrivers = []
    lock = threading.Lock() 
    @classmethod
    def register(cls, subscriver:CollaborationEventSubscriver):
        cls.subscrivers.append(subscriver)
    @classmethod
    def notify(cls, event:EnumEvent, data):
        cls.lock.acquire()
        for sub in cls.subscrivers:
           sub.update(event, data)
        cls.lock.release()

#排出位置候補クラス.
class CollaborationCandidatePlaceLocationArea(TargetArea):
    def __init__(self):
        super().__init__()

    def set_member(self, sx, sy, sz, ex, ey, ez):
        self.start_point.x = sx
        self.start_point.y = sy
        self.start_point.z = sz
        self.end_point.x = ex
        self.end_point.y = ey
        self.end_point.z = ez

#排出位置候補リスト.
class CollaborationPlaceAreaCandidatesList(PlaceAreaCandidatesList):
    def __init__(self):
        super().__init__()
    def add(self, area:CollaborationCandidatePlaceLocationArea):
        self.place_area_candidates.append(area)

#ワーク検出エリア.
class CollaborationWorkPresenceArea(TargetArea):
    def __init__(self):
        super().__init__()

    def set_member(self, sx, sy, sz, ex, ey, ez):
        self.start_point.x = sx
        self.start_point.y = sy
        self.start_point.z = sz
        self.end_point.x = ex
        self.end_point.y = ey
        self.end_point.z = ez

#作業コマンド.
class CollaborationTaskCommand(TaskCommand):
    def __init__(self):
        super().__init__()
    def set_member(self, task_command_id, work_type_id, number_of_items_picked):
        self.task_command_id = task_command_id
        self.work_type_id = work_type_id
        self.number_of_items_picked = number_of_items_picked

    def set_WorkPresenceArea(self, area:CollaborationWorkPresenceArea):
        self.work_presence_area = area

    def set_CandidatePlaceLocationAreaList(self, list:CollaborationPlaceAreaCandidatesList):
        self.candidate_place_location_list = list
    
    def get_PlaceLocationAreaList(self):
        return self.candidate_place_location_list.place_area_candidates


#作業コマンドリスト.
class CollaborationTaskCommandList:
    def __init__(self, tasks:TaskCommandList = None):
        self.tasks = tasks if tasks is not None else TaskCommandList()
       
    def add(self, task:CollaborationTaskCommand):
        self.tasks.task_commands.append(task)
    
    def get(self, index):
        return self.tasks.task_commands[index]

#作業開始オブザーバ.
class CollaborationEventSubscriverWorkStart(CollaborationEventSubscriver):
    def __init__(self):
        self.work_orders = queue.Queue()
    def enqueue(self, task:CollaborationTaskCommandList):
        self.work_orders.put(task)
    def dequeue(self):
        try:
            return self.work_orders.get(timeout=5)  # 5秒間待ってもデータがない場合、例外を発生
        except queue.Empty:
            print("Queue is empty after timeout")
            return None
    def getcount(self):
        return self.work_orders.qsize()
    
    def update(self, event:EnumEvent, data):
        if(event.is_workstart()):
            self.enqueue(data)
