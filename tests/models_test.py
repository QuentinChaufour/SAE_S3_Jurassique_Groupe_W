from LaboDino.models import *
from LaboDino.app import app, db
from sqlalchemy import text
from datetime import date

def clear_database():
    db.drop_all()
    db.create_all()
    db.session.commit()

def test_personnel():
    personnel1 = PERSONNEL("Dupont", "Jean", "mdp123", ROLE.administratif)
    personnel2 = PERSONNEL("Martin", "Sophie", "mdp456", ROLE.chercheur)
    personnel3 = PERSONNEL("Bernard", "Luc", "mdp789", ROLE.technicien)
    personnel4 = PERSONNEL("Dubois", "Marie", "mdp101", ROLE.direction)
    
    db.session.add_all([personnel1, personnel2, personnel3, personnel4])
    db.session.commit()
    
    assert PERSONNEL.query.count() == 4
    assert PERSONNEL.query.filter_by(nom="Dupont").first().prenom == "Jean"
    assert PERSONNEL.query.filter_by(nom="Martin").first().role == ROLE.chercheur
    assert PERSONNEL.query.filter_by(role=ROLE.direction).count() == 1

def test_habilitations():
    hab1 = HABILITATION(nom_habilitation="Manipulation ADN")
    hab2 = HABILITATION(nom_habilitation="Séquençage")
    hab3 = HABILITATION(nom_habilitation="Analyse génomique")
    
    db.session.add_all([hab1, hab2, hab3])
    db.session.commit()
    
    assert HABILITATION.query.count() == 3
    assert HABILITATION.query.filter_by(nom_habilitation="Séquençage").first() is not None
    assert hab1.id_habilitation is not None

def test_posseder():
    personnel_dupont = PERSONNEL.query.filter_by(nom="Dupont").first()
    personnel_martin = PERSONNEL.query.filter_by(nom="Martin").first()
    personnel_bernard = PERSONNEL.query.filter_by(nom="Bernard").first()
    
    hab_manipulation = HABILITATION.query.filter_by(nom_habilitation="Manipulation ADN").first()
    hab_sequencage = HABILITATION.query.filter_by(nom_habilitation="Séquençage").first()
    hab_analyse = HABILITATION.query.filter_by(nom_habilitation="Analyse génomique").first()
    
    poss1 = POSSEDER(hab_manipulation.id_habilitation, personnel_dupont.id_personnel)
    poss2 = POSSEDER(hab_sequencage.id_habilitation, personnel_martin.id_personnel)
    poss3 = POSSEDER(hab_manipulation.id_habilitation, personnel_bernard.id_personnel)
    poss4 = POSSEDER(hab_analyse.id_habilitation, personnel_bernard.id_personnel)
    
    db.session.add_all([poss1, poss2, poss3, poss4])
    db.session.commit()
    
    assert POSSEDER.query.count() == 4
    assert POSSEDER.query.filter_by(id_personnel=personnel_bernard.id_personnel).count() == 2
    assert len(personnel_bernard.posseder) == 2

def test_equipements():
    equip1 = EQUIPEMENT(nom_equipement="Séquenceur ADN")
    equip2 = EQUIPEMENT(nom_equipement="Microscope")
    equip3 = EQUIPEMENT(nom_equipement="Centrifugeuse")
    equip4 = EQUIPEMENT(nom_equipement="Pinceau")
    
    db.session.add_all([equip1, equip2, equip3, equip4])
    db.session.commit()
    
    assert EQUIPEMENT.query.count() == 4
    assert EQUIPEMENT.query.filter_by(nom_equipement="Séquenceur ADN").first() is not None
    assert equip1.id_equipement is not None

