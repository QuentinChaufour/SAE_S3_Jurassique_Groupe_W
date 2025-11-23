import enum
from .app import db,login_manager
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from flask_login import UserMixin

class ROLE(enum.Enum):
    administratif = 'administratif'
    chercheur = 'chercheur'
    technicien = 'technicien'
    direction = 'direction'

inclure_equipement = db.Table("INCLURE_EQUIPEMENT", 
                              db.Column("nom_plateforme_inclure", db.String(50), db.ForeignKey("PLATEFORME.nomPlateforme"), primary_key=True), 
                              db.Column("id_equipement_inclure", db.Integer, db.ForeignKey("EQUIPEMENT.idEquipement"), primary_key=True))

necessiter_habilitation = db.Table("NECESSITER_HABILITATION", 
                                   db.Column("id_equipement_necessiter", db.Integer, db.ForeignKey("EQUIPEMENT.idEquipement"), primary_key=True),
                                   db.Column("id_habilitation_necessiter", db.Integer, db.ForeignKey("HABILITATION.idHabilitation"), primary_key=True))

class ESPECE(db.Model):
    __tablename__ = 'ESPECE'
    id_espece = db.Column("idEspece", db.Integer, primary_key=True, autoincrement=True)
    nom_espece = db.Column("nomEspece",db.String(50))
    nom_scientifique = db.Column("nomScientifique", db.String(100))
    genome = db.Column(db.Text)
    echantillons = db.relationship("ECHANTILLON", back_populates="espece")

    def __init__(self, nom_espece, nom_scientifique=nom_espece, genome=""):
        self.nom_espece = nom_espece
        self.nom_scientifique = nom_scientifique
        self.genome = genome

    def __repr__(self):
        return f"<Espèce : {self.nom_espece}, {self.nom_scientifique}>"

class ECHANTILLON(db.Model):
    __tablename__ = 'ECHANTILLON'
    id_echantillon = db.Column("idEchantillon",db.Integer, primary_key=True, autoincrement=True)
    id_campagne = db.Column("idCampagne",db.Integer,db.ForeignKey("CAMPAGNE.idCampagne"))
    fichier_sequence_adn = db.Column("fichierSequenceADN",MEDIUMTEXT)
    id_espece = db.Column("idEspece", db.Integer, db.ForeignKey("ESPECE.idEspece"), nullable=True)
    commentaire = db.Column(db.Text)
    espece = db.relationship("ESPECE", back_populates="echantillons")
    campagne = db.relationship("CAMPAGNE", back_populates="echantillons")

    def __init__(self, id_campagne, fichier_sequence_adn, commentaire=None, id_espece=None):
        self.id_campagne = id_campagne
        self.fichier_sequence_adn = fichier_sequence_adn
        self.id_espece = id_espece
        self.commentaire = commentaire

    def __repr__(self):
        return f"<Échantillon de la campagne n°{self.id_campagne} la séquence adn: {self.fichier_sequence_adn}>"
    
class CAMPAGNE(db.Model):
    __tablename__ = 'CAMPAGNE'
    id_campagne = db.Column("idCampagne", db.Integer, primary_key=True, autoincrement=True)
    nom_plateforme = db.Column("nomPlateforme", db.String(50), db.ForeignKey("PLATEFORME.nomPlateforme"))
    dateDebut = db.Column(db.DATE)
    duree = db.Column(db.Integer)
    lieu = db.Column(db.String(100))
    valide = db.Column(db.Boolean)
    participerCampagne = db.relationship("PARTICIPER_CAMPAGNE", back_populates="campagne")
    plateforme = db.relationship("PLATEFORME", back_populates="campagnes")
    echantillons = db.relationship("ECHANTILLON", back_populates="campagne")


    def __init__(self, nom_plateforme, dateDebut, duree, lieu, valide=False ):
        self.nom_plateforme = nom_plateforme
        self.dateDebut = dateDebut
        self.duree = duree
        self.lieu = lieu
        self.valide = valide

    def __repr__(self):
        return f"<Campagne n°{self.id_campagne} sur la plateforme {self.nom_plateforme} a commencé le {self.dateDebut} pour une durée de {self.duree}>"



class PERSONNEL(db.Model, UserMixin):
    __tablename__ = "PERSONNEL"
    id_personnel = db.Column("idPersonnel", db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(50))
    prenom = db.Column(db.String(50))
    mdp = db.Column(db.String(10), unique=True)
    role = db.Column(db.Enum(ROLE))

    participerCampagne = db.relationship("PARTICIPER_CAMPAGNE", back_populates="personnel")
    posseder = db.relationship("POSSEDER", back_populates="personnels")

    def __init__(self, nom, prenom, mdp, role):
        self.nom = nom
        self.prenom = prenom
        self.mdp = mdp
        self.role = role
    
    def get_id(self):
        return self.id_personnel

    def get_role(self) -> ROLE:
        return self.role

    def __repr__(self):
        return f"<{self.nom} {self.prenom} : {self.role}>"

