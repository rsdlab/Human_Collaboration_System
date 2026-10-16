#!/usr/bin/env python3
# coding: UTF-8

from enum import IntEnum, auto

#イベントクラスの抽象クラス.
class BaseEvent(IntEnum):
    """
    Event for HumanCollaborationModule
    """
    def __init__(self, event):
        self.event = event

#イベントのEnum定義と判定を行うクラス.
class EnumEvent(BaseEvent):
    NOEVENT     = auto()
    WORKSTART   = auto()
    WORKSUSPEND = auto()
    WORKEND     = auto()
    PAUSE       = auto()
    PAUSECANCEL = auto()
    COLLABO     = auto()
    COLLABOEND  = auto()
    GETSTATE    = auto()
    END         = auto()

    def __init__(self, event):
        super().__init__(event)
    @classmethod
    def e_noevent(cls):
        return cls.NOEVENT
    @classmethod
    def e_workstart(cls):
        return cls.WORKSTART
    @classmethod
    def e_worksuspend(cls):
        return cls.WORKSUSPEND
    @classmethod
    def e_workend(cls):
        return cls.WORKEND
    @classmethod
    def e_pause(cls):
        return cls.PAUSE
    @classmethod
    def e_pausecancel(cls):
        return cls.PAUSECANCEL
    @classmethod
    def e_collabo(cls):
        return cls.COLLABO
    @classmethod
    def e_collaboend(cls):
        return cls.COLLABOEND
    @classmethod
    def e_getstate(cls):
        return cls.GETSTATE
    @classmethod
    def e_end(cls):
        return cls.END

    def is_workstart(self):
        return self.WORKSTART == self.event
    def is_worksuspend(self):
        return self.WORKSUSPEND == self.event
    def is_workend(self):
        return self.WORKEND == self.event
    def is_pause(self):
        return self.PAUSE == self.event
    def is_pausecancel(self):
        return self.PAUSECANCEL == self.event
    def is_collabo(self):
        return self.COLLABO == self.event
    def is_collaboend(self):
        return self.COLLABOEND == self.event
    def is_getstate(self):
        return self.GETSTATE == self.event
    def is_end(self):
        return self.END == self.event

#状態クラスの抽象クラス.
class BaseState:
    def __init__(self, state):
        self.state = state

#状態のEnum定義と判定を行うクラス.
class EnumState(BaseState):
    """
    State for HumanCollaborationModule

    Use in the following combinations.

    EnumState.INITIALIZING
    EnumState.STANDBY
    EnumState.RUNNING|EnumState.PREPARING
    EnumState.RUNNING|EnumState.WORKING|EnumState.OPERATING
    EnumState.RUNNING|EnumState.WORKING|EnumState.NONOPERATING
    EnumState.RUNNING|EnumState.INTERVING
    EnumState.RUNNING|EnumState.PAUSED
    EnumState.FINALIZING
    """
    NOSTATE         = 0
    INITIALIZING    = 1
    STANDBY         = 2
    RUNNING         = 4
    PREPARING       = 8
    WORKING         = 16
    OPERATING       = 32
    NONOPERATING    = 64
    PAUSED          = 128
    FINALIZING      = 256

    def __init__(self, state):
        super().__init__(state)

    @classmethod
    def e_initializing(cls):
        return cls.INITIALIZING
    @classmethod
    def e_standby(cls):
        return cls.STANDBY
    @classmethod
    def e_running(cls):
        return cls.RUNNING
    @classmethod
    def e_preparing(cls):
        return cls.RUNNING | cls.PREPARING
    @classmethod
    def e_working(cls):
        return cls.RUNNING | cls.WORKING
    @classmethod
    def e_operating(cls):
        return cls.RUNNING | cls.WORKING | cls.OPERATING
    @classmethod
    def e_nonoperating(cls):
        return cls.RUNNING | cls.WORKING | cls.NONOPERATING
    @classmethod
    def e_paused(cls):
        return cls.RUNNING | cls.PAUSED
    @classmethod
    def e_finalizing(cls):
        return cls.FINALIZING    

    def is_initializing(self):
        return self.INITIALIZING & self.state == self.INITIALIZING 
    def is_standby(self):
        return self.STANDBY & self.state == self.STANDBY 
    def is_running(self):
        return self.RUNNING & self.state == self.RUNNING 
    def is_preparing(self):
        return self.PREPARING & self.state == self.PREPARING 
    def is_working(self):
        return self.WORKING & self.state == self.WORKING 
    def is_operating(self):
        return self.OPERATING & self.state == self.OPERATING 
    def is_nonoperating(self):
        return self.NONOPERATING & self.state == self.NONOPERATING 
    def is_paused(self):
        return self.PAUSED & self.state == self.PAUSED 
    def is_finalizing(self):
        return self.FINALIZING & self.state == self.FINALIZING 

class EnumCommandReceiveState(BaseEvent):
    RECEIVED    = auto()
    BUSY        = auto()
    FATAL_ERROR = auto()

    def __init__(self, event):
        super().__init__(event)
    @classmethod
    def e_received(cls):
        return cls.RECEIVED
    @classmethod
    def e_busy(cls):
        return cls.BUSY
    @classmethod
    def e_fatal_error(cls):
        return cls.FATAL_ERROR