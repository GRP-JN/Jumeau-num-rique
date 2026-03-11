import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Va chercher ton fichier URDF compilé
    urdf_file = os.path.join(get_package_share_directory('mon_robot_gazebo'), 'urdf', 'robot.urdf')
    
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([
        # Le noeud qui lit l'URDF et le publie pour RViz
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}]
        ),
        # Lance RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2'
        )
    ])