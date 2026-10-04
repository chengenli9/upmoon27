# Simulation bringup: Gazebo + robot_state_publisher + rtabmap (RGB-D) + nav2.

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():

    world = LaunchConfiguration('world')
    use_sim_time = LaunchConfiguration('use_sim_time')
    nav2_params_file = LaunchConfiguration('nav2_params_file')
    rtabmap_params_file = LaunchConfiguration('rtabmap_params_file')
    database_path = LaunchConfiguration('database_path')
    delete_db_on_start = LaunchConfiguration('delete_db_on_start')
    autostart = LaunchConfiguration('autostart')
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_config = LaunchConfiguration('rviz_config')

    default_nav2_params_file = os.path.join(
        get_package_share_directory('rover_navigation'), 'config', 'nav2_params_pointcloud.yaml')
    default_rtabmap_params_file = os.path.join(
        get_package_share_directory('rover_slam'), 'config', 'rtabmap_params.yaml')

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('rover_description'), 'launch', 'sim.launch.py')),
        launch_arguments={'world': world}.items()
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

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
        condition=IfCondition(use_rviz)
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value='/workspace/gz_worlds/arena_box_craters.world',
            description='Full path to the Gazebo world file to load'),

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
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

        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Whether to launch RViz'),

        DeclareLaunchArgument(
            'rviz_config',
            default_value='/workspace/sim_test.rviz',
            description='Full path to the RViz config file to use'),

        sim,
        slam,
        navigation,
        rviz,
    ])
