import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    rtabmap_params_file = LaunchConfiguration('rtabmap_params_file')
    database_path = LaunchConfiguration('database_path')
    delete_db_on_start = LaunchConfiguration('delete_db_on_start')

    default_params_file = os.path.join(
        get_package_share_directory('rover_slam'), 'config', 'rtabmap_params.yaml')

    # Front/rear cameras are namespaced 'camera'/'camera_rear' in rover_description's
    # gazebo_ros_camera plugins, giving fixed topic names regardless of spawn order.
    node_rgbd_sync_front = Node(
        package='rtabmap_sync',
        executable='rgbd_sync',
        name='rgbd_sync_front',
        output='screen',
        parameters=[{'approx_sync': True, 'use_sim_time': use_sim_time}],
        remappings=[
            ('rgb/image', '/camera/image_raw'),
            ('depth/image', '/camera/depth/image_raw'),
            ('rgb/camera_info', '/camera/camera_info'),
            ('rgbd_image', '/camera/rgbd_image'),
        ]
    )

    node_rgbd_sync_rear = Node(
        package='rtabmap_sync',
        executable='rgbd_sync',
        name='rgbd_sync_rear',
        output='screen',
        parameters=[{'approx_sync': True, 'use_sim_time': use_sim_time}],
        remappings=[
            ('rgb/image', '/camera_rear/image_raw'),
            ('depth/image', '/camera_rear/depth/image_raw'),
            ('rgb/camera_info', '/camera_rear/camera_info'),
            ('rgbd_image', '/camera_rear/rgbd_image'),
        ]
    )

    node_rtabmap_common_kwargs = dict(
        package='rtabmap_slam',
        executable='rtabmap',
        name='rtabmap',
        output='screen',
        parameters=[rtabmap_params_file, {
            'use_sim_time': use_sim_time,
            'database_path': database_path,
        }],
        remappings=[
            ('rgbd_image0', '/camera/rgbd_image'),
            ('rgbd_image1', '/camera_rear/rgbd_image'),
            ('odom', '/odom'),
            ('grid_map', '/map'),
        ]
    )

    # Split into two nodes since the delete_db_on_start arg maps to a CLI flag,
    # not a yaml parameter, and launch conditions can't toggle arguments in place.
    node_rtabmap_fresh = Node(
        **node_rtabmap_common_kwargs,
        arguments=['-d'],
        condition=IfCondition(delete_db_on_start),
    )

    node_rtabmap_persist = Node(
        **node_rtabmap_common_kwargs,
        condition=UnlessCondition(delete_db_on_start),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use sim time if true'),

        DeclareLaunchArgument(
            'rtabmap_params_file',
            default_value=default_params_file,
            description='Full path to the rtabmap parameters file'),

        DeclareLaunchArgument(
            'database_path',
            default_value='/workspace/.rtabmap/rtabmap.db',
            description='Full path to the rtabmap session database'),

        DeclareLaunchArgument(
            'delete_db_on_start',
            default_value='true',
            description='Delete the rtabmap database on startup for a fresh map each run'),

        node_rgbd_sync_front,
        node_rgbd_sync_rear,
        node_rtabmap_fresh,
        node_rtabmap_persist,
    ])
