import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess

# from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node
from launch.substitutions import Command
import xacro

def generate_launch_description():

    pkg_scara_description = get_package_share_directory('scara_description')
    pkg_scara_bringup = get_package_share_directory('scara_bringup')

    urdf_path = os.path.join(pkg_scara_description, 'urdf', 'gz2_scara.xacro')
    gazebo_config_path = os.path.join(pkg_scara_bringup, 'config', 'gz_bridge.yaml')

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', urdf_path])}]
    )


    gz_ros_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': gazebo_config_path}],
        output='screen'
    )

    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', 'empty.sdf', '--render-engine', 'ogre'],
        output='screen'
    )

    spaw_entity = ExecuteProcess(
        cmd=['ros2', 'run', 'ros_gz_sim', 'create', '-topic', 'robot_description']
    )


    return LaunchDescription([
        robot_state_publisher_node,
        gz_sim,
        spaw_entity,
        gz_ros_bridge_node
    ])
