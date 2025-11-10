import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command

from launch.actions import ExecuteProcess

def generate_launch_description():

    # 1. Localizar los directorios de los paquetes
    pkg_my_robot_description = get_package_share_directory('my_robot_description')
    pkg_my_robot_bringup = get_package_share_directory('my_robot_bringup')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # 2. Definir las rutas a los archivos (equivalente a <let ...>)
    urdf_path = os.path.join(pkg_my_robot_description, 'urdf', 'my_robot.urdf.xacro')
    gazebo_config_path = os.path.join(pkg_my_robot_bringup, 'config', 'gazebo_bridge.yaml')
    rviz_config_path = os.path.join(pkg_my_robot_description, 'rviz', 'urdf_config.rviz')
    world_path = os.path.join(pkg_my_robot_bringup, 'worlds', 'empty.sdf')

    # 3. Nodo: robot_state_publisher
    # Usa 'Command' para ejecutar 'xacro' en tiempo de lanzamiento
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', urdf_path])}]
    )

    # 4. Inclusión: Gazebo Sim (gz_sim.launch.py)
    # Equivale a <include ...> con <arg ...>

    
    gz_sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'{world_path} -r'}.items()
    )
    '''

    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', 'empty.sdf', '--render-engine', 'ogre'],
        output='screen'
    )
    '''

    # 5. Nodo: Creación del robot en Gazebo (ros_gz_sim create)
    spawn_robot_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description'],
        output='screen'
    )

    # 6. Nodo: Puente de parámetros (ros_gz_bridge parameter_bridge)
    gz_ros_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': gazebo_config_path}],
        output='screen'
    )

    # 7. Nodo: RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path]
    )

    # Retornar la descripción del lanzamiento con todos los nodos y acciones
    return LaunchDescription([
        robot_state_publisher_node,
        gz_sim_launch,
        spawn_robot_node,
        gz_ros_bridge_node,
        rviz_node
    ])