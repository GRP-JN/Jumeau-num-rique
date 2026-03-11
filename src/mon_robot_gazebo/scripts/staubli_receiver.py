#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import socket
import math

class StaubliReceiverNode(Node):
    def __init__(self):
        super().__init__('staubli_receiver')
        
        # Ce "publisher" envoie les données au modèle 3D (URDF / RViz)
        self.publisher_ = self.create_publisher(JointState, 'joint_states', 10)
        
        # Paramètres réseau de la connexion directe
        self.robot_ip = '192.168.99.25'
        self.port = 1000
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_robot()

        # Le timer correspond aux 4ms (0.004s) de votre syncTask.pgx
        self.timer = self.create_timer(0.004, self.read_and_publish)

    def connect_to_robot(self):
        try:
            self.get_logger().info(f"Tentative de connexion au robot sur {self.robot_ip}:{self.port}...")
            self.sock.connect((self.robot_ip, self.port))
            self.get_logger().info("Connexion réussie ! En attente des données...")
        except Exception as e:
            self.get_logger().error(f"Échec de connexion (Vérifiez le câble et le ping) : {e}")

    def read_and_publish(self):
        try:
            # On lit le message envoyé par le robot (ex: "45.1, -10.5, 90.0, 0.0, 45.0, 0.0\n")
            data = self.sock.recv(1024).decode('utf-8').strip()
            
            if data:
                # On découpe la chaîne avec la virgule pour isoler chaque moteur
                angles_deg = [float(val) for val in data.split(',')]
                
                # Sécurité : on vérifie qu'on a bien reçu les 6 axes
                if len(angles_deg) == 6:
                    msg = JointState()
                    msg.header.stamp = self.get_clock().now().to_msg()
                    
                    # Noms exacts de vos articulations dans votre fichier URDF
                    msg.name = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
                    
                    # ATTENTION : Le robot parle en Degrés, ROS 2 et RViz parlent en Radians !
                    # On fait la conversion ici.
                    msg.position = [math.radians(a) for a in angles_deg]
                    
                    # On publie les données pour RViz2
                    self.publisher_.publish(msg)
                    
        except Exception as e:
            # On ignore les erreurs mineures (comme une trame vide) pour ne pas planter le direct
            pass

def main(args=None):
    rclpy.init(args=args)
    node = StaubliReceiverNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.sock.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
