#!/usr/bin/env python3
"""
Script de conversion automatique des géométries primitives en meshes STL
pour l'URDF du robot Staubli.

Utilisation :
  python3 generate_meshes.py --output meshes/

Les modèles STL générés peuvent être remplacés par des modèles réels.
"""

import argparse
import os
from pathlib import Path

def create_stl_placeholder(filename, description):
    """
    Crée un fichier STL placeholder simple (cube ou cylindre)
    
    Note: C'est un placeholder. Remplacer par des vrais modèles STL.
    """
    content = f"""solid {description}
  facet normal 0 0 1
    outer loop
      vertex 0 0 0
      vertex 1 0 0
      vertex 1 1 0
    endloop
  endfacet
  facet normal 0 0 1
    outer loop
      vertex 0 0 0
      vertex 1 1 0
      vertex 0 1 0
    endloop
  endfacet
endsolid {description}
"""
    with open(filename, 'w') as f:
        f.write(content)
    print(f"✓ Créé : {filename}")

def main():
    parser = argparse.ArgumentParser(description='Générer les fichiers STL du robot')
    parser.add_argument('--output', '-o', default='meshes', help='Répertoire de sortie')
    args = parser.parse_args()
    
    # Créer le répertoire s'il n'existe pas
    Path(args.output).mkdir(exist_ok=True)
    
    # Modèles à créer
    models = [
        ('base_link.stl', 'Base du robot'),
        ('link1.stl', 'Articulation 1 - Épaule'),
        ('link2.stl', 'Articulation 2 - Bras supérieur'),
        ('link3.stl', 'Articulation 3 - Avant-bras'),
        ('link4.stl', 'Articulation 4 - Poignet'),
        ('link5.stl', 'Articulation 5 - Poignet'),
        ('link6.stl', 'Articulation 6 - Effecteur final'),
        ('pyrometer.stl', 'Pyromètre'),
        ('buse.stl', 'Buse de soudage'),
    ]
    
    print("Génération des fichiers STL placeholder...")
    print("-" * 50)
    
    for model, desc in models:
        filepath = os.path.join(args.output, model)
        create_stl_placeholder(filepath, desc)
    
    print("-" * 50)
    print(f"✓ {len(models)} fichiers STL créés dans '{args.output}/'")
    print("\n⚠️  IMPORTANT :")
    print("   Ces fichiers sont des placeholders simples.")
    print("   Remplacez-les par vos vrais modèles 3D !")
    print("\n   Comment remplacer :")
    print("   1. Exporter vos modèles CAO en format STL (ASCII)")
    print("   2. Copier les fichiers STL dans le dossier meshes/")
    print("   3. Décommenter les sections <mesh> dans robot_model_with_meshes.urdf")
    print("   4. Valider avec : rosrun urdf_parser check_urdf robot_model_with_meshes.urdf")

if __name__ == '__main__':
    main()
