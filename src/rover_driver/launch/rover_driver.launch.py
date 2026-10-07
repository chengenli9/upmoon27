import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    params = os.path.join(
        get_package_share_directory('rover_driver'), 'config', 'rover_driver.yaml')
    return LaunchDescription([
        Node(
            package='rover_driver',
            executable='rover_driver',
            name='rover_driver',
            output='screen',
            parameters=[params],
        ),
    ])