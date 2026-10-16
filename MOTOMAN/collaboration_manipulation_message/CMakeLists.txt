cmake_minimum_required(VERSION 3.8)
project(collaboration_manipulation_message)

# 必要なパッケージ
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(action_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# メッセージの追加（msgディレクトリ内の.msgファイル一覧）
set(MSG_FILES
  "msg/ErrorInfomation.msg"
  "msg/MonitoringArea.msg"
  "msg/MonitoringAreaList.msg"
  "msg/PlaceAreaCandidatesList.msg"
  "msg/PlacePositionCandidate.msg"
  "msg/PlacePositionDetectionResult.msg"
  "msg/Property.msg"
  "msg/Status.msg"
  "msg/TaskCommand.msg"
  "msg/TaskCommandList.msg"
  "msg/TaskResult.msg"
  "msg/TargetArea.msg"
  "msg/WorkDetectionResult.msg"
  "msg/WorkDetectionResultList.msg"
  "msg/PersonObstacleInfomation.msg"
  "msg/PersonObstaclePoint.msg"
  "msg/PersonObstacleDetect.msg"
  "msg/EnviromentDetectionInfomation.msg"
  "msg/TaskStatus.msg"
  # "msg/WorkspacePerceptionResult.msg"
)


# メッセージ生成の定義
rosidl_generate_interfaces(${PROJECT_NAME}
  ${MSG_FILES}
  DEPENDENCIES std_msgs geometry_msgs action_msgs
)

# 依存のエクスポート
ament_export_dependencies(rosidl_default_runtime std_msgs geometry_msgs action_msgs)

# パッケージのインストール設定
ament_package()