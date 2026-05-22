# ROS Autonomous Mobile Robot

This project is a ROS Noetic based autonomous mobile robot simulation developed in Ubuntu 20.04.

The robot model was created using URDF/Xacro and simulated in Gazebo environment.  
A custom map was generated using SLAM and the robot can autonomously navigate on this map using RViz and Move Base.

A custom PyQt5 GUI was also developed for:

- Sending target positions
- Autonomous navigation
- Manual robot control
- Adjustable linear and angular velocity
- Semi-autonomous driving



---

## Features

- Differential drive mobile robot
- Autonomous navigation
- Semi-autonomous control
- SLAM mapping
- RViz visualization
- Gazebo simulation
- Goal-based navigation
- Adjustable robot speed
- PyQt5 GUI control panel

---

## Technologies Used

- ROS Noetic
- Ubuntu 20.04
- Gazebo
- RViz
- Move Base
- AMCL
- SLAM Gmapping
- URDF/Xacro
- Python
- PyQt5

---

## System Architecture

GUI  --->  /move_base_simple/goal  
GUI  --->  /cmd_vel  

Move Base  
AMCL Localization  
Costmaps  
Global & Local Planner  
Robot Controller  
Gazebo Simulation  

---

## Run Project

```bash
cd ~/catkin_ws

catkin_make

source devel/setup.bash

roslaunch otonom_robot bringup.launch
