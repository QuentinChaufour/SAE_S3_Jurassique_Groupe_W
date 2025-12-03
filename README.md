# SAE_S3_Jurassique_Groupe_W
## SAÉ ADN W :
* Bastien Moins Groupe 3A
* Nicolas Camera Groupe 3A
* Quentin Chaufour Groupe 3A

### Lancement de l'application Terminal

executez la commande `python -m exploitation_echantillons.app`

### Lancement de l'application Web

#### Installer les dépendances
Il faut avoir l'ensemble des dépendances nécessaires.
Nous pouvons utiliser un environment virtuel dans le dossier du projet avec notament la commande : `virtualenv venv -p python3`
Puis : `Source venv/bin/activate` sur linux, ou `Source venv/Script/activate` sur windows
Enfin installez les dépendances : `pip install -r requirements.txt`

#### Utilisation en local

Pour pouvoir utiliser l'application hors de l'IUT, un fichier docker est disponible.
Le logiciel Docker doit être installé sur la machine, et tourner en arrière plan.
Puis, dans le dossier du projet executez la commande : `docker compose up -d`
(Suppression des containes avec la commande : `docker compose down -v`)

Par la suite il faut modifier l'URL de la base de données, spécifié dans le fichier config.py
L'URL de cette nouvelle base de donnée sera : "mysql+pymysql://root:root_password@localhost:3306/labodino"

#### Lancer les tests et l'application

Pour lancer les tests, executez la commande: `coverage run -m pytest`
Pour lancer l'application web, executez la commande: `flask run`

## Le parc du Jurassique

Dans une équipe de trois personnes, nous avons pour but de créer une application web pour le laboratoire de paléontologie, l'application a pour but principal de préparer des campagnes de fouilles dans les différentes plateformes dont ils disposent et d'en traiter les résultats. \
L'application disposera de différents rôles utilisateurs et ces derniers disposeront de droits:
- Les personnels administratifs et techniques
- Les chercheuses et chercheurs
- La direction du laboratoire

### Architecture de la base de données

Objectif
- Définir l'architecture BD (MCD, script de création, scripts d'insertion/tests).
- Fournir la base pour les développements ultérieurs (API, UI, traitements).

Contenu
- script.sql: création des tables et contraintes.
- triggers.sql : création des fonctions et triggers
- populations.sql: jeux de données de test fonctionnelle
- testing_inserts.sql : jeux de données de test des contraintes
- delete.sql: suppression des objets pour réinitialiser l'environnement.
- MCD.svg: diagramme conceptuel (MCD).
- README.md: documentation d'utilisation.

Modèle de données (résumé)
- Entités principales : PERSONNEL, PLATEFORME, EQUIPEMENT, CAMPAGNE, BUDGET, ESPECE, ECHANTILLON, HABILITATION.
- Associations importantes : POSSEDER_HABILITATION, INCLURE_EQUIPEMENT, NECESSITER_HABILITATION, PARTICIPER_CAMPAGNE, MAINTENANCE.
- Clés : vérifiez les PrimaryKey/ForeignKey dans script.sql.

Décisions de conception
- Utilisation d'auto-increment pour certaines PrimaryKey (idCampagne, idEquipement, idHabilitation).
- Tables d'association pour gérer les relations entre les tables (habilitations, participation, inclusion d'équipements).
- Contraintes métiers implémentées via triggers/fonctions (vérification budget, disponibilité plateforme, habilitations requises).

Contraintes et triggers
- Triggers métier : checkBudget, checkCampagneValidity, checkUnEquipementSurPlateforme, etc.
- Ajout de fonction pour l'implémentation de trigger tel que: 
  - remainingBudget, plateformeAvailable pour le trigger checkCampagneValidity
  - plateformeInMaintenace pour le trigger checkCampagne
  - etc

Tests et validation
- Vérifier la présence des tables : SHOW TABLES;
- Contrôler quelques tuples : SELECT * FROM PLATEFORME;
- Tester les triggers métiers avec INSERT/UPDATE/DELETE et vérifier les messages d'erreur renvoyés (testing_inserts.sql).
