from .app import db
import enum
from sqlalchemy import Integer, Enum

from sqlalchemy.dialects.mysql import MEDIUMTEXT
class ROLE(db.Enum):
    administratif = 'administratif'
    chercheur = 'chercheur'
    technicien = 'technicien'
    direction = 'direction'

class ESPECE(db.Model):
    __tablename__ = 'ESPECE'
    id_espece = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_espece = db.Column(db.String(50))
    nom_scientifique = db.Column(db.String(100))
    genome = db.Column(db.Text)

    def __init__(self, nom_espece, nom_scientifique=nom_espece, genome=""):
        self.nom_espece = nom_espece
        self.nom_scientifique = nom_scientifique
        self.genome = genome

    def __repr__(self):
        return f"<Espèce : {self.nom_espece}, {self.nom_scientifique}>"

class ECHANTILLON(db.Model):
    __tablename__ = 'ECHANTILLON'
    id_echantillon = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_campagne = db.Column(db.Integer,db.ForeignKey("CAMPAGNE.id_campagne"))
    fichier_sequence_adn = db.Column(MEDIUMTEXT)
    id_espece = db.Column(db.Integer, db.ForeignKey("ESPECE.id_espece"), nullable=True)
    commentaire = db.Column(db.Text)

    def __init__(self, id_campagne, fichier_sequence_adn, id_espece=None, commentaire=""):
        self.id_campagne = id_campagne
        self.fichier_sequence_adn = fichier_sequence_adn
        self.id_espece = id_espece
        self.commentaire = commentaire

    def __repr__(self):
        return f"<Échantillon de la campagne n°{self.id_campagne} la séquence adn: {self.fichier_sequence_adn}>"

class CAMPAGNE(db.Model):
    __tablename__ = 'CAMPAGNE'
    id_campagne = db.Column(db.Integer, primary_key=True)
    nom_plateforme = db.Column(db.String(50), db.ForeignKey("PLATEFORME.nom_plateforme"))
    date_debut = db.Column(db.DATE)
    duree = db.Column(db.Integer)
    lieu = db.Column(db.String(100))
    valide = db.Column(db.Boolean)
    participer_campagne = db.relationship("PARTICIPER_CAMPAGNE", back_populates="campagne")
    plateforme = db.relationship("PLATEFORME", back_populates="campagnes")

    def __init__(self, nom_plateforme, date_debut, duree, lieu, valide=False ):
        self.nom_plateforme = nom_plateforme
        self.date_debut = date_debut
        self.duree = duree
        self.lieu = lieu
        self.valide = valide

    def __repr__(self):
        return f"<Campagne n°{self.id_campagne} sur la plateforme {self.nom_plateforme} a commencé le {self.date_debut} pour une durée de {self.duree}>"

class PERSONNEL(db.Model):
    __tablename__ = "PERSONNEL"
    id_personnel = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(50))
    prenom = db.Column(db.String(50))
    mdp = db.Column(db.String(10), unique=True)
    role = db.Column(ROLE)
    participer_campagne = db.relationship("PARTICIPER_CAMPAGNE", back_populates="personnel")
    posseder = db.relationship("POSSEDER", back_populates="personnel")

    def __init__(self, nom, prenom, mdp, role):
        self.nom = nom
        self.prenom = prenom
        self.mdp = mdp
        self.role = role

    def __repr__(self):
        return f"<{self.nom} {self.prenom} : {self.role}>"

class PARTICIPER_CAMPAGNE(db.Model):
    __tablename__ = "PARTICIPER_CAMPAGNE"
    id_campagne = db.Column( db.Integer, db.ForeignKey("CAMPAGNE.id_campagne"),primary_key=True)
    id_personnel = db.Column(db.Integer, db.ForeignKey("PERSONNEL.id_personnel"),primary_key=True)
    campagne = db.relationship("CAMPAGNE", back_populates="participer_campagne")
    personnel = db.relationship("PERSONNEL", back_populates="participer_campagne")

    def __init__(self, id_campagne, id_personnel):
        self.id_campagne = id_campagne
        self.id_personnel = id_personnel

    def __repr__(self):
        nom = getattr(self.personnel, 'nom', None)
        prenom = getattr(self.personnel, 'prenom', None)
        return f"<POSSEDER campagne= n°{self.id_campagne} personnel={nom!r} {prenom!r}>"

