# This script starts the ROS2 container and opens an interactive Bash shell.
docker compose up -d ros2 && docker compose exec ros2 bash
