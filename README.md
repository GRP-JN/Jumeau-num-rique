# Jumeau Numérique

Ce projet implémente un jumeau numérique pour la surveillance et la visualisation des données de processus industriels, notamment les températures mesurées par pyromètre et les paramètres de buse.

## Architecture du Projet

```
mon_projet_jumeau/
├── scripts/
│   ├── dashboard_gui.py     # Interface de visualisation
│   ├── data_processor.py    # Traitement des données pyromètre/buse
│   └── mock_publisher.py    # Générateur de fausses données pour tests
├── launch/
│   └── start_twin.launch    # Fichier de lancement ROS
├── urdf/
│   └── robot_model.urdf     # Modèle géométrique du robot
└── README.md
```

## Installation et Utilisation

1. Assurez-vous d'avoir ROS installé
2. Clonez ce repository
3. Lancez les nœuds avec : `roslaunch mon_projet_jumeau start_twin.launch`

## Fonctionnalités

- **Traitement des données** : Filtrage et analyse des données capteurs
- **Visualisation** : Interface graphique pour monitoring en temps réel
- **Simulation** : Génération de données mock pour les tests
- **Modélisation** : Description URDF du robot et équipements

Test, on essaye de push pr voir si ça marche