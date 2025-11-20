from LaboDino.models import ROLE, PLATEFORME, PERSONNEL, CAMPAGNE, ECHANTILLON, ESPECE
# Importer l'objet app en plus de db
from LaboDino.app import db, app
from sqlalchemy import text
import datetime

def models_test():
    plateforme = PLATEFORME("Plateforme 1", 5, 50, 10)
    db.session.add(plateforme)
    db.session.commit()
    
    # Ajout d'un print pour voir le résultat
    print("Plateformes:", PLATEFORME.query.all())

def personnel_tests():
    alice = PERSONNEL("Thymefield","Alice", "symmetrie1", ROLE.chercheur)
    db.session.add(alice)
    db.session.commit()

    print("Personnels:", PERSONNEL.query.all())

def campagne_tests():
    campagne = CAMPAGNE("Plateforme 1", datetime.date(2024,1,1), 30, "Jurassic Park", True)
    db.session.add(campagne)
    db.session.commit()

    print("Campagnes:", CAMPAGNE.query.all())

def participer_campagne_tests():
    alice = PERSONNEL("Wheel","Piper", "track2ter", ROLE.technicien)
    campagne2 = CAMPAGNE("Plateforme 1", datetime.date(2024,1,1), 30, "Jurassico Park", True)
    db.session.add(alice)
    db.session.add(campagne2)
    alice.campagne.append(campagne2)
    db.session.commit()


    print(f"Campagnes d'Alice : {alice.campagne}")
    print(f"Personnel de la campagne : {campagne2.personnel}")

def utiliser_tests():
    campagne3 = CAMPAGNE("Plateforme 2", datetime.date(2024,1,1), 30, "Jurassica Park", True)
    plateforme2 = PLATEFORME("Plateforme 2", 2, 30, 10)
    db.session.add_all([campagne3, plateforme2])
    plateforme2.campagnes.append(campagne3)
    db.session.commit()

    print(f"La plateforme de la campagne 3 : {campagne3.plateforme}")
    print(f"Campagnes de la plateforme 2: {plateforme2.campagnes}")

def espece_tests():
    calamar = ESPECE("Calamar","Loligo vulgaris","ACGTTA")
    db.session.add(calamar)
    db.session.commit()

def echantillon_tests():
    #Erreur: echantillon1 = ECHANTILLON(7, "adn.adn", "cette table est incorrect")
    echantillon = ECHANTILLON(3, "mystere.adn", "echantillon d'une espèce inconnu")
    db.session.add(echantillon)
    db.session.commit()
    print("ECHANTILLONS:", ECHANTILLON.query.all())

def appartenir_tests():
    echantillon1 = ECHANTILLON(1, "loligo.adn", "une espèce marine avec des tentacules...")
    echantillon2 = ECHANTILLON(1, "vulgaris.adn", "une espèce marine avec une tête ovale...")
    poulpe = ESPECE("Poulpe","Octopus vulgaris","AGGTTC")
    poulpe_espion = ESPECE("Poulpe?")
    db.session.add_all([echantillon1, echantillon2, poulpe, poulpe_espion])
    echantillon1.espece.append(poulpe)
    echantillon2.espece.append(poulpe)
    #Erreur: echantillon.espece.append(poulpe_espion)
    db.session.commit()
    print(f"L'echantillon1 vient de l'animal : {echantillon1.espece}")
    print(f"L'espèce poulpe possède comme echantillons : {poulpe.echantillons}")

def recolter_tests():
    echantillon = ECHANTILLON(2, "test.adn", "UNE ESPECE TEST")
    campagne4 = CAMPAGNE("Plateforme 1", datetime.date(2025, 10, 21), 20, "Test Park", True)
    db.session.add_all([echantillon, campagne4])
    campagne4.echantillons.append(echantillon)
    db.session.commit()
    print(f"L'echantillon vient de la campagne : {echantillon.campagne} donc {echantillon.id_campagne}")

# Mettre en place le contexte d'application avant d'appeler les fonctions
with app.app_context():
    print("--- Nettoyage de la base de données ---")
    
    # 1. ON DÉSACTIVE LA SÉCURITÉ
    db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    db.session.commit()
    
    db.drop_all()
    
    # 3. ON RÉACTIVE LA SÉCURITÉ
    db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    db.session.commit()
    
    db.create_all()
    
    print("--- Démarrage des tests ---")
    
    models_test()
    personnel_tests()
    campagne_tests()
    participer_campagne_tests()
    utiliser_tests()
    espece_tests()
    echantillon_tests()
    appartenir_tests()
    recolter_tests()
    
    print("--- Tests terminés ---") 