def test_plateformes():
    plat1 = PLATEFORME("Plateforme Sequence", 5, 1500, 90)
    plat2 = PLATEFORME("Plateforme Paléontologie", 3, 800, 60)
    plat3 = PLATEFORME("Plateforme Analyse", 4, 1200, 45)
    plat4 = PLATEFORME("Plateforme A", 5, 1500, 90)
    plat5 = PLATEFORME("Plateforme B", 3, 800, 60)
        
    db.session.add_all([plat1, plat2, plat3, plat4, plat5])
    db.session.commit()

    assert PLATEFORME.query.count() == 5
    assert PLATEFORME.query.filter_by(nom_plateforme="Plateforme Sequence").first().nb_personnes_requises == 5
    assert PLATEFORME.query.filter_by(nom_plateforme="Plateforme Sequence").first().cout_journalier == 1500
    assert PLATEFORME.query.filter_by(nom_plateforme="Plateforme A").first().nb_personnes_requises == 5

def test_inclure_equipement():

    sequenceur = EQUIPEMENT.query.filter_by(nom_equipement="Séquenceur ADN").first()
    microscope = EQUIPEMENT.query.filter_by(nom_equipement="Microscope").first()
    centrifugeuse = EQUIPEMENT.query.filter_by(nom_equipement="Centrifugeuse").first()
    pinceau = EQUIPEMENT.query.filter_by(nom_equipement="Pinceau").first()
    
    plateforme_sequence = PLATEFORME.query.filter_by(nom_plateforme="Plateforme Sequence").first()
    plateforme_paleontologie = PLATEFORME.query.filter_by(nom_plateforme="Plateforme Paléontologie").first()
    plateforme_analyse = PLATEFORME.query.filter_by(nom_plateforme="Plateforme Analyse").first()

    plateforme_sequence.equipements.append(sequenceur)
    plateforme_sequence.equipements.append(pinceau)
    plateforme_paleontologie.equipements.append(microscope)
    plateforme_analyse.equipements.append(centrifugeuse)

    db.session.commit()

    assert len(plateforme_sequence.equipements) == 2
    
    sequenceur_present = False
    pinceau_present = False
    
    for equip in plateforme_sequence.equipements:
        if equip.nom_equipement == "Séquenceur ADN":
            sequenceur_present = True
        if equip.nom_equipement == "Pinceau":
            pinceau_present = True
    
    assert sequenceur_present
    assert pinceau_present


def test_necessiter_habilitation():
    sequenceur = EQUIPEMENT.query.filter_by(nom_equipement="Séquenceur ADN").first()
    microscope = EQUIPEMENT.query.filter_by(nom_equipement="Microscope").first()
    pinceau = EQUIPEMENT.query.filter_by(nom_equipement="Pinceau").first()
    
    hab_manipulation = HABILITATION.query.filter_by(nom_habilitation="Manipulation ADN").first()
    hab_sequencage = HABILITATION.query.filter_by(nom_habilitation="Séquençage").first()
    hab_analyse = HABILITATION.query.filter_by(nom_habilitation="Analyse génomique").first()
    
    sequenceur.habilitations.append(hab_manipulation)
    sequenceur.habilitations.append(hab_sequencage)
    microscope.habilitations.append(hab_analyse)
    pinceau.habilitations.append(hab_manipulation)
    
    db.session.commit()
    
    sequenceur = EQUIPEMENT.query.filter_by(nom_equipement="Séquenceur ADN").first()
    microscope = EQUIPEMENT.query.filter_by(nom_equipement="Microscope").first()
    pinceau = EQUIPEMENT.query.filter_by(nom_equipement="Pinceau").first()
    
    assert len(sequenceur.habilitations) == 2
    assert len(microscope.habilitations) == 1
    assert len(pinceau.habilitations) == 1

