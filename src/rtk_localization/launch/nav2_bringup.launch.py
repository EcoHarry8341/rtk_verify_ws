import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_rtk = get_package_share_directory('rtk_localization')
    pkg_nav2 = get_package_share_directory('nav2_bringup')
    
    map_yaml_file = os.path.join(os.path.expanduser('~'), 'rtk_verify_ws', 'maps', 'absolute_parking052800.yaml')
    nav2_params_file = os.path.join(pkg_rtk, 'config', 'nav2_params_absolute.yaml')

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': map_yaml_file,
            'use_sim_time': 'false',
            'params_file': nav2_params_file,
            'autostart': 'true'
        }.items()
    )

    return LaunchDescription([nav2_launch])