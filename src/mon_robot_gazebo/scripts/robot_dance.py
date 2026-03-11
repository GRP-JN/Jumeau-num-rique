#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class RobotDance(Node):
    def __init__(self):
        super().__init__('robot_dance_node')
        # On publie sur le topic de ton contrôleur
        self.publisher_ = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.timer = self.create_timer(5.0, self.send_trajectory)
        self.state = 0
        self.get_logger().info('La danse du Stäubli commence !')

    def send_trajectory(self):
        msg = JointTrajectory()
        msg.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        
        point = JointTrajectoryPoint()
        
        if self.state == 0:
            # Position 1 : Bras incliné
            point.positions = [0.0, 0.5, -0.5, 0.0, 0.5, 0.0]
            self.state = 1
        else:
            # Position 2 : Bras droit
            point.positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            self.state = 0
            
        point.time_from_start = Duration(sec=2, nanosec=0)
        msg.points.append(point)
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = RobotDance()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
