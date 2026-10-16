#!/usr/bin/env python3
# coding: UTF-8

from .EnumerateModule import EnumEvent, EnumState
from .CollaborationToolModule import CollaborationTool

class _StateAndEvent:
    """
    Base class for HumanCollaboration state and event.

    Inherit this class and set the appropriate EnumState and EnumEvent.

    Attributes
    ----------
    state : EnumState
        state enum value
    event : EnumEvent
        event enum value
    """
    event = EnumEvent.NOEVENT
    history_state = EnumState.NOSTATE

    def __init__(self, state:EnumState):
        self.state = state

    @classmethod
    def set_event(cls, event:EnumEvent):
        """setter

        Parameters
        -------
        event : EnumEvent
        event enum value
        """
        CollaborationTool.loginfo('Set event {}'.format(event))
        cls.event = event

    @classmethod
    def get_event(cls):
        """getter

        Returns
        -------
        event : EnumEvent
        event enum value
        """
        return cls.event

    @classmethod
    def reset_event(cls):
        cls.set_event(EnumEvent(EnumEvent.e_noevent()))

    @classmethod
    def set_history_state(cls, state:EnumState):
        """setter

        Parameters
        -------
        event : EnumState
        event enum value
        """
        cls.history_state = state

    @classmethod
    def get_history_state(cls):
        """getter

        Parameters
        -------
        event : EnumState
        event enum value
        """
        return cls.history_state

    @classmethod
    def reset_history_state(cls):
        cls.set_history_state(EnumState(EnumState.e_initializing()))

    def get_state(self) -> EnumState :
        """getter

        Returns
        -------
        state : EnumState
        state enum value
        """
        return self.state
 
class Transition(_StateAndEvent):
    def __init__(self, state:EnumState):
        super().__init__(state)
        # [accept event, transision destinastion]
        self.dic = dict()

    def set_event(self, ev:EnumEvent):
        if self.accept(ev) :
            _StateAndEvent.set_event(ev)
        else:
            CollaborationTool.loginfo('ignore event %d', ev.event)

    def reset_event(self):
        _StateAndEvent.reset_event()

    def accept(self, ev:EnumEvent):
        values = self.dic[ev.event]
        return values[0]      

    def is_tran(self):
        event  = self.get_event()
        values = self.dic[event] 
        return False if values[1] == 'NA' else ( False if values[1] == 'succeeded' else True )

    def transition(self):
        event=self.get_event()
        values = self.dic[event]
        CollaborationTool.loginfo(values[1])
        return values[1]
            

class InitializingTran(Transition):
    def __init__(self):
        super().__init__(EnumState.e_initializing())
        # [accept event, transision destinastion]
        self.dic[EnumEvent.NOEVENT]    = [False, 'NA']
        self.dic[EnumEvent.WORKSTART]  = [False, 'NA']
        self.dic[EnumEvent.WORKSUSPEND]= [False, 'NA']
        self.dic[EnumEvent.WORKEND]    = [False, 'NA']
        self.dic[EnumEvent.PAUSE]      = [True,  'succeeded']#0524add
        self.dic[EnumEvent.PAUSECANCEL]= [False, 'NA']
        self.dic[EnumEvent.COLLABO]    = [False, 'NA']
        self.dic[EnumEvent.COLLABOEND] = [False, 'NA']
        self.dic[EnumEvent.GETSTATE]   = [False, 'NA']
        self.dic[EnumEvent.END]        = [False, 'NA']

class StandbyTran(Transition):
    def __init__(self):
        super().__init__(EnumState.e_standby())
        # [accept event, transision destinastion]
        self.dic[EnumEvent.NOEVENT]    = [True,  'NA']
        self.dic[EnumEvent.WORKSTART]  = [True,  'succeeded']
        self.dic[EnumEvent.WORKSUSPEND]= [False, 'NA']
        self.dic[EnumEvent.WORKEND]    = [False, 'NA']
        self.dic[EnumEvent.PAUSE]      = [False, 'NA']
        self.dic[EnumEvent.PAUSECANCEL]= [False, 'NA']
        self.dic[EnumEvent.COLLABO]    = [False, 'NA']
        self.dic[EnumEvent.COLLABOEND] = [False, 'NA']
        self.dic[EnumEvent.GETSTATE]   = [False, 'NA']
        self.dic[EnumEvent.END]        = [True,  'end']

class FinalizingTran(Transition):
    def __init__(self):
        super().__init__(EnumState.e_finalizing())
        # [accept event, transision destinastion]
        self.dic[EnumEvent.NOEVENT]    = [False, 'NA']
        self.dic[EnumEvent.WORKSTART]  = [False, 'NA']
        self.dic[EnumEvent.WORKSUSPEND]= [False, 'NA']
        self.dic[EnumEvent.WORKEND]    = [False, 'NA']
        self.dic[EnumEvent.PAUSE]      = [False, 'NA']
        self.dic[EnumEvent.PAUSECANCEL]= [False, 'NA']
        self.dic[EnumEvent.COLLABO]    = [False, 'NA']
        self.dic[EnumEvent.COLLABOEND] = [False, 'NA']
        self.dic[EnumEvent.GETSTATE]   = [False, 'NA']
        self.dic[EnumEvent.END]        = [False, 'NA']
 
