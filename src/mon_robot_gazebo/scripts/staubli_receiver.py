import socket
import csv
import os
import time
from datetime import datetime

# ==========================================
# CONFIGURATION (Doit matcher init.pgx) Fichier qui fonctionne sur le pc et sur le robot
# ==========================================
HOST = "198.168.99.1"  # Écoute sur toutes les cartes réseau du PC
PORT = 2005       # Port défini dans sioCtrl(sioSocket,"port",2005)

# Création du fichier CSV sur le Bureau
desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_filename = os.path.join(desktop, f"robot_data_{timestamp}.csv")

print(f"🖥️  PC en mode SERVEUR sur le port {PORT}...")
print(f"📁 Fichier de sauvegarde : {csv_filename}")
print("⏳ En attente de connexion du robot (Client)...")

# 1. Création du socket Serveur
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Option pour éviter l'erreur "Address already in use"
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    
    # Le PC s'arrête ici et attend que le robot appelle
    conn, addr = server_socket.accept()
    
    with conn:
        print(f"✅ Robot connecté ! Adresse du robot : {addr}")
        
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=';') 
            # En-tête basé sur la trame VAL3 {index;j1;j2;j3;j4;j5;j6}
            writer.writerow(["PC_Timestamp", "Index", "J1", "J2", "J3", "J4", "J5", "J6"]) 

            buffer = ""
            try:
                while True:
                    data = conn.recv(1024).decode('ascii')
                    if not data:
                        print("🔌 Le robot a coupé la connexion.")
                        break
                    
                    buffer += data
                    
                    # Le robot envoie nEol (code 10 / \n) à la fin de chaque trame
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        
                        # Nettoyage des accolades { } définies dans tPosition.pgx
                        if line.startswith("{") and line.endswith("}"):
                            content = line[1:-1] # Retire { et }
                            valeurs = content.split(';') # Séparateur défini dans VAL3
                            
                            if len(valeurs) == 7: # Index + 6 joints
                                writer.writerow([time.time()] + valeurs)
                                file.flush() # Sauvegarde immédiate
                                print(f"📥 Reçu [Frame {valeurs[0]}]: J1={valeurs[1]}, J2={valeurs[2]}...")

            except KeyboardInterrupt:
                print("\n🛑 Arrêt manuel (Ctrl+C).")

print(f"🏁 Terminé. Données enregistrées dans : {csv_filename}")