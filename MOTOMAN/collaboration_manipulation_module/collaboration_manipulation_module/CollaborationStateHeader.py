#!/usr/bin/env python3
# coding: UTF-8

from .EnumerateModule import EnumEvent
from .CollaborationCommunicationModule import *
from .CollaborationUserDefineModule import *
from .CollaborationEventModule import CollaborationTaskCommandList
from smach import State
from .TransitionModule import Transition
from .CollaborationToolModule import CollaborationTool

#状態遷移イベント抽象クラス.
class CollaborationState(State):
    """
    Base class for HumanCollaboration state.

    Inherit this class and set the appropriate EnumState.

    Attributes
    ----------
    history_label : str
        state name
    """
    history_label = None

    def __init__(self, label, tran:Transition,  outcomes=[], input_keys=[], output_keys=[], io_keys=[]):
        """constructor

        Parameters
        ----------
        label : str
            state name
        tran : Trsansition object
            state transition and state value, event value
        outcomes  : array of string
            Custom outcomes for this state. 
        """
        super().__init__(outcomes, input_keys, output_keys, io_keys)
        self.label = label
        self.tran = tran

    @classmethod
    def set_history_label(cls, label):
        cls.history_label = label

    @classmethod
    def reset_history_label(cls):
        cls.set_history_label(None)

    @classmethod
    def get_history_label(cls):
        return cls.history_label

    def set_event(self, event:EnumEvent):
        return self.tran.set_event(event)

    def get_state(self):
        return self.tran.get_state()

    def preempt(self, info):
        if self.preempt_requested():
            CollaborationTool.loginfo(info)
            self.service_preempt()
            return True
        else:
            return False
    
    #結果を文字列に変換.
    def return_btos(self, value : bool):
        return 'succeeded' if value else "retry"

#現在のデータを保持するクラス.
class CollaborationCurrentData():
    current_state = None
    @classmethod
    def GetCurrentState(cls):
        return cls.current_state
    
    @classmethod
    def SetCurrentState(cls, state:CollaborationState):
        cls.current_state = state

    current_command_list = None
    @classmethod
    def GetCurrentCommandList(cls):
        return cls.current_command_list
    
    @classmethod
    def SetCurrentCommandList(cls, command_list:CollaborationTaskCommandList):
        cls.current_command_list = command_list