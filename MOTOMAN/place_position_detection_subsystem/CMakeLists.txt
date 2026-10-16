cmake_minimum_required(VERSION 3.8)
project(place_position_detection_subsystem)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(action_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(collaboration_manipulation_message REQUIRED)

# DetectPlacePosition service
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/DetectPlacePosition.srv"
  DEPENDENCIES
    collaboration_manipulation_message
)

# Python node
install(
  PROGRAMS
    scripts/PlacePositionDetectionNode.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_python_install_package(${PROJECT_NAME})

ament_export_dependencies(rosidl_default_runtime std_msgs geometry_msgs action_msgs collaboration_manipulation_message)

ament_package()
