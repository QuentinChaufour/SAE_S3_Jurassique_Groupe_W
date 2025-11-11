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

class Budget(db.Model):
    __tablename__ = 'budget'
    
    date_mois_annee = db.Column(db.Date, primary_key=True)
    budget_total = db.Column(db.Numeric(10, 2))

    def __init__(self, date_mois_annee=None, budget_total=0):
        self.date_mois_annee = date_mois_annee
        self.budget_total = budget_total

    def __repr__(self):
        return 'Budget : ' + str(self.date_mois_annee)
    
class Plateforme(db.Model):
    __tablename__ = 'plateforme'
    
    nom_plateforme = db.Column(db.String(50), primary_key=True)
    nb_personnes_requises = db.Column(db.Integer)
    cout_journalier = db.Column(db.Numeric(10, 2))
    intervalle_maintenance = db.Column(db.Integer)
    
    #equipements = db.relationship('Equipement', back_populates='plateformes')
    #maintenances = db.relationship('Maintenance', back_populates='plateforme')
    #campagnes = db.relationship('Campagne', back_populates='plateformes')

    def __init__(self, nom_plateforme="", nb_personnes_requises=0, cout_journalier=0, intervalle_maintenance=0):
        self.nom_plateforme = nom_plateforme
        self.nb_personnes_requises = nb_personnes_requises
        self.cout_journalier = cout_journalier
        self.intervalle_maintenance = intervalle_maintenance

    def __repr__(self):
        return 'Plateforme : ' + self.nom_plateforme

class Habilitation(db.Model):
    __tablename__ = 'habilitation'
    
    id_habilitation = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_habilitation = db.Column(db.String(50))
    
    #personnels = db.relationship('Personnel', back_populates='habilitations')
    equipements = db.relationship('Equipement', back_populates='habilitations')

    def __init__(self, nom_habilitation=""):
        self.nom_habilitation = nom_habilitation

    def __repr__(self):
        return 'Habilitation : ' + self.nom_habilitation

class Equipement(db.Model):
    __tablename__ = 'equipement'
    
    id_equipement = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_equipement = db.Column(db.String(50))
    
    plateformes = db.relationship('Plateforme', back_populates='equipements')
    habilitations = db.relationship('Habilitation', back_populates='equipements')

    def __init__(self, nom_equipement=""):
        self.nom_equipement = nom_equipement

    def __repr__(self):
        return 'Equipement : ' + self.nom_equipement

class Maintenance(db.Model):
    __tablename__ = 'maintenance'
    
    nom_plateforme = db.Column(db.String(50), db.ForeignKey('plateforme.nom_plateforme'), primary_key=True)
    date_maintenance = db.Column(db.Date, primary_key=True)
    duree_maintenance = db.Column(db.Integer)
    
    plateforme = db.relationship('Plateforme', back_populates='maintenances')

    def __init__(self, nom_plateforme="", date_maintenance=None, duree_maintenance=0):
        self.nom_plateforme = nom_plateforme
        self.date_maintenance = date_maintenance
        self.duree_maintenance = duree_maintenance

    def __repr__(self):
        return 'Maintenance : ' + self.nom_plateforme

class Personnel:

    def __init__(self, id_personnel = 0, nom = "", prenom = "", role = "", mot_de_passe = ""):
        self.id_personnel = id_personnel
        self.nom = nom
        self.prenom = prenom
        self.role = role
        self.mot_de_passe = mot_de_passe