def test_campagnes():
    plateforme_sequence = PLATEFORME.query.filter_by(nom_plateforme="Plateforme Sequence").first()
    plateforme_paleontologie = PLATEFORME.query.filter_by(nom_plateforme="Plateforme Paléontologie").first()
    plateforme_analyse = PLATEFORME.query.filter_by(nom_plateforme="Plateforme Analyse").first()
    
    camp1 = CAMPAGNE(plateforme_sequence.nom_plateforme, date(2024, 1, 15), 30, "Montana, USA", True)
    camp2 = CAMPAGNE(plateforme_paleontologie.nom_plateforme, date(2024, 3, 10), 45, "Patagonie, Argentine", True)
    camp3 = CAMPAGNE(plateforme_analyse.nom_plateforme, date(2024, 6, 1), 20, "Gobi, Mongolie", False)
    
    db.session.add_all([camp1, camp2, camp3])
    db.session.commit()
    
    assert CAMPAGNE.query.count() == 3
    assert CAMPAGNE.query.filter_by(lieu="Montana, USA").first().valide == True
    assert CAMPAGNE.query.filter_by(lieu="Gobi, Mongolie").first().valide == False
    assert camp1.id_campagne is not None
    assert camp1.plateforme.nom_plateforme == "Plateforme Sequence"

def test_plateforme_campagne():
    plateforme_sequence = PLATEFORME.query.filter_by(nom_plateforme="Plateforme Sequence").first()
    plateforme_paleontologie = PLATEFORME.query.filter_by(nom_plateforme="Plateforme Paléontologie").first()
    campagne_montana = CAMPAGNE.query.filter_by(lieu="Montana, USA").first()
    plateforme = PLATEFORME.query.filter_by(nom_plateforme="Plateforme A").first()
    
    assert campagne_montana.plateforme.nom_plateforme == "Plateforme Sequence"
    assert len(plateforme_sequence.campagnes) == 1
    assert len(plateforme_paleontologie.campagnes) == 1
    assert CAMPAGNE.query.count() == 3
    assert CAMPAGNE.query.filter_by(lieu="Montana, USA").first().valide is True
    assert len(plateforme.campagnes) == 0
    
def test_budgets():
    budg1 = BUDGET(date(2024, 1, 1), 50000)
    budg2 = BUDGET(date(2024, 2, 1), 40000)
    budg3 = BUDGET(date(2024, 3, 1), 10000)
    budg4 = BUDGET(date(2024, 4, 1), 5000)
    
    db.session.add_all([budg1, budg2, budg3, budg4])
    db.session.commit()
    
    assert BUDGET.query.count() == 4
    assert BUDGET.query.filter_by(date_mois_annee=date(2024, 1, 1)).first().budget_total == 50000
    
    budg1.budget_total = 50000
    db.session.commit()
    
    assert BUDGET.query.filter_by(date_mois_annee=date(2024, 1, 1)).first().budget_total == 50000

def test_maintenances():
    plateforme_sequence = PLATEFORME.query.filter_by(nom_plateforme="Plateforme Sequence").first()
    plateforme_paleontologie = PLATEFORME.query.filter_by(nom_plateforme="Plateforme Paléontologie").first()
    
    maint1 = MAINTENANCE(plateforme_sequence.nom_plateforme, date(2024, 1, 15), 7)
    maint2 = MAINTENANCE(plateforme_sequence.nom_plateforme, date(2024, 4, 15), 5)
    maint3 = MAINTENANCE(plateforme_paleontologie.nom_plateforme, date(2024, 2, 20), 10)
    
    db.session.add_all([maint1, maint2, maint3])
    db.session.commit()
    
    maint_sequence_janvier = MAINTENANCE.query.filter_by(nom_plateforme="Plateforme Sequence", date_maintenance=date(2024, 1, 15)).first()

    assert MAINTENANCE.query.count() == 3
    assert maint_sequence_janvier.duree_maintenance == 7
    assert maint_sequence_janvier.plateforme.nom_plateforme == "Plateforme Sequence"
    assert len(plateforme_sequence.maintenances) == 2
    
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
    with app.app_context():
        print("Début des tests de l'ORM")
        clear_database()
        
        test_personnel()
        test_habilitations()
        test_posseder()
        test_equipements()
        test_plateformes()
        test_inclure_equipement()
        test_necessiter_habilitation()
        test_campagnes()
        test_plateforme_campagne()
        test_budgets()
        test_maintenances()
        test_participer_campagne()
        test_especes()
        test_echantillons()
        test_appartenir()
        test_recolter()

        print("Tests de l'ORM terminé, tout les tests sont passés")

if __name__ == "__main__":
    run_tests()
