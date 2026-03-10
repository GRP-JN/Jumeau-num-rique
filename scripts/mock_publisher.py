# Générateur de fausses données pour les tests
# Ce script simule les données des capteurs

import time
import random
import json

class MockPublisher:
    def __init__(self):
        self.running = True
        
    def generate_pyrometer_data(self):
        return {
            'temperature': random.uniform(1400, 1600),
            'timestamp': time.time()
        }
    
    def generate_buse_data(self):
        return {
            'pressure': random.uniform(2, 5),
            'flow_rate': random.uniform(10, 20),
            'timestamp': time.time()
        }
    
    def publish_data(self):
        while self.running:
            pyrometer_data = self.generate_pyrometer_data()
            buse_data = self.generate_buse_data()
            
            print("Pyrometer data:", json.dumps(pyrometer_data, indent=2))
            print("Buse data:", json.dumps(buse_data, indent=2))
            
            time.sleep(1)  # Publier toutes les secondes
    
    def stop(self):
        self.running = False

if __name__ == "__main__":
    publisher = MockPublisher()
    try:
        publisher.publish_data()
    except KeyboardInterrupt:
        publisher.stop()
        print("Mock publisher stopped.")