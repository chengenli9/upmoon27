# Simulation bringup: Gazebo + robot_state_publisher + slam_toolbox

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
    slam_params_file = LaunchConfiguration('slam_params_file')
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_config = LaunchConfiguration('rviz_config')

    default_slam_params_file = os.path.join(
        get_package_share_directory('rover_slam'), 'config', 'mapper_params_online_async.yaml')

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('rover_description'), 'launch', 'sim.launch.py')),
        launch_arguments={'world': world}.items()
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('rover_slam'), 'launch', 'online_async_launch.py')),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': slam_params_file,
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
            'slam_params_file',
            default_value=default_slam_params_file,
            description='Full path to the slam_toolbox parameters file'),

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
        rviz,
    ])
