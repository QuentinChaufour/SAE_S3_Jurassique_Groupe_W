# SAE_S3_Jurassique_Groupe_W
## SAÉ ADN W :
* Bastien Moins Groupe 3A
* Nicolas Camera Groupe 3A
* Quentin Chaufour Groupe 3A

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