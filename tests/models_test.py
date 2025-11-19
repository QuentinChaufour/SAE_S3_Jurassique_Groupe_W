from LaboDino.models import PLATEFORME, PERSONNEL
from LaboDino.app import app, db

def plateforme_test():
    plateforme = PLATEFORME("Plateforme 1", 5, 50, 10)
    db.session.add(plateforme)
    db.session.commit()
    
    print(PLATEFORME.query.all())

if __name__ == "__main__":
    with app.app_context():
        #db.drop_all()
        db.create_all()
        
        plateforme_test()
