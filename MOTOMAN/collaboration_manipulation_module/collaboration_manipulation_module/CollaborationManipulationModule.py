#!/usr/bin/env python3
# coding: UTF-8

#####################################################################################################################
#このノードは．人協働マニピュレーションモジュールを機能単位で作成したモジュールです．　
#ハンド部分のモジュールと人検知部分の追加を行っています．　　　　　　　　　　　　　　 #
#===================================================================================================================#
#バージョン管理
#===================================================================================================================#
#ver. 0.1:  基本実装（Linux版）　　　2023/11/07
#08/30 排出位置検出システム編集
#09/21 排出位置検出システム　統合
#09/28 WS環境認識システム作成
#10/05 排出位置検出システム　統合確認　
#===================================================================================================================#
#依存ノード
#===================================================================================================================#
#このノードはLinuxでのみ利用可能です．
#===================================================================================================================#

from .CollaborationStateModule import HumanCollaborationStateMachine
from .CollaborationCommunicationModule import TaskCommandServer, TaskCancelServer, TaskFinishServer, GetStatusServer, SystemTerminate, PeripheralEnvironmentAreaSetClient, PlacePositionClient, WorkDetectionClient, NotifyTaskResultClient, NotifyTaskCompleteClient
from .CollaborationEventModule import CollaborationEventPublisher, CollaborationEventSubscriverWorkStart
from .CollaborationToolModule import CollaborationTool

##################################################################
#　　　　　　　　　　　 クラス定義　                            #
##################################################################
class HumanCollaboration:
    def __init__(self):
        CollaborationTool.init_node('human_collaboration_node')
        area = PeripheralEnvironmentAreaSetClient()
        disc = PlacePositionClient()
        workd = WorkDetectionClient()
        workstart_event = CollaborationEventSubscriverWorkStart()
        TaskCommandServer()
        SystemTerminate()
        self.statemachine = HumanCollaborationStateMachine(
              NotifyTaskResultClient(),
              NotifyTaskCompleteClient(),
              TaskCancelServer(),
              TaskFinishServer(),
              GetStatusServer(),
              area,
              disc,
              workd,
              workstart_event
              )
        CollaborationEventPublisher.register(self.statemachine)
        CollaborationEventPublisher.register(workstart_event)

    def execute(self):
        CollaborationTool.loginfo('State machine Start')
        self.statemachine.execute()
        CollaborationTool.loginfo(' State machine End')

##################################################################
#　　　　　　　　　　　 以下実行処理内容                         #
##################################################################   
def main(args=None):
    hc = HumanCollaboration()

    CollaborationTool.start_executor()

    hc.execute()


if __name__ == '__main__':
    main()
