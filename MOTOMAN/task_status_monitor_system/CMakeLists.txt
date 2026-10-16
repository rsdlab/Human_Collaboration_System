cmake_minimum_required(VERSION 3.0.2)
project(task_status_monitor_system)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(action_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(collaboration_manipulation_message REQUIRED)

#ament_python_install_package(${PROJECT_NAME})

ament_export_dependencies(rosidl_default_runtime std_msgs geometry_msgs action_msgs collaboration_manipulation_message)

ament_package()
