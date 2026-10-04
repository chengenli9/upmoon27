FROM osrf/ros:humble-desktop-full

# Avoid interactive prompts during apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-pygame \
    python3-opencv \
    python3-scipy \
    python3-serial \
    python3-numpy \
    ros-humble-foxglove-bridge \
    ros-humble-apriltag \
    ros-humble-cv-bridge \
    ros-humble-xacro \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher \
    ros-humble-tf2-ros \
    ros-humble-tf2-msgs \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-rviz2 \
    ros-humble-gazebo-plugins \
    ros-humble-gazebo-msgs \
    ros-humble-teleop-twist-keyboard \
    'ros-humble-nav2-*' \
    ros-humble-navigation2 \
    ros-humble-turtlebot3 \
    ros-humble-turtlebot3-msgs \
    ros-humble-turtlebot3-simulations \
    ros-humble-slam-toolbox \
    ros-humble-robot-localization \
    ros-humble-pointcloud-to-laserscan \
    ros-humble-rtabmap-ros \
    libgazebo-dev \
    cmake \
    build-essential \
    curl \
    net-tools \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN python3 -m pip install --upgrade pip setuptools wheel

# Install uv for faster dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install python dependencies not in apt
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install pysabertooth typer "numpy<2.0.0" numpy-quaternion

# Create workspace
WORKDIR /workspace

# Set up environment sourcing in bashrc for interactive shells
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc
RUN printf '%s\n' "LS_COLORS=\$LS_COLORS:'ow=1;34:'" >> /root/.bashrc

# Default command
CMD ["/bin/bash"]
