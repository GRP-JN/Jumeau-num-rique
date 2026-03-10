# Traitement des données pyromètre et buse
# Ce script traite les données reçues des capteurs

class DataProcessor:
    def __init__(self):
        self.data_buffer = []
        
    def process_pyrometer_data(self, data):
        # Traiter les données du pyromètre
        processed_data = {
            'temperature': data.get('temperature', 0),
            'timestamp': data.get('timestamp'),
            'filtered_value': self.apply_filter(data.get('temperature', 0))
        }
        return processed_data
    
    def process_buse_data(self, data):
        # Traiter les données de la buse
        processed_data = {
            'pressure': data.get('pressure', 0),
            'flow_rate': data.get('flow_rate', 0),
            'timestamp': data.get('timestamp')
        }
        return processed_data
    
    def apply_filter(self, value):
        # Appliquer un filtre simple (moyenne mobile)
        self.data_buffer.append(value)
        if len(self.data_buffer) > 10:
            self.data_buffer.pop(0)
        return sum(self.data_buffer) / len(self.data_buffer)

if __name__ == "__main__":
    processor = DataProcessor()
    # Test avec des données d'exemple
    test_data = {'temperature': 1500, 'timestamp': '2023-01-01T00:00:00'}
    result = processor.process_pyrometer_data(test_data)
    print(result)