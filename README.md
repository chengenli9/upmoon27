# Gazebo Simulation

Autonomy pipeline: SLAM Toolbox + Nav2

## Packages
All the following packages are located in the `/src` folder:
- **rover_description**: URDF/Xacro robot description, Gazebo simulation launch, and robot_state_publisher.
- **rover_slam: slam_toolbox** configuration and launch files for online asynchronous SLAM mapping and localization.
- **rover_navigation**: Nav2 configuration and launch files for autonomous navigation, using slam_toolbox for localization instead of AMCL.
- **rover_bringup**: Top-level launch files that bring up the rover in simulation or on real hardware, combining robot description, slam_toolbox, and Nav2.

## Getting Started

### Docker Container
Setup the ROS2 environment

1. Navigate to root directory.
    ```
    cd ~/upmoon27
    ```
2. Build Container.
    ```
    ./build_docker.sh
    ```
    Will take a few minutes.
3. Run Container.
    ```
    ./start_docker.sh
    ```
4. Source workspace (VERY IMPORTANT)
    ```
    source install/setup.bash
    ```
5. Build the packages.
    ```
    colcon build 
    ```

Wah Lah! Your environment is setup. 

### Run Gazebo & Spawn Assets

1. Terminal 1: Run Gazebo & Spawn robot URDF model
    ```
    ros2 launch rover_description sim.launch.py
    ```
    This will launch Gazebo software with the default `obstacle.world` file, which can be found in `gz_worlds` folder. It will also spawn the robot. 

2. Terminal 2: View in RViz2
    
    Make sure each new terminal is in a container, run `./start_docker.sh` and `source install/setup.bash`
    ```
    rviz2 -d sim_test.rviz
    ```
3. Terminal 3: Control the robot with Keyboard
    ```
    ./teleop_kg.sh
    ```
    This will run the default ROS2 `telop_twist_keyboard` node.


### Run SLAM for Mapping
1. Terminal 4: Run SLAM toolbox node.
    ```
    ros2 launch rover_slam online_async_launch.py
    ```
2. Move the robot around the world, and watch as the occupancy map grows.

### Run Full Pipeline (Gazebo + SLAM + Nav2) (NOT WORKING)

This can be ran in just a single terminal. It will launch all the previous commands with the addition of the Nav2 node. 
```
ros2 launch rover_bringup sim_bringup.launch.py
```