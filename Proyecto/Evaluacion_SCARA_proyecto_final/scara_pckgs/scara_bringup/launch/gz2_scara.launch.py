import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch.substitutions import Command
import xacro

def generate_launch_description():

    pkg_scara_description = get_package_share_directory('scara_description')
    pkg_scara_bringup = get_package_share_directory('scara_bringup')

    # Archivos de configuración
    urdf_path = os.path.join(pkg_scara_description, 'urdf', 'gz2_scara.xacro')
    gazebo_config_path = os.path.join(pkg_scara_bringup, 'config', 'gz_bridge.yaml')

    # Procesar robot (xacro)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', urdf_path])}]
    )

    # Puente de ROS-Gazebo
    gz_ros_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': gazebo_config_path}],
        output='screen'
    )

    # Gazebo Sim (Arranca en Play con -r)
    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', 'empty.sdf', '--render-engine', 'ogre'],
        output='screen'
    )

    # Spawn (Aparecer el robot)
    # AQUÍ ESTÁ TU CONFIGURACIÓN SOLICITADA:
    spaw_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description', 
            '-name', 'scara_robot', 
            '-z', '0.0',                  # <--- Z en 0.0 (Al piso)
            '-J', 'link_1_joint', '0.0',  # Hombro recto
            '-J', 'link_2_joint', '0.0',  # Codo recto
            '-J', 'link_3_joint', '0.0'   # Muñeca recta
        ],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        gz_sim,
        spaw_entity,
        gz_ros_bridge_node
    ])