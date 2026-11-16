cmake_minimum_required(VERSION 3.8)
project(kepler_dexterous_hand_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf meshes launch rviz docs
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
