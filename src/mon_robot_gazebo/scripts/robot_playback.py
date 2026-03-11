#!/usr/bin/env python3
import rclpy
import json
import os
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from ament_index_python.packages import get_package_share_directory

class RobotPlayback(Node):
    def __init__(self):
        super().__init__('robot_playback_node')
        self.publisher_ = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        
        # Charger la banque de données
        pkg_path = get_package_share_directory('mon_robot_gazebo')
        json_path = os.path.join(pkg_path, 'scripts', 'positions.json')
        
        with open(json_path, 'r') as f:
            self.data = json.load(f)
            
        self.get_logger().info(f'Banque de données chargée : {len(self.data)} actions trouvées.')
        self.current_idx = 0
        self.timer = self.create_timer(3.0, self.execute_next_action)

    def execute_next_action(self):
        if self.current_idx >= len(self.data):
            self.get_logger().info('Fin de la séquence.')
            self.timer.cancel()
            return

        action = self.data[self.current_idx]
        self.get_logger().info(f"Exécution de : {action['name']}")

        msg = JointTrajectory()
        msg.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        
        point = JointTrajectoryPoint()
        point.positions = [float(p) for p in action['pos']]
        point.time_from_start = Duration(sec=2, nanosec=0)
        
        msg.points.append(point)
        self.publisher_.publish(msg)
        
        self.current_idx += 1

def main(args=None):
    rclpy.init(args=args)
    node = RobotPlayback()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
