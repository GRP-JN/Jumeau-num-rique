#!/usr/bin/env python3
# Générateur de fausses données pour les tests
# Ce script simule les données des capteurs en tant que nœud ROS

import rospy
from std_msgs.msg import Float64
import time
import random

class MockPublisher:
    def __init__(self):
        # Initialiser le nœud ROS
        rospy.init_node('mock_publisher', anonymous=True)
        
        # Publishers pour les données des capteurs (capteurs désactivés pour l'instant)
        # self.pyrometer_pub = rospy.Publisher('/pyrometer/temperature', Float64, queue_size=10)
        # self.buse_pressure_pub = rospy.Publisher('/buse/pressure', Float64, queue_size=10)
        # self.buse_flow_pub = rospy.Publisher('/buse/flow_rate', Float64, queue_size=10)
        
        self.rate = rospy.Rate(1)  # 1 Hz
        self.running = True
        
    def generate_pyrometer_data(self):
        return random.uniform(1400, 1600)
    
    def generate_buse_pressure(self):
        return random.uniform(2, 5)
    
    def generate_buse_flow(self):
        return random.uniform(10, 20)
    
    def publish_data(self):
        while not rospy.is_shutdown() and self.running:
            # Générer et publier les données
            temp = self.generate_pyrometer_data()
            pressure = self.generate_buse_pressure()
            flow = self.generate_buse_flow()
            
            # Publier sur les topics ROS
            self.pyrometer_pub.publish(temp)
            self.buse_pressure_pub.publish(pressure)
            self.buse_flow_pub.publish(flow)
            
            # Log des données
            rospy.loginfo("Published: Temp=%.2f°C, Pressure=%.2f bar, Flow=%.2f L/min", temp, pressure, flow)
            
            self.rate.sleep()
    
    def stop(self):
        self.running = False

if __name__ == "__main__":
    try:
        publisher = MockPublisher()
        publisher.publish_data()
    except rospy.ROSInterruptException:
        publisher.stop()
        print("Mock publisher stopped.")