from LaboDino.models import PLATEFORME
from LaboDino.app import db
class Models_Test():
    plateforme = PLATEFORME("Plateforme 1", 5, 50, 10)
    db.session.add(plateforme)
    db.session.commit()
    
    PLATEFORME.query.all()
