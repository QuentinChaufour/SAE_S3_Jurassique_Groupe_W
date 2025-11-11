from .app import db

class Role(db.Enum):
    administratif = 'administratif'
    chercheur = 'chercheur'
    technicien = 'technicien'
    direction = 'direction'

class ESPECE(db.Model):
    __tablename__ = 'ESPECE'
    idEspece = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nomEspece = db.Column(db.String(50))
    nomScientifique = db.Column(db.String(100))
    genome = db.Column(db.Text)

class ECHANTILLON(db.Model):
    __tablename__ = 'ECHANTILLON'
    idEchantillon = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idCampagne = db.Column(db.Integer,db.ForeignKey("CAMPAGNE.idCampagne"))
    fichierSequenceADN = db.Column(MEDIUMTEXT)
    idEspece = db.Column(db.Integer, db.ForeignKey("ESPECE.idEspece"), nullable=True)
    commentaire = db.Column(db.Text)

class CAMPAGNE(db.Model):
    __tablename__ = 'CAMPAGNE'
    idCampagne = db.Column(db.Integer, primary_key=True)
    nomPlateforme = db.Column(db.String(50), db.ForeignKey("PLATEFORME.nomPlateforme"))
    dateDebut = db.Column(db.DATE)
    duree = db.Column(db.Integer)
    lieu = db.Column(db.String(100))
    valide = db.Column(db.Boolean)
    participerCampagne = db.relationship("PARTICIPER_CAMPAGNE", back_populates="campagne")

class PERSONNEL(db.Model):
    __tablename__ = "PERSONNEL"
    idPersonnel = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(50))
    prenom = db.Column(db.String(50))
    mdp = db.Column(db.String(10), unique=True)
    role = db.Column(db.Enum(Role))
    participerCampagne = db.relationship("PARTICIPER_CAMPAGNE", back_populates="personnel")
    posseder = db.relationship("POSSEDER", back_populates="personnel")

class PARTICIPER_CAMPAGNE(db.Model):
    __tablename__ = "PARTICIPER_CAMPAGNE"
    idCampagne = db.Column( db.Integer, db.ForeignKey("CAMPAGNE.idCampagne"),primary_key=True)
    idPersonnel = db.Column(db.Integer, db.ForeignKey("PERSONNEL.idPersonnel"),primary_key=True)
    campagne = db.relationship("CAMPAGNE", back_populates="participerCampagne")
    personnel = db.relationship("PERSONNEL", back_populates="participerCampagne")

class POSSEDER(db.Model):
    __tablename__ = "POSSEDER"
    idPersonnel = db.Column(db.Integer, db.ForeingKey("PERSONNEL.idPersonnel"),primary_key=True)
    idHabilitation = db.Column(db.Integer, db.ForeignKey("HABILITATION.idHabilitation"), primary_key=True)
    personnel = db.relationship("PERSONNEL", back_populate="posseder")
    habilitation = db.relationship("HABILITATION", back_populates="posseder")

class Personnel:

    def __init__(self, id_personnel = 0, nom = "", prenom = "", role = "", mot_de_passe = ""):
        self.id_personnel = id_personnel
        self.nom = nom
        self.prenom = prenom
        self.role = role
        self.mot_de_passe = mot_de_passe