class RunningTran(Transition):
    def __init__(self):
        super().__init__(EnumState.e_running())
        # [accept event, transision destinastion]
        self.dic[EnumEvent.NOEVENT]    = [False, 'NA']
        self.dic[EnumEvent.WORKSTART]  = [False, 'NA']
        self.dic[EnumEvent.WORKSUSPEND]= [True,  'suspended']
        self.dic[EnumEvent.WORKEND]    = [True,  'workend']
        self.dic[EnumEvent.PAUSE]      = [False, 'NA']
        self.dic[EnumEvent.PAUSECANCEL]= [False, 'NA']
        self.dic[EnumEvent.COLLABO]    = [False, 'NA']
        self.dic[EnumEvent.COLLABOEND] = [False, 'NA']
        self.dic[EnumEvent.GETSTATE]   = [False, 'NA']
        self.dic[EnumEvent.END]        = [True,  'end']

class PreparingTran(Transition):
    def __init__(self):
        super().__init__(EnumState.e_preparing())
        # [accept event, transision destinastion]
        self.dic[EnumEvent.NOEVENT]    = [False, 'NA']
        self.dic[EnumEvent.WORKSTART]  = [False, 'NA']
        self.dic[EnumEvent.WORKSUSPEND]= [True,  'suspended']
        self.dic[EnumEvent.WORKEND]    = [True,  'workend']
        self.dic[EnumEvent.PAUSE]      = [False, 'NA']
        self.dic[EnumEvent.PAUSECANCEL]= [False, 'NA']
        self.dic[EnumEvent.COLLABO]    = [False, 'NA']
        self.dic[EnumEvent.COLLABOEND] = [False, 'NA']
        self.dic[EnumEvent.GETSTATE]   = [False, 'NA']
        self.dic[EnumEvent.END]        = [True,  'end']

class WorkingTran(Transition):
    def __init__(self):
        super().__init__(EnumState.e_working())
        # [accept event, transision destinastion]
        self.dic[EnumEvent.NOEVENT]    = [False, 'NA']
        self.dic[EnumEvent.WORKSTART]  = [False, 'NA']
        self.dic[EnumEvent.WORKSUSPEND]= [True,  'suspended']
        self.dic[EnumEvent.WORKEND]    = [True,  'workend']
        self.dic[EnumEvent.PAUSE]      = [True,  'paused']
        self.dic[EnumEvent.PAUSECANCEL]= [False, 'NA']
        self.dic[EnumEvent.COLLABO]    = [False, 'NA']
        self.dic[EnumEvent.COLLABOEND] = [False, 'NA']
        self.dic[EnumEvent.GETSTATE]   = [False, 'NA']
        self.dic[EnumEvent.END]        = [True,  'end']

class OperatingTran(Transition):
    def __init__(self):
        super().__init__(EnumState.e_operating())
        # [accept event, transision destinastion]
        self.dic[EnumEvent.NOEVENT]    = [False, 'NA']
        self.dic[EnumEvent.WORKSTART]  = [False, 'NA']
        self.dic[EnumEvent.WORKSUSPEND]= [True,  'suspended']
        self.dic[EnumEvent.WORKEND]    = [True,  'workend']
        self.dic[EnumEvent.PAUSE]      = [True,  'paused']
        self.dic[EnumEvent.PAUSECANCEL]= [False, 'NA']
        self.dic[EnumEvent.COLLABO]    = [True,  'collabo']
        self.dic[EnumEvent.COLLABOEND] = [False, 'NA']
        self.dic[EnumEvent.GETSTATE]   = [False, 'NA']
        self.dic[EnumEvent.END]        = [True,  'end']

class NonOperatingTran(Transition):
    def __init__(self):
        super().__init__(EnumState.e_nonoperating())
        # [accept event, transision destinastion]
        self.dic[EnumEvent.NOEVENT]    = [False, 'NA']
        self.dic[EnumEvent.WORKSTART]  = [False, 'NA']
        self.dic[EnumEvent.WORKSUSPEND]= [True,  'suspended']
        self.dic[EnumEvent.WORKEND]    = [True,  'workend']
        self.dic[EnumEvent.PAUSE]      = [True,  'paused']
        self.dic[EnumEvent.PAUSECANCEL]= [False, 'NA']
        self.dic[EnumEvent.COLLABO]    = [False, 'NA']
        self.dic[EnumEvent.COLLABOEND] = [True,  'collaboend']
        self.dic[EnumEvent.GETSTATE]   = [False, 'NA']
        self.dic[EnumEvent.END]        = [True,  'end']

class PausedTran(Transition):
    def __init__(self):
        super().__init__(EnumState.e_paused())
        # [accept event, transision destinastion]
        self.dic[EnumEvent.NOEVENT]    = [False, 'NA']
        self.dic[EnumEvent.WORKSTART]  = [False, 'NA']
        self.dic[EnumEvent.WORKSUSPEND]= [True,  'suspended']
        self.dic[EnumEvent.WORKEND]    = [True,  'workend']
        self.dic[EnumEvent.PAUSE]      = [False, 'NA']
        self.dic[EnumEvent.PAUSECANCEL]= [True,  'pausecancel']
        self.dic[EnumEvent.COLLABO]    = [False, 'NA']
        self.dic[EnumEvent.COLLABOEND] = [False, 'NA']
        self.dic[EnumEvent.GETSTATE]   = [False, 'NA']
        self.dic[EnumEvent.END]        = [True,  'end']

