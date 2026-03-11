import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Configuration des chemins
    pkg_name = 'mon_robot_gazebo'
    urdf_file = os.path.join(get_package_share_directory(pkg_name), 'urdf', 'robot.urdf')

    # 2. Lecture du robot
    with open(urdf_file, 'r') as infp:
        robot_description_raw = infp.read()

    # 3. Noeud Robot State Publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_raw,
            'use_sim_time': True
        }]
    )

    # 4. Inclure Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch'), '/gazebo.launch.py']),
    )

    # 5. Faire apparaître le robot
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description',
                   '-entity', 'staubli_rx160'],
        output='screen'
    )

    # 6. Charger le Joint State Broadcaster
    load_joint_state_broadcaster = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'joint_state_broadcaster'],
        output='screen'
    )

    # 7. Charger le Position Controller (Arm Controller)
    load_arm_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'arm_controller'],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        node_robot_state_publisher,
        spawn_entity,
        # On attend 5 secondes que Gazebo soit stable avant de charger les moteurs
        TimerAction(period=5.0, actions=[load_joint_state_broadcaster]),
        TimerAction(period=7.0, actions=[load_arm_controller]),
    ])