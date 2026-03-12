import time
try:
    import roslibpy
except ImportError:
    roslibpy = None

class RosConnector:
    def __init__(self, host='localhost', port=9090):
        self.host = host
        self.port = port
        self.ros = None
        self.is_connected = False
        self.subscriptions = []
        
    def connect(self):
        if not roslibpy:
            print("Erreur: roslibpy n'est pas installé. (pip install roslibpy)")
            return False
            
        try:
            self.ros = roslibpy.Ros(host=self.host, port=self.port)
            self.ros.run()
            self.is_connected = self.ros.is_connected
            print(f"Connexion ROSbridge (wss://{self.host}:{self.port}) : {self.is_connected}")
            return self.is_connected
        except Exception as e:
            print(f"Erreur de connexion ROSbridge: {e}")
            return False

    def subscribe(self, topic_name, topic_type, callback):
        if not self.ros or not self.is_connected:
            print(f"Cannot subscribe to {topic_name}: ROS not connected.")
            return None
        topic = roslibpy.Topic(self.ros, topic_name, topic_type)
        topic.subscribe(callback)
        self.subscriptions.append(topic)
        print(f"Subscribed to topic: {topic_name}")
        return topic

    def disconnect(self):
        for topic in self.subscriptions:
            try:
                topic.unsubscribe()
            except:
                pass
        self.subscriptions.clear()
        
        if self.ros and self.is_connected:
            self.ros.terminate()
            self.is_connected = False
            print("Déconnecté de ROSbridge.")
