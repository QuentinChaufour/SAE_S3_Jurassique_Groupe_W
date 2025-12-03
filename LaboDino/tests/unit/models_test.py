import pytest
from LaboDino.models import *
from LaboDino.app import db
from datetime import date

def test_personnel():

    personnel = PERSONNEL("Bernard", "Luc", "mdp789", ROLE.technicien)

    assert personnel.role == ROLE.technicien

def test_habilitations():
        
    hab1 = HABILITATION(nom_habilitation="Manipulation ADN")

    assert hab1.nom_habilitation == "Manipulation ADN"

def test_posseder():
    hab1 = HABILITATION(nom_habilitation="Manipulation ADN")
    hab2 = HABILITATION(nom_habilitation="Séquençage")
    hab3 = HABILITATION(nom_habilitation="Analyse génomique")
    personnel3 = PERSONNEL("Bernard", "Luc", "mdp789", ROLE.technicien)
    poss3 = POSSEDER(hab1.id_habilitation, personnel3.id_personnel)
    poss4 = POSSEDER(hab3.id_habilitation, personnel3.id_personnel)

    personnel3.posseder.append(poss3)
    personnel3.posseder.append(poss4)

    assert len(personnel3.posseder) == 2

def test_equipements():
    equip1 = EQUIPEMENT(nom_equipement="Séquenceur ADN")
    equip2 = EQUIPEMENT(nom_equipement="Microscope")
    equip3 = EQUIPEMENT(nom_equipement="Centrifugeuse")
    equip4 = EQUIPEMENT(nom_equipement="Pinceau")

    assert equip1.nom_equipement == "Séquenceur ADN"

def test_plateformes():
    plat1 = PLATEFORME("Plateforme Sequence", 5, 1500, 90)
    plat2 = PLATEFORME("Plateforme Paléontologie", 3, 800, 60)
    plat3 = PLATEFORME("Plateforme Analyse", 4, 1200, 45)
    plat4 = PLATEFORME("Plateforme A", 5, 1500, 90)
    plat5 = PLATEFORME("Plateforme B", 3, 800, 60)

    assert plat1.nom_plateforme == "Plateforme Sequence"

def test_inclure_equipement():
        plateforme_sequence = PLATEFORME("Plateforme Sequence", 5, 1500, 90)
        plateforme_paleontologie = PLATEFORME("Plateforme Paléontologie", 3, 800, 60)
        plateforme_analyse = PLATEFORME("Plateforme Analyse", 4, 1200, 45)

        sequenceur = EQUIPEMENT(nom_equipement="Séquenceur ADN")
        microscope = EQUIPEMENT(nom_equipement="Microscope")
        centrifugeuse = EQUIPEMENT(nom_equipement="Centrifugeuse")
        pinceau = EQUIPEMENT(nom_equipement="Pinceau")

        plateforme_sequence.equipements.append(sequenceur)
        plateforme_sequence.equipements.append(pinceau)
        plateforme_paleontologie.equipements.append(microscope)
        plateforme_analyse.equipements.append(centrifugeuse)

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
    
    hab1 = HABILITATION(nom_habilitation="Manipulation ADN")
    hab2 = HABILITATION(nom_habilitation="Séquençage")
    hab3 = HABILITATION(nom_habilitation="Analyse génomique")

    sequenceur = EQUIPEMENT(nom_equipement="Séquenceur ADN")
    pinceau = EQUIPEMENT(nom_equipement="Microscope")
    microscope = EQUIPEMENT(nom_equipement="Centrifugeuse")
    centrifugeuse = EQUIPEMENT(nom_equipement="Pinceau")

    sequenceur.habilitations.append(hab1)
    sequenceur.habilitations.append(hab2)
    microscope.habilitations.append(hab3)

    assert len(sequenceur.habilitations) == 2
    assert len(microscope.habilitations) == 1
    assert len(pinceau.habilitations) == 0

def test_campagnes():
        
    plateforme_sequence = PLATEFORME("Plateforme Sequence", 5, 1500, 90)
    plateforme_paleontologie = PLATEFORME("Plateforme Paléontologie", 3, 800, 60)
    plateforme_analyse = PLATEFORME("Plateforme Analyse", 4, 1200, 45)

    camp1 = CAMPAGNE(plateforme_sequence.nom_plateforme, date(2024, 1, 15), 30, "Montana, USA", True)
    camp2 = CAMPAGNE(plateforme_paleontologie.nom_plateforme, date(2024, 3, 10), 45, "Patagonie, Argentine", True)
    camp3 = CAMPAGNE(plateforme_analyse.nom_plateforme, date(2024, 6, 1), 20, "Gobi, Mongolie", False)

    camp1.plateforme = plateforme_sequence

    assert camp1.plateforme.nom_plateforme == "Plateforme Sequence"

def test_plateforme_campagne():
    
    plateforme_sequence = PLATEFORME("Plateforme Sequence", 5, 1500, 90)
    plateforme_paleontologie = PLATEFORME("Plateforme Paléontologie", 3, 800, 60)
    plateforme_analyse = PLATEFORME("Plateforme Analyse", 4, 1200, 45)
    campagne_montana = CAMPAGNE(plateforme_sequence.nom_plateforme, date(2024, 1, 15), 30, "Montana, USA", True)
    camp2 = CAMPAGNE(plateforme_paleontologie.nom_plateforme, date(2024, 3, 10), 45, "Patagonie, Argentine", True)

    campagne_montana.plateforme = plateforme_sequence
    camp2.plateforme = plateforme_paleontologie


    assert campagne_montana.plateforme.nom_plateforme == "Plateforme Sequence"
    assert len(plateforme_sequence.campagnes) == 1
    assert len(plateforme_paleontologie.campagnes) == 1
    assert len(plateforme_analyse.campagnes) == 0    
    
