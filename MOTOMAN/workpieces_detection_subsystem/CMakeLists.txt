cmake_minimum_required(VERSION 3.8)
project(workpieces_detection_subsystem)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(action_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(collaboration_manipulation_message REQUIRED)

# DetectWorkpieces service
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/DetectWorkpieces.srv"
  DEPENDENCIES
    collaboration_manipulation_message
)

# # Python node
# install(
#   PROGRAMS
#     scripts/WorkpiecesDetectionNode.py
#   DESTINATION lib/${PROJECT_NAME}
# )

# # Configuration files
# install(
#   DIRECTORY
#     config
#   DESTINATION share/${PROJECT_NAME}
# )

ament_python_install_package(${PROJECT_NAME})

ament_export_dependencies(rosidl_default_runtime std_msgs geometry_msgs action_msgs collaboration_manipulation_message)

ament_package()
