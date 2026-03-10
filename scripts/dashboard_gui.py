# Interface de visualisation du jumeau numérique
# Ce script gère l'affichage des données en temps réel avec 4 graphiques matplotlib en tant que nœud ROS

import rospy
from std_msgs.msg import Float64
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from collections import deque
import threading

class DashboardGUI:
    def __init__(self):
        # Initialiser le nœud ROS
        rospy.init_node('dashboard_gui', anonymous=True)
        
        # Buffers pour les données (pour les graphiques)
        self.max_points = 50
        self.temp_data = deque(maxlen=self.max_points)
        self.pressure_data = deque(maxlen=self.max_points)
        self.flow_data = deque(maxlen=self.max_points)
        self.time_data = deque(maxlen=self.max_points)
        
        # Subscribers pour les données traitées (capteurs désactivés pour l'instant)
        # self.temp_sub = rospy.Subscriber('/processed/pyrometer/temperature', Float64, self.temperature_callback)
        # self.pressure_sub = rospy.Subscriber('/processed/buse/pressure', Float64, self.pressure_callback)
        # self.flow_sub = rospy.Subscriber('/processed/buse/flow_rate', Float64, self.flow_callback)
        
        # Verrou pour la synchronisation des threads
        self.data_lock = threading.Lock()
        
        # Démarrer l'interface graphique dans un thread séparé
        self.gui_thread = threading.Thread(target=self.start_gui)
        self.gui_thread.daemon = True
        self.gui_thread.start()
    
    def temperature_callback(self, msg):
        with self.data_lock:
            self.temp_data.append(msg.data)
            if len(self.time_data) == 0 or len(self.temp_data) > len(self.time_data):
                self.time_data.append(rospy.get_time())
    
    def pressure_callback(self, msg):
        with self.data_lock:
            self.pressure_data.append(msg.data)
    
    def flow_callback(self, msg):
        with self.data_lock:
            self.flow_data.append(msg.data)
    
    def start_gui(self):
        # Créer l'interface Tkinter
        self.root = tk.Tk()
        self.root.title("Jumeau Numérique - Dashboard ROS")
        
        # Créer les 4 figures matplotlib
        self.create_windows()
        
        # Animer les graphiques
        self.animate_plots()
        
        # Démarrer la boucle Tkinter
        self.root.mainloop()
    
    def create_windows(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Créer 4 figures matplotlib
        self.fig1 = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax1 = self.fig1.add_subplot(111)
        self.ax1.set_title('Température Pyromètre')
        self.ax1.set_xlabel('Temps')
        self.ax1.set_ylabel('Température (°C)')
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=main_frame)
        self.canvas1.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)
        
        self.fig2 = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax2 = self.fig2.add_subplot(111)
        self.ax2.set_title('Pression Buse')
        self.ax2.set_xlabel('Temps')
        self.ax2.set_ylabel('Pression (bar)')
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=main_frame)
        self.canvas2.get_tk_widget().grid(row=0, column=1, padx=10, pady=10)
        
        self.fig3 = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax3 = self.fig3.add_subplot(111)
        self.ax3.set_title('Débit Buse')
        self.ax3.set_xlabel('Temps')
        self.ax3.set_ylabel('Débit (L/min)')
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=main_frame)
        self.canvas3.get_tk_widget().grid(row=1, column=0, padx=10, pady=10)
        
        self.fig4 = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax4 = self.fig4.add_subplot(111)
        self.ax4.set_title('Vue d\'ensemble')
        self.ax4.set_xlabel('Température')
        self.ax4.set_ylabel('Pression')
        self.canvas4 = FigureCanvasTkAgg(self.fig4, master=main_frame)
        self.canvas4.get_tk_widget().grid(row=1, column=1, padx=10, pady=10)
    
    def animate_plots(self):
        def animate(i):
            with self.data_lock:
                time_list = list(self.time_data)[-self.max_points:]
                temp_list = list(self.temp_data)[-self.max_points:]
                pressure_list = list(self.pressure_data)[-self.max_points:]
                flow_list = list(self.flow_data)[-self.max_points:]
            
            # Mettre à jour les graphiques
            self.ax1.clear()
            if time_list and temp_list:
                self.ax1.plot(time_list, temp_list)
            self.ax1.set_title('Température Pyromètre')
            self.ax1.set_xlabel('Temps')
            self.ax1.set_ylabel('Température (°C)')
            
            self.ax2.clear()
            if time_list and pressure_list:
                self.ax2.plot(time_list, pressure_list)
            self.ax2.set_title('Pression Buse')
            self.ax2.set_xlabel('Temps')
            self.ax2.set_ylabel('Pression (bar)')
            
            self.ax3.clear()
            if time_list and flow_list:
                self.ax3.plot(time_list, flow_list)
            self.ax3.set_title('Débit Buse')
            self.ax3.set_xlabel('Temps')
            self.ax3.set_ylabel('Débit (L/min)')
            
            self.ax4.clear()
            if temp_list and pressure_list:
                self.ax4.scatter(temp_list, pressure_list)
            self.ax4.set_title('Corrélation Température-Pression')
            self.ax4.set_xlabel('Température (°C)')
            self.ax4.set_ylabel('Pression (bar)')
            
            # Redessiner les canvas
            self.canvas1.draw()
            self.canvas2.draw()
            self.canvas3.draw()
            self.canvas4.draw()
        
        # Créer l'animation
        self.ani = animation.FuncAnimation(self.fig1, animate, interval=1000)
    
    def run(self):
        # Boucle principale ROS
        while not rospy.is_shutdown():
            rospy.sleep(1)

if __name__ == "__main__":
    try:
        dashboard = DashboardGUI()
        dashboard.run()
    except rospy.ROSInterruptException:
        pass