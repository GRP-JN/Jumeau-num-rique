# Interface de visualisation du jumeau numérique
# Ce script gère l'affichage des données en temps réel avec 4 fenêtres matplotlib

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from collections import deque
import time
import threading
from mock_publisher import MockPublisher
from data_processor import DataProcessor

class DashboardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jumeau Numérique - Dashboard")
        
        # Initialiser le processeur de données
        self.data_processor = DataProcessor()
        
        # Buffers pour les données (pour les graphiques)
        self.max_points = 50
        self.temp_data = deque(maxlen=self.max_points)
        self.pressure_data = deque(maxlen=self.max_points)
        self.flow_data = deque(maxlen=self.max_points)
        self.time_data = deque(maxlen=self.max_points)
        
        # Créer les 4 fenêtres matplotlib
        self.create_windows()
        
        # Démarrer le publisher mock dans un thread séparé
        self.publisher = MockPublisher()
        self.publisher_thread = threading.Thread(target=self.publisher.publish_data)
        self.publisher_thread.daemon = True
        self.publisher_thread.start()
        
        # Animer les graphiques
        self.animate_plots()
    
    def create_windows(self):
        # Fenêtre principale avec 4 frames pour les graphiques
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
        # Fonction d'animation pour mettre à jour les graphiques
        def animate(i):
            # Générer de nouvelles données
            pyrometer_data = self.publisher.generate_pyrometer_data()
            buse_data = self.publisher.generate_buse_data()
            
            # Traiter les données
            processed_pyro = self.data_processor.process_pyrometer_data(pyrometer_data)
            processed_buse = self.data_processor.process_buse_data(buse_data)
            
            # Ajouter aux buffers
            current_time = time.time()
            self.time_data.append(current_time)
            self.temp_data.append(processed_pyro['filtered_value'])
            self.pressure_data.append(processed_buse['pressure'])
            self.flow_data.append(processed_buse['flow_rate'])
            
            # Mettre à jour les graphiques
            self.ax1.clear()
            self.ax1.plot(list(self.time_data), list(self.temp_data))
            self.ax1.set_title('Température Pyromètre')
            self.ax1.set_xlabel('Temps')
            self.ax1.set_ylabel('Température (°C)')
            
            self.ax2.clear()
            self.ax2.plot(list(self.time_data), list(self.pressure_data))
            self.ax2.set_title('Pression Buse')
            self.ax2.set_xlabel('Temps')
            self.ax2.set_ylabel('Pression (bar)')
            
            self.ax3.clear()
            self.ax3.plot(list(self.time_data), list(self.flow_data))
            self.ax3.set_title('Débit Buse')
            self.ax3.set_xlabel('Temps')
            self.ax3.set_ylabel('Débit (L/min)')
            
            self.ax4.clear()
            self.ax4.scatter(list(self.temp_data), list(self.pressure_data))
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
    
    def update_data(self, data):
        # Méthode pour mettre à jour manuellement avec des données externes
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardGUI(root)
    root.mainloop()