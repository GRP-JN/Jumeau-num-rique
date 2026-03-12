import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox, QGridLayout, QComboBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtGui import QImage, QPixmap, QFont
import pyqtgraph as pg
import qdarktheme
from ros_connector import RosConnector

class StaubliDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jumeau Numérique Staubli RX160 - Dashboard")
        self.resize(1200, 800)
        
        # 1. Initialize data attributes FIRST
        self.time_steps = 0
        self.speed_data = [0]*100
        self.temp_data = [0]*100
        self.current_max_temp = 20.0
        self.current_speed = 0.0
        self.cap = None
        self.ros_connected = False
        
        # 2. Init ROS Connector
        self.ros_conn = RosConnector()
        
        # 3. Setup UI (which uses the attributes above)
        self.init_ui()
        
        # 4. Connect to ROS backend
        self.ros_connected = self.ros_conn.connect()
        if self.ros_connected:
            self.lbl_status.setText("Connecté: ROSbridge OK")
            self.lbl_status.setStyleSheet("color: #00ff00;")
            self.ros_conn.subscribe('/joint_states', 'sensor_msgs/JointState', self.on_joint_states)
        else:
            self.lbl_status.setText("Déconnecté: Lancer rosbridge!")
            self.lbl_status.setStyleSheet("color: #ff0000;")
        
        # 5. Start timers LAST
        self.cam_timer = QTimer()
        self.cam_timer.timeout.connect(self.update_camera_frame)
        self.cam_timer.start(33) # ~30 fps
        
        self.graph_timer = QTimer()
        self.graph_timer.timeout.connect(self.update_graphs)
        self.graph_timer.start(50)

        
    def init_ui(self):
        # Main widget & layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Left Panel (Controls & Stats) -------------------------
        left_panel = QVBoxLayout()
        
        # Robot Status Group
        status_group = QGroupBox("Statut Robot (ROS 2)")
        status_layout = QVBoxLayout()
        self.lbl_status = QLabel("Connecté: En attente...")
        self.lbl_status.setFont(QFont("Arial", 12, QFont.Bold))
        self.lbl_status.setStyleSheet("color: #ffcc00;")
        
        self.lbl_speed = QLabel("Vitesse: 0.0 rad/s")
        self.lbl_speed.setFont(QFont("Arial", 14))
        
        status_layout.addWidget(self.lbl_status)
        status_layout.addWidget(self.lbl_speed)
        status_group.setLayout(status_layout)
        
        # Speed Graph Group
        graph_group = QGroupBox("Vitesse (En temps réel)")
        graph_layout = QVBoxLayout()
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('default')
        self.speed_curve = self.graph_widget.plot(pen=pg.mkPen(color='#00ff00', width=2))
        graph_layout.addWidget(self.graph_widget)
        graph_group.setLayout(graph_layout)
        
        left_panel.addWidget(status_group)
        left_panel.addWidget(graph_group, stretch=1)
        
        # Central Panel (3D View WebEngine) -----------------------
        center_panel = QVBoxLayout()
        view3d_group = QGroupBox("Jumeau Numérique 3D (ROS3D)")
        view3d_layout = QVBoxLayout()
        
        self.web_view = QWebEngineView()
        # Ensure the view has a page and profile properly initialized
        local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "ros3d_viewer.html"))
        if not os.path.exists(local_path):
             print(f"ERREUR : Fichier introuvable : {local_path}")
        self.web_view.load(QUrl.fromLocalFile(local_path))
        view3d_layout.addWidget(self.web_view)
        
        view3d_group.setLayout(view3d_layout)
        center_panel.addWidget(view3d_group)
        
        # Right Panel (Thermal Camera) ----------------------------
        right_panel = QVBoxLayout()
        cam_group = QGroupBox("Caméra Thermique (PIX Connect XI400)")
        cam_layout = QVBoxLayout()
        
        self.lbl_camera = QLabel()
        self.lbl_camera.setMinimumSize(400, 300)
        self.lbl_camera.setAlignment(Qt.AlignCenter)
        self.lbl_camera.setStyleSheet("background-color: black;")
        
        cam_layout.addWidget(self.lbl_camera)
        
        cam_controls = QHBoxLayout()
        self.combo_cam = QComboBox()
        
        self.btn_connect_cam = QPushButton("Connecter")
        self.btn_connect_cam.clicked.connect(self.connect_camera)
        
        self.btn_scan_cam = QPushButton("Scanner")
        self.btn_scan_cam.clicked.connect(self.scan_cameras)
        
        self.scan_cameras() # Scan on start

        cam_controls.addWidget(QLabel("Index:"))
        cam_controls.addWidget(self.combo_cam)
        cam_controls.addWidget(self.btn_connect_cam)
        cam_controls.addWidget(self.btn_scan_cam)
        
        cam_layout.addLayout(cam_controls)
        cam_group.setLayout(cam_layout)
        
        # Temp Graph Group
        temp_group = QGroupBox("Température (Max détectée)")
        temp_layout = QVBoxLayout()
        self.temp_widget = pg.PlotWidget()
        self.temp_widget.setBackground('default')
        self.temp_curve = self.temp_widget.plot(pen=pg.mkPen(color='#ff5500', width=2))
        
        self.lbl_temp = QLabel("Température Max: 0.0 °C")
        self.lbl_temp.setFont(QFont("Arial", 12))
        self.lbl_temp.setStyleSheet("color: #ff5500;")
        
        temp_layout.addWidget(self.lbl_temp)
        temp_layout.addWidget(self.temp_widget)
        temp_group.setLayout(temp_layout)
        
        right_panel.addWidget(cam_group)
        right_panel.addWidget(temp_group, stretch=1)
        
        # Add to main layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(center_panel, 2) # Center panel takes more space
        main_layout.addLayout(right_panel, 1)

    def update_camera_frame(self):
        # Demo function to generate noise if no camera is connected
        if getattr(self, 'cap', None) is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None:
                # Calculate a mock max temperature from brightness, replace with actual SDK data if available
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                max_val = np.max(gray)
                self.current_max_temp = 20.0 + (max_val / 255.0) * 80.0  # Scale 0-255 to 20-100°C for demo
                
                frame = cv2.applyColorMap(frame, cv2.COLORMAP_INFERNO)
                self.display_image(frame)
            else:
                noise = np.zeros((300, 400, 3), dtype=np.uint8)
                cv2.putText(noise, "Erreur lecture flux (cadre vide)", (50, 150), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                self.display_image(noise)
        else:
            # Generate static noise as placeholder for thermal
            noise = np.random.randint(0, 255, (300, 400), dtype=np.uint8)
            self.current_max_temp = 20.0 + (np.max(noise) / 255.0) * 80.0
            
            colored_noise = cv2.applyColorMap(noise, cv2.COLORMAP_INFERNO)
            cv2.putText(colored_noise, "En attente flux PIX Connect...", (50, 150), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(colored_noise, "Vérifiez DirectShow dans PIX Connect", (50, 180), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            self.display_image(colored_noise)

    def display_image(self, img_np):
        qformat = QImage.Format_Indexed8
        if len(img_np.shape) == 3:
            if img_np.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
                
        img = QImage(img_np, img_np.shape[1], img_np.shape[0], img_np.strides[0], qformat)
        img = img.rgbSwapped() # BGR to RGB
        self.lbl_camera.setPixmap(QPixmap.fromImage(img).scaled(
            self.lbl_camera.width(), self.lbl_camera.height(), Qt.KeepAspectRatio))

    def update_graphs(self):
        self.time_steps += 0.05
        
        # If not connected, add zeroes
        if not self.ros_conn.is_connected:
            new_val = 0.0
        else:
            new_val = self.current_speed
            
        self.speed_data.append(new_val)
        self.speed_data.pop(0)
        self.speed_curve.setData(self.speed_data)
        self.lbl_speed.setText(f"Vitesse moy: {new_val:.2f} rad/s")
        
        # Temp Graph
        if hasattr(self, 'current_max_temp'):
            temp_val = self.current_max_temp
        else:
            temp_val = 20.0
            
        self.temp_data.append(temp_val)
        self.temp_data.pop(0)
        self.temp_curve.setData(self.temp_data)
        self.lbl_temp.setText(f"Temp. Max: {temp_val:.1f} °C")
    
    def on_joint_states(self, message):
        # Calculate an average or norm speed from joint states
        if 'velocity' in message and len(message['velocity']) > 0:
            velocities = message['velocity']
            avg_speed = sum(abs(v) for v in velocities) / len(velocities)
            self.current_speed = avg_speed

    def scan_cameras(self):
        """Scans for available cameras and updates the combo box."""
        self.combo_cam.clear()
        available = []
        for i in range(1, 10):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    # On affiche explicitement que l'index 0 est ignoré si nécessaire, 
                    # mais ici on ne cherche que de 1 à 9.
                    name = f"Index {i} (Détectée)"
                    available.append(name)
                cap.release()
        
        if not available:
            self.combo_cam.addItem("Aucune caméra trouvée")
            self.btn_connect_cam.setEnabled(False)
        else:
            self.combo_cam.addItems(available)
            self.btn_connect_cam.setEnabled(True)
            self.combo_cam.setCurrentIndex(0)

    def connect_camera(self):
        text = self.combo_cam.currentText()
        if "Index" not in text:
            return
            
        cam_index = int(text.split(" ")[1])
        print(f"Tentative de connexion à la caméra Thermique (Index {cam_index})...")
        
        if getattr(self, 'cap', None) is not None and self.cap.isOpened():
            self.cap.release()
            
        # Using CAP_DSHOW is required on Windows for some virtual cams like OBS or PixConnect.
        self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        
        if self.cap.isOpened():
            print(f"Caméra {cam_index} connectée avec succès.")
            self.btn_connect_cam.setText("Déconnecter")
            self.btn_connect_cam.setStyleSheet("background-color: #00aa00;")
            
            # Disconnect previous if any, assign new behavior
            try:
                self.btn_connect_cam.clicked.disconnect()
            except: pass
            self.btn_connect_cam.clicked.connect(self.disconnect_camera)
        else:
            print(f"Échec de la connexion à la caméra {cam_index}. Vérifiez que Pix Connect est ouvert.")

    def disconnect_camera(self):
        if getattr(self, 'cap', None) is not None and self.cap.isOpened():
            self.cap.release()
        self.btn_connect_cam.setText("Connecter Caméra")
        self.btn_connect_cam.setStyleSheet("")
        try:
            self.btn_connect_cam.clicked.disconnect()
        except: pass
        self.btn_connect_cam.clicked.connect(self.connect_camera)

    def closeEvent(self, event):
        self.ros_conn.disconnect()
        if getattr(self, 'cap', None) is not None and self.cap.isOpened():
            self.cap.release()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Apply a nice modern dark theme
    qdarktheme.setup_theme()
    
    # Custom tweaks for graph background
    pg.setConfigOption('background', '#121212')
    pg.setConfigOption('foreground', '#d3d3d3')
    
    win = StaubliDashboard()
    win.show()
    sys.exit(app.exec_())
