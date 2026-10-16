cmake_minimum_required(VERSION 3.8)
project(collaboration_manipulation_module)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(action_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(collaboration_manipulation_message REQUIRED)

# Pythonモジュール（setup.pyを使う場合はこの行が必要）
ament_python_install_package(${PROJECT_NAME})

# 依存のエクスポート
ament_export_dependencies(rosidl_default_runtime std_msgs geometry_msgs action_msgs collaboration_manipulation_message)

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/BeginIntervention.srv"
  "srv/CancelTask.srv"
  "srv/EndIntervention.srv"
  "srv/FinishTask.srv"
  "srv/GetStatus.srv"
  "srv/NotifyTaskStatus.srv"
  "srv/PauseTask.srv"
  "srv/ResumeTask.srv"
  "srv/SendTaskCommand.srv"
  "srv/StartManipulationTask.srv"
  "srv/StopManipulationTask.srv"
  "srv/TerminateSystem.srv"
  DEPENDENCIES
    std_msgs
    collaboration_manipulation_message
)

ament_package()
