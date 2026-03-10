#!/usr/bin/env python3
# Traitement des données pyromètre et buse
# Ce script traite les données reçues des capteurs en tant que nœud ROS

import rospy
from std_msgs.msg import Float64
from collections import deque

class DataProcessor:
    def __init__(self):
        # Initialiser le nœud ROS
        rospy.init_node('data_processor', anonymous=True)
        
        # Buffers pour les données (pour le filtrage)
        self.max_points = 10
        self.temp_buffer = deque(maxlen=self.max_points)
        self.pressure_buffer = deque(maxlen=self.max_points)
        self.flow_buffer = deque(maxlen=self.max_points)
        
        # Subscribers
        self.temp_sub = rospy.Subscriber('/pyrometer/temperature', Float64, self.temperature_callback)
        self.pressure_sub = rospy.Subscriber('/buse/pressure', Float64, self.pressure_callback)
        self.flow_sub = rospy.Subscriber('/buse/flow_rate', Float64, self.flow_callback)
        
        # Publishers pour les données traitées
        self.filtered_temp_pub = rospy.Publisher('/processed/pyrometer/temperature', Float64, queue_size=10)
        self.filtered_pressure_pub = rospy.Publisher('/processed/buse/pressure', Float64, queue_size=10)
        self.filtered_flow_pub = rospy.Publisher('/processed/buse/flow_rate', Float64, queue_size=10)
        
        self.rate = rospy.Rate(10)  # 10 Hz
        
    def temperature_callback(self, msg):
        # Traiter les données du pyromètre
        raw_temp = msg.data
        self.temp_buffer.append(raw_temp)
        filtered_temp = sum(self.temp_buffer) / len(self.temp_buffer)
        
        # Publier la température filtrée
        self.filtered_temp_pub.publish(filtered_temp)
        
        # Log
        rospy.loginfo("Processed temperature: Raw=%.2f°C, Filtered=%.2f°C", raw_temp, filtered_temp)
    
    def pressure_callback(self, msg):
        # Traiter les données de pression
        raw_pressure = msg.data
        self.pressure_buffer.append(raw_pressure)
        filtered_pressure = sum(self.pressure_buffer) / len(self.pressure_buffer)
        
        # Publier la pression filtrée
        self.filtered_pressure_pub.publish(filtered_pressure)
        
        # Log
        rospy.loginfo("Processed pressure: Raw=%.2f bar, Filtered=%.2f bar", raw_pressure, filtered_pressure)
    
    def flow_callback(self, msg):
        # Traiter les données de débit
        raw_flow = msg.data
        self.flow_buffer.append(raw_flow)
        filtered_flow = sum(self.flow_buffer) / len(self.flow_buffer)
        
        # Publier le débit filtré
        self.filtered_flow_pub.publish(filtered_flow)
        
        # Log
        rospy.loginfo("Processed flow: Raw=%.2f L/min, Filtered=%.2f L/min", raw_flow, filtered_flow)
    
    def run(self):
        # Boucle principale
        while not rospy.is_shutdown():
            self.rate.sleep()

if __name__ == "__main__":
    try:
        processor = DataProcessor()
        processor.run()
    except rospy.ROSInterruptException:
        pass