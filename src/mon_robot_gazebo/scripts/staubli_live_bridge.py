#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import PoseStamped
import socket
import math
import csv
import os
import time
from datetime import datetime

# CONFIGURATION
HOST = "0.0.0.0" 
PORT = 2005 

class StaubliBridgeROS2(Node):
    def __init__(self):
        super().__init__('staubli_live_bridge')
        
        # 1. Publieurs ROS 2
        self.pub_joints = self.create_publisher(JointState, '/joint_states', 10)
        self.pub_pose = self.create_publisher(PoseStamped, '/staubli/tcp_pose', 10)
        
        # 2. Préparation du fichier CSV
        home_dir = os.path.expanduser('~')
        desktop = os.path.join(home_dir, 'Desktop')
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.csv_filename = os.path.join(desktop, f"robot_live_data_{timestamp}.csv")
        
        self.get_logger().info(f"📁 Enregistrement CSV prévu dans : {self.csv_filename}")
        
        # 3. Ouverture du socket TCP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(1)
        
        self.get_logger().info(f"📡 Attente du robot sur le port {PORT}...")
        self.conn, addr = self.server_socket.accept()
        self.get_logger().info(f"✅ Robot connecté : {addr}")

        # On lance la boucle de réception
        self.receive_loop()

    def euler_to_quaternion(self, roll, pitch, yaw):
        """Convertit Euler (radians) en Quaternion pour ROS 2"""
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        return [
            sr * cp * cy - cr * sp * sy, # x
            cr * sp * cy + sr * cp * sy, # y
            cr * cp * sy - sr * sp * sy, # z
            cr * cp * cy + sr * sp * sy  # w
        ]

    def receive_loop(self):
        buffer = ""
        # On ouvre le fichier CSV
        with open(self.csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=',') # Virgule pour être raccord avec tes derniers tests
            writer.writerow(["PC_Timestamp", "Index", "J1", "J2", "J3", "J4", "J5", "J6", "X", "Y", "Z", "RX", "RY", "RZ"])

            while rclpy.ok():
                try:
                    data = self.conn.recv(1024).decode('ascii')
                    if not data:
                        self.get_logger().warn("🔌 Connexion coupée par le robot.")
                        break
                    
                    buffer += data
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        
                        if line.startswith("{") and line.endswith("}"):
                            content = line[1:-1]
                            parts = content.split(';')
                            
                            if len(parts) == 13:
                                # --- 💾 SAUVEGARDE CSV ---
                                writer.writerow([time.time()] + parts)
                                file.flush()
                                
                                # --- 🤖 PUBLICATION JOINTS ---
                                js = JointState()
                                js.header.stamp = self.get_clock().now().to_msg()
                                js.name = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
                                joints_deg = [float(p) for p in parts[1:7]]
                                js.position = [math.radians(d) for d in joints_deg]
                                self.pub_joints.publish(js)
                                
                                # --- 🎯 PUBLICATION POSE (TCP) ---
                                pose = PoseStamped()
                                pose.header.stamp = self.get_clock().now().to_msg()
                                pose.header.frame_id = "world"
                                
                                # mm -> m
                                pose.pose.position.x = float(parts[7]) / 1000.0
                                pose.pose.position.y = float(parts[8]) / 1000.0
                                pose.pose.position.z = float(parts[9]) / 1000.0
                                
                                # Euler (deg) -> Rad -> Quaternion
                                rx = math.radians(float(parts[10]))
                                ry = math.radians(float(parts[11]))
                                rz = math.radians(float(parts[12]))
                                q = self.euler_to_quaternion(rx, ry, rz)
                                
                                pose.pose.orientation.x = q[0]
                                pose.pose.orientation.y = q[1]
                                pose.pose.orientation.z = q[2]
                                pose.pose.orientation.w = q[3]
                                
                                self.pub_pose.publish(pose)
                                
                except Exception as e:
                    self.get_logger().error(f"Erreur : {e}")
                    break

def main(args=None):
    rclpy.init(args=args)
    node = StaubliBridgeROS2()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.server_socket.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()