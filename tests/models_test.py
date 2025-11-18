from LaboDino.models import PLATEFORME, PERSONNEL
from LaboDino.app import db
def plateforme_test():
    plateforme = PLATEFORME("Plateforme 1", 5, 50, 10)
    db.session.add(plateforme)
    db.session.commit()
    
    print(PLATEFORME.query.all())

plateforme_test()
