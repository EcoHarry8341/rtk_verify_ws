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
    # 2. 注入物理灵魂：建立静态 TF 树
    # 规则：[x, y, z, roll, pitch, yaw, parent_frame, child_frame]
    # 请根据你用尺子量出来的真实数据修改这些值！
    # =========================================================
    
# 替换雷达 TF
    tf_base_to_lidar = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_base_to_lidar',
        arguments=['-0.019', '0.0', '0.830', '0.0', '0.0', '0.0', 'base_footprint', 'rslidar']
    )

    # 替换 IMU TF
    tf_base_to_imu = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_base_to_imu',
        arguments=['-0.087', '0.0', '0.596', '0.0', '0.0', '0.0', 'base_footprint', 'imu_link']
    )

    # 替换 GPS 天线 TF
    tf_base_to_gps = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_base_to_gps',
        arguments=['-0.410', '0.135', '0.509', '0.0', '0.0', '0.0', 'base_footprint', 'gps_link']
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
        remappings=[('odometry/filtered', 'odometry/global')]
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
        tf_base_to_lidar,  # 挂载雷达
        tf_base_to_imu,    # 挂载IMU
        tf_base_to_gps,    # 挂载天线
        ekf_local_node,
        ekf_global_node,
        navsat_transform_node
    ])