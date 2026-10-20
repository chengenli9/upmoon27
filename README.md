# Gazebo Simulation

Autonomy pipeline: SLAM Toolbox + Nav2

## Packages
All the following packages are located in the `/src` folder:
| Package | Purpose |
| --- | --- |
| `rover_description` | URDF/Xacro robot model, Gazebo launch, and robot_state_publisher |
| `rover_slam` | SLAM Toolbox configuration and launch files for mapping and localization |
| `rover_navigation` | Nav2 configuration and launch files; intended to use SLAM Toolbox for localization instead of AMCL |
| `rover_bringup` | Top-level launch files combining the robot description, SLAM, and navigation |


## Getting Started

### Docker Container
Setup the ROS2 environment. Run Docker scripts on the host, then run the ROS2 scripts inside the container. Each script contains a comment and Bash command for ease of use. Use `bash SCRIPT.sh` to run it.

1. Navigate to root directory.
    ```bash
    cd ~/upmoon27
    ```
2. Build Container from the host terminal.
    ```bash
    bash build_docker.sh
    ```
    Will take a few minutes.
3. Open a container terminal.
    ```bash
    bash start_docker.sh
    ```

4. Build the packages and then source the workspace.
    ```bash
    bash source.sh
    bash colcon.sh

Your environment is set up!

### Run Gazebo & Spawn Assets

For each new terminal, run `bash start_docker.sh` from the host repository root. Inside the container, navigate to the workspace and source the environment before running a ROS2 script:

```bash
# IMPORTANT
bash source.sh
```

Replace the example container path with your actual workspace path. These scripts do not source the environment automatically.

1. Terminal 1: Run Gazebo & Spawn robot URDF model.
    ```bash
    bash start_sim.sh
    ```
    This will launch Gazebo software with the default `obstacle.world` file, which can be found in the `gz_worlds` folder. It will also spawn the robot.

    ![gazebo example](gazebo_example.png)

2. Terminal 2: View in RViz2.
    ```bash
    bash start_rviz.sh
    ```
    This opens RViz2 with the `sim_test.rviz` configuration.

    ![rviz example](rviz_example.png)

3. Terminal 3: Control the robot with Keyboard.
    ```bash
    bash teleop_keyboard.sh
    ```
    This will run the default ROS2 `teleop_twist_keyboard` node. Focus this terminal and make sure Gazebo is playing. Use `i` to move forward, `,` to reverse, `j`/`l` to turn, and `k` to stop.

### Run SLAM for Mapping

1. Terminal 4: Run SLAM toolbox node inside a sourced container terminal.
    ```bash
    bash start_slam.sh
    ```
2. Move the robot around the world, and watch as the occupancy map grows.

### Run Full Pipeline (Gazebo + SLAM + Nav2) (NOT WORKING)

This is intended to run in a single terminal. It launches the simulation and SLAM with the addition of Nav2.

```bash
ros2 launch rover_bringup sim_bringup.launch.py
```

Run this command inside a sourced container terminal. The combined launch is still under development. Do not run it alongside the separate simulation and SLAM launches.

## Command Cheat Sheet

### Scripts

Run Docker scripts from the repository root on the host. Run the other scripts from the workspace inside a sourced container terminal.

| Command | Where  | Purpose |
| --- | --- | --- |
| `bash build_docker.sh` | Host | Build the image and start the container |
| `bash start_docker.sh` | Host | Open an interactive container shell |
| `bash colcon.sh` | Container | Build all ROS2 packages |
| `bash start_sim.sh` | Container | Launch Gazebo and spawn the robot |
| `bash start_rviz.sh` | Container | Open RViz2 |
| `bash teleop_keyboard.sh` | Container | Start keyboard control |
| `bash start_slam.sh` | Container | Start SLAM mapping |

After rebuilding, run `bash source.sh` again and restart affected nodes. Restart the simulation after changing Xacro or Gazebo plugin settings.

### Docker — Host Terminal

| Command | Purpose |
| --- | --- |
| `docker compose ps` | Check container status |
| `docker compose config --services` | List service names |
| `docker compose exec ros2 pwd` | Check the default directory inside the container |
| `docker compose up -d ros2` | Start the ROS2 service |
| `docker compose logs --tail=100 ros2` | View recent container logs |
| `docker compose stop ros2` | Stop the container |
| `docker compose down` | Remove project containers and networks |

Avoid `docker compose down -v` unless you intend to delete named volumes. If the service has a different name, update the Docker scripts and substitute that name in these commands.

### ROS2 — Container Terminal

Open a container terminal with `bash start_docker.sh`, navigate to the workspace, and source ROS2 and `install/setup.bash` before running these commands.

| Command | Purpose |
| --- | --- |
| `ros2 node list` | List running nodes |
| `ros2 topic list -t` | List topics and message types |
| `ros2 topic info /cmd_vel --verbose` | Inspect velocity publishers and subscribers |
| `ros2 topic echo /cmd_vel` | Watch keyboard velocity commands |
| `ros2 topic hz /scan` | Check laser scan frequency |
| `ros2 topic hz /odom` | Check odometry frequency |
| `ros2 topic echo /clock --once` | Check the simulation clock |
| `ros2 run tf2_ros tf2_echo odom base_link` | Inspect the odometry-to-robot transform |
| `ros2 param get /slam_toolbox use_sim_time` | Check SLAM's simulation-time setting |

Topic and node names may differ with your configuration. Use Ctrl+C to stop continuous output.

### Helpful Repository Commands — Host Terminal


Run scripts with `bash SCRIPT.sh`; execute permissions and a shebang are not required when Bash is invoked explicitly.
