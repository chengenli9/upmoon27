# Real-robot bringup: robot_state_publisher + rtabmap (RGB-D) + nav2.

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    nav2_params_file = LaunchConfiguration('nav2_params_file')
    rtabmap_params_file = LaunchConfiguration('rtabmap_params_file')
    database_path = LaunchConfiguration('database_path')
    delete_db_on_start = LaunchConfiguration('delete_db_on_start')
    autostart = LaunchConfiguration('autostart')

    default_nav2_params_file = os.path.join(
        get_package_share_directory('rover_navigation'), 'config', 'nav2_params_pointcloud.yaml')
    default_rtabmap_params_file = os.path.join(
        get_package_share_directory('rover_slam'), 'config', 'rtabmap_params.yaml')

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('rover_description'), 'launch', 'rover.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('rover_slam'), 'launch', 'rtabmap_launch.py')),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'rtabmap_params_file': rtabmap_params_file,
            'database_path': database_path,
            'delete_db_on_start': delete_db_on_start,
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
            'rtabmap_params_file',
            default_value=default_rtabmap_params_file,
            description='Full path to the rtabmap parameters file'),

        DeclareLaunchArgument(
            'database_path',
            default_value='/workspace/.rtabmap/rtabmap.db',
            description='Full path to the rtabmap session database'),

        DeclareLaunchArgument(
            'delete_db_on_start',
            default_value='true',
            description='Delete the rtabmap database on startup for a fresh map each run'),

        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            description='Automatically startup the nav2 stack'),

        rsp,
        slam,
        navigation,
    ])
