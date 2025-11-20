from LaboDino.models import *
from LaboDino.app import app, db
from datetime import date

def clear_database():
    db.session.execute(db.text("SET FOREIGN_KEY_CHECKS=0;"))
    db.session.commit()
    
    # Supprimer toutes les tables
    db.drop_all()
    
    # Recréer toutes les tables
    db.create_all()
    
    # Réactiver les vérifications de clés étrangères
    db.session.execute(db.text("SET FOREIGN_KEY_CHECKS=1;"))
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
        
    db.session.add_all([plat1, plat2, plat3])
    db.session.commit()
    assert PLATEFORME.query.count() == 3
    assert PLATEFORME.query.filter_by(nom_plateforme="Plateforme Sequence").first().nb_personnes_requises == 5
    assert PLATEFORME.query.filter_by(nom_plateforme="Plateforme Sequence").first().cout_journalier == 1500

def test_inclure_equipement():
    plateformes = PLATEFORME.query.all()
    equipements = EQUIPEMENT.query.all()
    print("EQUIPEMENTS 0 ", equipements[0])
    
    EQUIPEMENT.query.filter_by(nom_equipement="Séquenceur ADN").first()
    EQUIPEMENT.query.filter_by(nom_equipement="Centrifugeuse").first()

    plateformes[0].equipements.append(equipements[0])
    plateformes[0].equipements.append(equipements[3])
    plateformes[1].equipements.append(equipements[1])
    plateformes[2].equipements.append(equipements[2])

    db.session.commit()
    
    assert len(plateformes[0].equipements) == 2
    assert len(plateformes[1].equipements) == 1
    assert len(plateformes[2].equipements) == 1

    plateforme_sequence = PLATEFORME.query.filter_by(nom_plateforme="Plateforme Sequence").first()
    sequenceur_present = False
    pinceau_present = False
    print(PLATEFORME.query.filter_by(nom_plateforme="Plateforme Sequence").first().equipements)
    for equip in plateforme_sequence.equipements:
        print("EQUIPEMENT", plateforme_sequence.equipements)
        if equip.nom_equipement == "Séquenceur ADN":
            sequenceur_present = True
        if equip.nom_equipement == "Pinceau":
            pinceau_present = True
    
    assert sequenceur_present
    assert pinceau_present


def test_necessiter_habilitation():
    equipements = EQUIPEMENT.query.all()
    habilitations = HABILITATION.query.all()
    
    equipements[0].habilitations.append(habilitations[0])
    equipements[0].habilitations.append(habilitations[1])
    equipements[1].habilitations.append(habilitations[2])
    equipements[3].habilitations.append(habilitations[0])
    
    db.session.commit()
    
    assert len(equipements[0].habilitations) == 2
    assert len(equipements[1].habilitations) == 1
    assert len(equipements[3].habilitations) == 1

def test_campagnes():
    plateformes = PLATEFORME.query.all()
    
    camp1 = CAMPAGNE(
        plateformes[0].nom_plateforme,
        date(2024, 1, 15),
        30,
        "Montana, USA",
        True
    )
    camp2 = CAMPAGNE(plateformes[1].nom_plateforme, date(2024, 3, 10), 45, "Patagonie, Argentine", True)
    camp3 = CAMPAGNE(plateformes[2].nom_plateforme, date(2024, 6, 1), 20, "Gobi, Mongolie", False)
    
    db.session.add_all([camp1, camp2, camp3])
    db.session.commit()
    
    assert CAMPAGNE.query.count() == 3
    assert CAMPAGNE.query.filter_by(lieu="Montana, USA").first().valide == True
    assert CAMPAGNE.query.filter_by(lieu="Gobi, Mongolie").first().valide == False
    assert camp1.id_campagne is not None
    assert camp1.plateforme.nom_plateforme == "Plateforme Sequence"

def test_plateforme_campagne():
    plateformes = PLATEFORME.query.all()
    campagnes = CAMPAGNE.query.all()
    
    assert campagnes[0].plateforme.nom_plateforme == "Plateforme Sequence"
    assert len(plateformes[0].campagnes) == 1
    assert len(plateformes[1].campagnes) == 1

def test_budgets():
    budg1 = BUDGET(date(2024, 1, 1), 50000)
    budg2 = BUDGET(date(2024, 2, 1), 40000)
    budg3 = BUDGET(date(2024, 3, 1), 10000)
    budg4 = BUDGET(date(2024, 4, 1), 5000)
    
    db.session.add_all([budg1, budg2, budg3, budg4])
    db.session.commit()
    
    assert BUDGET.query.count() == 4
    assert BUDGET.query.filter_by(date_mois_annee=date(2024, 1, 1)).first().budget_total ==50000
    
    budg1.budget_total = 50000
    db.session.commit()
    assert BUDGET.query.filter_by(date_mois_annee=date(2024, 1, 1)).first().budget_total == 50000

def test_maintenances():
    plateformes = PLATEFORME.query.all()
    
    maint1 = MAINTENANCE( plateformes[0].nom_plateforme, date(2024, 1, 15), 7)
    maint2 = MAINTENANCE( plateformes[0].nom_plateforme, date(2024, 4, 15), 5)
    maint3 = MAINTENANCE( plateformes[1].nom_plateforme, date(2024, 2, 20), 10)
    
    db.session.add_all([maint1, maint2, maint3])
    db.session.commit()
    
    assert MAINTENANCE.query.count() == 3
    assert MAINTENANCE.query.first().duree_maintenance == 7
    assert maint1.plateforme.nom_plateforme == "Plateforme Sequence"
    assert len(plateformes[0].maintenances) == 2

def run_tests():
    with app.app_context():
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

if __name__ == "__main__":
    run_tests()