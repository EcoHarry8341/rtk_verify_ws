import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_dir = get_package_share_directory('rtk_localization')
    config_dir = os.path.join(pkg_dir, 'config')

    # 原有的定位系统（请确认你的 launch 文件路径正确）
    rtk_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_dir, 'launch', 'rtk_localization.launch.py')
        )
    )

    # pointcloud_to_laserscan
    pc2scan = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        parameters=[os.path.join(config_dir, 'scan_filter_params.yaml')],
        remappings=[('cloud_in', '/rslidar_points'), ('scan', '/scan')],
    )

    # slam_toolbox
    slam = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        parameters=[os.path.join(config_dir, 'slam_mapping_absolute.yaml')],
    )

    # rviz2（可选，但推荐）
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', os.path.join(pkg_dir, 'config', 'mapping.rviz')],
    )

    return LaunchDescription([rtk_launch, pc2scan, slam, 
    rviz
    ])