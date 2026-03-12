import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, Image
from std_msgs.msg import Header
import time

class TwinDashboardNode(Node):
    def __init__(self):
        super().__init__('twin_dashboard_node')
        
        # Publisher pour la 3D (Gazebo/RViz/Foxglove)
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        
        # Simulation de slots pour les caméras (Optris, etc.)
        self.cam_pub = self.create_publisher(Image, 'camera/thermal_image', 10)

        # Timer pour lire les données à 4ms (correspondant à la syncTask du robot)
        self.timer = self.create_timer(0.004, self.publish_data)
        self.get_logger().info("Tableau de bord du Jumeau Numérique démarré.")

    def publish_data(self):
        # Ici, nous récupérons les données que vous loggez en CSV
        # Pour l'affichage direct, nous créons le message JointState
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        
        # Exemple de récupération (à lier à votre lecture de queue/CSV)
        # msg.position = [j1, j2, j3, j4, j5, j6] (en radians)
        
        self.joint_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = TwinDashboardNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()