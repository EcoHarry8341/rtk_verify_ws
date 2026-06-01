import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_dir = get_package_share_directory('rtk_localization')
    config_file = os.path.join(pkg_dir, 'config', 'dual_ekf_navsat.yaml')

    # 1. RTK 硬件驱动
    um982_driver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('nmea_navsat_driver'), 'launch', 'um982.launch.py')
        )
    )

    # =========================================================
    # 2. 注入物理灵魂：建立静态 TF 树 (强制 RPY 为 0，保证 2D SLAM 切片水平)
    # =========================================================
    
    # 2.1 雷达 (使用标定推算出的极高精度 XYZ，强制平放)
    # yaw = π: 传感器 X 轴翻转 180° 指向物理车头，符合 REP-105
    tf_base_to_lidar = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_base_to_lidar',
        arguments=[
            '--x', '-0.018', '--y', '0.027', '--z', '0.756',
            '--roll', '0.0', '--pitch', '0.0', '--yaw', '0.0',
            '--frame-id', 'base_footprint', '--child-frame-id', 'rslidar'
        ]
    )

    # 2.2 IMU
    # yaw = π: 传感器 X 轴翻转 180° 指向物理车头，符合 REP-105
    tf_base_to_imu = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_base_to_imu',
        arguments=[
            '--x', '-0.087', '--y', '0.0', '--z', '0.596',
            '--roll', '0.0', '--pitch', '0.0', '--yaw', '0.0',
            '--frame-id', 'base_footprint', '--child-frame-id', 'imu_link'
        ]
    )

    # 2.3 GPS天线
    # yaw = π: 传感器 X 轴翻转 180° 指向物理车头，符合 REP-105
    tf_base_to_gps = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_base_to_gps',
        arguments=[
            '--x', '-0.410', '--y', '0.135', '--z', '0.509',
            '--roll', '0.0', '--pitch', '0.0', '--yaw', '0.0',
            '--frame-id', 'base_footprint', '--child-frame-id', 'gps_link'
        ]
    )
    # =========================================================

    # 3. Local EKF (小脑)
    ekf_local_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node_local',
        output='screen',
        parameters=[config_file],
        remappings=[('odometry/filtered', 'odometry/local')]
    )

    # 4. Global EKF (大脑)
    ekf_global_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node_global',
        output='screen',
        parameters=[config_file],
        remappings=[
            ('odometry/filtered', 'odometry/global'),
            ('/set_pose', '/initialpose')
        ]
    )

    # 5. Navsat Transform (天眼转换器)
    navsat_transform_node = Node(
        package='robot_localization',
        executable='navsat_transform_node',
        name='navsat_transform_node',
        output='screen',
        parameters=[config_file],
        remappings=[
            ('imu/data', '/IMU_data'),            
            ('gps/fix', '/fix'),                  
            ('gps/filtered', 'gps/filtered'),
            ('odometry/gps', 'odometry/gps'),     
            ('odometry/filtered', 'odometry/global')
        ]
    )

    return LaunchDescription([
        um982_driver_launch,
        tf_base_to_lidar,  
        tf_base_to_imu,    
        tf_base_to_gps,    
        ekf_local_node,
        ekf_global_node,
        navsat_transform_node
    ])
