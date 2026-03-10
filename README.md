# Jumeau Numérique - Robot Staubli 6 Axes

Ce projet implémente un jumeau numérique pour la surveillance et la visualisation des données de processus industriels sur un robot Staubli 6 axes. Le système monitore les températures mesurées par pyromètre et les paramètres de buse attachés à l'effecteur final du robot.

## Architecture du Projet

```
mon_projet_jumeau/
├── scripts/
│   ├── dashboard_gui.py     # Interface de visualisation avec 4 graphiques matplotlib
│   ├── data_processor.py    # Traitement des données pyromètre/buse avec filtrage
│   └── mock_publisher.py    # Générateur de fausses données pour tests
├── launch/
│   └── start_twin.launch    # Fichier de lancement ROS avec RViz
├── urdf/
│   └── robot_model.urdf     # Modèle URDF complet du robot Staubli TX60 6 axes
└── README.md
```

## Modèle Robot

Le modèle URDF décrit un robot 6 axes Staubli TX60 avec :
- 6 articulations rotatives (joints 1-6)
- Effecteur final avec pyromètre et buse de soudage
- Propriétés visuelles, de collision et inertie complètes
- Compatible avec ROS/Gazebo pour simulation

## Installation et Utilisation

1. Assurez-vous d'avoir ROS installé (Noetic recommandé)
2. Clonez ce repository
3. Lancez les nœuds avec : `roslaunch mon_projet_jumeau start_twin.launch`
4. Le dashboard s'ouvrira automatiquement avec 4 fenêtres de monitoring

## Fonctionnalités

- **Modélisation Robot**: URDF complet pour simulation réaliste
- **Traitement des données** : Filtrage et analyse des données capteurs en temps réel
- **Visualisation** : Interface graphique avec 4 graphiques matplotlib :
  - Température pyromètre
  - Pression buse
  - Débit buse
  - Corrélation température-pression
- **Simulation** : Génération de données mock pour les tests sans matériel
- **ROS Integration** : Prêt pour intégration avec MoveIt! et Gazebo

Test, on essaye de push pr voir si ça marche