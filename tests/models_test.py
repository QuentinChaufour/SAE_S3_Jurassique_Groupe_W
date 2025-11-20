from LaboDino.models import ROLE, PLATEFORME, PERSONNEL, CAMPAGNE, ECHANTILLON, ESPECE, HABILITATION, POSSEDER, PARTICIPER_CAMPAGNE
from LaboDino.app import db, app
from sqlalchemy import text
from datetime import date

def clear_database():
    """Nettoie la base de données en supprimant et recréant toutes les tables."""
    # Désactiver la vérification des clés étrangères
    db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    db.session.commit()
    
    # Supprimer toutes les tables
    db.drop_all()
    
    # Recréer toutes les tables
    db.create_all()
    
    # Réactiver la vérification des clés étrangères
    db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    db.session.commit()

def test_personnel():
    """Teste la création d'entités PERSONNEL."""
    personnel1 = PERSONNEL("Dupont", "Jean", "mdp123", ROLE.administratif)
    personnel2 = PERSONNEL("Martin", "Sophie", "mdp456", ROLE.chercheur)
    personnel3 = PERSONNEL("Bernard", "Luc", "mdp789", ROLE.technicien)
    personnel4 = PERSONNEL("Dubois", "Mairie", "mdp101", ROLE.direction)
    db.session.add_all([personnel1, personnel2, personnel3, personnel4])
    db.session.commit()
    
    assert PERSONNEL.query.count() == 4
    assert PERSONNEL.query.filter_by(nom="Dupont").first().prenom == "Jean"
    assert PERSONNEL.query.filter_by(nom="Martin").first().role == ROLE.chercheur
    assert PERSONNEL.query.filter_by(role=ROLE.direction).count() == 1

def test_habilitations():
    """Teste la création d'entités HABILITATION."""
    hab1 = HABILITATION("Manipulation ADN")
    hab2 = HABILITATION("Séquençage")
    hab3 = HABILITATION(nom_habilitation="Analyse génomique")
    db.session.add_all([hab1, hab2, hab3])
    db.session.commit()
    
    assert HABILITATION.query.count() == 3
    assert HABILITATION.query.filter_by(nom_habilitation="Séquençage").first() is not None
    assert hab1.id_habilitation is not None

def test_plateformes():
    """Teste la création d'entités PLATEFORME."""
    plat1 = PLATEFORME("Plateforme A", 5, 1500, 90)
    plat2 = PLATEFORME("Plateforme B", 3, 800, 60)
    db.session.add_all([plat1, plat2])
    db.session.commit()

    assert PLATEFORME.query.count() == 2
    assert PLATEFORME.query.filter_by(nom_plateforme="Plateforme A").first().nb_personnes_requises == 5

def test_campagnes_et_utiliser():
    """Teste la création de CAMPAGNE et l'association UTILISER avec PLATEFORME."""
    plateforme = PLATEFORME.query.filter_by(nom_plateforme="Plateforme A").first()
    
    camp1 = CAMPAGNE(plateforme.nom_plateforme, date(2024, 1, 15), 30, "Montana, USA", True)
    camp2 = CAMPAGNE(plateforme.nom_plateforme, date(2024, 3, 10), 45, "Patagonie, Argentine", True)
    camp3 = CAMPAGNE(plateforme.nom_plateforme, date(2024, 7, 12), 50, "Le Caire, Égypte", True)
    
    db.session.add_all([camp1, camp2, camp3])
    db.session.commit()
    
    assert CAMPAGNE.query.count() == 3
    assert CAMPAGNE.query.filter_by(lieu="Montana, USA").first().valide is True
    assert camp1.plateforme.nom_plateforme == "Plateforme A"
    assert len(plateforme.campagnes) == 3