class PARTICIPER_CAMPAGNE(db.Model):
    __tablename__ = "PARTICIPER_CAMPAGNE"
    id_campagne = db.Column("idCampagne", db.Integer, db.ForeignKey("CAMPAGNE.idCampagne"),primary_key=True)
    id_personnel = db.Column("idPersonnel", db.Integer, db.ForeignKey("PERSONNEL.idPersonnel"),primary_key=True)
    campagne = db.relationship("CAMPAGNE", back_populates="participerCampagne")
    personnel = db.relationship("PERSONNEL", back_populates="participerCampagne")

    def __init__(self, id_campagne, id_personnel):
        self.id_campagne = id_campagne
        self.id_personnel = id_personnel

    def __repr__(self):
        nom = getattr(self.personnel, 'nom', None)
        prenom = getattr(self.personnel, 'prenom', None)
        return f"<POSSEDER campagne= n°{self.id_campagne} personnel={nom!r} {prenom!r}>"

class POSSEDER(db.Model):
    __tablename__ = "POSSEDER_HABILITATION"
    id_personnel = db.Column("idPersonnel", db.Integer, db.ForeignKey("PERSONNEL.idPersonnel"),primary_key=True)
    id_habilitation = db.Column("idHabilitation", db.Integer, db.ForeignKey("HABILITATION.idHabilitation"), primary_key=True)
    personnels = db.relationship("PERSONNEL", back_populates="posseder")
    habilitations = db.relationship("HABILITATION", back_populates="posseder")

    def __init__(self, id_habilitation, id_personnel):
        self.id_habilitation = id_habilitation
        self.id_personnel = id_personnel

    def __repr__(self):
        hab = getattr(self.habilitation, 'nom_habilitation', None)
        nom = getattr(self.personnel, 'nom', None)
        prenom = getattr(self.personnel, 'prenom', None)
        return f"<POSSEDER habilitation={hab!r} personnel={nom!r} {prenom!r}>"

class BUDGET(db.Model):
    __tablename__ = 'BUDGET'
    
    date_mois_annee = db.Column("dateMoisAnnee", db.Date, primary_key=True)
    budget_total = db.Column("budgetTotal", db.Numeric(10, 2))

    def __init__(self, date_mois_annee=None, budget_total=0):
        self.date_mois_annee = date_mois_annee
        self.budget_total = budget_total

    def __repr__(self):
        return 'Budget : ' + str(self.date_mois_annee)


class PLATEFORME(db.Model):
    __tablename__ = 'PLATEFORME'
    
    nom_plateforme = db.Column("nomPlateforme", db.String(50), primary_key=True)
    nb_personnes_requises = db.Column("nbPersonnesRequises", db.Integer)
    cout_journalier = db.Column("coutJournalier", db.Numeric(10, 2))
    intervalle_maintenance = db.Column("intervalleMaintenance", db.Integer)
    
    equipements = db.relationship('EQUIPEMENT', secondary=inclure_equipement, back_populates='plateformes')
    maintenances = db.relationship('MAINTENANCE', back_populates='plateforme')
    campagnes = db.relationship('CAMPAGNE', back_populates='plateforme')
    

    def __init__(self, nom_plateforme="", nb_personnes_requises=0, cout_journalier=0, intervalle_maintenance=0):
        self.nom_plateforme = nom_plateforme
        self.nb_personnes_requises = nb_personnes_requises
        self.cout_journalier = cout_journalier
        self.intervalle_maintenance = intervalle_maintenance

    def __repr__(self):
        return 'Plateforme : ' + self.nom_plateforme
    

class HABILITATION(db.Model):
    __tablename__ = 'HABILITATION'
    
    id_habilitation = db.Column("idHabilitation", db.Integer, primary_key=True, autoincrement=True)
    nom_habilitation = db.Column("nomHabilitation", db.String(50))

    equipements = db.relationship('EQUIPEMENT', secondary="NECESSITER_HABILITATION", back_populates='habilitations')
    posseder = db.relationship('POSSEDER', back_populates='habilitations')

    def __init__(self, nom_habilitation=""):
        self.nom_habilitation = nom_habilitation

    def __repr__(self):
        return 'Habilitation : ' + self.nom_habilitation

class EQUIPEMENT(db.Model):
    __tablename__ = 'EQUIPEMENT'
    
    id_equipement = db.Column("idEquipement", db.Integer, primary_key=True, autoincrement=True)
    nom_equipement = db.Column("nomEquipement", db.String(50))
    
    plateformes = db.relationship('PLATEFORME', secondary=inclure_equipement, back_populates='equipements')
    habilitations = db.relationship('HABILITATION', secondary="NECESSITER_HABILITATION", back_populates='equipements')

    def __init__(self, nom_equipement=""):
        self.nom_equipement = nom_equipement

    def __repr__(self):
        return 'Equipement : ' + self.nom_equipement

class MAINTENANCE(db.Model):
    __tablename__ = 'MAINTENANCE'
    
    nom_plateforme = db.Column("nomPlateforme", db.String(50), db.ForeignKey('PLATEFORME.nomPlateforme'), primary_key=True)
    date_maintenance = db.Column("dateMaintenance", db.Date, primary_key=True)
    duree_maintenance = db.Column("dureeMaintenance", db.Integer)
    
    plateforme = db.relationship('PLATEFORME', back_populates='maintenances')

    def __init__(self, nom_plateforme="", date_maintenance=None, duree_maintenance=0):
        self.nom_plateforme = nom_plateforme
        self.date_maintenance = date_maintenance
        self.duree_maintenance = duree_maintenance

    def __repr__(self):
        return 'Maintenance : ' + self.nom_plateforme

@login_manager.user_loader
def load_user(user_id: int) -> PERSONNEL:
    return PERSONNEL.query.filter_by(id_personnel=user_id).first()