def test_budgets():
    
    budg1 = BUDGET(date(2024, 1, 1), 50000)

    assert budg1.budget_total == 50000  

def test_maintenances():
    
    plateforme_sequence = PLATEFORME("Plateforme Sequence", 5, 1500, 90)
    plateforme_paleontologie = PLATEFORME("Plateforme Paléontologie", 3, 800, 60)
    plateforme_analyse = PLATEFORME("Plateforme Analyse", 4, 1200, 45)

    maint_sequence_janvier = MAINTENANCE(plateforme_sequence.nom_plateforme, date(2024, 1, 15), 7)
    maint_sequence_janvier.plateforme = plateforme_sequence


    assert maint_sequence_janvier.duree_maintenance == 7
    assert maint_sequence_janvier.plateforme.nom_plateforme == "Plateforme Sequence"
    assert len(plateforme_sequence.maintenances) == 1

        
        
    
def test_participer_campagne():
    """Teste l'association PARTICIPER_CAMPAGNE entre CAMPAGNE et PERSONNEL."""
    
    personnel3 = PERSONNEL("Bernard", "Luc", "mdp789", ROLE.technicien)

    plat1 = PLATEFORME("Plateforme Sequence", 5, 1500, 90)
    plat2 = PLATEFORME("Plateforme Paléontologie", 3, 800, 60)

    camp1 = CAMPAGNE(plat1.nom_plateforme, date(2024, 1, 15), 30, "Montana, USA", True)
    camp2 = CAMPAGNE(plat2.nom_plateforme, date(2024, 3, 10), 45, "Patagonie, Argentine", True)

    part_camp3 = PARTICIPER_CAMPAGNE(camp1.id_campagne, personnel3.id_personnel)
    part_camp4 = PARTICIPER_CAMPAGNE(camp2.id_campagne, personnel3.id_personnel)

    personnel3.participerCampagne.append(part_camp3)
    personnel3.participerCampagne.append(part_camp4)

    assert len(personnel3.participerCampagne) == 2

def test_especes():
    """Teste la création d'entités ESPECE."""
    
    espece1 = ESPECE("T-Rex", "Tyrannosaurus Rex", "AGCT...")
    espece2 = ESPECE("Triceratops", "Triceratops horridus", "GTCA...")

    assert espece1.genome == "AGCT..." 
    
def test_echantillons():
    """Teste la création d'entités ECHANTILLON."""
    
    plat1 = PLATEFORME("Plateforme Sequence", 5, 1500, 90)
    plat2 = PLATEFORME("Plateforme Paléontologie", 3, 800, 60)

    camp1 = CAMPAGNE(plat1.nom_plateforme, date(2024, 1, 15), 30, "Montana, USA", True)
    camp2 = CAMPAGNE(plat2.nom_plateforme, date(2024, 3, 10), 45, "Patagonie, Argentine", True)

    echantillon1 = ECHANTILLON(1, "TRex_dent.adn", "Dent de T-Rex")
    echantillon2 = ECHANTILLON(2, "Tric_corne.adn", "Corne de Triceratops")

    assert echantillon1 is not None

def test_appartenir():
    """Teste l'association APPARTENIR entre ECHANTILLON et ESPECE."""
    
    plat1 = PLATEFORME("Plateforme Sequence", 5, 1500, 90)

    camp1 = CAMPAGNE(plat1.nom_plateforme, date(2024, 1, 15), 30, "Montana, USA", True)

    echantillon1 = ECHANTILLON(camp1.id_campagne, "TRex_dent.adn", "Dent de T-Rex")

    espece1 = ESPECE("T-Rex", "Tyrannosaurus Rex", "AGCT...")

    echantillon1.espece = espece1

    assert echantillon1.espece.nom_espece == "T-Rex"
    assert len(espece1.echantillons) == 1
    assert espece1.echantillons[0].commentaire == "Dent de T-Rex"

def test_recolter():
    """Teste l'association RECOLTER entre ECHANTILLON et CAMPAGNE."""
    
    plat1 = PLATEFORME("Plateforme Sequence", 5, 1500, 90)
    plat2 = PLATEFORME("Plateforme Paléontologie", 3, 800, 60)
    plat3 = PLATEFORME("Plateforme Analyse", 4, 1200, 45)

    camp1 = CAMPAGNE(plat1.nom_plateforme, date(2024, 1, 15), 30, "Montana, USA", True)
    camp2 = CAMPAGNE(plat2.nom_plateforme, date(2024, 3, 10), 45, "Patagonie, Argentine", True)

    echantillon1 = ECHANTILLON(camp1.id_campagne, "TRex_dent.adn", "Dent de T-Rex")
    echantillon2 = ECHANTILLON(camp2.id_campagne, "Tric_corne.adn", "Corne de Triceratops")

    echantillon1.campagne = camp1
    camp2.echantillons.append(echantillon2)

    assert echantillon1.campagne.lieu == "Montana, USA"
    assert len(camp2.echantillons) == 1
    assert camp2.echantillons[0].commentaire == "Corne de Triceratops"
