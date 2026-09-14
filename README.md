# ROS2 Workspace Template

## Overview

This guide provides a basic setup and usage workflow for developing ROS 2 applications in a Linux environment. It covers setting up **WSL2 and Docker on Windows**, creating and building a ROS 2 workspace, creating and running ROS 2 packages, and configuring communication between multiple devices.

This repository uses **ROS 2 Humble**, which is based on **Ubuntu 22.04 (Jammy)**. Docker is used to provide a consistent Ubuntu environment so that the ROS 2 development environment remains consistent across different machines.


## Table of Contents

1. [Creating a Branch from This Template](#creating-a-branch-from-this-template)
2. [WSL (Windows Subsystem for Linux)](#wsl-windows-subsystem-for-linux)
   - [Install WSL2](#install-wsl2)
   - [Running WSL2](#running-wsl)
3. [Setup Docker](#setup-docker)
   - [Install Docker](#install-docker)
   - [Running the Docker Container](#running-the-docker-container)
4. [ROS2 Workspaces](#ros2-workspaces)
5. [Building the Workspace](#building-the-workspace)
   - [How to Use `colcon build`](#how-to-use-colcon-build)
   - [Useful Options](#useful-options)
   - [Sourcing the Workspace](#sourcing-the-workspace)
6. [How to Create a ROS2 Package](#how-to-create-a-ros2-package)
7. [Running a ROS2 Package](#running-a-ros2-package)
8. [ROS2 Multi-device Communication](#ros2-multi-device-communication)
   - [Verify Communication](#verify-communication)

## Creating a Branch from This Template

This repository's `template_ws` branch serves as a template for creating new ROS 2 workspace branches. Follow these steps to create your own branch based on this template:

### Using Git Command Line
1. Make sure you have the latest version of the repository:
    ```
    git fetch origin
    ```

2. Create a new branch from the `template_ws` branch:
    ```
    git checkout -b <your-new-branch-name> origin/template_ws
    ```
    Replace `<your-new-branch-name>` with your desired branch name (e.g., `my-robot-ws`, `project-x`, etc.)

3. Push your new branch to the remote repository:
    ```
    git push -u origin <your-new-branch-name>
    ```

### Using GitHub Web Interface
1. Navigate to the [upmoon27 repository](https://github.com/chengenli9/upmoon27)

2. Click the **Branch** dropdown button near the top of the page

3. Select the `template_ws` branch from the list

4. Click the **New branch** button (or use the branch selector dropdown)

5. Enter your new branch name and ensure `template_ws` is selected as the source branch

6. Click **Create branch**

7. To work with your new branch locally, pull it:
    ```
    git fetch origin
    git checkout <your-new-branch-name>
    ```

## WSL (Windows Subsystem for Linux)

If you're using a Windows Device and don't have access to a Linux Machine, you can use WSL.
### Install WSL2
In a terminal run:
```
wsl --install
```
This is will install the default Ubuntu distrubution (26.04). Any Ubuntu version is sufficient as long as it's 22.04 or newer. 

After installation completes, restart your computer for the changes to take effect.

### Running WSL

#### Launch WSL
To start WSL and access the Linux environment, open a PowerShell or Command Prompt and run:
```
wsl
```

This will launch the default WSL distribution (usually Ubuntu). You'll be logged in as your default WSL user.

## Setup Docker
ROS2 Humble runs on Ubuntu 22.04 Jammy, so we need to make sure we're running the same package versions. This is where Docker comes in. Docker is a tool that packages your application and all its required settings into a portable, lightweight box called a container. This container acts like a mini-environment that makes sure your code works the exact same way on your laptop, a coworker's computer, or a cloud server.

### Install Docker

1. Update the package index
    ```bash 
    sudo apt update && sudo apt upgrade -y
    ```

2. Install certificates and curl
    ```
    sudo apt install -y apt-transport-https ca-certificates curl
    ```

3. Create directory for keys and download Docker's GPG key
    ```
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    ```

4. Add the official Docker repository to your APT sources
    ```
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    ```

5. Install Docker Engine
    ```
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```

6. Configure Non-Root User Acess
    ```
    sudo usermod -aG docker $USER
    ```
    This will require you to restart WSL. 

7. Verify the Docker service status
    ```
    systemctl status docker
    ```
    If docker is running successfully, it should output this:
    ```bash 
    docker.service - Docker Application Container Engine
     Loaded: loaded (/usr/lib/systemd/system/docker.service; enabled; preset: enabled)
     Active: active (running) since Sun 2026-09-13 19:01:54 PDT; 40min ago
    ```

### Running The Docker Container
1. Navigate to the source directory:
    ```
    cd ~/upmoon27
    ```
2. Build the container:
    ```
    docker compose up -d --build
    ```
3. Run the container:
    ```
    xhost +local:docker
    docker compose exec ros2 bash 
    ```

## ROS2 Workspaces
A standard ROS 2 workspace template directory tree features a root folder containing a src directory for source code, which expands into `build`, `install`, and `log` folders after running a build command

Example: 
```
ros2_ws/
├── build/
├── install/
├── log/
└── src/
    └── my_python_package1/
        ├── my_python_package1/
        ├── resource/
        ├── package.xml
        ├── setup.py
        └── setup.cfg
    └── my_python_package2/
        ├── my_python_package2/
        ├── resource/
        ├── package.xml
        ├── setup.py
        └── setup.cfg
```

For this Repo:
```
upmoon27/
├── build/
├── install/
├── log/
└── src/
    └── rover_description/
        ├── rover_description/
        ├── resource/
        ├── package.xml
        ├── setup.py
        └── setup.cfg
    └── rover_navigation/
        ├── rover_navigation/
        ├── resource/
        ├── package.xml
        ├── setup.py
        └── setup.cfg
```
## Building The Workspace
`colcon build` is a command-line tool used in ROS2 to compile source code, handle package dependencies, and set up the workspace for execution

### How To Use `colcon build`
1. Navigate to the root directory of your ROS2 workspace (e.g., ~/ros2_ws) 
2. Ensure your source packages are inside a subdirectory named `src`.
3. Run the build command:
    ```
    colcon build
    ```
### Useful Options
- Symlink Install: use the `--symlink-install` so that changes to Python or interface files take effect immediately without needing to rebuild every time: 
  ```
  colcon build --symlink-install
  ```

- Select Specific Packages: Build only a specific package instead of the entire workspace:
  ```
  colcon build --packages-select <package_name>
  ```

### Sourcing The Workspace
After building your workspace, you must source the setup files so that ROS2 can find your packages, nodes, and executables 

Navigate to your workspace directory and run the following command:
```
source install/setup.bash
```

## How To Create a ROS2 Package
Navigate to the `/src` folder in your ROS2 workspace.

Run the command:
```
ros2 pkg create --build-type ament_python --license Apache-2.0 <package_name>
```
Verify package structure:
```
my_python_package/
  ├── my_python_package/
  ├── resource/
  ├── package.xml
  ├── setup.py
  └── setup.cfg
```
## Running a ROS2 Package
Make sure you are in the root directory of the workspace and you `colcon build`. 

`ros2 run`: Runs one specific node. Best for quick testing or simple single-node tasks.
```
ros2 run <package_name> <executable_name>
```
Example: Running the `teleop_twist_keyboard`
```
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

`ros2 launch`: Runs multiple nodes. Use this when you want to spin up an entire robot system (e.g., bringing up a camera driver, a lidar driver, and a mapping node all at once) 
```
ros2 launch <package_name> <launch_file_name>
```
Example: To launch a ros2 tutorial 
```
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```


## ROS2 Multi-device Communication
In ROS 2, nodes communicate across different machines or processes via a ROS Domain ID. By default, all ROS 2 nodes discover each other on Domain 0 because they use the same underlying network subnet and DDS (Data Distribution Service) settings.

To isolate or connect nodes across a network, you change the ROS_DOMAIN_ID environment variable in the terminal before running your node. 

```
export ROS_DOMAIN_ID=27 
```
### Verify Communcation
Device 1: Publisher
```
export ROS_DOMAIN_ID=27
ros2 run demo_nodes_py talker
```

Device 2: Listener
```
export ROS_DOMAIN_ID=27
ros2 run demo_nodes_py listener
```
You can also see if the topic is publishing by running `ros2 topic list`. You should see the following output:
```
/chatter
/parameter_events
/rosout
```

