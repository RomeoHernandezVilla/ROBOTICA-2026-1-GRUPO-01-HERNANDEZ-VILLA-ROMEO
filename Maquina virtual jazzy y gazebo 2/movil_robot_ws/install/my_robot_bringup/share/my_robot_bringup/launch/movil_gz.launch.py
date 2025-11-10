import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess

from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node
from launch.substitutions import Command
import xacro

def generate_launch_description():

    pkg_my_robot_description = get_package_share_directory('my_robot_description')
    pkg_my_robot_bringup = get_package_share_directory('my_robot_bringup')

    urdf_path = os.path.join(pkg_my_robot_description, 'urdf', 'my_robot.urdf.xacro')
    gazebo_config_path = os.path.join(pkg_my_robot_bringup, 'config', 'gazebo_bridge.yaml')

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', urdf_path])}]
    )

    '''

    path_urdf = '~/ROS2Dev/my_robot_ws/src/my_robot_description/urdf'


    node_robot_state_publisher =ExecuteProcess(
        cmd=['cd', '~/ROS2Dev/my_robot_ws/src/my_robot_description/urdf', '&&', 'ros2', 'run', 'robot_state_publisher',
              'robot_state_publisher', '--ros-args', '-p', 'robot_description:="$(xacro my_robot.urdf.xacro)"'],
             output='screen'
    )
    '''

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
