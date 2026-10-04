#!/bin/bash

echo "Cleaning workspace..."
sudo rm -rf build install log

echo "Building packages..."
colcon build --symlink-install

echo "Sourcing local setup..."
source install/local_setup.bash

echo "

Ready To Launch!

"