class POSSEDER(db.Model):
    __tablename__ = "POSSEDER"
    id_personnel = db.Column(db.Integer, db.ForeignKey("PERSONNEL.id_personnel"),primary_key=True)
    id_habilitation = db.Column(db.Integer, db.ForeignKey("HABILITATION.id_habilitation"), primary_key=True)
    personnel = db.relationship("PERSONNEL", back_populates="posseder")
    habilitation = db.relationship("HABILITATION", back_populates="posseder")

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
    
    date_mois_annee = db.Column(db.Date, primary_key=True)
    budget_total = db.Column(db.Numeric(10, 2))

    def __init__(self, date_mois_annee=None, budget_total=0):
        self.date_mois_annee = date_mois_annee
        self.budget_total = budget_total

    def __repr__(self):
        return 'Budget : ' + str(self.date_mois_annee)

inclure_equipement = db.Table("inclure_equipement", 
                              db.Column("nom_plateforme_inclure", db.String(50), db.ForeignKey("PLATEFORME.nom_plateforme")), 
                              db.Column("id_equipement_inclure", db.Integer, db.ForeignKey("EQUIPEMENT.id_equipement")))

class PLATEFORME(db.Model):
    __tablename__ = 'PLATEFORME'
    
    nom_plateforme = db.Column(db.String(50), primary_key=True)
    nb_personnes_requises = db.Column(db.Integer)
    cout_journalier = db.Column(db.Numeric(10, 2))
    intervalle_maintenance = db.Column(db.Integer)
    
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
necessiter_habilitation = db.Table("necessiter_habilitation", 
                                   db.Column("id_equipement_necessiter", db.Integer, db.ForeignKey("EQUIPEMENT.id_equipement")),
                                   db.Column("id_habilitation_necessiter", db.Integer, db.ForeignKey("HABILITATION.id_habilitation")))
class HABILITATION(db.Model):
    __tablename__ = 'HABILITATION'
    
    id_habilitation = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_habilitation = db.Column(db.String(50))
    equipements = db.relationship('EQUIPEMENT', secondary=necessiter_habilitation, back_populates='habilitations')
    posseder = db.relationship('POSSEDER', back_populates='habilitation')

    def __init__(self, nom_habilitation=""):
        self.nom_habilitation = nom_habilitation

    def __repr__(self):
        return 'Habilitation : ' + self.nom_habilitation

class EQUIPEMENT(db.Model):
    __tablename__ = 'EQUIPEMENT'
    
    id_equipement = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_equipement = db.Column(db.String(50))
    
    plateformes = db.relationship('PLATEFORME', secondary=inclure_equipement, back_populates='equipements')
    habilitations = db.relationship('HABILITATION', secondary=necessiter_habilitation, back_populates='equipements')
    def __init__(self, nom_equipement=""):
        self.nom_equipement = nom_equipement

    def __repr__(self):
        return 'Equipement : ' + self.nom_equipement

class MAINTENANCE(db.Model):
    __tablename__ = 'MAINTENANCE'
    
    nom_plateforme = db.Column(db.String(50), db.ForeignKey('PLATEFORME.nom_plateforme'), primary_key=True)
    date_maintenance = db.Column(db.Date, primary_key=True)
    duree_maintenance = db.Column(db.Integer)
    
    plateforme = db.relationship('PLATEFORME', back_populates='maintenances')

    def __init__(self, nom_plateforme="", date_maintenance=None, duree_maintenance=0):
        self.nom_plateforme = nom_plateforme
        self.date_maintenance = date_maintenance
        self.duree_maintenance = duree_maintenance

    def __repr__(self):
        return 'Maintenance : ' + self.nom_plateforme
