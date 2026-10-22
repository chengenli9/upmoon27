#!/usr/bin/env bash
# Run inside an interactive container terminal with ROS and the workspace sourced.
# The combined bringup is still under development; this script does not fix it.

# Run from the workspace root, where the other scripts are located.
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

# Keyboard control needs a terminal to read your key presses.
if [ ! -t 0 ]; then
    echo "Run this script in an interactive container terminal." >&2
    exit 1
fi

# Keep the process IDs so we can stop both programs when the script exits.
pipeline_pid=""
keyboard_pid=""

cleanup() {
    # Prevent another signal from interrupting shutdown.
    trap '' INT TERM

    echo "Stopping keyboard control and the simulation pipeline..."
    if [ -n "$keyboard_pid" ]; then
        kill "$keyboard_pid" 2>/dev/null || true
    fi
    if [ -n "$pipeline_pid" ]; then
        kill "$pipeline_pid" 2>/dev/null || true
    fi

    # Wait for the programs to finish shutting down.
    if [ -n "$keyboard_pid" ]; then
        wait "$keyboard_pid" 2>/dev/null || true
    fi
    if [ -n "$pipeline_pid" ]; then
        wait "$pipeline_pid" 2>/dev/null || true
    fi
}

# Clean up on normal exit, Ctrl+C, or a termination signal.
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# This launch file is intended to start Gazebo, SLAM Toolbox, and Nav2 together.
# Do not also call start_sim.sh or start_slam.sh: that would duplicate them.
echo "Starting Gazebo, SLAM, and Nav2..."
ros2 launch rover_bringup sim_bringup.launch.py &
pipeline_pid=$!

# Reuse the existing keyboard script. Explicitly connect it to the terminal
# because background commands otherwise may not receive keyboard input.
# exec replaces the wrapper shell, so keyboard_pid identifies the ROS process.
echo "Starting keyboard control. Use k to stop the robot and Ctrl+C to exit."
bash teleop_keyboard.sh "$@" </dev/tty &
keyboard_pid=$!

# Wait until either program exits, then the EXIT trap stops the other one.
# Requires Bash 4.3 or newer. Launch output and teleop share this terminal.
wait -n "$pipeline_pid" "$keyboard_pid"
