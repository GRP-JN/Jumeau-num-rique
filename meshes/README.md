# Modèles 3D STL du Robot Staubli

## Structure des Fichiers

```
meshes/
├── base_link.stl          # Base du robot
├── link1.stl              # Articulation 1 (épaule)
├── link2.stl              # Articulation 2 (bras supérieur)
├── link3.stl              # Articulation 3 (avant-bras)
├── link4.stl              # Articulation 4 (poignet)
├── link5.stl              # Articulation 5 (poignet)
├── link6.stl              # Effecteur final (pince/flange)
├── pyrometer.stl          # Pyromètre
└── buse.stl               # Buse de soudage
```

## Instructions d'Intégration

### 1. Format des Fichiers STL
- Format ASCII ou BINAIRE
- Unités en mètres (cohérent avec URDF)
- Orientation Z-up (axe Z vers le haut)

### 2. Ajouter les STL à l'URDF

Exemple pour un lien :
```xml
<link name="link1">
  <visual>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <geometry>
      <mesh filename="package://mon_projet_jumeau/meshes/link1.stl" scale="1 1 1"/>
    </geometry>
    <material name="blue">
      <color rgba="0.0 0.0 1.0 1.0"/>
    </material>
  </visual>
  <collision>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <geometry>
      <mesh filename="package://mon_projet_jumeau/meshes/link1.stl"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="5.0"/>
    <inertia ixx="0.05" ixy="0" ixz="0" iyy="0.05" iyz="0" izz="0.05"/>
  </inertial>
</link>
```

### 3. Éviter les Bugs Courants

**Problème 1 : Chemin du fichier incorrect**
- ✅ Bon : `package://mon_projet_jumeau/meshes/link1.stl`
- ❌ Mauvais : `./meshes/link1.stl` ou `/home/user/meshes/link1.stl`

**Problème 2 : Fichiers manquants**
- S'assurer que tous les fichiers STL référencés existent
- Utiliser des géométries primitives comme fallback

**Problème 3 : Orientation incorrecte**
- Vérifier l'orientation avec `check_urdf` :
  ```bash
  check_urdf robot_model.urdf
  ```

**Problème 4 : Fichiers STL corrompus**
- Valider les STL avec Meshlab ou Blender
- S'assurer qu'il n'y a pas d'arêtes vives non fermées

### 4. Convertir les Fichiers STL

Si vous avez des fichiers dans d'autres formats :

**STEP → STL** :
```bash
# Avec Freecad (Python)
import Part
shape = Part.open("model.stp")
Part.export([shape], "model.stl")
```

**URDF avec STL** :
- Utiliser le script Python pour convertir automatiquement
- Ou utiliser Blender pour exporter en STL

### 5. Optimisation des Performances

Pour éviter les ralentissements :
- Réduire le nombre de triangles dans les STL (< 50k triangles par modèle)
- Utiliser des modèles simplifiés pour la collision
- Séparer visual et collision meshes

### 6. Commandes Utiles

```bash
# Valider l'URDF avec meshes
rosrun urdf_parser check_urdf robot_model.urdf

# Visualiser en RViz
roslaunch mon_projet_jumeau start_twin.launch

# Vérifier les fichiers manquants
grep -r "meshes/" urdf/robot_model.urdf
```

## Ressources

- [URDF Documentation - Meshes](http://wiki.ros.org/urdf/XML/link)
- [Meshlab](https://www.meshlab.net/) - Vérification et optimisation STL
- [Blender](https://www.blender.org/) - Conversion et édition de modèles
