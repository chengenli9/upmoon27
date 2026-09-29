# Real-robot bringup: robot_state_publisher + slam_toolbox + nav2.

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    nav2_params_file = LaunchConfiguration('nav2_params_file')
    slam_params_file = LaunchConfiguration('slam_params_file')
    autostart = LaunchConfiguration('autostart')

    default_nav2_params_file = os.path.join(
        get_package_share_directory('rover_navigation'), 'config', 'nav2_params.yaml')
    default_slam_params_file = os.path.join(
        get_package_share_directory('rover_slam'), 'config', 'mapper_params_online_async.yaml')

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('rover_description'), 'launch', 'rover.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('rover_slam'), 'launch', 'online_async_launch.py')),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': slam_params_file,
        }.items()
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('rover_navigation'), 'launch', 'navigation.launch.py')),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': nav2_params_file,
            'autostart': autostart,
        }.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use sim time if true'),

        DeclareLaunchArgument(
            'nav2_params_file',
            default_value=default_nav2_params_file,
            description='Full path to the nav2 parameters file'),

        DeclareLaunchArgument(
            'slam_params_file',
            default_value=default_slam_params_file,
            description='Full path to the slam_toolbox parameters file'),

        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            description='Automatically startup the nav2 stack'),

        rsp,
        slam,
        navigation,
    ])
