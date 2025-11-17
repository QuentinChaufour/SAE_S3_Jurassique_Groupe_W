from LaboDino.models import ROLE, PLATEFORME, PERSONNEL, CAMPAGNE, ECHANTILLON, ESPECE, PARTICIPER_CAMPAGNE
# Importer l'objet app en plus de db
from LaboDino.app import db, app

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

    # Ajout d'un print pour voir le résultat
    print("Personnel:", PERSONNEL.query.all())

# Mettre en place le contexte d'application avant d'appeler les fonctions
with app.app_context():
    # Crée les tables si elles n'existent pas (important pour les tests)
    db.create_all()
    
    print("--- Démarrage des tests ---")
    models_test()
    personnel_tests()
    print("--- Tests terminés ---")