def test_participer_campagne():
    """Teste l'association PARTICIPER_CAMPAGNE entre CAMPAGNE et PERSONNEL."""
    personnel = PERSONNEL.query.all()
    campagnes = CAMPAGNE.query.all()
    
    part_camp1 = PARTICIPER_CAMPAGNE(campagnes[0].id_campagne, personnel[0].id_personnel)
    part_camp2 = PARTICIPER_CAMPAGNE(campagnes[1].id_campagne, personnel[1].id_personnel)
    part_camp3 = PARTICIPER_CAMPAGNE(campagnes[0].id_campagne, personnel[2].id_personnel)
    part_camp4 = PARTICIPER_CAMPAGNE(campagnes[2].id_campagne, personnel[2].id_personnel)
    
    db.session.add_all([part_camp1, part_camp2, part_camp3, part_camp4])
    db.session.commit()
    
    assert PARTICIPER_CAMPAGNE.query.count() == 4
    assert PARTICIPER_CAMPAGNE.query.filter_by(id_personnel=personnel[2].id_personnel).count() == 2
    assert len(personnel[2].posseder) == 2

def test_posseder():
    """Teste l'association POSSEDER entre HABILITATION et PERSONNEL."""
    personnel = PERSONNEL.query.all()
    habilitations = HABILITATION.query.all()
    
    poss1 = POSSEDER(habilitations[0].id_habilitation, personnel[0].id_personnel)
    poss2 = POSSEDER(habilitations[1].id_habilitation, personnel[1].id_personnel)
    poss3 = POSSEDER(habilitations[0].id_habilitation, personnel[2].id_personnel)
    poss4 = POSSEDER(habilitations[2].id_habilitation, personnel[2].id_personnel)
    
    db.session.add_all([poss1, poss2, poss3, poss4])
    db.session.commit()
    
    assert POSSEDER.query.count() == 4
    assert POSSEDER.query.filter_by(id_personnel=personnel[2].id_personnel).count() == 2
    assert len(personnel[2].posseder) == 2

def test_especes():
    """Teste la création d'entités ESPECE."""
    espece1 = ESPECE("T-Rex", "Tyrannosaurus Rex", "AGCT...")
    espece2 = ESPECE("Triceratops", "Triceratops horridus", "GTCA...")
    db.session.add_all([espece1, espece2])
    db.session.commit()

    assert ESPECE.query.count() == 2
    assert ESPECE.query.filter_by(nom_espece="T-Rex").first().genome == "AGCT..."

def test_echantillons():
    """Teste la création d'entités ECHANTILLON."""
    echantillon1 = ECHANTILLON(1, "TRex_dent.adn", "Dent de T-Rex")
    echantillon2 = ECHANTILLON(2, "Tric_corne.adn", "Corne de Triceratops")
    db.session.add_all([echantillon1, echantillon2])
    db.session.commit()

    assert ECHANTILLON.query.count() == 2
    assert ECHANTILLON.query.filter_by(commentaire="Dent de T-Rex").first() is not None

def test_appartenir():
    """Teste l'association APPARTENIR entre ECHANTILLON et ESPECE."""
    echantillon = ECHANTILLON.query.filter_by(commentaire="Dent de T-Rex").first()
    espece = ESPECE.query.filter_by(nom_espece="T-Rex").first()
    
    echantillon.espece = espece
    db.session.commit()
    
    assert echantillon.espece.nom_espece == "T-Rex"
    assert len(espece.echantillons) == 1
    assert espece.echantillons[0].commentaire == "Dent de T-Rex"

def test_recolter():
    """Teste l'association RECOLTER entre ECHANTILLON et CAMPAGNE."""
    echantillon = ECHANTILLON.query.filter_by(commentaire="Corne de Triceratops").first()
    campagne = CAMPAGNE.query.filter_by(lieu="Patagonie, Argentine").first()
    
    echantillon.campagne = campagne
    db.session.commit()
    
    assert echantillon.campagne.lieu == "Patagonie, Argentine"
    assert len(campagne.echantillons) == 1
    assert campagne.echantillons[0].commentaire == "Corne de Triceratops"

def run_tests():
    """Exécute tous les tests dans le contexte de l'application."""
    with app.app_context():
        print("--- Nettoyage de la base de données ---")
        clear_database()
        
        print("--- Démarrage des tests ---")
        

        test_personnel()
        test_habilitations()

        test_posseder()
        
        test_plateformes()
        test_especes()

        test_campagnes_et_utiliser()

        test_echantillons()
        
        test_participer_campagne()
        test_appartenir()
        test_recolter()
        
        print("--- Tests terminés avec succès ---")

if __name__ == "__main__":
    run_tests()

